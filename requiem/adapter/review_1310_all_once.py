from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");DRAFT=PROJECT/"packets"/"drafts"/"1310_slots_00001_00042_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
2:"문을, 자물쇠를, 잠가야 해…….",
3:"게르다는 반쯤 미친 상태로 잠꼬대처럼 중얼거렸다.",
5:"어쩔 수 없이 시설을 돌아다닐 때 몰래 모은 도구를 써서^n이것저것 시행착오를 거쳤다.",
8:"진찰실에서 훔쳐 온 머리핀으로 열쇠 구멍 안쪽을 더듬었지만,^n도중에 뚝 부러져 열쇠 구멍을 막는 꼴이 되어^n오히려 역효과가 났다.",
10:"조금만 더 냉정하게 생각할 힘이 남아 있었다면^n어쩌면 가능했을지도 모르지만,^n안타깝게도 지금 그녀는 몹시 지쳐 정신이 쇠약해진 상태였다.",
12:"마, 막아야 해…… 아무도 들어오지 못하게…….",
13:"다음으로 그녀는 문 앞에 가구를 쌓아 올려^n바리케이드를 만들려고 했다.",
15:"유일하게 움직일 수 있는 것은 벽난로 앞 흔들의자뿐이지만,^n그것 하나로는 도저히 바리케이드가 되지 않는다.",
19:"그런 적당한 물건은 방에 없다는 사실을 깨닫기까지^n상당한 시간을 허비했다.",
22:"서둘러야 한다.^n『그것』이 오기 전에.",
25:"어쨌든 이 방에 있으면 안 된다.^n빨리 달아나야 해──하지만 어디로?^n어디든 좋아, 일단 방에서 뛰쳐나가자.",
26:"문을 열자 그녀는^n『누군가』의 몸에 세게 부딪혀 튕겨 나왔다.",
27:"시야가 어두워진다.^n검푸르고 불길하게 뻗어 손쉽게 게르다를 뒤덮는 사람의 그림자 때문에──",
31:"뱀 앞의 개구리처럼 얼어붙어 게르다는 떨었다.^n팔다리에서 힘이 빠져나간다.",
32:"어제까지 그녀의 안을 차지하던 분노는 모두 타 버렸다.^n남은 불씨 속에는 체념만이 남았다.",
34:"안녕, 게르다. 좋은 저녁이야.",
35:"남자의 그림자가 그녀를 덮칠 듯 다가와 히죽 웃었다.",
36:"아프다거나 괴롭다거나 굴욕적이라거나 역겹다거나,^n그런 것들도 함께 타 버렸으면 좋았을 텐데.",
37:"마음까지 인형이 되어 버린다면,^n몸이 인형처럼 다뤄져도 신경 쓰이지 않을 텐데.",
39:"게르다에게 남은 게르다다운 부분이^n그녀 자신을 상처 입히고 몰아붙인다.",
42:"비단실보다도 가느다란 목소리로 게르다는 흐느꼈다.^n그 목소리가 약탈자의 정복욕을 더욱 부추길 뿐인 줄도 모른 채.",
}
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 draft=json.loads(DRAFT.read_text(encoding="utf-8"));expected=set(range(1,43))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1310_slots_00001_00042_draft":raise SystemExit("unexpected draft")
 entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]};changes=[]
 if set(entries)!=expected:raise SystemExit("draft coverage mismatch")
 for i,t in CORRECTIONS.items():
  before=str(entries[i]["target_text"]);entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 catalog={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1310.gsc":continue
   i=int(x["slot"])
   if i in expected:catalog[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(catalog)!=expected or lookup!=set(range(43,101)):raise SystemExit("catalog/lookup mismatch")
 final=[]
 for i in sorted(expected):
  e=entries[i];s,t=str(e["source_text"]),str(e["target_text"])
  if s!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]:raise SystemExit(f"source drift {i}")
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"});final.append(e)
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1310_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,42],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[43,100],"release_ready":False,"entries":final};out=PROJECT/"packets"/"reviewed"/"1310_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,42],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_43_100_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};ap=PROJECT/"audit"/"translation_review_1310_complete.json";ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
