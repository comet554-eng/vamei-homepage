"""李财（三花猫主持人）叠加层：素材来自骑行系列（licai-seq/*.js，逐帧动画，已转成 licai/<动作>/<帧>.webp + seq.json）。
李财只当主持人做出场和反应，技术动作仍由 2D 人物演示。
每集都按段落自动出场（见 ROLES），ep.py 里可以用 LICAI = {段落: [...]} 覆盖。"""
import os, json, math
import cairo
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.environ.get("LICAI_DIR", os.path.join(HERE, "licai"))
META = json.load(open(os.path.join(DIR, "seq.json")))
REF = META["ref"]
_cache = {}


def _frame(name, i):
    k = (name, i)
    if k not in _cache:
        im = Image.open(os.path.join(DIR, name, f"{i}.webp")).convert("RGBA")
        a = np.asarray(im).astype(np.float32)
        al = a[..., 3:4] / 255.0
        bgra = np.dstack([a[..., 2:3] * al, a[..., 1:2] * al, a[..., 0:1] * al, a[..., 3:4]]).astype(np.uint8).copy()
        s = cairo.ImageSurface.create_for_data(memoryview(bgra), cairo.FORMAT_ARGB32, im.width, im.height)
        _cache[k] = (s, bgra)
    return _cache[k][0]


def draw(c, name, t, x, y, h, fps=6, once=False, flip=False, alpha=1.0, rot=0.0, scale=1.0):
    """在 (x, y)（脚底中心）画李财的第 t 秒那一帧，高 h（按该动作的参考高度缩放）。"""
    if alpha <= 0 or name not in META["seq"]:
        return
    fr = META["seq"][name]; n = len(fr)
    i = int(max(0.0, t) * fps)
    i = min(i, n - 1) if once else i % n
    ox, oy = fr[i]
    s = h / REF * scale
    surf = _frame(name, i)
    c.save(); c.translate(x, y)
    if rot:
        c.rotate(rot)
    c.scale(-s if flip else s, s)
    c.set_source_surface(surf, ox, oy)
    c.paint_with_alpha(alpha)
    c.restore()


def _ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def _win(t, a, b, f=0.25):
    if t < a - f or t > b + f:
        return 0.0
    return min(_ease((t - a + f) / f), _ease((b + f - t) / f))


# 每段默认：(动作, 帧率, 只播一遍, x, y, 高, 左右翻转)
MISTAKE_REACT = [("摔跟头", 7, True), ("害羞捂脸", 6, False), ("吓一跳", 7, True), ("委屈难过", 5, False)]
POS = dict(side=(915, 1270, 250), foot=(860, 1500, 300), chart=(905, 1012, 215))


def overlay(c, t, sec, dur, kind, custom=None):
    """kind: 当前帧是 "F"（实拍）还是 "R"（演示）。sec = ep.SEC。"""
    custom = custom or {}
    if "hook" in sec:
        h0, h1, hs = sec["hook"]
        a = _win(t, h0 + 0.3, h1 - 0.1)
        if a > 0:
            k = _ease((t - h0 - 0.3) / 1.4)
            x = -220 + (560 + 220) * k
            bob = 10 * math.sin(t * 6)
            name = custom.get("hook", "滑雪板")
            draw(c, name, t, x, 1490 + bob, 400, fps=8, alpha=a, rot=-0.06 * (1 - k))
    for key in ("setup", "keys", "steps"):
        if key in sec:
            k0, k1, ks = sec[key]
            a = _win(t, k0 + 0.4, k1 - 0.2)
            x, y, h = POS["side"]
            draw(c, custom.get(key, "点头指向"), t - k0, x, y, h, fps=5, flip=True, alpha=a)
    if "why" in sec:
        w0, w1, ws = sec["why"]
        x, y, h = POS["chart"]
        cut = ws[1][1] if len(ws) > 1 else w0 + 2
        draw(c, custom.get("why0", "思考怀疑"), t - w0, x, y, h, fps=4, alpha=_win(t, w0 + 0.3, cut - 0.15) * (kind == "R" or 1))
        draw(c, custom.get("why1", "划重点"), t - cut, x, y, h, fps=5, alpha=_win(t, cut, w1 - 0.2))
    if "mistakes" in sec:
        m0, m1, ms = sec["mistakes"]
        x, y, h = POS["side"]
        for j, s in enumerate(ms):
            e = ms[j + 1][1] - 0.1 if j + 1 < len(ms) else m1 - 0.2
            nm, fps, once = (custom.get("mistakes") or MISTAKE_REACT)[j % 4]
            draw(c, nm, t - s[1], x, y, h * (1.9 if nm == "摔跟头" else 1), fps=fps, once=once, alpha=_win(t, s[1] + 0.1, e, 0.2))
    if "drill" in sec:
        d0, d1, ds = sec["drill"]
        cut = ds[1][1] if len(ds) > 1 else d1
        x, y, h = POS["side"]
        draw(c, custom.get("drill0", "叉腰得意"), t - d0, x, y, h, fps=5, alpha=_win(t, d0 + 0.3, cut - 0.2))
        x, y, h = POS["foot"]
        draw(c, custom.get("drill1", "拍手"), t - cut, x, y, h, fps=6, alpha=_win(t, cut + 0.2, d1 - 0.1))
    if "end" in sec:
        e0, e1, _ = sec["end"]
        a = _win(t, e0 + 0.2, dur + 1)
        draw(c, custom.get("end", "开心挥手"), t - e0, 540, 1530, 380, fps=6, alpha=a)
