"""提案 09：结构草图（铅笔草图风格）。双扣（ATOP 原厂旋钮，不印 logo）。
重点是结构：分片层次、RAIL 护条、双扣分区和走线、锁跟织带、内部加强件、内胆。
输出几张独立的 SVG，由 sheet9.py 排版。TP 坐标（鞋头朝左）。
usage: sketch9.py tp.json mono.json word.json outdir"""
import sys, math
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
from tpkit import Kit, spline, rounded, D, ld
from geom import to_poly

K = Kit(*sys.argv[1:4])
OUT = sys.argv[4]
sil = K.sil
mid = K.mid
out = to_poly(K.tp['P:2163']['d'])

PEN = '#3A3A3A'          # 铅笔
LIGHT = '#9A9A9A'
BLUE = '#2B63C6'         # 下区（前旋钮）
RED = '#C8402A'          # 上区 + 锁跟（侧旋钮）
WEB = '#D98A1F'          # 锁跟织带
NOTE = '#2B4FA0'         # 标注

def smooth(g, r=5):
    return g.buffer(r, join_style=1, quad_segs=16).buffer(-2 * r, join_style=1, quad_segs=16).buffer(r, join_style=1, quad_segs=16)

# ---------------- 结构几何 ----------------
DIAL_F = (186, 191)                 # 前旋钮（TP 位置，下区）
DIAL_S = (299.2, 175.2)             # 侧旋钮（TP 位置，上区 + 锁跟）
TOE = [(40, 386), (86, 390), (116, 402), (134, 422), (140, 452), (140, 520)]
toe = smooth(Polygon(spline(TOE, steps=16) + [(20, 520), (20, 380)]).buffer(0).intersection(sil), 3)
MUD = [(118, 420), (180, 428), (250, 432), (320, 428), (368, 416), (402, 394)]
mud = Polygon(spline(MUD, steps=16) + [(470, 380), (470, 560), (100, 560)]).buffer(0)
RISE = [(410, 392), (412, 352), (400, 306), (376, 262), (346, 222), (318, 192)]
rl = LineString(spline(RISE, steps=20))
rise = unary_union([Point(rl.interpolate(j / 60, normalized=True)).buffer(17 - 4 * j / 60) for j in range(61)])
plate = Point(*DIAL_S).buffer(26, quad_segs=32)
rail = smooth(unary_union([mud, rise, plate, toe]).intersection(sil.buffer(-0.01)), 5).intersection(sil)
CAGE = [(262, 96), (266, 160), (266, 222), (270, 272), (266, 312), (246, 342), (208, 364), (166, 378), (126, 388), (60, 396)]
cage = smooth(Polygon(spline(CAGE, steps=16) + [(20, 400), (20, 60)]).buffer(0).intersection(sil), 3)
COLLAR = [(228, 60), (228, 134), (262, 139), (300, 141), (338, 138), (370, 128), (393, 116), (430, 104), (430, 60)]
collar = smooth(Polygon(spline(COLLAR, steps=14)).buffer(0).intersection(sil), 2).difference(cage)
SPINE = [(430, 96), (384, 104), (388, 170), (396, 240), (404, 300), (430, 300)]
spine = smooth(Polygon(spline(SPINE, steps=14)).buffer(0).intersection(sil), 2)
def _back_x(y):
    hit = sil.exterior.intersection(LineString([(300, y), (480, y)]))
    return max(p.x for p in getattr(hit, 'geoms', [hit]))
_xb = _back_x(270)
notch = Polygon([(_xb + 1, 262), (_xb - 13, 270), (_xb + 1, 278)])           # 后背弯折缺口（切进后背）
# 鞋舌：前缘一条（在护片下面露出一点）
TONGUE_EDGE = [(226, 96), (230, 160), (226, 230), (214, 290), (190, 330), (150, 356), (110, 372)]
# 内部加强件（虚线）
heel_counter = smooth(Polygon(spline([(424, 470), (352, 470), (356, 420), (368, 372), (392, 340), (424, 332)], steps=12)).buffer(0)
                      .intersection(sil.buffer(-3)), 3)
toe_puff = smooth(Polygon(spline([(40, 400), (80, 402), (104, 416), (112, 440), (112, 470)], steps=12) + [(30, 470)]).buffer(0)
                  .intersection(sil.buffer(-3)), 3)

