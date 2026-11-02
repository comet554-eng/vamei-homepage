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
T_SIT = next(i for i, (s, _, p) in enumerate(PLAN) if p >= ep.W_SIT) / FPS


def zoom_fn(t, m, shot, p):
    if t < h1:
        k = ramp(t, T_SIT, T_SIT + 0.5)
        sh = math.exp(-((t - T_SIT - 0.5) / 0.12) ** 2)
        return 1 + 0.12 * k, (m["board"][0] + 0.01 * sh * math.sin(t * 90), m["board"][1])
    return 1.0, (0.5, 0.5)


def edge_name(broll):
    if broll > 3:
        return "后刃", ICE
    if broll < -3:
        return "前刃", GOLD
    return "平板", RED


def s_path(c, P, a, prog):
    """俯视：整条 S。弯 A（前→后）和弯 B（后→前），前刃段金、后刃段蓝；prog 0..1 画到哪。"""
    if a <= 0 or "A180" not in P:
        return
    seq = [("A", x) for x in ep.ARC_A] + [("B", x) for x in ep.ARC_B]
    n = max(2, int(round(prog * len(seq))))
    pts = [(k, ang, P[f"{k}{ang}"]) for k, ang in seq[:n]]
    for (k0, a0, p0), (k1, a1, p1) in zip(pts, pts[1:]):
        toe = (k1 == "A" and a1 >= 90) or (k1 == "B" and a1 > 90)
        col = GOLD if toe else ICE
        c.new_path(); c.move_to(*p0); c.line_to(*p1)
        c.set_source_rgba(0.02, 0.03, 0.06, 0.5 * a); c.set_line_width(16); c.stroke()
        c.new_path(); c.move_to(*p0); c.line_to(*p1); c.set_source_rgba(*col, a); c.set_line_width(9); c.stroke()


