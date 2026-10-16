"""单板 EP.11《大跳台：从起跳到落地》 (no voice-over)"""
import math
import numpy as np
from common import *
from art import *
from board import *

SERIES = SERIES_B
TITLE = "大跳台：从起跳到落地"
G = 9.81
LIP = math.radians(30)          # assumed take-off angle (示意)
TAB = 22.0                      # table length (m), Olympic ≈ 22 m
SL = math.radians(35)           # assumed landing slope (示意)
LL = 45.0


def gnd(x):
    if x < TAB:
        return 0.0
    if x < TAB + LL * math.cos(SL):
        return -(x - TAB) * math.tan(SL)
    return -LL * math.sin(SL)


def flight(kmh):
    v = kmh / 3.6
    t, dt, pts = 0.0, 0.002, []
    while True:
        t += dt
        x = v * math.cos(LIP) * t; y = v * math.sin(LIP) * t - G * t * t / 2
        pts.append((x, y))
        if t > 0.05 and y <= gnd(x):
            break
    vx, vy = v * math.cos(LIP), v * math.sin(LIP) - G * t
    return np.array(pts), x, y, t, math.hypot(vx, vy) * 3.6, (v * math.sin(LIP)) ** 2 / (2 * G)


V_MIN = math.sqrt(TAB * G / math.sin(2 * LIP)) * 3.6     # clear the table, lip at table level
CASES = [(50, ICE), (round(V_MIN), GOLD), (63, RED)]
RES = {k: flight(k) for k, _ in CASES}


def profile(c, V, a):
    """venue side view (metres): drop-in tower, in-run, kicker, table, landing, run-out (schematic)."""
    pts = [(-120, 58), (-112, 58), (-40, 4), (-8, -2.5), (0, 0.0), (TAB, 0.0)]
    pts += [(TAB + d * math.cos(SL), - d * math.sin(SL)) for d in np.linspace(0, LL, 10)]
    pts += [(TAB + LL * math.cos(SL) + 30, -LL * math.sin(SL))]
    P = V.P(pts)
    c.move_to(*P[0])
    for p in P[1:]:
        c.line_to(*p)
    c.line_to(P[-1][0], V.p(0, -60)[1]); c.line_to(P[0][0], V.p(0, -60)[1]); c.close_path()
    c.set_source_rgba(*TERRAIN_B, a); c.fill()
    c.move_to(*P[0])
    for p in P[1:]:
        c.line_to(*p)
    c.set_source_rgba(*RIM_B, 0.9 * a); c.set_line_width(3); c.stroke()


# ================================================================== S1 hook
S1_SUBS = seq(["北京冬奥的首钢大跳台，建在一座老钢厂里：背后就是冷却塔。",
               "选手从高处冲下来，在起跳台上一蹬，飞过一段平台，在空中转几圈，再落到又长又陡的坡上。",
               "这几秒里，到底发生了什么？"], t0=0.8)
S1_DUR = end_of(S1_SUBS) + 4.6


def s1(c, t, fi):
    paint_bg(c)
    a = ramp(t, 0, 0.8)
    V = View(1000, 520, 6.0)
    # cooling towers silhouette
    for cx in (300, 470):
        c.move_to(cx - 80, 900); c.curve_to(cx - 40, 700, cx - 50, 560, cx - 60, 430)
        c.line_to(cx + 60, 430); c.curve_to(cx + 50, 560, cx + 40, 700, cx + 80, 900); c.close_path()
        c.set_source_rgba(0.11, 0.13, 0.17, a); c.fill()
    profile(c, V, a)
    pts = RES[63][0]
    k = ((t * 0.4) % 1.3)
    if k < 1:
        i = min(len(pts) - 1, int(k * len(pts)))
        X, Y = V.p(pts[i][0], pts[i][1])
        rider_profile(c, X, Y, 40, alpha=a, wobble=k * 4 * math.pi)
    title_card(c, t, end_of(S1_SUBS) + 0.2, S1_DUR, TITLE, "场地尺寸 · 起跳速度 · 空中时间")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2 venue numbers
S2_SUBS = seq(["先看尺寸：全长约{w|164米}，最高处约{w|60米}；",
               "从出发点到落地区，垂直落差约{w|51米}——差不多17层楼。",
               "起跳台和落地坡之间，是一段可调的平台，{w|20到27米}长，奥运比赛大约{w|22米}。"])
