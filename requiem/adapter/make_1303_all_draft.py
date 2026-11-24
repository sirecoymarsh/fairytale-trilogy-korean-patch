from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
TARGETS=[None,
"여느 때처럼 의사에게 진찰받던 중이었다.^n진료 기록에 무언가를 쓰면서 의사가 말했다.","의사","아, 그러고 보니.^n지난번에 코미야 군이 폐를 끼쳤다더군.","나","네……?","갑자기 그런 이야기를 꺼내서 나는 당황했다.","나","아뇨, 저는 괜찮지만…….^n그 말은 제가 아니라 그레텔에게 해 주세요.","코미야라는 그 의사에게 시달린 탓에,^n그녀는 몹시 무서워했고 불쾌해하기도 했다.","어쩌면 그녀를 숲으로 끌고 가려던 사람이^n그 사람이 아니었을까 하는 말도 했다.","의사","음, 그렇군.^n나중에 나도 잘 사과해 두도록 하지.","의사는 그렇게 말하고 펜을 놀리던 손을 멈춘 뒤,^n고개를 들어 내 눈을 바라보며 물었다.","의사","그런데 자네는 그레텔을 어떻게 생각하나?","나","어떻게라니……?","허를 찌르는 질문이었다.","나","저, 무슨 뜻으로 하신 질문인지 잘 모르겠어요.","의사","흠…… 예를 들자면 말일세.^n지난번에 코미야 군에게 자기가 헨젤이라고 했다더군.^n무슨 의도로 그런 건가?","나","그건…… 그때는 그렇게라도 말하지 않으면,^n그 사람이 물러날 것 같지 않아서…….","의사","그렇군, 자네 나름대로 기지를 발휘한 거겠지.^n도리어 그를 격분시킨 것은 뭐, 계산 밖이었겠지만.","나","저…… 그게 무슨 문제라도 되나요?","의사","자네에게는 임시방편이었을지 모르지만.^n그레텔은 완전히 그렇게 믿게 된 모양이야.","나","그러니까 제가 헨젤이라고 굳게 믿고 있다……는 건가요.","의사","뭐, 그런 셈이지.^n진짜 남매도 아닌데 헨젤을 연기하는 일에 대해,^n자네 자신은 어떻게 생각하나?","나","저, 질문해도 될까요?^n진짜 헨젤은…… 그 아이의 오빠는……?","의사","없네.^n적어도 이 시설에는 없어.","나","그렇다면…… 적어도 이 시설에 있는 동안만이라도,^n그 아이의 오빠 역할을 해도 괜찮다고 생각해요.","나","뭐랄까…… 잘 대답할 수는 없지만,^n제가 할 수 있는 일은 해 주고 싶어요.","의사","그건 동정인가?^n아니면 다른 무언가인가?","나","다른 거라니……?"," 나는 질문의 뜻을 알 수 없었다.^n『동정』이라는 말은 이해한다.^n 그런 면이 전혀 없다고 단언할 수는 없으니까.","의사","아니, 예를 들자면 말일세.^n그렇게 해서 그 아이를 독차지할 수 있다든가──^n그런 생각에서 나온 행동은 아닌가?","나","독차지……?","의사","뭐, 자네도 그럴 나이의 남자아이니까.^n여자아이를 곁에 두고 싶고 접촉하고 싶다는 마음이^n싹트는 건 성장기의 지극히 자연스러운 현상이지.","나","(이 의사 선생님, 뭔가 이상한 걸 물어보는 것 같은데……)","나도 모르게 얼굴이 뜨거워졌다.^n어쩌면 귀까지 빨개졌을 것 같다.","나","(이렇게 얼굴을 붉히면,^n 마치 정곡을 찔린 것 같잖아)","나는 필사적으로 냉정해지려고,^n의사에게 들리지 않게 호흡을 가다듬었다.","나","(나는…… 딱히 불순한 마음으로^n 그 아이를 지키려 했던 게 아니야)","나","외로워 보이는 그 아이를 위로해 주고 싶다고는^n분명 생각했어요.","나","제게도 여동생이 있었던 듯한 느낌이 들어요.^n그래서 그 아이도 제 여동생처럼 생각하고 있고…….","나","그래서, 그게, 그러니까…….","말로 잘 표현하지 못하고 나는 머뭇거렸다.","의사","흠, 내가 곤란하게 한 건가?^n미안하네, 방금 질문은 잊어 주게.","의사는 의미심장하게 웃더니,^n다시 진료 기록에 무언가를 적기 시작했다.","의사에게 새삼 질문받고,^n나는 왜 헨젤을 자처하려 했는지 스스로에게 물었다.","나","(나로서도 언제까지고 이름 없이 지내면 불편하고…….^n 이름과 역할이 생기는 건 기쁘니까…… 그런 걸까)","그 아이가 내가 그러기를 바라는 동안,^n나는 헨젤을 연기하려고 한다."]
def main():
 expected=set(range(1,76))
 if len(TARGETS)!=76:raise SystemExit(f"target count {len(TARGETS)-1}")
 rows={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1303.gsc":continue
   i=int(x["slot"])
   if i in expected:rows[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(rows)!=expected or lookup!=set(range(76,134)):raise SystemExit("coverage mismatch")
 entries=[]
 for i in sorted(expected):
  row,t=rows[i],str(TARGETS[i]);s=str(row["source_text"])
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":s,"source_raw_sha256":row["source_raw_sha256"],"target_text":t,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 대기"})
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1303_slots_00001_00075_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};out=PROJECT/"packets"/"drafts"/"1303_slots_00001_00075_draft.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[76,133],"output":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
