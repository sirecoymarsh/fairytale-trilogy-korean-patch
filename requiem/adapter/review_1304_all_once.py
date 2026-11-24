from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");DRAFT=PROJECT/"packets"/"drafts"/"1304_slots_00001_00122_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
1:" 나는 그레텔과 함께,^n『헨젤과 그레텔』에서 숲에 뿌릴 『표식』으로 쓸^n 빵을 찾으러 주방에 왔다.",
2:"저녁에 닭고기 소테와 함께 바게트가 나왔으니,^n남은 빵이나 여분이 주방에 있을지도 모른다고^n생각해서 그레텔을 데려온 것이다.",
5:"어제 이곳에서 벌어진 불탄 시체 소동 탓에,^n모처럼 구워 줬을 빵은^n전부 못 쓰게 되고 말았다.",
7:"와…… 벌써 완전히 반짝반짝해졌네.",
11:"생각보다 그을음이 많이 뿜어져 나오진 않았지만,^n그래도 닦아 내기는 힘들었겠다는 생각이 든다.",
18:"응, 어제 탄 빵 말고.^n제대로 고소한 냄새야.^n",
20:"그레텔이 개라도 되는 듯 코를 벌름거렸다.^n하지만 『냄새가 나』라는 말을 들어도 나는 전혀 모르겠다.",
21:"그레텔이 냄새를 따라가자,^n찬장 안에 보관된 바게트 세 개를^n정말로 찾아냈다.",
23:"와, 정말 있었어.^n오빠는 대단해!",
26:"(분명 남아 있을지도 모른다고 한 건 나지만…….^n 냄새를 따라 찾아낸 네 쪽이 더 대단한 것 같은데)",
28:"으, 응.^n아무튼 다행이다.^n이걸로 챙겨 둘 수 있겠어──",
34:"(──또다──!)",
36:"아, 그레텔?^n그렇게 많이 먹어 버리면,^n표식으로 쓸 빵이 없어져!",
41:"말하면서도 그레텔은 두 번째 빵을 입에 물고 있었다.^n마치 슬라이서에 넣은 듯,^n길고 긴 바게트가 눈 깜짝할 사이 사라져 간다.",
45:"──아니, 앗!^n잠깐만, 그레텔!^n정말 다 없어지겠다니까!",
46:"내가 감탄 반 기막힘 반으로 그런 생각을 하는 사이,^n빵은 이제 마지막 한 개마저 절반밖에 남지 않았다.",
51:"내 말을 듣고 필사적으로 먹기를 멈춘 듯한 그레텔이^n꿀꺽 침을 삼켰다.",
56:"뭐…… 어쩔 수 없나.^n먹던 걸 남겨 봐야 소용없으니,^n그건 먹어도 돼.",
58:"식사에 빵이 나오면 남을 때도 있다는 걸 알았으니까.^n다음에 빵이 나오면 또 가지러 오자.",
63:"그 아이가 그렇게 맛있게 빵을 먹는 모습을 보고 있자니,^n내 마음속까지 포근해지는 느낌이 들었다.",
66:"그레텔이 먹는 모습을 지켜보던 내게^n옆에서 말을 건 사람이 있었다.^n바로 게르다였다.",
71:"그렇게 말한 게르다는 컵에 물을 따라^n그 물을 다 마신 뒤 우리를 바라보며 미소 지었다.",
73:"후후…….^n왠지 너희, 꼭 진짜 남매 같네.",
77:"응…….^n어째서인지 그리운 느낌이 들어.^n옛날에 이런 광경을 본 것 같아…….",
81:"글쎄…… 잘 모르겠어.^n떠올리려고 해도 떠오르지 않으니까…….",
85:"아니, 괜찮아. 신경 쓰지 마.^n너도 똑같잖아.^n",
87:"그래. 게르다와 나만이 아니다.^n그레텔도 분명 소중한 것을 여러 가지^n잊어버리고 왔을 것이다.",
90:"──모르겠다.^n그 아이에게는 어떤 『과거』가 있을까.^n어떻게 해야 그것을 되찾아 줄 수 있을까.",
92:"……다행이네.^n그레텔은 줄곧 오빠를 찾고 있었으니까.^n누군가를 계속 찾는 괴로움은 나도 잘 알아.",
96:"물론 네가 진짜 헨젤이 아닐지도 몰라.^n하지만…… 그 역할을 맡겠다고 나선다면,^n그것도 분명 좋은 일이야.",
97:"그리고 다시 한번 미소 지었다.^n그녀의 얼굴에는 말로 다 할 수 없는 쓸쓸한 기색이 감돌았다.",
99:"그녀에게 어떻게 대답해야 할까.^n그렇게 망설이자 게르다가 한마디 더 중얼거렸다.",
102:"그것은 몹시 다정한 미소였다.^n하지만 동시에 몹시 연약하고 어딘가 덧없는 미소라고^n느껴질 수밖에 없었다.",
103:"그녀가 한 말 역시^n몹시 무심한 듯 남겨진 말이었는데,^n어째서 이렇게 강하고 무겁게 내 안에 울리는 걸까──",
105:"아, 게르다 씨.^n아, 안녕.",
106:"빵을 다 먹고 한숨 돌린 모양이다.^n그레텔이 이제야 이쪽을 알아보고 꾸벅 고개를 숙였다.",
110:"……게, 게르다 씨, 무슨 일이야?",
112:"응? 무슨 일이라니…… 뭐가?",
115:"그레텔도 그녀의 이상을 눈치챈 모양이다.^n그렇게 물었지만 게르다는 고개를 저어 부정했다.",
118:"──빨리 여기서 도망치고 싶다는 생각은 하지만…….",
121:"이야기를 끝내려는 듯 게르다는 출구로 향했다.^n우리도 그녀를 따라 주방을 나섰다.",
122:"우리는 도중까지 함께 복도를 돌아간 뒤,^n각자의 방으로 헤어졌다.",
}
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 draft=json.loads(DRAFT.read_text(encoding="utf-8"));expected=set(range(1,123))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1304_slots_00001_00122_draft":raise SystemExit("unexpected draft")
 entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]};changes=[]
 if set(entries)!=expected:raise SystemExit("draft coverage mismatch")
 for i,t in CORRECTIONS.items():
  before=str(entries[i]["target_text"]);entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 catalog={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1304.gsc":continue
   i=int(x["slot"])
   if i in expected:catalog[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(catalog)!=expected or lookup!=set(range(123,181)):raise SystemExit("catalog/lookup mismatch")
 final=[]
 for i in sorted(expected):
  e=entries[i];s,t=str(e["source_text"]),str(e["target_text"])
  if s!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]:raise SystemExit(f"source drift {i}")
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"});final.append(e)
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1304_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,122],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[123,180],"release_ready":False,"entries":final};out=PROJECT/"packets"/"reviewed"/"1304_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,122],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_123_180_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};ap=PROJECT/"audit"/"translation_review_1304_complete.json";ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
