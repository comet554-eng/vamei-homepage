"""《单板从0到刻滑》第9课：中级道，陡了怎么办？新画风 + 动感背景音乐 B。
动作关键帧、镜头、字幕时间、音乐重拍和音效都在这里；../zero2carve-lib/render.py 渲 3D，composite.py 叠字幕出片。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "zero2carve-lib"))
from epbase import plain, timeline, pw, key, ease

FPS = 30
STYLE = "day"
MUSIC = "drive"
TITLE = "第9课 · 中级道，陡了怎么办"
LEVEL = "L3 中级道"
LESSON = 9
SLOPE = 20.0
R = 2.4

# ------------------------------------------------------------------ 原理和数据
# 雪道分级（阿尔卑斯常用标准）：蓝道最陡约 25%（≈14°），红道 25–40%（≈14–22°），黑道 >40%（>22°）
GRADES = [("初级道", 12), ("中级道", 20), ("高级道", 30)]
PULL = {d: math.sin(math.radians(d)) for _, d in GRADES}     # 往下拉的力占体重的比例
MORE = PULL[20] / PULL[12] - 1

# ------------------------------------------------------------------ 弯的几何
CA = (0.0, R)                      # 弯 A：前刃 → 后刃，板头从 -x 顺时针转到 +x
TRAV = 1.0                         # 两个弯之间后刃横切的距离
CB = (TRAV, 2 * R + 0.1 + R)       # 弯 B：后刃 → 前刃，逆时针


def pa(phi):
    p = math.radians(phi); return CA[0] - R * math.sin(p), CA[1] + R * math.cos(p)


def pb(phi):
    p = math.radians(phi); return CB[0] + R * math.sin(p), CB[1] - R * math.cos(p)


def edge(phi_from_fall):
    """离下坡线越远立得越高；正对下坡时平板。"""
    return 24 * min(1.0, abs(phi_from_fall) / 50)          # 坡陡了，刃要立得比坡还高


BASE = dict(slope=SLOPE, pz=0.74, arm=22, ab=35, elb=25, knee=(0.0, 1.0, 0.25), trail=1)


def A(phi, **kw):
    x, y = pa(phi); d = dict(gx=x, gy=y, yaw=phi)
    f = phi - 90                                    # >0 还在前刃一侧（面朝山上），<0 已到后刃
    d.update(broll=-edge(f) if f > 0 else edge(f), tilt=-4 if f > 8 else (3 if f < -8 else 0)); d.update(kw); return d


def B(phi, **kw):
    x, y = pb(phi); d = dict(gx=x, gy=y, yaw=phi)
    f = 90 - phi                                    # >0 还在后刃，<0 到前刃
    d.update(broll=edge(f) if f > 0 else -edge(f), tilt=3 if f > 8 else (-4 if f < -8 else 0)); d.update(kw); return d


WP = sum(((0.0, 0.0),) + tuple(pa(a) for a in (150, 120, 90, 60, 30, 0)) + (pb(0),) + tuple(pb(a) for a in (30, 60, 90, 120, 150, 180)), ())

# S：完整 S 弯（前刃横切 → 弯 A 换后刃 → 后刃横切 → 弯 B 换前刃 → 停）
S = [
    (0.0, dict(BASE, **A(180, tw=WP, tn=0))),
    (0.6, A(170, twist=-15, face=-20)),
    (1.3, A(130, tn=1, twist=-25, face=-30)),
    (1.8, A(100, tn=2, pz=0.86)),
    (2.1, A(90, tn=3, pz=0.88)),
    (2.5, A(60, tn=4, pz=0.78, twist=-15, face=-15)),
    (3.2, A(20, tn=5, twist=0, face=0)),
    (3.5, A(0, tn=6)),
    (4.0, dict(gx=TRAV, gy=2 * R + 0.1, yaw=0, broll=15, tn=7, twist=15, face=20)),
    (4.6, B(30, tn=8, twist=25, face=30)),
    (5.0, B(70, tn=9, pz=0.86)),
    (5.3, B(90, tn=10, pz=0.88)),
    (5.7, B(120, tn=11, pz=0.78, twist=15, face=15)),
    (6.4, B(165, tn=12, twist=0, face=0)),
    (6.8, B(180, tn=13, broll=-24)),
    (7.3, dict(gx=pb(180)[0] - 0.3, yaw=180)),
    (7.8, dict()),
]
S_KEYS = dict(a_start=0.6, a_flat=2.1, a_end=3.5, b_flat=5.3, b_end=6.8)
S_END = 7.8

# W：错误示范——坡一陡就怕，往后仰着“站直”，板尾吃重、板头发飘，转不过来，板往山下冲，人往后摔
W = [
    (0.0, dict(BASE, **B(15, tw=(0.0, 0.0), tn=0, tilt=14, pz=0.80))),
    (0.6, B(30, tilt=20, pz=0.78)),
    (1.2, B(55, tilt=24, py=-0.10, broll=10, arm=45, ab=40)),
    (1.6, dict(gx=pb(68)[0], gy=pb(68)[1] + 0.6, yaw=68, tilt=32, pz=0.62, py=-0.25, broll=6, arm=70, ab=45)),
    (2.0, dict(gx=pb(70)[0], gy=pb(70)[1] + 1.4, yaw=70, tilt=55, pz=0.32, py=-0.45, arm=-35, ab=25, elb=10, broll=4)),
    (2.5, dict(gy=pb(70)[1] + 1.8, tilt=72, pz=0.16, py=-0.52, arm=-30, elb=30, knee=(0.0, 0.3, 1.0))),
    (3.0, dict()),
]
W_BACK = 1.2

# X：原理——侧面看身体和坡面：垂直坡面（对）↔ 跟地面垂直（相对板后仰 20°，错）
X = [
    (0.0, dict(BASE, trail=0, broll=24, tilt=0, pz=0.76)),
    (1.0, dict()),
    (2.2, dict(tilt=20, pz=0.80)),
    (3.4, dict()),
    (4.6, dict(tilt=-2, pz=0.72)),
    (5.4, dict()),
]
X_KEYS = dict(good=1.0, back=2.2, good2=4.6)

PERF = dict(W=W, S=S, X=X)
SHOT_PERF = dict(W="W", X="X", S="S")
COVER3D = dict(perf="S", p=4.6, cam=((1.4, 2.6, 0.9), (0.0, 0.0, 0.5), 34), ring=None)
VO_EXTRA = dict(steps="陡坡上的S弯，四步。")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    if shot in ("W", "S"):
        pos, tgt = (gx + 1.0, gy + 5.0, 1.7), (gx - 0.4, gy - 0.2, 1.0)
    elif shot == "X":       # 沿板长轴看过去，侧看身体和坡面
        pos, tgt = (gx + 5.6, gy + 0.05, 0.95), (gx, gy + 0.05, 0.40)
        return _slope(pos, s), _slope(tgt, s), 30
    else:
        raise KeyError(shot)
    return _slope(pos, s), _slope(tgt, s), 30


ARC_A = (180, 150, 120, 90, 60, 30, 0)
ARC_B = (0, 30, 60, 90, 120, 150, 180)


def extra_points(P, J):
    from mathutils import Vector
    m = J["board_m"]; sm = J["slope_m"]
    from mathutils import Matrix
    pts = {"up_slope": J["pelvis"] + (J["slope_m"] @ Vector((0, 0, 1.0, 0))).xyz, "up_world": J["pelvis"] + Vector((0, 0, 1.0)),
           "board": m @ Vector((0, 0, 0.02)), "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)),
           "toe": m @ Vector((0, 0.125, 0.0)), "heel": m @ Vector((0, -0.125, 0.0))}
    pts.update({f"A{a}": sm @ Vector((*pa(a), 0.02)) for a in ARC_A})
    pts.update({f"B{a}": sm @ Vector((*pb(a), 0.02)) for a in ARC_B})
    return pts


# ------------------------------------------------------------------ 字幕（不配音：按阅读速度排时间）
SECTIONS = [   # (名字, 开头留白, 字幕, 结尾留白)
    ("hook", 0.3, ["中级道一陡，就{r|往后坐}？"], 0.4),
    ("why", 0.3, ["中级道{w|14°到22°}，陡一大截。",
                  "12°变20°，往下拉的力从{b|21%}到{r|34%}——{r|多六成}！",
                  "怕了想站“直”？20°的坡上，那等于相对板{r|后仰20°}！",
                  "重心到板尾，板头发飘：{r|转不动、刹不住}。",
                  "反过来：身体{w|垂直坡面}，往山下压！"], 0.4),
    ("steps", 1.2, ["①看山下，身体{w|垂直坡面}，压前脚。",
                    "②弯{w|短一点}，每个都走到横过来。",
                    "③20°的坡，立刃{w|超过20°}。",
                    "④膝盖更弯、重心更低，{w|S弯}连着下。"], 0.6),
    ("drill", 0.3, ["先挑中级道最缓的一段，连续S弯。",
                    "过关：{w|不后坐}，速度{w|不越滑越快}。",
                    "第一次上中级道啥感觉？{w|评论区}说说！"], 0.4),
    ("end", 0.3, [("下一课：从搓雪到{w|刻滑}！", 3.0)], 0.4),
]
SUBS, SEC, DUR = timeline(SECTIONS)


def _q(p, n):
    return round(p * n) / n


def plan():
    out = []
    h0, h1, _ = SEC["hook"]; w0, w1, ws = SEC["why"]; s0, s1, ss = SEC["steps"]; d0, d1, _ = SEC["drill"]
    K = S_KEYS
    for i in range(int(DUR * FPS)):
        t = i / FPS
        if t < h1:
            out.append(("W", "W", _q(pw([(0, 0.3), (h1 - 0.6, 2.7), (h1, 3.0)], t - h0), 30)))
        elif t < w1:          # 侧面看身体：对 → 后仰（错）→ 对
            a = [x[1] - w0 for x in ws]
            out.append(("X", "X", _q(pw([(0, 0.0), (a[2], X_KEYS["good"]), (a[2] + 2.0, X_KEYS["back"] + 1.2),
                                         (a[4], X_KEYS["back"] + 1.2), (a[4] + 1.8, 5.4)], t - w0), 20)))
        elif t < s1:
            st = [x[1] - s0 for x in ss]
            out.append(("S", "S", _q(pw([(st[0], 0.0), (st[1], K["a_start"] + 0.5), (st[2] - 0.2, K["a_end"]),
                                         (st[3] - 0.2, K["b_flat"]), (st[3] + 3.0, S_END)], t - s0), 30)))
        else:
            out.append(("S", "S", _q(pw([(0.3, 0.0), (0.3 + S_END * 1.3, S_END)], t - d0), 30)))
    return out


def music_hits():
    hits = [SEC[k][0] for k in ("why", "steps", "drill")]
    T_BACK = next(i for i, (s, _, p) in enumerate(plan()) if p >= 2.0) / FPS
    ws = SEC["why"][2]
    sfx = [(T_BACK + 0.2, "boom"), (ws[1][1] + 1.6, "ding"), (ws[1][1] + 3.6, "ding"), (ws[2][1] + 2.5, "boom")]
    sfx += [(h - 0.25, "whoosh") for h in hits]
    return hits, sfx


if __name__ == "__main__":
    print({d: round(v, 3) for d, v in PULL.items()}, "more", round(MORE, 2))
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), {k: (round(v[0], 1), round(v[1], 1)) for k, v in SEC.items()})
    P = plan()
    print("frames", len(P), "unique", len({key(s, p) for s, _, p in P}))
