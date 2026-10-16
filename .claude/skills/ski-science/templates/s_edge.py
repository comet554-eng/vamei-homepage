"""S4: tilt + press -> the edge becomes a tighter arc. 3D board mesh from ski.board_mesh."""
import math
import numpy as np
import cairo
from common import *
from draw import *
import ski

S4_DUR = 47.0
S4_SUBS = [
    ("把板立起来：只有{w|板头和板尾}碰到雪，", 1.0, 5.2),
    ("中间是悬空的。人的体重往下压，板被压弯，", 5.6, 10.6),
    ("直到整条刃贴住雪面——刃就成了一道{w|更紧}的弧。", 11.0, 16.4),
    ("立得越陡，弧越小：\n转弯半径 ≈ 侧切半径 × cos(立刃角)。", 17.0, 23.8),
    ("这块 8 米侧切的板，立到 60°，\n压出来的弧只剩 {w|4 米}。", 24.4, 30.8),
    ("所以不用拧板：立刃和压弯，\n已经替你决定了这个弯有多大。", 31.4, 38.0),
    ("板顺着这道弧走，就像车轮压着轨道——\n这就是{b|刻滑}。", 38.6, 46.6),
]
CAM = camera(58, 26)
ORG = (640, 560)
SC = 500.0
LIGHT = np.array([-0.3, 0.6, 0.75]); LIGHT /= np.linalg.norm(LIGHT)


def theta_at(t):
    a = ramp(t, 1.4, 4.4) * 30
    a += ramp(t, 18.0, 25.0) * 40          # 30 -> 70
    a -= ramp(t, 26.0, 28.6) * 10          # -> 60
    return math.radians(a)


def press_at(t):
    return ease_io((t - 7.2) / 4.0)


def P(x, y, z):
    pts = np.stack([np.atleast_1d(x), np.atleast_1d(y), np.atleast_1d(z)], 1)
    return proj(pts, CAM, ORG, SC)


def draw_snow_plane(c):
    xs = np.array([-3.2, 3.2, 3.2, -3.2]); ys = np.array([-2.0, -2.0, 3.6, 3.6])
    sx, sy = P(xs, ys, 0 * xs)
    c.move_to(sx[0], sy[0])
    for i in range(1, 4):
        c.line_to(sx[i], sy[i])
    c.close_path()
    g = cairo.LinearGradient(0, sy.min(), 0, sy.max())
    g.add_color_stop_rgb(0, 0.42, 0.48, 0.60)
    g.add_color_stop_rgb(1, 0.78, 0.80, 0.84)
    c.set_source(g); c.fill()
    c.set_line_width(1.0)
    for gx in np.arange(-3.0, 3.01, 0.25):
        a, b = P([gx, gx], [-2.0, 3.6], [0, 0])
        c.move_to(a[0], b[0]); c.line_to(a[1], b[1])
    for gy in np.arange(-2.0, 3.61, 0.25):
        a, b = P([-3.2, 3.2], [gy, gy], [0, 0])
        c.move_to(a[0], b[0]); c.line_to(a[1], b[1])
    c.set_source_rgba(0.15, 0.2, 0.3, 0.18); c.stroke()


def draw_trace(c, th, alpha):
    if alpha <= 0:
        return
    (cx, cy), r = ski.trace_circle(th)
    lim = min(3.0, 0.97 * r)
    xs = np.linspace(-lim, lim, 160)
    ys = cy - np.sqrt(r * r - xs ** 2)
    sx, sy = P(xs, ys, 0 * xs)
    behind = xs < -ski.BOARD_C / 2
    ahead = xs > ski.BOARD_C / 2
    c.set_line_width(4); c.set_source_rgba(0.08, 0.1, 0.16, 0.7 * alpha)
    idx = np.where(behind)[0]
    if len(idx) > 1:
        c.move_to(sx[idx[0]], sy[idx[0]])
        for i in idx[1:]:
            c.line_to(sx[i], sy[i])
        c.stroke()
    c.set_dash([10, 10]); c.set_line_width(2.4); c.set_source_rgba(*GOLD, 0.85 * alpha)
    idx = np.where(ahead)[0]
    if len(idx) > 1:
        c.move_to(sx[idx[0]], sy[idx[0]])
        for i in idx[1:]:
            c.line_to(sx[i], sy[i])
        c.stroke()
    c.set_dash([])


