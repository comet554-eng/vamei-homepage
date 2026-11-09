"""《单板新手课》第3课：直滑降（竖屏 1080×1920，实拍 + 2D 演示 + 数据图）。
plan() 每帧给出 ("F", 实拍镜头, 素材内时间) 或 ("R", 演示镜头, 表演时间)；overlay() 画这一集自己的标注和图表。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "newbie-lib"))
from epbase import plain, timeline, pw, key, ease

FPS = 30
LESSON = 3
SERIES = "单板新手课"
NAME = "直滑降"
TITLE = f"第{LESSON}课 · {NAME}"
STYLE = "day"
MUSIC = "drive"
TRACK = (963, 0.0)             # Mixkit 免费音乐 #963
MARKS = True

# ------------------------------------------------------------------ 数据（示意计算，见 方案.md）
SLOPE = 8.0                       # 示意：初级道里比较缓的一段
MU = 0.05                         # 单板在雪上的滑动摩擦系数取 0.05（文献范围约 0.02–0.14）
ACC = 9.81 * (math.sin(math.radians(SLOPE)) - MU * math.cos(math.radians(SLOPE)))   # ≈ 0.88 m/s²
DISTS = (5, 10, 20)
KMH = [round(math.sqrt(2 * ACC * d) * 3.6) for d in DISTS]                          # ≈ 11 / 15 / 21 km/h

# ------------------------------------------------------------------ 动作：板头朝下坡（yaw=90），人面朝 -x，沿 +y 往下滑
GOOD = dict(slope=SLOPE, yaw=90, pz=0.80, px=0.03, py=0.0, tilt=-6, arm=18, ab=30, elb=28, neck=0, curl=0, face=55, twist=8,
            knee=(0.25, 1.0, 0.2), trail=1, trw=0.32, ty0=0.0, gy=0.0)


def _run(t0, dur, y0, y1, n=6):
    """匀加速往下滑：gy 按 t² 增长。"""
    return [(t0 + dur * i / n, dict(gy=y0 + (y1 - y0) * (i / n) ** 2)) for i in range(1, n + 1)]


# G：正确的直滑降
G = [(0.0, dict(GOOD)), (1.0, dict())] + _run(1.0, 7.0, 0.0, 9.0)
G_END = 8.0

# B：错误1——重心在后脚：板头飘起来、板一转，人往后坐
B = [(0.0, dict(GOOD, px=-0.13, tilt=10, arm=40, ab=40, elb=15))] + _run(0.0, 1.6, 0.0, 1.6, 3) + [
    (2.2, dict(gy=2.4, yaw=115, arm=70, ab=50)),
    (2.7, dict(gy=2.9, yaw=140, tilt=40, pz=0.55, py=-0.30, arm=80, elb=10)),
    (3.2, dict(gy=3.1, yaw=150, tilt=72, pz=0.20, py=-0.50, arm=-30, elb=30, neck=-15, knee=(0.0, 0.3, 1.0))),
    (3.8, dict()),
]
B_END = 3.8

# L：错误2——怕快，上身往后仰、手往前抓
L = [(0.0, dict(GOOD, tilt=22, px=-0.06, arm=70, ab=20, elb=8, pz=0.88))] + _run(0.0, 3.4, 0.0, 3.0, 4) + [(3.6, dict())]
L_END = 3.6

# D：错误3——低头看板头，板慢慢偏
D = [(0.0, dict(GOOD, tilt=-14, curl=22, neck=42, face=30, arm=10, ab=20, elb=15))] + _run(0.0, 3.4, 0.0, 3.0, 4)
D[-1] = (D[-1][0], dict(D[-1][1], yaw=112))
D += [(3.6, dict())]
D_END = 3.6

PERF = dict(G=G, B=B, L=L, D=D)
SHOT_PERF = dict(G="G", B="B", L="L", D="D")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    pos, tgt = (gx - 2.3, gy + 2.6, 1.35), (gx, gy + 0.2, 0.55)
    return _slope(pos, s), _slope(tgt, s), 32


def extra_points(P, J):
    from mathutils import Vector
    m = J["board_m"]
    return {"nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)), "board": m @ Vector((0, 0, 0.02)),
            "footR": m @ Vector((0.26, 0, 0.03)), "footL": m @ Vector((-0.26, 0, 0.03))}


# ------------------------------------------------------------------ 字幕（不配音：按阅读速度排时间）
import epbase
epbase.CPS = 5.2
SECTIONS = [
    ("hook", 0.2, ["第一次{w|从坡上滑下来}。",
                   "不转弯、不刹车，先学会{w|直直地滑}。"], 0.1),
    ("keys", 0.3, ["①选{w|很缓的坡}，坡底要有{w|平地}。",
                   "②基本站姿，重心在{w|两脚中间}。",
                   "③板{w|放平}，板头朝{w|正下方}。",
                   "④眼睛{w|看前方}，到平地自然停下。"], 0.5),
    ("why", 0.2, ["为什么坡底一定要有平地？",
                  "直滑降不刹车，{b|速度会一直涨}。",
                  "8°缓坡：滑5米约{w|11 km/h}，滑20米就到{r|21 km/h}。"], 0.5),
    ("mistakes", 0.2, ["{r|重心在后脚}：板一转，人往后坐。",
                       "{r|怕快往后仰}：越仰越控制不住。",
                       "{r|低头看板头}：方向慢慢跑偏。"], 0.3),
    ("drill", 0.2, ["练习：缓坡上滑{w|5米}，到平地停下，重复。",
                    "过关：连续{w|5次}板头朝下，不转不摔。"], 0.3),
    ("end", 0.2, [("下一课：{w|后刃推坡}，学会刹车。", 3.0)], 0.3),
]
SUBS, SEC, DUR = timeline(SECTIONS)

FOOT = {
    "hook0": ("3381", 2.0, 0.40, 0.55),
    "hook1": ("3373", 6.0, 0.45, 0.60),
    "pass": ("4016", 4.0, 0.20, 0.35),
    "end": ("3378", 1.0, 0.50, 0.65),
}


def plan():
    out = []
    h0, h1, hs = SEC["hook"]; k0, k1, ks = SEC["keys"]; w0, w1, ws = SEC["why"]
    m0, m1, ms = SEC["mistakes"]; d0, d1, ds = SEC["drill"]; e0, e1, _ = SEC["end"]
    for i in range(int(round(DUR * FPS))):
        t = i / FPS
        if t < h1:
            cut = hs[1][1] - 0.1
            out.append(("F", "hook0", t) if t < cut else ("F", "hook1", t - cut))
        elif t < k1:
            a = [x[1] - k0 for x in ks]
            out.append(("R", "G", pw([(0, 0.0), (a[1] + 1.0, 1.0), (k1 - k0, G_END)], t - k0)))
        elif t < w1:
            out.append(("R", "G", G_END))
        elif t < m1:
            a = [x[1] - m0 for x in ms]; tt = t - m0
            if tt < a[1] - 0.1:
                out.append(("R", "B", pw([(0.2, 0.0), (a[1] - 0.3, B_END)], tt)))
            elif tt < a[2] - 0.1:
                out.append(("R", "L", pw([(a[1] - 0.1, 0.0), (a[2] - 0.2, L_END)], tt)))
            else:
                out.append(("R", "D", pw([(a[2] - 0.1, 0.0), (m1 - m0, D_END)], tt)))
        elif t < d1:
            a = [x[1] - d0 for x in ds]
            if t - d0 < a[1] - 0.1:
                out.append(("R", "G", pw([(0, 1.0), (a[1] - 0.1, 5.5)], t - d0)))
            else:
                out.append(("F", "pass", t - d0 - (a[1] - 0.1)))
        else:
            out.append(("F", "end", t - e0))
    return out


def music_hits():
    hits = [SEC[k][2][0][1] for k in ("keys", "why", "mistakes", "drill", "end")]
    sfx = [(SEC["hook"][2][1][1] + 0.1, "boom")]
    sfx += [(s[1] + 0.05, "ding") for s in SEC["keys"][2]]
    sfx += [(SEC["why"][2][2][1] + 0.6, "boom")]
    sfx += [(s[1] + 0.05, "whoosh") for s in SEC["mistakes"][2]]
    return hits, sfx


# ------------------------------------------------------------------ 叠加
def overlay(c, t, fr, pts, K):
    from vert import W, GOLD, ICE, RED, GREEN, INK, DIM, window, ramp, tag, ring, arrow, chips, stroke_text, card
    kind, shot, p = fr
    K.hook_title(c, t, NAME, "先直着滑", K.GOLD)
    k0, k1, ks = SEC["keys"]
    if k0 - 0.2 < t < k1 + 0.2:
        cur = max([j for j, s in enumerate(ks) if t >= s[1] - 0.2] or [0])
        chips(c, ["①缓坡+平地", "②重心居中", "③板放平", "④看前方"], cur, t, window(t, k0 + 0.1, k1, 0.3), y=300)
        a = window(t, *K.sec_window("keys", 0), 0.3)
        _profile(c, t, a, K)
        if pts:
            a = window(t, *K.sec_window("keys", 1), 0.3)
            K.weight_bar(c, t, a, 0.5 + 0.03 * ramp(t, ks[1][1] + 1.0, ks[1][1] + 1.8))
            a = window(t, *K.sec_window("keys", 2), 0.3)
            if a > 0:
                ring(c, *pts["nose"], 46, GOLD, a, t)
                tag(c, "板放平 · 板头朝正下方", GOLD, 200, 1340, a, 36)
            a = window(t, *K.sec_window("keys", 3), 0.3)
            if a > 0:
                ring(c, *pts["head"], 70, ICE, a, t, pulse=False)
                tag(c, "眼睛看滑行方向", ICE, 120, 1340, a, 36, "v")
                tag(c, "别盯着板头", RED, 600, 1340, a * ramp(t, ks[3][1] + 1.0, ks[3][1] + 1.3), 36, "x")
    w0, w1, ws = SEC["why"]
    if w0 - 0.2 < t < w1 + 0.2:
        a = window(t, w0 + 0.2, w1, 0.3)
        K.dim(c, a)
        cols = (K.GOLD, (1.0, 0.6, 0.3), K.RED)
        items = [(f"滑 {d} 米", KMH[i], cols[i], ws[2][1] + 0.3 + 0.6 * i, None) for i, d in enumerate(DISTS)]
        K.bars(c, t, a * ramp(t, ws[1][1] - 0.2, ws[1][1] + 0.2), f"{SLOPE:.0f}° 缓坡、不刹车：滑多远，速度到多少", items, 25,
               unit=" km/h", edge=K.GOLD, foot="示意 · 匀加速模型，摩擦系数取 0.05，没算空气阻力")
        stroke_text(c, "直滑降 = 不刹车", W / 2, 760, 80, INK, a * (1 - ramp(t, ws[1][1] - 0.2, ws[1][1] + 0.2)) if t < ws[1][1] + 0.2 else 0, face="Noto Serif SC")
        if t > ws[1][1] - 0.2:
            stroke_text(c, "速度会一直涨", W / 2, 760, 80, GOLD, a * ramp(t, ws[1][1] - 0.2, ws[1][1] + 0.3), face="Noto Serif SC")
            stroke_text(c, "参考：慢跑约 10 km/h，骑自行车约 15~20 km/h", W / 2, 860, 30, DIM, a * ramp(t, ws[2][1] + 1.5, ws[2][1] + 2.0), bold=False)
    m0, m1, ms = SEC["mistakes"]
    if m0 - 0.2 < t < m1 + 0.2:
        labs = ["重心在后脚", "怕快往后仰", "低头看板头"]
        for j in range(3):
            a = window(t, *K.sec_window("mistakes", j), 0.25)
            if a > 0:
                tag(c, f"错误{j + 1}：{labs[j]}", RED, 60, 330, a, 44, "x")
                if pts:
                    ring(c, *pts[("footL", "chest", "head")[j]], 60, RED, a, t)
    d0, d1, ds = SEC["drill"]
    if d0 - 0.2 < t < d1 + 0.2:
        if t < ds[1][1]:
            a = window(t, d0 + 0.2, ds[1][1] - 0.1, 0.3)
            tag(c, "滑 5 米", GOLD, 160, 1340, a, 44)
            tag(c, "平地停下", GREEN, 560, 1340, a * ramp(t, d0 + 2.0, d0 + 2.3), 44)
        else:
            K.stamp(c, "过关", W / 2, 760, t, ds[1][1] + 0.2, GREEN, window(t, ds[1][1], d1, 0.3))
            a = window(t, ds[1][1] + 0.3, d1, 0.3)
            for j, s in enumerate(("连续5次", "板头朝下 不转不摔")):
                tag(c, s, GREEN, 90 + j * 360, 1180, a * ramp(t, ds[1][1] + 0.5 + 0.4 * j, ds[1][1] + 0.8 + 0.4 * j), 40, "v")
    K.end_card(c, t, "后刃推坡")


def _profile(c, t, a, K):
    """坡的侧面示意：缓坡 + 坡底平地。"""
    from vert import GOLD, GREEN, ICE, DIM, INK, card, stroke_text, ramp
    if a <= 0:
        return
    x, y, w, h = 90, 1080, 900, 330
    card(c, x, y, w, h, a, GOLD)
    stroke_text(c, "侧面看：练直滑降的场地", x + 36, y + 56, 30, GOLD, a, align="l", stroke=0)
    x0, y0 = x + 60, y + 120; x1 = x + 560; y1 = y0 + (x1 - x0) * math.tan(math.radians(SLOPE)) * 1.6   # 坡度画夸张一点
    x2 = x + w - 60
    c.set_source_rgba(0.86, 0.90, 0.97, a)
    c.new_path(); c.move_to(x0, y0); c.line_to(x1, y1); c.line_to(x2, y1); c.line_to(x2, y + h - 30); c.line_to(x0, y + h - 30); c.close_path(); c.fill()
    k = K.ease((t - SEC["keys"][2][0][1] - 0.4) / 1.6)
    c.set_source_rgba(*GOLD, a); c.set_line_width(6); c.new_path(); c.move_to(x0, y0 - 8)
    xe = x0 + (x2 - 40 - x0) * k
    c.line_to(min(xe, x1), y0 - 8 + (min(xe, x1) - x0) * (y1 - y0) / (x1 - x0))
    if xe > x1:
        c.line_to(xe, y1 - 8)
    c.stroke()
    stroke_text(c, f"缓坡（示意 {SLOPE:.0f}°）", (x0 + x1) / 2 - 20, (y0 + y1) / 2 - 40, 28, INK, a, stroke=4)
    stroke_text(c, "坡底平地：自然停下", (x1 + x2) / 2, y1 + 60, 28, (0.15, 0.45, 0.3), a * ramp(t, SEC["keys"][2][0][1] + 1.2, SEC["keys"][2][0][1] + 1.6), stroke=0)


if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), {k: (round(v[0], 1), round(v[1], 1)) for k, v in SEC.items()})
    print("ACC", round(ACC, 3), "KMH", KMH)

COVER = dict(title=NAME, sub="先学会直直地滑下来", items=["缓坡", "重心居中", "板放平", "看前方"],
             perf="G", p=4.0, cam=((1.5, 3.0, 1.05), (0.0, 0.0, 0.55), 40), bg=("3381", 4.0), set=dict(yaw=0))
