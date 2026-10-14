"""Snowboard figures for 《单板 · 用数据说话》: profile rider (ride / fall back / fall forward), body hot-spot map, board top view."""
import math
from common import *
from art import _seg, LIMB, BODY, arrow

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


# ------------------------------------------------------------------ shared scene helpers for the 单板 series
SERIES_B = "单板 · 用数据说话"
SKI_C, BRD_C = (0.62, 0.66, 0.74), ICE


def subs(c, t, S):
    for s, a, b in S:
        subtitle(c, s, t, a, b)


def ground(c, gy, a, x0=0, x1=W):
    c.rectangle(x0, gy, x1 - x0, H - gy); c.set_source_rgba(*TERRAIN_B, a); c.fill()
    c.set_source_rgba(*RIM_B, 0.9 * a); c.rectangle(x0, gy - 1.5, x1 - x0, 3); c.fill()


TERRAIN_B = (0.13, 0.16, 0.21)
RIM_B = (0.86, 0.90, 0.95)


def title_card(c, t, t_in, t_out, title, sub):
    ta = ramp(t, t_in, t_in + 0.9) * (1 - ramp(t, t_out - 0.7, t_out))
    if ta <= 0:
        return
    c.set_source_rgba(*BG, 0.86 * ta); c.paint()
    text(c, SERIES_B, W / 2, 380, 30, DIM, ta, align="c", spacing=0.3)
    text(c, title, W / 2, 510, 92 if len(title) <= 11 else 76, INK, ta, align="c", bold=True)
    c.set_source_rgba(*GOLD, 0.8 * ta); c.rectangle(W / 2 - 160, 556, 320, 2); c.fill()
    text(c, sub, W / 2, 620, 32, GOLD, ta, align="c")


def end_card(c, a, nxt):
    if a <= 0:
        return
    text(c, "下一集", W / 2, 320, 34, DIM, a, align="c", spacing=0.3)
    text(c, nxt, W / 2, 440, 80 if len(nxt) <= 12 else 64, INK, a, align="c", bold=True)
    c.set_source_rgba(*GOLD, 0.8 * a); c.rectangle(W / 2 - 160, 486, 320, 2); c.fill()
    text(c, SERIES_B, W / 2, 560, 30, GOLD, a, align="c", spacing=0.3)


def numbered(c, items, t, alpha, x=520, y0=300, dy=170):
    """items: [(n, big, small, t_start)]"""
    for i, (n, big, small, ts) in enumerate(items):
        k = ramp(t, ts, ts + 0.6)
        if k <= 0:
            continue
        y = y0 + i * dy; a = alpha * k; xx = x - 40 * (1 - ease(k))
        c.arc(xx, y, 50, 0, 2 * math.pi); c.set_source_rgba(*GOLD, 0.9 * a); c.fill()
        text(c, n, xx, y + 20, 56, BG, a, align="c", bold=True)
        text(c, big, xx + 100, y + 16, 60, INK, a, bold=True)
        text(c, small, xx + 100, y + 66, 28, DIM, a)


