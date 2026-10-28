"""《雪板为什么能滑？》 scenes. Each scene: sN(c, t, fi) and duration."""
import math
import numpy as np
from common import *
from art import *
import art as A


def subs(c, t, SUBS):
    for s, a, b in SUBS:
        subtitle(c, s, t, a, b)


GR = Grains()


# ================================================================== S1  the textbook answer
S1_DUR = 18.0
S1_SUBS = [
    ("雪板为什么能在雪上滑？", 0.6, 3.8),
    ("很多课本里的答案是：人把雪{w|压化了}，\n板子踩在一层水上。", 4.1, 9.0),
    ("这个说法流传很广。我们来算一算。", 9.3, 12.2),
]


def claim_card(c, cx, cy, a, cross=0.0):
    if a <= 0:
        return
    items = ["压力", "冰融化", "水膜", "板变滑"]
    w = 210
    x = cx - (len(items) * w + (len(items) - 1) * 50) / 2
    for i, s in enumerate(items):
        ai = a * ramp(a * 10, i * 1.2, i * 1.2 + 1.5) if a < 1 else a
        rounded_rect(c, x, cy - 46, w, 80, 12)
        c.set_source_rgba(0.04, 0.05, 0.07, 0.85 * ai); c.fill_preserve()
        c.set_source_rgba(*GOLD, 0.6 * ai); c.set_line_width(1.5); c.stroke()
        text(c, s, x + w / 2, cy + 6, 34, INK, ai, align="c", bold=True)
        if i < len(items) - 1:
            arrow(c, x + w + 8, cy - 6, x + w + 42, cy - 6, DIM, ai, 2, 12)
        x += w + 50
    if cross > 0:
        text(c, "？", cx + 470, cy + 18, 80, RED, cross, align="c", bold=True)


def s1(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.8)
    gy = 760
    snow_ground(c, gy, t, 520, a_in)
    skier(c, 760, gy, 150, 0.35 + 0.05 * math.sin(t * 2), a_in, t * 2.5)
    # track behind the ski
    c.set_source_rgba(*RIM, 0.25 * a_in); c.rectangle(0, gy + 2, 640, 2); c.fill()
    ca = ramp(t, 4.3, 5.3) * (1 - ramp(t, 11.8, 12.4))
    claim_card(c, W / 2, 260, ca, ramp(t, 9.4, 10.0) * ca)
    ta = ramp(t, 12.6, 13.6) * (1 - ramp(t, 17.2, 18.0))
    if ta > 0:
        c.set_source_rgba(*BG, 0.85 * ta); c.paint()
        text(c, "滑雪里的物理", W / 2, 360, 30, DIM, ta, align="c", spacing=0.3)
        text(c, "雪板为什么能滑？", W / 2, 500, 96, INK, ta, align="c", bold=True)
        c.set_source_rgba(*GOLD, 0.8 * ta); c.rectangle(W / 2 - 160, 548, 320, 2); c.fill()
        text(c, "不是因为把雪压化了", W / 2, 612, 34, GOLD, ta, align="c")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2  pressure melting, calculated
