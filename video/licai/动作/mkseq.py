import numpy as np, base64, io, json
from PIL import Image, ImageFilter
from scipy import ndimage
names='探头 笑开 跑步 摔跟头 正面骑车 滑雪板 走路 挥手 蹦跳'.split(); out={}
for n in names:
    im=Image.open(f'licai/动作/{n}.webp').convert('RGB'); A=np.asarray(im).astype(int)
    fg=ndimage.binary_opening(np.abs(A-255).max(2)>22,iterations=1)
    cs=ndimage.uniform_filter1d(fg.sum(0).astype(float),9)
    xs=np.where(cs>0)[0]; L,R=int(xs[0]),int(xs[-1])+1; w=(R-L)/8; cuts=[L]
    for j in range(1,8):
        c=int(L+j*w); r=int(w*.3); cuts.append(int(c-r+np.argmin(cs[c-r:c+r])))
    cuts.append(R); fr=[]; bots=[]
    for j in range(8):
        x0,x1=cuts[j],cuts[j+1]; ys=np.where(fg[:,x0:x1].any(1))[0]; y0,y1=int(max(0,ys[0]-10)),int(min(im.height,ys[-1]+11))
        a=A[y0:y1,x0:x1]; th=7 if n in('走路','挥手','蹦跳') else 20; lab,k=ndimage.label(np.abs(a-255).max(2)<th)
        borders=[lab[0],lab[:,0],lab[:,-1]]+([] if n in('探头','笑开') else [lab[-1]])
        m=~np.isin(lab,list(set(np.unique(np.concatenate(borders)))-{0}))
        fl,fn=ndimage.label(m); sz=ndimage.sum(m,fl,range(1,fn+1)); bd=set(np.unique(np.concatenate([fl[:,:2].ravel(),fl[:,-2:].ravel()])))-{0}; big1=int(sz.argmax())+1
        m=np.isin(fl,[i+1 for i,s in enumerate(sz) if (i+1)==big1 or (s>sz.max()*.01 and (i+1) not in bd)]); m=ndimage.binary_fill_holes(m) if n in('走路','挥手','蹦跳') else m
        al=Image.fromarray(m.astype(np.uint8)*255).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.8))
        big=Image.open(f'/tmp/seq/{n}_{j}_up.png').convert('RGB'); al=al.resize(big.size,Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))
        big.putalpha(al); big.thumbnail((800,800),Image.LANCZOS); big.save(f'/tmp/seq/{n}_{j}_cut.png')
        b=io.BytesIO(); big.save(b,'WEBP',quality=86,method=6)
        fr.append({'src':'data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode(),'x':int(x0-(x0+x1)/2),'y':y0,'w':x1-x0,'h':y1-y0})
        bots.append(y1)
    base=max(bots); top=min(f['y'] for f in fr)
    for f in fr: f['y']-=base
    out[n]={'ref':base-top,'frames':fr}
open('licai-seq.js','w').write('// 李财逐帧动作：每组 8 帧（Real-ESRGAN 放大后抠图，原图在 licai/动作/）；x/y/w/h 为该帧在原图里相对“底线中心”的位置，ref 为整组高度\nvar LICAI_SEQ = '+json.dumps(out,ensure_ascii=False)+';\n')
print({n:out[n]['ref'] for n in out})
