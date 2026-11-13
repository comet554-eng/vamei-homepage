"""提案 09 结构草图排版：第 1 页外侧结构总览，第 2 页双扣系统（外侧走线 + 正面），第 3 页分层爆炸 + 脚踝剖面。
usage: sheet9.py build_dir word.json out.html"""
import json, sys
from shapely.ops import unary_union
from geom import to_poly

B = sys.argv[1]
word = json.load(open(sys.argv[2]))

def svg(name, width_pt):
    s = open(f'{B}/s9-{name}.svg').read()
    import re
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    h = width_pt * vb[3] / vb[2]
    s = re.sub(r'width="[\d.]+" height="[\d.]+"', f'width="{width_pt}pt" height="{h:.1f}pt"', s, count=1)
    # 每张图的滤镜 id 加前缀
    return s.replace('id="rough1"', f'id="rough1-{name}"').replace('id="rough2"', f'id="rough2-{name}"') \
            .replace('url(#rough1)', f'url(#rough1-{name})').replace('url(#rough2)', f'url(#rough2-{name})')

def wordmark_svg(h, color='#111'):
    letters = [w for w in word if w['id'] in ('P:77', 'P:91', 'P:94', 'P:106', 'P:119', 'P:141', 'P:158')]
    b = unary_union([to_poly(w['d']) for w in letters]).bounds
    w_ = (b[2] - b[0]) / (b[3] - b[1]) * h
    return (f'<svg width="{w_:.2f}pt" height="{h}pt" viewBox="{b[0]:.2f} {b[1]:.2f} {b[2] - b[0]:.2f} {b[3] - b[1]:.2f}">'
            + ''.join(f'<path d="{w["d"]}" fill="{color}"/>' for w in letters) + '</svg>')

P1 = [
    ('RAIL 护条', 'TPU 模压一体件：鞋头包头 → 防泥条 → 后跟杯外壳 → 外侧上升段 → 侧旋钮底座。整只鞋的骨架：抗扭、给侧旋钮当底座、给锁跟织带当锚点'),
    ('侧旋钮 · ATOP 原厂', '管上区 + 锁跟，装在 RAIL 末端的底座上，拉力直接传进 RAIL，不靠面料吃力'),
    ('前旋钮 · ATOP 原厂', '管下区（前脚掌 + 脚背），位置同双扣 TP'),
    ('鞋带区护片', '导向扣缝在护片上，钢丝的拉力分散到整片，不拉坏鞋面'),
    ('鞋舌', '硬鞋舌，脚踝前三道弯折槽，前倾时不顶脚背'),
    ('外侧大身', '一整片；沿 RAIL 内侧一道回声缝，中间一道横缝分上下两片（上软下挺）'),
    ('领口软垫', '上口一圈，和内胆分开做，包住小腿'),
    ('后背脊条 + 弯折缺口', '脊条撑住后倾，缺口让前倾顺一点'),
    ('魔术贴', 'power strap，沿用 TP'),
    ('内胆 · 提拉环', '沿用 TP 形状，可热塑'),
    ('中底 · 大底', '沿用双扣模具'),
    ('内部后跟杯 · 鞋头内衬', '虚线：藏在面料里的硬件，和 RAIL 外壳一起把后跟包死'),
]
p1 = ''.join(f'<div class="lg"><span class="n">{i + 1}</span><b>{t}</b>　{d}</div>' for i, (t, d) in enumerate(P1))

P2 = [
    ('<i class="sw b"></i>下区 · 前旋钮', '钢丝从前旋钮沿鞋带区往下，在护片导向扣和鞋舌之间来回，收前脚掌和脚背。'),
    ('<i class="sw r"></i>上区 · 侧旋钮', '侧旋钮往前出两根钢丝，绕过小腿上段（两个导向扣），收鞋筒。'),
    ('<i class="sw o"></i>锁跟 · 侧旋钮', '同一个侧旋钮再拉一根钢丝到脚背的锁跟环；锁跟织带从后跟两侧（锚在 RAIL 上）斜着上来，在脚背 V 形交汇。拧紧时织带把脚跟往后、往下压进后跟杯。'),
    ('为什么这么分', '前旋钮只管脚掌的包裹，侧旋钮管小腿和脚跟：滑行时最要紧的是脚跟不浮起来，所以锁跟和上区放在同一个旋钮上，一拧到位。'),
    ('名字的由来', 'RAIL（护条）是骨架，LOK（锁跟）挂在骨架上，侧旋钮就坐在 RAIL 的末端。'),
]
p2 = ''.join(f'<div class="lg2"><b>{t}</b><br>{d}</div>' for t, d in P2)

