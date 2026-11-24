from __future__ import annotations
import hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path

P = Path(r'P:\AI\Codex\projects\fairytale-requiem-ko')
OUT = P/'staging'/'runtime_text_format_repair_v1'
BACKUP = OUT/'maps_before'
AUDIT = P/'audit'/'scenario_runtime_text_format_repairs_v1.json'
if OUT.exists():
    raise SystemExit(f'refusing existing output root: {OUT}')
BACKUP.mkdir(parents=True)

def h(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

specs = {
 ('1614', 9): ('멈춰줘, 제발 멈춰줘.^n나는 그런 식[]이 되고 싶지 않은데.', '멈춰줘, 제발 멈춰줘.^n나는 그런 식이 되고 싶지 않은데.'),
 ('1614', 12): ('나를, 내가 아닌 무언가[]로 바꾸어 놓는다.', '나를, 내가 아닌 무언가로 바꾸어 놓는다.'),
 ('1614', 16): ('그럴 리 없어.^n나는 그런 식[]이 되고 싶지 않아.', '그럴 리 없어.^n나는 그런 식이 되고 싶지 않아.'),
 ('1701', 251): ("『──힘내.^n──포기하지 마, 오빠』'}]}```json}```json{", '『──힘내.^n──포기하지 마, 오빠』'),
 ('1702', 70): ('라기보다, 자세히 생각해보면 처음부터 그런 건 없었다.^n없는 것이 정상[]이다.^n그것은 "만약의 세계"에만 마련된 것일 테다.', '라기보다, 자세히 생각해 보면 처음부터 그런 건 없었다.^n없는 것이 정상이다.^n그것은 「만약의 세계」에만 마련된 것일 테다.'),
 ('1728', 81): ("대부분의 의사를 '적'으로 간주하는 게르다지만,^n환자[게르다]의 말을 비교적 성실하게 들어주는^n그에 대해서는 판단을 유보하고 있다.", '대부분의 의사를 「적」으로 여기는 게르다지만,^n게르다의 말을 비교적 진지하게 들어 주는^n그에 대해서는 판단을 유보하고 있다.'),
 ('1728', 155): ('알고 있어.^n너희가 더럽히고 더럽혀서, 엉망진창으로 바꿔 놓았으니까.^n지금은 [], 네버랜드가 아니지.', '알고 있어.^n너희가 더럽히고 또 더럽혀서, 엉망진창으로 바꾸어 놓았으니까.^n지금은 네버랜드가 아니지.'),
}
by_stem = {}
for key,val in specs.items(): by_stem.setdefault(key[0],{})[key[1]]=val
records=[]
for stem, fixes in sorted(by_stem.items()):
    path=P/'packets'/'reviewed'/f'{stem}_all_translatable_slots_reviewed_once.json'
    shutil.copy2(path, BACKUP/path.name)
    before_hash=h(path)
    data=json.loads(path.read_text(encoding='utf-8'))
    seen=set()
    for entry in data['entries']:
        slot=int(entry['uid'].rsplit('/',1)[1])
        if slot not in fixes: continue
        before,after=fixes[slot]
        if entry['target_text']!=before:
            raise SystemExit(f'expected-before mismatch {stem}/{slot}: '+ascii(entry['target_text']))
        after.encode('cp949','strict')
        entry['target_text']=after
        entry['notes']=entry.get('notes','')+'; post-review runtime format repair v1'
        seen.add(slot)
        records.append({'file':f'{stem}.gsc','slot':slot,'uid':entry['uid'],'before':before,'after':after,'reason':'remove malformed ruby/markup or model-response contamination detected by runtime/static audit'})
    if seen!=set(fixes): raise SystemExit(f'missing slots {stem}: {sorted(set(fixes)-seen)}')
    data.setdefault('post_review_repairs',[]).append({'id':'runtime_text_format_repair_v1','completed_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'slots':sorted(fixes),'reason':'runtime text-format-error investigation and strict target markup audit'})
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    after_hash=h(path)
    for rec in records:
        if rec['file']==f'{stem}.gsc': rec['map_before_sha256']=before_hash;rec['map_after_sha256']=after_hash
    # Keep resumable Gemma state aligned with corrected reviewed output, without rewriting historical drafts.
    state_candidates=list((P/'staging').glob(f'gemma_*/state/{stem}.json'))
    for state in state_candidates:
        sd=json.loads(state.read_text(encoding='utf-8'))
        changed=[]
        reviewed=sd.get('reviewed',{})
        for slot,(before,after) in fixes.items():
            k=str(slot)
            if reviewed.get(k)==before:
                reviewed[k]=after;changed.append(slot)
        if changed:
            sd.setdefault('post_review_repairs',[]).append({'id':'runtime_text_format_repair_v1','slots':sorted(changed)})
            state.write_text(json.dumps(sd,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report={'schema':'fairytale-requiem-scenario-runtime-text-format-repairs-v1','status':'PASS','completed_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'repair_count':len(records),'records':records,'backup_root':str(BACKUP)}
AUDIT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','repair_count':len(records),'audit':str(AUDIT),'audit_sha256':h(AUDIT),'backup_root':str(BACKUP)},ensure_ascii=True,indent=2))
