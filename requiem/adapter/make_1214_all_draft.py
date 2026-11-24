from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
WORK = Path(__file__).resolve().parent
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")


def main() -> int:
    expected = set(range(1, 340))
    targets: dict[int, str] = {}
    parts = sorted(WORK.glob("1214_draft_targets_part_*.json"))
    for path in parts:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("file") != "1214.gsc" or data.get("review_passes_completed") != 0:
            raise SystemExit(f"bad draft part: {path}")
        for raw_slot, target in data["targets"].items():
            index = int(raw_slot)
            if index in targets:
                raise SystemExit(f"duplicate slot: {index}")
            targets[index] = str(target)
    rows, lookup = {}, set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1214.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                rows[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(targets) != expected or set(rows) != expected or lookup != set(range(340, 398)):
        raise SystemExit(f"coverage mismatch targets_missing={sorted(expected-set(targets))} rows_missing={sorted(expected-set(rows))} lookup_missing={sorted(set(range(340,398))-lookup)}")
    entries = []
    for index in sorted(expected):
        row, target = rows[index], targets[index]
        source = str(row["source_text"])
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {index}: {CARET_RE.findall(source)} != {CARET_RE.findall(target)}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": row["uid"], "source_text": source, "source_raw_sha256": row["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 대기"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1214_slots_00001_00339_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1214_slots_00001_00339_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "parts": len(parts), "entries": len(entries), "lookup_slots_preserved": [340, 397], "output": str(out), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
