"""《单板新手课》第13课：中级道怎么滑。坡更陡：加速度 a = g(sinθ − μcosθ)。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "newbie-lib"))
from epbase import plain, timeline, pw, key, ease
import epkit, turns

FPS = 30
LESSON = 13
SERIES = "单板新手课"
NAME = "中级道怎么滑"
TITLE = f"第{LESSON}课 · {NAME}"
STYLE = "day"
MUSIC = "drive"
TRACK = (32, 0.0)              # Mixkit 免费音乐 #32 Driving Ambition
MARKS = True

SLOPE = 18.0                                         # 示意：中级道
MU = 0.10
ANGLES = [10, 18, 25]                                # 初级 / 中级 / 高级 的示意坡度
KMH_PER_S = {a: round(9.81 * (math.sin(math.radians(a)) - MU * math.cos(math.radians(a))) * 3.6, 1) for a in ANGLES}

BASE = dict(slope=SLOPE, arm=25, ab=38, elb=25, knee=(0.0, 1.0, 0.25), trail=1, pz=0.78)


def perf(segs, v=2.6, extra0=None, **kw):
    keys, wp, tws, t_end, marks = turns.path(segs, v=v, base=BASE, **kw)
    k0 = dict(BASE, gx=0.0, gy=0.0, yaw=0.0, broll=18, tilt=10, tw=wp, tws=tws, tn=0)
    k0.update(extra0 or {})
    return [(0.0, k0)] + keys + [(t_end + 0.5, dict())], t_end + 0.5, marks


# M：中级道上的完整弯（多横切、转到横过来）
M, M_END, M_M = perf([("line", 1.6), ("arc", 180, 2.6, 0.6), ("line", 1.4), ("arc", -180, 2.6, 0.6), ("line", 1.4), ("arc", 180, 2.6, 0.6),
                      ("line", 1.0)], emax=22, rise=0.06)
# 错误1：怕陡往山上靠（后仰）
_b, _bt, _ = perf([("line", 1.4), ("arc", 100, 2.6)], emax=20, extra0=dict(tilt=22, px=-0.10))
B = [(t, dict(d, tilt=d.get("tilt", 0) + 14, px=-0.12) if "gx" in d else d) for t, d in _b[:-1]] + turns.fall(_bt, "back", tilt=40)
# 错误2：弯太浅，一路加速
Z, Z_END, _ = perf([("arc", 30, 2.6), ("arc", -60, 2.6), ("arc", 60, 2.6), ("arc", -60, 2.6)], v=3.6, yaw0=75)
Z[0][1].update(yaw=75, broll=4)
Z = Z[:-1] + [(Z_END - 0.2, dict(arm=65, ab=50, tilt=14))]
# 错误3：在坡中间停下（挡住上面的人看不到的地方）
S, S_END, _ = perf([("line", 1.6), ("arc", 160, 2.6), ("line", 0.4)], emax=22)
S = S[:-1] + [(S_END + 0.4, dict(broll=-22)), (S_END + 2.0, dict())]

PERF = dict(M=M, B=B, Z=Z, S=S)
SHOT_PERF = dict(M="M", T="M", B="B", Z="Z", S="S")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    cx = 0.8 * gx + 0.2 * 1.5
    if shot == "T":                     # 侧面远一点：看得出坡有多陡
        tx, ty, tz = _slope((gx, gy, 0.5), s)                 # 跟着人，从正侧面平视：坡面是一条斜线
        return (tx + 7.0, ty, tz + 0.4), (tx, ty, tz - 0.2), 30
    pos, tgt = (cx + 1.4, gy + 4.8, 2.6), (cx, gy - 0.4, 0.45)
    return _slope(pos, s), _slope(tgt, s), 30


def extra_points(P, J):
    from mathutils import Vector
    m = J["board_m"]
    return {"board": m @ Vector((0, 0, 0.02)), "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)),
            "footR": m @ Vector((0.26, 0, 0.03)), "footL": m @ Vector((-0.26, 0, 0.03))}


import epbase
epbase.CPS = 5.2
SECTIONS = [
    ("hook", 0.2, ["第一次上中级道，往下一看{r|腿就软}？",
                   "其实只要改{w|四个地方}。"], 0.1),
    ("keys", 0.3, ["①先看坡：在{w|宽、缓}的地方起弯。",
                   "②身体{w|垂直坡面}，别往山上靠。",
                   "③弯转得{w|更完整}，多横切一段。",
                   "④太陡就{w|落叶飘}下去，不丢人。"], 0.5),
    ("why", 0.2, ["坡陡一点，速度涨得快很多。",
                  f"10°的坡：每秒时速多约{{g|{KMH_PER_S[10]:.0f}公里}}；18°：约{{w|{KMH_PER_S[18]:.0f}公里}}；",
                  f"25°：约{{r|{KMH_PER_S[25]:.0f}公里}}。所以弯要更完整。"], 0.5),
    ("mistakes", 0.2, ["{r|怕陡往山上靠}：板从脚下冲出去。",
                       "{r|弯太浅}：一路加速，越来越怕。",
                       "{r|停在坡中间}：上面的人看不到你。"], 0.3),
    ("drill", 0.2, ["练习：先在中级道{w|最缓的一段}连做4个弯。",
                    "过关：全程控制在{w|自己敢滑}的速度。"], 0.3),
    ("end", 0.2, [("下一课：{w|反脚滑行}。", 2.6)], 0.3),
]
SUBS, SEC, DUR = timeline(SECTIONS)

FOOT = {
    "hook0": ("3380", 7.0, 0.30, 0.45),
    "hook1": ("3378", 9.0, 0.45, 0.60),
    "pass": ("4016", 3.0, 0.45, 0.60),
    "end": ("3348", 3.5, 0.40, 0.55),
}

KEYS = ("M", [0.0, 0.5, M_M[1][0] - 0.2, M_M[2][0] - 0.2, M_END])
WHY = [("T", 0.0, M_END)]
MIST = [("B", 0.0, B[-1][0]), ("Z", 0.0, Z[-1][0]), ("S", 0.0, S[-1][0])]
DRILL = ("M", 0.0, M_END)
plan = epkit.std_plan(globals())
music_hits = epkit.std_hits(globals())

STAMP = "改四个地方"
CHIPS = ["宽缓处起弯", "垂直坡面", "弯更完整", "太陡就飘"]
KEY_TAGS = [("先看坡 · 宽、缓的地方起弯", "ICE", None, ["head"]),
            ("身体垂直坡面 · 别往山上靠", "GREEN", "v", ["chest"]),
            ("多横切 · 弯转到横过来", "GOLD", None, ["board"]),
            ("太陡 → 落叶飘下去", "GOLD", None, ["board"])]
MIST_LABS = ["往山上靠", "弯太浅", "停在坡中间"]
MIST_RINGS = ["pelvis", "nose", "board"]
DRILL_TAGS = ("中级道最缓的一段", "连做 4 个弯")
PASS_TAGS = ("速度在自己敢滑的范围", "停在雪道边上")
NEXT = "反脚滑行"


def WHY_DRAW(c, t, K, pts):
    from vert import window, stroke_text, DIM
    w0, w1, ws = SEC["why"]
    a = window(t, w0 + 0.2, w1, 0.3)
    K.dim(c, a * 0.6)
    cols = [K.GREEN, K.GOLD, K.RED]
    when = [ws[1][1] + 0.4, ws[1][1] + 2.4, ws[2][1] + 0.4]
    items = [(f"{g}° 的坡", KMH_PER_S[g], cols[i], when[i], ("初级", "中级", "高级")[i]) for i, g in enumerate(ANGLES)]
    K.bars(c, t, a, "板头朝下不刹车：每过 1 秒，时速多多少", items, 13, unit=" km/h", edge=K.GOLD,
           foot="示意 · 摩擦系数取 0.1；各国雪道分级标准不同，坡度只作参考")


overlay = epkit.std_overlay(globals())

COVER = dict(title=NAME, sub="往下一看腿就软？改四个地方", items=["宽缓处起弯", "垂直坡面", "弯更完整", "太陡就飘"],
             perf="M", p=2.0, cam=((1.5, 3.0, 1.05), (0.0, 0.0, 0.55), 40), bg=("3380", 7.5), set=dict(broll=0, yaw=0, tilt=0))

if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), KMH_PER_S, "M_END", round(M_END, 2))
