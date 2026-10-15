# 给每个页面只插入它用到的 licai-seq/<动作>.js
# 用法（在 video/ 下）：python3 licai/动作/splitseq.py
import json, os, re, glob
data = {}
for f in glob.glob('licai-seq/*.js'):
    data[os.path.basename(f)[:-3]] = 1
mv = open('licai-move.js').read()
anim = dict(re.findall(r"'([^']+)': \['([^']+)'", mv[mv.index('var ANIM_RAW'):]))
fb = dict(re.findall(r"'([^']+)': '([^']+)'", mv[mv.index('var SEQ_FALLBACK'):mv.index('\n', mv.index('var SEQ_FALLBACK'))]))
M0, M1 = '<!-- seq:begin -->', '<!-- seq:end -->'
for h in glob.glob('licai-*.html'):
    t = open(h).read()
    if 'licai-seq' not in t: continue
    names = set(re.findall(r"'([^'{}]+)'", t))
    need = sorted({n for n in names if n in data} | {anim[n] for n in names if n in anim and anim[n] in data})
    if 'seq-all' in h: need = list(data)
    tags = '\n'.join(f'<script src="licai-seq/{n}.js"></script>' for n in need)
    block = f'{M0}\n<script>var LICAI_SEQ = {{}};</script>\n{tags}\n{M1}'
    if M0 in t: t = t[:t.index(M0)] + block + t[t.index(M1) + len(M1):]
    else: t = t.replace('<script src="licai-seq.js"></script>', block)
    open(h, 'w').write(t); print(h, len(need))
