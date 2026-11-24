from __future__ import annotations
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
P=Path(r'P:\AI\Codex\projects\fairytale-requiem-ko')
path=P/'audit'/'translation_progress.json'
backup=P/'staging'/'runtime_text_format_repair_v1'/'translation_progress_before.json'
shutil.copy2(path,backup)
def h(q): return hashlib.sha256(q.read_bytes()).hexdigest().upper()
d=json.loads(path.read_text(encoding='utf-8'))
changed=[]
for row in d['completed_files']:
 if row['file'].removesuffix('.gsc') not in {'1614','1701','1702','1728'}: continue
 mp=P/row['review_map']; mf=P/row['build_manifest']
 before={'review_map_sha256':row['review_map_sha256'],'build_manifest_sha256':row['build_manifest_sha256']}
 row['review_map_sha256']=h(mp); row['build_manifest_sha256']=h(mf)
 changed.append({'file':row['file'],'before':before,'after':{'review_map_sha256':row['review_map_sha256'],'build_manifest_sha256':row['build_manifest_sha256']}})
d['updated_utc']=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
d.setdefault('post_review_runtime_repairs',[]).append({'id':'runtime_text_format_repair_v1','repair_count':7,'audit':'audit/scenario_runtime_text_format_repairs_v1.json','updated_files':[x['file'] for x in changed]})
path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report={'schema':'fairytale-requiem-progress-runtime-repair-update-v1','status':'PASS','changed':changed,'progress_sha256':h(path),'backup':str(backup)}
out=P/'audit'/'translation_progress_runtime_repair_update_v1.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','changed_files':len(changed),'progress_sha256':h(path),'audit':str(out)},ensure_ascii=True,indent=2))
