// out-the-door: BART departures, weather, an Oblique Strategies card and the
// moon phase on the CrowPanel's 2.13" e-paper screen, run from a battery.
//
// The board spends almost all its time in deep sleep, resting on the moon
// screen, which it redraws once an hour. A press of the wheel wakes it for five
// minutes, starting on fresh train times, with screens cycling and the wheel
// flipping between them; then it returns to the moon and sleeps.
#include <Arduino.h>
#include <driver/rtc_io.h>
#include <esp_sleep.h>
#include <time.h>

#include "bart.h"
#include "buttons.h"
#include "cards.h"
#include "clock.h"
#include "config.h"
#include "net.h"
#include "panel.h"
#include "screens.h"
#include "secrets.h"
#include "text.h"
#include "weather.h"

// After a wake or a button press the board stays awake this long.
static const uint32_t WAKE_MS = 5 * 60 * 1000;
// Minimum gap between attempts when a fetch keeps failing while awake.
static const uint32_t TRAINS_RETRY_S = 15, WEATHER_RETRY_S = 60;
// How often to resync the clock over NTP.
static const time_t CLOCK_SYNC_S = 6 * 60 * 60;

static GFXcanvas1 canvas(SCREEN_W, SCREEN_H);
static Panel panel(PANEL_REVISION);

// Kept in RTC memory across deep sleep. Only trusted after a deep-sleep wake.
RTC_DATA_ATTR static TrainRow trains[TRAIN_ROW_COUNT];
RTC_DATA_ATTR static bool haveTrains;
RTC_DATA_ATTR static time_t trainsAt, trainsTriedAt;
RTC_DATA_ATTR static CityWeather weather[2];
RTC_DATA_ATTR static bool haveWeather;
RTC_DATA_ATTR static time_t weatherAt, weatherTriedAt;
RTC_DATA_ATTR static time_t clockSyncedAt;
RTC_DATA_ATTR static int changes;
RTC_DATA_ATTR static bool restingOnArt;  // the screensaver is up; leave it until a wake

static int page = 0;
static uint32_t shownAt = 0;
static uint32_t wakeUntil = 0;

static time_t nowSeconds() { return time(nullptr); }
static long ageSeconds(time_t at) { return (long)(nowSeconds() - at); }

static void fetchTrains() {
  trainsTriedAt = nowSeconds();
  char url[160];
  bartUrl(STATION, BART_KEY, url, sizeof url);
  String body;
  TrainRow fresh[TRAIN_ROW_COUNT];
  if (httpGet(url, body) && parseBart(body.c_str(), TRAIN_ROWS, TRAIN_ROW_COUNT, fresh)) {
    memcpy(trains, fresh, sizeof trains);
    haveTrains = true;
    trainsAt = nowSeconds();
  }
}

static void fetchWeather() {
  weatherTriedAt = nowSeconds();
  char url[400];
  weatherUrl(CITIES, 2, url, sizeof url);
  String body;
  CityWeather fresh[2];
  if (httpGet(url, body) && parseWeather(body.c_str(), fresh, 2)) {
    // Air quality is a second request; the screen leaves it out if this fails.
    airQualityUrl(CITIES, 2, url, sizeof url);
    if (httpGet(url, body)) parseAirQuality(body.c_str(), fresh, 2);
    memcpy(weather, fresh, sizeof weather);
    haveWeather = true;
    weatherAt = nowSeconds();
  }
}

static bool trainsDue() {
  return (!haveTrains || ageSeconds(trainsAt) >= (long)TRAINS_MAX_AGE) &&
         ageSeconds(trainsTriedAt) >= (long)TRAINS_RETRY_S;
}

static bool weatherDue() {
  return (!haveWeather || ageSeconds(weatherAt) >= (long)WEATHER_MAX_AGE) &&
         ageSeconds(weatherTriedAt) >= (long)WEATHER_RETRY_S;
}