S2_DUR = end_of(S2_SUBS) + 0.8


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S2_DUR - 0.6, S2_DUR))
    T = [x for _, x, _ in S2_SUBS]
    V = View(1060, 560, 6.2)
    profile(c, V, a_in)
    la = a_in * ramp(t, T[0] + 0.4, T[0] + 1.0)
    x0, y0 = V.p(-120, 58); x1, _ = V.p(TAB + LL * math.cos(SL) + 30, 0)
    dim_line(c, x0, 940, x1, 940, "≈ 164 m", la, size=34, off=(0, -16), col=GOLD)
    dim_line(c, x0 - 50, y0, x0 - 50, V.p(0, -LL * math.sin(SL))[1], "≈ 51 m 落差", a_in * ramp(t, T[1], T[1] + 0.6), size=32, off=(-110, 0), col=RED)
    ta = a_in * ramp(t, T[2], T[2] + 0.6)
    ax, ay = V.p(0, 0); bx, _ = V.p(TAB, 0)
    dim_line(c, ax, ay - 40, bx, ay - 40, "平台 20–27 m（奥运约 22 m）", ta, size=30, off=(0, -16), col=ICE)
    chapter_tag(c, "场地", "首钢大跳台", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "Olympics.com · NBC · FIS", "长约 164 m，最高约 60 m，落差约 168 ft", "平台 20–27 m，奥运约 22 m", ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    model_note(c, a_in, "剖面为示意，坡角与形状非真实测绘")
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3 minimum speed
S3_SUBS = seq(["要飞过22米的平台，起跳时至少要多快？",
               f"假设起跳角30度、不算空气阻力，射程公式一算：至少约每小时{{w|{V_MIN:.0f}公里}}。",
               "慢了，就砸在平台上；只有落到后面的坡上，冲击才会顺着坡走掉。"])
S3_DUR = end_of(S3_SUBS) + 0.8


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S3_DUR - 0.6, S3_DUR))
    T = [x for _, x, _ in S3_SUBS]
    V = View(260, 430, 26)
    pts = [(-14, 2), (-6, -2.5), (0, 0), (TAB, 0)] + [(TAB + d * math.cos(SL), - d * math.sin(SL)) for d in np.linspace(0, 20, 6)]
    P = V.P(pts)
    c.move_to(*P[0])
    for p in P[1:]:
        c.line_to(*p)
    c.line_to(P[-1][0], 1080); c.line_to(P[0][0], 1080); c.close_path(); c.set_source_rgba(*TERRAIN_B, a_in); c.fill()
    polyline(c, P, RIM_B, a_in, 3)
    fa = a_in * ramp(t, T[1] - 0.2, T[1] + 0.4)
    text(c, "R = v² · sin(2θ) / g", 1450, 330, 46, GOLD, fa, align="c", bold=True)
    text(c, f"v ≥ √(22 × 9.81 / sin 60°) ≈ {V_MIN / 3.6:.1f} m/s", 1450, 400, 30, INK, fa, align="c")
    for (kmh, col), ts in zip(CASES, (T[2] - 0.6, T[1] + 1.6, T[2] + 0.6)):
        k = ramp(t, ts, ts + 1.2)
        if k <= 0:
            continue
        p, xl, yl, *_ = RES[kmh]
        q = p
        n = max(2, int(len(q) * k))
        polyline(c, V.P(q[:n]), col, a_in, 3.5, [10, 7])
        if k >= 1:
            X, Y = V.p(*q[-1])
            text(c, f"{kmh} km/h", X, Y - 30, 34, col, a_in, align="c", bold=True)
    chapter_tag(c, "最低速度", "飞过 22 m 平台", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "示意计算：起跳角 30°、起跳点与平台同高、忽略空气阻力")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4 air time and landing speed
P63 = RES[63]
S4_SUBS = seq([f"按每小时63公里起跳算：最高点比起跳台高出约{{w|{P63[5]:.1f}米}}，",
               f"空中时间大约{{w|{P63[3]:.1f}秒}}，水平飞出去约{P63[1]:.0f}米；",
               f"落地那一刻，速度反而更快——约每小时{{r|{P63[4]:.0f}公里}}，因为一路在往下掉。",
               "这么快的速度能站住，靠的还是落地坡：速度大部分顺着坡滑走，就像上几集说的等效下落高度。"])
