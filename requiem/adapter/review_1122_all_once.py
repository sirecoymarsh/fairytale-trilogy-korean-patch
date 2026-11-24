from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    9: "(이 사람은 어제 낮에 이야기했던 바로 그 의사 선생님이겠지.^n　──응, 아마 그럴 거야.)",
    13: "(오늘 아침 앨리스들을 진찰한 건 이 사람……^n　이 아니었을지도?)",
    27: "그렇다면 심인적인 원인…….^n불쾌한 일이 있어서 잊어버렸을 가능성이 크다는 얘기인데.",
    51: "──어릴 때는 누구에게나 있는 일이야.^n다만 『낙원』에 올 정도의 아이는 마음의 상처가 커서,^n치유하는 데 시간이 걸리고 신중함이 필요하지.",
    59: "우화할 때가 올 때까지 마음껏 느긋하게 지내게.",
    68: "그, 제가 이런 말을 하는 것도 이상할지 모르지만…….^n환자들에게는^n이야기에서 벗어난 사물이나 사람이 어떻게 보이나요?",
    69: "자기 망상 속에서 마음대로 살아가는 그녀들이지만,^n말을 걸면 내용을 있는 그대로 받아들이고^n나름대로 대답해 준다.",
    86: "무대 뒤에서 스태프의 보살핌을 받은 배우는 출연 시간이 오면 마음을 바꾸고,^n배역에 완전히 몰입해 무대로 나가.^n무대 위에서 그 역할로서의 삶을 다하는 거지.",
    93: "──그렇게 생각하면 아쉽군.^n그 아이들 하나하나가^n본래는 훌륭한 여배우가 될 수 있었을지도 몰라.",
    96: "방에 돌아가도^n심심함을 견디지 못해 다시 산책하러 나가겠지만,^n마음을 한 번 정리할 필요는 있으니까.",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_paths = [
        PROJECT / "packets" / "drafts" / "1122_slots_00001_00068_draft.json",
        PROJECT / "packets" / "drafts" / "1122_slots_00069_00136_draft.json",
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
    expected = set(range(1, 137))
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
            if row.get("file") == "1122.gsc" and int(row.get("slot", -1)) in expected:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1122_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 136], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [137, 194], "release_ready": False, "entries": final}
    out = PROJECT / "packets" / "reviewed" / "1122_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(path) for path in draft_paths], "output": str(out), "entry_count": len(final), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 136], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1122_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
