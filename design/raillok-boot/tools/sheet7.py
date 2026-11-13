"""提案 07「一笔」排版，照 Vamei 稿的格式（白底、左边鞋图、右边灰色说明栏）：
  第 1 页：白色款式图 + 编号说明；第 2 页：主推配色 石墨 + 色卡；第 3 页：四套配色。
usage: sheet7.py build_dir word.json out.html"""
import json, sys
from shapely.ops import unary_union
from geom import to_poly

B = sys.argv[1]
word = json.load(open(sys.argv[2]))

def svg(cw, width_pt, extra=''):
    s = open(f'{B}/r7-{cw}.svg').read()        # pattern id 在 tpkit 里已经按配色加了前缀
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
MARKS = [(1, 400, 300), (2, 330, 150), (3, 362, 270), (4, 246, 170), (5, 262, 344), (6, 76, 428),
         (7, 404, 236), (8, 172, 214), (9, 258, 438), (10, 330, 477)]
LEGEND = [
    ('一笔护条', '从鞋头后面沿底边走（防泥条），绕过后跟（后跟杯），再斜着扫上鞋筒，收进侧旋钮的底座：RAIL 一路走到 LOK'),
    ('侧旋钮 · ATOP 原厂', '双扣的第二个旋钮，装在护条末端的圆形底座上；原厂件，不印任何 logo'),
    ('两圈回声', '第一圈绒面贴着护条走，上面一排细孔；外面再一道双明线。整只鞋的线都跟着这一笔'),
    ('前护片', '鞋带区护片，里面一道顺着后沿走的回声缝'),
    ('鞋带窗', '脚背弯折处挖一个斜长圆：网布 + 交叉钢丝 + 导向扣'),
    ('鞋头', '一排透气孔，和护条同一个弧度收尾'),
    ('后背脊条', '两条反光拉片'),
    ('前旋钮 · ATOP 原厂', '管鞋带区，位置同双扣，不印 logo'),
    ('压印', 'RAILLOK 字标压在护条底边，图形标压在后跟，鞋舌顶上一个织唛；品牌只出现在鞋面上'),
    ('中底 / 大底', '沿用双扣模具，只换颜色'),
]

def marks():
    return ''.join(f'<circle cx="{x}" cy="{y}" r="6.2" fill="#111" stroke="#fff" stroke-width="1"/>'
                   f'<text x="{x}" y="{y + 2.5}" text-anchor="middle" class="num">{k}</text>' for k, x, y in MARKS)

CHIPS = [('炭黑', '#3A3D40', '大面鞋面、两圈回声'),
         ('岩灰', '#596268', '一笔护条'),
         ('深炭', '#2C2F32', '前护片、鞋头、领口、后背'),
         ('鼠尾草绿', '#C2D8C5', '护条滚边、鞋舌织唛、导向扣'),
         ('骨白', '#F3F2EE', '中底')]
COLORWAYS = [('graphite', '石墨（主推）', '鞋面炭黑，护条岩灰<br>前护片、鞋头深炭<br>鼠尾草绿一道滚边<br>骨白中底'),
             ('bone', '骨白', '鞋面骨白，护条暖灰<br>领口、大底岩灰<br>岩灰滚边'),
             ('slate', '岩灰', '鞋面岩灰，护条深一号<br>鞋头、领口深灰<br>骨白滚边'),
             ('sage', '鼠尾草', '鞋面灰鼠尾草，护条深一号<br>鞋头、领口苔绿<br>骨白滚边')]

legend = ''.join(f'<div class="lg"><span class="n">{i + 1}</span><b>{t}</b>　{d}</div>' for i, (t, d) in enumerate(LEGEND))
chips = ''.join(f'<div class="chip"><div class="sw" style="background:{c}"></div><div><div class="cn">{n} <span>{c}</span></div>'
                f'<div class="cd">{d}</div></div></div>' for n, c, d in CHIPS)
grid = ''.join(f'<div class="cell">{svg(k, 236)}<div class="gt"><div class="gn">{n}</div><div class="gd">{d}</div></div></div>' for k, n, d in COLORWAYS)

html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>RAILLOK 雪鞋款式提案 07 · 一笔</title>
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
.chip {{ display: flex; gap: 12pt; align-items: center; margin-bottom: 12pt; }}
.sw {{ width: 56pt; height: 56pt; flex: none; border: .5pt solid rgba(0,0,0,.2); }}
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
  <div class="title">{wordmark_svg(15)}<span>单板双扣雪鞋 · 款式 07「一笔」</span></div>
  <div class="boot">{svg('tp', 452, marks())}</div>
  <div class="panel">
    <div class="h">新鞋面分片说明</div>
    {legend}
    <div class="note">两个旋钮都是 ATOP 原厂件，按原厂外观画，不印任何 logo。<br>
      大底、中底、内胆、魔术贴沿用 Vamei 双扣 TP 的形状，开发主要动鞋面。</div>
  </div>
</section>

<section class="page">
  <div class="title">{wordmark_svg(15)}<span>单板双扣雪鞋 · 款式 07 · 石墨</span></div>
  <div class="boot">{svg('graphite', 452)}</div>
  <div class="panel">
    <div class="h">配色：石墨（主推）</div>
    {chips}
    <div class="note">品牌色取自 RAILLOK LOGO 规范，炭黑、深炭由岩灰压暗得来；打样时对实物色卡确认色号。</div>
  </div>
</section>

<section class="page">
  <div class="title">{wordmark_svg(15)}<span>单板双扣雪鞋 · 款式 07 · 配色</span></div>
  <div class="grid">{grid}</div>
  <div class="p3note">每套都是同一色系深浅两三个色 + 一道滚边，不撞色；两个 ATOP 旋钮按配色选原厂黑或白。</div>
</section>
</body></html>'''
open(sys.argv[3], 'w').write(html)
