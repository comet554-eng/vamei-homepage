"""Auto score: per scene a slow chord progression, soft bells at each subtitle, optional scene.ACCENTS.
python3 music.py EPDIR out.wav"""
import math, wave, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.abspath(sys.argv[1]))
import scenes as S


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



PROG = [[38, 50, 53, 57, 60, 64], [46, 53, 57, 62, 65], [43, 50, 53, 58, 62], [41, 53, 57, 60, 67], [45, 52, 55, 60, 64], [48, 55, 60, 62, 64]]
BELLS = [74, 77, 81, 79, 76, 72, 69, 84]
k = 0
for si, (name, fn, dur) in enumerate(S.SCENES):
    t0 = ST[si]
    drone(t0, dur, 38 if si % 2 == 0 else 41, 0.03)
    n = max(1, int(dur // 9))
    for j in range(n):
        pad(t0 + j * dur / n, dur / n + 0.6, PROG[(k + j) % len(PROG)], 0.042)
    k += n
    subs = getattr(S, name.upper() + "_SUBS", [])
    for i, (_, a, b) in enumerate(subs):
        bell(t0 + a + 0.05, BELLS[(si * 3 + i) % len(BELLS)], 0.022, 2.2, pan=0.4 * (-1) ** i)
for (t, kind) in getattr(S, "ACCENTS", []):
    {"thud": lambda x: thud(x, 0.09), "swoosh": lambda x: swoosh(x, 1.2, 0.02), "bell": lambda x: bell(x, 81, 0.04, 3.0)}[kind](t)


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
