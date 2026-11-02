"""All scenes of 《落在坡上，为什么不疼？》. Each scene: sN(c, t, fi) and SN_DUR."""
import math
from functools import lru_cache
import numpy as np
from common import *
from view import *
import jump as J

KMH = 1 / 3.6
INRUN = inrun()


def subs(c, t, SUBS):
    for s, a, b in SUBS:
        subtitle(c, s, t, a, b)


def inrun_pos(u):
    """u 0..1 along the in-run from x=-5.5 to the lip -> (x, y, angle)."""
    x = lerp(-5.5, 0.0, u)
    y = float(np.interp(x, INRUN[:, 0], INRUN[:, 1]))
    y2 = float(np.interp(x + 0.05, INRUN[:, 0], INRUN[:, 1]))
    return x, y, math.atan2(y2 - y, 0.05)


@lru_cache(maxsize=2048)
def land_const(v0, h=0.5):
    """landing on deck + constant-EFH curve (drag-free)."""
    _, xs, ys = CONST
    vx, vy = v0 * math.cos(J.TH), v0 * math.sin(J.TH)

    def sy(x):
        return 0.0 if x <= J.DECK else float(np.interp(x, xs, ys))
    t = 1e-3
    while True:
        x = vx * t; y = vy * t - 0.5 * J.G * t * t
        if y <= sy(x):
            break
        t += 1e-3
    X = vx * t; vyl = vy - J.G * t
    if X <= J.DECK:
        sl = 0.0
    else:
        j = int(np.searchsorted(xs, X)); j = min(max(j, 1), len(xs) - 1)
        sl = math.atan((ys[j] - ys[j - 1]) / (xs[j] - xs[j - 1]))
    v = math.hypot(vx, vyl); imp = math.atan2(vyl, vx)
    return dict(T=t, x=X, y=sy(X), v=v, imp=imp, slope=sl, efh=J.efh(v, imp, sl))


CONST = const_pts()


def jump_run(c, V, v0, lt, res=None, slow=0.75, approach=0.8, scale_r=None, trace_a=0.9,
             show_dec=True, dec_k=9.0, pill=True, crouch_land=True):
    """animate one jump. lt = local time. returns (phase, res)."""
    if lt < 0:
        return "pre", res
    res = res or fl(v0)
    s = scale_r or V.k
    T = res["T"]; dur = T / slow
    if lt < approach:
        x, y, a = inrun_pos(ease_io(lt / approach) * 0.6 + 0.4 * lt / approach)
        X, Y = V.p(x, y)
        nx, ny = -math.sin(a), math.cos(a)
        rider(c, X - nx * 0.0, Y - 0.0, -a, s, 0.45)
        return "approach", res
    tf = min((lt - approach) * slow, T)
    P = J.traj_points(v0, tf, 60)
    polyline(c, V.P(P), GOLD, trace_a * 0.8, 2.2, [6, 6])
    if lt < approach + dur:
        x, y = P[-1]
        k = tf / T
        ang = lerp(J.TH, res["slope"], ease_io(k))
        X, Y = V.p(x, y)
        rider(c, X, Y, -ang, s, lerp(0.45, 0.2, math.sin(math.pi * k)), arms=0.35 * math.sin(math.pi * k))
        return "flight", res
    # landed
    la = lt - approach - dur
    X, Y = V.p(res["x"], res["y"])
    hard = res["efh"] > 2
    sl = res["slope"]
    ra = 1 - ramp(la, 0.9, 1.4)
    slide = min(la, 0.9) * res["v"] * math.cos(sl - res["imp"]) * 0.35 if not hard else 0
    rx, ry = V.p(res["x"] + slide * math.cos(sl), res["y"] + slide * math.sin(sl))
    cr = 0.95 if hard else lerp(0.8, 0.4, ramp(la, 0, 0.6))
    rider(c, rx, ry, -sl, s, cr, ra)
    if hard:   # impact flash
        f = 1 - ramp(la, 0, 0.5)
        c.arc(X, Y, 20 + 60 * (1 - f), 0, 2 * math.pi); c.set_source_rgba(*RED, 0.5 * f); c.set_line_width(4); c.stroke()
    if show_dec:
        a = ramp(la, 0.2, 0.6)
        decomp(c, X, Y, res["v"], res["imp"], sl, dec_k, a, 1.0, labels=False)
    if pill:
        a = ramp(la, 0.4, 0.8)
        pill_label(c, f"EFH {res['efh']:.2f} m", X, Y + 74, 28, efh_col(res["efh"]), a)
    return "landed", res


