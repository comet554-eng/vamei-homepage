"""《单板从0到刻滑》竖屏 2D 叠加（1080×1920）：大字标题、描边字幕、关卡徽章、追踪 3D 关节的标注。"""
import math, subprocess
import cairo
import numpy as np
from PIL import Image

W, H, FPS = 1080, 1920, 30
SERIF, SANS = "Noto Serif SC", "Noto Sans SC"
INK = (0.97, 0.96, 0.93)
DIM = (0.70, 0.73, 0.78)
GOLD = (1.0, 0.78, 0.36)
ICE = (0.55, 0.80, 1.0)
RED = (1.0, 0.36, 0.30)
GREEN = (0.40, 0.90, 0.55)
SERIES = "单板从0到刻滑"


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x); return x * x * (3 - 2 * x)


def ramp(t, t0, t1):
    return ease((t - t0) / max(1e-6, t1 - t0))


def window(t, a, b, fade=0.3):
    return min(ramp(t, a - fade * 0.5, a + fade * 0.5), 1 - ramp(t, b - fade * 0.5, b + fade * 0.5))


def pop(t, t0, d=0.35):
    """弹出：0 -> 1.08 -> 1"""
    x = clamp((t - t0) / d)
    return 0 if x <= 0 else (1 - (1 - x) ** 3) * (1 + 0.25 * math.sin(math.pi * x) * (1 - x))


def font(c, size, bold=False, face=SANS):
    c.select_font_face(face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)


def tw(c, s):
    return c.text_extents(s).x_advance


def rrect(c, x, y, w, h, r):
    c.new_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def stroke_text(c, s, x, y, size, col=INK, alpha=1.0, bold=True, face=SANS, align="c", stroke=None, spacing=0.0):
    """带黑描边的字（手机上任何背景都看得清）。返回宽度。"""
    if alpha <= 0.003 or not s:
        return 0
    font(c, size, bold, face)
    w = tw(c, s) + spacing * size * (len(s) - 1)
    x0 = x - w / 2 if align == "c" else (x - w if align == "r" else x)
    c.new_path()
    xx = x0
    for ch in (s if spacing else [s]):
        c.move_to(xx, y); c.text_path(ch)
        xx += tw(c, ch) + spacing * size
    sw = stroke if stroke is not None else size * 0.16
    if sw:
        c.set_source_rgba(0.02, 0.03, 0.06, 0.85 * alpha); c.set_line_width(sw); c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.stroke_preserve()
    c.set_source_rgba(*col, alpha); c.fill()
    return w


COLS = {"b": ICE, "w": GOLD, "r": RED, "g": GREEN}


def spans(s):
    out, i = [], 0
    while i < len(s):
        j = s.find("{", i)
        if j < 0:
            out.append((s[i:], INK)); break
        if j > i:
            out.append((s[i:j], INK))
        k = s.find("}", j)
        out.append((s[j + 3:k], COLS[s[j + 1]])); i = k + 1
    return out


def rich_line(c, sp, cx, y, size, alpha=1.0, face=SANS):
    font(c, size, True, face)
    ws = [tw(c, s) for s, _ in sp]
    x = cx - sum(ws) / 2
    c.new_path()
    xx = x
    for (s, _), w in zip(sp, ws):
        c.move_to(xx, y); c.text_path(s); xx += w
    c.set_source_rgba(0.02, 0.03, 0.06, 0.9 * alpha); c.set_line_width(size * 0.18); c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.stroke()
    for (s, col), w in zip(sp, ws):
        c.move_to(x, y); c.set_source_rgba(*col, alpha); c.show_text(s); x += w


