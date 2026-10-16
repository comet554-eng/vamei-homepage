"""单板 EP.08《鸭子站还是前倾站？》 (no voice-over)"""
import math
from common import *
from art import *
from board import *

SERIES = SERIES_B
TITLE = "鸭子站还是前倾站？"
BOOT = 31.0      # boot length, cm (示意)
WAIST = 25.0     # board waist width, cm (示意)

# ================================================================== S1 hook
S1_SUBS = seq(["单板的固定器能转角度，每个人调得都不一样：",
               "有人两只脚往外八，像只鸭子；有人两只脚都朝着板头。",
               "角度到底怎么选？这一集，看几何，也看实验。"], t0=0.8)
S1_DUR = end_of(S1_SUBS) + 4.6


def s1(c, t, fi):
    paint_bg(c)
    a = ramp(t, 0, 0.8)
    T = [x for _, x, _ in S1_SUBS]
    kd = ramp(t, T[1] - 0.2, T[1] + 1.0); kf = ramp(t, T[1] + 1.6, T[1] + 2.6)
    board_top(c, W / 2, 380, 760, a, angles=(15 * kd, -15 * kd))
    board_top(c, W / 2, 640, 760, a * kf, angles=(45, 30))
    text(c, "鸭子站", W / 2, 250, 40, ICE, a * kd, align="c", bold=True)
    text(c, "前倾站", W / 2, 790, 40, GOLD, a * kf, align="c", bold=True)
    title_card(c, t, end_of(S1_SUBS) + 0.2, S1_DUR, TITLE, "常见设置 · 鞋与板边的几何 · 膝盖实验")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2 typical settings
S2_SUBS = seq(["常见的设置大致两类。",
               "玩公园、平花、经常反脚滑的人，多用小角度：前脚十几度，后脚调成负的——两脚外八，这就是{w|鸭子站}；",
               "刻滑、竞速的人，前脚常调到{w|40到60度}，后脚也朝前——两脚都对着板头，这是{w|前倾站}。",
               "角度从0到60度，人的身体也从“侧对坡下”，慢慢转成“面朝前方”。"])
S2_DUR = end_of(S2_SUBS) + 0.8


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S2_DUR - 0.6, S2_DUR))
    T = [x for _, x, _ in S2_SUBS]
    k1 = ease_io((t - T[1]) / 1.4); k2 = ease_io((t - T[2]) / 1.4)
    fa = 15 * k1 + (50 - 15) * k2; ra = -9 * k1 + (40 + 9) * k2
    board_top(c, W / 2, 470, 900, a_in, angles=(fa, ra))
    text(c, f"前脚 {fa:+.0f}°", W / 2 + 230, 300, 44, GOLD, a_in, align="c", bold=True)
    text(c, f"后脚 {ra:+.0f}°", W / 2 - 230, 300, 44, ICE, a_in, align="c", bold=True)
    lab = "鸭子站" if k2 < 0.5 else "前倾站"
    text(c, lab, W / 2, 680, 50, INK, a_in * ramp(t, T[1] + 1.0, T[1] + 1.6), align="c", bold=True)
    chapter_tag(c, "常见设置", "自由式 vs 刻滑", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "示意 · 常见范围，具体因人而异")
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3 geometry: boot overhang vs angle
S3_SUBS = seq(["角度还决定了一件事：鞋会不会伸出板边。",
               "拿一只31厘米长的鞋算：横着放、0度时，它在板宽方向占{w|31厘米}；",
               "转到15度，30厘米；30度，26.8厘米；45度，只剩{b|21.9厘米}。",
               "一块腰宽25厘米的板，0度时鞋两头各伸出3厘米；转到45度，就完全收在板里了。",
               "所以刻滑的人爱用大角度——立刃时不容易拖靴，这正是上上集讲的限制。"])
