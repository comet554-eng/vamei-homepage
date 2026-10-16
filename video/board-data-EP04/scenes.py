"""单板 EP.04《“单板踝”：被当成崴脚的骨折》 (no voice-over)"""
import math
from common import *
from art import *
from board import *
from art import _seg

SERIES = SERIES_B
TITLE = "“单板踝”：被当成崴脚的骨折"

# ================================================================== S1 hook
S1_SUBS = seq(["单板摔了一跤，脚踝外侧又肿又疼——你以为是崴脚，养两周就好。",
               "可能不是。有一种骨折，几乎是单板的“专利”，偏偏长得像扭伤。",
               "医生给它起了个外号：{r|单板踝}。"], t0=0.8)
S1_DUR = end_of(S1_SUBS) + 4.6


def s1(c, t, fi):
    paint_bg(c)
    a = ramp(t, 0, 0.8)
    T = [x for _, x, _ in S1_SUBS]
    ankle_bones(c, W / 2, 560, 230, a, lp_mark=ramp(t, T[1] + 1.0, T[1] + 2.0), crack=ramp(t, T[2], T[2] + 0.8), label=False)
    q = ramp(t, T[0] + 1.2, T[0] + 2.0) * (1 - ramp(t, T[1], T[1] + 0.6))
    pill_label(c, "扭伤？", W / 2 + 420, 520, 48, ICE, a * q)
    pill_label(c, "骨折！", W / 2 + 420, 620, 48, RED, a * ramp(t, T[2], T[2] + 0.6))
    title_card(c, t, end_of(S1_SUBS) + 0.2, S1_DUR, TITLE, "距骨外侧突骨折 · 发生率 · 漏诊 · 机制")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2 anatomy
S2_SUBS = seq(["先认识一块骨头：{w|距骨}，夹在小腿和脚跟之间，整个脚踝的重量都从它身上过。",
               "它外侧有一个小小的突起，叫{r|距骨外侧突}，就藏在外踝尖的正下方。",
               "单板踝，说的就是这一小块骨头折断了。"])
S2_DUR = end_of(S2_SUBS) + 0.8


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S2_DUR - 0.6, S2_DUR))
    T = [x for _, x, _ in S2_SUBS]
    lp = ramp(t, T[1], T[1] + 0.8)
    tip = ankle_bones(c, 820, 560, 240, a_in, lp_mark=lp, crack=ramp(t, T[2] + 0.4, T[2] + 1.0))
    if lp > 0:
        c.set_source_rgba(*RED, 0.8 * a_in * lp); c.set_line_width(2)
        c.move_to(tip[0] + 10, tip[1]); c.line_to(1250, 640); c.stroke()
        text(c, "距骨外侧突", 1270, 650, 44, RED, a_in * lp, bold=True)
        text(c, "外踝尖正下方", 1270, 700, 28, DIM, a_in * lp)
    chapter_tag(c, "解剖", "距骨 · 外侧突", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "示意图 · 非真实比例")
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3 Kirkpatrick: 3213 injuries
S3_SUBS = seq(["它有多常见？美国科罗拉多一项研究，统计了{w|3213}例单板受伤：",
               "距骨外侧突骨折，占了所有脚踝受伤的{r|15%}；",
               "在脚踝骨折里，它占{r|34%}——三个单板的脚踝骨折，就有一个是它。"])
