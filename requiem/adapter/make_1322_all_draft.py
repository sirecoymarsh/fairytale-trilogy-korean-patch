from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
LOCAL = Path(r"C:\Users\CadriacLord\Documents\Codex\2026-08-12\search-ms-displayname-20pc-20-20\work")
TARGET_PATHS = [LOCAL / "1322_targets_001_054.json"]
OUTPUT_PATH = PROJECT / "packets" / "drafts" / "1322_slots_00001_00054_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    targets: dict[int, str] = {}
    for path in TARGET_PATHS:
        fragment = json.loads(path.read_text(encoding="utf-8"))
        for key, value in fragment.items():
            slot = int(key)
            if slot in targets:
                raise SystemExit(f"duplicate target slot {slot}")
            targets[slot] = str(value)
    expected = set(range(1, 55))
    if set(targets) != expected:
        raise SystemExit(f"target coverage mismatch: missing={sorted(expected-set(targets))}, extra={sorted(set(targets)-expected)}")

    rows: dict[int, dict] = {}
    lookup: set[int] = set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("file") != "1322.gsc":
                continue
            slot = int(row["slot"])
            if slot in expected:
                rows[slot] = row
            elif "lookup_keys" in row.get("lanes", []):
                lookup.add(slot)
    if set(rows) != expected:
        raise SystemExit("catalog coverage mismatch")
    if lookup != set(range(55, 113)):
        raise SystemExit("lookup coverage mismatch")

    entries = []
    for slot in sorted(expected):
        row = rows[slot]
        source = str(row["source_text"])
        target = targets[slot]
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret token mismatch at slot {slot}: {CARET_RE.findall(source)} != {CARET_RE.findall(target)}")
        if JAPANESE_RE.search(target):
            raise SystemExit(f"Japanese kana residue at slot {slot}")
        target.encode("cp949", errors="strict")
        entries.append({
            "uid": row["uid"],
            "source_text": source,
            "source_raw_sha256": row["source_raw_sha256"],
            "target_text": target,
            "translator": "Codex internal model draft",
            "review_status": "draft_pending_single_review",
            "notes": "초벌 번역; 1차 검수 대기",
        })

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1322_slots_00001_00054_draft",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 0,
        "release_ready": False,
        "entries": entries,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "entries": len(entries),
        "lookup_slots_preserved": [55, 112],
        "output": str(OUTPUT_PATH),
        "sha256": sha256(OUTPUT_PATH),
    }, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
