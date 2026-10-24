"""叠字幕和标注，出竖屏成片：python3 composite.py FRAMEDIR OUT.mp4 [t0 t1]"""
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "zero2carve-lib"))
import cairo
import ep
from vert import *

FR, OUTF = sys.argv[1], sys.argv[2]
T0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
T1 = float(sys.argv[4]) if len(sys.argv) > 4 else ep.DUR
PLAN = ep.plan()
SEC = ep.SEC
h0, h1, hs = SEC["hook"]; w0, w1, ws = SEC["why"]; b0, b1, bs = SEC["back"]
f0, f1, fs = SEC["front"]; d0, d1, ds = SEC["drill"]; e0, e1, es = SEC["end"]
# 开场撞击的时刻（输出时间）
T_HIT = next(i for i, (s, _, p) in enumerate(PLAN) if p >= ep.A_IMPACT - 1e-6) / FPS
T_HIT2 = next(i for i, (s, _, p) in enumerate(PLAN) if s == "A2" and p >= ep.A_IMPACT - 1e-6) / FPS


def near_hand(m):
    return "handL" if m["handL"][2] < m["handR"][2] else "handR"


def chips(c, items, cur, t, alpha, y=380):
    """三步进度：当前一步亮金色，做完的打勾。"""
    if alpha <= 0:
        return
    n = len(items); gap = 16; wtot = W - 120; cw = (wtot - gap * (n - 1)) / n
    for i, s in enumerate(items):
        x = 60 + i * (cw + gap)
        on, done = i == cur, i < cur
        col = GOLD if on else (GREEN if done else (0.5, 0.53, 0.58))
        c.set_source_rgba(0.03, 0.045, 0.09, (0.85 if on else 0.6) * alpha); rrect(c, x, y, cw, 84, 20); c.fill()
        c.set_source_rgba(*col, alpha * (1 if on or done else 0.6)); c.set_line_width(4 if on else 2); rrect(c, x, y, cw, 84, 20); c.stroke()
        stroke_text(c, s, x + cw / 2, y + 55, 34 if len(s) <= 5 else 30, col if on else (INK if done else DIM), alpha, stroke=0)


def step_of(t, S):
    k = -1
    for i, (_, a, _) in enumerate(S):
        if t >= a - 0.1:
            k = i
    return k


STILLS = [float(x) for x in os.environ.get("STILLS", "").split()]   # 调版：只出这几个时刻的 png
AVAIL = sorted(f[:-5] for f in os.listdir(FR) if f.endswith(".json"))


def find(k):
    if os.path.exists(os.path.join(FR, k + ".json")) or not STILLS:
        return k
    sh, n = k.rsplit("_", 1)
    c = [a for a in AVAIL if a.rsplit("_", 1)[0] == sh]
    return min(c, key=lambda a: abs(int(a.rsplit("_", 1)[1]) - int(n)))


