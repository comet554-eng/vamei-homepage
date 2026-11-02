"""EP.04《搓雪为什么慢？》"""
import math
import numpy as np
from common import *
from art import *

SERIES = "双板 · 用数据说话"
TITLE = "搓雪为什么慢？"
D2R = math.pi / 180


def subs(c, t, S):
    for s, a, b in S:
        subtitle(c, s, t, a, b)


def snow_field(c, a):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, 0.16, 0.19, 0.25, a); g.add_color_stop_rgba(1, 0.09, 0.11, 0.15, a)
    c.rectangle(0, 0, W, H); c.set_source(g); c.fill()


def path_x(y, cx, amp, period, phase=0.0):
    return cx + amp * math.sin(2 * math.pi * y / period + phase)


def track(c, cx, y0, y1, amp, period, skid, a, col_line=RIM, spray=True, t=0.0):
    """top-view track from y0 down to y1 (screen, y grows downhill). skid: 0 = carve (two thin lines), 1 = wide scraped band."""
    ys = np.linspace(y0, y1, 160)
    pts = np.array([(path_x(y, cx, amp, period), y) for y in ys])
    if len(pts) < 3:
        return pts
    d = np.gradient(pts, axis=0); nrm = np.stack([-d[:, 1], d[:, 0]], 1); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
    slope = np.abs(d[:, 0] / d[:, 1])                       # how much the path traverses
    if skid > 0:
        wdt = (16 + 70 * skid * np.clip(slope, 0, 1.2)) * 1.0
        L = pts + nrm * wdt[:, None] / 2; R = pts - nrm * wdt[:, None] / 2
        poly = np.concatenate([L, R[::-1]])
        c.move_to(*poly[0])
        for p in poly[1:]:
            c.line_to(*p)
        c.close_path(); c.set_source_rgba(0.55, 0.62, 0.74, 0.35 * a); c.fill()
        for k in np.linspace(-0.4, 0.4, 6):
            Q = pts + nrm * wdt[:, None] * k
            c.move_to(*Q[0])
            for q in Q[1::3]:
                c.line_to(*q)
            c.set_source_rgba(0.9, 0.92, 0.96, 0.12 * a); c.set_line_width(1.2); c.stroke()
    else:
        for off in (-9, 9):
            Q = pts + nrm * off
            c.move_to(*Q[0])
            for q in Q[1:]:
                c.line_to(*q)
            c.set_source_rgba(*col_line, 0.85 * a); c.set_line_width(2.2); c.stroke()
    return pts


def skis_head(c, x, y, heading, s, a):
    """two skis seen from above, heading = angle of ski axis (rad, 0 = straight downhill)."""
    c.save(); c.translate(x, y); c.rotate(-heading)
    for dx in (-0.12 * s, 0.12 * s):
        rounded_rect(c, dx - 0.035 * s, -0.8 * s, 0.07 * s, 1.6 * s, 0.03 * s)
        c.set_source_rgba(*GOLD, a); c.fill()
    c.arc(0, 0, 0.18 * s, 0, 2 * math.pi); c.set_source_rgba(0.92, 0.93, 0.95, a); c.fill()
    c.restore()


# ================================================================== S1
S1_SUBS = seq(["同一条坡，两种滑法：一种留下两道细线，一种刮出一大片。",
               "哪种快？大家都知道：{w|刻滑快}。",
               "可是——慢下来的那部分速度，到底去哪儿了？"])
S1_DUR = end_of(S1_SUBS) + 5.0


def s1(c, t, fi):
    snow_field(c, 1.0)
    a_in = ramp(t, 0, 0.8)
    down = lerp(-50, H + 50, ease_io((t - 0.6) / 6.0))
    for cx, sk, lab, col in ((620, 0.0, "刻滑", ICE), (1300, 1.0, "搓雪", RED)):
        pts = track(c, cx, -50, down, 150, 520, sk, a_in)
        if 0 < down < H + 40:
            y = down; x = path_x(y, cx, 150, 520)
            dx = 150 * 2 * math.pi / 520 * math.cos(2 * math.pi * y / 520)
            vel = math.atan(dx)
            head = vel + (0.0 if sk == 0 else 0.7 * math.copysign(1, -dx) * min(1, abs(dx)))
            skis_head(c, x, y, -head, 90, a_in)
        pill_label(c, lab, cx, 120, 34, col, a_in * ramp(t, 1.0, 1.6))
    te = end_of(S1_SUBS)
    ta = ramp(t, te + 0.3, te + 1.2) * (1 - ramp(t, S1_DUR - 0.7, S1_DUR))
    if ta > 0:
        c.set_source_rgba(*BG, 0.88 * ta); c.paint()
        text(c, SERIES, W / 2, 380, 30, DIM, ta, align="c", spacing=0.3)
        text(c, TITLE, W / 2, 510, 92, INK, ta, align="c", bold=True)
        c.set_source_rgba(*GOLD, 0.8 * ta); c.rectangle(W / 2 - 160, 556, 320, 2); c.fill()
        text(c, "能量去哪了 · 什么时候必须搓", W / 2, 620, 32, GOLD, ta, align="c")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2  where energy goes
