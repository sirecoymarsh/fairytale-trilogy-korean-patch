from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
TARGETS=[None,
"그레텔의 방에서 돌아온 나는^n그 아이가 주운 카드 키 같은 물건을^n어둠 속에서 유심히 바라보고 있었다.",
"창문으로 희미하게 들어오는 달빛이^n금속 표면에 반사되어 아름다웠다.",
"나","(역시……^n 원래라면 직원에게 돌려줘야겠지)",
"기억을 잃고도 내 안에 남아 있던 이성과 상식은^n적어도 그렇게 주장하고 있었다.",
"하지만 동시에 다른 생각이^n내 마음속에서 고개를 들고 있었다.",
"나","(하지만 그러면 왠지 재미없는데……)",
"그것은 단순한 장난기라고 해야 할지도 모른다.",
"무엇을 할 자유도 없이 이 『낙원』에 갇힌^n울분의 반동이라고 한다면 부정할 수 없었다.",
"하지만 그 감정을^n또 한 명의 『나』가 정당화하려 한다.",
"나","(이 시설은 우리에게 뭔가를 숨기고 있어.^n 이 열쇠가 있으면 그게 뭔지 알아낼 수 있을지도 몰라)",
"무언가 수상한 목적으로 운영되는 시설의 비밀을 캐는 일은^n수용된 환자의 당연한 권리라는 나 나름의 논리.",
"허점투성이라 해도 결국 내가 납득하면 그만이다.",
"나","(애초에 머리가 이상하다는 이유로 여기 있는 거야.^n 이왕이면 정신 나간 환자다운 짓을 해 보자)",
"그런 자학에 가까운 감상마저 내 등을 떠밀었다.",
"나","(자, 어디부터 조사해 볼까……)",
"지금까지 시설을 돌아다니며^n수상해 보인다고 생각한 곳들을 떠올렸다.",
"탐색해야 할 『정당한 이유』는 제쳐 두고,^n내 마음은 장난기로 잔뜩 부풀어^n들뜨지 않을 수 없었다."]
def main():
 expected=set(range(1,23))
 if len(TARGETS)!=23:raise SystemExit("target count mismatch")
 rows={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1311.gsc":continue
   i=int(x["slot"])
   if i in expected:rows[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(rows)!=expected or lookup!=set(range(23,81)):raise SystemExit("coverage mismatch")
 entries=[]
 for i in sorted(expected):
  row,t=rows[i],str(TARGETS[i]);s=str(row["source_text"])
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":s,"source_raw_sha256":row["source_raw_sha256"],"target_text":t,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 대기"})
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1311_slots_00001_00022_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};out=PROJECT/"packets"/"drafts"/"1311_slots_00001_00022_draft.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[23,80],"output":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
