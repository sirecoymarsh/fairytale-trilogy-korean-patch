from __future__ import annotations
import csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

PROJECT=Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
BUNDLE=PROJECT/"review_sensitive_content"
FILE="1603.gsc"
STATUS="KEPT_SENSITIVE_NARROW_THRESHOLD"
REASON="The scene directly recalls a predatory medical humiliation in which Gerda's skirt was lifted, her buttocks exposed, and medicine forced in while she was embarrassed. Under the narrowed threshold, only those explicit coercive exposure and forced-treatment lines remain sensitive; the examination and suspicious dialogue elsewhere are general story context. The complete file is kept for context."
AUDIT_REL="audit/excluded_sensitive_content_1603.json"

def sha256(p: Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest().upper()

def rewrite_tsv(path: Path, master: bool)->int:
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        rows=list(csv.reader(f,delimiter="\t"))
    header=rows[0]; count=0
    for row in rows[1:]:
        if row and row[0]==FILE:
            count+=1
            if master:
                row[5]=STATUS; row[6]=REASON; row[7]=AUDIT_REL
            else:
                row[2]=REASON
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        csv.writer(f,delimiter="\t",lineterminator="\n").writerows(rows)
    return count

def main()->int:
    audit_path=PROJECT/AUDIT_REL
    previous_audit = json.loads(audit_path.read_text(encoding="utf-8-sig")) if audit_path.exists() else None
    now=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    source_path=BUNDLE/"files"/"1603_source_review.txt"
    lines=source_path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0]!="FILE: 1603.gsc": raise SystemExit("unexpected source review")
    lines[1]=f"STATUS: {STATUS}"
    lines[2]=f"CLASSIFICATION_REASON: {REASON}"
    lines[3]=f"AUDIT_RECORD: {AUDIT_REL}"
    source_path.write_text("\n".join(lines)+"\n",encoding="utf-8")
    decision=BUNDLE/"file_decisions.tsv"; master=BUNDLE/"sensitive_scene_slots_for_review.tsv"
    if rewrite_tsv(decision,False)!=1: raise SystemExit("decision row mismatch")
    if rewrite_tsv(master,True)!=74: raise SystemExit("master row mismatch")
    manifest_path=BUNDLE/"manifest.json"; manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    row=next((x for x in manifest["files"] if x.get("file")==FILE),None)
    if row is None: raise SystemExit("manifest row missing")
    row.update({"classification_status":STATUS,"classification_reason":REASON,"audit_record":AUDIT_REL,"source_review_sha256":sha256(source_path),"translation_map_created":True,"trial_modified":True})
    manifest["updated_utc"]=now; manifest["master_tsv_sha256"]=sha256(master); manifest["decision_template_sha256"]=sha256(decision)
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    audit={"schema":"fairytale-requiem-sensitive-content-exclusion-v1","status":STATUS,"file":FILE,"visible_slots":[1,74],"lookup_slots_preserved":[75,132],"focused_sensitive_slot_ranges":[[60,60],[65,65]],"reason":REASON,"translation_map_created":True,"review_pass_executed":True,"build_created":True,"trial_modified":True,"review_map":"packets/reviewed/1603_all_translatable_slots_reviewed_once.json","review_map_sha256":sha256(PROJECT/"packets"/"reviewed"/"1603_all_translatable_slots_reviewed_once.json"),"classified_utc":now}
    audit_path.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","file":FILE,"focused_sensitive_slot_ranges":[[60,60],[65,65]],"source_review_sha256":sha256(source_path),"manifest_sha256":sha256(manifest_path),"audit_sha256":sha256(audit_path)},ensure_ascii=True,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())