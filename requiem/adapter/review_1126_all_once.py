from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    1: "어젯밤과는 다른 방향으로 발길을 돌려 정원을 산책했다.",
    6: "라푼젤이 사는 탑──^n최상층 창문에서 늘어뜨린 두 갈래의 머리카락을 꽉 붙잡고,^n탑의 벽을 오르는 사람이 있다.",
    10: "그 사람은 누가 봐도 알 만큼 다리를 떨면서도,^n어떻게든 벽을 끝까지 올라갔다.^n라푼젤의 방 창문으로 굴러 들어가더니 사라졌다.",
    11: "얼굴은 보이지 않았지만,^n의사 선생님들과 비슷한 나이대의 남자였던 것 같다.",
    15: "밤에 창문으로 찾아오는 사람을 왕자님이라고 믿는 라푼젤은,^n그러니까 방금 굴러 들어간 남자도──",
    17: "(──그만 생각하자)",
    20: "하지만 필사적으로 창문에 매달린 채 굴러 들어가던^n꼴사납게 버둥거리는 엉덩이와 다리라는 우스꽝스러운 광경은,^n좀처럼 머릿속에서 지워질 것 같지 않았다.",
    21: "나에게 밀쳐지고 슬픈 듯 눈을 크게 뜨던^n어젯밤 라푼젤의 표정도──",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_path = PROJECT / "packets" / "drafts" / "1126_slots_00001_00021_draft.json"
    data = json.loads(draft_path.read_text(encoding="utf-8"))
    if data.get("review_passes_completed") != 0:
        raise SystemExit("input is not an unreviewed draft")
    entries = {slot(str(entry["uid"])): dict(entry) for entry in data["entries"]}
    expected = set(range(1, 22))
    if set(entries) != expected:
        raise SystemExit("draft coverage mismatch")

    changes = []
    for index, target in CORRECTIONS.items():
        before = str(entries[index]["target_text"])
        entries[index]["target_text"] = target
        changes.append({"slot": index, "before": before, "after": target})

    catalog: dict[int, dict] = {}
    lookup_slots = set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("file") != "1126.gsc":
                continue
            index = int(row["slot"])
            if index in expected:
                catalog[index] = row
            elif "lookup_keys" in row.get("lanes", []):
                lookup_slots.add(index)
    if set(catalog) != expected:
        raise SystemExit("catalog coverage mismatch")
    if lookup_slots != set(range(22, 80)):
        raise SystemExit("lookup-slot range mismatch")

    final = []
    for index in sorted(expected):
        entry = entries[index]
        source = str(entry["source_text"])
        target = str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift {index}")
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret token mismatch {index}")
        target.encode("cp949", errors="strict")
        entry.update({
            "translator": "Codex internal model",
            "review_status": "reviewed_once",
            "reviewer": "Codex internal model single review pass",
            "notes": "초벌 번역 후 1차 문맥·문체·용어·코드 검수 완료",
        })
        final.append(entry)

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1126_all_translatable_slots_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "every translatable slot received exactly one Codex review pass",
        "newly_reviewed_range": [1, 21],
        "new_review_change_count": len(changes),
        "new_review_changes": changes,
        "file_translation_complete": True,
        "lookup_slots_preserved": [22, 79],
        "release_ready": False,
        "entries": final,
    }
    out = PROJECT / "packets" / "reviewed" / "1126_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "draft_inputs": [str(draft_path)],
        "output": str(out),
        "entry_count": len(final),
        "review_passes_per_slot": 1,
        "newly_reviewed_slots": [1, 21],
        "new_review_change_count": len(changes),
        "checks": {
            "source_text_and_hash_match_catalog": True,
            "caret_token_order_preserved": True,
            "all_targets_strict_cp949": True,
            "exactly_one_review_per_slot": True,
            "all_translatable_slots_covered": True,
            "lookup_slots_excluded": True,
        },
        "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1126_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