S3_DUR = end_of(S3_SUBS) + 0.8


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S3_DUR - 0.6, S3_DUR))
    T = [x for _, x, _ in S3_SUBS]
    ang = 0.0
    for deg, ts in ((15, T[2]), (30, T[2] + 2.2), (45, T[2] + 4.2)):
        ang = ang + (deg - ang) * ease_io((t - ts) / 0.8) if t > ts else ang
    k = 22                                              # px per cm
    cx, cy = 620, 520
    # board strip (top view, width = waist)
    c.rectangle(cx - 360, cy - WAIST * k / 2, 720, WAIST * k); c.set_source_rgba(*mix(BOARD, GOLD, 0.25), a_in); c.fill()
    c.set_source_rgba(*GOLD, 0.9 * a_in); c.set_line_width(3)
    c.move_to(cx - 360, cy - WAIST * k / 2); c.line_to(cx + 360, cy - WAIST * k / 2); c.stroke()
    c.move_to(cx - 360, cy + WAIST * k / 2); c.line_to(cx + 360, cy + WAIST * k / 2); c.stroke()
    # boot
    c.save(); c.translate(cx, cy); c.rotate(math.radians(90 - ang) - math.pi / 2 * 0 + math.pi / 2 * 0)
    c.rotate(-math.pi / 2 + math.radians(90) - math.radians(ang) * 0)
    c.restore()
    c.save(); c.translate(cx, cy); c.rotate(math.radians(-ang))
    rounded_rect(c, -4.5 * k, -BOOT * k / 2, 9 * k, BOOT * k, 3 * k)
    c.set_source_rgba(0.30, 0.34, 0.42, 0.95 * a_in); c.fill()
    c.restore()
    span = BOOT * math.cos(math.radians(ang)) + 9 * math.sin(math.radians(ang)) * 0
    over = max(0.0, (span - WAIST) / 2)
    if over > 0:
        for sgn in (-1, 1):
            c.rectangle(cx - 140, cy + sgn * WAIST * k / 2 - (over * k if sgn < 0 else 0), 280, over * k)
            c.set_source_rgba(*RED, 0.5 * a_in); c.fill()
    ra = a_in * ramp(t, T[1] - 0.2, T[1] + 0.4)
    text(c, f"{ang:.0f}°", cx, cy - WAIST * k / 2 - 110, 60, GOLD, ra, align="c", bold=True)
    text(c, f"板宽方向占 {BOOT * math.cos(math.radians(ang)):.1f} cm", 1300, 420, 46, INK, ra, align="c", bold=True)
    text(c, f"每边伸出 {over:.1f} cm" if over > 0.05 else "完全收在板内", 1300, 500, 40, RED if over > 0.05 else BLUE_HI, ra, align="c", bold=True)
    text(c, "L · cos θ", 1300, 600, 36, DIM, ra, align="c")
    pa = a_in * ramp(t, T[4], T[4] + 0.6)
    pill_label(c, "大角度 → 不易拖靴（见 EP06）", 1300, 720, 30, GOLD, pa)
    chapter_tag(c, "几何", "鞋长 × cos(角度)", ramp(t, 0.5, 1.1) * a_in)
    model_note(c, a_in, "计算值 · 鞋长 31 cm、腰宽 25 cm 为示意取值，忽略鞋宽")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4 experiment: tibial rotation
S4_SUBS = seq(["那角度会不会伤膝盖？瑞士苏黎世联邦理工的一项研究，",
               "请了{w|10名}高水平自由式滑手，在3种站距 × 2种角度、一共{w|6种}设置下，做落地测试，测小腿的旋转。",
               "结果：{w|前脚角度大一点、后脚稍微负一点}的组合，小腿的内旋更小——膝盖被拧得更少；",
               "而用Ollie测的起跳高度，6种设置之间{b|没有明显差别}。"])
