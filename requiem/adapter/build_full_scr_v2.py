from __future__ import annotations
import hashlib,json,shutil,sys
from datetime import datetime,timezone
from pathlib import Path
P=Path(r'P:\AI\Codex\projects\fairytale-requiem-ko')
sys.path.insert(0,str(P/'adapter'))
from xfl_tool import parse_archive,inspect_archive,repack_archive,write_json
OUT=P/'staging'/'scr_full_korean_v2'
if OUT.exists(): raise SystemExit(f'refusing existing output root: {OUT}')
TREE=OUT/'tree';shutil.copytree(P/'extracted'/'scr',TREE)
def h(q):return hashlib.sha256(q.read_bytes()).hexdigest().upper()
manifest_path=P/'audit'/'scr_xfl_manifest.json';srcman=json.loads(manifest_path.read_text(encoding='utf-8'))
source=P/'baseline'/'scr.roundtrip.xfl'
if h(source)!=srcman['archive']['sha256']:raise SystemExit('source archive hash mismatch')
source_entries={e['name']:e for e in srcman['entries']}
if set(x.name for x in TREE.iterdir() if x.is_file())!=set(source_entries):raise SystemExit('tree entry set mismatch')
for name,e in source_entries.items():
 if h(TREE/name)!=e['sha256']:raise SystemExit('extracted baseline hash mismatch '+name)
progress=json.loads((P/'audit'/'translation_progress.json').read_text(encoding='utf-8'))
translated={}
for row in progress['completed_files']:
 man_path=P/row['build_manifest']
 if h(man_path)!=row['build_manifest_sha256']:raise SystemExit('manifest binding mismatch '+row['file'])
 man=json.loads(man_path.read_text(encoding='utf-8')); stage=Path(man['files'][0]['output_path']);stage=stage if stage.is_absolute() else P/stage
 if h(stage)!=man['files'][0]['output_sha256']:raise SystemExit('stage output hash mismatch '+row['file'])
 shutil.copy2(stage,TREE/row['file']); translated[row['file']]=h(stage)
changed=[]
for name,e in source_entries.items():
 now=h(TREE/name)
 if now!=e['sha256']:changed.append(name)
if set(changed)!=set(translated):raise SystemExit('strict changed allowlist mismatch')
a=OUT/'scr.ko-full-v2-a.xfl';b=OUT/'scr.ko-full-v2-b.xfl'
ra=repack_archive(TREE,manifest_path,a);rb=repack_archive(TREE,manifest_path,b)
write_json(P/'audit'/'scr_ko_full_v2_repack_a.json',ra);write_json(P/'audit'/'scr_ko_full_v2_repack_b.json',rb)
if a.read_bytes()!=b.read_bytes():raise SystemExit('A/B mismatch')
report={'schema':'fairytale-requiem-scr-full-korean-build-v2','status':'PASS','completed_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'source':{'path':str(source),'sha256':h(source),'entry_count':len(source_entries)},'translation':{'progress_path':str(P/'audit'/'translation_progress.json'),'progress_sha256':h(P/'audit'/'translation_progress.json'),'global_validation_v2':str(P/'audit'/'scenario_global_independent_validation_v2.json'),'global_validation_v2_sha256':h(P/'audit'/'scenario_global_independent_validation_v2.json'),'translated_file_count':len(translated),'translated_unit_count':sum(x['reviewed_units'] for x in progress['completed_files'])},'outputs':{'a':{'path':str(a),'size':a.stat().st_size,'sha256':h(a)},'b':{'path':str(b),'size':b.stat().st_size,'sha256':h(b)},'byte_identical':True},'delta':{'changed_entry_count':len(changed),'changed_entries':sorted(changed),'unchanged_entry_count':len(source_entries)-len(changed),'strict_allowlist_exact':True},'checks':{'source_manifest_hash_matches':True,'extracted_tree_hashes_match_manifest':True,'translated_allowlist_exact':True,'a_b_rebuild_byte_identical':True}}
out=P/'audit'/'scr_ko_full_v2_build.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','changed_entries':len(changed),'output_size':a.stat().st_size,'output_sha256':h(a),'audit':str(out),'audit_sha256':h(out)},ensure_ascii=True,indent=2))
