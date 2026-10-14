import gfx
from fonts import bold10, bold12, bold14, bold16, bold26, sans11

ROW_TOP, ROW_H = 18, 32


def draw(fb, now, cfg, minutes, age):
    # minutes: per-row lists of minutes already counted down, or None if we
    # have never fetched. age: seconds since the last good fetch.
    gfx.header(fb, cfg.STATION_LABEL, now.hm(), bold12)
    if minutes is None or age > cfg.TRAINS_GIVE_UP:
        gfx.text_center(fb, "No train times right now", gfx.W // 2, 44, bold14)
        gfx.text_center(fb, "Checking again shortly", gfx.W // 2, 66, sans11)
        gfx.dots(fb, 0)
        return
    for i, (label, _) in enumerate(cfg.TRAIN_ROWS):
        y = ROW_TOP + i * ROW_H
        gfx.text(fb, label, 4, y + 8, bold14)
        mins = minutes[i]
        right = gfx.W - 4
        if len(mins) >= 2:
            second = str(mins[1])
            gfx.text_right(fb, second, right, y + 10, bold16)
            right -= gfx.width(second, bold16) + 6
        if mins:
            gfx.text_right(fb, str(mins[0]), right, y + 1, bold26)
        else:
            gfx.text_right(fb, "--", right, y + 10, bold16)
        if i < len(cfg.TRAIN_ROWS) - 1:
            gfx.dotted_rule(fb, 4, gfx.W - 4, y + ROW_H - 1)
    if age > cfg.TRAINS_STALE:
        gfx.text_center(fb, "updated %d min ago" % (age // 60), gfx.W // 2, gfx.H - 12, bold10)
    else:
        gfx.dots(fb, 0)
