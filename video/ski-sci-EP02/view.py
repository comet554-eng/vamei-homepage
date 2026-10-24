"""Side-view drawing: terrain profiles, rider, velocity decomposition, EFH colour/ruler."""
import math
from functools import lru_cache
import numpy as np
from common import *
import jump as J

TERRAIN = (0.13, 0.16, 0.21)
TERRAIN2 = (0.07, 0.085, 0.11)
RIM = (0.86, 0.90, 0.95)


class View:
    """world metres -> screen px. origin = lip (0,0)."""
    def __init__(self, ox, oy, k):
        self.ox, self.oy, self.k = ox, oy, k

    def p(self, x, y):
        return self.ox + x * self.k, self.oy - y * self.k

    def P(self, pts):
        pts = np.asarray(pts, float)
        return np.stack([self.ox + pts[:, 0] * self.k, self.oy - pts[:, 1] * self.k], 1)


@lru_cache(maxsize=4096)
def fl(v0):
    return J.flight(v0)


def efh_col(h):
    if h <= 0.5:
        return mix(ICE, ICE, 0)
    if h <= 1.2:
        return mix(ICE, GOLD, (h - 0.5) / 0.7)
    return mix(GOLD, RED, clamp((h - 1.2) / 1.3))


# ------------------------------------------------------------------ profiles (world)
def inrun(x0=-8.0, y0=2.2, a0=math.radians(-25), n=60):
    """cubic Hermite from in-run to lip, ending at the takeoff angle."""
    m0, m1 = math.tan(a0), math.tan(J.TH)
    L = -x0
    xs = np.linspace(x0, 0, n)
    s = (xs - x0) / L
    h00 = 2 * s ** 3 - 3 * s ** 2 + 1; h10 = s ** 3 - 2 * s ** 2 + s; h11 = s ** 3 - s ** 2
    ys = h00 * y0 + h10 * L * m0 + h11 * L * m1
    return np.stack([xs, ys], 1)


def tabletop_pts(x0=-8.0, x1=40.0):
    P = list(inrun(x0))
    P += [(J.DECK, 0.0), (J.X_END, -J.DROP), (x1, -J.DROP)]
    return np.array(P)


def const_pts(x0=-6.0, x1=34.0, h=0.5):
    xs, ys = J.const_efh_surface(h=h, x0=J.DECK, y0=0.0, x1=x1)
    P = list(inrun(x0)) + [(J.DECK * 0.5, 0.0)] + list(zip(xs, ys))
    return np.array(P), xs, ys


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


# ------------------------------------------------------------------ rider
def rider(c, x, y, ang, s, crouch=0.35, alpha=1.0, arms=0.0):
    """snowboarder seen from the side, board centre at screen (x,y), board angle ang (screen rad),
    s = px per metre. crouch 0..1. arms: 0 = out for balance, 1 = up."""
    if alpha <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(ang)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    # shadow-ish glow
    body = (0.92, 0.93, 0.95)
    # board
    c.move_to(-0.80 * s, -0.04 * s)
    c.curve_to(-0.86 * s, -0.04 * s, -0.86 * s, -0.12 * s, -0.80 * s, -0.12 * s)
    c.line_to(0.80 * s, -0.12 * s)
    c.curve_to(0.86 * s, -0.12 * s, 0.86 * s, -0.04 * s, 0.80 * s, -0.04 * s)
    c.close_path()
    c.set_source_rgba(*GOLD, alpha); c.fill()
    leg = 0.47 * s
    hip_h = (0.88 - 0.38 * crouch) * s
    lw = 0.10 * s
    hips = []
    for fx in (-0.26, 0.26):
        foot = (fx * s, -0.14 * s)
        hip = (fx * 0.35 * s, -0.14 * s - hip_h)
        d = math.dist(foot, hip)
        half = min(d / 2, leg * 0.999)
        bend = math.sqrt(max(leg * leg - half * half, 0))
        mx, my = (foot[0] + hip[0]) / 2, (foot[1] + hip[1]) / 2
        ux, uy = (hip[0] - foot[0]) / d, (hip[1] - foot[1]) / d
        sgn = 1 if fx > 0 else -1
        knee = (mx - uy * bend * sgn, my + ux * bend * sgn)
        c.move_to(*foot); c.line_to(*knee); c.line_to(*hip)
        c.set_source_rgba(*mix(body, (0.55, 0.60, 0.68), 0.5), alpha); c.set_line_width(lw); c.stroke()
        hips.append(hip)
    hx, hy = (hips[0][0] + hips[1][0]) / 2, (hips[0][1] + hips[1][1]) / 2
    tl = 0.58 * s
    lean = 0.10 * crouch
    sx, sy = hx + math.sin(lean) * tl, hy - math.cos(lean) * tl
    c.move_to(hx, hy); c.line_to(sx, sy)
    c.set_source_rgba(*body, alpha); c.set_line_width(0.15 * s); c.stroke()
    for side in (-1, 1):
        ex = sx + side * 0.30 * s
        ey = sy + lerp(0.10, -0.25, arms) * s
        hx2 = sx + side * 0.55 * s
        hy2 = sy + lerp(0.22, -0.45, arms) * s
        c.move_to(sx, sy + 0.04 * s); c.line_to(ex, ey); c.line_to(hx2, hy2)
        c.set_source_rgba(*body, 0.92 * alpha); c.set_line_width(0.08 * s); c.stroke()
    c.arc(sx, sy - 0.17 * s, 0.13 * s, 0, 2 * math.pi)
    c.set_source_rgba(*body, alpha); c.fill()
    c.restore()


