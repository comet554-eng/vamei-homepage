"""《单板新手课》第9课：用转弯控速。轨迹用 newbie-lib/turns.py。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "newbie-lib"))
from epbase import plain, timeline, pw, key, ease
import epkit, turns

FPS = 30
LESSON = 9
SERIES = "单板新手课"
NAME = "用转弯控速"
TITLE = f"第{LESSON}课 · {NAME}"
STYLE = "day"
MUSIC = "drive"
TRACK = (729, 0.0)             # Mixkit 免费音乐 #729 Pop Track 03
MARKS = True

# ------------------------------------------------------------------ 示意模型：速度随时间（见 方案.md）
SLOPE, MU, CD = 12.0, 0.10, 0.0026          # 坡度、摩擦系数、空气阻力系数（0.5ρCdA/m，示意）
G = 9.81


def sim(amp, T=12.0, period=3.0, v0=3.0, dt=0.05):
    """板头和下坡线的夹角 β 按正弦来回摆（幅度 amp 度）；顺着行进方向：a = g·sinθ·cosβ − μ·g·cosθ − c·v²。"""
    v, out, t = v0, [], 0.0
    th = math.radians(SLOPE)
    while t <= T + 1e-9:
        out.append((t, v * 3.6))
        b = math.radians(amp * math.sin(2 * math.pi * t / period))
        a = G * math.sin(th) * math.cos(b) - MU * G * math.cos(th) - CD * v * v
        v = max(0.5, v + a * dt); t += dt
    return out


CURVES = [("直着冲", (1.0, 0.36, 0.30), sim(0)), ("浅弯（±30°）", (1.0, 0.78, 0.36), sim(30)), ("完整弯（±90°）", (0.40, 0.90, 0.55), sim(90))]
END_KMH = [round(cv[2][-1][1]) for cv in CURVES]

BASE = dict(slope=SLOPE, arm=22, ab=35, elb=25, knee=(0.0, 1.0, 0.25), trail=1, pz=0.80)


def perf(segs, v=2.2, yaw0=0.0, extra0=None, **kw):
    keys, wp, tws, t_end, marks = turns.path(segs, v=v, yaw0=yaw0, base=BASE, **kw)
    k0 = dict(BASE, gx=0.0, gy=0.0, yaw=yaw0, broll=turns.edge_for(yaw0), tilt=10, tw=wp, tws=tws, tn=0)
    k0.update(extra0 or {})
    return [(0.0, k0)] + keys, t_end, marks


# C：完整的“C”形弯：每个弯都转到横过来，弯尾搓一下
C, C_END, C_MARKS = perf([("line", 0.8), ("arc", 180, 2.4), ("line", 0.6, 0.7), ("arc", -180, 2.4), ("line", 0.6, 0.7),
                          ("arc", 180, 2.4), ("line", 0.6)], rise=0.05)
C = C + [(C_END + 0.5, dict())]; C_END += 0.5
# Z：错误1——弯太浅，板头一直朝下：越来越快
Z, Z_END, _ = perf([("arc", 30, 2.4), ("arc", -60, 2.4), ("arc", 60, 2.4), ("arc", -60, 2.4), ("arc", 60, 2.4)], v=3.2, yaw0=75)
Z = Z + [(Z_END + 0.3, dict(arm=60, ab=45, tilt=12))]; Z_END += 0.3
# P：错误2——一直用后刃推坡刹车：慢是慢，腿很累
P = [(0.0, dict(BASE, broll=18, tilt=10, tw=(0.0, 0.0), tn=0))]
for i in range(4):
    P += [(0.6 + i * 1.0, dict(broll=9, gy=0.55 * i + 0.3, pz=0.74)), (1.1 + i * 1.0, dict(broll=18, gy=0.55 * i + 0.5, pz=0.70 - 0.01 * i))]
P += [(5.0, dict(pz=0.68, tilt=16, curl=10))]
P_END = 5.0
# B：错误3——一快就往后靠：板从脚下冲出去
_b, _bt, _ = perf([("arc", 40, 2.4), ("arc", -40, 2.4)], v=3.2, yaw0=70, extra0=dict(tilt=18, px=-0.10))
B = _b + turns.fall(_bt, "back", tilt=30)

PERF = dict(C=C, Z=Z, P=P, B=B)
SHOT_PERF = dict(C="C", T="C", Z="Z", P="P", B="B")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    cx = 0.8 * gx + 0.2 * 1.2
    if shot == "P":
        pos, tgt = (gx + 1.5, gy + 3.2, 2.0), (gx, gy, 0.45)
    else:
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
    ("hook", 0.2, ["会转弯了，可是{r|越滑越快}？",
                   "不用刹车，{w|弯本身就是刹车}。"], 0.1),
    ("keys", 0.3, ["①每个弯都走到{w|板横过来}，再换刃。",
                   "②弯的形状像{w|“C”}，不是“Z”。",
                   "③弯尾{w|轻轻搓一下雪}，速度就掉一点。",
                   "④越快、越陡，弯就转得{w|越完整}。"], 0.5),
    ("why", 0.2, ["同一段坡，三种滑法，速度差多少？",
                  f"12秒后：直冲约{{r|{END_KMH[0]} km/h}}，浅弯约{{w|{END_KMH[1]} km/h}}，",
                  f"完整的弯基本{{g|稳在 {END_KMH[2]} km/h 左右}}。"], 0.5),
    ("mistakes", 0.2, ["{r|弯太浅}：板头一直朝下，越滑越快。",
                       "{r|一直推坡刹车}：慢是慢，腿很快就酸。",
                       "{r|一快就往后靠}：板冲出去，坐倒。"], 0.3),
    ("drill", 0.2, ["练习：同一段坡，先滑{w|浅弯}，再滑{w|完整弯}。",
                    "过关：靠转弯把速度控制在{w|慢跑}那么快。"], 0.3),
    ("end", 0.2, [("下一课：{w|搓雪和刻滑}。", 2.6)], 0.3),
]
SUBS, SEC, DUR = timeline(SECTIONS)

FOOT = {
    "hook0": ("3380", 3.0, 0.40, 0.55),
    "hook1": ("3378", 14.0, 0.40, 0.55),
    "pass": ("4016", 6.0, 0.30, 0.45),
    "end": ("3381", 15.0, 0.40, 0.55),
}

KEYS = ("C", [0.0, C_MARKS[1][0] + 0.3, (C_MARKS[1][0] + C_MARKS[1][1]) / 2, C_MARKS[2][0], C_END])
WHY = [("T", 0.0, C_END)]
MIST = [("Z", 0.0, Z_END), ("P", 0.0, P_END), ("B", 0.0, B[-1][0])]
DRILL = ("C", 0.0, C_END)
plan = epkit.std_plan(globals())
music_hits = epkit.std_hits(globals())

STAMP = "弯就是刹车"
CHIPS = ["转到横过来", "C不是Z", "弯尾搓一下", "快就多转"]
KEY_TAGS = [("每个弯都转到板横过来", "GOLD", None, ["footL", "footR"]),
            ("要 C 形弯，不要 Z 形弯", "ICE", None, ["board"]),
            ("弯尾轻轻搓雪 → 速度掉", "GREEN", "v", ["tail"]),
            ("越快、越陡 → 转得越完整", "GOLD", None, ["board"])]
MIST_LABS = ["弯太浅", "一直推坡刹车", "一快就往后靠"]
MIST_RINGS = ["nose", "kneeL", "pelvis"]
DRILL_TAGS = ("先浅弯，再完整弯", "感受速度差")
PASS_TAGS = ("慢跑那么快", "不靠推坡刹车")
NEXT = "搓雪和刻滑"


def WHY_DRAW(c, t, K, pts):
    from vert import window
    w0, w1, ws = SEC["why"]
    a = window(t, w0 + 0.2, w1, 0.3)
    K.dim(c, a * 0.8)
    t0 = ws[0][1] + 1.0
    series = [(n, col, pts_, t0 + 0.3 * i, 3.0) for i, (n, col, pts_) in enumerate(CURVES)]
    K.lines(c, t, a, "同一段 12° 的坡：时速随时间变化", series, 12, 50, xlab="秒", ylab="km/h",
            xticks=(0, 3, 6, 9, 12), yticks=(10, 20, 30, 40, 50), foot="示意模型：只算重力、摩擦（0.1）和空气阻力，弯形按正弦摆动")


overlay = epkit.std_overlay(globals())

COVER = dict(title=NAME, sub="不用刹车，弯就是刹车", items=["转到横", "C不是Z", "弯尾搓", "快就多转"],
             perf="C", p=2.0, cam=((1.5, 3.0, 1.05), (0.0, 0.0, 0.55), 40), bg=("3380", 4.0), set=dict(broll=0, yaw=0))

if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), END_KMH, "C_END", round(C_END, 2))
