"""渲 3D 帧（bpy）：python render3d.py EPDIR OUTDIR [preview SHOT:p ...]
已存在的帧跳过（可断点续渲）；每帧旁边存 .json（关节在画面上的像素位置，合成时用来画标注）。"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.abspath(sys.argv[1]); sys.path.insert(0, EP); sys.path.insert(0, HERE)
import ep
from rig3d import interp
from rig3d_day import Scene
from epbase import key

OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
preview = len(sys.argv) > 3 and sys.argv[3] == "preview"
RW, RH = int(os.environ.get("RW", 640)), int(os.environ.get("RH", 1138))
S = Scene(RW, RH, samples=int(os.environ.get("SAMPLES", 6)))
if preview:
    jobs = [(a.split(":")[0], float(a.split(":")[1])) for a in sys.argv[4:]]
else:
    seen, jobs = set(), []
    for kind, shot, p in ep.plan():
        if kind != "R":
            continue
        k = key(shot, p)
        if k not in seen:
            seen.add(k); jobs.append((shot, p))
    part = os.environ.get("PART")          # "i/n"：分给多个进程
    if part:
        i, n = map(int, part.split("/")); jobs = jobs[i::n]
PTS = ["handL", "handR", "elbL", "elbR", "pelvis", "head", "kneeL", "kneeR", "chest", "ankleL", "ankleR", "hipL", "hipR", "neck"]
for n, (shot, p) in enumerate(jobs):
    k = key(shot, p)
    path = os.path.join(OUT, k + ".png")
    if os.path.exists(path) and not preview:
        continue
    P = interp(ep.PERF[ep.SHOT_PERF[shot]], p)
    J = S.place(P)
    pos, tgt, lens = ep.cam(shot, p, P)
    S.camera(pos, tgt, lens)
    pts = {q: J[q] for q in PTS}
    pts.update(ep.extra_points(P, J))
    meta = S.project(pts)
    S.render(path)
    with open(os.path.join(OUT, k + ".json"), "w") as f:
        json.dump(meta, f)
    print(f"[{n + 1}/{len(jobs)}] {k}", flush=True)
