# 新画风三组：整张图先抠出每只猫（连通块），按重心分到 8 格，再各自放大
import numpy as np, base64, io, json, subprocess, sys
from PIL import Image, ImageFilter
from scipy import ndimage
SP=sys.argv[1]; res={}
for n in '走路 挥手 蹦跳'.split():
    im=Image.open(f'licai/动作/{n}.webp').convert('RGB'); A=np.asarray(im).astype(int)
    lab,k=ndimage.label(np.abs(A-255).max(2)<7)
    edge=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    m=ndimage.binary_fill_holes(~np.isin(lab,list(edge)))
    fl,fn=ndimage.label(m); sz=ndimage.sum(m,fl,range(1,fn+1))
    big=[i+1 for i,s in enumerate(sz) if s>sz.max()*.25]
    cents=sorted(big,key=lambda i: ndimage.center_of_mass(fl==i)[1]); assert len(cents)==8,(n,len(cents))
    cx=[ndimage.center_of_mass(fl==i)[1] for i in cents]
    small=[i+1 for i,s in enumerate(sz) if sz.max()*.002<s<=sz.max()*.25]
    groups={c:[c] for c in cents}
    for i in small:
        x=ndimage.center_of_mass(fl==i)[1]; groups[cents[int(np.argmin([abs(x-c) for c in cx]))]].append(i)
    fr=[]
    for c in cents:
        mm=np.isin(fl,groups[c]); ys,xs=np.where(mm); x0,x1=max(0,xs.min()-10),min(im.width,xs.max()+11); y0,y1=max(0,ys.min()-10),min(im.height,ys.max()+11)
        rgb=Image.fromarray(np.where(mm[...,None],A,255).astype(np.uint8)[y0:y1,x0:x1]); j=len(fr)
        rgb.save(f'/tmp/seq/{n}_{j}.png'); fr.append((x0,x1,y0,y1,mm[y0:y1,x0:x1]))
    res[n]=fr
args=[]
for n in res:
    for j in range(8): args+=[f'/tmp/seq/{n}_{j}.png',f'/tmp/seq/{n}_{j}_up.png']
subprocess.run(['python3',SP+'/esrgan.py']+args,check=True,stdout=subprocess.DEVNULL)
s=open('licai-seq.js').read(); data=json.loads(s[s.index('= ')+2:s.rindex(';')])
for n,fr in res.items():
    out=[]; bots=[]
    for j,(x0,x1,y0,y1,mm) in enumerate(fr):
        al=Image.fromarray(mm.astype(np.uint8)*255).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.8))
        b=Image.open(f'/tmp/seq/{n}_{j}_up.png').convert('RGB'); al=al.resize(b.size,Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))
        b.putalpha(al); b.thumbnail((800,800),Image.LANCZOS); b.save(f'/tmp/seq/{n}_{j}_cut.png')
        bio=io.BytesIO(); b.save(bio,'WEBP',quality=86,method=6)
        cxx=(x0+x1)/2 if n!='走路' else (x0+x1)/2
        out.append({'src':'data:image/webp;base64,'+base64.b64encode(bio.getvalue()).decode(),'x':int(x0-(x0+x1)/2),'y':int(y0),'w':int(x1-x0),'h':int(y1-y0)}); bots.append(int(y1))
    base=max(bots); top=min(f['y'] for f in out)
    for f in out: f['y']-=base
    data[n]={'ref':base-top,'frames':out}
open('licai-seq.js','w').write(s[:s.index('= ')+2]+json.dumps(data,ensure_ascii=False)+';\n')
print({n:data[n]['ref'] for n in data})
