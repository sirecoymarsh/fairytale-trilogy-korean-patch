from pathlib import Path
import cv2,numpy as np,json
ROOT=Path(r'P:\AI\Codex\projects\fairytale-requiem-ko');D=ROOT/'staging/grpe_wcg_thumbnail_audit_v1';src=cv2.imread(str(D/'3022.jpg'))
mask=np.ones(src.shape[:2],np.uint8)*255;mask[18:160,85:250]=0
# also score border-frame exactness and global color/edge consistency.
gs=cv2.cvtColor(src,cv2.COLOR_BGR2GRAY);sift=cv2.SIFT_create();kp,des=sift.detectAndCompute(gs,mask);bf=cv2.BFMatcher();rows=[]
for p in D.glob('*.jpg'):
 if p.stem=='3022':continue
 im=cv2.imread(str(p))
 if im is None or im.shape!=src.shape:continue
 d=np.abs(im.astype(np.int16)-src.astype(np.int16)).mean(2);mae=float(d[mask>0].mean());exact=float((d[mask>0]==0).mean())
 gi=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY);kp2,des2=sift.detectAndCompute(gi,None);good=0
 if des is not None and des2 is not None:
  ms=bf.knnMatch(des,des2,k=2);good=sum(1 for a,b in ms if a.distance<.72*b.distance)
 rows.append({'entry':p.stem+'.wcg','outside_text_mae':mae,'outside_exact_fraction':exact,'sift_good':good,'path':str(p)})
rows.sort(key=lambda x:(-x['sift_good'],x['outside_text_mae']));out={'schema':'fairytale-requiem-credit-background-donor-rank-v1','source':'3022.wcg','rows':rows};(ROOT/'audit/credit_background_donor_rank_v1.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(rows[:40],ensure_ascii=False,indent=2))