# ------------------------------------------------------------------ vectors
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


def decomp(c, X, Y, v, imp, slope, k, alpha=1.0, show_parts=1.0, labels=True, tail=True, size=24):
    """velocity arrow ending at (X,Y) screen, plus along / normal parts drawn from the tail.
    imp, slope: world angles (rad, up positive). k: px per (m/s)."""
    vx, vy = v * math.cos(imp), v * math.sin(imp)
    tx, ty = math.cos(slope), math.sin(slope)
    nx, ny = -math.sin(slope), math.cos(slope)
    va = vx * tx + vy * ty
    vn = vx * nx + vy * ny
    X0, Y0 = X - vx * k, Y + vy * k
    A = (X0 + va * tx * k, Y0 - va * ty * k)
    N = (X0 + vn * nx * k, Y0 - vn * ny * k)
    if show_parts > 0:
        a2 = alpha * show_parts
        c.set_dash([7, 7]); c.set_line_width(1.6)
        c.set_source_rgba(*DIM, 0.8 * a2)
        c.move_to(*A); c.line_to(X, Y); c.move_to(*N); c.line_to(X, Y); c.stroke(); c.set_dash([])
        arrow(c, X0, Y0, *A, ICE, a2, 4, 18)
        if abs(vn) * k > 4:
            arrow(c, X0, Y0, *N, RED, a2, 4.5, 18)
        if labels:
            text(c, "顺着坡", A[0] + 14, A[1] - 12, size, ICE, a2, bold=True)
            text(c, f"垂直于坡 {abs(vn):.1f} m/s", (X0 + N[0]) / 2 - 16, (Y0 + N[1]) / 2 + 8, size, RED, a2, align="r", bold=True)
    arrow(c, X0, Y0, X, Y, INK, alpha, 4, 20)
    if labels and tail:
        mx, my = (X0 + X) / 2, (Y0 + Y) / 2
        L = math.hypot(X - X0, Y - Y0) or 1
        text(c, f"{v:.0f} m/s", mx - (Y - Y0) / L * 34, my + (X - X0) / L * 34 + 8, size, INK, alpha, align="c", bold=True)
    return abs(vn)


def ruler(c, h, alpha, x=1700, y0=820, ppm=150.0, hmax=2.6, label=True):
    """vertical 'equivalent drop' ruler: filled bar to h metres."""
    if alpha <= 0:
        return
    c.set_source_rgba(*FAINT, alpha); c.set_line_width(1.5)
    c.move_to(x, y0); c.line_to(x, y0 - hmax * ppm); c.stroke()
    c.move_to(x - 70, y0); c.line_to(x + 130, y0); c.stroke()
    for k in range(int(hmax / 0.5) + 1):
        yy = y0 - k * 0.5 * ppm
        c.move_to(x, yy); c.line_to(x - 12, yy); c.stroke()
        text(c, f"{k * 0.5:.1f}", x - 20, yy + 7, 18, DIM, alpha, align="r")
    hh = min(h, hmax) * ppm
    col = efh_col(h)
    rounded_rect(c, x + 14, y0 - hh, 46, max(hh, 2), 4)
    c.set_source_rgba(*col, 0.85 * alpha); c.fill()
    # little falling figure at the top of the bar
    c.arc(x + 37, y0 - hh - 22, 10, 0, 2 * math.pi); c.set_source_rgba(*INK, 0.9 * alpha); c.fill()
    if label:
        text(c, "等效下落高度", x + 37, y0 + 44, 22, DIM, alpha, align="c")
        text(c, f"{h:.2f} m", x + 37, y0 - hh - 48, 30, col, alpha, align="c", bold=True)
