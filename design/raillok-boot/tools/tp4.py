"""RAILLOK 雪鞋 · 提案 04「轨与锁」：照 Vamei TP 的画法（黑描边、双线明缝、龟裂纹皮料、网布、压片投影）
画一版分片丰富的新鞋面。坐标就是 TP 稿的坐标（鞋头朝左），单位 pt。
usage: tp4.py tp.json mono.json word.json colorway out.svg [--debug]

沿用 TP 的通用件：中底、大底、内胆领口、提拉环、BOA、魔术贴（形状照搬，颜色按配色走）。
鞋面分片全部新画：
  前侧鞋带区护片、斜切鞋头（一排透气孔）、两条「轨」压条、后跟「锁」杯（上沿往前勾住脚踝）、
  后背脊条 + 反光拉片、领口软垫、上侧梯形网布窗、图形标铭牌、字标铭牌。"""
import json, math, sys
import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
from geom import to_poly, to_d

tp_items = json.load(open(sys.argv[1]))
tp = {x['id']: x for x in tp_items}
mono = json.load(open(sys.argv[2]))
word = json.load(open(sys.argv[3]))
CW = sys.argv[4]
OUT = sys.argv[5]
DEBUG = '--debug' in sys.argv

# 配色：每个部件一个颜色。'tp' 是白色线稿（和 Vamei TP 一样的画法）
COLORWAYS = {
    'tp':    dict(base='#FFFFFF', cage='#FFFFFF', toe='#FFFFFF', rail='#FFFFFF', lock='#FFFFFF', spine='#FFFFFF',
                  collar='#FFFFFF', window='#FFFFFF', plate='#FFFFFF', mark='#111111', liner='#141414',
                  strap='#141414', loop='#FFFFFF', mid='#FCFBFB', out='#0A0A0A', boa='#FFFFFF', boa_dark='#141414',
                  tex='#C9C9C9', line='#111111', stitch='#111111', shadow='#D6D6D6', rail_mark='#111111', heel_mark='#111111'),
    'slate': dict(base='#68747A', cage='#151617', toe='#151617', rail='#C2D8C5', lock='#151617', spine='#151617',
                  collar='#151617', window='#4E585E', plate='#151617', mark='#C2D8C5', liner='#151617',
                  strap='#151617', loop='#C2D8C5', mid='#F3F2EE', out='#151617', boa='#2E3134', boa_dark='#151617',
                  tex='rgba(255,255,255,.035)', line='#000000', stitch='rgba(255,255,255,.55)', shadow='rgba(0,0,0,.28)', rail_mark='#151617', heel_mark='#C2D8C5'),
    'bone':  dict(base='#F3F2EE', cage='#68747A', toe='#68747A', rail='#151617', lock='#68747A', spine='#68747A',
                  collar='#68747A', window='#E3E1DA', plate='#151617', mark='#F3F2EE', liner='#151617',
                  strap='#151617', loop='#151617', mid='#F3F2EE', out='#2B3033', boa='#2E3134', boa_dark='#151617',
                  tex='rgba(255,255,255,.14)', line='#111111', stitch='rgba(0,0,0,.45)', shadow='rgba(0,0,0,.18)', rail_mark='#F3F2EE', heel_mark='#F3F2EE'),
    'sage':  dict(base='#C2D8C5', cage='#151617', toe='#151617', rail='#F3F2EE', lock='#151617', spine='#151617',
                  collar='#151617', window='#AFC6B3', plate='#151617', mark='#C2D8C5', liner='#151617',
                  strap='#151617', loop='#F3F2EE', mid='#F3F2EE', out='#151617', boa='#2E3134', boa_dark='#151617',
                  tex='rgba(255,255,255,.035)', line='#000000', stitch='rgba(0,0,0,.45)', shadow='rgba(0,0,0,.22)', rail_mark='#151617', heel_mark='#C2D8C5'),
    'black': dict(base='#26282B', cage='#151617', toe='#151617', rail='#68747A', lock='#151617', spine='#151617',
                  collar='#151617', window='#1F2123', plate='#68747A', mark='#151617', liner='#151617',
                  strap='#151617', loop='#C2D8C5', mid='#151617', out='#0E0F10', boa='#2E3134', boa_dark='#151617',
                  tex='rgba(255,255,255,.035)', line='#000000', stitch='rgba(255,255,255,.4)', shadow='rgba(0,0,0,.35)', rail_mark='#151617', heel_mark='#C2D8C5'),
}
C = COLORWAYS[CW]
ON_DARK = lambda k: C[k] not in ('#FFFFFF', '#F3F2EE', '#FCFBFB', '#C2D8C5', '#E3E1DA')

