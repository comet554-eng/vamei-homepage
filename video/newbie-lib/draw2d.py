"""2D 扁平插画版：用和 3D 版完全相同的骨架（rig3d.skeleton）和相机，画成描边扁平风格。
draw_scene(c, P, cam) -> 关节在画面上的像素坐标 {名字: (x, y)}"""
import math
import cairo
from mathutils import Vector, Matrix
from rig3d import skeleton

W, H = 1080, 1920
OUT = (0.10, 0.12, 0.20)
SKY0, SKY1 = (0.55, 0.75, 0.93), (0.88, 0.94, 0.99)
SNOW, SNOW2 = (0.95, 0.97, 1.0), (0.84, 0.89, 0.96)
JACKET, JACKET2 = (0.98, 0.52, 0.12), (0.88, 0.40, 0.08)
PANTS, PANTS2 = (0.22, 0.27, 0.46), (0.17, 0.21, 0.37)
GLOVE = (0.16, 0.16, 0.20)
HELMET = (0.98, 0.98, 1.0)
GOGGLE = (0.30, 0.68, 1.0)
BOARD, BOARD2 = (0.22, 0.62, 0.95), (0.95, 0.97, 1.0)
BIND, STRAP = (0.20, 0.21, 0.25), (0.98, 0.70, 0.25)
SKIN = (0.96, 0.80, 0.68)
TREE, TREE2 = (0.36, 0.62, 0.55), (0.28, 0.52, 0.47)
MOUNT, MOUNT2, MOUNT3 = (0.97, 0.98, 1.0), (0.80, 0.86, 0.95), (0.70, 0.78, 0.90)


class Cam:
    def __init__(self, pos, tgt, lens):
        self.pos = Vector(pos); f = (Vector(tgt) - self.pos).normalized()
        r = f.cross(Vector((0, 0, 1))).normalized(); u = r.cross(f)
        self.f, self.r, self.u = f, r, u
        self.fpx = lens / 36.0 * H

    def depth(self, p):
        return (Vector(p) - self.pos).dot(self.f)

    def __call__(self, p):
        d = Vector(p) - self.pos
        z = max(1e-3, d.dot(self.f))
        return (W / 2 + self.fpx * d.dot(self.r) / z, H / 2 - self.fpx * d.dot(self.u) / z)

    def scale(self, p):
        return self.fpx / max(1e-3, self.depth(p))

    def horizon(self):
        h = Vector((self.f.x, self.f.y, 0)).normalized()
        return H / 2 - self.fpx * h.dot(self.u) / max(1e-3, h.dot(self.f))


def _poly(c, pts, fill, outline=OUT, lw=5):
    c.new_path(); c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.close_path()
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    if outline:
        c.set_source_rgb(*outline); c.set_line_width(lw * 2); c.stroke_preserve()
    c.set_source_rgb(*fill); c.fill()


def _limb(c, a, b, w, col, outline=OUT, lw=5):
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.new_path(); c.move_to(*a); c.line_to(*b)
    if outline:
        c.set_source_rgb(*outline); c.set_line_width(w + lw * 2); c.stroke_preserve()
    c.set_source_rgb(*col); c.set_line_width(w); c.stroke()


def background(c, cam):
    hy = cam.horizon()
    g = cairo.LinearGradient(0, 0, 0, hy); g.add_color_stop_rgb(0, *SKY0); g.add_color_stop_rgb(1, *SKY1)
    c.rectangle(0, 0, W, H); c.set_source(g); c.fill()
    if hy > 0:
        # 远山（三层），扁平雪山
        for k, (col, side, peaks) in enumerate(((MOUNT3, None, [(-80, 380), (260, 520), (620, 300), (980, 470), (1200, 360)]),
                                                (MOUNT2, None, [(-120, 250), (140, 300), (420, 210), (760, 330), (1160, 230)]),)):
            c.new_path(); c.move_to(-200, hy)
            for x, ht in peaks:
                c.line_to(x - 260, hy); c.line_to(x, hy - ht); c.line_to(x + 260, hy)
            c.line_to(W + 200, hy); c.close_path(); c.set_source_rgb(*col); c.fill()
            # 雪顶
            for x, ht in peaks:
                c.new_path(); c.move_to(x, hy - ht)
                c.line_to(x - 260 * 0.32, hy - ht * 0.68); c.line_to(x - 30, hy - ht * 0.74); c.line_to(x + 40, hy - ht * 0.62)
                c.line_to(x + 260 * 0.32, hy - ht * 0.68); c.close_path(); c.set_source_rgb(*MOUNT); c.fill()
        # 松树一排
        for i in range(-1, 14):
            x = i * 88 + (i * 37) % 50; s = 0.7 + ((i * 53) % 7) / 10
            for j, col in ((0, TREE2), (1, TREE)):
                c.new_path(); c.move_to(x, hy - 120 * s); c.line_to(x - 36 * s, hy + 2); c.line_to(x + 36 * s, hy + 2); c.close_path()
                c.set_source_rgb(*(TREE if (i % 3) else TREE2)); c.fill()
    g = cairo.LinearGradient(0, max(0, hy), 0, H); g.add_color_stop_rgb(0, *SNOW2); g.add_color_stop_rgb(0.35, *SNOW); g.add_color_stop_rgb(1, *SNOW)
    c.rectangle(0, max(0, hy), W, H); c.set_source(g); c.fill()


