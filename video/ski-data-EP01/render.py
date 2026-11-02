"""usage:
  python3 render.py still SCENE t1 t2 ...       -> out/_still_SCENE.png contact sheet
  python3 render.py video SCENE OUT.mp4 [a b]   -> encode frames a..b of SCENE
  python3 render.py all                          -> chunked render of every scene into out/parts, then concat
"""
import os, sys, time, subprocess
import numpy as np
from PIL import Image
from common import *
import scenes

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
SC = {n: (f, d) for n, f, d in scenes.SCENES}


def frame_to_np(surf):
    surf.flush()
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    return a[..., [2, 1, 0]].copy()


def still(name, ts):
    fn, _ = SC[name]
    tiles = []
    for t in ts:
        s, c = new_surface()
        t0 = time.time(); fn(c, t, int(t * FPS))
        print(f"{name} t={t:6.2f} {1000 * (time.time() - t0):.0f} ms")
        tiles.append(Image.fromarray(frame_to_np(s)).resize((W // 2, H // 2)))
    rows = (len(tiles) + 1) // 2
    sheet = Image.new("RGB", (W, rows * H // 2))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % 2) * W // 2, (i // 2) * H // 2))
    p = os.path.join(OUT, f"_still_{name}.png"); sheet.save(p); print(p)


def video(name, out, a=0, b=None):
    fn, dur = SC[name]
    n = int(round(dur * FPS)); b = n if b is None else min(n, b)
    wr = Writer(out)
    for i in range(a, b):
        s, c = new_surface(); fn(c, i / FPS, i); wr.write(s)
    wr.close()


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        still(sys.argv[2], [float(x) for x in sys.argv[3:]])
    elif mode == "video":
        video(sys.argv[2], sys.argv[3], *(int(x) for x in sys.argv[4:6]))
