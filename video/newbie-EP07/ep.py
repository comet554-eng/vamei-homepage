"""《单板新手课》第7课：第一次换刃（后刃 → 前刃）。动作参考《单板从0到刻滑》第7课（zero2carve-EP07）。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "newbie-lib"))
from epbase import plain, timeline, pw, key, ease
import epkit

FPS = 30
LESSON = 7
SERIES = "单板新手课"
NAME = "第一次换刃"
TITLE = f"第{LESSON}课 · {NAME}"
STYLE = "day"
MUSIC = "pop"
TRACK = (14, 0.0)              # Mixkit 免费音乐 #14 Swings and Slides
MARKS = True

SLOPE = 12.0
R = 3.0
MU = 0.10
ACC = 9.81 * (math.sin(math.radians(SLOPE)) - MU * math.cos(math.radians(SLOPE)))
KMH_PER_S = ACC * 3.6                      # 平板正对下坡，每多拖 1 秒增加的时速（≈3.9）


def arc(phi_deg, c=(0.6 - R * math.sin(math.radians(10)), 0.05 + R * math.cos(math.radians(10)))):
    p = math.radians(phi_deg)
    return c[0] + R * math.sin(p), c[1] - R * math.cos(p)


def at(phi, **kw):
    x, y = arc(phi); d = dict(gx=x, gy=y, yaw=phi); d.update(kw); return d


BASE = dict(slope=SLOPE, tilt=10, pz=0.80, arm=22, ab=35, elb=25, knee=(0.0, 1.0, 0.25), trail=1)
WP = sum(((0.0, 0.0),) + tuple(arc(a) for a in [10, 40, 70, 90, 120, 150, 175]), ())

# S：正确的第一次换刃
S = [
    (0.0, dict(BASE, yaw=10, broll=12, gx=0.0, gy=0.0, px=0.05, tw=WP, tn=0)),
    (1.0, at(10, broll=16, pz=0.76)),
    (1.8, at(40, broll=11, twist=20, face=25, pz=0.82, tn=1)),
    (2.3, at(70, broll=5, twist=28, face=30, pz=0.86, tilt=4, tn=2)),
    (2.6, at(90, broll=0, tilt=0, pz=0.88, twist=25, tn=3)),
    (3.2, at(120, broll=-14, tilt=-10, pz=0.78, twist=15, face=15, tn=4)),
    (3.9, at(150, broll=-17, tilt=-12, twist=5, face=5, tn=5)),
    (4.6, at(175, broll=-18, twist=0, face=0, px=0.0, tn=6)),
    (5.2, dict(gx=arc(175)[0] - 0.35, gy=arc(175)[1] + 0.02, yaw=180)),
    (5.8, dict()),
]
S_END = 5.8

# W：错误1——只拧上身、板没转过下坡线就压前刃：卡刃，往前扑
W = [
    (0.0, dict(BASE, yaw=10, broll=12, gx=0.0, gy=0.0, tw=(0.0, 0.0), tn=0)),
    (0.8, at(14, broll=14, twist=20, face=20)),
    (1.5, at(28, broll=6, twist=60, face=45, arm=40, ab=40)),
    (1.8, at(34, broll=-8, twist=60, tilt=-15)),
    (2.2, at(36, broll=-40, tilt=-60, pz=0.52, py=0.40, arm=80, elb=10, knee=(0.0, 1.0, -0.3))),
    (2.7, at(37, pz=0.32, py=0.80, tilt=-80, broll=-75, bz=0.12, arm=80, elb=60, neck=-30, knee=(0.0, 0.3, -1.0))),
    (3.2, dict()),
]
# H：错误2——平板时犹豫，板头一直对着下坡，越来越快
_y = [arc(90)[1] + d for d in (0.0, 0.8, 2.2, 4.2)]
H = [
    (0.0, dict(BASE, **at(60, broll=6, tw=(0.0, 0.0, *arc(90)), tn=0))),
    (0.6, at(90, broll=0, tilt=0, pz=0.92, arm=50, ab=45, tn=1)),
    (1.4, dict(gy=_y[1], arm=65)), (2.2, dict(gy=_y[2], tilt=8, arm=75)), (3.0, dict(gy=_y[3], tilt=14)), (3.3, dict()),
]
# B：错误3——换前刃时往后坐：重心离开板，后刃一碰雪就坐倒
B = [
    (0.0, dict(BASE, **at(60, broll=6, tw=(0.0, 0.0), tn=0))),
    (0.6, at(90, broll=0, tilt=0, pz=0.86)),
    (1.2, at(115, broll=-6, tilt=25, px=-0.12, arm=60, ab=40)),
] + [(1.6, dict(tilt=45, pz=0.45, py=-0.30, arm=-40, ab=25, elb=10, broll=6)),
     (2.1, dict(tilt=72, pz=0.18, py=-0.50, arm=-30, elb=30, knee=(0.0, 0.3, 1.0))), (2.6, dict())]

PERF = dict(S=S, W=W, H=H, B=B)
SHOT_PERF = dict(S="S", T="S", W="W", H="H", B="B")
CEN = arc(90)


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    if shot == "T":            # 高处看整条弯
        cx, cy = 0.5 * gx + 0.5 * CEN[0], 0.5 * gy + 0.5 * CEN[1]
        pos, tgt = (cx + 0.8, cy + 4.2, 3.6), (cx, cy - 0.3, 0.2)
        return _slope(pos, s), _slope(tgt, s), 30
    cx, cy = 0.8 * gx + 0.2 * CEN[0], 0.85 * gy + 0.15 * CEN[1]
    pos, tgt = (cx + 1.6, cy + 4.6, 2.4), (cx, cy - 0.1, 0.6)
    return _slope(pos, s), _slope(tgt, s), 30


def extra_points(P, J):
    from mathutils import Vector
    m = J["board_m"]
    return {"board": m @ Vector((0, 0, 0.02)), "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)),
            "toe": m @ Vector((0, 0.125, 0.0)), "heel": m @ Vector((0, -0.125, 0.0)),
            "footR": m @ Vector((0.26, 0, 0.03)), "footL": m @ Vector((-0.26, 0, 0.03))}


import epbase
epbase.CPS = 5.2
SECTIONS = [
    ("hook", 0.2, ["从后刃换到前刃，就是{w|第一个弯}。",
                   "为什么一换刃就{r|摔}？"], 0.1),
    ("keys", 0.3, ["①后刃落叶飘，先把{w|速度}放慢。",
                   "②眼睛和肩膀{w|先转}，看向要去的方向。",
                   "③板头一过下坡线，{w|马上压前刃}。",
                   "④前刃把弯走完，板横过来，{w|停住}。"], 0.5),
    ("why", 0.2, ["换刃中间有一下{w|平板}：两边刃都不吃雪。",
                  "12°的坡，平板每拖{w|1秒}，时速多约{r|4公里}；",
                  "拖{w|3秒}，快{r|12公里}。所以要{g|果断}。"], 0.5),
    ("mistakes", 0.2, ["{r|只拧上身、板没过下坡线}就压前刃：卡刃。",
                       "{r|平板时犹豫}：越拖越快，不敢转。",
                       "{r|换刃往后坐}：重心离开板，坐倒。"], 0.3),
    ("drill", 0.2, ["练习：缓坡上{w|落叶飘→换前刃停}，左右各5次。",
                    "过关：平板{w|不超过1秒}，不卡刃。"], 0.3),
    ("end", 0.2, [("下一课：连起来，{w|S弯}。", 2.6)], 0.3),
]
SUBS, SEC, DUR = timeline(SECTIONS)

FOOT = {
    "hook0": ("3381", 12.0, 0.40, 0.55),
    "hook1": ("3380", 0.5, 0.40, 0.55),
    "pass": ("4016", 2.0, 0.55, 0.70),
    "end": ("3378", 12.0, 0.45, 0.60),
}

KEYS = ("S", [0.0, 1.0, 2.0, 2.7, S_END])
WHY = [("T", 0.0, 2.6), ("T", 2.6, 2.6), ("T", 2.6, S_END)]
MIST = [("W", 0.0, 3.2), ("H", 0.0, 3.3), ("B", 0.0, 2.6)]
DRILL = ("S", 0.6, S_END)
plan = epkit.std_plan(globals())
music_hits = epkit.std_hits(globals())

STAMP = "第一个弯"
CHIPS = ["落叶飘慢下来", "眼肩先转", "过线压前刃", "前刃走完"]
KEY_TAGS = [("后刃落叶飘 · 速度放慢", "GOLD", None, ["footL", "footR"]),
            ("眼睛 → 肩 → 髋 → 板", "ICE", None, ["head"]),
            ("板头过下坡线 → 膝盖往前顶", "GREEN", "v", ["toe"]),
            ("前刃把弯走完 · 停住", "GREEN", "v", ["footL", "footR"])]
MIST_LABS = ["板没过线就压前刃", "平板时犹豫", "换刃往后坐"]
MIST_RINGS = ["toe", "board", "pelvis"]
DRILL_TAGS = ("落叶飘 → 换前刃停", "左右各 5 次")
PASS_TAGS = ("平板不超过 1 秒", "不卡刃")
NEXT = "S弯"


def WHY_DRAW(c, t, K, pts):
    from vert import window, ramp
    w0, w1, ws = SEC["why"]
    a = window(t, ws[1][1] - 0.2, w1, 0.3)
    K.dim(c, a * 0.7)
    items = [(f"拖 {s} 秒", round(KMH_PER_S * s), (K.GOLD, (1.0, 0.6, 0.3), K.RED)[s - 1],
              ws[1][1] + 0.5 if s == 1 else ws[2][1] + (0.2 if s == 2 else 0.9), None) for s in (1, 2, 3)]
    K.bars(c, t, a, "平板对着下坡，多拖几秒，时速多多少", items, 14, unit=" km/h", edge=K.GOLD,
           foot="示意 · 坡度 12°，摩擦系数取 0.1，匀加速模型")
    if pts and t < ws[1][1]:
        from vert import tag
        tag(c, "这一下 = 平板", K.GOLD, 120, 1340, window(t, ws[0][1] + 1.2, ws[1][1] - 0.2, 0.3), 40)


overlay = epkit.std_overlay(globals())

COVER = dict(title=NAME, sub="从后刃到前刃，第一个弯", items=["落叶飘", "眼肩先转", "过线压前刃", "走完停住"],
             perf="S", p=3.4, cam=((1.5, 3.0, 1.05), (0.0, 0.0, 0.55), 40), bg=("3381", 14.0), set=dict(broll=0, yaw=0))

if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), "kmh/s", round(KMH_PER_S, 2))
