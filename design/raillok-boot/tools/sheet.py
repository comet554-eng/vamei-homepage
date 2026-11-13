"""排版：第 1 页主推配色大图 + 部件标注 + 设计说明，第 2 页四套配色。
usage: sheet.py boot.svgfrag word.json out.html"""
import json, sys
from shapely.ops import unary_union
from geom import to_poly

frag = open(sys.argv[1]).read()
word = json.load(open(sys.argv[2]))
css = open(__file__.replace('sheet.py', 'boot.css')).read()

def wordmark_svg(h, color='#000'):
    """RAILLOK 字标，独立 svg，字高 h(pt)"""
    letters = [w for w in word if w['id'] in ('P:77', 'P:91', 'P:94', 'P:106', 'P:119', 'P:141', 'P:158')]
    b = unary_union([to_poly(w['d']) for w in letters]).bounds
    w_ = (b[2] - b[0]) / (b[3] - b[1]) * h
    return (f'<svg width="{w_:.2f}pt" height="{h}pt" viewBox="{b[0]:.2f} {b[1]:.2f} {b[2] - b[0]:.2f} {b[3] - b[1]:.2f}">'
            + ''.join(f'<path d="{w["d"]}" fill="{color}"/>' for w in letters) + '</svg>')

# 部件标注：(编号, 目标点, 标号位置)，坐标是鞋图坐标（鞋头朝右）
CALLOUTS = [
    (1, (84, 250), (34, 250)),
    (2, (172, 240), (140, 205)),
    (3, (186, 362), (166, 384)),
    (4, (296, 190), (324, 172)),
    (5, (270, 140), (318, 116)),
    (6, (318, 362), (336, 334)),
    (7, (412, 414), (440, 388)),
    (8, (73, 422), (30, 422)),
    (9, (263, 60), (292, 48)),
    (10, (120, 468), (30, 470)),
]
LEGEND = [
    ('标志框架', '鞋筒外侧这整块加固片就是 RAILLOK 标志：外框做后跟杯、后背支撑和领口。'),
    ('锁跟带', '标志里那一笔斜线，从脚背斜拉到后跟，把脚跟压进后跟杯。'),
    ('锁跟带旋钮', '标志末端的小方块就是旋钮底座，单独调后跟包裹。'),
    ('鞋带旋钮', '管前面的鞋带。'),
    ('鞋带护片', '沿鞋筒前缘一直到脚背，上宽下窄，挡住鞋带区。'),
    ('鞋带导向扣', '露在前缘的几个小扣，用点缀色。'),
    ('鞋头包头', '耐磨包头，和标志框架同色。'),
    ('字标', 'RAILLOK 字标印在后跟横条上。'),
    ('提拉环', '点缀色织带。'),
    ('中底 / 大底', '沿用 Vamei 双扣的模具，只换颜色，开发只动鞋面。'),
]

def callouts():
    s = []
    for k, (tx, ty), (bx, by) in CALLOUTS:
        s.append(f'<line x1="{bx}" y1="{by}" x2="{tx}" y2="{ty}" stroke="#111" stroke-width=".5"/>'
                 f'<circle cx="{tx}" cy="{ty}" r="1.3" fill="#111" stroke="#fff" stroke-width=".4"/>'
                 f'<circle cx="{bx}" cy="{by}" r="6.6" fill="#111" stroke="#fff" stroke-width=".8"/>'
                 f'<text x="{bx}" y="{by + 2.6}" text-anchor="middle" class="num">{k}</text>')
    return ''.join(s)

VB = (12, 34, 448, 474)   # 鞋图取景（鞋图坐标）
def boot_svg(cw, width_pt, extra=''):
    h = width_pt * VB[3] / VB[2]
    return (f'<svg class="cw-{cw}" width="{width_pt}pt" height="{h:.2f}pt" viewBox="{" ".join(map(str, VB))}">'
            f'{frag}{extra}</svg>')

COLORWAYS = [
    ('slate', '岩灰 SLATE', '主推', ['鞋面：岩灰', '标志框架、包头：黑', '鞋带护片：深一号岩灰', '点缀（提拉环、导向扣、字标）：鼠尾草绿', '中底骨白，大底黑']),
    ('bone', '骨白 BONE', '', ['鞋面：骨白', '标志框架、包头：岩灰', '点缀：鼠尾草绿', '字标：骨白', '中底骨白，大底深灰']),
    ('sage', '鼠尾草 SAGE', '', ['鞋面：鼠尾草绿', '标志框架、包头：黑', '点缀：骨白', '字标：鼠尾草绿', '中底骨白，大底黑']),
    ('black', '曜黑 BLACK', '', ['鞋面：黑', '标志框架：岩灰', '包头：黑', '点缀、字标：鼠尾草绿', '中底骨白，大底黑']),
]
BRAND = [('骨白', '#F3F2EE'), ('黑', '#000000'), ('鼠尾草绿', '#C2D8C5'), ('岩灰', '#68747A')]

legend_html = ''.join(
    f'<div class="lg"><span class="lgn">{i + 1}</span><b>{t}</b>　{d}</div>' for i, (t, d) in enumerate(LEGEND))
chips_html = ''.join(
    f'<div class="chip"><div class="sw" style="background:{c}"></div><div>{n}<br><span class="hex">{c}</span></div></div>'
    for n, c in BRAND)

