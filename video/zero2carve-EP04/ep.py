"""《单板从0到刻滑》第4课：后刃推坡（加原理和数据）。
动作关键帧、镜头、字幕时间都在这里；../zero2carve-lib/render.py 渲 3D，composite.py 叠字幕和数据出片。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "zero2carve-lib"))
from epbase import plain, timeline, pw, key, ease

FPS = 30
TITLE = "第4课 · 后刃推坡"
LEVEL = "L1 第一天"
LESSON = 4
SLOPE = 12.0           # 示意坡度（初级道最陡约 14°）
STOP, SLIDE = 18.0, 7.0

# ------------------------------------------------------------------ 原理和数据（示意计算）
MU_LO, MU_HI = 0.02, 0.14                      # 雪板/单板在雪上的滑动摩擦系数范围（文献）
MU_NEED = math.tan(math.radians(SLOPE))        # 只靠摩擦停在这个坡上需要的系数
MU_DEMO = 0.10                                 # 算“板放平滑多快”用的示意值
ACC = 9.81 * (math.sin(math.radians(SLOPE)) - MU_DEMO * math.cos(math.radians(SLOPE)))
KMH3 = ACC * 3 * 3.6

# ------------------------------------------------------------------ 动作（表演时间，秒）
BASE = dict(slope=SLOPE, tilt=10, pz=0.80, arm=20, ab=35, elb=25, knee=(0.0, 1.0, 0.25), trail=1, ty0=0.0)
# H：错误示范——板放平往下溜，越滑越快，下坡那边的前刃一碰雪，人被甩出去
H = [
    (0.0, dict(BASE, broll=4)),
    (0.7, dict(gy=0.30, broll=1)),
    (1.4, dict(gy=1.30, broll=0, tilt=4, arm=45, ab=40)),
    (1.6, dict(gy=1.62, broll=-7, tilt=-18, arm=60)),
    (2.0, dict(gy=1.72, broll=-40, tilt=-60, pz=0.52, py=0.40, arm=80, elb=10, knee=(0.0, 1.0, -0.3))),
    (2.5, dict(gy=1.75, pz=0.32, py=0.80, tilt=-80, broll=-75, bz=0.12, arm=80, elb=60, neck=-30, knee=(0.0, 0.3, -1.0))),
    (3.0, dict()),
]
H_CATCH = 1.6

# X：板的横截面——立刃角从 0 慢慢加到超过坡度，再放到负（前刃碰雪）
X = [
    (0.0, dict(BASE, broll=0, trail=0)),
    (1.5, dict(broll=12)), (2.5, dict(broll=12)),
    (3.5, dict(broll=20)), (4.5, dict(broll=20)),
    (5.5, dict(broll=6)), (6.5, dict(broll=6)),
    (7.5, dict(broll=-8)), (8.0, dict()),
]

# S：正确的后刃推坡——站稳 → 脚尖放低开始滑 → 脚尖抬起停住 → 两脚平均用力直直往下
S = [
    (0.0, dict(BASE, broll=STOP)),
    (0.5, dict(pz=0.74)), (1.0, dict(pz=0.76)),
    (1.6, dict(broll=SLIDE)),
    (2.6, dict(gy=0.55)), (3.6, dict(gy=1.20)),
    (4.2, dict(broll=STOP, gy=1.45)), (4.8, dict()),
    (5.3, dict(broll=SLIDE + 1)),
    (6.3, dict(gy=2.05)), (7.3, dict(gy=2.70)),
    (7.9, dict(broll=STOP, gy=2.88)), (8.4, dict()),
]
S_STEPS = [0.0, 1.0, 3.6, 4.8]
S_END = 8.4

PERF = dict(H=H, X=X, S=S)
SHOT_PERF = dict(H="H", X="X", S="S")
COVER3D = dict(perf="S", p=2.8, cam=((1.4, 2.6, 0.9), (0.0, 0.5, 0.45), 34), ring=None)
VO_EXTRA = dict(steps="正确的推坡，四步。")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def orbit(cx, cy, r, deg, z):
    a = math.radians(deg); return (cx + r * math.cos(a), cy + r * math.sin(a), z)


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    if shot == "H":      # 机位在下坡方向，看着人越滑越近
        pos, tgt = (gx + 2.0, 5.0, 1.4), (gx, gy + 0.2 * ease((p - 1.4) / 0.8), 0.85 - 0.35 * ease((p - 1.5) / 1.0))
    elif shot == "X":    # 沿着板的长轴看过去：板的横截面和坡面
        pos, tgt = (gx + 12.0, 0.05, 2.05), (gx, 0.05, 1.85)
        return _slope(pos, s), _slope(tgt, s), 55
    elif shot == "S":
        pos, tgt = orbit(gx, gy, 3.6, 62, 1.55), (gx, gy + 0.1, 0.85)
    else:
        raise KeyError(shot)
    return _slope(pos, s), _slope(tgt, s), 30


def extra_points(P, J):
    """后刃、前刃、板底中心，以及过后刃的水平线和坡面线（给原理图叠加用）。"""
    from mathutils import Vector, Matrix
    m = J["board_m"]
    heel = m @ Vector((0, -0.125, 0.0)); toe = m @ Vector((0, 0.125, 0.0))
    sm = Matrix.Rotation(math.radians(-P["slope"]), 3, "X")
    return {"heel": heel, "toe": toe, "base": m @ Vector((0, 0, 0.0)), "board": m @ Vector((0, 0, 0.02)),
            "hz": heel + Vector((0, 0.55, 0)), "sl": heel + sm @ Vector((0, 0.55, 0)),
            "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05))}


# ------------------------------------------------------------------ 字幕（不配音：按阅读速度排时间）
SECTIONS = [   # (名字, 开头留白, 字幕, 结尾留白)
    ("hook", 0.3, ["站在坡上{r|停不住}，越滑越快？"], 0.4),
    ("why", 0.3, ["板平放在坡上，板面朝下坡斜着，雪托不住。",
                  "雪面摩擦系数只有{b|0.02~0.14}，这个坡要停住得{r|0.21}。",
                  "光靠摩擦停不住：板放平，3秒就到{r|时速12公里}。",
                  "把脚尖抬起来，用{w|后刃}卡进雪里：",
                  "{w|立刃角大过坡度}，板面放平，就停住；比坡度小，就往下滑。",
                  "脚尖放太低，下坡这边的{r|前刃}碰到雪，人就被绊出去。"], 0.4),
    ("steps", 1.2, ["①面朝山下，膝盖弯，重心压在{w|后刃}。",
                    "②脚尖慢慢放低，立刃小于坡度，开始{w|往下滑}。",
                    "③脚尖抬起来，立刃大过坡度，{w|停住}。",
                    "④两只脚一样用力，板才{w|直直往下}，不往前后跑。"], 0.6),
    ("drill", 0.3, ["初级道上：滑三米、停住，连做五次。",
                    "过关标准：{w|想停就停}，板头板尾不乱跑。"], 0.4),
    ("end", 0.3, [("下一课：{w|落叶飘}，在坡上左右走。", 3.2)], 0.4),
]
SUBS, SEC, DUR = timeline(SECTIONS)


def _q(p, n):
    """原理图镜头不动，表演时间按 1/n 秒取整，少渲一半帧。"""
    return round(p * n) / n


def plan():
    out = []
    h0, h1, _ = SEC["hook"]; w0, w1, ws = SEC["why"]; s0, s1, ss = SEC["steps"]; d0, d1, _ = SEC["drill"]
    for i in range(int(DUR * FPS)):
        t = i / FPS
        if t < h1:
            out.append(("H", "H", pw([(0, 0.0), (2.6, 2.5), (h1, 3.0)], t - h0)))
        elif t < w1:
            a = [x[1] - w0 for x in ws]
            out.append(("X", "X", _q(pw([(0, 0.0), (a[3], 0.0), (a[3] + 2.2, 1.5), (a[4], 2.5), (a[4] + 1.2, 4.5),
                                      (a[4] + 4.2, 6.5), (a[5], 6.5), (a[5] + 1.6, 8.0)], t - w0), 20)))
        elif t < s1:
            st = [x[1] - s0 for x in ss]
            out.append(("S", "S", pw([(st[0], 0.0), (st[1], S_STEPS[1]), (st[1] + 0.4, S_STEPS[1]), (st[2], S_STEPS[2]),
                                      (st[2] + 1.2, S_STEPS[3]), (st[3], S_STEPS[3]), (st[3] + 3.6, S_END)], t - s0)))
        else:            # 练习 + 结尾：原速再滑一遍（复用 S 的帧）
            out.append(("S", "S", pw([(0.3, 1.0), (0.3 + S_END - 1.0, S_END)], t - d0)))
    return out


if __name__ == "__main__":
    print(f"mu_need={MU_NEED:.3f}  acc={ACC:.2f} m/s2  3s -> {KMH3:.1f} km/h")
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), {k: (round(v[0], 1), round(v[1], 1)) for k, v in SEC.items()})
    P = plan()
    print("frames", len(P), "unique", len({key(s, p) for s, _, p in P}))
