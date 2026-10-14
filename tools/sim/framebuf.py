"""A pure-Python stand-in for MicroPython's framebuf module.

It covers the calls the firmware makes, with the same buffer layouts, so the
screen code can run unchanged on a laptop for tools/preview.py.
"""

MONO_VLSB = 0
MONO_HLSB = 3


class FrameBuffer:
    def __init__(self, buf, width, height, fmt, stride=None):
        self.buf, self.width, self.height, self.fmt = buf, width, height, fmt
        self.stride = stride or width

    # ---- pixel access in the real layouts
    def _get(self, x, y):
        if self.fmt == MONO_VLSB:
            return (self.buf[(y >> 3) * self.stride + x] >> (y & 7)) & 1
        i = (y * ((self.stride + 7) // 8)) + (x >> 3)
        return (self.buf[i] >> (7 - (x & 7))) & 1

    def _set(self, x, y, c):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        if self.fmt == MONO_VLSB:
            i, bit = (y >> 3) * self.stride + x, 1 << (y & 7)
        else:
            i, bit = y * ((self.stride + 7) // 8) + (x >> 3), 0x80 >> (x & 7)
        if c:
            self.buf[i] |= bit
        else:
            self.buf[i] &= ~bit & 0xFF

    def pixel(self, x, y, c=None):
        if c is None:
            if 0 <= x < self.width and 0 <= y < self.height:
                return self._get(x, y)
            return None
        self._set(x, y, c)

    def fill(self, c):
        for i in range(len(self.buf)):
            self.buf[i] = 0xFF if c else 0

    def fill_rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.height, y + h)):
            for xx in range(max(0, x), min(self.width, x + w)):
                self._set(xx, yy, c)

    def hline(self, x, y, w, c):
        self.fill_rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill_rect(x, y, 1, h, c)

    def rect(self, x, y, w, h, c, f=False):
        if f:
            return self.fill_rect(x, y, w, h, c)
        self.hline(x, y, w, c)
        self.hline(x, y + h - 1, w, c)
        self.vline(x, y, h, c)
        self.vline(x + w - 1, y, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self._set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def ellipse(self, cx, cy, xr, yr, c, f=False, m=15):
        for y in range(-yr, yr + 1):
            for x in range(-xr, xr + 1):
                v = (x * x) / max(xr * xr, 1) + (y * y) / max(yr * yr, 1)
                if f:
                    if v <= 1.0 + 0.5 / max(xr, yr):
                        self._set(cx + x, cy + y, c)
                else:
                    inner_x, inner_y = max(xr - 1, 0), max(yr - 1, 0)
                    vi = (x * x) / max(inner_x * inner_x, 1) + (y * y) / max(inner_y * inner_y, 1)
                    if v <= 1.0 + 0.5 / max(xr, yr) and (vi > 1.0 + 0.5 / max(xr, yr) or xr <= 1):
                        self._set(cx + x, cy + y, c)

    def poly(self, x, y, coords, c, f=False):
        pts = [(coords[i] + x, coords[i + 1] + y) for i in range(0, len(coords), 2)]
        n = len(pts)
        for i in range(n):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
            self.line(x0, y0, x1, y1, c)
        if not f:
            return
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(n):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    xs.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for xx in range(int(round(a)), int(round(b)) + 1):
                    self._set(xx, yy, c)

    def blit(self, src, x, y, key=-1, palette=None):
        # Same rule as MicroPython: map through the palette, then skip `key`.
        for sy in range(src.height):
            for sx in range(src.width):
                col = src._get(sx, sy)
                if palette is not None:
                    col = palette._get(col, 0)
                if col != key:
                    self._set(x + sx, y + sy, col)

    def text(self, s, x, y, c=1):
        pass
