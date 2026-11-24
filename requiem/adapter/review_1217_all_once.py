from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko"); DRAFT=PROJECT/"packets"/"drafts"/"1217_slots_00001_00205_draft.json"; CARET_RE=re.compile(r"\^(?:n|m|d\d+)"); JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
27:"어머, 당신. 안녕하신가요.^n그동안 어떻게 지내셨나요?",
28:"앨리스는 치맛자락을 잡고 몸을 낮췄다.^n이런 인사도 정말 오랜만에 보는 느낌이다.",
39:"다, 당신과는 상관없는 일이에요.^n기억도 없는데 주식에 손을 댈 수는 없잖아요.^n그러니까 주, 주식 이야기는 됐어요. 그만하죠.",
55:"보세요, 이렇게 말씀하시잖아요.^n당신과 관련된 이야기는 아무것도 하지 않았어요.",
59:"친구라는 유대감을 높이려고 누군가를 따돌리는 일은^n아이들의 세계에서는 흔하지만(어른들의 세계에서도?),^n당하는 쪽의 비참한 기분은 이루 말할 수 없다.",
70:"앨리스는 그런 내 안색을 살피며^n앞뒤가 맞지 않게 말을 이었다.",
84:"아아, 맞다. 이러면 안 되지.^n어서 가지 않으면 안 돼, 자네. 목이 잘리고 말 거야.",
88:"하지만 나이도 지긋한 아저씨가 필사적으로^n앨리스의 망상에 장단을 맞추는 모습이 딱해,^n나는 일단 그 자리를 떠나기로 마음먹었다.",
104:"──바, 반갑습니다. 공작부인입니다.",
127:"너무나도 근심 없는 미소로 이케노 씨는 속뜻을 감춘다.",
140:"사람마다 제각각이지만.^n자신을 지키기 위해 『앨리스』를 택한 아이는 대개^n빈정거리거나, 건방지거나, 따지기를 좋아하거나──",
142:"굳이 말하면 어두운 아이가 많았어.^n속마음을 간파당하지 않고 여러 일에 속지 않으려고,^n늘 긴장하고 있는 듯한 아이.",
154:"──있잖아, 나나시.^n원작 『이상한 나라의 앨리스』가^n어떻게 만들어졌는지 아니?",
158:"그래. 수학자 도지슨이 리델가의 세 자매와^n소풍을 갔던 황금빛 오후.^n막내딸 앨리스를 주인공으로 삼은 모험담을 그 자리에서 들려주었지.",
160:"그 이야기는 앨리스의 부탁으로 먼저 손으로 만든 책이 되었고,^n친구 부부의 권유로 출간되었어.^n──그건 그렇고.",
170:"누구나 될 수 있었고, 어떤 여자아이의 마음 깊은 곳에도 있는,^n어른에게 이야기를 졸라 대는 아이로서의 『앨리스』…….",
185:"비밀이 늘고 다들 심술궂어졌다는 사실은^n절절히 느끼고 있지만,^n분명 그런 뜻은 아니겠지.",
188:"연막에 휘말린 듯 답답한 마음을 품은 채^n정원에서 돌아오는 길.",
196:"아마 주빈은 나이고,^n분명 악의보다 선의로 가득한 행사일 것이라고도 생각한다.",
202:"그녀는 왠지 이런 속내를 감춘 축제에는^n끼지 않을 것 같은 이미지가 있었으니까.",
}
def slot(uid:str)->int:
 m=re.search(r"slot/(\d+)$",uid)
 if not m: raise ValueError(uid)
 return int(m.group(1))
def main()->int:
 draft=json.loads(DRAFT.read_text(encoding="utf-8"))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1217_slots_00001_00205_draft": raise SystemExit("unexpected draft")
 expected=set(range(1,206)); entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]}
 if set(entries)!=expected: raise SystemExit("draft coverage mismatch")
 changes=[]
 for index,target in CORRECTIONS.items():
  before=str(entries[index]["target_text"]); entries[index]["target_text"]=target
  if before!=target: changes.append({"slot":index,"before":before,"after":target})
 catalog={}; lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as handle:
  for line in handle:
   item=json.loads(line)
   if item.get("file")!="1217.gsc": continue
   index=int(item["slot"])
   if index in expected: catalog[index]=item
   elif "lookup_keys" in item.get("lanes",[]): lookup.add(index)
 if set(catalog)!=expected or lookup!=set(range(206,264)): raise SystemExit("catalog/lookup mismatch")
 final=[]
 for index in sorted(expected):
  e=entries[index]; source,target=str(e["source_text"]),str(e["target_text"])
  if source!=catalog[index]["source_text"] or e["source_raw_sha256"]!=catalog[index]["source_raw_sha256"]: raise SystemExit(f"source drift {index}")
  if CARET_RE.findall(source)!=CARET_RE.findall(target): raise SystemExit(f"caret mismatch {index}")
  if JAPANESE_RE.search(target): raise SystemExit(f"Japanese residue {index}")
  target.encode("cp949",errors="strict"); e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"}); final.append(e)
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1217_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,205],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[206,263],"release_ready":False,"entries":final}
 out=PROJECT/"packets"/"reviewed"/"1217_all_translatable_slots_reviewed_once.json"; out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,205],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_206_263_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()}
 ap=PROJECT/"audit"/"translation_review_1217_complete.json"; ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
