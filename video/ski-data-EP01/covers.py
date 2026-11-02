"""4 covers: 9x16, 3x4, 16x9, 4x3. python3 covers.py OUT_PREFIX"""
import math, sys
import numpy as np
import cairo
from PIL import Image
from common import text, BG, INK, DIM, GOLD, ICE, RED, FAINT, rounded_rect
from art import skier_front, KNEE_PEAK, TERRAIN, RIM

SIZES = {"竖版9x16": (1080, 1920), "竖版3x4": (1080, 1440), "横版16x9": (1920, 1080), "横版4x3": (1440, 1080)}


def cover(w, h, path):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s)
    c.set_source_rgb(*BG); c.paint()
    portrait = h > w
    gy = h * (0.80 if portrait else 0.90)
    c.rectangle(0, gy, w, h - gy); c.set_source_rgb(*TERRAIN); c.fill()
    c.set_source_rgba(*RIM, 0.9); c.rectangle(0, gy - 1.5, w, 3); c.fill()
    fs = w / (11.5 if portrait else 19.0)
    tx = w / 2 if portrait else w * (0.31 if w / h > 1.5 else 0.30)
    ty = h * (0.09 if portrait else 0.16)
    stat_bottom = ty + fs * (4.4 + 1.6)
    sc = (gy - stat_bottom - h * 0.03) / 1.9 if portrait else h * 0.36
    fx = w * (0.5 if portrait else (0.74 if w / h > 1.5 else 0.80))
    skier_front(c, fx - sc * 0.2, gy, sc, lean=math.radians(13), valgus=1.0, out_edge=math.radians(40), in_edge=math.radians(25),
                out_slide=0.25, knee_mark=1.0)
    text(c, "双板 · 用数据说话", tx, ty, fs * 0.38, DIM, align="c", spacing=0.3)
    text(c, "双板断十字韧带", tx, ty + fs * 1.3, fs, INK, align="c", bold=True)
    text(c, "的三种方式", tx, ty + fs * 2.5, fs, INK, align="c", bold=True)
    c.set_source_rgba(*GOLD, 0.85); c.rectangle(tx - fs * 1.6, ty + fs * 2.95, fs * 3.2, 3); c.fill()
    # stat
    sy = ty + fs * (4.4 if portrait else 4.6)
    text(c, f"+{KNEE_PEAK - 100:.0f}%", tx, sy + fs * 0.6, fs * 1.25, RED, align="c", bold=True)
    text(c, "严重膝扭伤一度上涨（佛蒙特 34 年追踪）", tx, sy + fs * 1.3, fs * 0.36, DIM, align="c")
    s.flush()
    a = np.ndarray((h, w, 4), np.uint8, s.get_data())[..., [2, 1, 0]].copy()
    Image.fromarray(a).save(path, quality=92)


if __name__ == "__main__":
    pre = sys.argv[1]
    for name, (w, h) in SIZES.items():
        cover(w, h, f"{pre}-{name}.jpg"); print(f"{pre}-{name}.jpg")