# ================================================================== S1  hook
S1_DUR = 17.0
S1_SUBS = [
    ("左边：从 {w|1.5 米}高的台子，跳到平地上。", 0.6, 4.6),
    ("右边：以 36 km/h 起跳，飞出 {w|11 米}多，落在坡上。", 4.9, 9.2),
    ("哪一个落地更疼？", 9.5, 11.4),
]
VL = View(330, 760, 120)
VR = View(1240, 560, 30)
TT = tabletop_pts(-8, 25)


def s1(c, t, fi):
    paint_bg(c)
    dim = 1 - 0.75 * ramp(t, 11.4, 12.2)
    a_in = ramp(t, 0.0, 0.8) * dim
    # ---- left: platform drop
    c.save(); c.rectangle(0, 0, 958, H); c.clip()
    ground = VL.P([(-2.6, 1.5), (0, 1.5), (0, 0), (5, 0)])
    fill_terrain(c, ground, a_in)
    td = 1.6
    lt = t - td
    if lt < 0:
        rider(c, *VL.p(-0.9, 1.5), 0, VL.k * 0.9, 0.35, a_in)
    else:
        slow = 0.5
        tt = lt * slow
        Tf = math.sqrt(2 * 1.5 / J.G)
        vx = 1.6
        if tt < 0.55:  # walk off edge
            x = -0.9 + vx * tt * 1.0 / 0.55 * 0.55
            rider(c, *VL.p(min(x, -0.9 + 0.88), 1.5), 0, VL.k * 0.9, 0.35, a_in)
        else:
            tf = min(tt - 0.55, Tf)
            x = -0.02 + vx * tf; y = 1.5 - 0.5 * J.G * tf * tf
            land = tt - 0.55 >= Tf
            cr = 0.95 if land else 0.3
            rider(c, *VL.p(x, max(y, 0)), 0, VL.k * 0.9, cr, a_in)
            if land:
                la = (tt - 0.55 - Tf) / slow
                f = 1 - ramp(la, 0, 0.5)
                X, Y = VL.p(x, 0)
                c.arc(X, Y, 20 + 60 * (1 - f), 0, 2 * math.pi); c.set_source_rgba(*RED, 0.5 * f * dim); c.set_line_width(4); c.stroke()
    text(c, "1.5 m", VL.p(0, 0.75)[0] - 20, VL.p(0, 0.75)[1] + 10, 26, DIM, a_in, align="r")
    c.restore()
    # divider
    c.set_source_rgba(*FAINT, 0.6 * a_in); c.rectangle(959, 120, 1.5, 700); c.fill()
    # ---- right: tabletop
    c.save(); c.rectangle(962, 0, W - 962, H); c.clip()
    fill_terrain(c, VR.P(TT), a_in)
    if t < 5.0:
        x, y, a = inrun_pos(0.0)
        rider(c, *VR.p(x, y), -a, VR.k * 1.6, 0.4, a_in)
    else:
        jump_run(c, VR, 10.0, t - 5.0, scale_r=VR.k * 1.6, show_dec=False, pill=False, trace_a=0.7 * dim, slow=0.7)
    c.restore()
    if a_in < 0.999 and t < 1:
        pass
    # ---- title
    ta = ramp(t, 11.8, 12.8) * (1 - ramp(t, 16.2, 17.0))
    if ta > 0:
        c.set_source_rgba(0, 0, 0, 0.55 * ta); c.paint()
        text(c, "滑雪里的物理", W / 2, 360, 30, DIM, ta, align="c", spacing=0.3)
        text(c, "落在坡上，为什么不疼？", W / 2, 500, 92, INK, ta, align="c", bold=True)
        c.set_source_rgba(*GOLD, 0.8 * ta); c.rectangle(W / 2 - 160, 548, 320, 2); c.fill()
        text(c, "单板跳台落地 · 等效下落高度", W / 2, 612, 34, GOLD, ta, align="c")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2  decomposition