def wrap(s, maxc=13):
    """按标点把长字幕拆成最多两行（竖屏每行 ≤ 13 字左右）。"""
    from_plain = s
    vis = []
    i, depth = 0, 0
    while i < len(s):
        if s[i] == "{" and i + 2 < len(s) and s[i + 2] == "|":
            depth += 1; i += 3; continue
        if s[i] == "}" and depth:
            depth -= 1; i += 1; continue
        vis.append((i, s[i], depth)); i += 1
    n = len(vis)
    if n <= maxc:
        return [s]
    cand = [(k + 1, idx) for k, (idx, ch, d) in enumerate(vis) if ch in "，；：、。？" and not d and k + 1 < n]
    if not cand:
        cand = [(k + 1, idx) for k, (idx, ch, d) in enumerate(vis) if not d and k + 1 < n]
    k, idx = min(cand, key=lambda q: abs(q[0] - n / 2))
    a, b = s[:idx + 1], s[idx + 1:]
    # 断在标签里时补全标签
    if a.count("{") > a.count("}"):
        tag = a[a.rfind("{"):a.rfind("{") + 3]
        a += "}"; b = tag + b
    return [a, b]


def subtitle(c, s, t, t0, t1, y=1500, size=58):
    a = window(t, t0, t1, 0.25)
    if a <= 0:
        return
    lines = wrap(s)
    # 句末句号不显示（竖屏字幕习惯）
    lines = [ln[:-1] if ln.endswith("。") else ln for ln in lines]
    lines = [ln.replace("。}", "}") if ln.endswith("。}") else ln for ln in lines]
    lift = 6 * (1 - ramp(t, t0, t0 + 0.2))
    for i, ln in enumerate(lines):
        rich_line(c, spans(ln), W / 2, y + i * size * 1.35 + lift, size, a)


def badge(c, level, lesson, title, alpha=1.0, prog=0.0):
    """左上：系列名 + 关卡徽章 + 本集进度条。"""
    if alpha <= 0:
        return
    x, y = 60, 205
    stroke_text(c, SERIES, x, y, 26, GOLD, alpha, bold=True, align="l", stroke=5, spacing=0.12)
    font(c, 30, True)
    lab = f"{level} · 第{lesson}课"
    w = tw(c, lab)
    c.set_source_rgba(0.02, 0.03, 0.06, 0.55 * alpha); rrect(c, x, y + 18, w + 36, 52, 26); c.fill()
    c.set_source_rgba(*GOLD, alpha); c.set_line_width(2); rrect(c, x, y + 18, w + 36, 52, 26); c.stroke()
    stroke_text(c, lab, x + 18, y + 55, 30, INK, alpha, align="l", stroke=0)
    # 进度条
    c.set_source_rgba(1, 1, 1, 0.18 * alpha); rrect(c, x, y + 88, 300, 6, 3); c.fill()
    c.set_source_rgba(*GOLD, alpha); rrect(c, x, y + 88, max(6, 300 * prog), 6, 3); c.fill()


def big_title(c, lines, t, t0, t1, y=470, size=96, face=SERIF):
    """屏幕上方的大字：lines = [(markup, size_scale)]"""
    a = window(t, t0, t1, 0.3)
    if a <= 0:
        return
    for i, (ln, k) in enumerate(lines):
        p = pop(t, t0 + 0.12 * i, 0.4)
        if p <= 0:
            continue
        sz = size * k
        c.save()
        yy = y + sum(size * kk * 1.25 for _, kk in lines[:i])
        c.translate(W / 2, yy - sz * 0.35); c.scale(p, p); c.translate(-W / 2, -(yy - sz * 0.35))
        rich_line(c, spans(ln), W / 2, yy, sz, a, face)
        c.restore()


