"""TP 画法的共用工具：照 Vamei 双扣 TP 的样子画雪鞋侧视图（鞋头朝左，TP 坐标，单位 pt）。
黑描边、双线明缝、龟裂纹皮料、网布、压片投影；大底、中底、内胆、提拉环、BOA、魔术贴沿用 TP 的形状。
每个款式只写自己的分片，用 Sheet.panel() 一层层往上压，最后 Sheet.svg() 出图。"""
import json, math
import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
from geom import to_poly, to_d

UPPER_IDS = ['P:782', 'P:815', 'P:849', 'P:875', 'P:904', 'P:931', 'P:960', 'P:992', 'P:1027',
             'P:1089', 'P:1409', 'P:1735', 'P:1778', 'P:1930', 'P:1201']
WORD_IDS = ('P:77', 'P:91', 'P:94', 'P:106', 'P:119', 'P:141', 'P:158')

def spline(pts, closed=False, steps=12):
    """Catmull-Rom 曲线过所有控制点"""
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

def strip(pts, w, cap=2, steps=16):
    """沿一条曲线的等宽带子"""
    return LineString(spline(pts, steps=steps)).buffer(w / 2, cap_style=cap, join_style=1)

def tapered(pts, w0, w1, steps=24):
    """沿曲线、从 w0 渐变到 w1 宽的带子"""
    c = spline(pts, steps=steps)
    ln = LineString(c)
    n = 80
    blobs = [Point(ln.interpolate(k / n, normalized=True)).buffer((w0 + (w1 - w0) * k / n) / 2) for k in range(n + 1)]
    return unary_union(blobs).buffer(0.5).buffer(-0.5)

class Kit:
    def __init__(self, tp_json, mono_json, word_json):
        self.items = json.load(open(tp_json))
        self.tp = {x['id']: x for x in self.items}
        self.mono = json.load(open(mono_json))
        self.word = json.load(open(word_json))
        self.sil = unary_union([to_poly(self.tp[i]['d']) for i in UPPER_IDS]).buffer(3).buffer(-3)
        self.mid = to_poly(self.tp['P:1993']['d'])
        self.mono_poly = to_poly(self.mono[1]['d'], evenodd=True).union(to_poly(self.mono[2]['d']))

    def clip(self, g, r=1.6):
        return rounded(g.buffer(0).intersection(self.sil), r)