def slope_plane(c, cam, slope):
    """雪坡（过原点、绕 x 轴转 -slope 的平面）：它在画面上的“地平线”是一条直线，线下面都是坡面。"""
    if abs(slope) < 1e-3:
        return
    a = math.radians(slope)
    n = Vector((0, math.sin(a), math.cos(a)))
    nf, nr, nu = n.dot(cam.f), n.dot(cam.r), n.dot(cam.u)
    if nu <= 1e-4:
        return
    ys = [H / 2 + cam.fpx * (nf + (x - W / 2) / cam.fpx * nr) / nu for x in (-50, W + 50)]
    top = min(ys)
    g = cairo.LinearGradient(0, max(0, top), 0, H); g.add_color_stop_rgb(0, *SNOW2); g.add_color_stop_rgb(0.3, *SNOW); g.add_color_stop_rgb(1, *SNOW)
    c.new_path(); c.move_to(-50, ys[0]); c.line_to(W + 50, ys[1]); c.line_to(W + 50, H + 50); c.line_to(-50, H + 50); c.close_path()
    c.set_source(g); c.fill_preserve()
    c.set_source_rgba(*MOUNT3, 0.9); c.set_line_width(3); c.new_path(); c.move_to(-50, ys[0]); c.line_to(W + 50, ys[1]); c.stroke()


def snow_marks(c, cam, slope, center=(0.0, 0.0)):
    """坡面上固定不动的小雪包/雪印：人一动，它们相对人往后走，看得出在滑。"""
    S = Matrix.Rotation(math.radians(-slope), 3, "X")
    cx, cy = center
    for i in range(-16, 17):
        for j in range(-16, 17):
            h = (i * 73856093 ^ j * 19349663) & 0xffff
            x = i * 0.9 + (h % 97) / 97 * 0.7; y = j * 0.9 + ((h >> 7) % 89) / 89 * 0.7
            if abs(x - cx) > 9 or abs(y - cy) > 9:
                continue
            p = S @ Vector((x, y, 0.0))
            if cam.depth(p) < 0.6:
                continue
            q = cam(p); k = cam.scale(p)
            if not (-40 < q[0] < W + 40 and -40 < q[1] < H + 40):
                continue
            r = 0.035 + 0.03 * ((h >> 3) % 5) / 5
            e = S @ Vector((x + r, y, 0.0)); f = S @ Vector((x, y + r, 0.0))
            qe, qf = cam(e), cam(f)
            c.save(); c.translate(*q)
            m = cairo.Matrix(qe[0] - q[0], qe[1] - q[1], qf[0] - q[0], qf[1] - q[1], 0, 0)
            try:
                c.transform(m)
            except cairo.Error:
                c.restore(); continue
            c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
            c.set_source_rgba(0.66, 0.74, 0.87, 0.45); c.fill()


def trails(c, cam, J):
    """板在雪上推出来的痕（rig 里每段是一个 1×1 的面片的变换矩阵）。"""
    for m in J.get("trails", []):
        pts = [m @ Vector((x, y, 0.0)) for x, y in ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))]
        if min(cam.depth(p) for p in pts) < 0.3:
            continue
        q = [cam(p) for p in pts]
        c.new_path(); c.move_to(*q[0]); [c.line_to(*p) for p in q[1:]]; c.close_path()
        c.set_source_rgba(0.72, 0.80, 0.92, 0.75); c.fill()


def _board_outline(m, n=18):
    """板的轮廓（板局部坐标 -> 世界）：两头圆，带一点侧切。"""
    E, w = 0.66, 0.125                 # 有效刃长的一半、半宽
    pts = []
    for i in range(n + 1):
        x = -E + 2 * E * i / n
        pts.append((x, w - 0.012 * math.cos(math.pi * x / (2 * E))))
    for i in range(1, 12):
        a = math.pi / 2 - math.pi * i / 12
        pts.append((E + 0.12 * math.cos(a), w * math.sin(a)))
    for i in range(n + 1):
        x = E - 2 * E * i / n
        pts.append((x, -w + 0.012 * math.cos(math.pi * x / (2 * E))))
    for i in range(1, 12):
        a = -math.pi / 2 - math.pi * i / 12
        pts.append((-E + 0.12 * math.cos(a), w * math.sin(a)))
    return [m @ Vector((x, y, 0.02)) for x, y in pts]


