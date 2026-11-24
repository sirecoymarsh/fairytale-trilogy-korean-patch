from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT_PATH = (
    PROJECT / "packets" / "drafts" / "1136_slots_00001_00030_draft.json"
)
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")

CORRECTIONS = {
    1: "모퉁이를 막 돌려던 순간,^n그 너머에 모여 있는 흰 가운 무리를 발견하고,^n나는 반사적으로 걸음을 멈췄다.",
    2: "모두 똑같이 난처한 표정으로 무언가를 속삭이고 있다.^n이렇게 되면 누가 의사 선생님이고 누가 간호사 선생님이며,^n누가 그 밖의 직원인지 나는 구별할 수 없다.",
    4: "왜…… 어째서 그런 일이…….^n대체 누가 그런 짓을 한 거지.",
    11: "그냥 내버려 두는 수밖에 없겠죠.",
    13: "하지만 그러면 그 아이가 편히 잠들지 못해!",
    17: "글쎄요, 꼭 불에 타 죽었다고 볼 수는 없습니다, 이케노 씨.^n저는 죽은 뒤에 태워졌을 가능성이 더 높다고 봅니다.",
    19: "오히려 언제 죽어도 이상하지 않은 상태였잖아요.^n그 영 미심쩍은 모습을 보면요.^n화장할 수고를 던 셈 치면 되죠, 그렇죠?",
    22: "이케노 씨는 더는 견디지 못한 듯 눈가를 가리고 그 자리를 떠났다.",
    23: "나도 나대로,^n엿듣고 있었다는 걸 들키면 곤란하다는 걸 깨닫고,^n그곳을 떠나기로 했다.",
    25: "(역시 누군가 죽었어.^n여기 사람들은 어떻게든 이 일을 덮으려고 해.)",
    26: "나는 생각보다 동요하지 않은 모양이다.^n어쩌면 이 모든 것을 머리 한구석으로는 예상하고 있었는지도 모른다.",
    28: "(──그건 그렇고, 저런 이케노 씨는 처음 봤어.)",
    29: "언제나 싱글벙글 기분 좋아 보이던 얼굴을 일그러뜨리고,^n눈은 새빨갛게 충혈된 채──떠날 때는 정말 울고 있었던 것 같다.",
    30: "대체 사라져 버린 시체는 누구의 시체였을까.",
}


def slot_from_uid(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT_PATH.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0:
        raise SystemExit("input is not an unreviewed draft")
    if draft.get("scope") != "1136_slots_00001_00030_draft":
        raise SystemExit("unexpected draft scope")

    expected = set(range(1, 31))
    entries: dict[int, dict] = {}
    for source_entry in draft["entries"]:
        entry = dict(source_entry)
        slot = slot_from_uid(str(entry["uid"]))
        if slot in entries:
            raise SystemExit(f"duplicate draft slot {slot}")
        entries[slot] = entry
    if set(entries) != expected:
        raise SystemExit("draft coverage mismatch")

    changes = []
    for slot, target in CORRECTIONS.items():
        before = str(entries[slot]["target_text"])
        entries[slot]["target_text"] = target
        if before != target:
            changes.append({"slot": slot, "before": before, "after": target})

    catalog: dict[int, dict] = {}
    lookup_slots: set[int] = set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1136.gsc":
                continue
            slot = int(item["slot"])
            if slot in expected:
                catalog[slot] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup_slots.add(slot)
    if set(catalog) != expected:
        raise SystemExit("catalog coverage mismatch")
    if lookup_slots != set(range(31, 89)):
        raise SystemExit("lookup slot range mismatch")

    final_entries = []
    for slot in sorted(expected):
        entry = entries[slot]
        source = str(entry["source_text"])
        target = str(entry["target_text"])
        catalog_entry = catalog[slot]
        if source != catalog_entry["source_text"]:
            raise SystemExit(f"source text drift at slot {slot}")
        if entry["source_raw_sha256"] != catalog_entry["source_raw_sha256"]:
            raise SystemExit(f"source hash drift at slot {slot}")
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret token mismatch at slot {slot}")
        if JAPANESE_RE.search(target):
            raise SystemExit(f"Japanese kana residue at slot {slot}")
        target.encode("cp949", errors="strict")
        entry.update(
            {
                "translator": "Codex internal model",
                "review_status": "reviewed_once",
                "reviewer": "Codex internal model single review pass",
                "notes": "초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료",
            }
        )
        final_entries.append(entry)

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1136_all_translatable_slots_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "every translatable slot received exactly one Codex review pass",
        "newly_reviewed_range": [1, 30],
        "new_review_change_count": len(changes),
        "new_review_changes": changes,
        "file_translation_complete": True,
        "lookup_slots_preserved": [31, 88],
        "release_ready": False,
        "entries": final_entries,
    }
    out_path = (
        PROJECT
        / "packets"
        / "reviewed"
        / "1136_all_translatable_slots_reviewed_once.json"
    )
    out_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "draft_inputs": [str(DRAFT_PATH)],
        "output": str(out_path),
        "entry_count": len(final_entries),
        "review_passes_per_slot": 1,
        "newly_reviewed_slots": [1, 30],
        "new_review_change_count": len(changes),
        "checks": {
            "source_text_and_hash_match_catalog": True,
            "caret_token_order_preserved": True,
            "all_targets_strict_cp949": True,
            "no_kana_residue": True,
            "exactly_one_review_per_slot": True,
            "all_translatable_slots_covered": True,
            "lookup_slots_excluded": True,
            "lookup_range_31_88_preserved": True,
        },
        "output_sha256": hashlib.sha256(out_path.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1136_complete.json"
    audit_path.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
