from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    26: "으앗.",
    45: "앗, 괘, 괜찮아?",
    51: "목소리와 행동을 보고 예상은 했지만,^n그곳에 있던 건 작은 여자아이였다.",
    65: "주워서 그녀가 겁먹지 않을 만큼 거리를 둔 채 건네자,^n여자아이는 『고마워』라는 모양으로 입술을 움직이며 받아들었다.",
    92: "아, 그러니까…… 사실 나도 몰라.^n나는 그러니까, 기억이 좀 없거든.^n이름도 가족도 전부 떠오르지 않아.",
    100: "──너는 모르는 거야?^n여동생이니까 오빠가 어떻게 생겼는지^n알아볼 수 있지 않아?",
    113: "사실은 여러 가지를 물어보고 싶었지만,^n더 이상 부담을 주는 건 가엾다.",
    115: "그…… 오빠를 찾을 수 있으면 좋겠네.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_paths = [
        PROJECT / "packets" / "drafts" / "1103_slots_00001_00060_draft.json",
        PROJECT / "packets" / "drafts" / "1103_slots_00061_00119_draft.json",
    ]
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
    if set(entries) != set(range(1, 120)):
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
            if row.get("file") == "1103.gsc" and 1 <= int(row.get("slot", -1)) <= 119:
                catalog[int(row["slot"])] = row
    if set(catalog) != set(range(1, 120)):
        raise SystemExit("catalog coverage mismatch")

    final = []
    for index in range(1, 120):
        entry = entries[index]
        source = str(entry["source_text"])
        target = str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift {index}")
        if source.count("^n") != target.count("^n"):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entry.update(
            {
                "translator": "Codex internal model",
                "review_status": "reviewed_once",
                "reviewer": "Codex internal model single review pass",
                "notes": "초벌 번역 후 1차 문맥·문체·제어 코드 검수 완료",
            }
        )
        final.append(entry)

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1103_all_translatable_slots_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "every translatable slot received exactly one Codex review pass",
        "newly_reviewed_range": [1, 119],
        "new_review_change_count": len(changes),
        "new_review_changes": changes,
        "file_translation_complete": True,
        "lookup_slots_preserved": [120, 177],
        "release_ready": False,
        "entries": final,
    }
    out = PROJECT / "packets" / "reviewed" / "1103_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "draft_inputs": [str(path) for path in draft_paths],
        "output": str(out),
        "entry_count": 119,
        "review_passes_per_slot": 1,
        "newly_reviewed_slots": [1, 119],
        "new_review_change_count": len(changes),
        "checks": {
            "source_text_and_hash_match_catalog": True,
            "caret_token_counts_preserved": True,
            "all_targets_strict_cp949": True,
            "exactly_one_review_per_slot": True,
            "all_translatable_slots_covered": True,
            "lookup_slots_excluded": True,
        },
        "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1103_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