def tag(c, s, col, x, y, alpha=1.0, size=34, icon=None):
    """彩色小标签，比如 ✕ 错误示范 / ✓ 正确做法。"""
    if alpha <= 0:
        return
    font(c, size, True)
    w = tw(c, s) + (size * 1.1 if icon else 0)
    c.set_source_rgba(*col, 0.92 * alpha); rrect(c, x, y, w + 40, size + 26, (size + 26) / 2); c.fill()
    tx = x + 20
    if icon == "x":
        c.set_source_rgba(1, 1, 1, alpha); c.set_line_width(5); r = size * 0.32; cx, cy = tx + r, y + (size + 26) / 2
        c.move_to(cx - r, cy - r); c.line_to(cx + r, cy + r); c.move_to(cx + r, cy - r); c.line_to(cx - r, cy + r); c.stroke()
        tx += size * 1.1
    elif icon == "v":
        c.set_source_rgba(1, 1, 1, alpha); c.set_line_width(5); r = size * 0.34; cx, cy = tx + r, y + (size + 26) / 2
        c.move_to(cx - r, cy); c.line_to(cx - r * 0.25, cy + r * 0.7); c.line_to(cx + r, cy - r * 0.7); c.stroke()
        tx += size * 1.1
    c.move_to(tx, y + size + 6); c.set_source_rgba(1, 1, 1, alpha); c.show_text(s)


def ring(c, x, y, r, col, alpha=1.0, t=0.0, pulse=True, label=None, side=None):
    if alpha <= 0:
        return
    k = 1 + (0.08 * math.sin(t * 8) if pulse else 0)
    for rr, a, lw in ((r * k + 10, 0.25, 10), (r * k, 1.0, 5)):
        c.new_path(); c.arc(x, y, rr, 0, 2 * math.pi); c.set_source_rgba(*col, a * alpha); c.set_line_width(lw); c.stroke()
    if label:
        if side is None:
            side = -1 if x > W * 0.52 else 1
        lx = x + side * (r + 30)
        c.new_path(); c.move_to(x + side * r * 0.7, y - r * 0.7); c.line_to(lx, y - r - 30); c.line_to(lx + side * 30, y - r - 30)
        c.set_source_rgba(*col, alpha); c.set_line_width(4); c.stroke()
        stroke_text(c, label, lx + side * 40, y - r - 18, 52, col, alpha, align="l" if side > 0 else "r")


def arrow(c, x0, y0, x1, y1, col, alpha=1.0, w=10):
    if alpha <= 0:
        return
    ang = math.atan2(y1 - y0, x1 - x0); hl = w * 3
    xe, ye = x1 - hl * 0.8 * math.cos(ang), y1 - hl * 0.8 * math.sin(ang)
    c.new_path(); c.move_to(x0, y0); c.line_to(xe, ye)
    c.set_source_rgba(0.02, 0.03, 0.06, 0.6 * alpha); c.set_line_width(w + 6); c.stroke()
    c.move_to(x0, y0); c.line_to(xe, ye); c.set_source_rgba(*col, alpha); c.set_line_width(w); c.stroke()
    c.new_path(); c.move_to(x1, y1)
    c.line_to(x1 - hl * math.cos(ang - 0.45), y1 - hl * math.sin(ang - 0.45))
    c.line_to(x1 - hl * math.cos(ang + 0.45), y1 - hl * math.sin(ang + 0.45)); c.close_path()
    c.set_source_rgba(*col, alpha); c.fill()


def card(c, x, y, w, h, alpha=1.0, edge=GOLD):
    if alpha <= 0:
        return
    c.set_source_rgba(0.03, 0.045, 0.09, 0.82 * alpha); rrect(c, x, y, w, h, 28); c.fill()
    c.set_source_rgba(*edge, 0.9 * alpha); c.set_line_width(3); rrect(c, x, y, w, h, 28); c.stroke()


def note(c, s, alpha=1.0):
    stroke_text(c, s, 60, H - 330, 24, DIM, alpha * 0.9, bold=False, align="l", stroke=4)


