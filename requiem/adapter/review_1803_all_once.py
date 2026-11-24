from __future__ import annotations
import hashlib, json, re
from pathlib import Path
PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT=PROJECT/"packets"/"drafts"/"1803_slots_00001_00055_draft.json"
CORRECTIONS_PATH=Path(r"C:\Users\CadriacLord\Documents\Codex\2026-08-12\search-ms-displayname-20pc-20-20\work\1803_review_corrections.json")
OUTPUT_PATH=PROJECT/"packets"/"reviewed"/"1803_all_translatable_slots_reviewed_once.json"
AUDIT_PATH=PROJECT/"audit"/"translation_review_1803_complete.json"
CARET_RE=re.compile(r"\^(?:n|m|d\d+|s\d+)"); JAPANESE_RE=re.compile(r"[\u3040-\u30ff]")
CORRECTIONS={int(k):str(v) for k,v in json.loads(CORRECTIONS_PATH.read_text(encoding="utf-8")).items()}
def slot(uid):
    m=re.search(r"slot/(\d+)$",uid)
    if not m: raise ValueError(uid)
    return int(m.group(1))
def main():
    if OUTPUT_PATH.exists() or AUDIT_PATH.exists(): raise SystemExit("1803 review output already exists; refusing second pass")
    draft=json.loads(DRAFT.read_text(encoding="utf-8")); expected=set(range(1,56))
    if draft.get("review_passes_completed")!=0 or draft.get("scope")!="1803_slots_00001_00055_draft": raise SystemExit("unexpected draft")
    entries={slot(str(e["uid"])):dict(e) for e in draft["entries"]}
    if set(entries)!=expected or not set(CORRECTIONS).issubset(expected): raise SystemExit("coverage mismatch")
    changes=[]
    for i,target in CORRECTIONS.items():
        before=str(entries[i]["target_text"]); entries[i]["target_text"]=target
        if before!=target: changes.append({"slot":i,"before":before,"after":target})
    catalog={}; lookup=set()
    for line in (PROJECT/"catalog"/"scenario_catalog.jsonl").open(encoding="utf-8"):
        item=json.loads(line)
        if item.get("file")!="1803.gsc": continue
        i=int(item["slot"])
        if i in expected: catalog[i]=item
        elif "lookup_keys" in item.get("lanes",[]): lookup.add(i)
    if set(catalog)!=expected or lookup!=set(range(56,114)): raise SystemExit("catalog/lookup mismatch")
    final=[]
    for i in sorted(expected):
        e=entries[i]; source=str(e["source_text"]); target=str(e["target_text"])
        if source!=catalog[i]["source_text"] or e["source_raw_sha256"]!=catalog[i]["source_raw_sha256"]: raise SystemExit(f"source drift {i}")
        if CARET_RE.findall(source)!=CARET_RE.findall(target): raise SystemExit(f"caret mismatch {i}")
        if JAPANESE_RE.search(target): raise SystemExit(f"Japanese residue {i}")
        target.encode("cp949",errors="strict"); e.update({"translator":"Codex internal model","review_status":"reviewed_once","reviewer":"Codex internal model single review pass","notes":"Initial translation plus exactly one review; syntax, style, terminology, and control-code checks complete"}); final.append(e)
    out={"schema":"fairytale-requiem-translation-map-v1","scope":"1803_all_translatable_slots_reviewed_once","semantic_source":"ja-JP","target_language":"ko-KR","target_encoding":"cp949","translation_method":"Codex internal model only; no external MT/API","review_passes_completed":1,"review_policy":"every translatable slot received exactly one Codex review pass","newly_reviewed_range":[1,55],"new_review_change_count":len(changes),"new_review_changes":changes,"file_translation_complete":True,"lookup_slots_preserved":[56,113],"release_ready":False,"entries":final}
    OUTPUT_PATH.parent.mkdir(parents=True,exist_ok=True); OUTPUT_PATH.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    audit={"schema":"fairytale-requiem-translation-review-audit-v1","status":"PASS","scope":out["scope"],"draft_inputs":[str(DRAFT)],"output":str(OUTPUT_PATH),"entry_count":len(final),"review_passes_per_slot":1,"newly_reviewed_slots":[1,55],"new_review_change_count":len(changes),"checks":{"source_text_and_hash_match_catalog":True,"caret_token_order_preserved":True,"all_targets_strict_cp949":True,"no_kana_residue":True,"exactly_one_review_per_slot":True,"all_translatable_slots_covered":True,"lookup_slots_excluded":True,"lookup_range_56_113_preserved":True},"output_sha256":hashlib.sha256(OUTPUT_PATH.read_bytes()).hexdigest().upper()}
    AUDIT_PATH.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({**audit,"audit_path":str(AUDIT_PATH)},ensure_ascii=True,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())