"""Render scenes. usage:
  python render.py still SCENE t1 t2 ...   -> contact sheet PNG of those times
  python render.py video SCENE OUT.mp4      -> encode scene
"""
import sys, time, importlib
import numpy as np
from PIL import Image
from common import *

SCENES = {}


def reg():
    import importlib
    for mod, names in (("s_top", ["s1", "s2"]), ("s_cut", ["s3"]), ("s_edge", ["s4"]),
                       ("s_body", ["s5", "s6"]), ("s_end", ["s7", "s8"])):
        try:
            m = importlib.import_module(mod)
        except ImportError as e:
            print("partial:", e); continue
        for n in names:
            SCENES[n] = (getattr(m, n), getattr(m, n.upper() + "_DUR"))


ORDER = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8"]


def frame_to_np(surf):
    surf.flush()
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    return a[..., [2, 1, 0]].copy()


if __name__ == "__main__":
    reg()
    mode, name = sys.argv[1], sys.argv[2]
    fn, dur = SCENES[name]
    if mode == "still":
        ts = [float(x) for x in sys.argv[3:]]
        tiles = []
        for t in ts:
            s, c = new_surface()
            t0 = time.time()
            fn(c, t, int(t * FPS))
            print(f"t={t:6.2f}  {1000 * (time.time() - t0):.0f} ms")
            tiles.append(Image.fromarray(frame_to_np(s)).resize((W // 2, H // 2)))
        cols = 2
        rows = (len(tiles) + 1) // 2
        sheet = Image.new("RGB", (cols * W // 2, rows * H // 2))
        for i, im in enumerate(tiles):
            sheet.paste(im, ((i % cols) * W // 2, (i // cols) * H // 2))
        sheet.save(f"/sessions/nice-happy-fermi/mnt/outputs/_still_{name}.png")
    else:
        out = sys.argv[3]
        wr = Writer(out)
        n = int(round(dur * FPS))
        a = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        b = min(n, int(sys.argv[5])) if len(sys.argv) > 5 else n
        t0 = time.time()
        for i in range(a, b):
            s, c = new_surface()
            fn(c, i / FPS, i)
            wr.write(s)
            if i % 150 == 0:
                print(name, i, n, f"{time.time() - t0:.0f}s", flush=True)
        wr.close()
        print(name, "done", f"{time.time() - t0:.0f}s")
