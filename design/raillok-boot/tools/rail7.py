"""提案 07「一笔」：双扣（ATOP 原厂双旋钮，不印任何 logo）。
一条护条一笔画完：从鞋头后面沿底边往后（防泥条），绕过后跟（后跟杯），再顺着鞋筒斜着扫上去，
收进侧旋钮的底座——RAIL 一路走到 LOK。其余是大面积的同色磨砂皮，靠软阴影出体积。
画法照 TP，但阴影改成 TP 那种柔和的喷枪灰，不再用硬投影。TP 坐标，鞋头朝左。
usage: rail7.py tp.json mono.json word.json outdir"""
import sys, math
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
from tpkit import Kit, Sheet, spline, rounded, palette, dark_palette, D, ld

K = Kit(*sys.argv[1:4])
OUT = sys.argv[4]

DIAL_C, DIAL_R = (299.2, 175.2), 26.6        # TP 稿里侧旋钮的位置和外圈半径
SIDE_DIAL_IDS = ['P//Fm13:16', 'P:2533', 'P:2543', 'P:2555', 'P:2609', 'P:2663', 'P:2672', 'P:2682', 'P:2692', 'P:2704']
COLLAR = [(228, 60), (228, 134), (262, 139), (300, 141), (338, 138), (370, 128), (393, 116), (430, 104), (430, 60)]

def smooth(g, r=5):
    """内外拐角都倒圆，形状更顺"""
    return g.buffer(r, join_style=1, quad_segs=16).buffer(-2 * r, join_style=1, quad_segs=16).buffer(r, join_style=1, quad_segs=16)

class Soft(Sheet):
    """面片的阴影改成柔和的喷枪灰（模糊），面片边缘一圈轻微的体积暗角"""
    def soft_panel(self, g, fill, tex=None, stitch=(1.6, 3.0), shade=True, puff=0.10, lw=0.6):
        C = self.C
        if g is None or g.is_empty: return
        if shade:
            sh = affinity.translate(g, 1.0, 1.6)
            self.add(f'<g clip-path="url(#{self.u("sil")})"><path d="{D(sh)}" fill="#000" opacity="{C["shade"]}" filter="url(#{self.u("blur2")})"/></g>')
        self.add(f'<path d="{D(g)}" fill="{fill}"/>')
        if tex:
            self.add(f'<path d="{D(g)}" fill="url(#{self.u(tex)})"/>')
        if puff:
            cid = self.u(f'c{len(self.S)}')
            self.add(f'<clipPath id="{cid}"><path d="{D(g)}"/></clipPath>'
                     f'<g clip-path="url(#{cid})"><path d="{D(g)}" fill="none" stroke="#000" stroke-opacity="{puff}" '
                     f'stroke-width="7" filter="url(#{self.u("blur3")})"/></g>')
        for inset in stitch:
            s = g.buffer(-inset, join_style=1)
            if not s.is_empty:
                self.add(f'<path d="{D(s)}" fill="none" stroke="{C["stitch"]}" stroke-width=".26" stroke-dasharray="2 .6"/>')
        self.add(f'<path d="{D(g)}" fill="none" stroke="{C["line"]}" stroke-width="{lw}" stroke-linejoin="round"/>')

    def defs(self):
        d = super().defs()
        u = self.u
        extra = (f'<filter id="{u("blur2")}" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="1.5"/></filter>'
                 f'<filter id="{u("blur3")}" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="2.6"/></filter>'
                 f'<clipPath id="{u("sil")}"><path d="{D(self.k.sil)}"/></clipPath>'
                 f'<linearGradient id="{u("vol")}" x1="0" y1="0" x2="1" y2="1">'
                 f'<stop offset="0" stop-color="#fff" stop-opacity=".10"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/>'
                 f'<stop offset="1" stop-color="#000" stop-opacity=".10"/></linearGradient>')
        return d.replace('</defs>', extra + '</defs>')

