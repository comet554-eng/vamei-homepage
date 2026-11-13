"""提案 05：四个方向对比。第 1 页四款配色版总览，第 2–5 页每个方向一页（白色款式图 + 配色版 + 要点）。
usage: sheet5.py build_dir word.json out.html"""
import json, sys
from shapely.ops import unary_union
from geom import to_poly

B = sys.argv[1]
word = json.load(open(sys.argv[2]))

def svg(key, tag, width_pt):
    s = open(f'{B}/v5-{key}-{tag}.svg').read()
    return s.replace('width="880" height="940"', f'width="{width_pt}pt" height="{width_pt * 470 / 440:.2f}pt"')

def wordmark_svg(h, color='#111'):
    letters = [w for w in word if w['id'] in ('P:77', 'P:91', 'P:94', 'P:106', 'P:119', 'P:141', 'P:158')]
    b = unary_union([to_poly(w['d']) for w in letters]).bounds
    w_ = (b[2] - b[0]) / (b[3] - b[1]) * h
    return (f'<svg width="{w_:.2f}pt" height="{h}pt" viewBox="{b[0]:.2f} {b[1]:.2f} {b[2] - b[0]:.2f} {b[3] - b[1]:.2f}">'
            + ''.join(f'<path d="{w["d"]}" fill="{color}"/>' for w in letters) + '</svg>')

V = [
    ('A', '流线', '一条大斜带，从后领口斜挎到脚背',
     ['一条大斜带从后领口斜挎到脚背，再接进鞋头；上、下鞋身片的边都顺着它走',
      '斜带里压一道鼠尾草绿细线，RAILLOK 字标印在斜带上',
      '后跟杯、圆形图形标徽章、前下鞋身一块透气孔',
      '配色：骨白鞋身，岩灰斜带 / 护片 / 鞋头 / 后跟，鼠尾草绿细线']),
    ('B', '棱面', '直线和折角，后跟两片尖楔指向脚踝',
     ['全部用直线和折角；后跟两片楔形从后往前收成尖角，指向脚踝',
      '大楔片上沿一道平行细条；前侧护片后沿是台阶折线',
      '六边形网布窗 + 六边形铭牌，鞋头双排透气孔',
      '配色：全黑，内楔岩灰，细条鼠尾草绿']),
    ('C', '绑带', '外露的锁跟织带，从后跟往前包住脚踝',
     ['两条织带从后跟出发，一条往上到鞋带区、一条往下到脚背，把脚跟锁住',
      '后跟锚点是方框加交叉缝，前端穿过金属扣；字标印在织带上',
      '上鞋身横向绗缝（软垫），领口下一块字标铭牌，后跟压图形标',
      '配色：岩灰鞋身，黑色护片 / 鞋头 / 后跟，鼠尾草绿织带']),
    ('D', '等高线', '几层压片像等高线往上叠，越往后跟越高',
     ['四层压片从底部一层层叠上来，每层上沿是平行的弧线，越往后跟越高',
      '颜色同一色系由深到浅：最底下最深，往上越来越浅',
      '沿层边一排小孔；顶上一块梯形网布窗 + 图形标铭牌',
      '配色：岩灰四层渐变，黑色护片 / 鞋头 / 领口']),
]

over = ''.join(f'<div class="cell">{svg(k, "color", 232)}<div class="ct"><div class="cn"><b>{k}</b> {n}</div>'
               f'<div class="cs">{sub}</div></div></div>' for k, n, sub, _ in V)
pages = ''
for k, n, sub, pts in V:
    pages += f'''<section class="page">
  <div class="title">{wordmark_svg(14)}<span>单板雪鞋 · 方向 {k}「{n}」</span></div>
  <div class="pair"><div>{svg(k, 'tp', 392)}<div class="lab">白色款式图</div></div><div>{svg(k, 'color', 392)}<div class="lab">配色</div></div></div>
  <div class="pts">{''.join(f'<div>· {p}</div>' for p in pts)}</div>
</section>'''

html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>RAILLOK 雪鞋款式提案 05 · 四个方向</title>
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/400.css">
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/500.css">
<link rel="stylesheet" href="../node_modules/@fontsource/inter/600.css">
<style>
@page {{ size: 841.89pt 595.276pt; margin: 0; }}
html, body {{ margin: 0; padding: 0; }}
body {{ font-family: "Noto Sans SC", sans-serif; color: #111; }}
.page {{ position: relative; width: 841.89pt; height: 595.276pt; overflow: hidden; page-break-after: always; background: #fff; }}
.page:last-child {{ page-break-after: auto; }}
.title {{ position: absolute; left: 16pt; top: 14pt; display: flex; align-items: flex-end; gap: 8pt; font-size: 16pt; font-weight: 500; }}
.grid {{ position: absolute; left: 16pt; right: 16pt; top: 44pt; display: grid; grid-template-columns: 1fr 1fr; }}
.cell {{ display: flex; align-items: center; }}
.ct {{ flex: 1; padding-bottom: 24pt; }}
.cn {{ font-size: 15pt; font-weight: 500; margin-bottom: 4pt; }}
.cn b {{ font: 600 15pt Inter, sans-serif; margin-right: 4pt; }}
.cs {{ font-size: 9pt; color: #333; line-height: 1.6; padding-right: 10pt; }}
.pair {{ position: absolute; left: 18pt; right: 18pt; top: 40pt; display: flex; justify-content: space-between; }}
.lab {{ text-align: center; font-size: 9pt; color: #666; margin-top: -6pt; }}
.pts {{ position: absolute; left: 34pt; right: 34pt; bottom: 18pt; font-size: 9.4pt; line-height: 1.7; color: #222;
        border-top: .5pt solid #ccc; padding-top: 8pt; }}
.note {{ position: absolute; left: 32pt; bottom: 18pt; font-size: 8.6pt; color: #444; }}
</style></head><body>
<section class="page">
  <div class="title">{wordmark_svg(14)}<span>单板雪鞋 · 四个方向</span></div>
  <div class="grid">{over}</div>
  <div class="note">都照 Vamei TP 的画法；大底、中底、内胆、BOA、魔术贴沿用双扣 TP 的形状，开发只动鞋面。挑一个方向我再往下深化。</div>
</section>
{pages}
</body></html>'''
open(sys.argv[3], 'w').write(html)
