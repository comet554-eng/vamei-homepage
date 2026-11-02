"""《单板从0到刻滑》第7课：第一次换刃（后刃 → 前刃）。新画风 + 明快背景音乐 A。
动作关键帧、镜头、字幕时间、音乐重拍和音效都在这里；../zero2carve-lib/render.py 渲 3D，composite.py 叠字幕出片。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "zero2carve-lib"))
from epbase import plain, timeline, pw, key, ease

FPS = 30
STYLE = "day"
MUSIC = "pop"
TITLE = "第7课 · 第一次换刃"
LEVEL = "L2 学转弯"
LESSON = 7
SLOPE = 12.0
R = 3.0                                     # 弯的半径（示意）

# ------------------------------------------------------------------ 原理和数据（示意计算，摩擦系数沿用第4课的 0.1）
MU = 0.10
ACC = 9.81 * (math.sin(math.radians(SLOPE)) - MU * math.cos(math.radians(SLOPE)))
KMH_PER_S = ACC * 3.6                       # 平板正对下坡，每多拖 1 秒增加的时速


def arc(phi_deg, c=(0.6 - R * math.sin(math.radians(10)), 0.05 + R * math.cos(math.radians(10)))):
    """弯上的位置：板头朝向 φ（yaw）时板中心在哪。φ=10° 时在 (0.6, 0.05)，弯心在下坡一侧。"""
    p = math.radians(phi_deg)
    return c[0] + R * math.sin(p), c[1] - R * math.cos(p)


# ------------------------------------------------------------------ 动作（表演时间，秒）
BASE = dict(slope=SLOPE, tilt=10, pz=0.80, arm=22, ab=35, elb=25, knee=(0.0, 1.0, 0.25), trail=1)
WP_PHI = [10, 40, 70, 90, 120, 150, 175]
WP = sum(((0.0, 0.0),) + tuple(arc(a) for a in WP_PHI), ())


def at(phi, **kw):
    x, y = arc(phi); d = dict(gx=x, gy=y, yaw=phi); d.update(kw); return d


# W：错误示范——只拧上身，板转得慢，还没转过下坡线就把下坡那边的前刃压下去：卡刃，人被甩向山下
W = [
    (0.0, dict(BASE, yaw=10, broll=12, gx=0.0, gy=0.0, tw=(0.0, 0.0), tn=0)),
    (0.8, at(14, broll=14, twist=20, face=20)),
    (1.5, at(28, broll=6, twist=60, face=45, arm=40, ab=40)),
    (1.8, at(34, broll=-8, twist=60, tilt=-15)),
    (2.2, at(36, broll=-40, tilt=-60, pz=0.52, py=0.40, arm=80, elb=10, knee=(0.0, 1.0, -0.3))),
    (2.7, at(37, pz=0.32, py=0.80, tilt=-80, broll=-75, bz=0.12, arm=80, elb=60, neck=-30, knee=(0.0, 0.3, -1.0))),
    (3.2, dict()),
]
W_CATCH = 1.8

# S：正确的第一次换刃（后刃落叶飘 → 板头指向下坡 → 平板 → 换前刃 → 前刃把弯走完）
S = [
    (0.0, dict(BASE, yaw=10, broll=12, gx=0.0, gy=0.0, px=0.05, tw=WP, tn=0)),
    (1.0, at(10, broll=16, pz=0.76)),
    (1.8, at(40, broll=11, twist=20, face=25, pz=0.82, tn=1)),
    (2.3, at(70, broll=5, twist=28, face=30, pz=0.86, tilt=4, tn=2)),
    (2.6, at(90, broll=0, tilt=0, pz=0.88, twist=25, tn=3)),
    (3.2, at(120, broll=-14, tilt=-10, pz=0.78, twist=15, face=15, tn=4)),
    (3.9, at(150, broll=-17, tilt=-12, twist=5, face=5, tn=5)),
    (4.6, at(175, broll=-18, twist=0, face=0, px=0.0, tn=6)),
    (5.2, dict(gx=arc(175)[0] - 0.35, gy=arc(175)[1] + 0.02, yaw=180)),
    (5.8, dict()),
]
S_STEPS = [0.0, 1.0, 2.6, 3.9]
S_FLAT = (2.3, 3.0)                     # 板基本是平的那一段
S_END = 5.8

PERF = dict(W=W, S=S)
SHOT_PERF = dict(W="W", T="S", S="S")
COVER3D = dict(perf="S", p=3.3, cam=((1.6, 2.4, 1.0), (0.0, 0.0, 0.5), 34), ring=None)
VO_EXTRA = dict(steps="第一次换刃，四步。")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


CEN = arc(90)


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    if shot in ("W", "S"):   # 下坡一侧斜上方，半跟随
        cx, cy = 0.9 * gx + 0.1 * CEN[0], 0.8 * gy + 0.2 * CEN[1]
        pos, tgt = (cx + 1.8, cy + 5.0, 2.3), (cx, cy - 0.2, 0.75)
    elif shot == "T":        # 正上方俯视整条弯
        pos, tgt = (1.75, 3.1, 11.5), (1.75, 3.1, 0.0)
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
            "fall": c + sm @ Vector((0, 1.2, 0)),
            **{f"a{a}": J["slope_m"] @ Vector((*arc(a), 0.02)) for a in (10, 25, 40, 55, 70, 90, 105, 120, 135, 150, 165, 175)}}


# ------------------------------------------------------------------ 字幕（不配音：按阅读速度排时间）
SECTIONS = [   # (名字, 开头留白, 字幕, 结尾留白)
    ("hook", 0.3, ["第一次换刃，为啥{r|一换就摔}？"], 0.4),
    ("why", 0.3, ["换刃要经过一次{w|平板}：两边刃都不吃雪，板头正对山下——{r|它在加速}。",
                  "12°的坡，平板每拖1秒，时速多{r|4公里}；拖3秒，{r|快12公里}！",
                  "所以要{w|果断}：板头一过下坡线，马上压新刃。",
                  "顺序：{w|眼睛→肩→髋→板}，身体先转，板跟着走。"], 0.4),
    ("steps", 1.2, ["①后刃落叶飘，先把{w|速度}放下来。",
                    "②看向要去的方向，肩膀带着，板头{w|指向山下}。",
                    "③一过下坡线，膝盖往前顶，{w|换前刃}！",
                    "④前刃把弯走完，板横过来，{w|停住}。"], 0.6),
    ("drill", 0.3, ["缓坡：落叶飘→换前刃停，左右各五次。",
                    "过关：平板{w|不超过1秒}，不卡刃。",
                    "第一次换刃你摔了几次？{w|评论区}见！"], 0.4),
    ("end", 0.3, [("下一课：连起来，就是{w|S弯}！", 3.0)], 0.4),
]
VO_EXTRA = dict(steps="第一次换刃，四步。")
SUBS, SEC, DUR = timeline(SECTIONS)


def _q(p, n):
    return round(p * n) / n


def plan():
    out = []
    h0, h1, _ = SEC["hook"]; w0, w1, ws = SEC["why"]; s0, s1, ss = SEC["steps"]; d0, d1, _ = SEC["drill"]
    for i in range(int(DUR * FPS)):
        t = i / FPS
        if t < h1:
            out.append(("W", "W", _q(pw([(0, 0.4), (h1 - 0.7, 2.8), (h1, 3.2)], t - h0), 30)))
        elif t < w1:          # 俯视：整条弯慢放，在平板那一刻停住，算完账再走完
            a = [x[1] - w0 for x in ws]
            out.append(("T", "S", _q(pw([(0, 0.0), (a[0] + 3.0, 2.6), (a[2], 2.6), (a[2] + 2.0, 3.6),
                                         (a[3], 4.2), (a[3] + 3.0, S_END)], t - w0), 20)))
        elif t < s1:
            st = [x[1] - s0 for x in ss]
            out.append(("S", "S", _q(pw([(st[0], 0.0), (st[1], S_STEPS[1]), (st[2] - 0.3, 2.3), (st[2] + 1.6, S_STEPS[2] + 0.6),
                                         (st[3], S_STEPS[3]), (st[3] + 2.6, S_END)], t - s0), 30)))
        else:
            out.append(("S", "S", _q(pw([(0.3, 0.6), (0.3 + (S_END - 0.6) * 1.4, S_END)], t - d0), 30)))
    return out


def music_hits():
    """音乐重拍放在每段开头；音效：开场卡刃“砰”，数字揭晓“叮”，段落切换“嗖”。"""
    hits = [SEC[k][0] for k in ("why", "steps", "drill")]
    T_CATCH = next(i for i, (s, _, p) in enumerate(plan()) if p >= W_CATCH) / FPS
    ws = SEC["why"][2]
    sfx = [(T_CATCH, "boom"), (ws[1][1] + 1.6, "ding"), (ws[1][1] + 3.8, "ding")] + [(h - 0.25, "whoosh") for h in hits]
    return hits, sfx


if __name__ == "__main__":
    print(f"acc={ACC:.2f}  +{KMH_PER_S:.1f} km/h per s")
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), {k: (round(v[0], 1), round(v[1], 1)) for k, v in SEC.items()})
    P = plan()
    print("frames", len(P), "unique", len({key(s, p) for s, _, p in P}))
    print(music_hits())
