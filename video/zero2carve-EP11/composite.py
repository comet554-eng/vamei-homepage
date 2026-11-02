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


def edge_name(broll):
    if broll > 8:
        return "后刃", ICE
    if broll < -8:
        return "前刃", GOLD
    return "换刃", GREEN


def lean_card(c, y, a, t, t0):
    """同一个约 5 米的弯：速度越快，身体要倒得越多（tanφ = v²/gR）。"""
    if a <= 0:
        return
    card(c, 60, y, W - 120, 380, a, GOLD)
    stroke_text(c, "同一个 5 米的弯 · 身体要倒多少", W / 2, y + 52, 32, INK, a, stroke=0)
    for i, v in enumerate(ep.SPEEDS):
        ang = ep.LEAN[v]; tt = t0 + 1.6 + 1.8 * i; on = ramp(t, tt - 0.6, tt)
        yy = y + 95 + i * 82
        col = (ICE, GOLD, RED)[i]
        stroke_text(c, f"时速 {v}", 210, yy + 40, 36, INK, a, align="r", stroke=0)
        c.set_source_rgba(1, 1, 1, 0.08 * a); rrect(c, 235, yy + 6, W - 560, 46, 12); c.fill()
        c.set_source_rgba(*col, a); rrect(c, 235, yy + 6, max(18, (W - 560) * ang / 50 * on), 46, 12); c.fill()
        # 右边一个小人：按角度倒下去
        cx, cy = W - 190, yy + 52
        if on > 0.05:
            stroke_text(c, f"{ang * on:.0f}°", W - 245, yy + 44, 44, col, a, align="r", stroke=0)
        r_ = math.radians(ang * on)
        c.set_line_cap(1); c.set_source_rgba(*col, a); c.set_line_width(7)
        c.new_path(); c.move_to(cx, cy); c.line_to(cx + 52 * math.sin(r_), cy - 52 * math.cos(r_)); c.stroke()
        c.new_path(); c.arc(cx + 62 * math.sin(r_), cy - 62 * math.cos(r_), 9, 0, 2 * math.pi); c.fill()
        c.set_source_rgba(1, 1, 1, 0.35 * a); c.set_line_width(3)
        c.new_path(); c.move_to(cx - 40, cy + 2); c.line_to(cx + 40, cy + 2); c.stroke()
    stroke_text(c, "tanφ = v² / (gR) · 匀速圆周受力平衡 · 示意，忽略坡面分量", W / 2, y + 358, 22, DIM, a, bold=False, stroke=0)


