"""单板 EP.03《第一天最危险》 (no voice-over)"""
import math
from common import *
from art import *
from board import *

SERIES = SERIES_B
TITLE = "第一天，为什么最危险？"

# ================================================================== S1 hook
S1_SUBS = seq(["整个滑雪生涯里，最危险的一天，往往是第一天。",
               "不是因为坡陡、速度快——新手的坡最缓，速度最慢。",
               "可数据很一致：伤，扎堆出现在刚开始的那几天。"], t0=0.8)
S1_DUR = end_of(S1_SUBS) + 4.6


def s1(c, t, fi):
    paint_bg(c)
    a = ramp(t, 0, 0.8)
    T = [x for _, x, _ in S1_SUBS]
    gy = 780
    ground(c, gy, a)
    # a calendar strip: day 1 glows red
    for i in range(10):
        x = 300 + i * 135; k = ramp(t, 0.6 + i * 0.12, 1.0 + i * 0.12)
        hot = 1.0 - min(1, i / 5)
        col = mix(FAINT, RED, hot * ramp(t, T[2], T[2] + 1.2))
        rounded_rect(c, x, 150, 115, 120, 12); c.set_source_rgba(*col, a * k * 0.9); c.fill()
        text(c, f"第{i + 1}天", x + 57, 222, 30, INK, a * k, align="c", bold=True)
    wob = 0.05 * math.sin(t * 5)
    rider_profile(c, 960, gy, 240, back=0.15 + 0.1 * math.sin(t * 2.5), alpha=a, wobble=wob)
    title_card(c, t, end_of(S1_SUBS) + 0.2, S1_DUR, TITLE, "前瞻研究 · 病例对照 · 综述")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2 Machold: first half-day, first 4 days, first week
S2_SUBS = seq(["一项针对单板初学者的前瞻研究，跟踪了上课的学员：",
               "第一个半天，受伤的概率就有{r|3.5%}——差不多每{r|28}个人里，就有一个。",
               "{r|35%}的受伤，发生在前4天；{r|51%}，在第一周之内。"])