def spline(pts, closed=False, steps=12):
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

def rounded(g, r=1.6):
    return g.buffer(r, join_style=1).buffer(-2 * r, join_style=1).buffer(r, join_style=1)

def D(g, prec=2):
    return to_d(g, prec) if not g.is_empty else ''

def ld(pts):
    return 'M' + 'L'.join(f'{x:.2f} {y:.2f}' for x, y in pts)

# ---------------- 鞋面轮廓（TP 各片合并） ----------------
UPPER_IDS = ['P:782', 'P:815', 'P:849', 'P:875', 'P:904', 'P:931', 'P:960', 'P:992', 'P:1027',
             'P:1089', 'P:1409', 'P:1735', 'P:1778', 'P:1930', 'P:1201']
sil = unary_union([to_poly(tp[i]['d']) for i in UPPER_IDS]).buffer(3).buffer(-3)

def clip(g):
    return rounded(g.buffer(0).intersection(sil))

# ---------------- 分片 ----------------
# 领口软垫：沿鞋口一圈
collar = clip(Polygon(spline([(228, 60), (228, 134), (262, 139), (300, 141), (338, 138), (370, 128), (393, 116),
                              (430, 104), (430, 60)])))
# 后背脊条：后缘一条，从后跟杯顶一直到领口
spine = clip(Polygon(spline([(430, 90), (379, 100), (381, 160), (385, 230), (392, 268), (430, 268)])))
# 前侧鞋带区护片：沿鞋筒前缘到脚背，后缘在脚踝处折一个角
cage_edge = [(240, 60), (240, 125), (244, 172), (247, 212), (238, 226), (240, 262), (252, 300), (246, 324),
             (220, 344), (178, 362), (138, 376), (112, 384)]
cage = clip(Polygon(spline(cage_edge) + [(60, 384), (100, 200), (150, 60)]))
# 鞋头：后缘一刀斜切
toe = clip(Polygon([(20, 380), (100, 380), (124, 384), (150, 410), (178, 446), (178, 520), (20, 520)]))
toe_holes = [(122 + 7.2 * k, 398 + 8.6 * k) for k in range(5)]
# 两条「轨」：从后跟下方斜着扫过鞋身，一直钻到前侧护片底下，是整只鞋的主方向
RAIL_C = [(400, 458), (362, 414), (324, 372), (292, 332), (268, 294), (250, 254), (240, 216), (234, 190)]
rail_line = LineString(spline(RAIL_C, steps=20))
_m = rail_line.interpolate(0.5, normalized=True)
REAR = 1 if rail_line.offset_curve(20).interpolate(0.5, normalized=True).x > _m.x else -1   # 往后上方的偏移符号

def side(offset, rear=True):
    """轨道平行线（偏移 offset）后上方或前下方的那半边"""
    ln = rail_line.offset_curve(REAR * offset)
    pts = list(ln.coords)
    ext = [(pts[0][0] + (pts[0][0] - pts[3][0]) * 20, pts[0][1] + (pts[0][1] - pts[3][1]) * 20)] + pts + \
          [(pts[-1][0] + (pts[-1][0] - pts[-4][0]) * 20, pts[-1][1] + (pts[-1][1] - pts[-4][1]) * 20)]
    far = [(900, -400), (900, 900)] if rear else [(-400, 900), (-400, -400)]
    poly = Polygon(ext + far).buffer(0)
    if not poly.is_valid or poly.area < 1:
        poly = Polygon(ext + far[::-1]).buffer(0)
    probe = Point(_m.x + (60 if rear else -60), _m.y)
    return poly if poly.contains(probe) else box(-400, -400, 900, 900).difference(poly)

