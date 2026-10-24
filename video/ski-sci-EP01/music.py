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
Emaj9 = [40, 52, 56, 59, 63, 66]; Amaj7 = [45, 52, 56, 61, 64]; Csm9 = [49, 56, 59, 63, 64]
Badd9 = [47, 54, 59, 61, 63]; Fsm9 = [42, 54, 57, 61, 64]
# S1 gliding: soft air + motif
drone(s1, D[0] + 2, 40, 0.035); swoosh(s1 + 0.5, D[0] - 1, 0.012)
pad(s1 + 0.3, 9, Emaj9, 0.045); pad(s1 + 8.8, D[0] - 8, Amaj7, 0.05)
for i, tt in enumerate((1.0, 4.4, 9.5)):
    bell(s1 + tt, [71, 76, 70][i], 0.035, 2.6)
bell(s1 + 12.8, 76, 0.05, 4.0); bell(s1 + 13.3, 83, 0.04, 4.0)
# S2 calculation: sparse ticks, a falling figure at the tiny numbers
pad(s2, 11, Amaj7, 0.04); pad(s2 + 10.5, 11, Csm9, 0.04); pad(s2 + 21, 10, Fsm9, 0.04, bright=0.7); pad(s2 + 30.5, D[1] - 29, Emaj9, 0.045)
for tt, mm in ((0.8, 76), (5.0, 78), (11.0, 73), (17.0, 64), (22.2, 88), (26.2, 71), (32.2, 59), (38.6, 76)):
    bell(s2 + tt, mm, 0.03, 2.4)
for k, tt in enumerate(np.linspace(22.4, 24.0, 5)):
    bell(s2 + tt, 88 + [0, 2, 4, 7, 9][k], 0.012, 0.8)
# S3 heat: warm swell, steady pulse of contacts
drone(s3, D[2], 40, 0.03)
pad(s3, 6, Csm9, 0.04); pad(s3 + 5, 12, Amaj7, 0.045, bright=1.3); pad(s3 + 16.5, 14, Emaj9, 0.045); pad(s3 + 30, D[2] - 29, Badd9, 0.04)
for k, tt in enumerate(np.arange(5.5, 44, 1.6)):
    bell(s3 + tt, [64, 68, 71, 68][k % 4], 0.012, 1.0, pan=0.5 * (-1) ** k)
bell(s3 + 17.4, 78, 0.035, 3.0); bell(s3 + 24.2, 83, 0.03, 3.0)
# S4 colder: cooler chords
pad(s4, 12, Fsm9, 0.04); pad(s4 + 11.5, D[3] - 10, Csm9, 0.04)
bell(s4 + 5.6, 76, 0.03); bell(s4 + 6.8, 81, 0.035); bell(s4 + 12.2, 69, 0.03); bell(s4 + 12.8, 76, 0.035)
# S5 open question: rub, then unresolved add9
drone(s5, D[4], 40, 0.03)
pad(s5, 9, Csm9, 0.04); pad(s5 + 9.4, 7, [45, 57, 58, 64], 0.03, bright=0.6); pad(s5 + 16.6, 13, Amaj7, 0.04)
pad(s5 + 29, D[4] - 27, Badd9, 0.045)
bell(s5 + 3.5, 76, 0.03); bell(s5 + 10.0, 70, 0.03); bell(s5 + 17.2, 81, 0.03); bell(s5 + 29.6, 83, 0.035, 4.0)
# S6 return
drone(s6, D[5], 40, 0.035); swoosh(s6 + 0.5, D[5] - 2, 0.012)
pad(s6, 11, Amaj7, 0.045); pad(s6 + 10.5, D[5] - 9, Emaj9, 0.05, rel=5.0)
for i, tt in enumerate((1.0, 5.2, 11.0)):
    bell(s6 + tt, [71, 76, 78][i], 0.035, 2.6)
bell(s6 + 18.0, 88, 0.04, 5.0)


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