def load_frame(path, zoom=1.0, focus=(0.5, 0.5)):
    im = Image.open(path).convert("RGB")
    if zoom != 1.0:
        iw, ih = im.size
        cw, ch = iw / zoom, ih / zoom
        fx, fy = focus[0] * iw, focus[1] * ih
        x0 = clamp(fx - cw / 2, 0, iw - cw); y0 = clamp(fy - ch / 2, 0, ih - ch)
        im = im.crop((x0, y0, x0 + cw, y0 + ch))
    else:
        x0 = y0 = 0; cw, ch = im.size
    im = im.resize((W, H), Image.LANCZOS)
    a = np.asarray(im)
    buf = np.dstack([a[..., 2], a[..., 1], a[..., 0], np.full(a.shape[:2], 255, np.uint8)]).copy()
    s = cairo.ImageSurface.create_for_data(memoryview(buf), cairo.FORMAT_ARGB32, W, H)
    iw0 = Image.open(path).size

    def to_px(u, v):     # 归一化的 3D 投影坐标 -> 成片像素
        return ((u * iw0[0] - x0) / cw * W, (v * iw0[1] - y0) / ch * H)
    return s, buf, to_px


def vignette(c, a=0.55):
    g = cairo.RadialGradient(W / 2, H * 0.52, H * 0.25, W / 2, H * 0.52, H * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, a)
    c.set_source(g); c.paint()
    # 顶部、底部压暗，给文字留底
    for y0, y1, a0, a1 in ((0, 620, 0.55, 0.0), (1300, H, 0.0, 0.6)):
        g = cairo.LinearGradient(0, y0, 0, y1); g.add_color_stop_rgba(0, 0, 0, 0, a0); g.add_color_stop_rgba(1, 0, 0, 0, a1)
        c.rectangle(0, y0, W, y1 - y0); c.set_source(g); c.fill()


class Writer:
    def __init__(self, path, crf=20):
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                                   "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
                                   "-pix_fmt", "yuv420p", "-movflags", "+faststart", path], stdin=subprocess.PIPE)

    def write(self, s):
        s.flush(); self.p.stdin.write(s.get_data())

    def close(self):
        self.p.stdin.close(); self.p.wait()


def chips(c, items, cur, t, alpha, y=440):
    """分步进度条：当前一步亮金色，做完的变绿。"""
    if alpha <= 0:
        return
    n = len(items); gap = 14; cw = (W - 120 - gap * (n - 1)) / n
    for i, s in enumerate(items):
        x = 60 + i * (cw + gap)
        on, done = i == cur, i < cur
        col = GOLD if on else (GREEN if done else (0.5, 0.53, 0.58))
        c.set_source_rgba(0.03, 0.045, 0.09, (0.85 if on else 0.6) * alpha); rrect(c, x, y, cw, 84, 20); c.fill()
        c.set_source_rgba(*col, alpha * (1 if on or done else 0.6)); c.set_line_width(4 if on else 2); rrect(c, x, y, cw, 84, 20); c.stroke()
        size = 34 if len(s) <= 5 else (30 if len(s) <= 6 else 26)
        stroke_text(c, s, x + cw / 2, y + 55, size, col if on else (INK if done else DIM), alpha, stroke=0)


def step_of(t, S):
    k = -1
    for i, (_, a, _) in enumerate(S):
        if t >= a - 0.1:
            k = i
    return k


def mid(P, a, b):
    return ((P[a][0] + P[b][0]) / 2, (P[a][1] + P[b][1]) / 2)


