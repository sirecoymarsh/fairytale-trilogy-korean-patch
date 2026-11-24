from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");DRAFT=PROJECT/"packets"/"drafts"/"1306_slots_00001_00070_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
3:"진찰실 앞을 지나가다가^n안에서 게르다가 고함치는 소리가 들려왔다.",
4:"힘껏 닫았다가 튕겨 나왔는지,^n입구 문은 조금 열린 채였다.",
9:"왜 관계 기관에 연락하지 않는 거예요!?^n새까맣게 탄 시체 때도 그랬잖아요!",
15:"그건 제대로 조사해서^n문제가 없다는 결론이 났다네.",
16:"그때 의사의 시선과 말투가 조금 날카로워졌다.^n게르다의 심장을 향해 깊이 파고들 듯이.",
18:"그건 자네가 제일 잘 알고 있지 않나?",
25:"(설마 그녀가 범인일 리는 없다고 생각하지만──)",
28:"포기한 게 아니라,^n사건 이야기가 게르다에게도 아픈 곳을 찔렀기 때문일 것이다.",
29:"문틈으로 게르다가 손을 세게 움켜쥐는 모습이 보였다.^n손의 떨림을 억누르듯 몇 번이나,^n주먹 전체에서 핏기가 사라질 정도로.",
35:"시치미를 떼는 건지 정말 모르는 건지,^n어느 쪽으로도 들리는 태연한 말투로 의사가 되물었다.",
41:"자네를 어떻게 했다는 건가?^n아, 성적인 장난을 당했다는 이야기였나.",
42:"입에 올리기 어려운 일을 의사가 단도직입적으로 말하자,^n게르다는 치욕에 얼굴을 일그러뜨리며 분하다는 듯 고개를 끄덕였다.",
49:"(게르다가 남자들에게…… 그런 짓을 당했다니……?)",
51:"거짓말을 하는 건지 환각이라도 본 건지.^n어른을 놀리면 안 돼.^n나는 다 알고 있으니까.",
52:"의사는 그런 일이 있을 리 없다는 어조였다.^n타이르듯 두 손을 모으고 게르다를 빤히 바라본다.",
54:"거짓말이 아니에요……!^n그, 그건…… 그런 짓은…….",
55:"정신없이 흥분한 게르다가^n끔찍한 기억을 떨쳐 내려는 듯 고개를 저었다.",
56:"──그러자 그녀의 눈이^n문틈에서 들여다보던 내 눈과 우연히 마주쳤다.",
59:"죄책감이 가슴을 찔러 순간 말이 나오지 않는다.^n그러는 사이 게르다의 얼굴에서 순식간에 핏기가 가셨다.",
60:"엿보였다는 놀라움과 당혹감 따위를 걷어차고^n정체를 알 수 없는 감정이 그녀의 지적인 얼굴을 크게 일그러뜨린다──",
67:"게르다는 말을 붙일 틈도 없이^n진찰실을 뛰쳐나가 달아났다.",
70:"나는 그녀를 뒤쫓으려 했지만,^n의사에게 붙잡혀 그 뒤 엿본 일로 한동안 야단을 맞았다.",
}
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 draft=json.loads(DRAFT.read_text(encoding="utf-8"));expected=set(range(1,71))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1306_slots_00001_00070_draft":raise SystemExit("unexpected draft")
 entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]};changes=[]
 if set(entries)!=expected:raise SystemExit("draft coverage mismatch")
 for i,t in CORRECTIONS.items():
  before=str(entries[i]["target_text"]);entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 catalog={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1306.gsc":continue
   i=int(x["slot"])
   if i in expected:catalog[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(catalog)!=expected or lookup!=set(range(71,129)):raise SystemExit("catalog/lookup mismatch")
 final=[]
 for i in sorted(expected):
  e=entries[i];s,t=str(e["source_text"]),str(e["target_text"])
  if s!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]:raise SystemExit(f"source drift {i}")
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"});final.append(e)
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1306_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,70],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[71,128],"release_ready":False,"entries":final};out=PROJECT/"packets"/"reviewed"/"1306_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,70],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_71_128_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};ap=PROJECT/"audit"/"translation_review_1306_complete.json";ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
