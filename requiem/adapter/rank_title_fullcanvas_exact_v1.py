from PIL import Image
from pathlib import Path
import numpy as np, json, hashlib
base=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
shotp=base/'evidence/runtime/final_game_qa/01_title_menu_final.png'
shot=np.asarray(Image.open(shotp).convert('RGB').crop((3,26,1283,746)),dtype=np.int16)
roots=[base/'staging/ui_other_banks_audit_v1/exported_png',base/'evidence/ui/grpo_png',base/'staging/ui_missing_screen_deep_audit_v1/grpe_fullscan_png']
files=[]
for root in roots:
 if root.exists(): files.extend(root.rglob('*.png'))
rows=[]
for p in files:
 try: im=Image.open(p).convert('RGBA')
 except Exception: continue
 if im.size!=(1280,720): continue
 a=np.asarray(im,dtype=np.int16); alpha=a[:,:,3]
 for thr in (250,128,1):
  mask=alpha>=thr
  if mask.sum()>=500: break
 if mask.sum()<500: continue
 dif=np.abs(a[:,:,:3]-shot).mean(axis=2)[mask]
 rows.append(dict(file=str(p.relative_to(base)),alpha_pixels=int(mask.sum()),alpha_threshold=thr,mean_abs=float(dif.mean()),median_abs=float(np.median(dif)),p_lt3=float((dif<3).mean()),p_lt10=float((dif<10).mean()),p_lt30=float((dif<30).mean())))
rows.sort(key=lambda x:(-x['p_lt10'],x['mean_abs']))
out=base/'audit/title_fullcanvas_exact_rank_v1.json'; out.write_text(json.dumps({'shot':str(shotp),'crop':[3,26,1283,746],'scanned':len(rows),'top':rows[:200]},ensure_ascii=False,indent=2),encoding='utf-8')
print('scanned',len(rows));
for r in rows[:40]: print(f"{r['p_lt10']:.4f} {r['p_lt30']:.4f} med={r['median_abs']:.1f} mean={r['mean_abs']:.1f} n={r['alpha_pixels']} {r['file']}")