def side_dial(s, C, cx=DIAL_C[0], cy=DIAL_C[1]):
    """侧旋钮正视图：ATOP 原厂外观（底座 + 齿圈旋钮 + 中间一条凸起的翼片），不印任何 logo"""
    R = 17.5
    s.add(f'<circle cx="{cx + 1.2}" cy="{cy + 2}" r="{R + 2}" fill="#000" opacity=".25" filter="url(#{s.u("blur2")})"/>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{C["dial_ring"]}" stroke="#000" stroke-width=".6"/>')        # 底座
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{R - 3.2}" fill="{C["dial_knurl"]}" stroke="#000" stroke-width=".45"/>')  # 旋钮
    for j in range(36):                                                                                               # 外圈齿纹
        a = 2 * math.pi * j / 36
        s.add(f'<line x1="{cx + (R - 6.2) * math.cos(a):.2f}" y1="{cy + (R - 6.2) * math.sin(a):.2f}" '
              f'x2="{cx + (R - 3.4) * math.cos(a):.2f}" y2="{cy + (R - 3.4) * math.sin(a):.2f}" stroke="#000" stroke-opacity=".45" stroke-width=".35"/>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{R - 6.4}" fill="{C["dial_cap"]}" stroke="#000" stroke-width=".45"/>')    # 盖
    wing = affinity.rotate(rounded(box(cx - 9.5, cy - 2.6, cx + 9.5, cy + 2.6), 2.4), -30, origin=(cx, cy))          # 翼片
    s.add(f'<path d="{D(affinity.translate(wing, .6, 1))}" fill="#000" opacity=".25"/>')
    s.add(f'<path d="{D(wing)}" fill="{C["dial_wing"]}" stroke="#000" stroke-width=".5"/>')
    s.add(f'<path d="{D(wing.buffer(-1.1))}" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width=".4"/>')
    # 四个小凸点（ATOP 旋钮盖边上的防滑块）
    for j in range(4):
        a = math.radians(-30 + 90 * j + 45)
        s.add(f'<circle cx="{cx + (R - 8.4) * math.cos(a):.2f}" cy="{cy + (R - 8.4) * math.sin(a):.2f}" r="1.1" fill="{C["dial_ring"]}" stroke="#000" stroke-width=".3"/>')

