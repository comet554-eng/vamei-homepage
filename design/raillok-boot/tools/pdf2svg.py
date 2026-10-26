"""把 PDF 一页里的每个绘制操作转成 SVG path（页面坐标，y 向下），存成 JSON。
usage: pdf2svg.py in.pdf page_no out.json
每项：id（和 vamei-boot/tools/walk.py 的编号一致）、op、d、fill、stroke、sw、dash、cap、join、rule、alpha"""
import sys, json, math, pikepdf

def mul(a, b):
    a0, a1, a2, a3, a4, a5 = a; b0, b1, b2, b3, b4, b5 = b
    return (a0*b0 + a1*b2, a0*b1 + a1*b3, a2*b0 + a3*b2, a2*b1 + a3*b3,
            a4*b0 + a5*b2 + b4, a4*b1 + a5*b3 + b5)

def hexcol(kind, vals):
    try:
        v = [float(x) for x in vals]
    except (ValueError, TypeError):
        return None  # pattern
    if len(v) == 1: r = g = b = v[0]
    elif len(v) == 3: r, g, b = v
    elif len(v) == 4:
        c, m, y, k = v; r, g, b = (1-c)*(1-k), (1-m)*(1-k), (1-y)*(1-k)
    else: return None
    return '#%02x%02x%02x' % tuple(round(max(0, min(1, x)) * 255) for x in (r, g, b))

PAINT = {'f', 'F', 'f*', 'B', 'B*', 'b', 'b*', 'S', 's', 'n'}

def walk(obj, res, ctm, pid, H, out):
    st = dict(ctm=ctm, fill='#000000', stroke='#000000', lw=1.0, dash=None, cap=0, join=0, ca=1.0, CA=1.0)
    stack, d, cur = [], [], None
    def P(x, y):
        m = st['ctm']; return (m[0]*x + m[2]*y + m[4], H - (m[1]*x + m[3]*y + m[5]))
    for i, (a, o) in enumerate(pikepdf.parse_content_stream(obj)):
        o = str(o)
        if o == 'q': stack.append(dict(st))
        elif o == 'Q': st = stack.pop()
        elif o == 'cm': st['ctm'] = mul(tuple(float(x) for x in a), st['ctm'])
        elif o in ('g', 'rg', 'k', 'sc', 'scn'): st['fill'] = hexcol(o, a)
        elif o in ('G', 'RG', 'K', 'SC', 'SCN'): st['stroke'] = hexcol(o, a)
        elif o == 'w': st['lw'] = float(a[0])
        elif o == 'J': st['cap'] = int(a[0])
        elif o == 'j': st['join'] = int(a[0])
        elif o == 'd': st['dash'] = [float(x) for x in a[0]] or None
        elif o == 'gs':
            g = res.get('/ExtGState', {}).get(str(a[0]))
            if g is not None:
                st['ca'] = float(g.get('/ca', st['ca'])); st['CA'] = float(g.get('/CA', st['CA']))
        elif o == 'm': d.append('M%.3f %.3f' % P(float(a[0]), float(a[1])))
        elif o == 'l': d.append('L%.3f %.3f' % P(float(a[0]), float(a[1])))
        elif o == 'c':
            v = [float(x) for x in a]
            d.append('C%.3f %.3f %.3f %.3f %.3f %.3f' % (*P(v[0], v[1]), *P(v[2], v[3]), *P(v[4], v[5])))
            cur = (v[4], v[5])
        elif o == 'v':
            v = [float(x) for x in a]
            # 第一控制点 = 当前点
            last = d[-1].split()[-2:] if d else ['0', '0']
            d.append('C%s %s %.3f %.3f %.3f %.3f' % (last[0].lstrip('MLC'), last[1], *P(v[0], v[1]), *P(v[2], v[3])))
        elif o == 'y':
            v = [float(x) for x in a]
            d.append('C%.3f %.3f %.3f %.3f %.3f %.3f' % (*P(v[0], v[1]), *P(v[2], v[3]), *P(v[2], v[3])))
        elif o == 'h': d.append('Z')
        elif o == 're':
            x, y, w, h = (float(v) for v in a)
            d.append('M%.3f %.3fL%.3f %.3fL%.3f %.3fL%.3f %.3fZ' % (*P(x, y), *P(x+w, y), *P(x+w, y+h), *P(x, y+h)))
        elif o in PAINT:
            if o != 'n' and d:
                m = st['ctm']; scale = math.sqrt(abs(m[0]*m[3] - m[1]*m[2]))
                out.append(dict(id=f'{pid}:{i}', op=o, d=''.join(d),
                                fill=st['fill'] if o not in ('S', 's') else None,
                                stroke=st['stroke'] if o in ('S', 's', 'B', 'B*', 'b', 'b*') else None,
                                sw=round(st['lw']*scale, 3),
                                dash=[round(x*scale, 3) for x in st['dash']] if st['dash'] else None,
                                cap=st['cap'], join=st['join'],
                                rule='evenodd' if o.endswith('*') else 'nonzero',
                                alpha=st['ca'] if o not in ('S', 's') else st['CA']))
            d = []
        elif o == 'Do':
            xo = res.get('/XObject', {}).get(str(a[0]))
            if xo is not None and xo.get('/Subtype') == '/Form':
                m = tuple(float(x) for x in xo.get('/Matrix', [1, 0, 0, 1, 0, 0]))
                walk(xo, xo.get('/Resources', res), mul(m, st['ctm']), f'{pid}/{a[0]}', H, out)
    return out

pdf = pikepdf.open(sys.argv[1])
page = pdf.pages[int(sys.argv[2]) - 1]
H = float(page.mediabox[3])
out = walk(page.obj, page.obj.Resources, (1, 0, 0, 1, 0, 0), 'P', H, [])
json.dump(out, open(sys.argv[3], 'w'), ensure_ascii=False)
print(len(out), 'items')
