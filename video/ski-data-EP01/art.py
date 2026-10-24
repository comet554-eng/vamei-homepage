"""Shared drawing for 《雪板为什么能滑？》: terrain, arrows, skier, micro-scale snow, physics numbers."""
import math
import numpy as np
from common import *

TERRAIN = (0.13, 0.16, 0.21)
TERRAIN2 = (0.07, 0.085, 0.11)
RIM = (0.86, 0.90, 0.95)
WARM = (1.0, 0.62, 0.30)


class View:
    """world metres -> screen px. origin = lip (0,0)."""
    def __init__(self, ox, oy, k):
        self.ox, self.oy, self.k = ox, oy, k

    def p(self, x, y):
        return self.ox + x * self.k, self.oy - y * self.k

    def P(self, pts):
        pts = np.asarray(pts, float)
        return np.stack([self.ox + pts[:, 0] * self.k, self.oy - pts[:, 1] * self.k], 1)


def fill_terrain(c, S, alpha=1.0, upto=None, rim=True, col=TERRAIN, rim_col=RIM, rim_w=3.0):
    """S: screen pts of the surface (left->right). upto: reveal only x <= upto (px)."""
    if upto is not None:
        keep = S[:, 0] <= upto
        if keep.sum() < 1:
            return
        j = int(keep.sum())
        if j < len(S):
            a, b = S[j - 1], S[j]
            k = (upto - a[0]) / max(b[0] - a[0], 1e-9)
            S = np.vstack([S[:j], a + (b - a) * k])
        if len(S) < 2:
            return
    c.move_to(S[0, 0], H + 10)
    for p in S:
        c.line_to(*p)
    c.line_to(S[-1, 0], H + 10); c.close_path()
    g = cairo.LinearGradient(0, S[:, 1].min(), 0, H)
    g.add_color_stop_rgba(0, *col, alpha); g.add_color_stop_rgba(1, *TERRAIN2, alpha)
    c.set_source(g); c.fill()
    if rim:
        c.move_to(*S[0])
        for p in S[1:]:
            c.line_to(*p)
        c.set_source_rgba(*rim_col, 0.9 * alpha); c.set_line_width(rim_w); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()


def polyline(c, S, col, alpha=1.0, w=2.0, dash=None):
    if len(S) < 2 or alpha <= 0:
        return
    if dash:
        c.set_dash(dash)
    c.move_to(*S[0])
    for p in S[1:]:
        c.line_to(*p)
    c.set_source_rgba(*col, alpha); c.set_line_width(w); c.stroke()
    c.set_dash([])


def arrow(c, x0, y0, x1, y1, col, alpha=1.0, w=4.0, head=18):
    if alpha <= 0:
        return
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 2:
        return
    ang = math.atan2(y1 - y0, x1 - x0)
    hx, hy = x1 - math.cos(ang) * head * 0.7, y1 - math.sin(ang) * head * 0.7
    glow_line(c, x0, y0, hx, hy, col, w, alpha, w * 3)
    arrow_head(c, x1, y1, ang, head, col, alpha)


# ------------------------------------------------------------------ skier (side view, facing +x)
def skier(c, x, y, s, crouch=0.3, alpha=1.0, phase=0.0, col=(0.92, 0.93, 0.95)):
    if alpha <= 0:
        return
    c.save(); c.translate(x, y)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    # ski with upturned tip
    c.move_to(-0.85 * s, -0.02 * s); c.line_to(0.70 * s, -0.02 * s)
    c.curve_to(0.82 * s, -0.02 * s, 0.88 * s, -0.06 * s, 0.92 * s, -0.14 * s)
    c.set_source_rgba(*GOLD, alpha); c.set_line_width(0.06 * s); c.stroke()
    k = crouch
    ank = (0.0, -0.16 * s)
    knee = ((0.20 + 0.10 * k) * s, (-0.55 + 0.10 * k) * s)
    hip = ((-0.06 - 0.06 * k) * s, (-0.95 + 0.22 * k) * s)
    sh = ((0.16 + 0.10 * k) * s, (-1.48 + 0.25 * k) * s)
    c.move_to(*ank); c.line_to(*knee); c.line_to(*hip)
    c.set_source_rgba(*mix(col, (0.55, 0.60, 0.68), 0.45), alpha); c.set_line_width(0.11 * s); c.stroke()
    c.move_to(-0.06 * s, -0.10 * s); c.line_to(0.12 * s, -0.10 * s); c.line_to(0.10 * s, -0.24 * s); c.line_to(-0.04 * s, -0.26 * s); c.close_path()
    c.set_source_rgba(0.30, 0.34, 0.42, alpha); c.fill()
    c.move_to(*hip); c.line_to(*sh)
    c.set_source_rgba(*col, alpha); c.set_line_width(0.16 * s); c.stroke()
    c.arc(sh[0] + 0.09 * s, sh[1] - 0.19 * s, 0.12 * s, 0, 2 * math.pi); c.set_source_rgba(*col, alpha); c.fill()
    sw = 0.08 * math.sin(phase)
    el = (sh[0] + 0.22 * s, sh[1] + 0.30 * s)
    hd = (sh[0] + (0.42 + sw) * s, sh[1] + 0.45 * s)
    c.move_to(*sh); c.line_to(*el); c.line_to(*hd)
    c.set_source_rgba(*col, 0.92 * alpha); c.set_line_width(0.08 * s); c.stroke()
    c.move_to(*hd); c.line_to(hd[0] - 0.75 * s, -0.02 * s)
    c.set_source_rgba(0.62, 0.66, 0.72, 0.9 * alpha); c.set_line_width(0.025 * s); c.stroke()
    c.restore()


