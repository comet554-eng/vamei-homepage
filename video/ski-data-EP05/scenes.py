"""EP.05《立刃角和弯有多大？》"""
import math
import numpy as np
from common import *
from art import *

SERIES = "双板 · 用数据说话"
TITLE = "立刃角和弯有多大？"
D2R = math.pi / 180
RSC = 13.0          # sidecut radius used for the worked example (illustrative)


def subs(c, t, S):
    for s, a, b in S:
        subtitle(c, s, t, a, b)


def snow_field(c, a):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, 0.16, 0.19, 0.25, a); g.add_color_stop_rgba(1, 0.09, 0.11, 0.15, a)
    c.rectangle(0, 0, W, H); c.set_source(g); c.fill()


def ski_outline(c, cx, cy, L, waist, tip, a, exag=1.0, col=GOLD, fill=True):
    """top view ski along x, waist/tip widths in px; sidecut drawn as circular arcs."""
    xs = np.linspace(-L / 2, L / 2, 80)
    half = waist / 2 + (tip - waist) / 2 * (2 * xs / L) ** 2 * exag
    top = [(cx + x, cy - h) for x, h in zip(xs, half)]
    bot = [(cx + x, cy + h) for x, h in zip(xs[::-1], half[::-1])]
    c.move_to(*top[0])
    for p in top[1:] + bot:
        c.line_to(*p)
    c.close_path()
    if fill:
        c.set_source_rgba(0.14, 0.15, 0.19, a); c.fill_preserve()
    c.set_source_rgba(*col, a); c.set_line_width(2.5); c.stroke()


def cross_section(c, x, y, theta, a, s=1.0):
    """ski cross-section tilted by theta on the snow line, with a leg indicator."""
    c.set_source_rgba(*RIM, 0.9 * a); c.rectangle(x - 260 * s, y - 1.5, 520 * s, 3); c.fill()
    c.save(); c.translate(x, y); c.rotate(-theta)
    rounded_rect(c, 0, -14 * s, 150 * s, 14 * s, 4); c.set_source_rgba(*GOLD, a); c.fill()
    c.move_to(75 * s, -14 * s); c.line_to(75 * s, -170 * s); c.set_source_rgba(*LIMB, a); c.set_line_width(26 * s); c.stroke()
    c.restore()
    # angle arc
    c.new_path(); c.arc_negative(x, y, 110 * s, 0, -theta); c.set_source_rgba(*RED, 0.9 * a); c.set_line_width(3); c.stroke()
    text(c, f"{theta / D2R:.0f}°", x + 130 * s * math.cos(-theta / 2), y + 130 * s * math.sin(-theta / 2) + 8, 30, RED, a, bold=True)


def turn_arc(c, x0, y0, R, k, a, sweep=110):
    """arc of radius R metres starting at (x0, y0) heading downwards and turning to screen-right."""
    Rp = R * k
    cx = x0 + Rp
    c.new_path(); c.set_line_width(4); c.set_source_rgba(*ICE, a)
    c.arc_negative(cx, y0, Rp, math.pi, math.pi - sweep * D2R); c.stroke()
    c.set_dash([6, 6]); c.set_source_rgba(*DIM, 0.7 * a); c.set_line_width(1.5)
    c.move_to(cx, y0); c.line_to(x0, y0); c.stroke(); c.set_dash([])
    c.arc(cx, y0, 6, 0, 2 * math.pi); c.set_source_rgba(*DIM, a); c.fill()
    text(c, f"R = {R:.1f} m", (cx + x0) / 2, y0 - 14, 28, ICE, a, align="c", bold=True)


# ================================================================== S1
S1_SUBS = seq(["同一块板，有人弯得大，有人弯得小。差别在哪？",
               "答案在一个角度：{w|立刃角}。"])
S1_DUR = end_of(S1_SUBS) + 5.0