def build(C, uid):
    s = Soft(K, C, uid); k = K
    s.begin()
    sil = k.sil
    s.add(f'<path d="{D(sil)}" fill="url(#{s.u("vol")})"/>')
    # ---------- 主线：护条一笔 ----------
    MUD = [(118, 420), (180, 428), (250, 432), (320, 428), (368, 416), (402, 394)]
    mud = Polygon(spline(MUD, steps=16) + [(470, 380), (470, 560), (100, 560)]).buffer(0)
    RISE = [(410, 392), (412, 352), (400, 306), (376, 262), (346, 222), (318, 192)]
    rl = LineString(spline(RISE, steps=20))
    n = 60
    rise = unary_union([Point(rl.interpolate(j / n, normalized=True)).buffer(17 - 4 * j / n) for j in range(n + 1)])
    plate = Point(*DIAL_C).buffer(26, quad_segs=32)
    rail = smooth(unary_union([mud, rise, plate]).intersection(sil.buffer(-0.01)), 6).intersection(sil)
    # ---------- 回声：围着护条的两圈 ----------
    echo1 = smooth(rail.buffer(15, join_style=1, quad_segs=24), 4).intersection(sil)       # 第一圈：一整片绒面，贴着护条
    echo2 = smooth(rail.buffer(30, join_style=1, quad_segs=24), 4).intersection(sil)       # 第二圈：一道缝
    # ---------- 前侧护片（鞋带区），脚踝处开一个鞋带窗 ----------
    CAGE = [(262, 96), (266, 160), (266, 222), (270, 272), (266, 312), (246, 342), (208, 364), (166, 378), (126, 388), (60, 396)]
    cage = smooth(Polygon(spline(CAGE, steps=16) + [(20, 400), (20, 60)]).buffer(0).intersection(sil), 3)
    # 鞋带窗：开在脚背弯折处（和 TP 的鞋带窗同一位置），护片里挖一个斜的长圆
    wc = (240, 326)
    win = affinity.rotate(rounded(box(wc[0] - 24, wc[1] - 8, wc[0] + 24, wc[1] + 8), 7.5), -38, origin=wc).intersection(cage.buffer(-5))
    cage_cut = cage.difference(win)
    TOE = [(40, 386), (86, 390), (116, 402), (134, 422), (140, 452), (140, 520)]
    toe = smooth(Polygon(spline(TOE, steps=16) + [(20, 520), (20, 380)]).buffer(0).intersection(sil), 3)
    collar = smooth(Polygon(spline(COLLAR, steps=14)).buffer(0).intersection(sil), 2).difference(cage)
    # 后背脊条
    SPINE = [(430, 96), (384, 104), (388, 170), (396, 240), (404, 300), (430, 300)]
    spine = smooth(Polygon(spline(SPINE, steps=14)).buffer(0).intersection(sil), 2)

    # ---------- 从下往上画 ----------
    # 上鞋身：一道横缝分成上下两片（上片是软垫，横向两道浅绗缝）
    s.seam(spline([(262, 150), (310, 146), (360, 140), (400, 134)], steps=12))
    s.seam(spline([(262, 252), (300, 244), (340, 238), (390, 236)], steps=12), double=False)
    # 第二圈缝
    for g in getattr(echo2.boundary, 'geoms', [echo2.boundary]):
        ln = g.intersection(sil.buffer(-1.5))
        for gg in getattr(ln, 'geoms', [ln]):
            if gg.geom_type == 'LineString' and gg.length > 10:
                s.seam(list(gg.coords))
    s.soft_panel(echo1, C['echo'], stitch=(1.6,), puff=0.08)
    # 第一圈上一排细孔（顺着护条）
    ring = rail.buffer(8, join_style=1, quad_segs=24).boundary
    pts = [ring.interpolate(t) for t in range(0, int(ring.length), 4)]
    s.holes([(p.x, p.y) for p in pts if p.within(echo1.buffer(-2)) and not p.within(cage.buffer(2)) and p.y < 400], 0.7)
    s.soft_panel(spine, C['spine'], 'crackle', stitch=(1.6, 3.0))
    for y0 in (250, 270):
        tab = rounded(box(390, y0, 416, y0 + 9), 1).intersection(sil.buffer(-1))
        s.panel(tab, C['tab'], stitch=(1.2,), shadow=False, lw=.45)
    s.soft_panel(rail, C['rail'], 'crackle' if C.get('rail_tex') else None, stitch=(1.6, 3.0))
    # 护条上沿的点缀滚边
    edge = rail.buffer(1.0, join_style=1).difference(rail).intersection(sil).difference(box(0, 0, 150, 600))
    s.add(f'<path d="{D(edge)}" fill="{C["piping"]}"/>')
    s.soft_panel(collar, C['collar'], stitch=(2.0,), puff=0.18)
    # 鞋带窗：网布 + 两根钢丝交叉 + 导向扣
    s.add(f'<path d="{D(win)}" fill="{C["window"]}"/><path d="{D(win)}" fill="url(#{s.u("hexmesh")})"/>')
    # 两根钢丝在窗里交叉：导向扣在窗的两条长边上，交替连
    ax, ay = math.cos(math.radians(-38)), math.sin(math.radians(-38))
    nx, ny = -ay, ax
    A = [(wc[0] + ax * t + nx * 5.6, wc[1] + ay * t + ny * 5.6) for t in (-16, 0, 16)]
    F = [(wc[0] + ax * t - nx * 5.6, wc[1] + ay * t - ny * 5.6) for t in (-16, 0, 16)]
    for c in ([A[0], F[1], A[2]], [F[0], A[1], F[2]]):
        s.add(f'<path d="{ld(c)}" fill="none" stroke="{C["cable"]}" stroke-width="1.1"/>')
    s.soft_panel(cage_cut, C['cage'], stitch=(1.6, 3.0))
    # 前护片里一道回声缝：顺着护片后沿
    cl = LineString(spline(CAGE, steps=16)).offset_curve(-14 if LineString(spline(CAGE, steps=16)).offset_curve(-14).centroid.x < 250 else 14)
    seg = cl.intersection(cage_cut.buffer(-3))
    for g in getattr(seg, 'geoms', [seg]):
        if g.geom_type == 'LineString' and g.length > 20:
            s.seam(list(g.coords))
    for (x, y) in A + F:
        g = affinity.rotate(rounded(box(x - 3.2, y - 1.7, x + 3.2, y + 1.7), 1.6), -38, origin=(x, y))
        s.add(f'<path d="{D(g)}" fill="{C["guide"]}" stroke="#000" stroke-width=".4"/>')
    s.soft_panel(toe, C['toe'], 'crackle', stitch=(1.6, 3.0))
    s.holes([(96 + 6 * j, 400 + 7.4 * j) for j in range(5)], 1.05)
    # 字标、图形标：只在鞋身上压印，不上旋钮
    s.wordmark(292, 439, 5.0, C['emboss'], rot=-2)
    s.mono(410, 424, 10, C['emboss'])
    lab = rounded(box(236, 104, 252, 122), 1.5)
    s.panel(lab, C['label'], stitch=(), shadow=False, lw=.45)
    s.mono(244, 113, 10, C['label_mark'])
    s.add(f'<path d="{D(sil)}" fill="none" stroke="{C["line"]}" stroke-width=".7"/>')
    side_dial(s, C)
    s.finish('line')
    return s

