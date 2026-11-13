"""提案 05：四个方向，各自的分片。TP 坐标，鞋头朝左。
usage: variants.py tp.json mono.json word.json outdir
每个方向出两张：白色线稿（-tp.svg）和一套配色（-color.svg）。"""
import sys, math
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
from tpkit import Kit, Sheet, spline, rounded, strip, tapered, palette, dark_palette, D, ld

K = Kit(*sys.argv[1:4])
OUT = sys.argv[4]

def below(pts, x0=0, x1=480, y=560):
    """曲线以下的区域"""
    return Polygon(spline(pts, steps=14) + [(x1, y), (x0, y)]).buffer(0)

def above(pts, x0=0, x1=480, y=0):
    return Polygon(spline(pts, steps=14) + [(x1, y), (x0, y)]).buffer(0)

# 各方向都用的：领口软垫、前侧鞋带区护片的通用外形
COLLAR = [(228, 60), (228, 134), (262, 139), (300, 141), (338, 138), (370, 128), (393, 116), (430, 104), (430, 60)]

# ============ A 流线：一条大斜带从后领口扫到脚背，接进鞋头 ============
def flow(C, uid):
    s = Sheet(K, C, uid); k = K
    s.begin()
    SASH = [(404, 96), (372, 150), (334, 214), (298, 276), (262, 322), (214, 350), (160, 368), (104, 382), (60, 392)]
    sash = k.clip(unary_union([tapered(SASH[:5], 30, 34), tapered(SASH[4:], 34, 20)]), 1.6)
    sl = LineString(spline(SASH, steps=16))
    # 斜带后上方：上鞋身片（下沿和斜带平行）
    up_edge = sl.offset_curve(-30)
    upper = k.clip(Polygon(list(up_edge.coords) + [(480, 60), (480, -20)]).buffer(0).union(box(300, 0, 480, 60)))
    s.panel(upper, C['quarter'], stitch=(1.6, 3.0))
    # 斜带前下方：下鞋身片，上面一块透气孔
    lo_edge = sl.offset_curve(30)
    lower = k.clip(Polygon(list(lo_edge.coords) + [(20, 560), (480, 560)]).buffer(0))
    s.panel(lower, C['quarter2'], stitch=(1.6, 3.0))
    perf = []
    for i in range(4):
        ln = sl.offset_curve(42 + i * 4.6)
        for j in range(10):
            p = ln.interpolate(ln.length * 0.30 + j * 4.4 + (i % 2) * 2.2)
            if p.within(lower.buffer(-4)): perf.append((p.x, p.y))
    s.holes(perf, 0.9)
    # 后跟杯
    heel = k.clip(Polygon(spline([(460, 470), (352, 470), (356, 428), (368, 390), (392, 362), (460, 352)], steps=14)).buffer(0))
    s.panel(heel, C['heel'], 'crackle')
    s.panel(k.clip(Polygon(spline(COLLAR, steps=14)).buffer(0)), C['collar'], stitch=(2.0,))
    s.panel(sash, C['rib'], 'crackle')
    # 斜带里一条点缀细线
    pip = k.clip(sl.offset_curve(-7).buffer(1.6, cap_style=1), 0.6)
    s.panel(pip, C['accent'], stitch=(), shadow=False, lw=.45)
    cage = k.clip(Polygon(spline([(238, 60), (240, 125), (244, 180), (246, 236), (244, 280), (232, 312), (210, 330)], steps=14)
                          + [(150, 330), (100, 200), (150, 60)]).buffer(0))
    s.panel(cage, C['cage'], 'crackle')
    toe = k.clip(Polygon(spline([(20, 380), (70, 386), (104, 400), (124, 428), (130, 456), (130, 520)], steps=14) + [(20, 520)]).buffer(0))
    s.panel(toe, C['toe'], 'crackle')
    badge = Point(338, 166).buffer(16, quad_segs=24)
    s.panel(badge, C['plate'], stitch=(1.6, 3.0))
    s.mono(338, 166, 14, C['mark'])
    q0 = sl.interpolate(0.46, normalized=True); q1 = sl.interpolate(0.52, normalized=True)
    s.wordmark(q0.x, q0.y, 5.6, C['ribmark'], rot=math.degrees(math.atan2(q0.y - q1.y, q0.x - q1.x)))
    s.mono(414, 410, 11, C['heelmark'])
    s.finish('line')
    return s

