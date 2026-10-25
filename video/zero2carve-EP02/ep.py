"""《单板从0到刻滑》第2课：摔倒了怎么站起来。
动作关键帧、镜头、字幕时间都在这里；../zero2carve-lib/render.py 渲 3D，composite.py 叠字幕出片。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "zero2carve-lib"))
from epbase import plain, timeline, pw, key, ease

FPS = 30
TITLE = "第2课 · 摔倒了怎么站起来"
LEVEL = "L0 上雪前"
LESSON = 2
SLOPE = 12.0

# ------------------------------------------------------------------ 动作（表演时间，秒）
SIT = dict(pz=0.15, py=-0.45, tilt=30, by=0.25, knee=(0.0, 0.3, 1.0), slope=SLOPE)
# W：错误示范——腿伸着、板离屁股远，手往后撑硬起，板往下坡溜，又坐回去
W = [
    (0.0, dict(SIT, arm=-35, ab=20, elb=10)),
    (0.7, dict(pz=0.36, py=-0.34, tilt=16, arm=-40, by=0.30)),
    (1.2, dict(pz=0.44, py=-0.27, tilt=10, arm=45, ab=30, elb=20, by=0.42, broll=-4)),
    (1.7, dict(pz=0.16, py=-0.40, tilt=48, arm=-25, ab=25, elb=15, by=0.55, broll=0)),
    (2.4, dict(tilt=40)),
]
W_FAIL = 1.2

# G：坐着起（后刃）——板横过来 → 收脚 → 抓前刃把重心推到板上
G = [
    (0.0, dict(SIT, arm=30, ab=25, elb=40, yaw=50, yy=-0.45)),
    (1.2, dict(yaw=0)),
    (2.0, dict(by=-0.12, curl=25, tilt=15, arm=50, elb=30, knee=(0.0, 0.4, 1.0))),
    (2.8, dict(py=-0.26, pz=0.22, tilt=-5, curl=22, neck=-10, arm=70, ab=14, elb=8)),
    (3.6, dict(pz=0.55, py=-0.18, tilt=5, curl=25, neck=0, arm=60, elb=15)),
    (4.2, dict(pz=0.80, py=-0.06, tilt=10, curl=0, arm=20, ab=30, elb=25, broll=8, knee=(0.0, 1.0, 0.25))),
    (4.8, dict()),
]
G_STEPS = [1.2, 2.0, 4.2]

# K：跪着起（前刃）——双手撑雪 → 推起、板放平 → 站起来，膝盖顶向山坡
KNEEL = dict(pz=0.46, py=0.55, tilt=-15, broll=-80, bz=0.13, arm=30, ab=15, elb=40, knee=(0.0, 1.0, -0.6), slope=-SLOPE)
K = [
    (0.0, dict(KNEEL)),
    (1.2, dict(tilt=-55, pz=0.42, py=0.62, arm=70, ab=12, elb=5)),
    (2.2, dict(pz=0.62, py=0.25, tilt=-30, broll=-30, bz=0.05, arm=55, elb=20, knee=(0.0, 1.0, 0.0))),
    (3.0, dict(pz=0.82, py=0.05, tilt=-10, broll=-12, bz=0.0, arm=25, ab=30, elb=25, knee=(0.0, 1.0, 0.25))),
    (3.6, dict()),
]
K_STEPS = [1.2, 2.2, 3.0]

PERF = dict(W=W, G=G, K=K)
SHOT_PERF = dict(W1="W", W2="W", G="G", K="K", G2="G")


# ------------------------------------------------------------------ 镜头（坐标写在坡面坐标系里，再随坡转到世界）
def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))

COVER3D = dict(perf="G", p=3.3, cam=((2.2, 1.9, 0.9), (0, -0.2, 0.42), 34), ring=None)


def orbit(cx, cy, r, deg, z):
    a = math.radians(deg); return (cx + r * math.cos(a), cy + r * math.sin(a), z)


def cam(shot, p, P):
    gx, s = P["gx"], P["slope"]
    if shot == "W1":     # 开场：正前方偏侧，看他往后撑、板往下溜
        pos, tgt = orbit(gx, -0.2, 3.0, 62, 1.25), (gx, -0.1, 0.55)
    elif shot == "W2":   # 侧面：看清板离屁股多远
        pos, tgt = orbit(gx, -0.1, 3.0, 12, 0.9), (gx, -0.05, 0.45)
    elif shot in ("G", "G2"):
        k = ease((p - 2.4) / 1.8)
        pos, tgt = orbit(gx, -0.25, 3.1, 55 - 20 * k, 1.5), (gx, -0.25 + 0.15 * k, 0.40 + 0.40 * k)
    elif shot == "K":
        k = ease((p - 1.6) / 1.4)
        pos, tgt = orbit(gx, 0.3, 3.1, 45 - 10 * k, 1.4), (gx, 0.30 - 0.2 * k, 0.40 + 0.40 * k)
    else:
        raise KeyError(shot)
    return _slope(pos, s), _slope(tgt, s), 30


def extra_points(P, J):
    """2D 标注要用的额外点：板中心、板头。"""
    from mathutils import Vector, Matrix
    m = J["board_m"]
    b = m @ Vector((0, 0, 0.02))
    sg = 1 if P["slope"] >= 0 else -1
    dn = Matrix.Rotation(math.radians(-P["slope"]), 3, "X") @ Vector((0, sg, 0))
    return {"board": b, "nose": m @ Vector((0.72, 0, 0.05)), "tail": m @ Vector((-0.72, 0, 0.05)),
            "dn": b + dn * 0.8, "up": b - dn * 0.8}


# ------------------------------------------------------------------ 字幕（不配音：按阅读速度排时间）
SECTIONS = [   # (名字, 开头留白, 字幕, 结尾留白)
    ("hook", 0.3, ["穿着板坐在雪里，{r|站不起来}？"], 0.4),
    ("why", 0.3, ["越用力往后撑，板越往{r|下坡溜}。",
                  "问题不在力气，在{w|板的方向}和{w|脚的位置}。"], 0.4),
    ("back", 1.2, ["①先把板{w|横在坡上}，跟下坡方向垂直。",
                   "②脚跟往回收，板{w|贴近屁股}。",
                   "③抓住前刃，{w|把重心推到板上}，站起来。"], 0.6),
    ("front", 1.2, ["①跪着面朝山上，{w|双手撑雪}。",
                    "②手往回推，把{w|板放平}。",
                    "③站起来，{w|膝盖顶向山坡}，前刃立住。"], 0.6),
    ("drill", 0.3, ["坐着起不来？{w|翻个身}改成跪着，前刃起更省力。",
                    "缓坡上，坐着起三次、跪着起三次。",
                    "过关标准：站起来，{w|板不溜走}。"], 0.4),
    ("end", 0.3, [("下一课：{w|单脚蹬行}，自己滑到魔毯。", 3.2)], 0.4),
]
VO_EXTRA = dict(back="坐着起，记住三步。", front="跪着起，也是三步。")
SUBS, SEC, DUR = timeline(SECTIONS)


def plan():
    """每个输出帧 -> (shot, perf, p)。镜头随表演时间走，停帧时不用重渲。"""
    out = []
    h0, h1, _ = SEC["hook"]; w0, w1, ws = SEC["why"]; b0, b1, bs = SEC["back"]
    f0, f1, fs = SEC["front"]; d0, d1, ds = SEC["drill"]
    for i in range(int(DUR * FPS)):
        t = i / FPS
        if t < h1:
            out.append(("W1", "W", pw([(0, 0.0), (h1 - 0.6, 2.0), (h1, 2.4)], t - h0)))
        elif t < w1:
            out.append(("W2", "W", pw([(0, 0.3), (ws[0][2] - w0, 1.9), (ws[1][1] - w0 + 1.0, 2.4)], t - w0)))
        elif t < b1:
            sb = [x[1] - b0 for x in bs]
            out.append(("G", "G", pw([(sb[0] - 0.2, 0.0), (sb[0] + 1.6, G_STEPS[0]), (sb[1], G_STEPS[0]),
                                      (sb[1] + 1.2, G_STEPS[1]), (sb[2], G_STEPS[1]), (sb[2] + 3.0, G_STEPS[2]),
                                      (sb[2] + 3.6, 4.8)], t - b0)))
        elif t < f1:
            sf = [x[1] - f0 for x in fs]
            out.append(("K", "K", pw([(sf[0] - 0.2, 0.0), (sf[0] + 1.6, K_STEPS[0]), (sf[1], K_STEPS[0]),
                                      (sf[1] + 1.6, K_STEPS[1]), (sf[2], K_STEPS[1]), (sf[2] + 1.4, K_STEPS[2]),
                                      (sf[2] + 2.0, 3.6)], t - f0)))
        else:            # 练习 + 结尾：坐着起原速重放（复用 G 的帧）
            out.append(("G", "G", pw([(0.4, 0.0), (5.2, 4.8)], t - d0)))
    return out


if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), {k: (round(v[0], 1), round(v[1], 1)) for k, v in SEC.items()})
    P = plan()
    print("frames", len(P), "unique", len({key(s, p) for s, _, p in P}))
