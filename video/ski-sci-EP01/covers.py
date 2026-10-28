"""4 covers: 9x16, 3x4, 16x9, 4x3. python3 covers.py OUT_PREFIX"""
import sys
import numpy as np
import cairo
from PIL import Image
from common import text, BG, INK, DIM, GOLD, ICE, RED
from art import Grains, DT_SKIER

SIZES = {"竖版9x16": (1080, 1920), "竖版3x4": (1080, 1440), "横版16x9": (1920, 1080), "横版4x3": (1440, 1080)}
GR = Grains(width=3000, seed=11)


def cover(w, h, path):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s)
    c.set_source_rgb(*BG); c.paint()
    portrait = h > w
    sc = 1.25 if portrait else 1.0
    oy = h * (0.42 if portrait and h / w > 1.5 else 0.40 if portrait else 0.56)
    c.save(); c.translate(0, oy); c.scale(sc, sc)
    GR.draw(c, 0, 0, 300, heat=1.0, film=1.0, t=0.0, alpha=1.0, x0=0, x1=w / sc + 10)
    c.restore()
    fs = w / (9.6 if portrait else 15.0)
    ty = h * 0.08
    text(c, "滑雪里的物理", w / 2, ty, fs * 0.36, DIM, align="c", spacing=0.3)
    text(c, "雪板为什么能滑？", w / 2, ty + fs * 1.3, fs, INK, align="c", bold=True)
    c.set_source_rgba(*GOLD, 0.85); c.rectangle(w / 2 - fs * 1.6, ty + fs * 1.75, fs * 3.2, 3); c.fill()
    text(c, "不是因为把雪压化了", w / 2, ty + fs * 2.45, fs * 0.46, GOLD, align="c")
    # bottom stat on a dark band
    band_y = h * (0.74 if portrait else 0.86)
    g = cairo.LinearGradient(0, band_y - h * 0.06, 0, h)
    g.add_color_stop_rgba(0, *BG, 0); g.add_color_stop_rgba(0.35, *BG, 0.92); g.add_color_stop_rgba(1, *BG, 1)
    c.rectangle(0, band_y - h * 0.06, w, h); c.set_source(g); c.fill()
    if portrait:
        y0 = h * 0.80
        text(c, "人站在雪板上，熔点只降低", w / 2, y0, w * 0.045, DIM, align="c", bold=True)
        text(c, f"{abs(DT_SKIER):.5f} °C", w / 2, y0 + w * 0.15, w * 0.12, RED, align="c", bold=True)
    else:
        text(c, f"压力只让熔点降低 {abs(DT_SKIER):.5f} °C", w / 2, h * 0.93, fs * 0.42, RED, align="c", bold=True)
    s.flush()
    a = np.ndarray((h, w, 4), np.uint8, s.get_data())[..., [2, 1, 0]].copy()
    Image.fromarray(a).save(path, quality=92)


if __name__ == "__main__":
    pre = sys.argv[1]
    for name, (w, h) in SIZES.items():
        cover(w, h, f"{pre}-{name}.jpg"); print(f"{pre}-{name}.jpg")
