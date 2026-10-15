"""单板 EP.06《刻滑的单板，弯能有多小？》 (no voice-over)"""
import math
import numpy as np
from common import *
from art import *
from board import *

SERIES = SERIES_B
TITLE = "刻滑的单板，弯能有多小？"
G = 9.81
RSC = 7.0                                     # sidecut radius (m), typical snowboards 6–10 m
ANG = [30, 45, 60, 70]


def turn_r(deg):
    return RSC * math.cos(math.radians(deg))


def speed_kmh(deg):                           # flat-ground balance: tan(theta) = v^2 / (g R)
    return math.sqrt(G * RSC * math.sin(math.radians(deg))) * 3.6


def load(deg):
    return 1 / math.cos(math.radians(deg))


# ================================================================== S1 hook
S1_SUBS = seq(["单板刻滑，雪面上只留下一道细细的弧线，没有一点搓雪的雪雾。",
               "这道弧能有多小，一半由板决定，一半由你立多大的刃决定。",
               "今天用一个公式，把它算出来。"], t0=0.8)
S1_DUR = end_of(S1_SUBS) + 4.6


def s1(c, t, fi):
    paint_bg(c)
    a = ramp(t, 0, 0.8)
    # S-shaped carve lines drawn on the snow (top view)
    k = ramp(t, 0.4, 4.0)
    xs = np.linspace(200, 1720, 300)
    ys = 520 + 170 * np.sin((xs - 200) / 1520 * 3 * math.pi)
    n = max(2, int(len(xs) * k))
    for off, al in ((-10, 0.9), (10, 0.5)):
        polyline(c, np.stack([xs[:n], ys[:n] + off], 1), RIM_B, a * al, 2.5)
    if n > 2:
        bx, by = xs[n - 1], ys[n - 1]
        ang = math.atan2(ys[n - 1] - ys[n - 2], xs[n - 1] - xs[n - 2])
        c.save(); c.translate(bx, by); c.rotate(ang); board_top(c, 0, 0, 160, a, angles=(15, -15)); c.restore()
    title_card(c, t, end_of(S1_SUBS) + 0.2, S1_DUR, TITLE, "侧切半径 · 立刃角 · 需要的速度")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2 sidecut radius
S2_SUBS = seq(["从上往下看，单板的两条刃不是直线，而是一段圆弧。",
               "把这段弧补成一个整圆，它的半径就叫{w|侧切半径}。",
               "常见的单板，侧切半径大约在{w|6到10米}之间；下面拿一块{w|7米}的板来算。"])
