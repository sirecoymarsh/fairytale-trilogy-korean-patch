from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CATALOG = PROJECT / "work" / "1404_catalog_dump.json"
INSPECT = PROJECT / "work" / "1404_inspect.txt"
OUTPUT = PROJECT / "audit" / "pending_sensitive_content_1404.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


rows = json.loads(CATALOG.read_text(encoding="utf-8"))
by_slot = {int(row["slot"]): row for row in rows}
evidence_slots = [41, 42, 110]
result = {
    "schema": "fairytale-requiem-sensitive-content-pending-v1",
    "status": "PENDING_NOT_TRANSLATED",
    "file": "1404.gsc",
    "visible_slot_range": [1, 137],
    "lookup_slots_preserved": [138, 195],
    "reason": "The file contains graphically explicit sexual activity and directly describes the participating character as 少女. It remains outside the translated/reviewed/build sets.",
    "evidence": [
        {
            "slot": slot,
            "source_text": by_slot[slot]["source_text"],
            "source_raw_sha256": by_slot[slot]["source_raw_sha256"],
        }
        for slot in evidence_slots
    ],
    "catalog_dump": str(CATALOG),
    "catalog_dump_sha256": sha256(CATALOG),
    "inspect_dump": str(INSPECT),
    "inspect_dump_sha256": sha256(INSPECT),
    "translation_map_created": False,
    "review_passes_completed": 0,
    "build_created": False,
    "trial_modified": False,
}
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({**result, "output": str(OUTPUT), "output_sha256": sha256(OUTPUT)}, ensure_ascii=True, indent=2))