def rail(offset, w=9):
    return clip(rail_line.offset_curve(REAR * offset).buffer(w / 2, cap_style=2))
rails = [rail(-7), rail(7)]
# 上鞋身片：下沿和轨道平行（偏 24），里面是网布窗
upper_q = clip(side(24, rear=True).intersection(box(0, 0, 900, 330)))
# 前下鞋身片：后沿和轨道平行（偏 24），带透气孔
lower_q = clip(side(24, rear=False))
# 后跟「锁」杯：包住后跟，上前角斜切一刀，往前扣住脚踝
lock = clip(Polygon(spline([(440, 470), (336, 470), (342, 440), (352, 404), (364, 366), (372, 334)], steps=14)
                    + [(384, 318), (440, 304)]))
# 防泥条：沿底边一圈，接在鞋头后面、后跟杯前面
MUD = [(140, 412), (176, 423), (220, 429), (270, 431), (330, 427), (390, 419), (440, 411)]
mud = clip(Polygon(spline(MUD) + [(440, 520), (140, 520)]))
# 脚背透气孔阵：在前下鞋身片上，一排排和轨道平行
perf = []
_t = (RAIL_C[-1][0] - RAIL_C[0][0], RAIL_C[-1][1] - RAIL_C[0][1]); _n = math.hypot(*_t); _t = (_t[0] / _n, _t[1] / _n)
for i in range(5):
    ln = rail_line.offset_curve(-REAR * (33 + i * 4.6))
    for j in range(12):
        base = ln.interpolate(ln.length * 0.30 + j * 4.4 + (i % 2) * 2.2)
        if Point(base.x, base.y).within(lower_q.buffer(-3.5)):
            perf.append((base.x, base.y))
# 上侧梯形网布窗（标志外框的斜角）
window = rounded(Polygon([(286, 160), (352, 150), (362, 212), (302, 232)]), 3)
# 图形标铭牌：在网布窗上
plate_mono = rounded(Polygon([(312, 170), (338, 166), (342, 198), (316, 203)]), 2.5)
# 字标：印在后面那条轨道上
_a = rail_line.offset_curve(REAR * 7).interpolate(0.40, normalized=True)
_b = rail_line.offset_curve(REAR * 7).interpolate(0.46, normalized=True)
WM_ANGLE = math.degrees(math.atan2(_b.y - _a.y, _b.x - _a.x))
if WM_ANGLE > 90 or WM_ANGLE < -90: WM_ANGLE += 180
wm_center = ((_a.x + _b.x) / 2, (_a.y + _b.y) / 2)
# 后背两个反光拉片
tabs = [rounded(Polygon([(386, 246), (424, 246), (424, 258), (387, 258)]), 1),
        rounded(Polygon([(387, 270), (424, 270), (424, 282), (388, 282)]), 1)]

# ---------------- 纹理 ----------------
rng = np.random.default_rng(11)
def crackle_tile(size=48, n=500):
    pts = rng.random((n, 2)) * size
    allp = np.vstack([pts + [dx, dy] for dx in (-size, 0, size) for dy in (-size, 0, size)])
    vor = Voronoi(allp)
    segs = []
    for (a, b) in vor.ridge_vertices:
        if a < 0 or b < 0: continue
        p, q = vor.vertices[a], vor.vertices[b]
        if (-1 < p[0] < size + 1 and -1 < p[1] < size + 1) or (-1 < q[0] < size + 1 and -1 < q[1] < size + 1):
            # 轻微抖动，像皮面裂纹
            segs.append(f'M{p[0]:.2f} {p[1]:.2f}L{q[0]:.2f} {q[1]:.2f}')
    return ''.join(segs)

defs = f'''<defs>
<pattern id="crackle" width="48" height="48" patternUnits="userSpaceOnUse">
  <path d="{crackle_tile()}" fill="none" stroke="{C['tex']}" stroke-width=".22"/>
</pattern>
<pattern id="mesh" width="2.4" height="2.4" patternUnits="userSpaceOnUse" patternTransform="rotate(-32)">
  <line x1="0" y1="0" x2="0" y2="2.4" stroke="{C['tex'] if CW != 'tp' else '#B9BDC2'}" stroke-width=".9"/>
</pattern>
<pattern id="linermesh" width="2.2" height="2.2" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">
  <circle cx="1.1" cy="1.1" r=".45" fill="#fff" opacity=".22"/>
</pattern>
<pattern id="strapweb" width="1.6" height="1.6" patternUnits="userSpaceOnUse" patternTransform="rotate(-40)">
  <line x1="0" y1="0" x2="0" y2="1.6" stroke="#fff" stroke-opacity=".12" stroke-width=".5"/>
</pattern>
</defs>'''

