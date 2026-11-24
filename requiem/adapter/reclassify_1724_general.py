from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
BUNDLE = PROJECT / "review_sensitive_content"
FILE = "1724.gsc"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def remove_tsv_rows(path: Path) -> int:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    header, rows = lines[0], lines[1:]
    kept = [row for row in rows if not row.startswith(FILE + "\t")]
    removed = len(rows) - len(kept)
    path.write_text("\n".join([header, *kept]) + "\n", encoding="utf-8-sig")
    return removed


def main() -> int:
    source_review = BUNDLE / "files" / "1724_source_review.txt"
    if not source_review.exists():
        raise SystemExit("1724 source review already absent; refusing duplicate reclassification")
    decision_path = BUNDLE / "file_decisions.tsv"
    master_path = BUNDLE / "sensitive_scene_slots_for_review.tsv"
    removed_decisions = remove_tsv_rows(decision_path)
    removed_slots = remove_tsv_rows(master_path)
    if removed_decisions != 1 or removed_slots != 59:
        raise SystemExit(f"unexpected bundle rows removed: decisions={removed_decisions}, slots={removed_slots}")
    source_review.unlink()

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    manifest_path = BUNDLE / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    old_rows = manifest["files"]
    removed_manifest = [row for row in old_rows if row.get("file") == FILE]
    if len(removed_manifest) != 1:
        raise SystemExit("1524 manifest membership mismatch")
    manifest["files"] = [row for row in old_rows if row.get("file") != FILE]
    manifest["updated_utc"] = now
    manifest["classified_file_count"] = len(manifest["files"])
    manifest["classified_visible_nonempty_slot_count"] = sum(int(row["visible_nonempty_slots"]) for row in manifest["files"])
    manifest["master_tsv_sha256"] = sha256(master_path)
    manifest["decision_template_sha256"] = sha256(decision_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    exclusion_path = PROJECT / "audit" / "excluded_sensitive_content_1724.json"
    exclusion = json.loads(exclusion_path.read_text(encoding="utf-8"))
    original_reason = exclusion.get("original_classification_reason", exclusion.get("reason"))
    exclusion.update({
        "status": "RECLASSIFIED_GENERAL_FALSE_POSITIVE",
        "reason": "Reclassified as general content after the user requested a narrower sensitivity threshold. Non-graphic emotional manipulation, abandonment themes, and bullying without explicit sexual content, direct self-harm, or graphic bodily injury are general content.",
        "original_classification_reason": original_reason,
        "reclassified_utc": now,
        "translation_eligibility": "GENERAL_TRANSLATION_QUEUE",
        "translation_map_created": True,
        "review_pass_executed": True,
        "build_created": False,
        "trial_modified": False,
    })
    exclusion_path.write_text(json.dumps(exclusion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    policy_path = PROJECT / "audit" / "sensitive_reclassification_narrow_threshold_20260813.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if FILE not in policy["reclassified_general_files"]:
        policy["reclassified_general_files"].append(FILE)
    policy["reclassified_general_files"] = sorted(policy["reclassified_general_files"])
    policy["updated_utc"] = now
    policy_path.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    readme_path = BUNDLE / "README.md"
    lines = readme_path.read_text(encoding="utf-8").splitlines()
    lines[2] = f"- \ubd84\ub958 \ud30c\uc77c: **{manifest['classified_file_count']}\uac1c**"
    lines[3] = f"- \uc6d0\ubb38 \uc2ac\ub86f: **{manifest['classified_visible_nonempty_slot_count']}\uac1c**"
    lines[4] = "- \ud604\uc7ac \uc0c1\ud0dc: \ubbfc\uac10 \uac80\ud1a0 \ubaa9\ub85d\uc740 \uc720\uc9c0\ud558\uba70, \ubc88\uc5ed \uc644\ub8cc \ub9f5\uc740 `translated_maps`\uc5d0 \ubcc4\ub3c4 \uc218\uc9d1 \uc911"
    readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = {
        "status": "PASS",
        "file": FILE,
        "classification": "GENERAL_FALSE_POSITIVE",
        "removed_decision_rows": removed_decisions,
        "removed_slot_rows": removed_slots,
        "remaining_sensitive_files": manifest["classified_file_count"],
        "remaining_sensitive_slots": manifest["classified_visible_nonempty_slot_count"],
        "manifest_sha256": sha256(manifest_path),
    }
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())