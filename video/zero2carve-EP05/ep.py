"""《单板从0到刻滑》第5课：后刃落叶飘（加原理和数据）。
动作关键帧、镜头、字幕时间都在这里；../zero2carve-lib/render.py 渲 3D，composite.py 叠字幕和数据出片。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "zero2carve-lib"))
from epbase import plain, timeline, pw, key, ease

FPS = 30
TITLE = "第5课 · 后刃落叶飘"
LEVEL = "L1 第一天"
LESSON = 5
SLOPE = 12.0
STOP, SLIDE = 18.0, 9.0
LEAF = 15.0            # 落叶飘时板头（或板尾）朝下偏的角度

# ------------------------------------------------------------------ 原理和数据
ANGLES = [10, 20, 45, 90]                      # 板头朝下偏的角度
SHARE = {a: math.sin(math.radians(a)) for a in ANGLES}   # 下滑力顺着板长方向的份额

# ------------------------------------------------------------------ 动作（表演时间，秒）
BASE = dict(slope=SLOPE, tilt=10, pz=0.80, arm=20, ab=35, elb=25, knee=(0.0, 1.0, 0.25), broll=STOP, trail=1)

# W：错误示范——重心压前脚太多，板头一直往下转，转进滚落线变成直冲，最后坐倒
W = [
    (0.0, dict(BASE, broll=SLIDE, yaw=12, px=0.06, tw=(0.0, 0.0), tn=0)),
    (0.8, dict(gx=0.90, gy=0.30, yaw=25)),
    (1.4, dict(gx=1.60, gy=0.90, yaw=60, px=0.12, tilt=-4, arm=45, ab=40)),
    (1.9, dict(gx=1.85, gy=2.00, yaw=85, broll=5, tilt=14, arm=70, ab=45)),
    (2.4, dict(gx=1.95, gy=3.10, tilt=45, pz=0.45, py=-0.30, arm=-40, ab=25, elb=10, broll=4)),
    (2.9, dict(gy=3.50, tilt=70, pz=0.17, py=-0.50, arm=-30, elb=30, knee=(0.0, 0.3, 1.0))),
    (3.3, dict()),
]
W_TURN = 1.4

# T：俯视原理图——人站在原地，板头朝下转 0 → 10 → 20 → 45 → 90°
T = [(0.0, dict(BASE, trail=0, yaw=0))]
for i, a in enumerate(ANGLES):
    T += [(1.2 + 1.6 * i, dict(yaw=a, px=0.10 if a < 60 else 0.0)), (2.0 + 1.6 * i, dict())]
T_KEYS = [1.2 + 1.6 * i for i in range(len(ANGLES))]
T_END = 2.0 + 1.6 * (len(ANGLES) - 1)

# L：正确的后刃落叶飘——推坡停住 → 重心前脚往前飘 → 回中停住 → 重心后脚往回飘 → 停
WP = (0.0, 0.0, 2.6, 0.75, 2.85, 0.85, 0.25, 1.65, 0.0, 1.75)
L = [
    (0.0, dict(BASE, tw=WP, tn=0)),
    (1.0, dict(pz=0.76)),
    (1.8, dict(px=0.10, yaw=LEAF, broll=SLIDE, pz=0.78)),
    (2.6, dict(gx=0.45, gy=0.12)),
    (4.4, dict(gx=2.60, gy=0.75, tn=1)),
    (5.0, dict(px=0.0, yaw=0, broll=STOP, gx=2.85, gy=0.85, tn=2)),
    (5.6, dict()),
    (6.4, dict(px=-0.10, yaw=-LEAF, broll=SLIDE)),
    (7.2, dict(gx=2.40, gy=0.98)),
    (9.0, dict(gx=0.25, gy=1.65, tn=3)),
    (9.6, dict(px=0.0, yaw=0, broll=STOP, gx=0.0, gy=1.75, tn=4)),
    (10.2, dict()),
]
L_STEPS = [0.0, 1.0, 4.4, 5.6]
L_END = 10.2

PERF = dict(W=W, T=T, L=L)
SHOT_PERF = dict(W="W", T="T", L="L")
COVER3D = dict(perf="L", p=3.4, cam=((1.0, 2.8, 1.0), (0.0, 0.3, 0.45), 34), ring=None)
VO_EXTRA = dict(steps="正确的落叶飘，四步。")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def orbit(cx, cy, r, deg, z):
    a = math.radians(deg); return (cx + r * math.cos(a), cy + r * math.sin(a), z)


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    if shot == "W":      # 下坡方向斜上方，看板头转进滚落线
        pos, tgt = (1.6, 5.4, 2.3), (gx, gy, 0.6)
    elif shot == "T":    # 正上方往下看（上坡在画面上方）
        pos, tgt = (0.0, 0.62, 4.0), (0.0, 0.62, 0.0)
        return _slope(pos, s), _slope(tgt, s), 30
    elif shot == "L":    # 下坡方向看，跟着人左右走
        pos, tgt = (1.4 + 0.8 * (gx - 1.4), gy + 3.7, 2.0), (1.4 + 0.8 * (gx - 1.4), gy + 0.3, 0.62)
    else:
        raise KeyError(shot)
    return _slope(pos, s), _slope(tgt, s), 30


def extra_points(P, J):
    from mathutils import Vector, Matrix
    m = J["board_m"]
    sm = Matrix.Rotation(math.radians(-P["slope"]), 3, "X")
    c = m @ Vector((0, 0, 0.02))
    return {"board": c, "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)),
            "fall": c + sm @ Vector((0, 1.0, 0)), "heel": m @ Vector((0, -0.125, 0.0))}


# ------------------------------------------------------------------ 字幕（不配音：按阅读速度排时间）
SECTIONS = [   # (名字, 开头留白, 字幕, 结尾留白)
    ("hook", 0.3, ["落叶飘，一下就{r|冲出去}了？"], 0.4),
    ("why", 0.3, ["落叶飘，就是在推坡的基础上，{w|左右走}。",
                  "秘诀在前后脚：重心放哪只脚，那一头就{w|往下坡偏}。",
                  "板头朝下偏一个角，下滑的力就有一部分{b|顺着板}走。",
                  "偏10°只有{b|17%}，偏20°有{b|34%}，偏45°就{r|71%}。",
                  "转到正对下坡就是{r|100%}：不是飘，是{r|直冲}。"], 0.4),
    ("steps", 1.2, ["①先推坡，{w|后刃}立住，停稳。",
                    "②重心移到{w|前脚}，板头微微朝下，往前飘。",
                    "③重心回到中间，脚尖抬起来，{w|停住}。",
                    "④重心移到{w|后脚}，板尾朝下，往回飘。"], 0.6),
    ("drill", 0.3, ["初级道上：往前飘五米、停住、往回飘五米，来回三趟。",
                    "过关标准：板头{w|不转过下坡方向}，想停就停。"], 0.4),
    ("end", 0.3, [("下一课：换到{w|前刃}，推坡和落叶飘。", 3.2)], 0.4),
]
SUBS, SEC, DUR = timeline(SECTIONS)


def _q(p, n):
    return round(p * n) / n


def plan():
    out = []
    h0, h1, _ = SEC["hook"]; w0, w1, ws = SEC["why"]; s0, s1, ss = SEC["steps"]; d0, d1, _ = SEC["drill"]
    for i in range(int(DUR * FPS)):
        t = i / FPS
        if t < h1:
            out.append(("W", "W", pw([(0, 0.0), (h1 - 0.8, 2.9), (h1, 3.3)], t - h0)))
        elif t < w1:
            a = [x[1] - w0 for x in ws]
            out.append(("T", "T", _q(pw([(0, 0.0), (a[1], 0.0), (a[1] + 1.4, T_KEYS[0] + 0.4), (a[3], T_KEYS[0] + 0.8),
                                         (a[3] + 1.6, T_KEYS[1] + 0.8), (a[3] + 3.6, T_KEYS[2] + 0.8),
                                         (a[4], T_KEYS[2] + 0.8), (a[4] + 1.6, T_END)], t - w0), 20)))
        elif t < s1:
            st = [x[1] - s0 for x in ss]
            out.append(("L", "L", _q(pw([(st[0], 0.0), (st[1], L_STEPS[1]), (st[2], L_STEPS[2]), (st[3], 5.6),
                                         (st[3] + 4.6, L_END)], t - s0), 30)))
        else:
            out.append(("L", "L", _q(pw([(0.3, 1.0), (0.3 + L_END - 1.0, L_END)], t - d0), 30)))
    return out


if __name__ == "__main__":
    print({a: round(v, 3) for a, v in SHARE.items()})
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), {k: (round(v[0], 1), round(v[1], 1)) for k, v in SEC.items()})
    P = plan()
    print("frames", len(P), "unique", len({key(s, p) for s, _, p in P}))
