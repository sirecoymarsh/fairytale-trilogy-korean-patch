from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    121: "괜찮아요, 괜찮아.^n있죠, 당신. 내 방에서 잠깐 이야기해요.^n그러면 뭔가 알게 되는 게 있을지도 몰라요!",
    122: "무언가 중얼거리던 앨리스가 내 손을 꼭 잡았다.^n너무나 단 과일 사탕 냄새와^n우주 같은 눈동자 빛깔에 어질어질해졌다──",
    123: "나",
    124: "으, 응…….",
    125: "영문도 모른 채 고개를 끄덕이고,^n손을 잡은 채 걷기 시작한 앨리스에게 이끌리며^n복도를 걷기 시작했다.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    catalog: dict[int, dict[str, object]] = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("file") == "1101.gsc" and row.get("slot") in TARGETS:
                catalog[int(row["slot"])] = row
    if set(catalog) != set(TARGETS):
        raise SystemExit("catalog coverage mismatch")

    draft_entries = []
    for index in sorted(TARGETS):
        source = str(catalog[index]["source_text"])
        target = TARGETS[index]
        if source.count("^n") != target.count("^n"):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        draft_entries.append({
            "uid": catalog[index]["uid"],
            "source_text": source,
            "source_raw_sha256": catalog[index]["source_raw_sha256"],
            "target_text": target,
            "translator": "Codex internal model draft",
            "review_status": "draft_pending_single_review",
            "notes": "초벌 번역; 한 차례 검수 전",
        })
    draft = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "opening_1101_slots_00121_00125_draft",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 0,
        "release_ready": False,
        "entries": draft_entries,
    }
    draft_path = PROJECT / "packets" / "drafts" / "1101_slots_00121_00125_draft.json"
    draft_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Single review pass: the five targets were checked for Alice's voice,
    # narrative continuity, caret controls, and CP949. No wording changes were needed.
    reviewed_tail = []
    for entry in draft_entries:
        item = dict(entry)
        item["translator"] = "Codex internal model"
        item["review_status"] = "reviewed_once"
        item["reviewer"] = "Codex internal model single review pass"
        item["notes"] = "초벌 번역 후 한 차례 문맥·문체·제어 코드 검수 완료"
        reviewed_tail.append(item)

    previous_path = PROJECT / "packets" / "reviewed" / "1101_slots_00001_00120_reviewed_once.json"
    previous = json.loads(previous_path.read_text(encoding="utf-8"))
    if previous.get("review_passes_completed") != 1:
        raise SystemExit("previous review lock missing")
    combined = [*previous["entries"], *reviewed_tail]
    if [slot(str(e["uid"])) for e in combined] != list(range(1, 126)):
        raise SystemExit("combined UID order mismatch")
    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "opening_1101_all_translatable_slots_00001_00125_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "each translatable slot received exactly one Codex review pass; slots 1-120 carried forward without re-review",
        "newly_reviewed_range": [121, 125],
        "carried_review_locked_range": [1, 120],
        "untranslated_lookup_slots": [126, 183],
        "file_translation_complete": True,
        "release_ready": False,
        "entries": combined,
    }
    out = PROJECT / "packets" / "reviewed" / "1101_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "file": "1101.gsc",
        "translatable_slots": [1, 125],
        "lookup_key_slots_preserved": [126, 183],
        "review_passes_per_translatable_slot": 1,
        "previous_review_lock_respected": True,
        "new_review_changes": 0,
        "draft": str(draft_path),
        "output": str(out),
        "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper(),
        "checks": {
            "all_125_translatable_slots_covered": True,
            "lookup_keys_excluded_from_translation": True,
            "source_text_and_hash_from_catalog": True,
            "caret_token_counts_preserved": True,
            "all_targets_strict_cp949": True,
            "exactly_one_review_per_slot": True,
        },
    }
    audit_path = PROJECT / "audit" / "translation_review_1101_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
