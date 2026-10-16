"""Poster-style covers (v2): brushed dusk gradient, big left-aligned serif title, one restrained motif.
python3 covers2.py EPDIR OUT_PREFIX     (EPDIR/scenes.py defines COVER2, see below)
COVER2 = dict(kicker="单板 · 用数据说话", lines=[("往后摔", "ink"), ("还是往前摔", "gold")],
              sub="38 例严重颅脑损伤 · 68% 是后摔", motif="track" | "arcs" | "pipe" | "spin" | "jump" | "board", seed=7)"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.abspath(sys.argv[1]); sys.path.insert(0, HERE); sys.path.insert(0, EP)
import numpy as np
import cairo
from PIL import Image, ImageFilter
from common import font, text_w, SERIF, SANS
import scenes

SIZES = {"竖版9x16": (1080, 1920), "竖版3x4": (1080, 1440), "横版16x9": (1920, 1080), "横版4x3": (1440, 1080)}
INKC = (0.95, 0.93, 0.88)
GOLDC = (0.86, 0.66, 0.38)
ICEC = (0.55, 0.78, 0.98)
REDC = (0.85, 0.36, 0.32)
BOLD_TITLE = False
COLMAP = {"ink": INKC, "gold": GOLDC, "ice": ICEC, "red": REDC}


def background(w, h, seed):
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, h)[:, None]; x = np.linspace(0, 1, w)[None, :]
    top = np.array([0.075, 0.075, 0.08]); bot = np.array([0.42, 0.44, 0.50])
    warm = np.array([0.50, 0.45, 0.40])
    g = (y ** 1.3)[..., None]
    base = top * (1 - g) + (bot * (0.55 + 0.45 * x[..., None]) + warm * (0.45 - 0.45 * x[..., None])) * g
    # brushed vertical streaks
    n = rng.normal(0, 1, (h // 4 + 1, w))
    n = np.asarray(Image.fromarray(((n - n.min()) / (np.ptp(n)) * 255).astype(np.uint8)).resize((w, h)).filter(ImageFilter.GaussianBlur(1.2)), float) / 255 - 0.5
    streak = np.asarray(Image.fromarray(((n + 0.5) * 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(0)).resize((w, h)), float) / 255 - 0.5
    cloud = rng.normal(0, 1, (12, 20))
    cloud = np.asarray(Image.fromarray(((cloud - cloud.min()) / np.ptp(cloud) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), float) / 255 - 0.5
    img = base * (1 + 0.20 * streak[..., None] + 0.18 * cloud[..., None] * (0.3 + g))
    # vignette
    vx = (x - 0.5) * 2; vy = (y - 0.5) * 2
    img *= (1 - 0.25 * (vx ** 2 + vy ** 2) ** 1.2)[..., None]
    return np.clip(img, 0, 1)


def to_surface(img):
    h, w, _ = img.shape
    a = (img * 255).astype(np.uint8)
    buf = np.dstack([a[..., 2], a[..., 1], a[..., 0], np.full((h, w), 255, np.uint8)]).copy()
    s = cairo.ImageSurface.create_for_data(memoryview(buf), cairo.FORMAT_ARGB32, w, h)
    return s, buf


_KEEP = []


def soft_layer(w, h, draw, blur):
    """draw on a transparent layer, blur it, return a cairo surface."""
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s)
    draw(c)
    s.flush()
    a = np.ndarray((h, w, 4), np.uint8, s.get_data()).copy()
    im = Image.fromarray(a, "RGBA").filter(ImageFilter.GaussianBlur(blur))
    b = np.asarray(im).copy()
    out = cairo.ImageSurface.create_for_data(memoryview(b), cairo.FORMAT_ARGB32, w, h)
    _KEEP.append(b)
    return out


def path_pts(kind, w, h, rng, portrait):
    if portrait:
        x0, x1, y0, y1 = 0.42 * w, 0.62 * w, 0.42 * h, 0.86 * h
    else:
        x0, x1, y0, y1 = 0.50 * w, 0.92 * w, 0.0, 1.0 * h
    t = np.linspace(0, 1, 400)
    amp = (x1 - x0) * 0.6
    ph = rng.uniform(0, 1)
    xs = (x0 + x1) / 2 + amp * np.sin(2 * math.pi * (1.6 * t + ph)) * (0.6 + 0.4 * t)
    ys = y0 + (y1 - y0) * t
    return np.stack([xs, ys], 1)


def ribbon(c, pts, width, col, alpha):
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    for k, (wf, af) in enumerate(((1.0, 0.35), (0.7, 0.35), (0.4, 0.4))):
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        c.set_source_rgba(*col, alpha * af); c.set_line_width(width * wf); c.stroke()


def motif(c, kind, w, h, portrait, seed):
    rng = np.random.default_rng(seed)
    S = min(w, h)
    if kind in ("track", "board"):
        pts = path_pts(kind, w, h, rng, portrait)
        lay = soft_layer(w, h, lambda d: ribbon(d, pts, S * 0.09, (0.20, 0.26, 0.40), 0.9), 3)
        c.set_source_surface(lay); c.paint_with_alpha(0.85)
        ex, ey = pts[-1]
        ang = math.atan2(*(pts[-1] - pts[-6])[::-1])
        c.save(); c.translate(ex, ey); c.rotate(ang)
        L = S * 0.10
        c.new_path(); c.move_to(-L / 2, 0); c.line_to(L / 2, 0)
        c.set_source_rgba(0.08, 0.09, 0.12, 0.95); c.set_line_width(S * 0.022); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
        c.arc(0, 0, S * 0.008, 0, 2 * math.pi); c.set_source_rgba(*GOLDC, 1); c.fill()
        c.restore()
        for r, a in ((S * 0.065, 0.9), (S * 0.125, 0.35)):
            c.new_path(); c.arc(ex, ey, r, 0, 2 * math.pi); c.set_source_rgba(*REDC, a); c.set_line_width(2.5); c.stroke()
    elif kind == "arcs":
        cx, cy = (0.30 * w, 1.05 * h) if portrait else (0.62 * w, 1.10 * h)
        for i, (rf, col) in enumerate(((1.0, ICEC), (0.82, GOLDC), (0.48, REDC))):
            r = S * 0.62 * rf
            c.new_path(); c.arc(cx, cy, r, -math.pi * 0.95, -math.pi * 0.05)
            c.set_source_rgba(*col, 0.85); c.set_line_width(2.2); c.stroke()
            c.new_path(); c.arc(cx, cy, r + 5, -math.pi * 0.95, -math.pi * 0.05)
            c.set_source_rgba(0.05, 0.06, 0.08, 0.5); c.set_line_width(1.2); c.stroke()
    elif kind == "pipe":
        cx = 0.5 * w if portrait else 0.72 * w; base = 0.96 * h; R = S * (0.40 if portrait else 0.30); flat = S * 0.22
        lay = soft_layer(w, h, lambda d: _pipe(d, cx, base, R, flat), 2)
        c.set_source_surface(lay); c.paint()
        xr = cx + flat / 2 + R; top = base - R
        c.set_dash([8, 8]); c.set_source_rgba(*REDC, 0.9); c.set_line_width(2.5)
        c.move_to(xr, top); c.line_to(xr, top - R * (1.15 if not portrait else 0.9)); c.stroke(); c.set_dash([])
        c.arc(xr, top - R * (1.15 if not portrait else 0.9), S * 0.012, 0, 2 * math.pi); c.set_source_rgba(*GOLDC, 1); c.fill()
    elif kind == "spin":
        cx, cy = (0.5 * w, 0.66 * h) if portrait else (0.72 * w, 0.52 * h)
        for i in range(7):
            r = S * (0.10 + 0.035 * i)
            a0 = -math.pi / 2 + i * 0.5
            c.new_path(); c.arc(cx, cy, r, a0, a0 + math.pi * (1.2 + 0.1 * i))
            c.set_source_rgba(*(GOLDC if i < 6 else REDC), 0.25 + 0.1 * i); c.set_line_width(2.2); c.stroke()
        c.save(); c.translate(cx, cy); c.rotate(-0.5)
        c.new_path(); c.move_to(-S * 0.07, 0); c.line_to(S * 0.07, 0)
        c.set_source_rgba(0.08, 0.09, 0.12, 0.95); c.set_line_width(S * 0.022); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
        c.restore()
    elif kind == "jump":
        x0 = 0.30 * w if portrait else 0.62 * w; gy = 0.80 * h
        k = S * 0.0065
        prof = [(x0 - 60 * k, gy - 30 * k), (x0, gy - 2 * k), (x0 + 6 * k, gy - 6 * k), (x0 + 6 * k, gy), (x0 + 30 * k, gy),
                (x0 + 80 * k, gy + 34 * k), (w + 10, gy + 34 * k)]
        def dr(d):
            d.move_to(*prof[0])
            for p in prof[1:]:
                d.line_to(*p)
            d.line_to(w + 10, h + 10); d.line_to(prof[0][0], h + 10); d.close_path()
            d.set_source_rgba(0.12, 0.14, 0.19, 0.9); d.fill()
        lay = soft_layer(w, h, dr, 2); c.set_source_surface(lay); c.paint()
        c.set_dash([8, 8]); c.set_source_rgba(*GOLDC, 0.9); c.set_line_width(2.5)
        c.move_to(x0 + 6 * k, gy - 6 * k)
        c.curve_to(x0 + 20 * k, gy - 30 * k, x0 + 40 * k, gy - 30 * k, x0 + 52 * k, gy + 12 * k); c.stroke(); c.set_dash([])


def _pipe(d, cx, base, R, flat):
    d.move_to(cx - flat / 2 - R - 40, base - R)
    d.arc_negative(cx - flat / 2, base - R, R, math.pi, math.pi / 2)
    d.line_to(cx + flat / 2, base)
    d.arc_negative(cx + flat / 2, base - R, R, math.pi / 2, 0)
    d.line_to(cx + flat / 2 + R + 40, base - R)
    d.line_to(cx + flat / 2 + R + 40, base + 400); d.line_to(cx - flat / 2 - R - 40, base + 400); d.close_path()
    d.set_source_rgba(0.12, 0.14, 0.19, 0.92); d.fill()


def title_text(c, s, x, y, size, col, spacing=0.0):
    font(c, size, BOLD_TITLE, SERIF)
    if spacing:
        for ch in s:
            _shadow_text(c, ch, x, y, size, col); x += text_w(c, ch) + size * spacing
    else:
        _shadow_text(c, s, x, y, size, col)


def _shadow_text(c, s, x, y, size, col):
    c.move_to(x + size * 0.02, y + size * 0.03); c.set_source_rgba(0, 0, 0, 0.55); c.show_text(s)
    c.move_to(x, y); c.set_source_rgba(*col, 1); c.show_text(s)


def cover(w, h, path, C):
    portrait = h > w
    img = background(w, h, C.get("seed", 3))
    s, buf = to_surface(img); c = cairo.Context(s)
    motif(c, C.get("motif", "track"), w, h, portrait, C.get("seed", 3))
    lines = C["lines"]
    n = max(len(t) for t, _ in lines)
    if portrait:
        x = 0.095 * w
        big = min(w * 0.82 / max(n, 2), w * 0.20)
        y = 0.17 * h if h / w > 1.5 else 0.14 * h
    else:
        x = 0.05 * w
        big = min(0.40 * w / max(n, 2), h * 0.15)
        y = 0.30 * h
    font(c, big * 0.25, False, SERIF)
    title_text(c, C["kicker"], x, y, big * 0.28, (0.82, 0.82, 0.82), spacing=0.55)
    yy = y + big * 1.25
    for t, col in lines:
        title_text(c, t, x, yy, big, COLMAP.get(col, INKC))
        yy += big * 1.18
    font(c, big * 0.22, False, SANS)
    yy += big * 0.05
    _shadow_text(c, C["sub"], x, yy, big * 0.22, (0.92, 0.92, 0.92))
    s.flush()
    out = np.ndarray((h, w, 4), np.uint8, s.get_data())[..., [2, 1, 0]].copy()
    Image.fromarray(out).save(path, quality=93)


if __name__ == "__main__":
    pre = sys.argv[2]
    for name, (w, h) in SIZES.items():
        cover(w, h, f"{pre}-{name}.jpg", scenes.COVER2); print(f"{pre}-{name}.jpg")