S2_DUR = 46.0
S2_SUBS = [
    ("一个 75 公斤的人，站在两块雪板上。", 0.5, 4.4),
    ("板底面积约 0.22 平方米，压强约 {w|3.3 千帕}——\n只有一个大气压的三十分之一。", 4.7, 10.4),
    ("压力确实能让冰的熔点降低：\n但每多一个大气压，只降低 {b|0.0075 °C}。", 10.7, 16.4),
    ("所以这点压强，只能让熔点降低 {r|0.00024 °C}。", 16.7, 21.6),
    ("放大一万倍，才勉强看得见。", 21.9, 25.6),
    ("反过来算：想让 −10 °C 的雪靠压力化掉，\n要 {r|1300 多个大气压}——", 25.9, 31.6),
    ("相当于把整个人的体重，\n压在 {r|5 平方毫米}上——比一粒米的截面还小。", 31.9, 38.0),
    ("结论很清楚：{w|压力融化，解释不了}雪板为什么能滑。", 38.3, 45.4),
]


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, 45.4, 46.0))
    # phase A: skis top view + pressure (0 - 16.5)
    pa = a_in * (1 - ramp(t, 16.4, 17.0))
    if pa > 0:
        k = 620
        cx, cy = 820, 470
        skis_top(c, cx, cy, k, pa * ramp(t, 0.6, 1.4))
        dim_line(c, cx - SKI_L / 2 * k, cy + 0.30 * k, cx + SKI_L / 2 * k, cy + 0.30 * k, "1.6 m", pa * ramp(t, 4.8, 5.4))
        dim_line(c, cx + SKI_L / 2 * k + 40, cy + 0.13 * k - SKI_W / 2 * k, cx + SKI_L / 2 * k + 40, cy + 0.13 * k + SKI_W / 2 * k,
                 "7 cm", pa * ramp(t, 5.2, 5.8), off=(44, 8))
        # weight arrow
        wa = pa * ramp(t, 1.0, 1.8)
        arrow(c, cx, cy - 300, cx, cy - 110, INK, wa, 4, 20)
        text(c, "75 kg × g = 736 N", cx + 24, cy - 220, 28, INK, wa, bold=True)
        text(c, "俯视 · 两块雪板", cx, cy + 0.42 * k, 22, DIM, pa * ramp(t, 0.8, 1.4), align="c")
    pp = ramp(t, 4.7, 5.6)
    p_now = P_SKIER * pp
    # phase B: number line (16.7 - 25.8)
    pb = a_in * ramp(t, 16.8, 17.6) * (1 - ramp(t, 25.6, 26.2))
    melt_line(c, DT_SKIER, pb, zoom=ramp(t, 22.0, 23.0))
    # phase C: required pressure & tiny area (25.9 - 46)
    pc = a_in * ramp(t, 26.0, 26.8)
    if pc > 0:
        k = 620
        cx, cy = 820, 470
        skis_top(c, cx, cy, k, pc * 0.9)
        # true-scale 5.5 mm^2 square (k px per m)
        side = math.sqrt(AREA_10) * k
        sq = pc * ramp(t, 32.0, 32.8)
        if sq > 0:
            c.rectangle(cx - side / 2, cy - side / 2, max(side, 1.5), max(side, 1.5)); c.set_source_rgba(*RED, sq); c.fill()
            r = 40 + 8 * math.sin(t * 4)
            c.arc(cx, cy, r, 0, 2 * math.pi); c.set_source_rgba(*RED, 0.7 * sq); c.set_line_width(2.5); c.stroke()
            c.move_to(cx + r * 0.7, cy - r * 0.7); c.line_to(cx + 190, cy - 190); c.stroke()
            text(c, f"{AREA_10 * 1e6:.1f} mm²（按比例）", cx + 200, cy - 200, 28, RED, sq, bold=True)
        text(c, f"−10 °C 需要 {P_10 / 1e6:.0f} MPa ≈ {P_10 / ATM:.0f} 个大气压", cx, cy + 0.36 * k, 30, RED, pc * ramp(t, 26.4, 27.2), align="c", bold=True)
    # chapter tag: live readout
    if t < 16.6:
        chapter_tag(c, f"{p_now / 1000:.1f} kPa", f"压强 · 一个大气压 = 101 kPa", ramp(t, 4.7, 5.4) * a_in * (1 - ramp(t, 16.2, 16.6)))
    elif t < 25.8:
        chapter_tag(c, f"{DT_SKIER:.5f} °C", "压强 3.3 kPa 使熔点降低", pb)
    else:
        chapter_tag(c, f"{P_10 / ATM:.0f} atm", "让 −10 °C 的雪靠压力融化", pc)
    # formula card
    fa = a_in * ramp(t, 10.9, 11.7) * (1 - ramp(t, 16.2, 16.7))
    if fa > 0:
        text(c, "dT/dP = T·Δv / L", 1380, 250, 40, GOLD, fa, bold=True)
        text(c, f"= {DTDP * ATM:.4f} °C / 大气压", 1380, 300, 28, INK, fa)
        text(c, "克拉珀龙方程 · 冰与水的密度、熔化潜热", 1380, 340, 20, DIM, fa)
    cite_card(c, "Am. J. Phys. 63 · 1995", "压力融化不能解释冰的低摩擦", "S. C. Colbeck", ramp(t, 38.3, 39.0) * a_in)
    model_note(c, a_in * ramp(t, 1, 2), "示意 · 体重、板长板宽为假设值")
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3  frictional heating
S3_DUR = 46.0
S3_SUBS = [
    ("那水从哪来？答案是：{w|摩擦本身}。", 0.5, 4.4),
    ("板在雪上滑，摩擦做的功变成热，\n先加热了雪粒和板底接触的那一小点。", 4.7, 10.4),
    ("1939 年，Bowden 和 Hughes 用导热性不同的滑块做实验：\n融水来自{w|摩擦生热}，而不是压力。", 10.7, 16.8),
    ("算一下：75 公斤、54 km/h、摩擦系数 0.03——\n摩擦功率约 {w|330 瓦}，每滑 1 米产热 22 焦。", 17.1, 23.6),
    ("就算这些热全拿来化冰，每米也只化出 0.066 克水；\n摊在两块板底，水膜不到 {b|0.5 微米}。", 23.9, 30.4),
    ("（这是上限：实际上大部分热会传进板和雪里）", 30.7, 34.0),
    ("Colbeck 的理论：水膜太薄，雪粒会刮擦板底；\n水膜适中时，摩擦{b|最小}。", 34.3, 40.6),
    ("板底只靠很少几个点，托在这层看不见的水上。", 40.9, 45.4),
]


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, 45.4, 46.0))
    oy = 400
    heat = ramp(t, 5.0, 7.0)
    film = ramp(t, 11.5, 13.0)
    GR.draw(c, 0, oy, t * 160, heat=heat, film=film, t=t, alpha=a_in)
    text(c, "板底", 90, oy - 50, 26, INK, a_in * ramp(t, 0.8, 1.4), bold=True)
    pill_label(c, "雪粒（示意放大）", 200, oy + 330, 22, DIM, a_in * ramp(t, 0.8, 1.4))
    arrow(c, 1500, oy - 60, 1720, oy - 60, INK, a_in * ramp(t, 0.8, 1.4), 3, 16)
    text(c, "滑行方向", 1610, oy - 82, 22, DIM, a_in * ramp(t, 0.8, 1.4), align="c")
    # readouts panel
    ra = a_in * ramp(t, 17.3, 18.1)
    if ra > 0:
        x, y = 1180, 690
        rounded_rect(c, x - 30, y - 60, 680, 220, 14); c.set_source_rgba(0.02, 0.025, 0.035, 0.95 * ra); c.fill()
        rows = [("摩擦功率", f"{POWER:.0f} W", WARM, 17.3), ("每米产热", f"{J_PER_M:.0f} J", WARM, 19.5),
                ("每米最多化水", f"{G_PER_M:.3f} g", ICE, 24.2), ("水膜厚度（上限）", f"{FILM_UM:.1f} µm", ICE, 26.5)]
        for i, (lab, val, col, t0) in enumerate(rows):
            a = ra * ramp(t, t0, t0 + 0.6)
            text(c, lab, x, y + i * 46, 26, DIM, a)
            text(c, val, x + 620, y + i * 46, 32, col, a, align="r", bold=True)
        text(c, "P = μ · m · g · v", x, y - 20 + 0, 0.1, DIM, 0)
    cite_card(c, "Proc. R. Soc. A · 1939", "融水来自摩擦生热，不是压力", "F. P. Bowden · T. P. Hughes",
              ramp(t, 10.7, 11.5) * (1 - ramp(t, 33.8, 34.3)) * a_in)
    cite_card(c, "J. Glaciol. 34 · 1988", "水膜适中时摩擦最小，太薄会刮擦", "S. C. Colbeck", ramp(t, 34.3, 35.0) * a_in)
    chapter_tag(c, "摩擦生热", "接触点被加热 · 化出极薄水膜", ramp(t, 0.6, 1.2) * a_in)
    model_note(c, a_in * ramp(t, 1, 2), "示意 · 雪粒与水膜厚度不按比例")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4  colder = stickier
