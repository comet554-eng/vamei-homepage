"""Physics core for the film: thin-film / multilayer reflectance, ridge diffraction, spectrum->sRGB.

Every colour shown in the optical animations is computed here rather than hand-picked.
Model parameters (simplified, see README in the plan):
  cuticle (chitin) n = 1.56            Vukusic et al. 1999
  lamella thickness  d_c = 70 nm, air gap d_a = 115 nm -> quarter-wave-ish stack, peak ~450 nm
  ethanol n = 1.36 (fills air gaps in the alcohol experiment)
"""
import numpy as np

N_CHITIN = 1.56
N_AIR = 1.0
N_ETHANOL = 1.36
D_C = 70e-9
D_A = 115e-9

WL = np.linspace(380e-9, 780e-9, 201)  # wavelength grid


# ---------------------------------------------------------------- colour science
def _g(x, mu, s1, s2):
    s = np.where(x < mu, s1, s2)
    return np.exp(-0.5 * ((x - mu) / s) ** 2)


def cie_xyz_bar(wl_nm):
    """CIE 1931 2-deg CMFs, multi-lobe Gaussian fit (Wyman, Sloan & Shirley 2013)."""
    x = (1.056 * _g(wl_nm, 599.8, 37.9, 31.0) + 0.362 * _g(wl_nm, 442.0, 16.0, 26.7)
         - 0.065 * _g(wl_nm, 501.1, 20.4, 26.2))
    y = 0.821 * _g(wl_nm, 568.8, 46.9, 40.5) + 0.286 * _g(wl_nm, 530.9, 16.3, 31.1)
    z = 1.217 * _g(wl_nm, 437.0, 11.8, 36.0) + 0.681 * _g(wl_nm, 459.0, 26.0, 13.8)
    return np.stack([x, y, z], -1)


def d65_approx(wl_nm):
    # smooth daylight-like illuminant (6500 K blackbody shape); good enough for relative colour
    wl = wl_nm * 1e-9
    h, c, k, T = 6.626e-34, 3e8, 1.381e-23, 6500.0
    b = 1.0 / (wl ** 5 * (np.exp(h * c / (wl * k * T)) - 1))
    return b / b.max()


_CMF = cie_xyz_bar(WL * 1e9)
_ILL = d65_approx(WL * 1e9)
_WHITE_Y = (_CMF[:, 1] * _ILL).sum()
_M = np.array([[3.2406, -1.5372, -0.4986],
               [-0.9689, 1.8758, 0.0415],
               [0.0557, -0.2040, 1.0570]])


def spectrum_to_linear_rgb(R):
    """R: (..., len(WL)) reflectance spectrum -> linear sRGB under daylight (white = 1)."""
    xyz = (R * _ILL) @ _CMF / _WHITE_Y
    rgb = xyz @ _M.T
    # white-balance so that R==1 gives (1,1,1)
    wb = (np.ones_like(WL) * _ILL) @ _CMF / _WHITE_Y @ _M.T
    return rgb / wb


def encode(rgb_lin, exposure=1.0):
    """linear -> display sRGB 0..1, with soft gamut handling (desaturate toward luminance)."""
    c = np.asarray(rgb_lin, float) * exposure
    lum = c @ np.array([0.2126, 0.7152, 0.0722])
    lum = np.maximum(lum, 0)[..., None]
    neg = np.minimum(c.min(-1, keepdims=True), 0)
    t = np.where(neg < 0, lum / np.maximum(lum - neg, 1e-9), 1.0)
    c = lum + (c - lum) * t
    c = np.clip(c, 0, None)
    c = c / (1 + 0.15 * c)  # gentle highlight roll-off
    c = np.clip(c * 1.15, 0, 1)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def wavelength_rgb(wl_nm):
    """display colour of a monochromatic line (for drawing rays)."""
    xyz = cie_xyz_bar(np.atleast_1d(np.asarray(wl_nm, float)))
    rgb = xyz @ _M.T
    rgb = rgb - np.minimum(rgb.min(-1, keepdims=True), 0)      # desaturate out-of-gamut
    rgb = rgb / np.maximum(rgb.max(-1, keepdims=True), 1e-9)
    rgb = 0.82 * rgb + 0.18                                     # lift for legibility on dark bg
    out = np.where(rgb <= 0.0031308, 12.92 * rgb, 1.055 * np.power(rgb, 1 / 2.4) - 0.055)
    return out[0] if np.ndim(wl_nm) == 0 else out