# ============ B 棱面：直线和折角；后跟两片尖楔往前收，指向脚踝 ============
def facet(C, uid):
    s = Sheet(K, C, uid); k = K
    s.begin()
    upper = k.clip(Polygon([(236, 60), (236, 252), (460, 214), (460, 60)]), 1.4)
    s.panel(upper, C['quarter'], stitch=(1.6, 3.0))
    hexw = rounded(Polygon([(290, 150), (334, 144), (358, 170), (350, 204), (306, 210), (282, 186)]), 2)
    s.add(f'<path d="{D(hexw)}" fill="{C["vent"]}"/><path d="{D(hexw)}" fill="url(#{s.u("hexmesh")})"/>')
    s.add(f'<path d="{D(hexw.buffer(2.2, join_style=2))}" fill="none" stroke="{C["stitch"]}" stroke-width=".28" stroke-dasharray="2.2 .6"/>')
    s.add(f'<path d="{D(hexw)}" fill="none" stroke="{C["line"]}" stroke-width=".7"/>')
    mud = k.clip(Polygon([(120, 412), (210, 426), (300, 428), (380, 420), (460, 404), (460, 560), (120, 560)]), 1.2)
    s.panel(mud, C['toe'], 'crackle')
    s.panel(k.clip(Polygon(spline(COLLAR, steps=14)).buffer(0)), C['collar'], stitch=(2.0,))
    s.panel(k.clip(Polygon([(460, 92), (382, 100), (386, 200), (392, 262), (460, 252)]), 1.2), C['spine'], 'crackle')
    # 平行细条：贴着大楔片上沿
    stripe = k.clip(Polygon([(252, 290), (470, 316), (470, 322), (252, 296)]), 0.5)
    s.panel(stripe, C['accent'], stitch=(), lw=.45)
    # 大楔片：从后跟往前收成尖角
    dart = k.clip(Polygon([(470, 330), (258, 306), (330, 480), (470, 480)]), 1.8)
    s.panel(dart, C['wing'], 'crackle')
    # 小楔片：压在大楔片里，尖角往后退一点
    dart2 = k.clip(Polygon([(470, 372), (306, 346), (366, 480), (470, 480)]), 1.6)
    s.panel(dart2, C['wing2'], stitch=(1.5, 3.0))
    cage = k.clip(Polygon([(238, 60), (240, 150), (232, 162), (238, 232), (226, 244), (232, 300), (206, 334), (150, 360), (110, 376),
                           (60, 384), (100, 200), (150, 60)]), 1.4)
    s.panel(cage, C['cage'], 'crackle')
    toe = k.clip(Polygon([(20, 376), (100, 378), (134, 394), (120, 412), (156, 452), (156, 520), (20, 520)]), 1.4)
    s.panel(toe, C['toe'], 'crackle')
    s.holes([(104 + 3.6 * j, 398 + 5.5 * j) for j in range(4)] + [(116 + 3.6 * j, 396 + 5.5 * j) for j in range(4)], 1.0)
    plate = rounded(Polygon([(306, 162), (330, 158), (340, 176), (334, 194), (310, 198), (300, 180)]), 1.5)
    s.panel(plate, C['plate'], stitch=(1.3,))
    s.mono(320, 178, 15, C['mark'])
    s.wordmark(398, 448, 5.4, C['wingmark'], rot=0)
    s.finish('rails')
    return s

