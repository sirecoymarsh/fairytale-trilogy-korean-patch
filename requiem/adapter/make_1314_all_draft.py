from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");CARET_RE=re.compile(r"\^(?:n|m|d\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
TARGETS=[None,"나","으앗!?",
"그레텔의 방으로 가려고 복도를 걷던 내 앞에^n모퉁이에서 유령 같은 사람의 모습이 흐느적 나타났다.",
"게르다","………….","게르다였다.",
"원래 비칠 듯 하얀 그녀의 피부는^n오늘은 핏기를 잃어 한층 더 창백해 보였다.",
"나","괘, 괜찮아?^n상태가 상당히 안 좋아 보이는데……?",
"게르다는 마치 몽유병자처럼 천천히 고개를 돌려^n어딘가 초점이 맞지 않는 눈길을 내게 향했다.",
"게르다","응……?^n","아…… 너였구나…….",
"마치 이제야 알아챈 듯 그녀는 그렇게 말했다.^n원래 조용한 그녀였지만 목소리에 있었을^n힘과 생기가 전혀 느껴지지 않았다.",
"나","괜찮아? 방까지 데려다줄까?",
"게르다","아무것도 아니야.^n아무것도 아니니까…… 혼자 있게 해 줘…….",
"중얼중얼 염불이라도 외는 듯한 목소리로 그렇게 대답하고,^n게르다는 등을 돌려 휘청휘청 걸어갔다."]
def main():
 expected=set(range(1,20))
 if len(TARGETS)!=20:raise SystemExit("target count mismatch")
 rows={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1314.gsc":continue
   i=int(x["slot"])
   if i in expected:rows[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(rows)!=expected or lookup!=set(range(20,78)):raise SystemExit("coverage mismatch")
 entries=[]
 for i in sorted(expected):
  row,t=rows[i],str(TARGETS[i]);s=str(row["source_text"])
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(t):raise SystemExit(f"Japanese residue {i}")
  t.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":s,"source_raw_sha256":row["source_raw_sha256"],"target_text":t,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 대기"})
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1314_slots_00001_00019_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};out=PROJECT/"packets"/"drafts"/"1314_slots_00001_00019_draft.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[20,77],"output":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