# ---------------------------------------------------------------- multilayer (transfer matrix)
def multilayer_r(n_layers, d_layers, wl=WL, n_in=1.0, n_sub=1.0, theta0=0.0):
    """Complex amplitude reflection (s-pol) of a stack. Returns r(wl)."""
    wl = np.asarray(wl)
    kx = n_in * np.sin(theta0)
    cos_in = np.sqrt(1 - (kx / n_in) ** 2 + 0j)
    eta_in = n_in * cos_in
    M11 = np.ones_like(wl, complex); M12 = np.zeros_like(wl, complex)
    M21 = np.zeros_like(wl, complex); M22 = np.ones_like(wl, complex)
    for n, d in zip(n_layers, d_layers):
        cos_t = np.sqrt(1 - (kx / n) ** 2 + 0j)
        eta = n * cos_t
        delta = 2 * np.pi * n * d * cos_t / wl
        a11 = np.cos(delta); a12 = 1j * np.sin(delta) / eta
        a21 = 1j * eta * np.sin(delta); a22 = np.cos(delta)
        M11, M12, M21, M22 = (M11 * a11 + M12 * a21, M11 * a12 + M12 * a22,
                              M21 * a11 + M22 * a21, M21 * a12 + M22 * a22)
    eta_s = n_sub * np.sqrt(1 - (kx / n_sub) ** 2 + 0j)
    B = M11 + M12 * eta_s
    C = M21 + M22 * eta_s
    return (eta_in * B - C) / (eta_in * B + C)


K_CHITIN = 0.06  # Vukusic et al. 1999: n = 1.56 + 0.06i


def morpho_stack(N, gap_n=N_AIR, theta0=0.0, wl=WL, k=K_CHITIN):
    nc = N_CHITIN - 1j * k  # Macleod convention N = n - ik
    layers, ds = [], []
    for i in range(N):
        layers.append(nc); ds.append(D_C)
        if i < N - 1:
            layers.append(gap_n); ds.append(D_A)
    return multilayer_r(layers, ds, wl, n_in=gap_n if gap_n != N_AIR else 1.0,
                        n_sub=gap_n, theta0=theta0)


def morpho_R(N, gap_n=N_AIR, theta0=0.0, wl=WL, k=K_CHITIN):
    return np.abs(morpho_stack(N, gap_n, theta0, wl, k)) ** 2


def with_base(Rs, base_R):
    """incoherent combination of stack (R, T=1-R lossless) above a diffuse base."""
    Ts = 1 - Rs - 0.0  # absorption in the thin stack is small; treat as lossless for the base pass
    return Rs + Ts * Ts * base_R / (1 - Rs * base_R)


# ---------------------------------------------------------------- ridge array diffraction (Kinoshita-style model)
def ridge_far_field(angles, wl=WL, n_ridges=40, pitch=0.75e-6, width=0.35e-6,
                    height_jitter=0.0, n_real=1, N_layers=8, seed=1):
    """Normal incidence. Each ridge = narrow multilayer reflector of given width.
    Intensity I(theta, wl) = |sum_j rho(wl) * sinc(width) * exp(i k (x_j sin th + z_j (1+cos th)))|^2.
    height_jitter: std dev of random ridge-height offsets (m). Returns (n_angles, n_wl), normalised."""
    rng = np.random.default_rng(seed)
    k = 2 * np.pi / wl[None, :]
    th = angles[:, None]
    rho = morpho_stack(N_layers, wl=wl)[None, :]
    u = k * width * np.sin(th) / 2
    env = np.sinc(u / np.pi) * width
    obliq = (1 + np.cos(th)) / 2
    I = np.zeros((len(angles), len(wl)))
    x = (np.arange(n_ridges) - n_ridges / 2) * pitch
    for r in range(n_real):
        z = rng.normal(0, height_jitter, n_ridges) if height_jitter > 0 else np.zeros(n_ridges)
        ph = np.exp(1j * k[None] * (x[:, None, None] * np.sin(th)[None] + z[:, None, None] * (1 + np.cos(th))[None]))
        A = ph.sum(0) * rho * env * obliq
        I += np.abs(A) ** 2
    I /= n_real
    return I / I.max()


if __name__ == "__main__":
    wl_nm = WL * 1e9
    for N in (1, 2, 4, 6, 8, 10):
        R = morpho_R(N)
        print(f"N={N:2d} peak {wl_nm[R.argmax()]:.0f} nm  Rmax={R.max():.2f}  rgb={np.round(encode(spectrum_to_linear_rgb(R)),2)}")
    R = morpho_R(8, gap_n=N_ETHANOL)
    print(f"ethanol peak {wl_nm[R.argmax()]:.0f} nm Rmax={R.max():.2f} rgb={np.round(encode(spectrum_to_linear_rgb(R)),2)}")
    for a in (0, 20, 40, 60):
        R = morpho_R(8, theta0=np.radians(a))
        print(f"flat film {a:2d} deg peak {wl_nm[R.argmax()]:.0f} nm Rmax={R.max():.2f}")
    Rs = morpho_R(6)
    for b in (0.04, 0.9):
        Rt = with_base(Rs, b)
        print("base", b, np.round(encode(spectrum_to_linear_rgb(Rt)), 2))
    print("white", encode(spectrum_to_linear_rgb(np.ones_like(WL))))
    ang = np.radians(np.linspace(-80, 80, 81))
    for j in (0, 110e-9):
        I = ridge_far_field(ang, height_jitter=j, n_real=6 if j else 1)
        tot = I.sum(1); print("jitter", j, "angular profile", np.round(tot / tot.max(), 2)[::8])