# ============ C 绑带：外露的锁跟绑带，两条织带从后跟往前包住脚踝 ============
def harness(C, uid):
    s = Sheet(K, C, uid); k = K
    s.begin()
    upper = k.clip(Polygon(spline([(236, 250), (290, 246), (350, 242), (440, 236)], steps=12) + [(440, 60), (236, 60)]).buffer(0))
    s.panel(upper, C['quarter'], stitch=(1.6, 3.0))
    # 上鞋身横向绗缝（软垫）
    for y0 in (172, 196, 220):
        s.seam([(244, y0 + 6), (300, y0 + 2), (360, y0 - 2), (384, y0 - 3)], double=False)
    mud = k.clip(below([(120, 412), (176, 423), (220, 429), (270, 431), (330, 427), (390, 419), (440, 411)], 120, 440), 1.2)
    s.panel(mud, C['toe'], 'crackle')
    s.panel(k.clip(Polygon(spline(COLLAR, steps=14)).buffer(0)), C['collar'], stitch=(2.0,))
    s.panel(k.clip(Polygon(spline([(430, 92), (382, 100), (384, 170), (390, 250), (430, 250)], steps=10)).buffer(0)), C['spine'], 'crackle')
    # 后跟杯
    heel = k.clip(Polygon(spline([(440, 470), (336, 470), (338, 430), (346, 384), (360, 340), (382, 312), (440, 302)], steps=14)
                          + [(460, 300)]).buffer(0))
    s.panel(heel, C['heel'], 'crackle')
    # 两条织带：后跟出发，一条往前上去鞋带区，一条往前下去脚背
    S1 = [(392, 332), (350, 318), (306, 290), (268, 254), (240, 226)]
    S2 = [(394, 372), (352, 368), (304, 356), (262, 340), (226, 330)]
    for pts in (S1, S2):
        band = k.clip(strip(pts, 15), 1.0)
        s.panel(band, C['web'], 'web', stitch=(1.4,))
    # 织带锚点：方框 + 交叉缝
    for (pts, t) in ((S1, 0.08), (S2, 0.08)):
        ln = LineString(spline(pts, steps=16)); p = ln.interpolate(t, normalized=True); q = ln.interpolate(t + 0.06, normalized=True)
        ang = math.degrees(math.atan2(q.y - p.y, q.x - p.x))
        bx = affinity.rotate(box(p.x - 6, p.y - 4.6, p.x + 6, p.y + 4.6), ang, origin=p)
        cs = list(bx.exterior.coords)
        s.add(f'<path d="{ld(cs)}Z{ld([cs[0], cs[2]])}{ld([cs[1], cs[3]])}" fill="none" stroke="{C["stitch"]}" stroke-width=".4"/>')
    # 织带穿过鞋带区前的金属扣
    for (x, y, a) in ((244, 228, 48), (230, 330, 10)):
        ring = affinity.rotate(rounded(box(x - 3, y - 10, x + 3, y + 10), 2.5).difference(rounded(box(x - 1.2, y - 7.5, x + 1.2, y + 7.5), 1)), a, origin=(x, y))
        s.panel(ring, C['metal'], stitch=(), shadow=True, lw=.5)
    cage = k.clip(Polygon(spline([(238, 60), (240, 125), (244, 180), (248, 236), (248, 280), (236, 318), (200, 342), (150, 362),
                                  (110, 376)], steps=14) + [(60, 384), (100, 200), (150, 60)]).buffer(0))
    s.panel(cage, C['cage'], 'crackle')
    toe = k.clip(Polygon(spline([(20, 376), (96, 378), (124, 390), (140, 418), (146, 452), (146, 520)], steps=14) + [(20, 520)]).buffer(0))
    s.panel(toe, C['toe'], 'crackle')
    badge = rounded(box(318, 132, 352, 150), 3)
    s.panel(badge, C['plate'], stitch=(1.3,))
    s.wordmark(335, 141, 5.4, C['mark'])
    s.mono(410, 386, 12, C['heelmark'])
    # 字标印在上面那条织带上
    ln = LineString(spline(S1, steps=16)); p = ln.interpolate(0.5, normalized=True); q = ln.interpolate(0.56, normalized=True)
    s.wordmark(p.x, p.y, 4.6, C['webmark'], rot=math.degrees(math.atan2(p.y - q.y, p.x - q.x)))
    s.finish('tp')
    return s

