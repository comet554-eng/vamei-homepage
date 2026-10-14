# 新画风三组：整张图先抠出每只猫（连通块），按重心分到 8 格，再各自放大
import numpy as np, base64, io, json, subprocess, sys
from PIL import Image, ImageFilter
from scipy import ndimage
SP=sys.argv[1]; res={}
CFG={'走路':(7,1,0),'挥手':(7,1,0),'蹦跳':(7,1,0),'侧面骑车':(14,0,1),'侧面骑车2':(14,0,1),'点头指向':(12,1,0),'转身跑出':(12,1,0),'开心挥手':(12,1,0),'爬坡吃力':(14,0,1),'爬坡吃力2':(14,0,1),'骑车喝水':(14,0,1),'打气':(14,0,1),'戴头盔':(12,1,0),'吓一跳':(12,1,0),'摆爪否定':(12,1,0),'累瘫':(12,1,0),'叉腰得意':(12,1,0)}
ONLY=sys.argv[2].split(',') if len(sys.argv)>2 else list(CFG)
for n in ONLY:
    th,fill,wheel=CFG[n]
    im=Image.open(f'licai/动作/{n}.webp').convert('RGB'); A=np.asarray(im).astype(int)
    lab,k=ndimage.label(np.abs(A-255).max(2)<th)
    edge=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    if wheel:
        import cv2
        gray=A.mean(2).astype(np.uint8); mx=A.max(2); mn=A.min(2); sat=(mx-mn)/np.maximum(mx,1)
        dark=((gray<110)&(sat<.35)).astype(np.uint8)*255
        cs=cv2.HoughCircles(cv2.GaussianBlur(dark,(5,5),1.5),cv2.HOUGH_GRADIENT,dp=1,minDist=60,param1=80,param2=28,minRadius=32,maxRadius=75)
        rows=np.where((np.abs(A-255).max(2)>=th).any(1))[0]; ymid=rows[0]+(rows[-1]-rows[0])*.55
        dk=ndimage.binary_dilation(dark>0,iterations=2)
        def ok(x,y,r):
            if y<ymid: return False
            t=np.linspace(0,2*np.pi,90); px=np.clip((x+r*np.cos(t)).astype(int),0,A.shape[1]-1); py=np.clip((y+r*np.sin(t)).astype(int),0,A.shape[0]-1)
            return dk[py,px].mean()>.7
        circ=[] if cs is None else [c for c in cs[0].tolist() if ok(*c)]; print(n,'wheels',len(circ),flush=True)
        for i,sl in enumerate(ndimage.find_objects(lab)):
            if sl is None or i+1 in edge: continue
            cy,cx=(sl[0].start+sl[0].stop)/2,(sl[1].start+sl[1].stop)/2
            if any(all((px-x)**2+(py-y)**2<(r*.95)**2 for px,py in ((sl[1].start,sl[0].start),(sl[1].stop,sl[0].start),(sl[1].start,sl[0].stop),(sl[1].stop,sl[0].stop))) for x,y,r in circ): edge.add(i+1)
    m=~np.isin(lab,list(edge))
    if fill: m=ndimage.binary_fill_holes(m)
    fl,fn=ndimage.label(m); sz=ndimage.sum(m,fl,range(1,fn+1))
    big=[i+1 for i,s in enumerate(sz) if s>sz.max()*.25]
    cents=sorted(big,key=lambda i: ndimage.center_of_mass(fl==i)[1]); print(n,len(cents),flush=True)
    if len(cents)!=8: continue
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
