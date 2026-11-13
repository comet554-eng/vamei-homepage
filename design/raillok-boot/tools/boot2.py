"""RAILLOK 雪鞋 · 方向二「壳与芯」：渲染风格的侧视图（右脚外侧，鞋头朝右）。
usage: boot2.py ref.json mono.json word.json colorway out.svg [--debug]

标志是「一个外框里套着一个形」，鞋也拆成两层：
  壳 —— 硬壳从鞋头包到后跟、顺着后背往上，上沿是一条干净的斜线（硬、利落）；
  芯 —— 软芯从壳里长出来，包住脚踝和小腿，斜向绗缝，绗缝方向和壳的斜线平行（软、饱满）。
壳的边缘压一道点缀色细线；标志只缩小放在旋钮盖和后背脊条上。
坐标单位 pt，成品方向（鞋头朝右）。大底、中底形状来自 Vamei TP 稿（ref.json 已翻转好）。"""
import json, math, sys
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union, split
from geom import to_poly, to_d

ref = json.load(open(sys.argv[1]))
mono = json.load(open(sys.argv[2]))
word = json.load(open(sys.argv[3]))
CW = sys.argv[4]
OUT = sys.argv[5]
DEBUG = '--debug' in sys.argv

COLORWAYS = {
    # shell 壳, core 芯, line 包边细线, dial 旋钮, mid 中底, out 大底, loop 提拉环, mark 标志（压印）
    'black-bone': dict(shell='#1C1D1F', core='#ECEAE3', line='#C2D8C5', dial='#1C1D1F', dial_cap='#C2D8C5',
                       mid='#F3F2EE', out='#17181A', loop='#C2D8C5', mark='#3A3C3F', lining='#2A2C2E',
                       cover='#1C1D1F', guide='#3A3D41'),
    'slate-bone': dict(shell='#5F6A70', core='#ECEAE3', line='#C2D8C5', dial='#1C1D1F', dial_cap='#C2D8C5',
                       mid='#F3F2EE', out='#1C1D1F', loop='#C2D8C5', mark='#7A858B', lining='#2A2C2E',
                       cover='#5F6A70', guide='#C2D8C5'),
    'sage-bone':  dict(shell='#AFC7B3', core='#F0EEE8', line='#1C1D1F', dial='#1C1D1F', dial_cap='#F3F2EE',
                       mid='#F3F2EE', out='#1C1D1F', loop='#1C1D1F', mark='#9DB6A1', lining='#2A2C2E',
                       cover='#AFC7B3', guide='#1C1D1F'),
    'black-black': dict(shell='#1C1D1F', core='#2B2D30', line='#C2D8C5', dial='#111213', dial_cap='#C2D8C5',
                        mid='#1F2022', out='#141516', loop='#C2D8C5', mark='#34373A', lining='#151617',
                        cover='#1C1D1F', guide='#C2D8C5'),
}
C = COLORWAYS[CW]
_lum = sum(int(C['core'][i:i + 2], 16) for i in (1, 3, 5)) / 765
PAD_HI = '.55' if _lum > .5 else '.12'      # 深色芯的绗缝高光要弱

