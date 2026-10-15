"""单板 EP.10《转 2340°，要转多快？》 (no voice-over)"""
import math
import numpy as np
from common import *
from art import *
from board import *

SERIES = SERIES_B
TITLE = "转 2340°，要转多快？"
REV = 2340 / 360          # 6.5
T_SPIN = 2.5              # assumed spin time (s), 示意
RATE = REV / T_SPIN       # rev/s


def spinner(c, cx, cy, r, turns, alpha, col=GOLD, label=True):
    """a dial that winds `turns` revolutions: completed laps as rings, current lap as an arc."""
    if alpha <= 0:
        return
    full = int(turns)
    for i in range(full):
        c.new_path(); c.arc(cx, cy, r - i * 14, 0, 2 * math.pi); c.set_source_rgba(*col, 0.35 * alpha); c.set_line_width(8); c.stroke()
    frac = turns - full
    if frac > 0:
        c.new_path(); c.arc(cx, cy, r - full * 14, -math.pi / 2, -math.pi / 2 + 2 * math.pi * frac)
        c.set_source_rgba(*col, alpha); c.set_line_width(10); c.stroke()
    ang = -math.pi / 2 + 2 * math.pi * turns
    c.save(); c.translate(cx, cy); c.rotate(ang + math.pi / 2)
    board_top(c, 0, 0, r * 1.25, alpha)
    c.restore()
    if label:
        text(c, f"{turns * 360:.0f}°", cx, cy + r + 80, 64, col, alpha, align="c", bold=True)


# ================================================================== S1 hook
S1_SUBS = seq(["大跳台上，单板选手的转体度数一路往上涨：1440、1800、2160……",
               "到了2025年，2340度。",
               "2340度是几圈？要转多快？和花样滑冰比，谁更快？"], t0=0.8)
S1_DUR = end_of(S1_SUBS) + 4.6


def s1(c, t, fi):
    paint_bg(c)
    a = ramp(t, 0, 0.8)
    T = [x for _, x, _ in S1_SUBS]
    seq_deg = [1440, 1800, 2160, 2340]
    idx = min(3, int(max(0, t - T[0] - 0.6) / 1.2))
    if t > T[1]:
        idx = 3
    for i, d in enumerate(seq_deg):
        k = ramp(t, T[0] + 0.6 + i * 1.2, T[0] + 1.0 + i * 1.2) if i < 3 else ramp(t, T[1], T[1] + 0.6)
        col = RED if i == 3 else (INK if i == idx else DIM)
        text(c, f"{d}°", 360 + i * 400, 520, 90 if i == 3 else 70, col, a * k, align="c", bold=True)
    title_card(c, t, end_of(S1_SUBS) + 0.2, S1_DUR, TITLE, "圈数 · 转速 · 角动量")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2 how many turns
S2_SUBS = seq(["2340除以360，等于{r|6.5}——六圈半。",
               "2025年1月，X Games阿斯彭站，日本选手{w|荻原大翔}在大跳台完成了它，并拿下金牌。",
               "这个“世界第一”，多数报道都记在他名下。"])
S2_DUR = end_of(S2_SUBS) + 0.8


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S2_DUR - 0.6, S2_DUR))
    T = [x for _, x, _ in S2_SUBS]
    turns = REV * ease_io((t - T[0] - 0.3) / 3.0)
    spinner(c, W / 2, 480, 220, turns, a_in)
    text(c, f"{turns:.1f} 圈", W / 2, 490, 56, INK, a_in, align="c", bold=True)
    chapter_tag(c, "六圈半", "2340 ÷ 360 = 6.5", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "X Games Aspen · 2025-01", "大跳台首个 2340，夺得金牌", "荻原大翔（多数报道）", ramp(t, T[1], T[1] + 0.8) * a_in)
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3 rotation rate
S3_SUBS = seq(["空中只有几秒。假设真正用来转体的时间，是{w|2.5秒}：",
               "6.5圈 ÷ 2.5秒 ≈ 每秒{r|2.6圈}；换成角度，每秒转{r|936度}。",
               "2.5秒是示意的假设——空中时间越短，要转得越快。"])
