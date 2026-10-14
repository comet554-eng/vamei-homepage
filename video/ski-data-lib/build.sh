#!/bin/bash
# usage: bash build.sh EPDIR   -> EPDIR/out/final.mp4
set -e
LIB="$(cd "$(dirname "$0")" && pwd)"; EP="$(cd "$1" && pwd)"
mkdir -p "$EP/out/parts"
python3 - "$EP" > "$EP/out/jobs.txt" <<'PY'
import sys; sys.path.insert(0, sys.argv[1]); sys.path.insert(1, __import__('os').path.dirname(sys.argv[1]) + '/ski-data-lib')
import scenes
for n, f, d in scenes.SCENES:
    N = int(round(d * 30))
    for a in range(0, N, 300):
        print(n, a, min(N, a + 300))
PY
cat "$EP/out/jobs.txt" | xargs -P 4 -L 1 bash -c 'p='"$EP"'/out/parts/$0_$(printf %05d $1).mp4; [ -s $p ] || python3 '"$LIB"'/render.py '"$EP"' video $0 $p $1 $2'
ls "$EP"/out/parts/*.mp4 | sort -V | sed "s#^#file '#; s#\$#'#" > "$EP/out/concat.txt"
ffmpeg -v error -y -f concat -safe 0 -i "$EP/out/concat.txt" -c copy "$EP/out/video.mp4"
python3 "$LIB/music.py" "$EP" "$EP/out/music.wav"
AUD="$EP/out/music.wav"; AF="anull"
if [ -f "$EP/voice/durations.json" ]; then   # voiced episode: run tts.py first (see setup_tts.sh)
  python3 "$LIB/voice.py" mix "$EP" "$EP/out/music.wav" "$EP/out/mix.wav"; AUD="$EP/out/mix.wav"; AF="loudnorm=I=-16:TP=-1.5:LRA=11"
fi
ffmpeg -v error -y -i "$EP/out/video.mp4" -i "$AUD" -vf hqdn3d=3:2:6:4 -af "$AF" -ar 48000 -c:v libx264 -preset slow -crf 22 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart "$EP/out/final.mp4"
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$EP/out/final.mp4"
ls -la "$EP/out/final.mp4"