S2_SUBS = seq(["往下滑，高度变成速度；而速度会被两样东西一点点吃掉：",
               "{b|空气}，和{r|雪}。",
               "一项回转研究把损失拆开：空气阻力只占{b|约 20%}；",
               "最大的一块，来自{r|雪对板的阻力}。",
               ("（回转实测；其余项目的比例会不同）", 3.4)])
S2_DUR = end_of(S2_SUBS) + 0.8


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S2_DUR - 0.6, S2_DUR))
    T = [a for _, a, _ in S2_SUBS]
    cx, cy, R = W / 2, 470, 220
    k = ease_io((t - T[2]) / 1.4)
    c.set_line_width(70)
    c.new_path(); c.arc(cx, cy, R, 0, 2 * math.pi); c.set_source_rgba(*FAINT, a_in * ramp(t, T[1], T[1] + 0.6)); c.stroke()
    if k > 0:
        c.new_path(); c.arc(cx, cy, R, -math.pi / 2, -math.pi / 2 + 2 * math.pi * 0.2 * k); c.set_source_rgba(*ICE, a_in); c.stroke()
        text(c, "空气 ≈ 20%", cx + 280, cy - 170, 36, ICE, a_in * k, bold=True)
    k2 = ease_io((t - T[3]) / 1.6)
    if k2 > 0:
        c.new_path(); c.arc(cx, cy, R, -math.pi / 2 + 2 * math.pi * 0.2, -math.pi / 2 + 2 * math.pi * (0.2 + 0.8 * k2)); c.set_source_rgba(*RED, a_in); c.stroke()
        text(c, "雪对板的阻力", cx - 300, cy + 200, 36, RED, a_in * k2, align="r", bold=True)
        text(c, "最大的一块", cx - 300, cy + 244, 24, DIM, a_in * k2, align="r")
    text(c, "速度损失", cx, cy + 14, 44, INK, a_in * ramp(t, T[1], T[1] + 0.6), align="c", bold=True)
    chapter_tag(c, "≈ 20%", "空气阻力在回转能量损失中的占比", ramp(t, T[2], T[2] + 0.6) * a_in)
    cite_card(c, "挪威体育科学学院 · 博士论文", "回转能量损失：雪面阻力为主，空气约 20%", "M. Reid", ramp(t, T[2], T[2] + 0.8) * a_in)
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3  skidding = scraping
S3_SUBS = seq(["搓雪的时候，板指的方向和你前进的方向{w|不一致}，",
               "板的侧面横过来，像刮刀一样{r|刮着雪}往前走。",
               "刮起来的每一片雪，都是你的速度。",
               "研究者的模型也这么算：搓雪多了犁雪、刮冰的损耗；刻滑把它省掉，所以更快。",
               "看雪痕就知道：越宽，搓得越多；越细，越接近刻滑。"])
S3_DUR = end_of(S3_SUBS) + 0.8


