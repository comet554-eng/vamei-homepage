"""提案 08：Figma AI 概念渲染总览（5 个方向一页）。图在 renders/ 里，由 Figma AI 生成。
usage: sheet8.py word.json out.html"""
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

V = [('A', '石墨', '炭黑麂皮 + 岩灰护条一笔从鞋头绕后跟扫到侧旋钮，鼠尾草绿滚边'),
     ('B', '鼠尾草', '骨白护甲侧片框住侧旋钮，前面露鼠尾草网布内靴，鞋头后跟鼠尾草绒面'),
     ('C', '岩灰棱面', '岩灰鞋面 + 黑色棱面外骨骼包住后跟和侧旋钮，脚背一道鼠尾草细线'),
     ('D', '曜黑', '全黑皮革，上段横向绗缝，后跟一道鼠尾草细滚边，亮面包头'),
     ('E', '骨白等高线', '骨白皮 + 暖灰绒面一层层等高线往后跟抬，岩灰后跟和包头')]
cells = ''.join(f'<div class="c"><img src="../renders/r8-{k}-{n}.jpg"><div class="t"><b>{k}</b> {n}</div><div class="d">{d}</div></div>'
                for k, n, d in V)
html = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>RAILLOK 雪鞋概念渲染 08</title>
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/400.css">
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/500.css">
<link rel="stylesheet" href="../node_modules/@fontsource/inter/600.css">
<style>
@page {{ size: 841.89pt 595.276pt; margin: 0; }}
html, body {{ margin: 0; }}
body {{ font-family: "Noto Sans SC", sans-serif; color: #111; }}
.page {{ position: relative; width: 841.89pt; height: 595.276pt; overflow: hidden; background: #fff; }}
.title {{ position: absolute; left: 22pt; top: 18pt; display: flex; align-items: flex-end; gap: 8pt; font-size: 15pt; font-weight: 500; }}
.grid {{ position: absolute; left: 22pt; right: 22pt; top: 50pt; display: flex; flex-wrap: wrap; justify-content: center; gap: 10pt 12pt; }}
.c {{ width: 250pt; }}
.c img {{ width: 250pt; height: 167pt; object-fit: cover; display: block; border-radius: 2pt; }}
.t {{ font-size: 10.5pt; font-weight: 500; margin-top: 4pt; }}
.t b {{ font: 600 10.5pt Inter, sans-serif; margin-right: 3pt; }}
.d {{ font-size: 7.8pt; color: #444; line-height: 1.5; }}
.note {{ position: absolute; left: 22pt; right: 22pt; bottom: 14pt; font-size: 7.6pt; color: #666; }}
</style></head><body><section class="page">
<div class="title">{wordmark_svg(13)}<span>单板双扣雪鞋 · 概念渲染（5 个方向）</span></div>
<div class="grid">{cells}</div>
<div class="note">Figma AI 生成的概念效果图，用来定方向，不是生产图；两个旋钮都是空白的通用旋钮，实际用 ATOP 原厂件、不印 logo，品牌标识选定方向后再加在鞋面上。</div>
</section></body></html>'''
open(sys.argv[2], 'w').write(html)
