"""《单板新手课》第8课：连续S弯。轨迹用 newbie-lib/turns.py 生成（参考《单板从0到刻滑》第8课的弯形）。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "newbie-lib"))
from epbase import plain, timeline, pw, key, ease
import epkit, turns

FPS = 30
LESSON = 8
SERIES = "单板新手课"
NAME = "连续S弯"
TITLE = f"第{LESSON}课 · {NAME}"
STYLE = "day"
MUSIC = "drive"
TRACK = (860, 0.0)             # Mixkit 免费音乐 #860 Year 2001
MARKS = True

SLOPE = 12.0
BETAS = [90, 60, 30]                                       # 弯尾板头离下坡线的角度
SHARE = {b: round(100 * math.cos(math.radians(b))) for b in BETAS}   # 下滑力顺着板的份额 ≈ cos β

BASE = dict(slope=SLOPE, arm=22, ab=35, elb=25, knee=(0.0, 1.0, 0.25), trail=1, pz=0.80)


def perf(segs, v=2.2, extra0=None, **kw):
    keys, wp, tws, t_end, marks = turns.path(segs, v=v, base=BASE, **kw)
    k0 = dict(BASE, gx=0.0, gy=0.0, yaw=0.0, broll=14, tilt=10, tw=wp, tws=tws, tn=0)
    k0.update(extra0 or {})
    return [(0.0, k0)] + keys, t_end, marks


# S：后刃横切 → 弯1（换前刃）→ 前刃横切 → 弯2（换后刃）→ 后刃横切 → 弯3 → 停
S, S_END, S_MARKS = perf([("line", 1.6), ("arc", 180, 2.6), ("line", 1.4), ("arc", -180, 2.6), ("line", 1.4),
                          ("arc", 180, 2.6), ("line", 0.8)], rise=0.06)
S = S + [(S_END + 0.6, dict())]
S_END += 0.6
# 每个阶段的表演时间：第一个弯开始、平板（yaw=90）、第一个弯结束、第二个弯结束
T_A0, T_A1 = S_MARKS[1]
T_B1 = S_MARKS[3][1]

# B：错误1——换后刃时往后坐：板从脚下冲出去，坐倒
_b, _bt, _bm = perf([("line", 1.2), ("arc", 180, 2.6), ("line", 1.0), ("arc", -70, 2.6)])
B = _b + turns.fall(_bt, "back", tilt=30, px=-0.12)
# U：错误2——只转上身不压刃：板横着甩出去，搓着往下溜
_u, _ut, _um = perf([("line", 1.2), ("arc", 120, 2.6)])
U = _u + [(_ut + 0.6, dict(twist=60, face=50, broll=2, gy=_u[-1][1]["gy"] + 1.0, arm=60, ab=45)), (_ut + 1.6, dict(gy=_u[-1][1]["gy"] + 2.2)),
          (_ut + 2.0, dict())]
# L：错误3——横切太长、一直犹豫：每个弯之间停住，节奏全断
_l, _lt, _lm = perf([("line", 4.0), ("arc", 180, 2.6), ("line", 4.0)], v=1.6)
L = _l + [(_lt + 0.5, dict())]

PERF = dict(S=S, B=B, U=U, L=L)
SHOT_PERF = dict(S="S", T="S", B="B", U="U", L="L")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    cx = 0.8 * gx + 0.2 * 1.5
    if shot == "T":
        pos, tgt = (cx + 0.6, gy + 6.0, 4.6), (cx, gy - 1.2, 0.0)
    else:
        pos, tgt = (cx + 1.4, gy + 4.8, 2.6), (cx, gy - 0.4, 0.45)
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
    ("hook", 0.2, ["会换一次刃了，{w|连起来}呢？",
                   "前刃、后刃、前刃……这就是{w|S弯}。"], 0.1),
    ("keys", 0.3, ["①一个弯走完，先{w|横切}一小段。",
                   "②眼睛先看{w|下一个弯}，肩膀跟着转。",
                   "③板头过下坡线，{w|换刃}，起身轻一点。",
                   "④新刃把弯{w|走完整}，再接下一个。"], 0.5),
    ("why", 0.2, ["为什么弯要{w|走完整}？",
                  "板头离下坡线越远，下滑力顺着板的份额越小：",
                  "横过来{g|0%}，60°时{w|50%}，只转到30°还有{r|87%}。"], 0.5),
    ("mistakes", 0.2, ["{r|换刃往后坐}：板从脚下冲出去。",
                       "{r|只转上身不压刃}：板横着甩，一路搓下去。",
                       "{r|横切太长、犹豫}：节奏断了，越滑越僵。"], 0.3),
    ("drill", 0.2, ["练习：缓坡上连做{w|6个弯}，数着节奏。",
                    "过关：左右弯一样{w|顺}，中间不停。"], 0.3),
    ("end", 0.2, [("下一课：{w|用转弯控制速度}。", 3.0)], 0.3),
]
SUBS, SEC, DUR = timeline(SECTIONS)

FOOT = {
    "hook0": ("3373", 8.0, 0.40, 0.55),
    "hook1": ("3381", 4.5, 0.50, 0.65),
    "pass": ("3344", 0.5, 0.25, 0.40),
    "end": ("3348", 7.0, 0.40, 0.55),
}

KEYS = ("S", [0.0, T_A0 - 0.3, T_A0 + 0.6, (T_A0 + T_A1) / 2 + 0.3, S_END])
WHY = [("T", 0.0, T_A1), ("T", T_A1, T_B1), ("T", T_B1, S_END)]
MIST = [("B", 0.0, B[-1][0]), ("U", 0.0, U[-1][0]), ("L", 0.0, L[-1][0])]
DRILL = ("S", 0.0, S_END)
plan = epkit.std_plan(globals())
music_hits = epkit.std_hits(globals())

STAMP = "连起来"
CHIPS = ["横切一小段", "看下一个弯", "过线换刃", "走完整"]
KEY_TAGS = [("走完一个弯 · 横切一小段", "GOLD", None, ["footL", "footR"]),
            ("眼睛先看下一个弯", "ICE", None, ["head"]),
            ("过下坡线 · 换刃 · 起身轻一点", "GREEN", "v", ["board"]),
            ("新刃走完整 · 再接下一个", "GREEN", "v", ["footL", "footR"])]
MIST_LABS = ["换刃往后坐", "只转上身不压刃", "横切太长、犹豫"]
MIST_RINGS = ["pelvis", "chest", "board"]
DRILL_TAGS = ("连做 6 个弯", "数着节奏")
PASS_TAGS = ("左右弯一样顺", "中间不停")
NEXT = "用转弯控速"


def WHY_DRAW(c, t, K, pts):
    from vert import window, ramp
    w0, w1, ws = SEC["why"]
    a = window(t, ws[1][1] - 0.2, w1, 0.3)
    K.dim(c, a * 0.7)
    cols = [K.GREEN, K.GOLD, K.RED]
    when = [ws[2][1] + 0.3, ws[2][1] + 1.3, ws[2][1] + 2.6]
    items = [(f"离下坡线 {b}°", SHARE[b], cols[i], when[i], None) for i, b in enumerate(BETAS)]
    K.bars(c, t, a, "弯尾板头离下坡线多少度 → 下滑力顺着板的份额", items, 110, unit="%", edge=K.ICE,
           foot="示意 · 份额 ≈ cos(离下坡线的角度)")


overlay = epkit.std_overlay(globals())

COVER = dict(title=NAME, sub="前刃、后刃，连起来", items=["横切", "看下一个弯", "过线换刃", "走完整"],
             perf="S", p=3.0, cam=((1.5, 3.0, 1.05), (0.0, 0.0, 0.55), 40), bg=("3373", 9.0), set=dict(broll=0, yaw=0))

if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), SHARE, "S_END", round(S_END, 2), S_MARKS)
