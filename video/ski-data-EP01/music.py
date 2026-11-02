"""Score synthesised in numpy, aligned to scene timeline and to the computed landings.
python3 music.py out.wav"""
import math, wave, sys
import numpy as np
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


s1, s2, s3, s4, s5, s6 = ST[:6]
Dm9 = [38, 50, 53, 57, 60, 64]; Bbmaj7 = [46, 53, 57, 62, 65]; Gm9 = [43, 50, 53, 58, 62]
Fadd9 = [41, 53, 57, 60, 67]; Am7 = [45, 52, 55, 60, 64]; Cadd9 = [48, 55, 60, 62, 64]
# S1 data: two lines diverge
drone(s1, D[0] + 2, 38, 0.035)
pad(s1 + 0.3, 6, Dm9, 0.04); pad(s1 + 5.8, 6, Fadd9, 0.04); pad(s1 + 11.4, 12, Gm9, 0.04, bright=0.7); pad(s1 + 23.5, D[0] - 22, Bbmaj7, 0.05)
for k, tt in enumerate(np.linspace(6.2, 8.4, 5)):
    bell(s1 + tt, [81, 79, 77, 76, 74][k], 0.018, 1.2)
for k, tt in enumerate(np.linspace(12.0, 14.8, 6)):
    bell(s1 + tt, [62, 65, 69, 72, 74, 77][k], 0.02, 1.2)
bell(s1 + 24.2, 74, 0.05, 4.0); bell(s1 + 24.7, 81, 0.04, 4.0)
# S2 dots
pad(s2, 12, Am7, 0.04); pad(s2 + 11.5, 12, Dm9, 0.04, bright=0.7); pad(s2 + 23, D[1] - 22, Fadd9, 0.045)
bell(s2 + 1.2, 76, 0.03); bell(s2 + 12.1, 62, 0.04, 3.0); bell(s2 + 17.2, 69, 0.03)
for k, tt in enumerate(np.arange(6.4, 10.2, 0.25)):
    bell(s2 + tt, 86 + (k % 3) * 2, 0.008, 0.5, pan=-0.6 + 0.08 * k)
# S3 mechanisms
drone(s3, D[2], 38, 0.03)
pad(s3, 12, Gm9, 0.04); pad(s3 + 12, 9, Dm9, 0.04); pad(s3 + 20.8, 13, [43, 55, 56, 62], 0.03, bright=0.6)
pad(s3 + 33.6, 8, Bbmaj7, 0.04); pad(s3 + 41.5, 8.5, [46, 58, 59, 65], 0.03, bright=0.6); pad(s3 + 49.8, D[2] - 48, Fadd9, 0.045)
swoosh(s3 + 16.2, 4.6, 0.02); thud(s3 + 21.0, 0.1); thud(s3 + 38.0, 0.08); thud(s3 + 45.0, 0.08)
bell(s3 + 8.0, 74, 0.03); bell(s3 + 50.4, 77, 0.03); bell(s3 + 50.8, 81, 0.03); bell(s3 + 51.2, 84, 0.03)
# S4 phantom foot
drone(s4, D[3], 38, 0.03)
pad(s4, 10, Dm9, 0.04); pad(s4 + 10, 14, [38, 50, 51, 57], 0.03, bright=0.6); pad(s4 + 24, D[3] - 22, Gm9, 0.04)
thud(s4 + 11.4, 0.08)
for i, tt in enumerate((17.6, 19.4, 21.2, 24.6, 26.6, 28.6)):
    bell(s4 + tt, [69, 72, 76, 74, 72, 69][i], 0.025, 1.6)
# S5 prevention: resolves to major
pad(s5, 12, Bbmaj7, 0.045); pad(s5 + 11.5, 15, Fadd9, 0.05, bright=1.2); pad(s5 + 26, D[4] - 25, Cadd9, 0.045)
bell(s5 + 6.4, 77, 0.035, 3.0); bell(s5 + 7.6, 84, 0.035, 3.0)
for i in range(4):
    bell(s5 + 12.0 + i * 1.2, [72, 74, 77, 81][i], 0.025, 2.0)
# S6
drone(s6, D[5], 41, 0.035); swoosh(s6 + 0.5, D[5] - 2, 0.012)
pad(s6, D[5] - 1, Fadd9, 0.05, rel=5.0)
bell(s6 + 1.0, 77, 0.035); bell(s6 + 12.0, 84, 0.04, 5.0)


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
