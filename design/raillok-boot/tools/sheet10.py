"""提案 10：设计师手绘风概念草图总览（4 个方向一页）。图在 renders/ 里，由 Figma AI 生成。
usage: sheet10.py word.json out.html"""
import json, sys
from shapely.ops import unary_union
from geom import to_poly

word = json.load(open(sys.argv[1]))

def wordmark_svg(h, color='#111'):
    letters = [w for w in word if w['id'] in ('P:77', 'P:91', 'P:94', 'P:106', 'P:119', 'P:141', 'P:158')]
    b = unary_union([to_poly(w['d']) for w in letters]).bounds
    w_ = (b[2] - b[0]) / (b[3] - b[1]) * h
    return (f'<svg width="{w_:.2f}pt" height="{h}pt" viewBox="{b[0]:.2f} {b[1]:.2f} {b[2] - b[0]:.2f} {b[3] - b[1]:.2f}">'
            + ''.join(f'<path d="{w["d"]}" fill="{color}"/>' for w in letters) + '</svg>')

V = [('A', '外骨骼', 'TPU 镂空外骨骼包住鞋筒、后跟和鞋头，露出里面的 3D 针织内靴；锁跟织带穿过骨架绕脚踝，侧旋钮坐在骨架的凸台上，后跟杯带加强筋'),
     ('B', '甲片', '鞋筒是一片片叠起来的弧形甲片（像武士铠甲），每片双明线，往前倾能弯；后跟一体模压支架带肋，侧旋钮装在支架上；独立盾形鞋带盖'),
     ('C', '包裹', '一大片外包片从内侧横跨脚背、扣到外侧，把鞋带完全盖住；侧旋钮装在包片边缘，一拧把包片和内部锁跟一起收紧；底下几层分片错开'),
     ('D', '户外五金', '皮革 + 麂皮分片 + 双明线，后跟是几何镂空的 TPU 后跟杯；外露锁跟织带配金属 D 环和扣，从后跟绕脚踝；绗缝领口和鞋舌')]
cells = ''.join(f'<div class="c"><img src="../renders/r10-{k}-{n}.jpg"><div class="t"><b>{k}</b> {n}</div><div class="d">{d}</div></div>'
                for k, n, d in V)
html = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>RAILLOK 雪鞋概念草图 10</title>
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/400.css">
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/500.css">
<link rel="stylesheet" href="../node_modules/@fontsource/inter/600.css">
<style>
@page {{ size: 841.89pt 595.276pt; margin: 0; }}
html, body {{ margin: 0; }}
body {{ font-family: "Noto Sans SC", sans-serif; color: #111; }}
.page {{ position: relative; width: 841.89pt; height: 595.276pt; overflow: hidden; background: #F7F6F2; }}
.title {{ position: absolute; left: 22pt; top: 18pt; display: flex; align-items: flex-end; gap: 8pt; font-size: 15pt; font-weight: 500; }}
.grid {{ position: absolute; left: 22pt; right: 22pt; top: 42pt; display: flex; flex-wrap: wrap; justify-content: center; gap: 4pt 24pt; }}
.c {{ width: 318pt; }}
.c img {{ width: 318pt; height: 212pt; object-fit: cover; display: block; border-radius: 2pt; }}
.t {{ font-size: 10.5pt; font-weight: 500; margin-top: 4pt; }}
.t b {{ font: 600 10.5pt Inter, sans-serif; margin-right: 3pt; }}
.d {{ font-size: 7.8pt; color: #444; line-height: 1.5; min-height: 24pt; }}
.note {{ position: absolute; left: 22pt; right: 22pt; bottom: 14pt; font-size: 7.6pt; color: #666; }}
</style></head><body><section class="page">
<div class="title">{wordmark_svg(13)}<span>单板双扣雪鞋 · 概念草图 10（4 个方向）</span></div>
<div class="grid">{cells}</div>
<div class="note">Figma AI 生成的设计师手绘风概念草图，用来定结构方向，不是生产图；两个旋钮都是空白的通用旋钮，实际用 ATOP 原厂件、不印 logo。</div>
</section></body></html>'''
open(sys.argv[2], 'w').write(html)
