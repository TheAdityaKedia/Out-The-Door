// Moon phase from the date, no network needed.
#pragma once

static const double SYNODIC_MONTH = 29.530588853;

double moonAge(double utcDays);          // days since the last new moon
double moonIllumination(double age);     // 0..1
const char *moonPhaseName(double age);   // e.g. "Waxing Crescent"
double daysUntilFull(double age);
