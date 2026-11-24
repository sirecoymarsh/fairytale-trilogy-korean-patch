from __future__ import annotations
import copy,hashlib,json,shutil
from datetime import datetime,timedelta,timezone
from pathlib import Path
P=Path(r'P:\AI\Codex\projects\fairytale-requiem-ko')
BASE=P/'runtime'/'final_ko_rc1';CAND=P/'runtime'/'final_ko_rc2';AUD=P/'audit'
BASE_MAN=AUD/'final_ko_rc1_manifest.json';SCR_BUILD=AUD/'scr_ko_full_v3_layout_build.json';SCR_SRC=P/'staging'/'scr_full_korean_v3_layout'/'scr.ko-full-v3-layout-a.xfl'
KST=timezone(timedelta(hours=9));NOW=datetime.now(KST).isoformat(timespec='seconds')
def h(path,chunk=8*1024*1024):
 q=hashlib.sha256()
 with path.open('rb') as f:
  while True:
   b=f.read(chunk)
   if not b:break
   q.update(b)
 return q.hexdigest().upper()
def rows(root):
 out=[];fs=sorted((x for x in root.rglob('*') if x.is_file()),key=lambda x:x.relative_to(root).as_posix().casefold())
 for i,x in enumerate(fs,1):
  rel=x.relative_to(root).as_posix();dig=h(x);out.append({'path':rel,'size':x.stat().st_size,'sha256':dig});print(f'HASH {i:03d}/{len(fs):03d} {rel} {x.stat().st_size} {dig}',flush=True)
 return out
