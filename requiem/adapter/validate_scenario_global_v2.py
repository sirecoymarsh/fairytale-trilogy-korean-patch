from __future__ import annotations
import hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
P=Path(r'P:\AI\Codex\projects\fairytale-requiem-ko')
sys.path.insert(0,str(P/'adapter'))
from gsc_codec import parse_gsc,rebuild_gsc
UID=re.compile(r'^scr\.xfl::([^:]+\.gsc)::slot/([0-9]+)$',re.I)
CARET=re.compile(r'\^(?:g[0-9]{3}|d[0-9]+|s[0-9]+|cy|ck|n|m)')
RUBY=re.compile(r'\|([^\[\]\|]+)\[([^\[\]\|]+)\]')
FIXTURE=('1001.gsc',10)
def hbytes(b):return hashlib.sha256(b).hexdigest().upper()
def hfile(q):return hbytes(q.read_bytes())
progress_path=P/'audit'/'translation_progress.json'
progress=json.loads(progress_path.read_text(encoding='utf-8'))
fail=[]; files=[]; total=0; ruby=[]; suspicious=[]
for row in progress['completed_files']:
 fn=row['file']; mp=P/row['review_map']; mf=P/row['build_manifest']
 fd={'file':fn,'status':'PASS','checks':{}}
 if hfile(mp)!=row['review_map_sha256']: fail.append(f'{fn}: map hash binding')
 if hfile(mf)!=row['build_manifest_sha256']: fail.append(f'{fn}: manifest hash binding')
 m=json.loads(mp.read_text(encoding='utf-8')); man=json.loads(mf.read_text(encoding='utf-8'))
 if man['translation_map']['sha256']!=hfile(mp):fail.append(f'{fn}: manifest map hash')
 entry_by_slot={};
 for e in m['entries']:
  mm=UID.fullmatch(e['uid']);
  if not mm or mm.group(1).lower()!=fn.lower():fail.append(f'{fn}: bad uid {e.get("uid")}');continue
  slot=int(mm.group(2));
  if slot in entry_by_slot:fail.append(f'{fn}: duplicate slot {slot}')
  entry_by_slot[slot]=e
 stage=Path(man['files'][0]['output_path']); stage=stage if stage.is_absolute() else P/stage; source=P/'extracted'/'scr'/fn
 sb=source.read_bytes();tb=stage.read_bytes(); sp=parse_gsc(sb);tp=parse_gsc(tb)
 if rebuild_gsc(sp,sp.strings)!=sb:fail.append(f'{fn}: source no-change roundtrip')
 if sp.command!=tp.command:fail.append(f'{fn}: command drift')
 if sp.trailing!=tp.trailing:fail.append(f'{fn}: trailing drift')
 if len(sp.strings)!=len(tp.strings):fail.append(f'{fn}: slot count drift')
 changed=[]
 for i,(a,b) in enumerate(zip(sp.strings,tp.strings)):
  if a!=b:changed.append(i)
  if i in entry_by_slot:
   e=entry_by_slot[i]; s=e['target_text']; total+=1
   try:enc=s.encode('cp949','strict')
   except Exception as ex:fail.append(f'{fn}/{i}: cp949 {ex}');continue
   if b!=enc:fail.append(f'{fn}/{i}: staged bytes differ from target')
   src=e['source_text']
   if CARET.findall(src)!=CARET.findall(s):fail.append(f'{fn}/{i}: caret sequence')
   if '\x00' in s or '\ufffd' in s:fail.append(f'{fn}/{i}: NUL/replacement')
   matches=list(RUBY.finditer(s)); rem=RUBY.sub('',s)
   if any(c in rem for c in '|[]'):fail.append(f'{fn}/{i}: malformed/stray ruby markup {ascii(s)}')
   if matches:
    ruby.append({'file':fn,'slot':i,'count':len(matches),'target':s})
    if (fn,i)!=FIXTURE or len(matches)!=3:fail.append(f'{fn}/{i}: undocumented ruby markup')
   elif (fn,i)==FIXTURE:fail.append(f'{fn}/{i}: documented ruby fixture missing')
   low=s.lower()
   if '```' in s or re.search(r'(?:json|thought)\s*[\}\{]',low) or re.search(r'[\}\]]\s*[\}`]{2,}',s):
    suspicious.append({'file':fn,'slot':i,'target':s});fail.append(f'{fn}/{i}: model-response contamination')
  elif a!=b:fail.append(f'{fn}/{i}: non-target slot changed')
 if set(changed)!=set(entry_by_slot):fail.append(f'{fn}: changed slot set mismatch')
 fd['target_units']=len(entry_by_slot);fd['source_sha256']=hbytes(sb);fd['stage_sha256']=hbytes(tb);fd['map_sha256']=hfile(mp);fd['manifest_sha256']=hfile(mf);fd['changed_slot_set_exact']=set(changed)==set(entry_by_slot)
 files.append(fd)
if len(files)!=233:fail.append(f'file count {len(files)} != 233')
if total!=29376:fail.append(f'unit count {total} != 29376')
if [(x['file'],x['slot'],x['count']) for x in ruby] != [('1001.gsc',10,3)]:fail.append('global ruby fixture set mismatch')
status='PASS' if not fail else 'FAIL'
report={'schema':'fairytale-requiem-scenario-global-independent-validation-v2','status':status,'completed_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'progress':{'path':str(progress_path),'sha256':hfile(progress_path)},'counts':{'files':len(files),'target_units':total},'strict_markup':{'documented_ruby_fixture':ruby,'suspicious_model_response_targets':suspicious,'no_stray_pipe_or_brackets':not any('malformed/stray' in x for x in fail)},'failures':fail,'files':files}
out=P/'audit'/'scenario_global_independent_validation_v2.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':status,'files':len(files),'target_units':total,'ruby_targets':len(ruby),'suspicious_targets':len(suspicious),'failure_count':len(fail),'audit':str(out),'audit_sha256':hfile(out)},ensure_ascii=True,indent=2))
if fail:
 for x in fail[:50]:print(x)
 raise SystemExit(1)

