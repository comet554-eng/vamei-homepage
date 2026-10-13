"""S5 balance -> one speed per edge angle;  S6 real-world measurements (Reid et al. 2020)."""
import math
import numpy as np
from common import *
from draw import *
import ski

BG2 = (0.02, 0.025, 0.035)
DEG = math.radians


# ------------------------------------------------------------------ S5
S5_DUR = 42.0
S5_SUBS = [
    ("光立起刃还不够，人得{b|站得住}。", 0.8, 4.8),
    ("重力把人往下拉，转弯又把人往{w|弯外}甩；\n两股力合起来，必须正好指向脚下那条刃。", 5.2, 12.6),
    ("滑得太慢，合力落在刃的内侧——人会{r|倒进弯里}。", 13.4, 18.8),
    ("滑得太快，合力落到外侧——人会被{r|甩出去}。", 19.6, 24.8),
    ("所以在平地上，每个立刃角，只配一个速度。", 25.6, 30.4),
    ("这块 8 米侧切的板立到 45°，大约要 {w|27 km/h}；\n立得越陡，要滑得越快。", 30.8, 38.4),
    ("（把人简化成一个点，按平地计算）", 38.8, 41.6),
]


def s5_state(t):
    th = DEG(45)
    if t >= 30.0:
        th = DEG(45 + 15 * math.sin(2 * math.pi * (t - 30.0) / 9.0))
    v_ok = ski.ideal_speed(th)
    v = v_ok
    v = lerp(v, 17 / 3.6, ease_io((t - 13.0) / 1.6) * (1 - ease_io((t - 19.2) / 1.4)))
    v = lerp(v, 36 / 3.6, ease_io((t - 19.2) / 1.4) * (1 - ease_io((t - 24.8) / 1.4)))
    return th, v


def draw_balance(c, th, v, alpha=1.0, ex=560.0, ey=660.0, Lpx=360.0):
    R = ski.turn_radius(th)
    c.set_source_rgba(0.78, 0.80, 0.84, alpha); c.rectangle(80, ey, 960, 60); c.fill()
    text(c, "← 弯心", 110, ey + 50, 22, (0.25, 0.28, 0.34), alpha, bold=True)
    bx, by = ex - math.cos(th) * 120, ey + math.sin(th) * 0 - math.sin(th) * 120           # board cross-section
    c.move_to(ex, ey); c.line_to(bx, by); c.set_source_rgba(0.62, 0.48, 0.24, alpha); c.set_line_width(10); c.stroke()
    cx, cy = ex - math.sin(th) * Lpx, ey - math.cos(th) * Lpx           # centre of mass
    c.move_to(ex, ey); c.line_to(cx, cy); c.set_source_rgba(0.85, 0.87, 0.9, 0.85 * alpha); c.set_line_width(5); c.stroke()
    c.arc(cx - math.sin(th) * 70, cy - math.cos(th) * 70, 26, 0, 2 * math.pi); c.set_source_rgba(0.85, 0.87, 0.9, 0.85 * alpha); c.fill()
    c.arc(cx, cy, 11, 0, 2 * math.pi); c.set_source_rgba(1, 1, 1, alpha); c.fill()
    g = 130.0
    f = g * v * v / (ski.G * R)
    glow_line(c, cx, cy, cx, cy + g, (0.9, 0.9, 0.95), 3, alpha, 8); arrow_head(c, cx, cy + g, math.pi / 2, 16, (0.9, 0.9, 0.95), alpha)
    text(c, "重力", cx - 70, cy + g * 0.6, 22, INK, alpha)
    glow_line(c, cx, cy, cx + f, cy, GOLD, 3, alpha, 8); arrow_head(c, cx + f, cy, 0, 16, GOLD, alpha)
    text(c, "被甩向弯外", cx + f + 14, cy + 8, 22, GOLD, alpha)
    # resultant line, extended to the snow
    k = (ey - cy) / g
    hx = cx + f * k
    c.set_dash([10, 8]); c.set_source_rgba(*ICE, 0.9 * alpha); c.set_line_width(2.4)
    c.move_to(cx, cy); c.line_to(hx, ey); c.stroke(); c.set_dash([])
    off = hx - ex
    ok = abs(off) < 8
    c.arc(hx, ey, 9, 0, 2 * math.pi); c.set_source_rgba(*(GOLD if ok else RED), alpha); c.fill()
    c.arc(ex, ey, 5, 0, 2 * math.pi); c.set_source_rgba(1, 1, 1, alpha); c.fill()
    if not ok:
        lab = "合力落在刃内侧 → 倒进弯里" if off < 0 else "合力落在刃外侧 → 被甩出去"
        pill_label(c, lab, ex, ey + 112, 26, RED, alpha * clamp(abs(off) / 30))
    else:
        pill_label(c, "合力正好穿过刃 → 站得住", ex, ey + 112, 26, GOLD, alpha)


