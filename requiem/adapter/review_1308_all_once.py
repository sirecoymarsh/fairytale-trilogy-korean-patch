from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");DRAFT=PROJECT/"packets"/"drafts"/"1308_slots_00001_00051_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
2:"오, 오빠!^n오빠아!!",
4:"그휴헤휴헤헤에…….^n이제 방해꾼은 없어졌네, 그레텔아.^n두, 두, 둘만 남았어…… 부슛.",
5:"이름 없는 소년이 계단 아래로 굴러떨어진 채^n일어나지 않는 것을 확인하자,^n코미야는 기름진 얼굴을 그레텔에게 돌렸다.",
8:"소년이 굴러떨어져 공황에 빠졌는지,^n그레텔은 그 자리에 우두커니 서서^n목과 어깨를 부들부들 떨고 있다.",
10:"자…… 오빠와 함께^n이번에야말로 기분 좋은 일을 하자아?",
11:"앞으로 내민 두 손을 꿈틀거리며,^n냄새나는 숨을 헉헉 흩뿌리면서^n코미야가 그레텔에게 조금씩 다가간다.",
13:"……안 돼…….^n……오빠한테……, ……안 돼!",
14:"그저 울부짖을 뿐이던 그레텔이었지만,^n이번만은 달랐다.",
16:"──우리 오빠에게 무슨 짓이에요!!",
17:"외치면서 그레텔이 두 손을 코미야에게 내밀었다.",
21:"단풍나무 가지처럼 가느다란 팔에서 나온 믿을 수 없는 괴력에^n코미야의 몸이 날아갔다.",
24:"복도 벽에 뒤통수를 세게 부딪친 코미야는 고통에 몸부림쳤다.",
26:"히, 히익! 피, 피가, 피가 나잖아아아!^n누, 누구! 의사를 불러 줘!! 죽겠어어!!",
27:"손바닥에 철퍼덕 묻은 피를 확인한 그는^n요란한 비명을 지르며 벌떡 뛰어올라 그 자리에서 달아났다.",
28:"그때 둥근 거구로 굴러가듯 도망치는 코미야의 품에서^n툭 떨어진 것이 있었다.",
34:"얼결에 카드를 주웠지만 살펴볼 여유는 없어서,^n그녀는 이름 없는 소년──헨젤에게 달려갔다.",
37:"조금 전까지의 용감한 모습은 어디 갔는지.^n테디베어의 다리를 쥐어짜듯 붙잡아 늘어뜨리고,^n완전히 평소의 소심한 모습으로 허둥댄다.",
40:"생각이 나서 고개를 들고 두리번거리며 주위를 살폈다.",
41:"그러자 인기척 없는 복도 끝에^n불쑥 나타난 사람의 모습이 눈에 들어왔다.",
44:"──이런, 그레텔 아니야.",
46:"대체 무슨──^n",
50:"사…… 살려 주세요!!^n오, 오빠가, 오빠가아!!",
51:"그녀는 지옥에서 부처라도 만난 듯,^n달려들 기세로 이케노에게 도움을 청했다.",
}
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 draft=json.loads(DRAFT.read_text(encoding="utf-8"));expected=set(range(1,52))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1308_slots_00001_00051_draft":raise SystemExit("unexpected draft")
 entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]};changes=[]
 if set(entries)!=expected:raise SystemExit("draft coverage mismatch")
 for i,t in CORRECTIONS.items():
  before=str(entries[i]["target_text"]);entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 catalog={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1308.gsc":continue
   i=int(x["slot"])
   if i in expected:catalog[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(catalog)!=expected or lookup!=set(range(52,110)):raise SystemExit("catalog/lookup mismatch")
 final=[]
 for i in sorted(expected):
  e=entries[i];s,t=str(e["source_text"]),str(e["target_text"])
  if s!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]:raise SystemExit(f"source drift {i}")
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"});final.append(e)
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1308_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,51],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[52,109],"release_ready":False,"entries":final};out=PROJECT/"packets"/"reviewed"/"1308_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,51],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_52_109_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};ap=PROJECT/"audit"/"translation_review_1308_complete.json";ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
