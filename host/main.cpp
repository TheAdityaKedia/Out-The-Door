// Laptop-side checks for the parts that don't need the board, plus screen
// previews drawn by the same code the firmware runs.
//   host/build/check <fixtures dir> <previews dir>
#include <Adafruit_GFX.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include <string>

#include "bart.h"
#include "cards.h"
#include "clock.h"
#include "config.h"
#include "moon.h"
#include "screens.h"
#include "weather.h"

static int failures = 0;
#define CHECK(cond)                                                \
  do {                                                             \
    if (!(cond)) {                                                 \
      fprintf(stderr, "FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); \
      failures++;                                                  \
    }                                                              \
  } while (0)

static std::string readFile(const std::string &path) {
  FILE *f = fopen(path.c_str(), "rb");
  if (!f) {
    fprintf(stderr, "can't open %s\n", path.c_str());
    exit(2);
  }
  std::string s;
  char buf[4096];
  size_t n;
  while ((n = fread(buf, 1, sizeof buf, f)) > 0) s.append(buf, n);
  fclose(f);
  return s;
}

static time_t utc(int y, int mo, int d, int h, int mi) {
  struct tm t = {};
  t.tm_year = y - 1900;
  t.tm_mon = mo - 1;
  t.tm_mday = d;
  t.tm_hour = h;
  t.tm_min = mi;
  return timegm(&t);
}

static std::string hm(time_t t) {
  char buf[16];
  formatTime(makeNow(t), buf, sizeof buf);
  return buf;
}

static void checkClock() {
  // Daylight saving in 2026 starts Sun Mar 8 at 10:00 UTC and ends Sun Nov 1 at 09:00 UTC.
  CHECK(hm(utc(2026, 3, 8, 9, 59)) == "1:59a");
  CHECK(hm(utc(2026, 3, 8, 10, 0)) == "3:00a");
  CHECK(hm(utc(2026, 11, 1, 8, 59)) == "1:59a");
  CHECK(hm(utc(2026, 11, 1, 9, 0)) == "1:00a");
  CHECK(hm(utc(2026, 10, 14, 19, 5)) == "12:05p");
  const Now evening = makeNow(utc(2026, 10, 15, 3, 30));  // 8:30 pm the day before, local
  char buf[32];
  formatDayMonthDay(evening, buf, sizeof buf);
  CHECK(std::string(buf) == "Wed Oct 14");
  CHECK(hm(evening.epoch) == "8:30p");
}

static void checkBart(const std::string &dir) {
  TrainRow rows[TRAIN_ROW_COUNT];
  CHECK(parseBart(readFile(dir + "/bart_19th.json").c_str(), TRAIN_ROWS, TRAIN_ROW_COUNT, rows));
  CHECK(rows[0].count == 2 && rows[0].minutes[0] == 9 && rows[0].minutes[1] == 14);  // "Leaving" dropped
  CHECK(rows[1].count == 0);                                                            // no Antioch trains
  CHECK(rows[2].count == 4 && rows[2].minutes[0] == 3 && rows[2].minutes[1] == 5 &&
        rows[2].minutes[2] == 10 && rows[2].minutes[3] == 20);  // Daly City, SFO and Millbrae merged
  CHECK(rows[3].count == 2 && rows[3].minutes[0] == 7 && rows[3].minutes[1] == 22);
  const TrainRow later = countDown(rows[2], 6 * 60);
  CHECK(later.count == 2 && later.minutes[0] == 4 && later.minutes[1] == 14);
  CHECK(parseBart("{\"root\":{\"station\":[{\"abbr\":\"19TH\"}]}}", TRAIN_ROWS, TRAIN_ROW_COUNT, rows));
  CHECK(rows[0].count == 0 && rows[1].count == 0 && rows[2].count == 0 && rows[3].count == 0);
  CHECK(!parseBart("not json", TRAIN_ROWS, TRAIN_ROW_COUNT, rows));
}

static void checkWeather(const std::string &dir) {
  CityWeather w[2];
  CHECK(parseWeather(readFile(dir + "/weather.json").c_str(), w, 2));
  CHECK(w[0].uv == 6 && w[1].uv == 5 && w[0].aqi == -1);
  CHECK(parseAirQuality(readFile(dir + "/air_quality.json").c_str(), w, 2));
  CHECK(w[0].aqi == 42 && w[1].aqi == 38);
  CHECK(!parseAirQuality("not json", w, 2) && w[0].aqi == 42);
  CHECK(w[0].temp == 75 && w[0].high == 78 && w[0].low == 58 && w[0].icon == Icon::Sun);
  CHECK(w[1].temp == 63 && w[1].icon == Icon::Fog);
  char url[512];
  weatherUrl(CITIES, 2, url, sizeof url);
  CHECK(std::string(url).find("latitude=37.8044,37.7749") != std::string::npos);
}

static void checkMoon() {
  // The October 2026 full moon falls on the evening of Oct 25, Pacific time.
  const double age = moonAge(utc(2026, 10, 26, 4, 12) / 86400.0);
  CHECK(std::string(moonPhaseName(age)) == "Full Moon");
  CHECK(moonIllumination(age) > 0.99);
  const double crescent = moonAge(utc(2026, 10, 14, 14, 42) / 86400.0);
  CHECK(std::string(moonPhaseName(crescent)) == "Waxing Crescent");
  // Oakland on 2026-10-14: sunrise about 7:15 am, sunset about 6:33 pm PDT.
  long rise, set;
  CHECK(sunTimes(makeNow(utc(2026, 10, 14, 19, 0)).localDays, 37.8044, -122.2712, &rise, &set));
  CHECK(labs(rise - utc(2026, 10, 14, 14, 15)) < 4 * 60);
  CHECK(labs(set - utc(2026, 10, 15, 1, 33)) < 4 * 60);
}

static void writePbm(const GFXcanvas1 &c, const std::string &path) {
  FILE *f = fopen(path.c_str(), "wb");
  fprintf(f, "P4\n%d %d\n", c.width(), c.height());
  for (int y = 0; y < c.height(); y++) {
    for (int x = 0; x < c.width(); x += 8) {
      uint8_t b = 0;
      for (int k = 0; k < 8 && x + k < c.width(); k++)
        if (c.getPixel(x + k, y)) b |= 0x80 >> k;
      fputc(b, f);
    }
  }
  fclose(f);
}

template <typename Draw>
static void preview(const std::string &dir, const char *name, Draw draw) {
  GFXcanvas1 canvas(SCREEN_W, SCREEN_H);
  canvas.fillScreen(PAPER);
  draw(canvas);
  writePbm(canvas, dir + "/" + name + ".pbm");
}

int main(int argc, char **argv) {
  const std::string fixtures = argc > 1 ? argv[1] : "host/fixtures";
  const std::string out = argc > 2 ? argv[2] : "previews";
  setenv("TZ", TIME_ZONE, 1);
  tzset();

  checkClock();
  checkBart(fixtures);
  checkWeather(fixtures);
  checkMoon();

  const Now now = makeNow(utc(2026, 10, 14, 14, 42));  // 7:42 am PDT
  TrainRow rows[TRAIN_ROW_COUNT];
  parseBart(readFile(fixtures + "/bart_19th.json").c_str(), TRAIN_ROWS, TRAIN_ROW_COUNT, rows);
  CityWeather cities[2];
  parseWeather(readFile(fixtures + "/weather.json").c_str(), cities, 2);
  parseAirQuality(readFile(fixtures + "/air_quality.json").c_str(), cities, 2);
  const char *card = cardForDay(now.localDays);

  auto trains = [&](long age, bool have) {
    static TrainRow counted[TRAIN_ROW_COUNT];
    for (int i = 0; i < TRAIN_ROW_COUNT; i++) counted[i] = countDown(rows[i], age);
    return TrainsView{STATION_LABEL, TRAIN_ROWS, TRAIN_ROW_COUNT, have ? counted : nullptr, age,
                      (long)TRAINS_STALE, (long)TRAINS_GIVE_UP};
  };
  preview(out, "1_trains", [&](Adafruit_GFX &g) { drawTrains(g, now, trains(0, true)); });
  preview(out, "2_weather", [&](Adafruit_GFX &g) { drawWeather(g, now, CITIES, cities); });
  preview(out, "3_oblique", [&](Adafruit_GFX &g) { drawOblique(g, now, card); });
  preview(out, "4_moon", [&](Adafruit_GFX &g) { drawSunMoon(g, now, CITIES[0]); });
  preview(out, "4a_sun_moon_afternoon", [&](Adafruit_GFX &g) { drawSunMoon(g, makeNow(utc(2026, 10, 14, 22, 0)), CITIES[0]); });
  preview(out, "4b_sun_moon_night", [&](Adafruit_GFX &g) { drawSunMoon(g, makeNow(utc(2026, 10, 15, 5, 0)), CITIES[0]); });
  preview(out, "5_trains_stale", [&](Adafruit_GFX &g) { drawTrains(g, now, trains(4 * 60, true)); });
  preview(out, "6_trains_none", [&](Adafruit_GFX &g) { drawTrains(g, now, trains(0, false)); });
  preview(out, "7_oblique_long", [&](Adafruit_GFX &g) {
    drawOblique(g, now, "Look closely at the most embarrassing details and amplify them");
  });
  preview(out, "8_quiet", [&](Adafruit_GFX &g) { drawOblique(g, now, card, -1); });
  setWifiShown(false);
  preview(out, "10_trains_no_wifi", [&](Adafruit_GFX &g) { drawTrains(g, now, trains(0, true)); });
  setWifiShown(true);
  preview(out, "9_splash", [&](Adafruit_GFX &g) { drawSplash(g, "Connecting to Wi-Fi..."); });

  if (failures) {
    fprintf(stderr, "%d check(s) failed\n", failures);
    return 1;
  }
  printf("all checks passed; previews in %s/\n", out.c_str());
  return 0;
}
