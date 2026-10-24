"""封面参数（covers2.py 读这里）。"""
import json, os
_r = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_rider.json")))["ring"]
COVER2 = dict(kicker="单板从0到刻滑 · 第1课", lines=[("新手第一课", "ink"), ("先学会摔", "gold")],
              sub="手腕伤排第一 · 前跪后坐 3 步摔法", motif="image", image="cover_rider.png", ring=_r, seed=11)
