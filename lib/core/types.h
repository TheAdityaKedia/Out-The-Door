// Plain data shared by the data sources and the screens.
#pragma once
#include <stdint.h>

struct TrainRowConfig {
  const char *label;
  const char *codes[3];  // destination abbreviations; unused slots are null
};

struct CityConfig {
  const char *label;
  double lat, lon;
};

// Minutes until the next trains on one row, soonest first.
struct TrainRow {
  static const int MAX = 8;
  int minutes[MAX];
  int count;
};

enum class Icon : uint8_t { Sun, Moon, Partly, Cloud, Fog, Rain, Snow, Storm };

struct CityWeather {
  int temp, high, low;
  Icon icon;
  const char *label;
};

// A moment in Pacific time, plus the counters the screens need.
struct Now {
  int year, month, day, hour, minute, wday;  // month 1-12, wday 0 = Sunday
  long localDays;  // days since 1970-01-01 of the local date
  double utcDays;  // fractional days since 1970-01-01 00:00 UTC
  long epoch;      // seconds since 1970-01-01 UTC
};
