#!/bin/bash
# 20-frame contact sheet of EPDIR/out/final.mp4 -> EPDIR/out/qa_sheet.png
E="$1"; D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$E/out/final.mp4")
rm -f "$E"/out/qa_*.png
for i in $(seq 0 19); do t=$(python3 -c "print(2+$i*($D-4)/19)"); ffmpeg -v error -y -ss $t -i "$E/out/final.mp4" -frames:v 1 -vf scale=480:270 "$E/out/qa_$(printf %02d $i).png"; done
python3 -c "
from PIL import Image; import glob,sys
fs=sorted(glob.glob('$E/out/qa_[0-9]*.png')); s=Image.new('RGB',(480*4,270*5))
for i,f in enumerate(fs): s.paste(Image.open(f),((i%4)*480,(i//4)*270))
s.save('$E/out/qa_sheet.png')"
