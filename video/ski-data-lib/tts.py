"""Synthesize every voice line of an episode (run with the Kokoro venv python, see setup_tts.sh).
$TTS_HOME/venv/bin/python tts.py EPDIR      reads EPDIR/voice/lines.json, writes clips + durations.json"""
import os, sys, json, re
import numpy as np, soundfile as sf
T = os.environ.get("TTS_HOME", "/tmp/claude-0/tts")
from misaki import zh
import jieba, cn2an
from pypinyin import lazy_pinyin, Style
ZH = "\u4E00-\u9FFF"
NUM = set("零一二三四五六七八九十百千万亿点两第")


def g2p(text):
    """misaki's zh G2P plus the tone sandhi it lacks: 一 / 不 before 4th tone, 一 before others, 3-3 inside a word."""
    out = ""
    for seg in re.findall(f"[{ZH}]+|[^{ZH}]+", cn2an.transform(text, "an2cn")):
        if not re.match(f"[{ZH}]", seg):
            out += seg; continue
        words = jieba.lcut(seg, cut_all=False)
        syl = []                                  # [char, pinyin, word index]
        for wi, w in enumerate(words):
            for ch, py in zip(w, lazy_pinyin(w, style=Style.TONE3, neutral_tone_with_five=True)):
                syl.append([ch, py, wi])
        for i, (ch, py, wi) in enumerate(syl):
            nxt = syl[i + 1] if i + 1 < len(syl) else None
            if nxt is None:
                continue
            if ch == "一" and py == "yi1" and (i == 0 or syl[i - 1][0] not in NUM) and nxt[0] not in NUM:
                syl[i][1] = "yi2" if nxt[1].endswith("4") else "yi4"
            elif ch == "不" and nxt[1].endswith("4"):
                syl[i][1] = "bu2"
        for i in range(len(syl) - 2, -1, -1):     # third tone sandhi within a word
            if syl[i][1].endswith("3") and syl[i + 1][1].endswith("3") and syl[i][2] == syl[i + 1][2]:
                syl[i][1] = syl[i][1][:-1] + "2"
        parts = []
        for wi in range(len(words)):
            parts.append("".join(zh.ZHG2P.py2ipa(py) for _, py, w in syl if w == wi))
        out += " ".join(parts)
    return out.replace(chr(815), "")


def norm(s):
    s = re.sub(r"[——…·“”「」《》（）()]", lambda m: "，" if m.group() in "——…" else "", s)
    s = s.replace("：", "，").replace("；", "，").replace("—", "，")
    s = re.sub(r"，+", "，", s).strip("，")
    return s


def trim(a, sr, th=0.01):
    idx = np.where(np.abs(a) > th)[0]
    if not len(idx):
        return a
    return a[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.08 * sr)]


def main():
    from kokoro_onnx import Kokoro
    K = Kokoro(os.path.join(T, "expo-kokoro/package/build/kokoro-quantized.onnx"), os.path.join(T, "voices.npz"))
    EP = os.path.abspath(sys.argv[1]); VD = os.path.join(EP, "voice")
    L = json.load(open(os.path.join(VD, "lines.json"), encoding="utf-8"))
    dur = {}
    for ln in L:
        out = os.path.join(VD, ln["file"])
        if not os.path.exists(out):
            ph = g2p(norm(ln["say"]))
            a, sr = K.create(ph, voice=ln["voice"], speed=ln["speed"], is_phonemes=True)
            sf.write(out, trim(np.asarray(a, np.float32), sr), sr)
        a, sr = sf.read(out)
        dur[ln["key"]] = round(len(a) / sr, 3)
        print(f"{dur[ln['key']]:5.2f}s  {ln['say']}")
    json.dump(dur, open(os.path.join(VD, "durations.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("total voice", round(sum(dur.values()), 1), "s")


if __name__ == "__main__":
    main()
