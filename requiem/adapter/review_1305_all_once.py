from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");DRAFT=PROJECT/"packets"/"drafts"/"1305_slots_00001_00023_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
4:"무언가를 조용히, 하지만 강하게 호소해 오는 그 한마디에,^n나는 가슴이 꽉 조이는 듯한^n애달픈 기분을 느끼지 않을 수 없었다.",
7:"미소 속에 비친 쓸쓸한 기색이 마음에 걸렸다.^n왠지 자기 자신은 포기해 버린 듯한──^n그런 느낌마저 든다.",
8:"그래, 얼마 전까지 무슨 수를 써서라도 이 『낙원』에서 빠져나가려던^n강한 의지나 패기 같은 것이 부족한 듯한──^n달리 말하면 『그림자』가 옅어진 듯한──",
10:"(이상한 생각은 그만하자)",
14:"떨쳐 냈다고 생각한 불길한 기운은^n아무래도 잠 속까지 나를 따라온 모양이다.",
16:"(그만둬, 그녀에게만은 손대지 마!)",
17:"나는 외쳤다. 발버둥 쳤다.",
20:"그녀만은 더러운 일이나 괴로운 일에서 멀리하게 해 주고 싶었다.",
23:"무력감에 짓눌려,^n내 마음은 깊고 깊은 어둠 밑바닥으로 추락해 간다──",
}
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 draft=json.loads(DRAFT.read_text(encoding="utf-8"));expected=set(range(1,24))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1305_slots_00001_00023_draft":raise SystemExit("unexpected draft")
 entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]};changes=[]
 if set(entries)!=expected:raise SystemExit("draft coverage mismatch")
 for i,t in CORRECTIONS.items():
  before=str(entries[i]["target_text"]);entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 catalog={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1305.gsc":continue
   i=int(x["slot"])
   if i in expected:catalog[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(catalog)!=expected or lookup!=set(range(24,82)):raise SystemExit("catalog/lookup mismatch")
 final=[]
 for i in sorted(expected):
  e=entries[i];s,t=str(e["source_text"]),str(e["target_text"])
  if s!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]:raise SystemExit(f"source drift {i}")
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"});final.append(e)
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1305_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,23],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[24,81],"release_ready":False,"entries":final};out=PROJECT/"packets"/"reviewed"/"1305_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,23],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_24_81_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};ap=PROJECT/"audit"/"translation_review_1305_complete.json";ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
