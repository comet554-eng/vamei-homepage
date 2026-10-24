"""EP.02《外脚到底该压多少？》"""
import math
from common import *
from art import *

SERIES = "双板 · 用数据说话"
TITLE = "外脚到底该压多少？"


def subs(c, t, S):
    for s, a, b in S:
        subtitle(c, s, t, a, b)


def ground(c, gy, a):
    c.rectangle(0, gy, W, H - gy); c.set_source_rgba(*TERRAIN, a); c.fill()
    c.set_source_rgba(*RIM, 0.9 * a); c.rectangle(0, gy - 1.5, W, 3); c.fill()


# ================================================================== S1
S1_SUBS = seq(["教练常说：转弯的时候，重心要{w|全在外脚}。",
               "那外脚到底该压多少？百分之百吗？",
               "研究者在滑雪者的脚下装上测力板和压力鞋垫，把它量了出来。"])
S1_DUR = end_of(S1_SUBS) + 5.0


def s1(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.8)
    gy = 800
    ground(c, gy, a_in)
    sway = math.sin(t * 0.9)
    skier_front(c, 760, gy, 300, lean=math.radians(12 * sway), out_edge=math.radians(30), in_edge=math.radians(25), alpha=a_in)
    T = [a for _, a, _ in S1_SUBS]
    q = ramp(t, T[1], T[1] + 0.6)
    load_bars(c, 1240, 700, 1.0, a_in * q)
    if q > 0:
        text(c, "？", 1500, 560, 90, RED, a_in * q, bold=True)
    te = end_of(S1_SUBS)
    ta = ramp(t, te + 0.3, te + 1.2) * (1 - ramp(t, S1_DUR - 0.7, S1_DUR))
    if ta > 0:
        c.set_source_rgba(*BG, 0.85 * ta); c.paint()
        text(c, SERIES, W / 2, 380, 30, DIM, ta, align="c", spacing=0.3)
        text(c, TITLE, W / 2, 510, 92, INK, ta, align="c", bold=True)
        c.set_source_rgba(*GOLD, 0.8 * ta); c.rectangle(W / 2 - 160, 556, 320, 2); c.fill()
        text(c, "测力板 · 压力鞋垫 · 模型研究", W / 2, 620, 32, GOLD, ta, align="c")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2  the numbers
S2_SUBS = seq(["把几项研究放在一起，看外脚承担的比例——",
               "三维测力：外脚约 1800 牛，内脚约 800 牛——{w|69%}。",
               "精英滑手，压力鞋垫：左弯 65%，右弯 60%。",
               "普通平行转弯：78%；滑雪学校的教学动作：内外约 1:4，也就是 80%。",
               "而一项模型研究里，{r|初学者是 99%}——几乎全压在外脚上。",
               "高手反而{b|没有全压外脚}：大约六到八成。",
               ("（各研究方法不同：压力鞋垫会低估受力，内脚低估得更多，数字不能直接横向比较）", 5.0)])
