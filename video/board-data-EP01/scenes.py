"""单板 EP.01《单板最常伤哪里？》 (voiced: voice/durations.json from tts.py drives the timing)"""
import math
from common import *
from art import *
from board import *

use_voice(__file__)
VOICE = "zm_yunxi"
VOICE_SPEED = 0.9
SERIES = "单板 · 用数据说话"
TITLE = "单板最常伤哪里？"
SKI_C, BRD_C = (0.62, 0.66, 0.74), ICE      # skiing grey, snowboarding ice-blue


def subs(c, t, S):
    for s, a, b in S:
        subtitle(c, s, t, a, b)


def ground(c, gy, a):
    c.rectangle(0, gy, W, H - gy); c.set_source_rgba(*TERRAIN, a); c.fill()
    c.set_source_rgba(*RIM, 0.9 * a); c.rectangle(0, gy - 1.5, W, 3); c.fill()


# spoken text where the subtitle would be read wrongly
SAY = {
    "美国佛蒙特州，一家雪场诊所从1988年到2006年，登记了每一位伤者。": "美国佛蒙特州，一家雪场诊所从一九八八年到二零零六年，登记了每一位伤者。",
    "膝盖反倒被保护了：双板的每只板都是一根长杠杆，能把小腿往外拧；": "膝盖反倒被保护了：双板的每只板都是一根常杠杆，能把小腿往外拧；",
    "2025年的一项荟萃分析，汇总了77项研究、七十六万多名伤者。": "二零二五年的一项荟萃分析，汇总了七十七项研究、七十六万多名伤者。",
}

# ================================================================== S1  hook: two body maps
S1_SUBS = seq(["同样是摔，双板和单板，伤到的地方完全不一样。",
               "双板最常见的是{b|膝盖}；单板排第一的，是{r|手腕}。",
               "这不是印象，是一家雪场诊所，十八个雪季的病例统计。"], t0=0.8)
S1_DUR = end_of(S1_SUBS) + 4.6


def s1(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.8)
    T = [a for _, a, _ in S1_SUBS]
    kk = ramp(t, T[1], T[1] + 1.0); kw = ramp(t, T[1] + 1.6, T[1] + 2.6)
    pulse = 0.85 + 0.15 * math.sin(t * 4)
    for cx, lab, spots in ((620, "双板", [("knee", kk * pulse, BLUE_HI), ("knee_r", kk * pulse * 0.7, BLUE_HI)]),
                           (1300, "单板", [("wrist", kw * pulse, RED), ("wrist_r", kw * pulse * 0.7, RED)])):
        body_map(c, cx, 800, 300, spots, a_in)
        text(c, lab, cx, 880, 40, INK, a_in, align="c", bold=True)
    text(c, "膝盖", 620 + 150, 800 - 0.48 * 300 + 14, 42, BLUE_HI, a_in * kk, bold=True)
    text(c, "手腕", 1300 + 0.47 * 300 + 60, 800 - 0.86 * 300 + 14, 42, RED, a_in * kw, bold=True)
    te = end_of(S1_SUBS)
    ta = ramp(t, te + 0.2, te + 1.1) * (1 - ramp(t, S1_DUR - 0.7, S1_DUR))
    if ta > 0:
        c.set_source_rgba(*BG, 0.86 * ta); c.paint()
        text(c, SERIES, W / 2, 380, 30, DIM, ta, align="c", spacing=0.3)
        text(c, TITLE, W / 2, 510, 92, INK, ta, align="c", bold=True)
        c.set_source_rgba(*GOLD, 0.8 * ta); c.rectangle(W / 2 - 160, 556, 320, 2); c.fill()
        text(c, "18 个雪季 · 一篇综述 · 一项荟萃分析", W / 2, 620, 32, GOLD, ta, align="c")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2  Vermont, Kim et al. 2012