def wj(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if not BASE.is_dir():raise SystemExit('RC1 base missing')
if CAND.exists():raise SystemExit(f'refusing existing RC2 root: {CAND}')
base_manifest=json.loads(BASE_MAN.read_text(encoding='utf-8'))
if base_manifest['status']!='PASS_STATIC_RUNTIME_PENDING':raise SystemExit('RC1 manifest status mismatch')
expected={x['path']:x for x in base_manifest['files']}
print('PHASE validate_rc1_base',flush=True);base_rows=rows(BASE);base_map={x['path']:x for x in base_rows}
base_drift=[]
for rel in sorted(set(base_map)|set(expected),key=str.casefold):
 if base_map.get(rel)!=expected.get(rel):base_drift.append({'path':rel,'manifest':expected.get(rel),'current':base_map.get(rel)})
non_save_drift=[x for x in base_drift if not x['path'].startswith('save/')]
if non_save_drift:raise SystemExit(f'RC1 non-save files differ from bound manifest: {non_save_drift}')
scr_report=json.loads(SCR_BUILD.read_text(encoding='utf-8'))
if scr_report['status']!='PASS' or h(SCR_SRC)!=scr_report['outputs']['a']['sha256']:raise SystemExit('scr v3 build binding mismatch')
print('PHASE copy_rc1_to_rc2',flush=True);shutil.copytree(BASE,CAND,copy_function=shutil.copy2)
shutil.copy2(SCR_SRC,CAND/'scr.xfl')
print('PHASE manifest_rc2',flush=True);cand_rows=rows(CAND);cand_map={x['path']:x for x in cand_rows}
if set(base_map)!=set(cand_map):raise SystemExit('RC2 path set drift')
delta=[]
for rel in sorted(base_map,key=str.casefold):
 if base_map[rel]!=cand_map[rel]:delta.append({'path':rel,'before':base_map[rel],'after':cand_map[rel]})
if [x['path'] for x in delta]!=['scr.xfl']:raise SystemExit(f'RC2 delta is not scr-only: {[x["path"] for x in delta]}')
if cand_map['scr.xfl']['sha256']!=scr_report['outputs']['a']['sha256']:raise SystemExit('RC2 scr hash mismatch')
static_v3=AUD/'scenario_global_independent_validation_v3_layout.json';layout_rep=AUD/'scenario_layout_overflow_repairs_v1.json'
for q in (static_v3,layout_rep):
 j=json.loads(q.read_text(encoding='utf-8'))
 if j['status']!='PASS':raise SystemExit(f'bound static audit failed: {q.name}')
saves=[x for x in cand_rows if x['path'].startswith('save/')]
manifest={'schema':'fairytale-requiem-final-build-candidate-v2','created_at_kst':NOW,'status':'PASS_STATIC_RUNTIME_PENDING','delivery_stage':'FINAL_BUILD_CANDIDATE_ONLY','patch_packaging':'DEFERRED_UNTIL_FINAL_BUILD_RUNTIME_APPROVAL','base':{'root':str(BASE),'manifest':str(BASE_MAN),'manifest_sha256':h(BASE_MAN),'file_count':len(base_rows),'allowed_runtime_save_drift':base_drift},'candidate_root':str(CAND),'file_count':len(cand_rows),'total_bytes':sum(x['size'] for x in cand_rows),'delta_from_rc1':{'changed_file_count':len(delta),'strict_allowlist':['scr.xfl'],'strict_allowlist_exact':True,'files':delta},'scenario':{'scr_build':str(SCR_BUILD),'scr_build_sha256':h(SCR_BUILD),'scr_sha256':cand_map['scr.xfl']['sha256'],'global_validation_v3':str(static_v3),'global_validation_v3_sha256':h(static_v3),'layout_repair_audit':str(layout_rep),'layout_repair_audit_sha256':h(layout_rep),'script_files':233,'translation_units':29376,'layout_overflow_repairs':465,'remaining_layout_overflows':0},'test_save_files':{'included_for_user_runtime_test':True,'count':len(saves),'later_patch_payload_policy':'EXCLUDE','files':saves},'runtime_qa':'PENDING','files':cand_rows}
out=AUD/'final_ko_rc2_manifest.json';wj(out,manifest)
inv=copy.deepcopy(json.loads((AUD/'surface_inventory_v2.json').read_text(encoding='utf-8')))
inv['schema']='fairytale-requiem-surface-inventory-v3';inv['created_at_kst']=NOW;inv['bound_candidate']={'root':str(CAND),'manifest':str(out),'manifest_sha256':h(out),'status':'PASS_STATIC_RUNTIME_PENDING'};inv['overall']='PASS_STATIC_RUNTIME_PENDING'
for lane in inv['lanes']:
 if lane['id']=='scenario_core':
  lane['coverage']={'script_files':233,'translation_units':29376,'layout_overflow_count':0};lane['evidence']=['audit/scenario_global_independent_validation_v3_layout.json','audit/scr_ko_full_v3_layout_build.json'];lane['status']='PASS_STATIC_RUNTIME_PENDING'
 if lane['id']=='scenario_runtime_format_repairs':
  lane['surface']='잘못된 마크업 7건 및 네 줄 자동 줄바꿈으로 반복되던 텍스트 형식 오류 465건';lane['coverage']={'malformed_markup_repairs':7,'dialogue_layout_repairs':465,'automatic_reflows':430,'concise_rewrites':35,'remaining_layout_overflows':0};lane['evidence']=['audit/scenario_runtime_text_format_repairs_v1.json','audit/scenario_layout_overflow_repairs_v1.json','audit/scenario_global_independent_validation_v3_layout.json'];lane['status']='PASS_STATIC_RUNTIME_PENDING'
 if lane['id']=='runtime_gate':lane['storage']=str(CAND);lane['status']='PENDING'
wj(AUD/'surface_inventory_v3.json',inv)
print(json.dumps({'status':'PASS_STATIC_RUNTIME_PENDING','candidate_root':str(CAND),'file_count':len(cand_rows),'total_bytes':sum(x['size'] for x in cand_rows),'changed_files':[x['path'] for x in delta],'scr_sha256':cand_map['scr.xfl']['sha256'],'manifest':str(out),'manifest_sha256':h(out),'surface_inventory':str(AUD/'surface_inventory_v3.json')},ensure_ascii=False,indent=2),flush=True)