S = []
add = S.append
LW = 0.7

def panel(g, fill, tex=None, stitch=(1.5, 3.0), shadow=True, lw=LW):
    if g.is_empty: return
    if shadow:
        add(f'<path d="{D(affinity.translate(g, 1.3, 1.4))}" fill="{C["shadow"]}"/>')
    add(f'<path d="{D(g)}" fill="{fill}"/>')
    if tex:
        add(f'<path d="{D(g)}" fill="url(#{tex})"/>')
    for inset in stitch:
        s = g.buffer(-inset, join_style=1)
        if not s.is_empty:
            add(f'<path d="{D(s)}" fill="none" stroke="{C["stitch"]}" stroke-width=".28" stroke-dasharray="2.2 .6"/>')
    add(f'<path d="{D(g)}" fill="none" stroke="{C["line"]}" stroke-width="{lw}" stroke-linejoin="round"/>')

def tp_path(i, fill=None, stroke=None, sw=None, extra=''):
    x = tp[i]
    f = fill if fill is not None else 'none'
    s = f' stroke="{stroke}" stroke-width="{sw or x["sw"]}"' if stroke else ''
    return f'<path d="{x["d"]}" fill="{f}"{s} {extra}/>'

# 地面投影
add(f'<ellipse cx="236" cy="499" rx="205" ry="3.2" fill="#000" opacity=".55"/>')
# 提拉环
add(tp_path('P:596', C['loop'], C['line'], .7)); add(tp_path('P:651', C['loop'], C['line'], .7))
# 内胆领口（TP 形状，网布纹）
for i in ['P:623', 'P:676', 'P:712', 'P:739']:
    add(tp_path(i, C['liner'])); add(f'<path d="{tp[i]["d"]}" fill="url(#linermesh)"/>')
    add(tp_path(i, None, '#000', .7))
# 鞋面底色
add(f'<path d="{D(sil)}" fill="{C["base"]}"/>')
# 底色上的结构线：脚背、鞋身中部两道暗缝（让大面不空）
for pts in ([(250, 236), (300, 228), (352, 226), (384, 236)],):
    pass
# 分片：从下往上压
panel(lower_q, C['base'], stitch=(1.6, 3.0), shadow=True)
panel(upper_q, C['base'], stitch=(1.6, 3.0), shadow=True)
add(f'<path d="{D(window)}" fill="{C["window"]}"/><path d="{D(window)}" fill="url(#mesh)"/>')
add(f'<path d="{D(window.buffer(2.2, join_style=1))}" fill="none" stroke="{C["stitch"]}" stroke-width=".28" stroke-dasharray="2.2 .6"/>')
add(f'<path d="{D(window)}" fill="none" stroke="{C["line"]}" stroke-width="{LW}"/>')
for (hx, hy) in perf:
    add(f'<circle cx="{hx:.2f}" cy="{hy:.2f}" r=".95" fill="{C["base"] if CW == "tp" else "#000"}" stroke="{C["line"]}" stroke-width=".35"/>')
panel(mud, C['toe'], 'crackle')
panel(collar, C['collar'], stitch=(2.0,))
panel(spine, C['spine'], 'crackle')
for t in tabs:
    panel(t, '#FFFFFF' if CW == 'tp' else '#C9CDD0', stitch=(1.4,), shadow=False, lw=.5)
for r in rails:
    panel(r, C['rail'], stitch=(1.4,))
