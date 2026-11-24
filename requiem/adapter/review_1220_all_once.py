from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");DRAFT=PROJECT/"packets"/"drafts"/"1220_slots_00001_00087_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
9:"손이 있는 쪽을 들여다보고 처음 눈에 들어온 것은,^n찢겨 나가 아무렇게나 밀쳐져 있는^n책의 일부로 보이는 종이였다.",
15:"그 페이지를 뜯어낸 자리에 남은 톱니 모양 종잇조각 사이로,^n분홍색 실이 서툰 솜씨로 오가며,^n──다른 종이가 꿰매져 있다.",
19:"『왕자님과 앨리스는 맺어졌습니다.^n경사 났네, 경사 났어』",
22:"그때까지 침입자답게 숨을 죽이고 있었는데,^n어이없어하는 목소리가 힘껏 새어 나오고 말았다.",
28:"지독하게 낯간지럽고 간질거리며,^n스스로 그렇게 생각하는 것이 뻔뻔하게 느껴지지만,^n지금까지의 여러 일을 보면 거의 틀림없다고 생각한다.",
30:"(게다가 아마 이 『마음을 고백한다』는 건,^n 그 문제의 깜짝 행사와 관련이 있을 듯한……)",
36:"조금 전 내가 낸 어이없다는 목소리를 계기로,^n앨리스가 잠의 나라에서 돌아오고 말았다.",
50:"확실히 성서 옆에는 일기도 펼쳐져 있다.^n아무래도 성서의 새 페이지는^n이 일기에서 찢어 붙인 모양이다.",
56:"그런 건 하면 안 된다고 전하려고,^n해야 한다고 적어 둔 거예요.",
62:"──뭐, 됐어요.^n이렇게 한낮부터 졸음을 이기지 못한^n제 잘못도 있으니까요.",
69:"앨리스는 일기 아래 깔려 있던 종잇조각을^n거칠게 구겨 옆으로 밀치며 고개를 저었다.",
76:"며칠 전부터 앨리스가 뛰어다니며 준비한 무언가.^n아마 내게 하는 『고백』으로 이어질 무언가가,^n그 시각부터 마침내 시작되는 걸까.",
87:"익숙한 문을 바라보며,^n나는 좋은지 나쁜지 알 수 없는,^n그저 낯간지럽기만 한 예감에 사로잡혀 있었다.",
}
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 draft=json.loads(DRAFT.read_text(encoding="utf-8"));expected=set(range(1,88))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1220_slots_00001_00087_draft":raise SystemExit("unexpected draft")
 entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]};changes=[]
 if set(entries)!=expected:raise SystemExit("draft coverage mismatch")
 for i,t in CORRECTIONS.items():
  before=str(entries[i]["target_text"]);entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 catalog={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1220.gsc":continue
   i=int(x["slot"])
   if i in expected:catalog[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(catalog)!=expected or lookup!=set(range(88,146)):raise SystemExit("catalog/lookup mismatch")
 final=[]
 for i in sorted(expected):
  e=entries[i];s,t=str(e["source_text"]),str(e["target_text"])
  if s!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]:raise SystemExit(f"source drift {i}")
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"});final.append(e)
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1220_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,87],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[88,145],"release_ready":False,"entries":final};out=PROJECT/"packets"/"reviewed"/"1220_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,87],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_88_145_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};ap=PROJECT/"audit"/"translation_review_1220_complete.json";ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
