"""叠字幕、原理图和数据，出竖屏无声成片（音乐和音效由 ../zero2carve-lib/finish.py 配）：
python3 composite.py FRAMEDIR OUT.mp4（STILLS="t1 t2" 时只出静帧调版）"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "zero2carve-lib"))
import ep
from vert import *

FR, OUTF = sys.argv[1], sys.argv[2]
PLAN = ep.plan()
h0, h1, hs = ep.SEC["hook"]; w0, w1, ws = ep.SEC["why"]; s0, s1, ss = ep.SEC["steps"]; d0, d1, ds = ep.SEC["drill"]


def zoom_fn(t, m, shot, p):
    return 1.0, (0.5, 0.5)


def sidecut_card(c, y, a, t, t0):
    """板的俯视轮廓：两条边是弧，延长成一个半径约 7 米的大圆。"""
    if a <= 0:
        return
    card(c, 60, y, W - 120, 340, a, ICE)
    cx, cy = W / 2, y + 120
    L, wt, wm = 780, 130, 80                    # 画面上板长、板头宽、腰宽（夸大了侧切）
    k = ramp(t, t0, t0 + 0.8)
    c.new_path()
    n = 60
    pts_top = [(cx - L / 2 + L * i / n, cy - (wm / 2 + (wt - wm) / 2 * ((2 * i / n - 1) ** 2))) for i in range(n + 1)]
    pts_bot = [(x, 2 * cy - y_) for x, y_ in reversed(pts_top)]
    c.move_to(*pts_top[0])
    for q in pts_top[1:] + pts_bot:
        c.line_to(*q)
    c.close_path(); c.set_source_rgba(0.25, 0.55, 0.95, a); c.fill()
    for sx in (-1, 1):                            # 板头板尾的圆头
        c.save(); c.translate(cx + sx * L / 2, cy); c.scale(0.55, 1.0)
        c.new_path(); c.arc(0, 0, wt / 2, -math.pi / 2 if sx > 0 else math.pi / 2, math.pi / 2 if sx > 0 else 1.5 * math.pi)
        c.restore(); c.set_source_rgba(0.25, 0.55, 0.95, a); c.fill()
    # 下边的侧切弧延长成大圆的一段（虚线）
    sag = (wt - wm) / 2; R_px = (L / 2) ** 2 / (2 * sag)
    ccx, ccy = cx, cy + wm / 2 + R_px
    c.set_dash([10, 8]); c.new_path()
    span = math.asin(min(1, (L / 2 + 140 * k) / R_px))
    c.arc(ccx, ccy, R_px, -math.pi / 2 - span, -math.pi / 2 + span)
    c.set_source_rgba(*GOLD, a); c.set_line_width(4); c.stroke(); c.set_dash([])
    arrow(c, cx, cy + wm / 2 + 8, cx, cy + wm / 2 + 110, GOLD, a * k, w=5)
    stroke_text(c, "侧切半径 ≈ 7 米", cx + 24, cy + wm / 2 + 90, 40, GOLD, a * k, align="l")
    stroke_text(c, "（板的两条边是一段大圆弧）", W / 2, y + 315, 26, DIM, a, bold=False, stroke=0)


def radius_card(c, y, a, t, t0):
    if a <= 0:
        return
    card(c, 60, y, W - 120, 360, a, GOLD)
    stroke_text(c, "刻滑弯半径 ≈ 7 米 × cos(立刃角)", W / 2, y + 52, 32, INK, a, stroke=0)
    for i, e in enumerate(ep.EDGES):
        r = ep.RADIUS[e]; tt = t0 + 1.6 + 1.8 * i; on = ramp(t, tt - 0.6, tt)
        yy = y + 95 + i * 80
        col = (ICE, GOLD, RED)[i]
        stroke_text(c, f"立 {e}°", 170, yy + 40, 38, INK, a, align="r", stroke=0)
        c.set_source_rgba(1, 1, 1, 0.08 * a); rrect(c, 200, yy + 6, W - 440, 46, 12); c.fill()
        c.set_source_rgba(*col, a); rrect(c, 200, yy + 6, max(18, (W - 440) * r / 7.0 * on), 46, 12); c.fill()
        if on > 0.05:
            stroke_text(c, f"{r * on:.1f} 米", W - 100, yy + 44, 44, col, a, align="r", stroke=0)
    stroke_text(c, "Jentschura & Fahrbach · Can J Phys 2004 · 理想刻滑、侧切取 7 米", W / 2, y + 340, 22, DIM, a, bold=False, stroke=0)


def draw(c, t, P, m, shot, p):
    pose = m.get("_pose", {})
    broll = pose.get("broll", 0.0)
    if t < h1 + 0.3:
        a = window(t, -1, h1, 0.3)
        tag(c, "搓雪弯", RED, 60, 330, a)
        big_title(c, [("同样是转弯", 0.86), ("雪痕为啥{r|一大片}？", 1.0)], t, 0.1, h1, y=560, size=100)
        ring(c, *P["tail"], 56, RED, a * ramp(t, 1.5, 1.9), t, label="板尾往外甩")
    if w0 - 0.3 < t < w1 + 0.3:
        a = window(t, w0, w1, 0.3)
        if shot == "TK":
            tag(c, "搓雪 · 俯视", RED, 60, 330, a, icon="x")
            big_title(c, [("雪痕{r|一大片}", 1.0)], t, ws[0][1] + 2.0, ws[1][1] - 0.1, y=1380, size=90)
        else:
            tag(c, "刻滑 · 俯视", GREEN, 60, 330, a, icon="v")
            big_title(c, [("雪痕{w|一条线}", 1.0)], t, ws[1][1] + 2.0, ws[2][1] - 0.1, y=1380, size=90)
        sidecut_card(c, 1040, a * window(t, ws[2][1] - 0.2, ws[2][2] + 0.2, 0.3), t, ws[2][1] + 0.3)
        radius_card(c, 1040, a * window(t, ws[3][1] - 0.2, ws[3][2] + 0.2, 0.3), t, ws[3][1])
        a4 = a * window(t, ws[4][1], w1 + 0.2, 0.3)
        if a4 > 0:
            big_title(c, [("刃{w|立得高}", 1.0), ("板{w|不甩}", 1.0)], t, ws[4][1] + 0.1, w1, y=1150, size=100)
    if s0 - 0.3 < t < s1 + 0.3:
        a = window(t, s0, s1, 0.3)
        tag(c, "刻滑入门", GREEN, 60, 330, a, icon="v")
        big_title(c, [("刻滑入门 · {w|4 步}", 1.0)], t, s0 + 0.05, ss[0][1] - 0.05, y=600, size=96)
        cur = step_of(t, ss)
        ac = a * ramp(t, ss[0][1] - 0.2, ss[0][1] + 0.2)
        chips(c, ["①后刃横切", "②立高刃", "③不甩板尾", "④看雪痕"], cur, t, ac)
        if ac > 0:
            e = abs(broll)
            card(c, W - 360, 545, 300, 170, ac, GOLD)
            stroke_text(c, f"立刃 {e:.0f}°", W - 210, 615, 48, GOLD, ac, stroke=0)
            if e > 20:
                stroke_text(c, f"弯半径 ≈ {ep.RSC * math.cos(math.radians(e)):.1f} 米", W - 210, 675, 32, INK, ac, stroke=0)
            else:
                stroke_text(c, "换刃中", W - 210, 675, 32, DIM, ac, stroke=0)
        if cur == 1:
            kx, ky = mid(P, "kneeL", "kneeR")
            ring(c, kx, ky, 64, GOLD, a * ramp(t, ss[1][1] + 0.3, ss[1][1] + 0.6), t, label="膝髋往弯里倒")
        elif cur == 2:
            ring(c, *P["tail"], 56, GREEN, a * ramp(t, ss[2][1] + 0.3, ss[2][1] + 0.6), t, label="板尾不甩")
    if d0 - 0.3 < t < d1 + 0.3:
        a = window(t, d0, d1, 0.3)
        tag(c, "怎么练", GOLD, 60, 330, a)
        card(c, 60, 440, W - 120, 200, a)
        stroke_text(c, "缓坡 · 只做后刃", W / 2, 515, 38, DIM, a, stroke=0)
        rich_line(c, spans("横切 · 立高刃 · {w|回头看雪痕}"), W / 2, 600, 48, a)
        a2 = window(t, ds[1][1], d1, 0.3)
        if a2 > 0:
            card(c, 60, 670, W - 120, 150, a2, GREEN)
            stroke_text(c, "过关标准", 120, 755, 36, GREEN, a2, align="l", stroke=0)
            stroke_text(c, "雪痕 ≤ 一个板宽", W - 120, 762, 48, INK, a2, align="r", stroke=0)
        a3 = window(t, ds[2][1], d1, 0.3)
        if a3 > 0:
            tag(c, "评论区晒雪痕", ICE, 60, 850, a3 * pop(t, ds[2][1], 0.4), size=40)


run_episode(ep, FR, OUTF, draw, zoom_fn, next_lines=[("刻滑换刃", 0.9), ("{w|连起来}！", 1.15)])
