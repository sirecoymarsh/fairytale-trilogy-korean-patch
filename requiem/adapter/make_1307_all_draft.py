from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
TARGETS=[None,
"???","뭐야, 아직도 저런 녀석과 어울리는 거야?",
"그레텔","아우우…… 으으으…….",
"복도를 걷고 있는데^n앞쪽에서 어디선가 들은 적 있는 목소리가 들려왔다.^n불길한 예감에 나는 목소리가 나는 쪽으로 달렸다.",
"코미야","그러면 안 돼, 그레텔. 잘 보렴.^n네 오빠가 저런 사람이었던가?^n조금 다르지 않니이?",
"예상대로 뚱뚱한 흰 가운 차림이 보였다.^n직원들이 『코미야』라고 부르던 사람이다.",
"그레텔","으으……^n마, 만지지 마…….",
"조금도 정신을 차리지 못하고 그레텔을 따라다니며,^n스스럼없이 몸을 만지면서 말을 걸고 있다.",
"코미야","있지, 그레텔은^n조금 더 조심해야 해.^n몸을 노리고 같은 편인 척하는 건 흔한 일이거든.",
"달아나려는 그레텔의 한 손을 붙잡고,^n다른 손으로는 그레텔의 엉덩이를 더듬으며^n헉헉 거친 숨을 내쉬고 있다.",
"그레텔","시, 싫어. 기…… 기분, 나빠…….",
"나","이제 그만 좀 하세요!",
"나는 다시 그레텔의 앞을 가로막았다.",
"그레텔","흐에에에…… 오, 오빠……,^n","이, 이 사람이…… 흑……,^n","또, 또 이상한 짓을…… 흑…… 해.",
"그레텔이 내 등에 달라붙으며 눈물을 뚝뚝 흘렸다.^n그 작은 온기에 나는 가슴이 확 뜨거워지는 것을 느꼈다.",
"나","(이 아이를 울리다니……!)",
"나는 똑똑히 『적』을 바라보는 눈으로^n의사의 이중턱을 노려봤다.",
"나","또 괴롭히는 겁니까?^n직원이나 다른 의사 선생님에게 이를 거예요!",
"내가 그렇게 말하자 코미야는 움츠러들기는커녕,^n오히려 둥그런 얼굴을 새빨갛게 붉히고^n이를 드러내며 고함치기 시작했다.",
"코미야","아직도 오빠 행세냐! 이 가짜 녀석!",
"나","제가 가짜일지도 모르는 건 맞아요.^n하지만 당신 같은 사람에게 이래라저래라 들을 이유는 없어요.",
"코미야","뭐라고오?^n내가 뭘 했다는 거냐, 응?",
"코미야는 나를 노려보며 낮은 목소리로 위협하듯 으르렁거렸다.",
"나","방금 만졌잖아요.^n이 아이는 싫어했는데도!",
"코미야","뭐어? ──흥, 네 착각이야.^n남매라면 당연한 스킨십이잖아?^n그렇지, 그레텔?",
"그레텔","으으읏……!",
"이름을 불린 그레텔은^n내 뒤에서 작게 고개를 저었다.",
"나","시치미 떼지 마세요!^n그것뿐만이 아니에요. 지난번에 그 아이를 숲속으로^n억지로 끌고 가려던 사람도 당신이죠?",
"코미야","흥…… 무슨 증거라도 있어어?",
"코미야는 조금도 나쁜 줄 모르는 얼굴로^n귀를 후비는 시늉을 하며 콧방귀를 뀌었다.",
"나","그레텔이 당신이었다고 했어요.^n본인이 그렇게 말하니 틀림없어요.",
"코미야","너무하네, 그레텔은.^n지난번에는 사이좋게 산책하자고 했을 뿐이잖아?^n그런 말을 듣다니 오빠는 섭섭하네에.",
"내 몸 옆으로 얼굴을 내밀 듯이^n코미야가 간드러진 목소리로 말을 걸자,^n그레텔의 몸이 흠칫 떨렸다.",
"나","당신은 그 아이의 오빠가 아니에요!^n그 아이도 그런 건 인정하지 않아요!",
"나는 몸의 각도를 바꿔 다시 한번 그녀를^n코미야의 시선에서 가리고 따져 물었다.",
"나","왜 그렇게 그레텔을 따라다니는 겁니까?^n대체 그 아이에게 무슨 짓을 하려는 거예요?",
"코미야","무슨 짓이긴…… 그야^n의사 놀이로 정해져 있잖아아?",
"그레텔","──!?^n","……시, 싫어…… 흐에에에에…….",
"나","의…… 의사 놀이라니!?^n당신 진짜 의사 선생님…… 맞죠?",
"코미야","후훗…… 그러면 어쨌는데?",
"의미심장하고 여유로운 미소를 지으며^n코미야가 콧방울을 벌름거렸다.",
"나","의사라는 건 환자를 치료하는 사람이잖아요?^n왜 그런 끔찍한 짓을 하는 겁니까!",
"코미야","하하하하.^n나 말이야, 사실 의사 같은 게 아니거든. 이게 참.",
"나","네……!?",
"무슨 뜻인지 알 수 없었다.^n흰 가운을 입고 당당하게 병원 안을 다니는데^n의사가 아니라고?",
"동시에 크게 납득했고 안심도 했다.^n이런 녀석이 의사라니,^n환자로서도 그런 병원은 사양이다.",
"하지만──",
"나","그런 사람이 왜 여기에 있는 겁니까?",
"몰래 숨어들었다면 모를까,^n직원들도 이 사람을 아는 눈치였는데.",
"코미야","글쎄에. 그건 말할 수 없네에.^n하지만 그런 사람은 나뿐만이 아닌 모양이던데에.^n","──앗, 이런.",
"말을 너무 많이 했다는 듯,^n코미야는 황급히 손으로 입을 가렸다.",
"의사가 아닌데 의사 행세를 한다고?^n그런 사람이 이 사람뿐만도 아니라고?",
"나","그게 무슨 뜻이에요!?^n이 병원은 대체 어떻게 된 겁니까?",
"나","당신들은 우리를──^n그 아이를 어떻게 하려는 거예요?",
"추궁하려 했지만,^n코미야는 파리라도 쫓듯 두 손을 마구 휘저어^n나를 입 다물게 하려 했다.",
"코미야","시끄러워, 시끄럽다고!^n뭘 잘난 척하는 거야!!",
"코미야는 얼굴을 새빨갛게 붉히고^n거친 콧김을 내뿜으며 내게 서서히 다가왔다.",
"코미야","그렇게 멋있는 척해 봐야,^n결국 너도 그레텔의 몸을^n노리는 것뿐이잖아, 응!?",
"코미야는 내게 검지를 들이대며 제멋대로 단정했다.",
"나","(이 사람은 무슨 말을 하는 거지?^n 남매끼리 그럴 리 없잖아……)",
"코미야","너만 없으면 내가 그레텔의^n오빠가 될 수 있다고오오!!",
"나","왓!? 무, 무슨 짓이에요!?",
"격분한 코미야가 내게 달려들어 멱살을 잡았다.^n견디지 못하고 떨쳐 내려 했지만,^n그는 보기보다 민첩하고 힘도 셌다.",
"나","으아아아아────!?",
"몸싸움을 벌이다 나는 근처 계단에서 굴러떨어졌다.",
"그레텔","──오, 오빠!",
"그레텔의 외침이^n멀어져 가는 의식 너머에서 들렸다.",
"나","(────)",
"이름을 부르려 했는데 목소리가 나오지 않는다.",
"내가 부르려 한 이름은 그레텔?^n아니면──",
"아아, 그녀의 이름이 기억나지 않아──"]
def main():
 expected=set(range(1,116))
 if len(TARGETS)!=116:raise SystemExit(f"target count {len(TARGETS)-1}")
 rows={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1307.gsc":continue
   i=int(x["slot"])
   if i in expected:rows[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(rows)!=expected or lookup!=set(range(116,174)):raise SystemExit("coverage mismatch")
 entries=[]
 for i in sorted(expected):
  row,t=rows[i],str(TARGETS[i]);s=str(row["source_text"])
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":s,"source_raw_sha256":row["source_raw_sha256"],"target_text":t,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 대기"})
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1307_slots_00001_00115_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};out=PROJECT/"packets"/"drafts"/"1307_slots_00001_00115_draft.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[116,173],"output":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
