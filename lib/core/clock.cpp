#include "clock.h"

#include <stdio.h>

static const char *const DAYS[] = {"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"};
static const char *const MONTHS[] = {"Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};

// Days since 1970-01-01 for a Gregorian date (Howard Hinnant's algorithm).
static long daysFromCivil(int y, int m, int d) {
  y -= m <= 2;
  const long era = (y >= 0 ? y : y - 399) / 400;
  const long yoe = y - era * 400;
  const long doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
  const long doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + doe - 719468;
}

Now makeNow(time_t t) {
  struct tm lt;
  localtime_r(&t, &lt);
  Now n;
  n.year = lt.tm_year + 1900;
  n.month = lt.tm_mon + 1;
  n.day = lt.tm_mday;
  n.hour = lt.tm_hour;
  n.minute = lt.tm_min;
  n.wday = lt.tm_wday;
  n.localDays = daysFromCivil(n.year, n.month, n.day);
  n.utcDays = (double)t / 86400.0;
  n.epoch = (long)t;
  return n;
}

void formatTime(const Now &n, char *out, int size) {
  int h = n.hour % 12;
  snprintf(out, size, "%d:%02d%c", h ? h : 12, n.minute, n.hour < 12 ? 'a' : 'p');
}

void formatMonthDay(const Now &n, char *out, int size) {
  snprintf(out, size, "%s %d", MONTHS[n.month - 1], n.day);
}

void formatDayMonthDay(const Now &n, char *out, int size) {
  snprintf(out, size, "%s %s %d", DAYS[n.wday], MONTHS[n.month - 1], n.day);
}
