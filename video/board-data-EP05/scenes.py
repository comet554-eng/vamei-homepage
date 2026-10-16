"""单板 EP.05《跳台，为什么是重伤头号来源？》 (no voice-over)"""
import math
import numpy as np
from common import *
from art import *
from board import *

SERIES = SERIES_B
TITLE = "跳台，为什么是重伤头号来源？"

# ------------------------------------------------------------------ jump model (metres, lip at origin)
G = 9.81
LIP = math.radians(25)
TAB, KX, SL, LL = -1.0, 8.0, math.radians(30), 16.0
XE = KX + LL * math.cos(SL)


def gnd(x):
    if x < KX:
        return TAB
    if x < XE:
        return TAB - (x - KX) * math.tan(SL)
    return TAB - LL * math.sin(SL)


def gslope(x):
    return SL if KX <= x < XE else 0.0


def flight(v):
    """returns trajectory points, landing x, y, EFH"""
    t, dt, pts = 0.0, 0.002, []
    while True:
        t += dt
        x = v * math.cos(LIP) * t; y = v * math.sin(LIP) * t - G * t * t / 2
        pts.append((x, y))
        if t > 0.05 and y <= gnd(x):
            break
    vx, vy = v * math.cos(LIP), v * math.sin(LIP) - G * t
    sp, ang = math.hypot(vx, vy), math.atan2(-vy, vx)
    return np.array(pts), x, y, (sp * math.sin(ang - gslope(x))) ** 2 / (2 * G), t


CASES = [(22 / 3.6, "没飞够：砸在平台上", ICE), (36 / 3.6, "刚好：落在落地坡上", GOLD), (50 / 3.6, "飞过头：砸在坡底平地", RED)]
RES = [flight(v) for v, _, _ in CASES]


def terrain_pts():
    r0 = -(0 - TAB) / math.tan(LIP)          # kicker ramp start (x, TAB) -> lip (0, 0)
    pts = [(-14, TAB), (r0, TAB), (0.0, 0.0), (0.0, TAB)]
    pts += [(x, gnd(x)) for x in np.linspace(0.01, XE, 40)] + [(44, gnd(44))]
    return pts


def draw_jump(c, V, a, upto=None):
    pts = terrain_pts()
    poly = V.P(pts + [(44, -30), (-14, -30)])
    c.move_to(*poly[0])
    for p in poly[1:]:
        c.line_to(*p)
    c.close_path(); c.set_source_rgba(*TERRAIN_B, a); c.fill()
    S = V.P(pts)
    c.move_to(*S[0])
    for p in S[1:]:
        c.line_to(*p)
    c.set_source_rgba(*RIM_B, 0.9 * a); c.set_line_width(3); c.stroke()


# ================================================================== S1 hook
S1_SUBS = seq(["单板的重伤——脊柱、头部——有一个共同的高发地点：",
               "地形公园里的{r|跳台}。",
               "为什么偏偏是跳台？先看数据，再算一笔物理账。"], t0=0.8)
S1_DUR = end_of(S1_SUBS) + 4.6


def s1(c, t, fi):
    paint_bg(c)
    a = ramp(t, 0, 0.8)
    V = View(560, 430, 40)
    draw_jump(c, V, a)
    pts, xl, yl, efh, T = RES[1]
    k = ((t * 0.45) % 1.3) / 1.0
    i = min(len(pts) - 1, int(k * len(pts)))
    if k <= 1:
        X, Y = V.p(*pts[i])
        rider_profile(c, X, Y, 70, alpha=a, wobble=-0.3 + 0.6 * k)
    title_card(c, t, end_of(S1_SUBS) + 0.2, S1_DUR, TITLE, "美国 · 日本 · 等效下落高度")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2 USA: terrain park share and severity
S2_SUBS = seq(["美国两家雪场，5个雪季的伤病记录：",
               "{r|26.7%}的受伤发生在地形公园，伤者以年轻男性单板滑手为主。",
               "更要紧的是伤得多重：在公园里受伤，伤到头部的风险是普通雪道的{r|1.31倍}，伤到背部是{r|1.96倍}。"])
