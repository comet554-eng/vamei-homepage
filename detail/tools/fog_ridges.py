# 晨雾山峦（品牌屏背景）：品牌米白天空 + 6 层水墨山脊，越近越深，山谷积雾
# 用法: python3 -I tools/fog_ridges.py assets/gen/fog-ridges.jpg
import sys
import numpy as np
from PIL import Image

W, H = 1500, 3000
rng = np.random.default_rng(7)

def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float) / 255

def noise1d(n, freq, seed):
    r = np.random.default_rng(seed)
    pts = r.random(int(freq) + 3)
    x = np.linspace(0, freq, n)
    i = x.astype(int); f = x - i
    f = f * f * (3 - 2 * f)
    return pts[i] * (1 - f) + pts[i + 1] * f

def ridge(n, seed, octaves=6, base=3.0):
    v = np.zeros(n); amp, tot = 1.0, 0.0
    for o in range(octaves):
        r = 1 - np.abs(noise1d(n, base * 2 ** o, seed * 31 + o) * 2 - 1)
        v += amp * r ** 1.25; tot += amp; amp *= 0.45
    return v / tot

cream, paper, warm = hexrgb('#EFEDDF'), hexrgb('#F6F4EC'), hexrgb('#E9DFD8')
ink, haze = hexrgb('#3E3C4C'), hexrgb('#C9C4CB')

y = np.linspace(0, 1, H)[:, None]
img = np.ones((H, W, 3)) * paper
# 天空：上方纸色，往地平线方向略暖
t = np.clip((y - 0.2) / 0.5, 0, 1)
img = img * (1 - t[..., None] * 0.55) + (cream * 0.6 + warm * 0.4) * t[..., None] * 0.55
# 一轮很淡的太阳 / 月亮
yy, xx = np.mgrid[0:H, 0:W]
d = np.hypot(xx - W * 0.68, yy - H * 0.555)
disc = np.clip((150 - d) / 3, 0, 1) * 0.35 + np.exp(-(d / 420) ** 2) * 0.12
img = img * (1 - disc[..., None]) + np.array([1.0, 0.97, 0.95]) * disc[..., None]

TOPS = [0.585, 0.625, 0.672, 0.735, 0.80, 0.875]   # 各层山脊基线（占高度比例），间距不等，近处拉开
layers = len(TOPS)
for i, top in enumerate(TOPS):
    k = i / (layers - 1)                      # 0 远 → 1 近
    amp = 0.035 + 0.06 * k
    prof = (top - amp * ridge(W, seed=i + 3, octaves=5, base=1.3 + 0.7 * k)) * H
    col = haze * (1 - k) + ink * k
    s_ = 0.42 + 0.38 * k                      # 最近一层也只到 80% 墨色，保持清淡
    col = col * s_ + cream * (1 - s_)
    below = yy - prof[None, :]
    mask = np.clip(below / 1.6, 0, 1)         # 抗锯齿的山脊边缘
    # 山脊下方逐渐被雾吞没：越往下越接近雾色
    fog_depth = 140 + 260 * (1 - k)
    fog = 1 - np.exp(-np.clip(below, 0, None) / fog_depth)
    fog_col = cream * 0.85 + paper * 0.15
    layer = col[None, None, :] * (1 - fog[..., None] * 0.92) + fog_col * (fog[..., None] * 0.92)
    # 水墨肌理：沿 x 方向拉长的细噪声
    tex = (rng.random((H // 3 + 1, W // 24 + 1)) - 0.5)
    tex = np.array(Image.fromarray(((tex + 0.5) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)) / 255 - 0.5
    layer = layer + tex[..., None] * 0.035 * (1 - fog[..., None])
    img = img * (1 - mask[..., None]) + layer * mask[..., None]

# 层间横向雾带
for yb, a in [(0.645, .5), (0.70, .55), (0.77, .6), (0.845, .55)]:
    band = np.exp(-((y - yb) / 0.012) ** 2) * a
    img = img * (1 - band[..., None]) + (cream * 0.7 + paper * 0.3) * band[..., None]
# 底部整体雾气，和下一屏的纸色衔接
b = np.clip((y - 0.86) / 0.14, 0, 1) ** 1.4
img = img * (1 - b[..., None]) + paper * b[..., None]
# 纸纹 + 抖动，防止色带
img += (rng.random((H, W, 1)) - 0.5) * (3 / 255) + (rng.random((H, W, 1)) - 0.5) * 0.012
Image.fromarray((np.clip(img, 0, 1) * 255).round().astype(np.uint8)).save(sys.argv[1], quality=90)
print('saved', sys.argv[1])
