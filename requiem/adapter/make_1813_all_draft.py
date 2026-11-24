from __future__ import annotations
import hashlib,json,re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko");LOCAL=Path(r"C:\Users\CadriacLord\Documents\Codex\2026-08-12\search-ms-displayname-20pc-20-20\work");TARGET_PATH=LOCAL/"1813_targets_001_076.json";OUTPUT_PATH=PROJECT/"packets"/"drafts"/"1813_slots_00001_00076_draft.json";CARET_RE=re.compile(r"\^(?:n|m|d\d+|s\d+)");JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
def sha256(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def main():
 if OUTPUT_PATH.exists():raise SystemExit("1813 draft already exists; refusing overwrite")
 targets={int(k):str(v) for k,v in json.loads(TARGET_PATH.read_text(encoding="utf-8")).items()};expected=set(range(1,77))
 if set(targets)!=expected:raise SystemExit("target coverage mismatch")
 rows={};lookup=set()
 for line in (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8"):
  row=json.loads(line)
  if row.get("file")!="1813.gsc":continue
  i=int(row["slot"])
  if i in expected:rows[i]=row
  elif "lookup_keys" in row.get("lanes",[]):lookup.add(i)
 if set(rows)!=expected or lookup!=set(range(77,135)):raise SystemExit("catalog/lookup mismatch")
 entries=[]
 for i in sorted(expected):
  row=rows[i];source=str(row["source_text"]);target=targets[i]
  if CARET_RE.findall(source)!=CARET_RE.findall(target):raise SystemExit(f"caret mismatch {i}")
  if JAPANESE_RE.search(target):raise SystemExit(f"Japanese residue {i}")
  target.encode("cp949",errors="strict");entries.append({"uid":row["uid"],"source_text":source,"source_raw_sha256":row["source_raw_sha256"],"target_text":target,"translator":"Codex internal model draft","review_status":"draft_pending_single_review","notes":"Initial translation; exactly one review pass pending"})
 out={"schema":"fairytale-requiem-translation-map-v1","scope":"1813_slots_00001_00076_draft","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":0,"release_ready":False,"entries":entries};OUTPUT_PATH.parent.mkdir(parents=True,exist_ok=True);OUTPUT_PATH.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps({"status":"PASS","entries":len(entries),"lookup_slots_preserved":[77,134],"output":str(OUTPUT_PATH),"sha256":sha256(OUTPUT_PATH)},ensure_ascii=True,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
