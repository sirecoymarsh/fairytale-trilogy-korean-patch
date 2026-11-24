from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");DRAFT=PROJECT/"packets"/"drafts"/"1311_slots_00001_00022_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
1:"그레텔의 방에서 돌아온 나는^n그 아이가 주운 카드 키 같은 물건을^n어둠 속에서 유심히 바라보고 있었다.",
4:"(역시……^n 원래라면 직원에게 돌려줘야겠지)",
5:"기억을 잃고도 내 안에 남아 있던 이성과 상식은^n적어도 그렇게 주장하고 있었다.",
6:"하지만 동시에 다른 생각이^n내 마음속에서 고개를 들고 있었다.",
9:"그것은 그저 장난기라고 해야 할지도 모른다.",
10:"무엇을 할 자유도 없이 이 『낙원』에 갇힌^n울분의 반동이라고 한다면 부정할 수 없었다.",
11:"하지만 그 감정을^n또 한 명의 『나』가 정당화하려 한다.",
13:"(이 시설은 우리에게 뭔가를 숨기고 있어.^n 이 열쇠가 있으면 그게 뭔지 알아낼 수 있을지도 몰라)",
14:"무언가 수상한 목적으로 운영되는 시설의 비밀을 캐는 일은^n수용된 환자의 당연한 권리라는 나 나름의 논리.",
15:"허점투성이라 해도 결국 내가 납득하면 그만이다.",
17:"(애초에 머리가 이상하다는 이유로 여기 있는 거야.^n 이왕이면 정신 나간 환자다운 짓을 해 보자)",
18:"그런 자학에 가까운 생각마저 내 등을 떠밀었다.",
21:"지금까지 시설을 돌아다니며^n수상해 보인다고 생각한 곳들을 떠올렸다.",
22:"탐색해야 할 『정당한 이유』는 제쳐 두고,^n내 마음은 장난기로 잔뜩 부풀어^n들뜨지 않을 수 없었다.",
}
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 draft=json.loads(DRAFT.read_text(encoding="utf-8"));expected=set(range(1,23))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1311_slots_00001_00022_draft":raise SystemExit("unexpected draft")
 entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]};changes=[]
 if set(entries)!=expected:raise SystemExit("draft coverage mismatch")
 for i,t in CORRECTIONS.items():
  before=str(entries[i]["target_text"]);entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 catalog={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1311.gsc":continue
   i=int(x["slot"])
   if i in expected:catalog[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(catalog)!=expected or lookup!=set(range(23,81)):raise SystemExit("catalog/lookup mismatch")
 final=[]
 for i in sorted(expected):
  e=entries[i];s,t=str(e["source_text"]),str(e["target_text"])
  if s!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]:raise SystemExit(f"source drift {i}")
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"});final.append(e)
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1311_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,22],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[23,80],"release_ready":False,"entries":final};out=PROJECT/"packets"/"reviewed"/"1311_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,22],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_23_80_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};ap=PROJECT/"audit"/"translation_review_1311_complete.json";ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
