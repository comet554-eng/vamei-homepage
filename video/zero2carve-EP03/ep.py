"""《单板从0到刻滑》第3课：单脚蹬行。
动作关键帧、镜头、字幕时间都在这里；../zero2carve-lib/render.py 渲 3D，composite.py 叠字幕出片。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "zero2carve-lib"))
from epbase import plain, timeline, pw, key, ease

FPS = 30
TITLE = "第3课 · 单脚蹬行"
LEVEL = "L0 上雪前"
LESSON = 3
GROUND = 0.09          # 后脚踩在雪上时脚踝的高度

# ------------------------------------------------------------------ 动作（表演时间，秒）
# X：错误示范——后脚跑到板尾后面蹬，板绕着前脚打转
X = [
    (0.0, dict(lfw=1, lfx=-1.0, lfy=-0.20, lfz=GROUND, pz=0.80, yx=0.26)),
    (0.5, dict(gx=0.35, lfx=-1.35, tilt=5)),
    (0.8, dict(gx=0.50, lfx=-0.95, lfz=0.25, yaw=18)),
    (1.2, dict(gx=0.60, lfx=-0.65, lfz=0.20, yaw=55, tilt=15, arm=60, ab=40, elb=10)),
    (1.7, dict(gx=0.65, lfx=-0.50, lfy=-0.45, lfz=GROUND, yaw=85, tilt=24, pz=0.72, arm=80, ab=45)),
    (2.3, dict(yaw=90, tilt=18)),
]
X_SPIN = 1.2


def _strides(t0, g0, n, dur=1.0, step=0.9):
    """后脚在前刃一侧（+y）一步一步蹬：落脚 -> 蹬到后面 -> 抬脚收回。落地时脚在雪上不动（gx+lfx 不变）。"""
    keys, t, g = [], t0, g0
    for _ in range(n):
        keys += [
            (t + 0.45 * dur, dict(gx=g + 0.55 * step, lfx=-0.05 - 0.55 * step, lfz=GROUND, pz=0.77)),
            (t + 0.70 * dur, dict(gx=g + 0.78 * step, lfx=-0.30, lfz=0.24, pz=0.80)),
            (t + 1.00 * dur, dict(gx=g + step, lfx=-0.05, lfz=GROUND, pz=0.81)),
        ]
        t += dur; g += step
    return keys, t, g


# Y：正确做法——前脚绑好、后脚解开 → 肩和视线转向板头 → 后脚在前刃一侧小步蹬 → 踩上止滑垫滑一段
Y = [
    (0.0, dict(lfw=1, lfx=-0.05, lfy=0.32, lfz=GROUND, pz=0.82, arm=15, ab=30, elb=25)),
    (1.0, dict(twist=35, face=25, neck=5, ab=35)),
]
_k, _t, _g = _strides(1.6, 0.0, 3)
Y += [(1.6, dict(gx=0.0))] + _k
Y += [
    (_t + 0.35, dict(gx=_g + 0.40, lfx=-0.15, lfy=0.14, lfz=0.24, pz=0.82)),
    (_t + 0.65, dict(gx=_g + 0.75, lfx=-0.10, lfy=0.0, lfz=0.135, pz=0.83, twist=25)),
    (_t + 2.40, dict(gx=_g + 2.10, pz=0.84, arm=20, ab=38)),
]
Y_STEPS = [0.0, 1.0, 1.6, _t]
Y_END = _t + 2.4

PERF = dict(X=X, Y=Y)
SHOT_PERF = dict(X1="X", X2="X", Y="Y")

COVER3D = dict(perf="Y", p=2.05, cam=((1.6, 2.6, 1.0), (0.0, 0.1, 0.55), 34), ring="ankleL")


def orbit(cx, cy, r, deg, z):
    a = math.radians(deg); return (cx + r * math.cos(a), cy + r * math.sin(a), z)


def cam(shot, p, P):
    gx = P["gx"]
    if shot == "X1":     # 开场：斜前方，看板打转
        return orbit(gx, 0.0, 3.8, 62, 1.7), (gx - 0.1, 0.0, 0.88), 30
    if shot == "X2":     # 俯视：看清蹬的方向和板的方向
        return (gx - 0.2, 0.8, 3.7), (gx - 0.2, 0.0, 0.0), 30
    if shot == "Y":
        k = ease((p - 1.4) / 1.0)
        return orbit(gx + 0.2 * k, 0.1, 3.7, 75 - 20 * k, 1.45), (gx + 0.2 * k, 0.1, 0.90), 30
    raise KeyError(shot)


def extra_points(P, J):
    from mathutils import Vector
    m = J["board_m"]
    return {"bindL": m @ Vector((-0.26, 0, 0.08)), "bindR": m @ Vector((0.26, 0, 0.08)),
            "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)),
            "pad": m @ Vector((-0.10, 0, 0.03)), "board": m @ Vector((0, 0, 0.02))}


# ------------------------------------------------------------------ 字幕（不配音：按阅读速度排时间）
SECTIONS = [   # (名字, 开头留白, 字幕, 结尾留白)
    ("hook", 0.3, ["单脚蹬行，板总是{r|打转}？"], 0.4),
    ("why", 0.3, ["后脚跑到{r|板尾后面}去蹬，",
                  "力没顺着板的方向，板就绕着前脚{r|转圈}。"], 0.4),
    ("steps", 1.2, ["①前脚{w|绑好}，后脚{w|解开}。",
                    "②肩膀和视线，{w|转向板头}。",
                    "③后脚放在{w|前刃一侧}，贴着板小步蹬。",
                    "④滑起来后，后脚{w|踩上止滑垫}，滑一段。"], 0.6),
    ("drill", 0.3, ["平地上练：蹬三步，滑一段。",
                    "过关标准：蹬{w|20 米}不打转，踩上板能滑{w|两三米}。",
                    "上魔毯、排队等缆车，全靠这一招。"], 0.4),
    ("end", 0.3, [("下一课：{w|后刃推坡}，学会停下来。", 3.2)], 0.4),
]
VO_EXTRA = dict(steps="正确的蹬法，四步。")
SUBS, SEC, DUR = timeline(SECTIONS)


def plan():
    out = []
    h0, h1, _ = SEC["hook"]; w0, w1, ws = SEC["why"]; s0, s1, ss = SEC["steps"]; d0, d1, _ = SEC["drill"]
    for i in range(int(DUR * FPS)):
        t = i / FPS
        if t < h1:
            out.append(("X1", "X", pw([(0, 0.0), (2.6, 2.3)], t - h0)))
        elif t < w1:
            out.append(("X2", "X", pw([(0.2, 0.0), (ws[1][1] - w0 + 1.2, X_SPIN), (ws[1][1] - w0 + 3.6, 2.3)], t - w0)))
        elif t < s1:
            st = [x[1] - s0 for x in ss]
            out.append(("Y", "Y", pw([(st[0], 0.0), (st[1], 0.0), (st[1] + 1.4, Y_STEPS[1]), (st[2], Y_STEPS[1]),
                                      (st[2] + 0.5, Y_STEPS[2]), (st[3], Y_STEPS[3]), (st[3] + 2.6, Y_END)], t - s0)))
        else:            # 练习 + 结尾：完整重放一遍（复用 Y 的帧）
            out.append(("Y", "Y", pw([(0.4, 1.0), (0.4 + Y_END - 1.0, Y_END)], t - d0)))
    return out


if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), {k: (round(v[0], 1), round(v[1], 1)) for k, v in SEC.items()})
    P = plan()
    print("Y_END", Y_END, "frames", len(P), "unique", len({key(s, p) for s, _, p in P}))
