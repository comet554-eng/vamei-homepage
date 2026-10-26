"""《单板从0到刻滑》第6课：前刃推坡和落叶飘（新画风：白天雪山）。
动作关键帧、镜头、字幕时间都在这里；../zero2carve-lib/render.py 渲 3D，composite.py 叠字幕和数据出片。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "zero2carve-lib"))
from epbase import plain, timeline, pw, key, ease

FPS = 30
STYLE = "day"
TITLE = "第6课 · 前刃推坡和落叶飘"
LEVEL = "L1 第一天"
LESSON = 6
SLOPE = 12.0
STOP, SLIDE, LEAFE = 18.0, 9.0, 10.0      # 前刃立刃角（rig 里前刃为负）
LEAF = 15.0

# ------------------------------------------------------------------ 原理和数据
ROM_PF, ROM_DF = 50, 20      # 脚踝正常活动范围：跖屈（踮脚）约 50°，背屈（勾脚尖）约 20°（AAOS 常用正常值）

# ------------------------------------------------------------------ 动作（表演时间，秒）
# 面朝山上：坡角取负（+y 是上坡），往下滑 = gy 变小
BASE = dict(slope=-SLOPE, tilt=-12, pz=0.80, arm=25, ab=32, elb=30, knee=(0.0, 1.0, 0.25), broll=-STOP, trail=1)

# H：错误示范——弯腰撅屁股，重心离开板，前刃松掉，下坡那边的后刃一碰雪，人往后栽
H = [
    (0.0, dict(BASE, broll=-8, tilt=-38, py=-0.14, pz=0.84, arm=55, ab=20, elb=15, tw=(0.0, 0.0), tn=0)),
    (0.8, dict(gy=-0.50, broll=-4)),
    (1.3, dict(gy=-1.20, broll=1)),
    (1.5, dict(gy=-1.40, broll=8, tilt=-5, arm=80, ab=40)),
    (1.9, dict(gy=-1.50, tilt=50, pz=0.45, py=-0.35, arm=-40, ab=25, elb=10, broll=6)),
    (2.4, dict(gy=-1.55, tilt=76, pz=0.17, py=-0.52, arm=-30, elb=30, neck=-20, knee=(0.0, 0.3, 1.0))),
    (2.9, dict()),
]
H_CATCH = 1.5

# X：横截面原理图——前刃立刃角 0 → 12 → 20 → 6 → 放过头（后刃碰雪）
X = [
    (0.0, dict(BASE, broll=0, trail=0, tilt=-10)),
    (1.5, dict(broll=-12)), (2.5, dict(broll=-12)),
    (3.5, dict(broll=-20)), (4.5, dict(broll=-20)),
    (5.5, dict(broll=-6)), (6.5, dict(broll=-6)),
    (7.5, dict(broll=8)), (8.0, dict()),
]

# S：正确做法——前刃推坡（滑、停）→ 压前脚往前飘 → 停 → 回头看、压后脚往回飘 → 停
WP = (0.0, 0.0, 0.0, -1.2, 2.65, -1.95, 0.05, -2.75)
S = [
    (0.0, dict(BASE, tw=WP, tn=0)),
    (1.0, dict(pz=0.76)),
    (1.6, dict(broll=-SLIDE, pz=0.78)),
    (3.4, dict(gy=-1.0)),
    (3.8, dict(broll=-STOP, gy=-1.2, tn=1)),
    (4.4, dict(px=0.10, yaw=-LEAF, broll=-LEAFE, face=15)),
    (5.2, dict(gx=0.45, gy=-1.32)),
    (6.6, dict(gx=2.40, gy=-1.85)),
    (7.2, dict(px=0.0, yaw=0, broll=-STOP, gx=2.65, gy=-1.95, tn=2, face=0)),
    (7.8, dict(px=-0.10, yaw=LEAF, broll=-LEAFE, face=-45)),
    (8.6, dict(gx=2.20, gy=-2.08)),
    (10.0, dict(gx=0.30, gy=-2.65)),
    (10.6, dict(px=0.0, yaw=0, broll=-STOP, gx=0.05, gy=-2.75, tn=3, face=0)),
    (11.2, dict()),
]
S_STEPS = [0.0, 1.0, 4.4, 7.2]
S_END = 11.2

PERF = dict(H=H, X=X, S=S)
SHOT_PERF = dict(H="H", X="X", S="S")
COVER3D = dict(perf="S", p=5.8, cam=((1.2, 2.6, 1.0), (0.0, 0.2, 0.55), 34), ring=None)
VO_EXTRA = dict(steps="前刃的推坡和落叶飘，四步。")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    if shot == "H":      # 机位在上坡方向，正对着人
        pos, tgt = (gx + 1.6, gy + 4.2, 2.1), (gx, gy, 0.75 - 0.3 * ease((p - 1.5) / 0.8))
    elif shot == "X":    # 顺着板的长轴看过去
        pos, tgt = (gx + 12.0, 0.05, 2.05), (gx, 0.05, 1.85)
        return _slope(pos, s), _slope(tgt, s), 55
    elif shot == "S":
        cx = 1.3 + 0.8 * (gx - 1.3)
        pos, tgt = (cx + 0.3, gy + 3.9, 2.2), (cx, gy - 0.1, 0.65)
    else:
        raise KeyError(shot)
    return _slope(pos, s), _slope(tgt, s), 30


def extra_points(P, J):
    from mathutils import Vector, Matrix
    m = J["board_m"]
    sm = Matrix.Rotation(math.radians(-P["slope"]), 3, "X")
    c = m @ Vector((0, 0, 0.02))
    return {"board": c, "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)),
            "toe": m @ Vector((0, 0.125, 0.0)), "heel": m @ Vector((0, -0.125, 0.0)),
            "fall": c + sm @ Vector((0, -1.0, 0))}


# ------------------------------------------------------------------ 字幕（不配音：按阅读速度排时间）
SECTIONS = [   # (名字, 开头留白, 字幕, 结尾留白)
    ("hook", 0.3, ["前刃推坡，最怕{r|往后栽}。"], 0.4),
    ("why", 0.3, ["前刃推坡：面朝山上，踮起脚，用{w|前刃}卡住雪。",
                  "踮脚靠脚踝{b|跖屈}，能动约{b|50°}；勾脚尖的{b|背屈}只有约{r|20°}。",
                  "所以前刃更好立、停得更稳——但你{r|看不见山下}。",
                  "规矩跟后刃一样：{w|立刃角大过坡度}就停，小于坡度就滑。",
                  "弯腰撅屁股，重心离开板，下坡那边的{r|后刃}一碰雪，人就往后栽。"], 0.4),
    ("steps", 1.2, ["①面朝山上，{w|膝盖顶向山坡}，踮脚立住前刃。",
                    "②脚跟慢慢放低，往下滑；再踮起来，{w|停住}。",
                    "③重心移到{w|前脚}，板头微微朝下，往前飘。",
                    "④先{w|回头看路}，重心换到后脚，往回飘。"], 0.6),
    ("drill", 0.3, ["初级道：前刃推坡十米，再前刃落叶飘，来回两趟。",
                    "过关标准：{w|想停就停}；往哪边飘，先回头看哪边。"], 0.4),
    ("end", 0.3, [("下一课：第一次{w|换刃}。", 3.2)], 0.4),
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
            out.append(("H", "H", _q(pw([(0, 0.0), (h1 - 0.7, 2.5), (h1, 2.9)], t - h0), 30)))
        elif t < w1:
            a = [x[1] - w0 for x in ws]
            out.append(("X", "X", _q(pw([(0, 0.0), (a[3], 0.0), (a[3] + 2.2, 1.5), (a[3] + 3.0, 2.5), (a[3] + 4.2, 4.5),
                                         (a[4] - 0.4, 6.5), (a[4] + 1.6, 8.0)], t - w0), 20)))
        elif t < s1:
            st = [x[1] - s0 for x in ss]
            out.append(("S", "S", _q(pw([(st[0], 0.0), (st[1], S_STEPS[1]), (st[2], S_STEPS[2]), (st[3], S_STEPS[3]),
                                         (st[3] + 4.0, S_END)], t - s0), 30)))
        else:
            out.append(("S", "S", _q(pw([(0.3, 1.0), (0.3 + S_END - 1.0, S_END)], t - d0), 30)))
    return out


if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), {k: (round(v[0], 1), round(v[1], 1)) for k, v in SEC.items()})
    P = plan()
    print("frames", len(P), "unique", len({key(s, p) for s, _, p in P}))
