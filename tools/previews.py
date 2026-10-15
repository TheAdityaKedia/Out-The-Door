"""Turn previews/*.pbm (written by tools/host.sh) into PNGs and a contact sheet."""
import glob
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "previews")


def eink(im, scale):
    big = im.convert("L").resize((im.width * scale, im.height * scale), Image.NEAREST)
    big = big.point(lambda v: 232 if v > 128 else 34)  # paper and ink tones
    pad = 6 * scale
    framed = Image.new("L", (big.width + 2 * pad, big.height + 2 * pad), 60)
    framed.paste(big, (pad, pad))
    return framed


tiles = []
for path in sorted(glob.glob(os.path.join(OUT, "*.pbm"))):
    im = Image.open(path)
    name = os.path.splitext(path)[0]
    im.save(name + ".png")
    eink(im, 4).save(name + "_4x.png")
    tiles.append(eink(im, 3))
    os.remove(path)

gap = 24
sheet = Image.new("L", (tiles[0].width + 2 * gap, sum(t.height + gap for t in tiles) + gap), 255)
y = gap
for t in tiles:
    sheet.paste(t, (gap, y))
    y += t.height + gap
sheet.save(os.path.join(OUT, "all_screens.png"))
print("wrote %d previews and previews/all_screens.png" % len(tiles))