def snow_ground(c, y, t, speed, alpha=1.0, seed=3):
    """flat snow surface at screen y, scrolling left at `speed` px/s (camera follows the skier)."""
    c.rectangle(0, y, W, H - y)
    g = cairo.LinearGradient(0, y, 0, H)
    g.add_color_stop_rgba(0, *TERRAIN, alpha); g.add_color_stop_rgba(1, *TERRAIN2, alpha)
    c.set_source(g); c.fill()
    c.set_source_rgba(*RIM, 0.9 * alpha); c.rectangle(0, y - 1.5, W, 3); c.fill()
    rng = np.random.default_rng(seed)
    xs = rng.random(160) * (W + 200); ys = y + 8 + rng.random(160) ** 2 * (H - y - 20)
    rs = 0.8 + rng.random(160) * 1.6
    off = (t * speed) % (W + 200)
    for xx, yy, rr in zip(xs, ys, rs):
        sx = (xx - off * (0.4 + 0.6 * (yy - y) / (H - y))) % (W + 200) - 100
        c.arc(sx, yy, rr, 0, 2 * math.pi); c.set_source_rgba(0.8, 0.86, 0.95, 0.25 * alpha); c.fill()




# ------------------------------------------------------------------ data (see video/ski-data-EP01-方案.md)
# Johnson, Ettlinger, Shealy, ASTM STP 1510 (2009): Vermont 1972-2006, index 1972 = 100
LOWER_LEG_END = 100 * (1 - 0.87)          # twist-related lower leg injuries, -87 %
KNEE_PEAK = 100 * (1 + 2.68)              # severe knee sprains +268 % to early 1990s
KNEE_END = KNEE_PEAK * (1 - 0.37)         # then -37 %
# Posch et al. 2020: 282 MRI-confirmed knee injuries, all ACL
POSCH_N, POSCH_COMB = 282, 182
# Bere et al. 2011: 20 World Cup ACL cases, 10 slip-catch
BERE_N, BERE_SLIP = 20, 10
TRAIN_REDUCTION = 0.62                    # Ettlinger et al. 1995, as reported

LIMB = (0.62, 0.66, 0.74)
BODY = (0.92, 0.93, 0.95)


def _seg(c, pts, col, w, alpha):
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.set_source_rgba(*col, alpha); c.set_line_width(w); c.stroke()


# ------------------------------------------------------------------ front view skier (facing the camera)
def skier_front(c, x, y, s, lean=0.0, valgus=0.0, out_edge=0.5, in_edge=0.5, out_slide=0.0, alpha=1.0, knee_mark=0.0,
                inner_valgus=0.0):
    """ground point (x,y). lean>0 leans to screen-left (turn to the left: outer leg = screen-right).
    valgus: outer (right) knee collapses inward 0..1. out_edge/in_edge: ski edge angles (rad).
    out_slide: outer ski displaced to the right (m)."""
    if alpha <= 0:
        return
    c.save(); c.translate(x, y)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    # skis as cross-sections
    for fx, edge, sl in ((-0.16, in_edge, 0.0), (0.16 + out_slide, out_edge, out_slide)):
        c.save(); c.translate(fx * s, 0); c.rotate(-edge)
        rounded_rect(c, -0.09 * s, -0.045 * s, 0.18 * s, 0.045 * s, 0.012 * s)
        c.set_source_rgba(*GOLD, alpha); c.fill(); c.restore()
    c.rotate(-lean)
    feet = [(-0.16 * s, -0.06 * s), ((0.16 + out_slide * math.cos(lean)) * s, -0.06 * s + out_slide * math.sin(lean) * s)]
    hips = [(-0.11 * s, -0.92 * s), (0.11 * s, -0.92 * s)]
    knees = []
    for i, (f, h) in enumerate(zip(feet, hips)):
        mx, my = (f[0] + h[0]) / 2, (f[1] + h[1]) / 2
        v = valgus if i == 1 else inner_valgus
        sgn = -1 if i == 1 else 1
        knees.append((mx + sgn * 0.13 * v * s + (0.02 * s if i == 1 else -0.02 * s), my))
    for f, k, h in zip(feet, knees, hips):
        _seg(c, [f, k, h], LIMB, 0.10 * s, alpha)
        c.arc(f[0], f[1] - 0.06 * s, 0.07 * s, 0, 2 * math.pi); c.set_source_rgba(0.30, 0.34, 0.42, alpha); c.fill()
    sh = (0, -1.52 * s)
    _seg(c, [(0, -0.92 * s), sh], BODY, 0.24 * s, alpha)
    for side in (-1, 1):
        _seg(c, [(side * 0.14 * s, -1.45 * s), (side * 0.42 * s, -1.15 * s), (side * 0.55 * s, -1.0 * s)], BODY, 0.08 * s, 0.92 * alpha)
    c.arc(0, -1.72 * s, 0.13 * s, 0, 2 * math.pi); c.set_source_rgba(*BODY, alpha); c.fill()
    if knee_mark > 0:
        for i in ((1,) if inner_valgus == 0 else (0,)):
            kx, ky = knees[i]
            c.arc(kx, ky, 0.13 * s, 0, 2 * math.pi); c.set_source_rgba(*RED, 0.9 * knee_mark * alpha); c.set_line_width(4); c.stroke()
            c.arc(kx, ky, 0.22 * s, -2.3, -0.6); c.set_source_rgba(*RED, 0.8 * knee_mark * alpha); c.set_line_width(3); c.stroke()
            ax, ay = kx + 0.22 * s * math.cos(-0.6), ky + 0.22 * s * math.sin(-0.6)
            c.move_to(ax, ay); c.line_to(ax - 14, ay - 4); c.line_to(ax - 4, ay + 12); c.close_path(); c.fill()
    c.restore()


