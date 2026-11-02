"""Snow surface, tracks, board drawing (top view + 3D), spray."""
import math
import numpy as np
import cairo
from PIL import Image, ImageFilter
from common import *
import ski

_SNOW = {}


def _periodic_noise(h, w, rng, scale):
    """smooth noise, periodic in both axes (FFT-filtered white noise)."""
    f = np.fft.rfft2(rng.normal(0, 1, (h, w)))
    ky = np.fft.fftfreq(h)[:, None]; kx = np.fft.rfftfreq(w)[None, :]
    f *= np.exp(-((kx ** 2 + ky ** 2) * (scale ** 2)))
    n = np.fft.irfft2(f, (h, w)).astype(np.float32)
    return n / (n.std() + 1e-9)


def snow_texture(w=W, h=1400, seed=5):
    """tileable corduroy snow, blue hour with warm low light from the upper left."""
    key = (w, h, seed)
    if key in _SNOW:
        return _SNOW[key]
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    n = 0.5 * _periodic_noise(h, w, rng, 60) + 0.3 * _periodic_noise(h, w, rng, 20) + 0.2 * _periodic_noise(h, w, rng, 6)
    cord = 0.5 + 0.5 * np.sin(xx * 2 * math.pi / 9.0)          # groomer corduroy (fall line = vertical)
    band = 0.5 + 0.5 * np.sin(xx * 2 * math.pi / 240.0)
    lum = 0.86 + 0.035 * n + 0.025 * cord + 0.02 * band
    lit = np.clip(1.15 - (xx / w) * 0.9, 0, 1)[..., None]
    cool = np.array([0.50, 0.58, 0.74], np.float32)
    warm = np.array([0.93, 0.88, 0.82], np.float32)
    rgb = (cool * (1 - lit) + warm * lit) * lum[..., None]
    sp = rng.random((h, w)) > 0.9988                           # sparkle
    rgb[sp] = np.minimum(1, rgb[sp] + 0.25)
    rgba = np.dstack([np.clip(rgb * 255, 0, 255).astype(np.uint8), np.full((h, w), 255, np.uint8)])
    s = np_to_surface(rgba)
    _SNOW[key] = s
    return s


def paint_snow(c, oy=0.0, alpha=1.0, x0=0, y0=0, w=W, h=H):
    tex = snow_texture()
    th = tex.get_height()
    c.save()
    c.rectangle(x0, y0, w, h); c.clip()
    off = -round(oy % th)
    for k in range(3):
        c.set_source_surface(tex, x0, y0 + off + k * th)
        c.paint_with_alpha(alpha)
    c.restore()


def carve_line(c, P, alpha=1.0, w=2.6):
    """thin carved groove: shadow side + lit lip. P: Nx2 screen."""
    if len(P) < 2:
        return
    for dx, dy, col, a, lw in ((1.2, 1.2, (0.06, 0.08, 0.14), 0.75, w + 1.4), (-0.8, -0.8, (1.0, 0.94, 0.84), 0.85, w * 0.55)):
        c.move_to(P[0, 0] + dx, P[0, 1] + dy)
        for p in P[1:]:
            c.line_to(p[0] + dx, p[1] + dy)
        c.set_source_rgba(*col, a * alpha); c.set_line_width(lw); c.stroke()


def skid_band(c, P, widths, alpha=1.0):
    """wide scraped band: polygon from centreline P and local widths (px)."""
    if len(P) < 3:
        return
    d = np.gradient(P, axis=0)
    nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
    L = P + nrm * widths[:, None] / 2
    R = P - nrm * widths[:, None] / 2
    poly = np.concatenate([L, R[::-1]])
    c.move_to(*poly[0])
    for p in poly[1:]:
        c.line_to(*p)
    c.close_path()
    c.set_source_rgba(0.30, 0.36, 0.50, 0.38 * alpha); c.fill_preserve()
    c.set_source_rgba(0.95, 0.92, 0.88, 0.18 * alpha); c.set_line_width(1.2); c.stroke()
    # scrape streaks
    c.set_line_width(1.0)
    for k in np.linspace(-0.4, 0.4, 7):
        Q = P + nrm * widths[:, None] * k
        c.move_to(*Q[0])
        for q in Q[1::3]:
            c.line_to(*q)
        c.set_source_rgba(0.9, 0.9, 0.92, 0.10 * alpha); c.stroke()


