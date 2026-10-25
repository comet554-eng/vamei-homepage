"""叠字幕和标注，出竖屏成片：python3 composite.py FRAMEDIR OUT.mp4（STILLS="t1 t2" 时只出静帧调版）"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "zero2carve-lib"))
import ep
from vert import *

FR, OUTF = sys.argv[1], sys.argv[2]
PLAN = ep.plan()
h0, h1, hs = ep.SEC["hook"]; w0, w1, ws = ep.SEC["why"]; b0, b1, bs = ep.SEC["back"]
f0, f1, fs = ep.SEC["front"]; d0, d1, ds = ep.SEC["drill"]
T_FAIL = next(i for i, (s, _, p) in enumerate(PLAN) if p >= ep.W_FAIL) / FPS


def zoom_fn(t, m, shot, p):
    if t < h1:
        return 1 + 0.10 * ramp(t, T_FAIL - 0.1, T_FAIL + 0.3), (m["pelvis"][0], m["pelvis"][1])
    if t < w1:
        return 1 + 0.08 * ramp(t, w0, w1), (m["board"][0], m["board"][1])
    return 1.0, (0.5, 0.5)


def downhill(c, P, a, col=ICE, label="下坡"):
    if a <= 0:
        return
    (x0, y0), (x1, y1) = P["board"], P["dn"]
    arrow(c, x0, y0, x1, y1, col, a, w=9)
    stroke_text(c, label, x1 + (30 if x1 > x0 else -30), y1 + 20, 42, col, a, align="l" if x1 > x0 else "r")


def draw(c, t, P, m, shot, p):
    if t < h1 + 0.3:
        a = window(t, -1, h1, 0.3)
        tag(c, "错误示范", RED, 60, 330, a, icon="x")
        big_title(c, [("穿着板", 0.86), ("{r|站不起来}？", 1.1)], t, 0.1, h1, y=560, size=100)
        downhill(c, P, a * ramp(t, T_FAIL, T_FAIL + 0.3), RED, "板往下溜")
    if w0 - 0.3 < t < w1 + 0.3:
        a = window(t, w0, w1, 0.3)
        tag(c, "错误：腿伸直硬撑", RED, 60, 330, a, icon="x")
        downhill(c, P, a * window(t, ws[0][1], ws[0][2], 0.3), RED, "往下坡溜")
        a2 = window(t, ws[1][1], w1, 0.3)
        if a2 > 0:
            ax, ay = mid(P, "ankleL", "ankleR"); (px_, py_) = P["pelvis"]
            c.set_dash([14, 10]); c.new_path(); c.move_to(px_, py_); c.line_to(ax, ay)
            c.set_source_rgba(*RED, a2); c.set_line_width(6); c.stroke(); c.set_dash([])
            stroke_text(c, "板离屁股太远", (px_ + ax) / 2, (py_ + ay) / 2 - 60, 46, RED, a2)
    if b0 - 0.3 < t < b1 + 0.3:
        a = window(t, b0, b1, 0.3)
        tag(c, "正确：坐着起（后刃）", GREEN, 60, 330, a, icon="v")
        big_title(c, [("坐着起 · {w|3 步}", 1.0)], t, b0 + 0.05, bs[0][1] - 0.05, y=600, size=104)
        cur = step_of(t, bs)
        chips(c, ["① 板横过来", "② 收脚", "③ 抓前刃起"], cur, t, a * ramp(t, bs[0][1] - 0.2, bs[0][1] + 0.2))
        if cur == 0:
            a1 = a * ramp(t, bs[0][1] + 0.3, bs[0][1] + 0.7)
            downhill(c, P, a1)
            (x0, y0), (x1, y1) = P["tail"], P["nose"]
            c.new_path(); c.move_to(x0, y0); c.line_to(x1, y1); c.set_source_rgba(*GOLD, a1 * ramp(t, bs[0][1] + 1.6, bs[0][1] + 2.0))
            c.set_line_width(7); c.stroke()
            stroke_text(c, "板横在坡上", x1, y1 - 40, 44, GOLD, a1 * ramp(t, bs[0][1] + 1.6, bs[0][1] + 2.0))
        elif cur == 1:
            ax, ay = mid(P, "ankleL", "ankleR"); (px_, py_) = P["pelvis"]
            a1 = a * ramp(t, bs[1][1] + 0.2, bs[1][1] + 0.6)
            arrow(c, ax + 60, ay + 10, px_ + 60 + (ax - px_) * 0.35, py_ + 10 + (ay - py_) * 0.35, GOLD, a1)
            stroke_text(c, "脚跟收回来", ax + 80, ay + 80, 44, GOLD, a1, align="l")
        elif cur == 2:
            hx, hy = mid(P, "handL", "handR")
            ring(c, hx, hy, 66, GREEN, a * window(t, bs[2][1] + 0.6, bs[2][1] + 2.8, 0.3), t, label="抓住前刃")
            (px_, py_) = P["pelvis"]
            a2 = a * ramp(t, bs[2][1] + 2.6, bs[2][1] + 3.0)
            ring(c, px_, py_, 70, GREEN, a2, t, label="重心在板上")
    if f0 - 0.3 < t < f1 + 0.3:
        a = window(t, f0, f1, 0.3)
        tag(c, "正确：跪着起（前刃）", GREEN, 60, 330, a, icon="v")
        big_title(c, [("跪着起 · {w|3 步}", 1.0)], t, f0 + 0.05, fs[0][1] - 0.05, y=600, size=104)
        cur = step_of(t, fs)
        chips(c, ["① 双手撑雪", "② 推起放平", "③ 膝顶山坡"], cur, t, a * ramp(t, fs[0][1] - 0.2, fs[0][1] + 0.2))
        if cur == 0:
            hq = "handL" if m["handL"][2] < m["handR"][2] else "handR"
            ring(c, *P[hq], 60, GREEN, a * ramp(t, fs[0][1] + 1.4, fs[0][1] + 1.7), t, label="手撑雪面")
        elif cur == 1:
            ring(c, *P["board"], 90, GREEN, a * ramp(t, fs[1][1] + 1.3, fs[1][1] + 1.7), t, label="板放平")
        elif cur == 2:
            kq = "kneeL" if m["kneeL"][2] < m["kneeR"][2] else "kneeR"
            a1 = a * ramp(t, fs[2][1] + 1.0, fs[2][1] + 1.4)
            (x0, y0), (x1, y1) = P["board"], P["up"]
            arrow(c, P[kq][0], P[kq][1], P[kq][0] + (x1 - x0) * 0.8, P[kq][1] + (y1 - y0) * 0.8, GREEN, a1)
            stroke_text(c, "膝盖顶向山坡", P[kq][0], P[kq][1] - 90, 44, GREEN, a1)
    if d0 - 0.3 < t < d1 + 0.3:
        a = window(t, d0, d1, 0.3)
        tag(c, "怎么练", GOLD, 60, 330, a)
        card(c, 60, 440, W - 120, 250, a, ICE)
        stroke_text(c, "坐着起不来？", W / 2, 520, 40, DIM, a, stroke=0)
        rich_line(c, spans("{b|翻个身} → 跪着 → 前刃起"), W / 2, 610, 56, a)
        a2 = window(t, ds[1][1], d1, 0.3)
        if a2 > 0:
            card(c, 60, 720, W - 120, 150, a2)
            rich_line(c, spans("缓坡 · 坐起 {w|×3} · 跪起 {w|×3}"), W / 2, 815, 50, a2)
        a3 = window(t, ds[2][1], d1, 0.3)
        if a3 > 0:
            card(c, 60, 900, W - 120, 150, a3, GREEN)
            stroke_text(c, "过关标准", 120, 985, 36, GREEN, a3, align="l", stroke=0)
            stroke_text(c, "板不溜走", W - 120, 992, 56, INK, a3, align="r", stroke=0)


run_episode(ep, FR, OUTF, draw, zoom_fn, next_lines=[("单脚蹬行", 1.0), ("自己滑到{w|魔毯}", 0.8)])