# 下区走线（前旋钮）：沿鞋带区往下，护片前缘和鞋舌中线之间来回
# 鞋带区前缘（脚背到小腿前面那段轮廓）：钢丝在这里翻过鞋舌到内侧
_pts = [p for p in sil.exterior.coords if p[0] < 260 and 236 < p[1] < 376]
_thr = []
for p in sorted(_pts, key=lambda p: p[1]):
    # 同一高度只留最靠前（左上）的那个点
    if not _thr or abs(p[1] - _thr[-1][1]) > .5:
        _thr.append(p)
throat = LineString(_thr)

def _inset(t, d):
    """鞋带区前缘上第 t（0–1）处，往鞋里面缩 d"""
    q = throat.interpolate(t, normalized=True)
    a_ = throat.interpolate(max(0, t - .02), normalized=True); b_ = throat.interpolate(min(1, t + .02), normalized=True)
    tx, ty = b_.x - a_.x, b_.y - a_.y; n = math.hypot(tx, ty); nx, ny = -ty / n, tx / n
    if not sil.contains(Point(q.x + nx * 4, q.y + ny * 4)): nx, ny = -nx, -ny
    return (q.x + nx * d, q.y + ny * d)
TS = [0.08, 0.28, 0.48, 0.68, 0.88]
G_TON = [_inset(t, 2.5) for t in TS]                                   # 鞋舌一侧（钢丝从这里翻到内侧）
G_LAT = [_inset(t + 0.1, 24) for t in TS]                              # 护片上的导向扣
lower_cable = [DIAL_F, (206, 214)]
for a, b in zip(G_LAT, G_TON):
    lower_cable += [a, b]
# 上区 + 锁跟走线（侧旋钮）：往前到小腿两个导向扣，绕过鞋舌；往下到脚背的锁跟环
G_SHIN = [(258, 146), (258, 206)]
RING = (238, 300)                                                        # 锁跟环（织带在脚背交汇处）
upper_cable_a = [DIAL_S, (276, 162), G_SHIN[0], (226, 140)]              # 绕小腿上段
upper_cable_b = [DIAL_S, (282, 196), G_SHIN[1], (226, 214)]
lock_cable = [DIAL_S, (300, 230), (268, 268), RING]                      # 拉锁跟环
# 锁跟织带：从后跟两侧的锚点（RAIL 上）斜着往前上，绕过脚踝前面，在脚背交汇
ANCHOR = (388, 372)
harness = LineString(spline([ANCHOR, (350, 350), (306, 326), (268, 308), RING], steps=16))