class Sheet:
    """一张鞋图。C 是配色字典（见 base_colors）"""
    def __init__(self, kit, C, uid):
        self.k, self.C, self.uid = kit, C, uid
        self.S = []

    # ---------- 基本笔触 ----------
    def add(self, s):
        self.S.append(s)

    def u(self, name):                       # 每张图的 pattern id 加前缀，同页多张图互不干扰
        return f'{name}-{self.uid}'

    def panel(self, g, fill, tex=None, stitch=(1.5, 3.0), shadow=True, lw=0.7):
        C = self.C
        if g is None or g.is_empty: return
        if shadow:
            self.add(f'<path d="{D(affinity.translate(g, 1.3, 1.4))}" fill="{C["shadow"]}"/>')
        self.add(f'<path d="{D(g)}" fill="{fill}"/>')
        if tex:
            self.add(f'<path d="{D(g)}" fill="url(#{self.u(tex)})"/>')
        for inset in stitch:
            s = g.buffer(-inset, join_style=1)
            if not s.is_empty:
                self.add(f'<path d="{D(s)}" fill="none" stroke="{C["stitch"]}" stroke-width=".28" stroke-dasharray="2.2 .6"/>')
        self.add(f'<path d="{D(g)}" fill="none" stroke="{C["line"]}" stroke-width="{lw}" stroke-linejoin="round"/>')

    def seam(self, pts, double=True):
        """鞋面上的一道分割缝（描线 + 旁边一或两道明线）"""
        C = self.C
        ln = LineString(pts).intersection(self.k.sil.buffer(-0.5))
        if ln.is_empty: return
        for g in getattr(ln, 'geoms', [ln]):
            self.add(f'<path d="{ld(list(g.coords))}" fill="none" stroke="{C["line"]}" stroke-width=".6"/>')
            for off in ((1.6, 3.0) if double else (1.6,)):
                o = g.offset_curve(off)
                if not o.is_empty and o.geom_type == 'LineString':
                    self.add(f'<path d="{ld(list(o.coords))}" fill="none" stroke="{C["stitch"]}" stroke-width=".28" stroke-dasharray="2.2 .6"/>')

    def holes(self, pts, r=0.95):
        C = self.C
        fill = C['hole']
        for (x, y) in pts:
            self.add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{fill}" stroke="{C["line"]}" stroke-width=".35"/>')

    def mono(self, cx, cy, h, color, rot=0):
        k = self.k
        b = k.mono_poly.bounds; s = h / (b[3] - b[1])
        self.add(f'<g transform="translate({cx:.2f} {cy:.2f}) rotate({rot}) scale({s:.4f}) translate({-(b[0] + b[2]) / 2:.2f} {-(b[1] + b[3]) / 2:.2f})">'
                 f'<path d="{k.mono[1]["d"]}" fill-rule="evenodd" fill="{color}"/><path d="{k.mono[2]["d"]}" fill="{color}"/></g>')

    def wordmark(self, cx, cy, h, color, rot=0):
        letters = [w for w in self.k.word if w['id'] in WORD_IDS]
        b = unary_union([to_poly(w['d']) for w in letters]).bounds
        s = h / (b[3] - b[1])
        self.add(f'<g transform="translate({cx:.2f} {cy:.2f}) rotate({rot:.1f}) scale({s:.4f}) translate({-(b[0] + b[2]) / 2:.2f} {-(b[1] + b[3]) / 2:.2f})">'
                 + ''.join(f'<path d="{w["d"]}" fill="{color}"/>' for w in letters) + '</g>')

    def tp_path(self, i, fill=None, stroke=None, sw=None, extra=''):
        x = self.k.tp[i]
        f = fill if fill is not None else 'none'
        s = f' stroke="{stroke}" stroke-width="{sw or x["sw"]}"' if stroke else ''
        return f'<path d="{x["d"]}" fill="{f}"{s} {extra}/>'

    # ---------- 共用部件 ----------
    def begin(self):
        """地面投影、提拉环、内胆、鞋面底色"""
        C, k = self.C, self.k
        self.add('<ellipse cx="236" cy="499" rx="205" ry="3.2" fill="#000" opacity=".55"/>')
        self.add(self.tp_path('P:596', C['loop'], C['line'], .7)); self.add(self.tp_path('P:651', C['loop'], C['line'], .7))
        for i in ['P:623', 'P:676', 'P:712', 'P:739']:
            self.add(self.tp_path(i, C['liner'])); self.add(f'<path d="{k.tp[i]["d"]}" fill="url(#{self.u("linermesh")})"/>')
            self.add(self.tp_path(i, None, '#000', .7))
        self.add(f'<path d="{D(k.sil)}" fill="{C["base"]}"/>')

    def finish(self, midsole_grooves='rails'):
        """鞋面外轮廓、中底、大底、BOA、魔术贴"""
        C, k = self.C, self.k
        self.add(f'<path d="{D(k.sil)}" fill="none" stroke="{C["line"]}" stroke-width=".7"/>')
        self.add(self.tp_path('P:2163', C['out']))
        self.add(self.tp_path('P:1993', C['mid'], C['line'], .76))
        if midsole_grooves == 'rails':
            g = []
            for j in range(6):
                x0 = 300 + j * 17
                ln = LineString([(x0, 486), (x0 + 22, 440)]).intersection(k.mid.buffer(-2))
                if not ln.is_empty and ln.geom_type == 'LineString': g.append(ld(list(ln.coords)))
            self.add(f'<path d="{"".join(g)}" fill="none" stroke="#000" stroke-opacity=".14" stroke-width="1.4" stroke-linecap="round"/>')
        elif midsole_grooves == 'tp':
            for i in ['P:2325', 'P:2331', 'P:2337', 'P:2343', 'P:2349', 'P:2355', 'P:2361']:
                self.add(self.tp_path(i, None, '#000', 1.4, 'stroke-opacity=".12"'))
        elif midsole_grooves == 'line':
            ln = LineString(spline([(52, 452), (150, 462), (260, 470), (340, 468), (400, 456), (428, 440)])).intersection(k.mid.buffer(-2))
            for gg in getattr(ln, 'geoms', [ln]):
                if gg.geom_type == 'LineString':
                    self.add(f'<path d="{ld(list(gg.coords))}" fill="none" stroke="#000" stroke-opacity=".18" stroke-width=".9"/>')
        self.add(self.tp_path('P:2369', None, '#000', 1.2, 'stroke-opacity=".12"'))
        for x in k.items:
            n = int(x['id'].split(':')[-1]) if x['id'].startswith('P:') else -1
            if not (20 <= n <= 595 and x['d']): continue
            if x['fill']:
                self.add(f'<path d="{x["d"]}" fill="{C["boa"] if x["fill"] == "#ffffff" else C["boa_dark"]}"/>')
            if x['stroke']:
                self.add(f'<path d="{x["d"]}" fill="none" stroke="{C["line"]}" stroke-width="{x["sw"]}"/>')
        self.add(self.tp_path('P:1758', C['strap'])); self.add(f'<path d="{k.tp["P:1758"]["d"]}" fill="url(#{self.u("strapweb")})"/>')
        self.add(self.tp_path('P:1758', None, '#000', .7))

    def defs(self):
        C = self.C
        rng = np.random.default_rng(11)
        size, n = 48, 500
        pts = rng.random((n, 2)) * size
        allp = np.vstack([pts + [dx, dy] for dx in (-size, 0, size) for dy in (-size, 0, size)])
        vor = Voronoi(allp)
        segs = []
        for (a, b) in vor.ridge_vertices:
            if a < 0 or b < 0: continue
            p, q = vor.vertices[a], vor.vertices[b]
            if (-1 < p[0] < size + 1 and -1 < p[1] < size + 1) or (-1 < q[0] < size + 1 and -1 < q[1] < size + 1):
                segs.append(f'M{p[0]:.2f} {p[1]:.2f}L{q[0]:.2f} {q[1]:.2f}')
        u = self.u
        return f'''<defs>
<pattern id="{u('crackle')}" width="{size}" height="{size}" patternUnits="userSpaceOnUse">
  <path d="{''.join(segs)}" fill="none" stroke="{C['tex']}" stroke-width=".22"/></pattern>
<pattern id="{u('mesh')}" width="2.4" height="2.4" patternUnits="userSpaceOnUse" patternTransform="rotate(-32)">
  <line x1="0" y1="0" x2="0" y2="2.4" stroke="{C['meshline']}" stroke-width=".9"/></pattern>
<pattern id="{u('hexmesh')}" width="3.2" height="5.54" patternUnits="userSpaceOnUse">
  <path d="M0 0L1.6 .92L1.6 2.77L0 3.69M1.6 2.77L3.2 3.69M1.6 .92L3.2 0M0 3.69L0 5.54M3.2 3.69L3.2 5.54" fill="none" stroke="{C['meshline']}" stroke-width=".35"/></pattern>
<pattern id="{u('web')}" width="1.5" height="1.5" patternUnits="userSpaceOnUse" patternTransform="rotate({C.get('web_angle', 0)})">
  <line x1="0" y1="0" x2="0" y2="1.5" stroke="{C['webline']}" stroke-width=".55"/></pattern>
<pattern id="{u('linermesh')}" width="2.2" height="2.2" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">
  <circle cx="1.1" cy="1.1" r=".45" fill="#fff" opacity=".22"/></pattern>
<pattern id="{u('strapweb')}" width="1.6" height="1.6" patternUnits="userSpaceOnUse" patternTransform="rotate(-40)">
  <line x1="0" y1="0" x2="0" y2="1.6" stroke="#fff" stroke-opacity=".12" stroke-width=".5"/></pattern>
</defs>'''

    def svg(self, w=880, h=940):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="20 40 440 470" width="{w}" height="{h}">'
                + self.defs() + ''.join(self.S) + '</svg>')

def palette(**kw):
    """配色：白色线稿的默认值 + 覆盖。键见下面"""
    base = dict(base='#FFFFFF', liner='#141414', loop='#FFFFFF', strap='#141414', mid='#FCFBFB', out='#0A0A0A',
                boa='#FFFFFF', boa_dark='#141414', tex='#C9C9C9', meshline='#B9BDC2', webline='#D2D2D2',
                line='#111111', stitch='#111111', shadow='#D6D6D6', hole='#FFFFFF', mark='#111111')
    base.update(kw)
    return base

def dark_palette(**kw):
    """深色部件多的配色：明线变浅、纹理变淡"""
    d = dict(liner='#151617', strap='#151617', out='#151617', boa='#2E3134', boa_dark='#151617',
             tex='rgba(255,255,255,.035)', meshline='rgba(255,255,255,.18)', webline='rgba(255,255,255,.14)',
             line='#000000', stitch='rgba(255,255,255,.5)', shadow='rgba(0,0,0,.28)', hole='#000000')
    d.update(kw)
    return palette(**d)
