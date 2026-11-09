"""《单板新手课》第5课：前刃推坡（竖屏 1080×1920，实拍 + 2D 演示 + 数据图）。
动作参考《单板从0到刻滑》第6课（zero2carve-EP06）的关键帧。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "newbie-lib"))
from epbase import plain, timeline, pw, key, ease

FPS = 30
LESSON = 5
SERIES = "单板新手课"
NAME = "前刃推坡"
TITLE = f"第{LESSON}课 · {NAME}"
STYLE = "day"
MUSIC = "pop"
TRACK = (1142, 0.0)             # Mixkit 免费音乐 #1142
MARKS = True

# ------------------------------------------------------------------ 数据（见 方案.md）
SLOPE = 12.0
STOP, SLIDE = 18.0, 8.0          # 前刃立刃角（rig 里前刃为负）
ROM_PF, ROM_DF = 50, 20          # 脚踝正常活动范围：跖屈（踮脚尖）约 50°，背屈（勾脚尖）约 20°（AAOS 常用正常值）

# ------------------------------------------------------------------ 动作：面朝山上，坡角取负（+y 是上坡），往下滑 = gy 变小
BASE = dict(slope=-SLOPE, tilt=-12, pz=0.80, arm=25, ab=32, elb=30, knee=(0.0, 1.0, 0.25), broll=-STOP, trail=1, ty0=0.0)

S = [
    (0.0, dict(BASE, pz=0.86, tilt=-5)),
    (0.6, dict(pz=0.76, tilt=-12)), (1.0, dict()),
    (1.6, dict(broll=-SLIDE, pz=0.78)),
    (2.6, dict(gy=-0.55)), (3.6, dict(gy=-1.20)),
    (4.2, dict(broll=-STOP, gy=-1.45, pz=0.76)), (4.8, dict()),
    (5.3, dict(broll=-SLIDE - 1, pz=0.78)),
    (6.3, dict(gy=-2.05)), (7.3, dict(gy=-2.70)),
    (7.9, dict(broll=-STOP, gy=-2.88, pz=0.76)), (8.4, dict()),
]
S_END = 8.4

# H：错误1——弯腰撅屁股，重心离开板，前刃松掉，下坡那边的后刃一碰雪，人往后栽
H = [
    (0.0, dict(BASE, broll=-8, tilt=-38, py=-0.14, pz=0.84, arm=55, ab=20, elb=15)),
    (0.8, dict(gy=-0.50, broll=-4)),
    (1.3, dict(gy=-1.20, broll=1)),
    (1.5, dict(gy=-1.40, broll=8, tilt=-5, arm=80, ab=40)),
    (1.9, dict(gy=-1.50, tilt=50, pz=0.45, py=-0.35, arm=-40, ab=25, elb=10, broll=6)),
    (2.4, dict(gy=-1.55, tilt=76, pz=0.17, py=-0.52, arm=-30, elb=30, neck=-20, knee=(0.0, 0.3, 1.0))),
    (2.9, dict()),
]
H_END = 2.9

# T：错误2——只踮脚尖、腿不弯，一颠就晃
T = [(0.0, dict(BASE, broll=-SLIDE, pz=0.97, tilt=-3, arm=15, ab=25, elb=10))]
for _i, (_g, _tl, _ar) in enumerate(((-0.4, -18, 70), (-0.8, 6, 30), (-1.2, -20, 80), (-1.6, 2, 40), (-2.0, -16, 75))):
    T.append((0.5 + 0.6 * _i, dict(gy=_g, tilt=_tl, arm=_ar, ab=40 if _ar > 50 else 25)))
T += [(3.6, dict(gy=-2.3, tilt=-6, arm=30))]
T_END = 3.6

# Y：错误3——一只脚用力，板头往下坡转
Y = [(0.0, dict(BASE, broll=-SLIDE, yx=-0.26)),
     (1.0, dict(gy=-0.5, yaw=-10, px=0.10)),
     (2.0, dict(gy=-1.2, gx=0.2, yaw=-28, px=0.14)),
     (3.0, dict(gy=-2.1, gx=0.5, yaw=-48, px=0.14, arm=50, ab=45)),
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
            "heelR": m @ Vector((0.26, -0.12, 0.08)), "heelL": m @ Vector((-0.26, -0.12, 0.08)),
            "footR": m @ Vector((0.26, 0, 0.03)), "footL": m @ Vector((-0.26, 0, 0.03))}


# ------------------------------------------------------------------ 字幕
import epbase
epbase.CPS = 5.2
SECTIONS = [
    ("hook", 0.2, ["会了后刃，{w|换个方向}也要能停。",
                   "第二个刹车：{w|前刃推坡}。"], 0.1),
    ("keys", 0.3, ["①面朝{w|山上}，膝盖往前顶，{w|脚跟抬起}。",
                   "②前刃卡住雪就停住，{w|上身直立}别弯腰。",
                   "③脚跟{w|慢慢放低}，板开始往下溜。",
                   "④想停：{w|脚跟再抬起}，膝盖往前顶。"], 0.5),
    ("why", 0.2, ["前刃也一样：{b|立刃角}大过坡度就停。",
                  "踮脚尖，脚踝能动约{g|50°}；",
                  "勾脚尖只有约{w|20°}，所以前刃通常{g|更好控制}。"], 0.5),
    ("mistakes", 0.2, ["{r|弯腰撅屁股}：前刃一松，往后栽。",
                       "{r|只踮脚、腿不弯}：一颠就站不稳。",
                       "{r|一只脚用力}：板头往下转。"], 0.3),
    ("drill", 0.2, ["练习：面朝山上，滑一米{w|停一下}，连续10次。",
                    "过关：想停就停，{w|上身一直直立}。"], 0.3),
    ("end", 0.2, [("下一课：{w|落叶飘}。", 2.6)], 0.3),
]
SUBS, SEC, DUR = timeline(SECTIONS)

FOOT = {
    "hook0": ("3381", 8.0, 0.45, 0.60),
    "hook1": ("3373", 1.0, 0.40, 0.55),
    "pass": ("3344", 1.0, 0.55, 0.70),
    "end": ("4016", 8.0, 0.40, 0.55),
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


def music_hits():
    hits = [SEC[k][2][0][1] for k in ("keys", "why", "mistakes", "drill", "end")]
    sfx = [(SEC["hook"][2][1][1] + 0.1, "boom")]
    sfx += [(s[1] + 0.05, "ding") for s in SEC["keys"][2]]
    sfx += [(SEC["why"][2][1][1] + 0.5, "ding"), (SEC["why"][2][2][1] + 0.5, "ding")]
    sfx += [(s[1] + 0.05, "whoosh") for s in SEC["mistakes"][2]]
    return hits, sfx


def overlay(c, t, fr, pts, K):
    from vert import W, GOLD, ICE, RED, GREEN, INK, DIM, window, ramp, tag, ring, arrow, chips, stroke_text
    kind, shot, p = fr
    K.hook_title(c, t, NAME, "第二个刹车", K.GOLD)
    k0, k1, ks = SEC["keys"]
    if k0 - 0.2 < t < k1 + 0.2:
        cur = max([j for j, s in enumerate(ks) if t >= s[1] - 0.2] or [0])
        chips(c, ["①面朝山上", "②上身直立", "③放脚跟=滑", "④抬脚跟=停"], cur, t, window(t, k0 + 0.1, k1, 0.3), y=300)
        if pts:
            a = window(t, *K.sec_window("keys", 0), 0.3)
            if a > 0:
                for q in ("heelL", "heelR"):
                    x, y = pts[q]; arrow(c, x, y + 60, x, y - 50, GREEN, a, 8)
                for q in ("kneeL", "kneeR"):
                    ring(c, *pts[q], 44, GOLD, a, t)
                tag(c, "膝盖往前顶 · 脚跟抬起", GOLD, 200, 1340, a, 38)
            a = window(t, *K.sec_window("keys", 1), 0.3)
            if a > 0:
                px, py = pts["pelvis"]; hx, hy = pts["head"]
                c.set_source_rgba(*GREEN, a); c.set_line_width(6); c.set_dash([14, 10])
                c.move_to(px, py + 40); c.line_to(px + (hx - px) * 1.25, py + (hy - py) * 1.25); c.stroke(); c.set_dash([])
                tag(c, "上身直立 · 别弯腰", GREEN, 260, 1340, a, 38, "v")
            a = window(t, *K.sec_window("keys", 2), 0.3)
            if a > 0:
                for q in ("heelL", "heelR"):
                    x, y = pts[q]; arrow(c, x, y - 50, x, y + 50, GOLD, a, 8)
                tag(c, "脚跟放低 → 滑", GOLD, 300, 1340, a, 38)
            a = window(t, *K.sec_window("keys", 3), 0.3)
            if a > 0:
                for q in ("heelL", "heelR"):
                    x, y = pts[q]; arrow(c, x, y + 60, x, y - 50, GREEN, a, 8)
                tag(c, "脚跟抬起 → 停", GREEN, 300, 1340, a, 38, "v")
    w0, w1, ws = SEC["why"]
    if w0 - 0.2 < t < w1 + 0.2:
        a = window(t, w0 + 0.2, w1, 0.3)
        K.dim(c, a)
        a1 = a * (1 - ramp(t, ws[1][1] - 0.3, ws[1][1]))
        e = pw([(ws[0][1], 0.0), (ws[0][1] + 1.8, STOP)], t)
        K.edge_diagram(c, t, a1, SLOPE, e, "toe", y=1000)
        a2 = a * ramp(t, ws[1][1] - 0.3, ws[1][1])
        items = [("踮脚尖 · 前刃", ROM_PF, K.GREEN, ws[1][1] + 0.2, "跖屈"), ("勾脚尖 · 后刃", ROM_DF, K.GOLD, ws[2][1] + 0.2, "背屈")]
        K.bars(c, t, a2, "脚踝能活动多少度", items, 60, unit="°", edge=K.GREEN,
               foot="参考：美国骨科医师学会（AAOS）常用的关节活动度正常值")
    m0, m1, ms = SEC["mistakes"]
    if m0 - 0.2 < t < m1 + 0.2:
        labs = ["弯腰撅屁股", "只踮脚、腿不弯", "一只脚用力"]
        for j in range(3):
            a = window(t, *K.sec_window("mistakes", j), 0.25)
            if a > 0:
                tag(c, f"错误{j + 1}：{labs[j]}", RED, 60, 330, a, 44, "x")
                if pts:
                    if j == 1:
                        for q in ("kneeL", "kneeR"):
                            ring(c, *pts[q], 44, RED, a, t)
                    else:
                        ring(c, *pts[("pelvis", None, "footR")[j]], 60, RED, a, t)
    d0, d1, ds = SEC["drill"]
    if d0 - 0.2 < t < d1 + 0.2:
        if t < ds[1][1]:
            a = window(t, d0 + 0.2, ds[1][1] - 0.1, 0.3)
            tag(c, "滑一米", GOLD, 180, 1340, a, 44)
            tag(c, "停一下", GREEN, 560, 1340, a * ramp(t, d0 + 1.8, d0 + 2.1), 44)
        else:
            K.stamp(c, "过关", W / 2, 760, t, ds[1][1] + 0.2, GREEN, window(t, ds[1][1], d1, 0.3))
            a = window(t, ds[1][1] + 0.3, d1, 0.3)
            for j, s in enumerate(("想停就停", "上身一直直立")):
                tag(c, s, GREEN, 150 + j * 400, 1180, a * ramp(t, ds[1][1] + 0.5 + 0.4 * j, ds[1][1] + 0.8 + 0.4 * j), 40, "v")
    K.end_card(c, t, "落叶飘")


if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), {k: (round(v[0], 1), round(v[1], 1)) for k, v in SEC.items()})

COVER = dict(title=NAME, sub="面朝山上，也能稳稳停下", items=["面朝山上", "上身直立", "放脚跟", "抬脚跟"],
             perf="S", p=1.0, cam=((1.5, 3.0, 1.05), (0.0, 0.0, 0.55), 40), bg=("3380", 3.0), set=dict(broll=0))