def draw_board3d(c, th, pr):
    X, Y, Z = ski.board_mesh(th, pr)
    nx, ny = X.shape
    sx, sy = proj(np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1), CAM, ORG, SC)
    sx = sx.reshape(nx, ny); sy = sy.reshape(nx, ny)
    for i in range(nx - 1):
        for j in range(ny - 1):
            p0 = np.array([X[i, j], Y[i, j], Z[i, j]]); p1 = np.array([X[i + 1, j], Y[i + 1, j], Z[i + 1, j]])
            p2 = np.array([X[i, j + 1], Y[i, j + 1], Z[i, j + 1]])
            n = np.cross(p1 - p0, p2 - p0); nn = np.linalg.norm(n)
            if nn < 1e-12:
                continue
            n /= nn
            if n @ CAM[0] < 0:
                n = -n
            lam = 0.35 + 0.65 * max(0.0, n @ LIGHT)
            stripe = abs((j + 0.5) / (ny - 1) - 0.5) < 0.12
            base = (0.62, 0.48, 0.24) if stripe else (0.15, 0.16, 0.20)
            c.move_to(sx[i, j], sy[i, j]); c.line_to(sx[i + 1, j], sy[i + 1, j])
            c.line_to(sx[i + 1, j + 1], sy[i + 1, j + 1]); c.line_to(sx[i, j + 1], sy[i, j + 1]); c.close_path()
            c.set_source_rgb(*(b * lam for b in base)); c.fill_preserve()
            c.set_source_rgba(*(b * lam for b in base), 1); c.set_line_width(0.8); c.stroke()
    # bindings
    for xb in (-0.27, 0.27):
        i = int(np.argmin(np.abs(X[:, 0] - xb)))
        pts = [(sx[i - 1, 1], sy[i - 1, 1]), (sx[i + 1, 1], sy[i + 1, 1]), (sx[i + 1, ny - 2], sy[i + 1, ny - 2]), (sx[i - 1, ny - 2], sy[i - 1, ny - 2])]
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        c.close_path(); c.set_source_rgba(0.03, 0.03, 0.04, 0.95); c.fill()
    # edges
    for j, col, w in ((0, (0.6, 0.62, 0.66), 1.6), (ny - 1, GOLD, 3.2)):
        c.move_to(sx[0, j], sy[0, j])
        for i in range(1, nx):
            c.line_to(sx[i, j], sy[i, j])
        c.set_source_rgba(*col, 0.95); c.set_line_width(w); c.stroke()
    return X, Y, Z


def magnifier(c, th, pr, alpha, cx=1060, cy=262, R=118):
    if alpha <= 0:
        return
    c.save()
    c.arc(cx, cy, R, 0, 2 * math.pi); c.set_source_rgba(0.04, 0.05, 0.07, 0.9 * alpha); c.fill_preserve()
    c.set_source_rgba(1, 1, 1, 0.5 * alpha); c.set_line_width(1.6); c.stroke()
    c.arc(cx, cy, R - 2, 0, 2 * math.pi); c.clip()
    xs = np.linspace(-ski.BOARD_C / 2, ski.BOARD_C / 2, 60)
    d = ski.sag()
    Rx = ((ski.BOARD_C / 2) ** 2 + d * d) / (2 * d)
    s = ski.BOARD_W / 2 - (ski.BOARD_W / 2 - d + Rx - np.sqrt(Rx * Rx - xs ** 2))
    z = s * math.sin(th) * (1 - pr)
    kx, kz = 170 / ski.BOARD_C, 3600.0
    ys = cy + 40
    c.set_source_rgba(0.78, 0.80, 0.84, alpha); c.rectangle(cx - R, ys, 2 * R, R); c.fill()
    c.move_to(cx + xs[0] * kx, ys - z[0] * kz)
    for x, zz in zip(xs[1:], z[1:]):
        c.line_to(cx + x * kx, ys - zz * kz)
    c.set_source_rgba(*GOLD, alpha); c.set_line_width(3); c.stroke()
    c.restore()
    zmid = z.max() * 1000
    text(c, f"悬空 {zmid:.0f} mm" if zmid >= 0.5 else "贴住了", cx, cy - 34, 24, INK, alpha, align="c", bold=True)
    text(c, "刃的侧面 · 竖直放大 30 倍", cx, cy + R + 30, 20, DIM, alpha, align="c")


