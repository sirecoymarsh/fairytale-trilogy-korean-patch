from pathlib import Path
import cv2,numpy as np,json
base=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
src=next((base/'staging/title_lwg_audit_v1/9101').glob('*.png'))
im=cv2.imdecode(np.fromfile(src,dtype=np.uint8),cv2.IMREAD_COLOR);target=im[115:345,205:615]
sift=cv2.SIFT_create(nfeatures=1400,contrastThreshold=.015);kt,dt=sift.detectAndCompute(cv2.cvtColor(target,cv2.COLOR_BGR2GRAY),None);bf=cv2.BFMatcher(cv2.NORM_L2)
roots=[base/'staging/title_lwg_audit_v1/9101',base/'staging/ui_other_banks_audit_v1/exported_png',base/'evidence/ui/grpo_png',base/'staging/title_lwg_audit_v2',base/'staging/title_grpe_exact_scan_v2/top_png',base/'staging/ui_missing_screen_deep_audit_v1/grpe_selected_png']
files=[];seen=set()
for root in roots:
 if root.exists():
  for p in root.rglob('*.png'):
   q=str(p.resolve()).lower()
   if q not in seen:seen.add(q);files.append(p)
rows=[]
for p in files:
 img=cv2.imdecode(np.fromfile(p,dtype=np.uint8),cv2.IMREAD_UNCHANGED)
 if img is None:continue
 if img.ndim==2:g=img
 elif img.shape[2]==4:
  a=img[:,:,3:4].astype(np.float32)/255;g=cv2.cvtColor((img[:,:,:3]*a+220*(1-a)).astype(np.uint8),cv2.COLOR_BGR2GRAY)
 else:g=cv2.cvtColor(img[:,:,:3],cv2.COLOR_BGR2GRAY)
 k,d=sift.detectAndCompute(g,None)
 if d is None or len(d)<2:continue
 good=[m for m,n in bf.knnMatch(dt,d,k=2) if m.distance<.68*n.distance]
 inn=0;rat=0
 if len(good)>=4:
  s=np.float32([kt[m.queryIdx].pt for m in good]).reshape(-1,1,2);t=np.float32([k[m.trainIdx].pt for m in good]).reshape(-1,1,2);H,mask=cv2.findHomography(s,t,cv2.RANSAC,4)
  if mask is not None:inn=int(mask.sum());rat=float(mask.mean())
 rows.append({'file':str(p.relative_to(base)),'size':[img.shape[1],img.shape[0]],'good':len(good),'inliers':inn,'ratio':rat,'mean_distance':float(np.mean([m.distance for m in good])) if good else 999})
rows.sort(key=lambda r:(-r['inliers'],-r['good'],r['mean_distance']));(base/'audit/title_plaque_sibling_sift_v1.json').write_text(json.dumps({'target':str(src),'crop':[205,115,615,345],'results':rows},ensure_ascii=False,indent=2),encoding='utf-8')
for r in rows[:80]:print(r['inliers'],r['good'],round(r['ratio'],2),round(r['mean_distance'],1),r['size'],r['file'])