def dots(c, x0, y0, n, cols, gap, r, hot, alpha, reveal=1.0, col=FAINT, hot_col=RED):
    """n dots, the first `hot` of them highlighted."""
    m = int(round(n * reveal))
    for i in range(m):
        cx = x0 + (i % cols) * gap; cy = y0 + (i // cols) * gap
        c.arc(cx, cy, r, 0, 2 * math.pi); c.set_source_rgba(*(hot_col if i < hot else col), alpha); c.fill()


# ------------------------------------------------------------------ forearm + hand, palm down, falling onto the snow
def forearm(c, x, y, s, alpha=1.0, guard=0.0, impact=0.0, spread=0.0, extend=0.0):
    """side view: elbow at upper-left, hand flat on the snow at (x, y). s = forearm length px.
    guard 0..1 draws a wrist guard with splint; spread shows load spreading along the splint;
    extend 0..1 bends the wrist back (hyper-extension)."""
    if alpha <= 0:
        return
    c.save(); c.translate(x, y)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    wr = (0.0, -0.09 * s)
    ang = math.radians(48 - 18 * extend)                  # forearm angle above the snow
    el = (wr[0] - s * math.cos(ang), wr[1] - s * math.sin(ang))
    _seg(c, [el, wr], BODY, 0.16 * s, alpha)
    # hand: palm on the snow, fingers forward
    c.move_to(-0.04 * s, -0.10 * s); c.line_to(0.30 * s, -0.05 * s); c.line_to(0.34 * s, -0.01 * s); c.line_to(-0.02 * s, -0.01 * s); c.close_path()
    c.set_source_rgba(*BODY, alpha); c.fill()
    _seg(c, [(-0.02 * s, -0.06 * s), (0.30 * s, -0.035 * s)], BODY, 0.08 * s, alpha)
    if guard > 0:
        ga = alpha * guard
        # sleeve over wrist + splint along the palm side
        c.save(); c.translate(*wr); c.rotate(-ang + math.pi)
        rounded_rect(c, -0.04 * s, -0.10 * s, 0.42 * s, 0.20 * s, 0.05 * s); c.set_source_rgba(0.22, 0.25, 0.32, 0.95 * ga); c.fill()
        c.restore()
        c.move_to(-0.32 * s * math.cos(ang), wr[1] + 0.32 * s * math.sin(-ang) + 0.07 * s)
        c.line_to(0.20 * s, -0.012 * s)
        c.set_source_rgba(*GOLD, ga); c.set_line_width(0.035 * s); c.stroke()
    if impact > 0:
        for i in range(3):
            xx = (-0.05 + 0.15 * i) * s
            arrow(c, xx, 0.42 * s, xx, 0.02 * s, RED, alpha * impact, 4, 16)
        if guard <= 0:
            c.arc(*wr, 0.12 * s, 0, 2 * math.pi); c.set_source_rgba(*RED, 0.9 * alpha * impact); c.set_line_width(4); c.stroke()
    if spread > 0:
        n = 6
        for i in range(n):
            f = i / (n - 1)
            px = wr[0] - 0.55 * s * f * math.cos(ang); py = wr[1] - 0.55 * s * f * math.sin(ang)
            c.arc(px, py, 0.05 * s * (1 - 0.5 * f), 0, 2 * math.pi)
            c.set_source_rgba(*GOLD, 0.7 * alpha * spread * (1 - 0.6 * f)); c.fill()
    c.restore()


# ------------------------------------------------------------------ ankle bones, schematic side view (lateral)
def ankle_bones(c, x, y, s, alpha=1.0, lp_mark=0.0, crack=0.0, overlap=0.0, label=True):
    """schematic lateral view of the ankle. (x, y) = top of the talus dome. s = scale px."""
    if alpha <= 0:
        return
    c.save(); c.translate(x, y)
    bone = (0.78, 0.76, 0.70)
    # tibia (behind) and fibula (front, lateral)
    rounded_rect(c, -0.42 * s, -1.6 * s, 0.70 * s, 1.55 * s, 0.12 * s); c.set_source_rgba(*bone, 0.55 * alpha); c.fill()
    rounded_rect(c, 0.10 * s, -1.5 * s, 0.22 * s, 1.75 * s, 0.10 * s); c.set_source_rgba(*bone, 0.85 * alpha); c.fill()
    # talus dome + body
    c.move_to(-0.55 * s, 0.30 * s)
    c.curve_to(-0.55 * s, -0.10 * s, -0.20 * s, -0.12 * s, 0.05 * s, -0.05 * s)
    c.curve_to(0.40 * s, 0.00 * s, 0.70 * s, 0.10 * s, 0.75 * s, 0.35 * s)
    c.curve_to(0.55 * s, 0.50 * s, -0.30 * s, 0.50 * s, -0.55 * s, 0.30 * s)
    c.close_path(); c.set_source_rgba(*bone, 0.95 * alpha); c.fill()
    # lateral process (wedge under the fibula tip)
    lp = [(0.05 * s, 0.30 * s), (0.30 * s, 0.30 * s), (0.18 * s, 0.52 * s)]
    c.move_to(*lp[0]); c.line_to(*lp[1]); c.line_to(*lp[2]); c.close_path()
    c.set_source_rgba(*mix(bone, RED, lp_mark), alpha); c.fill()
    # calcaneus
    c.move_to(-0.80 * s, 0.55 * s); c.curve_to(-0.85 * s, 0.95 * s, 0.20 * s, 1.05 * s, 0.85 * s, 0.75 * s)
    c.curve_to(0.70 * s, 0.52 * s, -0.40 * s, 0.45 * s, -0.80 * s, 0.55 * s)
    c.close_path(); c.set_source_rgba(*bone, 0.70 * alpha); c.fill()
    if overlap > 0:      # X-ray: bones overlap and wash out the small process
        c.rectangle(-0.9 * s, -0.2 * s, 1.9 * s, 1.3 * s); c.set_source_rgba(0.85, 0.88, 0.92, 0.35 * overlap * alpha); c.fill()
    if crack > 0:
        c.move_to(0.06 * s, 0.34 * s); c.line_to(0.14 * s, 0.38 * s); c.line_to(0.12 * s, 0.42 * s); c.line_to(0.26 * s, 0.40 * s)
        c.set_source_rgba(*RED, alpha * crack); c.set_line_width(4); c.stroke()
    if label:
        text(c, "胫骨", -0.10 * s, -1.0 * s, 0.13 * s, BG, alpha * 0.9, align="c", bold=True)
        text(c, "腓骨", 0.21 * s, -1.75 * s, 0.11 * s, DIM, alpha, align="c")
        text(c, "距骨", -0.15 * s, 0.25 * s, 0.13 * s, BG, alpha * 0.9, align="c", bold=True)
        text(c, "跟骨", -0.15 * s, 0.82 * s, 0.11 * s, BG, alpha * 0.8, align="c", bold=True)
    c.restore()
    return (x + 0.18 * s, y + 0.40 * s)


# ------------------------------------------------------------------ board cross-section with boot (carving, boot-out)
def board_section(c, x, y, s, edge, alpha=1.0, overhang=0.0, boot_mark=0.0):
    """board cross-section pivoting on its edge at (x, y) on the snow line; edge angle in rad.
    overhang: boot length beyond the board edge as a fraction of board width."""
    if alpha <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(edge)
    w = s
    rounded_rect(c, -w, -0.05 * s, w, 0.05 * s, 0.015 * s); c.set_source_rgba(*GOLD, alpha); c.fill()
    # boot across the board, toe toward the edge on the snow (x = 0), sticking out by `overhang`
    rounded_rect(c, -0.95 * w, -0.20 * s, 0.95 * w + overhang * w, 0.15 * s, 0.04 * s)
    c.set_source_rgba(*mix((0.30, 0.34, 0.42), RED, boot_mark), alpha); c.fill()
    # shin rising from the boot
    _seg(c, [(-0.45 * w, -0.20 * s), (-0.35 * w, -1.1 * s)], LIMB, 0.16 * s, alpha)
    c.restore()
