import gfx
from fonts import bold12, bold14, bold17

BOX_TOP, BOX_BOTTOM = 22, gfx.H - 12
# (font, line height, most lines that fit in the card)
SIZES = ((bold17, 21, 3), (bold14, 17, 4), (bold12, 15, 5))


def draw(fb, now, card, page=2):
    gfx.header(fb, "Oblique Strategies", now.month_day(), bold12)
    fb.rect(6, BOX_TOP, gfx.W - 12, BOX_BOTTOM - BOX_TOP + 1, gfx.BLACK)
    for font, lh, most in SIZES:
        lines = gfx.wrap(card, font, gfx.W - 28)
        if len(lines) <= most:
            break
    lines = lines[:most]
    block = (len(lines) - 1) * lh + font.HEIGHT
    y = BOX_TOP + (BOX_BOTTOM - BOX_TOP - block) // 2 + 1
    for line in lines:
        gfx.text_center(fb, line, gfx.W // 2, y, font)
        y += lh
    if page is not None:
        gfx.dots(fb, page)
