"""《双板断十字韧带的三种方式》 scenes."""
import math
import numpy as np
from common import *
from art import *


def subs(c, t, SUBS):
    for s, a, b in SUBS:
        subtitle(c, s, t, a, b)


SERIES = "双板 · 用数据说话"


# ================================================================== S1  two lines going opposite ways
S1_DUR = 28.0
S1_SUBS = [
    ("美国佛蒙特的一家雪场，研究者连续追踪了 {w|34 年}的滑雪伤病。", 0.6, 5.6),
    ("固定器越做越好：扭转造成的小腿损伤，下降了 {b|87%}。", 5.9, 11.2),
    ("可严重的膝扭伤——大多是前十字韧带——\n到 90 年代初反而涨了 {r|268%}。", 11.5, 17.6),
    ("后来回落了 37%，但仍是起点的两倍多。\n固定器救了小腿，却没救膝盖。", 17.9, 23.4),
]


def trend_chart(c, t, a_in, t_leg=6.0, t_knee=11.8, x0=300, y0=230, w=1300, h=520):
    X = lambda u: x0 + u * w          # u: 0 = 1972 start, 0.6 = early 90s, 1 = 2006
    Y = lambda v: y0 + h - v / 400 * h
    c.set_source_rgba(*FAINT, a_in); c.set_line_width(1.4)
    c.move_to(x0, y0); c.line_to(x0, y0 + h); c.line_to(x0 + w, y0 + h); c.stroke()
    for v in (0, 100, 200, 300, 400):
        text(c, f"{v}", x0 - 14, Y(v) + 7, 20, DIM, a_in, align="r")
        c.set_source_rgba(*FAINT, 0.35 * a_in); c.rectangle(x0, Y(v), w, 1); c.fill()
    for u, lab in ((0, "1972"), (0.6, "90 年代初"), (1, "2006")):
        text(c, lab, X(u), y0 + h + 34, 22, DIM, a_in, align="c")
    text(c, "受伤率指数（1972 年 = 100）", x0, y0 - 24, 22, DIM, a_in)
    c.set_dash([6, 6]); c.set_source_rgba(*DIM, 0.6 * a_in); c.move_to(x0, Y(100)); c.line_to(x0 + w, Y(100)); c.stroke(); c.set_dash([])
    # lower-leg line: two points only (start, end)
    k = ease_io((t - t_leg) / 2.4)
    if k > 0:
        P = np.array([(X(0), Y(100)), (X(lerp(0, 1, k)), Y(lerp(100, LOWER_LEG_END, k)))])
        polyline(c, P, ICE, a_in, 5)
        if k >= 1:
            c.arc(X(1), Y(LOWER_LEG_END), 9, 0, 2 * math.pi); c.set_source_rgba(*ICE, a_in); c.fill()
            text(c, f"小腿扭转损伤  {LOWER_LEG_END:.0f}", X(1) - 14, Y(LOWER_LEG_END) - 20, 26, ICE, a_in, align="r", bold=True)
    k2 = ease_io((t - t_knee) / 3.0)
    if k2 > 0:
        pts = [(0, 100), (0.6, KNEE_PEAK), (1, KNEE_END)]
        seg = []
        for i in range(2):
            u0, v0 = pts[i]; u1, v1 = pts[i + 1]
            kk = clamp(k2 * 2 - i)
            if kk <= 0:
                break
            seg.append((X(u0), Y(v0))); seg.append((X(lerp(u0, u1, kk)), Y(lerp(v0, v1, kk))))
        polyline(c, np.array(seg), RED, a_in, 5)
        if k2 > 0.5:
            c.arc(X(0.6), Y(KNEE_PEAK), 9, 0, 2 * math.pi); c.set_source_rgba(*RED, a_in); c.fill()
            text(c, f"严重膝扭伤  {KNEE_PEAK:.0f}", X(0.6), Y(KNEE_PEAK) - 22, 26, RED, a_in, align="c", bold=True)
        if k2 >= 1:
            c.arc(X(1), Y(KNEE_END), 9, 0, 2 * math.pi); c.set_source_rgba(*RED, a_in); c.fill()
            text(c, f"{KNEE_END:.0f}", X(1) + 16, Y(KNEE_END) + 8, 26, RED, a_in, bold=True)
    text(c, "只有起点、峰值、终点三个数据点，连线为示意", x0 + w, y0 + h + 72, 18, DIM, a_in, align="r")