def draw_rider(c, P, cam, shadow=True):
    J = skeleton(P)
    pr = {k: cam(v) for k, v in J.items() if isinstance(v, Vector)}
    m = J["board_m"]
    # 影子（太阳在左后方）
    if not shadow:
        return _draw_body(c, P, cam, J, pr, m)
    S = J["slope_m"].to_3x3(); Si = S.inverted()

    def shp(p):                          # 影子落在坡面上：先转到坡面坐标，压扁到坡面，再转回来
        l = Si @ Vector(p)
        return cam(S @ Vector((l.x + 0.25 + l.z * 0.6, l.y - 0.05 - l.z * 0.3, 0.0)))
    sh = [shp(p) for p in _board_outline(m, 10)]
    c.new_path(); c.move_to(*sh[0]); [c.line_to(*p) for p in sh[1:]]; c.close_path()
    c.set_source_rgba(0.35, 0.45, 0.65, 0.22); c.fill()
    for leg in ("L", "R"):
        a, k, hp = J["ankle" + leg], J["knee" + leg], J["hip" + leg]
        pts = [shp(p) for p in (a, k, hp, J["chest"], J["head"])]
        c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.new_path(); c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]
        c.set_source_rgba(0.35, 0.45, 0.65, 0.07); c.set_line_width(0.13 * cam.scale(a)); c.stroke()
    return _draw_body(c, P, cam, J, pr, m)


