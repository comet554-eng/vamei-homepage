"""叠字幕和标注，出竖屏成片：python3 composite.py FRAMEDIR OUT.mp4（STILLS="t1 t2" 时只出静帧调版）"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "zero2carve-lib"))
import ep
from vert import *

FR, OUTF = sys.argv[1], sys.argv[2]
PLAN = ep.plan()
h0, h1, hs = ep.SEC["hook"]; w0, w1, ws = ep.SEC["why"]; s0, s1, ss = ep.SEC["steps"]; d0, d1, ds = ep.SEC["drill"]
T_SPIN = next(i for i, (s, _, p) in enumerate(PLAN) if p >= ep.X_SPIN) / FPS


def zoom_fn(t, m, shot, p):
    if t < h1:
        return 1 + 0.10 * ramp(t, T_SPIN - 0.2, T_SPIN + 0.3), (m["bindR"][0], m["bindR"][1])
    return 1.0, (0.5, 0.5)


def board_dir(P):
    (x0, y0), (x1, y1) = P["tail"], P["nose"]
    L = math.hypot(x1 - x0, y1 - y0) or 1
    return (x1 - x0) / L, (y1 - y0) / L


def draw(c, t, P, m, shot, p):
    if t < h1 + 0.3:
        a = window(t, -1, h1, 0.3)
        tag(c, "错误示范", RED, 60, 330, a, icon="x")
        big_title(c, [("单脚蹬行", 0.86), ("板总{r|打转}？", 1.1)], t, 0.1, h1, y=560, size=100)
        spin_arrow(c, *P["bindR"], 110, RED, a * ramp(t, T_SPIN - 0.3, T_SPIN), t)
    if w0 - 0.3 < t < w1 + 0.3:
        a = window(t, w0, w1, 0.3)
        tag(c, "错误：在板尾后面蹬", RED, 60, 330, a, icon="x")
        if p < ep.X_SPIN - 0.3:
            ring(c, *P["ankleL"], 54, RED, a * ramp(t, ws[0][1], ws[0][1] + 0.3), t, label="后脚在板尾后面")
        a2 = window(t, ws[1][1], w1, 0.3)
        if a2 > 0:
            dx, dy = board_dir(P)
            (fx, fy) = P["ankleL"]
            arrow(c, fx, fy, fx + dx * 170, fy + dy * 170, RED, a2 * window(t, ws[1][1], ws[1][1] + 1.6, 0.3))
            spin_arrow(c, *P["bindR"], 100, RED, a2 * ramp(t, ws[1][1] + 1.0, ws[1][1] + 1.4), t, label="绕着前脚转")
    if s0 - 0.3 < t < s1 + 0.3:
        a = window(t, s0, s1, 0.3)
        tag(c, "正确做法", GREEN, 60, 330, a, icon="v")
        big_title(c, [("单脚蹬行 · {w|4 步}", 1.0)], t, s0 + 0.05, ss[0][1] - 0.05, y=600, size=100)
        cur = step_of(t, ss)
        chips(c, ["①前绑后松", "②转向板头", "③前刃侧蹬", "④踩止滑垫"], cur, t, a * ramp(t, ss[0][1] - 0.2, ss[0][1] + 0.2))
        if cur == 0:
            ring(c, *P["bindR"], 56, GREEN, a * ramp(t, ss[0][1] + 0.2, ss[0][1] + 0.5), t, label="前脚绑好", side=1)
            ring(c, *P["ankleL"], 52, ICE, a * ramp(t, ss[0][1] + 1.2, ss[0][1] + 1.5), t, label="后脚解开", side=-1)
        elif cur == 1:
            dx, dy = board_dir(P)
            hx, hy = P["head"]
            a1 = a * ramp(t, ss[1][1] + 0.3, ss[1][1] + 0.7)
            arrow(c, hx, hy - 20, hx + dx * 220, hy - 20 + dy * 220, GOLD, a1)
            stroke_text(c, "看向板头", hx + dx * 120, hy - 90, 46, GOLD, a1)
        elif cur == 2:
            ring(c, *P["ankleL"], 52, GREEN, a * ramp(t, ss[2][1], ss[2][1] + 0.3), t, label="前刃这一侧")
        elif cur == 3:
            ring(c, *P["pad"], 60, GREEN, a * ramp(t, ss[3][1] + 0.6, ss[3][1] + 0.9), t, label="踩止滑垫")
    if d0 - 0.3 < t < d1 + 0.3:
        a = window(t, d0, d1, 0.3)
        tag(c, "怎么练", GOLD, 60, 330, a)
        card(c, 60, 440, W - 120, 200, a)
        stroke_text(c, "平地 · 一只脚绑板", W / 2, 515, 38, DIM, a, stroke=0)
        rich_line(c, spans("蹬 {w|3} 步 → 滑一段"), W / 2, 600, 58, a)
        a2 = window(t, ds[1][1], d1, 0.3)
        if a2 > 0:
            card(c, 60, 670, W - 120, 210, a2, GREEN)
            stroke_text(c, "过关标准", W / 2, 735, 36, GREEN, a2, stroke=0)
            rich_line(c, spans("蹬 {w|20 米}不打转"), W / 2, 800, 48, a2)
            rich_line(c, spans("踩上板滑 {w|2–3 米}"), W / 2, 860, 48, a2)
        a3 = window(t, ds[2][1], d1, 0.3)
        if a3 > 0:
            tag(c, "上魔毯", ICE, 60, 910, a3, size=34)
            tag(c, "排队等缆车", ICE, 270, 910, a3, size=34)


run_episode(ep, FR, OUTF, draw, zoom_fn, next_lines=[("后刃推坡", 1.0), ("学会{w|停下来}", 0.8)])
