from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    12: "쉿.",
    25: "바삭바삭 소리가 났다.^n보니 물담배 대신인 듯한 담배 모양 초콜릿을^n이케노 씨가 진지한 얼굴로 깨물고 있었다.",
    65: "구멍에 떨어진 뒤로 나는^n커졌다가 작아졌다가 하며 너무 불안정해서,^n십 분도 같은 모습으로 있을 수 없었어요.",
    87: "아니, 내 이야기는 됐어요.^n노래가 조금 엉터리가 되더라도,^n어떻게든 될 테니까요.",
    96: "나보다 이 사람부터 어떻게든 도와주세요!^n기억하고 있는 게 더 적단 말이에요.",
    113: "아, 놀랐어.^n엉터리 『윌리엄 아버지』를 외우는 장면인데,^n설마 앨리스가 『성서』에서 벗어난 행동을 하다니.",
    120: "흔히 있는 일은 아니야.",
    135: "그저 앨리스가 깨어날 무렵 다시 찾아와^n다시 한번 그녀와 이야기하겠다고 마음먹었다.",
}
CARET_RE = re.compile(r"\^[A-Za-z0-9]+")


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_paths = [
        PROJECT / "packets" / "drafts" / "1117_slots_00001_00070_draft.json",
        PROJECT / "packets" / "drafts" / "1117_slots_00071_00135_draft.json",
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
    expected = set(range(1, 136))
    if set(entries) != expected:
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
            if row.get("file") == "1117.gsc" and int(row.get("slot", -1)) in expected:
                catalog[int(row["slot"])] = row
    if set(catalog) != expected:
        raise SystemExit("catalog coverage mismatch")
    final = []
    for index in sorted(expected):
        entry = entries[index]
        source, target = str(entry["source_text"]), str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift {index}")
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret token mismatch {index}")
        target.encode("cp949", errors="strict")
        entry.update({"translator": "Codex internal model", "review_status": "reviewed_once", "reviewer": "Codex internal model single review pass", "notes": "초벌 번역 후 1차 문맥·문체·제어 코드 검수 완료"})
        final.append(entry)
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1117_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 135], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [136, 193], "release_ready": False, "entries": final}
    out = PROJECT / "packets" / "reviewed" / "1117_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(path) for path in draft_paths], "output": str(out), "entry_count": len(final), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 135], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1117_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