def draw(c, t, P, m, shot, p):
    pose = m.get("_pose", {})
    broll = pose.get("broll", 0.0)
    if t < h1 + 0.3:
        a = window(t, -1, h1, 0.3)
        tag(c, "错误示范", RED, 60, 330, a, icon="x")
        big_title(c, [("刻滑一换刃", 0.86), ("为啥又变回{r|搓雪}？", 1.0)], t, 0.1, h1, y=560, size=100)
        if p > ep.W_MID - 0.4:
            ring(c, *P["chest"], 60, RED, a * ramp(p, ep.W_MID - 0.4, ep.W_MID - 0.1), t, label="一换刃就站直")
        if p > ep.W_MID + 0.6:
            ring(c, *P["tail"], 56, RED, a * ramp(p, ep.W_MID + 0.6, ep.W_MID + 0.9), t, label="板尾甩出去")
    if w0 - 0.3 < t < w1 + 0.3:
        a = window(t, w0, w1, 0.3)
        if shot == "S":
            tag(c, "原理", ICE, 60, 330, a)
            a0 = a * window(t, ws[0][1] + 0.6, ws[0][2] + 0.2, 0.3)
            if a0 > 0:
                ring(c, *P["chest"], 64, GOLD, a0, t, label="身体往弯里倒")
            lean_card(c, 1040, a * window(t, ws[1][1] - 0.2, ws[1][2] + 0.2, 0.3), t, ws[1][1])
            a2 = a * window(t, ws[2][1], ws[3][1], 0.3)
            if a2 > 0:
                nm, col = edge_name(broll)
                card(c, W - 330, 545, 270, 150, a2, col)
                stroke_text(c, "现在", W - 195, 600, 28, DIM, a2, stroke=0)
                stroke_text(c, nm, W - 195, 668, 60, col, a2, stroke=0)
                if abs(broll) < 8:
                    ring(c, *P["board"], 64, GREEN, a2, t, label="板平一下")
        elif shot == "TW":
            tag(c, "错误 · 俯视", RED, 60, 330, a, icon="x")
            ak = a * ramp(p, 1.6, 2.0)
            if ak > 0:
                tag(c, "一条线 ✓", GREEN, P["turnA"][0] - 120, P["turnA"][1] - 40, ak, size=40)
            ab = a * ramp(p, ep.W_MID + 2.0, ep.W_MID + 2.4)
            if ab > 0:
                tag(c, "一大片 ✗", RED, P["turnB"][0] - 60, P["turnB"][1] - 40, ab, size=40)
            big_title(c, [("一站直，板就{r|甩}", 1.0)], t, ws[3][1] + 2.5, ws[4][1] - 0.1, y=1560, size=86)
        else:
            tag(c, "正确 · 俯视", GREEN, 60, 330, a, icon="v")
            big_title(c, [("一条线{w|到底}", 1.0)], t, ws[4][1] + 2.5, w1, y=1560, size=86)
    if s0 - 0.3 < t < s1 + 0.3:
        a = window(t, s0, s1, 0.3)
        tag(c, "正确做法", GREEN, 60, 330, a, icon="v")
        big_title(c, [("刻滑换刃 · {w|4 步}", 1.0)], t, s0 + 0.05, ss[0][1] - 0.05, y=600, size=96)
        cur = step_of(t, ss)
        ac = a * ramp(t, ss[0][1] - 0.2, ss[0][1] + 0.2)
        chips(c, ["①弯尾屈膝", "②身体过板", "③压前刃", "④立高刃"], cur, t, ac)
        if ac > 0:
            nm, col = edge_name(broll)
            card(c, W - 360, 545, 300, 170, ac, col)
            stroke_text(c, nm, W - 210, 612, 52, col, ac, stroke=0)
            stroke_text(c, f"立刃 {abs(broll):.0f}°" if abs(broll) >= 8 else "板平 · 别站直", W - 210, 675, 32, INK, ac, stroke=0)
        if cur == 0:
            kx, ky = mid(P, "kneeL", "kneeR")
            ring(c, kx, ky, 64, GOLD, a * ramp(t, ss[0][1] + 0.5, ss[0][1] + 0.8), t, label="膝盖别伸直")
        elif cur == 1:
            ring(c, *P["chest"], 64, GOLD, a * ramp(t, ss[1][1] + 0.3, ss[1][1] + 0.6), t, label="身体先过去")
        elif cur == 2:
            kx, ky = mid(P, "kneeL", "kneeR")
            ring(c, kx, ky, 64, GOLD, a * ramp(t, ss[2][1] + 0.3, ss[2][1] + 0.6), t, label="膝盖顶前刃")
    if d0 - 0.3 < t < d1 + 0.3:
        a = window(t, d0, d1, 0.3)
        tag(c, "怎么练", GOLD, 60, 330, a)
        card(c, 60, 440, W - 120, 200, a)
        stroke_text(c, "缓坡 · 连续刻滑 S 弯", W / 2, 515, 38, DIM, a, stroke=0)
        rich_line(c, spans("每个弯都{w|回头看雪痕}"), W / 2, 600, 48, a)
        a2 = window(t, ds[1][1], d1, 0.3)
        if a2 > 0:
            card(c, 60, 670, W - 120, 150, a2, GREEN)
            stroke_text(c, "过关标准", 120, 755, 36, GREEN, a2, align="l", stroke=0)
            stroke_text(c, "换刃处 · 不断 · 不变宽", W - 120, 762, 44, INK, a2, align="r", stroke=0)
        a3 = window(t, ds[2][1], d1, 0.3)
        if a3 > 0:
            tag(c, "评论区报个数", ICE, 60, 850, a3 * pop(t, ds[2][1], 0.4), size=40)


run_episode(ep, FR, OUTF, draw, zoom_fn, next_lines=[("刃再立高", 0.9), ("{w|手能摸雪}！", 1.15)])
