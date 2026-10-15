// out-the-door: rotates BART departures, weather, an Oblique Strategies card
// and the moon phase on the CrowPanel's 2.13" e-paper screen.
#include <Arduino.h>
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
#include "weather.h"

// After a button press the screen stays awake this long, even in quiet hours.
static const uint32_t WAKE_MS = 2 * 60 * 1000;
// Minimum gap between attempts when a fetch keeps failing.
static const uint32_t TRAINS_RETRY_MS = 15 * 1000, WEATHER_RETRY_MS = 60 * 1000;

static GFXcanvas1 canvas(SCREEN_W, SCREEN_H);
static Panel panel(PANEL_REVISION);

static int page = 0;
static int changes = 0;
static uint32_t shownAt = 0;
static uint32_t wakeUntil = 0;
static long quietDay = -1;  // local day whose quiet-hours card is on screen

static TrainRow trains[3];
static bool haveTrains = false;
static uint32_t trainsAt = 0, trainsTriedAt = 0;

static CityWeather weather[2];
static bool haveWeather = false;
static uint32_t weatherAt = 0, weatherTriedAt = 0;

static uint32_t ageSeconds(uint32_t at) { return (millis() - at) / 1000; }

static void fetchTrains() {
  trainsTriedAt = millis();
  char url[160];
  bartUrl(STATION, BART_KEY, url, sizeof url);
  String body;
  TrainRow fresh[3];
  if (httpGet(url, body) && parseBart(body.c_str(), TRAIN_ROWS, 3, fresh)) {
    memcpy(trains, fresh, sizeof trains);
    haveTrains = true;
    trainsAt = millis();
  }
}

static void fetchWeather() {
  weatherTriedAt = millis();
  char url[400];
  weatherUrl(CITIES, 2, url, sizeof url);
  String body;
  CityWeather fresh[2];
  if (httpGet(url, body) && parseWeather(body.c_str(), fresh, 2)) {
    memcpy(weather, fresh, sizeof weather);
    haveWeather = true;
    weatherAt = millis();
  }
}

static bool trainsDue() {
  return (!haveTrains || ageSeconds(trainsAt) >= TRAINS_MAX_AGE) &&
         millis() - trainsTriedAt >= TRAINS_RETRY_MS;
}

static bool weatherDue() {
  return (!haveWeather || ageSeconds(weatherAt) >= WEATHER_MAX_AGE) &&
         millis() - weatherTriedAt >= WEATHER_RETRY_MS;
}

static bool quietHours(const Now &n) {
  if (QUIET_START > QUIET_END) return n.hour >= QUIET_START || n.hour < QUIET_END;
  return n.hour >= QUIET_START && n.hour < QUIET_END;
}

static void showPage(bool full = false) {
  const Now now = makeNow(time(nullptr));
  canvas.fillScreen(PAPER);
  switch (page) {
    case 0: {
      TrainRow counted[3];
      const long age = haveTrains ? (long)ageSeconds(trainsAt) : 0;
      for (int i = 0; i < 3; i++) counted[i] = countDown(trains[i], age);
      const TrainsView view{STATION_LABEL, TRAIN_ROWS, haveTrains ? counted : nullptr, age,
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
  panel.show(canvas, full || changes % FULL_REFRESH_EVERY == 0);
  changes++;
  shownAt = millis();
}

static void splash(const char *line) {
  canvas.fillScreen(PAPER);
  drawSplash(canvas, line);
  panel.show(canvas, true);
}

void setup() {
  Serial.begin(115200);
  buttonsBegin();
  panel.begin();
  splash("Connecting to Wi-Fi...");
  if (!wifiConnect() || !clockStart()) splash("No Wi-Fi yet, still trying");
  fetchTrains();
  fetchWeather();
  page = 0;
  showPage(true);
}

void loop() {
  const Button pressed = buttonPressed();
  if (pressed != Button::None) wakeUntil = millis() + WAKE_MS;
  const bool awake = (int32_t)(wakeUntil - millis()) > 0;
  const Now now = makeNow(time(nullptr));

  // Quiet hours: hold the card of the day with Wi-Fi off until morning or a press.
  if (clockValid() && quietHours(now) && !awake) {
    if (quietDay != now.localDays) {
      canvas.fillScreen(PAPER);
      drawOblique(canvas, now, cardForDay(now.localDays), -1);
      panel.show(canvas, true);
      panel.sleep();
      wifiOff();
      quietDay = now.localDays;
    }
    delay(50);
    return;
  }
  if (quietDay != -1) {  // morning, or woken by a button
    quietDay = -1;
    wifiConnect();
    fetchTrains();
    fetchWeather();
    page = 0;
    showPage(true);
    return;
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
    case Button::Press:
    case Button::Menu:
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