static void syncClockIfDue() {
  if (!clockValid() || nowSeconds() - clockSyncedAt >= CLOCK_SYNC_S) {
    if (clockStart()) clockSyncedAt = nowSeconds();
  }
}

static void draw(int which) {
  const Now now = makeNow(nowSeconds());
  canvas.fillScreen(PAPER);
  switch (which) {
    case 0: {
      TrainRow counted[TRAIN_ROW_COUNT];
      const long age = haveTrains ? ageSeconds(trainsAt) : 0;
      for (int i = 0; i < TRAIN_ROW_COUNT; i++) counted[i] = countDown(trains[i], age);
      const TrainsView view{STATION_LABEL, TRAIN_ROWS, TRAIN_ROW_COUNT, haveTrains ? counted : nullptr, age,
                            (long)TRAINS_STALE, (long)TRAINS_GIVE_UP};
      drawTrains(canvas, now, view);
      break;
    }
    case 1:
      drawWeather(canvas, now, CITIES, haveWeather ? weather : nullptr);
      break;
    case 2:
      drawOblique(canvas, now, cardForDay(now.localDays));
      break;
    default:
      drawMoon(canvas, now);
      break;
  }
}

static void present(bool full = false) {
  panel.show(canvas, full || ++changes % FULL_REFRESH_EVERY == 0);
  shownAt = millis();
}

static void showPage(bool full = false) {
  draw(page);
  present(full);
}

static void splash(const char *line) {
  canvas.fillScreen(PAPER);
  drawSplash(canvas, line);
  panel.show(canvas, true);
}

// The screen the board rests on while asleep.
static const int REST_PAGE = PAGE_COUNT - 1;  // moon

// Seconds until the next hourly moon redraw.
static uint64_t secondsToNextWake() {
  const time_t t = nowSeconds();
  if (!clockValid()) return 60 * 60;
  return 60 * 60 - (t % (60 * 60)) + 1;
}

[[noreturn]] static void sleepNow() {
  panel.powerOff();
  wifiOff();
  const uint64_t seconds = secondsToNextWake();
  Serial.printf("sleep: %llu s\n", seconds);
  esp_sleep_enable_timer_wakeup(seconds * 1000000ULL);
  // Only pressing the wheel wakes it, so a bump to the other buttons doesn't.
  if (digitalRead(WAKE_PIN) == HIGH) {  // if held now, waking on it would loop
    rtc_gpio_pullup_en((gpio_num_t)WAKE_PIN);
    rtc_gpio_pulldown_dis((gpio_num_t)WAKE_PIN);
    esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_ON);
    esp_sleep_enable_ext1_wakeup(1ULL << WAKE_PIN, ESP_EXT1_WAKEUP_ANY_LOW);
  }
  Serial.flush();
  esp_deep_sleep_start();
}

// The screensaver, drawn in four greys. For now a test pattern: four bands
// (black, dark grey, light grey, white) and a dithered gradient, to check the
// greys on this panel before the art goes in.
static uint8_t greys[SCREEN_W * SCREEN_H];

static void showScreensaver() {
  for (int y = 0; y < SCREEN_H; y++) {
    for (int x = 0; x < SCREEN_W; x++) {
      uint8_t level;
      if (y < 80) {
        level = x * 4 / SCREEN_W;
      } else {
        // 4x4 ordered dither of a left-to-right gradient onto the four levels.
        static const uint8_t BAYER[4][4] = {{0, 8, 2, 10}, {12, 4, 14, 6}, {3, 11, 1, 9}, {15, 7, 13, 5}};
        const int v = x * 3 * 16 / (SCREEN_W - 1);  // 0..48
        level = (uint8_t)(v / 16 + ((v % 16) > BAYER[y & 3][x & 3] ? 1 : 0));
        if (level > 3) level = 3;
      }
      greys[y * SCREEN_W + x] = level;
    }
  }
  // Band numbers, in the opposite shade so they show on every band.
  canvas.fillScreen(PAPER);
  for (int i = 0; i < 4; i++) {
    char label[2] = {(char)('0' + i), 0};
    drawTextCenter(canvas, BOLD26, SCREEN_W * (2 * i + 1) / 8, 24, label, INK);
  }
  for (int y = 0; y < SCREEN_H; y++)
    for (int x = 0; x < SCREEN_W; x++)
      if (canvas.getPixel(x, y)) greys[y * SCREEN_W + x] = greys[y * SCREEN_W + x] < 2 ? 3 : 0;
  panel.showGrey4(greys);
  restingOnArt = true;
}

