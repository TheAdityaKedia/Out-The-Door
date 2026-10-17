// Everything you might want to change lives here.
#pragma once
#include "types.h"

// Display controller: 10 for the SSD1680, 12 for the JD79661. The revision
// printed on the back (V1.0 / V1.2) does not always match: a board labelled
// V1.2 turned out to have the SSD1680. If the screen never changes, try the other.
#define PANEL_REVISION 10

// Turn the picture upside down (if the board is mounted with USB on the other side).
#define PANEL_FLIP_180 0

// Swap black and white in what is sent to the panel. Only needed if the
// screen comes out as a negative on your board.
#define PANEL_INVERT 0

// BART station code (19TH = 19th St Oakland).
static const char *const STATION = "19TH";
static const char *const STATION_LABEL = "19th St BART";

// One row per direction: the label on screen and the destination codes that count.
static const TrainRowConfig TRAIN_ROWS[3] = {
    {"Richmond", {"RICH"}},
    {"SFO / Millbrae", {"SFIA", "MLBR"}},
    {"Berryessa", {"BERY"}},
};

// Weather locations.
static const CityConfig CITIES[2] = {
    {"Oakland", 37.8044, -122.2712},
    {"San Francisco", 37.7749, -122.4194},
};

// Seconds each screen stays up.
static const uint32_t SCREEN_SECONDS = 15;

// How old data may get before it is fetched again (seconds).
static const uint32_t TRAINS_MAX_AGE = 30;
static const uint32_t WEATHER_MAX_AGE = 15 * 60;

// Train data older than this shows "updated N min ago"; older than
// TRAINS_GIVE_UP the screen says it has none instead of showing stale trains.
static const uint32_t TRAINS_STALE = 2 * 60;
static const uint32_t TRAINS_GIVE_UP = 10 * 60;

// Quiet hours (local time, 24 h clock): the screen holds the card of the day,
// Wi-Fi is switched off and nothing is fetched.
static const int QUIET_START = 23;
static const int QUIET_END = 6;

// A full refresh (with the e-ink flash) every this many screen changes.
static const int FULL_REFRESH_EVERY = 40;

// Pacific time, with US daylight-saving rules.
static const char *const TIME_ZONE = "PST8PDT,M3.2.0,M11.1.0";
