from __future__ import annotations
import hashlib,json,shutil
from datetime import datetime,timezone,timedelta
from pathlib import Path
P=Path(r'P:\AI\Codex\projects\fairytale-requiem-ko')
SRC=P/'runtime'/'final_ko_rc2';DST=P/'runtime'/'final_ko_build_v1';A=P/'audit'
KST=timezone(timedelta(hours=9))
def sha(p:Path):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest().upper()
def manifest(root:Path):
 fs=sorted((x for x in root.rglob('*') if x.is_file()),key=lambda x:x.relative_to(root).as_posix().casefold());out=[]
 for i,p in enumerate(fs,1):
  rec={'path':p.relative_to(root).as_posix(),'size':p.stat().st_size,'sha256':sha(p)};out.append(rec);print(f'HASH {i:02d}/{len(fs):02d} {rec["path"]}',flush=True)
 return out
def loadpass(name,allowed=('PASS','PASS_RESOLVED')):
 p=A/name;d=json.loads(p.read_text(encoding='utf-8-sig'))
 if d.get('status') not in allowed:raise RuntimeError(f'{name} status {d.get("status")}')
 return {'path':str(p),'sha256':sha(p),'status':d.get('status')}
if not SRC.is_dir():raise RuntimeError('RC2 missing')
if DST.exists():raise RuntimeError(f'refusing existing final root: {DST}')
source=manifest(SRC);sm={x['path']:x for x in source}
if len(source)!=52:raise RuntimeError(f'unexpected file count {len(source)}')
if sm['scr.xfl']['sha256']!='6D25F45A83AAA9A009130ED9C258327A241BE4FC724AF9C737FF1B8A0DAF24A7':raise RuntimeError('scr mismatch')
# Bound user-requested complete saves must be exact copies of the installed original.
game_root=next((P for P in Path(r'Y:\GAME\H Games\FairyTale Requiem').iterdir() if P.is_dir() and (P/'save').is_dir()))
for n in ('FRsave.dat','FRsave01.dat','FRsave01.wcg'):
 rel=f'save/{n}';orig=game_root/'save'/n
 if sha(orig)!=sm[rel]['sha256']:raise RuntimeError(f'test save drift: {n}')
audits={
 'scenario':loadpass('scenario_global_independent_validation_v3_layout.json'),
 'layout_repairs':loadpass('scenario_layout_overflow_repairs_v1.json'),
 'text_error_resolution':loadpass('final_ko_rc2_text_format_error_resolution.json'),
 'save_metadata':loadpass('grps_save_metadata_korean_v1_independent_validation.json'),
 'sensitive_bundle':loadpass('sensitive_review_bundle_v3_layout_independent_validation.json'),
 'target_kana_scan':loadpass('scenario_target_kana_scan_v1.json',('PASS_NO_KANA',)),
 'target_cjk_scan':loadpass('scenario_target_cjk_ideograph_scan_v1.json',('PASS_NO_IDEOGRAPHS',)),
}
print('COPY final build',flush=True);shutil.copytree(SRC,DST,copy_function=shutil.copy2)
dest=manifest(DST);dm={x['path']:x for x in dest}
if source!=dest:raise RuntimeError('copy manifest differs from frozen RC2')
now=datetime.now(KST).isoformat(timespec='seconds')
report={
 'schema':'fairytale-requiem-final-korean-standalone-build-v1','created_at_kst':now,
 'status':'PASS_FINAL_BUILD_READY_FOR_USER_REVIEW','delivery_stage':'FINAL_STANDALONE_BUILD_BEFORE_PATCH',
 'patch_packaging':'DEFERRED_BY_USER_UNTIL_AFTER_FINAL_BUILD_REVIEW',
 'source_candidate':str(SRC),'final_root':str(DST),'file_count':len(dest),'total_bytes':sum(x['size'] for x in dest),
 'byte_identical_to_rc2':True,'scr_xfl_sha256':dm['scr.xfl']['sha256'],
 'coverage':{'scenario_files':233,'translation_units':29376,'remaining_layout_overflows':0,'remaining_kana_targets':0,'remaining_cjk_ideograph_targets':0,'save_metadata_assets':652,'sensitive_review_files':82,'sensitive_review_slots':13771},
 'runtime_qa':{
  'status':'PASS_RUNTIME_WITH_USER_CONFIRMATION',
  'text_format_error':'RESOLVED; 64 automated actions, zero error modals, clean exit; user confirmed no error',
  'title_menu_logo_opening_gallery_settings_dialogue':'PROVEN_IN_RUNTIME; payload hashes are unchanged in this final build',
  'save_load_heading':'PROVEN_KOREAN_IN_RUNTIME',
  'save_slot_metadata':'PASS_PERSISTED_ASSET_VALIDATION; runtime capture below the DirectDraw clip line was unavailable in the current desktop layout',
  'evidence':['audit/final_ko_rc2_text_format_error_resolution.json','evidence/runtime/final_game_qa/01_title_menu_final.png','evidence/runtime/final_game_qa/rc1_02_gallery_hub_screen.png','evidence/runtime/final_game_qa/rc2_dialogue_full_visible.png','evidence/runtime/final_ko_rc2/save_load_metadata/rc2_continue_screen_runtime_v3.png']
 },
 'test_saves':{'included':True,'exact_from_installed_original':True,'later_patch_policy':'EXCLUDE','files':[dm[f'save/{n}'] for n in ('FRsave.dat','FRsave01.dat','FRsave01.wcg')]},
 'deferred_or_preserved':{'kinetic_cutin_text':'DEFERRED_BY_USER_FOR_LATER_INCREMENTAL_WORK','original_staff_credits':'PRESERVED','ending_credit_movies':'PRESERVED','patch':'DEFERRED'},
 'bound_audits':audits,'sensitive_review_bundle':str(P/'review_sensitive_content_final_ko_v3_layout'),'files':dest
}
out=A/'final_ko_build_v1_manifest.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'final_root':str(DST),'file_count':len(dest),'total_bytes':report['total_bytes'],'scr_sha256':report['scr_xfl_sha256'],'manifest':str(out),'manifest_sha256':sha(out)},ensure_ascii=False,indent=2),flush=True)