S3_DUR = end_of(S3_SUBS) + 0.8


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S3_DUR - 0.6, S3_DUR))
    T = [x for _, x, _ in S3_SUBS]
    for i, (lab, frac, ts) in enumerate((("脚踝受伤", 0.15, T[1]), ("脚踝骨折", 0.34, T[2]))):
        cx, cy, r = 640 + i * 640, 520, 200
        k0 = ramp(t, ts - 0.2, ts + 0.4)
        if k0 <= 0:
            continue
        c.new_path(); c.arc(cx, cy, r, 0, 2 * math.pi); c.set_source_rgba(*FAINT, 0.45 * a_in * k0); c.fill()
        k = ease_io((t - ts - 0.4) / 1.0)
        if k > 0:
            c.new_path(); c.move_to(cx, cy); c.arc(cx, cy, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * frac * k); c.close_path()
            c.set_source_rgba(*RED, 0.9 * a_in); c.fill()
        text(c, f"{frac * 100 * max(k, 0):.0f}%", cx, cy + 22, 70, INK, a_in * k0, align="c", bold=True)
        text(c, lab, cx, cy + r + 60, 36, INK, a_in * k0, align="c", bold=True)
    na = a_in * ramp(t, T[0] + 0.4, T[0] + 1.0) * (1 - ramp(t, T[1] - 0.3, T[1] + 0.2))
    text(c, "3213", W / 2, 540, 160, INK, na, align="c", bold=True)
    text(c, "例单板受伤 · 科罗拉多", W / 2, 620, 34, DIM, na, align="c")
    chapter_tag(c, "有多常见", "科罗拉多 · 3213 例", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "Am J Sports Med · 1998", "脚踝受伤 15% · 脚踝骨折 34%", "Kirkpatrick · Hunter · Janes 等",
              ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4 missed diagnosis
S4_SUBS = seq(["麻烦在于：它很容易{r|漏诊}。",
               "1965年的一组早期病例里，13例中有{r|6}例，第一次看X光时被漏掉了——将近一半。",
               "外侧突很小，在普通X光片上和周围的骨头重叠；症状又和扭伤几乎一样。",
               "所以只要怀疑，医生通常会建议加做{w|CT}。"])
S4_DUR = end_of(S4_SUBS) + 0.8


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S4_DUR - 0.6, S4_DUR))
    T = [x for _, x, _ in S4_SUBS]
    da = a_in * ramp(t, T[1] - 0.2, T[1] + 0.4) * (1 - ramp(t, T[2] - 0.3, T[2] + 0.2))
    if da > 0:
        hot = int(round(6 * ramp(t, T[1] + 1.6, T[1] + 3.0)))
        dots(c, W / 2 - 12 * 80 / 2 + 40, 470, 13, 13, 80, 28, hot, da, col=ICE)
        text(c, "13 例中 6 例首诊漏诊", W / 2, 620, 50, RED, da * (hot > 0), align="c", bold=True)
    xa = a_in * ramp(t, T[2] - 0.1, T[2] + 0.5)
    if xa > 0:
        ov = ramp(t, T[2] + 0.8, T[2] + 1.8) * (1 - ramp(t, T[3], T[3] + 0.8))
        ankle_bones(c, 760, 540, 220, xa, lp_mark=ramp(t, T[3] + 0.4, T[3] + 1.2), crack=ramp(t, T[3] + 0.8, T[3] + 1.4), overlap=ov, label=False)
        text(c, "普通 X 光：骨头重叠，看不清", 1320, 420, 34, ICE, xa * ov, align="c", bold=True)
        text(c, "CT：断层成像，裂缝清楚", 1320, 500, 34, GOLD, xa * ramp(t, T[3] + 0.4, T[3] + 1.0), align="c", bold=True)
    chapter_tag(c, "漏诊", "X 光不容易看出来", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "J Bone Joint Surg Am · 1965", "13 例中 6 例初次阅片被漏诊", "Hawkins", ramp(t, T[1], T[1] + 0.8) * a_in * (1 - ramp(t, T[2] - 0.4, T[2])))
    model_note(c, a_in, "X 光 / CT 画面为示意")
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5 mechanism: dorsiflexion + eversion
S5_SUBS = seq(["它是怎么断的？研究者在实验室里，用尸体标本复现了这个伤：",
               "把踝关节往上勾（背屈），再往外翻——",
               "6个标本，{r|全部}在距骨外侧突骨折。",
               "放到雪上：落地时前脚掌被顶起来、脚踝再往外一拧，就是这个姿势。"])
