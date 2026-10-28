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
T_CATCH = next(i for i, (s, _, p) in enumerate(PLAN) if p >= ep.W_CATCH) / FPS
ARC = (10, 25, 40, 55, 70, 90, 105, 120, 135, 150, 165, 175)


def zoom_fn(t, m, shot, p):
    if t < h1:
        k = ramp(t, T_CATCH - 0.1, T_CATCH + 0.15)
        sh = math.exp(-((t - T_CATCH - 0.1) / 0.12) ** 2)          # 卡刃那一下轻微震动
        return 1 + 0.14 * k, (m["board"][0] + 0.01 * sh * math.sin(t * 90), m["board"][1])
    return 1.0, (0.5, 0.5)


def edge_name(broll):
    if broll > 3:
        return "后刃", ICE
    if broll < -3:
        return "前刃", GOLD
    return "平板", RED


def path(c, P, a, upto=999):
    """俯视图上的弯：后刃一段蓝、前刃一段金，平板点红。"""
    if a <= 0 or "a10" not in P:
        return
    pts = [(ang, P[f"a{ang}"]) for ang in ARC if ang <= upto]
    for seg, col in (([q for q in pts if q[0] <= 90], ICE), ([q for q in pts if q[0] >= 90], GOLD)):
        if len(seg) < 2:
            continue
        c.new_path(); c.move_to(*seg[0][1])
        for _, q in seg[1:]:
            c.line_to(*q)
        c.set_source_rgba(0.02, 0.03, 0.06, 0.5 * a); c.set_line_width(16); c.stroke_preserve()
        c.set_source_rgba(*col, a); c.set_line_width(9); c.stroke()
    lab = [(40, "后刃", ICE), (150, "前刃", GOLD)]
    for ang, txt, col in lab:
        if ang <= upto:
            x, y = P[f"a{ang}"]
            stroke_text(c, txt, x + 40, y, 44, col, a, align="l")