def _draw_body(c, P, cam, J, pr, m):
    # 板
    bo = [cam(p) for p in _board_outline(m)]
    s0 = cam.scale(J["pelvis"])
    _poly(c, bo, BOARD, lw=max(3, s0 * 0.012))
    # 板面白色条纹
    st = [cam(m @ Vector((x, y, 0.022))) for x, y in ((-0.55, 0.05), (0.55, 0.05), (0.55, -0.05), (-0.55, -0.05))]
    c.new_path(); c.move_to(*st[0]); [c.line_to(*p) for p in st[1:]]; c.close_path(); c.set_source_rgba(*BOARD2, 0.55); c.fill()
    # 固定器 + 鞋
    lw = max(3, s0 * 0.01)
    for side in ("L", "R"):
        fx = -0.26 if side == "L" else 0.26
        base = [cam(m @ Vector((fx + dx, dy, 0.03))) for dx, dy in ((-0.07, -0.15), (0.07, -0.15), (0.07, 0.15), (-0.07, 0.15))]
        _poly(c, base, BIND, lw=lw)
    order = sorted(("L", "R"), key=lambda s: -cam.depth(J["knee" + s]))
    sc = lambda p: cam.scale(p)
    for side in order:
        a, k, hp = J["ankle" + side], J["knee" + side], J["hip" + side]
        toe, heel = cam(m @ Vector(((-0.26 if side == "L" else 0.26), 0.14, 0.07))), cam(m @ Vector(((-0.26 if side == "L" else 0.26), -0.12, 0.07)))
        if side == "L" and P.get("lfw", 0) > 0.01:
            toe, heel = cam(a + Vector((0, 0.14, -0.06))), cam(a + Vector((0, -0.12, -0.06)))
        _limb(c, heel, toe, 0.12 * sc(a), (0.12, 0.12, 0.15), lw=lw)
        col = PANTS2 if side == order[0] else PANTS
        _limb(c, pr["knee" + side], pr["ankle" + side], 0.13 * sc(k), col, lw=lw)
        _limb(c, pr["hip" + side], pr["knee" + side], 0.16 * sc(k), col, lw=lw)
        # 固定器绑带
        sx = -0.26 if side == "L" else 0.26
        _limb(c, cam(m @ Vector((sx - 0.07, 0.04, 0.10))), cam(m @ Vector((sx + 0.07, 0.04, 0.10))), 0.035 * sc(a), STRAP, lw=max(2, lw * 0.6))
    # 骨盆（裤子）
    hl, hr = pr["hipL"], pr["hipR"]
    _limb(c, hl, hr, 0.18 * sc(J["pelvis"]), PANTS, lw=lw)
    # 手臂（远的一侧先画）
    arms = sorted(("L", "R"), key=lambda s: -cam.depth(J["elb" + s]))

    def arm(side, col):
        _limb(c, pr["sho" + side], pr["elb" + side], 0.11 * sc(J["elb" + side]), col, lw=lw)
        _limb(c, pr["elb" + side], pr["hand" + side], 0.10 * sc(J["hand" + side]), col, lw=lw)
        hx, hy = pr["hand" + side]; r = 0.055 * sc(J["hand" + side])
        c.new_path(); c.arc(hx, hy, r, 0, 2 * math.pi); c.set_source_rgb(*OUT); c.set_line_width(lw * 2); c.stroke_preserve()
        c.set_source_rgb(*GLOVE); c.fill()
    arm(arms[0], JACKET2)
    # 躯干
    tor = [pr["hipL"], pr["hipR"], pr["shoR"], pr["shoL"]]
    s1 = sc(J["chest"])
    c.new_path(); c.move_to(*tor[0]); [c.line_to(*p) for p in tor[1:]]; c.close_path()
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_source_rgb(*OUT); c.set_line_width(0.14 * s1 + lw * 2); c.stroke_preserve()
    c.set_source_rgb(*JACKET); c.set_line_width(0.14 * s1); c.stroke_preserve(); c.fill()
    # 拉链线
    zp = [cam(J["pelvis"] + (J["chest"] - J["pelvis"]) * 0.1 + Vector((0, 0.12, 0))), cam(J["neck"] + Vector((0, 0.08, 0)))]
    if cam.depth(J["chest"] + Vector((0, 0.2, 0))) < cam.depth(J["chest"]):
        c.new_path(); c.move_to(*zp[0]); c.line_to(*zp[1]); c.set_source_rgba(*OUT, 0.5); c.set_line_width(lw * 0.8); c.stroke()
    # 头
    hd = J["head"]; hx, hy = pr["head"]; r = 0.13 * sc(hd)
    _limb(c, pr["neck"], (hx, hy), 0.08 * sc(hd), SKIN, lw=lw)
    c.new_path(); c.arc(hx, hy, r, 0, 2 * math.pi); c.set_source_rgb(*OUT); c.set_line_width(lw * 2); c.stroke_preserve()
    c.set_source_rgb(*SKIN); c.fill()
    # 头盔（上半圆）
    face = J["head_m"].to_3x3() @ Vector((0, 1, 0))
    up = J["head_m"].to_3x3() @ Vector((0, 0, 1))
    pu = cam(hd + up * 0.13); ang = math.atan2(pu[1] - hy, pu[0] - hx)
    c.new_path(); c.arc(hx, hy, r * 1.08, ang - 1.75, ang + 1.75); c.close_path()
    c.set_source_rgb(*OUT); c.set_line_width(lw * 2); c.stroke_preserve(); c.set_source_rgb(*HELMET); c.fill()
    # 雪镜：在脸朝向的那一侧画一条蓝带
    pf = cam(hd + face * 0.13); vis = cam.depth(hd + face * 0.1) < cam.depth(hd)
    gx, gy = hx + (pf[0] - hx) * 0.55, hy + (pf[1] - hy) * 0.55
    gw = r * (1.25 if vis else 0.9)
    c.save(); c.translate(gx, gy); c.rotate(ang + math.pi / 2)
    c.new_path(); c.rectangle(-gw / 2, -r * 0.05 - r * 0.42, gw, r * 0.42)
    c.set_source_rgb(*OUT); c.set_line_width(lw * 1.6); c.stroke_preserve(); c.set_source_rgb(*(GOGGLE if vis else (0.25, 0.27, 0.32))); c.fill()
    c.restore()
    arm(arms[1], JACKET)
    pts = {k: pr[k] for k in pr}
    for nm, v in (("board", m @ Vector((0, 0, 0.02))), ("nose", m @ Vector((0.78, 0, 0.03))), ("tail", m @ Vector((-0.78, 0, 0.03))),
                  ("footR", m @ Vector((0.26, 0, 0.03))), ("footL", m @ Vector((-0.26, 0, 0.03))),
                  ("ground", Vector((J["pelvis"].x, J["pelvis"].y, 0.0)))):
        pts[nm] = cam(v)
    return pts


def draw_scene(c, P, cam_args, marks=False, extra=None):
    cam = Cam(*cam_args)
    background(c, cam)
    slope_plane(c, cam, P.get("slope", 0.0))
    if marks:
        snow_marks(c, cam, P.get("slope", 0.0), (P["gx"], P["gy"]))
    J = skeleton(P)
    trails(c, cam, J)
    pts = draw_rider(c, P, cam)
    if extra:
        pts.update({k: cam(v) for k, v in extra(P, J).items()})
    return pts
