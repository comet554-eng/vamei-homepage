"""叠字幕、原理图和数据，出竖屏成片：python3 composite.py FRAMEDIR OUT.mp4（STILLS="t1 t2" 时只出静帧调版）"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "zero2carve-lib"))
import ep
from vert import *

FR, OUTF = sys.argv[1], sys.argv[2]
PLAN = ep.plan()
h0, h1, hs = ep.SEC["hook"]; w0, w1, ws = ep.SEC["why"]; s0, s1, ss = ep.SEC["steps"]; d0, d1, ds = ep.SEC["drill"]
T_CATCH = next(i for i, (s, _, p) in enumerate(PLAN) if p >= ep.H_CATCH) / FPS


def zoom_fn(t, m, shot, p):
    if t < h1:
        return 1 + 0.12 * ramp(t, T_CATCH - 0.1, T_CATCH + 0.2), (m["toe"][0], m["toe"][1])
    return 1.0, (0.5, 0.5)


def state(broll, slope):
    if broll < 0:
        return "前刃碰雪 → 绊倒", RED
    if broll >= slope:
        return "板面放平 → 停住", GREEN
    return "板面朝下坡 → 往下滑", GOLD


def edge_diagram(c, cx, cy, sc, broll, slope, alpha, label=True, clip=None):
    """板的横截面放大图：坡面线、过后刃的水平线、板底，标出坡度和立刃角。左边上坡（后刃），右边下坡。"""
    if alpha <= 0:
        return
    c.save()
    if clip:
        rrect(c, *clip, 28); c.clip()
    sa, ba = math.radians(slope), math.radians(slope - broll)      # 坡面、板底相对水平往下倾的角
    hx, hy = cx - 0.20 * sc, cy                                     # 后刃落在坡面上的点
    L = 0.62 * sc
    # 雪：坡面线以下
    c.new_path(); c.move_to(hx - L, hy - L * math.tan(sa)); c.line_to(hx + 1.6 * L, hy + 1.6 * L * math.tan(sa))
    c.line_to(hx + 1.6 * L, hy + 0.9 * L); c.line_to(hx - L, hy + 0.9 * L); c.close_path()
    c.set_source_rgba(0.80, 0.86, 0.95, 0.20 * alpha); c.fill()
    c.new_path(); c.move_to(hx - L, hy - L * math.tan(sa)); c.line_to(hx + 1.6 * L, hy + 1.6 * L * math.tan(sa))
    c.set_source_rgba(0.85, 0.90, 1.0, 0.95 * alpha); c.set_line_width(4); c.stroke()
    # 水平虚线
    c.set_dash([12, 9]); c.new_path(); c.move_to(hx - 0.2 * L, hy); c.line_to(hx + 1.5 * L, hy)
    c.set_source_rgba(1, 1, 1, 0.6 * alpha); c.set_line_width(3); c.stroke(); c.set_dash([])
    # 板（宽 0.25 m 放大），绕后刃转
    bw, th = 0.25 * sc, 0.02 * sc + 6
    st, col = state(broll, slope)
    c.save(); c.translate(hx, hy); c.rotate(ba)
    rrect(c, 0, -th, bw, th, th / 2.5); c.set_source_rgba(0.25, 0.55, 0.95, alpha); c.fill()
    c.set_source_rgba(0.12, 0.13, 0.16, alpha); rrect(c, bw * 0.18, -th - 0.10 * sc, bw * 0.64, 0.10 * sc, 8); c.fill()   # 鞋
    c.restore()
    tx, ty = hx + bw * math.cos(ba), hy + bw * math.sin(ba)
    # 刃点
    for (x, y, cc) in ((hx, hy, GOLD), (tx, ty, RED if broll < 0 else (0.7, 0.75, 0.8))):
        c.new_path(); c.arc(x, y, 9, 0, 2 * math.pi); c.set_source_rgba(*cc, alpha); c.fill()
    if not label:
        c.restore()
        return
    if label:
        r1 = 0.95 * L
        c.new_path(); c.arc(hx, hy, r1, 0, sa); c.set_source_rgba(0.85, 0.90, 1.0, alpha); c.set_line_width(3); c.stroke()
        stroke_text(c, f"坡 {slope:.0f}°", hx + r1 - 16, hy + r1 * math.sin(sa) + 52, 36, ICE, alpha, align="r", stroke=5)
        r2 = 0.52 * L
        a0, a1 = sorted((ba, sa))
        c.new_path(); c.arc(hx, hy, r2, a0, a1); c.set_source_rgba(*GOLD, alpha); c.set_line_width(5); c.stroke()
        stroke_text(c, f"立刃 {broll:.0f}°", hx + 0.2 * L, hy - 0.24 * L, 44, GOLD, alpha, align="l", stroke=5)
        stroke_text(c, "后刃", hx - 20, hy + 52, 28, GOLD, alpha, align="r", stroke=4)
        stroke_text(c, st, cx, cy + 0.54 * L, 46, col, alpha, stroke=6)
    c.restore()


def draw(c, t, P, m, shot, p):
    pose = m.get("_pose", {"broll": 0, "slope": ep.SLOPE})
    if t < h1 + 0.3:
        a = window(t, -1, h1, 0.3)
        tag(c, "错误示范", RED, 60, 330, a, icon="x")
        big_title(c, [("站在坡上", 0.86), ("{r|停不住}？", 1.1)], t, 0.1, h1, y=560, size=100)
        if t >= T_CATCH - 0.05:
            ring(c, *P["toe"], 60, RED, a * ramp(t, T_CATCH, T_CATCH + 0.15), t, label="前刃卡住")
        fl = math.exp(-((t - T_CATCH) / 0.07) ** 2)
        if fl > 0.01:
            c.set_source_rgba(1, 1, 1, 0.5 * fl); c.paint()
    if w0 - 0.3 < t < w1 + 0.3:
        a = window(t, w0, w1, 0.3)
        tag(c, "原理", ICE, 60, 330, a)
        # ① 板放平 + ④⑤⑥ 立刃动画：横截面放大图
        ad = a * max(window(t, ws[0][1] - 0.2, ws[0][2] + 0.2, 0.3), ramp(t, ws[3][1] - 0.3, ws[3][1]))
        if ad > 0:
            c.set_source_rgba(0.01, 0.015, 0.03, 0.35 * ad); c.paint()
            card(c, 60, 420, W - 120, 620, ad, ICE)
            stroke_text(c, "横截面放大 · 顺着板看", W / 2, 478, 30, DIM, ad, bold=False, stroke=0)
            edge_diagram(c, W / 2 + 40, 690, 900, pose["broll"], pose["slope"], ad, clip=(60, 420, W - 120, 620))
        # ② 摩擦系数对比
        a2 = a * window(t, ws[1][1], ws[1][2] + 0.1, 0.3)
        if a2 > 0:
            card(c, 60, 420, W - 120, 470, a2, ICE)
            stroke_text(c, "摩擦系数", W / 2, 490, 38, DIM, a2, stroke=0)
            x0, x1, vmax = 130, W - 130, 0.25
            X = lambda v: x0 + (x1 - x0) * v / vmax
            k = ramp(t, ws[1][1] + 0.2, ws[1][1] + 1.2)
            c.set_source_rgba(*ICE, 0.9 * a2); rrect(c, X(ep.MU_LO), 560, (X(ep.MU_HI) - X(ep.MU_LO)) * k + 1, 70, 14); c.fill()
            stroke_text(c, f"雪面 {ep.MU_LO}~{ep.MU_HI}", X(ep.MU_LO), 690, 40, ICE, a2 * k, align="l", stroke=0)
            k2 = ramp(t, ws[1][1] + 1.5, ws[1][1] + 2.3)
            xn = X(ep.MU_NEED)
            c.set_source_rgba(*RED, a2 * k2); c.rectangle(xn - 4, 540, 8, 200); c.fill()
            stroke_text(c, f"停住要 {ep.MU_NEED:.2f}", xn, 790, 44, RED, a2 * k2, stroke=0)
            for v in (0, 0.1, 0.2):
                stroke_text(c, f"{v:g}", X(v), 535, 24, DIM, a2, bold=False, stroke=0)
            stroke_text(c, "Budde & Himes 2017 · Wolfsperger 等 2021", W / 2, 860, 22, DIM, a2, bold=False, stroke=0)
        # ③ 板放平 3 秒的速度
        a3 = a * window(t, ws[2][1], ws[2][2] + 0.1, 0.3)
        if a3 > 0:
            card(c, 60, 420, W - 120, 470, a3, RED)
            tt = clamp((t - ws[2][1] - 0.4) / 3.0) * 3.0
            v = ep.ACC * tt * 3.6
            stroke_text(c, f"板放平 · 第 {tt:.1f} 秒", W / 2, 500, 38, DIM, a3, stroke=0)
            stroke_text(c, f"{v:.0f}", W / 2 - 40, 700, 190, RED, a3, face=SERIF, stroke=0, align="r")
            stroke_text(c, "公里/小时", W / 2 - 10, 690, 50, INK, a3, align="l", stroke=0)
            c.set_source_rgba(1, 1, 1, 0.15 * a3); rrect(c, 130, 760, W - 260, 16, 8); c.fill()
            c.set_source_rgba(*RED, a3); rrect(c, 130, 760, max(16, (W - 260) * tt / 3.0), 16, 8); c.fill()
            stroke_text(c, f"坡 {ep.SLOPE:.0f}° · 摩擦系数取 {ep.MU_DEMO} · 示意计算", W / 2, 840, 24, DIM, a3, bold=False, stroke=0)
    if s0 - 0.3 < t < s1 + 0.3:
        a = window(t, s0, s1, 0.3)
        tag(c, "正确做法", GREEN, 60, 330, a, icon="v")
        big_title(c, [("后刃推坡 · {w|4 步}", 1.0)], t, s0 + 0.05, ss[0][1] - 0.05, y=600, size=100)
        cur = step_of(t, ss)
        ac = a * ramp(t, ss[0][1] - 0.2, ss[0][1] + 0.2)
        chips(c, ["①压后刃", "②脚尖放低", "③脚尖抬起", "④两脚平均"], cur, t, ac)
        # 右上角小仪表：实时立刃角
        if ac > 0:
            card(c, W - 400, 545, 340, 300, ac, ICE)
            edge_diagram(c, W - 220, 690, 380, pose["broll"], pose["slope"], ac, label=False, clip=(W - 400, 545, 340, 300))
            st, col = state(pose["broll"], pose["slope"])
            stroke_text(c, f"立刃 {pose['broll']:.0f}° / 坡 {pose['slope']:.0f}°", W - 230, 780, 30, INK, ac, stroke=0)
            stroke_text(c, st.split(" → ")[1], W - 230, 825, 36, col, ac, stroke=0)
        if cur == 0:
            ring(c, *P["heel"], 60, GOLD, a * ramp(t, ss[0][1] + 0.3, ss[0][1] + 0.6), t, label="后刃")
        elif cur == 3:
            for q, lab in (("ankleL", "50%"), ("ankleR", "50%")):
                ring(c, *P[q], 46, GREEN, a * ramp(t, ss[3][1] + 0.3, ss[3][1] + 0.6), t, pulse=False)
                stroke_text(c, lab, P[q][0], P[q][1] + 95, 40, GREEN, a * ramp(t, ss[3][1] + 0.3, ss[3][1] + 0.6))
    if d0 - 0.3 < t < d1 + 0.3:
        a = window(t, d0, d1, 0.3)
        tag(c, "怎么练", GOLD, 60, 330, a)
        card(c, 60, 440, W - 120, 200, a)
        stroke_text(c, "初级道 · 后刃", W / 2, 515, 38, DIM, a, stroke=0)
        rich_line(c, spans("滑 {w|3 米} → 停住 × {w|5}"), W / 2, 600, 58, a)
        a2 = window(t, ds[1][1], d1, 0.3)
        if a2 > 0:
            card(c, 60, 670, W - 120, 150, a2, GREEN)
            stroke_text(c, "过关标准", 120, 755, 36, GREEN, a2, align="l", stroke=0)
            stroke_text(c, "想停就停", W - 120, 762, 56, INK, a2, align="r", stroke=0)


run_episode(ep, FR, OUTF, draw, zoom_fn, next_lines=[("落叶飘", 1.0), ("在坡上{w|左右走}", 0.8)])
