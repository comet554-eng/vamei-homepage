"""EP.03《一个弯里，腿要扛几倍体重？》"""
import math
from common import *
from art import *

SERIES = "双板 · 用数据说话"
TITLE = "一个弯里，腿要扛几倍体重？"
D2R = math.pi / 180


def subs(c, t, S):
    for s, a, b in S:
        subtitle(c, s, t, a, b)


def ground(c, gy, a):
    c.rectangle(0, gy, W, H - gy); c.set_source_rgba(*TERRAIN, a); c.fill()
    c.set_source_rgba(*RIM, 0.9 * a); c.rectangle(0, gy - 1.5, W, 3); c.fill()


def bw_meter(c, x, y, v, a, label="× 体重"):
    col = ICE if v < 1.5 else GOLD if v < 2.2 else RED
    text(c, f"{v:.2f}", x, y, 120, col, a, align="r", bold=True)
    text(c, label, x + 16, y, 36, DIM, a)


def force_fig(c, t, phi, a, x=820, gy=800, s=300, k=150, show_parts=1.0):
    """front-view skier leaning phi (rad) to screen-left, reaction force along the body from the feet."""
    skier_front(c, x, gy, s, lean=phi, out_edge=phi * 0.95, in_edge=phi * 0.85, alpha=a)
    F = 1 / math.cos(phi)
    fx, fy = x, gy - 30
    ex, ey = fx - math.sin(phi) * F * k, fy - math.cos(phi) * F * k
    if show_parts > 0:
        ap = a * show_parts
        c.set_dash([6, 6]); c.set_source_rgba(*DIM, 0.7 * ap); c.set_line_width(1.5)
        c.move_to(ex, ey); c.line_to(fx, ey); c.move_to(ex, ey); c.line_to(ex, fy); c.stroke(); c.set_dash([])
        arrow(c, fx, fy, fx, ey, ICE, ap, 4, 16)
        text(c, "托住你：1 倍体重", fx + 16, (fy + ey) / 2, 24, ICE, ap, bold=True)
        if math.tan(phi) * k > 6:
            arrow(c, fx, fy, ex, fy, GOLD, ap, 4, 16)
            text(c, f"推进弯里：{math.tan(phi):.2f} 倍", ex - 16, fy - 14, 24, GOLD, ap, align="r", bold=True)
    arrow(c, fx, fy, ex, ey, RED, a, 6, 22)
    return F


# ================================================================== S1
S1_SUBS = seq(["转弯的时候，你的腿上压着多少重量？",
               "只是你自己的体重吗？{w|不止}。",
               "在世界杯回转选手的弯里，腿要扛住{r|大约三倍}体重。"])
S1_DUR = end_of(S1_SUBS) + 5.0


def s1(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.8)
    gy = 800
    ground(c, gy, a_in)
    T = [a for _, a, _ in S1_SUBS]
    phi = lerp(10, 71, ease_io((t - T[1]) / 5.0)) * D2R
    F = 1 / math.cos(phi)
    force_fig(c, t, phi, a_in, show_parts=0)
    bw_meter(c, 1560, 380, F, a_in * ramp(t, T[0] + 1, T[0] + 1.6))
    te = end_of(S1_SUBS)
    ta = ramp(t, te + 0.3, te + 1.2) * (1 - ramp(t, S1_DUR - 0.7, S1_DUR))
    if ta > 0:
        c.set_source_rgba(*BG, 0.85 * ta); c.paint()
        text(c, SERIES, W / 2, 380, 30, DIM, ta, align="c", spacing=0.3)
        text(c, TITLE, W / 2, 510, 84, INK, ta, align="c", bold=True)
        c.set_source_rgba(*GOLD, 0.8 * ta); c.rectangle(W / 2 - 160, 556, 320, 2); c.fill()
        text(c, "受力推导 · 世界杯实测", W / 2, 620, 32, GOLD, ta, align="c")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2  1 / cos(phi)
