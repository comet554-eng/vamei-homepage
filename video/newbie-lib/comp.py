"""《单板新手课》竖屏合成：实拍 / 3D 帧 / 2D 插画 + 字幕、标注、数据图。
python3 comp.py EPDIR 2d|3d OUT_RAW.mp4 [--frames a:b] [--still t1,t2,...]"""
import sys, os, math, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ap = argparse.ArgumentParser()
ap.add_argument("ep"); ap.add_argument("mode"); ap.add_argument("out")
ap.add_argument("--still", default=""); ap.add_argument("--r3d", default="r3d"); ap.add_argument("--foot", default="foot")
A = ap.parse_args()
sys.path.insert(0, os.path.abspath(A.ep))
import ep
import cairo
import numpy as np
from PIL import Image
import vert
from vert import (W, H, FPS, INK, DIM, GOLD, ICE, RED, GREEN, clamp, ease, ramp, window, pop, font, tw, rrect,
                  stroke_text, subtitle, big_title, tag, ring, arrow, card, Writer, chips, spans, rich_line)
from epbase import key, plain
from rig3d import interp

vert.SERIES = ep.SERIES
MODE = A.mode
PLAN = ep.plan()
SEC, SUBS, DUR = ep.SEC, ep.SUBS, ep.DUR
if MODE == "2d":
    from draw2d import draw_scene


# ------------------------------------------------------------------ 背景
def surf_from_rgb(a):
    buf = np.dstack([a[..., 2], a[..., 1], a[..., 0], np.full(a.shape[:2], 255, np.uint8)]).copy()
    return cairo.ImageSurface.create_for_data(memoryview(buf), cairo.FORMAT_ARGB32, W, H), buf


def base_frame(i):
    """返回 (cairo surface, buf, 关节像素坐标 or None)"""
    kind, shot, p = PLAN[i]
    if kind == "F":
        n = min(int(round(p * FPS)) + 1, len(os.listdir(os.path.join(A.foot, shot))))
        a = np.asarray(Image.open(os.path.join(A.foot, shot, f"{n:04d}.jpg")).convert("RGB"))
        s, b = surf_from_rgb(a)
        return s, b, None
    if MODE == "3d":
        k = key(shot, p)
        im = Image.open(os.path.join(A.r3d, k + ".png")).convert("RGB")
        iw, ih = im.size
        a = np.asarray(im.resize((W, H), Image.LANCZOS))
        s, b = surf_from_rgb(a)
        meta = json.load(open(os.path.join(A.r3d, k + ".json")))
        pts = {q: (v[0] * W, v[1] * H) for q, v in meta.items() if not q.startswith("_")}
        return s, b, pts
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    P = interp(ep.PERF[ep.SHOT_PERF[shot]], p)
    pts = draw_scene(c, P, ep.cam(shot, p, P), marks=getattr(ep, "MARKS", False), extra=getattr(ep, "extra_points", None))
    return s, None, pts


# ------------------------------------------------------------------ 小部件
def shade(c, top=0.45, bot=0.55):
    for y0, y1, a0, a1 in ((0, 560, top, 0.0), (1280, H, 0.0, bot)):
        g = cairo.LinearGradient(0, y0, 0, y1); g.add_color_stop_rgba(0, 0, 0, 0, a0); g.add_color_stop_rgba(1, 0, 0, 0, a1)
        c.rectangle(0, y0, W, y1 - y0); c.set_source(g); c.fill()


def header(c, t):
    a = 1 - window(t, 0, SEC["hook"][1], 0.3) if t < SEC["hook"][1] + 0.3 else 1.0
    a = min(a, 1 - ramp(t, DUR - 3.0, DUR - 2.6))
    if a <= 0:
        return
    stroke_text(c, ep.SERIES, 60, 175, 28, GOLD, a, align="l", stroke=5, spacing=0.12)
    stroke_text(c, ep.TITLE, 60, 228, 40, INK, a, align="l", stroke=7)
    c.set_source_rgba(1, 1, 1, 0.22 * a); rrect(c, 60, 252, 300, 6, 3); c.fill()
    c.set_source_rgba(*GOLD, a); rrect(c, 60, 252, max(6, 300 * t / DUR), 6, 3); c.fill()


