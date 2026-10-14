"""Checks for the parts that don't need hardware:  python3 tools/test_logic.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "sim"), os.path.join(HERE, "..", "firmware")]

import clock  # noqa: E402
import config  # noqa: E402
from sources import bart, moon, weather  # noqa: E402


def local(*utc):
    return clock.Local(utc + (0,) * (6 - len(utc)))


# Pacific time, both sides of each daylight-saving change in 2026
# (starts Sun Mar 8 at 10:00 UTC, ends Sun Nov 1 at 09:00 UTC).
assert local(2026, 3, 8, 9, 59).hm() == "1:59a"
assert local(2026, 3, 8, 10, 0).hm() == "3:00a"
assert local(2026, 11, 1, 8, 59).hm() == "1:59a"
assert local(2026, 11, 1, 9, 0).hm() == "1:00a"
n = local(2026, 10, 15, 3, 30)  # 8:30 pm the evening before, local
assert (n.month, n.day, n.hm()) == (10, 14, "8:30p"), (n.month, n.day, n.hm())
assert n.day_month_day() == "Wed Oct 14"
assert local(2026, 10, 14, 19, 5).hm() == "12:05p"
assert local(2026, 10, 14, 7, 0).hm() == "12:00a"
for z in (-1000, 0, 20375, 40000):
    assert clock.days_from_civil(*clock.civil_from_days(z)) == z

# BART: rows group destinations, "Leaving" and cancelled trains drop out.
with open(os.path.join(HERE, "fixtures", "bart_19th.json")) as f:
    rows = bart.parse(json.load(f), config.TRAIN_ROWS)
assert rows == [[9, 14], [5, 10, 20], [7, 22]], rows
assert bart.adjusted(rows, 125) == [[7, 12], [3, 8], [5, 20]]
assert bart.adjusted(rows, 6 * 60) == [[3, 8], [4, 14], [1, 16]]
assert bart.parse({"root": {"station": [{"abbr": "19TH"}]}}, config.TRAIN_ROWS) == [[], [], []]

# Weather
with open(os.path.join(HERE, "fixtures", "weather.json")) as f:
    w = weather.parse(json.load(f))
assert w[0] == {"temp": 75, "high": 78, "low": 58, "icon": "sun", "label": "Sunny"}, w[0]
assert w[1]["icon"] == "fog"

# Moon: the October 2026 full moon falls late on Oct 25, Pacific time.
a = moon.age(clock.days_from_civil(2026, 10, 26) + 4.2 / 24)
assert moon.name(a) == "Full Moon" and moon.illumination(a) > 0.99, (a, moon.illumination(a))

print("all checks passed")
