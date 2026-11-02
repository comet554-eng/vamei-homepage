"""S3: the board is not straight — sidecut circle (computed from ski.py)."""
import math
import numpy as np
from common import *
from draw import *
import ski

S3_DUR = 30.0
S3_SUBS = [
    ("从正上方看这块板：两条边{b|不是直的}。", 1.0, 6.0),
    ("它们微微向里收，是一段圆弧——", 6.6, 10.8),
    ("把这段弧补成整圆，半径大约 {w|8 米}。\n这叫{w|侧切半径}。", 11.4, 18.6),
    ("落到板上，每条边中间只往里收了约 {w|2.4 厘米}，\n板腰比两头窄两成。", 19.4, 26.0),
    ("板平放在雪上时，这道弧什么也不做。", 26.4, 29.8),
]
CX, CY_R = 0.0, None
_cx, _cy = ski.sidecut_circle()


def view(t):
    """(focus world point, px per m). Zoom out 11.4-15.4, back in 18.6-21.6."""
    s_near, s_far = 640.0, 44.0
    f_near = (0.0, 0.0)
    f_far = (0.0, _cy * 0.74)
    k = ease_io((t - 11.4) / 4.0) * (1 - ease_io((t - 18.6) / 3.0))
    s = math.exp(lerp(math.log(s_near), math.log(s_far), k))
    f = (lerp(f_near[0], f_far[0], k), lerp(f_near[1], f_far[1], k))
    return f, s, k


def s3(c, t, fi):
    paint_bg(c, BG := (0.02, 0.025, 0.035))
    paint_snow(c, oy=600, alpha=0.30)
    f, s, k = view(t)
    ox, oy = W / 2 - f[0] * s, H / 2 - 80 - 40 * k - f[1] * s
    X = lambda x: ox + x * s
    Y = lambda y: oy + y * s
    board_top(c, X(0), Y(0), 0.0, s, rider=False)
    # chord (straight reference) and highlighted arc on the +y edge
    C2 = ski.BOARD_C / 2
    ea = ramp(t, 3.0, 4.5)
    if ea > 0:
        c.set_dash([10, 8]); c.set_source_rgba(1, 1, 1, 0.55 * ea * (1 - k)); c.set_line_width(1.6)
        c.move_to(X(-C2), Y(ski.BOARD_W / 2)); c.line_to(X(C2), Y(ski.BOARD_W / 2)); c.stroke(); c.set_dash([])
        xs = np.linspace(-C2, C2, 80)
        ys = _cy - np.sqrt(ski.R_SC ** 2 - xs ** 2)
        c.move_to(X(xs[0]), Y(ys[0]))
        for x, y in zip(xs[1:], ys[1:]):
            c.line_to(X(x), Y(y))
        c.set_source_rgba(*GOLD, ea * ramp(t, 6.6, 8.0)); c.set_line_width(4); c.stroke()
        text(c, "直线", X(C2) + 18, Y(ski.BOARD_W / 2) + 8, 22, (0.85, 0.87, 0.9), ea * (1 - k))
    # full circle
    ca = ramp(t, 11.6, 14.0) * (1 - ramp(t, 18.6, 20.0))
    if ca > 0:
        c.set_source_rgba(*GOLD, 0.75 * ca); c.set_line_width(2.0)
        c.arc(X(_cx), Y(_cy), ski.R_SC * s, 0, 2 * math.pi); c.stroke()
        c.arc(X(_cx), Y(_cy), 5, 0, 2 * math.pi); c.fill()
        c.set_dash([8, 8]); c.move_to(X(_cx), Y(_cy)); c.line_to(X(_cx), Y(_cy - ski.R_SC)); c.stroke(); c.set_dash([])
        pill_label(c, f"侧切半径 ≈ {ski.R_SC:.0f} m", X(_cx) + 120, Y(_cy - ski.R_SC / 2), 30, GOLD, ca)
    # depth call-out
    da = ramp(t, 20.6, 22.0)
    if da > 0:
        d = ski.sag()
        y0, y1 = Y(ski.BOARD_W / 2), Y(ski.BOARD_W / 2 - d)
        c.set_source_rgba(1, 1, 1, 0.9 * da); c.set_line_width(2)
        x = X(0)
        for yy in (y0, y1):
            c.move_to(x - 30, yy); c.line_to(x + 30, yy)
        c.stroke()
        arrow_head(c, x, y1, -math.pi / 2, 12, (1, 1, 1), da)
        arrow_head(c, x, y0, math.pi / 2, 12, (1, 1, 1), da)
        c.move_to(x, y0); c.line_to(x, y1); c.stroke()
        pill_label(c, f"每边往里收 {d * 100:.1f} cm", x, y0 + 92, 30, GOLD, da)
        wt = (ski.BOARD_W - 2 * d) / ski.BOARD_W
        pill_label(c, f"板腰 {100 * (ski.BOARD_W - 2 * d):.0f} cm  /  两头 {100 * ski.BOARD_W:.0f} cm", X(0), Y(-ski.BOARD_W / 2) - 60, 24, (0.85, 0.87, 0.9), da)
    lab, bar = (("2 m", 2 * s) if s < 150 else ("20 cm", 0.2 * s))
    chapter_tag(c, lab, "侧切 · 俯视", alpha=window(t, 0.3, S3_DUR + 1, 0.5), bar=bar)
    cite_card(c, "arXiv physics/0310086", "《理想刻滑方程及其应用》", "Jentschura · Fahrbach · d ≈ C²/(8R)",
              alpha=window(t, 19.6, 26.0, 0.5))
    for st, a, b in S3_SUBS:
        subtitle(c, st, t, a, b)
    fade_black(c, 1 - ramp(t, 0, 0.8))
    overlays(c, fi)