S2_DUR = end_of(S2_SUBS) + 0.8
ROWS2 = [("三维测力", 69, GOLD, "1800 N : 800 N"), ("精英 · 左弯", 65, ICE, "压力鞋垫"), ("精英 · 右弯", 60, ICE, "压力鞋垫"),
         ("平行转弯", 78, GOLD, "压力鞋垫"), ("滑雪学校", 80, GOLD, "内外约 1:4"), ("模型 · 中级", 80, DIM, "模型研究"),
         ("模型 · 初学者", 99, RED, "模型研究")]


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S2_DUR - 0.6, S2_DUR))
    T = [a for _, a, _ in S2_SUBS]
    starts = [T[1], T[2], T[2] + 0.6, T[3], T[3] + 0.8, T[4], T[4] + 0.6]
    x0, y0, w = 560, 240, 900
    # 100 % reference and 60–80 % band
    ba = a_in * ramp(t, T[5], T[5] + 0.8)
    c.rectangle(x0 + w * 0.6, y0 - 20, w * 0.2, 7 * 82 + 10); c.set_source_rgba(*ICE, 0.10 * ba); c.fill()
    text(c, "高手区间 60–80%", x0 + w * 0.7, y0 - 32, 22, ICE, ba, align="c", bold=True)
    c.set_dash([6, 6]); c.set_source_rgba(*DIM, 0.6 * a_in); c.set_line_width(1.5)
    c.move_to(x0 + w, y0 - 20); c.line_to(x0 + w, y0 + 7 * 82); c.stroke(); c.set_dash([])
    text(c, "100%", x0 + w, y0 + 7 * 82 + 30, 20, DIM, a_in, align="c")
    for i, (lab, v, col, note) in enumerate(ROWS2):
        k = ease_io((t - starts[i]) / 0.8)
        if k <= 0:
            continue
        y = y0 + i * 82
        a = a_in * min(1, k * 2)
        text(c, lab, x0 - 20, y + 40, 26, INK, a, align="r", bold=True)
        c.rectangle(x0, y, w * v / 100 * k, 56); c.set_source_rgba(*col, 0.85 * a); c.fill()
        text(c, f"{v * k:.0f}%", x0 + 14, y + 40, 28, BG, a, bold=True)
        text(c, note, x0 + w + 24, y + 38, 20, DIM, a)
    chapter_tag(c, "外脚占比", "各研究测得的外脚负重比例", ramp(t, 0.6, 1.2) * a_in)
    cite_card(c, "arXiv:2411.08056 · 综述", "外脚 60–80% 是合理平衡；初学者 99%", "Stricker · Ogrin · Bon 等（转引）", ramp(t, T[1], T[1] + 0.8) * a_in)
    model_note(c, a_in, "不同方法不可直接比较 · 鞋垫低估内脚约 54%、外脚约 21%")
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3  why outside ski / three cases
S3_SUBS = seq(["为什么外脚是主力？",
               "外脚那块板立在刃上、被压弯——是它在{w|切出这个弯}。",
               "内脚也在干活：帮着保持平衡，跟着一起立刃。",
               "要是全压外脚、内腿完全不用力，身体容易僵直，被弯甩出去；",
               "要是两脚平均分，外板压不住，容易打滑。",
               "最危险的，是外脚压力突然没了：外板滑开、再猛地咬雪——\n这就是上一集讲的 {r|slip-catch}。"])
S3_DUR = end_of(S3_SUBS) + 0.8


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S3_DUR - 0.6, S3_DUR))
    T = [a for _, a, _ in S3_SUBS]
    gy = 800
    ground(c, gy, a_in)
    # states per sentence
    if t < T[3]:
        outer, stiff, slide, lean, val, lab, col = 0.7, 0.0, 0.0, 14, 0.0, "外脚为主 · 内脚帮忙", GOLD
    elif t < T[4]:
        outer, stiff, slide, lean, val, lab, col = 1.0, 1.0, 0.0, 6, 0.0, "全压外脚 · 内腿僵直", RED
    elif t < T[5]:
        outer, stiff, slide, lean, val, lab, col = 0.5, 0.0, 0.12 * ramp(t, T[4] + 0.6, T[4] + 2.0), 14, 0.0, "平均分 · 外板打滑", RED
    else:
        sl = 0.3 * ease_io((t - T[5]) / 1.6) * (1 - 0.5 * ramp(t, T[5] + 2.2, T[5] + 2.5))
        val = ramp(t, T[5] + 2.2, T[5] + 3.0)
        outer = lerp(0.2, 0.9, ramp(t, T[5] + 2.2, T[5] + 2.5))
        stiff, slide, lean, lab, col = 0.0, sl, 12, "外脚压力消失 → 突然咬雪", RED
    skier_front(c, 760, gy, 300, lean=math.radians(lean), out_edge=math.radians(40), in_edge=math.radians(30), out_slide=slide,
                valgus=val, knee_mark=val, stiff=stiff, alpha=a_in)
    if T[1] < t < T[3]:
        c.arc(760 + 0.25 * 300, gy - 20, 60, 0, 2 * math.pi); c.set_source_rgba(*GOLD, 0.6 * a_in * ramp(t, T[1], T[1] + 0.5)); c.set_line_width(3); c.stroke()
    load_bars(c, 1300, 700, outer, a_in)
    pill_label(c, lab, 1390, 260, 30, col, a_in * ramp(t, 0.6, 1.2))
    chapter_tag(c, "为什么", "外板切弯 · 内板帮忙", ramp(t, 0.6, 1.2) * a_in)
    model_note(c, a_in, "示意 · 正面视角，向画面左侧转弯")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4  practice
