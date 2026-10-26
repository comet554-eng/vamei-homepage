"""RAILLOK 雪鞋侧视图：生成一段 SVG（颜色全部走 CSS 变量，换配色只换变量）。
usage: boot.py tp.json mono.json word.json out.svgfrag [--debug]

TP 稿的形状是鞋头朝左的坐标；整只鞋最后水平翻转成鞋头朝右，这样外侧的标志是正的。
新画的部件直接按成品方向（鞋头朝右）写坐标，用 F() 换回翻转前的坐标。
文字、正面朝外的旋钮这类不能反的东西画在翻转组外面。

复用 TP 稿：大底、中底、内胆领口、提拉环、上区 BOA 旋钮（只取形状，颜色重配）。
新画：鞋面整体轮廓（TP 各片合并）、标志框架片（含锁跟带）、鞋带护片、鞋头包头、
     鞋带、第二个旋钮（锁跟带末端）、字标。"""
import json, math, sys
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from geom import to_poly, to_d

tp_items = json.load(open(sys.argv[1]))
tp = {x['id']: x for x in tp_items}
mono = json.load(open(sys.argv[2]))
word = json.load(open(sys.argv[3]))
OUT = sys.argv[4]
DEBUG = '--debug' in sys.argv
FLIP_X = 470.0                      # x(成品) = FLIP_X - x(TP)

def F(pts):
    return [(FLIP_X - x, y) for x, y in pts]

def n(i):
    return int(i.split(':')[-1]) if i.startswith('P:') else -1

def path(d, cls, extra=''):
    return f'<path class="{cls}" d="{d}" {extra}/>'

def poly_path(g, cls, extra=''):
    return path(to_d(g), cls, extra) if not g.is_empty else ''

def stitch(g, inset=2.0, cls='stitch'):
    s = g.buffer(-inset, join_style=2)
    return poly_path(s, cls, 'fill="none"') if not s.is_empty else ''

def spline(pts, closed=True, steps=12):
    """Catmull-Rom 曲线过所有点 -> 折线点列"""
    P = list(pts)
    if closed: P = [P[-1]] + P + [P[0], P[1]]
    else: P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(steps):
            t = k / steps; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not closed: out.append(P[-2])
    return out

# ---------- 鞋面轮廓：TP 稿各片合并 ----------
UPPER_IDS = ['P:782', 'P:815', 'P:849', 'P:875', 'P:904', 'P:931', 'P:960', 'P:992', 'P:1027',
             'P:1089', 'P:1409', 'P:1735', 'P:1778', 'P:1930', 'P:1201']
sil = unary_union([to_poly(tp[i]['d']) for i in UPPER_IDS]).buffer(2.5).buffer(-2.5)

# ---------- 标志框架：标志图形镜像后贴进鞋筒外侧的四边形（翻转后是正的） ----------
mono_poly = to_poly(mono[1]['d'], evenodd=True).union(to_poly(mono[2]['d']))
mx0, my0, mx1, my1 = mono_poly.bounds
QUAD = dict(TL=(232, 94), TR=(404, 86), BR=(442, 446), BL=(198, 446))   # TP 坐标
THIN = 3.0                                                               # 标志笔画收细（标志单位）

def warp_pt(x, y):
    u = 1 - (x - mx0) / (mx1 - mx0)
    v = (y - my0) / (my1 - my0)
    TL, TR, BR, BL = QUAD['TL'], QUAD['TR'], QUAD['BR'], QUAD['BL']
    top = (TL[0] + (TR[0] - TL[0]) * u, TL[1] + (TR[1] - TL[1]) * u)
    bot = (BL[0] + (BR[0] - BL[0]) * u, BL[1] + (BR[1] - BL[1]) * u)
    return (top[0] + (bot[0] - top[0]) * v, top[1] + (bot[1] - top[1]) * v)

def warp(geom):
    out = []
    for g in getattr(geom, 'geoms', [geom]):
        g = g.segmentize(1.0)
        out.append(Polygon([warp_pt(*p) for p in g.exterior.coords],
                           [[warp_pt(*p) for p in r.coords] for r in g.interiors]))
    return unary_union(out)

frame = warp(mono_poly.buffer(-THIN, join_style=1)).intersection(sil)
sq = to_poly(mono[2]['d']).centroid
dial2 = warp_pt(sq.x, sq.y)                 # 钩子末端的小方块 -> 锁跟带旋钮（TP 坐标）
dial2_final = (FLIP_X - dial2[0], dial2[1])

