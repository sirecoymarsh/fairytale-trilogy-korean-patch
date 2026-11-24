from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
TARGETS=[None,
" 나는 그레텔과 함께,^n『헨젤과 그레텔』에서 숲에 뿌릴 『표식』이 되는^n 빵을 찾으러 주방에 왔다.",
"저녁에 닭고기 소테와 함께 바게트가 나왔으니,^n남거나 여분인 빵이 주방에 있을지도 모른다고^n생각해서 그레텔을 데려온 것이다.",
"나",
"(원래라면 앨리스가 그 아이를 위해 빵을 구워 줘서,^n 보충할 수 있었을 텐데──)",
"어제 이곳에서 벌어진 불탄 시체 소동 탓에,^n모처럼 구워 줬을 빵은^n전부 못 쓰게 되어 버렸다.",
"그레텔","와…… 벌써 완전히 반짝반짝해.",
"그레텔이 눈을 휘둥그레 뜨고 놀랐다.^n어제 그토록 연기와 그을음이 날렸을 주방은^n벌써 말끔하게 청소되어 있었다.",
"나","그러게.^n시설 사람들이 치운 걸까……?",
"생각만큼 그을음이 많이 뿜어져 나오진 않았지만,^n그래도 닦아 내기는 힘들었겠다는 생각이 든다.",
"그레텔","킁킁킁…….^n","오빠, 빵 냄새가 나.",
"나","어, 정말?",
"그레텔","응, 어제 탄 것 말고.^n제대로 고소한 냄새야.^n","킁킁, 킁킁…….",
"그레텔이 개라도 되는 듯 코를 벌름거렸다.^n하지만 『냄새가 나』라고 해도 나는 전혀 모르겠다.",
"그 아이가 냄새를 따라가자,^n찬장 안에 보관된 바게트 세 개를^n정말로 찾아냈다.",
"그레텔","와, 정말 있었어.^n오빠, 대단해!",
"빵을 발견한 그레텔의 얼굴이 환하게 빛났다.",
"나","(분명 남아 있을지도 모른다고 한 건 나지만…….^n 냄새를 따라 찾아낸 네가 더 대단한 것 같은데)",
"나","으, 응.^n아무튼 다행이다.^n이걸로 보관해 둘 수 있겠어──",
"내가 그렇게 말한 바로 그 순간이었다.",
"그레텔","우물우물우물우물우물우물우물우물…… 꿀꺽.",
"모처럼 찾아낸 빵을^n그레텔이 게걸스럽게 먹기 시작했다.",
"나","(──또냐──!)",
"나","아, 그레텔?^n그렇게 많이 먹어 버리면,^n표식으로 쓸 빵이 없어져!",
"그레텔","미, 미안해, 오빠.^n","하지만 배가 고파져서……^n","냠냠냠냠냠냠냠냠.",
"그렇게 말하면서도 그레텔은 두 번째 빵을 입에 물고 있었다.^n마치 슬라이서에 넣은 듯,^n긴 바게트가 눈 깜짝할 사이 사라져 간다.",
"나","(조금 전에 저녁을 먹었을 텐데.^n 왜 벌써 배가 고픈 걸까?)",
"나","──아니, 아!^n잠깐만, 그레텔!^n정말 다 없어지겠다니까!",
"내가 감탄 반 기막힘 반으로 그런 생각을 하는 사이,^n빵은 이미 마지막 하나도 절반밖에 남지 않았다.",
"그레텔","우물우물우물우물쩝쩝쩝쩝.^n","앗! ","……꼬, 꿀꺽.",
"내 말을 듣고 필사적으로 먹기를 멈춘 듯한 그레텔이^n꿀꺽 침을 삼키며 목울대를 울렸다.",
"그레텔","으으으…… 미, 미안해.^n그, 그렇지만──",
"금방이라도 울 듯한 얼굴로 이쪽을 빤히 본다.^n아마 무척 먹고 싶은 거겠지.",
"나","뭐…… 어쩔 수 없나.^n먹다 만 걸 남겨 봐야 소용없으니,^n그건 먹어도 돼.",
"나","식사에 빵이 나오면 남을 때도 있다는 걸 알았으니까.^n다음에 빵이 나오면 또 가지러 오자.",
"그레텔","고, 고마워, 오, 오빠!^n","오물오물오물오물오물오물!",
"신이 나서 남은 빵을 깨끗이 먹어 치우는 그레텔.",
"그 아이가 그렇게 맛있게 빵을 먹는 모습을 보고 있자니,^n내 마음속까지 포근하게 따뜻해지는 느낌이 들었다.",
"게르다","후후…… 즐거워 보이네.",
"그레텔이 먹는 모습을 지켜보던 내게^n옆에서 말을 건 사람이 있었다.^n게르다였다.",
"나","게르다…….^n이 시간에 무슨 일이야?",
"게르다","목이 말라서.^n물을 마시러 왔을 뿐이야.",
"그렇게 말한 게르다는 컵에 물을 따라^n다 마신 뒤 우리를 바라보며 미소 지었다.",
"게르다","후후…….^n왠지 너희, 진짜 남매 같네.",
"나","어…… 그, 그런가.",
"게르다","응…….^n왜 그런지 그리운 느낌이 들어.^n옛날에 이런 광경을 본 것 같아…….",
"나","그건 네…… 기억이야?",
"게르다","글쎄…… 잘 모르겠어.^n떠올리려고 해도 생각나지 않으니까…….",
"나","……미안, 이상한 걸 물어서.",
"게르다","아니, 딱히 신경 쓰지 마.^n너도 똑같잖아.^n","아니, 이 『낙원』에 있는 환자는 모두 그래.",
"그렇다. 게르다와 나만이 아니다.^n그레텔도 분명 소중한 것을 여러 가지^n잊어버리고 왔을 것이다.",
"나","(그 아이가 이렇게까지 필사적으로 음식을 먹는 것도,^n 어쩌면 잊어버린 무언가를^n 되찾으려고 하기 때문일까……?)",
"──모르겠다.^n그 아이에게는 어떤 『과거』가 있을까.^n어떻게 해야 그것을 되찾아 줄 수 있을까.",
"게르다","……다행이네.^n그레텔은 줄곧 오빠를 찾고 있었으니까.^n누군가를 계속 찾아다니는 괴로움은 나도 잘 알아.",
"나","게르다…….",
"게르다","물론 네가 진짜 헨젤이 아닐지도 몰라.^n하지만…… 그 역할을 자청한다면,^n그것도 분명 좋은 일이야.",
"그리고 다시 한번 미소 지었다.^n그녀의 얼굴에는 말로 다 할 수 없는 쓸쓸한 기색이 감돌았다.",
"그녀가 어떤 마음으로 그런 말을 하는지^n나는 잘 모르겠다.",
"그녀에게 뭐라고 대답해야 할까.^n그렇게 망설이자 게르다가 한마디 더 중얼거렸다.",
"게르다","지켜 줘.",
"그것은 몹시 다정한 미소였다.^n하지만 동시에 몹시 연약하고 어딘가 덧없는 미소라고^n나는 생각할 수밖에 없었다.",
"그녀가 한 말도^n몹시 무심한 듯 남긴 말이었는데,^n어째서 이렇게 강하고 무겁게 내 안에 울리는 걸까──",
"그레텔","아, 게르다 씨.^n아, 안녕하세요.",
"빵을 다 먹고 한숨 돌린 모양이다.^n그레텔이 이제야 이쪽을 알아보고 꾸벅 고개를 숙였다.",
"게르다","안녕, 그레텔.",
"그레텔","……무, 무슨 일이야, 게르다 씨?",
"게르다","응? 무슨 일이냐니…… 뭐가?",
"그레텔","괘, 괜찮아?^n왠지 얼굴빛이…… 안 좋아.",
"그레텔도 그녀의 이상을 눈치챈 모양이다.^n그렇게 물었지만 게르다는 고개를 저어 부정했다.",
"게르다","나는 괜찮아.^n","──빨리 여기서 도망치고 싶다고는 생각하지만…….",
"게르다","슬슬 소등 시간이네.^n방으로 돌아갈까.",
"이야기를 끝내려는 듯 게르다는 출구로 향했다.^n우리도 그녀를 따라 주방을 나섰다.",
"우리는 도중까지 함께 복도를 돌아간 뒤,^n각자의 방으로 헤어졌다."]
def main():
 expected=set(range(1,123))
 if len(TARGETS)!=123:raise SystemExit(f"target count {len(TARGETS)-1}")
 rows={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1304.gsc":continue
   i=int(x["slot"])
   if i in expected:rows[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(rows)!=expected or lookup!=set(range(123,181)):raise SystemExit("coverage mismatch")
 entries=[]
 for i in sorted(expected):
  row,t=rows[i],str(TARGETS[i]);s=str(row["source_text"])
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}: {CARET_RE.findall(s)} != {CARET_RE.findall(t)}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":s,"source_raw_sha256":row["source_raw_sha256"],"target_text":t,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 대기"})
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1304_slots_00001_00122_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};out=PROJECT/"packets"/"drafts"/"1304_slots_00001_00122_draft.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[123,180],"output":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
