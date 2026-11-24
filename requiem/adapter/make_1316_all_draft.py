from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
WORK = Path(r"C:\Users\CadriacLord\Documents\Codex\2026-08-12\search-ms-displayname-20pc-20-20\work")
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")


def main() -> int:
    targets: dict[int, str] = {}
    for name in ("1316_targets_001_110.json", "1316_targets_111_222.json"):
        data = json.loads((WORK / name).read_text(encoding="utf-8"))
        for key, value in data.items():
            index = int(key)
            if index in targets:
                raise SystemExit(f"duplicate target {index}")
            targets[index] = str(value)

    expected = set(range(1, 223))
    if set(targets) != expected:
        raise SystemExit(f"target coverage mismatch: missing={sorted(expected-set(targets))}, extra={sorted(set(targets)-expected)}")

    rows = {}
    lookup = set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1316.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                rows[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(rows) != expected or lookup != set(range(223, 281)):
        raise SystemExit("catalog/lookup coverage mismatch")

    entries = []
    for index in sorted(expected):
        row = rows[index]
        source = str(row["source_text"])
        target = targets[index]
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch {index}: {CARET_RE.findall(source)} != {CARET_RE.findall(target)}")
        if JAPANESE_RE.search(target):
            raise SystemExit(f"Japanese residue {index}")
        target.encode("cp949", errors="strict")
        entries.append(
            {
                "uid": row["uid"],
                "source_text": source,
                "source_raw_sha256": row["source_raw_sha256"],
                "target_text": target,
                "translator": "Codex internal model draft",
                "review_status": "draft_pending_single_review",
                "notes": "초벌 번역; 1차 검수 대기",
            }
        )

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1316_slots_00001_00222_draft",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 0,
        "release_ready": False,
        "entries": entries,
    }
    output_path = PROJECT / "packets" / "drafts" / "1316_slots_00001_00222_draft.json"
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "PASS",
                "entries": len(entries),
                "lookup_slots_preserved": [223, 280],
                "output": str(output_path),
                "sha256": hashlib.sha256(output_path.read_bytes()).hexdigest().upper(),
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
