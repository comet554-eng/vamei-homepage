"""明快版背景音乐（替换原来偏暗的氛围铺底）：大调、四拍鼓点、贝斯、拨弦琶音，段落切换处加上扬音效和重拍。
python3 music_up.py OUT.wav DURATION [--style pop|drive] [--hits t1,t2,...] [--level -20]
  pop   = 轻快流行（118 BPM，C 大调 I–V–vi–IV）
  drive = 动感电子（128 BPM，D 大调，更重的鼓和锯齿和弦）
  hits  = 段落切换时刻（秒）：之前 2 拍上扬，切换点一个重拍
全部本地合成，没有版权问题。"""
import sys, math, wave, argparse
import numpy as np

SR = 44100
ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("dur", type=float)
ap.add_argument("--style", default="pop"); ap.add_argument("--hits", default="")
ap.add_argument("--level", type=float, default=-20.0)
A = ap.parse_args()
ST = dict(pop=dict(bpm=118, root=60, prog=[(0, "M"), (7, "M"), (9, "m"), (5, "M")], saw=0.25, kick=0.9),
          drive=dict(bpm=128, root=62, prog=[(0, "M"), (9, "m"), (5, "M"), (7, "M")], saw=0.7, kick=1.1))[A.style]
BPM = ST["bpm"]; BEAT = 60 / BPM; BAR = 4 * BEAT
N = int((A.dur + 1) * SR)
L = np.zeros(N, np.float32); R = np.zeros(N, np.float32)
rng = np.random.default_rng(3)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(t0, s, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or i < 0:
        return
    s = s[: N - i]
    L[i:i + len(s)] += s * g * math.cos((pan + 1) * math.pi / 4) * 1.414
    R[i:i + len(s)] += s * g * math.sin((pan + 1) * math.pi / 4) * 1.414


def tt(d):
    return np.arange(int(d * SR), dtype=np.float32) / SR


def kick(t0, g):
    t = tt(0.32); f = 45 + 110 * np.exp(-t * 28)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    s[:60] += np.linspace(0.6, 0, 60)                     # 一点点“咔”的起音
    add(t0, s, g)


def noise(d):
    return rng.normal(0, 1, int(d * SR)).astype(np.float32)


def hp(x):
    return np.diff(x, prepend=0).astype(np.float32)


def clap(t0, g):
    t = tt(0.22); x = hp(noise(0.22))
    e = np.exp(-t * 22) + 0.5 * np.exp(-np.maximum(t - 0.012, 0) * 30) * (t > 0.012)
    add(t0, x * e * 0.5, g, 0.1)


def hat(t0, g, open_=False):
    d = 0.18 if open_ else 0.05; t = tt(d); x = hp(hp(noise(d)))
    add(t0, x * np.exp(-t * (14 if open_ else 70)) * 0.35, g, -0.25)


def tone(f, d, kind="sine", dec=None, att=0.004):
    t = tt(d); ph = 2 * np.pi * f * t
    if kind == "saw":       # 加法合成的柔和锯齿
        s = sum(np.sin(k * ph) / k for k in range(1, 9))
    elif kind == "tri":
        s = sum(((-1) ** ((k - 1) // 2)) * np.sin(k * ph) / k ** 2 for k in range(1, 8, 2))
    else:
        s = np.sin(ph)
    e = np.ones_like(t)
    na = max(1, int(att * SR)); e[:na] = np.linspace(0, 1, na)
    if dec:
        e *= np.exp(-t / dec)
    nr = min(len(t) // 3, int(0.02 * SR)); e[-nr:] *= np.linspace(1, 0, nr)
    return (s * e).astype(np.float32)


def chord_notes(root, q):
    return [root, root + (4 if q == "M" else 3), root + 7]


def riser(t_end, d, g):
    t = tt(d); x = hp(noise(d))
    sweep = np.sin(2 * np.pi * np.cumsum(300 + 2500 * (t / d) ** 2) / SR)
    add(t_end - d, (x * 0.4 + sweep * 0.25) * (t / d) ** 2, g)


def impact(t0, g):
    t = tt(1.2); f = 40 + 60 * np.exp(-t * 6)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) + hp(noise(1.2)) * np.exp(-t * 8) * 0.4
    add(t0, s, g)
    for m in (0, 4, 7, 12):                                 # 一记明亮的和弦
        add(t0, tone(hz(ST["root"] + 12 + m), 1.4, "saw", dec=0.5), g * 0.05)


# ------------------------------------------------------------------ 编曲
hits = [float(x) for x in A.hits.split(",") if x.strip()]
nbars = int(A.dur / BAR) + 1
duck = np.ones(N, np.float32)                               # 跟着底鼓的“抽吸”感
for b in range(nbars):
    t_bar = b * BAR
    root_off, q = ST["prog"][b % 4]
    root = ST["root"] + root_off
    intro = b < 2
    for k in range(4):
        tb = t_bar + k * BEAT
        if not intro:
            kick(tb, ST["kick"])
            i0 = int(tb * SR); n = int(0.22 * SR)
            if i0 < N:
                duck[i0:i0 + n] = np.minimum(duck[i0:i0 + n], (0.35 + 0.65 * np.linspace(0, 1, n) ** 0.7)[: N - i0])
        if k in (1, 3) and not intro:
            clap(tb, 0.8)
        hat(tb + BEAT / 2, 0.8 if not intro else 0.5, open_=(k == 3 and b % 2 == 1))
        hat(tb, 0.35)
    # 贝斯：八分音符
    bnotes = [root - 24, root - 24, root - 12, root - 24]
    for e8 in range(8):
        add(t_bar + e8 * BEAT / 2, tone(hz(bnotes[e8 % 4]), BEAT / 2 * 0.9, "saw" if A.style == "drive" else "tri", dec=0.35), 0.22 if not intro else 0.0)
    # 和弦铺底（随底鼓抽吸）
    cn = chord_notes(root, q)
    for m in cn + [cn[0] + 12]:
        for det in (-0.003, 0.003):
            s = tone(hz(m) * (1 + det), BAR, "saw", dec=None, att=0.05) * ST["saw"]
            add(t_bar, s, 0.018, det * 150)
    # 拨弦琶音：十六分音符
    arp = [cn[0] + 12, cn[1] + 12, cn[2] + 12, cn[1] + 12, cn[0] + 24, cn[2] + 12, cn[1] + 12, cn[2] + 12]
    for s16 in range(16):
        if intro and s16 % 2:
            continue
        m = arp[s16 % 8]
        p = tone(hz(m), 0.25, "tri", dec=0.09)
        add(t_bar + s16 * BEAT / 4, p, 0.07, 0.35 * (1 if s16 % 2 else -1))
        add(t_bar + s16 * BEAT / 4 + 3 * BEAT / 4, p, 0.025, -0.5)        # 延迟回声
    # 每 4 小节一个短旋律钩子
    if b % 4 == 2 and not intro:
        for j, (off, d) in enumerate(((7, 0.5), (9, 0.5), (12, 1.0), (9, 0.5), (7, 1.5))):
            pos = sum(x[1] for x in ((7, 0.5), (9, 0.5), (12, 1.0), (9, 0.5), (7, 1.5))[:j])
            add(t_bar + pos * BEAT, tone(hz(ST["root"] + 12 + off), d * BEAT, "saw", dec=0.4), 0.05, 0.1)

for h in hits:
    riser(h, 2 * BEAT, 0.12)
    impact(h, 0.5)

L *= duck; R *= duck * 0.98 + 0.02
mix = np.stack([L, R], 1)[: int(A.dur * SR)]
fi, fo = int(0.3 * SR), int(1.5 * SR)
mix[:fi] *= np.linspace(0, 1, fi)[:, None]; mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix *= 10 ** (A.level / 20) / max(np.sqrt((mix ** 2).mean()), 1e-9)
if np.abs(mix).max() > 0.9:
    mix = np.tanh(mix / 0.9) * 0.9
with wave.open(A.out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print("ok", A.out, round(A.dur, 1), "s", A.style, BPM, "bpm")
