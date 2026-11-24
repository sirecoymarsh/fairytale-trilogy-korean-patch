from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, cv2, json, hashlib
ROOT=Path(r'P:\AI\Codex\projects\fairytale-requiem-ko')
SRC=sorted((ROOT/'staging/grpe_title_logo_korean_v1_assets/source/frames').glob('*.png'))[0]
DONOR=ROOT/'staging/ui_other_banks_audit_v1/exported_png/grpo_lib/0209.png'
FONT=ROOT/'tools/fonts/title_candidates/YeonSung-Regular.ttf'
OUT=ROOT/'staging/title_logo_korean_v9_coherent_plate'
OUT.mkdir(parents=True,exist_ok=True)

def fit(text,maxw,maxh,start):
 s=start
 while s>=10:
  f=ImageFont.truetype(str(FONT),s);box=f.getbbox(text)
  if box[2]-box[0]<=maxw and box[3]-box[1]<=maxh:return f
  s-=1
 raise RuntimeError('fit')
def bez(draw,pts,fill,width=2):
 P=np.array(pts,np.float32);last=P[0]
 for t in np.linspace(0,1,40)[1:]:
  q=(1-t)**3*P[0]+3*(1-t)**2*t*P[1]+3*(1-t)*t*t*P[2]+t**3*P[3]
  draw.line((tuple(last),tuple(q)),fill=fill,width=width);last=q
src=Image.open(SRC).convert('RGB');a=np.array(src);h,w=a.shape[:2]
# One coherent source-authored blank parchment slab for the whole plaque interior.
d=np.array(Image.open(DONOR).convert('RGB'))
x0,y0,x1,y1=226,137,605,306
patch=d[340:340+(y1-y0),120:120+(x1-x0)].copy()
if patch.shape[:2]!=(y1-y0,x1-x0):raise RuntimeError(patch.shape)
mask=np.zeros((h,w),np.uint8)
poly=np.array([[240,150],[582,150],[596,157],[597,282],[589,296],[241,296],[236,284],[236,158]],np.int32)
cv2.fillPoly(mask,[poly],255)
# Protect the four-point star exactly.
cv2.rectangle(mask,(249,258),(298,309),0,-1)
# Protect the complete red ribbon, its outline, and its white English lettering.
hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV);rr=np.zeros((h,w),np.uint8)
roi=(370,272,610,337);rx0,ry0,rx1,ry1=roi
sub=hsv[ry0:ry1,rx0:rx1]
red=((sub[:,:,1]>75)&((sub[:,:,0]<18)|(sub[:,:,0]>170))&(sub[:,:,2]>45)).astype(np.uint8)*255
num,lab,stats,_=cv2.connectedComponentsWithStats(red,8)
if num>1:
 keep=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]));red=(lab==keep).astype(np.uint8)*255
red=cv2.dilate(red,np.ones((11,11),np.uint8),iterations=1)
rr[ry0:ry1,rx0:rx1]=red
mask[rr>0]=0
# Match the donor's paper in Lab using only source background pixels.
gray=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY);sat=hsv[:,:,1]
bg=(mask>0)&(gray>185)&(sat<75)
pl=cv2.cvtColor(patch,cv2.COLOR_RGB2LAB).astype(np.float32)
tl=cv2.cvtColor(a,cv2.COLOR_RGB2LAB).astype(np.float32)
pm,ps=pl.reshape(-1,3).mean(0),pl.reshape(-1,3).std(0)+1
tm,ts=tl[bg].mean(0),tl[bg].std(0)+1
adj=np.clip((pl-pm)*(ts/ps)+tm,0,255).astype(np.uint8)
adj=cv2.cvtColor(adj,cv2.COLOR_LAB2RGB)
canvas=a.copy();soft=cv2.GaussianBlur(mask,(0,0),0.8).astype(np.float32)/255
roi_src=canvas[y0:y1,x0:x1].astype(np.float32)
canvas[y0:y1,x0:x1]=np.clip(roi_src*(1-soft[y0:y1,x0:x1,None])+adj*soft[y0:y1,x0:x1,None],0,255).astype(np.uint8)
clean=Image.fromarray(canvas,'RGB');out=clean.copy();draw=ImageDraw.Draw(out);ink=(55,51,52)
f1=fit('페어리테일',310,64,92);f2=fit('레퀴엠',235,64,96)
draw.text((425,184),'페어리테일',font=f1,fill=ink,anchor='mm')
draw.text((458,251),'레퀴엠',font=f2,fill=ink,anchor='mm')
bez(draw,[(272,206),(257,218),(267,224),(279,216)],ink,2)
bez(draw,[(558,204),(579,203),(580,188),(570,187)],ink,2)
bez(draw,[(552,274),(575,286),(580,272),(570,268)],ink,2)
src.save(OUT/'source.png');clean.save(OUT/'clean.png');out.save(OUT/'candidate.png')
for name,im in [('source_crop',src),('clean_crop',clean),('candidate_crop',out)]:im.crop((190,105,620,345)).save(OUT/f'{name}.png')
Image.fromarray(mask).save(OUT/'interior_mask.png');Image.fromarray((soft*255).astype(np.uint8)).save(OUT/'soft_mask.png')
(OUT/'report.json').write_text(json.dumps({'source':str(SRC),'donor':str(DONOR),'font_sizes':[f1.size,f2.size],'interior_polygon':poly.tolist(),'protected_star':[249,258,298,309],'protected_ribbon_roi':list(roi),'mask_pixels':int((mask>0).sum()),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest()},ensure_ascii=False,indent=2),encoding='utf-8')
print(OUT)