S2_DUR = 44.0
S2_SUBS = [
    ("落地那一刻，速度是一个{w|斜向下}的箭头。", 0.5, 4.6),
    ("把它拆成两份：{b|顺着坡}的，和{r|垂直于坡}的。", 4.9, 9.6),
    ("顺着坡的那份，继续往前滑走就好；\n垂直于坡的那份，要靠腿在一瞬间吸收掉。", 9.9, 15.6),
    ("把这个垂直速度，换算成“从多高掉到平地上”，\n就叫{w|等效下落高度}（EFH）。", 15.9, 21.6),
    ("落在平地上：垂直速度 6.9 m/s，\n相当于从 {r|2.4 米}高直直摔下来。", 21.9, 26.6),
    ("现在把地面倾斜：坡越接近你下落的方向，\n垂直的那份就越小。", 26.9, 33.6),
    ("落在 30° 的坡上：只剩 {b|6 厘米}。", 33.9, 38.6),
    ("（落地速度 12 m/s、向下 35°，把人当作一个点）", 38.9, 43.6),
]
V2 = 12.0
IMP2 = math.radians(-35)


def s2_slope(t):
    return -math.radians(30) * ease_io((t - 27.4) / 5.6)


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, 43.4, 44.0))
    sl = s2_slope(t)
    X, Y = 820, 690
    # ground line through landing point
    L = 1400
    tx, ty = math.cos(sl), -math.sin(sl)
    S = np.array([(X - tx * L, Y - ty * L), (X + tx * L, Y + ty * L)])
    fill_terrain(c, S, a_in)
    # rider at the tail of the velocity arrow
    k = 26.0
    vx, vy = V2 * math.cos(IMP2), V2 * math.sin(IMP2)
    X0, Y0 = X - vx * k, Y + vy * k
    rider(c, X0 - 14, Y0 - 16, -sl, 80, 0.3, a_in)
    a_arrow = ramp(t, 0.8, 1.6) * a_in
    a_parts = ramp(t, 5.2, 6.4)
    vn = decomp(c, X, Y, V2, IMP2, sl, k, a_arrow, a_parts, labels=True)
    # pulse the normal part, ghost the along part
    if 9.9 < t < 15.6:
        p = 0.5 + 0.5 * math.sin((t - 9.9) * 5)
        c.arc(X, Y, 16 + 8 * p, 0, 2 * math.pi); c.set_source_rgba(*RED, 0.6 * a_in); c.set_line_width(3); c.stroke()
        g = ramp(t, 10.2, 13.5)
        gx = X + tx * 380 * g; gy = Y + ty * 380 * g
        arrow(c, X, Y, gx + tx * 60, gy + ty * 60, ICE, 0.5 * (1 - g) * a_in, 3, 14)
    h = vn ** 2 / (2 * J.G)
    # formula card
    fa = ramp(t, 16.2, 17.2) * a_in
    if fa > 0:
        x0, y0 = 1040, 330
        text(c, "EFH  =  v⊥² ÷ 2g", x0, y0, 52, GOLD, fa, bold=True)
        text(c, "v⊥ = v · sin(坡角 − 落地方向角)", x0, y0 + 52, 26, INK, fa)
        text(c, "表达式与 skijumpdesign 源码一致（Moore & Hubbard）", x0, y0 + 92, 20, DIM, fa)
    ruler(c, h, ramp(t, 17.5, 18.5) * a_in)
    # chapter tag with live readout
    ca = ramp(t, 0.5, 1.2) * a_in
    chapter_tag(c, f"坡 {abs(math.degrees(sl)):.0f}°", f"垂直速度 {vn:.1f} m/s · EFH {h:.2f} m", ca)
    cite_card(c, "J. ASTM Int. · 2009", "冲击取决于垂直于落地面的速度", "M. Hubbard", ramp(t, 16.0, 17.0) * a_in)
    model_note(c, ramp(t, 38.9, 39.6) * a_in, "示意 · 质点模型，不含腿的缓冲动作")
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3  anatomy + speed sweep
S3_DUR = 46.0
S3_SUBS = [
    ("这是一座常见的{w|桌面跳台}。", 0.5, 4.6),
    ("起跳台、桌面、坡顶、落地坡、坡底——\n尺寸是示意的：起跳 20°，桌面 6 米，落地坡 30°、高 6 米。", 4.9, 10.4),
    ("滑得慢，落在桌面上：EFH 约 {b|0.4 米}。", 10.7, 16.0),
    ("快一点，刚好飞过坡顶、落在落地坡上——\nEFH 反而更小：{b|0.23 米}。", 16.3, 22.0),
    ("再快，落得越靠下，EFH 越大：\n38 km/h 时 {w|0.73 米}。", 22.3, 28.0),
    ("40 km/h，快到坡底了：{w|1.1 米}。", 28.3, 33.5),
    ("只再快 1 km/h——飞过坡底，砸在平地上：\nEFH {r|6.8 米}。", 33.8, 40.0),
    ("相当于从两层多楼高的地方，直直摔下来。", 40.3, 45.5),
]
V3 = View(560, 430, 56)
SEG3 = [(10.7, 30), (16.3, 35), (22.3, 38), (28.3, 40), (33.8, 41)]
LABELS3 = [  # (text, world x, world y, dx, dy, t)
    ("助滑道", -6.0, 1.2, -20, -40, 5.0),
    ("起跳台 20°", -0.6, 0.0, -40, -70, 5.6),
    ("桌面 6 m", 3.0, 0.0, 0, -40, 6.2),
    ("坡顶", J.DECK, 0.0, 10, -40, 6.8),
    ("落地坡 30°", 11.5, -3.2, 40, -40, 7.4),
    ("坡底平地", 19.5, -6.0, 0, -40, 8.0),
]


