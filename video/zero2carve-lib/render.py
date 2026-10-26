"""渲 3D 帧（bpy 环境），各集共用（METAONLY=1 时只重写已渲帧的 .json）：
  python render.py EPDIR OUTDIR                 渲全片需要的不重复帧（已存在的跳过，可断点续渲）
  python render.py EPDIR OUTDIR preview S:p ... 低清预览
EPDIR/ep.py 需要提供 PERF{表演名: 关键帧}、SHOT_PERF{镜头: 表演名}、cam(shot, p, P)、plan()。"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.abspath(sys.argv[1])
sys.path.insert(0, EP); sys.path.insert(0, HERE)
import ep
from rig3d import Scene, interp
from epbase import key

OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
preview = len(sys.argv) > 3 and sys.argv[3] == "preview"
RW, RH = int(os.environ.get("RW", 720)), int(os.environ.get("RH", 1280))
S = Scene(RW, RH, samples=int(os.environ.get("SAMPLES", 6)))

if preview:
    jobs = [(a.split(":")[0], ep.SHOT_PERF[a.split(":")[0]], float(a.split(":")[1])) for a in sys.argv[4:]]
else:
    seen, jobs = set(), []
    for shot, perf, p in ep.plan():
        k = key(shot, p)
        if k not in seen:
            seen.add(k); jobs.append((shot, perf, round(p * 60) / 60))

PTS = ["handL", "handR", "elbL", "elbR", "pelvis", "head", "kneeL", "kneeR", "chest", "ankleL", "ankleR", "hipL", "hipR"]
for n, (shot, perf, p) in enumerate(jobs):
    k = key(shot, p)
    path = os.path.join(OUT, k + ".png")
    meta_only = os.environ.get("METAONLY") and os.path.exists(path)     # 只重算关节投影，不重渲
    if os.path.exists(path) and not preview and not meta_only:
        continue
    P = interp(ep.PERF[perf], p)
    J = S.place(P)
    pos, tgt, lens = ep.cam(shot, p, P)
    S.camera(pos, tgt, lens)
    pts = {q: J[q] for q in PTS}
    pts.update({q: v for q, v in getattr(ep, "extra_points", lambda P, J: {})(P, J).items()})
    meta = S.project(pts)
    meta["_z"] = {q: round(J[q].z, 3) for q in PTS}
    meta["_pose"] = {q: P[q] for q in ("broll", "gx", "gy", "slope", "tilt", "yaw", "px")}
    if not meta_only:
        S.render(path)
    with open(os.path.join(OUT, k + ".json"), "w") as f:
        json.dump(meta, f)
    print(f"[{n + 1}/{len(jobs)}] {k}", flush=True)