S4_DUR = 30.0
S4_SUBS = [
    ("所以温度很关键：雪越冷，越难化出这层水。", 0.5, 4.8),
    ("整板实测：0 °C 时摩擦系数约 0.0145，\n−11 °C 时约 {r|0.033}——翻了一倍还多。", 5.1, 11.4),
    ("同样 54 km/h，冷雪上的摩擦功率\n是暖雪的两倍多：{b|160 瓦} 对 {r|364 瓦}。", 11.7, 18.0),
    ("这就是为什么特别冷的天，雪板会发“涩”。", 18.3, 23.4),
    ("（两个测量点之间的连线仅作示意）", 23.7, 29.0),
]


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, 29.4, 30.0))
    x0, y0, w, h = 260, 260, 760, 480
    X = lambda T: x0 + (T + 14) / 16 * w          # -14 .. +2 C
    Y = lambda mu: y0 + h - mu / 0.04 * h
    c.set_source_rgba(*FAINT, a_in); c.set_line_width(1.4)
    c.move_to(x0, y0); c.line_to(x0, y0 + h); c.line_to(x0 + w, y0 + h); c.stroke()
    for T in range(-14, 3, 2):
        text(c, f"{T}", X(T), y0 + h + 34, 20, DIM, a_in, align="c")
    for mu in (0, 0.01, 0.02, 0.03, 0.04):
        text(c, f"{mu:.2f}", x0 - 14, Y(mu) + 7, 20, DIM, a_in, align="r")
        c.set_source_rgba(*FAINT, 0.35 * a_in); c.rectangle(x0, Y(mu), w, 1); c.fill()
    text(c, "雪温 °C", x0 + w, y0 + h + 72, 22, DIM, a_in, align="r")
    text(c, "摩擦系数 μ", x0, y0 - 24, 22, DIM, a_in)
    la = a_in * ramp(t, 5.4, 6.4)
    polyline(c, np.array([(X(-11), Y(MU_COLD)), (X(0), Y(MU_WARM))]), DIM, 0.7 * la, 2, [8, 8])
    for T, mu, col, t0 in ((0, MU_WARM, ICE, 5.4), (-11, MU_COLD, RED, 6.6)):
        a = a_in * ramp(t, t0, t0 + 0.5)
        c.arc(X(T), Y(mu), 12, 0, 2 * math.pi); c.set_source_rgba(*col, a); c.fill()
        text(c, f"{mu}", X(T) + (24 if T == -11 else -24), Y(mu) - 20, 28, col, a, align="l" if T == -11 else "r", bold=True)
    # power bars
    bx, by, bw, bh = 1260, 740, 160, 440
    ba = a_in * ramp(t, 11.9, 12.7)
    for i, (lab, p, col) in enumerate((("0 °C", P_WARM, ICE), ("−11 °C", P_COLD, RED))):
        hh = bh * p / 400 * ramp(t, 12.0 + i * 0.6, 13.4 + i * 0.6)
        x = bx + i * (bw + 90)
        c.rectangle(x, by - hh, bw, hh); c.set_source_rgba(*col, 0.85 * ba); c.fill()
        text(c, f"{p:.0f} W", x + bw / 2, by - hh - 18, 32, col, ba, align="c", bold=True)
        text(c, lab, x + bw / 2, by + 40, 24, DIM, ba, align="c")
    text(c, "54 km/h 时的摩擦功率", bx + bw + 45, by + 84, 22, DIM, ba, align="c")
    chapter_tag(c, "越冷越涩", "温度低 · 摩擦热先得把雪加热到 0 °C", ramp(t, 0.6, 1.2) * a_in)
    cite_card(c, "arXiv:2212.08524", "整板实测：0 °C 约 0.0145，−11 °C 约 0.033", "预印本 · 整块雪板的摩擦实验", ramp(t, 5.1, 5.9) * a_in)
    model_note(c, a_in, "75 kg · 54 km/h · P = μmgv")
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5  the story is not finished
S5_DUR = 42.0
S5_SUBS = [
    ("但故事没有讲完。", 0.5, 3.0),
    ("2018 年，美国陆军寒区实验室用红外热像仪，\n以 15 微米的分辨率盯着雪粒看——", 3.3, 9.4),
    ("摩擦很低时，他们{r|没有看到雪粒融化}：\n雪粒是被一点点{w|磨掉}的，碎屑落进了雪粒间的空隙。", 9.7, 16.6),
    ("同一年，另一组研究者发现：冰的表面本来就有一层\n只被两根氢键拴住、会{b|滚动}的水分子。", 16.9, 23.6),
    ("温度越高，这样的分子越多、越活跃——冰也就越滑。", 23.9, 29.0),
    ("融水、磨损、表面分子：\n这几种机制谁占主导，{w|科学家还在争论}。", 29.3, 36.4),
    ("（三种机制的示意图均不按比例）", 36.7, 41.4),
]