S2_DUR = end_of(S2_SUBS) + 0.8


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S2_DUR - 0.6, S2_DUR))
    T = [x for _, x, _ in S2_SUBS]
    pa = a_in * ramp(t, T[1] - 0.2, T[1] + 0.4) * (1 - ramp(t, T[2] - 0.3, T[2] + 0.2))
    if pa > 0:
        cx, cy, r = W / 2, 500, 220
        k = ease_io((t - T[1] - 0.2) / 1.0)
        c.new_path(); c.arc(cx, cy, r, 0, 2 * math.pi); c.set_source_rgba(*FAINT, 0.45 * pa); c.fill()
        c.new_path(); c.move_to(cx, cy); c.arc(cx, cy, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * 0.267 * k); c.close_path()
        c.set_source_rgba(*RED, 0.9 * pa); c.fill()
        text(c, f"{26.7 * k:.1f}%", cx + r + 40, cy - 80, 64, RED, pa, bold=True)
        text(c, "发生在地形公园", cx + r + 40, cy - 20, 32, INK, pa)
        text(c, "公园受伤 3953 例", cx, cy + r + 60, 26, DIM, pa, align="c")
    ba = a_in * ramp(t, T[2] - 0.1, T[2] + 0.5)
    if ba > 0:
        x0, w = 640, 760
        for i, (lab, v, ts) in enumerate((("头部", 1.31, T[2] + 1.2), ("背部", 1.96, T[2] + 3.0))):
            y = 360 + i * 200
            k = ease_io((t - ts) / 1.0)
            text(c, lab, x0 - 30, y + 66, 44, INK, ba, align="r", bold=True)
            c.rectangle(x0, y, w / 2, 44); c.set_source_rgba(*SKI_C, 0.7 * ba); c.fill()
            text(c, "普通雪道 1.0", x0 + 14, y + 32, 24, BG, ba, bold=True)
            if k > 0:
                c.rectangle(x0, y + 52, w / 2 * (1 + (v - 1) * k), 44); c.set_source_rgba(*RED, 0.9 * ba); c.fill()
                text(c, f"公园 {1 + (v - 1) * k:.2f}×", x0 + w / 2 * (1 + (v - 1) * k) + 16, y + 86, 36, RED, ba, bold=True)
    chapter_tag(c, "地形公园", "美国 · 两家雪场 · 2000–05", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "Injury Prevention · 2010", "公园占 26.7%；头部 RR 1.31，背部 RR 1.96", "Brooks 等", ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    model_note(c, a_in, "RR = 相对风险（公园 ÷ 普通雪道）；含双板与单板")
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3 Japan: 11 years of spinal injuries
S3_SUBS = seq(["日本新潟一家雪场，统计了11年的单板脊柱损伤：",
               "{r|66.1%}的脊柱损伤，和地形公园的跳台有关——不论水平高低。",
               "留下神经后遗症的14例里，{r|11}例和跳台有关，其中9例是{r|完全性瘫痪}。",
               "而且这11年里，发生率并没有下降。"])
S3_DUR = end_of(S3_SUBS) + 0.8


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S3_DUR - 0.6, S3_DUR))
    T = [x for _, x, _ in S3_SUBS]
    pa = a_in * ramp(t, T[1] - 0.2, T[1] + 0.4) * (1 - ramp(t, T[2] - 0.3, T[2] + 0.2))
    if pa > 0:
        cx, cy, r = W / 2 - 200, 500, 220
        k = ease_io((t - T[1] - 0.2) / 1.0)
        c.new_path(); c.arc(cx, cy, r, 0, 2 * math.pi); c.set_source_rgba(*FAINT, 0.45 * pa); c.fill()
        c.new_path(); c.move_to(cx, cy); c.arc(cx, cy, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * 0.661 * k); c.close_path()
        c.set_source_rgba(*RED, 0.9 * pa); c.fill()
        text(c, f"{66.1 * k:.1f}%", cx + r + 60, cy, 72, RED, pa, bold=True)
        text(c, "与跳台有关（113 例）", cx + r + 60, cy + 56, 32, INK, pa)
    da = a_in * ramp(t, T[2] - 0.1, T[2] + 0.5)
    if da > 0:
        k1 = ramp(t, T[2] + 1.0, T[2] + 1.8); k2 = ramp(t, T[2] + 2.6, T[2] + 3.4)
        for i in range(14):
            x = W / 2 - 13 * 100 / 2 + i * 100
            col = FAINT
            if i < 11 and k1 > 0:
                col = mix(FAINT, GOLD, k1)
            if i < 9 and k2 > 0:
                col = mix(GOLD, RED, k2)
            c.arc(x, 480, 36, 0, 2 * math.pi); c.set_source_rgba(*col, da); c.fill()
        text(c, "14 例留下神经后遗症", W / 2, 380, 36, INK, da, align="c", bold=True)
        text(c, "11 例与跳台有关", W / 2 - 200, 590, 34, GOLD, da * k1, align="c", bold=True)
        text(c, "其中 9 例完全性瘫痪", W / 2 + 260, 590, 34, RED, da * k2, align="c", bold=True)
        text(c, "发生率 5.1 / 10 万人次，11 年未下降", W / 2, 720, 34, DIM, da * ramp(t, T[3], T[3] + 0.6), align="c")
    chapter_tag(c, "脊柱", "日本新潟 · 11 年 · 单板", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "BMJ Open Sport Exerc Med · 2020", "脊柱损伤 66.1% 与跳台有关", "新潟雪场 11 年回顾研究", ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    model_note(c, a_in, "完全性瘫痪 = Frankel A 级")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4 physics: equivalent fall height
S4_SUBS = seq(["物理账在落地：落在斜的落地坡上，速度大部分顺着坡面滑走，只有{w|垂直于坡面}那一份变成冲击。",
               "把这一份换算成“从多高直接掉下来”，叫{w|等效下落高度}。",
               "拿一个普通跳台算：起跳36公里每小时，刚好落在坡上，等效高度约{b|0.7米}；",
               "22公里每小时没飞够，砸在平台上，约{w|1.3米}；",
               "50公里每小时飞过头，砸在坡底平地，约{r|10.8米}——相当于从三层多的楼上往下跳。"])
S4_DUR = end_of(S4_SUBS) + 0.8


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S4_DUR - 0.6, S4_DUR))
    T = [x for _, x, _ in S4_SUBS]
    V = View(300, 360, 34)
    draw_jump(c, V, a_in)
    order = [(1, T[2]), (0, T[3]), (2, T[4])]
    for idx, ts in order:
        pts, xl, yl, efh, _ = RES[idx]
        _, lab, col = CASES[idx]
        k = ramp(t, ts + 0.2, ts + 1.6)
        if k <= 0:
            continue
        n = max(2, int(len(pts) * k))
        polyline(c, V.P(pts[:n]), col, 0.9 * a_in, 3.5, [10, 8])
        if k >= 1:
            X, Y = V.p(xl, yl)
            c.arc(X, Y, 11, 0, 2 * math.pi); c.set_source_rgba(*col, a_in); c.fill()
            lx = {0: X - 60, 1: X + 30, 2: X - 40}[idx]; ly = {0: Y - 200, 1: Y - 60, 2: Y - 110}[idx]
            text(c, f"{efh:.1f} m", lx, ly, 46, col, a_in, bold=True, align="c" if idx != 1 else "l")
            text(c, lab, lx, ly + 40, 26, col, a_in, align="c" if idx != 1 else "l")
    # first lines: slope decomposition sketch at the good landing point
    da = a_in * ramp(t, T[0] + 1.0, T[0] + 1.8) * (1 - ramp(t, T[2] - 0.3, T[2]))
    if da > 0:
        pts, xl, yl, efh, _ = RES[1]
        X, Y = V.p(xl, yl)
        arrow(c, X - 120, Y - 60, X, Y, INK, da, 4, 18)
        arrow(c, X, Y, X + 140 * math.cos(SL), Y + 140 * math.sin(SL), GOLD, da, 4, 18)
        arrow(c, X, Y, X + 50 * math.sin(SL), Y - 50 * math.cos(SL) + 100, RED, da * 0.0, 4, 18)
        text(c, "顺坡滑走", X + 150, Y + 110, 30, GOLD, da, bold=True)
        text(c, "垂直坡面 → 冲击", X - 260, Y + 80, 30, RED, da * ramp(t, T[0] + 2.4, T[0] + 3.0), bold=True)
    chapter_tag(c, "等效下落高度", "EFH = v⊥² / 2g", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "示意计算：起跳角 25°，平台 8 m，落地坡 30°；忽略空气阻力与吸收")
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5 back falls + design
S5_SUBS = seq(["单板落地失败，常常是往后倒——屁股、后背先着地，冲击直接沿着脊柱传上去。",
               "工程师已经提出一种设计：让落地坡的形状随距离变化，不管飞多远，等效下落高度都不超过一个安全值。",
               "可大多数公园的跳台，还是“平台 + 直坡”——落点准不准，全靠你自己。"])
