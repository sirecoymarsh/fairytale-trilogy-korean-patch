from __future__ import annotations
import hashlib,json,re
from pathlib import Path
P=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
C={
4:"근원을 따라가 보니 연기와 냄새가 나는 곳은^n같은 층의 주방인 듯했다.^n가라앉지 않는 혼란스러운 목소리와 함께 열린 문에서 새어 나온다.",
6:"콜록, 콜록콜록…….^n뭐, 뭐예요, 이게 뭐죠……!?",
8:"하늘의 구름을 그대로 가둔 듯한 광경 너머에서,^n기침하고 탄식하며 혼란에 빠진 여자아이들의 목소리가 울려온다.",
18:"콧속에 끈적하게 달라붙는 듯 기름지고 불쾌한 냄새,^n폐까지 그을릴 듯한 탄내,^n너무 구워 망쳐 버린 빵과 구운 과자의 냄새.",
21:"콜록, 콜록…… 아, 아파.^n부딪쳐서 볼을 떨어뜨렸어──",
25:"진정해요, 그레텔. 볼은 나중에 주워도 돼요.^n저도 딸기 소스 병을 엎질렀지만,^n신경 쓰지 않기로 했어요!",
29:"그런데…… 출구는 어디죠? 벌써 하룻밤 내내 걸은 기분이에요!",
32:"안에 있는 여자아이들──아마 앨리스와 그레텔이^n공황에 빠지는 것도 무리는 아니다.^n다그치는 사람은 오딜일까.",
45:"그런데 저건…… 방금, 누구죠? 누구예요?^n저는 저런 걸 굽지 않았어요!",
57:"아무리 그래도 너무 황당하다.^n분명 앨리스가 잘못 봤거나 평소처럼 이상하게 해석한 것이다.",
58:"그렇게 자신을 타이르지만 마음에 와닿지 않는다.^n한 번도 맡아 본 적 없는 불쾌한 냄새와 완전히 탁해진 공기 때문이다.",
60:"목소리만 주고받을 뿐 서로 아무것도 해 줄 수 없는 고립된 세계에서는,^n불길한 상상일수록 확실한 감촉을 지니고 부풀어 간다.",
62:"(아니, 아니야. 그럴 리 없어. 사람을 구웠다면 큰일이잖아.^n──하지만 『사람이 타는 냄새』라고 들으니^n왠지 정말 그런 것 같기도 하고……)",
66:"하아……?^n너희, 사람이라도 구웠어?",
72:"사람이랑 같이 구워진 새까만 과자라도 괜찮다면,^n나중에 마음껏 먹든가?",
78:"이 연기 속에서도 침착함을 잃지 않던 오딜의 목소리가,^n희미한 소리와 함께 갑자기 끊겼다.",
83:"꺄악! 누, 누구죠?^n누가 저를 만졌어요……?",
89:"뭐야, 이게. 무슨 일이 있었던 거야!?^n화재는 아닌 것 같지만…… 연기가 너무 심해.",
95:"애…… 앨리스가 화덕 안에서 사람이 나왔다고 했어.^n새, 새까맣게 탄 사람이…… 타, 타고…… 읏.^n",
100:"뭐라고?^n새까맣게 탄…… 사람? 화덕?^n",
109:"넘어졌어요…….^n아…… 주스 병이 있네요.^n이걸 마시면 커져서 이 방에서 나갈 수 있을까요…….",
117:"수수께끼의 연기와 냄새, 새까맣게 탄 시체.^n엄청난 사태라고 믿고 초조해했지만,^n결국 이건 그저 한바탕 소동으로 끝나는 게 아닐까──",
122:"겹겹이 드리운 연기 장막이 한 장, 또 한 장 걷히고,^n이곳저곳에서 주방의 본래 모습이^n희미하게 떠오른다.",
125:"활짝 열린 창문 앞 허리 높이 선반에 기대어,^n신선한 공기를 손으로 부치며 오딜이 중얼거렸다.",
128:"스읍, 하아, 스읍, 하아.^n다, 다행이야…….",
131:"훈연기 속 칠면조는 이런 기분일까요.^n",
137:"오딜은 우리의 감사 인사에 거의 반응하지 않았다.^n살짝 눈썹을 올렸을 뿐, 창밖을 향한 시선은 움직이지 않는다.",
142:"연기 속에서 소동을 들으며 막연히^n식기와 식재료가 흩뿌려진 난장판을^n떠올렸지만 실제로는 그 정도가 아니다.",
147:"네, 네. 그랬어요!^n제가 환풍기가 어디였더라 싶어서,^n저기 화덕 안을 들여다보니──",
151:"연기가 걷혀 상황과 마주하게 되자,^n잊어 가던 공황이 다시 밀려온 것 같았다.",
156:"네……? 어, 없다고요?^n저는 이 두 눈으로 봤다고요.",
161:"화덕 안에는^n탄화된 무언가의 덩어리가 여기저기 굴러다니고,^n검게 녹아내린 끈적한 액체가 곳곳에 달라붙어 있다.",
163:"코를 찌르는 것은 기름지고 끈적한 냄새로,^n진정하고 자세히 맡아 보면 분명^n고기를 굽는 냄새와 비슷한 면도 있는 것 같다.",
169:"어느새 뒤에 서 있던 게르다의 목소리에,^n나는 소름이 돋아 뒤돌아보았다.^n목소리가 가까운 것도 그렇지만 내용이 너무나 무서웠다.",
172:"『새까맣게 탄 시체』를 봤다는 말을 앨리스가 하는 것과 게르다가 하는 것은^n그 무게가 완전히 다르다.",
174:"게르다는 그 사실을 알면서도 말할 수 있었던 걸까.",
179:"그 뺨은 창백하고 눈빛도 힘없으며,^n평소의 게르다와는 다른, 금방이라도 쓰러질 듯한 덧없는 모습이었다.",
185:"나도──믿고 싶지 않았어…….^n잘못 본 거나 환상이라고 믿으려 했지만,^n그래도 역시 안 되네. 얼버무릴 수 없어.",
189:"아직 늦지 않았다.^n게르다가 착각이었다고 생각해 주면 없던 일로 만들 수 있다.^n그것이 헛된 발버둥임은 나 자신도 알고 있었다.",
195:"──사람이었던 것 같아.^n그래, 맞아. 역시 나 자신을 속일 수는 없어.^n싫은 일일수록 제대로 인정해야 해…….",
202:"나, 아까 연기 속에서 누군가와 스쳐 지나갔어.^n검은 사람 그림자──처음 보는 키였어.",
209:"오딜은 방금 내놓은 증언을^n아무렇지도 않게 자기 손으로 잘라 버린다.",
215:"문밖에서 갑자기 부르는 소리가 들려,^n주방 안에 있던 우리는 모두 그쪽을 보았다.",
223:"저는 여기서 이렇게 지켜보는 것밖에는 할 수 없어서.^n부끄러울 따름이에요.",
225:"방금 전에야 지나가던 분을 붙잡았어요.^n다른 분들도 불러 주시는 듯해서──",
232:"네? 무슨 기관 말인가요?^n무슨 일이 있었던 건가요?",
238:"일상이 위협받는 비명 같은, 소리 없는 목소리.",
240:"어쩌면 살인 사건일지도 몰라.^n──진상이 밝혀질 때까지 나는 한동안^n푹 자기는 어려울 것 같아.",
243:"^n^m──모두 중 한 명, 죄인이 있다──",}
R=re.compile(r"\^(?:n|m|d\d+)");J=re.compile(r"[\u3040-\u30ff]")
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 paths=[P/"packets"/"drafts"/n for n in ("1134_slots_00001_00080_draft.json","1134_slots_00081_00160_draft.json","1134_slots_00161_00243_draft.json")];es={}
 for path in paths:
  d=json.loads(path.read_text(encoding="utf-8"))
  if d.get("review_passes_completed")!=0:raise SystemExit("not draft")
  for e in d["entries"]:
   i=slot(str(e["uid"]));
   if i in es:raise SystemExit(f"dup {i}")
   es[i]=dict(e)
 expected=set(range(1,244));changes=[]
 if set(es)!=expected:raise SystemExit("coverage")
 for i,t in C.items():
  b=str(es[i]["target_text"]);es[i]["target_text"]=t
  if b!=t:changes.append({"slot":i,"before":b,"after":t})
 cat={};lookup=set()
 with (P/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for l in h:
   x=json.loads(l)
   if x.get("file")!="1134.gsc":continue
   i=int(x["slot"])
   if i in expected:cat[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(cat)!=expected or lookup!=set(range(244,302)):raise SystemExit("catalog lookup")
 final=[]
 for i in sorted(expected):
  e=es[i];s,t=str(e["source_text"]),str(e["target_text"])
  if s!=cat[i]["source_text"] or e["source_raw_sha256"]!=cat[i]["source_raw_sha256"]:raise SystemExit(f"drift {i}")
  if R.findall(s)!=R.findall(t):raise SystemExit(f"caret {i}")
  if J.search(t):raise SystemExit(f"JP {i}")
  t.encode("cp949",errors="strict");e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·코드 검수 완료"});final.append(e)
 o={"schema":"fairytale-requiem-translation-map-v1","scope":"1134_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,243],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[244,301],"release_ready":False,"entries":final};out=P/"packets"/"reviewed"/"1134_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 a={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":o["scope"],"draft_inputs":[str(x) for x in paths],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,243],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"append_dialogue_slots_included":True,"lookup_slots_excluded":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};(P/"audit"/"translation_review_1134_complete.json").write_text(json.dumps(a,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**a,"changes":changes},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
