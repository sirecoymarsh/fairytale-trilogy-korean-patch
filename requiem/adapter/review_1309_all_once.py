from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");DRAFT=PROJECT/"packets"/"drafts"/"1309_slots_00001_00136_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={
3:"혈관이 맥동할 때마다 욱신거리는 격통이 머릿속을 내달린다.",
5:"(윽…… 아파파파……)",
6:"통증을 견디지 못해 머리에 손을 대면서 나는 눈을 깜빡였다.",
9:"자는 동안 호흡이 상당히 얕아졌는지,^n신선한 공기를 원한 폐가 저절로 숨을 깊이 들이마셨다.",
12:"내가 눈을 뜬 곳은^n온통 새하얀 평소의 내 방이 아니었다.^n그렇다고 진찰실인 것 같지도 않다.",
13:"엉성한 목재를 짜 맞춘 천장이 바로 눈앞까지 다가와 있다.^n불은 켜져 있지만 앞의 판자가 가로막는지 어두컴컴하다.",
16:"상체를 일으키는 것까지는 괜찮지만 일어서려 하면^n나조차 머리를 부딪칠 것 같은 높이였다.",
17:"좌우 중 한쪽은 틈투성이 나무판자로 막혀 있고,^n반대쪽에는 기대면 부서질 듯한 난간이 달려 있다.^n그쪽에는 나무 사다리 같은 것이 위로 뻗어 있었다.",
21:"고개를 조금 기울이자 드러난 목재 사이에 걸친 밧줄에^n만국기처럼 형형색색인 천──누더기투성이 빨래가^n잔뜩 나부끼고 있었다.",
24:"고개를 더 기울이자 베갯머리에 붙어 있던 그레텔이^n나를 바라보며 어깨를 부들부들 떨고 있었다.",
29:"에흑, 에, 흐에우…….^n다, 다행이야…….",
30:"그녀는 구슬 같은 눈물을 뚝뚝 흘리며 울기 시작했다.",
32:"으으으…….^n다, 다시는 못 일어나는 줄 알았어…….",
34:"(아, 맞아.^n 나는 그때 코미야라는 사람에게 떠밀려서……)",
37:"혹시…… 네가 옮겨 준 거야?",
40:"흑…… 이, 이케노 씨가, 흑,^n옮겨 줬어…… 흑!",
43:"도움을 받아 고맙기도 했지만,^n의문스러운 점도 있었다.",
45:"(이케노 씨는 왜 진찰실이 아니라^n 그레텔의 방으로 옮긴 걸까?)",
49:"항상 뭔가 의미심장한 말을 해서^n내 머리를 복잡하게 하는 종잡을 수 없는 신비한 사람이다.^n이번에도 무슨 의도가 있는 것만 같았다.",
51:"이, 이케노 씨가 그냥 기절한 거라고, 흑!^n",
52:"고, 곧 눈을, 흑, 뜰 거라고^n",
53:"말했지만…… 흑…… 이, 일어나지 않았는걸…….",
56:"이케노 씨의 속셈은 둘째 치고,^n그녀를 울려 버린 것이 후회스러워 견딜 수 없었다.",
57:"그녀를 지켜 주겠다고 마음속으로 맹세했는데.^n게르다에게 『지켜 줘』라는 말을 들은 지 얼마 되지도 않았는데.^n오히려 나 때문에 그녀를 슬프게 만들고 말았다.",
59:"아, 아니…….^n오, 오빠가 무사해서 다행이야…….",
60:"하지만 눈물이 섞인 그녀의 말에^n한없이 그리운 감각이 치밀어 올랐다.",
62:"(아, 맞아…….^n 그 아이는 늘 나를 걱정해 줬지……)",
64:"아니면 헨젤이 되려는 내게^n그녀의 『이야기』가 새겨지고 있을 뿐일까?",
65:"──모르겠다.^n하지만 이렇게 나를 걱정하며 흐느끼는 여동생을^n무엇보다 안심시켜 주고 싶었다.",
68:"그렇게 말하며 손을 뻗어 그녀의 머리를 쓰다듬었다.^n그녀의 몸은 아직 흐느낌으로 심하게 떨리고 있었다.",
70:"뭘 그렇게 떨고 있어?^n나는 이제 괜찮으니까.",
72:"나…… 무, 무서웠어.^n저, 전에도 이런 일이 있었는데……^n그때는…… 피가 훨씬 많이 흘렀어…….",
75:"욱신, 욱신, 소리를 내며 머릿속 혈관이 뛰기 시작했다.^n피가 흐르는 소리가 휘잉 하는 이명처럼 머릿속 가득 울려 퍼진다.",
78:"그녀의 말이 방아쇠라도 된 듯^n내 머릿속에 되살아난 광경이 있었다.",
79:"동공이 오므라들어 새까매진 시야에^n끈적하고 선명하도록 붉은 액체가 퍼져 간다.",
80:"──피, 피, 피, 피. 새빨간 핏물이 흘러나온다.^n",
81:"──끝없이 번져 가는 온통 피 웅덩이.^n",
85:"머릿속이 새빨간 핏빛 하나로 뒤덮여,^n정작 『그 사람』의 모습도 얼굴도 전혀 보이지 않는다.",
86:"이윽고 사아…… 하고 바닷물이 빠지듯,^n내 시야에 펼쳐진 피의 바다가 물러갔다.",
87:"정신을 차리자 두 눈은 다시^n그레텔의 방을 비추고 있었다.",
90:"그레텔이 다시 걱정스러운 표정으로^n내 얼굴을 들여다보고 있었다.",
92:"아, 으, 응, 괜찮아.^n조금 어지러웠을 뿐이야.",
93:"걱정시키고 싶지 않은 마음에^n나도 모르게 그렇게 둘러대고 있었다.",
98:"(그 아이가 진정하면 나중에 물어볼까……)",
101:"상당히 늦어진 것 같으니,^n슬슬 내 방으로 돌아가야겠어.",
102:"그 아이의 방에는 시계가 없지만,^n기절하기 전 시간을 생각하면 벌써 한밤중일 것이다.",
103:"아무리 그 아이의 『오빠』를 연기하고 있다 해도,^n밤늦게까지 계속 그 아이의 방에 있기는 거리낌이 든다.",
105:"침대에서 일어나 출구로 향하려는 나를^n그레텔이 무언가 생각난 듯한 얼굴로 붙잡았다.",
107:"아, 마, 맞다!^n자, 잠깐만 기다려, 오빠.",
112:"그레텔이 내민 것은^n반짝반짝 빛나는 금색 카드였다.",
114:"뭘까. 무언가의 열쇠……인가?^n이건 어디서 났어?",
115:"묻자 그레텔은 멋쩍은 듯^n고개를 살짝 숙이고 대답했다.",
117:"저, 저기.^n그 사람이 떨어뜨리고 갔어…….",
124:"그 마음을 모르는 것은 아니다.^n아니, 잘 안다.",
125:"금색 카드라니 어른의 비밀 같은 냄새가 나고,^n틀림없이 『아무것도 아닌 물건』일 리는 없을 것이다.^n그대로 돌려주기는 아깝다.",
127:"알았어. 그럼 우선 내가 맡아 둘게.^n어떻게 할지는 내가 생각해 둘 테니까.",
128:"그렇게 말하자 그레텔은 연신 고개를 끄덕였다.",
133:"그레텔의 배웅을 받으며 나는 그녀의 방을 나섰다.",
136:"나는 복도 조명을 반사해 움직이는 네모난 금빛을 눈으로 좇으며^n저절로 입가가 풀리는 것을 느꼈다.",
}
def slot(u):
 m=re.search(r"slot/(\d+)$",u)
 if not m:raise ValueError(u)
 return int(m.group(1))
