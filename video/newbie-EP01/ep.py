"""《单板新手课》第1课：基本站姿（竖屏 1080×1920，实拍 + 2D/3D 演示 + 数据图）。
同一份字幕、镜头和动作，出 2D 和 3D 两个版本：
  plan() 每帧给出 (类型, 镜头, 参数)：
    ("F", 素材ID, 素材内时间)        实拍（Mixkit）
    ("R", 镜头名, 表演时间)          人物演示（3D 用 Blender 渲，2D 用 cairo 画同一套骨架）
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "newbie-lib"))
from epbase import plain, timeline, pw, key, ease

FPS = 30
LESSON = 1
SERIES = "单板新手课"
TITLE = "第1课 · 基本站姿"
STYLE = "day"
MUSIC = "bounce"
TRACK = (158, 0.0)             # Mixkit 免费音乐 #158

# ------------------------------------------------------------------ 数据（来源见 方案.md）
STANCE_FRONT, STANCE_BACK = 15, -6      # 常见入门角度：前脚 +15° 左右，后脚 0° 到 −6°
BUMP_H = 0.10                           # 小坎 10 cm
D_STRAIGHT, D_BENT = 0.02, 0.10         # 直腿 / 屈膝 能缓冲的距离（示意）
G_STRAIGHT = 1 + BUMP_H / D_STRAIGHT    # 匀减速简化模型：F/mg = 1 + h/d  -> 6
G_BENT = 1 + BUMP_H / D_BENT            # -> 2

# ------------------------------------------------------------------ 姿势（rig3d 参数；人面朝 +y，板头 +x = 前脚）
GOOD = dict(pz=0.80, px=0.03, py=0.0, tilt=-6, arm=18, ab=30, elb=28, neck=0, curl=0, face=55, twist=8, knee=(0.25, 1.0, 0.2))
TALL = dict(pz=0.99, px=0.0, tilt=0, arm=8, ab=18, elb=8, face=55, twist=0)
BUTT = dict(pz=0.80, px=-0.10, py=-0.17, tilt=-38, arm=45, ab=25, elb=20, face=40)
LOOK = dict(pz=0.86, px=0.0, py=0.02, tilt=-14, curl=22, neck=42, face=0, arm=10, ab=20, elb=15)

# K：四个要领，从直腿慢慢“摆”成正确站姿
K = [
    (0.0, dict(TALL)),
    (1.0, dict(TALL)),
    (2.2, dict(GOOD, arm=10, ab=18, elb=10, face=0, twist=0, px=0.0)),        # ① 屈膝
    (4.0, dict()),
    (5.0, dict(px=0.05)),                                                     # ② 重心稍偏前脚
    (6.0, dict(px=0.03)),
    (8.0, dict(arm=18, ab=30, elb=28)),                                       # ③ 上身直、手张开
    (10.0, dict()),
    (11.0, dict(face=55, twist=8)),                                           # ④ 看前方
    (13.0, dict()),
]
K_STEP = [0.0, 1.0, 4.0, 7.0, 10.0]

# B：减震——直腿过坎（整个人被顶起来），屈膝过坎（腿收一下，身体几乎不动）
def _bump(t0, bent):
    base = dict(GOOD) if bent else dict(TALL)
    up = 0.10
    body = 0.02 if bent else 0.10
    return [
        (t0, dict(base, bz=0.0)),
        (t0 + 0.35, dict(bz=up, pz=base["pz"] + body, tilt=base["tilt"] + (0 if bent else 6), arm=base["arm"] + (0 if bent else 30))),
        (t0 + 0.7, dict(bz=0.0, pz=base["pz"] - (0.04 if bent else 0.0), tilt=base["tilt"])),
        (t0 + 1.3, dict(pz=base["pz"], arm=base["arm"])),
    ]
B = [(0.0, dict(TALL))] + _bump(0.6, False)[1:] + [(2.6, dict(TALL)), (3.2, dict(GOOD))] + _bump(3.6, True)[1:] + [(5.6, dict())]
B_STRAIGHT, B_BENT = 0.6, 3.6

# M：三个常见错误，每个错完都回到正确站姿
M = [
    (0.0, dict(GOOD)),
    (0.8, dict(TALL)), (2.6, dict()),
    (3.4, dict(GOOD)), (4.0, dict(BUTT)), (5.8, dict()),
    (6.6, dict(GOOD)), (7.2, dict(LOOK)), (9.0, dict()),
    (9.8, dict(GOOD)), (10.5, dict()),
]
M_ERR = [0.8, 4.0, 7.2]

# D：练习——蹲起 3 次 + 小跳 2 次
D = [(0.0, dict(GOOD))]
_t = 0.4
for _ in range(3):
    D += [(_t + 0.5, dict(pz=0.66, tilt=-10)), (_t + 1.1, dict(pz=0.80, tilt=-6))]
    _t += 1.1
for _ in range(2):
    D += [(_t + 0.25, dict(pz=0.72, arm=-5)), (_t + 0.5, dict(pz=0.96, bz=0.16, arm=35)),
          (_t + 0.75, dict(pz=0.72, bz=0.0, arm=20)), (_t + 1.05, dict(pz=0.80, arm=18))]
    _t += 1.2
D += [(_t + 0.4, dict())]
D_END = _t + 0.4

# T：俯视看固定器（静止站姿）
T = [(0.0, dict(GOOD, face=0, twist=0)), (1.0, dict())]

PERF = dict(K=K, B=B, M=M, D=D, T=T)
SHOT_PERF = dict(K="K", B="B", M="M", D="D", T="T")


def cam(shot, p, P):
    """返回 (相机位置, 目标点, 焦距mm)。"""
    if shot == "T":                       # 俯视
        return (0.1, 2.5, 2.7), (0.0, 0.0, 0.25), 30
    if shot == "B":                       # 侧前方，稍低，看得见板离地
        return (2.0, 3.1, 0.85), (0.0, 0.0, 0.55), 36
    return (1.7, 3.1, 1.15), (0.0, 0.0, 0.52), 36


def extra_points(P, J):
    from mathutils import Vector
    m = J["board_m"]
    return {"board": m @ Vector((0, 0, 0.02)), "nose": m @ Vector((0.78, 0, 0.03)), "tail": m @ Vector((-0.78, 0, 0.03)),
            "footR": m @ Vector((0.26, 0, 0.03)), "footL": m @ Vector((-0.26, 0, 0.03)),
            "footR_toe": m @ Vector((0.26, 0.16, 0.03)), "footL_toe": m @ Vector((-0.26, 0.16, 0.03)),
            "footR_heel": m @ Vector((0.26, -0.16, 0.03)), "footL_heel": m @ Vector((-0.26, -0.16, 0.03)),
            "ground": Vector((J["pelvis"].x, J["pelvis"].y, 0.0))}


# ------------------------------------------------------------------ 字幕（不配音：按阅读速度排时间）
import epbase
epbase.CPS = 5.2
SECTIONS = [
    ("hook", 0.2, ["单板第一课：先学会{w|站}。",
                   "站不对，后面每课都在{r|摔}。"], 0.1),
    ("setup", 0.3, ["先调固定器：两脚距离{w|约等于肩宽}。",
                    "角度：前脚{b|+15°}，后脚{b|0°到−6°}，微微外八。"], 0.3),
    ("keys", 0.3, ["①脚踝膝盖{w|一起弯}，膝盖对脚尖。",
                   "②重心在{w|两脚中间}，略偏前脚。",
                   "③上身{w|直立}，手臂放松张开。",
                   "④眼睛{w|看前方}，别盯脚下。"], 0.3),
    ("why", 0.2, ["雪面从来不平，腿就是{b|减震器}。",
                  "过10厘米小坎：直腿只缓冲2厘米，冲击约{r|6倍体重}；",
                  "屈膝能缓冲10厘米，只有约{g|2倍体重}。"], 0.4),
    ("mistakes", 0.2, ["{r|直腿站}：一颠就弹起来。",
                       "{r|撅屁股}：重心跑到后脚。",
                       "{r|低头看板}：越滑越僵。"], 0.3),
    ("drill", 0.2, ["练习：平地绑好双脚，{w|蹲起10次}、{w|小跳5次}。",
                    "过关：落地不晃，膝盖{w|始终弯着}。"], 0.3),
    ("end", 0.2, [("下一课：{w|单脚蹬行}。", 2.6)], 0.3),
]
SUBS, SEC, DUR = timeline(SECTIONS)

# 实拍镜头：(素材ID, 入点秒, 横向平移起点 0..1, 终点 0..1)
FOOT = {
    "hook0": ("3373", 2.5, 0.50, 0.60),
    "hook1": ("3378", 4.0, 0.40, 0.55),
    "why0": ("3380", 2.0, 0.35, 0.55),
    "pass": ("3344", 1.0, 0.40, 0.55),
    "end": ("3348", 2.0, 0.45, 0.60),
}


def _q(p, n=20):
    return round(p * n) / n


def plan():
    out = []
    h0, h1, hs = SEC["hook"]; s0, s1, ss = SEC["setup"]; k0, k1, ks = SEC["keys"]
    w0, w1, ws = SEC["why"]; m0, m1, ms = SEC["mistakes"]; d0, d1, ds = SEC["drill"]; e0, e1, _ = SEC["end"]
    for i in range(int(round(DUR * FPS))):
        t = i / FPS
        if t < h1:
            cut = hs[1][1] - 0.1
            out.append(("F", "hook0", t) if t < cut else ("F", "hook1", t - cut))
        elif t < s1:
            out.append(("R", "T", 0.0))
        elif t < k1:
            a = [x[1] - k0 for x in ks]
            p = pw([(0, 0.0), (0.2, 1.0), (a[0] + 1.6, 2.2), (a[1], K_STEP[2]), (a[1] + 1.0, 5.0), (a[2], K_STEP[3]),
                    (a[2] + 1.0, 8.0), (a[3], K_STEP[4]), (a[3] + 1.0, 11.0), (k1 - k0, 12.0)], t - k0)
            out.append(("R", "K", _q(p)))
        elif t < w1:
            a = [x[1] - w0 for x in ws]
            if t - w0 < a[1] - 0.1:
                out.append(("F", "why0", t - w0))
            else:
                p = pw([(a[1] - 0.1, 0.0), (a[1] + 0.4, 0.6), (a[1] + 2.4, 2.6), (a[2] - 0.5, 3.2),
                        (a[2] + 0.1, 3.6), (a[2] + 2.1, 5.6)], t - w0)
                out.append(("R", "B", _q(p)))
        elif t < m1:
            a = [x[1] - m0 for x in ms]
            p = pw([(0, 0.6), (a[0] + 1.2, 2.6), (a[1] - 0.5, 3.4), (a[1] + 1.4, 5.8),
                    (a[2] - 0.5, 6.6), (a[2] + 1.4, 9.0), (m1 - m0, 10.0)], t - m0)
            out.append(("R", "M", _q(p)))
        elif t < d1:
            a = [x[1] - d0 for x in ds]
            if t - d0 < a[1] - 0.1:
                out.append(("R", "D", _q(pw([(0, 0.0), (a[1] - 0.1, D_END)], t - d0))))
            else:
                out.append(("F", "pass", t - d0 - (a[1] - 0.1)))
        else:
            out.append(("F", "end", t - e0))
    return out


def music_hits():
    hits = [SEC[k][2][0][1] for k in ("setup", "keys", "why", "mistakes", "drill", "end")]
    sfx = [(SEC["hook"][2][1][1] + 0.1, "boom")]
    sfx += [(s[1] + 0.05, "ding") for s in SEC["keys"][2]]
    sfx += [(SEC["why"][2][1][1] + 0.6, "boom"), (SEC["why"][2][2][1] + 0.6, "ding")]
    sfx += [(s[1] + 0.05, "whoosh") for s in SEC["mistakes"][2]]
    return hits, sfx


if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), {k: (round(v[0], 1), round(v[1], 1)) for k, v in SEC.items()})
    P = plan()
    R = {key(s, p) for k, s, p in P if k == "R"}
    print("frames", len(P), "unique 3D", len(R))
    print("G", G_STRAIGHT, G_BENT)

# 封面：3D 透明底人物
COVER3D = dict(perf="K", p=12.0, cam=((1.5, 3.0, 1.05), (0.0, 0.0, 0.55), 40), ring=None)
COVER = dict(title="基本站姿", sub="站对了，后面才不摔", items=["屈膝", "重心", "上身", "视线"],
             perf="K", p=12.0, cam=((1.5, 3.0, 1.05), (0.0, 0.0, 0.55), 40), bg=("3378", 4.0))
