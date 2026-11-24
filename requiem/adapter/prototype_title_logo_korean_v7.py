from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,cv2,json,hashlib
base=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
srcp=next((base/'staging/title_lwg_audit_v1/9101').glob('*.png'))
donorp=base/'staging/ui_other_banks_audit_v1/exported_png/grpo_lib/0209.png'
src=Image.open(srcp).convert('RGB'); donor=Image.open(donorp).convert('RGB')
S=np.array(src);D=np.array(donor)
rois={'top':(255,150,590,232),'bottom':(315,215,590,290)}
# Locate coherent, text-light donor slabs in the parchment-heavy right half of 3022.
def best_patch(w,h,target,key):
 # Two verified, continuous paper slabs from the same authored library-page asset.
 x,y=(120,340)
 return (0.0,x,y,D[y:y+h,x:x+w].copy())
clean=S.copy(); masks={}; donors={}
for key,(x0,y0,x1,y1) in rois.items():
 r=S[y0:y1,x0:x1]; gray=cv2.cvtColor(r,cv2.COLOR_RGB2GRAY)
 # seed only strong neutral dark ink, then include antialias fringe connected to it
 hsv=cv2.cvtColor(r,cv2.COLOR_RGB2HSV); seed=((gray<210)&(hsv[:,:,1]<90)).astype(np.uint8)
 n,lab,stats,_=cv2.connectedComponentsWithStats(seed,8); core=np.zeros_like(seed)
 for i in range(1,n):
  if stats[i,cv2.CC_STAT_AREA]>=4:core[lab==i]=1
 mask=cv2.dilate(core.astype(np.uint8),np.ones((7,7),np.uint8),iterations=1)*255
 score,dx,dy,patch=best_patch(x1-x0,y1-y0,r,key)
 # Lab mean/std match using only bright original paper pixels
 plab=cv2.cvtColor(patch,cv2.COLOR_RGB2LAB).astype(np.float32); tlab=cv2.cvtColor(r,cv2.COLOR_RGB2LAB).astype(np.float32); bright=gray>180
 pm=plab.mean((0,1)); ps=plab.std((0,1))+1; tm=tlab[bright].mean(0); ts=tlab[bright].std(0)+1
 adj=np.clip((plab-pm)*(ts/ps)+tm,0,255).astype(np.uint8); adj=cv2.cvtColor(adj,cv2.COLOR_LAB2RGB)
 soft=cv2.GaussianBlur(mask,(0,0),0.8).astype(np.float32)/255
 clean[y0:y1,x0:x1]=np.clip(r*(1-soft[:,:,None])+adj*soft[:,:,None],0,255).astype(np.uint8)
 masks[key]=mask;donors[key]={'x':dx,'y':dy,'width':x1-x0,'height':y1-y0,'score':float(score)}
clean_img=Image.fromarray(clean); stage=base/'staging/title_logo_korean_v7_prototype';stage.mkdir(parents=True,exist_ok=True);clean_img.save(stage/'clean_plate.png')
fonts={'gaegu':base/'tools/fonts/Gaegu-Bold.ttf','poorstory':base/'tools/fonts/PoorStory-Regular.ttf','nanumbrush':base/'tools/fonts/NanumBrushScript-Regular.ttf','diphylleia':base/'tools/fonts/title_candidates/Diphylleia-Regular.ttf','kirang':base/'tools/fonts/title_candidates/KirangHaerang-Regular.ttf','yeonsung':base/'tools/fonts/title_candidates/YeonSung-Regular.ttf'}

def fit(fontp,text,maxw,maxh,start=90):
 for sz in range(start,15,-1):
  f=ImageFont.truetype(str(fontp),sz);b=f.getbbox(text,stroke_width=0)
  if b[2]-b[0]<=maxw and b[3]-b[1]<=maxh:return f
 raise RuntimeError(text)
def bez(draw,pts,fill,width=2):
 p=np.array(pts,float);arr=[]
 for t in np.linspace(0,1,50):arr.append(tuple(((1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3]).tolist()))
 draw.line(arr,fill=fill,width=width,joint='curve')
records=[]
for name,fontp in fonts.items():
 im=clean_img.copy();ink=(55,51,52); d=ImageDraw.Draw(im)
 f1=fit(fontp,'페어리테일',310,64,92);f2=fit(fontp,'레퀴엠',225,58,96)
 # source-like offset two-line composition, preserving the four-point star and red English ribbon
 d.text((425,184),'페어리테일',font=f1,fill=ink,anchor='mm',stroke_width=0)
 d.text((458,251),'레퀴엠',font=f2,fill=ink,anchor='mm',stroke_width=0)
 # Fine fairytale curls, deliberately outside the glyph counters.
 bez(d,[(272,206),(257,218),(267,224),(279,216)],ink,2)
 bez(d,[(558,204),(579,203),(580,188),(570,187)],ink,2)
 bez(d,[(552,274),(575,286),(580,272),(570,268)],ink,2)
 out=stage/f'title_logo_{name}.png';im.save(out)
 crop=im.crop((190,105,620,345));crop.save(stage/f'title_logo_{name}_crop.png')
 records.append({'variant':name,'font':str(fontp),'top_size':f1.size,'bottom_size':f2.size,'path':str(out)})
(stage/'prototype_manifest.json').write_text(json.dumps({'source':str(srcp),'donor':str(donorp),'rois':rois,'donor_slabs':donors,'variants':records},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'donors':donors,'variants':records},ensure_ascii=False,indent=2))