def s1(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.8) * (1 - 0.8 * ramp(t, 23.6, 24.4))
    trend_chart(c, t, a_in)
    cite_card(c, "ASTM STP 1510 · 2009", "佛蒙特一家雪场 1972–2006 年的伤病趋势", "Johnson · Ettlinger · Shealy", ramp(t, 0.8, 1.6) * a_in)
    ta = ramp(t, 24.0, 25.0) * (1 - ramp(t, 27.2, 28.0))
    if ta > 0:
        text(c, SERIES, W / 2, 380, 30, DIM, ta, align="c", spacing=0.3)
        text(c, "双板断十字韧带的三种方式", W / 2, 510, 84, INK, ta, align="c", bold=True)
        c.set_source_rgba(*GOLD, 0.8 * ta); c.rectangle(W / 2 - 160, 556, 320, 2); c.fill()
        text(c, "世界杯录像 · 长期追踪 · 临床数据", W / 2, 620, 32, GOLD, ta, align="c")
    subs(c, t, S1_SUBS)
    overlays(c, fi)
    fade_black(c, 1 - ramp(t, 0, 0.6))


# ================================================================== S2  282 knees, all ACL
S2_DUR = 30.0
S2_SUBS = [
    ("在普通滑雪者里，膝盖是最常受伤的部位，约占{w|三分之一}。", 0.6, 5.6),
    ("奥地利一家雪场诊所，统计了 282 位因膝伤就诊、\n做过核磁确诊的普通滑雪者——", 5.9, 11.6),
    ("结果：{r|每一个人}，都伤到了前十字韧带。", 11.9, 16.6),
    ("其中 182 人还合并了其他损伤，最常见的是内侧副韧带；\n100 人是单纯的前十字韧带断裂。", 16.9, 23.6),
    ("所以，弄清楚它是{w|怎么断的}，就是双板安全的头号问题。", 23.9, 29.4),
]


def s2(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, 29.4, 30.0))
    # one-third ring
    ra = a_in * ramp(t, 0.8, 1.6) * (1 - ramp(t, 5.6, 6.2))
    if ra > 0:
        cx, cy, R = W / 2, 460, 200
        c.set_line_width(46)
        c.arc(cx, cy, R, 0, 2 * math.pi); c.set_source_rgba(*FAINT, ra); c.stroke()
        k = ease_io((t - 1.2) / 1.6)
        c.arc(cx, cy, R, -math.pi / 2, -math.pi / 2 + 2 * math.pi / 3 * k); c.set_source_rgba(*GOLD, ra); c.stroke()
        text(c, "约 1/3", cx, cy + 10, 72, GOLD, ra, align="c", bold=True)
        text(c, "膝盖", cx, cy + 70, 30, INK, ra, align="c")
    ma = a_in * ramp(t, 6.0, 6.8)
    if ma > 0:
        cols, gap, r = 24, 38, 13
        x0 = W / 2 - (cols - 1) * gap / 2
        y0 = 260
        reveal = ease_io((t - 6.2) / 4.0)
        lit = ramp(t, 12.0, 13.0)
        split = ramp(t, 17.2, 18.2)

        def col(i):
            base = mix(FAINT, RED, lit)
            if split > 0:
                return mix(base, GOLD if i < POSCH_COMB else RED, split)
            return base
        dot_matrix(c, x0, y0, POSCH_N, cols, gap, r, col, ma, reveal)
        la = ma * split
        text(c, f"{POSCH_COMB} 人 · 合并其他损伤", x0 - 20, y0 + 13 * gap - 10, 28, GOLD, la, bold=True)
        text(c, f"{POSCH_N - POSCH_COMB} 人 · 单纯前十字韧带", x0 + (cols - 1) * gap + 20, y0 + 13 * gap - 10, 28, RED, la, align="r", bold=True)
        chapter_tag(c, f"{POSCH_N} / {POSCH_N}", "核磁确诊的膝伤 · 全部伤及前十字韧带", lit * a_in)
    cite_card(c, "KSSTA · 2020", "需住院的膝伤，全部伤及前十字韧带", "Posch · Schranz · … · Ruedl", ramp(t, 6.0, 6.8) * a_in)
    subs(c, t, S2_SUBS)
    overlays(c, fi)


