"""《单板新手课》第11课：立刃角。刻滑弯半径 R ≈ R侧切·cos(立刃角)（Jentschura & Fahrbach 2004 的理想刻滑模型）。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "newbie-lib"))
from epbase import plain, timeline, pw, key, ease
import epkit, turns

FPS = 30
LESSON = 11
SERIES = "单板新手课"
NAME = "立刃角"
TITLE = f"第{LESSON}课 · {NAME}"
STYLE = "day"
MUSIC = "pop"
TRACK = (923, 0.0)             # Mixkit 免费音乐 #923 Yeah Yeah
MARKS = True

SLOPE = 12.0
RSC = 7.0                                          # 侧切半径（米，成人全能板常见约 7~8 米）
EDGES = [0, 30, 45, 60]
RADIUS = {e: round(RSC * math.cos(math.radians(e)), 1) for e in EDGES}

BASE = dict(slope=SLOPE, arm=25, ab=38, elb=25, knee=(0.0, 1.0, 0.25), trail=1, pz=0.80)


def perf(segs, v=3.0, extra0=None, **kw):
    keys, wp, tws, t_end, marks = turns.path(segs, v=v, base=BASE, **kw)
    k0 = dict(BASE, gx=0.0, gy=0.0, yaw=0.0, broll=14, tilt=10, tw=wp, tws=tws, tn=0)
    k0.update(extra0 or {})
    return [(0.0, k0)] + keys + [(t_end + 0.5, dict())], t_end + 0.5, marks


G = 0.04
# E：低刃大弯 → 高刃小弯（同一块板，刃立得越高弯越小）
E, E_END, E_M = perf([("line", 1.0, G), ("arc", 180, RADIUS[30], G), ("line", 0.6, G), ("arc", -180, RADIUS[60], G), ("line", 0.8, G)],
                     emax=40, lean=26)
# X：原理镜头——人站在原地，立刃 0 → 30 → 45 → 60（后刃）
X = [(0.0, dict(BASE, trail=0, broll=0, tilt=0, pz=0.82))]
for i, e in enumerate(EDGES[1:]):
    X += [(1.0 + 1.6 * i, dict(broll=e, tilt=4 + e * 0.45, py=-0.18 * e / 45, pz=0.80 - 0.15 * e / 60)), (1.8 + 1.6 * i, dict())]
X_END = 1.8 + 1.6 * 2
# A：错误1——只倒上身、腿是直的：板还是平的，一路搓
A, A_END, _ = perf([("line", 0.8, 0.5), ("arc", 140, 3.0, 1.0)], emax=8, skid=30, extra0=dict(), v=2.6)
A = [(t, dict(d, tilt=(d["tilt"] * 2.5 if "tilt" in d else 0), pz=0.95) if "gx" in d else d) for t, d in A]
# F：错误2——刃立得太猛、速度不够：倒进弯里
F, F_END, _ = perf([("line", 0.8, G), ("arc", 60, 2.0, G)], v=1.3, emax=55, lean=34)
F = F[:-1] + turns.fall(F_END - 0.5, "back", tilt=30)
# T：错误3——前后脚不同步：板扭着，弯忽大忽小
T, T_END, _ = perf([("line", 0.8, G), ("arc", 90, 3.0, 0.4), ("arc", 40, 1.6, 0.6), ("arc", 50, 4.0, 0.4)], emax=30, lean=15, skid=12)

PERF = dict(E=E, X=X, A=A, F=F, T=T)
SHOT_PERF = dict(E="E", X="X", A="A", F="F", T="T")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    if shot == "X":                    # 顺着板看过去：看得见板和雪面的夹角
        pos, tgt = (gx + 4.6, gy + 1.6, 1.3), (gx, gy, -0.45)
        return _slope(pos, s), _slope(tgt, s), 34
    cx = 0.8 * gx + 0.2 * 1.5
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
    ("hook", 0.2, ["同一块板，为什么弯能{w|大}也能{w|小}？",
                   "秘密在{w|立刃角}。"], 0.1),
    ("keys", 0.3, ["①立刃角：板面和{w|雪面}之间的夹角。",
                   "②靠{w|脚踝、膝盖、髋}一起把板立起来。",
                   "③上身{w|别跟着倒}，保持平衡。",
                   "④刃立得越高，弯就{w|越小}。"], 0.5),
    ("why", 0.2, [f"板的两条边是弧形的，侧切半径约{{b|{RSC:.0f}米}}。",
                  f"立30°：弯半径约{{w|{RADIUS[30]}米}}；45°约{{w|{RADIUS[45]}米}}；",
                  f"立到60°，只剩约{{r|{RADIUS[60]}米}}。"], 0.5),
    ("mistakes", 0.2, ["{r|只倒上身、腿是直的}：板还是平的。",
                       "{r|速度不够就立太高}：人倒进弯里。",
                       "{r|前后脚不同步}：板扭着，弯忽大忽小。"], 0.3),
    ("drill", 0.2, ["练习：后刃横切，{w|慢慢加立刃}，看弯变小。",
                    "过关：能{w|控制}弯的大小，雪痕一条线。"], 0.3),
    ("end", 0.2, [("下一课：{w|起伏和压板}。", 2.6)], 0.3),
]
SUBS, SEC, DUR = timeline(SECTIONS)

FOOT = {
    "hook0": ("3381", 0.5, 0.40, 0.55),
    "hook1": ("3373", 12.0, 0.35, 0.50),
    "pass": ("4016", 0.5, 0.35, 0.50),
    "end": ("3348", 8.5, 0.40, 0.55),
}

KEYS = ("E", [0.0, 1.2, E_M[1][0] + 0.8, E_M[2][0], E_END])
WHY = [("X", 0.0, 1.8), ("X", 1.8, 3.4), ("X", 3.4, X_END)]
MIST = [("A", 0.0, A_END), ("F", 0.0, F[-1][0]), ("T", 0.0, T_END)]
DRILL = ("E", 0.0, E_END)
plan = epkit.std_plan(globals())
music_hits = epkit.std_hits(globals())

STAMP = "立刃角"
CHIPS = ["什么是立刃", "脚踝膝盖髋", "上身别倒", "越高弯越小"]
KEY_TAGS = [("板面和雪面的夹角", "ICE", None, ["board"]),
            ("脚踝 + 膝盖 + 髋 一起送", "GOLD", None, ["kneeL", "kneeR", "pelvis"]),
            ("上身保持平衡", "GREEN", "v", ["chest"]),
            ("立得越高 → 弯越小", "GOLD", None, ["board"])]
MIST_LABS = ["只倒上身", "速度不够立太高", "前后脚不同步"]
MIST_RINGS = ["chest", "pelvis", "board"]
DRILL_TAGS = ("后刃横切", "慢慢加立刃")
PASS_TAGS = ("能控制弯的大小", "雪痕一条线")
NEXT = "起伏和压板"


def WHY_DRAW(c, t, K, pts):
    from vert import window
    w0, w1, ws = SEC["why"]
    a = window(t, w0 + 0.2, w1, 0.3)
    e = pw([(ws[0][1], 0.0), (ws[1][1], 0.0), (ws[1][1] + 1.0, 30.0), (ws[1][1] + 2.4, 30.0), (ws[1][1] + 3.2, 45.0),
            (ws[2][1], 45.0), (ws[2][1] + 1.0, 60.0)], t)
    cols = [K.ICE, K.GOLD, (1.0, 0.6, 0.3), K.RED]
    when = [ws[0][1] + 1.0, ws[1][1] + 0.8, ws[1][1] + 3.0, ws[2][1] + 0.8]
    items = [(f"立 {g}°", RADIUS[g], cols[i], when[i], None) for i, g in enumerate(EDGES)]
    K.bars(c, t, a, f"立刃角 → 刻滑弯半径（侧切 {RSC:.0f} 米的板）", items, 8.5, unit=" 米", edge=K.ICE, y=1040, h=380, fmt="{:.1f}",
           foot="理想刻滑模型：半径 ≈ 侧切半径 × cos(立刃角)")
    from vert import stroke_text
    stroke_text(c, f"立刃 {e:.0f}°", 60, 390, 64, K.GOLD, a, align="l", stroke=8)


W_HALF = 540
overlay = epkit.std_overlay(globals())

COVER = dict(title=NAME, sub="刃立得越高，弯越小", items=["夹角", "脚踝膝盖髋", "上身别倒", "越高越小"],
             perf="E", p=2.0, cam=((1.5, 3.0, 1.05), (0.0, 0.0, 0.55), 40), bg=("3381", 2.0), set=dict(broll=0, yaw=0, tilt=0, py=0))

if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), RADIUS, "E_END", round(E_END, 2))