L3 = ['① 外层鞋面分片', '② RAIL 护条（TPU 一体）', '③ 锁跟织带 · 钢丝 · 双旋钮', '④ 内部后跟杯 · 鞋头内衬', '⑤ 内胆 · 鞋垫 · 中底大底']
l3 = ''.join(f'<div>{t}</div>' for t in L3)
P3 = [
    ('从外到里五层', '外层面料只管外观和防水，受力的都在 ② ③ ④：RAIL 和内部后跟杯一里一外夹住后跟，锁跟织带锚在 RAIL 上。'),
    ('脚踝剖面', '锁跟织带从后跟两侧绕到脚背，在鞋舌上方交汇；侧旋钮一拉，织带收紧成一圈，把脚跟往后压（橙色箭头）。'),
    ('打样时要定的', 'RAIL 的 TPU 硬度；锁跟织带宽度和锚点位置；侧旋钮底座和 RAIL 的连接方式（一体注塑还是车缝）；后背脊条是否做成可换硬度的插片。'),
]
p3 = ''.join(f'<div class="lg2"><b>{t}</b><br>{d}</div>' for t, d in P3)

head = lambda sub: f'<div class="title">{wordmark_svg(13)}<span>单板双扣雪鞋 · 结构草图 09 · {sub}</span></div>'
html = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>RAILLOK 雪鞋结构草图 09</title>
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/400.css">
<link rel="stylesheet" href="../node_modules/@fontsource/noto-sans-sc/500.css">
<link rel="stylesheet" href="../node_modules/@fontsource/inter/600.css">
<style>
@page {{ size: 841.89pt 595.276pt; margin: 0; }}
html, body {{ margin: 0; }}
body {{ font-family: "Noto Sans SC", sans-serif; color: #222; }}
.page {{ position: relative; width: 841.89pt; height: 595.276pt; overflow: hidden; background: #FBFAF6; page-break-after: always; }}
.page:last-child {{ page-break-after: auto; }}
.title {{ position: absolute; left: 20pt; top: 16pt; display: flex; align-items: flex-end; gap: 8pt; font-size: 14pt; font-weight: 500; }}
.nn {{ font: 600 7px Inter, sans-serif; }}
.lab {{ font: 400 9px "Noto Sans SC", sans-serif; fill: #555; }}
.panel {{ position: absolute; top: 44pt; right: 20pt; width: 300pt; }}
.lg {{ font-size: 8.2pt; line-height: 1.45; margin: 0 0 6pt 17pt; text-indent: -17pt; }}
.lg b {{ font-weight: 500; }}
.n {{ display: inline-block; width: 11pt; height: 11pt; border-radius: 50%; border: .9pt solid #2B4FA0; color: #2B4FA0; text-indent: 0;
      font: 600 6.6pt/11pt Inter, sans-serif; text-align: center; margin-right: 5pt; vertical-align: .5pt; box-sizing: border-box; line-height: 9.6pt; }}
.lg2 {{ font-size: 8.4pt; line-height: 1.55; margin-bottom: 9pt; }}
.lg2 b {{ font-weight: 500; font-size: 9pt; }}
.sw {{ display: inline-block; width: 14pt; height: 3pt; margin-right: 5pt; vertical-align: 2pt; }}
.sw.b {{ background: #2B63C6; }} .sw.r {{ background: #C8402A; }} .sw.o {{ background: #D98A1F; }}
.foot {{ position: absolute; left: 20pt; bottom: 12pt; font-size: 7.4pt; color: #777; }}
.labels {{ position: absolute; left: 22pt; right: 22pt; top: 266pt; display: flex; justify-content: space-between; font-size: 8.4pt; font-weight: 500; }}
.labels div {{ width: 150pt; }}
</style></head><body>

<section class="page">{head('外侧结构')}
  <div style="position:absolute;left:4pt;top:40pt">{svg('structure', 470)}</div>
  <div class="panel">{p1}</div>
  <div class="foot">铅笔草图，表达结构关系，不是生产图。两个旋钮都是 ATOP 原厂件，不印 logo。</div>
</section>

<section class="page">{head('双扣系统')}
  <div style="position:absolute;left:4pt;top:40pt">{svg('closure', 400)}</div>
  <div style="position:absolute;left:396pt;top:40pt">{svg('front', 150)}<div class="lab" style="text-align:center;font-size:8pt;color:#555">正面</div></div>
  <div class="panel" style="width:260pt">{p2}</div>
  <div class="foot">蓝 = 下区（前旋钮）　红 = 上区 + 锁跟（侧旋钮）　橙 = 锁跟织带　箭头 = 拧紧时脚跟的受力方向</div>
</section>

<section class="page">{head('分层 · 剖面')}
  <div style="position:absolute;left:20pt;top:44pt">{svg('layers', 800)}</div>
  <div class="labels">{l3}</div>
  <div style="position:absolute;left:30pt;top:292pt">{svg('section', 330)}</div>
  <div class="panel" style="top:304pt;width:380pt">{p3}</div>
  <div class="foot">脚踝剖面为俯视，上方是脚背、下方是脚跟。</div>
</section>
</body></html>'''
open(sys.argv[3], 'w').write(html)
