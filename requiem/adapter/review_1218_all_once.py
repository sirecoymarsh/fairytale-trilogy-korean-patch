from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");DRAFT=PROJECT/"packets"/"drafts"/"1218_slots_00001_00067_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
2:"산들바람을 타고 나무 사이를 달려, 활짝 핀 꽃을 축복하고,^n붉은 페인트투성이 흰 장미를 달래며 흘러간다.",
3:"그 목소리는 큰 나무 아래에서 어깨를 맞댄 두 사람 중,^n나이가 더 많은 소녀의 입술에서 흘러나오고 있었다.",
13:"잠든 앨리스의 뺨이 부우 하고 부풀고,^n항의 같은 말을 웅얼웅얼 중얼거리는 모습을 보고,^n라푼젤은 조용히 미소 지었다.",
21:"잠든 앨리스가 조르고 있는데도^n라푼젤이 페이지를 넘기려 하지 않은 것은,^n차라리 자신도 낮잠에 몸을 맡기고 싶어졌기 때문이다.",
23:"갑자기 방에 나타나 꼭 손을 잡더니^n힘차게 끌고 걷기 시작한 앨리스 때문에,^n라푼젤은 몹시 당황했다.",
38:"그렇게 멀리 떨어져 표정도 희미했을 텐데,^n어떻게 라푼젤의 지루함과 불만을 알아차렸을까.",
51:"앨리스는 흔들리는 눈길을 라푼젤에게 둔 채,^n헤실거리며 뺨을 풀었다.",
60:"정말 앨리스의 언니였다면 좋았을 텐데.^n오직 그 생각만을 간절하고 또 간절하게 할 뿐이었다.",
65:"──라푼젤은 처음에는 무척 놀랐습니다.^n자란 뒤로 마녀 말고 다른 사람을 만난 것은 이번이 처음이었기 때문입니다.",
67:"이번에는 반드시,^n앨리스가 다시 깨어날 때까지 끊이지 않게 이어 가겠다고,^n남몰래 다짐하면서.",
}
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 draft=json.loads(DRAFT.read_text(encoding="utf-8"))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1218_slots_00001_00067_draft":raise SystemExit("unexpected draft")
 expected=set(range(1,68));entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]};changes=[]
 if set(entries)!=expected:raise SystemExit("draft coverage mismatch")
 for i,t in CORRECTIONS.items():
  before=str(entries[i]["target_text"]);entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 catalog={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1218.gsc":continue
   i=int(x["slot"])
   if i in expected:catalog[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(catalog)!=expected or lookup!=set(range(68,126)):raise SystemExit("catalog/lookup mismatch")
 final=[]
 for i in sorted(expected):
  e=entries[i];s,t=str(e["source_text"]),str(e["target_text"])
  if s!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]:raise SystemExit(f"source drift {i}")
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"});final.append(e)
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1218_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,67],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[68,125],"release_ready":False,"entries":final};out=PROJECT/"packets"/"reviewed"/"1218_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,67],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_68_125_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};ap=PROJECT/"audit"/"translation_review_1218_complete.json";ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
