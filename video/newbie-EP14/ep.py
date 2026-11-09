"""《单板新手课》第14课：反脚滑行（switch）。原来的后脚变前脚、板尾在前；固定器角度对正反脚的影响。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "newbie-lib"))
from epbase import plain, timeline, pw, key, ease
import epkit, turns

FPS = 30
LESSON = 14
SERIES = "单板新手课"
NAME = "反脚滑行"
TITLE = f"第{LESSON}课 · {NAME}"
STYLE = "day"
MUSIC = "pop"
TRACK = (988, 0.0)             # Mixkit 免费音乐 #988 Day Dreamin' with U
MARKS = True

SLOPE = 12.0
SETUPS = [("常见入门设置", 15, 0), ("鸭步（正反一样）", 15, -15)]     # (名字, 前脚角度, 后脚角度)

BASE = dict(slope=SLOPE, arm=25, ab=38, elb=25, knee=(0.0, 1.0, 0.25), trail=1, pz=0.80)


def perf(segs, v=2.0, extra0=None, **kw):
    keys, wp, tws, t_end, marks = turns.path(segs, v=v, base=BASE, **kw)
    d0 = keys[0][1]
    k0 = dict(BASE, gx=0.0, gy=0.0, yaw=d0["yaw"], broll=d0["broll"], tilt=d0["tilt"], face=d0["face"], twist=d0["twist"], tw=wp, tws=tws, tn=0)
    k0.update(extra0 or {})
    return [(0.0, k0)] + keys + [(t_end + 0.5, dict())], t_end + 0.5, marks


# W：反脚的 S 弯（板尾在前，看向板尾方向）
SW, SW_END, SW_M = perf([("line", 1.4), ("arc", 180, 2.6), ("line", 1.2), ("arc", -180, 2.6), ("line", 1.0)], switch=True, emax=16)
# 错误1：身体还朝着正脚方向（扭着、看板头）
X, X_END, _ = perf([("line", 1.4), ("arc", 100, 2.6)], switch=True, emax=14)
X = [(t, dict(d, face=50, twist=30) if "gx" in d else d) for t, d in X]
# 错误2：重心留在原来的前脚（现在的后脚）：后坐
_b, _bt, _ = perf([("line", 1.4), ("arc", 90, 2.6)], switch=True, emax=14)
B = [(t, dict(d, px=0.14, tilt=d.get("tilt", 0) + 10) if "gx" in d else d) for t, d in _b[:-1]] + turns.fall(_bt, "back", tilt=30)
# 错误3：反脚直接上陡坡：越滑越快、不敢转
Z, Z_END, _ = perf([("arc", 30, 2.6), ("arc", -50, 2.6), ("arc", 40, 2.6)], v=3.4, yaw0=78, switch=True)
Z = Z[:-1] + [(Z_END - 0.2, dict(arm=65, ab=50, tilt=-10))]

PERF = dict(SW=SW, X=X, B=B, Z=Z)
SHOT_PERF = dict(SW="SW", T="SW", X="X", B="B", Z="Z")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    cx = 0.8 * gx + 0.2 * 1.5
    pos, tgt = (cx + 1.4, gy + 4.8, 2.6), (cx, gy - 0.4, 0.45)
    return _slope(pos, s), _slope(tgt, s), 30


def extra_points(P, J):
    from mathutils import Vector
    m = J["board_m"]
    return {"board": m @ Vector((0, 0, 0.02)), "nose": m @ Vector((0.78, 0, 0.05)), "tail": m @ Vector((-0.78, 0, 0.05)),
            "footR": m @ Vector((0.26, 0, 0.03)), "footL": m @ Vector((-0.26, 0, 0.03))}


import epbase
epbase.CPS = 5.2
SECTIONS = [
    ("hook", 0.2, ["正脚滑得挺顺，{w|换个方向}呢？",
                   "反脚滑行：让你两边都{w|一样稳}。"], 0.1),
    ("keys", 0.3, ["①原来的后脚变{w|前脚}，眼睛看{w|板尾}方向。",
                   "②先在缓坡{w|推坡、落叶飘}，找回感觉。",
                   "③再练{w|换刃}，一个弯一个弯来。",
                   "④最后{w|连弯}，左右两边练一样多。"], 0.5),
    ("why", 0.2, ["固定器角度会影响反脚。",
                  "前+15°、后0°：一换方向，变成前0°、后−15°，{r|很别扭}；",
                  "鸭步前+15°、后−15°：正反{g|一模一样}。想练反脚可以这样调。"], 0.5),
    ("mistakes", 0.2, ["{r|身体还朝着原来的方向}：扭着滑。",
                       "{r|重心留在原来的前脚}：一转就后坐。",
                       "{r|反脚直接上陡坡}：越滑越快，不敢转。"], 0.3),
    ("drill", 0.2, ["练习：每坐一趟缆车，下一趟用{w|反脚}滑。",
                    "过关：反脚能{w|连续S弯}，不卡刃。"], 0.3),
    ("end", 0.2, [("下一课：{w|入门刻滑}。", 2.6)], 0.3),
]
SUBS, SEC, DUR = timeline(SECTIONS)

FOOT = {
    "hook0": ("3373", 5.0, 0.50, 0.65),
    "hook1": ("4018", 0.2, 0.62, 0.72),
    "pass": ("3344", 2.0, 0.30, 0.45),
    "end": ("3378", 4.0, 0.40, 0.55),
}

KEYS = ("SW", [0.0, 0.8, SW_M[1][0], SW_M[1][0] + 1.6, SW_END])
WHY = [("T", 0.0, SW_END)]
MIST = [("X", 0.0, X_END), ("B", 0.0, B[-1][0]), ("Z", 0.0, Z[-1][0])]
DRILL = ("SW", 0.0, SW_END)
plan = epkit.std_plan(globals())
music_hits = epkit.std_hits(globals())

STAMP = "两边一样稳"
CHIPS = ["后脚变前脚", "先推坡飘", "再练换刃", "最后连弯"]
KEY_TAGS = [("板尾在前 · 看板尾方向", "ICE", None, ["head", "tail"]),
            ("缓坡 · 推坡、落叶飘", "GOLD", None, ["board"]),
            ("一个弯一个弯来", "GOLD", None, ["board"]),
            ("左右练一样多", "GREEN", "v", ["board"])]
MIST_LABS = ["身体还朝原方向", "重心在原来的前脚", "反脚上陡坡"]
MIST_RINGS = ["chest", "footR", "board"]
DRILL_TAGS = ("一趟正脚", "一趟反脚")
PASS_TAGS = ("反脚连续 S 弯", "不卡刃")
NEXT = "入门刻滑"


def WHY_DRAW(c, t, K, pts):
    from vert import window, ramp, stroke_text, card, rrect, INK, DIM
    w0, w1, ws = SEC["why"]
    a = window(t, w0 + 0.2, w1, 0.3)
    K.dim(c, a * 0.75)
    if a <= 0:
        return
    x, y, w, h = 90, 860, 900, 600
    card(c, x, y, w, h, a, K.ICE)
    stroke_text(c, "俯视 · 固定器角度（板头在右）", x + 36, y + 56, 30, K.ICE, a, align="l", stroke=0)
    rows = [(SETUPS[0], ws[1][1]), (SETUPS[1], ws[2][1])]
    for r, ((name, fa, ba), t0) in enumerate(rows):
        ar = a * ramp(t, t0 - 0.2, t0 + 0.3)
        if ar <= 0:
            continue
        sw = ramp(t, t0 + 1.4, t0 + 2.4)                  # 0 = 正脚，1 = 反脚（板头板尾对调）
        cy = y + 190 + r * 250
        stroke_text(c, name, x + 40, cy - 70, 28, INK, ar, align="l", stroke=0)
        cx = x + w / 2
        c.set_source_rgba(0.22, 0.62, 0.95, ar); rrect(c, cx - 300, cy - 34, 600, 68, 34); c.fill()
        front = (cx + 150, fa) if sw < 0.5 else (cx - 150, -ba)
        back = (cx - 150, ba) if sw < 0.5 else (cx + 150, -fa)
        for (fx, ang), lab in ((front, "前"), (back, "后")):
            c.save(); c.translate(fx, cy); c.rotate(math.radians(-ang))
            c.set_source_rgba(0.1, 0.1, 0.14, ar); rrect(c, -14, -44, 28, 88, 10); c.fill()
            c.set_source_rgba(*K.GOLD, ar); c.set_line_width(5); c.move_to(0, -56); c.line_to(0, 56); c.stroke()
            c.restore()
        fs = f"前 {front[1]:+.0f}° · 后 {back[1]:+.0f}°".replace("+0°", "0°").replace("-0°", "0°")
        col = K.GREEN if (r == 1 or sw < 0.5) else K.RED
        stroke_text(c, ("反脚时：" if sw >= 0.5 else "正脚：") + fs, cx, cy + 100, 30, col, ar, stroke=0)
    stroke_text(c, "固定器常见调法，因人而异；板头方向 = 当时的前脚", x + 36, y + h - 24, 22, DIM, a, bold=False, align="l", stroke=0)


overlay = epkit.std_overlay(globals())

COVER = dict(title=NAME, sub="换个方向，两边一样稳", items=["后脚变前脚", "先推坡飘", "再练换刃", "最后连弯"],
             perf="SW", p=1.0, cam=((1.5, 3.0, 1.05), (0.0, 0.0, 0.55), 40), bg=("3373", 6.0), set=dict(broll=0, yaw=0, tilt=0))

if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), "SW_END", round(SW_END, 2))