def panel_box(c, x, y, w, h, title, a, col):
    rounded_rect(c, x, y, w, h, 14)
    c.set_source_rgba(0.02, 0.025, 0.035, 0.6 * a); c.fill_preserve()
    c.set_source_rgba(*col, 0.5 * a); c.set_line_width(1.5); c.stroke()
    text(c, title, x + w / 2, y + 46, 30, col, a, align="c", bold=True)


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, 41.4, 42.0))
    # layout: big single view, then three panels from 29.3
    three = ramp(t, 29.3, 30.4)
    if three < 1:
        a1 = a_in * (1 - three)
        if t < 16.9:
            heat = 0.25
            GR.draw(c, 0, 470, t * 140, heat=heat, film=0.0, abrade=ramp(t, 10.2, 11.2), t=t, alpha=a1 * ramp(t, 3.4, 4.2))
            # IR camera frame
            fa = a1 * ramp(t, 3.6, 4.4)
            c.set_source_rgba(*GOLD, 0.8 * fa); c.set_line_width(2)
            for (x, y, dx, dy) in ((560, 360, 1, 1), (1360, 360, -1, 1), (560, 640, 1, -1), (1360, 640, -1, -1)):
                c.move_to(x, y + 40 * dy); c.line_to(x, y); c.line_to(x + 40 * dx, y); c.stroke()
            text(c, "红外热像 · 15 µm", 580, 340, 22, GOLD, fa)
            na = a1 * ramp(t, 9.9, 10.6)
            pill_label(c, "未见融化 · 雪粒被磨损", 960, 760, 30, RED, na)
        else:
            ma = a1 * ramp(t, 17.0, 17.8)
            mob = 0.25 + 0.75 * ramp(t, 24.0, 28.0)
            molecules(c, 560, 300, 800, 400, t, mob, ma)
            text(c, "冰的表面（示意）", 960, 760, 24, DIM, ma, align="c")
            text(c, f"温度升高 → 表层分子更活跃", 960, 800, 26, ICE, ma * ramp(t, 24.0, 24.8), align="c", bold=True)
    if three > 0:
        a3 = a_in * three
        pw, ph, gap = 520, 520, 40
        x0 = (W - 3 * pw - 2 * gap) / 2
        y0 = 200
        titles = (("融水润滑", ICE), ("磨损", GOLD), ("表面分子", (0.55, 0.85, 0.65)))
        for i, (ti, col) in enumerate(titles):
            x = x0 + i * (pw + gap)
            panel_box(c, x, y0, pw, ph, ti, a3, col)
            c.save(); c.rectangle(x + 4, y0 + 70, pw - 8, ph - 80); c.clip()
            c.translate(x + 10, y0 + 260); c.scale(0.55, 0.55)
            if i == 0:
                GR.draw(c, 0, 0, t * 140, heat=0.6, film=1.0, t=t, alpha=a3, x0=0, x1=900)
            elif i == 1:
                GR.draw(c, 0, 0, t * 140, heat=0.2, abrade=1.0, t=t, alpha=a3, x0=0, x1=900)
            c.restore()
            if i == 2:
                c.save(); c.rectangle(x + 4, y0 + 70, pw - 8, ph - 80); c.clip()
                molecules(c, x + 40, y0 + 120, pw - 80, 300, t, 0.8, a3)
                c.restore()
            sub = ("Bowden & Hughes 1939 · Colbeck 1988", "Lever 等 2018", "Weber, Nagata 等 2018")[i]
            text(c, sub, x + pw / 2, y0 + ph - 24, 20, DIM, a3, align="c")
    cite_card(c, "J. Glaciol. 64 · 2018", "低摩擦时未观测到雪粒融化，雪粒被磨损", "Lever, Taylor, Song 等",
              ramp(t, 3.3, 4.0) * (1 - ramp(t, 16.4, 16.9)) * a_in)
    cite_card(c, "J. Phys. Chem. Lett. 9 · 2018", "冰表面可滚动的分子让冰变滑", "B. Weber, Y. Nagata 等",
              ramp(t, 16.9, 17.6) * (1 - ramp(t, 29.0, 29.5)) * a_in)
    chapter_tag(c, "仍在争论", "三种机制 · 2018 年的新证据", ramp(t, 0.6, 1.2) * a_in)
    subs(c, t, S5_SUBS)
    overlays(c, fi)


