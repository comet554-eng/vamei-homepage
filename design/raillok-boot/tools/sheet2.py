"""方向二「壳与芯」排版：第 1 页大图 + 标注 + 概念，第 2 页四套配色 + 细节。
usage: sheet2.py mono.json word.json out.html   （图片在 build/ 里，由 build.sh 先渲染好）"""
import json, sys
from shapely.ops import unary_union
from geom import to_poly

mono = json.load(open(sys.argv[1]))
word = json.load(open(sys.argv[2]))
BG = '#E9E8E3'

def wordmark_svg(h, color='#111'):
    letters = [w for w in word if w['id'] in ('P:77', 'P:91', 'P:94', 'P:106', 'P:119', 'P:141', 'P:158')]
    b = unary_union([to_poly(w['d']) for w in letters]).bounds
    w_ = (b[2] - b[0]) / (b[3] - b[1]) * h
    return (f'<svg width="{w_:.2f}pt" height="{h}pt" viewBox="{b[0]:.2f} {b[1]:.2f} {b[2] - b[0]:.2f} {b[3] - b[1]:.2f}">'
            + ''.join(f'<path d="{w["d"]}" fill="{color}"/>' for w in letters) + '</svg>')

def mono_svg(h, color='#111'):
    b = to_poly(mono[1]['d'], evenodd=True).union(to_poly(mono[2]['d'])).bounds
    w_ = (b[2] - b[0]) / (b[3] - b[1]) * h
    return (f'<svg width="{w_:.2f}pt" height="{h}pt" viewBox="{b[0]:.2f} {b[1]:.2f} {b[2] - b[0]:.2f} {b[3] - b[1]:.2f}">'
            f'<path d="{mono[1]["d"]}" fill-rule="evenodd" fill="{color}"/><path d="{mono[2]["d"]}" fill="{color}"/></svg>')

# 大图位置（pt）：鞋图坐标 viewBox 20 40 440 480
HX, HY, HW = 206, 62, 404
K = HW / 440
def P(bx, by):
    return (HX + (bx - 20) * K, HY + (by - 40) * K)

# 标注：目标点（鞋图坐标）、标签锚点（页面坐标）、标签对齐、标题、说明
NOTES = [
    ((92, 80), (256, 76), 'end', '后背脊条 · 提拉环', '壳沿后背一直到顶，标志压印在脊条上'),
    ((290, 92), (632, 96), 'start', '鞋舌拉环', '和后提拉环同色，前后呼应'),
    ((283, 175), (632, 150), 'start', '鞋带盖', '与壳同色，三面把软芯围住'),
    ((205, 232), (632, 206), 'start', '软芯 · 等高线绗缝', '顺着壳的边一圈圈往外走'),
    ((262, 393), (632, 330), 'start', '包边细线', '鼠尾草绿，沿壳的上沿一笔到底'),
    ((350, 425), (632, 392), 'start', '硬壳', '哑光 TPU 涂层，从鞋头包到后跟'),
    ((170, 380), (224, 371), 'end', '后跟锁定旋钮', '装在壳上，单独收紧后跟'),
    ((300, 466), (632, 470), 'start', '中底 / 大底', '沿用现有模具，只换颜色'),
]

def notes_svg():
    s = []
    for (bx, by), (lx, ly), anchor, t, d in NOTES:
        tx, ty = P(bx, by)
        ex = lx - 6 if anchor == 'start' else lx + 6          # 引线先水平走到标签旁
        s.append(f'<polyline points="{tx:.1f},{ty:.1f} {ex:.1f},{ly:.1f} {lx - (4 if anchor == "start" else -4):.1f},{ly:.1f}" '
                 f'fill="none" stroke="#2a2a2a" stroke-width=".45"/>'
                 f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="1.7" fill="#2a2a2a" stroke="#fff" stroke-width=".6"/>'
                 f'<text x="{lx}" y="{ly - 1.5}" text-anchor="{anchor}" class="nt">{t}</text>'
                 f'<text x="{lx}" y="{ly + 9.5}" text-anchor="{anchor}" class="nd">{d}</text>')
    return ''.join(s)

COLORWAYS = [
    ('black-bone', '曜黑 / 骨白', 'BLACK / BONE', '壳、鞋带盖黑，芯骨白，鼠尾草绿包边'),
    ('slate-bone', '岩灰 / 骨白', 'SLATE / BONE', '壳岩灰，芯骨白，鼠尾草绿包边'),
    ('sage-bone', '鼠尾草 / 骨白', 'SAGE / BONE', '壳鼠尾草绿，芯骨白，黑色包边和拉环'),
    ('black-black', '全黑', 'TRIPLE BLACK', '壳和芯都是黑，只留鼠尾草绿一条线'),
]
DETAILS = [
    ('detail-dial.jpg', '后跟锁定旋钮', '旋钮盖上是图形标'),
    ('detail-quilt.jpg', '等高线绗缝 + 鞋带盖', '软和硬在这里交界'),
    ('detail-spine.jpg', '后背脊条', '标志压印，和壳同色'),
]

cw_html = ''.join(
    f'<div class="cw"><img src="cw-{k}.png"><div class="cwn">{n}<span>{e}</span></div><div class="cwd">{d}</div></div>'
    for k, n, e, d in COLORWAYS)
dt_html = ''.join(
    f'<div class="dt"><img src="{f}"><div class="dtn">{n}</div><div class="dtd">{d}</div></div>' for f, n, d in DETAILS)

