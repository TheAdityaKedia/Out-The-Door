import gfx
from fonts import bold12, bold30, sans10


def draw(fb, now, cfg, cities):
    gfx.header(fb, "Weather", now.day_month_day(), bold12)
    half = gfx.W // 2
    fb.vline(half, 20, gfx.H - 32, gfx.BLACK)
    for i, (name, _, _) in enumerate(cfg.CITIES[:2]):
        x0 = i * half
        cx = x0 + half // 2
        gfx.text_center(fb, name, cx, 19, bold12)
        if not cities:
            gfx.text_center(fb, "--", cx, 50, bold30)
            continue
        c = cities[i]
        gfx.icon(fb, c["icon"], x0 + 24, 62)
        gfx.text(fb, "%d°" % c["temp"], x0 + 46, 40, bold30)
        gfx.text_center(fb, c["label"], x0 + 46 + (half - 50) // 2, 76, bold12)
        gfx.text_center(fb, "H %d  L %d" % (c["high"], c["low"]), cx, 96, sans10)
    gfx.dots(fb, 1)