// A timer wake: redraw the moon (the date or phase may have changed) and
// sleep again. Wi-Fi only comes on when the clock is due a resync.
static void tick() {
  if (restingOnArt) sleepNow();
  if (!clockValid() || nowSeconds() - clockSyncedAt >= CLOCK_SYNC_S) {
    if (wifiConnect(8000)) syncClockIfDue();
    wifiOff();
  }
  page = REST_PAGE;
  showPage();
  sleepNow();
}

void setup() {
  Serial.begin(115200);
  setenv("TZ", TIME_ZONE, 1);
  tzset();
  const esp_sleep_wakeup_cause_t cause = esp_sleep_get_wakeup_cause();
  const bool fromSleep = cause == ESP_SLEEP_WAKEUP_TIMER || cause == ESP_SLEEP_WAKEUP_EXT1;
  rtc_gpio_deinit((gpio_num_t)WAKE_PIN);
  buttonsBegin();
  panel.begin(fromSleep);
  if (cause != ESP_SLEEP_WAKEUP_TIMER) restingOnArt = false;

  Serial.printf("wake: cause %d\n", (int)cause);
  if (cause == ESP_SLEEP_WAKEUP_TIMER) tick();

  if (!fromSleep) {
    // Power on or reset: start from nothing.
    haveTrains = haveWeather = false;
    trainsAt = trainsTriedAt = weatherAt = weatherTriedAt = clockSyncedAt = 0;
    changes = 0;
    splash("Connecting to Wi-Fi...");
    if (!wifiConnect()) splash("No Wi-Fi yet, still trying");
  }
  // Power on, or woken by a button: stay up and browse for a while.
  if (wifiConnect()) {
    syncClockIfDue();
    if (trainsDue()) fetchTrains();
    if (weatherDue()) fetchWeather();
  }
  wakeUntil = millis() + WAKE_MS;
  page = 0;
  showPage(!fromSleep);
}

void loop() {
  const Button pressed = buttonPressed();
  if (pressed != Button::None) wakeUntil = millis() + WAKE_MS;

  if ((int32_t)(wakeUntil - millis()) <= 0) {
    // Done browsing: come to rest on the moon and sleep.
    if (page != REST_PAGE) {
      page = REST_PAGE;
      showPage();
    }
    sleepNow();
  }

  // Scroll wheel flips screens; pressing it (or Menu) jumps to fresh trains.
  switch (pressed) {
    case Button::Up:
      page = (page + PAGE_COUNT - 1) % PAGE_COUNT;
      showPage();
      return;
    case Button::Down:
      page = (page + 1) % PAGE_COUNT;
      showPage();
      return;
    case Button::Menu:
      // Sleep now, resting on the 4-grey screensaver instead of the moon.
      showScreensaver();
      sleepNow();
    case Button::Press:
      page = 0;
      fetchTrains();
      showPage();
      return;
    case Button::Back:
      page = 0;
      showPage();
      return;
    case Button::None:
      break;
  }

  if (millis() - shownAt >= SCREEN_SECONDS * 1000) {
    page = (page + 1) % PAGE_COUNT;
    if (page == 0 && trainsDue()) fetchTrains();
    showPage();
    return;
  }

  // While the screen before trains is up, fetch so the trains are fresh.
  if (page == PAGE_COUNT - 1 && trainsDue()) fetchTrains();
  if (weatherDue()) fetchWeather();
  delay(20);
}
