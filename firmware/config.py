# Everything you might want to change lives here.

# BART station code (19TH = 19th St Oakland). Codes: https://api.bart.gov/docs/overview/abbrev.aspx
STATION = "19TH"
STATION_LABEL = "19th St BART"

# One row per direction: (label shown on screen, destination codes that count).
TRAIN_ROWS = (
    ("Richmond", ("RICH",)),
    ("SFO / Millbrae", ("SFIA", "MLBR")),
    ("Berryessa", ("BERY",)),
)

# Weather locations: (label, latitude, longitude).
CITIES = (
    ("Oakland", 37.8044, -122.2712),
    ("San Francisco", 37.7749, -122.4194),
)

# Seconds each screen stays up.
SCREEN_SECONDS = 20

# How old data may get before it is fetched again (seconds).
TRAINS_MAX_AGE = 30
WEATHER_MAX_AGE = 15 * 60

# Train data older than this shows an "updated N min ago" note; older than
# TRAINS_GIVE_UP the screen says it has no data instead of showing stale trains.
TRAINS_STALE = 2 * 60
TRAINS_GIVE_UP = 10 * 60

# Quiet hours (local time, 24 h clock): rotation stops, fetching pauses,
# and the screen holds the card of the day.
QUIET_START = 23
QUIET_END = 6

# A full refresh (with the e-ink flash) every this many screen changes;
# the ones in between are partial refreshes.
FULL_REFRESH_EVERY = 10

# Re-sync the clock over NTP this often (seconds).
NTP_EVERY = 6 * 3600

# Display board version printed on its back: 3 or 4.
DISPLAY_VERSION = 4

# Rows the panel hides at the top of the driver's 128-row buffer. The panel is
# 122 rows tall; run tools/hello.py once and adjust if the border is cut off.
DISPLAY_Y_OFFSET = 0
