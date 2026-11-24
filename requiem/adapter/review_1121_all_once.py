from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    29: "이윽고 게르다가 꺼낸 것은 그런 질문이었다.^n주위를 의식하듯 작은 목소리로,^n어떻게든 해석할 수 있는 애매한 방식으로.",
    42: "이렇게 신세 지고 있으면서 이런 말 하긴 뭐하지만,^n──이상한 곳이라고 생각해.",
    52: "나는 참지 못하고 호흡을 흐트러뜨린다.",
    69: "그렇다고 해서^n빠져나간다거나, 도망친다거나, 맞선다거나──^n아직 그렇게까지 결심할 수는 없지만.",
    71: "알아. 갈 곳 따위 없잖아.^n게다가 이곳은 꽤 경비가 삼엄해.^n나는 몇 번이나 실패해 붙잡혀 돌아왔어.",
    75: "대놓고 물어도 될지 망설이자,^n게르다는 깊이 고민한 듯한 옆얼굴로 눈을 감았다.",
    79: "나는 분명 이상한 걸지도 몰라.^n나 자신도 어이없을 만큼 생각이 정리되지 않고 두서가 없어.^n치료가 필요할지도 모르지.",
    93: "게르다는 마음을 정한 듯 고개를 끄덕였다.",
    122: "왜냐하면──사실대로 이야기하면 인정해야 한다.^n이상한 곳에 휘말려 들어온 나를,^n그런데도 어디에도 갈 수 없는 나를.",
    137: "게르다의 태도에 달라진 점은 없지만,^n그녀가 변하려 하지 않는 나를 존중한 것과^n원래처럼 거리를 두려 한다는 것은 어렴풋이 알 수 있었다.",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_paths = [
        PROJECT / "packets" / "drafts" / "1121_slots_00001_00070_draft.json",
        PROJECT / "packets" / "drafts" / "1121_slots_00071_00140_draft.json",
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
    expected = set(range(1, 141))
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
            if row.get("file") == "1121.gsc" and int(row.get("slot", -1)) in expected:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1121_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 140], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [141, 198], "release_ready": False, "entries": final}
    out = PROJECT / "packets" / "reviewed" / "1121_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(path) for path in draft_paths], "output": str(out), "entry_count": len(final), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 140], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1121_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
