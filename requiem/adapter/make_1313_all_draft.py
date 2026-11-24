from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
TARGETS=[None,
"점심 전, 나는 그레텔의 방을 찾아갔다.^n어젯밤 맡은 카드 키를 상의하기 위해서다.",
"나","──그런 사정이라서.^n나는 이걸 사용해 탐험해 보려고 해.",
"그레텔","타, 탐험……!?",
"내 생각을 밝히자^n그레텔의 눈이 반짝반짝 빛났다.",
"나","그래, 이건 나와 그레텔만의 비밀이야.^n시설 사람들은 물론 다른 환자 아이들에게도 비밀이야.",
"들켜서 직원에게 이것을 빼앗기면 아무 소용도 없다.",
"중요한 비밀이 밝혀져 우리 환자 모두에게^n도움이 되는 일임을 알게 되면 다들 그때^n털어놓자──나는 그렇게 결심했다.",
"그레텔","응, 응.^n우리만의 비밀이네, 오빠.",
"『탐험』과 『비밀』이라는 말에 호기심을 자극받았는지,^n 그레텔은 밝은 얼굴로 연신 고개를 끄덕였다.",
"무언가를 먹을 때 말고 이렇게 즐거운 얼굴을 한^n그레텔은 처음 보는 것 같다.",
"코미야라는 사람과 얽힌 뒤로 싫은 일만 겪은^n그레텔에게 이것이 좋은 기분 전환이 되면 좋을 텐데.",
"나는 그렇게 생각하며^n그녀를 데리고 시설 안 탐험을 시작했다.",
"그레텔","후우…….^n좀처럼 찾을 수가 없네, 오빠…….",
"눈에 띄는 곳을 돌아봐도^n이 카드 키를 쓸 만한 곳은 찾지 못했다.",
"그레텔","으으…… 배…… 고파…….",
"처음의 활기는 어디로 갔는지,^n온몸의 뼈가 빠진 듯 주저앉은 그레텔의^n배꼽시계가 마침내 비명을 질렀다.",
"나","오늘은 여기까지 할까.^n조급해해도 소용없으니까.",
"나","(이렇게 되면 무슨 수를 써도 움직이지 않겠지……)",
"나","슬슬 점심시간이니,^n방으로 돌아가 밥 먹고 쉬자.",
"그레텔","응!^n밥이다♪ 밥이다♪",
"가벼운 걸음으로 복도를 걷는 그레텔을 따라가던 나는^n손에 든 키에 요철이 있다는 것을 깨닫고 멈춰 섰다.",
"각도를 바꿔 바라보자 카드 뒷면에는^n돋을새김으로 스무 자리쯤 되는 번호와 함께^n알파벳이 새겨져 있었다.",
"나","『GUEST』…… 게스트였나?",
"그러니까 이 카드를 가지고 있던 코미야라는 남자는^n정말 의사가 아니라^n이 시설의 손님이라는 걸까?",
"나","(하지만 왜 시설을 찾아온 손님이^n 의사 차림으로 제멋대로 굴 수 있는 거지?)",
"직원들에게 너무 심하다는 주의를 받기는 했지만,^n그 사람이 이 시설에 있는 것 자체는 허락된 모양이다.",
"나는 그것을 납득할 수 없었고,^n그 이유도 전혀 짐작할 수 없었다.",
"왜일까.^n조금 전 복도에서 마주친 게르다의 텅 빈 표정이 갑자기 떠올라,^n마음이 몹시 술렁였다.",
"──그때 앞서 걷던 그레텔이 돌아보더니,^n깡충깡충 뛰면서 나를 향해 손짓했다.",
"그레텔","오빠, 빨리 빨리!^n밥이 도망가 버려!",
"나","아하하.^n밥은 도망가지 않을 것 같은데…….",
"나는 쓴웃음을 지으며 불길한 생각을 떨쳐 내고,^n그레텔의 뒤를 따라 다시 복도를 걷기 시작했다."]
def main():
 expected=set(range(1,47))
 if len(TARGETS)!=47:raise SystemExit("target count mismatch")
 rows={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1313.gsc":continue
   i=int(x["slot"])
   if i in expected:rows[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(rows)!=expected or lookup!=set(range(47,105)):raise SystemExit("coverage mismatch")
 entries=[]
 for i in sorted(expected):
  row,t=rows[i],str(TARGETS[i]);s=str(row["source_text"])
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":s,"source_raw_sha256":row["source_raw_sha256"],"target_text":t,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 대기"})
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1313_slots_00001_00046_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};out=PROJECT/"packets"/"drafts"/"1313_slots_00001_00046_draft.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[47,104],"output":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
