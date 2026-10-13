"""Physics + geometry for the carving film. Everything shown is computed from these functions.

Sources:
  R_turn = R_sc * cos(theta)                  Howe 2001; Jentschura & Fahrbach arXiv physics/0310086 eq.(6)
  balance on flat ground: tan(Phi) = v^2/(g R) J&F eq.(29) with slope = 0
  => ideal speed v = sqrt(g R_sc sin(theta))   (edge angle = lean angle, point-mass rider)
  sidecut depth d ~ C^2 / (8 R_sc)             J&F eq.(4)
"""
import math
import numpy as np

G = 9.81
BOARD_L = 1.56      # m, overall length
BOARD_C = 1.25      # m, effective edge (contact) length  (J&F typical snowboard)
BOARD_W = 0.25      # m, width at nose/tail contact points
R_SC = 8.0          # m, snowboard sidecut radius (J&F: 6-8 m)
R_SL = 14.0         # m, slalom ski used by Reid et al. 2020


def sag(R=R_SC, C=BOARD_C):
    """exact sidecut depth of a circular arc with chord C."""
    return R - math.sqrt(R * R - (C / 2) ** 2)


def turn_radius(theta, R=R_SC):
    return R * math.cos(theta)


def ideal_speed(theta, R=R_SC):
    """m/s"""
    return math.sqrt(G * R * math.sin(theta)) if theta > 0 else 0.0


def lean_for(v, R):
    return math.atan2(v * v, G * R)


# ---------------------------------------------------------------- board outline (top view)
def board_outline(n=64, R=R_SC, ex=1.0):
    """board outline in metres, x along board (nose +), y across. ex exaggerates sidecut."""
    C, L, Wd = BOARD_C, BOARD_L, BOARD_W
    d = sag(R) * ex
    xs = np.linspace(-C / 2, C / 2, n)
    # circular arc through (+-C/2, W/2) and (0, W/2 - d)
    Rx = ((C / 2) ** 2 + d * d) / (2 * d)
    yc = Wd / 2 - d + Rx
    edge = yc - np.sqrt(Rx * Rx - xs * xs)
    # nose / tail caps (half-ellipses)
    cap = (L - C) / 2
    th = np.linspace(-math.pi / 2, math.pi / 2, 24)
    nose = np.stack([C / 2 + cap * np.cos(th), Wd / 2 * np.sin(th)], 1)
    tail = np.stack([-C / 2 - cap * np.cos(th), -Wd / 2 * np.sin(th)], 1)
    right = np.stack([xs, -edge], 1)          # y<0 side
    left = np.stack([xs[::-1], edge[::-1]], 1)
    return np.concatenate([right, nose, left, tail])


def sidecut_circle(R=R_SC):
    """centre (x, y) of the y>0 edge circle, in board coords."""
    d = sag(R)
    return 0.0, BOARD_W / 2 - d + R


# ---------------------------------------------------------------- 3D tilted + pressed board
def board_mesh(theta, press, nx=41, ny=7, ex=1.0):
    """Board tilted by theta onto its +y edge (toe edge on snow, z=0), bent by fraction `press`
    (0 = rigid: only nose & tail touch; 1 = whole edge on snow -> turn radius R_sc cos theta).
    Returns X,Y,Z arrays (nx, ny) in metres. Edge line is j = ny-1."""
    C = BOARD_C
    xs = np.linspace(-BOARD_L / 2, BOARD_L / 2, nx)
    xc = np.clip(xs, -C / 2, C / 2)
    d0 = sag()
    Rx = ((C / 2) ** 2 + d0 * d0) / (2 * d0)
    half_w = BOARD_W / 2 - d0 + Rx - np.sqrt(Rx * Rx - xc ** 2)       # half-width along length
    half_w = np.where(np.abs(xs) > C / 2, BOARD_W / 2 * np.sqrt(np.clip(1 - ((np.abs(xs) - C / 2) / ((BOARD_L - C) / 2)) ** 2, 0, 1)) + 0.0, half_w)
    # edge offset (inward) relative to the chord through nose/tail contact points
    s = (BOARD_W / 2) - half_w            # >= 0 inside contact length
    s = np.where(np.abs(xs) <= C / 2, s, 0)
    # bending deflection normal to plate: delta = press * s * tan(theta)
    delta = press * s * math.tan(theta) * ex
    v = np.linspace(-1, 1, ny)
    X = np.repeat(xs[:, None], ny, 1)
    Y = np.zeros_like(X); Z = np.zeros_like(X)
    ct, st = math.cos(theta), math.sin(theta)
    for j, vv in enumerate(v):
        w = half_w * vv                      # lateral position on plate (+ toward toe edge)
        dist = (BOARD_W / 2) - w             # distance from the chord line, measured on the plate
        # plate coordinates: along-u lies down from edge chord; tilt about chord (x axis at y0=W/2)
        u = dist                              # metres from chord, across the plate (e_u = (0,-cos,sin))
        # bend: whole cross-section moves by delta along plate normal n = (0, -sin, -cos);
        # for the edge (u = s) delta = s tan(theta) puts it exactly on z = 0 at y = -s/cos(theta)
        y = -u * ct - delta * st
        z = u * st - delta * ct
        # nose/tail kick
        kick = np.clip((np.abs(xs) - C / 2) / ((BOARD_L - C) / 2), 0, 1) ** 2 * 0.07
        Y[:, j] = y
        Z[:, j] = z + kick
    return X, Y, Z


