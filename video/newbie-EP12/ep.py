"""《单板新手课》第12课：起伏和压板。换刃时站高卸力，弯中间压低、腿撑住；转弯时腿要扛的力 = 体重 × √(1 + (v²/(gR))²)。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "newbie-lib"))
from epbase import plain, timeline, pw, key, ease
import epkit, turns

FPS = 30
LESSON = 12
SERIES = "单板新手课"
NAME = "起伏和压板"
TITLE = f"第{LESSON}课 · {NAME}"
STYLE = "day"
MUSIC = "drive"
TRACK = (1117, 0.0)            # Mixkit 免费音乐 #1117 Proud of You
MARKS = True

SLOPE = 12.0
R_TURN = 6.0
SPEEDS = [15, 20, 30]                                              # km/h
LOAD = {v: round(math.sqrt(1 + ((v / 3.6) ** 2 / (9.81 * R_TURN)) ** 2), 2) for v in SPEEDS}   # 几倍体重

BASE = dict(slope=SLOPE, arm=25, ab=38, elb=25, knee=(0.0, 1.0, 0.25), trail=1, pz=0.80)


def perf(segs, v=2.6, extra0=None, **kw):
    keys, wp, tws, t_end, marks = turns.path(segs, v=v, base=BASE, **kw)
    k0 = dict(BASE, gx=0.0, gy=0.0, yaw=0.0, broll=14, tilt=10, tw=wp, tws=tws, tn=0)
    k0.update(extra0 or {})
    return [(0.0, k0)] + keys + [(t_end + 0.5, dict())], t_end + 0.5, marks


# U：大起伏的 S 弯（换刃站高、弯中间压低）
U, U_END, U_M = perf([("line", 1.0), ("arc", 180, 3.0), ("line", 0.6), ("arc", -180, 3.0), ("line", 0.6), ("arc", 180, 3.0), ("line", 0.6)],
                     rise=0.14, emax=24)
# 错误1：一直蹲着不起伏
D, D_END, _ = perf([("line", 1.0), ("arc", 180, 3.0), ("line", 0.6), ("arc", -180, 3.0)], rise=0.0, emax=20)
D = [(t, dict(d, pz=0.66) if "gx" in d else d) for t, d in D]
# 错误2：站起来时往后仰，换刃后坐倒
_b, _bt, _ = perf([("line", 1.0), ("arc", 180, 3.0), ("line", 0.6), ("arc", -80, 3.0)], rise=0.14, emax=22)
B = _b[:-1] + turns.fall(_bt - 0.5, "back", tilt=28, px=-0.12)
# 错误3：压板时弯腰撅屁股
H, H_END, _ = perf([("line", 1.0), ("arc", 180, 3.0), ("line", 0.6)], rise=0.06, emax=18)
H = [(t, dict(d, tilt=-32, py=-0.12, curl=15) if "gx" in d else d) for t, d in H]

PERF = dict(U=U, D=D, B=B, H=H)
SHOT_PERF = dict(U="U", T="U", D="D", B="B", H="H")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    cx = 0.8 * gx + 0.2 * 1.5
    pos, tgt = (cx + 2.2, gy + 4.4, 1.6), (cx, gy - 0.2, 0.55)              # 低一点的机位，看得清身体高低
    return _slope(pos, s), _slope(tgt, s), 30


def extra_points(P, J):
    from mathutils import Vector
    m = J["board_m"]
    return {"board": m @ Vector((0, 0, 0.02)), "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)),
            "footR": m @ Vector((0.26, 0, 0.03)), "footL": m @ Vector((-0.26, 0, 0.03))}


import epbase
epbase.CPS = 5.2
SECTIONS = [
    ("hook", 0.2, ["转弯总是很僵、{r|腿很酸}？",
                   "试试{w|起伏}：一高一低，有节奏。"], 0.1),
    ("keys", 0.3, ["①换刃时{w|站起来}，板变轻，好转。",
                   "②进弯后慢慢{w|往下压}。",
                   "③弯中间最低，腿{w|用力撑住}。",
                   "④弯尾{w|吸收}一下，再站起来换刃。"], 0.5),
    ("why", 0.2, ["为什么弯中间要压？那时腿受力{w|最大}。",
                  f"半径{R_TURN:.0f}米的弯：15 km/h 约{{g|{LOAD[15]}倍}}体重，",
                  f"30 km/h 就到约{{r|{LOAD[30]}倍}}。腿弯着才扛得住。"], 0.5),
    ("mistakes", 0.2, ["{r|一直蹲着}：没有节奏，腿很快就酸。",
                       "{r|站起来时往后仰}：换刃后坐倒。",
                       "{r|压板时弯腰撅屁股}：重心跑到后面。"], 0.3),
    ("drill", 0.2, ["练习：连续S弯，{w|嘴里数}“起——压——”。",
                    "过关：每个弯都有{w|一起一压}，换刃很轻松。"], 0.3),
    ("end", 0.2, [("下一课：{w|中级道怎么滑}。", 2.8)], 0.3),
]
SUBS, SEC, DUR = timeline(SECTIONS)

FOOT = {
    "hook0": ("3378", 2.0, 0.55, 0.70),
    "hook1": ("3380", 6.0, 0.40, 0.55),
    "pass": ("3344", 3.0, 0.50, 0.65),
    "end": ("4016", 9.0, 0.40, 0.55),
}

KEYS = ("U", [0.0, U_M[1][0] - 0.3, U_M[1][0] + 1.0, (U_M[1][0] + U_M[1][1]) / 2 + 0.3, U_END])
WHY = [("T", 0.0, U_END)]
MIST = [("D", 0.0, D_END), ("B", 0.0, B[-1][0]), ("H", 0.0, H_END)]
DRILL = ("U", 0.0, U_END)
plan = epkit.std_plan(globals())
music_hits = epkit.std_hits(globals())

STAMP = "一起一压"
CHIPS = ["换刃站起", "进弯下压", "弯中撑住", "弯尾吸收"]
KEY_TAGS = [("换刃 · 站起来 → 板变轻", "ICE", None, ["pelvis"]),
            ("进弯 · 慢慢往下压", "GOLD", None, ["kneeL", "kneeR"]),
            ("弯中间最低 · 腿撑住", "GOLD", None, ["kneeL", "kneeR"]),
            ("弯尾吸收 → 再站起", "GREEN", "v", ["pelvis"])]
MIST_LABS = ["一直蹲着", "站起往后仰", "压板弯腰"]
MIST_RINGS = ["kneeL", "pelvis", "pelvis"]
DRILL_TAGS = ("连续 S 弯", "数 “起——压——”")
PASS_TAGS = ("每个弯一起一压", "换刃很轻松")
NEXT = "中级道怎么滑"


def WHY_DRAW(c, t, K, pts):
    from vert import window
    w0, w1, ws = SEC["why"]
    a = window(t, ws[0][1] + 0.8, w1, 0.3)
    K.dim(c, a * 0.75)
    cols = [K.GREEN, K.GOLD, K.RED]
    when = [ws[1][1] + 0.5, ws[1][1] + 2.2, ws[2][1] + 0.5]
    items = [(f"{v} km/h", LOAD[v], cols[i], when[i], None) for i, v in enumerate(SPEEDS)]
    K.bars(c, t, a, f"半径 {R_TURN:.0f} 米的弯，腿要扛几倍体重", items, 1.8, unit=" 倍", edge=K.GOLD, fmt="{:.2f}",
           foot="示意 · 匀速圆周：体重 × √(1 + (v²/gR)²)，没算坡度和起伏本身")


overlay = epkit.std_overlay(globals())

COVER = dict(title=NAME, sub="一高一低，转弯不再僵", items=["换刃站起", "进弯下压", "弯中撑住", "弯尾吸收"],
             perf="U", p=2.0, cam=((1.5, 3.0, 1.05), (0.0, 0.0, 0.55), 40), bg=("3378", 3.0), set=dict(broll=0, yaw=0, tilt=0))

if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), LOAD, "U_END", round(U_END, 2))
