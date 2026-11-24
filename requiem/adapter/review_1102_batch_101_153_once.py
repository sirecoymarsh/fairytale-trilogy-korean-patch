from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    102: "당신, 혹시 회색펠리컨 아닐까요?",
    113: "아니라고 해도요.^n회색이라고 해서 비둘기인 건 아니라고 생각해요.^n구구 하고 울지 않잖아요?",
    119: "정말이네요!　어머, 그랬군요.^n……미안해요. 인간은 너무나도 보기 드물어서요.^n특히 야옹도 꿀꿀도 하지 않으면서 말을 하는 인간은요.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    prev_path = PROJECT / "packets" / "reviewed" / "1102_slots_00001_00100_reviewed_once.json"
    draft_path = PROJECT / "packets" / "drafts" / "1102_slots_00101_00153_draft.json"
    prev = json.loads(prev_path.read_text(encoding="utf-8"))
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    if prev.get("review_passes_completed") != 1:
        raise SystemExit("previous review lock missing")

    old = {slot(str(entry["uid"])): dict(entry) for entry in prev["entries"]}
    new = {slot(str(entry["uid"])): dict(entry) for entry in draft["entries"]}
    if set(old) != set(range(1, 101)) or set(new) != set(range(101, 154)):
        raise SystemExit("range mismatch")

    changes = []
    for index, target in CORRECTIONS.items():
        before = str(new[index]["target_text"])
        new[index]["target_text"] = target
        changes.append({"slot": index, "before": before, "after": target})
    for entry in new.values():
        entry.update(
            {
                "translator": "Codex internal model",
                "review_status": "reviewed_once",
                "reviewer": "Codex internal model single review pass",
                "notes": "초벌 번역 후 1차 문맥·문체·제어 코드 검수 완료",
            }
        )

    combined = {**old, **new}
    catalog = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("file") == "1102.gsc" and 1 <= int(row.get("slot", -1)) <= 153:
                catalog[int(row["slot"])] = row
    if set(catalog) != set(range(1, 154)):
        raise SystemExit("catalog range mismatch")

    final = []
    for index in range(1, 154):
        entry = combined[index]
        source = str(entry["source_text"])
        target = str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift {index}")
        if source.count("^n") != target.count("^n"):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        if entry.get("review_status") != "reviewed_once":
            raise SystemExit(f"review state {index}")
        final.append(entry)

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1102_all_translatable_slots_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "each slot received exactly one Codex review pass; slots 1-100 carried forward without re-review",
        "newly_reviewed_range": [101, 153],
        "carried_review_locked_range": [1, 100],
        "new_review_change_count": len(changes),
        "new_review_changes": changes,
        "file_translation_complete": True,
        "lookup_slots_preserved": [154, 211],
        "release_ready": False,
        "entries": final,
    }
    out = PROJECT / "packets" / "reviewed" / "1102_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "previous_review_locked_input": str(prev_path),
        "new_draft_input": str(draft_path),
        "output": str(out),
        "entry_count": 153,
        "review_passes_per_slot": 1,
        "newly_reviewed_slots": [101, 153],
        "carried_without_re_review_slots": [1, 100],
        "new_review_change_count": len(changes),
        "checks": {
            "previous_review_lock_respected": True,
            "source_text_and_hash_match_catalog": True,
            "caret_token_counts_preserved": True,
            "all_targets_strict_cp949": True,
            "exactly_one_review_per_slot": True,
            "all_translatable_slots_covered": True,
            "lookup_slots_excluded": True,
        },
        "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1102_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
