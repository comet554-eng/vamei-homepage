"""《单板新手课》第6课：落叶飘（后刃）。动作参考《单板从0到刻滑》第5课（zero2carve-EP05）。
结构和标注用 newbie-lib/epkit.py 的通用模板。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "newbie-lib"))
from epbase import plain, timeline, pw, key, ease
import epkit

FPS = 30
LESSON = 6
SERIES = "单板新手课"
NAME = "落叶飘"
TITLE = f"第{LESSON}课 · {NAME}"
STYLE = "day"
MUSIC = "pop"
TRACK = (1154, 0.0)            # Mixkit 免费音乐 #1154 Reaching Out
MARKS = True

SLOPE = 12.0
STOP, SLIDE = 18.0, 9.0
LEAF = 15.0
ANGLES = [10, 20, 45, 90]
SHARE = {a: round(100 * math.sin(math.radians(a))) for a in ANGLES}     # 下滑力顺着板长方向的份额（%）

BASE = dict(slope=SLOPE, tilt=10, pz=0.80, arm=20, ab=35, elb=25, knee=(0.0, 1.0, 0.25), broll=STOP, trail=1)

# L：正确——推坡停住 → 看左压左脚（板头这边）往左飘 → 回中停 → 看右压右脚往回飘 → 停
WP = (0.0, 0.0, 2.6, 0.75, 2.85, 0.85, 0.25, 1.65, 0.0, 1.75)
L = [
    (0.0, dict(BASE, tw=WP, tn=0)),
    (1.0, dict(pz=0.76)),
    (1.8, dict(px=0.10, yaw=LEAF, broll=SLIDE, pz=0.78, twist=25, face=35)),
    (2.6, dict(gx=0.45, gy=0.12)),
    (4.4, dict(gx=2.60, gy=0.75, tn=1)),
    (5.0, dict(px=0.0, yaw=0, broll=STOP, gx=2.85, gy=0.85, tn=2, twist=0, face=0)),
    (5.6, dict()),
    (6.4, dict(px=-0.10, yaw=-LEAF, broll=SLIDE, twist=-25, face=-45)),
    (7.2, dict(gx=2.40, gy=0.98)),
    (9.0, dict(gx=0.25, gy=1.65, tn=3)),
    (9.6, dict(px=0.0, yaw=0, broll=STOP, gx=0.0, gy=1.75, tn=4, twist=0, face=0)),
    (10.2, dict()),
]
L_END = 10.2

# T：原理——人站在原地，板头朝下偏 0 → 10 → 20 → 45 → 90°
T = [(0.0, dict(BASE, trail=0, yaw=0))]
for i, a in enumerate(ANGLES):
    T += [(1.0 + 1.4 * i, dict(yaw=a, px=0.10 if a < 60 else 0.0)), (1.6 + 1.4 * i, dict())]
T_END = 1.6 + 1.4 * (len(ANGLES) - 1)

# W：错误1——压前脚太多，板头转进下坡线，直冲，坐倒
W = [
    (0.0, dict(BASE, broll=SLIDE, yaw=12, px=0.06, tw=(0.0, 0.0), tn=0)),
    (0.8, dict(gx=0.90, gy=0.30, yaw=25)),
    (1.4, dict(gx=1.60, gy=0.90, yaw=60, px=0.12, tilt=-4, arm=45, ab=40)),
    (1.9, dict(gx=1.85, gy=2.00, yaw=85, broll=5, tilt=14, arm=70, ab=45)),
    (2.4, dict(gx=1.95, gy=3.10, tilt=45, pz=0.45, py=-0.30, arm=-40, ab=25, elb=10, broll=4)),
    (2.9, dict(gy=3.50, tilt=70, pz=0.17, py=-0.50, arm=-30, elb=30, knee=(0.0, 0.3, 1.0))),
    (3.3, dict()),
]
# U：错误2——只扭上身，板不往旁边走，直直往下溜
U = [(0.0, dict(BASE, tw=(0.0, 0.0), tn=0)), (0.6, dict(twist=55, face=60, arm=40, ab=45, broll=SLIDE)),
     (3.0, dict(gy=1.6, gx=0.1)), (3.4, dict())]
# D：错误3——低头看板，重心往后，坐倒
D = [(0.0, dict(BASE, broll=SLIDE, yaw=10, tw=(0.0, 0.0), tn=0, neck=40, curl=20, tilt=-6)),
     (1.2, dict(gx=0.8, gy=0.3, tilt=8)), (1.7, dict(gx=1.0, gy=0.4, tilt=40, pz=0.48, py=-0.3, arm=-40, elb=10)),
     (2.2, dict(tilt=70, pz=0.18, py=-0.5, arm=-30, elb=30, knee=(0.0, 0.3, 1.0))), (2.8, dict())]

PERF = dict(L=L, T=T, W=W, U=U, D=D)
SHOT_PERF = dict(L="L", T="T", W="W", U="U", D="D")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    if shot == "T":
        pos, tgt = (1.2, 3.2, 2.0), (0.0, 0.0, 0.5)
    elif shot == "W":
        pos, tgt = (gx + 1.0, gy + 4.4, 2.4), (gx, gy, 0.5)
    else:
        cx = 1.4 + 0.8 * (gx - 1.4)
        pos, tgt = (cx, gy + 3.9, 2.1), (cx, gy + 0.2, 0.55)
    return _slope(pos, s), _slope(tgt, s), 30


def extra_points(P, J):
    from mathutils import Vector
    m = J["board_m"]
    return {"board": m @ Vector((0, 0, 0.02)), "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)),
            "footR": m @ Vector((0.26, 0, 0.03)), "footL": m @ Vector((-0.26, 0, 0.03))}


import epbase
epbase.CPS = 5.2
SECTIONS = [
    ("hook", 0.2, ["后刃推坡会了，{w|怎么往旁边走}？",
                   "像树叶一样左右飘：{w|落叶飘}。"], 0.1),
    ("keys", 0.3, ["①先用{w|后刃推坡}停稳。",
                   "②看板头那边，{w|重心移到前脚}，往前飘。",
                   "③想停：重心{w|回到中间}，脚尖勾起。",
                   "④再看另一边、{w|压后脚}，往回飘。"], 0.5),
    ("why", 0.2, ["板头只要往下偏{w|一点点}，板就会走。",
                  "偏10°：顺着板的下滑力约{g|17%}，慢慢走；",
                  "偏45°：约{r|71%}，太快了。偏{w|10~20°}就够。"], 0.5),
    ("mistakes", 0.2, ["{r|压前脚太多}：板头冲下去，越滑越快。",
                       "{r|只扭上身}：板不往旁边走，只往下溜。",
                       "{r|低头看板}：重心跑掉，一下就坐倒。"], 0.3),
    ("drill", 0.2, ["练习：从雪道一边飘到另一边，{w|来回5趟}。",
                    "过关：想飘就飘、{w|想停就停}，板头不冲下去。"], 0.3),
    ("end", 0.2, [("下一课：{w|第一次换刃}。", 2.6)], 0.3),
]
SUBS, SEC, DUR = timeline(SECTIONS)

FOOT = {
    "hook0": ("3378", 6.0, 0.30, 0.45),
    "hook1": ("3373", 3.0, 0.45, 0.60),
    "pass": ("3344", 5.5, 0.35, 0.50),
    "end": ("3348", 0.5, 0.40, 0.55),
}

KEYS = ("L", [0.0, 1.0, 4.4, 5.6, L_END])
WHY = [("T", 0.0, 1.6), ("T", 1.6, 3.0), ("T", 3.0, T_END)]
MIST = [("W", 0.0, 3.3), ("U", 0.0, 3.4), ("D", 0.0, 2.8)]
DRILL = ("L", 1.0, L_END)
plan = epkit.std_plan(globals())
music_hits = epkit.std_hits(globals())

STAMP = "左右飘"
CHIPS = ["推坡停稳", "压前脚", "回中停", "压后脚"]
KEY_TAGS = [("后刃立住 · 停稳", "GOLD", None, ["footL", "footR"]),
            ("看板头 · 压前脚 → 往前飘", "ICE", None, ["footR"]),
            ("回到中间 · 脚尖勾起 → 停", "GREEN", "v", ["footL", "footR"]),
            ("看板尾 · 压后脚 → 往回飘", "ICE", None, ["footL"])]
MIST_LABS = ["压前脚太多", "只扭上身", "低头看板"]
MIST_RINGS = ["footR", "chest", "head"]
DRILL_TAGS = ("一边飘到另一边", "来回 5 趟")
PASS_TAGS = ("想飘就飘、想停就停", "板头不冲下去")
NEXT = "第一次换刃"


def WHY_DRAW(c, t, K, pts):
    from vert import window, ramp
    w0, w1, ws = SEC["why"]
    a = window(t, w0 + 0.2, w1, 0.3)
    K.dim(c, a * 0.8)
    cols = [K.GREEN, K.GREEN, K.GOLD, K.RED]
    when = [ws[1][1] + 0.3, ws[1][1] + 1.3, ws[2][1] + 0.3, ws[2][1] + 1.6]
    items = [(f"偏 {g}°", SHARE[g], cols[i], when[i], None) for i, g in enumerate(ANGLES)]
    K.bars(c, t, a * ramp(t, ws[0][1] + 0.6, ws[0][1] + 1.0), "板头往下偏多少度 → 下滑力有多少顺着板", items, 110, unit="%",
           edge=K.ICE, foot="示意 · 顺着板的份额 = sin(偏角)；偏 90° 就是板头正对下坡")


overlay = epkit.std_overlay(globals())

COVER = dict(title=NAME, sub="像树叶一样左右飘", items=["推坡停稳", "压前脚", "回中停", "压后脚"],
             perf="L", p=3.0, cam=((1.5, 3.0, 1.05), (0.0, 0.0, 0.55), 40), bg=("3378", 8.0), set=dict(broll=0, yaw=0))

if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), SHARE)
