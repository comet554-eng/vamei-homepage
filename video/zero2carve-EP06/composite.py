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
FRONT, BACK = "ankleR", "ankleL"


def zoom_fn(t, m, shot, p):
    if t < h1:
        return 1 + 0.12 * ramp(t, T_CATCH - 0.1, T_CATCH + 0.3), (m["pelvis"][0], m["pelvis"][1])
    return 1.0, (0.5, 0.5)


def state(broll, slope):
    if broll < 0:
        return "后刃碰雪 → 往后栽", RED
    if broll >= slope:
        return "板面放平 → 停住", GREEN
    return "板面朝下坡 → 往下滑", GOLD


def edge_diagram(c, cx, cy, sc, broll, slope, alpha, label=True, clip=None):
    """板的横截面放大图（前刃版）：左边上坡是前刃，右边下坡是后刃。broll 传正的立刃角。"""
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
        stroke_text(c, "前刃", hx - 20, hy + 52, 28, GOLD, alpha, align="r", stroke=4)
        stroke_text(c, st, cx, cy + 0.54 * L, 46, col, alpha, stroke=6)
    c.restore()



def rom_card(c, y, alpha, t0, t):
    """脚踝活动范围：踮脚（跖屈）vs 勾脚尖（背屈），画成两段弧。"""
    if alpha <= 0:
        return
    card(c, 60, y, W - 120, 520, alpha, ICE)
    stroke_text(c, "脚踝能动多大角度", W / 2, y + 60, 36, DIM, alpha, stroke=0)
    for i, (lab, deg, col, sub) in enumerate((("踮脚 · 跖屈", ep.ROM_PF, GOLD, "用前刃"), ("勾脚尖 · 背屈", ep.ROM_DF, RED, "用后刃"))):
        cx, cy, r = 60 + (W - 120) * (0.27 + 0.46 * i), y + 330, 150
        k = ramp(t, t0 + 0.3 + 0.6 * i, t0 + 1.3 + 0.6 * i)
        c.new_path(); c.arc(cx, cy, r, math.pi, 1.5 * math.pi * 0 + math.pi + math.radians(90))
        c.set_source_rgba(1, 1, 1, 0.12 * alpha); c.set_line_width(26); c.stroke()
        c.new_path(); c.arc(cx, cy, r, math.pi, math.pi + math.radians(deg * 1.8) * k)
        c.set_source_rgba(*col, alpha); c.set_line_width(26); c.stroke()
        stroke_text(c, f"{deg * k:.0f}°", cx + 10, cy - 30, 90, col, alpha, face=SERIF, stroke=0)
        stroke_text(c, lab, cx, cy + 60, 34, INK, alpha, stroke=0)
        stroke_text(c, sub, cx, cy + 105, 30, DIM, alpha, bold=False, stroke=0)
    stroke_text(c, "AAOS 常用正常值 · 穿雪鞋后会更小，这里只比大小", W / 2, y + 500, 22, DIM, alpha, bold=False, stroke=0)