def s1(c, t, fi):
    snow_field(c, 1.0)
    a_in = ramp(t, 0, 0.8)
    down = lerp(0, H, ease_io((t - 0.4) / 5.0))
    for cx, amp, per, lab in ((560, 260, 900, "大弯"), (1360, 120, 360, "小弯")):
        ys = np.linspace(0, down, 200)
        for off in (-8, 8):
            c.move_to(cx + amp * math.sin(2 * math.pi * ys[0] / per) + off, ys[0])
            for y in ys[1:]:
                c.line_to(cx + amp * math.sin(2 * math.pi * y / per) + off, y)
            c.set_source_rgba(*RIM, 0.85 * a_in); c.set_line_width(2.2); c.stroke()
        pill_label(c, lab, cx, 120, 32, ICE, a_in * ramp(t, 1.0, 1.6))
    te = end_of(S1_SUBS)
    ta = ramp(t, te + 0.3, te + 1.2) * (1 - ramp(t, S1_DUR - 0.7, S1_DUR))
    if ta > 0:
        c.set_source_rgba(*BG, 0.88 * ta); c.paint()
        text(c, SERIES, W / 2, 380, 30, DIM, ta, align="c", spacing=0.3)
        text(c, TITLE, W / 2, 510, 92, INK, ta, align="c", bold=True)
        c.set_source_rgba(*GOLD, 0.8 * ta); c.rectangle(W / 2 - 160, 556, 320, 2); c.fill()
        text(c, "侧切 · 立刃 · 世界杯实测", W / 2, 620, 32, GOLD, ta, align="c")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2 sidecut
S2_SUBS = seq(["从上往下看，雪板的两条边不是直的，中间窄、两头宽——",
               "它是一个大圆上的一段弧。这个圆的半径，叫{w|侧切半径}。",
               "板平放在雪上，它只会直着走；要转弯，得先把它{w|立起来}。",
               ("（为了看清，画面把侧切放大了很多倍）", 3.4)])
S2_DUR = end_of(S2_SUBS) + 0.8


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S2_DUR - 0.6, S2_DUR))
    T = [a for _, a, _ in S2_SUBS]
    cx, cy, L = W / 2, 430, 1100
    ski_outline(c, cx, cy, L, 70, 150, a_in, exag=1.0)
    ca = a_in * ramp(t, T[1], T[1] + 1.0)
    if ca > 0:
        # circle through tip, waist, tail of the lower edge (exaggerated)
        sag = (150 - 70) / 2
        R = ((L / 2) ** 2 + sag ** 2) / (2 * sag)
        ccy = cy + 35 + R
        c.new_path(); c.arc(cx, ccy, R, -math.pi / 2 - 0.75, -math.pi / 2 + 0.75)
        c.set_source_rgba(*ICE, ca); c.set_line_width(2); c.set_dash([10, 8]); c.stroke(); c.set_dash([])
        c.move_to(cx, cy + 35); c.line_to(cx, min(ccy, 900)); c.set_source_rgba(*ICE, 0.7 * ca); c.stroke()
        text(c, "侧切半径 →", cx + 20, 760, 30, ICE, ca, bold=True)
        text(c, "（圆心在很远的地方）", cx + 20, 800, 22, DIM, ca)
    chapter_tag(c, "侧切", "雪板的边是一段圆弧", ramp(t, 0.6, 1.2) * a_in)
    model_note(c, a_in, "示意 · 侧切夸大")
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3 R = Rsc cos theta
S3_SUBS = seq(["把板立起来、压弯，刃就贴着雪划出一道弧。",
               "理想刻滑时：弯的半径 ≈ 侧切半径 × cos 立刃角。",
               "拿一块侧切 13 米的板算：立 30°，弯半径 11.3 米；立 45°，9.2 米；",
               "立 60°，6.5 米；立 70°，只剩 {r|4.4 米}。",
               "立得越陡，弯越小。"])
S3_DUR = end_of(S3_SUBS) + 0.8


def s3_theta(t, T):
    pts = [(0, 5), (T[0] + 1, 20), (T[2], 30), (T[2] + 3.0, 45), (T[3], 60), (T[3] + 3.0, 70), (T[4], 70)]
    v = pts[0][1]
    for (ta, va), (tb, vb) in zip(pts, pts[1:]):
        if t >= ta:
            v = lerp(va, vb, ease_io((t - ta) / max(tb - ta, 0.01))) if t < tb else vb
    if t > T[4]:
        v = 45 + 25 * math.sin((t - T[4]) * 0.9)
    return v


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S3_DUR - 0.6, S3_DUR))
    T = [a for _, a, _ in S3_SUBS]
    th = s3_theta(t, T)
    R = RSC * math.cos(th * D2R)
    cross_section(c, 420, 640, th * D2R, a_in)
    text(c, "立刃角（顺着板看）", 420, 720, 24, DIM, a_in, align="c")
    turn_arc(c, 900, 220, R, 40, a_in)
    text(c, "俯视：刃划出的弧", 1150, 860, 24, DIM, a_in, align="c")
    fa = a_in * ramp(t, T[1], T[1] + 0.8)
    text(c, "R = 13 m × cos θ", 1500, 330, 40, GOLD, fa, bold=True)
    chapter_tag(c, f"{R:.1f} m", f"立刃 {th:.0f}° · 侧切 13 m（示意）", ramp(t, 0.6, 1.2) * a_in)
    model_note(c, a_in, "理想刻滑 · Howe (2001) 公式 · 侧切半径为示意取值")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4 measured
