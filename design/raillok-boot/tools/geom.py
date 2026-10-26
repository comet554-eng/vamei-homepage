"""SVG path（只含绝对坐标 M/L/C/Z）和 shapely 多边形互转。"""
import re
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

TOK = re.compile(r'[MLCZ]|-?\d*\.?\d+(?:e-?\d+)?')

def subpaths(d, steps=16):
    """flatten -> list of point lists"""
    toks = TOK.findall(d); i = 0; out = []; cur = None; pts = []
    def num():
        nonlocal i; v = float(toks[i]); i += 1; return v
    cmd = None
    while i < len(toks):
        t = toks[i]
        if t in 'MLCZ': cmd = t; i += 1
        if cmd == 'M':
            if len(pts) > 2: out.append(pts)
            cur = (num(), num()); pts = [cur]; cmd = 'L'
        elif cmd == 'L':
            cur = (num(), num()); pts.append(cur)
        elif cmd == 'C':
            x1, y1, x2, y2, x3, y3 = (num() for _ in range(6))
            x0, y0 = cur
            for k in range(1, steps + 1):
                s = k / steps; u = 1 - s
                pts.append((u**3*x0 + 3*u*u*s*x1 + 3*u*s*s*x2 + s**3*x3,
                            u**3*y0 + 3*u*u*s*y1 + 3*u*s*s*y2 + s**3*y3))
            cur = (x3, y3)
        elif cmd == 'Z':
            if len(pts) > 2: out.append(pts)
            pts = [cur] if cur else []; cmd = None
    if len(pts) > 2: out.append(pts)
    return out

def to_poly(d, evenodd=False):
    polys = [Polygon(p).buffer(0) for p in subpaths(d)]
    polys = [p for p in polys if not p.is_empty]
    if not polys: return Polygon()
    if evenodd:
        g = polys[0]
        for p in polys[1:]: g = g.symmetric_difference(p)
        return g
    return unary_union(polys)

def to_d(geom, prec=2):
    """polygon(s) -> SVG path d (with holes, evenodd-safe)"""
    geoms = geom.geoms if isinstance(geom, MultiPolygon) else [geom]
    out = []
    for g in geoms:
        if g.is_empty: continue
        for ring in [g.exterior, *g.interiors]:
            c = list(ring.coords)
            out.append('M' + 'L'.join(f'{x:.{prec}f} {y:.{prec}f}' for x, y in c[:-1]) + 'Z')
    return ''.join(out)
