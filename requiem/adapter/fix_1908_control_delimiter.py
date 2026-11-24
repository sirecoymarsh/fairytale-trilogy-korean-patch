from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
MAP_PATH = PROJECT / "packets" / "reviewed" / "1908_all_translatable_slots_reviewed_once.json"
REVIEW_AUDIT = PROJECT / "audit" / "translation_review_1908_complete.json"
FIX_AUDIT = PROJECT / "audit" / "postreview_mechanical_fix_1908_control_delimiter.json"
GENERAL_CONTROL_RE = re.compile(r"\^[A-Za-z][0-9]*")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def main() -> int:
    if FIX_AUDIT.exists():
        raise SystemExit("mechanical fix audit already exists; refusing to apply twice")
    raw_before = MAP_PATH.read_bytes()
    data = json.loads(raw_before.decode("utf-8"))
    review = json.loads(REVIEW_AUDIT.read_text(encoding="utf-8"))
    if data.get("review_passes_completed") != 1:
        raise SystemExit("review count is not exactly one")
    if review.get("output_sha256") != digest(raw_before):
        raise SystemExit("review audit does not bind the current pre-fix map")
    entry = next(item for item in data["entries"] if str(item["uid"]).endswith("slot/00009"))
    before = str(entry["target_text"])
    expected_before = "여기저기 찾아봤거든.^n3월 토끼 씨와 바다거북 씨 모두 모른다는 거야.^n모자 장수는, 뭐, 물어봤자 소용없으니 안 물어봤지만."
    after = "여기저기 찾아봤거든.^n삼월 토끼 씨와 바다거북 씨 모두 모른다는 거야.^n모자 장수는, 뭐, 물어봤자 소용없으니 안 물어봤지만."
    if before != expected_before:
        raise SystemExit("unexpected slot 9 target")
    source_tokens = GENERAL_CONTROL_RE.findall(str(entry["source_text"]))
    before_tokens = GENERAL_CONTROL_RE.findall(before)
    after_tokens = GENERAL_CONTROL_RE.findall(after)
    if before_tokens == source_tokens:
        raise SystemExit("pre-fix target unexpectedly already safe")
    if after_tokens != source_tokens:
        raise SystemExit(f"post-fix control mismatch: {source_tokens} != {after_tokens}")
    after.encode("cp949", errors="strict")
    entry["target_text"] = after
    entry["notes"] = str(entry.get("notes", "")) + "; 검수 후 기계적 제어 코드 경계 수정(3월→삼월), 언어 재검수 아님"
    data["post_review_mechanical_fixes"] = [{
        "slot": 9,
        "kind": "control_token_delimiter",
        "before": before,
        "after": after,
        "review_pass_increment": 0,
    }]
    raw_after = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    MAP_PATH.write_bytes(raw_after)
    audit = {
        "schema": "fairytale-requiem-postreview-mechanical-fix-v1",
        "status": "PASS",
        "file": "1908.gsc",
        "slot": 9,
        "reason": "A digit immediately after ^n was parsed by the independent safety regex as ^n3; word-form 삼월 restores an unambiguous delimiter.",
        "language_review_passes_before": 1,
        "language_review_passes_after": 1,
        "language_rereview_performed": False,
        "before_review_map_sha256": digest(raw_before),
        "after_review_map_sha256": digest(raw_after),
        "source_control_tokens": source_tokens,
        "before_control_tokens": before_tokens,
        "after_control_tokens": after_tokens,
        "strict_cp949": True,
    }
    FIX_AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
