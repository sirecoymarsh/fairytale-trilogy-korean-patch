from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CONTROL=re.compile(r"\^[A-Za-z][0-9]*")
KANA=re.compile(r"[\u3040-\u30ff]")
SPECS={
 "3300":{"draft":"3300_slots_00001_00003_draft.json","slots":set(range(1,4)),"lookup":set(range(4,111)),"lookup_range":[4,110],"range":[1,3],"corrections":{3:"스케치북을 읽을까?^n아니면 다른 곳을 둘러볼까?"}},
 "3301":{"draft":"3301_slots_00028_00042_draft.json","slots":set(range(28,43)),"lookup":set(range(1,27)),"lookup_range":[1,26],"range":[28,42],"corrections":{
  28:"앨리스와의 추억을 되짚어 보겠습니까?",31:"그레텔과의 추억을 되짚어 보겠습니까?",34:"오데트와 오딜의 추억을 되짚어 보겠습니까?",37:"라푼젤과의 추억을 되짚어 보겠습니까?",40:"게르다와의 추억을 되짚어 보겠습니까?"}},
 "3600":{"draft":"3600_slots_00001_00011_draft.json","slots":set(range(1,12)),"lookup":set(range(12,21)),"lookup_range":[12,20],"range":[1,11],"corrections":{9:"이제 가 봐야겠어.",11:"슬슬 다른 곳으로 가 볼까."}}
}
def shab(b):return hashlib.sha256(b).hexdigest().upper()
def slot(uid):return int(uid.rsplit("/",1)[1])
catalog={k:{} for k in SPECS}; lookups={k:set() for k in SPECS}
for line in (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8"):
 r=json.loads(line); stem=str(r.get("file","")).removesuffix(".gsc")
 if stem not in SPECS:continue
 i=int(r["slot"])
 if i in SPECS[stem]["slots"]:catalog[stem][i]=r
 if "lookup_keys" in r.get("lanes",[]):lookups[stem].add(i)
for stem,s in SPECS.items():
 draft_path=PROJECT/"packets"/"drafts"/s["draft"]; out=PROJECT/"packets"/"reviewed"/f"{stem}_all_translatable_slots_reviewed_once.json"; audit_path=PROJECT/"audit"/f"translation_review_{stem}_complete.json"
 if out.exists() or audit_path.exists():raise SystemExit(f"{stem} review exists; refusing second pass")
 d=json.loads(draft_path.read_text(encoding="utf-8"))
 if d.get("review_passes_completed")!=0:raise SystemExit(f"{stem} bad draft")
 entries={slot(e["uid"]):dict(e) for e in d["entries"]}
 if set(entries)!=s["slots"] or set(catalog[stem])!=s["slots"] or lookups[stem]!=s["lookup"]:raise SystemExit(f"{stem} coverage")
 changes=[]
 for i,t in s["corrections"].items():
  before=str(entries[i]["target_text"]); entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 final=[]
 for i in sorted(s["slots"]):
  e=entries[i]; src=str(e["source_text"]); tgt=str(e["target_text"]); c=catalog[stem][i]
  if src!=c["source_text"] or e["source_raw_sha256"]!=c["source_raw_sha256"]:raise SystemExit(f"{stem}:{i} source")
  if CONTROL.findall(src)!=CONTROL.findall(tgt):raise SystemExit(f"{stem}:{i} control")
  if KANA.search(tgt):raise SystemExit(f"{stem}:{i} kana")
  tgt.encode("cp949")
  e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 정확히 1회 문맥·문체·용어·제어 코드 검수 완료"})
  final.append(e)
 data={"schema":"fairytale-requiem-translation-map-v1","scope":f"{stem}_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":s["range"],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":s["lookup_range"],"release_ready":False,"entries":final}
 raw=(json.dumps(data,ensure_ascii=False,indent=2)+"\n").encode("utf-8");out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":data["scope"],"draft_inputs":[str(draft_path)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":s["range"],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"control_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True},"output_sha256":shab(raw)}
 audit_path.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({**audit,"audit_path":str(audit_path)},ensure_ascii=True))
