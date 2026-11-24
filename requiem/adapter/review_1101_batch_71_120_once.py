from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    72: "어머! 어머나, 참 정중하시기도 하네요.^n",
    117: "모른다…… 자신이 누군지 모른다…….^n그런 일이 있을 수 있을까요.^n요즘은 장미도 고양이도 자기가 장미라고, 고양이라고 떠들썩할 정도인데.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    previous_path = PROJECT / "packets" / "reviewed" / "1101_slots_00001_00070_reviewed_once.json"
    draft_path = PROJECT / "packets" / "drafts" / "1101_slots_00071_00120_draft.json"
    previous = json.loads(previous_path.read_text(encoding="utf-8"))
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    if previous.get("review_passes_completed") != 1:
        raise SystemExit("previous range is not review-locked at one pass")
    entries: dict[int, dict[str, object]] = {slot(str(e["uid"])): dict(e) for e in previous["entries"]}
    new_entries = {slot(str(e["uid"])): dict(e) for e in draft["entries"]}
    if set(entries) != set(range(1, 71)) or set(new_entries) != set(range(71, 121)):
        raise SystemExit("range mismatch")

    change_log = []
    for index, replacement in CORRECTIONS.items():
        before = str(new_entries[index]["target_text"])
        if before != replacement:
            new_entries[index]["target_text"] = replacement
            change_log.append({"slot": index, "before": before, "after": replacement})

    for index, entry in new_entries.items():
        entry["translator"] = "Codex internal model"
        entry["review_status"] = "reviewed_once"
        entry["reviewer"] = "Codex internal model single review pass"
        entry["notes"] = "초벌 번역 후 한 차례 문맥·문체·제어 코드 검수 완료"
        entries[index] = entry

    catalog: dict[int, dict[str, object]] = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("file") == "1101.gsc" and 1 <= int(row.get("slot", -1)) <= 120:
                catalog[int(row["slot"])] = row
    if set(catalog) != set(range(1, 121)):
        raise SystemExit("catalog coverage mismatch")
    final = []
    for index in range(1, 121):
        entry = entries[index]
        if entry["source_text"] != catalog[index]["source_text"]:
            raise SystemExit(f"source drift {index}")
        if entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source hash drift {index}")
        target = str(entry["target_text"])
        if str(entry["source_text"]).count("^n") != target.count("^n"):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        if entry.get("review_status") != "reviewed_once":
            raise SystemExit(f"unreviewed entry {index}")
        final.append(entry)

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "opening_1101_slots_00001_00120_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "each slot received exactly one Codex review pass; slots 1-70 were carried forward without re-review",
        "newly_reviewed_range": [71, 120],
        "carried_review_locked_range": [1, 70],
        "new_review_change_count": len(change_log),
        "new_review_changes": change_log,
        "release_ready": False,
        "entries": final,
    }
    out = PROJECT / "packets" / "reviewed" / "1101_slots_00001_00120_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "previous_review_locked_input": str(previous_path),
        "new_draft_input": str(draft_path),
        "output": str(out),
        "entry_count": len(final),
        "review_passes_per_slot": 1,
        "newly_reviewed_slots": list(range(71, 121)),
        "carried_without_re_review_slots": list(range(1, 71)),
        "new_review_change_count": len(change_log),
        "checks": {
            "slots_exactly_1_through_120": True,
            "previous_review_lock_respected": True,
            "source_text_and_hash_match_catalog": True,
            "caret_token_counts_preserved": True,
            "all_targets_strict_cp949": True,
            "exactly_one_review_per_slot": True,
        },
        "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1101_slots_00071_00120.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": change_log}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
