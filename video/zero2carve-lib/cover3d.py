"""封面用的 3D 人物（透明底 PNG + 标注点位置）：python cover3d.py EPDIR OUT.png
EPDIR/ep.py 里写 COVER3D = dict(perf="G", p=3.6, cam=((x,y,z), (x,y,z), lens), ring="handL"|None)，相机坐标相对 gx。"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.abspath(sys.argv[1]); sys.path.insert(0, EP); sys.path.insert(0, HERE)
import ep
from rig3d import interp
if getattr(ep, "STYLE", "night") == "day":
    from rig3d_day import Scene        # 第6课起：白天雪山 + 一体成型人物
else:
    from rig3d import Scene
from mathutils import Vector

out = sys.argv[2]
C = ep.COVER3D
S = Scene(1200, 1200, samples=int(os.environ.get("SAMPLES", 24)), transparent=True)
P = interp(ep.PERF[C["perf"]], C["p"])
P["slope"] = 0.0; P["trail"] = 0.0      # 封面不要坡和雪痕，人物摆正
J = S.place(P)
g = Vector((P["gx"], 0, 0))
pos, tgt, lens = C["cam"]
S.camera(Vector(pos) + g, Vector(tgt) + g, lens)
meta = {}
if C.get("ring"):
    meta["ring"] = S.project({"r": J[C["ring"]]})["r"][:2]
S.render(out)
json.dump(meta, open(out[:-4] + ".json", "w"))