wr = None if STILLS else Writer(OUTF)
n0, n1 = int(T0 * FPS), min(len(PLAN), int(T1 * FPS))
for i in ([int(x * FPS) for x in STILLS] or range(n0, n1)):
    t = i / FPS
    shot, perf, p = PLAN[i]
    k = find(ep.key(shot, p))
    m = json.load(open(os.path.join(FR, k + ".json")))
    hk = near_hand(m)
    # 镜头推拉：开场撞击时猛推一下，慢放定格时缓慢推近
    zoom, focus = 1.0, (0.5, 0.5)
    if t < h1:
        zoom = 1 + 0.16 * ramp(t, T_HIT - 0.08, T_HIT + 0.05) - 0.06 * ramp(t, T_HIT + 0.3, h1)
        focus = (m[hk][0], m[hk][1])
    elif t < w1:
        zoom = 1 + 0.12 * ramp(t, T_HIT2, w1 - 0.5)
        focus = ((m[hk][0] + m["pelvis"][0]) / 2, (m[hk][1] + m["pelvis"][1]) / 2)
    elif t >= e0:
        zoom = 1 + 0.05 * ramp(t, e0, e1)
    s, buf, px = load_frame(os.path.join(FR, k + ".png"), zoom, focus)
    c = cairo.Context(s)
    P = {q: px(m[q][0], m[q][1]) for q in m if not q.startswith("_")}
    vignette(c, 0.45)
    if t >= e0:
        c.set_source_rgba(0.01, 0.015, 0.03, 0.6 * ramp(t, e0, e0 + 0.5)); c.paint()

    badge(c, ep.LEVEL, ep.LESSON, ep.TITLE, ramp(t, 0.0, 0.4), t / ep.DUR)
    stroke_text(c, "3D 示意", W - 60, 235, 24, DIM, 0.8, bold=False, align="r", stroke=4)

    # ---------------------------------------------------------------- 开场
    if t < h1 + 0.3:
        a = window(t, -1, h1, 0.3)
        tag(c, "错误示范", RED, 60, 330, a, icon="x")
        big_title(c, [("新手受伤", 0.86), ("第一名是{r|手腕}", 1.08)], t, 0.1, h1, y=540, size=100)
        if t >= T_HIT - 0.02:
            ring(c, *P[hk], 62, RED, a * ramp(t, T_HIT, T_HIT + 0.15), t, label="手腕")
        fl = math.exp(-((t - T_HIT) / 0.07) ** 2)
        if fl > 0.01:
            c.set_source_rgba(1, 1, 1, 0.55 * fl); c.paint()

    # ---------------------------------------------------------------- 为什么是手腕
    if w0 - 0.3 < t < w1 + 0.3:
        a = window(t, w0, w1, 0.3)
        tag(c, "错误：伸手撑地", RED, 60, 330, a, icon="x")
        if t >= T_HIT2 - 0.02:
            ring(c, *P[hk], 58, RED, a * ramp(t, T_HIT2, T_HIT2 + 0.2), t, label="手腕")
        a2 = window(t, ws[1][1], ws[1][2] + 0.2, 0.3)
        if a2 > 0:   # 体重 -> 手腕
            x0, y0 = P["chest"]; x1, y1 = P[hk]
            kk = ramp(t, ws[1][1], ws[1][1] + 0.5)
            arrow(c, x0, y0, x0 + (x1 - x0) * 0.8 * kk + 1e-3, y0 + (y1 - y0) * 0.8 * kk, RED, a2)
            stroke_text(c, "全身重量", (x0 + x1) / 2 + 40, (y0 + y1) / 2, 50, INK, a2, align="l")
        a3 = window(t, ws[2][1], w1 + 0.1, 0.3)
        if a3 > 0:
            p3 = pop(t, ws[2][1], 0.45)
            card(c, 60, 430, W - 120, 300, a3, RED)
            c.save(); c.translate(W / 2, 600); c.scale(p3, p3); c.translate(-W / 2, -600)
            stroke_text(c, "27.6%", W / 2, 640, 170, RED, a3, face=SERIF, stroke=0)
            c.restore()
            stroke_text(c, "单板受伤里，手腕的占比", W / 2, 700, 36, INK, a3, stroke=0)
            stroke_text(c, "Kim 等 · Am J Sports Med · 2012", W / 2, 760, 26, DIM, a3, bold=False, stroke=0)

    # ---------------------------------------------------------------- 往后摔
    if b0 - 0.3 < t < b1 + 0.3:
        a = window(t, b0, b1, 0.3)
        tag(c, "正确：往后摔", GREEN, 60, 330, a, icon="v")
        big_title(c, [("往后摔 · {w|3 步}", 1.0)], t, b0 + 0.05, bs[0][1] - 0.05, y=560, size=104)
        cur = step_of(t, bs)
        chips(c, ["① 蹲低", "② 握拳收胸", "③ 坐下再滚"], cur, t, a * ramp(t, bs[0][1] - 0.2, bs[0][1] + 0.2), y=440)
        if cur == 0:
            x, y = P["pelvis"]
            arrow(c, x + 150, y - 140, x + 150, y + 60, GOLD, a * ramp(t, bs[0][1] + 0.3, bs[0][1] + 0.7))
            stroke_text(c, "重心往下", x + 180, y - 160, 44, GOLD, a * ramp(t, bs[0][1] + 0.3, bs[0][1] + 0.7))
        elif cur == 1:
            x = (P["handL"][0] + P["handR"][0]) / 2; y = (P["handL"][1] + P["handR"][1]) / 2
            ring(c, x, y, 70, GREEN, a * ramp(t, bs[1][1], bs[1][1] + 0.3), t, label="拳头收胸前")
        elif cur == 2:
            ring(c, *P["pelvis"], 80, GREEN, a * window(t, bs[2][1] + 0.6, bs[2][1] + 2.4, 0.3), t, label="屁股先着地")
            if t > bs[2][1] + 2.3:
                bx = (P["ankleL"][0] + P["ankleR"][0]) / 2; by = (P["ankleL"][1] + P["ankleR"][1]) / 2
                ring(c, bx, by, 90, GREEN, a * ramp(t, bs[2][1] + 2.4, bs[2][1] + 2.7), t, label="板抬起来")

    # ---------------------------------------------------------------- 往前摔
    if f0 - 0.3 < t < f1 + 0.3:
        a = window(t, f0, f1, 0.3)
        tag(c, "正确：往前摔", GREEN, 60, 330, a, icon="v")
        big_title(c, [("往前摔 · {w|3 步}", 1.0)], t, f0 + 0.05, fs[0][1] - 0.05, y=560, size=104)
        cur = step_of(t, fs)
        chips(c, ["① 膝盖先跪", "② 小臂着地", "③ 脸侧开"], cur, t, a * ramp(t, fs[0][1] - 0.2, fs[0][1] + 0.2), y=440)
        if cur == 0:
            kq = "kneeL" if m["kneeL"][2] < m["kneeR"][2] else "kneeR"
            ring(c, *P[kq], 64, GREEN, a * ramp(t, fs[0][1] + 1.5, fs[0][1] + 1.8), t, label="膝盖")
        elif cur == 1:
            eq = "elbL" if m["elbL"][2] < m["elbR"][2] else "elbR"
            hq = "handL" if eq == "elbL" else "handR"
            x = (P[eq][0] + P[hq][0]) / 2; y = (P[eq][1] + P[hq][1]) / 2
            ring(c, x, y, 80, GREEN, a * ramp(t, fs[1][1] + 1.5, fs[1][1] + 1.8), t, label="整条小臂")
        elif cur == 2:
            ring(c, *P["head"], 72, GREEN, a * ramp(t, fs[2][1], fs[2][1] + 0.3), t, label="脸让开")

    # ---------------------------------------------------------------- 练习
    if d0 - 0.3 < t < d1 + 0.3:
        a = window(t, d0, d1, 0.3)
        tag(c, "怎么练", GOLD, 60, 330, a)
        card(c, 60, 440, W - 120, 330, a)
        stroke_text(c, "平地 · 穿着板", W / 2, 520, 40, DIM, a, stroke=0)
        rich_line(c, spans("蹲下 → 坐下 → 往后滚"), W / 2, 600, 58, a)
        stroke_text(c, "× 5 次", W / 2, 690, 62, GOLD, a, face=SERIF, stroke=0)
        a2 = window(t, ds[1][1], d1, 0.3)
        if a2 > 0:
            card(c, 60, 800, W - 120, 150, a2, GREEN)
            stroke_text(c, "过关标准", 120, 885, 36, GREEN, a2, align="l", stroke=0)
            stroke_text(c, "手不先碰地", W - 120, 892, 56, INK, a2, align="r", stroke=0)
        a3 = window(t, ds[2][1], d1, 0.3)
        if a3 > 0:
            tag(c, "护腕", ICE, 60, 980, a3, size=34)
            tag(c, "护臀", ICE, 240, 980, a3, size=34)

    # ---------------------------------------------------------------- 结尾
    if t >= e0 - 0.3:
        a = ramp(t, e0, e0 + 0.4)
        stroke_text(c, "下一课", W / 2, 720, 48, GOLD, a, spacing=0.3)
        big_title(c, [("摔倒了", 1.0), ("怎么{w|站起来}？", 1.0)], t, e0 + 0.1, e1 + 5, y=860, size=110)
        stroke_text(c, "关注我，跟着练到刻滑", W / 2, 1180, 40, INK, a * ramp(t, e0 + 0.8, e0 + 1.2), bold=False)

    for st, a0, a1 in ep.SUBS:
        if st != es[0][0]:
            subtitle(c, st, t, a0, a1)
    fade = 1 - ramp(t, 0, 0.15) + ramp(t, ep.DUR - 0.4, ep.DUR)
    if fade > 0:
        c.set_source_rgba(0, 0, 0, min(1, fade)); c.paint()
    if STILLS:
        s.write_to_png(f"{OUTF}_{t:05.2f}.png")
    else:
        wr.write(s)
if wr:
    wr.close()
print("frames", n1 - n0)