# ================================================================== S6  ending
S6_DUR = 24.0
S6_SUBS = [
    ("所以，雪板能滑，靠的{w|不是压力}。", 0.6, 4.6),
    ("是摩擦生热、雪粒磨损，\n和冰表面本身那层会动的分子。", 4.9, 10.4),
    ("下次在雪道上飞驰时——你脚下这层薄薄的东西，\n科学家到今天还没完全弄明白。", 10.7, 17.4),
    ("（画面为示意；数值为按文中假设的估算）", 17.7, 22.4),
]


def s6(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, 22.4, 23.8))
    gy = 760
    snow_ground(c, gy, t + 30, 520, a_in)
    skier(c, 760, gy, 150, 0.35 + 0.05 * math.sin(t * 2), a_in, t * 2.5)
    c.set_source_rgba(*RIM, 0.25 * a_in); c.rectangle(0, gy + 2, 640, 2); c.fill()
    # thin glowing film under the ski
    fa = a_in * ramp(t, 5.0, 6.0)
    c.set_source_rgba(*ICE, 0.9 * fa); c.rectangle(632, gy + 1, 275, 4); c.fill()
    end = ramp(t, 17.8, 18.6) * a_in
    if end > 0:
        text(c, "滑雪里的物理", W / 2, 300, 30, DIM, end, align="c", spacing=0.3)
        text(c, "雪板为什么能滑？", W / 2, 400, 64, INK, end, align="c", bold=True)
    chapter_tag(c, "答案", "摩擦热 · 磨损 · 表面分子", ramp(t, 0.6, 1.2) * a_in)
    subs(c, t, S6_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, 23.0, 24.0))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR), ("s6", s6, S6_DUR)]