def draw_labels(c, V, t, LAB, alpha=1.0):
    for s, x, y, dx, dy, t0 in LAB:
        a = ramp(t, t0, t0 + 0.4) * alpha
        if a <= 0:
            continue
        X, Y = V.p(x, y)
        c.set_source_rgba(*DIM, 0.7 * a); c.set_line_width(1.2)
        c.move_to(X, Y - 6); c.line_to(X + dx, Y + dy + 10); c.stroke()
        text(c, s, X + dx, Y + dy, 24, INK, a, align="c", bold=True)


def tabletop_scene(c, t, V, a_in, reveal_t0=0.4, reveal_t1=2.6):
    S = V.P(tabletop_pts(-8, 40))
    up = lerp(-10, W + 10, ease_io((t - reveal_t0) / (reveal_t1 - reveal_t0)))
    fill_terrain(c, S, a_in, upto=up)


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.5) * (1 - ramp(t, 45.4, 46.0))
    tabletop_scene(c, t, V3, a_in)
    lab_a = a_in * (1 - 0.6 * ramp(t, 10.5, 11.2))
    draw_labels(c, V3, t, LABELS3, lab_a)
    cur = None
    for i, (t0, kmh) in enumerate(SEG3):
        t1 = SEG3[i + 1][0] if i + 1 < len(SEG3) else S3_DUR
        if t < t0:
            continue
        if t < t1:
            cur = (t0, kmh)
        else:  # past jumps: faint trace + landing dot
            r = fl(kmh * KMH)
            polyline(c, V3.P(J.traj_points(kmh * KMH, r["T"], 50)), efh_col(r["efh"]), 0.28 * a_in, 1.6, [4, 6])
            X, Y = V3.p(r["x"], r["y"])
            c.arc(X, Y, 6, 0, 2 * math.pi); c.set_source_rgba(*efh_col(r["efh"]), 0.6 * a_in); c.fill()
    if cur:
        t0, kmh = cur
        ph, r = jump_run(c, V3, kmh * KMH, t - t0 - 0.3, scale_r=V3.k * 1.15)
        tag_a = ramp(t, 10.7, 11.3) * a_in
        e = r["efh"] if ph == "landed" else None
        chapter_tag(c, f"{kmh} km/h", "起跳速度 · " + (f"EFH {e:.2f} m" if e is not None else "飞行中…"), tag_a)
    else:
        chapter_tag(c, "桌面跳台", "侧面剖面 · 示意尺寸", ramp(t, 0.6, 1.3) * a_in * (1 - ramp(t, 10.4, 10.7)))
    model_note(c, ramp(t, 5, 6) * a_in, "示意 · 质点模型，忽略空气阻力")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4  EFH vs speed
