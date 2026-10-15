"""单板 EP.09《U 型池，选手到底飞多高？》 (no voice-over)"""
import math
import numpy as np
from common import *
from art import *
from board import *

SERIES = SERIES_B
TITLE = "U 型池，选手到底飞多高？"
G = 9.81
WALL = 6.7            # superpipe wall height (m), 22 ft
AIR = 7.72            # Guinness record above the lip (m)
V_UP = math.sqrt(2 * G * AIR)
T_AIR = 2 * V_UP / G


def pipe(c, ox, oy, k, a, width=19.0):
    """cross-section of a superpipe: flat bottom + two quarter-circle walls of radius WALL, then vertical extension.
    ox, oy = centre of the flat bottom; k = px per metre."""
    flat = width - 2 * WALL
    pts = [(-width / 2 - 3, WALL)]
    for th in np.linspace(math.pi, 1.5 * math.pi, 30):              # left wall
        pts.append((-flat / 2 + WALL * math.cos(th), WALL + WALL * math.sin(th)))
    pts += [(flat / 2, 0.0)]
    for th in np.linspace(1.5 * math.pi, 2 * math.pi, 30):          # right wall
        pts.append((flat / 2 + WALL * math.cos(th), WALL + WALL * math.sin(th)))
    pts.append((width / 2 + 3, WALL))
    S = [(ox + x * k, oy - y * k) for x, y in pts]
    c.move_to(*S[0])
    for p in S[1:]:
        c.line_to(*p)
    c.line_to(S[-1][0], oy + 300); c.line_to(S[0][0], oy + 300); c.close_path()
    c.set_source_rgba(*TERRAIN_B, a); c.fill()
    c.move_to(*S[0])
    for p in S[1:]:
        c.line_to(*p)
    c.set_source_rgba(*RIM_B, 0.9 * a); c.set_line_width(3); c.stroke()
    return (ox - (flat / 2 + WALL) * k, oy - WALL * k), (ox + (flat / 2 + WALL) * k, oy - WALL * k)


# ================================================================== S1 hook
S1_SUBS = seq(["单板U型池：两面雪墙，选手从这边冲上去，飞出池沿，在空中翻转，再落回墙上。",
               "电视上看，他们轻飘飘的。",
               "可到底飞了多高？算一下，会吓一跳。"], t0=0.8)
S1_DUR = end_of(S1_SUBS) + 4.6


def s1(c, t, fi):
    paint_bg(c)
    a = ramp(t, 0, 0.8)
    k = 48
    L, R = pipe(c, W / 2, 780, k, a)
    # rider loops up the right wall
    ph = (t * 0.35) % 1.0
    if ph < 0.8:
        u = ph / 0.8
        x = R[0] + 10; y = R[1] - (V_UP * (u * T_AIR) - G * (u * T_AIR) ** 2 / 2) * k * 0.55
        rider_profile(c, x, y, 70, alpha=a, wobble=u * 2 * math.pi)
    title_card(c, t, end_of(S1_SUBS) + 0.2, S1_DUR, TITLE, "池墙高度 · 吉尼斯纪录 · 起飞速度")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2 the pipe
S2_SUBS = seq(["先看池子。奥运级的超级U型池，墙高大约{w|6.7米}——22英尺，两层多楼高；",
               "墙的上半截几乎是竖直的，整条池子顺着{w|16到18度}的坡往下延伸。"])
