"""Physics core: tabletop jump geometry, drag-free flight, equivalent fall height (EFH).

EFH = v^2 sin^2(slope - impact_angle) / (2 g)
  -- same expression as skijumpdesign 1.4.0, surfaces.py, Surface.calculate_efh()
     (Moore & Hubbard, JOSS 2018; theory: Hubbard 2009, McNeil et al. 2012, Levy et al. 2015)
Model: rider = point mass, no air drag, no snow friction in flight. Deck level with the lip (simplified).
"""
import math
import numpy as np

G = 9.81
TH = math.radians(20.0)      # takeoff angle
DECK = 6.0                   # tabletop length (m)
LAND = math.radians(30.0)    # landing slope angle
DROP = 6.0                   # landing slope height (m)
X_END = DECK + DROP / math.tan(LAND)   # bottom of landing slope (16.39 m)


def surface(x):
    """tabletop profile -> (y, slope angle rad). x measured from the lip."""
    if x <= DECK:
        return 0.0, 0.0
    if x <= X_END:
        return -(x - DECK) * math.tan(LAND), -LAND
    return -DROP, 0.0


def flight(v0, th=TH):
    """landing of a drag-free flight from the lip on the tabletop profile."""
    vx, vy = v0 * math.cos(th), v0 * math.sin(th)
    # bisection on time over each piece is overkill; fine stepping + refine
    t, dt = 1e-4, 1e-3
    while True:
        x = vx * t; y = vy * t - 0.5 * G * t * t
        if y <= surface(x)[0]:
            break
        t += dt
    a, b = t - dt, t
    for _ in range(40):
        m = 0.5 * (a + b)
        x = vx * m; y = vy * m - 0.5 * G * m * m
        if y <= surface(x)[0]:
            b = m
        else:
            a = m
    T = b
    X, Y = vx * T, vy * T - 0.5 * G * T * T
    vyl = vy - G * T
    v = math.hypot(vx, vyl)
    imp = math.atan2(vyl, vx)
    sl = surface(X)[1]
    return dict(T=T, x=X, y=Y, v=v, imp=imp, slope=sl, efh=efh(v, imp, sl), vx=vx, vy=vy)


def efh(v, imp, slope):
    return (v * math.sin(slope - imp)) ** 2 / (2 * G)


def traj_points(v0, T, n=80, th=TH):
    vx, vy = v0 * math.cos(th), v0 * math.sin(th)
    t = np.linspace(0, T, n)
    return np.stack([vx * t, vy * t - 0.5 * G * t * t], 1)


def zone(x):
    return "deck" if x <= DECK else ("slope" if x <= X_END else "flat")


# ---------------------------------------------------------------- constant-EFH landing surface
def const_efh_surface(h=0.5, x0=2.0, y0=0.0, x1=34.0, n=640, th=TH):
    """integrate dy/dx = tan(phi + asin(sqrt(2gh)/v)), where (v, phi) are the impact speed/angle of the
    one trajectory from the lip that passes through (x, y). Drag-free version of Hubbard (2009)."""
    vperp = math.sqrt(2 * G * h)

    def f(x, y):
        den = 2 * math.cos(th) ** 2 * (x * math.tan(th) - y)
        v0 = math.sqrt(G * x * x / den)
        vx = v0 * math.cos(th); vy = v0 * math.sin(th) - G * x / vx
        v = math.hypot(vx, vy); phi = math.atan2(vy, vx)
        return math.tan(phi + math.asin(min(1.0, vperp / v)))

    xs = np.linspace(x0, x1, n); ys = np.empty(n); ys[0] = y0
    for i in range(n - 1):
        x, y, d = xs[i], ys[i], xs[i + 1] - xs[i]
        k1 = f(x, y); k2 = f(x + d / 2, y + d * k1 / 2); k3 = f(x + d / 2, y + d * k2 / 2); k4 = f(x + d, y + d * k3)
        ys[i + 1] = y + d * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return xs, ys


def v0_through(x, y, th=TH):
    return math.sqrt(G * x * x / (2 * math.cos(th) ** 2 * (x * math.tan(th) - y)))


if __name__ == "__main__":
    for kmh in (25, 30, 34, 35, 36, 38, 40, 41, 45, 54):
        r = flight(kmh / 3.6)
        print(f"{kmh:3d} km/h  land {r['x']:5.1f} m  {zone(r['x']):5s}  v {r['v']:4.1f}  imp {math.degrees(r['imp']):6.1f}  EFH {r['efh']:.2f}")
    sp = np.linspace(20, 60, 801) / 3.6
    zs = [zone(flight(v)['x']) for v in sp]
    sl = [v * 3.6 for v, z in zip(sp, zs) if z == "slope"]
    print("slope window km/h", min(sl), max(sl))
    e = [flight(v)['efh'] for v in sp]
    i = int(np.argmax([z == 'flat' for z in zs])); print("jump at", sp[i - 1] * 3.6, e[i - 1], "->", sp[i] * 3.6, e[i])
    xs, ys = const_efh_surface()
    for x in (2, 5, 10, 15, 20, 25, 30, 34):
        j = np.argmin(abs(xs - x)); print(f"const-EFH x {xs[j]:.1f} y {ys[j]:.2f} v0 {v0_through(xs[j], ys[j]) * 3.6:.1f} km/h")
    # check: fly to that surface and recompute EFH
    for x in (6, 15, 28):
        j = np.argmin(abs(xs - x)); v0 = v0_through(xs[j], ys[j])
        vx = v0 * math.cos(TH); vy = v0 * math.sin(TH) - G * xs[j] / vx
        s = math.atan((ys[j + 1] - ys[j - 1]) / (xs[j + 1] - xs[j - 1]))
        print("check efh", round(efh(math.hypot(vx, vy), math.atan2(vy, vx), s), 3))