S4_DUR = 40.0
S4_SUBS = [
    ("把每一个起跳速度的结果，画成一条线。", 0.5, 4.8),
    ("左边是{b|桌面区}：太慢，落在平台上，EFH 0.3 到 0.5 米。", 5.1, 10.4),
    ("中间是{w|落地坡}：这才是跳台留给你落的地方——\n大约 34 到 40 km/h，只有 6 km/h 宽。", 10.7, 16.4),
    ("右边是{r|平地区}：过了 40 km/h，\nEFH 从 1.1 米一下跳到 6.7 米。", 16.7, 22.6),
    ("而且在落地坡上，越往下落，EFH 越大——\n直线落地坡的冲击，随落点距离一路往上涨。", 22.9, 29.6),
    ("所以跳台对速度很挑剔：快一点、慢一点，结果完全不一样。", 29.9, 35.4),
]
SP4 = np.linspace(20, 55, 1401)
EF4 = np.array([fl(v * KMH)["efh"] for v in SP4])
ZN4 = [J.zone(fl(v * KMH)["x"]) for v in SP4]
B1 = float(SP4[[z != "deck" for z in ZN4].index(True)])
B2 = float(SP4[[z == "flat" for z in ZN4].index(True)])


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, 39.4, 40.0))
    x0, y0, w, h = 260, 290, 1400, 470
    X = lambda kmh: x0 + (kmh - 20) / 35 * w
    Y = lambda e: y0 + h - e / 8.0 * h
    # zone bands
    for (a, b, col, lab, t0) in ((20, B1, ICE, "桌面区", 5.1), (B1, B2, GOLD, "落地坡", 10.7), (B2, 55, RED, "平地区", 16.7)):
        za = ramp(t, t0, t0 + 0.6) * a_in
        c.rectangle(X(a), y0, X(b) - X(a), h); c.set_source_rgba(*col, 0.08 * za); c.fill()
        text(c, lab, (X(a) + X(b)) / 2, y0 + 40, 30, col, za, align="c", bold=True)
    # axes
    c.set_source_rgba(*FAINT, a_in); c.set_line_width(1.4)
    c.move_to(x0, y0); c.line_to(x0, y0 + h); c.line_to(x0 + w, y0 + h); c.stroke()
    for k in range(20, 56, 5):
        text(c, f"{k}", X(k), y0 + h + 34, 20, DIM, a_in, align="c")
    for e in range(0, 9, 2):
        text(c, f"{e}", x0 - 14, Y(e) + 7, 20, DIM, a_in, align="r")
        c.set_source_rgba(*FAINT, 0.35 * a_in); c.rectangle(x0, Y(e), w, 1); c.fill()
    text(c, "起跳速度 km/h", x0 + w, y0 + h + 72, 22, DIM, a_in, align="r")
    text(c, "等效下落高度 EFH（m）", x0, y0 - 24, 22, DIM, a_in)
    # curve draw-on, broken at zone changes
    up = lerp(20, 55, ease_io((t - 0.9) / 3.4))
    c.set_line_width(4)
    prev = None
    for v, e, z in zip(SP4, EF4, ZN4):
        if v > up:
            break
        p = (X(v), Y(e))
        if prev is not None and prev[2] == z:
            c.move_to(*prev[:2]); c.line_to(*p)
            c.set_source_rgba(*efh_col(e), a_in); c.stroke()
        prev = (p[0], p[1], z)
    # marker that walks along according to narration
    mk = [(5.1, 28), (10.7, 35), (13.5, 39.5), (16.7, 40.1), (18.5, 41), (22.9, B1 + 0.2), (27.5, B2 - 0.1), (29.9, 37)]
    if t > 5.1:
        v = mk[0][1]
        for tt, val in mk[1:]:
            if t >= tt:
                v = lerp(v, val, ease_io((t - tt) / 1.4))
        e = float(np.interp(v, SP4, EF4))
        col = efh_col(e)
        c.arc(X(v), Y(e), 11, 0, 2 * math.pi); c.set_source_rgba(*col, a_in); c.fill()
        c.set_dash([5, 6]); c.set_source_rgba(*col, 0.6 * a_in); c.set_line_width(1.5)
        c.move_to(X(v), Y(e)); c.line_to(X(v), y0 + h); c.stroke(); c.set_dash([])
        chapter_tag(c, f"{v:.0f} km/h", f"EFH {e:.2f} m · 落在{dict(deck='桌面', slope='落地坡', flat='坡底平地')[J.zone(fl(v * KMH)['x'])]}", ramp(t, 5.1, 5.7) * a_in)
    # window bracket
    wa = ramp(t, 12.0, 12.8) * a_in * (1 - ramp(t, 22.5, 23.2))
    if wa > 0:
        yy = Y(2.6)
        c.set_source_rgba(*GOLD, wa); c.set_line_width(2)
        c.move_to(X(B1), yy - 12); c.line_to(X(B1), yy); c.line_to(X(B2), yy); c.line_to(X(B2), yy - 12); c.stroke()
        text(c, f"{B1:.0f}–{B2:.0f} km/h", (X(B1) + X(B2)) / 2, yy - 22, 26, GOLD, wa, align="c", bold=True)
    cite_card(c, "Sports Eng. 2009 · NPS 2010", "直线落地坡上，EFH 随落点距离增大", "McNeil & McNeil；Swedberg", ramp(t, 22.9, 23.8) * a_in)
    model_note(c, a_in, "示意跳台 · 质点模型，忽略空气阻力")
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5  constant-EFH surface
S5_DUR = 36.0
S5_SUBS = [
    ("能不能让落地坡，对每个速度都一样温柔？", 0.5, 5.0),
    ("工程师算出了一种曲线：\n每一点都和从那里落下来的轨迹，几乎平行。", 5.3, 11.6),
    ("不管起跳多快，落下来的 EFH 都一样——这里取 {b|0.5 米}。", 11.9, 19.6),
    ("2016 年，意大利的研究者按这个思路建了一座，\n在人和板上装加速度计，测落地冲击。", 19.9, 26.4),
    ("结论：这样的跳台{w|能设计，也建得出来}。", 26.7, 31.6),
    ("（曲线为本片按无空气阻力的简化模型算出，仅作示意）", 31.9, 35.6),
]
V5 = View(300, 330, 42)
SP5 = [34, 38, 42, 46, 50, 54, 57]


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, 35.4, 36.0))
    # old tabletop, dim
    S_old = V5.P(tabletop_pts(-6, 40))
    fill_terrain(c, S_old, a_in * (1 - ramp(t, 5.0, 6.0)))
    polyline(c, S_old, DIM, 0.45 * a_in * (1 - 0.5 * ramp(t, 5.3, 6.5)), 2.0, [8, 8])
    P, xs, ys = CONST
    S = V5.P(P)
    up = lerp(V5.p(J.DECK, 0)[0], W + 10, ease_io((t - 5.6) / 3.2))
    if t > 5.6:
        fill_terrain(c, S, a_in * ramp(t, 5.6, 6.0), upto=up, rim_col=ICE)
    text(c, "普通桌面跳台", *V5.p(17.5, -6.0 + 0.6), 22, DIM, 0.8 * a_in * (1 - ramp(t, 5.3, 6.5)) + 0.4 * a_in * ramp(t, 6.5, 7.5), align="l")
    lab = ramp(t, 8.0, 8.8) * a_in
    if lab > 0:
        Xl, Yl = V5.p(24, float(np.interp(24, xs, ys)))
        text(c, "等 EFH 落地面", Xl + 30, Yl - 30, 28, ICE, lab, bold=True)
    # sweep of jumps
    t0 = 11.9
    if t > t0:
        for i, kmh in enumerate(SP5):
            lt = t - t0 - i * 1.05
            r = land_const(kmh * KMH)
            if lt < 0:
                continue
            done = lt > 0.6 + r["T"] / 0.9
            if done or i < len(SP5) - 1 and t - t0 - (i + 1) * 1.05 > 0:
                polyline(c, V5.P(J.traj_points(kmh * KMH, r["T"], 50)), GOLD, 0.35 * a_in, 1.6, [4, 6])
                X, Y = V5.p(r["x"], r["y"])
                c.arc(X, Y, 6, 0, 2 * math.pi); c.set_source_rgba(*ICE, 0.9 * a_in); c.fill()
                text(c, f"{kmh}", X, Y + 34, 18, DIM, 0.8 * a_in, align="c")
            else:
                jump_run(c, V5, kmh * KMH, lt, res=r, slow=0.9, approach=0.6, scale_r=V5.k * 1.2, show_dec=False, pill=False)
        last = None
        for i, kmh in enumerate(SP5):
            r = land_const(kmh * KMH)
            if t - t0 - i * 1.05 > 0.6 + r["T"] / 0.9:
                last = (kmh, r)
        if last:
            chapter_tag(c, f"EFH {last[1]['efh']:.2f} m", f"{last[0]} km/h 起跳 · 落点 {last[1]['x']:.0f} m", a_in)
    cite_card(c, "Sports Eng. · 2012 / 2015", "可以设计“EFH 恒定”的落地面", "McNeil · Hubbard · Swedberg · Levy",
              ramp(t, 5.3, 6.2) * (1 - ramp(t, 19.4, 19.9)) * a_in)
    cite_card(c, "arXiv:1611.04448 · 2016", "建成并实测了等 EFH 跳台", "Petrone · Cognolato · McNeil · Hubbard",
              ramp(t, 19.9, 20.6) * a_in)
    model_note(c, a_in, "示意 · 无空气阻力的简化模型")
    subs(c, t, S5_SUBS)
    overlays(c, fi)