# ================================================================== S3  World Cup video: three mechanisms
S3_DUR = 66.0
S3_SUBS = [
    ("挪威的研究者调出了世界杯 3 个赛季、20 次前十字韧带断裂的录像，\n请 7 位国际专家逐帧分析。", 0.6, 7.4),
    ("他们把受伤动作归成三类。最多的一类，占了 {r|一半}：", 7.7, 12.0),
    ("{r|slip-catch}——“滑脱后卡住”。", 12.3, 15.6),
    ("转弯时，外板压力没了、往外滑开……", 15.9, 20.6),
    ("……接着内刃突然重新咬进雪里，\n板一下被卡住，膝盖被拧向内侧、小腿向内旋转。", 20.9, 28.2),
    ("动作本身只是一瞬间：不是撞，是自己把自己拧伤的。", 28.5, 33.6),
    ("第二类：{w|后坐着落地}。\n跳跃落地时重心在后，板尾先着地。", 33.9, 41.4),
    ("第三类：{w|动态犁式}。\n失衡时内板翻到内刃、卡进雪里，膝盖同样被拧向内。", 41.7, 49.6),
    ("研究者的结论：这些受伤，主要来自{w|技术失误}和战术选择，\n而不是运气。", 49.9, 56.6),
    ("（受伤动作为示意，只演示研究中描述过的特征）", 56.9, 65.4),
]


