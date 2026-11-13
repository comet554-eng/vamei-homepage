"""提案 06「护甲」：参考 Vamei 实物的设计语言——外层护甲侧片挖出大窗口、露出另一色的网布内靴，
BOA 钢丝在窗口里交叉；双 BOA（小腿前一个、侧片上一个，侧片压一块盾形凸起框住旋钮）；
护甲外沿一圈加厚包边 + 装饰打结线；织带拉片、织唛标签、同色模压浮雕线、鞋头后跟包胶。
倒角用 RAILLOK 标志的斜角。TP 坐标，鞋头朝左。
usage: armor6.py tp.json mono.json word.json outdir"""
import sys, math
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
from tpkit import Kit, Sheet, spline, rounded, strip, palette, dark_palette, D, ld

K = Kit(*sys.argv[1:4])
OUT = sys.argv[4]

# 护甲前沿：从领口直下，脚踝处斜切一刀（标志的斜角），再顺着脚背扫到鞋头
FRONT = [(292, 96), (292, 140), (294, 214), (272, 244), (268, 292), (252, 320), (214, 342), (164, 360), (120, 374), (84, 384), (40, 396)]
# 上侧片的下沿：从脚踝前斜切处往后扫到后跟杯上方
LOWER = [(260, 300), (292, 330), (330, 346), (372, 348), (410, 338), (470, 326)]
COLLAR = [(228, 60), (228, 134), (262, 139), (300, 141), (338, 138), (370, 128), (393, 116), (430, 104), (430, 60)]

def armor_parts():
    k = K
    fl = LineString(spline(FRONT, steps=14))
    armor = k.clip(Polygon(list(fl.coords) + [(20, 400), (20, 560), (480, 560), (480, 60), (274, 60)]).buffer(0), 2.0)
    # 包边：沿护甲前沿和领口的一圈宽边
    up = rounded(armor.intersection(Polygon(spline(LOWER, steps=14) + [(470, 0), (240, 0)]).buffer(0)), 1.6)
    frame = rounded(up.difference(up.buffer(-9, join_style=1)), 0.6)       # 一整圈包边，框住上侧片
    inner = up.buffer(-9, join_style=1)
    lower = armor.difference(up)
    return fl, armor, frame, inner, lower

def dial_face(s, cx, cy, r, C):
    """侧片上的旋钮（正面看）：齿圈 + 盖 + 图形标"""
    s.add(f'<circle cx="{cx + 1.2}" cy="{cy + 1.4}" r="{r + .5}" fill="{C["shadow"]}"/>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{C["dial_ring"]}" stroke="{C["line"]}" stroke-width=".6"/>')
    for j in range(40):
        a = 2 * math.pi * j / 40
        s.add(f'<line x1="{cx + (r - 2.6) * math.cos(a):.2f}" y1="{cy + (r - 2.6) * math.sin(a):.2f}" '
              f'x2="{cx + (r - .4) * math.cos(a):.2f}" y2="{cy + (r - .4) * math.sin(a):.2f}" stroke="{C["line"]}" stroke-width=".3"/>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{r - 3.4}" fill="{C["dial_cap"]}" stroke="{C["line"]}" stroke-width=".5"/>')
    s.mono(cx, cy, (r - 3.4) * 1.1, C['dial_mark'])

def guide(s, x, y, ang, C):
    g = affinity.rotate(rounded(box(x - 4.4, y - 2.2, x + 4.4, y + 2.2), 2.0), ang, origin=(x, y))
    s.add(f'<path d="{D(g)}" fill="{C["guide"]}" stroke="{C["line"]}" stroke-width=".4"/>')

