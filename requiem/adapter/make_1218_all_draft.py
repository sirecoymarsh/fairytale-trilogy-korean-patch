from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko"); CARET_RE=re.compile(r"\^(?:n|m|d\d+)")
TARGETS=[None,
"늦은 오후의 정원에 아름답고 온화한 목소리가 울려 퍼진다.",
"산들바람을 타고 나무 사이를 달려, 활짝 핀 꽃을 축복하고,^n붉은 페인트투성이 흰 장미를 어루만지며 흘러간다.",
"그 목소리는 큰 나무 아래에서 어깨를 맞댄 두 사람 중,^n나이가 더 많은 소녀의 입술에서 흘러나오고 있었다.",
"라푼젤","………….",
"페이지를 넘기려던 손을 멈추고,^n라푼젤은 살며시 앨리스의 상태를 살폈다.",
"아마도 오가기를 반복하던 잠의 나라로^n이번에야말로 떠나 버린 것이리라.",
"깨어 있었다면 라푼젤이 이야기를 멈춘 데 대해^n뺨을 부풀리며 항의했을 것이다.",
"앨리스","새근, 새근…….^n으응…… 우뉴…….","라푼젤","어머…….",
"잠든 앨리스의 뺨이 부우 하고 부풀고,^n항의 같은 말을 웅얼웅얼 중얼거리는 모습을 보고,^n라푼젤은 살며시 미소 지었다.",
"아무래도 앨리스는 잠의 나라로 가는 길을 따라가면서도^n이야기를 계속해 달라고 조를 생각인 듯하다.",
"앨리스","새근…… 새그은…….",
"고요한 숨소리를 듣는 동안 라푼젤 또한^n늦은 오후 특유의 나른한 졸음을 느끼고 있었다.",
"큰 나무의 무성한 잎이 만든 푸른 그늘.^n산들바람에는 상쾌한 초록빛 향기가 배어 있고,^n나뭇잎 사이 햇살은 변덕스럽게 반짝인다.",
"라푼젤","………….",
"잠든 앨리스가 조르고 있는데도^n라푼젤이 페이지를 넘기려 하지 않은 것은,^n차라리 자신도 낮잠에 몸을 맡기고 싶어졌기 때문이다.",
"──바로 조금 전의 일.",
"갑자기 방에 나타나 꼭 손을 잡더니^n세차게 끌고 걷기 시작한 앨리스 때문에,^n라푼젤은 몹시 당황했다.",
"라푼젤","안 돼, 안 돼요, 앨리스.^n여기서 나가면 할머님께 무슨 말을 들을지…….",
"앨리스","할머님께 꾸중을 들으면 제가 어떻게든 할게요.^n",
"방법은 얼마든지 있으니까요.",
"라푼젤","앨리스도 참……!","앨리스",
"저는 밖이 좋아요.^n라푼젤은 정원 나무 그늘에서 제게 책을 읽어 주는 거예요.",
"앨리스","라푼젤도 창문에서 이쪽을 그렇게 바라봤잖아요…….^n데리고 나가 달라고 얼굴에 쓰여 있었어요.",
"라푼젤","………….",
"역시 늦은 오후 창문에서 정원을 한눈에 바라보았을 때^n정원에 있던 앨리스와 눈이 마주친 것은 기분 탓이 아니었다.",
"그렇게 멀리 떨어져 표정도 희미했을 텐데,^n어떻게 라푼젤의 지루함과 불만을 알아차렸을까.",
"앨리스","……응, 으응…… 으…….",
"문득 앨리스가 몸을 뒤척였다.",
"무슨 일이 있어도 잠들기 전 이야기를 계속 듣고 싶다는^n의사 표시일까──",
"앨리스","으응……? 응……?^n──아…… 어라……?",
"앨리스는 희미하게 눈을 떴다.",
"풀어진 눈동자 표면에 라푼젤을 비추고,^n눈을 연달아 깜빡였지만,^n졸음의 흐림은 좀처럼 가시지 않는 모양이다.",
"라푼젤","왜 그래요, 앨리스?","앨리스","……………….",
"앨리스는 흔들리는 눈길을 라푼젤에게 둔 채,^n헤실 하고 뺨을 풀었다.",
"아이처럼 부드럽고 행복해 보이는 미소였다.",
"앨리스","아아…… 언니, 살아 있었구나.^n다행이다…….",
"앨리스","저 말이에요, 계속 나쁜 꿈을 꾸고 있었어요…….",
"라푼젤","………….",
"라푼젤은 아무 말도 할 수 없었다.",
"정말 앨리스의 언니였다면 좋았을 텐데.^n오직 그 생각만을 간절하고 또 간절하게 할 뿐이었다.",
"앨리스","언…… 니…….^n………………………….",
"앨리스는 다시 잠든 듯하다.^n고요하고 규칙적인 숨소리가 들린다.",
"라푼젤",
"──라푼젤은 처음에는 무척 놀랐습니다.^n자란 뒤로 마녀 말고 다른 사람을 만난 것은 이번이 처음이었기 때문입니다.",
"라푼젤은 이야기의 다음 대목으로 나아갔다.",
"이번에는 확실히,^n앨리스가 다시 깨어날 때까지 끊이지 않게 이어 가겠다고,^n남몰래 다짐하면서."]
def main()->int:
 expected=set(range(1,68));
 if len(TARGETS)!=68: raise SystemExit(f"target count {len(TARGETS)-1}")
 rows={}; lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   item=json.loads(line)
   if item.get("file")!="1218.gsc":continue
   i=int(item["slot"])
   if i in expected:rows[i]=item
   elif "lookup_keys" in item.get("lanes",[]):lookup.add(i)
 if set(rows)!=expected or lookup!=set(range(68,126)):raise SystemExit("coverage mismatch")
 entries=[]
 for i in sorted(expected):
  row,target=rows[i],str(TARGETS[i]);source=str(row["source_text"])
  if CARET_RE.findall(source)!=CARET_RE.findall(target):raise SystemExit(f"caret mismatch {i}")
  target.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":source,"source_raw_sha256":row["source_raw_sha256"],"target_text":target,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 대기"})
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1218_slots_00001_00067_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};out=PROJECT/"packets"/"drafts"/"1218_slots_00001_00067_draft.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[68,125],"output":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
