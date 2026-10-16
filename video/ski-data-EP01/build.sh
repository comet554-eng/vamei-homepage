#!/bin/bash
# chunked parallel render -> out/parts, concat, mux music. usage: bash build.sh
set -e
cd "$(dirname "$0")"
mkdir -p out/parts
python3 - > out/jobs.txt <<'PY'
import scenes
for n, f, d in scenes.SCENES:
    N = int(round(d * 30))
    for a in range(0, N, 300):
        print(n, a, min(N, a + 300))
PY
cat out/jobs.txt | xargs -P 4 -L 1 bash -c 'p=out/parts/$0_$(printf %05d $1).mp4; [ -s $p ] || python3 render.py video $0 $p $1 $2'
ls out/parts/*.mp4 | sort -V | sed "s#^out/#file '#; s#\$#'#" > out/concat.txt
ffmpeg -v error -y -f concat -safe 0 -i out/concat.txt -c copy out/video.mp4
python3 music.py out/music.wav
ffmpeg -v error -y -i out/video.mp4 -i out/music.wav -vf hqdn3d=3:2:6:4 -c:v libx264 -preset slow -crf 22 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart out/final.mp4
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 out/final.mp4
ls -la out/final.mp4
