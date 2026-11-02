"""单板 EP.02《护腕到底有没有用？》 (no voice-over: subtitles timed at reading speed, user records the narration)"""
import math
from common import *
from art import *
from board import *

SERIES = SERIES_B
TITLE = "护腕到底有没有用？"

# ================================================================== S1 hook
S1_SUBS = seq(["上一集说到：单板受伤，{r|手腕}排第一。",
               "那护腕，到底有没有用？",
               "这次不看感觉，看三项研究：一个随机试验、一篇系统综述、一项病例对照。"], t0=0.8)
S1_DUR = end_of(S1_SUBS) + 4.6


def s1(c, t, fi):
    paint_bg(c)
    a = ramp(t, 0, 0.8)
    T = [x for _, x, _ in S1_SUBS]
    gy = 760
    ground(c, gy, a)
    k = ease_io((t - 0.6) / 1.6)
    forearm(c, 700, gy, 360, a, guard=0, impact=ramp(t, T[0] + 0.8, T[0] + 1.4) * (1 - ramp(t, T[1], T[1] + 0.6)))
    g = ramp(t, T[1] + 0.3, T[1] + 1.2)
    forearm(c, 1300, gy, 360, a * g, guard=1.0)
    text(c, "不戴", 600, 420, 40, INK, a, align="c", bold=True)
    text(c, "戴护腕", 1200, 420, 40, GOLD, a * g, align="c", bold=True)
    text(c, "？", 1500, 420, 90, RED, a * ramp(t, T[1] + 1.0, T[1] + 1.6), bold=True)
    title_card(c, t, end_of(S1_SUBS) + 0.2, S1_DUR, TITLE, "随机试验 · 系统综述 · 病例对照")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2 RCT, Norway
S2_SUBS = seq(["2001年，挪威。研究者把{w|5029}名单板滑手随机分成两组：一组发护腕，一组不戴。",
               "一个雪季下来，不戴护腕的一组，手腕受伤{r|29}例；",
               "戴护腕的一组，只有{b|8}例。",
               "随机分组，排除了“戴护腕的人本来就更小心”这种干扰——这是证据等级里最硬的一种。"])