html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>RAILLOK 雪鞋款式提案 02 · 壳与芯</title>
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/300.css">
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/400.css">
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/500.css">
<link rel="stylesheet" href="../node_modules/@fontsource/inter/400.css">
<link rel="stylesheet" href="../node_modules/@fontsource/inter/600.css">
<style>
@page {{ size: 841.89pt 595.276pt; margin: 0; }}
html, body {{ margin: 0; padding: 0; }}
body {{ font-family: "Noto Sans SC", sans-serif; color: #1a1a1a; }}
.page {{ position: relative; width: 841.89pt; height: 595.276pt; overflow: hidden; page-break-after: always; background: {BG}; }}
.page:last-child {{ page-break-after: auto; }}
.brand {{ position: absolute; left: 36pt; top: 34pt; }}
.kicker {{ position: absolute; left: 36pt; top: 52pt; font-size: 7.6pt; color: #77756f; letter-spacing: .4pt; }}
.title {{ position: absolute; left: 34pt; top: 96pt; font-size: 42pt; font-weight: 300; letter-spacing: 4pt; line-height: 1; }}
.title-en {{ position: absolute; left: 37pt; top: 148pt; font: 400 7.6pt Inter, sans-serif; letter-spacing: 3.2pt; color: #55534e; }}
.concept {{ position: absolute; left: 36pt; top: 178pt; width: 150pt; font-size: 8.6pt; line-height: 1.85; font-weight: 300; }}
.diagram {{ position: absolute; left: 36pt; top: 448pt; width: 150pt; }}
.diag-row {{ display: flex; align-items: center; justify-content: space-between; }}
.diag-cap {{ display: flex; justify-content: space-between; font-size: 7pt; color: #66645e; margin-top: 7pt; }}
.arrow {{ font: 300 14pt Inter, sans-serif; color: #888; }}
.hero {{ position: absolute; left: {HX}pt; top: {HY}pt; width: {HW}pt; }}
.overlay {{ position: absolute; left: 0; top: 0; width: 841.89pt; height: 595.276pt; }}
.nt {{ font: 500 8.4px "Noto Sans SC", sans-serif; fill: #1a1a1a; }}
.nd {{ font: 300 7.2px "Noto Sans SC", sans-serif; fill: #66645e; }}
.foot {{ position: absolute; left: 36pt; bottom: 24pt; font-size: 7pt; color: #8a8882; }}
.p2title {{ position: absolute; left: 36pt; top: 72pt; font-size: 18pt; font-weight: 300; letter-spacing: 2pt; }}
.cws {{ position: absolute; left: 30pt; right: 30pt; top: 104pt; display: flex; justify-content: space-between; }}
.cw {{ width: 190pt; }}
.cw img {{ width: 190pt; display: block; }}
.cwn {{ font-size: 9.6pt; font-weight: 500; margin: 4pt 0 2pt 10pt; }}
.cwn span {{ font: 400 6.6pt Inter, sans-serif; letter-spacing: 1.6pt; color: #77756f; margin-left: 6pt; }}
.cwd {{ font-size: 7.4pt; font-weight: 300; color: #55534e; margin-left: 10pt; }}
.dts {{ position: absolute; left: 36pt; right: 36pt; top: 392pt; display: flex; justify-content: space-between; }}
.dt {{ width: 246pt; }}
.dt img {{ width: 246pt; height: 152pt; object-fit: cover; display: block; border-radius: 2pt; }}
.dtn {{ font-size: 8.4pt; font-weight: 500; margin-top: 6pt; }}
.dtd {{ font-size: 7.2pt; font-weight: 300; color: #66645e; }}
.rule {{ position: absolute; left: 36pt; right: 36pt; top: 380pt; border-top: .5pt solid #cfcdc6; }}
</style></head><body>

<section class="page">
  <div class="brand">{wordmark_svg(9.5)}</div>
  <div class="kicker">单板雪鞋 · 款式提案 02</div>
  <div class="title">壳与芯</div>
  <div class="title-en">SHELL / CORE</div>
  <div class="concept">RAILLOK 的标志，是一个外框里套着一个形。<br><br>
    鞋也拆成两层：外面一层硬壳，从鞋头包到后跟，再沿后背一路往上，和鞋带盖一起把鞋围住；
    里面一层软芯，绗缝顺着壳的边一圈圈往外走。<br><br>
    硬的利落，软的饱满。标志不贴在鞋上，只把它的道理放进结构里。</div>
  <div class="diagram">
    <div class="diag-row">{mono_svg(46)}<span class="arrow">→</span><img src="icon.svg" style="height:50pt"></div>
    <div class="diag-cap"><span>外框 + 内形</span><span>壳 + 芯</span></div>
  </div>
  <img class="hero" src="hero.png">
  <svg class="overlay" viewBox="0 0 841.89 595.276">{notes_svg()}</svg>
  <div class="foot">右脚外侧 · 主推配色 曜黑 / 骨白 · 品牌色取自 LOGO 规范</div>
</section>

<section class="page">
  <div class="brand">{wordmark_svg(9.5)}</div>
  <div class="kicker">单板雪鞋 · 款式提案 02 · 壳与芯</div>
  <div class="p2title">配色</div>
  <div class="cws">{cw_html}</div>
  <div class="rule"></div>
  <div class="dts">{dt_html}</div>
</section>
</body></html>'''
open(sys.argv[3], 'w').write(html)
