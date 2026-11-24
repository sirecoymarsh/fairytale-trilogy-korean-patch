from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");DRAFT=PROJECT/"packets"/"drafts"/"1312_slots_00001_00022_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
1:"카드 키의 용도를^n늦은 밤까지 궁리하던 나는^n날이 밝아도 침대에서 꾸벅꾸벅 졸고 있었다.",
3:"갑자기 그 뻐꾸기시계 같은 소리가 울리기 시작해^n나는 황급히 침대에서 벌떡 일어났다.",
5:"(또 이 소리야.^n 이제 정말 그만했으면 좋겠어……)",
7:"처음에는 멍하니 있었고,^n무슨 일이 벌어질까 하는 호기심까지 더해져^n그곳에 비치는 것을 보았다.",
8:"하지만 그곳에 비치는 것은^n언제나 어김없이 여자아이들의 부끄러운 모습이었다.",
9:"대부분은 진찰 장면이었지만,^n도저히 평범한 진찰로 보이지 않았다.",
10:"그래, 그레텔을 대할 때의^n코미야라는 그 의사와 똑같은 얼굴을 하고^n여자아이들의 몸을 더듬고 있다.",
11:"중간까지 본 라푼젤의 영상은^n진찰조차 아니었던 것 같다.",
12:"그것을 엿보는 건 그녀들에게 미안한 느낌이 들어^n요즘 나는 이 소리가 날 때마다 방을 나서고 있었다.",
16:"그런데도──^n내 심장은 두근두근 요란하게 울렸다.",
19:"가슴속이 왠지 답답하고,^n무겁고 괴로운 무언가가 빙빙 도는 듯한 기분이 들었다.",
22:"내 안에서 고개를 드는 그 감정의 이름을^n나는 아직 몰랐다.",
}
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 draft=json.loads(DRAFT.read_text(encoding="utf-8"));expected=set(range(1,23))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1312_slots_00001_00022_draft":raise SystemExit("unexpected draft")
 entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]};changes=[]
 if set(entries)!=expected:raise SystemExit("draft coverage mismatch")
 for i,t in CORRECTIONS.items():
  before=str(entries[i]["target_text"]);entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 catalog={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1312.gsc":continue
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
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1312_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,22],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[23,80],"release_ready":False,"entries":final};out=PROJECT/"packets"/"reviewed"/"1312_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,22],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_23_80_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};ap=PROJECT/"audit"/"translation_review_1312_complete.json";ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