S2_SUBS = seq(["美国佛蒙特州，一家雪场诊所从1988年到2006年，登记了每一位伤者。",
               "单板受伤里，{r|手腕}占了{r|27.6%}；双板只有2.8%，单板是它的将近十倍。",
               "反过来，双板最常见的是{b|前十字韧带}扭伤，占17.2%；单板只有1.7%。",
               "再按滑雪日算：单板平均每345个滑雪日出一次伤，双板是400个——单板伤得更频繁。"])
S2_DUR = end_of(S2_SUBS) + 0.8


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S2_DUR - 0.6, S2_DUR))
    T = [a for _, a, _ in S2_SUBS]
    # timeline of seasons (first line)
    la = a_in * (1 - ramp(t, T[1] - 0.2, T[1] + 0.4))
    if la > 0:
        x0, x1, y = 360, 1560, 520
        k = ramp(t, T[0] + 0.3, T[0] + 3.2)
        c.set_source_rgba(*FAINT, la); c.rectangle(x0, y - 2, x1 - x0, 4); c.fill()
        n = int(18 * k)
        for i in range(18):
            xx = x0 + (i + 0.5) * (x1 - x0) / 18
            a = la * (1.0 if i < n else 0.15)
            c.arc(xx, y, 11, 0, 2 * math.pi); c.set_source_rgba(*ICE, a); c.fill()
        text(c, "1988", x0, y + 60, 30, DIM, la, align="c"); text(c, "2006", x1, y + 60, 30, DIM, la, align="c")
        text(c, f"{n} 个雪季", W / 2, y - 60, 44, INK, la, align="c", bold=True)
    # grouped bars
    ga = a_in * ramp(t, T[1] - 0.1, T[1] + 0.5) * (1 - ramp(t, T[3] - 0.2, T[3] + 0.4))
    if ga > 0:
        x0, w, bh = 620, 900, 54
        groups = [("手腕", 27.6, 2.8, T[1] + 0.3), ("前十字韧带", 1.7, 17.2, T[2] + 0.2)]
        for gi, (lab, vb, vs, ts) in enumerate(groups):
            y = 330 + gi * 260
            text(c, lab, x0 - 30, y + 80, 40, INK, ga * ramp(t, ts - 0.3, ts), align="r", bold=True)
            for j, (who, v, col) in enumerate((("单板", vb, BRD_C), ("双板", vs, SKI_C))):
                k = ease_io((t - ts - j * 0.5) / 0.9)
                if k <= 0:
                    continue
                yy = y + j * (bh + 14)
                hot = (gi == 0 and j == 0) or (gi == 1 and j == 1)
                cc = (RED if gi == 0 else BLUE_HI) if hot else col
                c.rectangle(x0, yy, w * v / 30 * k, bh); c.set_source_rgba(*cc, 0.88 * ga); c.fill()
                text(c, who, x0 + 14, yy + 37, 24, BG, ga * min(1, k * 2) * (1 if w * v / 30 * k > 80 else 0), bold=True)
                text(c, f"{v * k:.1f}%", x0 + w * v / 30 * k + 16, yy + 39, 32, cc, ga * min(1, k * 2), bold=True)
        kx = ramp(t, T[1] + 2.2, T[1] + 3.0)
        text(c, "≈ 10 ×", x0 + w * 27.6 / 30 - 40, 300, 40, RED, ga * kx, align="c", bold=True)
        text(c, "占各自全部伤病的比例", x0, 860, 22, DIM, ga, align="l")
    # mean days between injuries
    ma = a_in * ramp(t, T[3], T[3] + 0.7)
    if ma > 0:
        for cx, who, v, col in ((W / 2 - 300, "单板", 345, BRD_C), (W / 2 + 300, "双板", 400, SKI_C)):
            k = ease_io((t - T[3] - 0.3) / 1.4)
            text(c, who, cx, 360, 40, col, ma, align="c", bold=True)
            text(c, f"{v * k:.0f}", cx, 560, 150, INK, ma, align="c", bold=True)
            text(c, "个滑雪日 / 一次伤", cx, 630, 28, DIM, ma, align="c")
        text(c, "<", W / 2, 540, 90, GOLD, ma * ramp(t, T[3] + 2.0, T[3] + 2.6), align="c", bold=True)
    chapter_tag(c, "18 个雪季", "佛蒙特 · 雪场诊所 · 病例对照", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "Am J Sports Med · 2012", "单板手腕 27.6% · 双板前十字韧带 17.2%", "Kim · Endres · Johnson · Ettlinger · Shealy",
              ramp(t, T[0] + 0.6, T[0] + 1.4) * a_in)
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3  ranking of body parts (review)
S3_SUBS = seq(["再看一篇综述：把多项研究汇总，单板受伤的部位排行是这样的——",
               "手腕{r|23%}，排第一；脚踝16.7%；膝盖16.3%。",
               "后面是头部9.2%，肩膀8.3%。",
               "和双板相比，单板{w|上肢和脚踝}伤得更多，膝盖伤得更少。"])