def mode_tag(c, a=1.0):
    s = "3D 演示" if MODE == "3d" else "2D 演示"
    font(c, 26, True); w = tw(c, s)
    c.set_source_rgba(0.03, 0.045, 0.09, 0.55 * a); rrect(c, W - 60 - w - 30, 150, w + 30, 44, 22); c.fill()
    stroke_text(c, s, W - 60 - w / 2 - 15, 181, 26, ICE, a, stroke=0)


def note(c, s, a=1.0, y=H - 300):
    stroke_text(c, s, 60, y, 26, DIM, a * 0.95, bold=False, align="l", stroke=5)


def stance_card(c, t, a, t_ang):
    """俯视示意图：站距 + 固定器角度。"""
    if a <= 0:
        return
    x, y, w, h = 90, 1085, 900, 330
    card(c, x, y, w, h, a, ICE)
    stroke_text(c, "俯视 · 入门常用设置", x + 36, y + 56, 30, ICE, a, align="l", stroke=0)
    cx, cy = x + w / 2, y + 190
    L, hw = 330, 62
    c.save(); c.translate(cx, cy)
    # 板
    c.new_path()
    c.move_to(-L + 40, -hw); c.line_to(L - 40, -hw); c.curve_to(L + 10, -hw, L + 10, hw, L - 40, hw)
    c.line_to(-L + 40, hw); c.curve_to(-L - 10, hw, -L - 10, -hw, -L + 40, -hw); c.close_path()
    c.set_source_rgba(0.22, 0.62, 0.95, a); c.fill_preserve(); c.set_source_rgba(1, 1, 1, 0.6 * a); c.set_line_width(3); c.stroke()
    stroke_text(c, "板头", -L + 30, -hw - 18, 24, DIM, a, bold=False, stroke=0)
    stroke_text(c, "板尾", L - 30, -hw - 18, 24, DIM, a, bold=False, stroke=0)
    stroke_text(c, "脚尖一侧", 0, hw + 100, 22, DIM, a * 0, bold=False, stroke=0)
    k = ramp(t, t_ang, t_ang + 0.8)
    for fx, ang, col, lab in ((-150, ep.STANCE_FRONT, GOLD, f"前脚 +{ep.STANCE_FRONT}°"), (150, ep.STANCE_BACK, GOLD, f"后脚 0~{ep.STANCE_BACK}°")):
        th = math.radians(ang * k)
        c.save(); c.translate(fx, 0)
        # 0° 参考线
        c.set_source_rgba(1, 1, 1, 0.35 * a); c.set_line_width(2); c.set_dash([8, 8])
        c.move_to(0, -hw - 6); c.line_to(0, hw + 6); c.stroke(); c.set_dash([])
        c.rotate(th)
        rrect(c, -26, -hw + 4, 52, 2 * hw - 8, 14); c.set_source_rgba(0.12, 0.12, 0.15, a); c.fill()
        c.set_source_rgba(*col, a); c.set_line_width(5); c.move_to(0, -hw - 14); c.line_to(0, hw + 14); c.stroke()
        c.restore()
        if k > 0.05:
            stroke_text(c, lab, fx, hw + 58, 30, col, a * k, stroke=0)
    # 站距
    kw = ramp(t, SEC["setup"][2][0][1] + 0.3, SEC["setup"][2][0][1] + 1.1)
    if kw > 0:
        yy = -hw - 52
        c.set_source_rgba(*INK, a * kw); c.set_line_width(3)
        c.move_to(-150, yy); c.line_to(150, yy); c.stroke()
        for xx in (-150, 150):
            c.move_to(xx, yy - 12); c.line_to(xx, yy + 12); c.stroke()
        stroke_text(c, "≈ 肩宽", 0, yy - 14, 30, INK, a * kw, stroke=0)
    c.restore()


