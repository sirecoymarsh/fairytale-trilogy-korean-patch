from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
EXPECTED_SLOTS = set(range(1, 23)) | set(range(49, 107)) | set(range(156, 174))
CORRECTIONS = {
    20: "내 물건일까 생각하기보다,^n전에 살던 사람의 것이겠다고 나는 생각했다.",
    75: "뒷부분은 어린애가 쓴 듯한 이상한 문장이고 글씨도 서툴다.^n천진하게, 순진하게, 아무 생각 없이,^n남이 시키는 대로 적은 듯한 인상이다.",
    77: "우리 중 한 명, 죄지은 사람이──^n사람을 죽인 죄지은 사람이──",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_paths = [PROJECT / "packets" / "drafts" / "1108_translatable_batch_a_draft.json", PROJECT / "packets" / "drafts" / "1108_translatable_batch_b_draft.json"]
    entries = {}
    for path in draft_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("review_passes_completed") != 0:
            raise SystemExit(f"not a draft: {path}")
        for entry in data["entries"]:
            index = slot(str(entry["uid"]))
            if index in entries:
                raise SystemExit(f"duplicate draft slot {index}")
            entries[index] = dict(entry)
    if set(entries) != EXPECTED_SLOTS:
        raise SystemExit("draft coverage mismatch")
    changes = []
    for index, target in CORRECTIONS.items():
        before = str(entries[index]["target_text"])
        entries[index]["target_text"] = target
        changes.append({"slot": index, "before": before, "after": target})
    catalog = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("file") == "1108.gsc" and int(row.get("slot", -1)) in EXPECTED_SLOTS:
                catalog[int(row["slot"])] = row
    if set(catalog) != EXPECTED_SLOTS:
        raise SystemExit("catalog coverage mismatch")
    final = []
    for index in sorted(EXPECTED_SLOTS):
        entry = entries[index]
        source, target = str(entry["source_text"]), str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift {index}")
        if source.count("^n") != target.count("^n"):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entry.update({"translator": "Codex internal model", "review_status": "reviewed_once", "reviewer": "Codex internal model single review pass", "notes": "초벌 번역 후 1차 문맥·문체·제어 코드 검수 완료"})
        final.append(entry)
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1108_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_slot_ranges": [[1, 22], [49, 106], [156, 173]], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [[23, 48], [107, 155], [174, 231]], "release_ready": False, "entries": final}
    out = PROJECT / "packets" / "reviewed" / "1108_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(path) for path in draft_paths], "output": str(out), "entry_count": len(final), "review_passes_per_slot": 1, "newly_reviewed_slot_ranges": output["newly_reviewed_slot_ranges"], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_counts_preserved": True, "all_targets_strict_cp949": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1108_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
