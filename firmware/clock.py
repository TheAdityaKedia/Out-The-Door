# Pacific time and calendar helpers.
# MicroPython has no time zones, and its epoch differs between ports, so
# everything here works from the UTC tuple that time.gmtime() returns and
# does its own date arithmetic.
import time

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def days_from_civil(y, m, d):
    # Days since 1970-01-01 for a proleptic Gregorian date (Howard Hinnant).
    y -= m <= 2
    era = (y if y >= 0 else y - 399) // 400
    yoe = y - era * 400
    doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def civil_from_days(z):
    z += 719468
    era = (z if z >= 0 else z - 146096) // 146097
    doe = z - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    y = yoe + era * 400
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    d = doy - (153 * mp + 2) // 5 + 1
    m = mp + (3 if mp < 10 else -9)
    return y + (m <= 2), m, d


def weekday(days):
    # 0 = Monday, for a day count from days_from_civil (1970-01-01 was a Thursday).
    return (days + 3) % 7


def _nth_sunday(y, m, n):
    first = days_from_civil(y, m, 1)
    return first + (6 - weekday(first)) % 7 + 7 * (n - 1)


def _is_dst(y, mo, d, h):
    # US rules: 2 am local on the second Sunday of March (10:00 UTC)
    # to 2 am local on the first Sunday of November (09:00 UTC).
    hours = days_from_civil(y, mo, d) * 24 + h
    start = _nth_sunday(y, 3, 2) * 24 + 10
    end = _nth_sunday(y, 11, 1) * 24 + 9
    return start <= hours < end


class Local:
    # A Pacific-time moment: year, month, day, hour, minute, second, plus
    # `days` (day count of the local date) and `utc_days` (fractional UTC days).
    def __init__(self, utc=None):
        t = time.gmtime() if utc is None else utc
        y, mo, d, h, mi, s = t[0], t[1], t[2], t[3], t[4], t[5]
        self.utc_days = days_from_civil(y, mo, d) + (h + mi / 60 + s / 3600) / 24
        offset = -7 if _is_dst(y, mo, d, h) else -8
        local_minutes = days_from_civil(y, mo, d) * 1440 + (h + offset) * 60 + mi
        self.days = local_minutes // 1440
        self.year, self.month, self.day = civil_from_days(self.days)
        self.hour = (local_minutes % 1440) // 60
        self.minute = local_minutes % 60
        self.second = s

    def hm(self):
        h = self.hour % 12 or 12
        return "%d:%02d%s" % (h, self.minute, "a" if self.hour < 12 else "p")

    def month_day(self):
        return "%s %d" % (MONTHS[self.month - 1], self.day)

    def day_month_day(self):
        return "%s %s" % (DAYS[weekday(self.days)], self.month_day())


def date_label(days):
    y, m, d = civil_from_days(days)
    return "%s %s %d" % (DAYS[weekday(days)], MONTHS[m - 1], d)
