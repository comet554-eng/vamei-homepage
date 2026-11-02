"""《单板从0到刻滑》第11课：刻滑换刃，连起来。新画风 + 背景音乐 C（阳光律动）。
同一条 S 弯做两遍：错误（换刃时站直，板一平就甩，第二个弯变回搓雪）和正确（膝盖一直弯，身体先倒过去，两个弯都是一条线）。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "zero2carve-lib"))
from epbase import plain, timeline, pw, key, ease

FPS = 30
STYLE = "day"
MUSIC = "bounce"
TITLE = "第11课 · 刻滑换刃，连起来"
LEVEL = "L4 进阶"
LESSON = 11
SLOPE = 12.0

# ------------------------------------------------------------------ 原理和数据：匀速圆周的受力平衡 tanφ = v²/(gR)（示意：忽略坡面分量）
R = 7.0 * math.cos(math.radians(45))       # 第10课：侧切 7 米、立刃 45° → 弯半径约 4.9 米
SPEEDS = [15, 20, 25]                       # km/h
LEAN = {v: math.degrees(math.atan((v / 3.6) ** 2 / (9.81 * R))) for v in SPEEDS}


def s_turn(A, B, pz_mid, dt=0.20, step=15, trav=1.0):
    """一条 S：后刃横切 → 弯 A（顺时针，换后刃）→ 换刃 → 弯 B（逆时针，换前刃）→ 停。
    A/B = dict(edge, skid, lean, w)：最大立刃角、板尾外甩角、身体往弯里倒的程度、雪痕宽度。pz_mid = 换刃那一下骨盆高度。"""
    CA = (0.0, R)
    CB = (trav, 2 * R + 0.1 + R)
    pa = lambda f: (CA[0] - R * math.sin(math.radians(f)), CA[1] + R * math.cos(math.radians(f)))
    pb = lambda f: (CB[0] + R * math.sin(math.radians(f)), CB[1] - R * math.cos(math.radians(f)))

    def pose(x, y, heading, side_from_fall, toe_first, T):
        k = min(1.0, abs(side_from_fall) / 50)
        on_toe = (side_from_fall > 0) == toe_first
        e = T["edge"] * k
        lean = T["lean"]
        pz = pz_mid + (0.82 - 0.18 * lean / 30 - pz_mid) * k
        return dict(gx=x, gy=y, yaw=heading, broll=-e if on_toe else e, tilt=(-1 if on_toe else 1) * (4 + lean * k),
                    pz=pz, py=(0.18 if on_toe else -0.18) * lean / 30 * k)
    keys, wp, ws = [], [(0.0, 0.0)], []
    base = dict(slope=SLOPE, pz=0.80, arm=25, ab=38, elb=25, knee=(0.0, 1.0, 0.25), trail=1)
    x, y = pa(180)
    keys.append((0.0, dict(base, **pose(x, y, 180, 90, True, A), tn=0)))
    t = 0.5
    for f in range(180, -1, -step):
        x, y = pa(f); wp.append((x, y)); ws.append(A["w"])
        sk = A["skid"] * math.sin(math.radians(180 - f)) if 0 < f < 180 else 0
        keys.append((t, dict(pose(x, y, f - sk, f - 90, True, A), tn=len(wp) - 1)))
        t += dt * (1.4 if abs(f - 90) > 60 else 1.0)
    x, y = trav, 2 * R + 0.1; wp.append((x, y)); ws.append(B["w"]); t += 0.3
    keys.append((t, dict(pose(x, y, 0, -90, True, B), pz=pz_mid, tn=len(wp) - 1)))
    mid = t
    for f in range(0, 181, step):
        x, y = pb(f); wp.append((x, y)); ws.append(B["w"]); t += dt * (1.4 if abs(f - 90) > 60 else 1.0)
        sk = B["skid"] * math.sin(math.radians(f)) if 0 < f < 180 else 0
        keys.append((t, dict(pose(x, y, f + sk, 90 - f, False, B), tn=len(wp) - 1)))
    x, y = pb(180)
    keys.append((t + 0.5, dict(gx=x - 0.3, gy=y, yaw=180, broll=-18, tilt=-4, pz=0.80, py=0.0)))
    keys.append((t + 1.0, dict()))
    keys[0][1]["tw"] = sum(wp, ())
    keys[0][1]["tws"] = tuple(ws)
    return keys, t + 1.0, mid


CARVE = dict(edge=45, skid=0, lean=30, w=0.16)
# W：错误示范——弯 A 刻得好好的，换刃时站直，板一平就甩，弯 B 变回搓雪（雪痕从一条线变成一大片）
W, W_END, W_MID = s_turn(CARVE, dict(edge=14, skid=32, lean=0, w=1.1), pz_mid=0.95)
# C：正确——膝盖一直弯着，身体先倒过去，两个弯都是一条线
C, C_END, C_MID = s_turn(CARVE, CARVE, pz_mid=0.70)

PERF = dict(W=W, C=C)
SHOT_PERF = dict(H="W", TW="W", TC="C", S="C")
COVER3D = dict(perf="C", p=C_MID * 0.55, cam=((1.6, 2.4, 0.9), (0.0, 0.0, 0.5), 34), ring=None)
VO_EXTRA = dict(steps="刻滑换刃，四步。")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    if shot in ("H", "S"):
        pos, tgt = (gx + 1.2, gy + 5.6, 1.9), (gx - 0.4, gy - 0.2, 1.0)
    elif shot in ("TW", "TC"):
        pos, tgt = (0.4, 10.0, 30.0), (0.4, 10.0, 0.0)
    else:
        raise KeyError(shot)
    return _slope(pos, s), _slope(tgt, s), 30


def extra_points(P, J):
    from mathutils import Vector
    m = J["board_m"]; sm = J["slope_m"]
    return {"board": m @ Vector((0, 0, 0.02)), "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)),
            "toe": m @ Vector((0, 0.125, 0.0)), "heel": m @ Vector((0, -0.125, 0.0)),
            "xover": sm @ Vector((1.0, 2 * R + 0.1, 0.02)),
            "turnA": sm @ Vector((-R, R, 0.02)), "turnB": sm @ Vector((1.0 + R, 3 * R + 0.1, 0.02))}


# ------------------------------------------------------------------ 字幕（不配音：按阅读速度排时间）
L = {v: round(LEAN[v]) for v in SPEEDS}
SECTIONS = [   # (名字, 开头留白, 字幕, 结尾留白)
    ("hook", 0.3, ["刻滑一换刃，为啥又变回{r|搓雪}？"], 0.4),
    ("why", 0.3, ["刻滑弯里，身体要{w|往弯里倒}——靠它扛住离心力。",
                  f"倒多少看速度：同一个5米的弯，\n时速15倒{{b|{L[15]}°}}，20倒{{b|{L[20]}°}}，25就得倒{{r|{L[25]}°}}！",
                  "换刃，就是身体从一边{w|倒到另一边}——\n中间板会平一下。",
                  "最常见的错：一换刃就{r|站直}，\n板一平就甩，又变回{r|搓雪}。",
                  "正确：膝盖{w|一直弯着}，\n身体先倒过去，板跟着翻刃。"], 0.4),
    ("steps", 1.2, ["①后刃刻到弯尾，膝盖{w|别伸直}。",
                    "②身体往{w|新弯}倒，从板上方越过去。",
                    "③板平的那一瞬，膝盖顶住，压{w|前刃}。",
                    "④前刃立高，弯{w|接着弯}——一条连续的S！"], 0.6),
    ("drill", 0.3, ["缓坡：连续刻滑S弯，每个弯都回头看雪痕。",
                    "过关：换刃那里雪痕{w|不断}、{w|不变宽}。",
                    "你能连刻几个弯？{w|评论区}报个数！"], 0.4),
    ("end", 0.3, [("下一课：刃再立高，{w|手能摸雪}！", 3.0)], 0.4),
]
SUBS, SEC, DUR = timeline(SECTIONS)


def _q(p, n):
    return round(p * n) / n


def plan():
    out = []
    h0, h1, _ = SEC["hook"]; w0, w1, ws = SEC["why"]; s0, s1, ss = SEC["steps"]; d0, d1, _ = SEC["drill"]
    for i in range(int(DUR * FPS)):
        t = i / FPS
        if t < h1:          # 错误示范：从弯 A 后半段到弯 B 甩起来
            out.append(("H", "W", _q(pw([(0, W_MID * 0.55), (h1, W_MID + 1.6)], t - h0), 30)))
        elif t < w1:
            a = [x[1] - w0 for x in ws]
            if t - w0 < a[3]:          # 正面：刻滑弯里身体倒进去，然后换刃
                if t - w0 < a[1]:      # 弯 A 慢放一遍
                    out.append(("S", "C", _q(pw([(0, 0.6), (a[1], C_MID - 0.6)], t - w0), 30)))
                elif t - w0 < a[2]:    # 讲数据时再放一遍（复用同一批帧）
                    out.append(("S", "C", _q(pw([(a[1], 0.6), (a[2], C_MID - 0.6)], t - w0), 30)))
                else:                  # 换刃慢放
                    out.append(("S", "C", _q(pw([(a[2], C_MID - 1.2), (a[3], C_MID + 1.0)], t - w0), 30)))
            elif t - w0 < a[4]:        # 俯视：错误——一条线变一大片
                out.append(("TW", "W", _q(pw([(a[3], 0.0), (a[4] - 0.3, W_END)], t - w0), 15)))
            else:                      # 俯视：正确——一条线到底
                out.append(("TC", "C", _q(pw([(a[4], 0.0), (w1 - w0 - 0.2, C_END)], t - w0), 15)))
        elif t < s1:
            st = [x[1] - s0 for x in ss]
            out.append(("S", "C", _q(pw([(0, 0.0), (st[1], C_MID - 1.0), (st[3], C_MID + 0.5), (st[3] + 3.0, C_END)], t - s0), 30)))
        else:
            out.append(("S", "C", _q(pw([(0.3, 0.0), (0.3 + C_END * 1.2, C_END)], t - d0), 30)))
    return out


def music_hits():
    hits = [SEC[k][0] for k in ("why", "steps", "drill")]
    ws = SEC["why"][2]
    sfx = [(ws[1][1] + 1.6, "ding"), (ws[1][1] + 3.4, "ding"), (ws[1][1] + 5.2, "ding"), (ws[3][1] + 0.3, "whoosh")]
    sfx += [(h - 0.25, "whoosh") for h in hits]
    return hits, sfx


if __name__ == "__main__":
    print("R", round(R, 2), {v: round(x, 1) for v, x in LEAN.items()}, "W_END", round(W_END, 2), "C_END", round(C_END, 2), "MID", round(C_MID, 2))
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), {k: (round(v[0], 1), round(v[1], 1)) for k, v in SEC.items()})
    P = plan()
    print("frames", len(P), "unique", len({key(s, p) for s, _, p in P}))
