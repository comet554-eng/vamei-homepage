"""Ambient score synthesised in numpy, aligned to the scene timeline.
Ideas: soft pads + glassy bells; S4 'cancellation' = a tone and its phase-drifting copy really cancel."""
import math, wave, sys
import numpy as np

SR = 44100


def durations():
    from s_top import S1_DUR, S2_DUR
    from s_cut import S3_DUR
    from s_edge import S4_DUR
    from s_body import S5_DUR, S6_DUR
    from s_end import S7_DUR, S8_DUR
    return [S1_DUR, S2_DUR, S3_DUR, S4_DUR, S5_DUR, S6_DUR, S7_DUR, S8_DUR]


D = durations()
ST = np.concatenate([[0], np.cumsum(D)])
TOTAL = float(ST[-1])
N = int(TOTAL * SR) + SR
L = np.zeros(N, np.float32)
R = np.zeros(N, np.float32)


def hz(n):  # midi -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def add(t0, sig, pan=0.0, g=1.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    L[i:i + len(sig)] += sig * g * l * 1.414
    R[i:i + len(sig)] += sig * g * r * 1.414


def env_adsr(n, a, rel):
    e = np.ones(n, np.float32)
    na, nr = int(a * SR), int(rel * SR)
    na, nr = min(na, n // 2), min(nr, n // 2)
    e[:na] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, na))
    e[n - nr:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, nr))
    return e


def pad(t0, dur, notes, g=0.05, a=2.5, rel=3.0, bright=1.0):
    n = int((dur + rel) * SR)
    t = np.arange(n, dtype=np.float32) / SR
    e = env_adsr(n, a, rel)
    for k, m in enumerate(notes):
        f = hz(m)
        for det, pan in ((-0.004, -0.5), (0.004, 0.5)):
            ph = 2 * np.pi * f * (1 + det) * t + 0.002 * np.sin(2 * np.pi * 0.2 * t + k)
            s = np.sin(ph) + 0.25 * bright * np.sin(2 * ph) + 0.08 * bright * np.sin(3 * ph)
            add(t0, (s * e).astype(np.float32), pan * 0.7, g / len(notes))


def bell(t0, m, g=0.06, dec=2.8, pan=0.0):
    n = int(dec * 2.5 * SR)
    t = np.arange(n, dtype=np.float32) / SR
    f = hz(m)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t / dec)
         + 0.35 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t / (dec * 0.5))
         + 0.12 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t / (dec * 0.3)))
    s[:200] *= np.linspace(0, 1, 200)
    add(t0, s.astype(np.float32), pan, g)


def drone(t0, dur, m, g=0.05, rel=4.0):
    n = int((dur + rel) * SR)
    t = np.arange(n, dtype=np.float32) / SR
    s = np.sin(2 * np.pi * hz(m) * t) + 0.3 * np.sin(2 * np.pi * hz(m + 12) * t)
    s *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * t)
    add(t0, (s * env_adsr(n, 4.0, rel)).astype(np.float32), 0, g)


def cancel_pair(t0, dur, m, g=0.06):
    """two identical tones; the second slides from in-phase to opposite phase -> real silence."""
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    f = hz(m)
    drift = np.pi * np.clip((t - 0.8) / (dur - 2.0), 0, 1)
    s = np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * f * t + drift)
    add(t0, (s * env_adsr(n, 0.6, 1.0) * 0.5).astype(np.float32), 0, g)


def air(t0, dur, g=0.02):
    n = int(dur * SR)
    rng = np.random.default_rng(int(t0 * 10))
    x = rng.normal(0, 1, n).astype(np.float32)
    for _ in range(3):  # crude low-pass
        x = np.convolve(x, np.ones(24) / 24, "same").astype(np.float32)
    add(t0, x * env_adsr(n, dur * 0.6, dur * 0.4), 0, g)


# ------------------------------------------------------------------ score (E major, light, gliding)
s1, s2, s3, s4, s5, s6, s7, s8 = ST[:8]
Emaj9 = [40, 52, 56, 59, 63, 66]; Amaj7 = [45, 52, 56, 61, 64]; Csm9 = [49, 56, 59, 63, 64]
Badd9 = [47, 54, 59, 61, 63]; Fsm9 = [42, 54, 57, 61, 64]; Eadd9 = [40, 52, 56, 59, 66]
motif = [71, 76, 78, 75, 73, 71]
# S1: dawn; a soft tick for each turn of the carve (one turn = 15 m / 3.6 m/s)
drone(s1, D[0] + 2, 40, 0.04)
pad(s1 + 0.4, 8, Emaj9, 0.05); pad(s1 + 7.5, 7, Amaj7, 0.05)
for k in range(4):
    bell(s1 + 1.6 + k * 15 / 3.6, motif[k], 0.035, 2.4, pan=0.4 * (-1) ** k)
