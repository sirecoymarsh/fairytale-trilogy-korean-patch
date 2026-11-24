from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    50: "무, 무슨 소리를 하는 거야.^n우리는 어제 처음 만났을 뿐이잖아.",
    52: "아아, 여자한테 익숙하지 않구나.^n뭐든 전부 서툴러.",
    60: "그 여자는 호수는커녕 늪 같은 여자니까.^n귀엽다, 무력하다, 순수하다, 기특하다──그 여자의 멍청함을^n그런 식으로 받아들이고 헤벌쭉하는 놈들이 많았지만…….",
    62: "좋은 결말을 맞은 놈은 하나도 없어.^n남자에게 매달리고 남자를 파멸시켜야만 구원받는^n구제 불능의 창녀. 그게 그 여자야.",
    77: "뺨이 확 달아올랐다.^n나를 분노하게 한 건 오딜의 저속한 말이 아니었다.^n그녀가 띤 연민의 미소였다.",
    111: "하지만 그것은 어디까지가 진심이었을까.^n열에 들뜬 채 품었을 뿐인 얄팍한 충동이 아니었을까.",
    137: "(이런 상처를 줄 거였다면,^n　처음부터 지크프리트라고 하지 말았어야 했어.)",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_paths = [
        PROJECT / "packets" / "drafts" / "1119_slots_00001_00070_draft.json",
        PROJECT / "packets" / "drafts" / "1119_slots_00071_00137_draft.json",
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
    expected = set(range(1, 138))
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
            if row.get("file") == "1119.gsc" and int(row.get("slot", -1)) in expected:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1119_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 137], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [138, 195], "release_ready": False, "entries": final}
    out = PROJECT / "packets" / "reviewed" / "1119_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(path) for path in draft_paths], "output": str(out), "entry_count": len(final), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 137], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1119_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
