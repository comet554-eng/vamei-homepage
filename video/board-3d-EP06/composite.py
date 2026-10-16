"""Overlay the series' 2D graphics on the 3D frames and encode.
python3 composite.py FRAMEDIR OUT.mp4"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ski-data-lib"))
import numpy as np
import cairo
from PIL import Image
from common import *
from art import *
from board import board_section, SERIES_B

FR, OUTF = sys.argv[1], sys.argv[2]
FPS, PH = 30, 3.5
ANG = [30, 45, 70]
COLS = [(0.45, 0.72, 1.0), (1.0, 0.80, 0.46), (0.92, 0.42, 0.36)]
RSC = 7.0
SUBS = [("立 {b|30°}：弯半径 = 7 × cos 30° ≈ {b|6.1 米}", 0.3, 3.4),
        ("立 {w|45°}：弯半径 ≈ {w|4.9 米}", 3.8, 6.9),
        ("立到 {r|70°}：只剩 {r|2.4 米}", 7.3, 10.4),
        ("同一块板，立得越陡，弯刻得越小。", 10.9, 14.3)]

files = sorted(f for f in os.listdir(FR) if f.endswith(".png"))
wr = Writer(OUTF)
for idx, fn in enumerate(files):
    t = idx / FPS
    im = Image.open(os.path.join(FR, fn)).convert("RGB").resize((W, H), Image.LANCZOS)
    a = np.asarray(im)
    rgba = np.dstack([a[..., 2], a[..., 1], a[..., 0], np.full(a.shape[:2], 255, np.uint8)]).copy()
    s = cairo.ImageSurface.create_for_data(memoryview(rgba), cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    i = min(2, int(t // PH)) if t < 3 * PH else 2
    top = t >= 3 * PH
    deg = ANG[i]; R = RSC * math.cos(math.radians(deg)); col = COLS[i]
    ain = ramp(t, 0.2, 0.8)
    chapter_tag(c, "理想刻滑", "R = R侧切 · cos θ · 3D 示意", ain)
    if not top:
        # readout card (top right)
        c.set_source_rgba(0.02, 0.025, 0.035, 0.78 * ain); rounded_rect(c, W - 520, 60, 450, 190, 16); c.fill()
        text(c, f"立刃 {deg}°", W - 295, 140, 64, col, ain, align="c", bold=True)
        text(c, f"弯半径 {R:.1f} m", W - 295, 210, 44, INK, ain, align="c", bold=True)
        # edge-angle gauge: board cross-section on a snow line
        gx, gy = W - 300, 820
        c.set_source_rgba(0.02, 0.025, 0.035, 0.78 * ain); rounded_rect(c, gx - 210, gy - 250, 420, 300, 16); c.fill()
        c.set_source_rgba(*RIM, 0.8 * ain); c.rectangle(gx - 180, gy, 360, 2); c.fill()
        k = min(1.0, (t - i * PH) / 0.6)
        prev = ANG[i - 1] if i > 0 else 0
        th = math.radians(prev + (deg - prev) * ease(k))
        board_section(c, gx + 60, gy, 150, th, ain)
        c.new_path(); c.arc(gx + 60, gy, 120, math.pi, math.pi + th); c.set_source_rgba(*col, ain); c.set_line_width(4); c.stroke()
        text(c, f"{math.degrees(th):.0f}°", gx - 110, gy - 30, 34, col, ain, bold=True)
        text(c, "板的横截面", gx, gy + 40, 22, DIM, ain, align="c")
    else:
        ka = ramp(t, 3 * PH + 1.6, 3 * PH + 2.4)
        c.set_source_rgba(0.02, 0.025, 0.035, 0.8 * ka); rounded_rect(c, W - 540, 60, 470, 260, 16); c.fill()
        for j in range(3):
            Rj = RSC * math.cos(math.radians(ANG[j]))
            c.set_source_rgba(*COLS[j], ka); c.rectangle(W - 500, 112 + j * 70, 46, 8); c.fill()
            text(c, f"{ANG[j]}°  →  {Rj:.1f} m", W - 430, 128 + j * 70, 40, COLS[j], ka, bold=True)
        cite_card(c, "Can J Phys · 2004", "理想刻滑：弯半径 ≈ R侧切 · cos θ", "Jentschura · Fahrbach", 0)
    for st, a0, a1 in SUBS:
        subtitle(c, st, t, a0, a1)
    model_note(c, ain, "3D 示意 · 侧切 7 m · 平地理想刻滑（无侧滑）")
    text(c, SERIES_B, W - 72, H - 40, 20, DIM, ain * 0.8, align="r", spacing=0.2)
    if not os.environ.get("NOFADE"):
        fade_black(c, 1 - ramp(t, 0, 0.5) + ramp(t, len(files) / FPS - 0.6, len(files) / FPS))
    s.flush()
    wr.write(s)
wr.close()
print("frames", len(files))