cells = ''
for cw, name, tag, lines in COLORWAYS:
    cells += (f'<div class="cell"><div class="cboot">{boot_svg(cw, 214)}</div>'
              f'<div class="ctext"><div class="cname">{name}{f"<span class=tag>{tag}</span>" if tag else ""}</div>'
              + ''.join(f'<div class="cl">{l}</div>' for l in lines) + '</div></div>')

html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>RAILLOK 雪鞋款式提案</title>
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/300.css">
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/400.css">
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/500.css">
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/700.css">
<link rel="stylesheet" href="../node_modules/@fontsource/inter/600.css">
<style>
@page {{ size: 841.89pt 595.276pt; margin: 0; }}
html, body {{ margin: 0; padding: 0; }}
body {{ font-family: "Noto Sans SC", sans-serif; color: #111; }}
.page:last-child {{ page-break-after: auto; }}
.page {{ position: relative; width: 841.89pt; height: 595.276pt; overflow: hidden; page-break-after: always; background: #fff; }}
.title {{ position: absolute; left: 24pt; top: 20pt; display: flex; align-items: flex-end; gap: 10pt; }}
.title .t {{ font-size: 13pt; font-weight: 400; line-height: 1; padding-bottom: 1pt; }}
.sub {{ position: absolute; left: 24pt; top: 44pt; font-size: 9pt; color: #666; }}
.mainboot {{ position: absolute; left: 4pt; top: 70pt; }}
.panel {{ position: absolute; left: 463.6pt; top: 15pt; width: 355.2pt; height: 557.3pt; background: #EFEEE9;
          box-sizing: border-box; padding: 20pt 20pt 0 20pt; }}
.h {{ font-size: 15pt; font-weight: 500; margin-bottom: 7pt; }}
.intro {{ font-size: 9.6pt; line-height: 1.65; font-weight: 400; margin-bottom: 10pt; }}
.lg {{ font-size: 8.4pt; line-height: 1.45; margin: 0 0 4.6pt 17pt; text-indent: -17pt; font-weight: 300; }}
.lg b {{ font-weight: 500; }}
.lgn {{ display: inline-block; width: 11pt; height: 11pt; border-radius: 50%; background: #111; color: #fff;
        font: 600 6.6pt/11pt Inter, sans-serif; text-align: center; text-indent: 0; margin-right: 6pt; vertical-align: 0.5pt; }}
.h2 {{ font-size: 10pt; font-weight: 500; margin: 12pt 0 5pt; }}
.lg2 {{ font-size: 8.4pt; line-height: 1.5; margin: 0 0 4pt 9pt; text-indent: -9pt; font-weight: 300; }}
.chips {{ position: absolute; left: 20pt; right: 20pt; bottom: 18pt; }}
.chips .lab {{ font-size: 8pt; color: #555; margin-bottom: 6pt; }}
.chiprow {{ display: flex; gap: 10pt; }}
.chip {{ display: flex; gap: 5pt; align-items: center; font-size: 7.6pt; line-height: 1.3; }}
.sw {{ width: 20pt; height: 20pt; border: .5pt solid rgba(0,0,0,.15); }}
.hex {{ font-family: Inter, sans-serif; font-weight: 600; font-size: 6.6pt; color: #666; }}
.num {{ font: 600 7.6px Inter, sans-serif; fill: #fff; }}
.grid {{ position: absolute; left: 24pt; top: 66pt; right: 24pt; bottom: 18pt; display: grid;
         grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 6pt 18pt; }}
.cell {{ display: flex; align-items: center; gap: 4pt; border-top: .5pt solid #ccc; }}
.ctext {{ flex: 1; }}
.cname {{ font-size: 12pt; font-weight: 500; margin-bottom: 6pt; }}
.tag {{ font-size: 7.4pt; font-weight: 400; background: #111; color: #fff; padding: 1pt 4pt; margin-left: 6pt; vertical-align: 2pt; }}
.cl {{ font-size: 8.4pt; line-height: 1.6; font-weight: 300; }}
{css}
</style></head><body>

<section class="page">
  <div class="title">{wordmark_svg(14)}<span class="t">单板雪鞋 · 款式提案 01</span></div>
  <div class="sub">右脚外侧 · 主推配色 岩灰 SLATE</div>
  <div class="mainboot">{boot_svg('slate', 452, callouts())}</div>
  <div class="panel">
    <div class="h">设计说明</div>
    <div class="intro">从侧面看，这只鞋本身就是 RAILLOK 的标志：外框围住鞋筒，做成后跟杯、后背支撑和领口；
      里面那一笔折线做成锁跟带，末端的小方块放第二个旋钮。标志不是贴上去的图案，而是鞋的结构。</div>
    {legend_html}
    <div class="h2">另外</div>
    <div class="lg2">· 左右脚对称：左脚外侧（和每只鞋的内侧）标志框架是镜像的，锁跟带都从脚背拉向后跟，就像耐克的勾在两侧都朝前。</div>
    <div class="lg2">· 材料建议：标志框架和包头用 TPU 热压、车一道边线；鞋面 PU 合成革；鞋带护片用耐磨布。</div>
    <div class="chips"><div class="lab">品牌色（取自 LOGO 规范，打样时对实物色卡确认）</div><div class="chiprow">{chips_html}</div></div>
  </div>
</section>

<section class="page">
  <div class="title">{wordmark_svg(14)}<span class="t">单板雪鞋 · 款式提案 01 · 配色</span></div>
  <div class="sub">四套配色都只用品牌的四个颜色：骨白、黑、鼠尾草绿、岩灰</div>
  <div class="grid">{cells}</div>
</section>

</body></html>'''
open(sys.argv[3], 'w').write(html)
