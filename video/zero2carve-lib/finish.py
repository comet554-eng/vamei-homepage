"""给合成好的无声成片配上背景音乐和音效，再压成最终 mp4：
python3 finish.py EPDIR RAW.mp4 OUT.mp4
EPDIR/ep.py 里：MUSIC = "pop" | "drive" | None；music_hits() -> (重拍时刻列表, [(时刻, "boom"|"ding"|"whoosh")])"""
import sys, os, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.abspath(sys.argv[1]); sys.path.insert(0, EP); sys.path.insert(0, HERE)
import ep

raw, out = sys.argv[2], sys.argv[3]
style = getattr(ep, "MUSIC", None)
if style:
    hits, sfx = ep.music_hits() if hasattr(ep, "music_hits") else ([], [])
    wav = os.path.join(tempfile.gettempdir(), f"music_{ep.LESSON}.wav")
    subprocess.run([sys.executable, os.path.join(HERE, "..", "ski-data-lib", "music_up.py"), wav, f"{ep.DUR:.2f}",
                    "--style", style, "--level", "-22",
                    "--hits", ",".join(f"{h:.2f}" for h in hits),
                    "--sfx", ",".join(f"{t:.2f}:{k}" for t, k in sfx)], check=True)
    aud = ["-i", wav]
else:
    aud = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw] + aud + ["-shortest", "-c:v", "libx264", "-crf", "21", "-preset", "slow",
                "-pix_fmt", "yuv420p", "-af", "alimiter=limit=0.84:level=false", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
print("ok", out)