def pal(fn, **kw):
    d = dict(rail='#FFFFFF', cage='#FFFFFF', toe='#FFFFFF', collar='#FFFFFF', piping='#FFFFFF', label='#111111',
             label_mark='#FFFFFF', emboss='#B8B8B8', dial_ring='#C9C4B6', dial_knurl='#FFFFFF', dial_cap='#FFFFFF',
             dial_wing='#FFFFFF', echo='#FFFFFF', spine='#FFFFFF', tab='#E6E6E6', window='#FFFFFF', cable='#555555',
             guide='#FFFFFF', shade='.28')
    d.update(kw)
    return fn(**d)

COLORWAYS = {
    'tp': pal(palette, rail_tex=True),
    # 石墨：深炭灰磨砂鞋面，护条岩灰，一道鼠尾草滚边，骨白中底
    'graphite': pal(dark_palette, base='#3A3D40', rail='#596268', cage='#2C2F32', toe='#26282B', collar='#26282B',
                    piping='#C2D8C5', label='#C2D8C5', label_mark='#26282B', emboss='#4A5257', loop='#596268',
                    mid='#F3F2EE', out='#1E2022', dial_ring='#4A4E52', dial_knurl='#2A2C2E', dial_cap='#1F2123',
                    dial_wing='#34373A', echo='#33373A', spine='#26282B', tab='#B9BDC0', window='#4A5257', cable='#B9BDC0',
                    guide='#C2D8C5', shade='.45', tex='rgba(255,255,255,.04)', stitch='rgba(255,255,255,.4)'),
    # 骨白：骨白鞋面，护条暖灰，岩灰滚边
    'bone': pal(palette, base='#EDEBE5', rail='#D3CFC6', cage='#E3E0D8', toe='#D3CFC6', collar='#68747A', piping='#68747A',
                label='#68747A', label_mark='#EDEBE5', emboss='#BFBAB0', loop='#68747A', liner='#68747A', strap='#D3CFC6',
                echo='#E3E0D8', spine='#D3CFC6', tab='#B9BDC0', window='#68747A', cable='#8A8F92', guide='#F7F7F5',
                dial_ring='#C9C4B6', dial_knurl='#F7F7F5', dial_cap='#F7F7F5', dial_wing='#E6E3DC',
                mid='#F3F2EE', out='#68747A', boa='#F7F7F5', boa_dark='#C9C4B6', tex='rgba(0,0,0,.05)',
                stitch='rgba(0,0,0,.35)', line='#2B2E30', hole='#68747A', shade='.22'),
    # 岩灰：岩灰鞋面，护条深一号，骨白滚边
    'slate': pal(dark_palette, base='#68747A', rail='#4B555B', cage='#5D686E', toe='#3E474C', collar='#2B3033',
                 piping='#F3F2EE', label='#F3F2EE', label_mark='#4B555B', emboss='#3E474C', loop='#F3F2EE',
                 mid='#F3F2EE', out='#2B3033', dial_ring='#4A4E52', dial_knurl='#2A2C2E', dial_cap='#1F2123',
                 dial_wing='#34373A', echo='#5D686E', spine='#3E474C', tab='#B9BDC0', window='#2B3033', cable='#B9BDC0',
                 guide='#F3F2EE', shade='.35', stitch='rgba(255,255,255,.4)'),
    # 鼠尾草：灰鼠尾草鞋面，护条深一号，骨白滚边
    'sage': pal(palette, base='#A3B5A8', rail='#7E9185', cage='#96A99C', toe='#6E8075', collar='#5F7066', piping='#F3F2EE',
                label='#F3F2EE', label_mark='#5F7066', emboss='#6E8075', loop='#F3F2EE', liner='#5F7066', strap='#7E9185',
                echo='#94A799', spine='#6E8075', tab='#D9DDDA', window='#5F7066', cable='#7A7F80', guide='#F7F7F5',
                dial_ring='#C9C4B6', dial_knurl='#F7F7F5', dial_cap='#F7F7F5', dial_wing='#E6E3DC',
                mid='#F3F2EE', out='#5F7066', boa='#F7F7F5', boa_dark='#C9C4B6', tex='rgba(255,255,255,.06)',
                stitch='rgba(0,0,0,.35)', line='#26292B', hole='#5F7066', shade='.28'),
}

if __name__ == '__main__':
    for name, C in COLORWAYS.items():
        open(f'{OUT}/r7-{name}.svg', 'w').write(build(C, f'r7{name}').svg())
        print('ok', name)
