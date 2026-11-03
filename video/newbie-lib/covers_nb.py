"""《单板新手课》封面（明亮风）：实拍雪山做底 + 人物（3D 渲染或 2D 插画）+ 大标题。
python3 covers_nb.py EPDIR 2d|3d BG.jpg OUT_PREFIX [RIDER3D.png]
第2课起每集 ep.py 里写 COVER = dict(title, sub, items, perf, p, cam, bg=(素材ID, 秒))；只出 竖版3x4 和 横版4x3（2026-11 起）。
BG.jpg 写 auto 时，按 COVER["bg"] 从 Mixkit 原片里截一帧。"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); EP = os.path.abspath(sys.argv[1]); sys.path.insert(0, EP)
import ep
import cairo
import numpy as np
from PIL import Image, ImageFilter
from vert import font, tw, rrect, stroke_text, GOLD, ICE, INK

MODE, BG, OUT = sys.argv[2], sys.argv[3], sys.argv[4]
R3D = sys.argv[5] if len(sys.argv) > 5 else None
SIZES = {"竖版3x4": (1080, 1440), "横版4x3": (1440, 1080)}
if os.environ.get("ALL4"):
    SIZES = {"竖版9x16": (1080, 1920), **SIZES, "横版16x9": (1920, 1080)}
CV = getattr(ep, "COVER", None) or dict(title="基本站姿", sub="站对了，后面才不摔", items=["屈膝", "重心", "上身", "视线"],
                                        perf="K", p=12.0, cam=ep.COVER3D["cam"])
if BG == "auto":
    import subprocess, tempfile
    BG = os.path.join(tempfile.gettempdir(), f"cover_bg_{ep.LESSON}.jpg")
    clips = os.environ.get("CLIPS", "")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(CV["bg"][1]), "-i", os.path.join(clips, f"mixkit-{CV['bg'][0]}.mp4"),
                    "-frames:v", "1", BG], check=True)


def rider_image():
    if MODE == "3d":
        from PIL import ImageEnhance
        im = Image.open(R3D).convert("RGBA")
        al = im.getchannel("A")
        rgb = ImageEnhance.Contrast(ImageEnhance.Color(im.convert("RGB")).enhance(1.35)).enhance(1.12)
        im = rgb.convert("RGBA"); im.putalpha(al.point(lambda v: 0 if v < 90 else v))   # 去掉淡淡的影子
        return im
    from rig3d import interp
    from draw2d import draw_rider, Cam
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1080, 1920); c = cairo.Context(s)
    P = interp(ep.PERF[CV["perf"]], CV["p"])
    P.update(gx=0.0, gy=0.0, slope=0.0, trail=0.0)          # 封面：人物摆正，不要坡和雪痕
    P.update(CV.get("set", {}))
    draw_rider(c, P, Cam(*CV["cam"]), shadow=False)
    s.flush()
    a = np.ndarray((1920, 1080, 4), np.uint8, s.get_data()).copy()
    im = Image.fromarray(a[..., [2, 1, 0, 3]], "RGBA")
    return im.crop(im.getbbox())


RIDER = rider_image()
RIDER = RIDER.crop(RIDER.getbbox())
bg0 = Image.open(BG).convert("RGB")

for name, (w, h) in SIZES.items():
    # 底图：实拍铺满 + 轻微压暗
    bw, bh = bg0.size; k = max(w / bw, h / bh)
    bg = bg0.resize((int(bw * k) + 1, int(bh * k) + 1), Image.LANCZOS)
    x0 = (bg.width - w) // 2; y0 = (bg.height - h) // 2
    bg = bg.crop((x0, y0, x0 + w, y0 + h)).filter(ImageFilter.GaussianBlur(2))
    a = np.asarray(bg, float) / 255
    yy = np.linspace(0, 1, h)[:, None, None]; xx = np.linspace(0, 1, w)[None, :, None]
    portrait = h > w
    if portrait:
        dark = 0.62 * np.clip(1 - yy / 0.45, 0, 1) + 0.35 * np.clip((yy - 0.75) / 0.25, 0, 1)
    else:
        dark = 0.65 * np.clip(1 - xx / 0.55, 0, 1)
    a = a * (1 - dark) + np.array([0.02, 0.05, 0.12]) * dark
    img = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    # 人物
    if portrait:
        rh = int(h * (0.56 if h / w > 1.6 else 0.50)); rx = 0.5; ry = 0.98
    else:
        rh = int(h * 0.84); rx = 0.74; ry = 0.97
    r = RIDER.resize((int(RIDER.width * rh / RIDER.height), rh), Image.LANCZOS)
    pad = 60     # 影子先留边再模糊，不然模糊被裁在人物框里，会留下一道方形的边
    sh = Image.new("RGBA", (r.width + 2 * pad, r.height + 2 * pad), (0, 0, 0, 0))
    al = Image.new("L", sh.size, 0); al.paste(r.getchannel("A").point(lambda v: int(v * 0.45)), (pad, pad)); sh.putalpha(al)
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    px = int(w * rx - r.width / 2); py = int(h * ry - r.height)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); lay.paste(sh, (px + 14 - pad, py + 18 - pad)); img.alpha_composite(lay)
    img.alpha_composite(r, (px, py))
    # 文字
    arr = np.asarray(img.convert("RGB"))
    buf = np.dstack([arr[..., 2], arr[..., 1], arr[..., 0], np.full((h, w), 255, np.uint8)]).copy()
    s = cairo.ImageSurface.create_for_data(memoryview(buf), cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s)
    u = min(w, h) / 1080
    if portrait:
        tx, ty, al = w / 2, h * (0.10 if h / w > 1.6 else 0.09), "c"
    else:
        tx, ty, al = 90 * u, 190 * u, "l"
    stroke_text(c, ep.SERIES + f" · 第{ep.LESSON}课", tx, ty + 30 * u, 44 * u, GOLD, 1, align=al, stroke=7 * u, spacing=0.12)
    fs = 190 if len(CV["title"]) <= 4 else 150
    stroke_text(c, CV["title"], tx, ty + 210 * u, fs * u, INK, 1, align=al, stroke=16 * u, face="Noto Serif SC")
    stroke_text(c, CV["sub"], tx, ty + 320 * u, 62 * u, ICE, 1, align=al, stroke=9 * u)
    # 四个要点小标签
    items = CV["items"]
    font(c, 36 * u, True)
    ws = [tw(c, it) + 50 * u for it in items]; gap = 16 * u
    total = sum(ws) + gap * 3
    x = tx - total / 2 if al == "c" else tx
    y = ty + 370 * u
    for it, ww in zip(items, ws):
        c.set_source_rgba(0.02, 0.05, 0.12, 0.7); rrect(c, x, y, ww, 62 * u, 31 * u); c.fill()
        c.set_source_rgba(*GOLD, 1); c.set_line_width(3 * u); rrect(c, x, y, ww, 62 * u, 31 * u); c.stroke()
        stroke_text(c, it, x + ww / 2, y + 44 * u, 36 * u, INK, 1, stroke=0)
        x += ww + gap
    tagtxt = "3D 演示" if MODE == "3d" else "2D 演示"
    font(c, 30 * u, True); tww = tw(c, tagtxt)
    bx = (w - tww - 70 * u) if portrait else (90 * u)
    by = (h - 110 * u) if portrait else (h - 120 * u)
    c.set_source_rgba(*ICE, 0.95); rrect(c, bx, by, tww + 40 * u, 54 * u, 27 * u); c.fill()
    stroke_text(c, tagtxt, bx + 20 * u + tww / 2, by + 38 * u, 30 * u, (0.02, 0.05, 0.12), 1, stroke=0)
    s.flush()
    out = np.ndarray((h, w, 4), np.uint8, s.get_data())
    Image.fromarray(out[..., [2, 1, 0]]).save(f"{OUT}-{name}.jpg", quality=92)
    print(name)
