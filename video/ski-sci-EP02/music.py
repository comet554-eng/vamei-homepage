"""Score synthesised in numpy, aligned to scene timeline and to the computed landings.
Soft landing on a slope = clean bell; landing on the flat = low thud. python3 music.py out.wav"""
import math, wave, sys
import numpy as np
import scenes as S
import jump as J
from view import fl

SR = 44100
D = [d for _, _, d in S.SCENES]
ST = np.concatenate([[0], np.cumsum(D)])
TOTAL = float(ST[-1])
N = int(TOTAL * SR) + SR
L = np.zeros(N, np.float32); R = np.zeros(N, np.float32)


def hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def add(t0, sig, pan=0.0, g=1.0):
    i = int(t0 * SR)
    if i >= N or i < 0:
        return
    sig = sig[: N - i]
    l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    L[i:i + len(sig)] += sig * g * l * 1.414
    R[i:i + len(sig)] += sig * g * r * 1.414


def env(n, a, rel):
    e = np.ones(n, np.float32)
    na, nr = min(int(a * SR), n // 2), min(int(rel * SR), n // 2)
    e[:na] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, na))
    e[n - nr:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, nr))
    return e


def pad(t0, dur, notes, g=0.05, a=2.5, rel=3.0, bright=1.0):
    n = int((dur + rel) * SR); t = np.arange(n, dtype=np.float32) / SR; e = env(n, a, rel)
    for k, m in enumerate(notes):
        f = hz(m)
        for det, pan in ((-0.004, -0.5), (0.004, 0.5)):
            ph = 2 * np.pi * f * (1 + det) * t + 0.002 * np.sin(2 * np.pi * 0.2 * t + k)
            s = np.sin(ph) + 0.25 * bright * np.sin(2 * ph) + 0.08 * bright * np.sin(3 * ph)
            add(t0, (s * e).astype(np.float32), pan * 0.7, g / len(notes))


def bell(t0, m, g=0.05, dec=2.6, pan=0.0):
    n = int(dec * 2.5 * SR); t = np.arange(n, dtype=np.float32) / SR; f = hz(m)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t / dec) + 0.35 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / (dec * 0.5))
         + 0.12 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t / (dec * 0.3)))
    s[:200] *= np.linspace(0, 1, 200)
    add(t0, s.astype(np.float32), pan, g)


def thud(t0, g=0.22):
    n = int(1.2 * SR); t = np.arange(n, dtype=np.float32) / SR
    f = 55 * np.exp(-t * 3) + 38
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    rng = np.random.default_rng(int(t0 * 100))
    nz = rng.normal(0, 1, n).astype(np.float32) * np.exp(-t * 30)
    nz = np.convolve(nz, np.ones(30) / 30, "same")
    add(t0, (s + 0.6 * nz).astype(np.float32), 0, g)


def swoosh(t0, dur, g=0.02):
    n = int(dur * SR); rng = np.random.default_rng(int(t0 * 37))
    x = rng.normal(0, 1, n).astype(np.float32)
    for _ in range(2):
        x = np.convolve(x, np.ones(12) / 12, "same").astype(np.float32)
    add(t0, x * env(n, dur * 0.5, dur * 0.5), 0.3, g)


def drone(t0, dur, m, g=0.04, rel=4.0):
    n = int((dur + rel) * SR); t = np.arange(n, dtype=np.float32) / SR
    s = np.sin(2 * np.pi * hz(m) * t) + 0.3 * np.sin(2 * np.pi * hz(m + 12) * t)
    s *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * t)
    add(t0, (s * env(n, 4.0, rel)).astype(np.float32), 0, g)


def landing(t_land, efh, pitch=76):
    if efh > 2:
        thud(t_land)
    else:
        bell(t_land, pitch, 0.045, 2.4)


def jump_sound(t_scene0, lt0, v0, slow=0.75, approach=0.8, pitch=76, res=None):
    r = res or fl(v0)
    tk = t_scene0 + lt0 + approach
    swoosh(tk - 0.4, r["T"] / slow + 0.4, 0.018)
    landing(tk + r["T"] / slow, r["efh"], pitch)


s1, s2, s3, s4, s5, s6 = ST[:6]
Dmaj9 = [38, 50, 54, 57, 61, 64]; Gmaj7 = [43, 50, 54, 59, 62]; Bm9 = [47, 54, 57, 61, 62]
Asus = [45, 52, 57, 59, 64]; Em9 = [40, 52, 55, 59, 62]; Fsm = [42, 54, 57, 61]
# S1
drone(s1, D[0] + 2, 38, 0.035)
pad(s1 + 0.3, 9, Bm9, 0.045); pad(s1 + 9, D[0] - 8, Gmaj7, 0.05)
thud(s1 + 1.6 + (0.55 + math.sqrt(2 * 1.5 / J.G)) / 0.5)
jump_sound(s1, 5.0, 10.0, slow=0.7, pitch=78)
bell(s1 + 12.0, 74, 0.05, 4.0); bell(s1 + 12.5, 81, 0.04, 4.0)
# S2
pad(s2, 16, Dmaj9, 0.042); pad(s2 + 15.5, 11, Em9, 0.042); pad(s2 + 26, 8, Asus, 0.045); pad(s2 + 33.5, D[1] - 32, Dmaj9, 0.05, bright=1.2)
bell(s2 + 1.0, 74, 0.03); bell(s2 + 5.4, 78, 0.03); bell(s2 + 16.6, 81, 0.035)
thud(s2 + 22.4, 0.12)
for k, tt in enumerate(np.linspace(27.6, 32.8, 7)):
    bell(s2 + tt, [69, 71, 73, 74, 76, 78, 81][k], 0.02, 1.4, pan=-0.6 + 0.2 * k)