def grid20(c, t, a, x0=660, y0=230, cell=110, gap=14):
    for i in range(BERE_N):
        cx = x0 + (i % 5) * (cell + gap); cy = y0 + (i // 5) * (cell + gap)
        slip = i < BERE_SLIP
        k = ramp(t, 8.0 + i * 0.06, 8.4 + i * 0.06)
        col = mix(FAINT, RED if slip else GOLD, k)
        rounded_rect(c, cx, cy, cell, cell, 10); c.set_source_rgba(*col, (0.85 if slip else 0.5) * a); c.fill()
    la = a * ramp(t, 9.5, 10.2)
    text(c, "slip-catch  10 例", x0 - 30, y0 + cell, 30, RED, la, align="r", bold=True)
    text(c, "后坐落地 / 动态犁式", x0 + 5 * (cell + gap) + 16, y0 + 3 * (cell + gap) - 10, 26, GOLD, la, bold=True)
    text(c, "共 10 例", x0 + 5 * (cell + gap) + 16, y0 + 3 * (cell + gap) + 26, 22, DIM, la)


def s3(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, 65.4, 66.0))
    ga = a_in * (1 - ramp(t, 12.0, 12.6))
    if ga > 0:
        grid20(c, t, ga * ramp(t, 0.6, 1.4))
    # slip-catch front view (12.3 - 33.6)
    sa = a_in * ramp(t, 12.4, 13.0) * (1 - ramp(t, 33.6, 34.2))
    if sa > 0:
        gy = 780
        c.rectangle(0, gy, W, H - gy); c.set_source_rgba(*TERRAIN, sa); c.fill()
        c.set_source_rgba(*RIM, 0.9 * sa); c.rectangle(0, gy - 1.5, W, 3); c.fill()
        slide = 0.35 * ease_io((t - 16.2) / 2.6) * (1 - ease_io((t - 21.0) / 0.5) * 0.4)
        catch = ramp(t, 21.0, 21.5)
        val = catch * ramp(t, 21.2, 22.4)
        lean = math.radians(lerp(10, 15, ease_io((t - 16.2) / 2.6)))
        skier_front(c, 760, gy, 300, lean=lean, valgus=val, out_edge=math.radians(lerp(30, 8, ramp(t, 16.2, 18.5)) + 40 * catch * math.pi / 180),
                    in_edge=math.radians(25), out_slide=slide, alpha=sa, knee_mark=val)
        if 16.2 < t < 21.0:
            arrow(c, 900, gy + 40, 1080, gy + 40, ICE, sa * 0.9, 3, 16)
            pill_label(c, "外板滑开 · 压力消失", 1400, 330, 30, ICE, sa)
        if t > 21.0:
            pill_label(c, "内刃突然咬雪 → 膝外翻 + 小腿内旋", 1400, 330, 30, RED, sa * ramp(t, 21.4, 22.0))
        text(c, "正面示意 · 向画面左侧转弯，外侧腿在画面右侧", 960, 200, 22, DIM, sa, align="c")
        chapter_tag(c, "slip-catch", "10 / 20 · 最常见", sa)
    # landing back-weighted (33.9 - 41.4): side view
    la = a_in * ramp(t, 34.0, 34.6) * (1 - ramp(t, 41.4, 42.0))
    if la > 0:
        gy = 760
        c.rectangle(0, gy, W, H - gy); c.set_source_rgba(*TERRAIN, la); c.fill()
        c.set_source_rgba(*RIM, 0.9 * la); c.rectangle(0, gy - 1.5, W, 3); c.fill()
        k = ease_io((t - 35.0) / 3.0)
        y = lerp(gy - 300, gy, k)
        pitch = lerp(0.25, 0.10, k)
        side_pose(c, 900 + 200 * k, y - 0.85 * 260 * math.sin(pitch) * (1 - k * 0.0), 260, back=lerp(0.4, 0.85, k), pitch=pitch, alpha=la,
                  tail_mark=ramp(t, 37.6, 38.2), knee_mark=ramp(t, 38.0, 38.6))
        pill_label(c, "重心在后 · 板尾先着地", 1400, 330, 30, GOLD, la * ramp(t, 38.0, 38.6))
        chapter_tag(c, "后坐落地", "landing back-weighted", la)
    # dynamic snowplow (41.7 - 49.6): front view, inner ski catches
    da = a_in * ramp(t, 41.8, 42.4) * (1 - ramp(t, 49.6, 50.2))
    if da > 0:
        gy = 780
        c.rectangle(0, gy, W, H - gy); c.set_source_rgba(*TERRAIN, da); c.fill()
        c.set_source_rgba(*RIM, 0.9 * da); c.rectangle(0, gy - 1.5, W, 3); c.fill()
        k = ramp(t, 43.5, 45.5)
        skier_front(c, 760, gy, 300, lean=math.radians(lerp(10, -6, k)), inner_valgus=k, in_edge=math.radians(lerp(10, -30, k)),
                    out_edge=math.radians(15), alpha=da, knee_mark=ramp(t, 45.0, 45.6))
        pill_label(c, "内板翻到内刃、卡雪 → 膝盖被拧向内", 1400, 330, 30, GOLD, da * ramp(t, 45.0, 45.6))
        chapter_tag(c, "动态犁式", "dynamic snowplow", da)
    # conclusion card
    ca = a_in * ramp(t, 50.0, 50.8)
    if ca > 0:
        for i, (lab, col) in enumerate((("技术失误", GOLD), ("战术选择", GOLD), ("比赛条件", DIM))):
            x = 560 + i * 400
            rounded_rect(c, x - 160, 380, 320, 150, 14); c.set_source_rgba(0.03, 0.04, 0.05, 0.9 * ca); c.fill_preserve()
            c.set_source_rgba(*col, 0.7 * ca); c.set_line_width(1.5); c.stroke()
            text(c, lab, x, 472, 40, col, ca * ramp(t, 50.4 + i * 0.4, 51.0 + i * 0.4), align="c", bold=True)
        chapter_tag(c, "主要原因", "20 例世界杯受伤录像", ca)
    cite_card(c, "Am J Sports Med 39 · 2011", "20 例世界杯 ACL 断裂：三种受伤机制", "Bere · Flørenes · Krosshaug 等",
              ramp(t, 0.6, 1.4) * (1 - ramp(t, 49.4, 49.9)) * a_in)
    cite_card(c, "Br J Sports Med 45 · 2011", "主因：技术失误、战术选择与比赛条件", "Bere · Flørenes · Krosshaug 等", ramp(t, 49.9, 50.6) * a_in)
    if t < 12:
        chapter_tag(c, "20 例", "世界杯 3 个赛季 · 7 位专家逐帧分析", ramp(t, 0.6, 1.2) * a_in * (1 - ramp(t, 11.6, 12.0)))
    model_note(c, a_in * ramp(t, 12.4, 13.4), "示意 · 小人动作不代表真实关节角度")
    subs(c, t, S3_SUBS)
    overlays(c, fi)


