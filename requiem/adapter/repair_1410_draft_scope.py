from __future__ import annotations
import hashlib
import json
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1410_slots_00001_00056_draft.json"
TARGETS = Path(r"C:\Users\CadriacLord\Documents\Codex\2026-08-12\search-ms-displayname-20pc-20-20\work\1410_targets_001_056.json")
AUDIT = PROJECT / "audit" / "draft_metadata_repair_1410.json"
EXPECTED_BEFORE = "7BC2E50DADF8A5649E787413FC8D874B4A1571D41FA29C1EE8E041DD175EA181"
OLD_SCOPE = "1410_slots_00001_00049_draft"
NEW_SCOPE = "1410_slots_00001_00056_draft"

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def main() -> int:
    if AUDIT.exists():
        raise SystemExit("1410 draft metadata repair already recorded")
    before = digest(DRAFT)
    if before != EXPECTED_BEFORE:
        raise SystemExit(f"unexpected draft hash before repair: {before}")
    data = json.loads(DRAFT.read_text(encoding="utf-8"))
    targets = {int(k): str(v) for k, v in json.loads(TARGETS.read_text(encoding="utf-8")).items()}
    if data.get("scope") != OLD_SCOPE or data.get("review_passes_completed") != 0 or len(data.get("entries", [])) != 56:
        raise SystemExit("unexpected draft metadata")
    slots = {int(e["uid"].rsplit("/", 1)[1]): str(e["target_text"]) for e in data["entries"]}
    if slots != targets:
        raise SystemExit("draft translations do not match frozen first-pass targets")
    data["scope"] = NEW_SCOPE
    DRAFT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    after = digest(DRAFT)
    result = {
        "schema": "fairytale-requiem-draft-metadata-repair-v1",
        "status": "PASS",
        "file": "1410.gsc",
        "field_changed": "scope",
        "before": OLD_SCOPE,
        "after": NEW_SCOPE,
        "translation_entries_unchanged": True,
        "review_passes_completed": 0,
        "before_sha256": before,
        "after_sha256": after,
    }
    AUDIT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())