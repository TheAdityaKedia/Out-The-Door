// Moon phase and sun times from the date, no network needed.
#pragma once

static const double SYNODIC_MONTH = 29.530588853;

double moonAge(double utcDays);          // days since the last new moon
double moonIllumination(double age);     // 0..1
const char *moonPhaseName(double age);   // e.g. "Waxing Crescent"
double daysUntilFull(double age);

// Today's sunrise and sunset as Unix times for the local date localDays at
// (lat, lon). False when the sun doesn't rise or set that day.
bool sunTimes(long localDays, double lat, double lon, long *rise, long *set);