S3_DUR = end_of(S3_SUBS) + 0.8
ROWS3 = [("手腕", 23.0, RED, "wrist"), ("脚踝", 16.7, GOLD, "ankle"), ("膝盖", 16.3, BLUE_HI, "knee"),
         ("头部", 9.2, ICE, "head"), ("肩膀", 8.3, ICE, "shoulder")]


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S3_DUR - 0.6, S3_DUR))
    T = [a for _, a, _ in S3_SUBS]
    st = [T[1], T[1] + 1.9, T[1] + 3.4, T[2], T[2] + 1.4]
    spots = []
    for (lab, v, col, sp), s0 in zip(ROWS3, st):
        k = ramp(t, s0, s0 + 0.8)
        spots += [(sp, k * v / 23, col), (sp + "_r" if sp != "head" else sp, k * v / 23 * 0.8, col)]
    body_map(c, 470, 880, 360, spots, a_in)
    x0, y0, w = 900, 290, 760
    for i, ((lab, v, col, _), s0) in enumerate(zip(ROWS3, st)):
        k = ease_io((t - s0) / 0.8)
        if k <= 0:
            continue
        a = a_in * min(1, k * 2); y = y0 + i * 96
        text(c, lab, x0 - 24, y + 44, 34, INK, a, align="r", bold=True)
        c.rectangle(x0, y, w * v / 25 * k, 62); c.set_source_rgba(*col, 0.85 * a); c.fill()
        text(c, f"{v * k:.1f}%", x0 + w * v / 25 * k + 16, y + 46, 34, col, a, bold=True)
    ka = a_in * ramp(t, T[3], T[3] + 0.8)
    if ka > 0:
        for i, (s_, col) in enumerate((("上肢 ↑", RED), ("脚踝 ↑", GOLD), ("膝盖 ↓", BLUE_HI))):
            pill_label(c, f"比双板 {s_}", x0 + 120 + i * 230, y0 + 5 * 96 + 50, 26, col, ka)
    chapter_tag(c, "部位排行", "单板受伤部位 · 多项研究汇总", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "Am Fam Physician · 1999 · 综述", "单板：手腕、脚踝多，膝盖少", "Young · Niedfeldt", ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    model_note(c, a_in, "综述汇总表 · 各研究人群与统计口径不同")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4  why the wrist / why not the knee
S4_SUBS = seq(["为什么偏偏是手腕？因为单板的两只脚，绑在{w|同一块板}上。",
               "失去平衡时，脚迈不出去，人只能整个往后坐，或者往前扑。",
               "这一瞬间，人会本能地伸手撑地——冲击集中到{r|一只手腕}上。",
               "膝盖反倒被保护了：双板的每只板都是一根长杠杆，能把小腿往外拧；",
               "单板两脚一起固定在板上，这种扭转就很难发生。"])
S4_DUR = end_of(S4_SUBS) + 0.8


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S4_DUR - 0.6, S4_DUR))
    T = [a for _, a, _ in S4_SUBS]
    gy = 780
    pa = a_in * (1 - ramp(t, T[3] - 0.3, T[3] + 0.3))
    if pa > 0:
        ground(c, gy, pa)
        # top view of the board (first line), then the falls
        ba = pa * ramp(t, T[0] + 0.8, T[0] + 1.5) * (1 - ramp(t, T[1] - 0.2, T[1] + 0.3))
        if ba > 0:
            board_top(c, W / 2, 470, 620, ba, lock=ramp(t, T[0] + 1.6, T[0] + 2.4))
            text(c, "两只脚  ·  同一块板", W / 2, 330, 40, GOLD, ba, align="c", bold=True)
        ra = pa * ramp(t, T[1] - 0.2, T[1] + 0.4)
        if ra > 0:
            # left: heel-side fall (sit back); right: toe-side fall (forward)
            kb = ease_io((t - T[1] - 0.6) / 1.2); kf = ease_io((t - T[1] - 1.8) / 1.2)
            mk = ramp(t, T[2] + 1.0, T[2] + 1.8)
            wob = 0.04 * math.sin(t * 6) * (1 - kb)
            pb = rider_profile(c, 720, gy, 300, back=kb, wrist_mark=mk, alpha=ra, wobble=wob)
            pf = rider_profile(c, 1180, gy, 300, fwd=kf, wrist_mark=mk, alpha=ra)
            text(c, "后刃摔：往后坐", 620, 300, 32, INK, ra * ramp(t, T[1] + 0.8, T[1] + 1.4), align="c", bold=True)
            text(c, "前刃摔：往前扑", 1320, 300, 32, INK, ra * ramp(t, T[1] + 2.0, T[1] + 2.6), align="c", bold=True)
            if mk > 0:
                for p in (pb["wrist"], pf["wrist"]):
                    arrow(c, p[0], p[1] + 150, p[0], p[1] + 30, RED, ra * mk, 5, 20)
                text(c, "冲击 → 手腕", W / 2, 420, 40, RED, ra * mk, align="c", bold=True)
    # knee: ski lever vs locked board
    ka = a_in * ramp(t, T[3] - 0.1, T[3] + 0.5)
    if ka > 0:
        cy = 520
        # skis: one ski swings out around the boot -> twisting arrow
        k = ramp(t, T[3] + 1.4, T[3] + 2.6)
        sw = 0.38 * ease_io(k) * (0.8 + 0.2 * math.sin(t * 3))
        cx = 560
        for i, (dy, rot) in enumerate(((-55, 0.0), (55, sw))):
            c.save(); c.translate(cx, cy + dy); c.rotate(rot)
            rounded_rect(c, -300, -16, 600, 32, 14); c.set_source_rgba(*mix((0.16, 0.17, 0.21), GOLD, 0.3), ka); c.fill_preserve()
            c.set_source_rgba(*GOLD, 0.85 * ka); c.set_line_width(2); c.stroke()
            rounded_rect(c, -50, -24, 100, 48, 10); c.set_source_rgba(0.30, 0.34, 0.42, ka); c.fill()
            c.restore()
        if k > 0:
            c.new_path(); c.arc(cx, cy + 55, 330, 0.05, 0.05 + sw); c.set_source_rgba(*RED, 0.9 * ka * k); c.set_line_width(5); c.stroke()
            ex, ey = cx + 330 * math.cos(0.05 + sw), cy + 55 + 330 * math.sin(0.05 + sw)
            arrow_head(c, ex, ey, 0.05 + sw + math.pi / 2, 22, RED, ka * k)
            text(c, "长杠杆 → 拧膝盖", cx, cy + 300, 36, RED, ka * k, align="c", bold=True)
        text(c, "双板：两只脚各自一根杠杆", cx, cy - 170, 32, INK, ka, align="c", bold=True)
        b = ka * ramp(t, T[4] - 0.2, T[4] + 0.5)
        board_top(c, 1360, cy, 560, b, lock=ramp(t, T[4] + 0.4, T[4] + 1.2))
        text(c, "单板：两脚锁在一起", 1360, cy - 170, 32, INK, b, align="c", bold=True)
        text(c, "很难单独拧一条腿", 1360, cy + 300, 36, ICE, b * ramp(t, T[4] + 1.0, T[4] + 1.8), align="c", bold=True)
    chapter_tag(c, "为什么", "双脚固定 · 摔倒方式 · 杠杆", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "示意 · 通俗解释，非受力计算")
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5  meta-analysis 2025
S5_SUBS = seq(["2025年的一项荟萃分析，汇总了77项研究、七十六万多名伤者。",
               "上肢伤占全部受伤的比例：单板{r|26%}，双板18%。",
               "单板的上肢伤里，{r|手腕}最多，占36%；双板的上肢伤，最多的却是{b|肩膀}，占37%。"])