S2_DUR = end_of(S2_SUBS) + 0.8


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S2_DUR - 0.6, S2_DUR))
    T = [x for _, x, _ in S2_SUBS]
    da = a_in * ramp(t, T[1] - 0.2, T[1] + 0.4) * (1 - ramp(t, T[2] - 0.3, T[2] + 0.2))
    if da > 0:
        hot = 1 if t > T[1] + 1.6 else 0
        dots(c, W / 2 - 14 * 50 / 2 + 25, 360, 28, 14, 50, 17, hot, da, ramp(t, T[1], T[1] + 1.4), col=ICE)
        text(c, "第一个半天", W / 2, 300, 40, INK, da, align="c", bold=True)
        text(c, "3.5% ≈ 1 / 28", W / 2, 560, 60, RED, da * hot, align="c", bold=True)
    ca = a_in * ramp(t, T[2] - 0.1, T[2] + 0.5)
    if ca > 0:
        x0, x1, y = 260, 1660, 420
        wd = x1 - x0
        c.rectangle(x0, y, wd, 90); c.set_source_rgba(*FAINT, 0.35 * ca); c.fill()
        k1 = ease_io((t - T[2] - 0.4) / 1.0); k2 = ease_io((t - T[2] - 2.6) / 1.0)
        c.rectangle(x0, y, wd * 0.35 * k1, 90); c.set_source_rgba(*RED, 0.9 * ca); c.fill()
        c.rectangle(x0 + wd * 0.35, y, wd * 0.16 * k2, 90); c.set_source_rgba(*mix(RED, GOLD, 0.5), 0.8 * ca); c.fill()
        for f, lab, kk, ly in ((0.35, "前 4 天  35%", k1, y - 40), (0.51, "第 1 周  51%", k2, y + 170)):
            if kk > 0:
                xx = x0 + wd * f
                c.set_source_rgba(*INK, 0.8 * ca * kk); c.rectangle(xx - 1.5, y - 20 if ly < y else y, 3, 110 if ly < y else 130); c.fill()
                text(c, lab, xx, ly, 40, INK, ca * kk, align="c", bold=True)
        text(c, "全部受伤 = 100%", x1, y + 130, 26, DIM, ca, align="r")
        text(c, "按发生时间累计", x0, y + 130, 26, DIM, ca)
    chapter_tag(c, "前几天", "单板初学者 · 前瞻研究", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "J Trauma · 2000 · 前瞻研究", "首个半天 3.5% · 前 4 天 35% · 首周 51%", "Machold · Kwasny · Gassler 等",
              ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3 Weir CMAJ review: first time / first season
S3_SUBS = seq(["加拿大医学会杂志的一篇综述，把视野拉长到整个雪季：",
               "将近{r|四分之一}的单板受伤，发生在第一次上板；",
               "将近{r|一半}，发生在第一个雪季。"])
S3_DUR = end_of(S3_SUBS) + 0.8


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S3_DUR - 0.6, S3_DUR))
    T = [x for _, x, _ in S3_SUBS]
    cx, cy, r = W / 2, 500, 230
    k0 = ramp(t, T[0] + 0.3, T[0] + 1.0)
    c.new_path(); c.arc(cx, cy, r, 0, 2 * math.pi); c.set_source_rgba(*FAINT, 0.4 * a_in * k0); c.fill()
    for frac, col, ts, lab, lx, al in ((0.50, mix(RED, GOLD, 0.5), T[2], "第一个雪季  ≈ 1/2", cx - r - 40, "r"),
                                        (0.25, RED, T[1], "第一次上板  ≈ 1/4", cx + r + 40, "l")):
        k = ease_io((t - ts - 0.3) / 1.0)
        if k <= 0:
            continue
        c.new_path(); c.move_to(cx, cy); c.arc(cx, cy, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * frac * k); c.close_path()
        c.set_source_rgba(*col, (0.95 if frac < 0.3 else 0.5) * a_in); c.fill()
        text(c, lab, lx, cy - 60 if frac < 0.3 else cy + 120, 42, col, a_in * k, align=al, bold=True)
    text(c, "单板受伤 = 100%", cx, cy + r + 60, 26, DIM, a_in * k0, align="c")
    chapter_tag(c, "第一个雪季", "综述 · 新手风险最高", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "CMAJ · 2001 · 综述", "近 1/4 在首次上板，近 1/2 在首个雪季", "Weir", ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    model_note(c, a_in, "综述中的“将近”，图按 1/4、1/2 示意")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4 Scotland case-control + Norway RCT finding
S4_SUBS = seq(["苏格兰的一项病例对照研究：伤者里，第一天上雪的人，是正常比例的{r|2.2倍}。",
               "和第一天受伤有关的因素里，有两条值得注意：{w|玩单板}，和{w|租来或借来的装备}。",
               "挪威那项护腕试验也发现：前5天的新手、用租赁装备的人，更容易受伤。"])
S4_DUR = end_of(S4_SUBS) + 0.8


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S4_DUR - 0.6, S4_DUR))
    T = [x for _, x, _ in S4_SUBS]
    xa = a_in * (1 - ramp(t, T[1] - 0.3, T[1] + 0.2))
    if xa > 0:
        # two bars: share among all riders vs share among the injured
        k = ease_io((t - T[0] - 1.0) / 1.4)
        for i, (lab, v, col) in enumerate((("雪场里的第一天新手", 1.0, ICE), ("伤者里的第一天新手", 2.2, RED))):
            y = 360 + i * 170
            text(c, lab, 760, y + 60, 36, INK, xa, align="r", bold=True)
            vv = 1 + (v - 1) * k if i else 1.0
            c.rectangle(800, y, 300 * vv, 90); c.set_source_rgba(*col, 0.88 * xa); c.fill()
            text(c, f"× {vv:.1f}", 800 + 300 * vv + 20, y + 64, 52, col, xa, bold=True)
    pa = a_in * ramp(t, T[1] - 0.1, T[1] + 0.5)
    if pa > 0:
        items = [("单板", "首日受伤的相关因素之一", T[1] + 1.4), ("租 / 借的装备", "不合脚、没调好", T[1] + 3.0), ("前 5 天", "挪威试验里的高风险期", T[2] + 0.4)]
        for i, (big, small, ts) in enumerate(items):
            k = ramp(t, ts, ts + 0.6)
            y = 330 + i * 170
            pill_label(c, big, 620, y, 48, (ICE, GOLD, RED)[i], pa * k)
            text(c, small, 860, y + 14, 34, DIM, pa * k)
    chapter_tag(c, "风险因素", "苏格兰 · 挪威", ramp(t, 0.5, 1.1) * a_in)
    if t < T[2]:
        cite_card(c, "Am J Sports Med · 2004 · 病例对照", "首日者在伤者中多出 2.2 倍", "Langran · Selvaraj",
                  ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in * (1 - ramp(t, T[2] - 0.5, T[2])))
    else:
        cite_card(c, "Am J Sports Med · 2001 · RCT", "前 5 天、租赁装备者更易受伤", "Rønning · Rønning · Gerner · Engebretsen", ramp(t, T[2], T[2] + 0.6) * a_in)
    model_note(c, a_in, "2.2 倍：伤者中的占比 ÷ 全体滑雪者中的占比")
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5 why: catching an edge
S5_SUBS = seq(["新手为什么容易伤？最常见的一种摔法，叫{r|吃刃}：",
               "板在雪上平滑，下坡那一侧的刃一挂进雪里，板瞬间停住，人却还在往前冲。",
               "后刃吃刃，人往后砸，屁股、后脑和手腕先着地；",
               "前刃吃刃，人往前扑，膝盖和手腕先着地——而且来得太快，根本来不及反应。"])
