from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    23: "　이 불길한 나무들은 아무래도 진열대인 듯,^n　하이힐과 목걸이, 숄 등이 걸려 있지만,^n『여자가 저주로 나무가 된 것』처럼밖에 보이지 않는다.",
    27: "유일하게 눈을 달래 줄 만한 것은,^n천장에서 호수 위로 매달린 커다란 새장이었다.^n금빛 새장의 섬세한 광채가 이 풍경 속에서는 눈부시다.",
    41: "뭐야. 무슨 말이라도 해 보지 그래.^n아까 문 너머에서 이러쿵저러쿵 지저귀고 있었으니,^n말을 못 하는 건 아니잖아.",
    57: "댈 이름이 없다면 어쩔 수 없지.^n난 있으니까 말해 둘게.^n──나는 오딜.",
    96: "아하하, 걸작이야!　『성서』를 놓친 것 하나 때문에,^n과거와 미래까지 바뀌어 버리다니.^n자기 멍청함을 저주하는 게 좋겠네.",
    104: "찾으면 좋겠네.^n소중하고 소중한, 너 자신이 말이야.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_paths = [
        PROJECT / "packets" / "drafts" / "1104_slots_00001_00055_draft.json",
        PROJECT / "packets" / "drafts" / "1104_slots_00056_00107_draft.json",
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
    if set(entries) != set(range(1, 108)):
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
            if row.get("file") == "1104.gsc" and 1 <= int(row.get("slot", -1)) <= 107:
                catalog[int(row["slot"])] = row
    if set(catalog) != set(range(1, 108)):
        raise SystemExit("catalog coverage mismatch")

    final = []
    for index in range(1, 108):
        entry = entries[index]
        source, target = str(entry["source_text"]), str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift {index}")
        if source.count("^n") != target.count("^n"):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entry.update({"translator": "Codex internal model", "review_status": "reviewed_once", "reviewer": "Codex internal model single review pass", "notes": "초벌 번역 후 1차 문맥·문체·제어 코드 검수 완료"})
        final.append(entry)

    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1104_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 107], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [108, 165], "release_ready": False, "entries": final}
    out = PROJECT / "packets" / "reviewed" / "1104_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(path) for path in draft_paths], "output": str(out), "entry_count": 107, "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 107], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_counts_preserved": True, "all_targets_strict_cp949": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1104_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
