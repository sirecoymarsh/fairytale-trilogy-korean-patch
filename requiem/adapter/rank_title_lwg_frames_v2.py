from PIL import Image
from pathlib import Path
import numpy as np,json
base=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
shot=np.asarray(Image.open(base/'evidence/runtime/final_game_qa/01_title_menu_final.png').convert('RGB').crop((3,26,1283,746)),dtype=np.int16)
root=base/'staging/title_lwg_audit_v2'; rows=[]
for p in root.rglob('*.png'):
 im=Image.open(p).convert('RGBA')
 if im.size!=(1280,720): continue
 a=np.asarray(im,dtype=np.int16); alpha=a[:,:,3]
 mask=alpha>=250
 if mask.sum()<500: continue
 dif=np.abs(a[:,:,:3]-shot).mean(axis=2)[mask]
 rows.append({'file':str(p.relative_to(base)),'alpha_pixels':int(mask.sum()),'mean_abs':float(dif.mean()),'median_abs':float(np.median(dif)),'p_lt3':float((dif<3).mean()),'p_lt10':float((dif<10).mean()),'p_lt30':float((dif<30).mean())})
rows.sort(key=lambda x:(-x['p_lt10'],x['mean_abs']))
(base/'audit/title_lwg_frame_exact_rank_v2.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
for r in rows[:40]: print(f"{r['p_lt10']:.4f} {r['p_lt30']:.4f} med={r['median_abs']:.1f} mean={r['mean_abs']:.1f} n={r['alpha_pixels']} {r['file']}")
