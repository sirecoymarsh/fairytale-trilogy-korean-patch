from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
TARGETS=[None,
"내 방으로 돌아온 나는^n침대에 벌렁 드러누워 잠들려 했다.",
"『지켜 줘』",
"──하지만 조금 전 게르다가 한 말이^n마음속에 메아리쳐 도무지 잠들 수 없었다.",
"무언가를 조용히, 하지만 강하게 호소하는 그 한마디에,^n나는 가슴이 꽉 조이는 듯한^n애달픈 기분을 느끼지 않을 수 없었다.",
"나","(게르다는 그레텔에게 자신을 겹쳐 보고 있는 걸까?)",
"미소 속에 비친 쓸쓸한 모습이 마음에 걸렸다.^n왠지 자기 자신은 포기해 버린 듯한──^n그런 느낌마저 든다.",
"그래, 얼마 전까지 무슨 수를 써서라도 이 『낙원』에서 빠져나가려던^n강한 의지나 패기 같은 것이 부족한 듯한──^n달리 말하면 『그림자』가 옅어진 듯한──",
"나","(이상한 생각은 그만하자, 나)",
"나는 검은 안개 같은 불길한 예감을 떨쳐 내고,^n이불을 머리끝까지 뒤집어쓴 채 억지로 잠들었다.",
"나","(으…… 으으……)",
"떨쳐 냈다고 생각한 불길한 기척은^n아무래도 잠 속까지 나를 따라온 모양이다.",
"나","(그만둬, 그 아이에게만은 손대지 마!)",
"나는 외쳤다. 발버둥 쳤다.",
"그런데도 목소리가 나오지 않는다. 손발도 움직이지 않는다.",
"지켜 주고 싶었다.",
"그 아이만은 더러운 일과 괴로운 일에서 멀리하고 싶었다.",
"그런데도…….",
"나는 아무것도 할 수 없었다──^n아무런 힘도 없었다.",
"무력감에 짓눌려,^n내 마음은 깊고 깊은 어둠 밑바닥으로 떨어져 간다──"]
def main():
 expected=set(range(1,24))
 if len(TARGETS)!=24:raise SystemExit("target count mismatch")
 rows={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1305.gsc":continue
   i=int(x["slot"])
   if i in expected:rows[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(rows)!=expected or lookup!=set(range(24,82)):raise SystemExit("coverage mismatch")
 entries=[]
 for i in sorted(expected):
  row,t=rows[i],str(TARGETS[i]);s=str(row["source_text"])
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":s,"source_raw_sha256":row["source_raw_sha256"],"target_text":t,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 대기"})
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1305_slots_00001_00023_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};out=PROJECT/"packets"/"drafts"/"1305_slots_00001_00023_draft.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[24,81],"output":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