S5_DUR = end_of(S5_SUBS) + 0.8


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S5_DUR - 0.6, S5_DUR))
    T = [a for _, a, _ in S5_SUBS]
    # dot matrix: 77 studies
    da = a_in * (1 - ramp(t, T[1] - 0.2, T[1] + 0.3))
    if da > 0:
        dot_matrix(c, W / 2 - 13 * 38 / 2 + 19, 330, 77, 14, 40, 13, lambda i: ICE, da, ramp(t, T[0] + 0.3, T[0] + 2.8))
        text(c, "77 项研究", W / 2, 640, 48, INK, da, align="c", bold=True)
        text(c, "764,423 名伤者", W / 2, 700, 32, DIM, da * ramp(t, T[0] + 2.0, T[0] + 2.8), align="c")
    # two vertical bars
    va = a_in * ramp(t, T[1] - 0.1, T[1] + 0.5) * (1 - ramp(t, T[2] - 0.2, T[2] + 0.3))
    if va > 0:
        for i, (who, v, col) in enumerate((("单板", 26, RED), ("双板", 18, SKI_C))):
            k = ease_io((t - T[1] - 0.4 - i * 0.5) / 1.0)
            bx = W / 2 - 230 + i * 300; base = 800; hh = 480 * v / 30 * k
            c.rectangle(bx, base - 480 * 100 / 30 * 0 - 480, 160, 480); c.set_source_rgba(*FAINT, 0.18 * va); c.fill()
            c.rectangle(bx, base - hh, 160, hh); c.set_source_rgba(*col, 0.9 * va); c.fill()
            text(c, f"{v * k:.0f}%", bx + 80, base - hh - 20, 56, col, va, align="c", bold=True)
            text(c, who, bx + 80, base + 50, 34, INK, va, align="c", bold=True)
        text(c, "上肢伤 / 全部伤", W / 2, 250, 30, DIM, va, align="c")
    # body maps: wrist vs shoulder
    ba = a_in * ramp(t, T[2] - 0.1, T[2] + 0.5)
    if ba > 0:
        kw = ramp(t, T[2] + 0.6, T[2] + 1.4); ks = ramp(t, T[2] + 3.2, T[2] + 4.0)
        for cx, who, sp, kk, col, lab in ((640, "单板", "wrist", kw, RED, "手腕 36%"), (1280, "双板", "shoulder", ks, BLUE_HI, "肩膀 37%")):
            body_map(c, cx, 820, 300, [(sp, kk, col), (sp + "_r", kk * 0.8, col)], ba)
            text(c, who, cx, 900, 36, INK, ba, align="c", bold=True)
            text(c, lab, cx, 250, 50, col, ba * kk, align="c", bold=True)
        text(c, "上肢伤里最多的部位", W / 2, 180, 26, DIM, ba, align="c")
    chapter_tag(c, "76 万人", "荟萃分析 · 77 项研究 · 1939–2024", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "Shoulder & Elbow · 2025 · 荟萃分析", "单板上肢伤以手腕为主，双板以肩为主", "Chauffard · Traverso · Vauclair 等",
              ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    subs(c, t, S5_SUBS)
    overlays(c, fi)


# ================================================================== S6  beginners
S6_SUBS = seq(["还有一个规律：伤，最集中在刚开始的那几天。",
               "一项针对单板初学者的前瞻研究：{r|35%}的受伤发生在前4天，{r|51%}在第一周之内。",
               "苏格兰的一项研究发现：伤者里，第一天上雪的人是正常比例的{r|2.2倍}。",
               "佛蒙特的数据也一样：受伤率最高的，是年轻、经验少的女性单板滑手。"])
S6_DUR = end_of(S6_SUBS) + 0.8


def s6(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S6_DUR - 0.6, S6_DUR))
    T = [a for _, a, _ in S6_SUBS]
    # cumulative bar: share of all injuries by experience
    ca = a_in * ramp(t, T[0] + 0.3, T[0] + 1.0) * (1 - ramp(t, T[2] - 0.2, T[2] + 0.3))
    if ca > 0:
        x0, x1, y = 260, 1660, 470
        wd = x1 - x0
        c.rectangle(x0, y, wd, 90); c.set_source_rgba(*FAINT, 0.35 * ca); c.fill()
        k1 = ease_io((t - T[1] - 1.0) / 1.0); k2 = ease_io((t - T[1] - 3.2) / 1.0)
        c.rectangle(x0, y, wd * 0.35 * k1, 90); c.set_source_rgba(*RED, 0.9 * ca); c.fill()
        c.rectangle(x0 + wd * 0.35, y, wd * 0.16 * k2, 90); c.set_source_rgba(*mix(RED, GOLD, 0.5), 0.8 * ca); c.fill()
        for f, lab, kk, ly in ((0.35, "前 4 天  35%", k1, y - 50), (0.51, "第 1 周  51%", k2, y + 160)):
            if kk > 0:
                xx = x0 + wd * f
                c.set_source_rgba(*INK, 0.8 * ca * kk); c.rectangle(xx - 1.5, min(ly, y) - 10 if ly < y else y, 3, 120 if ly > y else 100); c.fill()
                text(c, lab, xx, ly + (10 if ly > y else 0), 38, INK, ca * kk, align="c", bold=True)
        text(c, "全部受伤 = 100%", x1, y + 130, 26, DIM, ca, align="r")
        text(c, "初学者的受伤，按发生时间累计", x0, y + 130, 26, DIM, ca)
    # 2.2x
    xa = a_in * ramp(t, T[2] + 0.3, T[2] + 0.9) * (1 - ramp(t, T[3] - 0.2, T[3] + 0.3))
    if xa > 0:
        k = ease_io((t - T[2] - 0.6) / 1.4)
        text(c, f"{1 + 1.2 * k:.1f} ×", W / 2, 560, 180, RED, xa, align="c", bold=True)
        text(c, "第一天上雪的人，在伤者中的占比（相对正常比例）", W / 2, 650, 30, DIM, xa, align="c")
    # highest-risk group
    ha = a_in * ramp(t, T[3] - 0.1, T[3] + 0.5)
    if ha > 0:
        for i, s_ in enumerate(("年轻", "经验少", "女性", "单板")):
            pill_label(c, s_, W / 2 - 390 + i * 260, 520, 44, (RED, GOLD, ICE, ICE)[i], ha * ramp(t, T[3] + 0.5 + i * 0.5, T[3] + 1.0 + i * 0.5))
        text(c, "受伤率最高的人群", W / 2, 420, 34, DIM, ha, align="c")
    chapter_tag(c, "前几天", "初学期 · 受伤最集中", ramp(t, 0.5, 1.1) * a_in)
    if t < T[2]:
        cite_card(c, "J Trauma · 2000 · 前瞻研究", "35% 在前 4 天，51% 在第一周", "Machold · Kwasny · Gassler 等",
                  ramp(t, T[1], T[1] + 0.8) * a_in * (1 - ramp(t, T[2] - 0.5, T[2])))
    elif t < T[3]:
        cite_card(c, "Wilderness Environ Med · 2004", "第一天的人在伤者中多出 2.2 倍", "Langran · Selvaraj",
                  ramp(t, T[2], T[2] + 0.6) * a_in * (1 - ramp(t, T[3] - 0.5, T[3])))
    else:
        cite_card(c, "Am J Sports Med · 2012", "年轻、经验少的女性单板滑手受伤率最高", "Kim · Endres · Johnson 等", ramp(t, T[3], T[3] + 0.6) * a_in)
    subs(c, t, S6_SUBS)
    overlays(c, fi)