# ---------------- 草图笔触 ----------------
class SK:
    def __init__(self, vb, w):
        self.vb, self.w = vb, w
        self.layers = {}
    def line(self, d, color=PEN, sw=0.8, dash=None, op=1.0, layer='pen'):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        self.layers.setdefault(layer, []).append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-opacity="{op}"{da} stroke-linecap="round" stroke-linejoin="round"/>')
    def geom(self, g, **kw):
        for p in getattr(g, 'geoms', [g]):
            if p.is_empty: continue
            if p.geom_type == 'Polygon':
                self.line(ld(list(p.exterior.coords)) + 'Z', **kw)
                for r in p.interiors: self.line(ld(list(r.coords)) + 'Z', **kw)
            elif p.geom_type == 'LineString':
                self.line(ld(list(p.coords)), **kw)
    def pts(self, pts, **kw):
        self.line(ld(pts), **kw)
    def raw(self, s, layer='ink'):
        self.layers.setdefault(layer, []).append(s)
    def hatch(self, g, gap=3.0, ang=45, color=LIGHT, sw=0.35, layer='hatch'):
        """在区域里画平行排线（阴影）"""
        b = g.bounds; cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2; R = math.hypot(b[2] - b[0], b[3] - b[1])
        a = math.radians(ang); dx, dy = math.cos(a), math.sin(a); nx, ny = -dy, dx
        k = -R
        while k < R:
            ln = LineString([(cx + nx * k - dx * R, cy + ny * k - dy * R), (cx + nx * k + dx * R, cy + ny * k + dy * R)]).intersection(g)
            for s in getattr(ln, 'geoms', [ln]):
                if s.geom_type == 'LineString' and s.length > 1:
                    self.line(ld(list(s.coords)), color=color, sw=sw, layer=layer)
            k += gap
    def note(self, k, tx, ty, lx, ly, color=NOTE):
        """编号标注：目标点 → 圆圈编号"""
        self.raw(f'<path d="M{tx} {ty}L{lx} {ly}" stroke="{color}" stroke-width=".55" fill="none"/>'
                 f'<circle cx="{tx}" cy="{ty}" r="1.4" fill="{color}"/>'
                 f'<circle cx="{lx}" cy="{ly}" r="6" fill="#FBFAF6" stroke="{color}" stroke-width=".9"/>'
                 f'<text x="{lx}" y="{ly + 2.4}" text-anchor="middle" class="nn" fill="{color}">{k}</text>', layer='notes')
    def svg(self):
        vb = self.vb; h = self.w * vb[3] / vb[2]
        f = ('<defs>'
             '<filter id="rough1" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".06" numOctaves="2" seed="3" result="n"/>'
             '<feDisplacementMap in="SourceGraphic" in2="n" scale="1.5"/></filter>'
             '<filter id="rough2" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".05" numOctaves="2" seed="11" result="n"/>'
             '<feDisplacementMap in="SourceGraphic" in2="n" scale="2.2"/></filter>'
             '</defs>')
        body = ''
        L = self.layers
        body += f'<g filter="url(#rough1)" opacity=".9">{"".join(L.get("hatch", []))}</g>'
        pen = ''.join(L.get('pen', []))
        body += f'<g filter="url(#rough2)" opacity=".35">{pen}</g><g filter="url(#rough1)">{pen}</g>'
        body += f'<g filter="url(#rough1)">{"".join(L.get("ink", []))}</g>'
        body += ''.join(L.get('notes', []))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(map(str, vb))}" width="{self.w}" height="{h:.1f}">'
                + f + body + '</svg>')

def tp_line(s, i, **kw):
    s.line(K.tp[i]['d'], **kw)

def boot_base(s, ghost=False):
    """轮廓、内胆、提拉环、中底大底、前旋钮（TP 形状）"""
    c = LIGHT if ghost else PEN
    for i in ['P:596', 'P:651', 'P:623', 'P:676', 'P:712', 'P:739']:
        tp_line(s, i, color=c, sw=.6)
    s.geom(sil, color=c, sw=1.0 if not ghost else .7)
    tp_line(s, 'P:1993', color=c, sw=.8)
    tp_line(s, 'P:2163', color=c, sw=.8)
    s.hatch(out.difference(mid), gap=2.2, ang=60, color=c, sw=.35)
    for x in K.items:                                    # 前旋钮（ATOP，原厂外观，TP 原图）
        n = int(x['id'].split(':')[-1]) if x['id'].startswith('P:') else -1
        if 20 <= n <= 595 and x['d'] and (x['stroke'] or x['fill']):
            s.line(x['d'], color=c, sw=.5 if x['fill'] else .4)
    tp_line(s, 'P:1758', color=c, sw=.6)                # 魔术贴

def side_dial(s, color=PEN, R=17.5):
    cx, cy = DIAL_S
    s.raw(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{color}" stroke-width=".8"/>'
          f'<circle cx="{cx}" cy="{cy}" r="{R - 3.2}" fill="none" stroke="{color}" stroke-width=".6"/>'
          f'<circle cx="{cx}" cy="{cy}" r="{R - 6.4}" fill="none" stroke="{color}" stroke-width=".5"/>')
    for j in range(24):
        a = 2 * math.pi * j / 24
        s.raw(f'<line x1="{cx + (R - 6.2) * math.cos(a):.2f}" y1="{cy + (R - 6.2) * math.sin(a):.2f}" x2="{cx + (R - 3.4) * math.cos(a):.2f}" '
              f'y2="{cy + (R - 3.4) * math.sin(a):.2f}" stroke="{color}" stroke-width=".3"/>')
    w = affinity.rotate(rounded(box(cx - 9.5, cy - 2.6, cx + 9.5, cy + 2.6), 2.4), -30, origin=(cx, cy))
    s.geom(w, color=color, sw=.55, layer='ink')