def draw_speed_chart(c, th, alpha, x0=1120, y0=250, w=680, h=420):
    if alpha <= 0:
        return
    X = lambda d: x0 + d / 80 * w
    Y = lambda kmh: y0 + h - kmh / 50 * h
    c.set_source_rgba(*FAINT, alpha); c.set_line_width(1.2)
    c.move_to(x0, y0); c.line_to(x0, y0 + h); c.line_to(x0 + w, y0 + h); c.stroke()
    for d in (0, 20, 40, 60, 80):
        text(c, f"{d}°", X(d), y0 + h + 32, 18, DIM, alpha, align="c")
    for k in (10, 20, 30, 40, 50):
        text(c, f"{k}", x0 - 12, Y(k) + 6, 16, FAINT, alpha, align="r")
    text(c, "立刃角", x0 + w, y0 + h + 60, 20, DIM, alpha, align="r")
    text(c, "需要的速度 km/h", x0, y0 - 20, 20, DIM, alpha)
    for R, col, lab in ((ski.R_SL, (0.6, 0.64, 0.7), "回转双板 14 m"), (ski.R_SC, GOLD, "单板 8 m")):
        ds = np.linspace(1, 78, 120)
        vs = [ski.ideal_speed(DEG(d), R) * 3.6 for d in ds]
        c.move_to(X(ds[0]), Y(vs[0]))
        for d, v in zip(ds[1:], vs[1:]):
            c.line_to(X(d), Y(v))
        c.set_source_rgba(*col, alpha); c.set_line_width(2.6 if R == ski.R_SC else 1.6); c.stroke()
        text(c, lab, X(78) + 8, Y(vs[-1]) + 6, 18, col, alpha)
    d = math.degrees(th); v = ski.ideal_speed(th) * 3.6
    c.arc(X(d), Y(v), 9, 0, 2 * math.pi); c.set_source_rgba(1, 1, 1, alpha); c.fill()
    pill_label(c, f"{d:.0f}° → {v:.0f} km/h · 弯半径 {ski.turn_radius(th):.1f} m", X(d), Y(v) - 28, 22, INK, alpha)


def s5(c, t, fi):
    paint_bg(c, BG2)
    th, v = s5_state(t)
    draw_balance(c, th, v, ramp(t, 0.3, 1.2))
    draw_speed_chart(c, th, ramp(t, 25.6, 27.0))
    chapter_tag(c, f"{v * 3.6:.0f} km/h", f"立刃 {math.degrees(th):.0f}° · 弯半径 {ski.turn_radius(th):.1f} m",
                alpha=window(t, 0.6, S5_DUR + 1, 0.5))
    cite_card(c, "arXiv physics/0310086", "平衡：tan(倾角) = v² / (g·R)", "Jentschura · Fahrbach · 平地情形",
              alpha=window(t, 5.4, 12.4, 0.5))
    model_note(c, 1.0, "示意 · 人简化为一个点，平地；v² = g · 侧切半径 · sin(立刃角)")
    for st, a, b in S5_SUBS:
        subtitle(c, st, t, a, b)
    fade_black(c, 1 - ramp(t, 0, 0.8))
    fade_black(c, ramp(t, S5_DUR - 0.5, S5_DUR))
    overlays(c, fi)


# ------------------------------------------------------------------ S6
S6_DUR = 32.0
S6_SUBS = [
    ("真实的雪道上呢？研究者测过高水平运动员的回转赛：", 0.8, 6.6),
    ("立刃最大约 {w|66–71°}，最小转弯半径约 {w|4–5 米}——\n在立刃很大时，和公式对得上。", 7.0, 14.6),
    ("可立刃小的时候，实际的弯比公式{r|大得多}：", 15.2, 19.8),
    ("板在轻微打滑，雪也被压出一道槽，不是坚硬的轨道。", 20.2, 25.4),
    ("所以就算是世界杯选手，转弯时也会扬起一点雪。", 25.8, 31.4),
]


