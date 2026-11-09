"""《单板新手课》第15课：入门刻滑。刻滑弯半径 R ≈ R侧切·cos θ；身体倒进弯里 θ 时要的速度 v = √(g·R·tan θ)（简化模型）。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "newbie-lib"))
from epbase import plain, timeline, pw, key, ease
import epkit, turns

FPS = 30
LESSON = 15
SERIES = "单板新手课"
NAME = "入门刻滑"
TITLE = f"第{LESSON}课 · {NAME}"
STYLE = "day"
MUSIC = "drive"
TRACK = (1001, 0.0)            # Mixkit 免费音乐 #1001 I Do!
MARKS = True

SLOPE = 14.0
RSC = 7.0
EDGES = [30, 45, 60]
NEED_KMH = {e: round(math.sqrt(9.81 * RSC * math.cos(math.radians(e)) * math.tan(math.radians(e))) * 3.6) for e in EDGES}

BASE = dict(slope=SLOPE, arm=28, ab=40, elb=25, knee=(0.0, 1.0, 0.25), trail=1, pz=0.80)
G = 0.04


def perf(segs, v=3.4, extra0=None, **kw):
    keys, wp, tws, t_end, marks = turns.path(segs, v=v, base=BASE, **kw)
    k0 = dict(BASE, gx=0.0, gy=0.0, yaw=0.0, broll=20, tilt=10, tw=wp, tws=tws, tn=0)
    k0.update(extra0 or {})
    return [(0.0, k0)] + keys + [(t_end + 0.5, dict())], t_end + 0.5, marks


# C：刻滑 S 弯（立刃高、身体往弯里倒、雪痕一条线）
C, C_END, C_M = perf([("line", 1.2, G), ("arc", 180, 5.0, G), ("line", 0.6, G), ("arc", -180, 5.0, G), ("line", 0.6, G)],
                     emax=42, lean=28)
# H：先只做后刃横切练立刃（练习用）
H, H_END, _ = perf([("line", 1.0, G), ("arc", 60, 6.0, G), ("arc", -20, 8.0, G), ("line", 1.0, G)], emax=35, lean=20)
# 错误1：速度太慢就立高刃：倒进弯里
F, F_END, _ = perf([("line", 0.8, G), ("arc", 60, 3.0, G)], v=1.4, emax=50, lean=34)
F = F[:-1] + turns.fall(F_END - 0.5, "back", tilt=30)
# 错误2：甩板尾：一下变回搓雪
SK, SK_END, _ = perf([("line", 1.0, G), ("arc", 120, 4.0, 1.1)], emax=20, skid=40)
# 错误3：只倒上身（A 字腿）：板没立起来
A, A_END, _ = perf([("line", 1.0, 0.5), ("arc", 120, 4.0, 0.8)], emax=10, skid=20)
A = [(t, dict(d, tilt=(d["tilt"] * 3 if "tilt" in d else 0), pz=0.94, curl=12) if "gx" in d else d) for t, d in A]

PERF = dict(C=C, H=H, F=F, SK=SK, A=A)
SHOT_PERF = dict(C="C", T="C", H="H", F="F", SK="SK", A="A")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    cx = 0.9 * gx + 0.1 * 2.5
    if shot == "T":
        pos, tgt = (cx + 1.0, gy + 7.0, 5.0), (cx, gy - 1.5, 0.0)
    else:
        pos, tgt = (cx + 1.8, gy + 5.0, 2.2), (cx, gy - 0.4, 0.5)
    return _slope(pos, s), _slope(tgt, s), 30


def extra_points(P, J):
    from mathutils import Vector
    m = J["board_m"]
    return {"board": m @ Vector((0, 0, 0.02)), "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)),
            "footR": m @ Vector((0.26, 0, 0.03)), "footL": m @ Vector((-0.26, 0, 0.03))}


import epbase
epbase.CPS = 5.2
SECTIONS = [
    ("hook", 0.2, ["新手课最后一课：{w|入门刻滑}。",
                   "回头一看，雪上只有{w|一条线}。"], 0.1),
    ("keys", 0.3, ["①选{w|宽、平整}的雪道，速度要够。",
                   "②先只做{w|后刃横切}，练把刃立高。",
                   "③刃立高、{w|板不甩}，让板自己转过来。",
                   "④回头看雪痕：{w|一条线}就对了。"], 0.5),
    ("why", 0.2, ["为什么刻滑要有速度？",
                  f"身体要倒进弯里，靠速度撑着：立30°约要{{w|{NEED_KMH[30]} km/h}}，",
                  f"45°约{{w|{NEED_KMH[45]} km/h}}，60°约{{r|{NEED_KMH[60]} km/h}}。太慢就会倒。"], 0.5),
    ("mistakes", 0.2, ["{r|速度太慢就立高刃}：人倒进弯里。",
                       "{r|甩板尾}：一下又变回搓雪。",
                       "{r|只倒上身}：腿没送进去，板立不起来。"], 0.3),
    ("drill", 0.2, ["练习：宽雪道上只做{w|后刃横切}，再接{w|前刃}。",
                    "过关：连续4个弯，雪痕{w|都是细线}。"], 0.3),
    ("end", 0.2, [("新手课毕业！{w|评论区}晒晒你的雪痕。", 3.4)], 0.3),
]
SUBS, SEC, DUR = timeline(SECTIONS)

FOOT = {
    "hook0": ("3373", 0.5, 0.40, 0.55),
    "hook1": ("3381", 16.0, 0.40, 0.55),
    "pass": ("3344", 4.0, 0.40, 0.55),
    "end": ("3348", 9.0, 0.40, 0.55),
}

KEYS = ("C", [0.0, 0.6, C_M[1][0] + 0.6, (C_M[1][0] + C_M[1][1]) / 2, C_END])
WHY = [("T", 0.0, C_END)]
MIST = [("F", 0.0, F[-1][0]), ("SK", 0.0, SK_END), ("A", 0.0, A_END)]
DRILL = ("H", 0.0, H_END)
plan = epkit.std_plan(globals())
music_hits = epkit.std_hits(globals())

STAMP = "一条线"
CHIPS = ["速度要够", "后刃练立刃", "板不甩", "看雪痕"]
KEY_TAGS = [("宽、平整的雪道 · 速度要够", "ICE", None, ["board"]),
            ("先只做后刃横切", "GOLD", None, ["footL", "footR"]),
            ("刃立高 · 板不甩", "GREEN", "v", ["kneeL", "kneeR"]),
            ("雪痕一条线 = 对了", "GREEN", "v", ["tail"])]
MIST_LABS = ["太慢就立高刃", "甩板尾", "只倒上身"]
MIST_RINGS = ["pelvis", "tail", "chest"]
DRILL_TAGS = ("后刃横切 → 前刃横切", "宽雪道")
PASS_TAGS = ("连续 4 个弯", "雪痕都是细线")
NEXT = "毕业啦"
END_HEAD = "新手课"


def WHY_DRAW(c, t, K, pts):
    from vert import window
    w0, w1, ws = SEC["why"]
    a = window(t, ws[0][1] + 0.8, w1, 0.3)
    K.dim(c, a * 0.75)
    cols = [K.GOLD, (1.0, 0.6, 0.3), K.RED]
    when = [ws[1][1] + 1.6, ws[2][1] + 0.3, ws[2][1] + 1.4]
    items = [(f"立 {e}°", NEED_KMH[e], cols[i], when[i], None) for i, e in enumerate(EDGES)]
    K.bars(c, t, a, f"刻滑时身体倒到这个角度，大约要多快（侧切 {RSC:.0f} 米）", items, 35, unit=" km/h", edge=K.GOLD,
           foot="简化模型：半径 ≈ 侧切×cosθ，速度 ≈ √(g·半径·tanθ)；没算坡度和起伏")


overlay = epkit.std_overlay(globals())
LICAI = dict(end="蹦跳欢呼")

COVER = dict(title=NAME, sub="雪痕只有一条线", items=["速度要够", "练立刃", "板不甩", "看雪痕"],
             perf="C", p=2.0, cam=((1.5, 3.0, 1.05), (0.0, 0.0, 0.55), 40), bg=("3373", 2.0), set=dict(broll=0, yaw=0, tilt=0, py=0))

if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), NEED_KMH, "C_END", round(C_END, 2))