def weight_bar(c, t, a, front):
    """两脚重心分配条。"""
    if a <= 0:
        return
    x, y, w, h = 140, 1190, 800, 150
    card(c, x - 30, y - 70, w + 60, h + 100, a, GOLD)
    stroke_text(c, "重心分配", x, y - 22, 30, GOLD, a, align="l", stroke=0)
    fb = w * front
    c.set_source_rgba(*ICE, 0.85 * a); rrect(c, x, y + 10, w - fb, 56, 14); c.fill()
    c.set_source_rgba(*GOLD, 0.95 * a); rrect(c, x + w - fb, y + 10, fb, 56, 14); c.fill()
    stroke_text(c, f"后脚 {round((1 - front) * 100)}%", x + 20, y + 50, 30, (0.03, 0.05, 0.1), a, align="l", stroke=0)
    stroke_text(c, f"前脚 {round(front * 100)}%", x + w - 20, y + 50, 30, (0.03, 0.05, 0.1), a, align="r", stroke=0)
    stroke_text(c, "示意：平地站立时大约一半一半，略偏前脚", x, y + 112, 24, DIM, a, bold=False, align="l", stroke=0)


def impact_chart(c, t, a, t1, t2):
    """柱状图：过 10 cm 小坎时腿要扛的冲击（倍体重）。"""
    if a <= 0:
        return
    x, y, w, h = 90, 1040, 900, 380
    card(c, x, y, w, h, a, GOLD)
    stroke_text(c, "过 10 厘米小坎，腿要扛多少？", x + 36, y + 56, 30, GOLD, a, align="l", stroke=0)
    base = y + h - 70; top = y + 100; scale = (base - top) / 6.5
    for i, (lab, sub, g, col, t0) in enumerate((("直腿", "缓冲约 2 cm", ep.G_STRAIGHT, RED, t1), ("屈膝", "缓冲约 10 cm", ep.G_BENT, GREEN, t2))):
        k = ease((t - t0) / 0.8)
        bx = x + 200 + i * 340; bw = 150
        c.set_source_rgba(1, 1, 1, 0.08 * a); rrect(c, bx, top, bw, base - top, 12); c.fill()
        if k > 0:
            hh = g * scale * k
            c.set_source_rgba(*col, 0.95 * a); rrect(c, bx, base - hh, bw, hh, 12); c.fill()
            stroke_text(c, f"{g * k:.0f} 倍体重" if k > 0.95 else f"{g * k:.1f}", bx + bw / 2, base - hh - 18, 38, col, a, stroke=6)
        stroke_text(c, lab, bx + bw / 2, base + 40, 32, INK, a, stroke=0)
        stroke_text(c, sub, bx + bw + 20, base - 12, 24, DIM, a * clamp(k * 3), bold=False, align="l", stroke=0)
    # 1 倍体重参考线
    c.set_source_rgba(1, 1, 1, 0.35 * a); c.set_dash([6, 6]); c.set_line_width(2)
    c.move_to(x + 160, base - scale); c.line_to(x + w - 40, base - scale); c.stroke(); c.set_dash([])
    stroke_text(c, "1 倍体重", x + w - 40, base - scale - 10, 22, DIM, a, bold=False, align="r", stroke=0)


def counter(c, t, a, t0, t_hop):
    if a <= 0:
        return
    sq = min(10, int(max(0, t - t0 - 0.4) / 1.1 * 10 / 3 + 0.0)) if t < t_hop else 10
    tag(c, f"蹲起 ×10", GOLD, 120, 1150, a, 40)
    tag(c, f"小跳 ×5", ICE, 600, 1150, a * ramp(t, t_hop - 0.3, t_hop), 40)


def stamp(c, s, x, y, t, t0, col=GREEN, a=1.0):
    p = pop(t, t0, 0.35)
    if p <= 0 or a <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(-0.12); c.scale(p, p)
    font(c, 64, True); w = tw(c, s)
    c.set_source_rgba(*col, 0.95 * a); c.set_line_width(7); rrect(c, -w / 2 - 30, -62, w + 60, 92, 18); c.stroke()
    c.move_to(-w / 2, 0); c.set_source_rgba(*col, a); c.show_text(s)
    c.restore()