def armor(C, uid):
    s = Sheet(K, C, uid); k = K
    s.begin()
    fl, arm, frame, inner, lower = armor_parts()
    # 内靴：鞋面底色就是内靴色；上段光面、下段网布
    s.add(f'<path d="{D(k.sil)}" fill="url(#{s.u("hexmesh")})"/>')
    top_smooth = k.clip(Polygon(spline([(160, 214), (196, 238), (236, 240), (268, 222), (296, 196)], steps=12) + [(296, 60), (160, 60)]).buffer(0), 1.2)
    s.panel(top_smooth, C['inner_top'], stitch=(1.6, 3.0), shadow=False)
    # 钢丝：两根，在窗口里交叉；先画，护甲盖在钢丝的一头上
    A = [(286, 158), (284, 202), (270, 252), (262, 290), (240, 322)]
    F = [(200, 182), (206, 226), (212, 268), (216, 304), (196, 336)]
    c1 = [(204, 196), F[0], A[1], F[2], A[3], F[4]]       # 从前旋钮出来
    c2 = [(206, 202), A[0], F[1], A[2], F[3]]
    for c in (c1, c2):
        s.add(f'<path d="{ld(c)}" fill="none" stroke="{C["cable"]}" stroke-width="1.25" stroke-linejoin="round"/>')
        s.add(f'<path d="{ld(c)}" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width=".45" stroke-dasharray="1 .9"/>')
    # 护甲 + 包边
    s.panel(arm, C['armor'], stitch=(), shadow=True)
    s.panel(lower, C['armor'], stitch=(1.6,), shadow=False)
    s.panel(inner, C['armor'], stitch=(1.6,), shadow=False)
    # 护甲上的模压浮雕线（同色，顺着前沿）
    ll = LineString(spline(LOWER, steps=14))
    for off in (14, 26, -14, -26):
        rl = ll.offset_curve(off)
        seg = rl.intersection(lower.buffer(-4))
        for g in getattr(seg, 'geoms', [seg]):
            if g.geom_type == 'LineString' and g.length > 20:
                pts = list(g.coords)
                s.add(f'<path d="{ld(pts)}" fill="none" stroke="{C["relief_hi"]}" stroke-width="1.6" transform="translate(-.6 -.7)"/>')
                s.add(f'<path d="{ld(pts)}" fill="none" stroke="{C["relief_lo"]}" stroke-width=".8" transform="translate(.5 .6)"/>')
    # 下半截两道轮廓缝：一道顺着窗口下沿，一道沿中底上方
    s.seam(list(fl.offset_curve(-22).coords)[int(len(fl.coords) * .45):])
    s.seam(spline([(126, 430), (180, 438), (250, 442), (320, 440), (366, 432)], steps=12))
    s.panel(frame, C['frame'], stitch=(1.4, 6.0), shadow=False)
    # 包边上的装饰打结线
    for t in (0.12, 0.2, 0.3, 0.46, 0.58, 0.7):
        p = fl.interpolate(t, normalized=True); q = fl.interpolate(t + 0.01, normalized=True)
        a = math.atan2(q.y - p.y, q.x - p.x); nx, ny = -math.sin(a), math.cos(a)
        cx, cy = p.x - nx * 4.6, p.y - ny * 4.6
        if not Point(cx, cy).within(frame): cx, cy = p.x + nx * 4.6, p.y + ny * 4.6
        s.add(f'<line x1="{cx - math.cos(a) * 2.6:.2f}" y1="{cy - math.sin(a) * 2.6:.2f}" x2="{cx + math.cos(a) * 2.6:.2f}" '
              f'y2="{cy + math.sin(a) * 2.6:.2f}" stroke="{C["tack"]}" stroke-width="1.1" stroke-linecap="round"/>')
    # 导向扣（护甲前沿一排、前面一排）
    for (x, y) in A[:4]:
        guide(s, x, y, 70, C)
    for (x, y) in F[1:]:
        guide(s, x, y, 80, C)
    # 织带拉片：护甲前沿一个织带环，挂一片布拉手
    loop = affinity.rotate(rounded(box(258, 272, 280, 281), 1.2), -20, origin=(269, 276))
    s.panel(loop, C['web'], 'web', stitch=(1.0,), shadow=True, lw=.5)
    tab = Polygon([(238, 290), (254, 279), (258, 286), (244, 298)])
    s.panel(rounded(tab, 1.2), C['web'], stitch=(), shadow=True, lw=.5)
    # 侧片盾形凸起 + 旋钮
    shield = rounded(Polygon([(318, 152), (368, 146), (378, 184), (362, 218), (330, 222), (312, 192)]), 3)
    s.panel(shield, C['armor'], stitch=(1.6,), shadow=True)
    s.add(f'<path d="{D(shield.buffer(-5, join_style=1))}" fill="none" stroke="{C["relief_lo"]}" stroke-width=".7"/>')
    dial_face(s, 345, 185, 14, C)
    # 织唛标签
    lab_c = (306, 262)
    lab = affinity.rotate(rounded(box(lab_c[0] - 16, lab_c[1] - 5, lab_c[0] + 16, lab_c[1] + 5), 1), -70, origin=lab_c)
    s.panel(lab, C['label'], stitch=(), shadow=True, lw=.5)
    s.wordmark(lab_c[0], lab_c[1], 3.6, C['label_mark'], rot=-70)
    # 后跟杯
    heel = k.clip(Polygon(spline([(470, 470), (360, 470), (362, 432), (372, 392), (390, 352), (470, 338)], steps=14)).buffer(0))
    s.panel(heel, C['heel'], 'crackle')
    s.mono(410, 400, 11, C['heel_mark'])
    # 领口软垫
    s.panel(k.clip(Polygon(spline(COLLAR, steps=14)).buffer(0)).difference(Polygon(list(fl.coords) + [(20, 400), (20, 0)]).buffer(0)),
            C['collar'], stitch=(2.0,))
    # 鞋头：缝线 + 包胶
    toe = k.clip(Polygon(spline([(20, 376), (70, 382), (104, 394), (122, 418), (128, 452), (128, 520)], steps=14) + [(20, 520)]).buffer(0))
    s.panel(toe, C['armor'], stitch=(1.5, 3.0))
    bumper_t = k.clip(Polygon(spline([(20, 412), (52, 420), (88, 432), (112, 446), (124, 470)], steps=12) + [(124, 520), (20, 520)]).buffer(0), 1.2)
    bumper_h = k.clip(Polygon(spline([(370, 470), (384, 446), (410, 432), (470, 426)], steps=12) + [(470, 520), (370, 520)]).buffer(0), 1.2)
    s.panel(bumper_t, C['rubber'], stitch=(), shadow=False)
    s.panel(bumper_h, C['rubber'], stitch=(), shadow=False)
    s.finish('line')
    return s

