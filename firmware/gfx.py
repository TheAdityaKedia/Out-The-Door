# Drawing helpers shared by the screens: text in our bitmap fonts, the header
# bar, page dots and weather icons. Everything draws onto a 250x122 framebuf.
import math
from array import array

import framebuf

W, H = 250, 122
BLACK, WHITE = 0, 1

_glyph_cache = {}
_palette = framebuf.FrameBuffer(bytearray(1), 2, 1, framebuf.MONO_HLSB)


def _glyph(font, ch):
    key = (id(font), ch)
    g = _glyph_cache.get(key)
    if g is None:
        w, data = font.GLYPHS.get(ch) or font.GLYPHS["?"]
        g = (w, framebuf.FrameBuffer(bytearray(data), w, font.HEIGHT, framebuf.MONO_HLSB))
        _glyph_cache[key] = g
    return g


def width(s, font):
    return sum((font.GLYPHS.get(ch) or font.GLYPHS["?"])[0] for ch in s)


def text(fb, s, x, y, font, color=BLACK):
    # Draws s with its top-left at (x, y); only ink pixels are touched.
    _palette.pixel(0, 0, 1 - color)
    _palette.pixel(1, 0, color)
    x = int(x)
    for ch in s:
        w, g = _glyph(font, ch)
        fb.blit(g, x, int(y), 1 - color, _palette)
        x += w
    return x


def text_right(fb, s, right, y, font, color=BLACK):
    text(fb, s, right - width(s, font), y, font, color)


def text_center(fb, s, cx, y, font, color=BLACK):
    text(fb, s, cx - width(s, font) // 2, y, font, color)


def wrap(s, font, max_w):
    words, lines, line = s.split(), [], ""
    for word in words:
        trial = word if not line else line + " " + word
        if width(trial, font) <= max_w:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def header(fb, left, right, font):
    fb.fill_rect(0, 0, W, 16, BLACK)
    text(fb, left, 4, 1, font, WHITE)
    text_right(fb, right, W - 4, 1, font, WHITE)


def dots(fb, index, count=4):
    for k in range(count):
        x = W // 2 - 18 + k * 12
        fb.ellipse(x, H - 5, 2, 2, BLACK, k == index)


def dotted_rule(fb, x0, x1, y):
    for x in range(x0, x1, 2):
        fb.pixel(x, y, BLACK)


def thick_line(fb, x0, y0, x1, y1):
    fb.line(x0, y0, x1, y1, BLACK)
    fb.line(x0 + 1, y0, x1 + 1, y1, BLACK)
    fb.line(x0, y0 + 1, x1, y1 + 1, BLACK)


# ---- weather icons, each drawn centred on (cx, cy), about 32 px across

def _sun(fb, cx, cy, r=9):
    fb.ellipse(cx, cy, r, r, BLACK, True)
    for k in range(8):
        a = k * math.pi / 4
        c, s = math.cos(a), math.sin(a)
        thick_line(fb, int(cx + (r + 3) * c), int(cy + (r + 3) * s),
                   int(cx + (r + 7) * c), int(cy + (r + 7) * s))


def _cloud(fb, cx, cy):
    fb.ellipse(cx - 8, cy, 6, 6, BLACK, True)
    fb.ellipse(cx + 2, cy - 4, 8, 8, BLACK, True)
    fb.ellipse(cx + 10, cy + 1, 5, 5, BLACK, True)
    fb.fill_rect(cx - 8, cy, 18, 7, BLACK)


def _moon(fb, cx, cy):
    fb.ellipse(cx, cy, 10, 10, BLACK, True)
    fb.ellipse(cx + 6, cy - 4, 9, 9, WHITE, True)


def icon(fb, kind, cx, cy):
    if kind == "sun":
        _sun(fb, cx, cy)
    elif kind == "moon":
        _moon(fb, cx, cy)
    elif kind == "partly":
        _sun(fb, cx + 5, cy - 6, 7)
        fb.fill_rect(cx - 16, cy - 2, 30, 14, WHITE)
        _cloud(fb, cx - 2, cy + 4)
    elif kind == "fog":
        _cloud(fb, cx, cy - 4)
        for j, (a, b) in enumerate(((-16, 10), (-10, 16), (-16, 8))):
            fb.fill_rect(cx + a, cy + 7 + j * 4, b - a, 2, BLACK)
    elif kind == "rain":
        _cloud(fb, cx, cy - 4)
        for dx in (-8, 0, 8):
            thick_line(fb, cx + dx, cy + 7, cx + dx - 3, cy + 14)
    elif kind == "snow":
        _cloud(fb, cx, cy - 4)
        for dx, dy in ((-8, 9), (0, 13), (8, 9)):
            fb.fill_rect(cx + dx - 1, cy + dy - 1, 3, 3, BLACK)
    elif kind == "storm":
        _cloud(fb, cx, cy - 4)
        bolt = array("h", (2, 4, -4, 12, 0, 12, -3, 19, 5, 9, 1, 9))
        fb.fill_rect(cx - 5, cy + 3, 11, 4, WHITE)
        fb.poly(cx, cy, bolt, BLACK, True)
    else:
        _cloud(fb, cx, cy)
