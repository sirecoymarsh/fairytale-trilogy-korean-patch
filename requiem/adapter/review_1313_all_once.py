from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");DRAFT=PROJECT/"packets"/"drafts"/"1313_slots_00001_00046_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
1:"점심 전, 나는 그레텔의 방을 찾아갔다.^n어젯밤 맡아 둔 카드 키를 상의하기 위해서다.",
3:"──그런 이유로.^n나는 이걸 사용해 탐험해 보려고 해.",
6:"내 생각을 밝히자^n그레텔의 눈이 반짝반짝 빛났다.",
8:"그래, 이건 나와 그레텔만의 비밀이야.^n시설 사람들은 물론 다른 환자 아이들에게도 비밀이야.",
9:"들켜서 직원에게 이것을 빼앗기면 아무 소용도 없다.",
10:"중요한 비밀이 밝혀져 우리 환자 모두에게^n도움이 되는 일임을 알게 되면 다들 그때^n털어놓자──나는 그렇게 결심했다.",
13:"『탐험』과 『비밀』이라는 말에 호기심을 자극받았는지,^n 그레텔은 밝은 얼굴로 연신 고개를 끄덕였다.",
14:"무언가를 먹을 때 말고 이렇게 즐거운 얼굴을 한^n그레텔은 처음 보는 것 같다.",
15:"코미야라는 사람과 얽힌 뒤로 싫은 일만 겪은^n그레텔에게 이것이 좋은 기분 전환이 되면 좋을 텐데.",
18:"후우…….^n좀처럼 못 찾겠네, 오빠…….",
19:"눈여겨본 곳을 돌아봐도^n이 카드 키를 쓸 만한 곳은 찾지 못했다.",
22:"처음의 활기는 어디로 갔는지,^n온몸의 뼈가 빠진 듯 주저앉은 그레텔의^n배꼽시계가 마침내 비명을 질렀다.",
24:"오늘은 여기까지 할까.^n조급해해도 소용없으니까.",
26:"(이렇게 되면 무슨 수를 써도 움직이지 않겠지……)",
28:"슬슬 점심시간이니,^n방으로 돌아가 밥을 먹으며 쉬자.",
31:"가벼운 걸음으로 복도를 걷는 그레텔을 따라가던 나는^n손에 든 카드에 요철이 있다는 것을 깨닫고 멈춰 섰다.",
32:"각도를 바꿔 바라보자 카드 뒷면에는^n돋을새김으로 스무 자리쯤 되는 번호와 함께^n알파벳이 새겨져 있었다.",
34:"『GUEST』…… 게스트였나?",
35:"그러니까 이 카드를 가지고 있던 코미야라는 남자는^n정말 의사가 아니라^n이 시설의 손님이라는 걸까?",
37:"(하지만 왜 시설을 찾아온 손님이^n 의사 차림으로 제멋대로 굴 수 있는 거지?)",
38:"직원들에게 너무 심하다는 주의를 받기는 했지만,^n그 사람이 이 시설에 있는 것 자체는 허락된 모양이다.",
39:"나는 그것을 납득할 수 없었고,^n그 이유도 전혀 짐작할 수 없었다.",
40:"왜일까.^n조금 전 복도에서 마주친 게르다의 텅 빈 표정이 갑자기 떠올라,^n마음이 몹시 술렁였다.",
41:"──그때 앞서 걷던 그레텔이 돌아보더니,^n깡충깡충 뛰면서 나를 향해 손짓했다.",
46:"나는 쓴웃음을 지으며 불길한 생각을 떨쳐 내고,^n그레텔의 뒤를 따라 다시 복도를 걷기 시작했다.",
}
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 draft=json.loads(DRAFT.read_text(encoding="utf-8"));expected=set(range(1,47))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1313_slots_00001_00046_draft":raise SystemExit("unexpected draft")
 entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]};changes=[]
 if set(entries)!=expected:raise SystemExit("draft coverage mismatch")
 for i,t in CORRECTIONS.items():
  before=str(entries[i]["target_text"]);entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 catalog={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1313.gsc":continue
   i=int(x["slot"])
   if i in expected:catalog[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(catalog)!=expected or lookup!=set(range(47,105)):raise SystemExit("catalog/lookup mismatch")
 final=[]
 for i in sorted(expected):
  e=entries[i];s,t=str(e["source_text"]),str(e["target_text"])
  if s!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]:raise SystemExit(f"source drift {i}")
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"});final.append(e)
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1313_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,46],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[47,104],"release_ready":False,"entries":final};out=PROJECT/"packets"/"reviewed"/"1313_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,46],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_47_104_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};ap=PROJECT/"audit"/"translation_review_1313_complete.json";ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
