"""从大图里裁提案 03 的细节图，贴到页面底色上。usage: crops3.py hero3.png outdir"""
import sys
from PIL import Image
im = Image.open(sys.argv[1])
bg = Image.new('RGBA', im.size, (233, 232, 227, 255))
im = Image.alpha_composite(bg, im).convert('RGB')
s = im.width / 440
CROPS = {'detail3-heel': (52, 352, 110, 68), 'detail3-dial': (110, 190, 110, 68), 'detail3-tongue': (176, 262, 110, 68)}
for name, (x, y, w, h) in CROPS.items():
    box = tuple(round(v) for v in ((x - 20) * s, (y - 40) * s, (x - 20 + w) * s, (y - 40 + h) * s))
    im.crop(box).save(f'{sys.argv[2]}/{name}.jpg', quality=92)