# ================================================================== S4  phantom foot
S4_DUR = 42.0
S4_SUBS = [
    ("普通滑手最常见的，是另一种：{r|幽灵脚}（phantom foot）。", 0.6, 5.6),
    ("人向后失去平衡，重量压在下坡那块板上——", 5.9, 10.6),
    ("板尾加上硬硬的雪鞋后帮，像一根{r|撬棍}，\n把膝盖往里拧。", 10.9, 17.0),
    ("三个危险信号：上坡那只手落在后面、\n重心往后倒、{r|屁股低于膝盖}。", 17.3, 24.0),
    ("最危险的三个时刻：失衡了还想硬救回来、\n摔倒了还在滑就想站起来、失控时想往后坐下。", 24.3, 32.0),
    ("研究者把它叫作幽灵脚，因为下坡板的板尾，\n就像一只朝后长出来的“脚”。", 32.3, 38.6),
    ("（姿势为示意；危险信号来自佛蒙特滑雪安全研究）", 38.9, 41.6),
]


def s4(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, 41.4, 42.0))
    gy = 760
    # slope tilted (skiing to the right, downhill to the right)
    sl = math.radians(12)
    c.save(); c.translate(960, gy); c.rotate(sl)
    c.rectangle(-1400, 0, 2800, 900); c.set_source_rgba(*TERRAIN, a_in); c.fill()
    c.set_source_rgba(*RIM, 0.9 * a_in); c.rectangle(-1400, -1.5, 2800, 3); c.fill()
    back = ease_io((t - 6.0) / 3.0)
    j = side_pose(c, -40, 0, 330, back=back, pitch=0, alpha=a_in, tail_mark=ramp(t, 11.0, 11.8),
                  knee_mark=ramp(t, 12.0, 12.8), arm_back=ramp(t, 17.6, 18.6))
    c.restore()
    # lever arrows (screen space, approximate around the tail)
    la = a_in * ramp(t, 11.4, 12.2) * (1 - ramp(t, 24.0, 24.6))
    if la > 0:
        tx, ty = 960 + math.cos(sl) * (-40 - 0.6 * 330), gy + math.sin(sl) * (-40 - 0.6 * 330)
        arrow(c, tx - 20, ty + 90, tx - 10, ty + 14, RED, la, 4, 18)
        text(c, "板尾", tx - 40, ty + 130, 26, RED, la, align="c", bold=True)
    # three warning signs
    for i, (lab, t0) in enumerate((("① 上坡手在后", 17.6), ("② 重心向后", 19.4), ("③ 髋低于膝", 21.2))):
        a = a_in * ramp(t, t0, t0 + 0.6) * (1 - ramp(t, 23.8, 24.3))
        pill_label(c, lab, 1460, 330 + i * 90, 32, RED, a, align="l")
    # three moments
    for i, (lab, t0) in enumerate((("失衡硬救", 24.6), ("摔倒还在滑就想站起", 26.6), ("失控时往后坐", 28.6))):
        a = a_in * ramp(t, t0, t0 + 0.6) * (1 - ramp(t, 38.6, 39.2))
        pill_label(c, lab, 1460, 330 + i * 90, 30, GOLD, a, align="l")
    chapter_tag(c, "幽灵脚", "phantom foot · 普通滑手最常见", ramp(t, 0.6, 1.2) * a_in)
    cite_card(c, "Vermont Ski Safety", "向后失衡 + 下坡板板尾 = 撬膝盖", "Ettlinger · Johnson · Shealy", ramp(t, 6.0, 6.8) * a_in)
    model_note(c, a_in, "示意 · 侧面视角，向画面右侧下坡")
    subs(c, t, S4_SUBS)
    overlays(c, fi)


# ================================================================== S5  prevention
S5_DUR = 32.0
S5_SUBS = [
    ("能预防吗？研究者给 20 家雪场的员工上了一堂识别课——", 0.6, 5.6),
    ("据报道，受训的人，下一季前十字韧带受伤{b|少了 62%}。", 5.9, 11.4),
    ("要点只有四步：不做高风险动作，练好技术，\n认出危险姿势，用对的方式应对。", 11.7, 18.4),
    ("应对就是：手往前，脚并拢，重心往前；\n摔就摔，{w|别硬撑}，等停稳了再起身。", 18.7, 26.0),
    ("（不构成医疗建议；膝盖受伤请及时就医）", 26.3, 31.4),
]