def tilt_panel(c, th, alpha, cx=300, cy=330):
    """cross-section from behind: board tilted theta onto its edge."""
    if alpha <= 0:
        return
    rounded_rect(c, cx - 200, cy - 130, 400, 220, 14); c.set_source_rgba(0.03, 0.04, 0.06, 0.78 * alpha); c.fill()
    text(c, "从板后方看", cx - 180, cy - 98, 20, DIM, alpha)
    ex, ey = cx + 60, cy + 40
    c.set_source_rgba(0.78, 0.80, 0.84, alpha); c.rectangle(cx - 190, ey, 380, 40); c.fill()
    L = 150
    dx, dy = -math.cos(th) * L, -math.sin(th) * L
    nx, ny = math.sin(th) * 10, -math.cos(th) * 10
    c.move_to(ex, ey); c.line_to(ex + dx, ey + dy); c.line_to(ex + dx + nx, ey + dy + ny); c.line_to(ex + nx, ey + ny); c.close_path()
    c.set_source_rgba(0.62, 0.48, 0.24, alpha); c.fill()
    c.arc(ex, ey, 6, 0, 2 * math.pi); c.set_source_rgba(*GOLD, alpha); c.fill()
    c.set_source_rgba(1, 1, 1, 0.8 * alpha); c.set_line_width(1.6)
    c.arc_negative(ex, ey, 70, math.pi, math.pi + th); c.stroke()
    text(c, f"{math.degrees(th):.0f}°", ex - 96, ey - 18, 24, INK, alpha, bold=True)
    text(c, "刃", ex + 14, ey - 10, 20, GOLD, alpha)


def inset(c, th, alpha, x0=1300, y0=262):
    if alpha <= 0:
        return
    s = 30.0
    bx, by = x0 + 270, y0 + 18
    c.save()
    rounded_rect(c, x0, y0 - 52, 540, 580, 16); c.set_source_rgba(0.03, 0.04, 0.06, 0.78 * alpha); c.fill()
    text(c, "俯视 · 真实比例", x0 + 24, y0 - 16, 22, DIM, alpha)
    c.set_dash([6, 8]); c.set_source_rgba(1, 1, 1, 0.45 * alpha); c.set_line_width(1.4)
    c.arc(bx, by + ski.R_SC * s, ski.R_SC * s, 0, 2 * math.pi); c.stroke(); c.set_dash([])
    r = ski.turn_radius(th)
    c.set_source_rgba(*GOLD, alpha); c.set_line_width(2.6)
    c.arc(bx, by + r * s, r * s, 0, 2 * math.pi); c.stroke()
    board_top(c, bx, by, 0.0, s, alpha, rider=False)
    c.restore()
    text(c, "侧切 8 m", bx + 8 * s * 0.72, by + 8 * s * 0.28 + 8 * s * 0.0 + 60, 20, DIM, alpha)
    pill_label(c, f"R = 8 m × cos {math.degrees(th):.0f}° = {r:.1f} m", x0 + 270, y0 + 500, 26, GOLD, alpha)


def s4(c, t, fi):
    paint_bg(c, (0.02, 0.025, 0.035))
    th, pr = theta_at(t), press_at(t)
    draw_snow_plane(c)
    draw_trace(c, th, ramp(t, 11.0, 12.6))
    draw_board3d(c, th, pr)
    tilt_panel(c, th, ramp(t, 1.2, 2.2))
    magnifier(c, th, pr, ramp(t, 3.6, 4.8) * (1 - ramp(t, 16.0, 17.0)), cx=1060, cy=330)
    inset(c, th, ramp(t, 12.4, 13.6))
    deg = math.degrees(th)
    chapter_tag(c, f"立刃 {deg:.0f}°", f"刃在雪上的弧：半径 {ski.turn_radius(th):.1f} m" if pr > 0.95 else "转弯半径 —",
                alpha=window(t, 0.6, S4_DUR + 1, 0.5))
    cite_card(c, "Howe 2001 · Reid et al. 2020", "R = 侧切半径 × cos(立刃角)", "理想刚性雪面 · 整条刃贴雪",
              alpha=window(t, 17.2, 30.6, 0.5))
    model_note(c, ramp(t, 1.0, 2.0), "示意 · 按理想刚性雪面计算；板的形状与弯曲为真实比例")
    for st, a, b in S4_SUBS:
        subtitle(c, st, t, a, b)
    fade_black(c, 1 - ramp(t, 0, 0.8))
    fade_black(c, ramp(t, S4_DUR - 0.5, S4_DUR))
    overlays(c, fi)