# ============ D 等高线：几层压片像等高线一样往上叠，往后跟方向抬高 ============
def contour(C, uid):
    s = Sheet(K, C, uid); k = K
    s.begin()
    W = [
        [(20, 384), (120, 400), (220, 412), (320, 410), (400, 392), (460, 380)],   # 第 1 层上沿（最低）
        [(20, 372), (130, 378), (220, 372), (300, 352), (370, 330), (460, 318)],
        [(140, 352), (210, 330), (270, 300), (330, 276), (390, 262), (460, 256)],
        [(230, 268), (280, 238), (340, 216), (400, 206), (460, 202)],
    ]
    layers = [k.clip(below(w), 1.4) for w in W]
    fills = [C['l4'], C['l3'], C['l2'], C['l1']]       # 最上面一层最浅，往下越来越深
    texs = [None, None, None, 'crackle']
    # 从最上面那层（覆盖面积最大）往下压，下面的层压在上面
    for g, f, t in zip(layers[::-1], fills, texs):
        s.panel(g, f, t, stitch=(1.6, 3.0))
    s.panel(k.clip(Polygon(spline(COLLAR, steps=14)).buffer(0)), C['collar'], stitch=(2.0,))
    # 顶上一块梯形网布窗 + 徽章
    win = rounded(Polygon([(296, 150), (356, 142), (364, 186), (306, 196)]), 3)
    s.add(f'<path d="{D(win)}" fill="{C["vent"]}"/><path d="{D(win)}" fill="url(#{s.u("mesh")})"/>')
    s.add(f'<path d="{D(win.buffer(2.2, join_style=1))}" fill="none" stroke="{C["stitch"]}" stroke-width=".28" stroke-dasharray="2.2 .6"/>')
    s.add(f'<path d="{D(win)}" fill="none" stroke="{C["line"]}" stroke-width=".7"/>')
    s.panel(k.clip(Polygon(spline([(430, 92), (382, 100), (384, 170), (388, 206), (430, 206)], steps=10)).buffer(0)), C['spine'], 'crackle')
    cage = k.clip(Polygon(spline([(238, 60), (240, 125), (244, 180), (248, 236), (248, 280), (236, 318), (200, 342), (150, 362),
                                  (110, 376)], steps=14) + [(60, 384), (100, 200), (150, 60)]).buffer(0))
    s.panel(cage, C['cage'], 'crackle')
    toe = k.clip(Polygon(spline([(20, 370), (90, 372), (122, 386), (138, 414), (144, 452), (144, 520)], steps=14) + [(20, 520)]).buffer(0))
    s.panel(toe, C['toe'], 'crackle')
    plate = rounded(Polygon([(318, 158), (340, 155), (343, 180), (321, 183)]), 2)
    s.panel(plate, C['plate'], stitch=(1.3,))
    s.mono(330.5, 169, 16, C['mark'])
    # 每层边上沿一排小孔（最底下两层）
    for w, off in ((W[1], 6), (W[2], 6)):
        ln = LineString(spline(w, steps=16)).offset_curve(-off)
        pts = [ln.interpolate(ln.length * (0.38 + 0.03 * j)) for j in range(8)]
        s.holes([(p.x, p.y) for p in pts if p.within(k.sil.buffer(-3))], 0.9)
    s.wordmark(372, 360, 5.0, C['l2mark'], rot=-17)
    s.mono(408, 400, 11, C['heelmark'])
    s.finish('line')
    return s

