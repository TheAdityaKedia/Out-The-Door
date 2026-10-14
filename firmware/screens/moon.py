import math

import clock
import gfx
from fonts import bold12, bold14, bold18, sans11
from sources import moon

CX, CY, R = 40, 64, 32


def _disc(fb, age):
    # Lit side white, dark side a checker dither, like the mockup.
    phase = age / moon.SYNODIC
    k = math.cos(2 * math.pi * phase)
    rr = R * R
    edge = (R - 1) * (R - 1)
    for y in range(-R, R + 1):
        w = math.sqrt(rr - y * y)
        t = k * w
        for x in range(-int(w), int(w) + 1):
            d = x * x + y * y
            if d > rr:
                continue
            lit = (x > t) if phase < 0.5 else (x < -t)
            if not lit and ((x + y) % 2 == 0 or d > edge):
                fb.pixel(CX + x, CY + y, gfx.BLACK)
    fb.ellipse(CX, CY, R, R, gfx.BLACK)


def draw(fb, now, cfg):
    gfx.header(fb, "Moon", now.month_day(), bold12)
    age = moon.age(now.utc_days)
    _disc(fb, age)
    words = moon.name(age).split()
    tx = 84
    gfx.text(fb, words[0], tx, 22, bold18)
    gfx.text(fb, words[1], tx, 42, bold18)
    gfx.text(fb, "%d%% lit" % round(moon.illumination(age) * 100), tx, 66, bold14)
    if words[0] == "Full":
        ahead, what = (moon.SYNODIC - age) % moon.SYNODIC, "New moon"
    else:
        ahead, what = moon.days_to_full(age), "Full moon"
    # Local date of that moment (offset from now's local day by whole days).
    local_frac = (now.hour + now.minute / 60) / 24
    gfx.text(fb, "%s %s" % (what, clock.date_label(now.days + int(local_frac + ahead))), tx, 86, sans11)
    gfx.dots(fb, 3)