def s6(c, t, fi):
    paint_bg(c, BG2)
    a = ramp(t, 0.4, 1.4)
    x0, y0, w, h = 200, 230, 1000, 500
    X = lambda d: x0 + d / 80 * w
    Y = lambda r: y0 + h - r / 16 * h
    lo = ramp(t, 15.2, 16.6)
    if lo > 0:   # low-edge-angle region: real turns larger (qualitative band)
        c.rectangle(X(0), y0, X(40) - X(0), h); c.set_source_rgba(*RED, 0.10 * lo); c.fill()
        pill_label(c, "立刃小：实际的弯更大（打滑、压槽）", X(20), Y(9), 22, RED, lo)
    hi = ramp(t, 7.0, 8.4)
    if hi > 0:
        c.rectangle(X(66), y0, X(71) - X(66), h); c.set_source_rgba(*GOLD, 0.22 * hi); c.fill()
        c.rectangle(X(0), Y(5), w, Y(4) - Y(5)); c.set_source_rgba(*GOLD, 0.12 * hi); c.fill()
        pill_label(c, "实测：立刃 66–71°，最小半径 4–5 m", X(54), Y(4.5) - 54, 22, GOLD, hi)
    c.set_source_rgba(*FAINT, a); c.set_line_width(1.2)
    c.move_to(x0, y0); c.line_to(x0, y0 + h); c.line_to(x0 + w, y0 + h); c.stroke()
    for d in (0, 20, 40, 60, 80):
        text(c, f"{d}°", X(d), y0 + h + 32, 18, DIM, a, align="c")
    for r in (4, 8, 12, 16):
        text(c, f"{r} m", x0 - 12, Y(r) + 6, 16, FAINT, a, align="r")
    text(c, "立刃角", x0 + w, y0 + h + 60, 20, DIM, a, align="r")
    text(c, "转弯半径", x0, y0 - 20, 20, DIM, a)
    k = ramp(t, 1.6, 4.4)
    ds = np.linspace(0, 80 * k, 200)
    if len(ds) > 1 and k > 0:
        c.move_to(X(ds[0]), Y(ski.R_SL * math.cos(DEG(ds[0]))))
        for d in ds[1:]:
            c.line_to(X(d), Y(ski.R_SL * math.cos(DEG(d))))
        c.set_source_rgba(1, 1, 1, 0.9 * a); c.set_line_width(2.6); c.stroke()
        text(c, "公式：14 m × cos(立刃角)", X(4), Y(14) - 18, 22, INK, a * ramp(t, 3.0, 4.0))
    # right: spray from a top-view carved arc
    if t > 25.6:
        sa = ramp(t, 25.8, 27.0)
        sx, sy = 1560, 520
        c.save(); rounded_rect(c, 1300, 250, 520, 480, 14); c.clip()
        paint_snow(c, oy=300, alpha=sa, x0=1300, y0=250, w=520, h=480)
        th = np.linspace(-0.9, 0.9, 80)
        P = np.stack([sx - 260 + 200 * np.cos(th) * 0 + 160 * np.sin(th) + 100, sy - 40 + 160 * (1 - np.cos(th)) - 80], 1)
        carve_line(c, P, sa, 2.4)
        board_top(c, P[60, 0], P[60, 1], math.atan2(P[61, 1] - P[59, 1], P[61, 0] - P[59, 0]), 60, sa)
        spray(c, P[60, 0], P[60, 1], math.atan2(P[61, 1] - P[59, 1], P[61, 0] - P[59, 0]) + math.pi, 0.35, t, 60, seed=9, alpha=sa)
        c.restore()
    chapter_tag(c, "66–71°", "实测：回转赛最大立刃", alpha=window(t, 0.6, S6_DUR + 1, 0.5))
    cite_card(c, "Front. Sports Act. Living 2 (2020)", "《回转赛中的雪板运动特征》", "Reid · Haugen · Gilgien · Kipp · Smith",
              alpha=window(t, 0.8, 25.4, 0.5))
    for st, a2, b in S6_SUBS:
        subtitle(c, st, t, a2, b)
    fade_black(c, 1 - ramp(t, 0, 0.8))
    fade_black(c, ramp(t, S6_DUR - 0.5, S6_DUR))
    overlays(c, fi)
