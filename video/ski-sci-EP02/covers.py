"""4 covers: 9x16, 3x4, 16x9, 4x3. python3 covers.py OUT_PREFIX"""
import math, sys
import numpy as np
import cairo
from PIL import Image
from common import text, BG, INK, DIM, GOLD, ICE, RED, FAINT, rounded_rect
from view import View, tabletop_pts, rider, decomp, polyline, TERRAIN, TERRAIN2, RIM, fl
import jump as J

SIZES = {"竖版9x16": (1080, 1920), "竖版3x4": (1080, 1440), "横版16x9": (1920, 1080), "横版4x3": (1440, 1080)}


def terrain(c, S, w, h):
    c.move_to(S[0, 0], h + 10)
    for p in S:
        c.line_to(*p)
    c.line_to(S[-1, 0], h + 10); c.close_path()
    g = cairo.LinearGradient(0, S[:, 1].min(), 0, h)
    g.add_color_stop_rgb(0, *TERRAIN); g.add_color_stop_rgb(1, *TERRAIN2)
    c.set_source(g); c.fill()
    polyline(c, S, RIM, 0.95, 4)


def cover(w, h, path):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s)
    c.set_source_rgb(*BG); c.paint()
    portrait = h > w
    bx0, bx1 = w * 0.03, w * 0.97
    by0, by1 = (h * 0.36, h * 0.74) if portrait else (h * 0.47, h * 0.99)
    k = min((bx1 - bx0) / 24.0, (by1 - by0) / 8.6)
    V = View(bx0 + 3.0 * k + ((bx1 - bx0) - 24 * k) / 2, by0 + 1.8 * k, k)
    terrain(c, V.P(tabletop_pts(-10, 40)), w, h)
    v0 = 37 / 3.6; r = fl(v0)
    polyline(c, V.P(J.traj_points(v0, r["T"], 80)), GOLD, 0.9, 3, [9, 8])
    v1 = 45 / 3.6; r1 = fl(v1)
    polyline(c, V.P(J.traj_points(v1, r1["T"], 80)), RED, 0.55, 2.5, [6, 8])
    Xf, Yf = V.p(r1["x"], r1["y"])
    c.arc(Xf, Yf, 9, 0, 2 * math.pi); c.set_source_rgba(*RED, 0.9); c.fill()
    tt = r["T"] * 0.93
    P = J.traj_points(v0, tt, 2)[-1]
    X, Y = V.p(*P)
    rider(c, X, Y - 4, -lerp_ang(r), k * 1.3, 0.55)
    Xl, Yl = V.p(r["x"], r["y"])
    decomp(c, Xl, Yl, r["v"], r["imp"], r["slope"], k / 6.5, 1.0, 1.0, labels=False)
    fs = w / (8.8 if portrait else 15.0)
    nsz = k * 0.62
    if portrait:
        y0 = h * 0.82
        for cx, lab, val, col in ((w * 0.28, "落在坡上", r["efh"], ICE), (w * 0.72, "落在平地", r1["efh"], RED)):
            text(c, lab, cx, y0, w * 0.05, DIM, align="c", bold=True)
            text(c, f"{val:.1f} m", cx, y0 + w * 0.15, w * 0.13, col, align="c", bold=True)
        text(c, "等效下落高度（示意计算）", w / 2, y0 + w * 0.24, w * 0.035, DIM, align="c")
        c.set_source_rgba(*FAINT, 0.9); c.rectangle(w / 2 - 1, y0 - w * 0.04, 2, w * 0.2); c.fill()
    else:
        text(c, f"落在坡上  EFH {r['efh']:.1f} m", *V.p(r["x"] + 1.6, r["y"] + 2.6), nsz, ICE, bold=True)
        xr, yr = V.p(r1["x"] + 1.2, -J.DROP + 1.4)
        text(c, f"落在平地  EFH {r1['efh']:.1f} m", min(xr, w - 30), yr, nsz, RED, bold=True, align="r")
    # title block
    ty = h * (0.08 if portrait else 0.08)
    text(c, "滑雪里的物理", w / 2, ty, fs * 0.36, DIM, align="c", spacing=0.3)
    text(c, "落在坡上，", w / 2, ty + fs * 1.25, fs, INK, align="c", bold=True)
    text(c, "为什么不疼？", w / 2, ty + fs * 2.45, fs, INK, align="c", bold=True)
    c.set_source_rgba(*GOLD, 0.85); c.rectangle(w / 2 - fs * 1.6, ty + fs * 2.85, fs * 3.2, 3); c.fill()
    text(c, "单板跳台落地 · 等效下落高度", w / 2, ty + fs * 3.5, fs * 0.42, GOLD, align="c")
    s.flush()
    a = np.ndarray((h, w, 4), np.uint8, s.get_data())[..., [2, 1, 0]].copy()
    Image.fromarray(a).save(path, quality=92)


def lerp_ang(r):
    return J.TH + (r["slope"] - J.TH) * 0.9


if __name__ == "__main__":
    pre = sys.argv[1]
    for name, (w, h) in SIZES.items():
        cover(w, h, f"{pre}-{name}.jpg"); print(f"{pre}-{name}.jpg")
