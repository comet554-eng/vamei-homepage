"""Snowboard figures for 《单板 · 用数据说话》: profile rider (ride / fall back / fall forward), body hot-spot map, board top view."""
import math
from common import *
from art import _seg, LIMB, BODY

BOARD = (0.16, 0.17, 0.21)

# profile rider facing +x (toe side to the right), board in cross-section under the feet. y up = negative.
_RIDE = dict(knee=(0.20, -0.48), hip=(-0.06, -0.86), sh=(0.06, -1.40), head=(0.11, -1.61),
             e1=(0.26, -1.16), h1=(0.44, -1.06), e2=(-0.06, -1.12), h2=(0.06, -0.95))
_BACK = dict(knee=(0.20, -0.36), hip=(-0.44, -0.13), sh=(-0.64, -0.64), head=(-0.70, -0.85),
             e1=(-0.32, -0.46), h1=(-0.12, -0.40), e2=(-0.86, -0.34), h2=(-1.02, -0.03))
_FWD = dict(knee=(0.44, -0.06), hip=(0.30, -0.50), sh=(0.76, -0.74), head=(0.93, -0.84),
            e1=(0.96, -0.42), h1=(1.10, -0.03), e2=(0.70, -0.40), h2=(0.86, -0.06))


def _pose(back, fwd):
    out = {}
    for k in _RIDE:
        x, y = _RIDE[k]
        x += (_BACK[k][0] - _RIDE[k][0]) * back + (_FWD[k][0] - _RIDE[k][0]) * fwd
        y += (_BACK[k][1] - _RIDE[k][1]) * back + (_FWD[k][1] - _RIDE[k][1]) * fwd
        out[k] = (x, y)
    return out


def rider_profile(c, x, y, s, back=0.0, fwd=0.0, wrist_mark=0.0, knee_mark=0.0, alpha=1.0, wobble=0.0):
    """ground point (x, y) = board centre on the snow. back/fwd 0..1 blend to a heel-side / toe-side fall."""
    if alpha <= 0:
        return {}
    P = _pose(back, fwd)
    c.save(); c.translate(x, y); c.rotate(wobble)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    # board cross-section: wide, thin slab
    rounded_rect(c, -0.20 * s, -0.045 * s, 0.40 * s, 0.045 * s, 0.015 * s)
    c.set_source_rgba(*GOLD, alpha); c.fill()
    S_ = lambda p: (p[0] * s, p[1] * s)
    ank = (0.0, -0.10 * s)
    _seg(c, [ank, S_(P["knee"]), S_(P["hip"])], LIMB, 0.11 * s, alpha)
    # boot + highback
    c.move_to(-0.10 * s, -0.045 * s); c.line_to(0.12 * s, -0.045 * s); c.line_to(0.10 * s, -0.22 * s); c.line_to(-0.08 * s, -0.30 * s); c.close_path()
    c.set_source_rgba(0.30, 0.34, 0.42, alpha); c.fill()
    _seg(c, [S_(P["e2"]), S_(P["sh"])], mix(BODY, FAINT, 0.35), 0.08 * s, 0.8 * alpha)
    _seg(c, [S_(P["e2"]), S_(P["h2"])], mix(BODY, FAINT, 0.35), 0.075 * s, 0.8 * alpha)
    _seg(c, [S_(P["hip"]), S_(P["sh"])], BODY, 0.17 * s, alpha)
    hx, hy = S_(P["head"])
    c.arc(hx, hy, 0.12 * s, 0, 2 * math.pi); c.set_source_rgba(*BODY, alpha); c.fill()
    _seg(c, [S_(P["sh"]), S_(P["e1"]), S_(P["h1"])], BODY, 0.08 * s, 0.95 * alpha)
    out = {}
    for key, mk, pt in (("wrist", wrist_mark, P["h2"] if back >= fwd else P["h1"]), ("knee", knee_mark, P["knee"])):
        px, py = S_(pt)
        out[key] = c.user_to_device(px, py)
        if mk > 0:
            for r, a in ((0.11, 0.95), (0.11 + 0.12 * mk, 0.5 * (1 - 0.6 * mk))):
                c.arc(px, py, r * s, 0, 2 * math.pi); c.set_source_rgba(*RED, a * mk * alpha); c.set_line_width(4); c.stroke()
    c.restore()
    return out


# front-facing body map: name -> (x, y) in units of body height s, ground at 0
SPOTS = dict(head=(0, -1.70), neck=(0, -1.50), shoulder=(-0.25, -1.40), shoulder_r=(0.25, -1.40),
             wrist=(-0.47, -0.86), wrist_r=(0.47, -0.86), knee=(-0.12, -0.48), knee_r=(0.12, -0.48),
             ankle=(-0.13, -0.09), ankle_r=(0.13, -0.09), spine=(0, -1.0))


def body_map(c, x, y, s, spots=(), alpha=1.0, col=None):
    """spots: [(name, strength 0..1, colour)]  -> glowing discs on a neutral silhouette."""
    if alpha <= 0:
        return
    col = col or (0.40, 0.44, 0.52)
    c.save(); c.translate(x, y)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    for side in (-1, 1):
        _seg(c, [(side * 0.11 * s, -0.94 * s), (side * 0.12 * s, -0.48 * s), (side * 0.13 * s, -0.06 * s)], col, 0.12 * s, alpha)
        _seg(c, [(side * 0.19 * s, -1.42 * s), (side * 0.33 * s, -1.14 * s), (side * 0.47 * s, -0.86 * s)], col, 0.08 * s, alpha)
    rounded_rect(c, -0.21 * s, -1.50 * s, 0.42 * s, 0.60 * s, 0.10 * s); c.set_source_rgba(*col, alpha); c.fill()
    c.arc(0, -1.70 * s, 0.13 * s, 0, 2 * math.pi); c.fill()
    for name, k, sc in spots:
        if k <= 0:
            continue
        px, py = SPOTS[name][0] * s, SPOTS[name][1] * s
        r = (0.05 + 0.11 * math.sqrt(k)) * s
        g = cairo.RadialGradient(px, py, 0, px, py, r * 1.8)
        g.add_color_stop_rgba(0, *sc, 0.95 * alpha); g.add_color_stop_rgba(0.45, *sc, 0.55 * alpha); g.add_color_stop_rgba(1, *sc, 0)
        c.arc(px, py, r * 1.8, 0, 2 * math.pi); c.set_source(g); c.fill()
    c.restore()


def board_top(c, cx, cy, k, alpha=1.0, angles=(15, -15), lock=0.0):
    """snowboard seen from above, length 1.55 k, with two bindings (duck stance)."""
    if alpha <= 0:
        return
    L, Wd = 1.55 * k, 0.26 * k
    rounded_rect(c, cx - L / 2, cy - Wd / 2, L, Wd, Wd * 0.48)
    c.set_source_rgba(*mix(BOARD, GOLD, 0.25), alpha); c.fill_preserve()
    c.set_source_rgba(*GOLD, 0.85 * alpha); c.set_line_width(2); c.stroke()
    for fx, a in zip((-0.27, 0.27), angles):
        c.save(); c.translate(cx + fx * k, cy); c.rotate(math.radians(90 + a))
        rounded_rect(c, -0.13 * k, -0.045 * k, 0.26 * k, 0.09 * k, 0.03 * k)
        c.set_source_rgba(*mix((0.30, 0.34, 0.42), RED, lock * 0.5), alpha); c.fill(); c.restore()
