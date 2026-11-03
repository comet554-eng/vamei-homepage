import sys, json, pikepdf
from pikepdf import Operator

def mat_mul(a, b):
    # a then b  (row-vector convention: p' = p*a*b)
    a0,a1,a2,a3,a4,a5 = a; b0,b1,b2,b3,b4,b5 = b
    return (a0*b0+a1*b2, a0*b1+a1*b3, a2*b0+a3*b2, a2*b1+a3*b3, a4*b0+a5*b2+b4, a4*b1+a5*b3+b5)
def apply(m, x, y):
    return (m[0]*x+m[2]*y+m[4], m[1]*x+m[3]*y+m[5])

PAINT = {'f','F','f*','B','B*','b','b*','S','s','n'}
def walk(stream_obj, resources, ctm, path_id, out, depth=0):
    ops = pikepdf.parse_content_stream(stream_obj)
    stack = []
    st = dict(ctm=ctm, fill=('g',(0,)), stroke=('G',(0,)), lw=1)
    pts = []
    for i, (operands, op) in enumerate(ops):
        o = str(op)
        if o == 'q': stack.append(dict(st))
        elif o == 'Q': st = stack.pop() if stack else st
        elif o == 'cm':
            m = tuple(float(x) for x in operands); st['ctm'] = mat_mul(m, st['ctm'])
        elif o in ('g','rg','k'): st['fill'] = (o, tuple(round(float(x),3) for x in operands))
        elif o in ('G','RG','K'): st['stroke'] = (o, tuple(round(float(x),3) for x in operands))
        elif o in ('cs',): st['fill'] = ('cs', (str(operands[0]),))
        elif o in ('scn','sc'): st['fill'] = ('scn', tuple(str(x) for x in operands))
        elif o in ('CS',): st['stroke'] = ('CS', (str(operands[0]),))
        elif o in ('SCN','SC'): st['stroke'] = ('SCN', tuple(str(x) for x in operands))
        elif o == 'w': st['lw'] = float(operands[0])
        elif o in ('m','l'): pts.append(apply(st['ctm'], float(operands[0]), float(operands[1])))
        elif o == 'c':
            for k in range(0,6,2): pts.append(apply(st['ctm'], float(operands[k]), float(operands[k+1])))
        elif o in ('v','y'):
            for k in range(0,4,2): pts.append(apply(st['ctm'], float(operands[k]), float(operands[k+1])))
        elif o == 're':
            x,y,w,h = (float(v) for v in operands)
            for (a,b) in ((x,y),(x+w,y),(x+w,y+h),(x,y+h)): pts.append(apply(st['ctm'], a, b))
        elif o in PAINT:
            if pts:
                xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
                bbox=(round(min(xs),2),round(min(ys),2),round(max(xs),2),round(max(ys),2))
            else: bbox=None
            out.append(dict(id=f"{path_id}:{i}", op=o, fill=st['fill'], stroke=st['stroke'], lw=st['lw'], bbox=bbox, npts=len(pts), depth=depth))
            pts = []
        elif o == 'Do':
            name = str(operands[0])
            xo = resources.get('/XObject', {}).get(name)
            if xo is not None and xo.get('/Subtype') == '/Form':
                m = tuple(float(x) for x in xo.get('/Matrix', [1,0,0,1,0,0]))
                res = xo.get('/Resources', resources)
                out.append(dict(id=f"{path_id}:{i}", op='Do', name=name, depth=depth))
                walk(xo, res, mat_mul(m, st['ctm']), f"{path_id}/{name}", out, depth+1)
            else:
                out.append(dict(id=f"{path_id}:{i}", op='DoImg', name=name, ctm=st['ctm'], depth=depth))
        elif o == 'sh':
            out.append(dict(id=f"{path_id}:{i}", op='sh', name=str(operands[0]), depth=depth))
        elif o in ('BT','Tj','TJ',"'",'"'):
            if o in ('Tj','TJ'): out.append(dict(id=f"{path_id}:{i}", op=o, fill=st['fill'], depth=depth))
    return out

pdf = pikepdf.open(sys.argv[1])
page = pdf.pages[0]
out = walk(page.obj, page.obj.Resources, (1,0,0,1,0,0), "P", [])
json.dump(out, open(sys.argv[2],'w'), ensure_ascii=False)
from collections import Counter
c = Counter((d['op'], str(d.get('fill'))) for d in out if d['op'] in ('f','F','f*','B','B*','b','b*'))
for k,v in c.most_common(): print(v, k)
print(len(out))
