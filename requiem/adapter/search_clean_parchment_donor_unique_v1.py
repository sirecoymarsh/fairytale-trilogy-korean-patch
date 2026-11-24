from pathlib import Path
import cv2,numpy as np,json
from PIL import Image
base=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
source=next((base/'staging/title_lwg_audit_v1/9101').glob('*.png'));S=np.array(Image.open(source).convert('RGB'))
roots=[base/'staging/ui_other_banks_audit_v1/exported_png',base/'staging/title_grpe_exact_scan_v2/top_png',base/'staging/ui_missing_screen_deep_audit_v1/grpe_selected_png']
files=[];seen=set()
for r in roots:
 if r.exists():
  for p in r.rglob('*.png'):
   q=str(p.resolve()).lower()
   if q not in seen:seen.add(q);files.append(p)

def ii(a):return cv2.integral(a.astype(np.float64))
def sums(I,x,y,w,h):return I[y+h,x+w]-I[y,x+w]-I[y+h,x]+I[y,x]
rows=[]
for key,(x0,y0,x1,y1) in {'top':(255,150,590,220),'bottom':(320,225,580,285)}.items():
 target=S[y0:y1,x0:x1];tg=cv2.cvtColor(target,cv2.COLOR_RGB2GRAY);bright=tg>180;tm=target[bright].mean(0);ts=target[bright].std(0)+1;w=x1-x0;h=y1-y0;cands=[]; best_by_file={}
 for p in files:
  try:im=np.array(Image.open(p).convert('RGB'))
  except:continue
  H,W=im.shape[:2]
  if W<w or H<h:continue
  g=cv2.cvtColor(im,cv2.COLOR_RGB2GRAY);hsv=cv2.cvtColor(im,cv2.COLOR_RGB2HSV);edge=(cv2.Canny(g,40,100)>0).astype(float);dark=(g<175).astype(float);sat=hsv[:,:,1].astype(float)/255
  ie,idk,isa,ig,ig2=[ii(a) for a in [edge,dark,sat,g,g.astype(float)**2]]
  for y in range(0,H-h+1,12):
   for x in range(0,W-w+1,12):
    area=w*h;e=sums(ie,x,y,w,h)/area;d=sums(idk,x,y,w,h)/area;sa=sums(isa,x,y,w,h)/area;m=sums(ig,x,y,w,h)/area;v=max(0,sums(ig2,x,y,w,h)/area-m*m);st=v**.5
    # require a coherent quiet slab; color/variance can be adjusted later
    score=e*900+d*900+sa*80+abs(m-float(np.mean(tm)))/8+abs(st-float(np.mean(ts)))/8
    old=best_by_file.get(str(p));
    if old is None or score<old[0]: best_by_file[str(p)]=(score,p,x,y,e,d,sa,m,st)
 cands=sorted(best_by_file.values(),key=lambda z:z[0])[:100]
 rows.append({'key':key,'size':[w,h],'target_mean_rgb':tm.tolist(),'target_std_rgb':ts.tolist(),'candidates':[{'score':float(s),'file':str(p.relative_to(base)),'x':x,'y':y,'edge':float(e),'dark':float(d),'sat':float(sa),'gray_mean':float(m),'gray_std':float(st)} for s,p,x,y,e,d,sa,m,st in cands]})
out=base/'audit/title_logo_clean_donor_search_v1.json';out.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
for r in rows:
 print('\n',r['key'],r['target_mean_rgb'],r['target_std_rgb']);
 for c in r['candidates'][:30]:print(round(c['score'],2),round(c['edge'],3),round(c['dark'],3),round(c['sat'],3),round(c['gray_mean'],1),round(c['gray_std'],1),c['x'],c['y'],c['file'])