def trace_circle(theta):
    """circle through the pressed edge on snow: chord on y=0, waist at y=-d/cos(theta), centre +y."""
    d2 = sag() / math.cos(theta)
    r = ((BOARD_C / 2) ** 2 + d2 * d2) / (2 * d2)
    return (0.0, r - d2), r


# ---------------------------------------------------------------- S-track (top view, metres)
def s_track(n_turns=6, th_min=math.radians(8), th_max=math.radians(55), ds=0.02, R=R_SC):
    """integrate heading with curvature 1/(R cos theta(s)); theta oscillates per turn.
    Returns (pts Nx2, heading N, theta N, s N). Downhill = +y."""
    pts, hd, ths, ss = [], [], [], []
    x = y = 0.0
    h = math.pi / 2           # pointing downhill
    s = 0.0
    # length of one turn chosen so heading swings symmetrically about the fall line
    Lt = 8.5
    total = n_turns * Lt
    while s < total:
        k = (s % Lt) / Lt
        sgn = 1 if int(s // Lt) % 2 == 0 else -1
        th = th_min + (th_max - th_min) * math.sin(math.pi * k) ** 2
        curv = sgn / turn_radius(th, R) * math.sin(math.pi * k) ** 1.2
        h += curv * ds
        x += math.cos(h) * ds
        y += math.sin(h) * ds
        s += ds
        pts.append((x, y)); hd.append(h); ths.append(th * sgn * (math.sin(math.pi * k) > 0.05)); ss.append(s)
    pts = np.array(pts)
    # re-centre the drift so the track runs straight down the fall line
    drift = np.polyfit(pts[:, 1], pts[:, 0], 1)
    pts[:, 0] -= np.polyval(drift, pts[:, 1])
    return pts, np.array(hd), np.array(ths), np.array(ss)


if __name__ == "__main__":
    print("sidecut depth", round(sag() * 100, 2), "cm  (J&F: ~2.4 cm)")
    print("waist width", round((BOARD_W - 2 * sag()) * 100, 1), "cm")
    for d in (30, 45, 60, 70):
        t = math.radians(d)
        print(d, "deg  R", round(turn_radius(t), 2), "m  v", round(ideal_speed(t) * 3.6, 1), "km/h",
              " lean check", round(math.degrees(lean_for(ideal_speed(t), turn_radius(t))), 2))
    X, Y, Z = board_mesh(math.radians(45), 1.0)
    edge = np.stack([X[:, -1], Y[:, -1], Z[:, -1]], 1)
    inside = np.abs(X[:, -1]) <= BOARD_C / 2
    e = edge[inside]
    # fit circle to (x,y) of edge: y = r - sqrt(r^2 - x^2)  -> r ~ x^2/(2y)
    yy = e[:, 1] - e[np.argmin(np.abs(e[:, 0])), 1]
    print("pressed edge z max (should be ~0):", round(np.abs(e[:, 2]).max() * 1000, 3), "mm")
    dp = -e[np.argmin(np.abs(e[:, 0])), 1]          # depth of the edge arc on snow
    r_fit = ((BOARD_C / 2) ** 2 + dp * dp) / (2 * dp)
    print("edge-on-snow radius fit", round(abs(r_fit), 2), "m  vs R cos45 =", round(turn_radius(math.radians(45)), 2))
    pts, hd, th, s = s_track()
    print("track", pts.shape, "x range", pts[:, 0].min().round(2), pts[:, 0].max().round(2), "y", pts[:, 1].max().round(1))
