from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    3: "창가에서 이쪽을 돌아본 라푼젤은^n후드가 드리운 그림자 속에서 조심스레 미소 짓고 있었다.",
    7: "어젯밤에 본 정열적이고 『가식 없이 드러난』 얼굴이 거짓말 같다.^n라푼젤 자신도 잊어버린 게 아닐까 싶을 만큼.",
    22: "저는 이곳에서 나가지 않아요.^n그리고 할머님 말고는 아무도 이곳에 오지 않아요.^n──그렇지요? 알고 계시지요, 할머님.",
    25: "너무 노골적이고 너무나 허술한 거짓말에^n내 가슴은 걷잡을 수 없이 답답해졌다.",
    55: "네, 바깥은 제게 필요하지 않아요.^n그런 억지는 부리지 않을 테니 안심하세요.",
    63: "그리고 라푼젤이 입에 담은 『소원』은^n여러 의미에서 예상 밖이었다.",
    78: "그저, 말이지. 그렇군.^n본래의 그녀가 바라는 일일지도 모르겠네.^n낫기 시작했다는 뜻이려나.",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_path = PROJECT / "packets" / "drafts" / "1120_slots_00001_00087_draft.json"
    data = json.loads(draft_path.read_text(encoding="utf-8"))
    if data.get("review_passes_completed") != 0:
        raise SystemExit("not a draft")
    entries = {slot(str(entry["uid"])): dict(entry) for entry in data["entries"]}
    expected = set(range(1, 88))
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
            if row.get("file") == "1120.gsc" and int(row.get("slot", -1)) in expected:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1120_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 87], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [88, 145], "release_ready": False, "entries": final}
    out = PROJECT / "packets" / "reviewed" / "1120_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(draft_path)], "output": str(out), "entry_count": len(final), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 87], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1120_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
