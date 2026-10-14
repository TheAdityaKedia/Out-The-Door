# Moon phase from the date, no network needed.
import math

SYNODIC = 29.530588853
# A known new moon: 2000-01-06 18:14 UTC, as days since 1970-01-01.
NEW_MOON_EPOCH = 10962 + (18 + 14 / 60) / 24

NAMES = ("New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
         "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent")


def age(utc_days):
    return (utc_days - NEW_MOON_EPOCH) % SYNODIC


def illumination(a):
    return (1 - math.cos(2 * math.pi * a / SYNODIC)) / 2


def name(a):
    return NAMES[int(a / SYNODIC * 8 + 0.5) % 8]


def days_to_full(a):
    return (SYNODIC / 2 - a) % SYNODIC
