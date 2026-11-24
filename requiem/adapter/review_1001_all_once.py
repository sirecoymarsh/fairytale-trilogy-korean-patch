from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1001_slots_00001_00071_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    3: "막상 그렇게 되고 보니, 역시 그녀의 어깨와 팔은 여리고 부드러워서,^n내가 몹시 난폭한 짓을 한 듯한 기분이 들어 손을 놓았다.",
    4: "한때 불쑥 덮친 충동의 폭풍이었는지,^n그녀는 더 이상 캔버스에 손댈 생각은 없어 보였다.",
    11: "난롯불이 일렁이는 어스름한 실내에서,^n여러 개의 그림자가 소녀를 둘러싸고 있었다.",
    12: "남자들은 게르다에게 정액을 뿜었다.^n온천에 몸을 담근 듯 만족스러운 한숨을 내쉬거나,^n딸꾹질 같은 우스꽝스러운 소리로 목을 울리면서.",
    13: "──부탁이야, 그만 울어.^n──있잖아. 단것, 좋아하지?",
    38: "왼쪽. １명.",
    39: "왼쪽. ２명.",
    40: "왼쪽. ３명.",
    42: "３명.",
    43: "２명.",
    48: "로드 위치별로 추적 변수가 제대로 처리되는지 확인.",
    52: "로드 위치별로 추적 변수가 제대로 처리되는지 확인.",
    56: "화면 갱신·줌 업데이트 테스트.",
    57: "마스크 갱신보다 더 동적으로 업데이트하고 싶을 때 사용.",
    58: "두 번째 매개변수로 갱신 후 초점을 변경.",
    59: "하단 왼쪽부터 １, ２, ３.^n중단 왼쪽부터 ４, ５, ６(０도 중앙).^n하단 왼쪽부터 ７, ８, ９.",
    60: "첫 번째 매개변수 ０(현재 갱신)은 모양새가 좋지 않으므로 사용하지 않습니다.",
    62: "이동 시 장면 전환 등에 쓸 만한 곳이 있으면 사용합시다.^n방향은 로드 명령의 마지막 매개변수로 변경합니다.^n이것은 위에서 아래로.",
    66: "대형 배경·소형 배경 동시 표시. 이미 해당 소형 배경의 장소에 있을 때 사용.",
    67: "대형 배경 표시 후 소형 배경을 시간차로 표시. 이동해 온 느낌을 강조할 때.",
    68: "대형 배경·소형 배경·바스트업 동시 갱신. 『……라는 말이네요』처럼 앞 내용을 이어받아, 처음부터 그 캐릭터가 그곳에 있음을 아는 장면 등에.",
    69: "모든 캐릭터에 감정 기호를 표시합니다.",
    70: "두 번째 매개변수를 ０으로 설정하면 해제됩니다.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1001_slots_00001_00071_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 72))
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
            if item.get("file") != "1001.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    expected_lookup = set(range(72, 130))
    if set(catalog) != expected or lookup != expected_lookup:
        raise SystemExit("catalog or lookup coverage mismatch")

    final_entries = []
    for index in sorted(expected):
        entry = entries[index]
        source, target = str(entry["source_text"]), str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift at slot {index}")
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {index}")
        if index == 10 and (source.count("|") != target.count("|") or source.count("[") != target.count("[") or source.count("]") != target.count("]")):
            raise SystemExit("layout-test ruby markup mismatch at slot 10")
        if JAPANESE_RE.search(target):
            raise SystemExit(f"Japanese residue at slot {index}")
        target.encode("cp949", errors="strict")
        entry.update({"translator": "Codex internal model", "review_status": "reviewed_once", "reviewer": "Codex internal model single review pass", "notes": "초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"})
        final_entries.append(entry)

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1001_all_translatable_slots_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "every translatable slot received exactly one Codex review pass",
        "newly_reviewed_range": [1, 71],
        "new_review_change_count": len(changes),
        "new_review_changes": changes,
        "file_translation_complete": True,
        "lookup_slots_preserved": [72, 129],
        "release_ready": False,
        "entries": final_entries,
    }
    out = PROJECT / "packets" / "reviewed" / "1001_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "draft_inputs": [str(DRAFT)],
        "output": str(out),
        "entry_count": len(final_entries),
        "review_passes_per_slot": 1,
        "newly_reviewed_slots": [1, 71],
        "new_review_change_count": len(changes),
        "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "layout_test_ruby_markup_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_72_129_preserved": True},
        "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1001_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
