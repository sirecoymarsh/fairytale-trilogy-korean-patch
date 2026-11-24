from assets import *
from focus import fullpath
import subprocess
data=read('audit/index.json')
keys=[k for k in data['Encore'] if (k.startswith('grpo_cu/56') or k.startswith('grpo_cu/57') or k.startswith('grpo_bg/11') or k in ['grpe/3001.wcg','grpe/3002.wcg','grpe/3003.wcg']) and 'size' in data['Encore'][k]]
jobs=[]
for key in keys:
    dst=fullpath('Encore',key)
    if dst.exists():continue
    bank,name=key.split('/')
    org=source('Encore')/(bank+'.xfl');e=entry_map(org)[name]
    dst.parent.mkdir(exist_ok=True,parents=True)
    jobs.append('\t'.join(map(str,[org,e.absolute_offset,e.size,dst,0])))
if jobs:
    ts=ROOT/'audit/prop-jobs.tsv';ts.write_text('\n'.join(jobs),encoding='utf-8-sig')
    subprocess.run([str(ROOT/'tools/RasterBatch.exe'),str(ts)],check=True)
print([(k,data['Encore'][k]['size']) for k in keys])

