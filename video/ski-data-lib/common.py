"""Shared canvas, typography, overlays and encoder for the film."""
import math, subprocess
import numpy as np
import cairo

W, H, FPS = 1920, 1080, 30
SERIF = "Noto Serif SC"
SANS = "Noto Sans SC"

BG = (0.027, 0.035, 0.047)
INK = (0.90, 0.91, 0.92)
DIM = (0.55, 0.58, 0.62)
FAINT = (0.30, 0.33, 0.37)
BLUE = (0.30, 0.55, 0.95)
BLUE_HI = (0.45, 0.72, 1.0)
BROWN = (0.62, 0.42, 0.24)
GREEN = (0.45, 0.85, 0.55)
RED = (0.92, 0.42, 0.36)
ICE = (0.62, 0.84, 1.0)
GOLD = (1.0, 0.80, 0.46)
SNOW_LIT = (0.80, 0.84, 0.90)
SNOW_SH = (0.30, 0.36, 0.48)


# ------------------------------------------------------------------ easing / timing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_io(x):
    x = clamp(x)
    return 0.5 - 0.5 * math.cos(math.pi * x)


def ramp(t, t0, t1):
    return ease((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t0)


def window(t, a, b, fade=0.5):
    """1 inside [a,b] with fades."""
    return min(ramp(t, a, a + fade), 1 - ramp(t, b - fade, b))


def lerp(a, b, x):
    return a + (b - a) * x


def mix(c1, c2, x):
    return tuple(lerp(a, b, x) for a, b in zip(c1, c2))


# ------------------------------------------------------------------ surfaces
def new_surface():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    return s, cairo.Context(s)


def np_to_surface(arr_rgba):
    """uint8 HxWx4 RGBA -> cairo surface (premultiplied BGRA)."""
    a = arr_rgba.astype(np.float32)
    al = a[..., 3:4] / 255.0
    bgra = np.empty_like(arr_rgba)
    bgra[..., 0] = (a[..., 2] * al[..., 0]).astype(np.uint8)
    bgra[..., 1] = (a[..., 1] * al[..., 0]).astype(np.uint8)
    bgra[..., 2] = (a[..., 0] * al[..., 0]).astype(np.uint8)
    bgra[..., 3] = arr_rgba[..., 3]
    h, w = arr_rgba.shape[:2]
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    buf = np.ndarray((h, s.get_stride() // 4, 4), np.uint8, s.get_data())
    buf[:, :w] = bgra
    s.mark_dirty()
    return s


def paint_bg(c, col=BG):
    c.set_source_rgb(*col)
    c.paint()


def fade_black(c, a):
    if a > 0:
        c.set_source_rgba(0, 0, 0, clamp(a))
        c.paint()


# ------------------------------------------------------------------ text
def font(c, size, bold=False, face=SERIF, italic=False):
    c.select_font_face(face, cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    m = cairo.Matrix(size, 0, -0.22 * size if italic else 0, size, 0, 0)
    c.set_font_matrix(m)


def text_w(c, s):
    return c.text_extents(s).x_advance


def text(c, s, x, y, size, col=INK, alpha=1.0, bold=False, align="l", face=SERIF, italic=False, spacing=0.0):
    if alpha <= 0.003 or not s:
        return
    font(c, size, bold, face, italic)
    w = text_w(c, s) + spacing * size * (len(s) - 1)
    if align == "c":
        x -= w / 2
    elif align == "r":
        x -= w
    c.set_source_rgba(*col, alpha)
    if spacing == 0:
        c.move_to(x, y)
        c.show_text(s)
    else:
        for ch in s:
            c.move_to(x, y)
            c.show_text(ch)
            x += text_w(c, ch) + spacing * size


def rich(c, spans, cx, y, size, alpha=1.0, bold=True, shadow=True):
    """spans: list of (str, colour). Centered line."""
    font(c, size, bold)
    widths = [text_w(c, s) for s, _ in spans]
    x = cx - sum(widths) / 2
    if shadow:
        for dx, dy, a in ((0, 3, 0.55), (0, 1, 0.5)):
            xx = x
            for (s, _), w in zip(spans, widths):
                c.set_source_rgba(0, 0, 0, a * alpha)
                c.move_to(xx + dx, y + dy)
                c.show_text(s)
                xx += w
    for (s, col), w in zip(spans, widths):
        c.set_source_rgba(*col, alpha)
        c.move_to(x, y)
        c.show_text(s)
        x += w


def parse_markup(s):
    """'普通{蓝|高亮}普通' -> spans. Tag letter picks colour: 蓝 b, 褐 w, 绿 g, 红 r."""
    cols = {"b": ICE, "w": GOLD, "g": (0.45, 0.85, 0.55), "r": RED}
    spans, i = [], 0
    while i < len(s):
        j = s.find("{", i)
        if j < 0:
            spans.append((s[i:], INK)); break
        if j > i:
            spans.append((s[i:j], INK))
        k = s.find("}", j)
        tag, body = s[j + 1], s[j + 3:k]
        spans.append((body, cols[tag]))
        i = k + 1
    return spans


# ------------------------------------------------------------------ overlays
def wrap_sub(s, maxc=30):
    """break a long subtitle at the punctuation nearest its middle (never inside a {x|...} span)."""
    if "\n" in s:
        return s
    vis, depth, cand, n = [], 0, [], 0
    i = 0
    while i < len(s):
        if s[i] == "{" and i + 2 < len(s) and s[i + 2] == "|":
            depth += 1; i += 3; continue
        if s[i] == "}" and depth:
            depth -= 1; i += 1; continue
        n += 1
        if not depth and s[i] in "，；：——、。？":
            cand.append((n, i))
        i += 1
    if n <= maxc or not cand:
        return s
    pos, idx = min(cand, key=lambda q: abs(q[0] - n / 2))
    while idx + 1 < len(s) and s[idx + 1] == "—":
        idx += 1
    return s[:idx + 1] + "\n" + s[idx + 1:]


def subtitle(c, s, t, t0, t1, y=H - 118, size=46):
    a = window(t, t0, t1, 0.35)
    if a <= 0:
        return
    s = wrap_sub(s)
    lines = s.split("\n")
    # soft band behind text for legibility on bright frames
    g = cairo.LinearGradient(0, y - 120 - 60 * (len(lines) - 1), 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(0.6, 0, 0, 0, 0.35 * a)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.5 * a)
    c.rectangle(0, y - 120 - 60 * (len(lines) - 1), W, H)
    c.set_source(g)
    c.fill()
    for i, ln in enumerate(lines):
        yy = y - (len(lines) - 1 - i) * (size * 1.45)
        rich(c, parse_markup(ln), W / 2, yy, size, a)


def _backing(c, x0, y0, x1, y1, a):
    """feathered dark corner glow behind corner labels (no hard edges)."""
    cx = x0 if x0 == 0 else x1
    c.save()
    c.translate(cx, 0)
    c.scale(1.0, 0.45)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, (x1 - x0) * 1.15)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.62 * a)
    g.add_color_stop_rgba(0.55, 0, 0, 0, 0.38 * a)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.0)
    c.set_source(g)
    c.paint()
    c.restore()


def chapter_tag(c, big, small, alpha=1.0, x=72, y=118, bar=None):
    """big label + rule; if bar given, a bright segment of that many px = true scale bar."""
    if alpha <= 0:
        return
    _backing(c, 0, 0, 560, 240, alpha)
    text(c, big, x, y, 64, (0.80, 0.84, 0.90), alpha, bold=True)
    c.set_source_rgba(*FAINT, 0.9 * alpha)
    c.rectangle(x, y + 26, 320, 1.2)
    c.fill()
    if bar:
        c.set_source_rgba(0.85, 0.90, 0.98, alpha)
        c.rectangle(x, y + 24, bar, 4)
        c.fill()
    font(c, 24)
    sw = text_w(c, small)
    c.set_source_rgba(0.02, 0.025, 0.035, 0.55 * alpha)
    rounded_rect(c, x - 10, y + 38, sw + 20, 34, 6); c.fill()
    text(c, small, x, y + 62, 24, (0.80, 0.83, 0.88), alpha)


def cite_card(c, latin, zh, who, alpha=1.0, x=W - 72, y=96):
    if alpha <= 0:
        return
    _backing(c, W - 700, 0, W, 240, alpha)
    text(c, latin, x - 64, y, 26, (0.78, 0.80, 0.84), alpha, align="r", italic=True)
    text(c, zh, x - 64, y + 44, 28, GOLD, alpha, align="r", bold=True)
    text(c, who, x - 64, y + 82, 21, DIM, alpha, align="r")
    c.set_source_rgba(*FAINT, 0.9 * alpha)
    c.rectangle(x - 520, y + 100, 456, 1.2)
    c.fill()
    # small seal
    c.set_source_rgba(0.62, 0.46, 0.20, 0.9 * alpha)
    c.rectangle(x - 46, y - 30, 46, 46)
    c.fill()
    text(c, "文", x - 23, y - 9, 18, (0.92, 0.94, 1.0), alpha, align="c", bold=True)
    text(c, "献", x - 23, y + 11, 18, (0.92, 0.94, 1.0), alpha, align="c", bold=True)


def model_note(c, alpha=1.0, s="示意 · 简化模型计算"):
    font(c, 20)
    c.set_source_rgba(0.02, 0.025, 0.035, 0.5 * alpha)
    rounded_rect(c, 62, H - 62, text_w(c, s) + 20, 32, 6); c.fill()
    text(c, s, 72, H - 40, 20, (0.62, 0.66, 0.72), alpha)


def pill_label(c, s, x, y, size, col, alpha=1.0, align="c"):
    font(c, size, True)
    w = text_w(c, s)
    x0 = x - w / 2 if align == "c" else x
    c.set_source_rgba(0.02, 0.025, 0.035, 0.62 * alpha)
    rounded_rect(c, x0 - 16, y - size - 6, w + 32, size + 22, 10); c.fill()
    text(c, s, x0, y, size, col, alpha, bold=True)


_VIG = None
_GRAIN = []


def _make_overlays():
    global _VIG
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    a = np.clip((r - 0.55) / 0.75, 0, 1) ** 1.6 * 0.72
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., 3] = (a * 255).astype(np.uint8)
    _VIG = np_to_surface(rgba)
    rng = np.random.default_rng(7)
    for _ in range(6):
        n = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
        g = np.zeros((H // 2, W // 2, 4), np.uint8)
        v = np.clip(128 + n * 60, 0, 255).astype(np.uint8)
        g[..., 0] = g[..., 1] = g[..., 2] = v
        g[..., 3] = 10
        _GRAIN.append(np_to_surface(g))


def overlays(c, frame_idx, vig=1.0):
    if _VIG is None:
        _make_overlays()
    if vig > 0:
        c.set_source_surface(_VIG, 0, 0)
        c.paint_with_alpha(vig)
    c.save()
    c.scale(2, 2)
    c.set_source_surface(_GRAIN[frame_idx % len(_GRAIN)], 0, 0)
    c.get_source().set_filter(cairo.FILTER_FAST)
    c.paint()
    c.restore()


# ------------------------------------------------------------------ encoder
class Writer:
    def __init__(self, path):
        self.p = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
             "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", path],
            stdin=subprocess.PIPE)

    def write(self, surf):
        surf.flush()
        self.p.stdin.write(surf.get_data())

    def close(self):
        self.p.stdin.close()
        self.p.wait()


# ------------------------------------------------------------------ drawing helpers
def glow_line(c, x0, y0, x1, y1, col, width=3, alpha=1.0, glow=10):
    for w, a in ((glow, 0.10), (glow * 0.5, 0.18), (width, 1.0)):
        c.set_source_rgba(*col, a * alpha)
        c.set_line_width(w)
        c.move_to(x0, y0)
        c.line_to(x1, y1)
        c.stroke()


def arrow_head(c, x, y, ang, size, col, alpha=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.move_to(0, 0)
    c.line_to(-size, -size * 0.45)
    c.line_to(-size, size * 0.45)
    c.close_path()
    c.set_source_rgba(*col, alpha)
    c.fill()
    c.restore()


def rounded_rect(c, x, y, w, h, r):
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def swatch(c, x, y, w, h, col, alpha=1.0, label=None):
    rounded_rect(c, x, y, w, h, 10)
    c.set_source_rgba(*col, alpha)
    c.fill_preserve()
    c.set_source_rgba(1, 1, 1, 0.18 * alpha)
    c.set_line_width(1.2)
    c.stroke()
    if label:
        text(c, label, x + w / 2, y + h + 34, 22, DIM, alpha, align="c")