S2_DUR = end_of(S2_SUBS) + 0.8


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S2_DUR - 0.6, S2_DUR))
    T = [x for _, x, _ in S2_SUBS]
    k = 52
    L, R = pipe(c, W / 2, 740, k, a_in)
    da = a_in * ramp(t, T[0] + 0.6, T[0] + 1.4)
    dim_line(c, R[0] + 60, 740, R[0] + 60, R[1], "6.7 m", da, size=40, off=(70, 10), col=GOLD)
    # a person for scale on the floor
    hk = ramp(t, T[0] + 1.6, T[0] + 2.4)
    rider_profile(c, W / 2, 740, 1.75 * k, alpha=a_in * hk)
    text(c, "人 ≈ 1.75 m", W / 2, 740 - 2.1 * k, 24, DIM, a_in * hk, align="c")
    sa = a_in * ramp(t, T[1], T[1] + 0.6)
    pill_label(c, "整条池子顺坡 16–18°", W / 2, 300, 32, ICE, sa)
    chapter_tag(c, "池子", "超级 U 型池 · 横截面", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "Britannica · 单板 U 型池", "池墙约 3.3–6.7 m，坡度 16–18°", "超级 U 型池墙高可达 22 ft", ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    model_note(c, a_in, "示意 · 横截面按比例简化")
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3 the record
S3_SUBS = seq(["那选手能飞多高？2026年3月，瑞士莱克斯，日本选手平野海祝，飞出了池沿以上{r|7.72米}——",
               "吉尼斯世界纪录，U型池单板最高的一跳。",
               "如果从池底算，6.7加7.7，超过{r|14米}——差不多五层楼。"])
S3_DUR = end_of(S3_SUBS) + 0.8


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S3_DUR - 0.6, S3_DUR))
    T = [x for _, x, _ in S3_SUBS]
    k = 42
    L, R = pipe(c, W / 2 - 200, 820, k, a_in)
    kk = ease_io((t - T[0] - 0.8) / 1.6)
    top = R[1] - AIR * k * kk
    c.set_source_rgba(*RED, 0.9 * a_in); c.set_line_width(3); c.set_dash([10, 8])
    c.move_to(R[0], R[1]); c.line_to(R[0], top); c.stroke(); c.set_dash([])
    rider_profile(c, R[0], top, 60, alpha=a_in * (kk > 0.02))
    text(c, f"{AIR * kk:.2f} m", R[0] + 50, (R[1] + top) / 2, 56, RED, a_in * (kk > 0.02), bold=True)
    ta = a_in * ramp(t, T[2], T[2] + 0.8)
    if ta > 0:
        dim_line(c, R[0] + 300, 820, R[0] + 300, top, f"{WALL + AIR:.1f} m", ta, size=44, off=(90, 10), col=GOLD)
        for i in range(5):                      # five storeys of ~3 m for scale
            y0 = 820 - (i + 1) * 3.0 * k
            c.rectangle(R[0] + 430, y0, 120, 3.0 * k - 6); c.set_source_rgba(*FAINT, 0.6 * ta); c.fill()
        text(c, "≈ 5 层楼", R[0] + 490, 820 - 15.6 * k, 30, GOLD, ta, align="c", bold=True)
    chapter_tag(c, "纪录", "U 型池单板最高的一跳", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "吉尼斯世界纪录 · 2026", "池沿以上 7.72 m（25 ft 4 in）", "平野海祝 · 瑞士莱克斯", ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    model_note(c, a_in, "按 6.7 m 池墙计算；每层楼按约 3 m 示意")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4 physics: takeoff speed & air time
S4_SUBS = seq(["飞7.72米高，离开池沿那一刻，竖直往上的速度要多大？",
               "v = √(2gh)：大约{w|每秒12.3米}，也就是{w|每小时44公里}——这还只是竖直的那一份。",
               "从飞出到落回池沿，空中时间 t = 2v / g：约{w|2.5秒}。",
               "2.5秒，足够在空中转上好几圈——这就是为什么飞得越高，动作越难。"])
S4_DUR = end_of(S4_SUBS) + 0.8


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S4_DUR - 0.6, S4_DUR))
    T = [x for _, x, _ in S4_SUBS]
    fa = a_in * ramp(t, T[1] - 0.2, T[1] + 0.4)
    text(c, "v = √(2 g h)", 560, 360, 64, GOLD, fa, align="c", bold=True)
    text(c, f"= √(2 × 9.81 × 7.72) ≈ {V_UP:.1f} m/s", 560, 450, 38, INK, fa, align="c")
    text(c, f"≈ {V_UP * 3.6:.0f} km/h（竖直分量）", 560, 520, 44, GOLD, fa, align="c", bold=True)
    ta = a_in * ramp(t, T[2] - 0.2, T[2] + 0.4)
    text(c, "t = 2 v / g", 560, 650, 56, ICE, ta, align="c", bold=True)
    text(c, f"≈ {T_AIR:.1f} s", 560, 730, 56, ICE, ta, align="c", bold=True)
    # height vs time curve
    x0, y0, w, h = 1060, 820, 720, 480
    ca = a_in * ramp(t, T[0] + 0.4, T[0] + 1.0)
    c.set_source_rgba(*FAINT, ca); c.rectangle(x0, y0, w, 2); c.fill(); c.rectangle(x0, y0 - h, 2, h); c.fill()
    text(c, "时间 (s)", x0 + w, y0 + 50, 24, DIM, ca, align="r")
    text(c, "池沿以上高度 (m)", x0, y0 - h - 20, 24, DIM, ca)
    kk = ease_io((t - T[0] - 0.8) / 2.5)
    ts = np.linspace(0, T_AIR * kk, 80)
    hs = V_UP * ts - G * ts ** 2 / 2
    if kk > 0:
        polyline(c, np.stack([x0 + ts / 2.7 * w, y0 - hs / 8.5 * h], 1), GOLD, ca, 4)
    for v in (2, 4, 6, 8):
        text(c, f"{v}", x0 - 14, y0 - v / 8.5 * h + 8, 22, DIM, ca, align="r")
    for v in (0.5, 1.0, 1.5, 2.0, 2.5):
        text(c, f"{v}", x0 + v / 2.7 * w, y0 + 30, 22, DIM, ca, align="c")
    chapter_tag(c, "物理账", "竖直上抛", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "计算值 · 只算竖直分量，忽略空气阻力")
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5 landing on the wall
S5_SUBS = seq(["落回来时，从7米多高掉下来，为什么腿没断？",
               "因为落点在{w|几乎竖直的墙上}：速度大部分顺着墙面滑下去，只有垂直于墙面的那一小份，变成冲击。",
               "和跳台的落地坡是同一个道理。要是落在池沿上面的平台、或者没够着墙掉到池底——就是另一回事了。"])