def main():
 draft=json.loads(DRAFT.read_text(encoding="utf-8"));expected=set(range(1,137))
 if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1309_slots_00001_00136_draft":raise SystemExit("unexpected draft")
 entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]};changes=[]
 if set(entries)!=expected:raise SystemExit("draft coverage mismatch")
 for i,t in CORRECTIONS.items():
  before=str(entries[i]["target_text"]);entries[i]["target_text"]=t
  if before!=t:changes.append({"slot":i,"before":before,"after":t})
 catalog={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1309.gsc":continue
   i=int(x["slot"])
   if i in expected:catalog[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(catalog)!=expected or lookup!=set(range(137,195)):raise SystemExit("catalog/lookup mismatch")
 final=[]
 for i in sorted(expected):
  e=entries[i];s,t=str(e["source_text"]),str(e["target_text"])
  if s!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]:raise SystemExit(f"source drift {i}")
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"});final.append(e)
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1309_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,136],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[137,194],"release_ready":False,"entries":final};out=PROJECT/"packets"/"reviewed"/"1309_all_translatable_slots_reviewed_once.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":output["scope"],"draft_inputs":[str(DRAFT)],"output":str(out),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,136],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_137_194_preserved":True},"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()};ap=PROJECT/"audit"/"translation_review_1309_complete.json";ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({**audit,"audit_path":str(ap)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