def s3(c, t, fi):
    snow_field(c, 1.0)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S3_DUR - 0.6, S3_DUR))
    T = [a for _, a, _ in S3_SUBS]
    cx, cy = 820, 470
    skid = 38 * ramp(t, 1.5, 3.0)
    # velocity: straight down-right; ski heading rotated by skid angle
    vel = 25 * D2R
    # scraped band behind
    band = ramp(t, T[1], T[1] + 1.0)
    if band > 0:
        L = 600
        c.save(); c.translate(cx, cy); c.rotate(-vel)
        w = 1.6 * 150 * math.sin(skid * D2R)
        c.rectangle(-w / 2, -L, w, L); c.set_source_rgba(0.55, 0.62, 0.74, 0.35 * band * a_in); c.fill()
        c.restore()
        rng = np.random.default_rng(int(t * 30))
        for i in range(int(50 * band)):
            ang = -vel + math.pi / 2 + rng.normal(0, 0.5)
            dist = 120 + rng.random() * 160
            c.arc(cx + math.cos(ang) * dist * 0.6 + rng.normal(0, 10), cy + math.sin(ang) * dist * 0.4, 1.5 + 2 * rng.random(), 0, 2 * math.pi)
            c.set_source_rgba(0.95, 0.96, 0.98, 0.6 * band * a_in); c.fill()
    skis_head(c, cx, cy, vel + skid * D2R, 150, a_in)
    va = a_in * ramp(t, 0.8, 1.4)
    arrow(c, cx, cy, cx + math.sin(vel) * 300, cy + math.cos(vel) * 300, ICE, va, 4, 20)
    text(c, "前进方向", cx + math.sin(vel) * 300 + 20, cy + math.cos(vel) * 300, 24, ICE, va, bold=True)
    hx, hy = cx + math.sin(vel + skid * D2R) * 260, cy + math.cos(vel + skid * D2R) * 260
    c.set_dash([8, 6]); c.set_source_rgba(*GOLD, va); c.set_line_width(2); c.move_to(cx, cy); c.line_to(hx, hy); c.stroke(); c.set_dash([])
    text(c, "板指的方向", hx + 16, hy, 24, GOLD, va, bold=True)
    text(c, f"偏差 {skid:.0f}°", cx + 120, cy + 60, 30, RED, va * ramp(t, 1.5, 2.0), bold=True)
    # mini tracks comparison in the last sentence
    ma = a_in * ramp(t, T[4], T[4] + 0.8)
    if ma > 0:
        c.rectangle(1240, 160, 600, 640); c.set_source_rgba(0.05, 0.06, 0.08, 0.7 * ma); c.fill()
        for k, (sk, lab, col) in enumerate(((0.0, "细 = 刻滑", ICE), (0.5, "中", GOLD), (1.0, "宽 = 搓雪", RED))):
            x = 1340 + k * 200
            c.save(); c.rectangle(x - 95, 180, 190, 560); c.clip()
            track(c, x, 180, 740, 50, 300, sk, ma)
            c.restore()
            text(c, lab, x, 780, 22, col, ma, align="c", bold=True)
    chapter_tag(c, "刮雪", "板的方向 ≠ 前进方向", ramp(t, 0.6, 1.2) * a_in)
    cite_card(c, "arXiv:1812.02539", "搓雪多出犁雪、刮冰的损耗", "Modelling of carving turns", ramp(t, T[3], T[3] + 0.8) * a_in)
    model_note(c, a_in, "示意 · 俯视")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4  why not carve everything
S4_SUBS = seq(["那为什么不一直刻滑？",
               "同一个模型算出：纯刻滑只在大约 {b|8° 到 20°} 的坡上做得到。",
               "坡再陡，只靠刻滑，速度会越来越快——必须加一点搓雪来刹车。",
               "世界杯也一样：回转门距 13 米时，比 10 米刻滑得更多；\n弯一急、坡一陡，高手也得搓。"])
