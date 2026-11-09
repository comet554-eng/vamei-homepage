"""《单板新手课》第2课：单脚蹬行（竖屏 1080×1920，实拍 + 2D 演示 + 数据图）。
plan() 每帧给出 ("F", 实拍镜头, 素材内时间) 或 ("R", 演示镜头, 表演时间)；overlay() 画这一集自己的标注和图表。
动作参考《单板从0到刻滑》第3课（zero2carve-EP03）的关键帧。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "newbie-lib"))
from epbase import plain, timeline, pw, key, ease

FPS = 30
LESSON = 2
SERIES = "单板新手课"
NAME = "单脚蹬行"
TITLE = f"第{LESSON}课 · {NAME}"
STYLE = "day"
MUSIC = "pop"
TRACK = (1077, 0.0)             # Mixkit 免费音乐 #1077
MARKS = True              # 地上画雪印，看得出人在走

# ------------------------------------------------------------------ 数据（示意计算，见 方案.md）
ANGLES = (0, 20, 45)                                          # 蹬的方向和板长轴的夹角
FWD = [round(100 * math.cos(math.radians(a))) for a in ANGLES]   # 往前的分力 %：100 / 94 / 71
SIDE = [round(100 * math.sin(math.radians(a))) for a in ANGLES]  # 侧向分力 %：0 / 34 / 71

GROUND = 0.09          # 后脚踩在雪上时脚踝的高度

# ------------------------------------------------------------------ 动作
def _strides(t0, g0, n, dur=1.0, step=0.9, lfy=None, extra=None, lift=0.24):
    """后脚一步一步蹬：落脚 → 蹬到后面 → 抬脚收回。落地时脚在雪上不动（gx+lfx 不变）。"""
    keys, t, g = [], t0, g0
    for i in range(n):
        e = (extra[i % len(extra)] if extra else {})
        a = dict(gx=g + 0.55 * step, lfx=-0.05 - 0.55 * step, lfz=GROUND, pz=0.77)
        if lfy is not None:
            a["lfy"] = lfy
        keys += [
            (t + 0.45 * dur, dict(a, **e)),
            (t + 0.70 * dur, dict(gx=g + 0.78 * step, lfx=-0.30, lfz=lift, pz=0.80)),
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

# X：错误1——后脚跑到板尾后面蹬，板绕着前脚打转
X = [
    (0.0, dict(lfw=1, lfx=-1.0, lfy=-0.20, lfz=GROUND, pz=0.80, yx=0.26)),
    (0.5, dict(gx=0.35, lfx=-1.35, tilt=5)),
    (0.8, dict(gx=0.50, lfx=-0.95, lfz=0.25, yaw=18)),
    (1.2, dict(gx=0.60, lfx=-0.65, lfz=0.20, yaw=55, tilt=15, arm=60, ab=40, elb=10)),
    (1.7, dict(gx=0.65, lfx=-0.50, lfy=-0.45, lfz=GROUND, yaw=85, tilt=24, pz=0.72, arm=80, ab=45)),
    (2.3, dict(yaw=90, tilt=18)),
]

# Z：错误2——步子太大，脚伸到很远，人晃
_z, _zt, _zg = _strides(0.4, 0.0, 2, dur=1.4, step=1.7, lift=0.30,
                        extra=[dict(tilt=14, arm=60, ab=55, elb=8, pz=0.86), dict(tilt=-16, arm=70, ab=20, elb=8, pz=0.86)])
Z = [(0.0, dict(lfw=1, lfx=-0.05, lfy=0.32, lfz=GROUND, pz=0.82, twist=35, face=25, arm=15, ab=30, elb=25))] + _z + [(_zt + 0.3, dict(tilt=0, arm=20, ab=35))]
Z_END = _zt + 0.3

# V：错误3——身体侧着、低头看脚
_v, _vt, _vg = _strides(0.4, 0.0, 2, dur=1.0, step=0.9)
V = [(0.0, dict(lfw=1, lfx=-0.05, lfy=0.32, lfz=GROUND, pz=0.82, twist=0, face=0, neck=40, curl=18, tilt=-12, arm=10, ab=18, elb=15))] + _v + [(_vt + 0.3, dict())]
V_END = _vt + 0.3

PERF = dict(Y=Y, X=X, Z=Z, V=V)
SHOT_PERF = dict(Y="Y", X="X", Z="Z", V="V", C="Y")


def cam(shot, p, P):
    gx = P["gx"]
    if shot == "X":            # 斜上方看，看得清板在转
        return (0.5 + 1.2, 3.0, 2.3), (0.4, 0.0, 0.35), 32
    if shot == "C":            # 封面
        return (gx + 1.5, 3.0, 1.05), (gx, 0.0, 0.55), 40
    return (gx + 1.7, 3.2, 1.2), (gx, 0.0, 0.50), 34


def extra_points(P, J):
    from mathutils import Vector
    m = J["board_m"]
    return {"bindL": m @ Vector((-0.26, 0, 0.08)), "bindR": m @ Vector((0.26, 0, 0.08)),
            "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)),
            "pad": m @ Vector((-0.10, 0, 0.03)), "board": m @ Vector((0, 0, 0.02))}


# ------------------------------------------------------------------ 字幕（不配音：按阅读速度排时间）
import epbase
epbase.CPS = 5.2
SECTIONS = [
    ("hook", 0.2, ["单板在平地上，{w|怎么往前走}？",
                   "排队、下缆车，全靠{w|单脚蹬行}。"], 0.1),
    ("keys", 0.3, ["①前脚{w|绑好}，后脚{w|解开}。",
                   "②肩膀和视线，{w|转向板头}。",
                   "③后脚放在{w|前刃一侧}，贴着板小步蹬。",
                   "④滑起来后，后脚{w|踩上止滑垫}。"], 0.6),
    ("why", 0.2, ["为什么要{b|顺着板}蹬？",
                  "顺着板蹬，力{g|全部}往前；",
                  "斜着45°蹬，只剩{r|约七成}往前，另一部分在推板{r|打转}。"], 0.5),
    ("mistakes", 0.2, ["{r|后脚跑到板尾后面}：板绕前脚转圈。",
                       "{r|步子太大}：脚伸太远，人跟着晃。",
                       "{r|身体侧着、低头}：越蹬越歪。"], 0.3),
    ("drill", 0.2, ["练习：平地上{w|蹬三步，滑一段}。",
                    "过关：蹬{w|20米}不打转，踩上板能滑{w|2~3米}。"], 0.3),
    ("end", 0.2, [("下一课：{w|直滑降}。", 2.6)], 0.3),
]
SUBS, SEC, DUR = timeline(SECTIONS)

# 实拍镜头：(素材ID, 入点秒, 横向平移起点 0..1, 终点 0..1)
FOOT = {
    "hook0": ("4016", 0.5, 0.55, 0.70),
    "hook1": ("4018", 5.8, 0.62, 0.72),
    "pass": ("3344", 1.0, 0.40, 0.55),
    "end": ("3348", 2.0, 0.45, 0.60),
}


def plan():
    out = []
    h0, h1, hs = SEC["hook"]; k0, k1, ks = SEC["keys"]; w0, w1, ws = SEC["why"]
    m0, m1, ms = SEC["mistakes"]; d0, d1, ds = SEC["drill"]; e0, e1, _ = SEC["end"]
    for i in range(int(round(DUR * FPS))):
        t = i / FPS
        if t < h1:
            cut = hs[1][1] - 0.1
            out.append(("F", "hook0", t) if t < cut else ("F", "hook1", t - cut))
        elif t < k1:
            a = [x[1] - k0 for x in ks]
            p = pw([(0, 0.0), (a[1], 0.0), (a[1] + 1.2, Y_STEPS[1]), (a[2], Y_STEPS[1]), (a[2] + 0.3, Y_STEPS[2]),
                    (a[3], Y_STEPS[3]), (a[3] + 2.4, Y_END)], t - k0)
            out.append(("R", "Y", p))
        elif t < w1:
            out.append(("R", "Y", Y_END))
        elif t < m1:
            a = [x[1] - m0 for x in ms]
            tt = t - m0
            if tt < a[1] - 0.1:
                out.append(("R", "X", pw([(0.2, 0.0), (a[1] - 0.4, 2.3)], tt)))
            elif tt < a[2] - 0.1:
                out.append(("R", "Z", pw([(a[1] - 0.1, 0.0), (a[2] - 0.2, Z_END)], tt)))
            else:
                out.append(("R", "V", pw([(a[2] - 0.1, 0.0), (m1 - m0, V_END)], tt)))
        elif t < d1:
            a = [x[1] - d0 for x in ds]
            if t - d0 < a[1] - 0.1:
                out.append(("R", "Y", pw([(0, Y_STEPS[2]), (a[1] - 0.1, Y_END)], t - d0)))
            else:
                out.append(("F", "pass", t - d0 - (a[1] - 0.1)))
        else:
            out.append(("F", "end", t - e0))
    return out


def music_hits():
    hits = [SEC[k][2][0][1] for k in ("keys", "why", "mistakes", "drill", "end")]
    sfx = [(SEC["hook"][2][1][1] + 0.1, "boom")]
    sfx += [(s[1] + 0.05, "ding") for s in SEC["keys"][2]]
    sfx += [(SEC["why"][2][1][1] + 0.6, "ding"), (SEC["why"][2][2][1] + 0.6, "boom")]
    sfx += [(s[1] + 0.05, "whoosh") for s in SEC["mistakes"][2]]
    return hits, sfx


# ------------------------------------------------------------------ 叠加（标注、图表）
def overlay(c, t, fr, pts, K):
    from vert import W, GOLD, ICE, RED, GREEN, INK, window, ramp, tag, ring, arrow, chips, stroke_text
    kind, shot, p = fr
    K.hook_title(c, t, NAME, "上下缆车全靠它", K.GOLD)
    k0, k1, ks = SEC["keys"]
    if k0 - 0.2 < t < k1 + 0.2:
        cur = max([j for j, s in enumerate(ks) if t >= s[1] - 0.2] or [0])
        chips(c, ["①解后脚", "②看板头", "③小步蹬", "④踩垫子"], cur, t, window(t, k0 + 0.1, k1, 0.3), y=300)
        if pts:
            a = window(t, *K.sec_window("keys", 0), 0.3)
            if a > 0:
                ring(c, *pts["bindR"], 50, GREEN, a, t)
                tag(c, "前脚 绑好", GREEN, 600, 1340, a, 38, "v")
                ring(c, *pts["ankleL"], 50, GOLD, a, t)
                tag(c, "后脚 解开", GOLD, 140, 1340, a, 38)
            a = window(t, *K.sec_window("keys", 1), 0.3)
            if a > 0:
                hx, hy = pts["head"]; nx, ny = pts["nose"]; bx, by = pts["board"]
                dx, dy = nx - bx, ny - by; L = math.hypot(dx, dy) or 1
                arrow(c, hx + 40 * dx / L, hy + 40, hx + 300 * dx / L, hy + 40 + 300 * dy / L, ICE, a, 8)
                stroke_text(c, "看板头方向", hx + 200 * dx / L, hy + 150 + 300 * dy / L, 38, ICE, a)
            a = window(t, *K.sec_window("keys", 2), 0.3)
            if a > 0:
                ring(c, *pts["ankleL"], 46, GOLD, a, t)
                tag(c, "前刃一侧 · 贴着板 · 小步", GOLD, 170, 1340, a, 36)
            a = window(t, *K.sec_window("keys", 3), 0.3)
            if a > 0:
                ring(c, *pts["pad"], 44, GREEN, a * ramp(t, ks[3][1] + 0.6, ks[3][1] + 0.9), t)
                tag(c, "后脚踩止滑垫，滑一段", GREEN, 190, 1340, a, 36, "v")
    w0, w1, ws = SEC["why"]
    if w0 - 0.2 < t < w1 + 0.2:
        a = window(t, w0 + 0.2, w1, 0.3)
        K.dim(c, a)
        items = [(f"{ang}°", FWD[i], (K.GREEN, K.GOLD, K.RED)[i], ws[1][1] + 0.3 + 0.5 * i if i < 2 else ws[2][1] + 0.3,
                  f"侧推 {SIDE[i]}%") for i, ang in enumerate(ANGLES)]
        K.bars(c, t, a, "蹬的方向偏离板多少度 → 往前的力还剩多少", items, 110, unit="%", edge=K.ICE,
               foot="示意 · 往前的力 = 蹬力 × cos(偏角)，其余变成侧推")
        _push_icon(c, t, a, K)
    m0, m1, ms = SEC["mistakes"]
    if m0 - 0.2 < t < m1 + 0.2:
        labs = ["后脚在板尾后面", "步子太大", "身体侧着、低头"]
        for j in range(3):
            a = window(t, *K.sec_window("mistakes", j), 0.25)
            if a > 0:
                tag(c, f"错误{j + 1}：{labs[j]}", RED, 60, 330, a, 44, "x")
                if pts:
                    q = ("ankleL", "ankleL", "head")[j]
                    ring(c, *pts[q], 60, RED, a, t)
    d0, d1, ds = SEC["drill"]
    if d0 - 0.2 < t < d1 + 0.2:
        if t < ds[1][1]:
            a = window(t, d0 + 0.2, ds[1][1] - 0.1, 0.3)
            tag(c, "蹬 · 蹬 · 蹬", GOLD, 130, 1340, a, 44)
            tag(c, "滑一段", GREEN, 600, 1340, a * ramp(t, d0 + 2.6, d0 + 2.9), 44)
        else:
            K.stamp(c, "过关", W / 2, 760, t, ds[1][1] + 0.2, GREEN, window(t, ds[1][1], d1, 0.3))
            a = window(t, ds[1][1] + 0.3, d1, 0.3)
            for j, s in enumerate(("蹬20米不打转", "踩上板滑2~3米")):
                tag(c, s, GREEN, 110 + j * 450, 1180, a * ramp(t, ds[1][1] + 0.5 + 0.4 * j, ds[1][1] + 0.8 + 0.4 * j), 40, "v")
    K.end_card(c, t, "直滑降")


def _push_icon(c, t, a, K):
    """图表上方的小俯视图：板 + 三个方向的蹬力箭头（只画 0° 和 45°）。"""
    from vert import ICE, GREEN, RED, DIM, arrow, stroke_text, rrect, card
    if a <= 0:
        return
    x, y = 140, 560
    card(c, x - 50, y - 70, 900, 360, a, ICE)
    stroke_text(c, "俯视 · 后脚蹬地的方向", x - 14, y - 16, 28, ICE, a, align="l", stroke=0)
    # 板（横着，板头在右）
    cx, cy = x + 420, y + 140
    c.set_source_rgba(0.22, 0.62, 0.95, a); rrect(c, cx - 300, cy - 40, 600, 80, 40); c.fill()
    stroke_text(c, "板头 →", cx + 300, cy - 56, 24, DIM, a, bold=False, align="r", stroke=0)
    # 0°：贴着板、顺着板往后蹬 → 板往前
    k1 = K.ease((t - SEC["why"][2][1][1]) / 0.6)
    if k1 > 0:
        arrow(c, cx - 140, cy + 80, cx - 140 + 260 * k1, cy + 80, GREEN, a, 9)
        stroke_text(c, "顺着板：全往前", cx - 20, cy + 135, 28, GREEN, a * k1)
    k2 = K.ease((t - SEC["why"][2][2][1]) / 0.6)
    if k2 > 0:
        L = 260 * k2
        arrow(c, cx - 300, cy - 110, cx - 300 + L * 0.71, cy - 110 + L * 0.71, RED, a, 9)
        stroke_text(c, "斜45°：一部分在推板转", x + 830, y - 16, 28, RED, a * k2, align="r")


if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), {k: (round(v[0], 1), round(v[1], 1)) for k, v in SEC.items()})
    print("FWD", FWD, "SIDE", SIDE, "Y_END", Y_END)

COVER = dict(title=NAME, sub="没有雪杖，平地也能走", items=["解后脚", "看板头", "小步蹬", "踩垫子"],
             perf="Y", p=3.0, cam=((1.6, 3.0, 1.05), (0.0, 0.0, 0.55), 40), bg=("4016", 3.0))
