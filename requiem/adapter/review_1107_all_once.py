from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    5: "뒤돌아보자 머리 하나만큼 위에서,^n입꼬리를 씨익 치켜올렸지만 그다지 즐거워 보이지 않는 미소가^n나를 내려다보고 있었다.",
    22: "(우와…….)",
    34: "아니야, 괜찮단다.^n우리 같은 아저씨들은 걱정하는 게 일이니까.",
    72: "그렇게 생각하면서도 말을 삼킨 건 정말 그냥 어쩐지 그랬기 때문이다.^n──기억은 없지만 나는 늘 그렇게 해 온 것 같다.",
    151: "하지만 나는 하아, 하고 맥없는 대답을 했다.^n애초에 그다지 즐거운 일이라고 생각하지도 않았으니까.",
    156: "──그래도 그런 일이 생긴 뒤,^n빠져 버린 머리에 달린 인형의 눈이 빤히 바라본다면,^n분명 어색할 것이다.",
    202: "그 뒤 손에 든 차트 같은 것에^n무언가를 벅벅 적던 의사 선생님은 이윽고,^n하아, 하고 크게 한숨을 내쉬며 머리를 감쌌다.",
    239: "결국 어떤 계기로 기억이 돌아왔을 때,^n위험한 증상이 나타나면 우리 책임이 되고.^n다른 병원으로 보낼 수도 없겠군. 그럴 수 없지.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_paths = [
        PROJECT / "packets" / "drafts" / "1107_slots_00001_00070_draft.json",
        PROJECT / "packets" / "drafts" / "1107_slots_00071_00140_draft.json",
        PROJECT / "packets" / "drafts" / "1107_slots_00141_00210_draft.json",
        PROJECT / "packets" / "drafts" / "1107_slots_00211_00273_draft.json",
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
    if set(entries) != set(range(1, 274)):
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
            if row.get("file") == "1107.gsc" and 1 <= int(row.get("slot", -1)) <= 273:
                catalog[int(row["slot"])] = row
    if set(catalog) != set(range(1, 274)):
        raise SystemExit("catalog coverage mismatch")
    final = []
    for index in range(1, 274):
        entry = entries[index]
        source, target = str(entry["source_text"]), str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift {index}")
        if source.count("^n") != target.count("^n"):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entry.update({"translator": "Codex internal model", "review_status": "reviewed_once", "reviewer": "Codex internal model single review pass", "notes": "초벌 번역 후 1차 문맥·문체·제어 코드 검수 완료"})
        final.append(entry)

    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1107_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 273], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [274, 331], "release_ready": False, "entries": final}
    out = PROJECT / "packets" / "reviewed" / "1107_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(path) for path in draft_paths], "output": str(out), "entry_count": 273, "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 273], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_counts_preserved": True, "all_targets_strict_cp949": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1107_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
