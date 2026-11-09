"""《单板新手课》第4课：后刃推坡（竖屏 1080×1920，实拍 + 2D 演示 + 数据图）。
动作参考《单板从0到刻滑》第4课（zero2carve-EP04）的关键帧。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "newbie-lib"))
from epbase import plain, timeline, pw, key, ease

FPS = 30
LESSON = 4
SERIES = "单板新手课"
NAME = "后刃推坡"
TITLE = f"第{LESSON}课 · {NAME}"
STYLE = "day"
MUSIC = "bounce"
TRACK = (780, 0.0)             # Mixkit 免费音乐 #780
MARKS = True

# ------------------------------------------------------------------ 数据（示意，见 方案.md）
SLOPE = 12.0           # 示意坡度（初级道最陡的地方大约十几度）
STOP, SLIDE = 18.0, 7.0  # 立刃角（相对坡面）：大于坡度停住，小于坡度往下溜

# ------------------------------------------------------------------ 动作（rig 里 broll > 0 = 前刃抬起、后刃压雪；+y 是下坡）
BASE = dict(slope=SLOPE, tilt=10, pz=0.80, arm=20, ab=35, elb=25, knee=(0.0, 1.0, 0.25), trail=1, ty0=0.0)

# S：正确的后刃推坡——站稳 → 坐低 → 脚尖放低开始滑 → 脚尖抬起停住 → 两脚平均用力直直往下
S = [
    (0.0, dict(BASE, broll=STOP, pz=0.86, tilt=2)),
    (0.6, dict(pz=0.74, tilt=10)), (1.0, dict(pz=0.76)),
    (1.6, dict(broll=SLIDE)),
    (2.6, dict(gy=0.55)), (3.6, dict(gy=1.20)),
    (4.2, dict(broll=STOP, gy=1.45)), (4.8, dict()),
    (5.3, dict(broll=SLIDE + 1)),
    (6.3, dict(gy=2.05)), (7.3, dict(gy=2.70)),
    (7.9, dict(broll=STOP, gy=2.88)), (8.4, dict()),
]
S_END = 8.4

# H：错误1——板放平往下溜，越滑越快，下坡那边的前刃一碰雪，人被甩出去
H = [
    (0.0, dict(BASE, broll=4)),
    (0.7, dict(gy=0.30, broll=1)),
    (1.4, dict(gy=1.30, broll=0, tilt=4, arm=45, ab=40)),
    (1.6, dict(gy=1.62, broll=-7, tilt=-18, arm=60)),
    (2.0, dict(gy=1.72, broll=-40, tilt=-60, pz=0.52, py=0.40, arm=80, elb=10, knee=(0.0, 1.0, -0.3))),
    (2.5, dict(gy=1.75, pz=0.32, py=0.80, tilt=-80, broll=-75, bz=0.12, arm=80, elb=60, neck=-30, knee=(0.0, 0.3, -1.0))),
    (3.0, dict()),
]
H_END = 3.0

# T：错误2——直腿站，板一颠人就晃
T = [(0.0, dict(BASE, broll=SLIDE, pz=0.97, tilt=4, arm=15, ab=25, elb=10))]
for _i, (_g, _tl, _ar) in enumerate(((0.4, 18, 70), (0.8, -8, 30), (1.2, 22, 80), (1.6, 0, 40), (2.0, 16, 75))):
    T.append((0.5 + 0.6 * _i, dict(gy=_g, tilt=_tl, arm=_ar, ab=40 if _ar > 50 else 25)))
T += [(3.6, dict(gy=2.3, tilt=6, arm=30))]
T_END = 3.6

# Y：错误3——只压前脚，板头往下坡转，越滑越歪
Y = [(0.0, dict(BASE, broll=SLIDE, yx=-0.26)),
     (1.0, dict(gy=0.5, yaw=10, px=0.10)),
     (2.0, dict(gy=1.2, gx=0.2, yaw=28, px=0.14)),
     (3.0, dict(gy=2.1, gx=0.5, yaw=48, px=0.14, arm=50, ab=45)),
     (3.6, dict())]
Y_END = 3.6

PERF = dict(S=S, H=H, T=T, Y=Y)
SHOT_PERF = dict(S="S", H="H", T="T", Y="Y")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    pos, tgt = (gx + 1.5, gy + 3.2, 2.0), (gx, gy, 0.45)
    return _slope(pos, s), _slope(tgt, s), 32


def extra_points(P, J):
    from mathutils import Vector
    m = J["board_m"]
    return {"heel": m @ Vector((0, -0.125, 0.0)), "toe": m @ Vector((0, 0.125, 0.0)), "board": m @ Vector((0, 0, 0.02)),
            "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)),
            "toeR": m @ Vector((0.26, 0.14, 0.08)), "toeL": m @ Vector((-0.26, 0.14, 0.08)),
            "footR": m @ Vector((0.26, 0, 0.03)), "footL": m @ Vector((-0.26, 0, 0.03))}


# ------------------------------------------------------------------ 字幕
import epbase
epbase.CPS = 5.2
SECTIONS = [
    ("hook", 0.2, ["站在坡上{r|停不住}，越滑越快？",
                   "第一个刹车：{w|后刃推坡}。"], 0.1),
    ("keys", 0.3, ["①面朝下坡，{w|屈膝坐低}，像要坐椅子。",
                   "②{w|脚尖勾起}，后刃卡住雪，人就停住。",
                   "③脚尖{w|慢慢放低}，板开始往下溜。",
                   "④两脚{w|平均用力}，板横着，直直往下。"], 0.5),
    ("why", 0.2, ["停还是滑，看{b|立刃角}和{b|坡度}谁大。",
                  "立刃比坡度{g|大}：刃卡进雪，停住；",
                  "比坡度{w|小}：往下溜；完全放平，{r|前刃一碰雪就摔}。"], 0.5),
    ("mistakes", 0.2, ["{r|板放平}：前刃挂雪，往前摔。",
                       "{r|直腿站}：一颠就失去平衡。",
                       "{r|只压一只脚}：板头往下转，越滑越歪。"], 0.3),
    ("drill", 0.2, ["练习：滑一米，{w|停一下}，连续10次。",
                    "过关：{w|想停就停}，板一直横着。"], 0.3),
    ("end", 0.2, [("下一课：{w|前刃推坡}。", 2.6)], 0.3),
]
SUBS, SEC, DUR = timeline(SECTIONS)

FOOT = {
    "hook0": ("3378", 0.5, 0.35, 0.50),
    "hook1": ("3380", 5.5, 0.40, 0.55),
    "pass": ("3344", 6.0, 0.30, 0.45),
    "end": ("3348", 5.5, 0.40, 0.55),
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
            out.append(("R", "S", pw([(0, 0.0), (a[0] + 0.6, 0.0), (a[0] + 2.0, 1.0), (a[2], 1.0), (a[2] + 0.4, 1.6),
                                      (a[3] - 0.2, 4.2), (a[3], 4.8), (k1 - k0, S_END)], t - k0)))
        elif t < w1:
            out.append(("R", "S", S_END))
        elif t < m1:
            a = [x[1] - m0 for x in ms]; tt = t - m0
            if tt < a[1] - 0.1:
                out.append(("R", "H", pw([(0.2, 0.0), (a[1] - 0.3, H_END)], tt)))
            elif tt < a[2] - 0.1:
                out.append(("R", "T", pw([(a[1] - 0.1, 0.0), (a[2] - 0.2, T_END)], tt)))
            else:
                out.append(("R", "Y", pw([(a[2] - 0.1, 0.0), (m1 - m0, Y_END)], tt)))
        elif t < d1:
            a = [x[1] - d0 for x in ds]
            if t - d0 < a[1] - 0.1:
                out.append(("R", "S", pw([(0, 1.0), (a[1] - 0.1, S_END)], t - d0)))
            else:
                out.append(("F", "pass", t - d0 - (a[1] - 0.1)))
        else:
            out.append(("F", "end", t - e0))
    return out


def edge_at(t):
    """原理段里截面图的立刃角，跟着字幕走：先停（18°），再滑（7°），最后放平到负（前刃碰雪）。"""
    w0, w1, ws = SEC["why"]
    a = [x[1] for x in ws]
    return pw([(a[0], 0.0), (a[0] + 1.6, SLOPE), (a[1], SLOPE), (a[1] + 0.8, STOP), (a[2], STOP), (a[2] + 0.8, SLIDE),
               (a[2] + 2.6, SLIDE), (a[2] + 3.6, -5.0)], t)


def music_hits():
    hits = [SEC[k][2][0][1] for k in ("keys", "why", "mistakes", "drill", "end")]
    sfx = [(SEC["hook"][2][1][1] + 0.1, "boom")]
    sfx += [(s[1] + 0.05, "ding") for s in SEC["keys"][2]]
    sfx += [(SEC["why"][2][1][1] + 0.8, "ding"), (SEC["why"][2][2][1] + 3.6, "boom")]
    sfx += [(s[1] + 0.05, "whoosh") for s in SEC["mistakes"][2]]
    return hits, sfx


def overlay(c, t, fr, pts, K):
    from vert import W, GOLD, ICE, RED, GREEN, INK, DIM, window, ramp, tag, ring, arrow, chips, stroke_text
    kind, shot, p = fr
    K.hook_title(c, t, NAME, "第一个刹车", K.GOLD)
    k0, k1, ks = SEC["keys"]
    if k0 - 0.2 < t < k1 + 0.2:
        cur = max([j for j, s in enumerate(ks) if t >= s[1] - 0.2] or [0])
        chips(c, ["①坐低", "②勾脚尖=停", "③放脚尖=滑", "④两脚平均"], cur, t, window(t, k0 + 0.1, k1, 0.3), y=300)
        if pts:
            a = window(t, *K.sec_window("keys", 0), 0.3)
            if a > 0:
                for q in ("kneeL", "kneeR"):
                    ring(c, *pts[q], 44, GOLD, a, t)
                tag(c, "屈膝 · 屁股往下坐", GOLD, 220, 1340, a, 38)
            a = window(t, *K.sec_window("keys", 1), 0.3)
            if a > 0:
                for q in ("toeL", "toeR"):
                    x, y = pts[q]; arrow(c, x, y + 60, x, y - 50, GREEN, a, 8)
                tag(c, "脚尖勾起 → 停", GREEN, 300, 1340, a, 38, "v")
            a = window(t, *K.sec_window("keys", 2), 0.3)
            if a > 0:
                for q in ("toeL", "toeR"):
                    x, y = pts[q]; arrow(c, x, y - 50, x, y + 50, GOLD, a, 8)
                tag(c, "脚尖放低 → 滑", GOLD, 300, 1340, a, 38)
            a = window(t, *K.sec_window("keys", 3), 0.3)
            if a > 0:
                for q in ("footL", "footR"):
                    ring(c, *pts[q], 46, ICE, a, t)
                tag(c, "两脚一样用力 · 板横着", ICE, 200, 1340, a, 38)
    w0, w1, ws = SEC["why"]
    if w0 - 0.2 < t < w1 + 0.2:
        a = window(t, w0 + 0.2, w1, 0.3)
        K.dim(c, a)
        K.edge_diagram(c, t, a, SLOPE, edge_at(t), "heel", y=1000)
        stroke_text(c, "示意：立刃角按相对坡面算，坡度取 12°", 90, 1460, 24, DIM, a, bold=False, align="l", stroke=4)
    m0, m1, ms = SEC["mistakes"]
    if m0 - 0.2 < t < m1 + 0.2:
        labs = ["板放平", "直腿站", "只压一只脚"]
        for j in range(3):
            a = window(t, *K.sec_window("mistakes", j), 0.25)
            if a > 0:
                tag(c, f"错误{j + 1}：{labs[j]}", RED, 60, 330, a, 44, "x")
                if pts:
                    if j == 1:
                        for q in ("kneeL", "kneeR"):
                            ring(c, *pts[q], 44, RED, a, t)
                    else:
                        ring(c, *pts[("toe", None, "footR")[j]], 60, RED, a, t)
    d0, d1, ds = SEC["drill"]
    if d0 - 0.2 < t < d1 + 0.2:
        if t < ds[1][1]:
            a = window(t, d0 + 0.2, ds[1][1] - 0.1, 0.3)
            tag(c, "滑一米", GOLD, 180, 1340, a, 44)
            tag(c, "停一下", GREEN, 560, 1340, a * ramp(t, d0 + 1.8, d0 + 2.1), 44)
        else:
            K.stamp(c, "过关", W / 2, 760, t, ds[1][1] + 0.2, GREEN, window(t, ds[1][1], d1, 0.3))
            a = window(t, ds[1][1] + 0.3, d1, 0.3)
            for j, s in enumerate(("想停就停", "板一直横着")):
                tag(c, s, GREEN, 170 + j * 400, 1180, a * ramp(t, ds[1][1] + 0.5 + 0.4 * j, ds[1][1] + 0.8 + 0.4 * j), 40, "v")
    K.end_card(c, t, "前刃推坡")


if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), {k: (round(v[0], 1), round(v[1], 1)) for k, v in SEC.items()})

COVER = dict(title=NAME, sub="学会在坡上停下来", items=["坐低", "勾脚尖", "放脚尖", "两脚平均"],
             perf="S", p=1.0, cam=((1.5, 3.0, 1.05), (0.0, 0.0, 0.55), 40), bg=("3378", 2.0), set=dict(broll=0))
