"""提案 06「护甲」排版，照 Vamei 稿的格式（白底、左边鞋图、右边灰色说明栏）：
  第 1 页：白色款式图 + 编号说明；第 2 页：主推配色 鼠尾草 + 色卡；第 3 页：四套配色。
usage: sheet6.py build_dir word.json out.html"""
import json, sys
from shapely.ops import unary_union
from geom import to_poly

B = sys.argv[1]
word = json.load(open(sys.argv[2]))

def svg(cw, width_pt, extra=''):
    s = open(f'{B}/a6-{cw}.svg').read()        # pattern id 在 tpkit 里已经按配色加了前缀
    h = width_pt * 470 / 440
    s = s.replace('width="880" height="940"', f'width="{width_pt}pt" height="{h:.2f}pt"')
    return s.replace('</svg>', extra + '</svg>')

def wordmark_svg(h, color='#111'):
    letters = [w for w in word if w['id'] in ('P:77', 'P:91', 'P:94', 'P:106', 'P:119', 'P:141', 'P:158')]
    b = unary_union([to_poly(w['d']) for w in letters]).bounds
    w_ = (b[2] - b[0]) / (b[3] - b[1]) * h
    return (f'<svg width="{w_:.2f}pt" height="{h}pt" viewBox="{b[0]:.2f} {b[1]:.2f} {b[2] - b[0]:.2f} {b[3] - b[1]:.2f}">'
            + ''.join(f'<path d="{w["d"]}" fill="{color}"/>' for w in letters) + '</svg>')

# 编号标注（TP 坐标，鞋头朝左）
MARKS = [(1, 400, 268), (2, 297, 190), (3, 246, 252), (4, 345, 162), (5, 186, 186), (6, 256, 282),
         (7, 306, 286), (8, 330, 400), (9, 422, 362), (10, 70, 446)]
LEGEND = [
    ('护甲侧片', '外层一整块护甲，前沿在脚踝处斜切一刀（标志的斜角），挖出一个大窗口露出里面的内靴'),
    ('加厚包边', '一整圈骨白包边框住上侧片，边上一排装饰打结线'),
    ('网布内靴 · 钢丝', '窗口里露出另一色的六角网布内靴，两根 BOA 钢丝在里面交叉，导向扣沿两边排开'),
    ('侧片旋钮 · 盾形凸起', '第二个 BOA 管小腿上段，装在一块盾形凸起里；旋钮盖上是图形标'),
    ('前旋钮', '管鞋带区，位置沿用双扣'),
    ('织带拉片', '护甲前沿一个织带环，挂一片布拉手'),
    ('织唛标签', 'RAILLOK 字标织唛，竖着缝在包边旁'),
    ('模压浮雕线', '下半截护甲上几道同色浮雕线，顺着包边的弧线走'),
    ('后跟杯', '内靴同色，压一个小图形标'),
    ('鞋头 · 后跟包胶', '鞋头和后跟各一块耐磨包胶，和大底同色'),
]

def marks():
    return ''.join(f'<circle cx="{x}" cy="{y}" r="6.2" fill="#111" stroke="#fff" stroke-width="1"/>'
                   f'<text x="{x}" y="{y + 2.5}" text-anchor="middle" class="num">{k}</text>' for k, x, y in MARKS)

CHIPS = [('浅鼠尾草', '#D6E4D8', '护甲侧片、鞋头、侧片盾形凸起'),
         ('骨白', '#F3F2EE', '加厚包边、中底、标签字'),
         ('深鼠尾草', '#8CA394', '网布内靴、后跟杯、领口、提拉环、织带、打结线'),
         ('苔绿', '#7F968A', '鞋头 / 后跟包胶、大底')]
COLORWAYS = [('sage', '鼠尾草（主推）', '护甲浅鼠尾草，包边骨白<br>内靴、后跟杯深鼠尾草<br>包胶、大底苔绿'),
             ('slate', '雾灰', '护甲浅灰，包边同色（靠浮雕）<br>内靴、后跟杯岩灰<br>包胶、大底岩灰'),
             ('bone', '骨白', '护甲骨白，包边浅一号<br>内靴、后跟杯鼠尾草绿<br>包胶、大底灰绿'),
             ('black', '曜黑', '护甲黑，包边岩灰<br>内靴鼠尾草绿，后跟杯黑<br>中底骨白，大底黑')]

legend = ''.join(f'<div class="lg"><span class="n">{i + 1}</span><b>{t}</b>　{d}</div>' for i, (t, d) in enumerate(LEGEND))
chips = ''.join(f'<div class="chip"><div class="sw" style="background:{c}"></div><div><div class="cn">{n} <span>{c}</span></div>'
                f'<div class="cd">{d}</div></div></div>' for n, c, d in CHIPS)
grid = ''.join(f'<div class="cell">{svg(k, 236)}<div class="gt"><div class="gn">{n}</div><div class="gd">{d}</div></div></div>' for k, n, d in COLORWAYS)

html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>RAILLOK 雪鞋款式提案 06 · 护甲</title>
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
  <div class="title">{wordmark_svg(15)}<span>单板雪鞋 · 款式 06「护甲」</span></div>
  <div class="boot">{svg('tp', 452, marks())}</div>
  <div class="panel">
    <div class="h">新鞋面分片说明</div>
    {legend}
    <div class="note">参考 Vamei 实物的设计语言：外层护甲挖窗露出另一色内靴、双 BOA、包边、同色浮雕。<br>
      大底、中底、内胆、BOA、魔术贴沿用 Vamei 双扣 TP 的形状，开发主要动鞋面。</div>
  </div>
</section>

<section class="page">
  <div class="title">{wordmark_svg(15)}<span>单板雪鞋 · 款式 06 · 鼠尾草</span></div>
  <div class="boot">{svg('sage', 452)}</div>
  <div class="panel">
    <div class="h">配色：鼠尾草（主推）</div>
    {chips}
    <div class="note">深浅三个绿由品牌鼠尾草绿 #C2D8C5 推出来，骨白取自 RAILLOK LOGO 规范；打样时对实物色卡确认色号。</div>
  </div>
</section>

<section class="page">
  <div class="title">{wordmark_svg(15)}<span>单板雪鞋 · 款式 06 · 配色</span></div>
  <div class="grid">{grid}</div>
  <div class="p3note">配色思路照 Vamei 实物：同一色系深浅两色 + 骨白包边；深色给内靴、后跟、包胶，浅色给护甲。</div>
</section>
</body></html>'''
open(sys.argv[3], 'w').write(html)