pad(s1 + 14.0, D[0] - 13, Csm9, 0.055); bell(s1 + 14.4, 68, 0.05, 4.0); bell(s1 + 14.9, 75, 0.04, 4.0)
# S2: skid (gritty air) vs carve (clean bell)
pad(s2, 11, Fsm9, 0.04); air(s2 + 2.0, 7.0, 0.035)
pad(s2 + 10.5, D[1] - 10, Emaj9, 0.045)
bell(s2 + 11.8, 76, 0.045, 3.2); bell(s2 + 17.2, 78, 0.04, 3.0)
# S3: geometry, sparse and curious; swell when the full circle appears
pad(s3, 12, Amaj7, 0.04); pad(s3 + 11.4, 8, Emaj9, 0.05, bright=1.3); pad(s3 + 19, D[2] - 18, Badd9, 0.04)
for tt, mm in ((1.2, 76), (6.8, 73), (11.8, 64), (12.4, 71), (13.0, 76), (21.0, 83)):
    bell(s3 + tt, mm, 0.035, 2.6)
# S4: tilt, press, formula; rising ticks while the edge angle sweeps 30 -> 70
drone(s4, D[3], 40, 0.035)
pad(s4, 11, Csm9, 0.04); pad(s4 + 10.6, 7, Amaj7, 0.045); pad(s4 + 17, 14, Emaj9, 0.05, bright=1.2)
bell(s4 + 1.6, 71, 0.03); bell(s4 + 11.2, 76, 0.045, 3.5)
for k, tt in enumerate(np.linspace(18.2, 24.8, 9)):
    bell(s4 + tt, 64 + [0, 2, 4, 7, 9, 11, 12, 14, 16][k], 0.022, 1.4, pan=-0.6 + 0.15 * k)
bell(s4 + 24.6, 83, 0.04, 4.0)
pad(s4 + 31, 8, Badd9, 0.04); pad(s4 + 38.5, D[3] - 37, Emaj9, 0.05)
for i, tt in enumerate((39.0, 41.0, 43.0)):
    bell(s4 + tt, motif[i], 0.03, 2.4)
# S5: balance; unstable intervals while off balance, resolve on balance
pad(s5, 13, Amaj7, 0.04)
cancel_pair(s5 + 13.4, 5.8, 57, 0.035)
pad(s5 + 13.2, 6, [45, 57, 58, 64], 0.03, bright=0.6)        # rub (A + Bb) = unstable
pad(s5 + 19.4, 6, [47, 59, 60, 66], 0.03, bright=0.6)        # rub (B + C)
pad(s5 + 25.4, D[4] - 24, Emaj9, 0.05)
bell(s5 + 25.8, 76, 0.04, 3.5)
for k, tt in enumerate(np.arange(30.6, 40.0, 1.5)):
    bell(s5 + tt, [71, 73, 76, 78, 76, 73, 71][k % 7], 0.025, 1.6)
# S6: measurement, neutral
pad(s6, 15, Fsm9, 0.04); pad(s6 + 14.6, D[5] - 14, Csm9, 0.04)
bell(s6 + 7.2, 76, 0.035, 3.0); bell(s6 + 15.4, 70, 0.03, 2.4); air(s6 + 25.8, 4.0, 0.02)
# S7: return; opening motif, resolve
drone(s7, D[6], 40, 0.04)
pad(s7, 13, Amaj7, 0.045); pad(s7 + 12.6, 8, Csm9, 0.045); pad(s7 + 20, 8, Eadd9, 0.055, rel=5.0)
for i, tt in enumerate((1.2, 3.6, 6.0, 8.4, 13.4, 16.0)):
    bell(s7 + tt, motif[i], 0.033, 2.6, pan=0.3 * (-1) ** i)
bell(s7 + 20.8, 80, 0.04, 5.0)
pad(s8, D[7] - 1, [52, 59, 63, 66], 0.025, a=2.0, rel=3.0, bright=0.4)

# ------------------------------------------------------------------ reverb (overlap-add FFT)
def reverb(x, sec=3.2, wet=0.32, seed=1):
    rng = np.random.default_rng(seed)
    n = int(sec * SR)
    t = np.arange(n) / SR
    ir = rng.normal(0, 1, n) * np.exp(-t / 0.9)
    ir[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
    ir = (ir / np.sqrt((ir ** 2).sum())).astype(np.float32)
    blk = SR
    nfft = 1 << int(math.ceil(math.log2(blk + n)))
    IR = np.fft.rfft(ir, nfft)
    y = np.zeros(len(x) + n, np.float32)
    for i in range(0, len(x), blk):
        seg = x[i:i + blk]
        out = np.fft.irfft(np.fft.rfft(seg, nfft) * IR, nfft)[: len(seg) + n]
        y[i:i + len(out)] += out.astype(np.float32)
    return (1 - wet) * x + wet * 3.0 * y[: len(x)]


L2, R2 = reverb(L, seed=1), reverb(R, seed=2)
mix_ = np.stack([L2, R2], 1)[: int(TOTAL * SR)]
fade = int(1.5 * SR)
mix_[-fade:] *= np.linspace(1, 0, fade)[:, None]
rms = np.sqrt((mix_ ** 2).mean())
mix_ *= 10 ** (-21 / 20) / max(rms, 1e-9)
pk = np.abs(mix_).max()
if pk > 0.89:
    mix_ = np.tanh(mix_ / 0.89) * 0.89
out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/music.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix_, -1, 1) * 32767).astype(np.int16).tobytes())
print("total", TOTAL, "s; rms dBFS", 20 * math.log10(np.sqrt((mix_ ** 2).mean())), "peak", np.abs(mix_).max())
