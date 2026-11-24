from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    13: "간신히 문에 정면으로 부딪히는 것을 피한 내게^n앨리스는 어딘가 건성인 듯 사과한다.",
    35: "그 손밑을 들여다보니 책상 위에는^n메모지와 공책 조각, 전단지 뒷면 같은 것들이^n뿌려 놓은 듯 어지럽게 겹쳐 있었다.",
    46: "──있잖아요. 예전에 모자 장수가 낸 문제가 있었는데,^n내가 마침내 풀어냈어요.^n머릿속에서 민트 사이다가 톡 터진 듯한 번뜩임이었죠.",
    80: "　까마귀도 글 쓰는 책상도,^n『둘 다 검은 것이 날아다녀요』──",
    92: "앨리스의 목소리가 들뜬다.^n안 그래도 별이 가득한 밤하늘처럼 반짝이던 눈동자가,^n거의 빅뱅 같은 빛을 내며 기쁨으로 일렁인다.",
    94: "아아, 내가 해냈군요.^n이 이상한 세계에서 제대로 된 답을 찾아낸 건^n처음일지도 몰라요…….",
    122: "난 알고 있어요. 모르는 부분에는 값을 대입하면,^n깔끔하게 풀린다고요.^n그래서 많이 대입해 봤어요.",
    135: "앨리스는 하품으로 답했다.^n손끝까지 쭉 편 손을 우아하게 갖다 대도,^n여유롭게 삐져나올 만큼 커다란 하품이다.",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_paths = [
        PROJECT / "packets" / "drafts" / "1123_slots_00001_00060_draft.json",
        PROJECT / "packets" / "drafts" / "1123_slots_00061_00120_draft.json",
        PROJECT / "packets" / "drafts" / "1123_slots_00121_00170_draft.json",
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
    expected = set(range(1, 171))
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
            if row.get("file") == "1123.gsc" and int(row.get("slot", -1)) in expected:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1123_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 170], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [171, 228], "release_ready": False, "entries": final}
    out = PROJECT / "packets" / "reviewed" / "1123_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(path) for path in draft_paths], "output": str(out), "entry_count": len(final), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 170], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1123_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
