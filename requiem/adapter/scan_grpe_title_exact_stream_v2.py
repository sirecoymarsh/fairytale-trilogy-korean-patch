from pathlib import Path
import sys,subprocess,tempfile,shutil,json
import numpy as np
from PIL import Image
base=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");sys.path.insert(0,str(base/'adapter'))
from xfl_tool import parse_archive
arc=base/'runtime/trial_ko/grpe.xfl'; tool=base/'adapter/UiAssetTool.exe'
shot=np.asarray(Image.open(base/'evidence/runtime/final_game_qa/01_title_menu_final.png').convert('RGB').crop((3,26,1283,746)),dtype=np.int16)
outroot=base/'staging/title_grpe_exact_scan_v2';topdir=outroot/'top_png';outroot.mkdir(parents=True,exist_ok=True);topdir.mkdir(exist_ok=True)
a=parse_archive(arc); rows=[]
with tempfile.TemporaryDirectory(dir=outroot) as td, arc.open('rb') as f:
 td=Path(td); w=td/'x.wcg';p=td/'x.png'
 for idx,e in enumerate(a.entries):
  if not e.name.lower().endswith('.wcg'):continue
  f.seek(e.absolute_offset);w.write_bytes(f.read(e.size))
  q=subprocess.run([str(tool),'wcg2png',str(w),str(p)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  if q.returncode: rows.append({'name':e.name,'error':q.stderr.decode(errors='replace')});continue
  im=Image.open(p).convert('RGBA')
  if im.size!=(1280,720): rows.append({'name':e.name,'size':list(im.size),'skipped':'not_fullscreen'});continue
  ar=np.asarray(im,dtype=np.int16);alpha=ar[:,:,3]
  mask=alpha>=250
  if mask.sum()<500: mask=alpha>=128
  if mask.sum()<500: mask=alpha>=1
  dif=np.abs(ar[:,:,:3]-shot).mean(axis=2)[mask]
  row={'name':e.name,'size':[1280,720],'alpha_pixels':int(mask.sum()),'mean_abs':float(dif.mean()),'median_abs':float(np.median(dif)),'p_lt3':float((dif<3).mean()),'p_lt10':float((dif<10).mean()),'p_lt30':float((dif<30).mean())}
  rows.append(row)
  if idx%40==0: print(idx,e.name,row['p_lt10'],flush=True)
valid=[r for r in rows if 'p_lt10'in r]; valid.sort(key=lambda x:(-x['p_lt10'],x['mean_abs']))
# second pass save top 30
wanted={r['name'] for r in valid[:30]}
with arc.open('rb') as f:
 for e in a.entries:
  if e.name not in wanted:continue
  w=outroot/(Path(e.name).stem+'.wcg');p=topdir/(Path(e.name).stem+'.png');f.seek(e.absolute_offset);w.write_bytes(f.read(e.size));subprocess.run([str(tool),'wcg2png',str(w),str(p)],check=True,stdout=subprocess.DEVNULL);w.unlink()
report={'schema':'fairytale-title-grpe-exact-stream-v2','shot':str(base/'evidence/runtime/final_game_qa/01_title_menu_final.png'),'content_crop':[3,26,1283,746],'scanned_wcg':sum(1 for e in a.entries if e.name.lower().endswith('.wcg')),'fullcanvas_compared':len(valid),'results':valid,'non_fullscreen_or_errors':[r for r in rows if 'p_lt10' not in r]}
(base/'audit/title_grpe_exact_stream_v2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('TOP')
for r in valid[:40]:print(f"{r['p_lt10']:.5f} {r['p_lt30']:.5f} med={r['median_abs']:.1f} mean={r['mean_abs']:.1f} n={r['alpha_pixels']} {r['name']}")