def draw(c, t, P, m, shot, p):
    pose = m.get("_pose", {})
    broll = pose.get("broll", 0.0)
    if t < h1 + 0.3:
        a = window(t, -1, h1, 0.3)
        tag(c, "错误示范", RED, 60, 330, a, icon="x")
        big_title(c, [("S弯", 0.86), ("总在{r|换后刃}时摔？", 1.0)], t, 0.1, h1, y=560, size=100)
        ring(c, *P["pelvis"], 70, RED, a * ramp(t, T_SIT - 0.5, T_SIT - 0.2), t, label="往后坐")
        fl = math.exp(-((t - T_SIT - 0.5) / 0.07) ** 2)
        if fl > 0.01:
            c.set_source_rgba(1, 1, 1, 0.55 * fl); c.paint()
    if w0 - 0.3 < t < w1 + 0.3:
        a = window(t, w0, w1, 0.3)
        tag(c, "原理 · 俯视", ICE, 60, 330, a)
        s_path(c, P, a, clamp(p / ep.S_END * 1.02))
        a0 = a * window(t, ws[0][1], ws[0][2] + 0.2, 0.3)
        if a0 > 0 and "A90" in P:
            stroke_text(c, "前刃", P["A150"][0] + 50, P["A150"][1], 40, GOLD, a0, align="l")
            stroke_text(c, "后刃", P["A30"][0] + 50, P["A30"][1], 40, ICE, a0, align="l")
        # ② ③ 弯尾 β 和 cos β
        a2 = a * window(t, ws[1][1], ws[2][2] + 0.2, 0.3)
        if a2 > 0:
            card(c, 60, 1040, W - 120, 380, a2, ICE)
            stroke_text(c, "弯尾板头离开下坡线 β · 下滑力顺着板的份额 = cos β", W / 2, 1095, 28, DIM, a2, bold=False, stroke=0)
            for i, b in enumerate(ep.BETAS):
                yy = 1140 + i * 88
                tt0 = ws[2][1] + 1.0 + 2.0 * i
                on = ramp(t, tt0 - 0.5, tt0)
                v = ep.SHARE[b]
                col = GREEN if b == 90 else (GOLD if b == 60 else RED)
                lab = {90: "横过来 90°", 60: "转到 60°", 30: "只转 30°"}[b]
                stroke_text(c, lab, 110, yy + 44, 36, INK, a2, align="l", stroke=0)
                c.set_source_rgba(1, 1, 1, 0.08 * a2); rrect(c, 360, yy + 12, W - 560, 42, 12); c.fill()
                c.set_source_rgba(*col, a2); rrect(c, 360, yy + 12, max(16, (W - 560) * v * on), 42, 12); c.fill()
                if on > 0.05:
                    s_ = max(pop(t, tt0, 0.3), 1e-3)
                    c.save(); c.translate(W - 110, yy + 40); c.scale(s_, s_); c.translate(-(W - 110), -(yy + 40))
                    stroke_text(c, f"{v * 100 * on:.0f}%", W - 110, yy + 50, 48, col, a2, align="r", stroke=0)
                    c.restore()
        a3 = a * window(t, ws[3][1], ws[3][2] + 0.1, 0.3)
        if a3 > 0:
            big_title(c, [("弯要{w|走完}！", 1.2)], t, ws[3][1] + 0.1, ws[3][2], y=1250, size=110)
        a4 = a * window(t, ws[4][1], w1 + 0.2, 0.3)
        if a4 > 0:
            card(c, 60, 1080, W - 120, 280, a4, RED)
            tag(c, "往后坐", RED, 110, 1120, a4, size=44, icon="x")
            tag(c, "手往前 · 重心在板中间", GREEN, 110, 1240, a4 * ramp(t, ws[4][1] + 1.5, ws[4][1] + 1.9), size=44, icon="v")
    if s0 - 0.3 < t < s1 + 0.3:
        a = window(t, s0, s1, 0.3)
        tag(c, "正确做法", GREEN, 60, 330, a, icon="v")
        big_title(c, [("前刃换后刃 · {w|4 步}", 1.0)], t, s0 + 0.05, ss[0][1] - 0.05, y=600, size=96)
        cur = step_of(t, ss)
        ac = a * ramp(t, ss[0][1] - 0.2, ss[0][1] + 0.2)
        chips(c, ["①看下一个弯", "②手往前", "③换后刃", "④接前刃弯"], cur, t, ac)
        if ac > 0:
            nm, col = edge_name(broll)
            card(c, W - 330, 545, 270, 150, ac, col)
            stroke_text(c, "现在", W - 195, 600, 28, DIM, ac, stroke=0)
            stroke_text(c, nm, W - 195, 668, 60, col, ac, stroke=0)
        if cur == 0:
            ring(c, *P["head"], 60, GOLD, a * ramp(t, ss[0][1] + 0.3, ss[0][1] + 0.6), t, label="看下一个方向")
        elif cur == 1:
            hx, hy = mid(P, "handL", "handR")
            ring(c, hx, hy, 70, GOLD, a * ramp(t, ss[1][1] + 0.3, ss[1][1] + 0.6), t, label="手往前")
    if d0 - 0.3 < t < d1 + 0.3:
        a = window(t, d0, d1, 0.3)
        tag(c, "怎么练", GOLD, 60, 330, a)
        card(c, 60, 440, W - 120, 200, a)
        stroke_text(c, "缓坡", W / 2, 515, 38, DIM, a, stroke=0)
        rich_line(c, spans("连续 S 弯 {w|6} 个 · 每个走到{w|横过来}"), W / 2, 600, 46, a)
        a2 = window(t, ds[1][1], d1, 0.3)
        if a2 > 0:
            card(c, 60, 670, W - 120, 150, a2, GREEN)
            stroke_text(c, "过关标准", 120, 755, 36, GREEN, a2, align="l", stroke=0)
            stroke_text(c, "不加速 · 不坐下", W - 120, 762, 50, INK, a2, align="r", stroke=0)
        a3 = window(t, ds[2][1], d1, 0.3)
        if a3 > 0:
            tag(c, "评论区报数", ICE, 60, 850, a3 * pop(t, ds[2][1], 0.4), size=40)


run_episode(ep, FR, OUTF, draw, zoom_fn, next_lines=[("中级道", 0.9), ("{w|陡了}怎么办？", 1.1)])