S4_DUR = end_of(S4_SUBS) + 0.8


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S4_DUR - 0.6, S4_DUR))
    T = [a for _, a, _ in S4_SUBS]
    # slope gauge: arc from 0 to 40 degrees
    cx, cy, R = 760, 760, 520
    ang = lambda d: -d * D2R
    c.set_line_width(2); c.set_source_rgba(*FAINT, a_in)
    c.arc_negative(cx, cy, R, 0, ang(40)); c.stroke()
    for d in range(0, 41, 5):
        x0, y0 = cx + math.cos(ang(d)) * R, cy + math.sin(ang(d)) * R
        x1, y1 = cx + math.cos(ang(d)) * (R + 16), cy + math.sin(ang(d)) * (R + 16)
        c.move_to(x0, y0); c.line_to(x1, y1); c.stroke()
        text(c, f"{d}°", cx + math.cos(ang(d)) * (R + 50), cy + math.sin(ang(d)) * (R + 50) + 8, 20, DIM, a_in, align="c")
    ka = a_in * ramp(t, T[1], T[1] + 0.8)
    c.move_to(cx, cy); c.arc_negative(cx, cy, R, ang(8), ang(20)); c.close_path(); c.set_source_rgba(*ICE, 0.25 * ka); c.fill()
    mid = 14
    text(c, "纯刻滑可行", cx + math.cos(ang(mid)) * R * 0.62, cy + math.sin(ang(mid)) * R * 0.62, 30, ICE, ka, align="c", bold=True)
    sa = a_in * ramp(t, T[2], T[2] + 0.8)
    c.move_to(cx, cy); c.arc_negative(cx, cy, R, ang(20), ang(40)); c.close_path(); c.set_source_rgba(*RED, 0.18 * sa); c.fill()
    text(c, "需要部分搓雪", cx + math.cos(ang(30)) * R * 0.66, cy + math.sin(ang(30)) * R * 0.66, 30, RED, sa, align="c", bold=True)
    # needle sweeping
    d = lerp(5, 35, 0.5 + 0.5 * math.sin((t - T[1]) * 0.6)) if t > T[1] else 5
    c.set_source_rgba(*INK, a_in); c.set_line_width(4)
    c.move_to(cx, cy); c.line_to(cx + math.cos(ang(d)) * (R - 20), cy + math.sin(ang(d)) * (R - 20)); c.stroke()
    c.set_source_rgba(*RIM, 0.9 * a_in); c.rectangle(cx - 60, cy, R + 120, 3); c.fill()
    ga = a_in * ramp(t, T[3], T[3] + 0.8)
    if ga > 0:
        rounded_rect(c, 1360, 300, 460, 260, 14); c.set_source_rgba(0.03, 0.04, 0.05, 0.9 * ga); c.fill()
        text(c, "回转门距", 1590, 360, 26, DIM, ga, align="c")
        text(c, "13 m > 10 m", 1590, 440, 52, GOLD, ga, align="c", bold=True)
        text(c, "刻滑程度", 1590, 500, 26, DIM, ga, align="c")
    chapter_tag(c, f"{d:.0f}°", "坡度 · 纯刻滑能不能做到", ramp(t, 0.6, 1.2) * a_in)
    cite_card(c, "arXiv:1812.02539", "纯刻滑约限于 8°–20° 的坡", "Modelling of carving turns", ramp(t, T[1], T[1] + 0.8) * (1 - ramp(t, T[3], T[3] + 0.4)) * a_in)
    cite_card(c, "挪威体育科学学院 · 博士论文", "13 m 门距比 10 m 刻滑程度更高", "M. Reid", ramp(t, T[3], T[3] + 0.8) * a_in)
    model_note(c, a_in, "8°–20° 为模型结果，随雪况和板的侧切变化")
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5 practice + end
S5_SUBS = seq(["所以：缓坡上练刻滑，体会弯里“不掉速”的感觉；",
               "陡坡上用搓雪控速——搓雪不是错，{w|是刹车}。"])
S5_DUR = end_of(S5_SUBS) + 4.0


def s5(c, t, fi):
    snow_field(c, 1.0)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S5_DUR - 1.4, S5_DUR - 0.4))
    down = lerp(-50, H + 50, ease_io((t - 0.3) / 6.0))
    track(c, 620, -50, down, 150, 520, 0.0, a_in)
    track(c, 1300, -50, down, 150, 520, 0.6, a_in)
    pill_label(c, "缓坡 · 刻滑", 620, 120, 32, ICE, a_in)
    pill_label(c, "陡坡 · 搓雪控速", 1300, 120, 32, GOLD, a_in)
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
    c.rectangle(0, 0, 1000, 800); c.set_source_rgb(0.13, 0.16, 0.21); c.fill()
    c.save(); c.rectangle(0, 0, 1000, 800); c.clip()
    track(c, 280, -20, 820, 140, 480, 0.0, 1.0)
    track(c, 720, -20, 820, 140, 480, 1.0, 1.0)
    c.restore()
    pill_label(c, "刻滑", 280, 70, 40, ICE, 1.0)
    pill_label(c, "搓雪", 720, 70, 40, RED, 1.0)


COVER = dict(lines=["搓雪", "为什么慢？"], stat="≈ 20%", caption="空气阻力只占回转速度损失约两成", color=ICE, figure=_cover_fig)