S5_DUR = end_of(S5_SUBS) + 0.8


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S5_DUR - 0.6, S5_DUR))
    T = [x for _, x, _ in S5_SUBS]
    k = 52
    L, R = pipe(c, W / 2, 760, k, a_in)
    va = a_in * ramp(t, T[1] - 0.2, T[1] + 0.5)
    if va > 0:
        X, Y = R[0] - 4, R[1] + 30
        arrow(c, X, Y - 220, X, Y, INK, va, 5, 22)
        text(c, "下落速度", X + 30, Y - 150, 30, INK, va, bold=True)
        arrow(c, X, Y, X - 30, Y + 200, GOLD, va * ramp(t, T[1] + 1.0, T[1] + 1.6), 5, 22)
        text(c, "顺墙滑走（大部分）", X - 60, Y + 250, 30, GOLD, va * ramp(t, T[1] + 1.0, T[1] + 1.6), align="r", bold=True)
        arrow(c, X, Y, X + 40, Y + 6, RED, va * ramp(t, T[1] + 2.6, T[1] + 3.2), 5, 16)
        text(c, "垂直墙面 → 冲击（一小份）", X + 70, Y + 20, 30, RED, va * ramp(t, T[1] + 2.6, T[1] + 3.2), bold=True)
    da = a_in * ramp(t, T[2] + 2.0, T[2] + 2.6)
    if da > 0:
        for (x, y) in ((R[0] + 120, R[1]), (W / 2, 760)):
            c.new_path(); c.arc(x, y, 30, 0, 2 * math.pi); c.set_source_rgba(*RED, da); c.set_line_width(5); c.stroke()
        pill_label(c, "平台 / 池底：冲击全部压上来", W / 2, 300, 32, RED, da)
    chapter_tag(c, "落地", "落在墙上，而不是平地", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "示意 · 速度分解为定性说明")
    subs(c, t, S5_SUBS)
    overlays(c, fi)


# ================================================================== S6 end
S6_SUBS = seq(["池墙6.7米，再飞7.7米；空中2.5秒，离开池沿时竖直速度每小时44公里——",
               "下次再看U型池，你就知道这“轻飘飘”有多难了。",
               "转2340度，要转多快？下一集，用数据说话。"])
S6_DUR = end_of(S6_SUBS) + 4.0


def s6(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S6_DUR - 1.4, S6_DUR - 0.4))
    T = [x for _, x, _ in S6_SUBS]
    la = a_in * (1 - ramp(t, T[2] - 0.2, T[2] + 0.4))
    for i, (big, small, col) in enumerate((("6.7 m", "池墙", ICE), ("7.72 m", "池沿以上", RED), ("2.5 s", "空中时间", GOLD), ("44 km/h", "竖直起飞速度", GOLD))):
        k = ramp(t, T[0] + i * 1.2, T[0] + 0.6 + i * 1.2)
        x = 330 + i * 420
        text(c, big, x, 520, 80, col, la * k, align="c", bold=True)
        text(c, small, x, 590, 30, DIM, la * k, align="c")
    end_card(c, a_in * ramp(t, T[2], T[2] + 0.8), "转 2340°，要转多快？")
    subs(c, t, S6_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, S6_DUR - 1.0, S6_DUR))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR), ("s6", s6, S6_DUR)]


def _cover_fig(c):
    k = 30
    L, R = pipe(c, 430, 780, k, 1.0)
    top = R[1] - AIR * k
    c.set_source_rgba(*RED, 0.95); c.set_line_width(4); c.set_dash([12, 9])
    c.move_to(R[0], R[1]); c.line_to(R[0], top); c.stroke(); c.set_dash([])
    rider_profile(c, R[0], top, 60)
    text(c, "7.72 m", R[0] + 40, (R[1] + top) / 2, 70, RED, bold=True)


COVER = dict(lines=["U 型池", "选手到底飞多高？"], stat="14 m+", caption="6.7 m 池墙 + 池沿以上 7.72 m（吉尼斯纪录）", color=RED, figure=_cover_fig)