# ============ 配色 ============
WHITE = dict(quarter='#FFFFFF', quarter2='#FFFFFF', vent='#FFFFFF', rib='#FFFFFF', accent='#FFFFFF', collar='#FFFFFF',
             spine='#FFFFFF', cage='#FFFFFF', toe='#FFFFFF', plate='#FFFFFF', ribmark='#111111', wing='#FFFFFF',
             wing2='#FFFFFF', wingmark='#111111', heel='#FFFFFF', web='#FFFFFF', metal='#FFFFFF', heelmark='#111111',
             webmark='#111111', l1='#FFFFFF', l2='#FFFFFF', l3='#FFFFFF', l4='#FFFFFF', l2mark='#111111')
STYLES = {
    'A': (flow, '流线', palette(**WHITE),
          palette(**{**WHITE, 'base': '#F3F2EE', 'quarter': '#F3F2EE', 'quarter2': '#F3F2EE', 'heel': '#68747A', 'heelmark': '#F3F2EE',
                     'vent': '#DCDAD3', 'rib': '#68747A', 'accent': '#C2D8C5',
                     'collar': '#68747A', 'spine': '#68747A', 'cage': '#68747A', 'toe': '#68747A', 'plate': '#151617',
                     'mark': '#C2D8C5', 'ribmark': '#F3F2EE', 'loop': '#C2D8C5', 'mid': '#F3F2EE', 'out': '#3B4246',
                     'boa': '#2E3134', 'boa_dark': '#151617', 'tex': 'rgba(255,255,255,.06)', 'stitch': 'rgba(0,0,0,.5)',
                     'shadow': 'rgba(0,0,0,.16)', 'hole': '#2B3033', 'meshline': '#B9BDC2'})),
    'B': (facet, '棱面', palette(**WHITE),
          dark_palette(**{**WHITE, 'base': '#26282B', 'quarter': '#26282B', 'quarter2': '#68747A', 'vent': '#1F2123', 'collar': '#151617',
                          'spine': '#151617', 'cage': '#151617', 'toe': '#151617', 'wing': '#151617', 'wing2': '#68747A',
                          'accent': '#C2D8C5', 'plate': '#68747A', 'mark': '#151617', 'wingmark': '#C2D8C5', 'loop': '#C2D8C5',
                          'mid': '#F3F2EE'})),
    'C': (harness, '绑带', palette(**WHITE),
          dark_palette(**{**WHITE, 'base': '#68747A', 'quarter': '#68747A', 'collar': '#151617', 'spine': '#151617', 'heel': '#151617',
                          'cage': '#151617', 'toe': '#151617', 'web': '#C2D8C5', 'webline': 'rgba(0,0,0,.10)', 'metal': '#B9BDC0',
                          'plate': '#151617', 'mark': '#C2D8C5', 'heelmark': '#C2D8C5', 'webmark': '#151617', 'loop': '#C2D8C5',
                          'mid': '#F3F2EE', 'stitch': 'rgba(255,255,255,.5)'})),
    'D': (contour, '等高线', palette(**WHITE),
          dark_palette(**{**WHITE, 'base': '#B9C4C8', 'l4': '#B9C4C8', 'l3': '#8F9CA2', 'l2': '#68747A', 'l1': '#454E53',
                          'vent': '#A7B3B8', 'collar': '#151617', 'spine': '#151617', 'cage': '#151617', 'toe': '#151617',
                          'plate': '#151617', 'mark': '#C2D8C5', 'l2mark': '#F3F2EE', 'heelmark': '#C2D8C5', 'loop': '#C2D8C5',
                          'mid': '#F3F2EE', 'meshline': 'rgba(0,0,0,.14)', 'stitch': 'rgba(255,255,255,.55)'})),
}

if __name__ == '__main__':
    for key, (fn, name, white, color) in STYLES.items():
        for tag, C in (('tp', white), ('color', color)):
            sh = fn(C, f'{key}{tag}')
            open(f'{OUT}/v5-{key}-{tag}.svg', 'w').write(sh.svg())
        print('ok', key, name)
