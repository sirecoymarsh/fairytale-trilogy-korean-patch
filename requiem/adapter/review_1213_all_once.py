from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1213_slots_00001_00104_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    7: "속으로 그렇게 자조했지만, 변명이 허락된다면^n그저 엿보고 싶은 마음에 침입한 건 아니다.",
    9: "이상한 것을 먹은 길고양이처럼^n툭 쓰러진 채 허무하게 죽어 있지는 않을까,^n어째서인지 그런 최악의 상상이 멈추지 않았기 때문이다.",
    26: "가장 남에게 읽히고 싶지 않은 물건인 일기에^n『읽어 줘!』라는 글자를 써 넣은 대담함을 생각하며,^n나는 피식 웃었다.",
    30: "엿듣기에, 방 침입까지.^n이제 와서 점잔을 뺄 필요는 느끼지 못했다.",
    64: "『이렇게 빨리! 나는 사랑을 알게 되었을지도 모른다.^n어제까지만 해도 내 심장은 도감에 실릴 법한^n징그러운 고깃덩어리였다』",
    66: "『아니, 분명 이건 『연정』 쪽이겠지.^n왜냐하면 나는 툭, 하고 연정에 빠졌으니까』",
    70: "(앨리스는 연정에 빠진 거야?)",
    79: "이렇게 읽고 있으니 지레짐작이 심한 게 안쓰럽기도 하고,^n어디서부터 지적해야 할지 모를 만큼^n터무니없다고 느낄 뿐이지만.",
    85: "『백화점에서 나는 인형을 사 달라고 졸라서 사 주셨다.^n돌아오는 길, 차 안에서 기다리지 못하고 포장을 뜯어 꺼냈다』",
    91: "진중하고 꼼꼼한,^n우등생의 공책 같은 흑백의 지면.",
    102: "익숙했을 앨리스의 미소를 떠올리려 해도,^n귀에 익었을 웃음소리를 그려 보려 해도,^n윤곽만 덧그린 평면적인 이미지가 되는 것이 싫었다.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1213_slots_00001_00104_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 105))
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
            if item.get("file") != "1213.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(105, 163)):
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1213_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 104], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [105, 162], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1213_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 104], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_105_162_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1213_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