def draw(c, t, P, m, shot, p):
    pose = m.get("_pose", {})
    edge = -pose.get("broll", 0.0)
    yaw = pose.get("yaw", 0.0)
    if t < h1 + 0.3:
        a = window(t, -1, h1, 0.3)
        tag(c, "错误示范", RED, 60, 330, a, icon="x")
        big_title(c, [("前刃推坡", 0.86), ("最怕{r|往后栽}", 1.08)], t, 0.1, h1, y=560, size=100)
        ring(c, *P["pelvis"], 70, RED, a * window(t, 0.4, T_CATCH - 0.1, 0.3), t, label="弯腰撅屁股")
        if t >= T_CATCH - 0.05:
            ring(c, *P["heel"], 60, RED, a * ramp(t, T_CATCH, T_CATCH + 0.15), t, label="后刃碰雪")
        fl = math.exp(-((t - T_CATCH) / 0.07) ** 2)
        if fl > 0.01:
            c.set_source_rgba(1, 1, 1, 0.5 * fl); c.paint()
    if w0 - 0.3 < t < w1 + 0.3:
        a = window(t, w0, w1, 0.3)
        tag(c, "原理", ICE, 60, 330, a)
        ring(c, *P["toe"], 60, GOLD, a * window(t, ws[0][1] + 0.4, ws[0][2] + 0.2, 0.3), t, label="前刃")
        rom_card(c, 420, a * window(t, ws[1][1] - 0.2, ws[1][2] + 0.2, 0.3), ws[1][1], t)
        a2 = a * window(t, ws[2][1] - 0.2, ws[2][2] + 0.2, 0.3)
        if a2 > 0:
            card(c, 60, 420, W - 120, 300, a2, ICE)
            for i, (txt, col, ic) in enumerate((("前刃：立得高、停得稳", GREEN, "v"), ("但面朝山上，看不见山下", RED, "x"))):
                tag(c, txt, col, 110, 470 + i * 120, a2 * ramp(t, ws[2][1] + 0.4 * i, ws[2][1] + 0.4 * i + 0.4), size=40, icon=ic)
        ad = a * ramp(t, ws[3][1] - 0.3, ws[3][1])
        if ad > 0:
            c.set_source_rgba(0.01, 0.015, 0.03, 0.30 * ad); c.paint()
            card(c, 60, 420, W - 120, 620, ad, ICE)
            stroke_text(c, "横截面放大 · 顺着板看", W / 2, 478, 30, DIM, ad, bold=False, stroke=0)
            edge_diagram(c, W / 2 + 40, 690, 900, edge, ep.SLOPE, ad, clip=(60, 420, W - 120, 620))
    if s0 - 0.3 < t < s1 + 0.3:
        a = window(t, s0, s1, 0.3)
        tag(c, "正确做法", GREEN, 60, 330, a, icon="v")
        big_title(c, [("前刃推坡 + 落叶飘", 0.92)], t, s0 + 0.05, ss[0][1] - 0.05, y=600, size=96)
        cur = step_of(t, ss)
        ac = a * ramp(t, ss[0][1] - 0.2, ss[0][1] + 0.2)
        chips(c, ["①膝顶山坡", "②滑·停", "③压前脚飘", "④回头再飘"], cur, t, ac)
        if ac > 0:
            card(c, W - 400, 545, 340, 300, ac, ICE)
            edge_diagram(c, W - 220, 690, 380, edge, ep.SLOPE, ac, label=False, clip=(W - 400, 545, 340, 300))
            st, col = state(edge, ep.SLOPE)
            stroke_text(c, f"前刃 {edge:.0f}° / 坡 {ep.SLOPE:.0f}°", W - 230, 780, 30, INK, ac, stroke=0)
            if abs(yaw) > 4:
                st2 = "往板头飘" if yaw < 0 else "往板尾飘"
                stroke_text(c, st2, W - 230, 825, 36, GOLD, ac, stroke=0)
            else:
                stroke_text(c, st.split(" → ")[1], W - 230, 825, 36, col, ac, stroke=0)
        if cur == 0:
            kx, ky = mid(P, "kneeL", "kneeR")
            ring(c, kx, ky, 70, GOLD, a * ramp(t, ss[0][1] + 0.3, ss[0][1] + 0.6), t, label="膝盖顶向山坡")
        elif cur == 2:
            ring(c, *P[FRONT], 50, GOLD, a * ramp(t, ss[2][1] + 0.3, ss[2][1] + 0.6), t, label="前脚多压")
        elif cur == 3:
            ring(c, *P["head"], 64, GOLD, a * window(t, ss[3][1] + 0.2, ss[3][1] + 2.0, 0.3), t, label="先回头看")
            ring(c, *P[BACK], 50, GOLD, a * ramp(t, ss[3][1] + 1.8, ss[3][1] + 2.1), t, label="后脚多压")
    if d0 - 0.3 < t < d1 + 0.3:
        a = window(t, d0, d1, 0.3)
        tag(c, "怎么练", GOLD, 60, 330, a)
        card(c, 60, 440, W - 120, 200, a)
        stroke_text(c, "初级道 · 前刃", W / 2, 515, 38, DIM, a, stroke=0)
        rich_line(c, spans("推坡 {w|10 米} → 落叶飘 {w|× 2 趟}"), W / 2, 600, 52, a)
        a2 = window(t, ds[1][1], d1, 0.3)
        if a2 > 0:
            card(c, 60, 670, W - 120, 150, a2, GREEN)
            stroke_text(c, "过关标准", 120, 755, 36, GREEN, a2, align="l", stroke=0)
            stroke_text(c, "想停就停 · 先回头看", W - 120, 762, 46, INK, a2, align="r", stroke=0)


run_episode(ep, FR, OUTF, draw, zoom_fn, next_lines=[("第一次换刃", 1.0), ("从后刃到{w|前刃}", 0.8)])
