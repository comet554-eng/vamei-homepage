"""提案 04「轨与锁」排版，照 Vamei 稿的格式（白底、左边鞋图、右边灰色说明栏）：
  第 1 页：白色款式图 + 编号说明；第 2 页：主推配色 岩灰 + 色卡；第 3 页：四套配色。
usage: sheet4.py build_dir word.json out.html"""
import json, sys
from shapely.ops import unary_union
from geom import to_poly

B = sys.argv[1]
word = json.load(open(sys.argv[2]))

def svg(cw, width_pt, extra=''):
    s = open(f'{B}/t4-{cw}.svg').read()
    h = width_pt * 470 / 440
    s = s.replace('width="880" height="940"', f'width="{width_pt}pt" height="{h:.2f}pt"')
    # 每张图的 pattern id 加前缀，避免同一页里互相引用
    for pid in ('crackle', 'mesh', 'linermesh', 'strapweb'):
        s = s.replace(f'id="{pid}"', f'id="{pid}-{cw}"').replace(f'url(#{pid})', f'url(#{pid}-{cw})')
    return s.replace('</svg>', extra + '</svg>')

def wordmark_svg(h, color='#111'):
    letters = [w for w in word if w['id'] in ('P:77', 'P:91', 'P:94', 'P:106', 'P:119', 'P:141', 'P:158')]
    b = unary_union([to_poly(w['d']) for w in letters]).bounds
    w_ = (b[2] - b[0]) / (b[3] - b[1]) * h
    return (f'<svg width="{w_:.2f}pt" height="{h}pt" viewBox="{b[0]:.2f} {b[1]:.2f} {b[2] - b[0]:.2f} {b[3] - b[1]:.2f}">'
            + ''.join(f'<path d="{w["d"]}" fill="{color}"/>' for w in letters) + '</svg>')

# 编号标注（TP 坐标，鞋头朝左）
MARKS = [(1, 296, 330), (2, 380, 432), (3, 354, 168), (4, 306, 408), (5, 224, 292), (6, 82, 412),
         (7, 222, 437), (8, 434, 264), (9, 330, 127), (10, 332, 477)]
LEGEND = [
    ('两条「轨」', '平行压条从后跟斜扫到脚踝前侧，钻进前护片底下；上面一条印 RAILLOK 字标'),
    ('后跟「锁」杯', '龟裂纹皮料包住后跟，上沿斜切；后跟压一个小图形标'),
    ('上鞋身片', '下沿和轨道平行；嵌一块梯形网布窗，窗上是图形标铭牌'),
    ('前下鞋身片', '后沿和轨道平行；透气孔阵沿轨道方向斜排'),
    ('前侧护片', '从领口一直到脚背，BOA 位置沿用双扣'),
    ('鞋头', '后缘斜切，和轨道同一个角度；一排透气孔沿切边走'),
    ('防泥条', '沿底边一圈，接住鞋头和后跟杯'),
    ('后背脊条', '两条反光拉片'),
    ('领口软垫 / 内胆', '形状沿用 TP'),
    ('中底', '后跟的放射线改成平行斜纹，呼应「轨」；中底、大底模具沿用'),
]

def marks():
    return ''.join(f'<circle cx="{x}" cy="{y}" r="6.2" fill="#111" stroke="#fff" stroke-width="1"/>'
                   f'<text x="{x}" y="{y + 2.5}" text-anchor="middle" class="num">{k}</text>' for k, x, y in MARKS)

CHIPS = [('岩灰', '#68747A', '上鞋身片、前下鞋身片'),
         ('黑', '#151617', '前侧护片、鞋头、防泥条、后跟杯、后背、领口、内胆、魔术贴'),
         ('鼠尾草绿', '#C2D8C5', '两条轨、提拉环、标志'),
         ('骨白', '#F3F2EE', '中底')]
COLORWAYS = [('slate', '岩灰（主推）', '鞋身岩灰<br>护片、鞋头、后跟杯等黑<br>轨道、提拉环鼠尾草绿<br>中底骨白'),
             ('bone', '骨白', '鞋身骨白<br>护片、鞋头、后跟杯等岩灰<br>轨道、提拉环黑<br>中底骨白'),
             ('sage', '鼠尾草', '鞋身鼠尾草绿<br>护片、鞋头、后跟杯等黑<br>轨道、提拉环骨白<br>中底骨白'),
             ('black', '全黑', '鞋身深灰黑<br>护片、鞋头、后跟杯等黑<br>轨道岩灰，提拉环鼠尾草绿<br>中底黑')]

