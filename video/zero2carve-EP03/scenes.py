"""封面参数（covers2.py 读这里）。"""
import json, os
_r = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_rider.json"))).get("ring")
COVER2 = dict(kicker="单板从0到刻滑 · 第3课", lines=[("单脚蹬行", "ink"), ("板不打转", "gold")],
              sub="后脚在前刃一侧蹬 · 上魔毯全靠它", motif="image", image="cover_rider.png", ring=_r, ring_col="green", seed=13)
