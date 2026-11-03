"""白灰配色：根据 TP 线稿的绘制顺序（walk.py 的输出）生成 recolor.py 用的换色表。
usage: spec.py tp.json spec.json

部件编号是 TP 稿内容流里的绘制序号（P:<序号>，表单里的写成 P//FmN:<序号>），
对照黑灰稿逐块确认过：黑灰稿里是灰的面，这里同样是灰；黑灰稿里是黑的面，这里换成米白。"""
import json, sys

tp = json.load(open(sys.argv[1]))

CD = [0.941, 0.933, 0.914]      # PANTONE 11-4201 TPG Cloud Dancer 米白
QS = [0.537, 0.537, 0.537]      # PANTONE 18-4006 TPG Quiet Shade，沿用黑灰稿中间面的显示灰度
QS_DARK = [0.447, 0.443, 0.443] # 黑灰稿里鞋舌旁织网用的深一点的灰
QS_LIGHT = [0.66, 0.66, 0.66]   # 提拉环内侧（受光面）
TRI = [0.349, 0.341, 0.341]     # 圆标三角，和黑灰稿一致
SHADOW = [0.30, 0.30, 0.30]     # 地面投影，灰色大底下用纯黑太重

parts = {
    # 中间面：上后片、大中间片、下中间片、底部窄条
    'mid_panel':     (QS, ['P:782', 'P:815', 'P:1089', 'P:1735']),
    'liner':         (QS, ['P:623', 'P:676', 'P:712', 'P:739']),       # 内里领口（网布纹理叠在上面）
    'strap':         (QS, ['P:1758']),                                  # 魔术贴织带
    'pull_loop_out': (QS, ['P:596']),
    'pull_loop_in':  (QS_LIGHT, ['P:651']),
    'outsole':       (QS, ['P:2163']),                                  # 大底齿纹
    'logo_text':     (CD, ['P:1624', 'P:1633', 'P:1665', 'P:1686', 'P:1701', 'P:1716']),
    'badge_tri':     (TRI, ['P:2720']),
    'heel_tri':      (QS, ['P:2493']),
    'heel_wave':     (CD, ['P:2516']),
    'heel_tabs':     (QS, ['P:2416', 'P:2448']),
    'lace_window':   (QS_DARK, ['P:1201']),                             # 鞋舌旁织网窗
    'shadow':        (SHADOW, ['P//Fm0:10']),
}
fill = {i: color for color, ids in parts.values() for i in ids}

# 大图上其余白色 / 近白的面（鞋带区、侧片、鞋头、后跟、中底、BOA、鞋带、透气孔……）一律米白
for d in tp:
    if d['op'] not in ('f', 'f*', 'B', 'B*', 'b', 'b*') or not d.get('bbox'):
        continue
    if d['bbox'][2] > 463:  # 只动左边大图
        continue
    kind, val = d['fill']
    white = (kind == 'rg' and min(val) >= 0.98) or (kind == 'g' and val[0] >= 0.98)
    if white and d['id'] not in fill:
        fill[d['id']] = CD

# 去掉右侧的小图、红框、修改说明，以及左下角那句白色提示（换成右栏里的说明）
drop = []
for d in tp:
    if d['op'] in ('f', 'f*', 'B', 'B*', 'b', 'b*', 'S', 's') and d.get('bbox') \
            and d['bbox'][0] >= 463 and d['id'] != 'P:5':
        drop.append(d['id'])
    if d['op'] == 'Do' and '/' not in d['id'] and d['name'] in ['/Fm%d' % k for k in range(14, 28)]:
        drop.append(d['id'])
drop += ['P:5521', 'P:5537', 'P:5539', 'P:5541', 'P:5544', 'P:5546']

json.dump({'fill': fill, 'drop': drop, 'strip_pieceinfo': True}, open(sys.argv[2], 'w'), indent=1)
print(f'{len(fill)} fills, {len(drop)} drops')