S4_SUBS = seq(["真实的世界杯呢？研究者给回转选手装上三维动作捕捉：",
               "峰值立刃 {r|65.7°} 到 {r|71°}，最小的弯半径只有 {r|4 到 5 米}。",
               "他们把实测的轨迹和这个公式对比：{w|吻合得很好}。",
               "不过立刃小的时候，板会打滑，实际的弯比公式大——\n研究者说，这部分还需要更多研究。"])
S4_DUR = end_of(S4_SUBS) + 0.8


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S4_DUR - 0.6, S4_DUR))
    T = [a for _, a, _ in S4_SUBS]
    cards = [("10 m 门距", "65.7°", "3.96 m"), ("13 m 门距", "71.0°", "4.94 m")]
    for i, (lab, e, r) in enumerate(cards):
        a = a_in * ramp(t, T[1] + i * 0.8, T[1] + i * 0.8 + 0.8)
        x = 620 + i * 680
        rounded_rect(c, x - 280, 260, 560, 360, 16); c.set_source_rgba(0.03, 0.04, 0.05, 0.9 * a); c.fill_preserve()
        c.set_source_rgba(*GOLD, 0.6 * a); c.set_line_width(1.5); c.stroke()
        text(c, lab, x, 330, 32, INK, a, align="c", bold=True)
        text(c, "峰值立刃", x - 130, 420, 24, DIM, a, align="c")
        text(c, e, x - 130, 500, 64, RED, a, align="c", bold=True)
        text(c, "最小弯半径", x + 130, 420, 24, DIM, a, align="c")
        text(c, r, x + 130, 500, 64, ICE, a, align="c", bold=True)
    ma = a_in * ramp(t, T[2], T[2] + 0.8)
    pill_label(c, "实测轨迹 ≈ Howe 公式", W / 2, 740, 34, GOLD, ma)
    la = a_in * ramp(t, T[3], T[3] + 0.8)
    pill_label(c, "小立刃角：打滑 → 实际弯更大", W / 2, 820, 28, DIM, la)
    chapter_tag(c, "实测", "世界杯水平回转 · 三维动作捕捉", ramp(t, 0.6, 1.2) * a_in)
    cite_card(c, "Front. Sports Act. Living 2:25 · 2020", "高立刃时实测与 Howe 公式吻合良好", "Reid · Haugen · Gilgien · Kipp · Smith", ramp(t, T[0], T[0] + 0.8) * a_in)
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5 practice + end
S5_SUBS = seq(["所以想把弯滑小，不是去拧板，而是把板{w|立起来}。",
               "立得越陡，身体倾斜越大——上一集说过，腿要扛的力也越大。"])
S5_DUR = end_of(S5_SUBS) + 4.0


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S5_DUR - 1.4, S5_DUR - 0.4))
    th = 30 + 35 * (0.5 + 0.5 * math.sin(t * 0.9))
    cross_section(c, 560, 620, th * D2R, a_in)
    turn_arc(c, 1000, 200, RSC * math.cos(th * D2R), 40, a_in)
    ea = ramp(t, end_of(S5_SUBS) - 0.5, end_of(S5_SUBS) + 0.3) * a_in
    if ea > 0:
        c.set_source_rgba(*BG, 0.8 * ea); c.paint()
        text(c, SERIES, W / 2, 400, 30, DIM, ea, align="c", spacing=0.3)
        text(c, TITLE, W / 2, 500, 60, INK, ea, align="c", bold=True)
    subs(c, t, S5_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, S5_DUR - 1.0, S5_DUR))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR)]


def _cover_fig(c):
    cross_section(c, 260, 620, 66 * D2R, 1.0, s=1.3)
    turn_arc(c, 520, 160, 4.9, 70, 1.0, sweep=120)


COVER = dict(lines=["立刃角和", "弯有多大？"], stat="4–5 米", caption="世界杯回转最小弯半径（峰值立刃 66°–71°）", color=RED, figure=_cover_fig)
