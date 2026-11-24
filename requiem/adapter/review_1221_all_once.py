from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");DRAFT=PROJECT/"packets"/"drafts"/"1221_slots_00001_00151_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
6:"이야, 완전히 밤이구나.^n종이 몸이 눅눅해지겠어!",
9:" 아니, 직원들──이 아니라,^n『트럼프 병사들』이다.^n 그들의 마음속에서는.",
19:"험상궂은 얼굴, 지친 얼굴, 주름져 메마른 얼굴,^n저마다 어른 그 자체인 얼굴에^n반짝이는 천진난만함이 배어 있다.",
24:"그 장소에 도착한 내가 처음 내지른 것은^n비명이 섞인 큰 목소리였다.",
25:"그럴 만도 했다. 앨리스의 휘청거리고 불안한 발걸음이^n이 나뭇가지에서 저 나뭇가지로 옮겨 가는 것이 보였으니까.",
34:"영, 차…… 괜찮아요.^n지난번처럼 받아 주실 거라면…….^n──영, 차……!",
37:"앨리스가 말 몇 마디로 멈출 여자아이가 아니라는 사실을^n나는 지겹도록 깨달았어야 했다.",
65:"천과 가랜드로 예쁘게 꾸민 나무도 있는데,^n이건 오딜에게서 무언가 천을 받았던^n그레텔과 라푼젤의 작품일까.",
73:"(대단해, 앨리스.^n 대체 무슨 일을 벌이고 만 거야, 너는……)",
75:"(바보 같아. 엄청나게 바보 같아.^n 사람에게 좋아한다고 말하려고 어떻게 여기까지 할 수 있어?)",
77:"가슴만이 아니다.^n목구멍까지 치밀어 오른 말로 할 수 없는 감정도,^n눈가에 서서히 번지는 무언가도, ──견딜 수 없을 만큼 뜨겁다.",
83:"……봤어요? 제대로 봐 주셨어요?^n제 마음이 제대로 글자로 나타났나요?",
87:"나뭇가지를 휘감듯 매달려 끝으로 나아가는 앨리스의 모습이^n시야에 뛰어들었기 때문이다.",
99:"지난번에 뼈저리게 겪은 그 충격이^n다시 두 팔에서 어깨로 내달렸다.",
108:"이게 제가 『연정에 빠진』 무게예요!",
110:"이것이…… 이렇게 어깨가 빠질 듯하고,^n손끝까지 저릴 만큼 무거운 것이^n앨리스의 마음이 지닌 강함이라면.",
114:"나는 『받아 버린 것』에^n영혼 밑바닥부터 압도당하는 기분이었다.",
117:"앨리스는 분명 『앨리스가 나를 좋아한다』는 사실을^n말을 늘어놓는 대신 있는 그대로의 감촉과 무게와 온도로^n내게 알려 주고 싶었던 것이다.",
120:"아아, 다행이에요.^n드디어 당신에게 건넬 수 있네요.",
122:"나무를 타느라 더러워지고 자잘한 상처가 난 손바닥을 보여 주려고──^n한 것은 아니고, 보이지 않는 가면을 내게 씌우는 듯한 몸짓이다.",
136:"네, 맞아요!^n당신이라면 체셔 고양이보다 훨씬 매력적으로 웃을 수 있어요.",
142:"뱃속부터 목구멍 깊은 곳까지 떨며,^n들이쉬고 내쉬는 숨이 폐의 경련으로 갈기갈기 흐트러지는 듯한,^n엉망진창인 웃음소리.",
144:"지금까지 무언가를 의식해 쓸데없이 쌓아 둔 웃음을^n한꺼번에 소화해 장부를 맞추고 있을 뿐이다.^n눈물이나 고함도 흔히 그러니까.",
150:"──앨리스가 멀게 느껴져 쓸쓸하다.^n──저 별이 빛나는 밤하늘 같은 눈을 들여다보고 싶다.",
}
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 draft=json.loads(DRAFT.read_text(encoding="utf-8"));expected=set(range(1,152))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1221_slots_00001_00151_draft":raise SystemExit("unexpected draft")
 entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]};changes=[]
 if set(entries)!=expected:raise SystemExit("draft coverage mismatch")
 for i,t in CORRECTIONS.items():
  before=str(entries[i]["target_text"]);entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 catalog={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1221.gsc":continue
   i=int(x["slot"])
   if i in expected:catalog[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(catalog)!=expected or lookup!=set(range(152,210)):raise SystemExit("catalog/lookup mismatch")
 final=[]
 for i in sorted(expected):
  e=entries[i];s,t=str(e["source_text"]),str(e["target_text"])
  if s!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]:raise SystemExit(f"source drift {i}")
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"});final.append(e)
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1221_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,151],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[152,209],"release_ready":False,"entries":final};out=PROJECT/"packets"/"reviewed"/"1221_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,151],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_152_209_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};ap=PROJECT/"audit"/"translation_review_1221_complete.json";ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
