"""《单板从0到刻滑》第8课：前刃换后刃，连起来就是 S 弯。新画风 + 动感背景音乐 B。
动作关键帧、镜头、字幕时间、音乐重拍和音效都在这里；../zero2carve-lib/render.py 渲 3D，composite.py 叠字幕出片。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "zero2carve-lib"))
from epbase import plain, timeline, pw, key, ease

FPS = 30
STYLE = "day"
MUSIC = "drive"
TITLE = "第8课 · 连起来，S弯"
LEVEL = "L2 学转弯"
LESSON = 8
SLOPE = 12.0
R = 3.0

# ------------------------------------------------------------------ 原理和数据：弯尾板头离下坡线 β，下滑力顺着板的份额 = cos β
BETAS = [90, 60, 30]
SHARE = {b: math.cos(math.radians(b)) for b in BETAS}

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
    return 16 * min(1.0, abs(phi_from_fall) / 50)


BASE = dict(slope=SLOPE, pz=0.80, arm=22, ab=35, elb=25, knee=(0.0, 1.0, 0.25), trail=1)


def A(phi, **kw):
    x, y = pa(phi); d = dict(gx=x, gy=y, yaw=phi)
    f = phi - 90                                    # >0 还在前刃一侧（面朝山上），<0 已到后刃
    d.update(broll=-edge(f) if f > 0 else edge(f), tilt=-12 if f > 8 else (10 if f < -8 else 0)); d.update(kw); return d


def B(phi, **kw):
    x, y = pb(phi); d = dict(gx=x, gy=y, yaw=phi)
    f = 90 - phi                                    # >0 还在后刃，<0 到前刃
    d.update(broll=edge(f) if f > 0 else -edge(f), tilt=10 if f > 8 else (-12 if f < -8 else 0)); d.update(kw); return d


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
    (6.8, B(180, tn=13, broll=-18)),
    (7.3, dict(gx=pb(180)[0] - 0.3, yaw=180)),
    (7.8, dict()),
]
S_KEYS = dict(a_start=0.6, a_flat=2.1, a_end=3.5, b_flat=5.3, b_end=6.8)
S_END = 7.8

# W：错误示范——前刃换后刃时往后坐，板从脚下冲出去，一屁股坐倒
W = [
    (0.0, dict(BASE, **A(180, tw=(0.0, 0.0), tn=0))),
    (0.7, A(150)),
    (1.3, A(105, tilt=20, pz=0.70, py=-0.15, arm=50)),
    (1.7, A(85, tilt=38, pz=0.55, py=-0.30, arm=70, ab=40, broll=4)),
    (2.1, dict(gx=pa(70)[0], gy=pa(70)[1] + 0.3, yaw=72, tilt=55, pz=0.30, py=-0.45, arm=-35, ab=25, elb=10, broll=3)),
    (2.6, dict(gy=pa(70)[1] + 0.45, tilt=70, pz=0.16, py=-0.52, arm=-30, elb=30, knee=(0.0, 0.3, 1.0))),
    (3.0, dict()),
]
W_SIT = 1.7

PERF = dict(W=W, S=S)
SHOT_PERF = dict(W="W", T="S", S="S")
COVER3D = dict(perf="S", p=4.2, cam=((1.4, 2.6, 1.0), (0.0, 0.0, 0.5), 34), ring=None)
VO_EXTRA = dict(steps="前刃换后刃，四步。")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    if shot in ("W", "S"):
        pos, tgt = (gx + 1.0, gy + 5.0, 1.7), (gx - 0.4, gy - 0.2, 1.0)
    elif shot == "T":
        pos, tgt = (-1.2, 6.2, 19.5), (-1.2, 6.2, 0.0)
    else:
        raise KeyError(shot)
    return _slope(pos, s), _slope(tgt, s), 30


ARC_A = (180, 150, 120, 90, 60, 30, 0)
ARC_B = (0, 30, 60, 90, 120, 150, 180)


def extra_points(P, J):
    from mathutils import Vector
    m = J["board_m"]; sm = J["slope_m"]
    pts = {"board": m @ Vector((0, 0, 0.02)), "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)),
           "toe": m @ Vector((0, 0.125, 0.0)), "heel": m @ Vector((0, -0.125, 0.0))}
    pts.update({f"A{a}": sm @ Vector((*pa(a), 0.02)) for a in ARC_A})
    pts.update({f"B{a}": sm @ Vector((*pb(a), 0.02)) for a in ARC_B})
    return pts


# ------------------------------------------------------------------ 字幕（不配音：按阅读速度排时间）
SECTIONS = [   # (名字, 开头留白, 字幕, 结尾留白)
    ("hook", 0.3, ["S弯，为啥总在{r|换后刃}时摔？"], 0.4),
    ("why", 0.3, ["S弯，就是前刃弯和后刃弯{w|连起来}。",
                  "速度靠什么控？看弯尾：板头{w|离开下坡线}多少。",
                  "横过来90°，下滑力顺着板{g|0%}；只转到60°，还剩{w|50%}；30°，{r|87%}！",
                  "弯不走完，速度一路攒，最后只能{r|摔着停}。",
                  "换后刃最常见的错：{r|往后坐}——手往前，重心压在板中间！"], 0.4),
    ("steps", 1.2, ["①前刃走完上一个弯，{w|看向}下一个方向。",
                    "②手往前，{w|别后坐}，板头指向山下。",
                    "③过了下坡线，脚尖抬起，{w|换后刃}！",
                    "④后刃把弯走完，再接前刃弯——{w|S弯}！"], 0.6),
    ("drill", 0.3, ["缓坡：连续S弯六个，每个都走到{w|横过来}。",
                    "过关：一路{w|不加速}，换后刃{w|不坐下}。",
                    "你能连几个？{w|评论区}报个数！"], 0.4),
    ("end", 0.3, [("下一课：中级道，{w|陡了}怎么办？", 3.0)], 0.4),
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
            out.append(("W", "W", _q(pw([(0, 0.4), (h1 - 0.6, 2.7), (h1, 3.0)], t - h0), 30)))
        elif t < w1:          # 俯视：整条 S 慢放一遍
            a = [x[1] - w0 for x in ws]
            out.append(("T", "S", _q(pw([(0, 0.0), (a[1], K["a_end"]), (a[3], K["b_end"]), (a[3] + 1.5, S_END)], t - w0), 20)))
        elif t < s1:
            st = [x[1] - s0 for x in ss]
            out.append(("S", "S", _q(pw([(st[0], 0.0), (st[1], K["a_start"] + 0.5), (st[2] - 0.2, K["a_flat"]),
                                         (st[3] - 0.2, K["a_end"] + 0.3), (st[3] + 4.0, S_END)], t - s0), 30)))
        else:
            out.append(("S", "S", _q(pw([(0.3, 0.0), (0.3 + S_END * 1.3, S_END)], t - d0), 30)))
    return out


def music_hits():
    hits = [SEC[k][0] for k in ("why", "steps", "drill")]
    T_SIT = next(i for i, (s, _, p) in enumerate(plan()) if p >= W_SIT) / FPS
    ws = SEC["why"][2]
    sfx = [(T_SIT + 0.4, "boom"), (ws[2][1] + 1.0, "ding"), (ws[2][1] + 3.0, "ding"), (ws[2][1] + 5.0, "ding")]
    sfx += [(h - 0.25, "whoosh") for h in hits]
    return hits, sfx


if __name__ == "__main__":
    print({b: round(v, 2) for b, v in SHARE.items()}, pa(90), pb(180))
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), {k: (round(v[0], 1), round(v[1], 1)) for k, v in SEC.items()})
    P = plan()
    print("frames", len(P), "unique", len({key(s, p) for s, _, p in P}))
