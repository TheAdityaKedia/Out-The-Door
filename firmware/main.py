# out-the-door: rotates BART departures, weather, an Oblique Strategies card
# and the moon phase on a 2.13" e-paper display. Runs at boot on the Pico.
import gc
import time

import machine

import clock
import config
import gfx
import net
import secrets
from display import Display
from fonts import bold14, sans11
from screens import moon as moon_screen
from screens import oblique as oblique_screen
from screens import trains as trains_screen
from screens import weather as weather_screen
from sources import bart, oblique, weather

PAGES = 4


class Data:
    def __init__(self):
        self.trains = None  # per-row minutes as of trains_at
        self.trains_at = None  # ticks_ms of the last good BART fetch
        self.weather = None
        self.weather_at = None
        self.clock_at = None


def age_s(at):
    return None if at is None else time.ticks_diff(time.ticks_ms(), at) // 1000


def stale(at, max_age):
    a = age_s(at)
    return a is None or a >= max_age


def fetch_trains(d):
    if not net.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD):
        return
    try:
        raw = net.get_json(bart.url(config.STATION, secrets.BART_KEY))
        d.trains = bart.parse(raw, config.TRAIN_ROWS)
        d.trains_at = time.ticks_ms()
    except Exception as e:
        print("bart:", e)
    gc.collect()


def fetch_weather(d):
    if not net.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD):
        return
    try:
        d.weather = weather.parse(net.get_json(weather.url(config.CITIES)))
        d.weather_at = time.ticks_ms()
    except Exception as e:
        print("weather:", e)
    gc.collect()


def keep_clock(d):
    if stale(d.clock_at, config.NTP_EVERY) and net.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD):
        if net.sync_clock():
            d.clock_at = time.ticks_ms()


def quiet(now):
    s, e = config.QUIET_START, config.QUIET_END
    return (now.hour >= s or now.hour < e) if s > e else (s <= now.hour < e)


def draw(fb, page, now, d):
    if page == 0:
        a = age_s(d.trains_at)
        mins = None if d.trains is None else bart.adjusted(d.trains, a)
        trains_screen.draw(fb, now, config, mins, a or 0)
    elif page == 1:
        weather_screen.draw(fb, now, config, d.weather)
    elif page == 2:
        oblique_screen.draw(fb, now, oblique.card_for(now.days))
    else:
        moon_screen.draw(fb, now, config)


def splash(disp, line):
    fb = disp.canvas()
    gfx.text_center(fb, "out the door", gfx.W // 2, 40, bold14)
    gfx.text_center(fb, line, gfx.W // 2, 64, sans11)
    disp.show(full=True)


def run():
    disp = Display(config.DISPLAY_VERSION, config.DISPLAY_Y_OFFSET, config.FULL_REFRESH_EVERY)
    d = Data()
    splash(disp, "Connecting to Wi-Fi...")
    keep_clock(d)
    fetch_trains(d)
    fetch_weather(d)

    page = 0
    quiet_day = None  # local day whose quiet-hours card is on screen
    while True:
        now = clock.Local()
        if quiet(now):
            if quiet_day != now.days:
                oblique_screen.draw(disp.canvas(), now, oblique.card_for(now.days), page=None)
                disp.show(full=True)
                disp.sleep()
                quiet_day = now.days
            time.sleep(60)
            continue
        if quiet_day is not None:
            quiet_day = None
            page = 0
            keep_clock(d)
            fetch_trains(d)
            fetch_weather(d)

        start = time.ticks_ms()
        draw(disp.canvas(), page, now, d)
        disp.show()
        page = (page + 1) % PAGES

        # Use the time this screen is up to fetch what the next ones need.
        if page == 0 and stale(d.trains_at, config.TRAINS_MAX_AGE):
            fetch_trains(d)
        if stale(d.weather_at, config.WEATHER_MAX_AGE):
            fetch_weather(d)
        keep_clock(d)

        left = config.SCREEN_SECONDS * 1000 - time.ticks_diff(time.ticks_ms(), start)
        if left > 0:
            time.sleep_ms(left)


try:
    run()
except KeyboardInterrupt:
    print("stopped")
except Exception as e:
    # Anything unexpected: log it, wait a moment, and start over.
    import sys
    sys.print_exception(e)
    time.sleep(10)
    machine.reset()
