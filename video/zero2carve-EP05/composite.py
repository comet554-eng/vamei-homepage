"""叠字幕、原理图和数据，出竖屏成片：python3 composite.py FRAMEDIR OUT.mp4（STILLS="t1 t2" 时只出静帧调版）"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "zero2carve-lib"))
import ep
from vert import *

FR, OUTF = sys.argv[1], sys.argv[2]
PLAN = ep.plan()
h0, h1, hs = ep.SEC["hook"]; w0, w1, ws = ep.SEC["why"]; s0, s1, ss = ep.SEC["steps"]; d0, d1, ds = ep.SEC["drill"]
T_TURN = next(i for i, (s, _, p) in enumerate(PLAN) if p >= ep.W_TURN) / FPS
FRONT, BACK = "ankleR", "ankleL"          # 板头在 +x，右脚是前脚


def zoom_fn(t, m, shot, p):
    if t < h1:
        return 1 + 0.10 * ramp(t, T_TURN, T_TURN + 0.8), (m["board"][0], m["board"][1])
    return 1.0, (0.5, 0.5)


def unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
    return dx / L, dy / L


def zigzag(c, x, y, w, h, k, alpha):
    """落叶飘路线示意：在坡上左右来回，一点点往下。上方是山上。"""
    if alpha <= 0:
        return
    card(c, x, y, w, h, alpha, ICE)
    stroke_text(c, "山上", x + w / 2, y + 48, 28, DIM, alpha, bold=False, stroke=0)
    stroke_text(c, "山下", x + w / 2, y + h - 22, 28, DIM, alpha, bold=False, stroke=0)
    pts = [(x + 0.18 * w, y + 0.22 * h)]
    for i in range(1, 6):
        pts.append((x + (0.82 if i % 2 else 0.18) * w, y + (0.22 + 0.13 * i) * h))
    n = k * (len(pts) - 1)
    c.new_path(); c.move_to(*pts[0])
    for i in range(1, len(pts)):
        f = clamp(n - (i - 1))
        if f <= 0:
            break
        x0, y0 = pts[i - 1]; x1, y1 = pts[i]
        c.line_to(x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)
    c.set_source_rgba(*GOLD, alpha); c.set_line_width(6); c.set_dash([16, 10]); c.stroke(); c.set_dash([])
    # 板（横着）跟着路线走
    i = min(int(n), len(pts) - 2); f = n - i
    bx = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f; by = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f
    c.save(); c.translate(bx, by); c.rotate(math.radians(12 if pts[i + 1][0] > pts[i][0] else -12))
    rrect(c, -70, -14, 140, 28, 14); c.set_source_rgba(0.25, 0.55, 0.95, alpha); c.fill(); c.restore()


def bars(c, x, y, w, alpha, yaw):
    """偏角 -> 下滑力顺着板走的份额。"""
    if alpha <= 0:
        return
    card(c, x, y, w, 360, alpha, ICE)
    stroke_text(c, "板头朝下偏 α，下滑力顺着板走的份额 = sin α", x + w / 2, y + 52, 30, DIM, alpha, bold=False, stroke=0)
    for i, a in enumerate(ep.ANGLES):
        yy = y + 100 + i * 62
        on = yaw >= a - 0.5
        v = ep.SHARE[a]
        col = (RED if a >= 45 else ICE) if on else (0.4, 0.43, 0.48)
        stroke_text(c, f"{a}°", x + 110, yy + 34, 34, INK if on else DIM, alpha, align="r", stroke=0)
        c.set_source_rgba(1, 1, 1, 0.08 * alpha); rrect(c, x + 130, yy + 8, w - 300, 34, 10); c.fill()
        c.set_source_rgba(*col, alpha); rrect(c, x + 130, yy + 8, max(20, (w - 300) * v * (1 if on else 0.0) + 1), 34, 10); c.fill()
        if on:
            stroke_text(c, f"{v * 100:.0f}%", x + w - 40, yy + 36, 36, col, alpha, align="r", stroke=0)


def leaf_gauge(c, x, y, alpha, yaw):
    """右上角俯视小图：下坡箭头 + 板的朝向 + 往哪边飘。"""
    if alpha <= 0:
        return
    card(c, x, y, 340, 300, alpha, ICE)
    cx, cy = x + 170, y + 130
    arrow(c, cx, cy - 70, cx, cy + 90, (0.6, 0.65, 0.72), alpha * 0.8, w=5)
    stroke_text(c, "下坡", cx + 20, cy + 90, 24, DIM, alpha, align="l", stroke=0)
    c.save(); c.translate(cx, cy); c.rotate(math.radians(yaw))
    rrect(c, -110, -18, 220, 36, 18); c.set_source_rgba(0.25, 0.55, 0.95, alpha); c.fill()
    c.new_path(); c.arc(105, 0, 8, 0, 2 * math.pi); c.set_source_rgba(*GOLD, alpha); c.fill()     # 板头
    c.restore()
    if yaw > 4:
        lab, col = f"偏 {yaw:.0f}° → 往板头飘", GOLD
    elif yaw < -4:
        lab, col = f"偏 {-yaw:.0f}° → 往板尾飘", GOLD
    else:
        lab, col = "板横着 → 停住", GREEN
    stroke_text(c, lab, cx, y + 270, 32, col, alpha, stroke=0)


def draw(c, t, P, m, shot, p):
    pose = m.get("_pose", {})
    yaw = pose.get("yaw", 0.0)
    if t < h1 + 0.3:
        a = window(t, -1, h1, 0.3)
        tag(c, "错误示范", RED, 60, 330, a, icon="x")
        big_title(c, [("落叶飘", 0.86), ("一下就{r|冲出去}？", 1.05)], t, 0.1, h1, y=560, size=100)
        a2 = a * ramp(t, T_TURN, T_TURN + 0.4)
        if a2 > 0:
            (x0, y0), (x1, y1) = P["tail"], P["nose"]
            c.new_path(); c.move_to(x0, y0); c.line_to(x1, y1); c.set_source_rgba(*RED, a2); c.set_line_width(7); c.stroke()
            stroke_text(c, "板头转向山下", x1, y1 + 70, 44, RED, a2)
    if w0 - 0.3 < t < w1 + 0.3:
        a = window(t, w0, w1, 0.3)
        tag(c, "原理", ICE, 60, 330, a)
        zigzag(c, 60, 420, W - 120, 560, ramp(t, ws[0][1], ws[0][2]), a * window(t, ws[0][1] - 0.3, ws[0][2] + 0.2, 0.3))
        a1 = a * window(t, ws[1][1], ws[1][2] + 0.2, 0.3)
        if a1 > 0:
            ring(c, *P[FRONT], 50, GOLD, a1 * ramp(t, ws[1][1] + 0.2, ws[1][1] + 0.5), t, label="重心前脚")
        a2 = a * ramp(t, ws[2][1] - 0.2, ws[2][1] + 0.3)
        if a2 > 0 and abs(yaw) > 1:          # 受力分解：下滑力（白）和顺着板的那一份（蓝）
            b = P["board"]; fu = unit(b, P["fall"]); bu = unit(P["tail"], P["nose"])
            Lf = 260
            arrow(c, b[0], b[1], b[0] + fu[0] * Lf, b[1] + fu[1] * Lf, INK, a2, w=8)
            stroke_text(c, "下滑力", b[0] + fu[0] * Lf + 20, b[1] + fu[1] * Lf + 10, 36, INK, a2, align="l")
            comp = fu[0] * bu[0] + fu[1] * bu[1]
            arrow(c, b[0], b[1], b[0] + bu[0] * Lf * comp, b[1] + bu[1] * Lf * comp, ICE, a2, w=8)
            stroke_text(c, f"α = {yaw:.0f}°", b[0] - 40, b[1] - 120, 46, GOLD, a2, align="r")
        a3 = a * ramp(t, ws[3][1] - 0.2, ws[3][1] + 0.3)
        bars(c, 60, 1080, W - 120, a3, yaw)
    if s0 - 0.3 < t < s1 + 0.3:
        a = window(t, s0, s1, 0.3)
        tag(c, "正确做法", GREEN, 60, 330, a, icon="v")
        big_title(c, [("后刃落叶飘 · {w|4 步}", 1.0)], t, s0 + 0.05, ss[0][1] - 0.05, y=600, size=96)
        cur = step_of(t, ss)
        ac = a * ramp(t, ss[0][1] - 0.2, ss[0][1] + 0.2)
        chips(c, ["①推坡停稳", "②压前脚飘", "③回中停住", "④压后脚飘"], cur, t, ac)
        leaf_gauge(c, W - 400, 545, ac, yaw)
        if cur == 0:
            ring(c, *P["heel"], 56, GOLD, a * ramp(t, ss[0][1] + 0.3, ss[0][1] + 0.6), t, label="后刃立住")
        elif cur == 1:
            ring(c, *P[FRONT], 50, GOLD, a * ramp(t, ss[1][1] + 0.3, ss[1][1] + 0.6), t, label="前脚多压")
        elif cur == 3:
            ring(c, *P[BACK], 50, GOLD, a * ramp(t, ss[3][1] + 0.3, ss[3][1] + 0.6), t, label="后脚多压")
    if d0 - 0.3 < t < d1 + 0.3:
        a = window(t, d0, d1, 0.3)
        tag(c, "怎么练", GOLD, 60, 330, a)
        card(c, 60, 440, W - 120, 200, a)
        stroke_text(c, "初级道 · 后刃", W / 2, 515, 38, DIM, a, stroke=0)
        rich_line(c, spans("前飘 {w|5 米} → 停 → 回飘 {w|5 米}"), W / 2, 600, 52, a)
        a2 = window(t, ds[1][1], d1, 0.3)
        if a2 > 0:
            card(c, 60, 670, W - 120, 150, a2, GREEN)
            stroke_text(c, "过关标准", 120, 755, 36, GREEN, a2, align="l", stroke=0)
            stroke_text(c, "板头不转过下坡", W - 120, 762, 50, INK, a2, align="r", stroke=0)


run_episode(ep, FR, OUTF, draw, zoom_fn, next_lines=[("换到前刃", 1.0), ("推坡和{w|落叶飘}", 0.8)])
