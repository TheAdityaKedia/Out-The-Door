# The e-paper panel: wraps Waveshare's driver (V3 or V4 board) and decides
# between partial refreshes and the occasional full one.
import framebuf

import gfx


class Display:
    def __init__(self, version, y_offset, full_every):
        if version == 3:
            from lib.epd_v3 import EPD_2in13_V3_Landscape as EPD
        else:
            from lib.epd_v4 import EPD_2in13_V4_Landscape as EPD
        self.epd = EPD()  # runs the panel's init
        self._partial = getattr(self.epd, "displayPartial", None) or self.epd.display_Partial
        # Screens draw into this 250x122 canvas; it is copied into the driver's
        # 250x128 buffer at y_offset so the visible rows line up.
        self.fb = framebuf.FrameBuffer(bytearray(gfx.W * 16), gfx.W, gfx.H, framebuf.MONO_VLSB)
        self.y_offset = y_offset
        self.full_every = full_every
        self.changes = 0
        self.asleep = False

    def canvas(self):
        self.fb.fill(gfx.WHITE)
        return self.fb

    def show(self, full=False):
        if self.asleep:
            self.epd.init()
            self.asleep = False
            full = True
        self.epd.fill(gfx.WHITE)
        self.epd.blit(self.fb, 0, self.y_offset)
        if full or self.changes % self.full_every == 0:
            self.epd.init()
            # Display_Base writes both RAM banks, so later partial refreshes
            # have the right "previous" image to diff against.
            self.epd.Display_Base(self.epd.buffer)
        else:
            self._partial(self.epd.buffer)
        self.changes += 1

    def sleep(self):
        if not self.asleep:
            self.epd.sleep()
            self.asleep = True
