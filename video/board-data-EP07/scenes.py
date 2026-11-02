"""单板 EP.07《往后摔，还是往前摔？》 (no voice-over)"""
import math
from common import *
from art import *
from board import *

SERIES = SERIES_B
TITLE = "往后摔，还是往前摔？"

# ================================================================== S1 hook
S1_SUBS = seq(["单板的摔法，基本只有两个方向：往后坐，或者往前扑。",
               "双脚绑在一块板上，侧着摔的反而少。",
               "哪个方向更危险？伤到的地方，完全不一样。"], t0=0.8)
S1_DUR = end_of(S1_SUBS) + 4.6


def s1(c, t, fi):
    paint_bg(c)
    a = ramp(t, 0, 0.8)
    T = [x for _, x, _ in S1_SUBS]
    gy = 780
    ground(c, gy, a)
    kb = ease_io((t - T[0] - 0.8) / 0.8); kf = ease_io((t - T[0] - 2.2) / 0.8)
    rider_profile(c, 640, gy, 280, back=kb, alpha=a)
    rider_profile(c, 1240, gy, 280, fwd=kf, alpha=a)
    text(c, "往后坐", 560, 330, 40, ICE, a * kb, align="c", bold=True)
    text(c, "往前扑", 1340, 330, 40, GOLD, a * kf, align="c", bold=True)
    title_card(c, t, end_of(S1_SUBS) + 0.2, S1_DUR, TITLE, "颅脑损伤 · 计算机模拟 · 上肢伤")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2 head injuries: direction
S2_SUBS = seq(["先看最严重的伤：头。日本一项研究，分析了{w|38例}单板造成的严重颅脑损伤——",
               "其中{r|68%}，是往后摔的。",
               "一篇文献综述把多项研究汇总：单板摔伤头部的跌倒里，往后摔占{r|48%到79%}，",
               "往前摔占9%到45%，侧着摔只有6%到12%。"])
S2_DUR = end_of(S2_SUBS) + 0.8


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S2_DUR - 0.6, S2_DUR))
    T = [x for _, x, _ in S2_SUBS]
    da = a_in * ramp(t, T[0] + 0.5, T[0] + 1.2) * (1 - ramp(t, T[2] - 0.3, T[2] + 0.2))
    if da > 0:
        hot = int(round(26 * ramp(t, T[1] + 0.2, T[1] + 1.6)))       # 68% of 38 ≈ 26
        dots(c, W / 2 - 18 * 70 / 2 + 35, 400, 38, 19, 70, 24, hot, da, col=ICE)
        text(c, "38 例严重颅脑损伤", W / 2, 320, 40, INK, da, align="c", bold=True)
        if hot:
            text(c, f"{hot} 例往后摔 ≈ 68%", W / 2, 640, 56, RED, da, align="c", bold=True)
    ra = a_in * ramp(t, T[2] - 0.1, T[2] + 0.5)
    if ra > 0:
        x0, w = 560, 1000
        rows = [("往后摔", 48, 79, RED, T[2] + 0.8), ("往前摔", 9, 45, GOLD, T[3] + 0.2), ("侧着摔", 6, 12, ICE, T[3] + 2.2)]
        c.set_source_rgba(*FAINT, ra); c.rectangle(x0, 720, w, 2); c.fill()
        for v in (0, 25, 50, 75, 100):
            text(c, f"{v}%", x0 + w * v / 100, 760, 24, DIM, ra, align="c")
        for i, (lab, lo, hi, col, ts) in enumerate(rows):
            k = ease_io((t - ts) / 0.9)
            if k <= 0:
                continue
            y = 330 + i * 120
            text(c, lab, x0 - 30, y + 46, 40, INK, ra, align="r", bold=True)
            c.rectangle(x0 + w * lo / 100, y, w * (hi - lo) / 100 * k, 64); c.set_source_rgba(*col, 0.88 * ra); c.fill()
            text(c, f"{lo}–{hi}%", x0 + w * hi / 100 * k + 20 if k < 1 else x0 + w * hi / 100 + 20, y + 46, 36, col, ra * k, bold=True)
        text(c, "各研究的范围（区间）", x0, 290, 24, DIM, ra)
    chapter_tag(c, "头部", "严重颅脑损伤 · 摔的方向", ramp(t, 0.5, 1.1) * a_in)
    if t < T[2]:
        cite_card(c, "J Neurosurg · 2002", "38 例严重颅脑损伤，68% 为后摔", "Nakaguchi · Fujimaki · Ueki 等",
                  ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in * (1 - ramp(t, T[2] - 0.5, T[2])))
    else:
        cite_card(c, "文献综述 · 多项研究汇总", "后摔 48–79% · 前摔 9–45% · 侧摔 6–12%", "单板头部损伤的跌倒方向", ramp(t, T[2], T[2] + 0.6) * a_in)
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3 opposite-edge phenomenon
S3_SUBS = seq(["最凶的一种往后摔，日本研究者叫它{r|反刃现象}：",
               "板平着滑，下坡那一侧的刃突然挂进雪里，人被整个掀翻，",
               "后脑像鞭梢一样，甩着砸到雪面上。",
               "研究者认为：这一甩产生的旋转，会扯断大脑表面的血管——这是严重颅脑损伤的主要机制。"])