def hook_title(c, t, name, stamp_text=None, stamp_col=RED):
    """开头：大标题“单板第N课 / 名字”，第二句字幕出来时盖一个章。"""
    h0, h1, hs = SEC["hook"]
    if t < h1 + 0.2:
        big_title(c, [(f"单板{{w|第{ep.LESSON}课}}", 0.8), (name, 1.25)], t, 0.15, h1 + 0.1, y=560, size=110)
        if stamp_text and len(hs) > 1 and t > hs[1][1]:
            stamp(c, stamp_text, W / 2, 1180, t, hs[1][1] + 0.1, stamp_col)


def end_card(c, t, nxt):
    e0, e1, _ = SEC["end"]
    if t > e0 - 0.2:
        big_title(c, [("下一课", 0.6), ("{w|" + nxt + "}", 1.15)], t, e0 + 0.1, DUR + 1, y=720, size=110)
        stroke_text(c, ep.SERIES, W / 2, 1080, 34, GOLD, window(t, e0 + 0.5, DUR + 1, 0.3), spacing=0.2, stroke=6)


def sec_window(name, j=None, fade=0.3, lead=0.0):
    """第 name 段（或段内第 j 句到下一句之前）的显示窗口 (t0, t1)。"""
    a0, a1, ss = SEC[name]
    if j is None:
        return a0, a1
    s0 = ss[j][1] - lead
    s1 = ss[j + 1][1] - 0.1 if j + 1 < len(ss) else a1
    return s0, s1


def edge_diagram(c, t, a, slope, edge, side="heel", y=1030, title=None, stop_at=None):
    """推坡原理图：坡面、水平线、板的横截面（立刃角相对坡面）。
    edge > slope：板面翻过水平，刃卡进雪 → 停；0 < edge < slope：还在往下溜 → 滑；edge < 0：下坡那边的刃碰雪 → 摔。"""
    if a <= 0:
        return
    x, w, h = 90, 900, 400
    card(c, x, y, w, h, a, ICE)
    stroke_text(c, title or ("后刃推坡：横截面" if side == "heel" else "前刃推坡：横截面"), x + 36, y + 56, 30, ICE, a, align="l", stroke=0)
    # 坡面：左高右低（右边是下坡）；后刃推坡时人面朝下坡，后刃在左（上坡一侧）
    ex, ey = x + 330, y + 250                       # 上坡一侧的刃（支点）
    sa = math.radians(slope)
    c.set_source_rgba(*SNOW_C, 0.95 * a)
    c.new_path(); c.move_to(x + 30, ey - math.tan(sa) * (ex - x - 30)); c.line_to(x + w - 30, ey + math.tan(sa) * (x + w - 30 - ex))
    c.line_to(x + w - 30, y + h - 20); c.line_to(x + 30, y + h - 20); c.close_path(); c.fill()
    # 水平线
    c.set_source_rgba(1, 1, 1, 0.5 * a); c.set_dash([8, 8]); c.set_line_width(2)
    c.move_to(ex - 220, ey); c.line_to(ex + 470, ey); c.stroke(); c.set_dash([])
    stroke_text(c, "水平", ex - 220, ey - 10, 22, DIM, a, bold=False, align="l", stroke=0)
    stroke_text(c, f"坡度 {slope:.0f}°", x + w - 50, ey + math.tan(sa) * (x + w - 50 - ex) + 50, 24, (0.25, 0.3, 0.4), a, bold=False, align="r", stroke=0)
    # 板：从支点往下坡方向伸出，角度 = 坡度 - 立刃角（相对水平，往下为正）
    L = 380
    ang = min(sa - math.radians(edge), sa + 0.04)          # 立刃为负时板“插进”坡里，画的时候贴着坡面
    bx, by = ex + L * math.cos(ang), ey + L * math.sin(ang)
    if edge > slope + 0.5:
        col, lab = GREEN, "板面翻过水平，刃卡住 → 停"
    elif edge > 0.5:
        col, lab = GOLD, "板面还朝下坡，往下溜 → 滑"
    else:
        col, lab = RED, ("前刃碰雪 → 往前摔" if side == "heel" else "后刃碰雪 → 往后摔")
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_source_rgba(0.08, 0.1, 0.16, a); c.set_line_width(34); c.move_to(ex, ey); c.line_to(bx, by); c.stroke()
    c.set_source_rgba(*col, a); c.set_line_width(24); c.move_to(ex, ey); c.line_to(bx, by); c.stroke()
    c.set_line_cap(cairo.LINE_CAP_BUTT)
    # 角度弧：坡面 → 板
    r = 140
    c.set_source_rgba(*col, 0.9 * a); c.set_line_width(4); c.new_path()
    a0, a1 = sorted((sa, ang)); c.arc(ex, ey, r, a0, a1); c.stroke()
    stroke_text(c, f"立刃 {edge:.0f}°", ex + L + 30, by + 10, 30, col, a, align="l", stroke=5)
    stroke_text(c, "上坡刃（" + ("后刃" if side == "heel" else "前刃") + "）", ex - 20, ey + 46, 24, INK, a, bold=False, align="r", stroke=4)
    stroke_text(c, lab, x + w / 2, y + h - 36, 34, col, a, stroke=6)