S5_DUR = end_of(S5_SUBS) + 0.8


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S5_DUR - 0.6, S5_DUR))
    T = [x for _, x, _ in S5_SUBS]
    gy = 780
    ground(c, gy, a_in)
    # rider slides, then the downhill edge catches
    ca = a_in * (1 - ramp(t, T[2] - 0.3, T[2] + 0.2))
    if ca > 0:
        k = ramp(t, T[1] + 1.4, T[1] + 1.9)
        x = 520 + 380 * ramp(t, T[0], T[1] + 1.4)
        rider_profile(c, x, gy, 280, alpha=ca, wobble=-0.15 * k, fwd=0.35 * k)
        arrow(c, x - 260, gy - 420, x - 60, gy - 420, ICE, ca * (1 - k), 5, 22)
        text(c, "平滑", x - 160, gy - 450, 30, ICE, ca * (1 - k), align="c")
        if k > 0:
            c.arc(x + 50, gy, 34, 0, 2 * math.pi); c.set_source_rgba(*RED, ca * k); c.set_line_width(5); c.stroke()
            text(c, "下坡刃挂进雪里：板停，人还在冲", W / 2, 300, 40, RED, ca * k, align="c", bold=True)
    fa = a_in * ramp(t, T[2] - 0.2, T[2] + 0.4)
    if fa > 0:
        kb = ease_io((t - T[2] - 0.3) / 0.5); kf = ease_io((t - T[3] - 0.3) / 0.5)
        pb = rider_profile(c, 700, gy, 280, back=kb, wrist_mark=kb, alpha=fa)
        pf = rider_profile(c, 1200, gy, 280, fwd=kf, wrist_mark=kf, knee_mark=kf, alpha=fa * ramp(t, T[3] - 0.2, T[3] + 0.3))
        text(c, "后刃吃刃", 620, 320, 38, INK, fa, align="c", bold=True)
        text(c, "前刃吃刃", 1300, 320, 38, INK, fa * ramp(t, T[3] - 0.2, T[3] + 0.3), align="c", bold=True)
        text(c, "不到 0.5 秒", W / 2, 420, 34, RED, fa * ramp(t, T[3] + 2.0, T[3] + 2.6), align="c", bold=True)
    chapter_tag(c, "吃刃", "新手最典型的摔法", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "示意 · 通俗解释；“不到 0.5 秒”为示意")
    subs(c, t, S5_SUBS)
    overlays(c, fi)


# ================================================================== S6 advice + end
S6_SUBS = seq(["所以第一天，最划算的几件事：",
               "第一，{w|护腕、头盔}戴上；",
               "第二，租的装备要试合脚，固定器让店员帮你调好；",
               "第三，在缓坡上把落叶飘练熟，别急着上中级道。",
               "被当成崴脚的骨折——单板踝。下一集，用数据说话。"])
S6_DUR = end_of(S6_SUBS) + 4.0


def s6(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S6_DUR - 1.4, S6_DUR - 0.4))
    T = [x for _, x, _ in S6_SUBS]
    la = a_in * (1 - ramp(t, T[4] - 0.2, T[4] + 0.4))
    numbered(c, [("1", "护腕 + 头盔", "首日就戴", T[1]), ("2", "装备合脚", "租赁装备是风险因素", T[2]),
                 ("3", "缓坡练落叶飘", "前一周最危险", T[3])], t, la)
    end_card(c, a_in * ramp(t, T[4], T[4] + 0.8), "“单板踝”：被当成崴脚的骨折")
    subs(c, t, S6_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, S6_DUR - 1.0, S6_DUR))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR), ("s6", s6, S6_DUR)]


def _cover_fig(c):
    for i in range(7):
        x = 40 + i * 135; hot = 1 - min(1, i / 3.5)
        rounded_rect(c, x, 120, 115, 130, 12); c.set_source_rgba(*mix(FAINT, RED, hot), 0.95); c.fill()
        text(c, f"第{i + 1}天", x + 57, 200, 30, INK, align="c", bold=True)
    c.rectangle(-300, 700, 1600, 300); c.set_source_rgb(*TERRAIN_B); c.fill()
    c.set_source_rgba(*RIM_B, 0.9); c.rectangle(-300, 698, 1600, 3); c.fill()
    rider_profile(c, 560, 700, 300, back=0.85, wrist_mark=1.0)


COVER = dict(lines=["第一天", "为什么最危险？"], stat="3.5%", caption="单板初学者第一个半天的受伤概率", color=RED, figure=_cover_fig)
