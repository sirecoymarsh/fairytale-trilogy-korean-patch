from pathlib import Path
import cv2,numpy as np,json
from PIL import Image
base=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
shotp=Path(r"C:\Users\CADRIA~1\AppData\Local\Temp\codex-clipboard-6017eb99-9745-4630-82c3-0e02109315d4.png")
shot=cv2.imdecode(np.fromfile(shotp,dtype=np.uint8),cv2.IMREAD_COLOR)
target=shot[100:340,185:600]
# emphasize plaque and glyph edges
sift=cv2.SIFT_create(nfeatures=1200,contrastThreshold=.02)
kt,dt=sift.detectAndCompute(cv2.cvtColor(target,cv2.COLOR_BGR2GRAY),None)
roots=[base/'staging/ui_other_banks_audit_v1/exported_png',base/'evidence/ui/grpo_png',base/'staging/title_lwg_audit_v2',base/'staging/title_grpe_exact_scan_v2/top_png',base/'staging/ui_missing_screen_deep_audit_v1/grpe_selected_png']
seen=set();files=[]
for root in roots:
 if root.exists():
  for p in root.rglob('*.png'):
   q=str(p.resolve()).lower()
   if q not in seen:seen.add(q);files.append(p)
rows=[];bf=cv2.BFMatcher(cv2.NORM_L2)
for i,p in enumerate(files):
 try: img=cv2.imdecode(np.fromfile(p,dtype=np.uint8),cv2.IMREAD_UNCHANGED)
 except:continue
 if img is None:continue
 if img.ndim==2: gray=img
 elif img.shape[2]==4:
  # composite alpha over neutral parchment gray, preserving authored visible pixels
  a=img[:,:,3:4].astype(np.float32)/255.; bgr=img[:,:,:3].astype(np.float32); comp=(bgr*a+128*(1-a)).astype(np.uint8);gray=cv2.cvtColor(comp,cv2.COLOR_BGR2GRAY)
 else:gray=cv2.cvtColor(img[:,:,:3],cv2.COLOR_BGR2GRAY)
 h,w=gray.shape
 scale=min(1.0,1280/max(h,w))
 if scale<1: gray=cv2.resize(gray,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
 k,d=sift.detectAndCompute(gray,None)
 if d is None or len(d)<2:continue
 ms=bf.knnMatch(dt,d,k=2);good=[m for m,n in ms if m.distance<0.72*n.distance]
 if not good:continue
 row={'file':str(p.relative_to(base)),'size':[w,h],'keypoints':len(k),'good_matches':len(good),'mean_distance':float(np.mean([m.distance for m in good]))}
 if len(good)>=4:
  src=np.float32([kt[m.queryIdx].pt for m in good]).reshape(-1,1,2);dst=np.float32([k[m.trainIdx].pt for m in good]).reshape(-1,1,2)
  H,mask=cv2.findHomography(src,dst,cv2.RANSAC,5.0)
  row['homography_inliers']=int(mask.sum()) if mask is not None else 0
  row['homography_ratio']=float(mask.mean()) if mask is not None else 0
 else:row['homography_inliers']=0;row['homography_ratio']=0
 rows.append(row)
 if i%300==0:print(i,len(files),p.name,flush=True)
rows.sort(key=lambda x:(-x['homography_inliers'],-x['good_matches'],x['mean_distance']))
out={'target':str(shotp),'crop':[185,100,600,340],'target_keypoints':len(kt),'scanned_png':len(files),'results':rows}
(base/'audit/title_logo_sift_search_v1.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
for r in rows[:60]: print(r['homography_inliers'],r['good_matches'],round(r['mean_distance'],1),r['size'],r['file'])
