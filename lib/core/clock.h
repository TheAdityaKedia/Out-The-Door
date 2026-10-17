// Turning a Unix time into a Pacific-time Now. Uses the C library's time zone
// support, so call setenv("TZ", ...) and tzset() (or configTzTime) first.
#pragma once
#include <time.h>
#include "types.h"

Now makeNow(time_t t);
// Time of day like "7:42a".
void formatTime(const Now &n, char *out, int size);
// "Oct 14" and "Wed Oct 14".
void formatMonthDay(const Now &n, char *out, int size);
void formatDayMonthDay(const Now &n, char *out, int size);
