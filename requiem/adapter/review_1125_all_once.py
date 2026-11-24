from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    3: "그녀가 오데트에게 품은 악의는^n접하는 것만으로도 기분 좋은 것이 아니다.",
    57: "아, 아니야. 그런…… 그렇지 않아.^n그냥 왠지 손가락이 떨려서 이 버클이 잠기지 않아서…….",
    84: "오딜이 연달아 퍼붓는 핵심어와,^n타이츠 가장자리를 팽팽하게 다시 당기는 몸짓에,^n오데트는 마치 고삐를 당긴 듯 반응하고 있다.",
    86: "무언가 말하고 싶은 듯 입술이 떨리지만,^n흘러나오는 것은 야릇하게 흐트러진 숨소리와,^n말이 되지 못한 끊어진 목소리뿐.",
    90: "우, 우, 움직이는 거, 아……!^n빠, 빨리, 빨리 해 줘, 오딜.",
    93: "나도 얼른 끝내고 싶은데.^n누가 제멋대로 흥분하는 바람에 손이 빗나가잖아.",
    113: "숨겨도 소용없어. ──내가 누군 줄 알아?^n너에게 저주를 건 부엉이 악마 로트바르트의 딸이야.^n전부 훤히 보인다고…….",
    120: "악의가 선명하게 배어나는 몸짓.^n그런데도 오딜은 연민을 담아 태연히 말한다.",
    124: "──다만 너는 데자뷔가 스쳐 가지만.^n관객인 나로서는 조금 신물이 나.",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_paths = [
        PROJECT / "packets" / "drafts" / "1125_slots_00001_00070_draft.json",
        PROJECT / "packets" / "drafts" / "1125_slots_00071_00139_draft.json",
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
    expected = set(range(1, 140))
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
            if row.get("file") == "1125.gsc" and int(row.get("slot", -1)) in expected:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1125_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 139], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [140, 197], "release_ready": False, "entries": final}
    out = PROJECT / "packets" / "reviewed" / "1125_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(path) for path in draft_paths], "output": str(out), "entry_count": len(final), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 139], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1125_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