legend = ''.join(f'<div class="lg"><span class="n">{i + 1}</span><b>{t}</b>　{d}</div>' for i, (t, d) in enumerate(LEGEND))
chips = ''.join(f'<div class="chip"><div class="sw" style="background:{c}"></div><div><div class="cn">{n} <span>{c}</span></div>'
                f'<div class="cd">{d}</div></div></div>' for n, c, d in CHIPS)
grid = ''.join(f'<div class="cell">{svg(k, 236)}<div class="gt"><div class="gn">{n}</div><div class="gd">{d}</div></div></div>' for k, n, d in COLORWAYS)

html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>RAILLOK 雪鞋款式提案 04 · 轨与锁</title>
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/400.css">
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/500.css">
<link rel="stylesheet" href="../node_modules/@fontsource/inter/600.css">
<style>
@page {{ size: 841.89pt 595.276pt; margin: 0; }}
html, body {{ margin: 0; padding: 0; }}
body {{ font-family: "Noto Sans SC", sans-serif; color: #111; }}
.page {{ position: relative; width: 841.89pt; height: 595.276pt; overflow: hidden; page-break-after: always; background: #fff; }}
.page:last-child {{ page-break-after: auto; }}
.title {{ position: absolute; left: 14pt; top: 14pt; display: flex; align-items: flex-end; gap: 8pt; font-size: 17pt; font-weight: 500; }}
.boot {{ position: absolute; left: 4pt; top: 50pt; }}
.panel {{ position: absolute; left: 463.6pt; top: 15pt; width: 355.2pt; height: 557.3pt; background: #C9C9C9;
          box-sizing: border-box; padding: 22pt 22pt 0 22pt; }}
.h {{ font-size: 15pt; font-weight: 500; margin-bottom: 12pt; }}
.lg {{ font-size: 9pt; line-height: 1.5; margin: 0 0 7pt 18pt; text-indent: -18pt; }}
.lg b {{ font-weight: 500; }}
.n {{ display: inline-block; width: 12pt; height: 12pt; border-radius: 50%; background: #111; color: #fff; text-indent: 0;
      font: 600 7pt/12pt Inter, sans-serif; text-align: center; margin-right: 6pt; vertical-align: .5pt; }}
.num {{ font: 600 7.2px Inter, sans-serif; fill: #fff; }}
.note {{ position: absolute; left: 22pt; right: 22pt; bottom: 20pt; font-size: 8.4pt; line-height: 1.6; color: #333; }}
.chip {{ display: flex; gap: 12pt; align-items: center; margin-bottom: 16pt; }}
.sw {{ width: 64pt; height: 64pt; flex: none; border: .5pt solid rgba(0,0,0,.2); }}
.cn {{ font-size: 15pt; font-weight: 400; }}
.cn span {{ font: 600 8pt Inter, sans-serif; color: #444; margin-left: 4pt; }}
.cd {{ font-size: 9pt; color: #222; margin-top: 3pt; line-height: 1.5; }}
.grid {{ position: absolute; left: 16pt; right: 16pt; top: 40pt; display: grid; grid-template-columns: 1fr 1fr; gap: 0 10pt; }}
.cell {{ display: flex; align-items: center; }}
.gt {{ flex: 1; padding-bottom: 20pt; }}
.gn {{ font-size: 13pt; font-weight: 500; margin-bottom: 4pt; }}
.gd {{ font-size: 9pt; color: #333; line-height: 1.6; }}
.p3note {{ position: absolute; left: 30pt; bottom: 26pt; font-size: 8.4pt; color: #444; }}
</style></head><body>

<section class="page">
  <div class="title">{wordmark_svg(15)}<span>单板雪鞋 · 款式 04「轨与锁」</span></div>
  <div class="boot">{svg('tp', 452, marks())}</div>
  <div class="panel">
    <div class="h">新鞋面分片说明</div>
    {legend}
    <div class="note">大底、中底、内胆、BOA、魔术贴沿用 Vamei 双扣 TP 的形状，开发主要动鞋面。<br>
      若按此白色配色打样，白色请选偏暖的米白，不要太假白。</div>
  </div>
</section>

<section class="page">
  <div class="title">{wordmark_svg(15)}<span>单板雪鞋 · 款式 04 · 岩灰</span></div>
  <div class="boot">{svg('slate', 452)}</div>
  <div class="panel">
    <div class="h">配色：岩灰（主推）</div>
    {chips}
    <div class="note">品牌色取自 RAILLOK LOGO 规范，打样时对实物色卡确认色号。</div>
  </div>
</section>

<section class="page">
  <div class="title">{wordmark_svg(15)}<span>单板雪鞋 · 款式 04 · 配色</span></div>
  <div class="grid">{grid}</div>
  <div class="p3note">四套配色都只用品牌四色：骨白、黑、鼠尾草绿、岩灰。</div>
</section>
</body></html>'''
open(sys.argv[3], 'w').write(html)
