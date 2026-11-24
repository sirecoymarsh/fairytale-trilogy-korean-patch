from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")


REVIEW_CORRECTIONS = {
    8: "선명하고 어지러울 만큼 현란한 색채.^n맑은 날의 해바라기밭에서 두 팔을 벌리고,^n빙글빙글 힘껏 계속 도는 듯한.",
    9: "두서없이 떠들썩한 소리.^n웅성거림, 비명, 담소, 흐느낌, 환호, 비탄.^n추억 속 목소리들이 제멋대로 소용돌이치는 듯한.",
    13: "오르골을 떨어뜨렸을 때처럼,^n기묘하고 애처로운 비명 같은 울림.^n──싱거울 만큼 갑작스러운 꿈의 끝이었다.",
    34: "역시 처음 방만큼은 취향이 고약했던 거다.^n그렇게 모든 것이 하얗고 거의 아무것도 없던 방이라니──",
    47: "기다려!　기다려, 토끼 씨!^n",
    54: "가벼운 충돌감이었다.^n달고 또 단, 일부러 그런 듯 지독히 단 과자 냄새가 났다.",
    59: "유난히 반짝이는, 무서울 만큼 아름다운 눈동자.^n떠올리고 생각한 모든 것이 하나하나 별이 되어^n빽빽하게 서로를 밀어내며 빛나는 것만 같다.",
    60: "그 신비한 빛깔의 눈으로 머리끝부터 발끝까지 찬찬히 바라보자,^n어쩐지 부끄러워져 피부가 따끔따끔 화끈거렸다.^n내가 이곳에 있다는 사실을 싫어도 깨닫게 된다.",
    63: "어머나, 어머나, 무슨 일이죠? 대답이 없다니.",
}


def slot_from_uid(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    pilot_path = PROJECT / "packets" / "translated" / "pilot_1101_slots_00001_00020.json"
    draft_path = PROJECT / "packets" / "drafts" / "1101_slots_00021_00070_draft.json"
    pilot = json.loads(pilot_path.read_text(encoding="utf-8"))
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    combined: dict[int, dict[str, object]] = {}
    for entry in [*pilot["entries"], *draft["entries"]]:
        slot = slot_from_uid(str(entry["uid"]))
        if slot in combined:
            raise SystemExit(f"duplicate slot {slot}")
        combined[slot] = dict(entry)
    if set(combined) != set(range(1, 71)):
        raise SystemExit("combined slots are not exactly 1..70")

    change_log: list[dict[str, object]] = []
    for slot, target in REVIEW_CORRECTIONS.items():
        before = str(combined[slot]["target_text"])
        if before != target:
            change_log.append({"slot": slot, "before": before, "after": target})
            combined[slot]["target_text"] = target

    catalog_rows: dict[int, dict[str, object]] = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1101.gsc" and 1 <= int(item.get("slot", -1)) <= 70:
                catalog_rows[int(item["slot"])] = item
    if set(catalog_rows) != set(range(1, 71)):
        raise SystemExit("catalog coverage mismatch")

    entries: list[dict[str, object]] = []
    for slot in range(1, 71):
        entry = combined[slot]
        source = str(catalog_rows[slot]["source_text"])
        target = str(entry["target_text"])
        if str(entry["source_text"]) != source:
            raise SystemExit(f"source drift at slot {slot}")
        if str(entry["source_raw_sha256"]) != str(catalog_rows[slot]["source_raw_sha256"]):
            raise SystemExit(f"source hash drift at slot {slot}")
        if source.count("^n") != target.count("^n"):
            raise SystemExit(f"caret count mismatch at slot {slot}")
        target.encode("cp949", errors="strict")
        entries.append(
            {
                "uid": entry["uid"],
                "source_text": source,
                "source_raw_sha256": entry["source_raw_sha256"],
                "target_text": target,
                "translator": "Codex internal model",
                "review_status": "reviewed_once",
                "reviewer": "Codex internal model single review pass",
                "notes": "초벌 번역 후 한 차례 문맥·문체·제어 코드 검수 완료",
            }
        )

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "opening_1101_slots_00001_00070_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "exactly one Codex review pass; no second offline review",
        "review_change_count": len(change_log),
        "review_changes": change_log,
        "release_ready": False,
        "entries": entries,
    }
    out = PROJECT / "packets" / "reviewed" / "1101_slots_00001_00070_reviewed_once.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "draft_inputs": [str(pilot_path), str(draft_path)],
        "output": str(out),
        "entry_count": len(entries),
        "review_passes_completed": 1,
        "review_change_count": len(change_log),
        "reviewed_slots": list(range(1, 71)),
        "checks": {
            "slots_exactly_1_through_70": True,
            "source_text_and_hash_match_catalog": True,
            "caret_token_counts_preserved": True,
            "all_targets_strict_cp949": True,
            "single_review_pass_recorded": True,
        },
        "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1101_slots_00001_00070.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": change_log}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
