# 新画风三组：整张图先抠出每只猫（连通块），按重心分到 8 格，再各自放大
import numpy as np, base64, io, json, subprocess, sys
from PIL import Image, ImageFilter
from scipy import ndimage
SP=sys.argv[1]; res={}
CFG={'走路':(7,1,0),'挥手':(7,1,0),'蹦跳':(7,1,0),'侧面骑车':(14,0,1),'侧面骑车2':(14,0,1),'点头指向':(12,1,0),'转身跑出':(12,1,0),'开心挥手':(12,1,0),'爬坡吃力':(14,0,1),'爬坡吃力2':(14,0,1),'骑车喝水':(14,0,1),'打气':(14,0,1),'戴头盔':(12,1,0),'吓一跳':(12,1,0),'摆爪否定':(12,1,0),'累瘫':(12,1,0),'叉腰得意':(12,1,0),'拍照':(12,1,0),'举手':(12,1,0),'划重点':(12,1,0),'拍手':(12,1,0),'抬头张望':(12,1,0),'思考怀疑':(12,1,0),'背包出发':(12,1,0),'放大镜':(12,1,0),'记笔记':(12,1,0),'雨衣跑':(12,1,0),'蹦跳欢呼':(12,1,0),'眺望':(12,1,0),'卷尺':(12,1,0),'骑车挥手':(14,0,1),'骑车开心':(14,0,1),'画饼图':(12,1,0),'摘头盔':(14,0,1),'温度计':(12,1,0),'踢石头':(12,1,0),'检查车轮':(14,0,1),'按车铃':(14,0,1),'绕锥桶':(14,0,1),'生气跺脚':(12,1,0),'下车推车':(14,0,1),'骑车摇摆':(14,0,1),'偷笑':(12,1,0),'发现目标':(12,1,0),'摔倒爬起':(12,1,0),'望远镜':(12,1,0),'背包出发2':(12,1,0),'骑车开心2':(14,0,1),'伸展运动':(12,1,0),'捡树叶':(12,1,0),'拍照2':(12,1,0),'转圈':(12,1,0),'搭帐篷':(12,1,0),'喝茶':(12,1,0),'发现脚印':(12,1,0),'骑车跳跃':(14,0,1),'撑伞':(12,1,0),'看地图':(12,1,0),'乖巧张望':(12,1,0),'站立拍手':(12,1,0),'害羞捂脸':(12,1,0),'指南针':(12,1,0),'看书':(12,1,0),'打哈欠':(12,1,0),'闻花':(12,1,0),'擦汗':(12,1,0),'弓背伸懒腰':(12,1,0),'打招呼':(12,1,0),'放大镜2':(12,1,0),'举手欢迎':(12,1,0),'侧身挥手':(12,1,0),'吃鲷鱼烧':(12,1,0),'抱松果':(12,1,0),'戴墨镜':(12,1,0),'开心合掌':(12,1,0),'委屈难过':(12,1,0),'摆爪否定B':(12,1,0),'跨上车':(14,0,1),'检查车轮2':(14,0,1),'吃能量棒':(14,0,1),'生气挥爪':(12,1,0),'开车灯':(14,0,1),'看手表':(12,1,0),'吃能量棒2':(14,0,1),'吃能量棒3':(14,0,1),'指向':(12,1,0)}
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
    fb=len(cents)!=8
    if fb:
        cs2=ndimage.uniform_filter1d(m.sum(0).astype(float),9); xs=np.where(cs2>0)[0]; L,R=xs[0],xs[-1]+1; w=(R-L)/8; cuts=[L]
        for j in range(1,8):
            c=int(L+j*w); r=int(w*.3); cuts.append(c-r+int(np.argmin(cs2[c-r:c+r])))
        cuts.append(R); fl=np.zeros_like(fl); 
        for j in range(8): fl[:,cuts[j]:cuts[j+1]]=np.where(m[:,cuts[j]:cuts[j+1]],j+1,0)
        cents=list(range(1,9)); cx=[(cuts[j]+cuts[j+1])/2 for j in range(8)]; small=[]
    cx=[ndimage.center_of_mass(fl==i)[1] for i in cents]
    small=[] if fb else [i+1 for i,s in enumerate(sz) if sz.max()*.002<s<=sz.max()*.25]
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
import glob as _g
data={}
for _f in _g.glob('licai-seq/*.js'):
    _t=open(_f).read(); data[_t[_t.index('[')+2:_t.index(']')-1]]=json.loads(_t[_t.index('= ')+2:_t.rindex(';')])
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
[open(f'licai-seq/{n}.js','w').write('LICAI_SEQ[%s] = %s;\n'%(json.dumps(n,ensure_ascii=False),json.dumps(data[n],ensure_ascii=False))) for n in res]
print({n:data[n]['ref'] for n in data})