# ================================================================== S7  what to do + end
S7_SUBS = seq(["所以对单板来说，最值得做的三件事：",
               "第一，{w|戴护腕}——手腕伤排第一。",
               "第二，学会摔：别直着胳膊撑地，往前跪，往后坐、顺势滚。",
               "第三，前几天别硬冲，找个教练。",
               "护腕到底能防住多少？下一集，用数据说话。"])
S7_DUR = end_of(S7_SUBS) + 4.0


def s7(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S7_DUR - 1.4, S7_DUR - 0.4))
    T = [a for _, a, _ in S7_SUBS]
    la = a_in * (1 - ramp(t, T[4] - 0.2, T[4] + 0.4))
    items = [("1", "戴护腕", "手腕伤排第一", T[1]), ("2", "学会摔", "不直臂撑地 · 前跪后坐 · 顺势滚", T[2]), ("3", "前几天找教练", "受伤集中在第一周", T[3])]
    for i, (n, big, small, ts) in enumerate(items):
        k = ramp(t, ts, ts + 0.6)
        if k <= 0:
            continue
        y = 300 + i * 170; a = la * k; x = 520 - 40 * (1 - ease(k))
        c.arc(x, y, 50, 0, 2 * math.pi); c.set_source_rgba(*GOLD, 0.9 * a); c.fill()
        text(c, n, x, y + 20, 56, BG, a, align="c", bold=True)
        text(c, big, x + 100, y + 16, 60, INK, a, bold=True)
        text(c, small, x + 100, y + 66, 28, DIM, a)
    ea = a_in * ramp(t, T[4], T[4] + 0.8)
    if ea > 0:
        text(c, "下一集", W / 2, 320, 34, DIM, ea, align="c", spacing=0.3)
        text(c, "护腕到底有没有用？", W / 2, 440, 84, INK, ea, align="c", bold=True)
        c.set_source_rgba(*GOLD, 0.8 * ea); c.rectangle(W / 2 - 160, 486, 320, 2); c.fill()
        text(c, SERIES, W / 2, 560, 30, GOLD, ea, align="c", spacing=0.3)
    subs(c, t, S7_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, S7_DUR - 1.0, S7_DUR))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR),
          ("s5", s5, S5_DUR), ("s6", s6, S6_DUR), ("s7", s7, S7_DUR)]


def _cover_fig(c):
    c.rectangle(-300, 760, 1600, 300); c.set_source_rgb(*TERRAIN); c.fill()
    c.set_source_rgba(*RIM, 0.9); c.rectangle(-300, 758, 1600, 3); c.fill()
    body_map(c, 270, 760, 360, [("wrist", 1.0, RED), ("wrist_r", 0.8, RED), ("ankle", 0.35, GOLD), ("ankle_r", 0.3, GOLD),
                                ("knee", 0.15, BLUE_HI), ("knee_r", 0.12, BLUE_HI)])
    rider_profile(c, 820, 760, 300, back=1.0, wrist_mark=1.0)


COVER = dict(lines=["单板", "最常伤哪里？"], stat="27.6%", caption="手腕占单板伤病的比例（双板仅 2.8%）", color=RED, figure=_cover_fig)
COVER2 = dict(kicker="单板 · 用数据说话", lines=[("单板", "ink"), ("最常伤哪里", "gold")], sub="手腕占 27.6% · 双板只有 2.8%", motif="track", seed=1)
