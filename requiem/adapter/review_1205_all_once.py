from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1205_slots_00001_00030_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    4: "그 뒤 앨리스와 함께 밤의 정원을 산책했다.^n물론 모니터에 비친 광경의 기억을^n희미하게 만들기 위해서였다.",
    5: "도중에 오데트를 만나 잠시 서서 이야기를 나누기도 하고,^n장미 생울타리가 미로처럼 얽힌 곳에서^n술래잡기 흉내를 내기도 했다──",
    8: "무언가에 정신이 팔려 있을 때는 순순히 잊고 있지만,^n머릿속에 여유가 생기면 되살아나는 거품 같은 명멸을^n반복했던 것 같다.",
    9: "혐오감보다는 호기심을 자극받은 듯했다.^n뭐, 그것이 나를 경멸하는 형태로 나타나지 않았다는 건^n내게는 다행이었겠지.",
    11: "(………………자야겠다)",
    13: "침대에 들어가려던 참에,^n그 옆에 그대로 놓여 있던^n바구니를 어떻게 치울지 난감해졌다.",
    16: "고민 끝에 옷장에 밀어 넣기로 했다.^n침대 밑에 두었다가 청소하는 아주머니에게 보이면^n분명 부끄러워질 것 같다.",
    19: "질감도 색도 인상도 제각각인 잡동사니가^n하얀 옷장 문 뒤로 닫혀 가는 모습을 보며,^n나는 그렇게 결심했다.",
    20: "혼자 있으면 잡동사니를 보며 설레던 기분보다,^n마음 깊은 곳의 무기질적인 『경고』가 훨씬 강하게 느껴진다.",
    25: "아무것도 장식하고 싶지 않은 것은 내 자유고,^n딱히 떳떳하지 못할 이유도 없다.",
    27: "나는 침대에 눕기 전에,^n방 안 풍경을 천천히 둘러보았다.",
    28: "깨끗하고 쓸데없는 물건이 없으며 말끔하고,^n이곳에 사는 나 자신의 냄새조차 느껴지지 않는,^n공허하지만 마음이 편해지는 방.",
    29: "처음에는 마음이 놓이지 않았지만,^n이건 이것대로 괜찮고 이 방은 이 모습으로 완성된 거라며^n──그런 자랑스러움마저 느낀다.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1205_slots_00001_00030_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 31))
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
            if item.get("file") != "1205.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(31, 89)):
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1205_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 30], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [31, 88], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1205_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 30], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_31_88_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1205_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