S2_DUR = end_of(S2_SUBS) + 0.8


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S2_DUR - 0.6, S2_DUR))
    T = [x for _, x, _ in S2_SUBS]
    k = 640                                   # px per metre
    cx, cy = W / 2, 330
    L, waist, tipw = 1.56, 0.25, 0.29
    depth = (tipw - waist) / 2
    # exaggerate the sidecut 6x so the arc is visible
    ex = 2.5
    xs = np.linspace(-L / 2, L / 2, 60)
    sag = depth * ex * (1 - (2 * xs / L) ** 2)
    top = np.stack([cx + xs * k, cy - (tipw / 2 - sag) * k], 1)
    bot = np.stack([cx + xs[::-1] * k, cy + (tipw / 2 - sag[::-1]) * k], 1)
    c.move_to(*top[0])
    for p in list(top[1:]) + list(bot):
        c.line_to(*p)
    c.close_path(); c.set_source_rgba(*mix(BOARD, GOLD, 0.25), a_in); c.fill_preserve()
    c.set_source_rgba(*GOLD, 0.9 * a_in); c.set_line_width(3); c.stroke()
    ea = a_in * ramp(t, T[0] + 1.0, T[0] + 1.8)
    polyline(c, bot[::-1], RED, ea, 5)
    # complete the circle under the bottom edge
    ca = a_in * ramp(t, T[1], T[1] + 1.4)
    if ca > 0:
        # circle through the three points of the (exaggerated) bottom edge
        p1, p2, p3 = bot[-1], bot[len(bot) // 2], bot[0]
        ax, ay = p1; bx, by = p2; qx, qy = p3
        d = 2 * (ax * (by - qy) + bx * (qy - ay) + qx * (ay - by))
        ux = ((ax ** 2 + ay ** 2) * (by - qy) + (bx ** 2 + by ** 2) * (qy - ay) + (qx ** 2 + qy ** 2) * (ay - by)) / d
        uy = ((ax ** 2 + ay ** 2) * (qx - bx) + (bx ** 2 + by ** 2) * (ax - qx) + (qx ** 2 + qy ** 2) * (bx - ax)) / d
        rr = math.hypot(ax - ux, ay - uy)
        c.new_path(); c.arc(ux, uy, rr, -math.pi / 2 - 2.6 * ca, -math.pi / 2 + 2.6 * ca)
        c.set_source_rgba(*RED, 0.5 * ca); c.set_dash([10, 10]); c.set_line_width(2.5); c.stroke(); c.set_dash([])
        c.move_to(ux, uy - rr); c.line_to(ux, 820); c.set_source_rgba(*RED, 0.8 * ca); c.set_line_width(2); c.stroke()
        arrow_head(c, ux, 820, math.pi / 2, 18, RED, ca)
        text(c, "↓ 圆心在很远的下方", ux + 20, 800, 26, DIM, ca)
        text(c, "侧切半径", ux + 20, 560, 40, RED, ca, bold=True)
    ra = a_in * ramp(t, T[2], T[2] + 0.6)
    pill_label(c, "常见单板 6–10 m  ·  本集取 7 m", W / 2, 230, 32, GOLD, ra)
    chapter_tag(c, "侧切半径", "板刃是一段圆弧", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "示意 · 侧切弧度放大 2.5 倍以便看清")
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3 R = Rsc cos(theta)
S3_SUBS = seq(["板立起来、被压弯，刃就贴着雪划出一道弧。理想刻滑时：",
               "{w|弯半径 ≈ 侧切半径 × cos（立刃角）}。",
               "7米的板：立30°，弯半径6.1米；立45°，4.9米；",
               "立60°，3.5米；立到70°，只剩{r|2.4米}——还不到一辆小轿车的长度。"])
S3_DUR = end_of(S3_SUBS) + 0.8


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S3_DUR - 0.6, S3_DUR))
    T = [x for _, x, _ in S3_SUBS]
    fa = a_in * ramp(t, T[1] - 0.1, T[1] + 0.5)
    text(c, "R = R侧切 · cos θ", W / 2, 260, 64, GOLD, fa, align="c", bold=True)
    # concentric arcs, top view, scale 60 px / m, centred bottom-left
    ox, oy, k = 380, 860, 75
    st = [T[2] + 0.2, T[2] + 2.6, T[3] + 0.2, T[3] + 2.2]
    cols = [ICE, ICE, GOLD, RED]
    c.new_path(); c.arc(ox, oy, RSC * k, -math.pi / 2, 0); c.set_source_rgba(*DIM, 0.6 * fa); c.set_dash([8, 8]); c.set_line_width(2); c.stroke(); c.set_dash([])
    text(c, "R侧切 = 7 m", ox + RSC * k * 0.72 + 10, oy - RSC * k * 0.72 - 10, 26, DIM, fa)
    for deg, s0, col in zip(ANG, st, cols):
        kk = ease_io((t - s0) / 0.9)
        if kk <= 0:
            continue
        R = turn_r(deg)
        c.new_path(); c.arc(ox, oy, R * k, -math.pi / 2, -math.pi / 2 + math.pi / 2 * kk)
        c.set_source_rgba(*col, a_in); c.set_line_width(5); c.stroke()
        text(c, f"{deg}° → {R:.1f} m", 1080, 400 + ANG.index(deg) * 95, 48, col, a_in * min(1, kk * 2), bold=True)
    c.arc(ox, oy, 8, 0, 2 * math.pi); c.set_source_rgba(*INK, fa); c.fill()
    ca = a_in * ramp(t, T[3] + 3.0, T[3] + 3.8)
    if ca > 0:
        rounded_rect(c, 1080, 800, 2.4 * 75 * 1.8, 50, 18); c.set_source_rgba(*FAINT, ca); c.fill()
        text(c, "小轿车约 4.5 m", 1080 + 2.4 * 75 * 0.9, 836, 24, INK, ca, align="c")
    chapter_tag(c, "理想刻滑", "弯半径随立刃角变小", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "Can J Phys · 2004", "理想刻滑方程：弯半径 ≈ R侧切 · cos θ", "Jentschura · Fahrbach", ramp(t, T[1], T[1] + 0.8) * a_in)
    model_note(c, a_in, "计算值 · 理想刻滑（无侧滑），板完全贴雪弯曲")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4 the speed you need
S4_SUBS = seq(["可是刃立得起来，靠的是速度：人斜着不倒，得让离心力和重力刚好平衡。",
               "在平地上近似算，立的角度越大，需要的速度也越大：",
               "立45°，约25公里每小时；立60°，约28；立70°，约29。",
               "有意思的是，从30°到70°，速度只多了8公里每小时——因为弯同时在变小。",
               "速度不够还硬立刃，人只会往弯里倒。"])