S2_DUR = end_of(S2_SUBS) + 0.8


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S2_DUR - 0.6, S2_DUR))
    T = [x for _, x, _ in S2_SUBS]
    # 5029 riders -> two halves (each dot = 25 people, 100 per side)
    ka = a_in * ramp(t, T[0] + 0.3, T[0] + 1.2)
    split = ease_io((t - T[0] - 2.5) / 1.4)
    centers = [lerp(W / 2 - 160, 620, split), lerp(W / 2 + 160, 1300, split)]
    for side, (lab, col) in enumerate((("不戴护腕", SKI_C), ("戴护腕", GOLD))):
        cx = centers[side]
        for i in range(100):
            c.arc(cx - 135 + (i % 10) * 30, 300 + (i // 10) * 30, 9, 0, 2 * math.pi)
            c.set_source_rgba(*mix(ICE, col, split), ka * 0.45); c.fill()
        text(c, lab, cx, 640, 38, col if side else INK, ka * split, align="c", bold=True)
    text(c, "5029 人 · 随机分两组", W / 2, 230, 34, DIM, ka * (1 - split), align="c")
    for side, (n, col, ts) in enumerate(((29, RED, T[1]), (8, BLUE_HI, T[2]))):
        cx = centers[side]
        k = ramp(t, ts + 0.2, ts + 1.6); m = int(round(n * k))
        for i in range(m):
            c.arc(cx - 135 + (i % 10) * 30, 300 + (i // 10) * 30, 12, 0, 2 * math.pi); c.set_source_rgba(*col, a_in); c.fill()
        if k > 0:
            text(c, f"{m} 例手腕伤", cx, 720, 50, col, a_in, align="c", bold=True)
    text(c, "每个点 ≈ 25 人", W / 2, 860, 22, DIM, ka * split * 0.9, align="c")
    pa = a_in * ramp(t, T[3], T[3] + 0.7)
    pill_label(c, "随机对照试验 RCT", W / 2, 800, 32, GOLD, pa)
    chapter_tag(c, "随机试验", "挪威 · 5029 名单板滑手", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "Am J Sports Med · 2001 · RCT", "护腕组 8 例 vs 对照组 29 例手腕伤", "Rønning · Rønning · Gerner · Engebretsen",
              ramp(t, T[0] + 0.6, T[0] + 1.4) * a_in)
    model_note(c, a_in, "点阵示意：两组人数按约各半画出")
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3 systematic review
S3_SUBS = seq(["2007年，一篇系统综述把6项研究放在一起，其中2项是随机试验。",
               "戴护腕，手腕受伤的风险降到不戴的{w|23%}——少了将近八成。",
               "细分来看：手腕骨折降到29%，手腕扭伤降到17%。"])
S3_DUR = end_of(S3_SUBS) + 0.8
ROWS3 = [("不戴护腕", 100, SKI_C), ("手腕受伤", 23, GOLD), ("手腕骨折", 29, GOLD), ("手腕扭伤", 17, GOLD)]


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S3_DUR - 0.6, S3_DUR))
    T = [x for _, x, _ in S3_SUBS]
    st = [T[1] - 0.2, T[1] + 0.6, T[2] + 0.3, T[2] + 1.6]
    x0, y0, w = 620, 300, 960
    for i, ((lab, v, col), s0) in enumerate(zip(ROWS3, st)):
        k = ease_io((t - s0) / 0.9)
        if k <= 0:
            continue
        a = a_in * min(1, k * 2); y = y0 + i * 110
        text(c, lab, x0 - 24, y + 48, 36, INK, a, align="r", bold=True)
        c.rectangle(x0, y, w * v / 100 * k, 70); c.set_source_rgba(*col, 0.85 * a); c.fill()
        text(c, f"{v * k:.0f}%" if i else "100%（基准）", x0 + w * v / 100 * k + 18, y + 50, 36, col, a, bold=True)
    ka = a_in * ramp(t, T[1] + 1.4, T[1] + 2.2)
    text(c, "↓ 约 77%", x0 + w * 0.23 + 220, y0 + 110 + 50, 44, GOLD, ka, bold=True)
    text(c, "相对风险（戴 / 不戴）", x0, y0 - 30, 24, DIM, a_in * ramp(t, T[1] - 0.2, T[1] + 0.4))
    dots(c, 760, 760, 6, 6, 70, 22, 2, a_in * ramp(t, T[0] + 0.3, T[0] + 1.0) * (1 - ramp(t, T[1] - 0.4, T[1])), col=ICE, hot_col=GOLD)
    text(c, "6 项研究 · 其中 2 项随机试验", W / 2, 860, 30, DIM, a_in * ramp(t, T[0] + 0.3, T[0] + 1.0) * (1 - ramp(t, T[1] - 0.4, T[1])), align="c")
    chapter_tag(c, "系统综述", "6 项研究合并", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "Clin J Sport Med · 2007 · 系统综述", "手腕伤 RR 0.23 · 骨折 0.29 · 扭伤 0.17", "Russell · Hagel · Francescutti",
              ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    model_note(c, a_in, "RR = 相对风险，戴护腕组 ÷ 不戴组")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4 how it works
S4_SUBS = seq(["护腕为什么管用？它在手掌一侧有一条硬板。",
               "撑地的一瞬间，冲击不再全压在腕关节上，而是顺着硬板分散到整段前臂；",
               "同时，硬板挡住手腕被猛地往后掰——很多手腕骨折，就是这样掰断的。"])
S4_DUR = end_of(S4_SUBS) + 0.8


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S4_DUR - 0.6, S4_DUR))
    T = [x for _, x, _ in S4_SUBS]
    gy = 760
    ground(c, gy, a_in)
    imp = ramp(t, T[1], T[1] + 0.5)
    ext = ease_io((t - T[2] - 0.3) / 0.8) * (1 - ramp(t, T[2] + 2.6, T[2] + 3.2))
    forearm(c, 640, gy, 380, a_in, guard=0, impact=imp, extend=ext)
    forearm(c, 1340, gy, 380, a_in, guard=ramp(t, T[0] + 0.5, T[0] + 1.2), impact=imp, spread=ramp(t, T[1] + 0.8, T[1] + 1.8))
    text(c, "不戴：冲击集中在手腕", 560, 320, 34, RED, a_in * imp, align="c", bold=True)
    text(c, "戴：硬板把冲击分到前臂", 1260, 320, 34, GOLD, a_in * ramp(t, T[1] + 0.8, T[1] + 1.4), align="c", bold=True)
    if ext > 0:
        text(c, "手腕被往后掰", 560, 380, 30, RED, a_in * ext, align="c")
        text(c, "硬板挡住", 1260, 380, 30, GOLD, a_in * ext, align="c")
    chapter_tag(c, "原理", "分散冲击 · 限制后伸", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "示意 · 通俗解释")
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5 caveat: case-control, Quebec
S5_SUBS = seq(["但它不是万能的。加拿大魁北克，19家雪场，2000多名单板滑手的病例对照研究：",
               "戴护腕，手、手腕、前臂受伤的几率，只有不戴的{w|0.15倍}；",
               "可肘部、上臂和肩膀，几率比却是{r|2.35}——",
               "这个结果统计上不显著，但研究者提醒：冲击可能顺着胳膊，往上转移了。"])
S5_DUR = end_of(S5_SUBS) + 0.8


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S5_DUR - 0.6, S5_DUR))
    T = [x for _, x, _ in S5_SUBS]
    # odds-ratio axis (log scale), 1 = no effect
    x0, x1, y = 300, 1620, 560
    lg = lambda v: x0 + (math.log10(v) - math.log10(0.05)) / (math.log10(10) - math.log10(0.05)) * (x1 - x0)
    aa = a_in * ramp(t, T[0] + 0.4, T[0] + 1.0)
    c.set_source_rgba(*FAINT, aa); c.rectangle(x0, y - 1, x1 - x0, 2); c.fill()
    for v in (0.1, 0.5, 1, 2, 5):
        c.rectangle(lg(v) - 1, y - 10, 2, 20); c.fill()
        text(c, f"{v:g}", lg(v), y + 50, 24, DIM, aa, align="c")
    c.set_dash([6, 6]); c.set_source_rgba(*INK, 0.6 * aa); c.set_line_width(2)
    c.move_to(lg(1), 280); c.line_to(lg(1), 760); c.stroke(); c.set_dash([])
    text(c, "1 = 没有差别", lg(1), 260, 24, DIM, aa, align="c")
    text(c, "← 更安全", lg(0.3), 800, 28, GOLD, aa, align="c", bold=True)
    text(c, "更危险 →", lg(3.5), 800, 28, RED, aa, align="c", bold=True)
    for (est, lo, hi, lab, col, yy, ts) in ((0.15, 0.05, 0.45, "手 · 腕 · 前臂", GOLD, 440, T[1]), (2.35, 0.70, 7.81, "肘 · 上臂 · 肩", RED, 660, T[2])):
        k = ramp(t, ts + 0.2, ts + 1.0)
        if k <= 0:
            continue
        c.set_source_rgba(*col, 0.7 * a_in * k); c.set_line_width(5)
        c.move_to(lg(lo), yy); c.line_to(lg(hi), yy); c.stroke()
        c.arc(lg(est), yy, 16, 0, 2 * math.pi); c.set_source_rgba(*col, a_in * k); c.fill()
        text(c, f"{est:g}", lg(est), yy - 30, 40, col, a_in * k, align="c", bold=True)
        text(c, lab, lg(lo) - 24, yy + 12, 30, INK, a_in * k, align="r", bold=True)
    pa = a_in * ramp(t, T[3], T[3] + 0.6)
    pill_label(c, "置信区间跨过 1：不显著", lg(2.35), 740, 26, RED, pa)
    chapter_tag(c, "病例对照", "魁北克 · 19 家雪场", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "Am J Epidemiol · 2005 · 病例对照", "手腕区 OR 0.15 · 肘肩区 OR 2.35（不显著）", "Hagel · Pless · Goulet 等",
              ramp(t, T[0] + 0.6, T[0] + 1.4) * a_in)
    model_note(c, a_in, "OR = 几率比，横线为 95% 置信区间，对数坐标")
    subs(c, t, S5_SUBS)
    overlays(c, fi)