S3_DUR = end_of(S3_SUBS) + 0.8


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S3_DUR - 0.6, S3_DUR))
    T = [x for _, x, _ in S3_SUBS]
    # timeline 0..2.5 s with rotation ticks
    x0, x1, y = 260, 1660, 640
    ta = a_in * ramp(t, T[0] + 0.3, T[0] + 1.0)
    c.set_source_rgba(*FAINT, ta); c.rectangle(x0, y - 2, x1 - x0, 4); c.fill()
    for s in (0, 0.5, 1.0, 1.5, 2.0, 2.5):
        text(c, f"{s:.1f} s", x0 + (x1 - x0) * s / 2.5, y + 50, 24, DIM, ta, align="c")
    k = ramp(t, T[0] + 1.0, T[0] + 1.0 + T_SPIN * 1.6)
    for i in range(14):
        tt = i * 0.5 / RATE
        if tt / 2.5 > k:
            break
        xx = x0 + (x1 - x0) * tt / 2.5
        c.new_path(); c.arc(xx, y - 80, 16 if i % 2 == 0 else 8, 0, 2 * math.pi); c.set_source_rgba(*GOLD, ta); c.fill()
    text(c, "每个大点 = 1 圈", x1, y - 150, 24, DIM, ta, align="r")
    fa = a_in * ramp(t, T[1] - 0.1, T[1] + 0.5)
    text(c, f"6.5 圈 ÷ {T_SPIN} s ≈ {RATE:.1f} 圈/秒", W / 2, 340, 60, GOLD, fa, align="c", bold=True)
    text(c, f"≈ {RATE * 360:.0f}° / 秒", W / 2, 430, 60, RED, fa * ramp(t, T[1] + 1.6, T[1] + 2.2), align="c", bold=True)
    chapter_tag(c, "转速", "圈数 ÷ 时间", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "示意计算 · 转体时间 2.5 s 为假设值")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4 vs figure skating
S4_SUBS = seq(["和花样滑冰比一比：花滑的四周跳，空中只有大约{w|0.65到0.75秒}，",
               "转速约每秒{r|4.5到6圈}——比单板大跳台快将近一倍。",
               "可单板选手脚上绑着一块一米五长的板，转起来像抡着一根棍子；",
               "而且他们常常是斜着轴转、又翻又转——难度在另一个维度上。"])
S4_DUR = end_of(S4_SUBS) + 0.8


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S4_DUR - 0.6, S4_DUR))
    T = [x for _, x, _ in S4_SUBS]
    x0, w = 560, 1000
    rows = [("单板 2340", RATE, RATE, GOLD, T[0] - 0.2), ("花滑四周跳", 4.5, 6.0, ICE, T[1])]
    ba = a_in * ramp(t, T[0] - 0.4, T[0] + 0.3)
    for i, (lab, lo, hi, col, ts) in enumerate(rows):
        k = ease_io((t - ts) / 0.9)
        if k <= 0:
            continue
        y = 360 + i * 160
        text(c, lab, x0 - 30, y + 56, 42, INK, ba, align="r", bold=True)
        c.rectangle(x0, y, w * lo / 7 * k, 84); c.set_source_rgba(*col, 0.88 * ba); c.fill()
        if hi > lo:
            c.rectangle(x0 + w * lo / 7 * k, y, w * (hi - lo) / 7 * k, 84); c.set_source_rgba(*col, 0.4 * ba); c.fill()
        lab2 = f"{lo:.1f} 圈/秒" if hi == lo else f"{lo}–{hi} 圈/秒"
        text(c, lab2, x0 + w * hi / 7 * k + 20, y + 58, 40, col, ba * k, bold=True)
    for v in range(0, 8):
        text(c, f"{v}", x0 + w * v / 7, 720, 24, DIM, ba, align="c")
    ra = a_in * ramp(t, T[2], T[2] + 0.6)
    if ra > 0:
        c.save(); c.translate(W / 2, 790); c.rotate(t * 2.6 * 2 * math.pi * 0.25)
        board_top(c, 0, 0, 170, ra)
        c.restore()
        text(c, "1.5 m 长的板一起转", W / 2 + 180, 800, 30, GOLD, ra, bold=True)
    ca = a_in * ramp(t, T[3], T[3] + 0.6)
    pill_label(c, "斜轴转体（cork）：又翻又转", W / 2, 300, 30, ICE, ca)
    chapter_tag(c, "对比", "花样滑冰四周跳", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "运动生物力学报道 · 汇总", "四周跳腾空约 0.65–0.75 s，转速约 4.5–6 圈/秒", "多篇科普与访谈资料", ramp(t, T[0] + 0.3, T[0] + 1.1) * a_in)
    model_note(c, a_in, "单板转速为示意计算；花滑数据为近似值")
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5 angular momentum
S5_SUBS = seq(["转速从哪来？起跳那一刻就基本定了：空中没有东西可以推，{w|角动量守恒}。",
               "把身体收紧、抱住板，转动惯量变小，就转得更快；",
               "快落地时打开身体，转速慢下来，才能看准、站稳——和花滑收臂、展臂，是同一个道理。"])