def spline(pts, closed=True, steps=14):
    P = list(pts)
    P = ([P[-1]] + P + [P[0], P[1]]) if closed else ([P[0]] + P + [P[-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(steps):
            t = k / steps; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not closed: out.append(P[-2])
    return out

def D(g, prec=2):
    return to_d(g, prec) if not g.is_empty else ''

def line_d(pts):
    return 'M' + 'L'.join(f'{x:.2f} {y:.2f}' for x, y in pts)

# ---------------- 形 ----------------
UPPER = [(84, 100), (100, 104), (125, 113), (165, 117), (215, 115), (250, 110), (266, 108), (279, 99), (292, 98),
         (298, 108), (294, 132), (281, 175), (269, 220), (259, 265), (253, 305), (255, 333), (270, 349), (300, 362),
         (340, 374), (380, 384), (410, 390), (428, 401), (436, 418), (435, 436), (420, 452), (330, 472),
         (200, 470), (90, 462), (48, 452), (46, 425), (50, 385), (58, 342), (67, 298), (73, 250), (77, 200), (80, 150)]
upper = Polygon(spline(UPPER)).buffer(0)

# 壳的上沿：一条线从脚背往后扫，绕过后跟往上收成后背脊条——壳是一个「L」，
# 对应标志外框的底边和后边；芯在 L 里面
HERO = [(440, 352), (392, 383), (340, 392), (280, 394), (225, 386), (180, 365), (140, 335), (115, 300),
        (104, 255), (100, 200), (98, 150), (97, 112), (96, 60)]
hero_pts = spline(HERO, closed=False, steps=20)
hero_line = LineString(hero_pts)
below = Polygon(hero_pts + [(0, 60), (0, 600), (480, 600), (480, 352)]).buffer(0)   # 线的后下方 = 壳
shell = upper.intersection(below)
core = upper.difference(below)

# 芯：前缘一条光面（鞋带盖），领口一圈包边，其余斜向绗缝
front_chain = LineString(spline([(285, 92), (292, 98), (298, 108), (294, 132), (281, 175), (269, 220), (259, 265), (253, 305),
                                 (255, 333), (270, 349), (300, 362), (340, 374), (380, 384), (410, 392)], closed=False))
lace_cover = core.intersection(front_chain.buffer(19, cap_style=2)).buffer(0)
collar_chain = LineString(spline([(80, 101), (100, 104), (125, 113), (165, 117), (215, 115), (250, 110),
                                  (266, 108), (278, 100)], closed=False))
collar = core.intersection(collar_chain.buffer(8.5, cap_style=2)).difference(lace_cover)
quilt = core.difference(lace_cover).difference(collar)

# 鞋头：包头一道缝线；后背：脊条
toe_seam = spline([(410, 386), (402, 405), (403, 428), (410, 452), (417, 470)], closed=False)
toe_cap = shell.intersection(Polygon(toe_seam + [(470, 470), (470, 370)]).buffer(0))
rear_chain = LineString(spline([(84, 100), (80, 150), (77, 200), (73, 250), (67, 298), (58, 342), (50, 385),
                                (46, 425), (47, 452)], closed=False))
spine = shell.intersection(rear_chain.buffer(9, cap_style=2))

# 中底、大底
mid = to_poly(ref['mid'])
out = to_poly(ref['out'])

# 旋钮：壳上、斜线下方
DIAL = (170, 380)

# ---------------- 渲染 ----------------
dx, dy = 0.9933, 0.1155                  # 绗缝方向：垂直于鞋筒轴线（鞋筒前倾约 6.6°，和标志的倾角一样）
nx, ny = -dy, dx                          # 绗缝渐变方向
Q = 11.0                                  # 绗缝间距

def contour(d):
    """离壳的边距离 d 的等距线（裁到绗缝区里）"""
    reg = shell.buffer(d, join_style=1, quad_segs=24)
    reg = reg.buffer(0.7 * d, quad_segs=24).buffer(-0.7 * d, quad_segs=24)    # 内拐角倒圆
    ring = reg.boundary.intersection(quilt.buffer(-0.4))
    return ''.join(line_d(list(g.coords)) for g in getattr(ring, 'geoms', [ring])
                   if g.geom_type == 'LineString' and g.length > 2)

def quilt_lines():
    """平行于斜线的绗缝线（裁到绗缝区里）"""
    s = []
    for k in range(-40, 40):
        ox, oy = 215 + nx * Q * k, 254 + ny * Q * k
        ln = LineString([(ox - dx * 500, oy - dy * 500), (ox + dx * 500, oy + dy * 500)]).intersection(quilt.buffer(-0.6))
        for g in getattr(ln, 'geoms', [ln]):
            if g.length > 2:
                s.append(line_d(list(g.coords)))
    return ''.join(s)

mb = to_poly(mono[1]['d'], evenodd=True).union(to_poly(mono[2]['d'])).bounds
def monogram(cx, cy, h, fill, extra=''):
    s = h / (mb[3] - mb[1])
    return (f'<g transform="translate({cx} {cy}) scale({s:.4f}) translate({-(mb[0] + mb[2]) / 2:.2f} {-(mb[1] + mb[3]) / 2:.2f})" {extra}>'
            f'<path d="{mono[1]["d"]}" fill-rule="evenodd" fill="{fill}"/><path d="{mono[2]["d"]}" fill="{fill}"/></g>')

def wordmark(x, y, h, fill, extra=''):
    letters = [w for w in word if w['id'] in ('P:77', 'P:91', 'P:94', 'P:106', 'P:119', 'P:141', 'P:158')]
    b = unary_union([to_poly(w['d']) for w in letters]).bounds
    s = h / (b[3] - b[1])
    return (f'<g transform="translate({x} {y}) scale({s:.4f}) translate({-b[0]:.2f} {-b[3]:.2f})" {extra}>'
            + ''.join(f'<path d="{w["d"]}" fill="{fill}"/>' for w in letters) + '</g>')

def dial(cx, cy, r=13):
    s = [f'<circle cx="{cx}" cy="{cy + 1.6}" r="{r + 1.5}" fill="#000" opacity=".35" filter="url(#soft)"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{C["dial"]}"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#dialSheen)"/>']
    for k in range(48):
        a = 2 * math.pi * k / 48
        s.append(f'<line x1="{cx + (r - 2.4) * math.cos(a):.2f}" y1="{cy + (r - 2.4) * math.sin(a):.2f}" '
                 f'x2="{cx + (r - 0.5) * math.cos(a):.2f}" y2="{cy + (r - 0.5) * math.sin(a):.2f}" stroke="#fff" stroke-opacity=".22" stroke-width=".45"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r - 3.4}" fill="{C["dial_cap"]}"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r - 3.4}" fill="url(#capSheen)"/>')
    s.append(monogram(cx, cy, (r - 3.4) * 1.05, C['dial'], 'opacity=".85"'))
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#000" stroke-opacity=".6" stroke-width=".5"/>')
    return ''.join(s)

def clip(cid, g):
    return f'<clipPath id="{cid}"><path d="{D(g)}"/></clipPath>'

defs = f'''<defs>
{clip('cUpper', upper)}{clip('cShell', shell)}{clip('cCore', core)}{clip('cQuilt', quilt)}{clip('cMid', mid)}
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.6"/></filter>
<filter id="blur3" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="blur6" x="-20%" y="-100%" width="140%" height="300%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="2" seed="7" result="n"/>
  <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.4 1.05"/>
</filter>
<linearGradient id="volX" x1="40" y1="0" x2="440" y2="0" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#000" stop-opacity=".30"/><stop offset=".12" stop-color="#000" stop-opacity=".08"/>
  <stop offset=".45" stop-color="#fff" stop-opacity=".06"/><stop offset=".7" stop-color="#fff" stop-opacity="0"/>
  <stop offset="1" stop-color="#000" stop-opacity=".18"/>
</linearGradient>
<linearGradient id="volY" x1="0" y1="100" x2="0" y2="470" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#fff" stop-opacity=".10"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/>
  <stop offset=".85" stop-color="#000" stop-opacity=".06"/><stop offset="1" stop-color="#000" stop-opacity=".22"/>
</linearGradient>
<linearGradient id="quiltG" x1="215" y1="254" x2="{215 + nx * Q:.3f}" y2="{254 + ny * Q:.3f}" gradientUnits="userSpaceOnUse" spreadMethod="repeat">
  <stop offset="0" stop-color="#000" stop-opacity=".16"/><stop offset=".18" stop-color="#000" stop-opacity=".02"/>
  <stop offset=".45" stop-color="#fff" stop-opacity=".22"/><stop offset=".7" stop-color="#fff" stop-opacity=".05"/>
  <stop offset="1" stop-color="#000" stop-opacity=".16"/>
</linearGradient>
<linearGradient id="collarG" x1="0" y1="100" x2="0" y2="126" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#fff" stop-opacity=".28"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/>
  <stop offset="1" stop-color="#000" stop-opacity=".18"/>
</linearGradient>
<linearGradient id="midG" x1="0" y1="430" x2="0" y2="490" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#fff" stop-opacity=".5"/><stop offset=".35" stop-color="#fff" stop-opacity="0"/>
  <stop offset="1" stop-color="#000" stop-opacity=".16"/>
</linearGradient>
<radialGradient id="dialSheen" cx=".35" cy=".3" r=".8">
  <stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset=".5" stop-color="#fff" stop-opacity=".05"/>
  <stop offset="1" stop-color="#000" stop-opacity=".25"/>
</radialGradient>
<radialGradient id="capSheen" cx=".35" cy=".3" r=".75">
  <stop offset="0" stop-color="#fff" stop-opacity=".45"/><stop offset="1" stop-color="#000" stop-opacity=".18"/>
</radialGradient>
</defs>'''

S = []
add = S.append
# 地面投影
add('<ellipse cx="240" cy="500" rx="210" ry="7" fill="#000" opacity=".28" filter="url(#blur6)"/>')
add('<ellipse cx="240" cy="499" rx="185" ry="2.6" fill="#000" opacity=".35" filter="url(#soft)"/>')

# 提拉环（后背顶上）
loop = Polygon(spline([(84, 112), (84, 88), (89, 72), (99, 70), (103, 84), (101, 112)])).buffer(0).difference(
    Polygon(spline([(89, 110), (89, 90), (92, 80), (97, 81), (97, 92), (96, 110)])).buffer(0))
add(f'<path d="{D(loop)}" fill="{C["loop"]}"/><path d="{D(loop)}" fill="url(#volY)"/>'
    f'<path d="{D(loop)}" fill="none" stroke="#000" stroke-opacity=".45" stroke-width=".4"/>')

# 内里口（领口上沿露出的一圈内里）
add(f'<path d="{line_d(spline([(84, 101), (100, 104), (125, 112), (165, 116), (215, 114), (250, 109), (276, 112), (291, 120)], closed=False))}" '
    f'fill="none" stroke="{C["lining"]}" stroke-width="3.2" stroke-linecap="round"/>')

# 芯
add(f'<path d="{D(core)}" fill="{C["core"]}"/>')
# 绗缝：顺着壳的边一圈圈往外（等距线），每格中间鼓、缝线处凹
QC = 12.5
seams = ''.join(contour(QC * k) for k in range(1, 22))
pads = ''.join(contour(QC * (k - 0.5)) for k in range(1, 23))
add(f'<g clip-path="url(#cQuilt)">'
    f'<path d="{pads}" fill="none" stroke="#fff" stroke-opacity="{PAD_HI}" stroke-width="{QC * .5:.1f}" stroke-linecap="round" filter="url(#blur3)"/>'
    f'<path d="{seams}" fill="none" stroke="#000" stroke-opacity=".16" stroke-width="3.2" filter="url(#soft)"/>'
    f'<path d="{seams}" fill="none" stroke="#000" stroke-opacity=".28" stroke-width=".45" stroke-dasharray="1.3 .8"/>'
    f'</g>')
add(f'<path d="{D(collar)}" fill="url(#collarG)"/>')
add(f'<path d="{D(collar)}" fill="none" stroke="#000" stroke-opacity=".18" stroke-width=".5"/>')
# 鞋带盖（和壳同色）：外框从后、下、前三面包住软芯
add(f'<path d="{D(lace_cover)}" fill="{C["cover"]}"/>')
add(f'<path d="{D(lace_cover)}" fill="none" stroke="#000" stroke-opacity=".45" stroke-width=".5"/>')
lc_stitch = lace_cover.buffer(-2.2, join_style=2)
add(f'<path d="{D(lc_stitch)}" fill="none" stroke="#fff" stroke-opacity=".22" stroke-width=".4" stroke-dasharray="1.3 .8"/>')
# 鞋带导向扣：沿前缘露出的小扣
ub = LineString(upper.exterior.coords)
for (px, py) in [(290, 150), (281, 192), (271, 236), (262, 280), (300, 362), (338, 374)]:
    q = ub.interpolate(ub.project(Point(px, py)))
    a = ub.interpolate(ub.project(q) - 1.5); b = ub.interpolate(ub.project(q) + 1.5)
    ang = math.degrees(math.atan2(b.y - a.y, b.x - a.x)) + 90
    add(f'<g transform="translate({q.x:.2f} {q.y:.2f}) rotate({ang:.1f})">'
        f'<rect x="-1.5" y="-1.2" width="3" height="9" rx="1.5" fill="{C["guide"]}" stroke="#000" stroke-opacity=".5" stroke-width=".3"/></g>')
# 鞋舌顶上的小拉环
tl = Polygon(spline([(281, 100), (283, 86), (290, 80), (297, 85), (296, 100)])).buffer(0).difference(
    Polygon(spline([(285, 99), (287, 89), (290, 86), (293, 89), (292, 99)])).buffer(0))
S.insert(2, f'<path d="{D(tl)}" fill="{C["loop"]}"/><path d="{D(tl)}" fill="none" stroke="#000" stroke-opacity=".45" stroke-width=".4"/>')

# 壳在芯上投下的阴影（沿斜线上方一道柔影）
add(f'<g clip-path="url(#cCore)"><path d="{line_d(hero_pts)}" fill="none" stroke="#000" stroke-opacity=".35" '
    f'stroke-width="5" filter="url(#blur3)"/></g>')

# 壳
add(f'<path d="{D(shell)}" fill="{C["shell"]}"/>')
add(f'<path d="{D(toe_cap)}" fill="#000" opacity=".10"/>')
add(f'<path d="{D(spine)}" fill="#fff" opacity=".06"/>')
add(f'<g clip-path="url(#cShell)">'
    # 壳沿下方的一道柔光（硬壳边缘翻起来的高光）
    f'<path d="{line_d(hero_pts)}" fill="none" stroke="#fff" stroke-opacity=".16" stroke-width="10" filter="url(#blur3)"/>'
    f'<path d="{line_d(toe_seam)}" fill="none" stroke="#000" stroke-opacity=".45" stroke-width=".55"/>'
    f'<path d="{line_d(toe_seam)}" fill="none" stroke="#fff" stroke-opacity=".12" stroke-width=".5" transform="translate(-.8 0)"/>'
    f'<path d="{D(spine)}" fill="none" stroke="#000" stroke-opacity=".35" stroke-width=".5"/>'
    f'</g>')

# 整体体积 + 质感
add(f'<g clip-path="url(#cUpper)"><rect x="0" y="0" width="480" height="520" fill="url(#volX)"/>'
    f'<rect x="0" y="0" width="480" height="520" fill="url(#volY)"/>'
    f'<rect x="0" y="0" width="480" height="520" filter="url(#grain)" opacity=".06"/></g>')
# 鞋头、后跟的一点哑光高光
add(f'<g clip-path="url(#cShell)"><ellipse cx="392" cy="402" rx="34" ry="9" fill="#fff" opacity=".10" filter="url(#blur6)" transform="rotate(14 392 402)"/>'
    f'<ellipse cx="70" cy="330" rx="7" ry="60" fill="#fff" opacity=".07" filter="url(#blur6)"/></g>')

# 壳沿：点缀色细线 + 一丝高光
add(f'<g clip-path="url(#cUpper)"><path d="{line_d(hero_pts)}" fill="none" stroke="{C["line"]}" stroke-width="1.5"/>'
    f'<path d="{line_d(hero_pts)}" fill="none" stroke="#000" stroke-opacity=".35" stroke-width=".35" transform="translate(-.9 .7)"/></g>')

# 后背脊条上的小标志、壳上的字标（压印：比壳色稍亮）
add(monogram(88.5, 150, 9, C['mark']))
add(wordmark(96, 437, 5.2, C['mark']))

# 轮廓
add(f'<path d="{D(upper)}" fill="none" stroke="#000" stroke-opacity=".7" stroke-width=".5"/>')

# 中底、大底
add(f'<path d="{D(out)}" fill="{C["out"]}"/>')
add(f'<path d="{D(mid)}" fill="{C["mid"]}"/>')
add(f'<path d="{D(mid)}" fill="url(#midG)"/>')
groove = spline([(58, 452), (150, 457), (260, 466), (340, 466), (405, 452), (428, 436)], closed=False)
add(f'<g clip-path="url(#cMid)"><path d="{line_d(groove)}" fill="none" stroke="#000" stroke-opacity=".16" stroke-width=".7"/>'
    f'<path d="{line_d(groove)}" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width=".5" transform="translate(0 .9)"/></g>')
add(f'<path d="{D(mid)}" fill="none" stroke="#000" stroke-opacity=".5" stroke-width=".45"/>')

# 旋钮
add(dial(*DIAL))

if DEBUG:
    add(f'<path d="{line_d(hero_pts)}" fill="none" stroke="red" stroke-width=".3"/>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="20 40 440 480" width="880" height="960">'
       + defs + ''.join(S) + '</svg>')
open(OUT, 'w').write(svg)
if '--icon' in sys.argv:
    # 概念图用的平面小图：壳 + 鞋带盖（黑）、芯（白），只有形，没有光影
    icon = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="30 50 420 460">'
            f'<path d="{D(core)}" fill="#F3F2EE" stroke="#111" stroke-width="2"/>'
            f'<path d="{D(unary_union([shell, lace_cover]))}" fill="#111"/>'
            f'<path d="{D(mid)}" fill="none" stroke="#111" stroke-width="2"/></svg>')
    open(OUT.replace('.svg', '-icon.svg'), 'w').write(icon)
print('ok', CW)