S4_DUR = end_of(S4_SUBS) + 0.8


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S4_DUR - 0.6, S4_DUR))
    T = [x for _, x, _ in S4_SUBS]
    ga = a_in * ramp(t, T[1] - 0.2, T[1] + 0.5)
    if ga > 0:
        for i in range(6):
            col = i % 3; row = i // 3
            x = 480 + col * 480; y = 330 + row * 210
            k = ramp(t, T[1] + 1.0 + i * 0.3, T[1] + 1.5 + i * 0.3)
            best = (i == 4 or i == 5) and t > T[2]
            angles = ((15, -15) if row == 0 else (24, -6))
            board_top(c, x, y, 250 + 25 * col, ga * k, angles=angles, lock=1.0 if best else 0.0)
            if k > 0:
                text(c, ["窄", "中", "宽"][col] + " · " + ["鸭子站", "前脚大·后脚小负"][row], x, y + 80, 24, GOLD if best else DIM, ga * k, align="c", bold=best)
    ra = a_in * ramp(t, T[2] + 0.4, T[2] + 1.0)
    pill_label(c, "小腿内旋更小", 900, 800, 34, GOLD, ra)
    oa = a_in * ramp(t, T[3], T[3] + 0.6)
    if oa > 0:
        for i in range(6):
            h = 80 + 4 * math.sin(i * 1.7)
            c.rectangle(1460 + i * 50, 830 - h, 34, h); c.set_source_rgba(*ICE, 0.8 * oa); c.fill()
        text(c, "Ollie 高度：无显著差别", 1600, 870, 26, ICE, oa, align="c", bold=True)
    chapter_tag(c, "膝盖实验", "10 名高水平自由式滑手 · 6 种设置", ramp(t, 0.5, 1.1) * a_in)
    cite_card(c, "ISBS 2012 · 会议论文", "前脚大角度 + 后脚小负角：小腿内旋更小", "List · Bründler 等（ETH Zürich）", ramp(t, T[0] + 0.5, T[0] + 1.3) * a_in)
    model_note(c, a_in, "会议论文、小样本；测的是小腿旋转，不是受伤率；板上角度为示意")
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5 practical + end
S5_SUBS = seq(["所以没有唯一正确的角度，看你怎么滑：",
               "玩公园、常反脚滑——鸭子站，前后对称，正反都顺；",
               "爱刻滑、想立高刃——前脚角度往大调，鞋更不容易拖雪；",
               "不管哪种，调好以后蹲一下：{w|膝盖要和脚尖朝同一个方向}，别让膝盖往里扣。",
               "U型池，选手到底飞多高？下一集，用数据说话。"])
S5_DUR = end_of(S5_SUBS) + 4.0


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, S5_DUR - 1.4, S5_DUR - 0.4))
    T = [x for _, x, _ in S5_SUBS]
    la = a_in * (1 - ramp(t, T[4] - 0.2, T[4] + 0.4))
    numbered(c, [("公", "公园 / 反脚：鸭子站", "前后对称", T[1]), ("刻", "刻滑：前脚大角度", "不易拖靴", T[2]),
                 ("!", "膝盖对脚尖", "别往里扣", T[3])], t, la)
    end_card(c, a_in * ramp(t, T[4], T[4] + 0.8), "U 型池，选手到底飞多高？")
    subs(c, t, S5_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, S5_DUR - 1.0, S5_DUR))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR)]


def _cover_fig(c):
    board_top(c, 500, 270, 560, angles=(15, -15))
    board_top(c, 500, 550, 560, angles=(50, 40))
    text(c, "+15° / −15°", 500, 140, 44, ICE, align="c", bold=True)
    text(c, "+50° / +40°", 500, 700, 44, GOLD, align="c", bold=True)


COVER = dict(lines=["鸭子站", "还是前倾站？"], stat="21.9 cm", caption="31 cm 的鞋转到 45° 时在板宽方向只占这么多（计算值）", color=GOLD, figure=_cover_fig)
COVER2 = dict(kicker="单板 · 用数据说话", lines=[("鸭子站", "ice"), ("还是前倾站", "gold")], sub="一个角度，决定鞋会不会伸出板边", motif="track", seed=8)