SNOW_C = (0.86, 0.90, 0.97)


def dim(c, a, k=0.55):
    """讲原理、看图表的时候把后面的画面压暗。"""
    if a > 0:
        c.set_source_rgba(0.02, 0.04, 0.09, k * a); c.rectangle(0, 0, W, H); c.fill()


def bars(c, t, a, title, items, vmax, y=1020, h=420, unit="", edge=GOLD, foot=None):
    """柱状图：items = [(标签, 数值, 颜色, 出现时刻, 小注)]"""
    if a <= 0:
        return
    x, w = 90, 900
    card(c, x, y, w, h, a, edge)
    stroke_text(c, title, x + 36, y + 56, 30, edge, a, align="l", stroke=0)
    n = len(items); base = y + h - 100; top = y + 110; sc = (base - top) / vmax
    bw = min(170, (w - 160) / n - 50); gap = (w - 120 - n * bw) / max(1, n - 1) if n > 1 else 0
    for i, (lab, v, col, t0, sub) in enumerate(items):
        k = ease((t - t0) / 0.7)
        bx = x + 60 + i * (bw + gap)
        c.set_source_rgba(1, 1, 1, 0.08 * a); rrect(c, bx, top, bw, base - top, 12); c.fill()
        if k > 0:
            hh = max(4, v * sc * k)
            c.set_source_rgba(*col, 0.95 * a); rrect(c, bx, base - hh, bw, hh, 12); c.fill()
            stroke_text(c, f"{v * k:.0f}{unit}" if k > 0.95 else f"{v * k:.0f}", bx + bw / 2, base - hh - 16, 38, col, a, stroke=6)
        stroke_text(c, lab, bx + bw / 2, base + 40, 30, INK, a, stroke=0)
        if sub:
            stroke_text(c, sub, bx + bw / 2, base + 76, 24, DIM, a * clamp(k * 3), bold=False, stroke=0)
    if foot:
        stroke_text(c, foot, x + 36, y + h + 40, 24, DIM, a, bold=False, align="l", stroke=4)


