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
