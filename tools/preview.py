"""Render the screens to PNG on a laptop, using the firmware's own drawing code.

    python3 tools/preview.py          # sample data from tools/fixtures/
    python3 tools/preview.py --live   # real BART and Open-Meteo data, current time

Writes previews/*.png (actual size and a 4x "e-ink" view) and previews/all_screens.png.
Needs Pillow.
"""
import json
import os
import runpy
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FW = os.path.join(ROOT, "firmware")
sys.path[:0] = [os.path.join(HERE, "sim"), FW]

import framebuf  # noqa: E402  (the simulator)
from PIL import Image  # noqa: E402

import clock  # noqa: E402
import config  # noqa: E402
import gfx  # noqa: E402
from screens import moon as moon_screen  # noqa: E402
from screens import oblique as oblique_screen  # noqa: E402
from screens import trains as trains_screen  # noqa: E402
from screens import weather as weather_screen  # noqa: E402
from sources import bart, oblique, weather  # noqa: E402

OUT = os.path.join(ROOT, "previews")


def canvas():
    fb = framebuf.FrameBuffer(bytearray(gfx.W * 16), gfx.W, gfx.H, framebuf.MONO_VLSB)
    fb.fill(gfx.WHITE)
    return fb


def to_image(fb):
    im = Image.new("1", (gfx.W, gfx.H), 1)
    px = im.load()
    for y in range(gfx.H):
        for x in range(gfx.W):
            px[x, y] = fb.pixel(x, y)
    return im


def eink(im, scale=4):
    big = im.convert("L").resize((gfx.W * scale, gfx.H * scale), Image.NEAREST)
    big = big.point(lambda v: 232 if v > 128 else 34)
    pad = 6 * scale
    framed = Image.new("L", (big.width + 2 * pad, big.height + 2 * pad), 60)
    framed.paste(big, (pad, pad))
    return framed


def fetch(url):
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.load(r)


def main():
    live = "--live" in sys.argv
    if live:
        now = clock.Local()
        path = os.path.join(FW, "secrets.py")
        if not os.path.exists(path):
            path = os.path.join(FW, "secrets_example.py")
        key = runpy.run_path(path)["BART_KEY"]
        bart_json = fetch(bart.url(config.STATION, key))
        weather_json = fetch(weather.url(config.CITIES))
    else:
        now = clock.Local((2026, 10, 14, 14, 42, 0))  # 7:42 am PDT
        with open(os.path.join(HERE, "fixtures", "bart_19th.json")) as f:
            bart_json = json.load(f)
        with open(os.path.join(HERE, "fixtures", "weather.json")) as f:
            weather_json = json.load(f)

    minutes = bart.parse(bart_json, config.TRAIN_ROWS)
    cities = weather.parse(weather_json)
    card = oblique.card_for(now.days, os.path.join(FW, "cards.txt"))

    shots = []

    def shot(name, draw):
        fb = canvas()
        draw(fb)
        im = to_image(fb)
        im.save(os.path.join(OUT, name + ".png"))
        eink(im).save(os.path.join(OUT, name + "_4x.png"))
        shots.append(im)

    os.makedirs(OUT, exist_ok=True)
    shot("1_trains", lambda fb: trains_screen.draw(fb, now, config, bart.adjusted(minutes, 0), 0))
    shot("2_weather", lambda fb: weather_screen.draw(fb, now, config, cities))
    shot("3_oblique", lambda fb: oblique_screen.draw(fb, now, card))
    shot("4_moon", lambda fb: moon_screen.draw(fb, now, config))
    if not live:
        # States worth eyeballing: stale trains, no data, a long card, quiet hours.
        shot("5_trains_stale", lambda fb: trains_screen.draw(
            fb, now, config, bart.adjusted(minutes, 4 * 60), 4 * 60))
        shot("6_trains_none", lambda fb: trains_screen.draw(fb, now, config, None, 0))
        shot("7_oblique_long", lambda fb: oblique_screen.draw(
            fb, now, "Be the first not to do what has never not been done before"))
        shot("8_quiet", lambda fb: oblique_screen.draw(fb, now, card, page=None))

    tiles = [eink(im, 3) for im in shots]
    gap = 24
    sheet = Image.new("L", (tiles[0].width + 2 * gap, sum(t.height + gap for t in tiles) + gap), 255)
    y = gap
    for t in tiles:
        sheet.paste(t, (gap, y))
        y += t.height + gap
    sheet.save(os.path.join(OUT, "all_screens.png"))
    print("wrote %d screens to previews/" % len(shots))


if __name__ == "__main__":
    main()