bell(s2 + 34.2, 86, 0.04, 4.0)
# S3
drone(s3, D[2], 38, 0.03)
pad(s3, 11, Gmaj7, 0.04); pad(s3 + 10.5, 12, Dmaj9, 0.04); pad(s3 + 22, 12, Bm9, 0.04); pad(s3 + 33.5, D[2] - 32, Fsm, 0.04, bright=0.6)
for tt, mm in ((0.8, 74), (5.0, 78), (5.6, 79), (6.2, 81), (6.8, 83), (7.4, 81), (8.0, 78)):
    bell(s3 + tt, mm, 0.022, 1.6)
for (t0, kmh), p in zip(S.SEG3, (74, 78, 76, 74, 50)):
    jump_sound(s3, t0 + 0.3, kmh / 3.6, pitch=p)
# S4
pad(s4, 11, Dmaj9, 0.04); pad(s4 + 10.5, 6.5, Asus, 0.04); pad(s4 + 16.5, 6.5, [42, 54, 55, 61], 0.03, bright=0.6)
pad(s4 + 22.6, D[3] - 21, Em9, 0.042)
bell(s4 + 5.2, 74, 0.03); bell(s4 + 10.8, 78, 0.035); thud(s4 + 18.6, 0.1); bell(s4 + 23.0, 76, 0.03)
# S5
drone(s5, D[4], 38, 0.03)
pad(s5, 6, Bm9, 0.04); pad(s5 + 5.5, 7, Gmaj7, 0.045); pad(s5 + 12, 8, Dmaj9, 0.05, bright=1.2); pad(s5 + 19.5, D[4] - 18, Dmaj9, 0.045)
for i, kmh in enumerate(S.SP5):
    r = S.land_const(kmh / 3.6)
    jump_sound(s5, 11.9 + i * 1.05, kmh / 3.6, slow=0.9, approach=0.6, pitch=[74, 76, 78, 81, 83, 86, 88][i], res=r)
bell(s5 + 27.0, 81, 0.04, 4.0)
# S6
pad(s6, 11, Gmaj7, 0.045); pad(s6 + 10.5, 7, Asus, 0.045); pad(s6 + 17, D[5] - 16, Dmaj9, 0.05, rel=5.0)
for k in range(3):
    lt0 = 0.4 + k * 7.6
    if lt0 < 15.6:
        jump_sound(s6, lt0, 37 / 3.6, pitch=78)
jump_sound(s6, 15.6, 37 / 3.6, pitch=81)
bell(s6 + 20.2, 86, 0.04, 5.0)


def reverb(x, sec=3.0, wet=0.3, seed=1):
    rng = np.random.default_rng(seed); n = int(sec * SR); t = np.arange(n) / SR
    ir = rng.normal(0, 1, n) * np.exp(-t / 0.85); ir[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
    ir = (ir / np.sqrt((ir ** 2).sum())).astype(np.float32)
    blk = SR; nfft = 1 << int(math.ceil(math.log2(blk + n))); IR = np.fft.rfft(ir, nfft)
    y = np.zeros(len(x) + n, np.float32)
    for i in range(0, len(x), blk):
        seg = x[i:i + blk]; out = np.fft.irfft(np.fft.rfft(seg, nfft) * IR, nfft)[: len(seg) + n]
        y[i:i + len(out)] += out.astype(np.float32)
    return (1 - wet) * x + wet * 3.0 * y[: len(x)]


L2, R2 = reverb(L, seed=1), reverb(R, seed=2)
mix_ = np.stack([L2, R2], 1)[: int(TOTAL * SR)]
fade = int(2.0 * SR); mix_[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix_ *= 10 ** (-21 / 20) / max(np.sqrt((mix_ ** 2).mean()), 1e-9)
if np.abs(mix_).max() > 0.89:
    mix_ = np.tanh(mix_ / 0.89) * 0.89
out = sys.argv[1] if len(sys.argv) > 1 else "out/music.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix_, -1, 1) * 32767).astype(np.int16).tobytes())
print("total", TOTAL, "s; rms dBFS", 20 * math.log10(np.sqrt((mix_ ** 2).mean())), "peak", np.abs(mix_).max())
