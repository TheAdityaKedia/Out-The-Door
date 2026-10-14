# Run once on the Pico (after deploying) to check the display:
#   mpremote run tools/hello.py
# You should see a 1-pixel border on all four edges and the text centred.
# If the top or bottom edge is missing, change DISPLAY_Y_OFFSET in config.py
# (try 6) and run this again. If nothing shows at all, check DISPLAY_VERSION.
import config
import gfx
from display import Display
from fonts import bold14, sans11

disp = Display(config.DISPLAY_VERSION, config.DISPLAY_Y_OFFSET, config.FULL_REFRESH_EVERY)
fb = disp.canvas()
fb.rect(0, 0, gfx.W, gfx.H, gfx.BLACK)
gfx.text_center(fb, "Hello from out-the-door", gfx.W // 2, 44, bold14)
gfx.text_center(fb, "board V%d, offset %d" % (config.DISPLAY_VERSION, config.DISPLAY_Y_OFFSET),
                gfx.W // 2, 66, sans11)
disp.show(full=True)
disp.sleep()
print("done")