S2_SUBS = seq(["转弯时，雪不只要托住你，还要把你“推”进弯里。",
               "这两股力合起来，顺着身体的方向，压在腿上。",
               "身体倾斜得越厉害，合力越大：倾斜角为 Φ 时，\n腿上的力 = 体重 ÷ cos Φ。",
               "30° 时是 1.15 倍；45° 时 1.41 倍；60° 时，{w|整整两倍}。",
               "世界杯回转选手实测立刃 66° 到 71°：\n算出来是 {r|2.4 到 3.1 倍}体重。",
               ("（平地、把人当成一个点、倾斜角≈立刃角的简化计算）", 4.0)])
S2_DUR = end_of(S2_SUBS) + 0.8


def s2_phi(t, T):
    pts = [(0, 20), (T[3], 30), (T[3] + 2.2, 45), (T[3] + 4.4, 60), (T[4], 60), (T[4] + 1.5, 65.7), (T[4] + 4.5, 71)]
    v = pts[0][1]
    for (ta, va), (tb, vb) in zip(pts, pts[1:]):
        if t >= ta:
            v = lerp(va, vb, ease_io((t - ta) / max(tb - ta, 0.01))) if t < tb else vb
    return v


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S2_DUR - 0.6, S2_DUR))
    T = [a for _, a, _ in S2_SUBS]
    gy = 800
    ground(c, gy, a_in)
    deg = s2_phi(t, T)
    F = force_fig(c, t, deg * D2R, a_in, show_parts=ramp(t, T[0] + 0.8, T[0] + 1.6))
    bw_meter(c, 1560, 380, F, a_in)
    text(c, f"倾斜 {deg:.0f}°", 1576, 450, 32, INK, a_in, align="r", bold=True)
    fa = a_in * ramp(t, T[2], T[2] + 0.8)
    text(c, "F = 体重 ÷ cos Φ", 1250, 600, 44, GOLD, fa, bold=True)
    chapter_tag(c, f"{deg:.0f}°", "倾斜角 · 腿上受力实时计算", ramp(t, 0.6, 1.2) * a_in)
    cite_card(c, "Front. Sports Act. Living · 2020", "回转实测峰值立刃 65.7° / 71.0°", "Reid · Haugen · Gilgien · Kipp · Smith", ramp(t, T[4], T[4] + 0.8) * a_in)
    model_note(c, a_in, "示意 · 平地、质点模型")
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3  measured
S3_SUBS = seq(["那真实测出来是多少？",
               "研究者让世界杯的先导滑手背上高精度定位，\n结合雪面地形，算出整条赛道上的受力：",
               "滑降平均 1.21 倍体重，超级大回转 1.42，{w|大回转 1.46}。",
               "这是一整段的平均——到了弯顶，峰值高得多：\n另一项研究测得平均约 {r|2.3 倍}，而且人和人差别很大。",
               "弯越急、立得越陡，峰值越高：回转的计算峰值到了 3 倍以上。"])
S3_DUR = end_of(S3_SUBS) + 0.8
ROWS3 = [("滑降 · 全程平均", 1.21, ICE), ("超级大回转 · 全程平均", 1.42, ICE), ("大回转 · 全程平均", 1.46, GOLD),
         ("弯顶 · 平均", 2.3, RED), ("回转 · 计算峰值（71°）", 3.07, RED)]


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S3_DUR - 0.6, S3_DUR))
    T = [a for _, a, _ in S3_SUBS]
    starts = [T[2], T[2] + 0.8, T[2] + 1.6, T[3] + 1.5, T[4]]
    x0, y0, w = 760, 260, 900
    c.set_dash([6, 6]); c.set_source_rgba(*DIM, 0.6 * a_in); c.set_line_width(1.5)
    c.move_to(x0 + w / 3.5, y0 - 20); c.line_to(x0 + w / 3.5, y0 + 5 * 100); c.stroke(); c.set_dash([])
    text(c, "1 倍体重", x0 + w / 3.5, y0 + 5 * 100 + 30, 20, DIM, a_in, align="c")
    for i, (lab, v, col) in enumerate(ROWS3):
        k = ease_io((t - starts[i]) / 0.8)
        if k <= 0:
            continue
        a = a_in * min(1, 2 * k)
        y = y0 + i * 100
        text(c, lab, x0 - 20, y + 44, 28, INK, a, align="r", bold=True)
        c.rectangle(x0, y, w * v / 3.5 * k, 64); c.set_source_rgba(*col, 0.85 * a); c.fill()
        text(c, f"{v * k:.2f}", x0 + w * v / 3.5 * k + 16, y + 46, 32, col, a, bold=True)
    chapter_tag(c, "实测", "世界杯先导滑手 dGNSS · 弯顶测力", ramp(t, 0.6, 1.2) * a_in)
    cite_card(c, "Front. Physiol. · 2018 等", "大回转全程平均 1.46 倍体重", "Gilgien 等（世界杯先导滑手）", ramp(t, T[1], T[1] + 0.8) * (1 - ramp(t, T[3], T[3] + 0.5)) * a_in)
    cite_card(c, "Science and Skiing V", "弯顶平均约 2.3 倍体重，个体差异大", "单人分析研究", ramp(t, T[3], T[3] + 0.8) * a_in)
    model_note(c, a_in, "最后一行为按 71° 的简化计算，不是实测")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4  your legs