S5_DUR = end_of(S5_SUBS) + 0.8


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S5_DUR - 0.6, S5_DUR))
    T = [x for _, x, _ in S5_SUBS]
    fa = a_in * ramp(t, T[0] + 0.6, T[0] + 1.2)
    text(c, "L = I · ω = 常数", W / 2, 300, 64, GOLD, fa, align="c", bold=True)
    # two figures: open (big I, slow) vs tucked (small I, fast)
    tuck = ramp(t, T[1], T[1] + 0.8) * (1 - ramp(t, T[2], T[2] + 0.8))
    I = 1.0 - 0.5 * tuck
    om = 1.0 / I
    ang = t * om * 2.2
    cx, cy = W / 2, 600
    reach = 220 * (1 - 0.55 * tuck)
    c.save(); c.translate(cx, cy); c.rotate(ang)
    _ = None
    for sgn in (-1, 1):
        c.set_source_rgba(*BODY, a_in); c.set_line_width(26); c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(0, 0); c.line_to(sgn * reach, 0); c.stroke()
        c.arc(sgn * reach, 0, 22, 0, 2 * math.pi); c.set_source_rgba(*GOLD, a_in); c.fill()
    c.arc(0, 0, 48, 0, 2 * math.pi); c.set_source_rgba(*BODY, a_in); c.fill()
    c.restore()
    text(c, f"转动惯量 I：{'小' if tuck > 0.5 else '大'}", 400, 560, 40, ICE, a_in * ramp(t, T[1] - 0.4, T[1]), align="c", bold=True)
    text(c, f"转速 ω：{'快' if tuck > 0.5 else '慢'}", 1520, 560, 40, RED if tuck > 0.5 else ICE, a_in * ramp(t, T[1] - 0.4, T[1]), align="c", bold=True)
    text(c, "收紧" if tuck > 0.5 else "打开", W / 2 + 330, 680, 36, INK, a_in * ramp(t, T[1] - 0.4, T[1]), align="c")
    chapter_tag(c, "角动量", "收紧转快 · 打开转慢", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "示意 · 俯视简化模型")
    subs(c, t, S5_SUBS)
    overlays(c, fi)


# ================================================================== S6 end
S6_SUBS = seq(["六圈半、每秒两圈半以上；还要抱着一块板、斜着轴转，最后稳稳落在坡上。",
               "这些动作是在什么样的台子上完成的？",
               "大跳台：从起跳到落地，发生了什么？下一集，用数据说话。"])
S6_DUR = end_of(S6_SUBS) + 4.0


def s6(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S6_DUR - 1.4, S6_DUR - 0.4))
    T = [x for _, x, _ in S6_SUBS]
    la = a_in * (1 - ramp(t, T[2] - 0.2, T[2] + 0.4))
    spinner(c, W / 2, 470, 200, REV * ramp(t, T[0], T[0] + 4.0), la)
    end_card(c, a_in * ramp(t, T[2], T[2] + 0.8), "大跳台：从起跳到落地")
    subs(c, t, S6_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, S6_DUR - 1.0, S6_DUR))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR), ("s6", s6, S6_DUR)]


def _cover_fig(c):
    spinner(c, 500, 380, 300, REV, 1.0, label=False)
    text(c, "6.5 圈", 500, 400, 90, INK, align="c", bold=True)


COVER = dict(lines=["转 2340°", "要转多快？"], stat="936°/s", caption="假设 2.5 秒转完六圈半的平均转速（示意计算）", color=RED, figure=_cover_fig)
