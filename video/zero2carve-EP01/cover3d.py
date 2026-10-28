"""封面用的 3D 人物（透明底 PNG + 手腕位置）：python cover3d.py OUT.png"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "zero2carve-lib"))
import ep
from rig3d import Scene, interp

out = sys.argv[1]
S = Scene(1200, 1200, samples=int(os.environ.get("SAMPLES", 24)), transparent=True)
P = interp(ep.A, ep.A_IMPACT)
J = S.place(P)
gx = P["gx"]
S.camera((gx + 2.6, 1.9, 0.75), (gx, -0.35, 0.42), 34)
m = S.project({"hand": J["handL"] if (J["handL"] - S.cam.location).length < (J["handR"] - S.cam.location).length else J["handR"]})
S.render(out)
json.dump({"ring": m["hand"][:2]}, open(out[:-4] + ".json", "w"))
