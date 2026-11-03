"""实拍片段：按 ep.FOOT 从 Mixkit 横版原片裁出竖条（608×1080，带横向平移），放大到 1080×1920，存成 jpg 序列；
同时把实际用到的那段原片（不裁）存成 镜头X-mixkit-ID.mp4，放进素材目录备查。
python3 foot.py EPDIR CLIPS_DIR FOOT_OUT [CLIP_COPY_DIR]
FOOT = {镜头名: (素材ID, 入点秒, 平移起点 0..1, 平移终点 0..1)}"""
import sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.abspath(sys.argv[1]); sys.path.insert(0, EP); sys.path.insert(0, HERE)
import ep

CL, OUT = sys.argv[2], sys.argv[3]
COPY = sys.argv[4] if len(sys.argv) > 4 else None
need = {}
for k, n, t in ep.plan():
    if k == "F":
        need[n] = max(need.get(n, 0), t)
letters = iter("ABCDEFGHIJKL")
for n in ep.FOOT:
    if n not in need:
        continue
    mid, ss, a, b = ep.FOOT[n]; D = need[n] + 0.2
    d = os.path.join(OUT, n); os.makedirs(d, exist_ok=True)
    src = os.path.join(CL, f"mixkit-{mid}.mp4")
    vf = f"fps=30,crop=608:1080:x='(iw-608)*({a}+({b}-{a})*t/{D})':y=0,scale=1080:1920:flags=lanczos"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", f"{D:.2f}", "-i", src, "-vf", vf, "-q:v", "3",
                    os.path.join(d, "%04d.jpg")], check=True)
    if COPY:
        os.makedirs(COPY, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", f"{D:.2f}", "-i", src, "-an", "-c:v", "libx264",
                        "-crf", "23", "-preset", "medium", os.path.join(COPY, f"镜头{next(letters)}-mixkit-{mid}.mp4")], check=True)
    print(n, mid, f"{ss:.1f}-{ss + D:.1f}s", len(os.listdir(d)), "frames")
