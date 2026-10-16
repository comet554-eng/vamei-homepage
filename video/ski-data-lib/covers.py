"""Shared 4-size cover generator for 《双板 · 用数据说话》.
python3 covers.py EPDIR OUT_PREFIX  (EPDIR/scenes.py must define COVER = dict(lines, stat, caption, color, figure))
figure(c) draws into a 1000 x 800 reference box."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.abspath(sys.argv[1]); sys.path.insert(0, HERE); sys.path.insert(0, EP)
import numpy as np
import cairo
from PIL import Image
from common import text, BG, INK, DIM, GOLD
import scenes

SIZES = {"竖版9x16": (1080, 1920), "竖版3x4": (1080, 1440), "横版16x9": (1920, 1080), "横版4x3": (1440, 1080)}
SERIES = getattr(scenes, "SERIES", "双板 · 用数据说话")


def cover(w, h, path, C):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s)
    c.set_source_rgb(*BG); c.paint()
    portrait = h > w
    if portrait:
        box = (0.04 * w, 0.40 * h, 0.96 * w, 0.78 * h)
        tx, ty, fs = w / 2, 0.08 * h, w / 10.5
        sy = 0.86 * h
    else:
        box = (0.50 * w, 0.14 * h, 0.98 * w, 0.92 * h)
        tx, ty, fs = 0.27 * w, 0.16 * h, w / 19.0
        sy = ty + fs * 4.9
    bx0, by0, bx1, by1 = box
    sc = min((bx1 - bx0) / 1000, (by1 - by0) / 800)
    c.save(); c.rectangle(bx0, by0, bx1 - bx0, by1 - by0); c.clip()
    c.translate(bx0 + ((bx1 - bx0) - 1000 * sc) / 2, by0 + ((by1 - by0) - 800 * sc) / 2); c.scale(sc, sc)
    C["figure"](c)
    c.restore()
    text(c, SERIES, tx, ty, fs * 0.36, DIM, align="c", spacing=0.3)
    for i, ln in enumerate(C["lines"]):
        text(c, ln, tx, ty + fs * (1.3 + 1.2 * i), fs, INK, align="c", bold=True)
    yl = ty + fs * (1.3 + 1.2 * (len(C["lines"]) - 1) + 0.45)
    c.set_source_rgba(*GOLD, 0.85); c.rectangle(tx - fs * 1.6, yl, fs * 3.2, 3); c.fill()
    text(c, C["stat"], tx, sy, fs * 1.15, C["color"], align="c", bold=True)
    text(c, C["caption"], tx, sy + fs * 0.75, fs * 0.36, DIM, align="c")
    s.flush()
    a = np.ndarray((h, w, 4), np.uint8, s.get_data())[..., [2, 1, 0]].copy()
    Image.fromarray(a).save(path, quality=92)


if __name__ == "__main__":
    pre = sys.argv[2]
    for name, (w, h) in SIZES.items():
        cover(w, h, f"{pre}-{name}.jpg", scenes.COVER); print(f"{pre}-{name}.jpg")
