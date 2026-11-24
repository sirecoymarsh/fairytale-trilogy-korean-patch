from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");WORK=Path(__file__).resolve().parent;CARET_RE=re.compile(r"\^(?:n|m|d\d+)")
def main():
 expected=set(range(1,152));targets={}
 for p in sorted(WORK.glob("1221_draft_targets_part_*.json")):
  d=json.loads(p.read_text(encoding="utf-8"))
  if d.get("file")!="1221.gsc" or d.get("review_passes_completed")!=0:raise SystemExit("bad part")
  for k,v in d["targets"].items():
   i=int(k)
   if i in targets:raise SystemExit(f"duplicate {i}")
   targets[i]=str(v)
 rows={};lookup=set()
 with (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8") as h:
  for line in h:
   x=json.loads(line)
   if x.get("file")!="1221.gsc":continue
   i=int(x["slot"])
   if i in expected:rows[i]=x
   elif "lookup_keys" in x.get("lanes",[]):lookup.add(i)
 if set(targets)!=expected or set(rows)!=expected or lookup!=set(range(152,210)):raise SystemExit("coverage mismatch")
 entries=[]
 for i in sorted(expected):
  row,t=rows[i],targets[i];s=str(row["source_text"])
  if CARET_RE.findall(s)!=CARET_RE.findall(t):raise SystemExit(f"caret mismatch {i}")
  t.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":s,"source_raw_sha256":row["source_raw_sha256"],"target_text":t,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"초벌 번역; 1차 검수 대기"})
 output={"schema":"fairytale-requiem-translation-map-v1","scope":"1221_slots_00001_00151_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};out=PROJECT/"packets"/"drafts"/"1221_slots_00001_00151_draft.json";out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[152,209],"output":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest().upper()},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