WHITE = dict(armor='#FFFFFF', frame='#FFFFFF', inner_top='#FFFFFF', heel='#FFFFFF', collar='#FFFFFF', web='#FFFFFF',
             label='#111111', label_mark='#FFFFFF', guide='#FFFFFF', cable='#555555', tack='#111111', rubber='#FFFFFF',
             dial_ring='#FFFFFF', dial_cap='#FFFFFF', dial_mark='#111111', heel_mark='#111111',
             relief_hi='#FFFFFF', relief_lo='#BDBDBD')

def cw(fn, **kw):
    d = dict(WHITE); d.update(kw)
    return fn(**d)

COLORWAYS = {
    'tp':    palette(**WHITE),
    # 鼠尾草：浅绿护甲 + 骨白包边 + 深绿内靴 / 后跟 / 包胶（对照 Vamei 浅紫那双）
    'sage':  cw(palette, base='#8CA394', inner_top='#8CA394', armor='#D6E4D8', frame='#F3F2EE', heel='#8CA394', collar='#8CA394',
                web='#8CA394', label='#5F7568', label_mark='#F3F2EE', guide='#F7F7F5', cable='#6B6F70', tack='#8CA394',
                rubber='#7F968A', dial_ring='#C9C4B6', dial_cap='#F7F7F5', dial_mark='#8CA394', heel_mark='#F3F2EE',
                relief_hi='rgba(255,255,255,.7)', relief_lo='rgba(0,0,0,.14)', loop='#8CA394', liner='#7F968A',
                strap='#8CA394', mid='#F3F2EE', out='#7F968A', boa='#F7F7F5', boa_dark='#C9C4B6',
                tex='rgba(255,255,255,.08)', meshline='rgba(255,255,255,.22)', webline='rgba(255,255,255,.25)',
                stitch='rgba(0,0,0,.35)', shadow='rgba(0,0,0,.14)', line='#2B2E30', hole='#5F7568'),
    # 岩灰：浅灰护甲（包边同色，靠浮雕）+ 岩灰内靴 / 后跟 / 包胶（对照 Vamei 浅灰那双）
    'slate': cw(palette, base='#68747A', inner_top='#7C878D', armor='#DADDDE', frame='#E6E8E8', heel='#68747A', collar='#68747A',
                web='#E6E8E8', label='#68747A', label_mark='#F3F2EE', guide='#F7F7F5', cable='#8A8F92', tack='#9CA3A7',
                rubber='#68747A', dial_ring='#B9BDC0', dial_cap='#F7F7F5', dial_mark='#68747A', heel_mark='#DADDDE',
                relief_hi='rgba(255,255,255,.8)', relief_lo='rgba(0,0,0,.14)', loop='#68747A', liner='#E6E8E8',
                strap='#DADDDE', mid='#F3F2EE', out='#68747A', boa='#F7F7F5', boa_dark='#B9BDC0',
                tex='rgba(255,255,255,.08)', meshline='rgba(255,255,255,.2)', webline='rgba(0,0,0,.08)',
                stitch='rgba(0,0,0,.32)', shadow='rgba(0,0,0,.14)', line='#2B2E30', hole='#68747A'),
    # 骨白：骨白护甲 + 骨白包边 + 鼠尾草绿内靴 / 后跟 / 包胶
    'bone':  cw(palette, base='#C2D8C5', inner_top='#C2D8C5', armor='#F3F2EE', frame='#E9E7E0', heel='#C2D8C5', collar='#C2D8C5',
                web='#C2D8C5', label='#151617', label_mark='#C2D8C5', guide='#FFFFFF', cable='#7A7F80', tack='#9DB6A1',
                rubber='#9DB6A1', dial_ring='#C9C4B6', dial_cap='#FFFFFF', dial_mark='#151617', heel_mark='#F3F2EE',
                relief_hi='rgba(255,255,255,.9)', relief_lo='rgba(0,0,0,.12)', loop='#C2D8C5', liner='#F3F2EE',
                strap='#C2D8C5', mid='#F3F2EE', out='#9DB6A1', boa='#FFFFFF', boa_dark='#C9C4B6',
                tex='rgba(0,0,0,.06)', meshline='rgba(255,255,255,.35)', webline='rgba(0,0,0,.08)',
                stitch='rgba(0,0,0,.32)', shadow='rgba(0,0,0,.12)', line='#2B2E30', hole='#9DB6A1'),
    # 曜黑：黑护甲 + 岩灰包边 + 鼠尾草绿内靴
    'black': cw(dark_palette, base='#9DB6A1', inner_top='#9DB6A1', armor='#232527', frame='#68747A', heel='#151617', collar='#151617',
                web='#C2D8C5', label='#C2D8C5', label_mark='#151617', guide='#E6E8E8', cable='#B9BDC0', tack='#C2D8C5',
                rubber='#151617', dial_ring='#68747A', dial_cap='#232527', dial_mark='#C2D8C5', heel_mark='#C2D8C5',
                relief_hi='rgba(255,255,255,.12)', relief_lo='rgba(0,0,0,.5)', loop='#C2D8C5', mid='#F3F2EE',
                meshline='rgba(0,0,0,.18)', webline='rgba(0,0,0,.1)'),
}

if __name__ == '__main__':
    for name, C in COLORWAYS.items():
        open(f'{OUT}/a6-{name}.svg', 'w').write(armor(C, f'a6{name}').svg())
        print('ok', name)
