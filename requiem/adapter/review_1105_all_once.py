from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    23: "──창가에 있으면 햇살이 포근하게 느껴져서^n이런 한낮에도 하품이 나올 정도예요.^n정말 좋은 날씨라 다행이에요, 고델 할머님.",
    48: "저에 대해 할머님이 모르는 일은 없으시잖아요.^n태어나자마자 저를 데려와,^n이곳에서 길러 주셨잖아요.",
    64: "어쩔 수 없네요.^n할머님 마음이 풀릴 때까지 제가 장단을 맞춰 드릴게요.",
    65: "라푼젤은 우아한 손짓으로 둥근 의자를 권했다.^n나는 그 하얀 손끝에 조종당하듯 툭 걸터앉았다.",
    72: "라푼젤에게 나는 아직^n골치 아픈 치매 증상이 생겨 버린 할머님이다.",
    83: "『성서』랍니다.^n　제 일이라면 무엇이든 적혀 있어요.^n",
    95: "그건 됐어요.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_paths = [PROJECT / "packets" / "drafts" / "1105_slots_00001_00055_draft.json", PROJECT / "packets" / "drafts" / "1105_slots_00056_00107_draft.json"]
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
            if row.get("file") == "1105.gsc" and 1 <= int(row.get("slot", -1)) <= 107:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1105_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 107], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [108, 165], "release_ready": False, "entries": final}
    out = PROJECT / "packets" / "reviewed" / "1105_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(path) for path in draft_paths], "output": str(out), "entry_count": 107, "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 107], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_counts_preserved": True, "all_targets_strict_cp949": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1105_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