S5_DUR = end_of(S5_SUBS) + 0.8


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S5_DUR - 0.6, S5_DUR))
    T = [x for _, x, _ in S5_SUBS]
    fa = a_in * (1 - ramp(t, T[1] - 0.3, T[1] + 0.2))
    if fa > 0:
        gy = 760
        ground(c, gy, fa)
        kb = ease_io((t - T[0] - 0.5) / 0.6)
        p = rider_profile(c, 900, gy, 320, back=kb, alpha=fa)
        if kb > 0.8:
            for i in range(4):
                c.arc(900 - 0.44 * 320 - 0.06 * 320 * i, gy - 0.13 * 320 - 0.13 * 320 * i, 14, 0, 2 * math.pi)
                c.set_source_rgba(*RED, fa * (1 - i * 0.2)); c.fill()
            text(c, "冲击沿脊柱向上", 1200, 420, 40, RED, fa, align="c", bold=True)
    da = a_in * ramp(t, T[1] - 0.1, T[1] + 0.5)
    if da > 0:
        # constant-EFH landing: a curve getting steeper with distance (schematic)
        V = View(320, 300, 34)
        xs = np.linspace(0, 40, 80)
        prof = [(x, -1.0 - 0.012 * x * x - 0.05 * x) for x in xs]
        poly = V.P([(-6, 0), (0, 0)] + prof + [(40, -40), (-6, -40)])
        c.move_to(*poly[0])
        for q in poly[1:]:
            c.line_to(*q)
        c.close_path(); c.set_source_rgba(*TERRAIN_B, da); c.fill()
        polyline(c, V.P([(-6, 0), (0, 0)] + prof), GOLD, da, 3)
        for v in (8, 11, 14):
            tt = np.linspace(0, 3, 200)
            x = v * math.cos(LIP) * tt; y = v * math.sin(LIP) * tt - G * tt * tt / 2
            yp = -1.0 - 0.012 * x * x - 0.05 * x
            m = np.argmax(y < yp) if np.any(y < yp) else len(tt)
            polyline(c, V.P(np.stack([x[:m], y[:m]], 1)), ICE, 0.7 * da, 2.5, [8, 8])
        text(c, "恒定等效下落高度落地坡（示意）", 1300, 330, 34, GOLD, da, align="c", bold=True)
        pill_label(c, "多数公园：平台 + 直坡", 1300, 420, 30, RED, da * ramp(t, T[2], T[2] + 0.6))
    chapter_tag(c, "设计", "让落地本身变安全", ramp(t, 0.5, 1.1) * a_in)
    if t >= T[1]:
        cite_card(c, "Sports Engineering · 2015", "限制等效下落高度的跳台设计", "Levy · Hubbard · McNeil · Swedberg", ramp(t, T[1], T[1] + 0.8) * a_in)
    model_note(c, a_in, "示意 · 曲线形状非实际设计")
    subs(c, t, S5_SUBS)
    overlays(c, fi)