S4_SUBS = seq(["所以目标不是“全压”，而是{w|外脚为主、内脚帮忙}：大约七三开。",
               "一个练习：在缓坡上转弯时，轻轻把内脚的板尾抬起一点——",
               "抬得起来，说明外脚在承重；完全不敢抬，说明重心还压在内脚上。",
               ("（练习为常见教学方法；比例为各研究的大致范围）", 4.0)])
S4_DUR = end_of(S4_SUBS) + 0.8


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S4_DUR - 0.6, S4_DUR))
    T = [a for _, a, _ in S4_SUBS]
    gy = 800
    ground(c, gy, a_in)
    lift = 0.12 * ramp(t, T[1] + 1.0, T[1] + 2.0) * (0.6 + 0.4 * math.sin(t * 2.5))
    outer = 0.7 if t < T[1] + 1.0 else lerp(0.7, 0.95, ramp(t, T[1] + 1.0, T[1] + 2.0))
    skier_front(c, 760, gy, 300, lean=math.radians(14), out_edge=math.radians(35), in_edge=math.radians(30), inner_lift=lift, alpha=a_in)
    load_bars(c, 1300, 700, outer, a_in)
    pill_label(c, "七三开", 1390, 260, 34, GOLD, a_in * ramp(t, 0.6, 1.2) * (1 - ramp(t, T[1], T[1] + 0.4)))
    pill_label(c, "练习：抬内脚板尾", 1390, 260, 30, ICE, a_in * ramp(t, T[1], T[1] + 0.6))
    chapter_tag(c, "七三开", "外脚为主 · 内脚帮忙", ramp(t, 0.6, 1.2) * a_in)
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5  end
S5_SUBS = seq(["外脚为主，内脚帮忙——高手的脚下，从来不是百分之百。"])
S5_DUR = end_of(S5_SUBS) + 4.0


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S5_DUR - 1.4, S5_DUR - 0.4))
    gy = 760
    snow_ground(c, gy, t, 480, a_in)
    skier(c, 760, gy, 150, 0.35 + 0.05 * math.sin(t * 2), a_in, t * 2.5)
    ea = ramp(t, end_of(S5_SUBS) - 1.0, end_of(S5_SUBS)) * a_in
    text(c, SERIES, W / 2, 300, 30, DIM, ea, align="c", spacing=0.3)
    text(c, TITLE, W / 2, 400, 60, INK, ea, align="c", bold=True)
    subs(c, t, S5_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, S5_DUR - 1.0, S5_DUR))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR)]


def _cover_fig(c):
    c.rectangle(-200, 700, 1400, 300); c.set_source_rgb(*TERRAIN); c.fill()
    c.set_source_rgba(*RIM, 0.9); c.rectangle(-200, 698, 1400, 3); c.fill()
    skier_front(c, 330, 700, 330, lean=math.radians(14), out_edge=math.radians(35), in_edge=math.radians(30))
    load_bars(c, 680, 600, 0.7, 1.0, h=380, w=90)


COVER = dict(lines=["外脚到底", "该压多少？"], stat="60–80%", caption="高手外脚的负重比例（多项研究）", color=GOLD, figure=_cover_fig)
