"""渲 3D 帧（bpy 环境）：
  python render.py OUTDIR                 渲全片需要的所有不重复帧（已存在的跳过，可断点续渲）
  python render.py OUTDIR preview S:p ... 低清预览指定镜头/表演时间
每帧旁边写一个 .json：关节在画面里的位置（给 2D 叠加用）。"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "zero2carve-lib"))
import ep
from rig3d import Scene, interp

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
preview = len(sys.argv) > 2 and sys.argv[2] == "preview"
RW, RH = (int(os.environ.get("RW", 720)), int(os.environ.get("RH", 1280)))
S = Scene(RW, RH, samples=int(os.environ.get("SAMPLES", 6)))

if preview:
    jobs = []
    for a in sys.argv[3:]:
        shot, p = a.split(":"); jobs.append((shot, {"A1": "A", "A2": "A"}.get(shot, shot), float(p)))
else:
    seen, jobs = set(), []
    for shot, perf, p in ep.plan():
        k = ep.key(shot, p)
        if k not in seen:
            seen.add(k); jobs.append((shot, perf, round(p * 60) / 60))

PTS = ["handL", "handR", "elbL", "elbR", "pelvis", "head", "kneeL", "kneeR", "chest", "ankleL", "ankleR"]
for n, (shot, perf, p) in enumerate(jobs):
    k = ep.key(shot, p)
    path = os.path.join(OUT, k + ".png")
    if os.path.exists(path) and not preview:
        continue
    P = interp(ep.PERF[perf], p)
    J = S.place(P)
    pos, tgt, lens = ep.cam(shot, p, P["gx"])
    S.camera(pos, tgt, lens)
    meta = S.project({q: J[q] for q in PTS})
    meta["_z"] = {q: round(J[q].z, 3) for q in PTS}
    S.render(path)
    with open(os.path.join(OUT, k + ".json"), "w") as f:
        json.dump(meta, f)
    print(f"[{n + 1}/{len(jobs)}] {k}", flush=True)