# ---------- 鞋带护片：沿鞋筒前缘、脚背上沿的一条带子，上宽下窄 ----------
from shapely.ops import substring
def front_chain(a_final, b_final):
    """鞋面轮廓上从 a 到 b（成品坐标）的那段前缘，返回 TP 坐标折线"""
    ring = LineString(sil.exterior.coords)
    pa, pb = Point(F([a_final])[0]), Point(F([b_final])[0])
    da, db = ring.project(pa), ring.project(pb)
    seg = substring(ring, min(da, db), max(da, db))
    if seg.length > ring.length / 2:      # 取短的那一段
        seg = LineString(list(substring(ring, max(da, db), ring.length).coords) + list(substring(ring, 0, min(da, db)).coords))
    return seg
GUARD_A, GUARD_B = (300, 96), (400, 384)        # 领口前端 -> 脚背和包头交界
chain = front_chain(GUARD_A, GUARD_B)
def guard_width(t):                              # t: 0 在领口，1 在脚背末端
    return 46 - 26 * min(1, t / 0.55) - 4 * max(0, (t - 0.55) / 0.45)
blobs = [Point(chain.interpolate(k / 80, normalized=True)).buffer(guard_width(k / 80 if chain.coords[0][1] < chain.coords[-1][1] else 1 - k / 80))
         for k in range(81)]
guard = unary_union(blobs).buffer(4).buffer(-4).intersection(sil)

# ---------- 鞋头包头 ----------
toe_edge = [(318, 452), (334, 436), (356, 418), (382, 403), (410, 394), (440, 390)]
toe_out = [(470, 400), (470, 500), (318, 500)]
toe = Polygon(F(spline(toe_edge, closed=False) + toe_out)).buffer(0).intersection(sil)

# ---------- 输出（翻转组里，TP 坐标） ----------
parts = []
def add(s):
    if s: parts.append(s)

add('<ellipse class="shadow" cx="232" cy="497" rx="205" ry="4.5"/>')

# 提拉环、内胆领口
for i, cls in [('P:596', 'loop'), ('P:651', 'loop-in')]:
    add(path(tp[i]['d'], cls)); add(path(tp[i]['d'], 'line', 'fill="none"'))
for i in ['P:623', 'P:676', 'P:712', 'P:739']:
    add(path(tp[i]['d'], 'liner')); add(path(tp[i]['d'], 'liner-line', 'fill="none"'))

# 鞋面底色
add(poly_path(sil, 'base'))

# 鞋带护片
add(poly_path(guard, 'guard'))
add(stitch(guard))
add(poly_path(guard, 'line', 'fill="none"'))

# 鞋带导向片：沿前缘（鞋舌两侧）露出的小扣，横跨轮廓线
def edge_point(xf, top=True):
    """成品坐标 x 处，鞋面前缘（上沿）的点和外法线"""
    x = FLIP_X - xf
    hit = sil.boundary.intersection(LineString([(x, 60), (x, 380)]))
    pts = sorted([(p.x, p.y) for p in getattr(hit, 'geoms', [hit])], key=lambda p: p[1])
    y = pts[0][1]
    a = sil.boundary.interpolate(sil.boundary.project(Point(x - 1.5, y)))
    b = sil.boundary.interpolate(sil.boundary.project(Point(x + 1.5, y)))
    return (x, y), math.atan2(b.y - a.y, b.x - a.x)
for xf in (268, 292, 318, 345, 372):
    (x, y), ang = edge_point(xf)
    deg = math.degrees(ang) + 90
    add(f'<g transform="translate({x:.2f} {y:.2f}) rotate({deg:.1f})">'
        f'<rect class="cable line-thin" x="-1.6" y="-5.5" width="3.2" height="11" rx="1.6"/></g>')

# 鞋头包头
add(poly_path(toe, 'toe'))
add(stitch(toe, cls='stitch-f'))
add(poly_path(toe, 'line', 'fill="none"'))

# 体积阴影（整只鞋面一层渐变）
add(poly_path(sil, 'shade', 'fill="url(#shade)"'))
add(poly_path(sil, 'shade', 'fill="url(#shadeV)"'))

# 标志框架（压在最上面，带一点投影）
add(poly_path(frame.buffer(0.9).intersection(sil), 'drop'))
add(poly_path(frame, 'frame'))
add(stitch(frame, cls='stitch-f'))
add(poly_path(frame, 'line', 'fill="none"'))

add(poly_path(sil, 'line', 'fill="none"'))