# ================================================================== S6 conclusion + end
S6_SUBS = seq(["结论：护腕便宜、轻，证据很硬——手腕伤能少七八成，值得戴。",
               "但它不是让你放心直臂撑地的理由：摔的时候，照样要收手、团身、顺势滚。",
               "第一天上雪，为什么最危险？下一集，用数据说话。"])
S6_DUR = end_of(S6_SUBS) + 4.0


def s6(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S6_DUR - 1.4, S6_DUR - 0.4))
    T = [x for _, x, _ in S6_SUBS]
    la = a_in * (1 - ramp(t, T[2] - 0.2, T[2] + 0.4))
    numbered(c, [("1", "戴护腕", "手腕伤少七八成（RCT + 综述）", T[0] + 0.3),
                 ("2", "照样学摔", "收手 · 团身 · 顺势滚", T[1] + 0.3)], t, la, y0=360, dy=200)
    end_card(c, a_in * ramp(t, T[2], T[2] + 0.8), "第一天，为什么最危险？")
    subs(c, t, S6_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, S6_DUR - 1.0, S6_DUR))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR), ("s6", s6, S6_DUR)]


def _cover_fig(c):
    c.rectangle(-300, 640, 1600, 400); c.set_source_rgb(*TERRAIN_B); c.fill()
    c.set_source_rgba(*RIM_B, 0.9); c.rectangle(-300, 638, 1600, 3); c.fill()
    forearm(c, 330, 640, 330, guard=0, impact=1.0)
    forearm(c, 800, 640, 330, guard=1.0, spread=1.0)
    text(c, "29", 250, 230, 120, RED, bold=True, align="c")
    text(c, "8", 720, 230, 120, GOLD, bold=True, align="c")
    text(c, "不戴", 250, 300, 40, DIM, align="c"); text(c, "戴护腕", 720, 300, 40, DIM, align="c")


COVER = dict(lines=["护腕", "到底有没有用？"], stat="↓77%", caption="戴护腕后手腕受伤风险（系统综述，RR 0.23）", color=GOLD, figure=_cover_fig)
COVER2 = dict(kicker="单板 · 用数据说话", lines=[("护腕", "ink"), ("到底有没有用", "gold")], sub="随机试验：手腕伤 29 例 vs 8 例", motif="guard", seed=2)
