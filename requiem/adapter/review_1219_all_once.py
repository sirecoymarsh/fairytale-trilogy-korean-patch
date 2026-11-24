from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");DRAFT=PROJECT/"packets"/"drafts"/"1219_slots_00001_00111_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
2:"여전하다고 해야 할지,^n특별히 신경 쓰이는 일은 없습니다.",
6:"처음에는 제자리걸음인 상황이 답답했지만,^n이제 슬슬 아무래도 상관없어지고 있다.",
10:"어떤 사정이 있든 그것은,^n모든 것을 떠올리고 돌아가야 할 곳으로 돌아가는 일이^n반드시 행복으로 이어지지는 않음을 보여 주는 듯했다.",
21:"앨리스니까^n분명 나쁜 뜻은 없다고 생각하지만,^n그, 무슨 일을 당할지 몰라 불안해서요…….",
31:"그러니까, 아, 흐음…….^n뭐, 신경 쓰지 않아도 되지 않겠니.",
45:"아아, 이거 곤란하군. 비밀은 포박을 푸는 솜씨가 좋네.^n스르르 밧줄을 풀고 매끄럽게 목구멍을 빠져나왔어.",
47:"너, 네 귓속에 손가락을 넣으면,^n고막을 떨게 하기 전에 붙잡을 수 있을지도 몰라.^n못 들은 일로 해 줄 수 있겠니?",
53:"잘 표현할 수는 없지만 앨리스만큼 본격적이지는 않은 듯하다.^n어쩐지 어른의 딱딱한 머리로 온 힘을 다해^n앨리스 흉내를 내는 것 같다.",
61:"깜짝 행사는 몰라야 성립하는 법이야.^n그러니까 몰랐던 일이 되게 해.^n아무것도 모르는 네가 되는 거야. 알겠지?",
66:"좋아, 아무것도 모르는 네가 되도록 약을 내주마.^n──오늘은 꽤 더워질 듯하니,^n비스킷이 좋겠구나.",
68:"자네, 꿈 비스킷 좀 가져와. 곰 인형 옆에 있는 것.^n이 아이에게 사흘 치, 그리고 내가 지금 먹을 것까지.",
83:" 예쁜 통의 뚜껑을 열고 간호사가^n『약』을 나누어 담는다.",
97:"여러 색깔의 복잡한 모양을 한 비스킷을 앞에 두고^n두 사람이 이리저리 의미를 끼워 맞추는 모습은^n어쩐지 심리 검사 같다.",
107:"늘 지친 얼굴에 미소를 붙이고 있던 직원이,^n나를 가볍게 툭 치거나 머리를 쓰다듬어 격려하고,^n시시한 농담을 하며 무척 즐겁게 웃는다.",
111:"휴식 종료 알람과 함께 쓱 생기가 빠져나간^n직원들의 모습을 보며 나는,^n언제까지나 함께 놀 수 있으면 좋겠다고 생각했다.",
}
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 draft=json.loads(DRAFT.read_text(encoding="utf-8"));expected=set(range(1,112))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1219_slots_00001_00111_draft":raise SystemExit("unexpected draft")
 entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]};changes=[]
 if set(entries)!=expected:raise SystemExit("draft coverage mismatch")
 for i,t in CORRECTIONS.items():
  before=str(entries[i]["target_text"]);entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 catalog={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1219.gsc":continue
   i=int(x["slot"])
   if i in expected:catalog[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(catalog)!=expected or lookup!=set(range(112,170)):raise SystemExit("catalog/lookup mismatch")
 final=[]
 for i in sorted(expected):
  e=entries[i];s,t=str(e["source_text"]),str(e["target_text"])
  if s!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]:raise SystemExit(f"source drift {i}")
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"});final.append(e)
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1219_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,111],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[112,169],"release_ready":False,"entries":final};out=PROJECT/"packets"/"reviewed"/"1219_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,111],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_112_169_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};ap=PROJECT/"audit"/"translation_review_1219_complete.json";ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
