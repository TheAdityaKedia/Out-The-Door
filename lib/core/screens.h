// The four screens, each drawn onto a 250x122 1-bit canvas. INK pixels are
// black on the panel, PAPER pixels white.
#pragma once
#include <Adafruit_GFX.h>

#include "types.h"

static const int SCREEN_W = 250, SCREEN_H = 122;
static const uint16_t INK = 1, PAPER = 0;
static const int PAGE_COUNT = 4;

struct TrainsView {
  const char *stationLabel;
  const TrainRowConfig *rows;
  int rowCount;             // 3 or 4
  const TrainRow *minutes;  // already counted down; null if never fetched
  long ageSeconds;          // since the last good fetch
  long staleAfter, giveUpAfter;
};

void drawTrains(Adafruit_GFX &g, const Now &now, const TrainsView &v);
// cities: null if weather has never been fetched.
void drawWeather(Adafruit_GFX &g, const Now &now, const CityConfig *config, const CityWeather *cities);
// page < 0 hides the page dots (quiet hours).
void drawOblique(Adafruit_GFX &g, const Now &now, const char *card, int page = 2);
void drawMoon(Adafruit_GFX &g, const Now &now);
// Shown while the board starts up.
void drawSplash(Adafruit_GFX &g, const char *line);