# ================================================================== S6  ending
S6_DUR = 24.0
S6_SUBS = [
    ("落在坡上不疼，是因为那一刻，你和坡{b|几乎平行}。", 0.6, 5.4),
    ("上跳台前：先看落地坡在哪、有多长。", 5.7, 10.4),
    ("第一次先压着速度试，\n宁可落在桌面，也别{r|飞过坡底}。", 10.7, 15.6),
    ("落地时，让板顺着坡。", 15.9, 19.6),
    ("（以上为常见经验做法；跳台尺寸与数字均为示意计算）", 19.9, 23.0),
]


def s6(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, 22.4, 23.8))
    tabletop_scene(c, t + 10, V3, a_in)
    # highlight landing slope extent
    ha = ramp(t, 5.9, 6.6) * (1 - ramp(t, 10.4, 11.0)) * a_in
    if ha > 0:
        polyline(c, V3.P([(J.DECK, 0), (J.X_END, -J.DROP)]), GOLD, ha, 7)
        Xm, Ym = V3.p((J.DECK + J.X_END) / 2, -J.DROP / 2)
        pill_label(c, "落地坡", Xm + 60, Ym - 20, 28, GOLD, ha)
    fa = ramp(t, 10.9, 11.6) * (1 - ramp(t, 15.5, 16.0)) * a_in
    if fa > 0:
        polyline(c, V3.P([(J.X_END, -J.DROP), (30, -J.DROP)]), RED, fa, 7)
        pill_label(c, "别飞到这里", *V3.p(21, -J.DROP + 1.2), 28, RED, fa)
    lt = (t - 0.4) % 7.6 if t < 15.6 else t - 15.6
    jump_run(c, V3, 37 * KMH, lt, scale_r=V3.k * 1.15, show_dec=t < 5.6, pill=t < 5.6, dec_k=9)
    chapter_tag(c, "顺着坡", "落地时板与坡几乎平行", ramp(t, 0.6, 1.2) * a_in)
    end = ramp(t, 20.0, 20.8) * a_in
    if end > 0:
        text(c, "滑雪里的物理", W / 2, 300, 30, DIM, end, align="c", spacing=0.3)
    subs(c, t, S6_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, 23.0, 24.0))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR), ("s6", s6, S6_DUR)]
