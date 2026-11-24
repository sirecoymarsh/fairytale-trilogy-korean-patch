#!/usr/bin/env python3
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import sys,subprocess,tempfile,shutil,json,hashlib
from PIL import Image
sys.path.insert(0,r'P:\AI\Codex\projects\fairytale-requiem-ko\adapter');import xfl_tool
ROOT=Path(r'P:\AI\Codex\projects\fairytale-requiem-ko');ARC=ROOT/'runtime/trial_ko/grpe.xfl';TOOL=ROOT/'adapter/UiAssetTool.exe';OUT=ROOT/'staging/grpe_wcg_thumbnail_audit_v1';OUT.mkdir(parents=True,exist_ok=True);TMP=OUT/'tmp';TMP.mkdir(exist_ok=True)
a=xfl_tool.parse_archive(ARC);es=[e for e in a.entries if e.name.lower().endswith('.wcg')]
def one(e):
 raw=TMP/e.name;png=TMP/(Path(e.name).stem+'.png');jpg=OUT/(Path(e.name).stem+'.jpg')
 with ARC.open('rb') as f:f.seek(e.absolute_offset);raw.write_bytes(f.read(e.size))
 try:
  subprocess.run([str(TOOL),'wcg2png',str(raw),str(png)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,creationflags=0x08000000)
  with Image.open(png) as im:
   size=list(im.size);mode=im.mode;im=im.convert('RGB');im.thumbnail((320,180));im.save(jpg,'JPEG',quality=72,optimize=True)
  return {'entry':e.name,'payload_bytes':e.size,'size':size,'mode':mode,'thumbnail':str(jpg),'status':'ok'}
 except Exception as ex:return {'entry':e.name,'payload_bytes':e.size,'status':'error','error':repr(ex)}
 finally:
  raw.unlink(missing_ok=True);png.unlink(missing_ok=True)
rows=[]
with ThreadPoolExecutor(max_workers=4) as ex:
 futs=[ex.submit(one,e) for e in es]
 for i,f in enumerate(as_completed(futs),1):
  rows.append(f.result())
  if i%25==0:print('progress',i,'/',len(es),flush=True)
rows.sort(key=lambda x:x['entry']);report={'schema':'fairytale-requiem-grpe-wcg-thumbnail-audit-v1','archive':str(ARC),'archive_sha256':hashlib.sha256(ARC.read_bytes()).hexdigest().upper(),'entry_count':len(es),'ok':sum(x['status']=='ok' for x in rows),'rows':rows};(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');shutil.rmtree(TMP,ignore_errors=True);print(json.dumps({'entries':len(es),'ok':report['ok'],'out':str(OUT)},ensure_ascii=False))