# ------------------------------------------------------------------ 每帧叠加
def overlay(c, t, i, pts):
    kind, shot, p = PLAN[i]
    if hasattr(ep, "overlay"):
        shade(c, 0.5, 0.65) if kind == "F" else shade(c, 0.35, 0.45)
        header(c, t)
        if kind == "R":
            mode_tag(c)
        ep.overlay(c, t, PLAN[i], pts, sys.modules[__name__])
        if kind == "F":
            stroke_text(c, f"实拍：Mixkit #{ep.FOOT[shot][0]}", W - 50, H - 70, 20, DIM, 0.75, bold=False, align="r", stroke=4)
        for s, a0, a1 in SUBS:
            if a0 - 0.2 < t < a1 + 0.2:
                subtitle(c, s, t, a0, a1, y=1580, size=60)
        return
    if kind == "F":
        shade(c, 0.5, 0.65)
    else:
        shade(c, 0.35, 0.45)
    header(c, t)
    if kind == "R":
        mode_tag(c)
    h0, h1, hs = SEC["hook"]
    if t < h1 + 0.2:
        big_title(c, [("单板{w|第1课}", 0.8), ("基本站姿", 1.25)], t, 0.15, h1 + 0.1, y=560, size=110)
        if t > hs[1][1]:
            stamp(c, "站不对 = 一直摔", W / 2, 1180, t, hs[1][1] + 0.1, RED)
    s0, s1, ss = SEC["setup"]
    if s0 - 0.2 < t < s1 + 0.2:
        stance_card(c, t, window(t, s0 + 0.2, s1, 0.4), ss[1][1] + 0.2)
        if pts and "footL" in pts:
            a = window(t, ss[0][1] + 0.2, s1, 0.3)
            for q in ("footL", "footR"):
                ring(c, *pts[q], 46, GOLD, a, t)
            c.set_source_rgba(*INK, a); c.set_line_width(4); c.set_dash([10, 8])
            c.move_to(*pts["footL"]); c.line_to(*pts["footR"]); c.stroke(); c.set_dash([])
    k0, k1, ks = SEC["keys"]
    if k0 - 0.2 < t < k1 + 0.2:
        cur = max([j for j, s in enumerate(ks) if t >= s[1] - 0.2] or [0])
        chips(c, ["①屈膝", "②重心", "③上身", "④视线"], cur, t, window(t, k0 + 0.1, k1, 0.3), y=300)
        if pts:
            a = window(t, ks[0][1] + 0.3, ks[1][1] - 0.1, 0.3)
            for q in ("kneeL", "kneeR"):
                ring(c, *pts[q], 44, GOLD, a, t)
            for sd in ("L", "R"):
                if "foot" + sd in pts:
                    kx, ky = pts["knee" + sd]; fx, fy = pts["foot" + sd]
                    arrow(c, kx, ky + 50, fx + (kx - fx) * 0.2, fy - 40, GOLD, a, 7)
            weight_bar(c, t, window(t, ks[1][1] + 0.1, ks[2][1] - 0.1, 0.3), 0.5 + 0.05 * ramp(t, ks[1][1] + 1.2, ks[1][1] + 2.0))
            a = window(t, ks[2][1] + 0.3, ks[3][1] - 0.1, 0.3)
            if a > 0:
                px, py = pts["pelvis"]; hx, hy = pts["head"]
                c.set_source_rgba(*GREEN, a); c.set_line_width(6); c.set_dash([14, 10])
                c.move_to(px, py + 40); c.line_to(px + (hx - px) * 1.25, py + (hy - py) * 1.25); c.stroke(); c.set_dash([])
                for q in ("handL", "handR"):
                    ring(c, *pts[q], 34, GREEN, a, t, pulse=False)
                tag(c, "上身直立 · 手臂张开", GREEN, 260, 1340, a, 36, "v")
            a = window(t, ks[3][1] + 0.3, k1, 0.3)
            if a > 0:
                hx, hy = pts["head"]; nx, ny = pts["nose"]
                dx, dy = nx - pts["board"][0], ny - pts["board"][1]
                L = math.hypot(dx, dy) or 1
                arrow(c, hx + 40 * dx / L, hy + 60, hx + 330 * dx / L, hy + 60 + 60 * dy / L, ICE, a, 8)
                stroke_text(c, "看前进方向", hx + 230 * dx / L, hy + 150, 38, ICE, a)
                tag(c, "别盯着脚下", RED, 330, 1340, a * ramp(t, ks[3][1] + 1.0, ks[3][1] + 1.3), 36, "x")
    w0, w1, ws = SEC["why"]
    if w0 - 0.2 < t < w1 + 0.2:
        if t < ws[1][1]:
            big_title(c, [("腿 = {b|减震器}", 1.0)], t, w0 + 0.2, ws[1][1] - 0.1, y=640, size=104)
        else:
            impact_chart(c, t, window(t, ws[1][1] - 0.1, w1, 0.3), ws[1][1] + 0.8, ws[2][1] + 0.5)
            note(c, "示意 · 简化模型：冲击 ≈ 体重 ×（1 + 坎高 / 缓冲距离）", window(t, ws[1][1], w1, 0.3), y=1460 - 30)
    m0, m1, ms = SEC["mistakes"]
    if m0 - 0.2 < t < m1 + 0.2:
        labs = ["直腿站", "撅屁股", "低头看板"]
        for j, s in enumerate(ms):
            e = ms[j + 1][1] - 0.1 if j + 1 < len(ms) else m1
            a = window(t, s[1], e, 0.25)
            if a > 0:
                tag(c, f"错误{j + 1}：{labs[j]}", RED, 60, 330, a, 44, "x")
                if pts:
                    q = ("kneeL", "pelvis", "head")[j]
                    if j == 0:
                        for qq in ("kneeL", "kneeR"):
                            ring(c, *pts[qq], 44, RED, a, t)
                    else:
                        ring(c, *pts[q], 64, RED, a, t)
        a = window(t, m1 - 0.9, m1 + 0.3, 0.3)
        tag(c, "回到正确站姿", GREEN, 60, 330, a, 44, "v")
    d0, d1, ds = SEC["drill"]
    if d0 - 0.2 < t < d1 + 0.2:
        if t < ds[1][1]:
            a = window(t, d0 + 0.2, ds[1][1] - 0.1, 0.3)
            tag(c, "蹲起 ×10", GOLD, 120, 1340, a, 44)
            tag(c, "小跳 ×5", ICE, 600, 1340, a * ramp(t, d0 + 3.6, d0 + 3.9), 44)
        else:
            stamp(c, "过关", W / 2, 760, t, ds[1][1] + 0.2, GREEN, window(t, ds[1][1], d1, 0.3))
            a = window(t, ds[1][1] + 0.3, d1, 0.3)
            for j, s in enumerate(("落地不晃", "膝盖始终弯着")):
                tag(c, s, GREEN, 160 + j * 380, 1180, a * ramp(t, ds[1][1] + 0.5 + 0.4 * j, ds[1][1] + 0.8 + 0.4 * j), 40, "v")
    e0, e1, _ = SEC["end"]
    if t > e0 - 0.2:
        big_title(c, [("下一课", 0.6), ("{w|单脚蹬行}", 1.15)], t, e0 + 0.1, DUR + 1, y=720, size=110)
        stroke_text(c, ep.SERIES, W / 2, 1080, 34, GOLD, window(t, e0 + 0.5, DUR + 1, 0.3), spacing=0.2, stroke=6)
    # 实拍来源角标
    if kind == "F":
        stroke_text(c, f"实拍：Mixkit #{ep.FOOT[shot][0]}", W - 50, H - 70, 20, DIM, 0.75, bold=False, align="r", stroke=4)
    for s, a0, a1 in SUBS:
        if a0 - 0.2 < t < a1 + 0.2:
            subtitle(c, s, t, a0, a1, y=1580, size=60)


def frame(i):
    t = i / FPS
    s, buf, pts = base_frame(i)
    c = cairo.Context(s)
    overlay(c, t, i, pts)
    return s, buf


if __name__ == "__main__":
    if A.still:
        for ts in A.still.split(","):
            i = min(len(PLAN) - 1, int(float(ts) * FPS))
            s, _ = frame(i)
            s.write_to_png(f"{A.out}_{MODE}_{float(ts):05.1f}.png")
        sys.exit()
    wr = Writer(A.out, crf=18)
    for i in range(len(PLAN)):
        s, _ = frame(i)
        wr.write(s)
        if i % 150 == 0:
            print(i, len(PLAN), flush=True)
    wr.close()
    print("ok", A.out)
