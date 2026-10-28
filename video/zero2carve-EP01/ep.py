"""《单板从0到刻滑》第1课：先学会摔。
动作关键帧、镜头、字幕时间都在这里；render.py 渲 3D，composite.py 叠字幕出片。
本文件不依赖 bpy/cairo，两边都能 import。"""
import math

FPS = 30
TITLE = "第1课 · 先学会摔"
LEVEL = "L0 上雪前"
LESSON = 1

# ------------------------------------------------------------------ 动作（表演时间，秒）
# A：错误示范——往后倒，直臂撑地
A = [
    (0.0, dict()),
    (0.35, dict(gx=0.42, tilt=8, pz=0.84, arm=25, ab=30, elb=25)),
    (0.70, dict(gx=0.78, tilt=30, py=-0.15, pz=0.70, arm=70, ab=35, elb=10, broll=6, neck=-5)),
    (1.00, dict(gx=1.00, tilt=50, py=-0.32, pz=0.46, arm=-40, ab=22, elb=5, broll=10, neck=-12)),
    (1.15, dict(gx=1.05, tilt=58, py=-0.42, pz=0.34, arm=-52, ab=20, elb=2, broll=12, neck=-15)),
    (1.50, dict(gx=1.08, tilt=72, py=-0.50, pz=0.17, arm=-28, elb=35, broll=8, neck=-25)),
    (2.20, dict(gx=1.09)),
]
A_IMPACT = 1.15

# C：正确的后摔——蹲低 → 握拳收胸 → 屁股着地 → 顺势滚
C = [
    (0.0, dict()),
    (0.50, dict(gx=0.55, tilt=10, arm=30, ab=30, elb=25)),
    (1.20, dict(gx=1.05, pz=0.55, py=-0.10, tilt=14, curl=25, neck=20, arm=20, ab=12, elb=112, fin=30)),
    (1.40, dict(gx=1.15)),
    (2.10, dict(gx=1.40, pz=0.16, py=-0.42, tilt=35, curl=35, neck=30)),
    (2.90, dict(gx=1.52, pz=0.15, py=-0.62, tilt=92, curl=40, neck=45, by=-0.25, bz=0.52, broll=150,
                knee=(0.0, 0.3, 1.0))),
    (3.60, dict(gx=1.55, tilt=84, curl=32, bz=0.44, broll=140)),
]
C_STEPS = [1.2, 1.4, 2.1, 2.9]          # 蹲低、手收好、屁股着地、滚

# D：正确的前摔——膝盖先跪 → 小臂着地 → 脸侧开
D = [
    (0.0, dict()),
    (0.50, dict(gx=0.55, tilt=-12, broll=-8, arm=30)),
    (1.10, dict(gx=1.00, pz=0.50, py=0.20, tilt=-20, broll=-35, bz=0.05, arm=60, ab=15, elb=60,
                knee=(0.0, 1.0, -0.3))),
    (1.70, dict(gx=1.15, pz=0.46, py=0.55, tilt=-15, broll=-80, bz=0.13, arm=70, elb=70, knee=(0.0, 1.0, -0.6))),
    (2.40, dict(gx=1.22, pz=0.33, py=0.75, tilt=-80, curl=8, neck=-35, face=35, arm=80, ab=10, elb=95, fin=20,
                knee=(0.0, 0.3, -1.0))),
    (3.20, dict(gx=1.24, tilt=-82)),
]
D_STEPS = [1.7, 2.4, 2.4]

PERF = dict(A=A, C=C, D=D)


# ------------------------------------------------------------------ 镜头（随表演时间走，停帧时镜头也停 -> 重复帧不用重渲）
def cam(shot, p, gx):
    def ease(x):
        x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

    def orbit(cx, cy, r, deg, z):
        a = math.radians(deg); return (cx + r * math.cos(a), cy + r * math.sin(a), z)
    if shot == "A1":                       # 开场：前侧 3/4，低机位，跟着人往下落
        k = ease((p - 0.6) / 0.6)
        return orbit(gx, -0.2, 3.3 - 0.6 * k, 42, 1.0 - 0.25 * k), (gx, -0.25, 1.02 - 0.52 * k), 30
    if shot == "A2":                       # 慢放：正侧面
        return orbit(gx, -0.3, 2.6, 8, 0.75), (gx, -0.30, 0.55), 30
    if shot == "C":                        # 先正面看手，再转到侧面看滚
        k = ease((p - 1.4) / 1.5)
        return orbit(gx, -0.3 - 0.35 * k, 3.3 - 0.4 * k, 40 - 30 * k, 1.15 - 0.3 * k), (gx, -0.30 - 0.35 * k, 1.02 - 0.52 * k), 30
    if shot == "D":
        k = ease((p - 0.8) / 1.6)
        return orbit(gx, 0.4 + 0.5 * k, 3.3, 35 - 5 * k, 1.15 - 0.1 * k), (gx, 0.40 + 0.5 * k, 1.02 - 0.60 * k), 30
    raise KeyError(shot)