S4_DUR = end_of(S4_SUBS) + 0.8


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S4_DUR - 0.6, S4_DUR))
    T = [x for _, x, _ in S4_SUBS]
    # chart: x = edge angle 20..75, y = speed km/h 0..35
    x0, y0, w, h = 380, 820, 1100, 480
    ax = lambda d: x0 + (d - 20) / 55 * w
    ay = lambda v: y0 - v / 35 * h
    ca = a_in * ramp(t, T[1] - 0.2, T[1] + 0.4)
    c.set_source_rgba(*FAINT, ca); c.rectangle(x0, y0, w, 2); c.fill(); c.rectangle(x0, y0 - h, 2, h); c.fill()
    for d in (20, 30, 40, 50, 60, 70):
        text(c, f"{d}°", ax(d), y0 + 40, 24, DIM, ca, align="c")
    for v in (10, 20, 30):
        text(c, f"{v}", x0 - 20, ay(v) + 8, 24, DIM, ca, align="r")
        c.set_source_rgba(*FAINT, 0.3 * ca); c.rectangle(x0, ay(v), w, 1); c.fill()
    text(c, "立刃角", x0 + w, y0 + 80, 26, DIM, ca, align="r")
    text(c, "需要的速度 km/h", x0, y0 - h - 24, 26, DIM, ca)
    k = ease_io((t - T[1] - 0.4) / 2.0)
    ds = np.linspace(20, 20 + 55 * k, 80)
    if k > 0:
        polyline(c, np.stack([[ax(d) for d in ds], [ay(speed_kmh(d)) for d in ds]], 1), GOLD, ca, 4)
    for deg, ts in zip((45, 60, 70), (T[2], T[2] + 2.0, T[2] + 3.6)):
        kk = ramp(t, ts, ts + 0.5)
        if kk > 0:
            X, Y = ax(deg), ay(speed_kmh(deg))
            c.arc(X, Y, 10, 0, 2 * math.pi); c.set_source_rgba(*GOLD, a_in * kk); c.fill()
            text(c, f"{speed_kmh(deg):.0f}", X, Y - 24, 36, INK, a_in * kk, align="c", bold=True)
    ba = a_in * ramp(t, T[3], T[3] + 0.6)
    if ba > 0:
        X1, Y1, X2, Y2 = ax(30), ay(speed_kmh(30)), ax(70), ay(speed_kmh(70))
        c.set_source_rgba(*ICE, ba); c.set_line_width(2); c.set_dash([6, 6])
        c.move_to(X1, Y1); c.line_to(X2, Y1); c.line_to(X2, Y2); c.stroke(); c.set_dash([])
        text(c, f"+{speed_kmh(70) - speed_kmh(30):.0f} km/h", X2 + 20, (Y1 + Y2) / 2 + 10, 34, ICE, ba, bold=True)
        text(c, f"30°：{speed_kmh(30):.0f} km/h", X1, Y1 + 50, 28, ICE, ba, align="c")
    la = a_in * ramp(t, T[0] + 0.5, T[0] + 1.2) * (1 - ramp(t, T[1] - 0.3, T[1]))
    text(c, "tan θ = v² / (g · R)", W / 2, 420, 60, GOLD, la, align="c", bold=True)
    text(c, "R = R侧切 · cos θ  ⇒  v = √(g · R侧切 · sin θ)", W / 2, 520, 40, INK, la, align="c")
    chapter_tag(c, "需要的速度", "倾斜平衡", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "计算值 · 平地近似，忽略坡度、身体倾角与立刃角的差别")
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5 load + boot-out
S5_SUBS = seq(["立得越陡，腿上的负担也越大：立60°，要扛住约{w|2倍}体重；立70°，接近{r|3倍}。",
               "单板还有一个双板没有的限制：鞋子横跨在板上，脚尖、脚跟会伸出板边。",
               "立刃一大，伸出去的鞋先碰到雪——这叫{r|拖靴}（boot out），板会被直接撬离雪面。",
               "所以刻滑板往往更宽，或者把固定器角度调大，让鞋别伸出去太多。"])