def draw(c, t, P, m, shot, p):
    pose = m.get("_pose", {})
    broll = pose.get("broll", 0.0)
    if t < h1 + 0.3:
        a = window(t, -1, h1, 0.3)
        tag(c, "错误示范", RED, 60, 330, a, icon="x")
        big_title(c, [("第一次换刃", 0.86), ("为啥{r|一换就摔}？", 1.05)], t, 0.1, h1, y=560, size=100)
        ring(c, *P["chest"], 60, RED, a * window(t, 0.8, T_CATCH - 0.1, 0.25), t, label="只拧上身")
        if t >= T_CATCH - 0.05:
            ring(c, *P["toe"], 60, RED, a * ramp(t, T_CATCH, T_CATCH + 0.15), t, label="下坡的刃卡住")
        fl = math.exp(-((t - T_CATCH) / 0.07) ** 2)
        if fl > 0.01:
            c.set_source_rgba(1, 1, 1, 0.55 * fl); c.paint()
    if w0 - 0.3 < t < w1 + 0.3:
        a = window(t, w0, w1, 0.3)
        tag(c, "原理 · 俯视", ICE, 60, 330, a)
        path(c, P, a, upto=max(10, min(175, pose.get("yaw", 10))))
        if 80 < pose.get("yaw", 0) < 100 or (ws[0][1] + 2.5 < t < ws[2][1] + 1.5):
            ring(c, *P["board"], 64, RED, a * window(t, ws[0][1] + 2.2, ws[2][1] + 1.5, 0.3), t, label="平板 · 正对山下")
        # ② 平板每拖 1 秒多 4 km/h
        a2 = a * window(t, ws[1][1] - 0.2, ws[1][2] + 0.2, 0.3)
        if a2 > 0:
            card(c, 60, 1060, W - 120, 330, a2, RED)
            stroke_text(c, f"坡 {ep.SLOPE:.0f}° · 平板正对山下", W / 2, 1120, 32, DIM, a2, stroke=0)
            for i, (sec, tt0) in enumerate(((1, ws[1][1] + 1.6), (3, ws[1][1] + 3.8))):
                k = ramp(t, tt0 - 0.6, tt0)
                x = 60 + (W - 120) * (0.27 + 0.46 * i)
                stroke_text(c, f"拖 {sec} 秒", x, 1190, 40, INK, a2 * ramp(t, tt0 - 0.8, tt0 - 0.5), stroke=0)
                p_ = pop(t, tt0, 0.35)
                c.save(); c.translate(x, 1290); s_ = max(p_, 1e-3); c.scale(s_, s_); c.translate(-x, -1290)
                stroke_text(c, f"+{ep.KMH_PER_S * sec * k:.0f}", x, 1320, 120, RED, a2 * (1 if t >= tt0 - 0.6 else 0), face=SERIF, stroke=0)
                c.restore()
                stroke_text(c, "公里/小时", x, 1370, 30, DIM, a2 * ramp(t, tt0, tt0 + 0.2), stroke=0)
        # ③ 果断
        a3 = a * window(t, ws[2][1], ws[2][2] + 0.1, 0.3)
        if a3 > 0:
            big_title(c, [("{w|果断}！", 1.3)], t, ws[2][1] + 0.1, ws[2][2], y=1250, size=110)
        # ④ 眼睛 → 肩 → 髋 → 板
        a4 = a * window(t, ws[3][1] - 0.1, w1 + 0.2, 0.3)
        if a4 > 0:
            card(c, 60, 1080, W - 120, 260, a4, GOLD)
            items = ["眼睛", "肩", "髋", "板"]
            for i, it in enumerate(items):
                x = 60 + (W - 120) * (0.13 + 0.25 * i)
                on = ramp(t, ws[3][1] + 0.5 + 0.6 * i, ws[3][1] + 0.8 + 0.6 * i)
                c.new_path(); c.arc(x, 1200, 70, 0, 2 * math.pi)
                c.set_source_rgba(*GOLD, a4 * (0.25 + 0.75 * on)); c.fill()
                stroke_text(c, it, x, 1218, 48, (0.05, 0.05, 0.08) if on > 0.5 else INK, a4, stroke=0)
                if i < 3:
                    arrow(c, x + 80, 1200, x + 165, 1200, GOLD, a4 * on, w=6)
            stroke_text(c, "身体先转，板跟着走", W / 2, 1310, 34, INK, a4, stroke=0)
    if s0 - 0.3 < t < s1 + 0.3:
        a = window(t, s0, s1, 0.3)
        tag(c, "正确做法", GREEN, 60, 330, a, icon="v")
        big_title(c, [("第一次换刃 · {w|4 步}", 1.0)], t, s0 + 0.05, ss[0][1] - 0.05, y=600, size=96)
        cur = step_of(t, ss)
        ac = a * ramp(t, ss[0][1] - 0.2, ss[0][1] + 0.2)
        chips(c, ["①落叶飘减速", "②看·转肩", "③换前刃", "④横过来停"], cur, t, ac)
        if ac > 0:      # 右上角：现在用的是哪条刃
            nm, col = edge_name(broll)
            card(c, W - 330, 545, 270, 150, ac, col)
            stroke_text(c, "现在", W - 195, 600, 28, DIM, ac, stroke=0)
            stroke_text(c, nm, W - 195, 668, 60, col, ac, stroke=0)
        if cur == 1:
            ring(c, *P["head"], 60, GOLD, a * ramp(t, ss[1][1] + 0.2, ss[1][1] + 0.5), t, label="先看要去的方向")
        elif cur == 2:
            kx, ky = mid(P, "kneeL", "kneeR")
            ring(c, kx, ky, 66, GOLD, a * ramp(t, ss[2][1] + 0.4, ss[2][1] + 0.7), t, label="膝盖往前顶")
    if d0 - 0.3 < t < d1 + 0.3:
        a = window(t, d0, d1, 0.3)
        tag(c, "怎么练", GOLD, 60, 330, a)
        card(c, 60, 440, W - 120, 200, a)
        stroke_text(c, "缓坡", W / 2, 515, 38, DIM, a, stroke=0)
        rich_line(c, spans("落叶飘 → 换前刃停 · 左右各 {w|5} 次"), W / 2, 600, 48, a)
        a2 = window(t, ds[1][1], d1, 0.3)
        if a2 > 0:
            card(c, 60, 670, W - 120, 150, a2, GREEN)
            stroke_text(c, "过关标准", 120, 755, 36, GREEN, a2, align="l", stroke=0)
            stroke_text(c, "平板 ≤ 1 秒 · 不卡刃", W - 120, 762, 46, INK, a2, align="r", stroke=0)
        a3 = window(t, ds[2][1], d1, 0.3)
        if a3 > 0:
            tag(c, "评论区见", ICE, 60, 850, a3 * pop(t, ds[2][1], 0.4), size=40)


run_episode(ep, FR, OUTF, draw, zoom_fn, next_lines=[("连起来", 0.9), ("就是{w|S弯}！", 1.15)])
