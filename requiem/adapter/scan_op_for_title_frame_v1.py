from pathlib import Path
import cv2,numpy as np,json
base=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
vid=str(base/'staging/runtime_backup_before_op_subtitles_20260814_045737/mov/0001.mpg')
shot=cv2.imdecode(np.fromfile(base/'evidence/runtime/final_game_qa/01_title_menu_final.png',dtype=np.uint8),cv2.IMREAD_COLOR)[26:746,3:1283]
small=cv2.resize(shot,(160,90),interpolation=cv2.INTER_AREA); target_roi=cv2.resize(shot[70:360,130:650],(160,90),interpolation=cv2.INTER_AREA)
cap=cv2.VideoCapture(vid);fps=cap.get(cv2.CAP_PROP_FPS);rows=[];i=0
while True:
 ok,fr=cap.read();
 if not ok:break
 if i%3==0:
  a=cv2.resize(fr,(160,90),interpolation=cv2.INTER_AREA).astype(np.int16)
  b=cv2.resize(fr[70:360,130:650],(160,90),interpolation=cv2.INTER_AREA).astype(np.int16)
  rows.append({'frame':i,'time':i/fps,'full_mad':float(np.abs(a-small.astype(np.int16)).mean()),'logo_roi_mad':float(np.abs(b-target_roi.astype(np.int16)).mean())})
 i+=1
cap.release();full=sorted(rows,key=lambda x:x['full_mad']);roi=sorted(rows,key=lambda x:x['logo_roi_mad']);
(base/'audit/op_title_frame_scan_v1.json').write_text(json.dumps({'fps':fps,'frames':i,'full_top':full[:100],'roi_top':roi[:100]},indent=2),encoding='utf-8')
print('FULL',full[:20]);print('ROI',roi[:20])
