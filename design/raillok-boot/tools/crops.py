"""从 4 倍大图里裁细节图。usage: crops.py hero-bg.png outdir"""
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGB')
s = im.width / 440                    # 每个鞋图单位多少像素
CROPS = {'detail-dial': (112, 334, 120, 74), 'detail-quilt': (166, 186, 120, 74), 'detail-spine': (58, 92, 120, 74)}
for name, (x, y, w, h) in CROPS.items():
    box = tuple(round(v) for v in ((x - 20) * s, (y - 40) * s, (x - 20 + w) * s, (y - 40 + h) * s))
    im.crop(box).save(f'{sys.argv[2]}/{name}.jpg', quality=90)