S3_DUR = end_of(S3_SUBS) + 0.8


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S3_DUR - 0.6, S3_DUR))
    T = [x for _, x, _ in S3_SUBS]
    gy = 780
    ground(c, gy, a_in)
    k = ease_io((t - T[1] - 1.6) / 0.6)
    x = 600 + 300 * ramp(t, T[0], T[1] + 1.6)
    rider_profile(c, x, gy, 320, back=k, alpha=a_in, wobble=0.12 * k * (1 - k) * 4)
    edge = ramp(t, T[1] + 1.2, T[1] + 1.6)
    if edge > 0:
        c.new_path(); c.arc(x - 30, gy, 34, 0, 2 * math.pi); c.set_source_rgba(*RED, a_in * edge * (1 - k * 0.6)); c.set_line_width(5); c.stroke()
        text(c, "下坡刃挂雪", x - 30, gy + 70, 30, RED, a_in * edge * (1 - k * 0.6), align="c", bold=True)
    wa = a_in * ramp(t, T[2], T[2] + 0.6)
    if wa > 0:
        # whip arc of the head
        hx, hy = x - 0.70 * 320, gy - 0.85 * 320
        c.new_path(); c.arc(x - 0.2 * 320, gy - 0.3 * 320, 0.62 * 320, math.pi * 1.05, math.pi * 1.45)
        c.set_source_rgba(*RED, 0.9 * wa); c.set_line_width(6); c.stroke()
        arrow_head(c, x - 0.2 * 320 + 0.62 * 320 * math.cos(math.pi * 1.05), gy - 0.3 * 320 + 0.62 * 320 * math.sin(math.pi * 1.05), math.pi * 1.05 - math.pi / 2, 24, RED, wa)
        text(c, "后脑被“甩”向雪面", 1300, 360, 40, RED, wa, align="c", bold=True)
    ma = a_in * ramp(t, T[3] + 0.5, T[3] + 1.2)
    if ma > 0:
        pill_label(c, "旋转加速度 → 剪切 → 血管撕裂", 1300, 450, 32, GOLD, ma)
    chapter_tag(c, "反刃现象", "opposite-edge phenomenon", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "J Neurosurg · 2002", "反刃现象：旋转导致的剪切应变", "Nakaguchi · Fujimaki · Ueki 等", ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    model_note(c, a_in, "示意 · 动作与轨迹为通俗演示")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4 computer simulation: head impact speed
S4_SUBS = seq(["往后摔，头撞雪到底有多快？法国一个团队，用计算机模拟了{w|324种}往后摔：",
               "头撞向雪面的平均速度，每小时{r|28公里}——比美国头盔标准测试用的速度还高；",
               "324种情况里，{r|70%}有轻度脑损伤的高风险，{r|15%}有重度脑损伤的高风险。"])
S4_DUR = end_of(S4_SUBS) + 0.8


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S4_DUR - 0.6, S4_DUR))
    T = [x for _, x, _ in S4_SUBS]
    # speedometer-like bar
    sa = a_in * ramp(t, T[1] - 0.2, T[1] + 0.4)
    x0, y0, w = 420, 330, 1080
    if sa > 0:
        c.rectangle(x0, y0, w, 70); c.set_source_rgba(*FAINT, 0.4 * sa); c.fill()
        k = ease_io((t - T[1] - 0.2) / 1.2)
        c.rectangle(x0, y0, w * 28 / 40 * k, 70); c.set_source_rgba(*RED, 0.9 * sa); c.fill()
        lo, hi = 22, 34
        c.set_source_rgba(*INK, 0.7 * sa * k); c.set_line_width(3)
        c.move_to(x0 + w * lo / 40, y0 + 100); c.line_to(x0 + w * hi / 40, y0 + 100); c.stroke()
        text(c, f"{28 * k:.0f} km/h", x0 + w * 28 / 40 * k, y0 - 24, 56, RED, sa, align="c", bold=True)
        text(c, "± 6 km/h", x0 + w * 28 / 40, y0 + 140, 26, DIM, sa * k, align="c")
        for v in (0, 10, 20, 30, 40):
            text(c, f"{v}", x0 + w * v / 40, y0 + 190, 24, DIM, sa, align="c")
        text(c, "头部垂直撞向雪面的速度（平均）", x0, y0 - 90, 28, DIM, sa)
    da = a_in * ramp(t, T[2] - 0.1, T[2] + 0.5)
    if da > 0:
        n = 100
        hot1 = int(70 * ramp(t, T[2] + 0.8, T[2] + 2.0)); hot2 = int(15 * ramp(t, T[2] + 3.0, T[2] + 3.8))
        for i in range(n):
            cx = 560 + (i % 20) * 42; cy = 590 + (i // 20) * 42
            col = RED if i < hot2 else GOLD if i < hot1 else FAINT
            c.arc(cx, cy, 15, 0, 2 * math.pi); c.set_source_rgba(*col, da); c.fill()
        text(c, "轻度高风险 70%", 1420, 630, 32, GOLD, da * (hot1 > 0), bold=True)
        text(c, "重度高风险 15%", 1420, 690, 32, RED, da * (hot2 > 0), bold=True)
    ia = a_in * ramp(t, T[0] + 0.5, T[0] + 1.2) * (1 - ramp(t, T[1] - 0.4, T[1]))
    text(c, "324", W / 2, 540, 180, INK, ia, align="c", bold=True)
    text(c, "种模拟的往后摔：速度 · 雪的软硬 · 体型 · 姿势", W / 2, 620, 32, DIM, ia, align="c")
    chapter_tag(c, "计算机模拟", "324 种往后摔", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "Scand J Med Sci Sports · 2017", "头部撞击 28 ± 6 km/h，高于头盔标准", "Bailly 等", ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    model_note(c, a_in, "数值模拟结果 · 高风险阈值：峰值加速度 > 80 g（轻度）、HIC > 1000（重度）")
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5 upper limb: direction decides the injury
S5_SUBS = seq(["胳膊也一样，摔的方向决定伤在哪。日本一家医院统计单板的上肢伤：",
               "手腕骨折里{r|68.1%}、肘关节脱位里{r|63.5%}，来自{b|往后摔}——手往身后撑；",
               "肩关节脱位里{r|68.9%}、上臂骨折里{r|60.7%}，来自{w|往前摔}——整个人扑在胳膊上。"])
S5_DUR = end_of(S5_SUBS) + 0.8


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S5_DUR - 0.6, S5_DUR))
    T = [x for _, x, _ in S5_SUBS]
    kb = ramp(t, T[1] + 0.3, T[1] + 1.3); kf = ramp(t, T[2] + 0.3, T[2] + 1.3)
    body_map(c, 620, 770, 300, [("wrist", kb, BLUE_HI), ("wrist_r", kb * 0.8, BLUE_HI), ("elbow", kb * 0.8, BLUE_HI), ("elbow_r", kb * 0.6, BLUE_HI)], a_in)
    body_map(c, 1300, 770, 300, [("shoulder", kf, GOLD), ("shoulder_r", kf * 0.8, GOLD), ("upperarm", kf * 0.8, GOLD), ("upperarm_r", kf * 0.6, GOLD)], a_in)
    text(c, "往后摔", 620, 830, 40, BLUE_HI, a_in, align="c", bold=True)
    text(c, "往前摔", 1300, 830, 40, GOLD, a_in, align="c", bold=True)
    for i, (lab, x, y, k, col) in enumerate((("手腕骨折 68.1%", 430, 500, kb, BLUE_HI), ("肘关节脱位 63.5%", 430, 560, kb, BLUE_HI),
                                             ("肩关节脱位 68.9%", 1490, 380, kf, GOLD), ("上臂骨折 60.7%", 1490, 440, kf, GOLD))):
        text(c, lab, x, y, 34, col, a_in * k, bold=True, align="r" if x < 960 else "l")
    chapter_tag(c, "上肢", "摔的方向 → 受伤部位", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "Am J Sports Med · 2010", "腕骨折、肘脱位多为后摔；肩脱位、上臂骨折多为前摔", "Yamauchi · Wakahara · Fukuta 等",
              ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    model_note(c, a_in, "百分比 = 该类损伤中由该方向跌倒造成的比例")
    subs(c, t, S5_SUBS)
    overlays(c, fi)


# ================================================================== S6 how to fall + end
S6_SUBS = seq(["所以怎么摔，是能练的：",
               "往后摔：收下巴、低头看肚子，用屁股和整个后背着地，别伸手往后撑；",
               "往前摔：用膝盖和小臂着地，顺势往前滚，别直着胳膊扑；",
               "还有——{w|戴头盔}。往后摔的那一下，谁都来不及反应。",
               "鸭子站还是前倾站？下一集，用数据说话。"])
S6_DUR = end_of(S6_SUBS) + 4.0


def s6(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S6_DUR - 1.4, S6_DUR - 0.4))
    T = [x for _, x, _ in S6_SUBS]
    la = a_in * (1 - ramp(t, T[4] - 0.2, T[4] + 0.4))
    numbered(c, [("后", "收下巴 · 屁股后背着地", "别伸手往后撑", T[1]), ("前", "膝盖小臂着地 · 顺势滚", "别直臂扑", T[2]),
                 ("!", "戴头盔", "后摔来不及反应", T[3])], t, la)
    end_card(c, a_in * ramp(t, T[4], T[4] + 0.8), "鸭子站还是前倾站？")
    subs(c, t, S6_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, S6_DUR - 1.0, S6_DUR))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR), ("s6", s6, S6_DUR)]


def _cover_fig(c):
    c.rectangle(-300, 700, 1600, 300); c.set_source_rgb(*TERRAIN_B); c.fill()
    c.set_source_rgba(*RIM_B, 0.9); c.rectangle(-300, 698, 1600, 3); c.fill()
    rider_profile(c, 360, 700, 300, back=1.0, wrist_mark=1.0)
    rider_profile(c, 660, 700, 300, fwd=1.0)


COVER = dict(lines=["往后摔", "还是往前摔？"], stat="68%", caption="38 例单板严重颅脑损伤中，往后摔的比例", color=RED, figure=_cover_fig)
COVER2 = dict(kicker="单板 · 用数据说话", lines=[("往后摔", "ink"), ("还是往前摔", "gold")], sub="严重颅脑损伤 68% 是后摔 · 头撞雪 28 km/h", motif="falls", seed=7)