panel(lock, C['lock'], 'crackle')
# 后跟小图形标
_hb = to_poly(mono[1]['d'], evenodd=True).union(to_poly(mono[2]['d'])).bounds; _hs = 12 / (_hb[3] - _hb[1])
add(f'<g transform="translate(406 384) scale({_hs:.4f}) translate({-(_hb[0] + _hb[2]) / 2:.2f} {-(_hb[1] + _hb[3]) / 2:.2f})">'
    f'<path d="{mono[1]["d"]}" fill-rule="evenodd" fill="{C["heel_mark"]}"/><path d="{mono[2]["d"]}" fill="{C["heel_mark"]}"/></g>')
panel(cage, C['cage'], 'crackle')
panel(toe, C['toe'], 'crackle')
for (hx, hy) in toe_holes:
    add(f'<circle cx="{hx}" cy="{hy}" r="1.3" fill="{C["base"] if CW == "tp" else "#000"}" stroke="{C["line"]}" stroke-width=".45"/>')
# 铭牌
panel(plate_mono, C['plate'], stitch=(1.4,))
mb = to_poly(mono[1]['d'], evenodd=True).union(to_poly(mono[2]['d'])).bounds
mc = plate_mono.centroid; ms = 22 / (mb[3] - mb[1])
add(f'<g transform="translate({mc.x:.2f} {mc.y:.2f}) rotate(-4) scale({ms:.4f}) translate({-(mb[0] + mb[2]) / 2:.2f} {-(mb[1] + mb[3]) / 2:.2f})">'
    f'<path d="{mono[1]["d"]}" fill-rule="evenodd" fill="{C["mark"]}"/><path d="{mono[2]["d"]}" fill="{C["mark"]}"/></g>')
letters = [w for w in word if w['id'] in ('P:77', 'P:91', 'P:94', 'P:106', 'P:119', 'P:141', 'P:158')]
wb = unary_union([to_poly(w['d']) for w in letters]).bounds
ws = 4.4 / (wb[3] - wb[1])
add(f'<g transform="translate({wm_center[0]:.2f} {wm_center[1]:.2f}) rotate({WM_ANGLE:.1f}) scale({ws:.4f}) '
    f'translate({-(wb[0] + wb[2]) / 2:.2f} {-(wb[1] + wb[3]) / 2:.2f})">'
    + ''.join(f'<path d="{w["d"]}" fill="{C["rail_mark"]}"/>' for w in letters) + '</g>')
# 鞋面外轮廓
add(f'<path d="{D(sil)}" fill="none" stroke="{C["line"]}" stroke-width="{LW}"/>')

# 中底、大底（TP 形状）；中底后跟改成平行斜纹（「轨」）
add(tp_path('P:2163', C['out']))
add(tp_path('P:1993', C['mid'], C['line'], .76))
mid_poly = to_poly(tp['P:1993']['d'])
grooves = []
for k in range(6):
    x0 = 300 + k * 17
    ln = LineString([(x0, 486), (x0 + 22, 440)]).intersection(mid_poly.buffer(-2))
    if not ln.is_empty and ln.geom_type == 'LineString':
        grooves.append(ld(list(ln.coords)))
add(f'<path d="{"".join(grooves)}" fill="none" stroke="#000" stroke-opacity=".14" stroke-width="1.4" stroke-linecap="round"/>')
add(tp_path('P:2369', None, '#000', 1.2, 'stroke-opacity=".12"'))

# BOA（TP 形状）
for x in tp_items:
    n = int(x['id'].split(':')[-1]) if x['id'].startswith('P:') else -1
    if not (20 <= n <= 595 and x['d']): continue
    if x['fill']:
        add(f'<path d="{x["d"]}" fill="{C["boa"] if x["fill"] == "#ffffff" else C["boa_dark"]}"/>')
    if x['stroke']:
        add(f'<path d="{x["d"]}" fill="none" stroke="{C["line"]}" stroke-width="{x["sw"]}"/>')
# 魔术贴（TP 形状）
add(tp_path('P:1758', C['strap'])); add(f'<path d="{tp["P:1758"]["d"]}" fill="url(#strapweb)"/>')
add(tp_path('P:1758', None, '#000', .7))

if DEBUG:
    add(f'<path d="{ld(spline(RAIL_C))}" fill="none" stroke="red" stroke-width=".4"/>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="20 40 440 470" width="880" height="940">'
       + defs + ''.join(S) + '</svg>')
open(OUT, 'w').write(svg)
print('ok', CW)
