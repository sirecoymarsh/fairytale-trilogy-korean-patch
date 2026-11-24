from pathlib import Path
import cv2,json,hashlib
from PIL import Image,ImageDraw
ROOT=Path(r'P:\AI\Codex\projects\fairytale-requiem-ko');MOV=ROOT/'runtime/trial_ko/mov';OUT=ROOT/'staging/remaining_movies_audit_v1';OUT.mkdir(parents=True,exist_ok=True)
rows=[]
for p in sorted(MOV.glob('*.mpg')):
 cap=cv2.VideoCapture(str(p));fps=cap.get(cv2.CAP_PROP_FPS);frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT));dur=frames/fps if fps else None
 ims=[]
 for idx,f in enumerate([.05,.25,.5,.75,.95]):
  cap.set(cv2.CAP_PROP_POS_FRAMES,max(0,min(frames-1,int(frames*f))));ok,b=cap.read()
  if ok:
   b=cv2.cvtColor(b,cv2.COLOR_BGR2RGB);im=Image.fromarray(b);im.thumbnail((320,180));ims.append((f,im.copy()))
 cap.release()
 contact=Image.new('RGB',(320*len(ims),210),(30,30,30));d=ImageDraw.Draw(contact)
 for i,(f,im) in enumerate(ims):contact.paste(im,(i*320,25));d.text((i*320+5,5),f'{f:.0%}',fill='white')
 contact.save(OUT/f'{p.stem}_contact.jpg',quality=82)
 rows.append({'file':p.name,'bytes':p.stat().st_size,'fps':fps,'frames':frames,'duration_seconds':dur,'width':w,'height':h,'contact':str(OUT/f'{p.stem}_contact.jpg')})
(OUT/'report.json').write_text(json.dumps({'schema':'fairytale-requiem-remaining-movies-audit-v1','movies':rows},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False,indent=2))
