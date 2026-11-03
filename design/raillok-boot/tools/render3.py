"""RAILLOK 雪鞋 · 提案 03「一体 MONOLITH」：同色系、少接缝，靠材质和光影出层次。
usage: render3.py ref.json mono.json word.json colorway out.png [px_per_pt]

不再画平面色块：每个部件先算一张高度图（边缘倒角、领口软垫鼓起、缝线凹槽、
压印凹陷、包边台阶），再按灯光算明暗、高光和自阴影，做成接近 3D 渲染的质感。
坐标单位 pt，鞋头朝右（右脚外侧）；大底、中底形状来自 Vamei TP 稿（ref.json）。"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union
from geom import to_poly

ref = json.load(open(sys.argv[1]))
mono = json.load(open(sys.argv[2]))
word = json.load(open(sys.argv[3]))
CW = sys.argv[4]
OUT = sys.argv[5]
PX = float(sys.argv[6]) if len(sys.argv) > 6 else 5.0      # 每 pt 多少像素（渲染时再 2 倍超采样）
SS = 2
R = PX * SS                                                   # 渲染分辨率：px/pt
X0, Y0, W, H = 20, 40, 440, 480                               # 取景（鞋图坐标）
NX, NY = int(W * R), int(H * R)

# ---------------- 配色：同色系，只换材质 ----------------
COLORWAYS = {
    #            鞋面        领口软垫     包头/后跟   中底        大底        旋钮盖      金属圈      背景
    'bone':  dict(upper='#E7E3DA', collar='#DEDAD0', rand='#E2DDD2', mid='#EEEBE4', out='#8B877F',
                  cap='#E2DDD2', ring='#C8CACB', bg='#DEDCD6'),
    'black': dict(upper='#2A2B2E', collar='#222326', rand='#1F2023', mid='#242528', out='#18191B',
                  cap='#1F2023', ring='#7A7E83', bg='#ECEBE7'),
    'slate': dict(upper='#67737A', collar='#5F6A71', rand='#5B666C', mid='#E9E6DE', out='#2A2C2E',
                  cap='#5B666C', ring='#C8CACB', bg='#ECEBE7'),
    'sage':  dict(upper='#B9CDBC', collar='#AFC3B2', rand='#A9BEAD', mid='#EEEBE4', out='#5E6A64',
                  cap='#A9BEAD', ring='#C8CACB', bg='#ECEBE7'),
}
C = {k: np.array([int(v[i:i + 2], 16) / 255 for i in (1, 3, 5)]) for k, v in COLORWAYS[CW].items()}

# ---------------- 形 ----------------
def spline(pts, closed=True, steps=14):
    P = list(pts)
    P = ([P[-1]] + P + [P[0], P[1]]) if closed else ([P[0]] + P + [P[-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(steps):
            t = k / steps; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not closed: out.append(P[-2])
    return out

UPPER = [(84, 100), (100, 104), (125, 113), (165, 117), (215, 115), (248, 112), (262, 104), (272, 88), (286, 84),
         (297, 92), (296, 118), (294, 132), (281, 175), (269, 220), (259, 265), (253, 305), (255, 333), (270, 349), (300, 362),
         (340, 374), (380, 384), (410, 390), (428, 401), (436, 418), (435, 436), (420, 452), (330, 472),
         (200, 470), (90, 462), (48, 452), (46, 425), (50, 385), (58, 342), (67, 298), (73, 250), (77, 200), (80, 150)]
upper = Polygon(spline(UPPER)).buffer(0)
mid = to_poly(ref['mid'])
out = to_poly(ref['out'])

# 鞋带盖 / 鞋舌：沿鞋筒前缘到脚背的一条，同色；上端高出外壳，是有厚度的鞋舌
FRONT = [(268, 80), (286, 84), (297, 92), (296, 118), (294, 132), (281, 175), (269, 220), (259, 265),
         (253, 305), (255, 333), (270, 349), (300, 362), (340, 374), (378, 384)]
front_chain = LineString(spline(FRONT, closed=False))
cover = upper.intersection(front_chain.buffer(15, cap_style=2))
# 外壳上沿：比鞋口低一截，软内胆从里面冒出来
SHELL_TOP = spline([(40, 150), (82, 140), (120, 147), (170, 153), (220, 150), (252, 141), (275, 132), (300, 128)],
                   closed=False)
above_top = Polygon(SHELL_TOP + [(300, 0), (40, 0)]).buffer(0)
liner = upper.intersection(above_top).difference(cover)
shell = upper.difference(liner)
# 包头 + 后跟杯：一圈模压橡胶，前面包住鞋头，沿底边走，到后跟往上抬成后跟杯
RAND_EDGE = [(470, 372), (430, 384), (402, 392), (372, 410), (330, 430), (270, 441), (210, 442), (165, 436),
             (130, 420), (104, 394), (86, 358), (74, 318), (60, 290), (20, 280)]
rand = upper.intersection(Polygon(spline(RAND_EDGE, closed=False) + [(20, 600), (470, 600)]).buffer(0))

DIAL = (150, 222)        # 旋钮：鞋筒外侧、脚踝上方，嵌在一个凹槽里
TAB = Polygon(spline([(84, 112), (84, 88), (89, 72), (99, 70), (103, 84), (101, 112)])).buffer(0).difference(
    Polygon(spline([(89, 104), (89, 90), (92, 80), (97, 81), (97, 92), (96, 104)])).buffer(0))   # 后提拉环（织带）   # 后提拉片

# ---------------- 栅格工具 ----------------
def to_px(x, y):
    return ((x - X0) * R, (y - Y0) * R)

def mask(geom):
    im = Image.new('L', (NX, NY), 0)
    d = ImageDraw.Draw(im)
    for g in getattr(geom, 'geoms', [geom]):
        if g.is_empty: continue
        d.polygon([to_px(*p) for p in g.exterior.coords], fill=255)
        for r in g.interiors:
            d.polygon([to_px(*p) for p in r.coords], fill=0)
    return np.asarray(im, dtype=np.float32) / 255

def line_mask(pts_list, width_pt=0.4, dash=None):
    im = Image.new('L', (NX, NY), 0)
    d = ImageDraw.Draw(im)
    for pts in pts_list:
        if dash:
            ls = LineString(pts); on, off = dash; t = 0
            while t < ls.length:
                seg = [ls.interpolate(t), ls.interpolate(min(t + on, ls.length))]
                d.line([to_px(p.x, p.y) for p in seg], fill=255, width=max(1, int(width_pt * R)))
                t += on + off
        else:
            d.line([to_px(*p) for p in pts], fill=255, width=max(1, int(width_pt * R)), joint='curve')
    return np.asarray(im, dtype=np.float32) / 255

def dist_in(m):
    """到区域边缘的距离（pt），区域外为 0"""
    return ndi.distance_transform_edt(m > 0.5) / R

def bevel(d, r):
    """圆角倒边：边上 0，往里 r 之内按四分之一圆升到 1"""
    t = np.clip(d / r, 0, 1)
    return np.sqrt(1 - (1 - t) ** 2)

def blur(a, sigma_pt):
    return ndi.gaussian_filter(a, sigma_pt * R)

def blur_big(a, sigma_pt, k=8):
    """大半径模糊：先缩小再模糊再放大"""
    small = ndi.gaussian_filter(a[::k, ::k], sigma_pt * R / k)
    big = ndi.zoom(small, k, order=3)[:a.shape[0], :a.shape[1]]
    pad = ((0, a.shape[0] - big.shape[0]), (0, a.shape[1] - big.shape[1]))
    return np.pad(big, pad, mode='edge')

def boundary_lines(geom, inset=0.0):
    g = geom.buffer(-inset, join_style=1) if inset else geom
    out = []
    for p in getattr(g, 'geoms', [g]):
        if p.is_empty: continue
        out.append(list(p.exterior.coords))
        out += [list(r.coords) for r in p.interiors]
    return out

def inner_edge(region, other, inset):
    """region 和 other 交界的那一段边，往 region 里缩 inset —— 用来画缝线"""
    e = region.buffer(-inset, join_style=1).boundary.intersection(other.buffer(inset + 1.2))
    return [list(g.coords) for g in getattr(e, 'geoms', [e]) if g.geom_type == 'LineString' and g.length > 1]

# ---------------- 高度图（单位 pt） ----------------
M_up = mask(upper); M_cov = mask(cover); M_rand = mask(rand)
yy, xx = np.mgrid[0:NY, 0:NX].astype(np.float32)
M_mid = mask(mid); M_out = mask(out); M_tab = mask(TAB)
d_up = dist_in(M_up)

M_sh = mask(shell); M_lin = mask(liner)
pillow = blur_big(M_up, 20)
h = np.zeros((NY, NX), np.float32)
# 外壳：边缘圆倒角（上沿是一圈翻边）+ 整体鼓起
h += M_sh * (5.0 * bevel(dist_in(M_sh), 9) + 26.0 * pillow)
# 内胆领口：比外壳低一截，再自己鼓起来（软垫）
h += M_lin * (22.0 * pillow + 4.5 * bevel(dist_in(M_lin), 7))
# 腰线：从脚背走到旋钮的一道雕刻折线，上沿受光、下沿落影（同色，不拼接）——「轨」引向「锁」
CHAR = spline([(402, 391), (340, 388), (276, 366), (222, 322), (186, 276), (163, 241)], closed=False, steps=20)
m_line = line_mask([CHAR], 0.3)
d_line = ndi.distance_transform_edt(m_line < 0.5) / R
above = mask(Polygon(CHAR + [(163, 0), (480, 0), (480, 391)]).buffer(0))
s_d = np.where(above > 0.5, d_line, -d_line)                     # 线上方为正
fade = np.clip(1 - np.hypot(*[(a - b) for a, b in zip(np.mgrid[0:NY, 0:NX][::-1], to_px(*CHAR[-1]))]) / R / 30, 0, 1) ** 1.5   # 末端 30pt 内慢慢收细
crease = np.where(s_d >= 0, np.exp(-np.clip(s_d, 0, 50) / 7.0), np.exp(np.clip(s_d, -50, 0) / 0.45))
h += M_up * (1 - M_rand) * 1.6 * crease * (1 - fade)
# 鞋带盖：比外壳高一点点，边缘小倒角；上端鞋舌更厚
d_cov = dist_in(M_cov)
tongue_w = np.clip((to_px(0, 160)[1] - yy) / (25 * R), 0, 1)       # 越往上越厚
h += M_cov * (1.2 * bevel(d_cov, 1.6) + 4.5 * tongue_w * bevel(d_cov, 7))
# 脚踝前面的弯折纹：鞋带盖上几道横向浅槽
flex = []
for yv in (288, 302, 316):
    q = min((front_chain.interpolate(t, normalized=True) for t in np.linspace(0, 1, 400)), key=lambda p: abs(p.y - yv))
    t0 = front_chain.project(q); a_ = front_chain.interpolate(t0 - 1); b_ = front_chain.interpolate(t0 + 1)
    tx, ty = b_.x - a_.x, b_.y - a_.y; nrm = math.hypot(tx, ty); nx_, ny_ = -ty / nrm, tx / nrm
    flex.append([(q.x - nx_ * 17, q.y - ny_ * 17), (q.x + nx_ * 17, q.y + ny_ * 17)])
h -= M_cov * 1.4 * blur(line_mask(flex, 0.8), 0.7)
# 鞋带导向扣：鞋带盖前缘的几个小凸起
for t in (0.17, 0.29, 0.41, 0.53, 0.83, 0.93):
    q = front_chain.interpolate(t, normalized=True)
    t0 = front_chain.project(q); a_ = front_chain.interpolate(t0 - 1); b_ = front_chain.interpolate(t0 + 1)
    tx, ty = b_.x - a_.x, b_.y - a_.y; nrm = math.hypot(tx, ty); nx_, ny_ = -ty / nrm, tx / nrm
    gx_, gy_ = to_px(q.x - nx_ * 5, q.y - ny_ * 5)
    rg = np.hypot(xx - gx_, yy - gy_) / R
    h += M_cov * 1.4 * np.sqrt(np.clip(1 - (rg / 2.6) ** 2, 0, 1))
# 包头 / 后跟杯：模压橡胶一层台阶
h += M_rand * 1.5 * bevel(dist_in(M_rand), 1.0)

# 缝线凹槽 + 明线
seam = line_mask(inner_edge(cover, upper.difference(cover), 0), 0.35)
h -= 0.7 * blur(seam, 0.35)
stitch = line_mask(inner_edge(cover, shell, 1.9) + inner_edge(shell, liner, 2.4)
                   + inner_edge(liner, upper.difference(upper.buffer(-0.01)).buffer(1), 2.6), 0.45, dash=(1.5, 0.9))
h -= 0.35 * blur(stitch, 0.18)
stitch2 = line_mask(boundary_lines(TAB, 1.6), 0.4, dash=(1.3, 0.8))

# 旋钮凹槽 + 旋钮
px_, py_ = to_px(*DIAL)
rr = np.hypot(xx - px_, yy - py_) / R
th = np.arctan2(yy - py_, xx - px_)
POCKET, DR = 17.5, 12.5
h -= M_up * 1.4 * np.clip((POCKET - rr) / 1.6, 0, 1)                      # 凹槽
dome = np.clip(1 - (rr / DR) ** 2, 0, 1)
h += np.where(rr < DR, 3.4 + 1.6 * np.sqrt(dome), 0)                         # 旋钮
ring = (rr > DR - 2.6) & (rr < DR)
h += np.where(ring, 0.28 * np.cos(th * 56), 0)                               # 齿纹
h += np.where((rr > DR - 3.0) & (rr < DR - 2.6), -0.6, 0)                   # 盖和圈之间的缝

# 压印：后跟杯上的图形标，旋钮盖上的图形标
def mono_mask(cx, cy, hpt):
    mb = to_poly(mono[1]['d'], evenodd=True).union(to_poly(mono[2]['d']))
    b = mb.bounds; s = hpt / (b[3] - b[1])
    from shapely import affinity
    g = affinity.translate(affinity.scale(mb, s, s, origin=((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)),
                           cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2)
    return mask(g)
m_heel = mono_mask(96, 392, 15)
h -= 0.55 * blur(m_heel, 0.25)
m_cap = mono_mask(DIAL[0], DIAL[1], 10.5)
h -= 0.45 * blur(m_cap, 0.2)

# 后提拉片（在鞋面后面，单独一层）
h_tab = M_tab * (2.0 * bevel(dist_in(M_tab), 1.5)) - 0.3 * blur(stitch2, 0.15)

# 中底、大底
h_mid = M_mid * (4.0 * bevel(dist_in(M_mid), 4.5))
h_out = M_out * (3.0 * bevel(dist_in(M_out), 1.5))

# ---------------- 光照 ----------------
L = np.array([-0.42, -0.58, 0.70]); L /= np.linalg.norm(L)
V = np.array([0, 0, 1.0]); Hh = (L + V) / np.linalg.norm(L + V)
L2 = np.array([0.75, -0.35, 0.35]); L2 /= np.linalg.norm(L2)          # 轮廓光：从右后上方来
H2 = (L2 + V) / np.linalg.norm(L2 + V)

def normals(hm):
    hm = blur(hm, 0.12)                 # 去掉栅格边缘的台阶纹
    gy, gx = np.gradient(hm * R)        # 高度 pt -> px，再对 px 求导（等于对 pt 求导）
    n = np.dstack([-gx, -gy, np.ones_like(hm)])
    return n / np.linalg.norm(n, axis=2, keepdims=True)

def self_shadow(hm, reach_pt=4.0):
    """沿光的方向往回看（最远 reach_pt），被挡住就算阴影，再柔化一下"""
    lxy = math.hypot(L[0], L[1]); tan_e = L[2] / lxy
    sh = np.zeros_like(hm)
    n = int(reach_pt * R)
    for k in range(1, n + 1, max(1, n // 16)):
        dx, dy = int(round(L[0] / lxy * k)), int(round(L[1] / lxy * k))   # 朝光源方向的偏移
        shifted = np.roll(hm, (-dy, -dx), axis=(0, 1))
        sh = np.maximum(sh, shifted - hm - (k / R) * tan_e)
    return blur(np.clip(sh / 0.8, 0, 1), 0.5)

def shade(hm, albedo, ks, shin, amb=0.30, kd=0.86, shadows=True):
    n = normals(hm)
    ndl = np.clip(n @ L, 0, 1)
    ndh = np.clip(n @ Hh, 0, 1)
    shadow = self_shadow(hm) if shadows else 0
    cavity = np.clip((blur(hm, 2.5) - hm) * 0.9, 0, 0.6)     # 凹处暗一点（环境光遮蔽）
    rim = np.clip(n @ L2, 0, 1) ** 2.5
    softbox = np.exp(-((n[..., 0] - 0.30) / 0.10) ** 2) * np.exp(-((n[..., 1] + 0.05) / 0.45) ** 2)   # 影棚柔光箱的竖条反光
    light = amb * (1 - cavity) + kd * ndl * (1 - 0.75 * shadow) + 0.22 * rim
    col = albedo * light[..., None] + (ks * ndh ** shin * (1 - shadow) + 0.6 * ks * np.clip(n @ H2, 0, 1) ** shin
                                       + 1.6 * ks * softbox)[..., None]
    return col

rng = np.random.default_rng(3)
def grain(sigma_px, amp):
    return 1 + amp * ndi.gaussian_filter(rng.standard_normal((NY, NX)).astype(np.float32), sigma_px) / (0.28 / max(sigma_px, .5))

def paint(m, color, tex=None):
    a = np.ones((NY, NX, 3), np.float32) * color
    if tex is not None: a *= tex[..., None]
    return a

nubuck = grain(0.7, 0.018) * grain(14, 0.006)
rubber = grain(1.2, 0.012)
foam = grain(1.0, 0.015)

# 鞋面层（鞋面 + 盖 + 领口 + 包头 + 旋钮）一起算光
alb = paint(M_up, C['upper'], nubuck)
alb = np.where(M_lin[..., None] > 0.5, paint(M_lin, C['collar'], grain(0.6, 0.05)), alb)
alb = np.where(M_rand[..., None] > 0.5, paint(M_rand, C['rand'], rubber), alb)
in_dial = (rr < DR)[..., None]
metal = C['ring'] * (0.85 + 0.15 * np.cos(th * 2 + 0.6))[..., None]  # 拉丝金属的明暗变化
alb = np.where(in_dial, np.where(((rr > DR - 2.6) & (rr < DR))[..., None], metal, C['cap']), alb)
ks = 0.05 * M_up + 0.10 * M_rand - 0.02 * M_lin
ks = np.where(rr < DR, np.where((rr > DR - 2.6), 0.55, 0.12), ks)
upper_rgb = shade(h, alb, ks, 14)

tab_rgb = shade(h_tab, paint(M_tab, C['upper'], nubuck), 0.05, 10, shadows=False)
mid_rgb = shade(h_mid, paint(M_mid, C['mid'], foam), 0.06, 12, amb=0.5, kd=0.62, shadows=False)
out_rgb = shade(h_out, paint(M_out, C['out'], rubber), 0.08, 16, shadows=False)

# ---------------- 合成（透明底，投影是半透明黑） ----------------
cx, cy = to_px(240, 498)
sh_ground = np.exp(-(((xx - cx) / (205 * R)) ** 2 + ((yy - cy) / (5.5 * R)) ** 2) * 2.2)
sh_ground = blur(sh_ground, 2.0)
contact = blur(M_out * (yy > to_px(0, 488)[1]), 1.2)
img = np.zeros((NY, NX, 3), np.float32)                  # 预乘颜色
alpha = np.clip(0.30 * sh_ground + 0.25 * contact, 0, 1)

def over(c, a, layer, m):
    return layer * m[..., None] + c * (1 - m[..., None]), m + a * (1 - m)

def aa(m):
    return np.clip(blur(m, 0.25), 0, 1)

img, alpha = over(img, alpha, tab_rgb, aa(M_tab))
img, alpha = over(img, alpha, out_rgb, aa(M_out))
img, alpha = over(img, alpha, upper_rgb, aa(M_up))
img *= (1 - 0.22 * blur(M_up, 1.0) * M_mid * (1 - M_up))[..., None]   # 鞋面压在中底上的接触阴影
img, alpha = over(img, alpha, mid_rgb, aa(M_mid))
img = np.where(alpha[..., None] > 1e-4, img / np.maximum(alpha, 1e-4)[..., None], 0)
img = np.clip(img, 0, 1) ** (1 / 1.05)
rgba = np.dstack([img, np.clip(alpha, 0, 1)])
im = Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA')
im = im.resize((int(NX / SS), int(NY / SS)), Image.LANCZOS)
im.save(OUT)
print('ok', CW, im.size)
