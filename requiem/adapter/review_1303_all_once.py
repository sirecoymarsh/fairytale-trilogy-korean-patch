from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");DRAFT=PROJECT/"packets"/"drafts"/"1303_slots_00001_00075_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
3:"아, 그러고 보니.^n지난번에 코미야 군이 폐를 끼친 모양이더군.",
8:"아뇨, 저는 괜찮지만…….^n그 말은 제가 아니라 그레텔에게 해 주세요.",
9:"코미야라는 그 의사에게 시달린 탓에,^n그녀는 몹시 무서워했고 꺼림칙해하기도 했다.",
10:"어쩌면 그녀를 숲으로 끌고 가려던 사람이^n그 사람이 아니었을까 하는 말도 했다.",
13:"의사는 그렇게 말하고 펜을 놀리던 손을 멈춘 뒤,^n고개를 들어 내 눈을 바라보며 물었다.",
22:"흠…… 예를 들어 말일세.^n지난번에 코미야 군에게 자기가 헨젤이라고 했다더군.^n무슨 의도로 그런 건가?",
26:"그렇군, 자네 나름대로 재치를 발휘한 거겠지.^n도리어 그를 격분시킨 것은 뭐, 계산 밖이었겠지만.",
30:"자네에게는 임시방편이었을지 모르지만,^n그레텔은 완전히 그렇게 믿게 된 모양이야.",
32:"그러니까 제가 헨젤이라고 굳게 믿고 있다……는 거군요.",
34:"뭐, 그런 셈이지.^n진짜 남매도 아닌데 헨젤을 연기하는 일에 대해,^n자네 자신은 어떻게 생각하나?",
47:" 나는 질문의 뜻을 알 수 없었다.^n『동정』이라는 말은 이해한다.^n 그런 면이 전혀 없다고 단언할 수는 없으니까.",
49:"아니, 예를 들자면 말일세.^n그렇게 해서 그 아이를 독차지할 수 있다든가──^n그런 생각에서 나온 행동은 아닌가?",
53:"뭐, 자네도 그럴 나이의 남자아이니까.^n여자아이를 곁에 두고 싶고 서로 접촉하고 싶다는 마음이^n싹트는 건 사춘기의 지극히 자연스러운 현상이지.",
55:"(이 의사 선생님, 뭔가 이상한 걸 묻는 것 같은데……)",
56:"나도 모르게 얼굴이 뜨거워졌다.^n어쩌면 귀까지 빨개졌을지도 모른다.",
59:"나는 필사적으로 침착해지려고,^n의사에게 들리지 않게 호흡을 가다듬었다.",
63:"불안해 보이는 그 아이를 위로해 주고 싶다고는^n분명 생각했어요.",
65:"제게도 여동생이 있었던 듯한 느낌이 들어요.^n그래서 그 아이도 제 여동생처럼 여기고 있고…….",
70:"흠, 내가 곤란하게 한 건가?^n미안하네, 방금 질문은 잊어 주게.",
71:"의사는 의미심장하게 웃더니,^n다시 진료 기록에 무언가를 적기 시작했다.",
72:"의사에게 새삼 질문받자,^n나는 왜 헨젤을 자처하려 했는지 스스로에게 물었다.",
74:"(나로서도 언제까지고 이름 없이 지내면 불편하고…….^n 이름이나 역할이 생기면 기쁘니까…… 그런 걸까)",
75:"그 아이가 내가 그러기를 바라는 한,^n나는 헨젤을 연기하려고 한다.",
}
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 draft=json.loads(DRAFT.read_text(encoding="utf-8"));expected=set(range(1,76))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1303_slots_00001_00075_draft":raise SystemExit("unexpected draft")
 entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]};changes=[]
 if set(entries)!=expected:raise SystemExit("draft coverage mismatch")
 for i,t in CORRECTIONS.items():
  before=str(entries[i]["target_text"]);entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 catalog={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1303.gsc":continue
   i=int(x["slot"])
   if i in expected:catalog[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(catalog)!=expected or lookup!=set(range(76,134)):raise SystemExit("catalog/lookup mismatch")
 final=[]
 for i in sorted(expected):
  e=entries[i];s,t=str(e["source_text"]),str(e["target_text"])
  if s!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]:raise SystemExit(f"source drift {i}")
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"});final.append(e)
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1303_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,75],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[76,133],"release_ready":False,"entries":final};out=PROJECT/"packets"/"reviewed"/"1303_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,75],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_76_133_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};ap=PROJECT/"audit"/"translation_review_1303_complete.json";ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
