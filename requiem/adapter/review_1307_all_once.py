from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");DRAFT=PROJECT/"packets"/"drafts"/"1307_slots_00001_00115_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
2:"뭐야, 아직도 저런 녀석과 어울려 다니는 거야?",
5:"복도를 걷고 있는데^n앞쪽에서 어디선가 들은 적 있는 목소리가 들려왔다.^n불길한 예감이 들어 나는 목소리가 나는 쪽으로 달렸다.",
7:"그러면 안 돼, 그레텔아. 잘 보렴.^n네 오빠가 저런 사람이었던가?^n조금 다르지 않니이?",
8:"예상대로 뚱뚱한 흰 가운 차림이 보였다.^n직원들이 『코미야』라고 부르던 사람이다.",
11:"아직도 정신을 못 차리고 그레텔을 따라다니며,^n스스럼없이 이곳저곳 만지면서 말을 걸고 있다.",
13:"있지, 그레텔은^n조금 더 조심해야 해.^n몸을 노리고 같은 편인 척하는 건 흔한 일이거든.",
16:"시, 싫어. 기…… 기분, 나빠…….",
18:"이제 그만하세요!",
21:"흐에에에…… 오, 오빠……,^n",
24:"그레텔이 내 등에 달라붙으며 눈물을 뚝뚝 흘렸다.^n그 작은 온기에 가슴이 확 뜨거워지는 것을 느꼈다.",
27:"나는 똑똑히 『적』을 바라보는 눈으로^n의사의 이중턱을 올려다보며 노려봤다.",
29:"또 괴롭히는 겁니까?^n직원이나 다른 의사 선생님에게 이를 거예요!",
30:"내가 그렇게 말하자 코미야는 움츠러들기는커녕,^n오히려 둥그런 얼굴을 새빨갛게 붉히고^n이를 드러내며 고함치기 시작했다.",
34:"제가 가짜일지도 모르는 건 맞아요.^n하지만 당신 같은 사람에게 이래라저래라 들을 이유는 없어요.",
39:"방금 만지고 있었잖아요.^n이 아이는 싫어했는데도!",
41:"뭐어? ──흥, 네 착각이야.^n남매라면 당연한 스킨십이잖아?^n그렇지, 그레텔?",
46:"시치미 떼지 마세요!^n그것뿐만이 아니에요. 지난번에 그 아이를 숲속으로^n억지로 끌고 가려던 사람도 당신이죠?",
49:"코미야는 조금도 나쁜 줄 모르는 얼굴로^n귀를 후비는 시늉을 하며 콧방귀를 뀌었다.",
53:"너무하네, 그레텔은.^n지난번에는 사이좋게 산책하자고 했을 뿐이잖아?^n그런 말을 듣다니 오빠는 섭섭하네에.",
54:"내 몸 옆으로 얼굴을 내밀 듯이^n코미야가 간드러진 목소리로 말을 걸자,^n그레텔의 몸이 흠칫 떨렸다.",
57:"나는 몸을 틀어 다시 한번 그녀를^n코미야의 시선에서 가리고 따져 물었다.",
61:"무슨 짓이긴…… 그야^n의사 놀이로 정해져 있잖아아?",
66:"의…… 의사 놀이라니!?^n당신 진짜 의사 선생님…… 맞죠?",
69:"의미심장하고 여유로운 미소를 지으며^n코미야가 콧방울을 벌름거렸다.",
71:"의사라는 건 환자를 치료하는 사람이잖아요?^n왜 그런 끔찍한 짓을 하는 겁니까!",
73:"하하하하.^n나 말이야, 사실 의사 따위가 아니거든. 이게 참.",
76:"무슨 뜻인지 알 수 없었다.^n흰 가운을 입고 당당하게 병원 안을 다니는데^n의사가 아니라고?",
77:"동시에 크게 납득했고 안심도 했다.^n이런 녀석이 의사라니,^n환자인 나로서도 그런 병원은 사양이다.",
81:"몰래 숨어들었다면 모를까,^n직원들도 이 사람을 아는 눈치였는데.",
83:"글쎄에. 그건 말할 수 없네에.^n하지만 그런 사람은 나뿐만이 아닌 모양이던데에.^n",
85:"말을 너무 많이 했다는 듯,^n코미야는 황급히 손으로 입을 가렸다.",
86:"의사가 아닌데 의사 행세를 한다고?^n그런 사람이 이 사람뿐만도 아니라고?",
88:"그게 무슨 뜻이에요!?^n이 병원은 대체 어떻게 된 겁니까?",
91:"추궁하려 했지만,^n코미야는 파리라도 쫓듯 두 손을 마구 휘저어^n나를 입 다물게 하려 했다.",
94:"코미야는 얼굴을 새빨갛게 붉히고^n거친 콧김을 내뿜으며 내게 조금씩 다가왔다.",
96:"그렇게 멋있는 척해 봐야,^n결국 너도 그레텔의 몸을^n노리는 것뿐이잖아, 응!?",
99:"(이 사람은 무슨 말을 하는 거지?^n 남매끼리 그럴 리 없잖아……)",
101:"너만 없으면 내가 그레텔의^n오빠가 될 수 있다고오오!!",
104:"격분한 코미야가 내게 달려들었다.^n견디지 못하고 떨쳐 내려 했지만,^n그는 보기보다 민첩하고 힘도 셌다.",
107:"몸싸움 끝에 나는 근처 계단에서 굴러떨어졌다.",
110:"그레텔의 외침이^n멀어져 가는 의식 너머에서 들렸다.",
113:"이름을 부르려 했는데 목소리가 나오지 않는다.",
114:"내가 부르려 한 이름은 그레텔?^n아니면──",
115:"아아, 그녀의 이름이 기억나지 않아──",
}
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 draft=json.loads(DRAFT.read_text(encoding="utf-8"));expected=set(range(1,116))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1307_slots_00001_00115_draft":raise SystemExit("unexpected draft")
 entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]};changes=[]
 if set(entries)!=expected:raise SystemExit("draft coverage mismatch")
 for i,t in CORRECTIONS.items():
  before=str(entries[i]["target_text"]);entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 catalog={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1307.gsc":continue
   i=int(x["slot"])
   if i in expected:catalog[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(catalog)!=expected or lookup!=set(range(116,174)):raise SystemExit("catalog/lookup mismatch")
 final=[]
 for i in sorted(expected):
  e=entries[i];s,t=str(e["source_text"]),str(e["target_text"])
  if s!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]:raise SystemExit(f"source drift {i}")
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"});final.append(e)
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1307_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,115],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[116,173],"release_ready":False,"entries":final};out=PROJECT/"packets"/"reviewed"/"1307_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,115],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_116_173_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};ap=PROJECT/"audit"/"translation_review_1307_complete.json";ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
