"""Top-view scenes: S1 groomed slope + title, S2 skid vs carve, S3 sidecut geometry, S7 return."""
import math
import numpy as np
import cairo
from common import *
from draw import *
import ski

BG2 = (0.02, 0.025, 0.035)


def nice_bar(s):
    """px/m -> (label, px) with bar 110..300 px"""
    for L, lab in ((10, "10 m"), (5, "5 m"), (2, "2 m"), (1, "1 m"), (0.5, "50 cm"), (0.2, "20 cm"), (0.1, "10 cm"),
                   (0.05, "5 cm"), (0.02, "2 cm")):
        if 110 <= L * s <= 300:
            return lab, L * s
    return "1 m", s


def integrate_turns(n_turns, Lt, th_min, th_max, R=ski.R_SC, ds=0.02, swing=None):
    """S-turns: curvature 1/(R cos th) * profile, sign alternates. Heading symmetric about fall line."""
    prof = lambda k: math.sin(math.pi * k) ** 1.2
    thk = lambda k: th_min + (th_max - th_min) * math.sin(math.pi * k) ** 2
    # heading swing produced by one turn
    ks = np.linspace(0, 1, 400)
    sw = np.trapz([prof(k) / ski.turn_radius(thk(k), R) for k in ks], ks) * Lt
    h = math.pi / 2 - sw / 2
    x = y = s = 0.0
    out = []
    while s < n_turns * Lt:
        k = (s % Lt) / Lt
        sgn = 1 if int(s // Lt) % 2 == 0 else -1
        th = thk(k)
        h += sgn * prof(k) / ski.turn_radius(th, R) * ds
        x += math.cos(h) * ds; y += math.sin(h) * ds; s += ds
        out.append((x, y, h, th * (1 if prof(k) > 0.08 else 0), s, sgn))
    a = np.array(out)
    a[:, 0] -= a[:, 0].mean()
    return a


TRACK = integrate_turns(7, 15.0, math.radians(8), math.radians(55))   # x,y,h,theta,s,sign


def at_s(tr, s):
    i = int(np.clip(np.searchsorted(tr[:, 4], s), 1, len(tr) - 1))
    return tr[i]


def draw_track_scene(c, s_r, S=42.0, rider_y=H * 0.68, alpha=1.0, show_rider=True, extra=None, focus=None):
    """camera follows rider at track length s_r (or holds on world point `focus`)."""
    r = at_s(TRACK, s_r)
    f = focus if focus is not None else (0.35 * r[0], r[1])
    camx = f[0]
    oy = f[1] * S - rider_y
    paint_snow(c, oy=oy, alpha=alpha)
    sx = lambda x: W / 2 + (x - camx) * S
    sy = lambda y: rider_y + (y - f[1]) * S
    m = (TRACK[:, 4] <= s_r)
    P = np.stack([sx(TRACK[m, 0]), sy(TRACK[m, 1])], 1)
    vis = (P[:, 1] > -60) & (P[:, 1] < H + 60)
    carve_line(c, P[vis], alpha)
    if show_rider:
        board_top(c, sx(r[0]), sy(r[1]), r[2], S, alpha)
    if extra:
        extra(c, sx, sy)
    return sx, sy


# ------------------------------------------------------------------ S1
S1_DUR = 22.0
S1_SUBS = [
    ("清晨，雪道刚被压过，平整得像一张纸。", 1.0, 6.4),
    ("一块单板滑过，留下一道干净的{b|S 形}细痕。", 7.0, 12.6),
]


def s1(c, t, fi):
    paint_bg(c, BG2)
    draw_track_scene(c, 3.6 * (t + 3.0))
    chapter_tag(c, "5 m", "雪道 · 俯视", alpha=window(t, 0.8, 13.6, 0.8), bar=5 * 42)
    for s, a, b in S1_SUBS:
        subtitle(c, s, t, a, b)
    fade_black(c, 0.80 * ramp(t, 13.4, 14.8))
    ta = window(t, 14.0, S1_DUR - 0.3, 1.0)
    if ta > 0:
        rich(c, [("板子为什么会", INK), ("自己", GOLD), ("转弯？", INK)], W / 2, H / 2 + 10, 92, ta)
        text(c, "关于刻滑与侧切", W / 2, H / 2 + 92, 30, DIM, ta, align="c", spacing=0.12)
        c.set_source_rgba(*FAINT, ta); c.rectangle(W / 2 - 160, H / 2 + 44, 320, 1.2); c.fill()
    fade_black(c, 1 - ramp(t, 0, 1.4))
    fade_black(c, ramp(t, S1_DUR - 0.5, S1_DUR))
    overlays(c, fi)


# ------------------------------------------------------------------ S2
S2_DUR = 24.0
S2_SUBS = [
    ("转弯有两种。一种是{w|推雪}：板横着蹭过雪面，", 1.0, 6.0),
    ("留下一道宽宽的刮痕，扬起一片雪。", 6.4, 10.8),
    ("另一种是{b|刻滑}：板立在刃上，像车轮压着轨道走，", 11.4, 16.6),
    ("只留下一道细线。刻滑时人并没有拧板——\n是板{b|自己}弯过去的。", 17.0, 23.6),
]
TURN = integrate_turns(1, 11.0, math.radians(10), math.radians(55))


def _panel(c, x0, t, t0, t1, mode):
    S = 58.0
    k = clamp((t - t0) / (t1 - t0))
    s_r = k * TURN[-1, 4]
    c.save(); c.rectangle(x0, 0, W / 2, H); c.clip()
    paint_snow(c, oy=200 + x0 * 0.3, x0=x0, w=W / 2)
    sx = lambda x: x0 + W / 4 + x * S - 60
    sy = lambda y: 250 + y * S
    m = TURN[:, 4] <= s_r
    P = np.stack([sx(TURN[m, 0]), sy(TURN[m, 1])], 1)
    r = at_s(TURN, max(s_r, 0.05))
    kk = (r[4] % 11.0) / 11.0
    if mode == "skid":
        yaw = np.radians(38) * np.sin(np.pi * np.clip(TURN[m, 4] / TURN[-1, 4], 0, 1)) ** 0.8
        wid = ski.BOARD_L * np.sin(yaw) * S + 10
        skid_band(c, P, wid)
        y_now = math.radians(38) * math.sin(math.pi * kk) ** 0.8
        board_top(c, sx(r[0]), sy(r[1]), r[2] + y_now, S)
        if 0 < k < 1:
            spray(c, sx(r[0]), sy(r[1]), r[2], math.sin(math.pi * kk) ** 2, t, S, seed=3)
        pill_label(c, "推雪 · 侧滑", x0 + W / 4, 150, 30, GOLD, ramp(t, t0 - 0.6, t0))
    else:
        carve_line(c, P, 1.0, 2.4)
        board_top(c, sx(r[0]), sy(r[1]), r[2], S)
        pill_label(c, "刻滑", x0 + W / 4, 150, 30, ICE, ramp(t, t0 - 0.6, t0))
    c.restore()


def s2(c, t, fi):
    paint_bg(c, BG2)
    _panel(c, 0, t, 1.2, 9.6, "skid")
    if t > 10.2:
        c.push_group(); _panel(c, W / 2, t, 11.6, 20.0, "carve"); c.pop_group_to_source()
        c.paint_with_alpha(ramp(t, 10.2, 11.2))
    c.set_source_rgba(0, 0, 0, 0.6); c.rectangle(W / 2 - 1, 0, 2, H); c.fill()
    chapter_tag(c, "2 m", "两种转弯 · 俯视", alpha=window(t, 0.3, S2_DUR + 1, 0.5), bar=2 * 58)
    for s, a, b in S2_SUBS:
        subtitle(c, s, t, a, b)
    fade_black(c, 1 - ramp(t, 0, 0.8))
    fade_black(c, ramp(t, S2_DUR - 0.5, S2_DUR))
    overlays(c, fi)
