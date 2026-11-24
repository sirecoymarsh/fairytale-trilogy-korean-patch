from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1216_slots_00001_00026_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    2: "방으로 찾아가도 문이 활짝 열려 있을 때는^n언제나 자리를 비웠고, 닫혀 있을 때는 노크 소리에^n졸린 목소리가 대답해서 물러날 수밖에 없었다.",
    8: "아, 그리고 이게 가장 중요하네요.^n──당신에게 제 마음을 전할 준비를 해야 해요!",
    11: "그때는 앨리스가 회복한 것이 그저 기뻐서,^n말실수를 해 버린 경솔함과 둘러대는 모습에^n흐뭇하게 쓴웃음을 짓는 것으로 끝났지만.",
    16: "내 머릿속에서^n앨리스의 일기에 적힌 내용과 이어지고 말았을 때는^n부끄러워서 몸부림치고 싶어졌다.",
    20: "하지만 뭐랄까, 어떻게 말해야 할까.^n기쁨보다 당혹감이 강하다.^n그리고 당혹감보다 압도적으로 낯부끄러움이 앞선다.",
    21: "이렇게 간질간질하고 낯간지러운 기분이 드는 건^n본래 앨리스 쪽이어야 하지 않을까.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1216_slots_00001_00026_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 27))
    entries = {slot(str(entry["uid"])): dict(entry) for entry in draft["entries"]}
    if set(entries) != expected:
        raise SystemExit("draft coverage mismatch")
    changes = []
    for index, target in CORRECTIONS.items():
        before = str(entries[index]["target_text"])
        entries[index]["target_text"] = target
        if before != target:
            changes.append({"slot": index, "before": before, "after": target})
    catalog, lookup = {}, set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1216.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(27, 85)):
        raise SystemExit("catalog or lookup coverage mismatch")
    final_entries = []
    for index in sorted(expected):
        entry = entries[index]
        source, target = str(entry["source_text"]), str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift at slot {index}")
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {index}")
        if JAPANESE_RE.search(target):
            raise SystemExit(f"Japanese residue at slot {index}")
        target.encode("cp949", errors="strict")
        entry.update({"translator": "Codex internal model", "review_status": "reviewed_once", "reviewer": "Codex internal model single review pass", "notes": "초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"})
        final_entries.append(entry)
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1216_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 26], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [27, 84], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1216_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 26], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_27_84_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1216_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
