"""S7 back to the snow: one arc, its radius and edge angle;  S8 sources."""
import math
import numpy as np
from common import *
from draw import *
import ski
from s_top import TRACK, draw_track_scene

S7_DUR = 26.0
S7_SUBS = [
    ("回到那道雪痕。这一段弧：", 1.0, 5.4),
    ("板立了 55°，弧的半径约 4.6 米——\n正是 8 米 × cos 55°。", 5.8, 12.4),
    ("板会自己转弯，是因为它两边本来就是弧；\n立多陡，就决定了弯多大。", 13.0, 20.0),
    ("剩下的，是让速度和身体跟上它。", 20.6, 25.0),
]
# apex of a turn: maximum edge angle
_i = int(np.argmax(np.abs(TRACK[len(TRACK) // 3: 2 * len(TRACK) // 3, 3]))) + len(TRACK) // 3
APEX = TRACK[_i]


def s7(c, t, fi):
    paint_bg(c, (0.02, 0.025, 0.035))
    S = lerp(70.0, 34.0, ease_io((t - 18.0) / 7.0))
    s_r = APEX[4] + 6.0

    def extra(c, sx, sy):
        a = ramp(t, 5.6, 7.0) * (1 - ramp(t, 19.0, 21.0))
        if a <= 0:
            return
        th = abs(APEX[3])
        r = ski.turn_radius(th)
        sgn = APEX[5]
        h = APEX[2]
        nx, ny = -math.sin(h) * sgn, math.cos(h) * sgn
        cx, cy = APEX[0] + nx * r, APEX[1] + ny * r
        c.set_dash([12, 9]); c.set_source_rgba(0.55, 0.38, 0.10, 0.95 * a); c.set_line_width(3.2)
        c.arc(sx(cx), sy(cy), r * S, 0, 2 * math.pi); c.stroke()
        c.move_to(sx(cx), sy(cy)); c.line_to(sx(APEX[0]), sy(APEX[1])); c.stroke(); c.set_dash([])
        c.arc(sx(cx), sy(cy), 5, 0, 2 * math.pi); c.fill()
        pill_label(c, f"立刃 {math.degrees(th):.0f}° · 半径 {r:.1f} m", sx(cx), sy(cy) - 24, 28, GOLD, a)

    draw_track_scene(c, s_r, S=S, rider_y=H * 0.42, show_rider=False, extra=extra, focus=(APEX[0] + 2.0 * APEX[5], APEX[1]))
    chapter_tag(c, "2 m", "雪痕 · 俯视", alpha=window(t, 0.4, 21.0, 0.5), bar=2 * S)
    for st, a, b in S7_SUBS:
        subtitle(c, st, t, a, b)
    fade_black(c, 1 - ramp(t, 0, 0.8))
    fade_black(c, ramp(t, S7_DUR - 1.2, S7_DUR))
    overlays(c, fi)


def at_y(s_r):
    i = int(np.clip(np.searchsorted(TRACK[:, 4], s_r), 1, len(TRACK) - 1))
    return TRACK[i, 1]


S8_DUR = 11.0
SOURCES = [
    "Jentschura U. D., Fahrbach F. Physics of skiing: the ideal-carving equation and its applications. arXiv:physics/0310086",
    "Reid R. C., Haugen P., Gilgien M., Kipp R. W., Smith G. A. Alpine ski motion characteristics in slalom. Front. Sports Act. Living 2:25 (2020)",
    "Howe J. The New Skiing Mechanics (2001) — turn-radius formula, as cited in Reid et al. 2020",
    "Kröll J. et al. Sidecut radius and the mechanics of turning. Br. J. Sports Med. 50 (2016)",
    "Physics of skiing FAQ, rec.skiing.alpine (sidecut-radius geometry)",
]


def s8(c, t, fi):
    paint_bg(c, (0.012, 0.014, 0.018))
    a = window(t, 0.3, S8_DUR - 0.2, 0.8)
    text(c, "资料", 160, 250, 40, INK, a, bold=True)
    c.set_source_rgba(*FAINT, a); c.rectangle(160, 280, 1600, 1.2); c.fill()
    for i, s in enumerate(SOURCES):
        text(c, s, 160, 350 + i * 64, 23, (0.74, 0.77, 0.81), a)
    text(c, "片中雪道、雪板与人物为程序绘制的示意图；半径、速度与板的弯曲均按文中公式实时计算。", 160, 720, 24, DIM, a)
    text(c, "简化：理想刚性雪面、整条刃贴雪、人视为一个点、平地。真实滑行在坡上，立刃与速度一直在变。", 160, 762, 24, DIM, a)
    overlays(c, fi, vig=0.6)