S4_SUBS = seq(["再接上一集：外脚扛七成。", "立刃 71° 的弯里，外侧那一条腿，就要扛住约 {r|2.1 倍}体重。",
               "普通滑手立刃 30° 到 45°：腿上 1.15 到 1.4 倍体重——\n一个弯接一个弯，这就是一天下来腿会酸的原因。",
               "所以想滑得陡、弯得急，腿的力量要跟上：\n深蹲、单腿蹲，比你想的更重要。",
               ("（训练建议为常见做法；外脚七成取自上一集的研究范围）", 4.0)])
S4_DUR = end_of(S4_SUBS) + 0.8


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S4_DUR - 0.6, S4_DUR))
    T = [a for _, a, _ in S4_SUBS]
    gy = 800
    ground(c, gy, a_in)
    deg = 71 if t < T[2] else lerp(71, 38, ease_io((t - T[2]) / 2.0))
    phi = deg * D2R
    F = 1 / math.cos(phi)
    skier_front(c, 700, gy, 300, lean=phi, out_edge=phi * 0.95, in_edge=phi * 0.85, alpha=a_in)
    load_bars(c, 1180, 700, 0.7, a_in, h=300)
    out = 0.7 * F
    text(c, f"外腿 {out:.2f} 倍", 1560, 360, 64, RED if out > 1.6 else GOLD, a_in, align="c", bold=True)
    text(c, f"全身 {F:.2f} 倍 × 70%", 1560, 420, 28, DIM, a_in, align="c")
    text(c, f"立刃 {deg:.0f}°", 1560, 470, 28, INK, a_in, align="c")
    chapter_tag(c, "外腿", "全身受力 × 外脚占比（示意）", ramp(t, 0.6, 1.2) * a_in)
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5 end
S5_SUBS = seq(["弯越急，腿越重：滑雪是一项用腿“扛”出来的运动。"])
S5_DUR = end_of(S5_SUBS) + 4.0


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S5_DUR - 1.4, S5_DUR - 0.4))
    gy = 760
    snow_ground(c, gy, t, 480, a_in)
    skier(c, 760, gy, 150, 0.35 + 0.05 * math.sin(t * 2), a_in, t * 2.5)
    ea = ramp(t, end_of(S5_SUBS) - 1.0, end_of(S5_SUBS)) * a_in
    text(c, SERIES, W / 2, 300, 30, DIM, ea, align="c", spacing=0.3)
    text(c, TITLE, W / 2, 400, 56, INK, ea, align="c", bold=True)
    subs(c, t, S5_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, S5_DUR - 1.0, S5_DUR))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR)]


def _cover_fig(c):
    c.rectangle(-200, 720, 1400, 300); c.set_source_rgb(*TERRAIN); c.fill()
    c.set_source_rgba(*RIM, 0.9); c.rectangle(-200, 718, 1400, 3); c.fill()
    force_fig(c, 0, 71 * D2R, 1.0, x=700, gy=720, s=330, k=150, show_parts=0)
    text(c, "71° → 3.07 ×", 520, 200, 96, RED, 1.0, align="c", bold=True)


COVER = dict(lines=["一个弯里，腿要扛", "几倍体重？"], stat="≈ 3 倍", caption="回转峰值立刃 71° 时的计算值", color=RED, figure=_cover_fig)
