"""从 TP 稿取中底、大底，翻成鞋头朝右（和 boot2.py 同一坐标）。
usage: ref.py tp.json ref.json"""
import json, sys
from shapely import affinity
from geom import to_poly, to_d

tp = {x['id']: x for x in json.load(open(sys.argv[1]))}
flip = lambda g: affinity.scale(g, xfact=-1, yfact=1, origin=(235, 0))
json.dump({'mid': to_d(flip(to_poly(tp['P:1993']['d']))), 'out': to_d(flip(to_poly(tp['P:2163']['d'])))},
          open(sys.argv[2], 'w'))
