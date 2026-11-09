"""《单板新手课》第10课：搓雪和刻滑的区别。同一条 S 弯做两遍：搓雪（板尾外甩、雪痕一大片）和刻滑（板顺着弧线走、雪痕一条线）。
参考《单板从0到刻滑》第10课。"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "newbie-lib"))
from epbase import plain, timeline, pw, key, ease
import epkit, turns

FPS = 30
LESSON = 10
SERIES = "单板新手课"
NAME = "搓雪和刻滑"
TITLE = f"第{LESSON}课 · {NAME}"
STYLE = "day"
MUSIC = "drive"
TRACK = (51, 0.0)              # Mixkit 免费音乐 #51 Sports Highlights
MARKS = True

SLOPE = 12.0
W_SKID, W_CARVE = 110, 15      # 雪痕宽度（厘米，示意）：搓雪时板尾外甩约 30°，刻滑时只留板刃切出的一道

BASE = dict(slope=SLOPE, arm=25, ab=38, elb=25, knee=(0.0, 1.0, 0.25), trail=1, pz=0.80)


def perf(segs, v=2.4, extra0=None, **kw):
    keys, wp, tws, t_end, marks = turns.path(segs, v=v, base=BASE, **kw)
    k0 = dict(BASE, gx=0.0, gy=0.0, yaw=0.0, broll=14, tilt=10, tw=wp, tws=tws, tn=0)
    k0.update(extra0 or {})
    return [(0.0, k0)] + keys + [(t_end + 0.5, dict())], t_end + 0.5, marks


def segs(w_arc, w_line):
    return [("line", 1.0, w_line), ("arc", 180, 3.0, w_arc), ("line", 0.8, w_line), ("arc", -180, 3.0, w_arc), ("line", 0.8, w_line)]


SK, SK_END, SK_M = perf(segs(W_SKID / 100, 0.5), skid=30, emax=14)
CV, CV_END, CV_M = perf(segs(0.04, 0.04), v=3.2, emax=40, lean=25)

# 错误1：以为蹲得低就是刻滑——蹲很低，还是在甩板尾
LO, LO_END, _ = perf([("line", 0.8), ("arc", 180, 3.0, 1.1)], skid=35, emax=12)
LO = [(t, dict(d, pz=d.get("pz", 0.8) - 0.14) if "gx" in d else d) for t, d in LO]
# 错误2：速度不够就立高刃——板“卡”住，人倒向弯里
SL, SL_END, _ = perf([("line", 0.8, 0.04), ("arc", 70, 2.4, 0.04)], v=1.4, emax=40, lean=28)
SL = SL[:-1] + turns.fall(SL_END - 0.5, "back", tilt=30)
# 错误3：后脚甩板尾——板头不动、板尾横扫
SW, SW_END, _ = perf([("line", 0.8), ("arc", 120, 2.6, 1.3)], skid=55, emax=12, extra0=dict())

PERF = dict(SK=SK, CV=CV, LO=LO, SL=SL, SW=SW)
SHOT_PERF = dict(SK="SK", CV="CV", TK="SK", TC="CV", LO="LO", SL="SL", SW="SW")


def _slope(v, s):
    a = math.radians(s); x, y, z = v
    return (x, y * math.cos(a) + z * math.sin(a), -y * math.sin(a) + z * math.cos(a))


def cam(shot, p, P):
    gx, gy, s = P["gx"], P["gy"], P["slope"]
    if shot in ("TK", "TC"):          # 高处往下看整条 S 的雪痕
        pos, tgt = (1.6, 9.5, 9.0), (1.6, 3.6, 0.0)
        return _slope(pos, s), _slope(tgt, s), 30
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
    ("hook", 0.2, ["同样是转弯，为什么别人的雪痕{w|一条线}？",
                   "这一课分清：{w|搓雪}和{w|刻滑}。"], 0.1),
    ("keys", 0.3, ["①搓雪：板尾往外甩，雪是{r|刮}下来的。",
                   "②刻滑：板顺着弧线走，雪是{w|切}开的。",
                   "③刻滑靠{w|立刃}转弯，不靠甩板。",
                   "④先把搓雪弯滑稳，再慢慢{w|少甩一点}。"], 0.5),
    ("why", 0.2, ["回头看雪痕，就知道你是哪种。",
                  f"搓雪的雪痕约{{r|{W_SKID}厘米}}宽，",
                  f"刻滑只有约{{g|{W_CARVE}厘米}}：刮掉的雪少，速度也{{w|掉得少}}。"], 0.5),
    ("mistakes", 0.2, ["{r|以为蹲低就是刻滑}：还是在甩板尾。",
                       "{r|速度不够就立高刃}：板卡住，人倒进弯里。",
                       "{r|后脚甩板尾}：板横着扫，雪痕一大片。"], 0.3),
    ("drill", 0.2, ["练习：缓坡上只做{w|后刃横切}，立刃，回头看雪痕。",
                    "过关：雪痕{w|不超过一个板宽}。"], 0.3),
    ("end", 0.2, [("下一课：{w|立刃角}。", 2.6)], 0.3),
]
SUBS, SEC, DUR = timeline(SECTIONS)

FOOT = {
    "hook0": ("3373", 11.0, 0.40, 0.55),
    "hook1": ("3381", 8.0, 0.35, 0.50),
    "pass": ("3344", 7.0, 0.45, 0.60),
    "end": ("3378", 16.0, 0.40, 0.55),
}

KEYS = ("SK", [0.0, 0.0, 0.0, 0.0, 0.0])          # 要领段手动切镜头（见下面的 plan）
WHY = [("TK", 0.0, SK_END), ("TK", SK_END, SK_END), ("TC", 0.0, CV_END)]
MIST = [("LO", 0.0, LO_END), ("SL", 0.0, SL[-1][0]), ("SW", 0.0, SW_END)]
DRILL = ("CV", 0.0, CV_END)
_std = epkit.std_plan(globals())


def plan():
    out = _std()
    k0, k1, ks = SEC["keys"]
    a = [s[1] for s in ks]
    for i in range(len(out)):
        t = i / FPS
        if k0 <= t < k1:
            if t < a[1] - 0.15:
                out[i] = ("R", "SK", round(pw([(k0, 0.0), (a[1] - 0.15, SK_END)], t) * 30) / 30)
            elif t < a[3] - 0.15:
                out[i] = ("R", "CV", round(pw([(a[1] - 0.15, 0.0), (a[3] - 0.15, CV_END)], t) * 30) / 30)
            else:
                out[i] = ("R", "SK", round(pw([(a[3] - 0.15, 0.0), (k1, SK_END)], t) * 30) / 30)
    return out


music_hits = epkit.std_hits(globals())

STAMP = "雪痕会说话"
CHIPS = ["搓雪=刮", "刻滑=切", "靠立刃", "慢慢少甩"]
KEY_TAGS = [("板尾外甩 · 雪痕一大片", "RED", "x", ["tail"]),
            ("板顺着弧线走 · 雪痕一条线", "GREEN", "v", ["board"]),
            ("膝盖、髋往弯里送 · 立刃", "ICE", None, ["kneeL", "kneeR"]),
            ("先滑稳，再少甩", "GOLD", None, ["tail"])]
MIST_LABS = ["蹲低≠刻滑", "速度不够立高刃", "后脚甩板尾"]
MIST_RINGS = ["tail", "pelvis", "tail"]
DRILL_TAGS = ("只做后刃横切", "回头看雪痕")
PASS_TAGS = ("雪痕不超过一个板宽", "板尾不甩")
NEXT = "立刃角"


def WHY_DRAW(c, t, K, pts):
    from vert import window, tag
    w0, w1, ws = SEC["why"]
    a = window(t, ws[1][1] - 0.2, w1, 0.3)
    tag(c, "搓雪的雪痕" if t < ws[2][1] - 0.15 else "刻滑的雪痕", K.RED if t < ws[2][1] - 0.15 else K.GREEN, 60, 330,
        window(t, w0 + 0.2, w1, 0.3), 42)
    items = [("搓雪", W_SKID, K.RED, ws[1][1] + 0.4, None), ("刻滑", W_CARVE, K.GREEN, ws[2][1] + 0.4, None)]
    K.bars(c, t, a, "雪痕有多宽", items, 130, unit=" cm", edge=K.ICE, y=1040, h=380,
           foot="示意 · 板宽约 25 cm；搓雪按板尾外甩约 30° 估算")


overlay = epkit.std_overlay(globals())

COVER = dict(title=NAME, sub="看雪痕就知道你是哪种", items=["搓雪=刮", "刻滑=切", "靠立刃", "少甩"],
             perf="CV", p=2.0, cam=((1.5, 3.0, 1.05), (0.0, 0.0, 0.55), 40), bg=("3373", 12.0), set=dict(broll=0, yaw=0, tilt=0, py=0))

if __name__ == "__main__":
    for s in SUBS:
        print(f"{s[1]:6.2f}-{s[2]:6.2f}  {plain(s[0])}")
    print("dur", round(DUR, 2), "SK_END", round(SK_END, 2), "CV_END", round(CV_END, 2))