# ================================================================== S6 advice + end
S6_SUBS = seq(["所以进公园之前：",
               "第一，先站在旁边看一遍落地区，再从最小的台子练起；",
               "第二，控制速度——落点要在{w|落地坡}上，没飞够、飞过头，冲击都会成倍增加；",
               "第三，{w|头盔、护具}都戴上。",
               "刻滑的单板，弯能有多小？下一集，用数据说话。"])
S6_DUR = end_of(S6_SUBS) + 4.0


def s6(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S6_DUR - 1.4, S6_DUR - 0.4))
    T = [x for _, x, _ in S6_SUBS]
    la = a_in * (1 - ramp(t, T[4] - 0.2, T[4] + 0.4))
    numbered(c, [("1", "先看落地区", "从小台子练起", T[1]), ("2", "控制速度", "落点在落地坡上", T[2]), ("3", "头盔 + 护具", "", T[3])], t, la)
    end_card(c, a_in * ramp(t, T[4], T[4] + 0.8), "刻滑的单板，弯能有多小？")
    subs(c, t, S6_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, S6_DUR - 1.0, S6_DUR))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR), ("s6", s6, S6_DUR)]


def _cover_fig(c):
    V = View(140, 280, 24)
    draw_jump(c, V, 1.0)
    for idx in (1, 2):
        pts, xl, yl, efh, _ = RES[idx]
        _, lab, col = CASES[idx]
        polyline(c, V.P(pts), col, 0.95, 4, [10, 8])
        X, Y = V.p(xl, yl)
        c.arc(X, Y, 12, 0, 2 * math.pi); c.set_source_rgba(*col, 1); c.fill()
        text(c, f"{efh:.1f} m", X + (20 if idx == 1 else -30), Y - 40, 56, col, bold=True, align="l" if idx == 1 else "c")


COVER = dict(lines=["跳台为什么", "是重伤头号来源？"], stat="66%", caption="新潟 11 年单板脊柱损伤中与跳台有关的比例", color=RED, figure=_cover_fig)
COVER2 = dict(kicker="单板 · 用数据说话", lines=[("跳台", "ink"), ("重伤头号来源", "gold")], sub="脊柱损伤 66% 和跳台有关", motif="spine", seed=5)