def run_episode(ep, FR, OUTF, draw, zoom_fn=None, next_lines=None):
    """逐帧：读 3D 帧 + 关节投影 -> 暗角、徽章、本集标注(draw)、字幕、结尾下一课卡片 -> 编码。
    环境变量 STILLS="1.0 2.5" 时只出这几个时刻的 png（找不到的帧用同镜头最近的一帧代替）。"""
    import os, json
    import cairo as _c
    plan = ep.plan()
    e0, e1, es = ep.SEC["end"]
    stills = [float(x) for x in os.environ.get("STILLS", "").split()]
    avail = sorted(f[:-5] for f in os.listdir(FR) if f.endswith(".json"))

    def find(k):
        if os.path.exists(os.path.join(FR, k + ".json")) or not stills:
            return k
        sh, n = k.rsplit("_", 1)
        cand = [a for a in avail if a.rsplit("_", 1)[0] == sh]
        return min(cand, key=lambda a: abs(int(a.rsplit("_", 1)[1]) - int(n)))

    wr = None if stills else Writer(OUTF)
    frames = [int(x * FPS) for x in stills] or range(len(plan))
    for i in frames:
        t = i / FPS
        shot, perf, p = plan[i]
        k = find(ep.key(shot, p))
        m = json.load(open(os.path.join(FR, k + ".json")))
        zoom, focus = (zoom_fn(t, m, shot, p) if zoom_fn else (1.0, (0.5, 0.5)))
        if t >= e0:
            zoom *= 1 + 0.05 * ramp(t, e0, e1)
        s, buf, px = load_frame(os.path.join(FR, k + ".png"), zoom, focus)
        c = _c.Context(s)
        P = {q: px(m[q][0], m[q][1]) for q in m if not q.startswith("_")}
        vignette(c, 0.45)
        if t >= e0:
            c.set_source_rgba(0.01, 0.015, 0.03, 0.6 * ramp(t, e0, e0 + 0.5)); c.paint()
        badge(c, ep.LEVEL, ep.LESSON, ep.TITLE, ramp(t, 0.0, 0.4), t / ep.DUR)
        stroke_text(c, "3D 示意", W - 60, 235, 24, DIM, 0.8, bold=False, align="r", stroke=4)
        draw(c, t, P, m, shot, p)
        if t >= e0 - 0.3 and next_lines:
            a = ramp(t, e0, e0 + 0.4)
            stroke_text(c, "下一课", W / 2, 720, 48, GOLD, a, spacing=0.3)
            big_title(c, next_lines, t, e0 + 0.1, e1 + 5, y=860, size=110)
            stroke_text(c, "关注我，跟着练到刻滑", W / 2, 1180, 40, INK, a * ramp(t, e0 + 0.8, e0 + 1.2), bold=False)
        for st, a0, a1 in ep.SUBS:
            if st != es[0][0]:
                subtitle(c, st, t, a0, a1)
        fade = 1 - ramp(t, 0, 0.15) + ramp(t, ep.DUR - 0.4, ep.DUR)
        if fade > 0:
            c.set_source_rgba(0, 0, 0, min(1, fade)); c.paint()
        if stills:
            s.write_to_png(f"{OUTF}_{t:05.2f}.png")
        else:
            wr.write(s)
    if wr:
        wr.close()


def spin_arrow(c, x, y, r, col, alpha=1.0, t=0.0, label=None):
    """绕一点转圈的弧形箭头（板打转）。"""
    if alpha <= 0:
        return
    a0 = t * 2.5
    c.new_path(); c.arc(x, y, r, a0, a0 + 4.6)
    c.set_source_rgba(0.02, 0.03, 0.06, 0.6 * alpha); c.set_line_width(14); c.stroke()
    c.new_path(); c.arc(x, y, r, a0, a0 + 4.6); c.set_source_rgba(*col, alpha); c.set_line_width(8); c.stroke()
    ae = a0 + 4.6; ex, ey = x + r * math.cos(ae), y + r * math.sin(ae)
    tx, ty = -math.sin(ae), math.cos(ae)
    c.new_path(); c.move_to(ex + tx * 26, ey + ty * 26)
    c.line_to(ex - ty * 16 - tx * 4, ey + tx * 16 - ty * 4); c.line_to(ex + ty * 16 - tx * 4, ey - tx * 16 - ty * 4); c.close_path()
    c.set_source_rgba(*col, alpha); c.fill()
    if label:
        stroke_text(c, label, x, y - r - 30, 48, col, alpha)