# 中底、大底
add(path(tp['P:2163']['d'], 'outsole'))
add(path(tp['P:1993']['d'], 'midsole'))
add(path(tp['P:1993']['d'], 'line', 'fill="none"'))
for i in ['P:2325', 'P:2331', 'P:2337', 'P:2343', 'P:2349', 'P:2355', 'P:2361', 'P:2369']:
    add(path(tp[i]['d'], 'mid-detail', 'fill="none"'))

# 上区 BOA（TP 里 P:20–P:595 是旋钮组，位置不动）
for x in tp_items:
    if not (x['id'].startswith('P:') and 20 <= n(x['id']) <= 595 and x['d']):
        continue
    if x['fill']:
        add(path(x['d'], 'boa' if x['fill'] == '#ffffff' else 'boa-dark'))
    if x['stroke']:
        add(path(x['d'], 'line-thin', 'fill="none"'))

if DEBUG:
    for p in QUAD.values():
        add(f'<circle cx="{p[0]}" cy="{p[1]}" r="2" fill="red"/>')

flipped = f'<g transform="matrix(-1 0 0 1 {FLIP_X} 0)">' + '\n'.join(parts) + '</g>'

# ---------- 翻转组外：锁跟带旋钮（正面）、字标 ----------
def dial_face(cx, cy, r=12):
    """正面看的旋钮：底座（标志末端的方块）+ 齿圈 + 盖子 + 小标志"""
    s = [f'<rect class="frame line" x="{cx - r - 3.2}" y="{cy - r - 3.2}" width="{2 * r + 6.4}" height="{2 * r + 6.4}" rx="4"/>',
         f'<circle class="boa-dark line" cx="{cx}" cy="{cy}" r="{r}"/>']
    for k in range(36):
        a = 2 * math.pi * k / 36
        s.append(f'<line class="knurl" x1="{cx + (r - 2.2) * math.cos(a):.2f}" y1="{cy + (r - 2.2) * math.sin(a):.2f}" '
                 f'x2="{cx + (r - 0.4) * math.cos(a):.2f}" y2="{cy + (r - 0.4) * math.sin(a):.2f}"/>')
    s.append(f'<circle class="boa-cap" cx="{cx}" cy="{cy}" r="{r - 3}"/>')
    s.append(f'<circle class="dial-ring" cx="{cx}" cy="{cy}" r="{r - 3}" fill="none"/>')
    mb = mono_poly.bounds; size = (r - 4.6) * 2 / (mb[3] - mb[1])
    s.append(f'<g transform="translate({cx} {cy}) scale({size:.4f}) translate({-(mb[0] + mb[2]) / 2:.2f} {-(mb[1] + mb[3]) / 2:.2f})">'
             f'<path class="mark" d="{mono[1]["d"]}" fill-rule="evenodd"/><path class="mark" d="{mono[2]["d"]}"/></g>')
    return ''.join(s)

def wordmark(x, y, h, cls='mark'):
    """RAILLOK 字标，左下角放在 (x, y)，字高 h"""
    letters = [w for w in word if w['id'] in ('P:77', 'P:91', 'P:94', 'P:106', 'P:119', 'P:141', 'P:158')]
    gs = unary_union([to_poly(w['d']) for w in letters])
    b = gs.bounds; s = h / (b[3] - b[1])
    return (f'<g transform="translate({x} {y}) scale({s:.4f}) translate({-b[0]:.2f} {-b[3]:.2f})">'
            + ''.join(f'<path class="{cls}" d="{w["d"]}"/>' for w in letters) + '</g>')

front = [dial_face(*dial2_final)]
fb = frame.bounds
front.append(wordmark(78, 425.5, 6.4))   # 后跟下方框架横条上的字标

defs = '''<defs>
<linearGradient id="shade" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#000" stop-opacity="0"/>
  <stop offset="0.55" stop-color="#000" stop-opacity="0"/>
  <stop offset="0.92" stop-color="#000" stop-opacity="0.14"/>
  <stop offset="1" stop-color="#000" stop-opacity="0.05"/>
</linearGradient>
<linearGradient id="shadeV" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity="0.07"/>
  <stop offset="0.45" stop-color="#fff" stop-opacity="0"/>
  <stop offset="0.85" stop-color="#000" stop-opacity="0"/>
  <stop offset="1" stop-color="#000" stop-opacity="0.12"/>
</linearGradient>
</defs>'''
open(OUT, 'w').write(defs + flipped + ''.join(front))
meta = dict(dial2=dial2_final, frame_bounds=fb, sil_bounds=sil.bounds)
json.dump(meta, open(OUT + '.json', 'w'))
print(meta)