S5_DUR = end_of(S5_SUBS) + 0.8


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S5_DUR - 0.6, S5_DUR))
    T = [x for _, x, _ in S5_SUBS]
    la = a_in * (1 - ramp(t, T[1] - 0.3, T[1] + 0.2))
    if la > 0:
        x0, y0 = 620, 300
        for i, deg in enumerate(ANG):
            kk = ease_io((t - T[0] - 0.4 - i * 0.6) / 0.8)
            if kk <= 0:
                continue
            y = y0 + i * 120; v = load(deg)
            text(c, f"{deg}°", x0 - 30, y + 50, 40, INK, la, align="r", bold=True)
            col = RED if deg >= 70 else GOLD if deg >= 60 else ICE
            c.rectangle(x0, y, 300 * v * kk, 70); c.set_source_rgba(*col, 0.88 * la); c.fill()
            text(c, f"{v * kk:.2f} 倍体重", x0 + 300 * v * kk + 20, y + 50, 38, col, la, bold=True)
        text(c, "F / mg = 1 / cos θ", x0, y0 - 40, 30, DIM, la)
    ba = a_in * ramp(t, T[1] - 0.1, T[1] + 0.5)
    if ba > 0:
        gy = 760
        ground(c, gy, ba)
        e1 = math.radians(20 + 40 * ease_io((t - T[2]) / 1.4))
        mark = ramp(t, T[2] + 1.2, T[2] + 1.6)
        board_section(c, 760, gy, 300, e1, ba, overhang=0.18, boot_mark=mark)
        board_section(c, 1300, gy, 300, e1 if t < T[3] else math.radians(60), ba * ramp(t, T[3], T[3] + 0.6), overhang=0.0)
        text(c, "鞋伸出板边", 640, 330, 36, INK, ba, align="c", bold=True)
        text(c, "（从板头方向看：板的横截面 + 鞋）", W / 2, 260, 28, DIM, ba, align="c")
        if mark > 0:
            c.new_path(); c.arc(760 + 0.18 * 300 * 0.5, gy, 34, 0, 2 * math.pi); c.set_source_rgba(*RED, ba * mark); c.set_line_width(5); c.stroke()
            text(c, "鞋先碰雪 → 拖靴", 640, 390, 34, RED, ba * mark, align="c", bold=True)
        text(c, "更宽的板 / 更大的固定器角度", 1220, 330, 32, GOLD, ba * ramp(t, T[3], T[3] + 0.6), align="c", bold=True)
    chapter_tag(c, "代价", "腿的负担 · 拖靴", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "负担为计算值（理想圆周、平地）；板与鞋为示意")
    subs(c, t, S5_SUBS)
    overlays(c, fi)


# ================================================================== S6 summary + end
S6_SUBS = seq(["想把单板的弯刻小，三件事：",
               "第一，把板{w|立起来}——弯半径跟着 cos θ 一起变小；",
               "第二，{w|速度给够}——立得越陡，越需要速度撑住；",
               "第三，别让鞋伸出板边太多——不然立到一半就拖靴。",
               "往后摔，还是往前摔？下一集，用数据说话。"])
S6_DUR = end_of(S6_SUBS) + 4.0


def s6(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S6_DUR - 1.4, S6_DUR - 0.4))
    T = [x for _, x, _ in S6_SUBS]
    la = a_in * (1 - ramp(t, T[4] - 0.2, T[4] + 0.4))
    numbered(c, [("1", "立起来", "R = R侧切 · cos θ", T[1]), ("2", "速度给够", "70° 约 29 km/h", T[2]), ("3", "别拖靴", "板宽 / 固定器角度", T[3])], t, la)
    end_card(c, a_in * ramp(t, T[4], T[4] + 0.8), "往后摔，还是往前摔？")
    subs(c, t, S6_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, S6_DUR - 1.0, S6_DUR))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR), ("s6", s6, S6_DUR)]


def _cover_fig(c):
    ox, oy, k = 120, 760, 90
    c.new_path(); c.arc(ox, oy, RSC * k, -math.pi / 2, 0); c.set_source_rgba(*DIM, 0.6); c.set_dash([8, 8]); c.set_line_width(3); c.stroke(); c.set_dash([])
    for deg, col in zip(ANG, [ICE, ICE, GOLD, RED]):
        c.new_path(); c.arc(ox, oy, turn_r(deg) * k, -math.pi / 2, 0); c.set_source_rgba(*col, 1); c.set_line_width(7); c.stroke()
        text(c, f"{deg}°", ox + turn_r(deg) * k * 0.74 + 10, oy - turn_r(deg) * k * 0.74 - 10, 34, col, bold=True)


COVER = dict(lines=["刻滑的单板", "弯能有多小？"], stat="2.4 m", caption="侧切 7 m 的板立刃 70° 时的弯半径（计算值）", color=RED, figure=_cover_fig)