S4_DUR = end_of(S4_SUBS) + 0.8


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S4_DUR - 0.6, S4_DUR))
    T = [x for _, x, _ in S4_SUBS]
    V = View(260, 380, 17)
    pts = [(-14, 2), (-6, -2.5), (0, 0), (TAB, 0)] + [(TAB + d * math.cos(SL), - d * math.sin(SL)) for d in np.linspace(0, LL, 10)] + [(100, -LL * math.sin(SL))]
    P = V.P(pts)
    c.move_to(*P[0])
    for p in P[1:]:
        c.line_to(*p)
    c.line_to(P[-1][0], 1080); c.line_to(P[0][0], 1080); c.close_path(); c.set_source_rgba(*TERRAIN_B, a_in); c.fill()
    polyline(c, P, RIM_B, a_in, 3)
    p, xl, yl, tf, vland, apex = P63
    k = ramp(t, T[0] - 0.2, T[0] + 2.2)
    n = max(2, int(len(p) * k))
    polyline(c, V.P(p[:n]), GOLD, a_in, 4, [10, 7])
    X, Y = V.p(*p[n - 1])
    rider_profile(c, X, Y, 30, alpha=a_in, wobble=k * 6 * math.pi)
    i_ap = int(np.argmax(p[:, 1]))
    if k > i_ap / len(p):
        ax, ay = V.p(*p[i_ap])
        dim_line(c, ax, V.p(0, 0)[1], ax, ay, f"{apex:.1f} m", a_in, size=28, off=(50, 0), col=GOLD)
    if t > T[1]:
        text(c, f"空中 ≈ {tf:.1f} s", 1500, 300, 50, ICE, a_in * ramp(t, T[1], T[1] + 0.6), align="c", bold=True)
    if t > T[2]:
        Xl, Yl = V.p(xl, yl)
        c.new_path(); c.arc(Xl, Yl, 14, 0, 2 * math.pi); c.set_source_rgba(*RED, a_in); c.fill()
        text(c, f"落地 ≈ {vland:.0f} km/h", Xl - 40, Yl - 40, 40, RED, a_in * ramp(t, T[2], T[2] + 0.6), align="r", bold=True)
    chapter_tag(c, "飞行", "63 km/h 起跳（示意）", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "示意计算：起跳角 30°、落地坡 35°（假设）、忽略空气阻力")
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5 time budget
S5_SUBS = seq([f"把这{P63[3]:.0f}秒拆开看：起跳那一下，蹬板、给出转体的力，转速基本就定了；",
               "中间两秒多，收紧身体、抱住板，一圈一圈地转——上一集的2340，就是在这里完成的；",
               "最后半秒，打开身体、减速，眼睛找落地点，板头对准坡——差一点角度，就是一次重摔。"])
S5_DUR = end_of(S5_SUBS) + 0.8


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S5_DUR - 0.6, S5_DUR))
    T = [x for _, x, _ in S5_SUBS]
    tf = P63[3]
    x0, x1, y = 260, 1660, 520
    wd = x1 - x0
    segs = [(0, 0.3, "起跳：蹬出转速", GOLD, T[0]), (0.3, tf - 0.5, "空中：收紧 · 转体", ICE, T[1]), (tf - 0.5, tf, "落地前：打开 · 对准", RED, T[2])]
    for a0, a1, lab, col, ts in segs:
        k = ease_io((t - ts - 0.2) / 0.8)
        if k <= 0:
            continue
        xa, xb = x0 + wd * a0 / tf, x0 + wd * a1 / tf
        c.rectangle(xa, y, (xb - xa) * k, 110); c.set_source_rgba(*col, 0.85 * a_in); c.fill()
        text(c, lab, (xa + xb) / 2, y - 40 if col != RED else y + 170, 34, col, a_in * k, align="c", bold=True)
    for s in np.arange(0, tf + 0.01, 0.5):
        text(c, f"{s:.1f} s", x0 + wd * s / tf, y + 150 if s not in () else y, 22, DIM, a_in, align="c")
    chapter_tag(c, "时间账", f"约 {tf:.1f} 秒的空中", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "示意 · 各阶段时长为通俗划分")
    subs(c, t, S5_SUBS)
    overlays(c, fi)


# ================================================================== S6 end
S6_SUBS = seq([f"60米高的台子，22米的平台，起跳至少{V_MIN:.0f}公里每小时，空中近三秒，落地近90公里每小时——",
               "大跳台的每一跳，都是一道算好了的物理题。",
               "平花的物理：压板头，为什么能转？下一集，用数据说话。"])
S6_DUR = end_of(S6_SUBS) + 4.0


def s6(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S6_DUR - 1.4, S6_DUR - 0.4))
    T = [x for _, x, _ in S6_SUBS]
    la = a_in * (1 - ramp(t, T[2] - 0.2, T[2] + 0.4))
    for i, (big, small, col) in enumerate((("60 m", "台高", ICE), ("22 m", "平台", ICE), (f"≥{V_MIN:.0f}", "起跳 km/h", GOLD),
                                           (f"{P63[3]:.0f} s", "空中", GOLD), (f"{P63[4]:.0f}", "落地 km/h", RED))):
        k = ramp(t, T[0] + i * 0.9, T[0] + 0.5 + i * 0.9)
        x = 280 + i * 340
        text(c, big, x, 520, 72, col, la * k, align="c", bold=True)
        text(c, small, x, 590, 28, DIM, la * k, align="c")
    end_card(c, a_in * ramp(t, T[2], T[2] + 0.8), "平花：压板头为什么能转？")
    subs(c, t, S6_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, S6_DUR - 1.0, S6_DUR))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR), ("s6", s6, S6_DUR)]


def _cover_fig(c):
    V = View(560, 420, 4.6)
    profile(c, V, 1.0)
    polyline(c, V.P(RES[63][0]), GOLD, 1.0, 4, [10, 7])


COVER = dict(lines=["大跳台", "从起跳到落地"], stat=f"≥{V_MIN:.0f} km/h", caption="飞过 22 m 平台需要的起跳速度（示意计算）", color=GOLD, figure=_cover_fig)
COVER2 = dict(kicker="单板 · 用数据说话", lines=[("大跳台", "ink"), ("起跳到落地", "gold")], sub="飞过 22 米平台，至少 57 公里每小时", motif="jump", seed=11)
