from __future__ import annotations
import hashlib,json,re
from pathlib import Path
P=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
C={
4:"오늘 진찰에서는 여러 검사를 받았다.^n형광빛이 도는 보라색 액체를 마시고, 시험관 네 개 분량의 피를 뽑히고,^n정체를 알 수 없는 시험 문제 같은 것도 풀었다.",
5:"마신 것이 이상하게 작용한 건지,^n피가 부족해진 건지, 머리를 너무 많이 쓴 건지──^n아무튼 머리는 무겁고 몸은 나른하다.",
8:"드물게 그런 생각을 떠올린 바로 그 순간.",
11:"몇 번인가 들은 적 있는,^n이제는 완전히 불길한 인상이 박혀 버린^n뻐꾸기 울음소리가 울렸다.",
13:"커다란 종을 울렸을 때 귓속에 남는 여운.^n그 『위화감의 파동』 같은 것에 일그러져 변질된,^n종잡을 수 없이 음울한 울림──",
15:"이유는 모르지만, 그래서 더욱 불길했다.^n이성보다 먼저 살갗으로 느낀 이상만큼 무서운 것은 없다.",
19:"내 시선을 기다렸다는 듯,^n부웅…… 하고 전원이 들어왔다.",
20:"지금까지는 전원이 들어오면 바로 선명한 영상이 비쳤다.^n하지만 내 눈앞에는 그저 흑백으로 된 화면 잡음만 흔들리고 있다.",
24:"눈은 못 박힌 채,^n평평한 화면 잡음 속에서 의미 있는 것을 계속 찾아 헤매며,^n시선을 돌릴 수가 없다.",
29:"나는 허벅지 근처를 문질러,^n손바닥에 밴 차가운 땀을 닦았다.",
30:"이상이 일어난 것은 고작 십여 초였다고 생각한다.^n그런데도 내 몸은 심지까지 꽁꽁 얼어 있었다.^n피부의 모든 모공이 움츠러들어 온몸에 소름이 돋았다.",
31:"마음도 얼버무릴 수 없을 만큼 겁에 질려 있었다.^n쿵쿵쿵쿵, 귓속에서 빠르게 울리는 종소리가 들린다.^n한동안은 손가락 하나 움직이는 것조차 무서울 만큼.",
32:"지금까지 보게 된 여자아이들의 모습과는 완전히 다른 의미로,^n없던 일로 만들고 싶다, 빨리 잊고 싶다고 바랐다.",
38:"화면 잡음은 사라지기 직전 갑자기 형태를 이루었다.^n그것은 검은 옷을 입은 창백한 피부의 여자아이──",
42:"분명 멀리서 들려온 비명이었는데,^n양쪽 귀에서 머리가 관통당한 듯했다.",
45:"하지만 이번 것은 정체를 아는 현상이다.^n그 사실이 나를 단숨에 진정시켰다.",}
R=re.compile(r"\^(?:n|d\d+)"); J=re.compile(r"[\u3040-\u30ff]")
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m: raise ValueError(u)
 return int(m.group(1))
def main():
 dpath=P/"packets"/"drafts"/"1133_slots_00001_00047_draft.json"; d=json.loads(dpath.read_text(encoding="utf-8"))
 if d.get("review_passes_completed")!=0: raise SystemExit("not draft")
 es={slot(str(e["uid"])):dict(e) for e in d["entries"]}; expected=set(range(1,48)); changes=[]
 if set(es)!=expected: raise SystemExit("coverage")
 for i,t in C.items():
  b=str(es[i]["target_text"]); es[i]["target_text"]=t
  if b!=t: changes.append({"slot":i,"before":b,"after":t})
 cat={}; lookup=set()
 with (P/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1133.gsc": continue
   i=int(x["slot"])
   if i in expected: cat[i]=x
   elif "lookup_keys" in x.get("lanes",[]): lookup.add(i)
 if set(cat)!=expected or lookup!=set(range(48,106)): raise SystemExit("catalog/lookup")
 final=[]
 for i in sorted(expected):
  e=es[i]; s,t=str(e["source_text"]),str(e["target_text"])
  if s!=cat[i]["source_text"] or e["source_raw_sha256"]!=cat[i]["source_raw_sha256"]: raise SystemExit(f"drift {i}")
  if R.findall(s)!=R.findall(t): raise SystemExit(f"caret {i}")
  if J.search(t): raise SystemExit(f"JP {i}")
  t.encode("cp949",errors="strict"); e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·코드 검수 완료"}); final.append(e)
 o={"schema":"fairytale-requiem-translation-map-v1","scope":"1133_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,47],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[48,105],"release_ready":False,"entries":final}
 out=P/"packets"/"reviewed"/"1133_all_translatable_slots_reviewed_once.json"; out.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 a={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":o["scope"],"draft_inputs":[str(dpath)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,47],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()}; (P/"audit"/"translation_review_1133_complete.json").write_text(json.dumps(a,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({**a,"changes":changes},ensure_ascii=True,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