def board_top(c, x, y, heading, scale, alpha=1.0, rider=True, ex=1.0):
    """snowboard seen from above at screen (x,y), heading rad (screen), scale px/m."""
    P = ski.board_outline(ex=ex)
    ch, sh = math.cos(heading), math.sin(heading)
    Q = np.stack([x + scale * (P[:, 0] * ch - P[:, 1] * sh), y + scale * (P[:, 0] * sh + P[:, 1] * ch)], 1)
    # shadow toward lower right (sun upper left)
    c.save(); c.translate(min(14, scale * 0.18), min(10, scale * 0.12))
    _poly(c, Q); c.set_source_rgba(0.03, 0.04, 0.08, 0.35 * alpha); c.fill()
    c.restore()
    _poly(c, Q)
    g = cairo.LinearGradient(x - scale * 0.8 * ch, y - scale * 0.8 * sh, x + scale * 0.8 * ch, y + scale * 0.8 * sh)
    g.add_color_stop_rgba(0, 0.10, 0.11, 0.14, alpha)
    g.add_color_stop_rgba(0.5, 0.16, 0.17, 0.21, alpha)
    g.add_color_stop_rgba(1, 0.10, 0.11, 0.14, alpha)
    c.set_source(g); c.fill_preserve()
    c.set_source_rgba(*GOLD, 0.65 * alpha); c.set_line_width(max(1.0, scale * 0.006)); c.stroke()
    if rider:
        for b in (-0.27, 0.27):   # bindings
            bx, by = x + scale * b * ch, y + scale * b * sh
            c.save(); c.translate(bx, by); c.rotate(heading + math.pi / 2 + (0.25 if b > 0 else -0.1))
            rounded_rect(c, -scale * 0.11, -scale * 0.05, scale * 0.22, scale * 0.10, scale * 0.03)
            c.set_source_rgba(0.04, 0.04, 0.05, 0.95 * alpha); c.fill(); c.restore()
        # rider seen from above: shoulders + head, offset slightly toward the turn
        c.save(); c.translate(x, y); c.rotate(heading)
        c.scale(1, 0.55)
        c.arc(0, 0, scale * 0.24, 0, 2 * math.pi)
        c.set_source_rgba(0.08, 0.09, 0.12, 0.9 * alpha); c.fill()
        c.restore()
        c.arc(x, y, scale * 0.11, 0, 2 * math.pi)
        c.set_source_rgba(0.75, 0.55, 0.30, alpha); c.fill()


def _poly(c, Q):
    c.move_to(*Q[0])
    for q in Q[1:]:
        c.line_to(*q)
    c.close_path()


def spray(c, x, y, heading, strength, t, scale, seed=0, alpha=1.0):
    """deterministic snow spray thrown outward from a skidding board."""
    if strength <= 0.01:
        return
    rng = np.random.default_rng(seed + int(t * 30))
    n = int(60 * strength)
    out = heading - math.pi / 2
    for i in range(n):
        age = rng.random()
        a = out + rng.normal(0, 0.45)
        dist = (0.3 + 1.6 * age) * scale * (0.6 + 0.6 * rng.random())
        px = x + math.cos(a) * dist + rng.normal(0, 4)
        py = y + math.sin(a) * dist + rng.normal(0, 4)
        r = (1.2 + 2.6 * rng.random()) * (1 - 0.5 * age)
        c.arc(px, py, r, 0, 2 * math.pi)
        c.set_source_rgba(0.97, 0.96, 0.95, 0.75 * (1 - age) * strength * alpha); c.fill()


# ---------------------------------------------------------------- 3D projection (orthographic)
def camera(az, el):
    a, e = math.radians(az), math.radians(el)
    v = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    r = np.cross(np.array([0, 0, 1.0]), v); r /= np.linalg.norm(r)
    u = np.cross(v, r)
    return v, r, u


def proj(P, cam, org, s):
    v, r, u = cam
    return org[0] + s * (P @ r), org[1] - s * (P @ u)
