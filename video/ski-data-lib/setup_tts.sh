#!/bin/bash
# One-time setup of the offline Chinese voice (Kokoro-82M, 8 zh voices) -> $TTS_HOME (default /tmp/claude-0/tts).
# Only pypi + npm are reachable here: the weights and voice files ship inside the npm package expo-kokoro.
set -e
T="${TTS_HOME:-/tmp/claude-0/tts}"; mkdir -p "$T"; cd "$T"
[ -d venv ] || python3 -m venv venv
. venv/bin/activate
pip install -q -U pip setuptools wheel
pip install -q kokoro-onnx "misaki[zh]" soundfile numpy
if [ ! -f expo-kokoro/package/build/kokoro-quantized.onnx ]; then
  mkdir -p expo-kokoro && (cd expo-kokoro && npm pack expo-kokoro --silent && tar xzf expo-kokoro-*.tgz)
fi
python3 - <<'PY'
import numpy as np, glob, os
d = {os.path.basename(f)[:-4]: np.fromfile(f, dtype=np.float32).reshape(-1, 1, 256)
     for f in glob.glob('expo-kokoro/package/build/voices/*.bin')}
np.savez('voices.npz', **d); print(len(d), 'voices')
PY