# ------------------------------------------------------------------ 字幕（不配音：按阅读速度排时间）
def plain(s):
    for m in ("{b|", "{w|", "{r|", "}", "\n"):
        s = s.replace(m, "")
    return s


def seq(items, t0=0.3, gap=0.3, cps=4.4):
    out, t = [], t0
    for it in items:
        s, md = (it, 0) if isinstance(it, str) else it
        d = max(md, len(plain(s)) / cps + 0.25 * (s.count("，") + s.count("、")) + 0.6, 2.4)
        out.append((s, t, t + d)); t += d + gap
    return out


SECTIONS = [   # (名字, 开头留白, 字幕)
    ("hook", 0.3, ["新手受伤，排第一的是{r|手腕}。"]),
    ("why", 0.3, ["摔倒时，人会本能地{r|伸手撑地}。",
                  "全身重量，全砸在{r|手腕}上。",
                  "单板受伤里，手腕占{r|27.6%}。"]),
    ("back", 1.2, ["①先{w|蹲低}，离雪面越近摔得越轻。",
                   "②手{w|握拳收在胸前}，下巴收紧。",
                   "③{w|屁股先着地}，顺势往后滚，板抬起来。"]),
    ("front", 1.2, ["①{w|膝盖先跪}下去。",
                    "②{w|小臂整条着地}，别用手掌撑。",
                    "③脸侧开，别磕到雪面。"]),
    ("drill", 0.3, ["平地穿板练：蹲下、坐下、往后滚，五次。",
                    "过关标准：摔的时候{w|手不先碰地}。",
                    "再戴上{w|护腕}，第一天少挨很多疼。"]),
    ("end", 0.3, [("下一课：摔倒了怎么{w|站起来}？", 3.0)]),
]


def timeline():
    """-> SUBS [(text, t0, t1)] 全片时间, SEC {name: (t0, t1, [subs])}"""
    subs, sec, t = [], {}, 0.0
    for name, lead, items in SECTIONS:
        S = seq(items, t0=t + lead)
        end = S[-1][2] + 0.4
        sec[name] = (t, end, S)
        subs += S; t = end
    return subs, sec, t


SUBS, SEC, DUR = timeline()


def _pw(anchors, t):
    """分段线性：anchors [(out_t, perf_t)]"""
    if t <= anchors[0][0]:
        return anchors[0][1]
    for (a0, p0), (a1, p1) in zip(anchors, anchors[1:]):
        if t <= a1:
            return p0 + (p1 - p0) * (t - a0) / max(1e-6, a1 - a0)
    return anchors[-1][1]


def plan():
    """每个输出帧 -> (shot, perf_shot, p)。"""
    out = []
    h0, h1, _ = SEC["hook"]
    w0, w1, ws = SEC["why"]
    b0, b1, bs = SEC["back"]
    f0, f1, fs = SEC["front"]
    d0, d1, _ = SEC["drill"]
    e0, e1, _ = SEC["end"]
    for i in range(int(DUR * FPS)):
        t = i / FPS
        if t < h1:   # 开场：0.2→1.15 半速，撞击后超慢放
            p = _pw([(0, 0.25), (1.8, A_IMPACT), (h1, A_IMPACT + 0.22)], t - h0)
            out.append(("A1", "A", p))
        elif t < w1:   # 侧面慢放到撞击，然后定格
            p = _pw([(0, 0.55), (ws[0][2] - w0, A_IMPACT)], t - w0)
            out.append(("A2", "A", p))
        elif t < b1:
            sb = [x[1] - b0 for x in bs]
            p = _pw([(0, 0.0), (sb[0], 0.5), (sb[0] + 1.6, C_STEPS[0]), (sb[1], C_STEPS[0]), (sb[1] + 1.0, C_STEPS[1]),
                     (sb[2], C_STEPS[1]), (sb[2] + 0.9, C_STEPS[2]), (sb[2] + 2.6, 3.6)], t - b0)
            out.append(("C", "C", p))
        elif t < f1:
            sf = [x[1] - f0 for x in fs]
            p = _pw([(0, 0.0), (sf[0], 0.5), (sf[0] + 1.8, D_STEPS[0]), (sf[1], D_STEPS[0]), (sf[1] + 1.8, D_STEPS[1]),
                     (sf[2] + 1.0, 3.2)], t - f0)
            out.append(("D", "D", p))
        elif t < d1:   # 练习：后摔原速重放（复用 C 的帧）
            p = _pw([(0.6, 0.0), (4.2, 3.6)], t - d0)
            out.append(("C", "C", p))
        else:
            out.append(("C", "C", 3.6))
    return out


def key(shot, p):
    return f"{shot}_{int(round(p * 60)):04d}"


if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", DUR)
    for k, v in SEC.items():
        print(k, round(v[0], 2), round(v[1], 2))
    P = plan()
    print("frames", len(P), "unique", len({key(s, p) for s, _, p in P}))
