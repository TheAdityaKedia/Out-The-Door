#include "moon.h"

#include <math.h>

// A known new moon: 2000-01-06 18:14 UTC, as days since 1970-01-01.
static const double NEW_MOON_EPOCH = 10962 + (18 + 14 / 60.0) / 24;

static const char *const NAMES[] = {"New Moon",     "Waxing Crescent", "First Quarter",
                                    "Waxing Gibbous", "Full Moon",     "Waning Gibbous",
                                    "Last Quarter", "Waning Crescent"};

double moonAge(double utcDays) {
  double a = fmod(utcDays - NEW_MOON_EPOCH, SYNODIC_MONTH);
  return a < 0 ? a + SYNODIC_MONTH : a;
}

double moonIllumination(double age) { return (1 - cos(2 * M_PI * age / SYNODIC_MONTH)) / 2; }

const char *moonPhaseName(double age) {
  return NAMES[(int)(age / SYNODIC_MONTH * 8 + 0.5) % 8];
}

double daysUntilFull(double age) {
  double d = fmod(SYNODIC_MONTH / 2 - age, SYNODIC_MONTH);
  return d < 0 ? d + SYNODIC_MONTH : d;
}

// The usual sunrise equation (about a minute's accuracy at these latitudes).
bool sunTimes(long localDays, double lat, double lon, long *rise, long *set) {
  const double rad = M_PI / 180;
  const double jStar = (localDays - 10957) - lon / 360;  // days since 2000-01-01 12:00 UTC, near local noon
  const double m = fmod(357.5291 + 0.98560028 * jStar, 360);
  const double c = 1.9148 * sin(m * rad) + 0.02 * sin(2 * m * rad) + 0.0003 * sin(3 * m * rad);
  const double l = fmod(m + c + 180 + 102.9372, 360);
  const double transit = jStar + 0.0053 * sin(m * rad) - 0.0069 * sin(2 * l * rad);
  const double sinDec = sin(l * rad) * sin(23.4397 * rad), cosDec = cos(asin(sinDec));
  const double cosW = (sin(-0.833 * rad) - sin(lat * rad) * sinDec) / (cos(lat * rad) * cosDec);
  if (cosW < -1 || cosW > 1) return false;
  const double half = acos(cosW) / rad / 360;
  *rise = (long)lround((transit - half + 10957.5) * 86400);
  *set = (long)lround((transit + half + 10957.5) * 86400);
  return true;
}