# ================= 图 1：外侧结构总览 =================
def fig_structure():
    s = SK((20, 40, 440, 470), 880)
    boot_base(s)
    # 分片
    s.geom(rail, sw=1.1)
    s.hatch(rail.difference(plate.buffer(-6)), gap=3.4, ang=40, color='#B5B5B5', sw=.3)
    for inset in (1.8,):
        s.geom(rail.buffer(-inset, join_style=1), color=PEN, sw=.35, dash='2 1.2')
    s.geom(cage, sw=1.0)
    s.geom(cage.buffer(-1.8, join_style=1), sw=.35, dash='2 1.2')
    s.geom(collar, sw=.9)
    s.geom(spine, sw=.9)
    s.geom(notch, sw=.8)
    s.pts(spline(TONGUE_EDGE, steps=12), sw=.7)
    # 外侧主片的分割缝：一道沿 RAIL 内侧的回声缝，一道上下分割
    echo = rail.buffer(14, join_style=1, quad_segs=16).boundary.intersection(sil.buffer(-2)).difference(cage.buffer(2))
    s.geom(echo, sw=.6)
    s.geom(echo.buffer(1.6).boundary.intersection(sil.buffer(-3)).difference(rail.buffer(15.2)), sw=.3, dash='2 1.2')
    s.pts(spline([(266, 252), (304, 244), (344, 238), (392, 236)], steps=10), sw=.6)
    # 内部加强件（虚线）
    s.geom(heel_counter, color=LIGHT, sw=.7, dash='4 2.5')
    s.geom(toe_puff, color=LIGHT, sw=.7, dash='4 2.5')
    # 导向扣
    for (x, y) in G_LAT + G_SHIN:
        s.raw(f'<rect x="{x - 3.2}" y="{y - 1.6}" width="6.4" height="3.2" rx="1.6" fill="#FBFAF6" stroke="{PEN}" stroke-width=".5" transform="rotate(-40 {x} {y})"/>')
    side_dial(s)
    # 鞋舌弯折槽
    for t in (0.52, 0.58, 0.64):
        p = LineString(spline(TONGUE_EDGE, steps=12)).interpolate(t, normalized=True)
        s.pts([(p.x - 12, p.y - 6), (p.x + 4, p.y + 6)], sw=.5)
    # 标注
    N = [(1, 340, 434, 300, 470), (2, 299, 152, 326, 120), (3, 178, 196, 140, 186), (4, 238, 260, 200, 230),
         (5, 214, 290, 176, 270), (6, 320, 300, 300, 290), (7, 330, 124, 360, 86), (8, 412, 270, 446, 262),
         (9, 404, 150, 446, 150), (10, 240, 72, 210, 60), (11, 220, 478, 180, 498), (12, 400, 420, 446, 420)]
    for k, tx, ty, lx, ly in N:
        s.note(k, tx, ty, lx, ly)
    return s.svg()

