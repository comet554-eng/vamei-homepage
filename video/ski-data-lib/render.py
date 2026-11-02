"""python3 render.py EPDIR still SCENE t1 t2 ...   |   python3 render.py EPDIR video SCENE OUT a b"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.abspath(sys.argv[1]); sys.path.insert(0, HERE); sys.path.insert(0, EP)
import numpy as np
from PIL import Image
from common import *
import scenes
OUT = os.path.join(EP, "out"); os.makedirs(OUT, exist_ok=True)
SC = {n: (f, d) for n, f, d in scenes.SCENES}
mode = sys.argv[2]
if mode == "still":
    name = sys.argv[3]; fn, _ = SC[name]; tiles = []
    for t in [float(x) for x in sys.argv[4:]]:
        s, c = new_surface(); fn(c, t, int(t * FPS)); s.flush()
        a = np.ndarray((H, W, 4), np.uint8, s.get_data())[..., [2, 1, 0]].copy()
        tiles.append(Image.fromarray(a).resize((W // 2, H // 2)))
    sheet = Image.new("RGB", (W, (len(tiles) + 1) // 2 * H // 2))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % 2) * W // 2, (i // 2) * H // 2))
    sheet.save(os.path.join(OUT, f"_still_{name}.png"))
else:
    name, out, a, b = sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6])
    fn, dur = SC[name]; b = min(b, int(round(dur * FPS)))
    wr = Writer(out)
    for i in range(a, b):
        s, c = new_surface(); fn(c, i / FPS, i); wr.write(s)
    wr.close()
