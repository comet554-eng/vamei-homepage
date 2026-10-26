"""Recolor selected paint ops in a PDF page.
usage: recolor.py in.pdf out.pdf spec.json
spec: {"fill": {"P:782": [r,g,b], "P//Fm5:31": [r,g,b], ...},
       "stroke": {...}, "drop": ["P:123", ...], "strip_pieceinfo": true}
Op ids match walk.py: <stream path>:<op index>. Fill override inserts an `rg` before the
paint op (inside a q/Q so state after it is unchanged)."""
import sys, json, pikepdf
from pikepdf import Operator

def rewrite(stream_obj, resources, path_id, spec, pdf, seen):
    ops = pikepdf.parse_content_stream(stream_obj)
    fills, strokes, drop = spec.get('fill', {}), spec.get('stroke', {}), set(spec.get('drop', []))
    new = []
    changed = False
    for i, (operands, op) in enumerate(ops):
        oid = f"{path_id}:{i}"
        o = str(op)
        if o == 'Do':
            name = str(operands[0])
            xo = resources.get('/XObject', {}).get(name)
            if xo is not None and xo.get('/Subtype') == '/Form':
                sub = f"{path_id}/{name}"
                if any(k.startswith(sub + ':') or k.startswith(sub + '/') for k in list(fills) + list(strokes) + list(drop)):
                    # copy the form so other users of it are unaffected
                    nxo = pdf.copy_foreign(xo) if False else pikepdf.Stream(pdf, xo.read_bytes())
                    for k, v in xo.items():
                        if k not in ('/Length', '/Filter', '/DecodeParms'):
                            nxo[k] = v
                    rewrite(nxo, xo.get('/Resources', resources), sub, spec, pdf, seen)
                    newname = pikepdf.Name(name + 'r' + str(len(seen)))
                    seen.append(newname)
                    resources.XObject[newname] = nxo
                    operands = [newname]
                    changed = True
        if oid in drop:
            changed = True
            if o in ('Do', 'Tj', 'TJ', "'", '"'):
                continue  # remove the op entirely
            # replace paint op by 'n' (end path without painting)
            new.append(([], Operator('n')))
            continue
        if oid in fills or oid in strokes:
            pre = []
            if oid in fills:
                c = fills[oid]
                pre.append(([pikepdf.Name('/DeviceRGB')], Operator('cs')))
                pre.append((list(c), Operator('sc')))
            if oid in strokes:
                c = strokes[oid]
                pre.append(([pikepdf.Name('/DeviceRGB')], Operator('CS')))
                pre.append((list(c), Operator('SC')))
            # path is already constructed; color ops are allowed only outside path construction,
            # so we must put color before path. Find start of current path in `new`.
            j = len(new)
            while j > 0 and str(new[j-1][1]) in ('m','l','c','v','y','h','re'):
                j -= 1
            new[j:j] = pre
            new.append((operands, op))
            # restore is tricky; we wrap in q..Q around path
            new.insert(j, ([], Operator('q')))
            new.append(([], Operator('Q')))
            changed = True
            continue
        new.append((operands, op))
    if changed:
        stream_obj.write(pikepdf.unparse_content_stream(new))

pdf = pikepdf.open(sys.argv[1])
spec = json.load(open(sys.argv[3]))
page = pdf.pages[0]
# page content may be array; normalise
page.contents_coalesce()
rewrite(page.obj.Contents, page.obj.Resources, 'P', spec, pdf, [])
if spec.get('strip_pieceinfo', True):
    if '/PieceInfo' in page.obj: del page.obj['/PieceInfo']
    if '/Thumb' in page.obj: del page.obj['/Thumb']
pdf.save(sys.argv[2])