def s5(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, 31.4, 32.0))
    ba = a_in * ramp(t, 6.0, 6.8) * (1 - ramp(t, 11.6, 12.2))
    if ba > 0:
        x0, y0, bw, bh = 560, 280, 800, 110
        k = ease_io((t - 6.2) / 1.6)
        for i, (lab, v, col) in enumerate((("未受训", 1.0, RED), ("受训后", 1 - TRAIN_REDUCTION * k, ICE))):
            y = y0 + i * 190
            text(c, lab, x0 - 30, y + 70, 34, INK, ba, align="r", bold=True)
            c.rectangle(x0, y, bw * v, bh); c.set_source_rgba(*col, 0.85 * ba); c.fill()
        text(c, f"−{TRAIN_REDUCTION * 100 * k:.0f}%", x0 + bw * (1 - TRAIN_REDUCTION) + 30, y0 + 190 + 76, 56, ICE, ba, bold=True)
        text(c, "前十字韧带受伤（相对值）", x0, y0 - 30, 22, DIM, ba)
    sa = a_in * ramp(t, 11.8, 12.6)
    if sa > 0:
        steps = ("不做高风险动作", "练好技术", "认出危险姿势", "正确应对")
        for i, s in enumerate(steps):
            x = 300 + i * 440
            a = sa * ramp(t, 12.0 + i * 1.2, 12.6 + i * 1.2)
            rounded_rect(c, x - 190, 300, 380, 170, 14); c.set_source_rgba(0.03, 0.04, 0.05, 0.9 * a); c.fill_preserve()
            c.set_source_rgba(*GOLD, 0.6 * a); c.set_line_width(1.5); c.stroke()
            text(c, f"{i + 1}", x, 370, 48, GOLD, a, align="c", bold=True)
            text(c, s, x, 432, 32, INK, a, align="c", bold=True)
        ra = a_in * ramp(t, 18.8, 19.6)
        if ra > 0:
            for i, s in enumerate(("手往前", "脚并拢", "重心往前", "摔就摔，别硬撑", "停稳再起身")):
                pill_label(c, s, 300 + i * 330, 620, 30, ICE, ra * ramp(t, 19.0 + i * 0.9, 19.6 + i * 0.9))
    chapter_tag(c, "62%", "受训员工下一季 ACL 受伤减少（据报道）", ramp(t, 0.6, 1.2) * a_in)
    cite_card(c, "Am J Sports Med · 1995", "识别训练：ACL 受伤减少约 62%（据后续报道）", "Ettlinger · Johnson · Shealy", ramp(t, 0.6, 1.4) * a_in)
    subs(c, t, S5_SUBS)
    overlays(c, fi)


# ================================================================== S6  end
S6_DUR = 16.0
S6_SUBS = [
    ("固定器保护不了膝盖，但你可以。", 0.6, 4.6),
    ("认得这几个动作：外板卡雪、后坐落地、内板卡雪、幽灵脚——\n比什么护具都管用。", 4.9, 11.6),
]


def s6(c, t, fi):
    paint_bg(c)
    a_in = ramp(t, 0, 0.6) * (1 - ramp(t, 14.6, 15.6))
    gy = 760
    snow_ground(c, gy, t, 480, a_in)
    skier(c, 760, gy, 150, 0.35 + 0.05 * math.sin(t * 2), a_in, t * 2.5)
    ea = ramp(t, 11.8, 12.6) * a_in
    if ea > 0:
        text(c, SERIES, W / 2, 300, 30, DIM, ea, align="c", spacing=0.3)
        text(c, "双板断十字韧带的三种方式", W / 2, 400, 60, INK, ea, align="c", bold=True)
    subs(c, t, S6_SUBS)
    overlays(c, fi)
    fade_black(c, ramp(t, 15.0, 16.0))


SCENES = [("s1", s1, S1_DUR), ("s2", s2, S2_DUR), ("s3", s3, S3_DUR), ("s4", s4, S4_DUR), ("s5", s5, S5_DUR), ("s6", s6, S6_DUR)]