S5_DUR = end_of(S5_SUBS) + 0.8


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S5_DUR - 0.6, S5_DUR))
    T = [x for _, x, _ in S5_SUBS]
    # foot pictogram: shin + foot, rotating
    cx, cy = 760, 560
    dor = ease_io((t - T[1] - 0.2) / 0.9); ev = ease_io((t - T[1] - 1.6) / 0.9)
    c.save(); c.translate(cx, cy)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    _seg(c, [(0, -360), (0, 0)], LIMB, 70, a_in)
    c.save(); c.rotate(-math.radians(25) * dor)
    c.scale(1 - 0.35 * ev, 1)
    rounded_rect(c, -60, -30, 330, 70, 30); c.set_source_rgba(0.30, 0.34, 0.42, a_in); c.fill()
    c.restore()
    c.restore()
    if dor > 0:
        c.new_path(); c.arc(cx, cy, 300, -math.radians(28) * dor, 0); c.set_source_rgba(*GOLD, a_in * dor); c.set_line_width(5); c.stroke()
        text(c, "背屈（往上勾）", cx + 330, cy - 120, 36, GOLD, a_in * dor, bold=True)
    if ev > 0:
        text(c, "外翻（往外翻）", cx + 330, cy - 60, 36, GOLD, a_in * ev, bold=True)
    res = a_in * ramp(t, T[2], T[2] + 0.6)
    if res > 0:
        for i in range(6):
            x = 1200 + i * 100
            c.arc(x, 760, 30, 0, 2 * math.pi); c.set_source_rgba(*RED, res); c.fill()
        text(c, "6 / 6 外侧突骨折", 1450, 700, 40, RED, res, align="c", bold=True)
    chapter_tag(c, "机制", "背屈 + 外翻", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "Am J Sports Med · 2003 · 尸体实验", "背屈 + 外翻：6 个标本全部外侧突骨折", "Funk · Srinivasan · Crandall 等",
              ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    model_note(c, a_in, "示意 · 动作幅度非真实角度")
    subs(c, t, S5_SUBS)
    overlays(c, fi)


# ================================================================== S6 what to do + end
S6_SUBS = seq(["为什么不能当崴脚养？骨块没固定好，可能长不上，日后变成距下关节的关节炎。",
               "所以记住一个信号：单板摔后，{r|外踝尖正下方}按着特别疼、肿得厉害——",
               "别硬撑，去拍片；X光看着正常也别大意，必要时做CT。",
               "跳台，为什么是单板重伤的头号来源？下一集，用数据说话。"])
S6_DUR = end_of(S6_SUBS) + 4.0


def s6(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S6_DUR - 1.4, S6_DUR - 0.4))
    T = [x for _, x, _ in S6_SUBS]
    la = a_in * (1 - ramp(t, T[3] - 0.2, T[3] + 0.4))
    numbered(c, [("!", "外踝尖下方压痛", "肿得厉害、不能负重", T[1]), ("→", "拍片", "X 光正常也别大意", T[2]), ("→", "必要时 CT", "别当崴脚硬养", T[2] + 1.6)], t, la)
    end_card(c, a_in * ramp(t, T[3], T[3] + 0.8), "跳台，为什么是重伤头号来源？")
    subs(c, t, S6_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, S6_DUR - 1.0, S6_DUR))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR), ("s6", s6, S6_DUR)]


def _cover_fig(c):
    ankle_bones(c, 500, 470, 250, lp_mark=1.0, crack=1.0, label=False)
    c.set_source_rgba(*RED, 0.9); c.set_line_width(3)
    c.arc(500 + 0.18 * 250, 470 + 0.40 * 250, 50, 0, 2 * math.pi); c.stroke()


COVER = dict(lines=["“单板踝”", "被当成崴脚的骨折"], stat="34%", caption="单板脚踝骨折中，距骨外侧突骨折的占比", color=RED, figure=_cover_fig)
COVER2 = dict(kicker="单板 · 用数据说话", lines=[("单板踝", "ink"), ("被当成崴脚的骨折", "gold")], sub="单板脚踝骨折，三个里就有一个", motif="ankle", seed=4)
