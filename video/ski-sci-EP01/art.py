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


# ------------------------------------------------------------------ physics numbers (all computed, see 方案)
G = 9.81
T0 = 273.15
RHO_W, RHO_I, L_F = 999.84, 916.7, 333.55e3          # kg/m3, kg/m3, J/kg
DTDP = T0 * (1 / RHO_W - 1 / RHO_I) / L_F             # K/Pa (Clausius-Clapeyron), negative
ATM = 101325.0
MASS = 75.0
SKI_L, SKI_W = 1.6, 0.07
AREA = 2 * SKI_L * SKI_W
P_SKIER = MASS * G / AREA
DT_SKIER = P_SKIER * DTDP
P_10 = -10 / DTDP
AREA_10 = MASS * G / P_10
MU, V = 0.03, 15.0
POWER = MU * MASS * G * V
J_PER_M = MU * MASS * G
G_PER_M = J_PER_M / L_F * 1e3
FILM_UM = J_PER_M / L_F / RHO_I / (2 * SKI_W) * 1e6
MU_WARM, MU_COLD = 0.0145, 0.033                      # arXiv:2212.08524, 0 C and -11 C
P_WARM, P_COLD = MU_WARM * MASS * G * V, MU_COLD * MASS * G * V


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


# ------------------------------------------------------------------ top view of the two skis
def skis_top(c, cx, cy, k, alpha=1.0, glow=0.0):
    for dy in (-0.13, 0.13):
        x0, y0 = cx - SKI_L / 2 * k, cy + dy * k - SKI_W / 2 * k
        rounded_rect(c, x0, y0, SKI_L * k, SKI_W * k, SKI_W * k * 0.45)
        c.set_source_rgba(*mix((0.16, 0.17, 0.21), GOLD, 0.25 + 0.5 * glow), alpha); c.fill_preserve()
        c.set_source_rgba(*GOLD, 0.8 * alpha); c.set_line_width(2); c.stroke()


def dim_line(c, x0, y0, x1, y1, label, alpha, size=24, off=(0, -14), col=DIM):
    if alpha <= 0:
        return
    c.set_source_rgba(*col, 0.8 * alpha); c.set_line_width(1.4)
    c.move_to(x0, y0); c.line_to(x1, y1); c.stroke()
    ang = math.atan2(y1 - y0, x1 - x0)
    for (x, y) in ((x0, y0), (x1, y1)):
        c.move_to(x - 8 * math.sin(ang), y + 8 * math.cos(ang)); c.line_to(x + 8 * math.sin(ang), y - 8 * math.cos(ang)); c.stroke()
    text(c, label, (x0 + x1) / 2 + off[0], (y0 + y1) / 2 + off[1], size, col, alpha, align="c")


# ------------------------------------------------------------------ number line with zoom inset
def melt_line(c, dt, alpha, x0=180, x1=1740, y=420, zoom=0.0):
    """0 .. -10 C number line; marker at dt (C). zoom 0..1 reveals a x10000 inset."""
    if alpha <= 0:
        return
    X = lambda v: x1 + (v / 10.0) * (x1 - x0)          # v in C (negative)
    c.set_source_rgba(*FAINT, alpha); c.set_line_width(2); c.move_to(x0, y); c.line_to(x1, y); c.stroke()
    for v in range(0, -11, -1):
        c.move_to(X(v), y - 10); c.line_to(X(v), y + 10); c.stroke()
        text(c, f"{v} °C", X(v), y + 44, 22, DIM, alpha, align="c")
    c.arc(X(dt), y, 9, 0, 2 * math.pi); c.set_source_rgba(*RED, alpha); c.fill()
    text(c, "冰的熔点", X(0), y - 30, 24, INK, alpha, align="c", bold=True)
    if zoom > 0:
        a = alpha * zoom
        ix0, ix1, iy = 760, 1640, y + 190
        c.set_source_rgba(*FAINT, 0.6 * a); c.set_line_width(1.2)
        c.move_to(X(0) - 6, y + 14); c.line_to(ix1, iy - 40); c.move_to(X(0) - 6, y + 14); c.line_to(ix0, iy - 40); c.stroke()
        rounded_rect(c, ix0 - 30, iy - 60, ix1 - ix0 + 60, 150, 10)
        c.set_source_rgba(0.03, 0.04, 0.05, 0.9 * a); c.fill_preserve()
        c.set_source_rgba(*FAINT, a); c.stroke()
        XI = lambda v: ix1 + (v / 0.001) * (ix1 - ix0)
        c.set_source_rgba(*DIM, a); c.set_line_width(2); c.move_to(ix0, iy); c.line_to(ix1, iy); c.stroke()
        for i in range(0, 11):
            v = -i * 0.0001
            hh = 12 if i % 5 == 0 else 6
            c.move_to(XI(v), iy - hh); c.line_to(XI(v), iy + hh); c.stroke()
        for v in (0, -0.0005, -0.001):
            text(c, f"{v:.4f} °C" if v else "0 °C", XI(v), iy + 46, 20, DIM, a, align="c")
        c.arc(XI(dt), iy, 9, 0, 2 * math.pi); c.set_source_rgba(*RED, a); c.fill()
        text(c, f"{dt:.5f} °C", XI(dt), iy - 22, 24, RED, a, align="c", bold=True)
        text(c, "放大 1 万倍", ix0 - 10, iy - 74, 20, DIM, a)


