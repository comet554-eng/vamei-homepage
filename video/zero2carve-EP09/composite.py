"""叠字幕、原理图和数据，出竖屏无声成片（音乐和音效由 ../zero2carve-lib/finish.py 配）：
python3 composite.py FRAMEDIR OUT.mp4（STILLS="t1 t2" 时只出静帧调版）"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "zero2carve-lib"))
import ep
from vert import *

FR, OUTF = sys.argv[1], sys.argv[2]
PLAN = ep.plan()
h0, h1, hs = ep.SEC["hook"]; w0, w1, ws = ep.SEC["why"]; s0, s1, ss = ep.SEC["steps"]; d0, d1, ds = ep.SEC["drill"]
T_BACK = next(i for i, (s, _, p) in enumerate(PLAN) if p >= ep.W_BACK) / FPS
T_FALL = next(i for i, (s, _, p) in enumerate(PLAN) if p >= 2.0) / FPS


def zoom_fn(t, m, shot, p):
    if t < h1:
        k = ramp(t, T_FALL - 0.2, T_FALL + 0.2)
        sh = math.exp(-((t - T_FALL - 0.1) / 0.12) ** 2)
        return 1 + 0.12 * k, (m["board"][0] + 0.01 * sh * math.sin(t * 90), m["board"][1])
    return 1.0, (0.5, 0.5)


def axis_lines(c, P, a, tilt, show_world=True, show_slope=True):
    """从骨盆画：竖直线（跟地面垂直，红虚线）、坡面法线（垂直坡面，绿），身体轴线按姿势变色。"""
    if a <= 0:
        return
    px, py = P["pelvis"]

    def ext(q, L=1.15):
        x, y = P[q]; return px + (x - px) * L, py + (y - py) * L
    wx, wy = ext("up_world"); sx, sy = ext("up_slope")
    s_right = sx >= wx                     # 两条线哪条在右，标签就往哪边放，免得叠在一起
    if show_world:
        c.set_dash([14, 10]); c.new_path(); c.move_to(px, py); c.line_to(wx, wy)
        c.set_source_rgba(*RED, a); c.set_line_width(6); c.stroke(); c.set_dash([])
        stroke_text(c, "跟地面垂直", wx + (-20 if s_right else 20), wy + 20, 38, RED, a, align="r" if s_right else "l")
    if show_slope:
        c.new_path(); c.move_to(px, py); c.line_to(sx, sy)
        c.set_source_rgba(*GREEN, a); c.set_line_width(6); c.stroke()
        stroke_text(c, "垂直坡面", sx + (20 if s_right else -20), sy + 20, 38, GREEN, a, align="l" if s_right else "r")
    hx, hy = P["head"]
    col = RED if tilt > 8 else GREEN
    c.new_path(); c.move_to(px, py); c.line_to(px + (hx - px) * 1.05, py + (hy - py) * 1.05)
    c.set_source_rgba(*col, a); c.set_line_width(10); c.stroke()
    lab = f"相对板后仰 {tilt:.0f}°" if tilt > 3 else "身体垂直坡面"
    stroke_text(c, lab, px, py + 150, 46, col, a)


def grades_card(c, y, a, t, t0):
    if a <= 0:
        return
    card(c, 60, y, W - 120, 330, a, ICE)
    stroke_text(c, "雪道多陡（阿尔卑斯常用分级）", W / 2, y + 55, 30, DIM, a, bold=False, stroke=0)
    rows = [("初级道", "≤ 14°", 14, GREEN), ("中级道", "14–22°", 22, ICE), ("高级道", "> 22°", 30, (0.75, 0.78, 0.85))]
    for i, (nm, rng, deg, col) in enumerate(rows):
        x = 60 + (W - 120) * (0.18 + 0.32 * i); yy = y + 250
        k = ramp(t, t0 + 0.3 * i, t0 + 0.3 * i + 0.5)
        ang = math.radians(deg) * k
        c.new_path(); c.move_to(x - 90, yy); c.line_to(x + 90, yy); c.line_to(x + 90, yy - 180 * math.tan(ang)); c.close_path()
        c.set_source_rgba(*col, 0.85 * a); c.fill()
        stroke_text(c, nm, x, y + 110, 34, INK, a, stroke=0)
        stroke_text(c, rng, x, yy + 52, 34, col, a, stroke=0)


def pull_card(c, y, a, t, t0):
    if a <= 0:
        return
    card(c, 60, y, W - 120, 330, a, RED)
    stroke_text(c, "往下拉你的力 = 体重 × sin(坡度)", W / 2, y + 55, 30, DIM, a, bold=False, stroke=0)
    for i, (deg, col, tt) in enumerate(((12, ICE, t0 + 1.2), (20, RED, t0 + 3.2))):
        v = ep.PULL[deg]; k = ramp(t, tt - 0.6, tt)
        yy = y + 105 + i * 95
        stroke_text(c, f"{deg}°", 160, yy + 40, 42, INK, a, align="r", stroke=0)
        c.set_source_rgba(1, 1, 1, 0.08 * a); rrect(c, 190, yy, W - 420, 52, 14); c.fill()
        c.set_source_rgba(*col, a); rrect(c, 190, yy, max(20, (W - 420) * v / 0.4 * k), 52, 14); c.fill()
        stroke_text(c, f"{v * 100 * k:.0f}%", W - 110, yy + 44, 50, col, a, align="r", stroke=0)
    kk = pop(t, t0 + 4.0, 0.35)
    if kk > 0:
        stroke_text(c, f"+{ep.MORE * 100:.0f}%", W - 110, y + 315, 44, RED, a, align="r", stroke=0)


def draw(c, t, P, m, shot, p):
    pose = m.get("_pose", {})
    broll, tilt = pose.get("broll", 0.0), pose.get("tilt", 0.0)
    if t < h1 + 0.3:
        a = window(t, -1, h1, 0.3)
        tag(c, "错误示范", RED, 60, 330, a, icon="x")
        big_title(c, [("中级道一陡", 0.86), ("就{r|往后坐}？", 1.1)], t, 0.1, h1, y=560, size=100)
        ring(c, *P["pelvis"], 70, RED, a * ramp(t, T_BACK, T_BACK + 0.3), t, label="往后坐")
        fl = math.exp(-((t - T_FALL - 0.1) / 0.07) ** 2)
        if fl > 0.01:
            c.set_source_rgba(1, 1, 1, 0.55 * fl); c.paint()
    if w0 - 0.3 < t < w1 + 0.3:
        a = window(t, w0, w1, 0.3)
        tag(c, "原理 · 侧面看", ICE, 60, 330, a)
        grades_card(c, 1100, a * window(t, ws[0][1] - 0.2, ws[0][2] + 0.2, 0.3), t, ws[0][1] + 0.3)
        pull_card(c, 1100, a * window(t, ws[1][1] - 0.2, ws[1][2] + 0.2, 0.3), t, ws[1][1])
        a2 = a * window(t, ws[2][1] - 0.2, w1 + 0.2, 0.3)
        axis_lines(c, P, a2, tilt, show_world=t < ws[4][1] + 1.0)
        a3 = a * window(t, ws[3][1], ws[3][2] + 0.2, 0.3)
        if a3 > 0:
            ring(c, *P["tail"], 54, RED, a3, t, label="板尾吃重")
            ring(c, *P["nose"], 54, GOLD, a3 * ramp(t, ws[3][1] + 0.6, ws[3][1] + 0.9), t, label="板头发飘")
    if s0 - 0.3 < t < s1 + 0.3:
        a = window(t, s0, s1, 0.3)
        tag(c, "正确做法", GREEN, 60, 330, a, icon="v")
        big_title(c, [("陡坡S弯 · {w|4 步}", 1.0)], t, s0 + 0.05, ss[0][1] - 0.05, y=600, size=96)
        cur = step_of(t, ss)
        ac = a * ramp(t, ss[0][1] - 0.2, ss[0][1] + 0.2)
        chips(c, ["①垂直坡面", "②弯短一点", "③立刃>坡", "④压低重心"], cur, t, ac)
        if ac > 0:
            e = abs(broll); ok = e >= ep.SLOPE
            col = GREEN if ok else (GOLD if e > 3 else RED)
            card(c, W - 360, 545, 300, 170, ac, col)
            stroke_text(c, f"立刃 {e:.0f}°", W - 210, 615, 48, col, ac, stroke=0)
            stroke_text(c, f"坡 {ep.SLOPE:.0f}° · " + ("咬得住" if ok else ("换刃中" if e <= 3 else "不够")), W - 210, 675, 30, INK, ac, stroke=0)
        if cur == 0:
            ring(c, *P["head"], 60, GOLD, a * ramp(t, ss[0][1] + 0.3, ss[0][1] + 0.6), t, label="看山下")
        elif cur == 3:
            kx, ky = mid(P, "kneeL", "kneeR")
            ring(c, kx, ky, 64, GOLD, a * ramp(t, ss[3][1] + 0.3, ss[3][1] + 0.6), t, label="膝盖更弯")
    if d0 - 0.3 < t < d1 + 0.3:
        a = window(t, d0, d1, 0.3)
        tag(c, "怎么练", GOLD, 60, 330, a)
        card(c, 60, 440, W - 120, 200, a)
        stroke_text(c, "中级道最缓的一段", W / 2, 515, 38, DIM, a, stroke=0)
        rich_line(c, spans("连续 S 弯 · 每个都{w|走完}"), W / 2, 600, 50, a)
        a2 = window(t, ds[1][1], d1, 0.3)
        if a2 > 0:
            card(c, 60, 670, W - 120, 150, a2, GREEN)
            stroke_text(c, "过关标准", 120, 755, 36, GREEN, a2, align="l", stroke=0)
            stroke_text(c, "不后坐 · 不越滑越快", W - 120, 762, 46, INK, a2, align="r", stroke=0)
        a3 = window(t, ds[2][1], d1, 0.3)
        if a3 > 0:
            tag(c, "评论区说说", ICE, 60, 850, a3 * pop(t, ds[2][1], 0.4), size=40)


run_episode(ep, FR, OUTF, draw, zoom_fn, next_lines=[("从搓雪", 0.9), ("到{w|刻滑}！", 1.15)])
