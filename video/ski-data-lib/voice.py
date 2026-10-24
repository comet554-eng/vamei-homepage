"""Voice-over helpers (system python).
python3 voice.py list EPDIR                    -> EPDIR/voice/lines.json (every *_SUBS line; scenes.SAY overrides the spoken text)
python3 voice.py mix  EPDIR music.wav out.wav  -> voice placed on the subtitle times, music ducked under it"""
import os, sys, json, hashlib, wave, math
HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.abspath(sys.argv[2]); sys.path.insert(0, HERE); sys.path.insert(0, EP)
import numpy as np
import scenes as S
from art import plain

VD = os.path.join(EP, "voice"); os.makedirs(VD, exist_ok=True)
VOICE = getattr(S, "VOICE", "zm_yunxi"); SPEED = getattr(S, "VOICE_SPEED", 1.0); SAY = getattr(S, "SAY", {})


def lines():
    """[(global_start, key, say)] in film order."""
    out, t0 = [], 0.0
    for name, _, dur in S.SCENES:
        for s, a, _ in getattr(S, name.upper() + "_SUBS", []):
            k = plain(s); say = SAY.get(k, k)
            if say:
                out.append((t0 + a, k, say))
        t0 += dur
    return out


def fname(say):
    return hashlib.sha1(f"{VOICE}|{SPEED}|{say}".encode()).hexdigest()[:12] + ".wav"


if sys.argv[1] == "list":
    L = [dict(key=k, say=say, voice=VOICE, speed=SPEED, file=fname(say)) for _, k, say in lines()]
    json.dump(L, open(os.path.join(VD, "lines.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(L), "lines")
else:
    import soundfile as sf
    SR = 44100
    m, msr = sf.read(sys.argv[3], dtype="float32"); assert msr == SR
    N = len(m); v = np.zeros(N, np.float32)
    for t, k, say in lines():
        a, sr = sf.read(os.path.join(VD, fname(say)), dtype="float32")
        a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a).astype(np.float32)
        i = int((t + 0.08) * SR); a = a[: max(0, N - i)]
        v[i:i + len(a)] += a
    # voice: gentle high-pass + presence, level to -19 dBFS RMS over the spoken parts
    v = v - np.convolve(v, np.ones(220) / 220, "same")
    act = np.convolve(np.abs(v) > 0.01, np.ones(int(0.3 * SR)), "same") > 0
    v *= 10 ** (-19 / 20) / max(np.sqrt((v[act] ** 2).mean()), 1e-9)
    # duck music ~9 dB while speaking (smooth 250 ms envelope)
    env = np.convolve(act.astype(np.float32), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
    g = 1 - (1 - 10 ** (-9 / 20)) * np.clip(env, 0, 1)
    out = m * g[:, None] + v[:, None] * np.array([0.98, 1.0], np.float32)
    pk = np.abs(out).max()
    if pk > 0.95:
        out = np.tanh(out / 0.95) * 0.95
    sf.write(sys.argv[4], out, SR, subtype="PCM_16")
    print("voice lines", len(lines()), "peak", round(float(pk), 3))