# ------------------------------------------------------------------ micro-scale snow under the base
class Grains:
    """deterministic packed snow grains under a flat base at y=0 (local px). units: px."""
    def __init__(self, width=2600, depth=300, seed=11):
        rng = np.random.default_rng(seed)
        pts = []
        tries = 0
        while len(pts) < 260 and tries < 20000:
            tries += 1
            r = 22 + rng.random() * 34
            x = rng.random() * width
            y = r * 0.6 + rng.random() * depth
            if y - r < -4:
                continue
            if all((x - a) ** 2 + (y - b) ** 2 > (r + rr - 6) ** 2 for a, b, rr in pts):
                pts.append((x, y, r))
        # lift the top layer so a few grains touch the base (top at y=0)
        self.g = []
        for x, y, r in pts:
            top = y - r
            if top < 26:
                y -= top            # touching
            self.g.append((x, y, r))
        self.width = width

    def draw(self, c, ox, oy, shift, heat=0.0, film=0.0, abrade=0.0, t=0.0, alpha=1.0, base=True, x0=0, x1=W):
        """shift: base slides right relative to snow -> we scroll grains left by shift (px)."""
        c.save(); c.rectangle(x0, oy - 200, x1 - x0, 700); c.clip()
        for (gx, gy, r) in self.g:
            X = ox + ((gx - shift) % self.width) - 200
            if X < x0 - 80 or X > x1 + 80:
                continue
            Y = oy + gy
            touch = gy - r < 1
            fade = clamp(1 - (gy - 80) / 320, 0.15, 1)
            c.arc(X, Y, r, 0, 2 * math.pi)
            gr = cairo.RadialGradient(X - r * 0.35, Y - r * 0.35, r * 0.1, X, Y, r)
            gr.add_color_stop_rgba(0, 0.88, 0.92, 0.98, 0.95 * alpha * fade); gr.add_color_stop_rgba(1, 0.45, 0.55, 0.70, 0.85 * alpha * fade)
            c.set_source(gr); c.fill()
            if touch and heat > 0:
                hg = cairo.RadialGradient(X, oy, 0, X, oy, r * 1.3)
                hg.add_color_stop_rgba(0, *WARM, 1.0 * heat * alpha); hg.add_color_stop_rgba(0.5, *WARM, 0.45 * heat * alpha); hg.add_color_stop_rgba(1, *WARM, 0)
                c.set_source(hg); c.arc(X, oy, r * 1.3, 0, 2 * math.pi); c.fill()
            if touch and film > 0:
                c.save(); c.translate(X, oy + 3); c.scale(1, 0.22)
                c.arc(0, 0, r * 1.05, 0, 2 * math.pi); c.restore()
                c.set_source_rgba(0.55, 0.85, 1.0, 1.0 * film * alpha); c.fill()
            if touch and abrade > 0:
                rng = np.random.default_rng(int(gx))
                for i in range(7):
                    ph = (t * 1.3 + rng.random()) % 1.0
                    px = X - 10 - ph * (40 + 50 * rng.random())
                    py = oy + 4 + ph * (30 + 60 * rng.random())
                    c.arc(px, py, 2.4 + 2 * rng.random(), 0, 2 * math.pi)
                    c.set_source_rgba(0.92, 0.95, 1.0, 0.85 * abrade * (1 - ph) * alpha); c.fill()
        if base:
            c.rectangle(x0, oy - 120, x1 - x0, 120)
            g = cairo.LinearGradient(0, oy - 120, 0, oy)
            g.add_color_stop_rgba(0, 0.10, 0.11, 0.14, alpha); g.add_color_stop_rgba(1, 0.20, 0.21, 0.26, alpha)
            c.set_source(g); c.fill()
            c.set_source_rgba(*GOLD, 0.7 * alpha); c.rectangle(x0, oy - 3, x1 - x0, 3); c.fill()
            # base structure marks that slide right
            for k in range(-2, 40):
                xx = x0 + ((k * 90 + shift) % ((x1 - x0) + 180)) - 90
                c.set_source_rgba(1, 1, 1, 0.06 * alpha); c.rectangle(xx, oy - 100, 26, 90); c.fill()
        c.restore()


# ------------------------------------------------------------------ ice surface molecules (schematic)
def molecules(c, x0, y0, w, h, t, mobility, alpha=1.0, seed=5):
    """hexagonal-ish lattice; the top layer jiggles and rolls with `mobility` 0..1."""
    if alpha <= 0:
        return
    rng = np.random.default_rng(seed)
    dx, dy = 34, 30
    rows = int(h / dy); cols = int(w / dx)
    for j in range(rows):
        for i in range(cols):
            x = x0 + i * dx + (dx / 2 if j % 2 else 0)
            y = y0 + h - j * dy
            top = j >= rows - 2
            if top:
                ph = rng.random() * 6.28
                amp = mobility * (10 if j == rows - 1 else 4)
                x += amp * math.sin(t * 3.1 + ph) + (mobility * 25 * t * (1 if j == rows - 1 else 0)) % dx * 0
                y += amp * 0.7 * math.cos(t * 2.7 + ph)
                if j == rows - 1:
                    x = x0 + ((x - x0 + mobility * 30 * t) % (w + dx / 2))
            col = ICE if top else (0.55, 0.65, 0.80)
            c.arc(x, y, 9 if top else 8, 0, 2 * math.pi); c.set_source_rgba(*col, (0.95 if top else 0.6) * alpha); c.fill()
            if not top and i < cols - 1:
                c.set_source_rgba(0.55, 0.65, 0.80, 0.25 * alpha); c.set_line_width(2)
                c.move_to(x, y); c.line_to(x + dx, y); c.stroke()