# ------------------------------------------------------------------ side view with free pose (facing +x)
def side_pose(c, x, y, s, back=0.0, pitch=0.0, alpha=1.0, tail_mark=0.0, knee_mark=0.0, arm_back=0.0):
    """back 0 = balanced, 1 = 'phantom foot' (off-balance to the rear, hips below knees).
    pitch: ski rotation (rad, + = tip up). ski centre at (x,y)."""
    if alpha <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(-pitch)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    # ski
    c.move_to(-0.85 * s, -0.02 * s); c.line_to(0.70 * s, -0.02 * s)
    c.curve_to(0.82 * s, -0.02 * s, 0.88 * s, -0.06 * s, 0.92 * s, -0.14 * s)
    c.set_source_rgba(*GOLD, alpha); c.set_line_width(0.06 * s); c.stroke()
    if tail_mark > 0:
        c.move_to(-0.85 * s, -0.02 * s); c.line_to(-0.25 * s, -0.02 * s)
        c.set_source_rgba(*RED, tail_mark * alpha); c.set_line_width(0.07 * s); c.stroke()
    c.rotate(pitch)
    b = back
    ank = (0.0, -0.16 * s)
    knee = (lerp(0.24, 0.30, b) * s, lerp(-0.55, -0.48, b) * s)
    hip = (lerp(-0.10, -0.42, b) * s, lerp(-0.90, -0.40, b) * s)
    sh = (lerp(0.16, -0.38, b) * s, lerp(-1.42, -1.0, b) * s)
    _seg(c, [ank, knee, hip], LIMB, 0.11 * s, alpha)
    c.move_to(-0.06 * s, -0.10 * s); c.line_to(0.12 * s, -0.10 * s); c.line_to(0.10 * s, -0.26 * s); c.line_to(-0.04 * s, -0.28 * s); c.close_path()
    c.set_source_rgba(0.30, 0.34, 0.42, alpha); c.fill()
    _seg(c, [hip, sh], BODY, 0.16 * s, alpha)
    hx = sh[0] + lerp(0.09, -0.06, b) * s
    c.arc(hx, sh[1] - 0.19 * s, 0.12 * s, 0, 2 * math.pi); c.set_source_rgba(*BODY, alpha); c.fill()
    # front arm and (uphill) arm that drifts back
    _seg(c, [sh, (sh[0] + 0.25 * s, sh[1] + 0.28 * s), (sh[0] + 0.45 * s, sh[1] + 0.40 * s)], BODY, 0.08 * s, 0.92 * alpha)
    ab = arm_back
    _seg(c, [sh, (sh[0] + lerp(0.20, -0.25, ab) * s, sh[1] + lerp(0.30, 0.22, ab) * s),
             (sh[0] + lerp(0.40, -0.50, ab) * s, sh[1] + lerp(0.42, 0.10, ab) * s)], mix(BODY, RED, ab * 0.8), 0.08 * s, 0.85 * alpha)
    if knee_mark > 0:
        c.arc(knee[0], knee[1], 0.12 * s, 0, 2 * math.pi); c.set_source_rgba(*RED, 0.9 * knee_mark * alpha); c.set_line_width(4); c.stroke()
    c.restore()
    return dict(knee=(x + knee[0], y + knee[1]), hip=(x + hip[0], y + hip[1]), sh=(x + sh[0], y + sh[1]))


# ------------------------------------------------------------------ data graphics
def dot_matrix(c, x0, y0, n, cols, gap, r, colors, alpha=1.0, reveal=1.0):
    """colors: function i -> rgb. reveal: fraction of dots shown."""
    m = int(round(n * reveal))
    for i in range(m):
        cx = x0 + (i % cols) * gap; cy = y0 + (i // cols) * gap
        c.arc(cx, cy, r, 0, 2 * math.pi); c.set_source_rgba(*colors(i), alpha); c.fill()
