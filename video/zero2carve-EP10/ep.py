"""《单板从0到刻滑》第10课：从搓雪到刻滑。新画风 + 动感背景音乐 B。
同一条 S 弯做两遍：搓雪（板尾外甩、雪痕一大片）和刻滑（板顺着弧线走、雪痕一条线）。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "zero2carve-lib"))
from epbase import plain, timeline, pw, key, ease

FPS = 30
STYLE = "day"
MUSIC = "drive"
TITLE = "第10课 · 从搓雪到刻滑"
LEVEL = "L4 进阶"
LESSON = 10
SLOPE = 12.0

# ------------------------------------------------------------------ 原理和数据：理想刻滑弯半径 R ≈ R侧切 · cos(立刃角)（Jentschura & Fahrbach 2004）
RSC = 7.0
EDGES = [30, 45, 60]
RADIUS = {e: RSC * math.cos(math.radians(e)) for e in EDGES}


def s_turn(R, edge_max, skid, lean, trw, dt=0.18, step=15, trav=1.0):
    """一条 S：前刃横切 → 弯 A（顺时针，换后刃）→ 后刃横切 → 弯 B（逆时针，换前刃）→ 停。
    skid = 板尾外甩角（搓雪），lean = 身体往弯里倒的程度（刻滑），每 step° 一个关键帧。"""
    CA = (0.0, R)
    CB = (trav, 2 * R + 0.1 + R)
    pa = lambda f: (CA[0] - R * math.sin(math.radians(f)), CA[1] + R * math.cos(math.radians(f)))
    pb = lambda f: (CB[0] + R * math.sin(math.radians(f)), CB[1] - R * math.cos(math.radians(f)))

    def pose(x, y, heading, side_from_fall, toe_first):
        """side_from_fall>0：还在前一条刃上；toe_first：这个弯开头是前刃。"""
        k = min(1.0, abs(side_from_fall) / 50)
        on_toe = (side_from_fall > 0) == toe_first
        e = edge_max * k
        broll = -e if on_toe else e
        tl = (-1 if on_toe else 1) * (4 + lean * k)
        d = dict(gx=x, gy=y, yaw=heading, broll=broll, tilt=tl,
                 pz=0.82 - 0.18 * lean / 30 * k, py=(0.18 if on_toe else -0.18) * lean / 30 * k)
        return d
    keys, wp, t = [], [(0.0, 0.0)], 0.0
    base = dict(slope=SLOPE, pz=0.80, arm=25, ab=38, elb=25, knee=(0.0, 1.0, 0.25), trail=1, trw=trw)
    x, y = pa(180)
    keys.append((0.0, dict(base, **pose(x, y, 180, 90, True), tn=0)))
    t = 0.5
    phis = list(range(180, -1, -step))
    for f in phis:
        x, y = pa(f); wp.append((x, y))
        sk = skid * math.sin(math.radians(180 - f)) if 0 < f < 180 else 0
        keys.append((t, dict(pose(x, y, f - sk, f - 90, True), tn=len(wp) - 1)))
        t += dt * (1.4 if abs(f - 90) > 60 else 1.0)
    x, y = trav, 2 * R + 0.1; wp.append((x, y)); t += 0.3
    keys.append((t, dict(pose(x, y, 0, -90, True), tn=len(wp) - 1)))
    mid = t
    for f in range(0, 181, step):
        x, y = pb(f); wp.append((x, y)); t += dt * (1.4 if abs(f - 90) > 60 else 1.0)
        sk = skid * math.sin(math.radians(f)) if 0 < f < 180 else 0
        keys.append((t, dict(pose(x, y, f + sk, 90 - f, False), tn=len(wp) - 1)))
    x, y = pb(180)
    keys.append((t + 0.5, dict(gx=x - 0.3, gy=y, yaw=180, broll=-18, tilt=-4, pz=0.80, py=0.0)))
    keys.append((t + 1.0, dict()))
    keys[0][1]["tw"] = sum(wp, ())
    return keys, t + 1.0, mid, CA, CB, R


# K：搓雪 S 弯——半径小、立刃低、板尾外甩 30°，雪痕一大片
K, K_END, K_MID, K_CA, K_CB, K_R = s_turn(R=3.0, edge_max=14, skid=30, lean=0, trw=1.1, dt=0.17)
# C：刻滑 S 弯——立刃 45°、身体往弯里倒，板顺着弧线走，半径 ≈ 7 × cos45° ≈ 4.9 m，雪痕一条线
C, C_END, C_MID, C_CA, C_CB, C_R = s_turn(R=RADIUS[45], edge_max=45, skid=0, lean=30, trw=0.16, dt=0.20)

PERF = dict(K=K, C=C)
SHOT_PERF = dict(H="K", TK="K", TC="C", S="C")
COVER3D = dict(perf="C", p=C_MID * 0.55, cam=((1.6, 2.4, 0.9), (0.0, 0.0, 0.5), 34), ring=None)
VO_EXTRA = dict(steps="刻滑入门，四步。")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    if shot in ("H", "S"):
        pos, tgt = (gx + 1.2, gy + 5.6, 1.9), (gx - 0.4, gy - 0.2, 1.0)
    elif shot == "TK":
        pos, tgt = (-1.2, 6.2, 19.5), (-1.2, 6.2, 0.0)
    elif shot == "TC":
        pos, tgt = (0.4, 10.0, 30.0), (0.4, 10.0, 0.0)
    else:
        raise KeyError(shot)
    return _slope(pos, s), _slope(tgt, s), 30


def extra_points(P, J):
    from mathutils import Vector
    m = J["board_m"]
    return {"board": m @ Vector((0, 0, 0.02)), "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)),
            "toe": m @ Vector((0, 0.125, 0.0)), "heel": m @ Vector((0, -0.125, 0.0))}


# ------------------------------------------------------------------ 字幕（不配音：按阅读速度排时间）
SECTIONS = [   # (名字, 开头留白, 字幕, 结尾留白)
    ("hook", 0.3, ["同样是转弯，你的雪痕为啥{r|一大片}？"], 0.4),
    ("why", 0.3, ["搓雪：板尾往外甩，雪是{r|刮}下来的——雪痕一大片。",
                  "刻滑：板顺着自己的弧线走，雪是{w|切}开的——雪痕{w|一条线}！",
                  "板的两条边是弧形的，侧切半径大约{b|7米}。",
                  "刃立得越高，弯越小：30°是{b|6.1米}，45°是{b|4.9米}，60°只剩{r|3.5米}！",
                  "所以刻滑的关键：{w|刃立得高}，板{w|不甩}。"], 0.4),
    ("steps", 1.2, ["①缓坡，中等速度，先用{w|后刃}横切。",
                    "②膝盖和髋往弯里倒，把刃{w|立高}。",
                    "③别甩板尾，让板{w|自己转}过来。",
                    "④回头看雪痕：{w|一条线}就对了！"], 0.6),
    ("drill", 0.3, ["缓坡：只做后刃横切，立高刃，看雪痕。",
                    "过关：雪痕{w|不超过一个板宽}。",
                    "晒晒你的雪痕，{w|评论区}比一比！"], 0.4),
    ("end", 0.3, [("下一课：刻滑换刃，{w|连起来}！", 3.0)], 0.4),
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
            out.append(("H", "K", _q(pw([(0, 0.5), (h1, K_MID + 0.6)], t - h0), 30)))
        elif t < w1:
            a = [x[1] - w0 for x in ws]
            if t - w0 < a[1]:          # 俯视：搓雪的整条 S
                out.append(("TK", "K", _q(pw([(0, 0.0), (a[1] - 0.2, K_END)], t - w0), 15)))
            else:                      # 俯视：刻滑的整条 S
                out.append(("TC", "C", _q(pw([(a[1], 0.0), (a[2] + 1.0, C_END)], t - w0), 15)))
        elif t < s1:
            st = [x[1] - s0 for x in ss]
            out.append(("S", "C", _q(pw([(0, 0.0), (st[3] + 2.0, C_END)], t - s0), 30)))
        else:
            out.append(("S", "C", _q(pw([(0.3, 0.0), (0.3 + C_END * 1.2, C_END)], t - d0), 30)))
    return out


def music_hits():
    hits = [SEC[k][0] for k in ("why", "steps", "drill")]
    ws = SEC["why"][2]
    sfx = [(ws[1][1] + 0.3, "whoosh"), (ws[3][1] + 1.6, "ding"), (ws[3][1] + 3.4, "ding"), (ws[3][1] + 5.2, "ding")]
    sfx += [(h - 0.25, "whoosh") for h in hits]
    return hits, sfx


if __name__ == "__main__":
    print({e: round(r, 2) for e, r in RADIUS.items()}, "K_END", round(K_END, 2), "C_END", round(C_END, 2))
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), {k: (round(v[0], 1), round(v[1], 1)) for k, v in SEC.items()})
    P = plan()
    print("frames", len(P), "unique", len({key(s, p) for s, _, p in P}))
