#!/usr/bin/env python3
"""把 Mixkit 实拍片段按镜头表叠进手绘层的相框，并截出实际用到的片段存档。

用法（在 video/ 下）：python3 tut-comp.py 镜头表.json
镜头表：{"base": 手绘层.mp4, "out": 成片.mp4, "clips": 原片目录, "keep": 片段存档目录,
        "shots": [[开始, 结束, 素材ID, 入点, "W"|"V", 裁切(可空，如 "686:1220:300:700"), 镜头字母], ...]}
相框位置和 tutkit.js 的 TFR 一致；片段只缩小不放大。
"""
import json, subprocess, sys
from pathlib import Path

FR = {'W': (60, 430, 960, 540), 'V': (70, 430, 420, 746)}
cfg = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
ins, fc, prev = [], [], '[0:v]'
for i, (t0, t1, mid, ss, fr, crop, tag) in enumerate(cfg['shots'], 1):
    x, y, w, h = FR[fr]
    ins += ['-ss', str(ss), '-t', str(round(t1 - t0 + .1, 2)), '-i', f"{cfg['clips']}/mixkit-{mid}.mp4"]
    cr = f'crop={crop},' if crop else ''
    fc.append(f"[{i}:v]fps=30,{cr}scale={w}:{h}:flags=lanczos,setsar=1,setpts=PTS-STARTPTS+{t0}/TB[c{i}];"
              f"{prev}[c{i}]overlay={x}:{y}:eof_action=pass:enable='between(t,{t0},{t1 - .001})'[v{i}]")
    prev = f'[v{i}]'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', cfg['base'], *ins, '-filter_complex', ';'.join(fc), '-map', prev, '-map', '0:a',
                '-c:v', 'libx264', '-preset', 'slow', '-b:v', '7M', '-maxrate', '10M', '-bufsize', '20M', '-pix_fmt', 'yuv420p', '-r', '30',
                '-c:a', 'copy', cfg['out']], check=True)
keep = Path(cfg['keep']); keep.mkdir(parents=True, exist_ok=True)
for t0, t1, mid, ss, fr, crop, tag in cfg['shots']:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ss), '-t', str(round(t1 - t0 + .1, 2)), '-i', f"{cfg['clips']}/mixkit-{mid}.mp4",
                    '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', str(keep / f'镜头{tag}-mixkit-{mid}.mp4')], check=True)
print('ok', cfg['out'])
