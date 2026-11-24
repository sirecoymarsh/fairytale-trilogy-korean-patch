from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
TARGETS=[None,
"그레텔","오, 오빠!^n오빠아!!",
"코미야","그휴헤휴헤헤에…….^n이제 방해꾼은 없어졌네, 그레텔아.^n두, 두, 둘만 남았어…… 부슛.",
"이름 없는 소년이 계단 아래로 굴러떨어진 채^n일어나지 않는 것을 확인하자,^n코미야는 기름진 얼굴을 그레텔에게 돌렸다.",
"그레텔","아…… 아아아아…….",
"소년이 굴러떨어져 공황에 빠졌는지,^n그레텔은 그 자리에 우두커니 서서^n목과 어깨를 부들부들 떨고 있다.",
"코미야","자…… 오빠와 함께^n이번에야말로 기분 좋은 일을 하자아?",
"앞으로 내민 두 손을 꿈틀거리며,^n냄새나는 숨을 헉헉 흩뿌리는 채^n코미야가 그레텔에게 조금씩 다가간다.",
"그레텔","……거야…….^n……어치……, ……거야!",
"그저 울부짖을 뿐이던 그레텔이었지만,^n이번만은 달랐다.",
"그레텔","──우리 오빠에게 무슨 짓이에요!!",
"외치면서 그레텔이 두 손을 코미야에게 뻗었다.",
"코미야","어?",
" 아아────!?",
"단풍나무 가지처럼 가느다란 그녀의 팔에서는 믿을 수 없는 괴력이 나와,^n코미야의 몸을 날려 버렸다.",
"코미야","끄아아악!?",
"복도 벽에 뒤통수를 세게 부딪친 코미야는 고통에 몸부림쳤다.",
"코미야","히, 히익! 피, 피가, 피가 나잖아아아!^n누, 누구! 의사를 불러 줘!! 죽겠어어!!",
"손바닥에 철퍼덕 묻은 피를 확인한 그는^n요란한 비명을 지르며 벌떡 뛰어올라 그 자리에서 달아났다.",
"그때 둥근 거구로 굴러가듯 도망치는 코미야의 품에서^n툭 떨어진 것이 있었다.",
"그레텔","뭐야…… 이거……?",
"그것은 금빛으로 반짝이는 금속제 카드였다.",
"그레텔","아, 맞다. 오, 오빠를!",
"얼결에 카드를 주웠지만 살펴볼 여유는 없어서,^n그녀는 이름 없는 소년──헨젤에게 달려갔다.",
"그레텔","어, 어떡해, 오빠, 오빠……!",
"조금 전까지의 용감한 모습은 어디 갔는지.^n테디베어의 다리를 쥐어짜듯 붙잡아 늘어뜨리고,^n완전히 평소의 소심한 모습으로 허둥댄다.",
"그레텔","누, 누군가, 사, 사람을 불러야…….",
"생각이 나서 고개를 들고 두리번거리며 주위를 살폈다.",
"그러자 인기척 없는 복도 끝에^n불쑥 나타난 사람의 모습이 눈에 들어왔다.",
"이케노","뭔가 소란스러웠는데……?^n","──이런, 그레텔 아니야.",
"이케노","대체 무슨──^n","……으아아아아!?",
"그레텔","아, 이, 이케노 씨,^n","사…… 살려 주세요!!^n오, 오빠가, 오빠가아!!",
"그녀는 지옥에서 부처라도 만난 듯,^n달려들 기세로 이케노에게 도움을 청했다."]
def main():
 expected=set(range(1,52))
 if len(TARGETS)!=52:raise SystemExit(f"target count {len(TARGETS)-1}")
 rows={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1308.gsc":continue
   i=int(x["slot"])
   if i in expected:rows[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(rows)!=expected or lookup!=set(range(52,110)):raise SystemExit("coverage mismatch")
 entries=[]
 for i in sorted(expected):
  row,t=rows[i],str(TARGETS[i]);s=str(row["source_text"])
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":s,"source_raw_sha256":row["source_raw_sha256"],"target_text":t,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 대기"})
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1308_slots_00001_00051_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};out=PROJECT/"packets"/"drafts"/"1308_slots_00001_00051_draft.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[52,109],"output":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