# ================= 图 2：双扣系统（外侧） =================
def fig_closure():
    s = SK((20, 40, 440, 470), 880)
    boot_base(s, ghost=True)
    s.geom(rail, color=LIGHT, sw=.7)
    s.geom(cage, color=LIGHT, sw=.6)
    s.pts(spline(TONGUE_EDGE, steps=12), color=LIGHT, sw=.5)
    # 锁跟织带（橙）
    s.geom(harness.buffer(4.2, cap_style=2), color=WEB, sw=.9, layer='ink')
    s.hatch(harness.buffer(4.2, cap_style=2), gap=1.6, ang=-30, color=WEB, sw=.35)
    s.raw(f'<rect x="{ANCHOR[0] - 6}" y="{ANCHOR[1] - 5}" width="12" height="10" fill="none" stroke="{WEB}" stroke-width=".8"/>'
          f'<path d="M{ANCHOR[0] - 6} {ANCHOR[1] - 5}L{ANCHOR[0] + 6} {ANCHOR[1] + 5}M{ANCHOR[0] + 6} {ANCHOR[1] - 5}L{ANCHOR[0] - 6} {ANCHOR[1] + 5}" stroke="{WEB}" stroke-width=".5"/>')
    s.raw(f'<circle cx="{RING[0]}" cy="{RING[1]}" r="4.6" fill="#FBFAF6" stroke="{RED}" stroke-width="1.1"/>')
    # 下区钢丝（蓝）
    s.pts(lower_cable, color=BLUE, sw=1.2, layer='ink')
    for (x, y) in G_LAT + G_TON:
        s.raw(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#FBFAF6" stroke="{BLUE}" stroke-width=".8"/>')
    s.raw(f'<circle cx="{DIAL_F[0]}" cy="{DIAL_F[1]}" r="9" fill="none" stroke="{BLUE}" stroke-width="1.6"/>')
    # 上区 + 锁跟钢丝（红）
    for c in (upper_cable_a, upper_cable_b, lock_cable):
        s.pts(spline(c, steps=8), color=RED, sw=1.2, layer='ink')
    for (x, y) in G_SHIN + [(300, 230), (268, 268)]:
        s.raw(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#FBFAF6" stroke="{RED}" stroke-width=".8"/>')
    side_dial(s, color=RED)
    # 受力箭头：脚跟被往后、往下压进后跟杯
    def arrow(x0, y0, x1, y1, col):
        a = math.atan2(y1 - y0, x1 - x0)
        s.raw(f'<path d="M{x0} {y0}L{x1} {y1}M{x1} {y1}L{x1 - 6 * math.cos(a - .45):.1f} {y1 - 6 * math.sin(a - .45):.1f}'
              f'M{x1} {y1}L{x1 - 6 * math.cos(a + .45):.1f} {y1 - 6 * math.sin(a + .45):.1f}" stroke="{col}" stroke-width="1.3" fill="none"/>')
    arrow(330, 360, 372, 392, WEB)
    arrow(262, 334, 292, 360, WEB)
    # 区域说明（手写感文字放在 sheet 里，这里只放分区底色）
    zone_low = Polygon([(100, 240), (250, 225), (262, 360), (110, 400)])
    zone_up = Polygon([(220, 110), (300, 110), (300, 236), (220, 236)])
    return s.svg()

# ================= 图 3：正面（脚背锁跟织带怎么包） =================
def fig_front():
    s = SK((-90, 40, 180, 470), 360)
    # 正面轮廓：鞋筒上口是领口软垫，往下收到脚踝，再放宽成鞋头
    shell = Polygon(spline([(-50, 104), (-52, 200), (-50, 290), (-58, 350), (-68, 400), (-72, 440), (-66, 470), (66, 470), (72, 440),
                            (68, 400), (58, 350), (50, 290), (52, 200), (50, 104), (30, 98), (0, 102), (-30, 98)], closed=True, steps=10)).buffer(0)
    s.geom(shell, sw=1.0)
    s.pts(spline([(-50, 112), (-28, 106), (0, 110), (28, 106), (50, 112)], steps=8), sw=.6)          # 领口软垫
    s.pts(spline([(-66, 452), (-40, 420), (0, 410), (40, 420), (66, 452)], steps=8), sw=.7)          # 鞋头包头
    s.pts(spline([(-58, 350), (-30, 362), (0, 366), (30, 362), (58, 350)], steps=8), sw=.4, dash='3 2')  # 脚背弯折
    s.pts([(-66, 470), (-70, 488), (70, 488), (66, 470)], sw=.9)
    s.hatch(Polygon([(-70, 478), (70, 478), (70, 488), (-70, 488)]), gap=2.2, ang=60, sw=.35)
    tongue = Polygon(spline([(-22, 70), (-24, 200), (-26, 330), (-30, 420), (0, 438), (30, 420), (26, 330), (24, 200), (22, 70)], steps=10)).buffer(0)
    s.geom(tongue, sw=.9)
    s.pts([(-18, 300), (18, 300)], sw=.4); s.pts([(-19, 312), (19, 312)], sw=.4); s.pts([(-20, 324), (20, 324)], sw=.4)
    # 上区：小腿两圈钢丝
    for y in (146, 206):
        s.pts([(-54, y + 6), (-30, y), (0, y - 2), (30, y), (54, y + 6)], color=RED, sw=1.2, layer='ink')
    # 下区：鞋舌两侧来回
    zig = [(0, 150)]
    for k, y in enumerate(range(230, 420, 30)):
        zig += [(-30 - k * .8, y), (30 + k * .8, y + 15)]
    s.pts(zig[1:], color=BLUE, sw=1.1, layer='ink')
    s.raw(f'<circle cx="0" cy="190" r="10" fill="none" stroke="{BLUE}" stroke-width="1.6"/>')
    # 锁跟织带：两边从后跟上来，在脚背 V 形交汇于锁跟环
    for sgn in (-1, 1):
        band = LineString([(sgn * 62, 372), (sgn * 40, 336), (sgn * 12, 304)]).buffer(4.2, cap_style=2)
        s.geom(band, color=WEB, sw=.9, layer='ink')
        s.hatch(band, gap=1.6, ang=-30 * sgn, color=WEB, sw=.35)
    s.raw(f'<circle cx="0" cy="300" r="5.2" fill="#FBFAF6" stroke="{RED}" stroke-width="1.2"/>')
    s.pts([(4, 296), (34, 270), (56, 240)], color=RED, sw=1.2, layer='ink')                 # 拉到外侧旋钮
    s.raw(f'<circle cx="60" cy="176" r="9" fill="none" stroke="{RED}" stroke-width="1.6"/>')
    s.raw(f'<text x="-86" y="110" class="lab">内侧</text><text x="86" y="110" text-anchor="end" class="lab">外侧</text>')
    return s.svg()

# ================= 图 4：分层爆炸图 =================
def fig_layers():
    s = SK((0, 0, 1100, 300), 1100)
    sc = 0.5
    def place(g, dx, dy):
        return affinity.translate(affinity.scale(g, sc, sc, origin=(0, 0)), dx, dy)
    def place_d(d, dx, dy):
        return f'<g transform="translate({dx} {dy}) scale({sc})">'
    X = [0, 214, 428, 642, 856]
    Y = 30
    # ① 外层鞋面分片
    for g in (sil, cage, collar, spine):
        s.geom(place(g, X[0], Y), sw=.8)
    s.geom(place(rail.buffer(14, join_style=1).boundary.intersection(sil.buffer(-2)), X[0], Y), sw=.4)
    # ② RAIL 护条（TPU 一体）
    s.geom(place(rail, X[1], Y), sw=1.0)
    s.hatch(place(rail.difference(plate.buffer(-6)), X[1], Y), gap=2.4, ang=40, sw=.3)
    s.geom(place(sil, X[1], Y), color='#C8C8C8', sw=.5, dash='3 2')
    # ③ 锁跟织带 + 钢丝 + 两个旋钮
    s.geom(place(sil, X[2], Y), color='#C8C8C8', sw=.5, dash='3 2')
    s.geom(place(harness.buffer(4.2, cap_style=2), X[2], Y), color=WEB, sw=.8, layer='ink')
    s.pts([(X[2] + x * sc, Y + y * sc) for x, y in lower_cable], color=BLUE, sw=.9, layer='ink')
    for c in (upper_cable_a, upper_cable_b, lock_cable):
        s.pts([(X[2] + x * sc, Y + y * sc) for x, y in spline(c, steps=8)], color=RED, sw=.9, layer='ink')
    s.raw(f'<circle cx="{X[2] + DIAL_S[0] * sc}" cy="{Y + DIAL_S[1] * sc}" r="8" fill="none" stroke="{RED}" stroke-width="1.2"/>'
          f'<circle cx="{X[2] + DIAL_F[0] * sc}" cy="{Y + DIAL_F[1] * sc}" r="5" fill="none" stroke="{BLUE}" stroke-width="1.2"/>')
    # ④ 内部加强件：后跟杯、鞋头内衬、后背脊条（可换硬度）
    s.geom(place(sil, X[3], Y), color='#C8C8C8', sw=.5, dash='3 2')
    for g in (heel_counter, toe_puff):
        s.geom(place(g, X[3], Y), sw=.9)
        s.hatch(place(g, X[3], Y), gap=2.0, ang=-45, sw=.3)
    # ⑤ 内胆 + 鞋垫 + 中底大底
    # 内胆：比外壳小一圈，上口高出鞋筒（TP 的内胆领口）
    liner_top = unary_union([to_poly(K.tp[i]['d']) for i in ('P:623', 'P:676', 'P:712', 'P:739')])
    liner = smooth(unary_union([sil.buffer(-7, join_style=1), liner_top.buffer(1)]).intersection(box(0, 0, 480, 452)), 3)
    s.geom(place(liner, X[4], Y), sw=.9)
    s.geom(place(mid, X[4], Y + 14), sw=.8)
    s.geom(place(out.difference(mid), X[4], Y + 14), sw=.7)
    s.pts([(X[4] + 60 * sc, Y + 440 * sc), (X[4] + 400 * sc, Y + 440 * sc)], sw=.6, dash='3 2')
    for k in range(4):
        s.raw(f'<path d="M{X[k] + 216} 150 L{X[k] + 232} 150" stroke="{LIGHT}" stroke-width="1"/>'
              f'<path d="M{X[k] + 227} 146L{X[k] + 233} 150L{X[k] + 227} 154" stroke="{LIGHT}" stroke-width="1" fill="none"/>')
    return s.svg()

# ================= 图 5：脚踝横剖面（俯视） =================
def fig_section():
    s = SK((-130, -122, 260, 230), 520)
    shell = Point(0, 0).buffer(1, quad_segs=48)
    shell = affinity.scale(shell, 92, 74)
    liner_o = affinity.scale(Point(0, 0).buffer(1, quad_segs=48), 80, 62)
    liner_i = affinity.scale(Point(0, 0).buffer(1, quad_segs=48), 66, 50)
    s.geom(shell, sw=1.2)
    s.geom(affinity.scale(Point(0, 0).buffer(1, quad_segs=48), 88, 70), sw=.5)
    s.hatch(liner_o.difference(liner_i), gap=2.6, ang=30, sw=.3)
    s.geom(liner_o, sw=.8); s.geom(liner_i, sw=.8)
    # 脚踝（胫骨、腓骨、跟腱）
    s.raw(f'<ellipse cx="-14" cy="6" rx="18" ry="16" fill="none" stroke="{PEN}" stroke-width=".7"/>'
          f'<ellipse cx="34" cy="14" rx="8" ry="8" fill="none" stroke="{PEN}" stroke-width=".7"/>'
          f'<ellipse cx="6" cy="44" rx="10" ry="5" fill="none" stroke="{PEN}" stroke-width=".7"/>', layer='ink')
    # 鞋舌（前面，上方 = 前）
    tongue = affinity.scale(Point(0, -70).buffer(1, quad_segs=24), 34, 10)
    s.geom(tongue, sw=.9)
    # 锁跟织带：从后两侧锚点绕到前面，交在鞋舌上
    for sgn in (-1, 1):
        arc = [(sgn * 60, 48), (sgn * 80, 10), (sgn * 70, -40), (sgn * 30, -72), (sgn * 6, -80)]
        s.pts(spline(arc, steps=10), color=WEB, sw=2.4, op=.85, layer='ink')
    s.raw(f'<circle cx="0" cy="-82" r="4.6" fill="#FBFAF6" stroke="{RED}" stroke-width="1.2"/>')
    s.pts([(4, -84), (60, -76), (96, -50)], color=RED, sw=1.2, layer='ink')
    s.raw(f'<circle cx="100" cy="-44" r="8" fill="none" stroke="{RED}" stroke-width="1.6"/>')
    # 受力箭头
    for (x0, y0, x1, y1) in ((0, -96, 0, -84), (-50, 66, -40, 52), (50, 66, 40, 52)):
        s.raw(f'<path d="M{x0} {y0}L{x1} {y1}" stroke="{WEB}" stroke-width="1.4"/>')
    s.raw(f'<text x="0" y="-104" text-anchor="middle" class="lab">前（脚背）</text>'
          f'<text x="0" y="92" text-anchor="middle" class="lab">后（脚跟）</text>'
          f'<text x="-112" y="4" class="lab">内侧</text><text x="112" y="4" text-anchor="end" class="lab">外侧</text>')
    return s.svg()

if __name__ == '__main__':
    for name, fn in (('structure', fig_structure), ('closure', fig_closure), ('front', fig_front),
                     ('layers', fig_layers), ('section', fig_section)):
        open(f'{OUT}/s9-{name}.svg', 'w').write(fn())
        print('ok', name)
