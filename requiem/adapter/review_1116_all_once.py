from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    21: "뻐꾸기는 마지막으로 한 번 울고,^n문 안으로 사라지는 참이었다.",
    36: "어제 데려가진 진찰실 안.^n어딘가에 설치된 카메라가 찍은 영상일까.",
    38: "『……네, 난 원래 몸이 따뜻해요.^n　그러니까 그 정도면 딱 좋아요, 선생님.^n　열이 나는 건 아니에요.』",
    43: "음, 확실히 늘 높은 편이고 본인이 그렇다면…….^n하지만 몸이 안 좋아지면 바로 말하렴.",
    47: "크고 무거워 보이는 그 가슴이^n흘러내리거나 늘어지지 않고^n팽팽하고 둥글게 솟아 있는 것이 신기했다.",
    58: "앨리스와 달리 굴곡 없는 몸이었다.^n어디를 만져도 부드러울 듯한 살집에,^n가슴팍만 다른 곳보다 아주 조금 도톰하다.",
    74: "의사 선생님은 앨리스의 가슴을 움켜쥐고,^n청진기 끝을 가져다 댔다.",
    84: "미안해, 몸이 이상해지면 제대로 말하렴.^n배가 달아오른다든가, 숨이 막힌다든가.",
    98: "꾸우욱……! 열 손가락을 깊이 파묻고,^n기괴한 모양으로 앨리스의 가슴을 일그러뜨리며^n의사 선생님은 웃는다.",
    136: "그레텔은 눈을 크게 뜨고 머리를 좌우로 흔들었다.^n마른 잎 색깔의 머리카락이 거칠게 흐트러진다.",
    183: "그래.^n의사 선생님은 제대로 자기 일을 했을 뿐이고,^n불순한 짓은 하나도 없었다.",
    191: "(──역겨워.)",
    197: "이 『낙원』에서 수상한 낌새를 느껴도,^n내 자신이 역겹다는 생각이 들어도,^n나는 『낙원』에서도 내 몸에서도 도망칠 수 없다.",
}
CARET_RE = re.compile(r"\^[A-Za-z0-9]+")


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_paths = [
        PROJECT / "packets" / "drafts" / "1116_slots_00001_00070_draft.json",
        PROJECT / "packets" / "drafts" / "1116_slots_00071_00140_draft.json",
        PROJECT / "packets" / "drafts" / "1116_slots_00141_00198_draft.json",
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
    expected = set(range(1, 199))
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
            if row.get("file") == "1116.gsc" and int(row.get("slot", -1)) in expected:
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
            raise SystemExit(f"caret token mismatch {index}: {CARET_RE.findall(source)} != {CARET_RE.findall(target)}")
        target.encode("cp949", errors="strict")
        entry.update({"translator": "Codex internal model", "review_status": "reviewed_once", "reviewer": "Codex internal model single review pass", "notes": "초벌 번역 후 1차 문맥·문체·제어 코드 검수 완료"})
        final.append(entry)
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1116_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 198], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [199, 256], "release_ready": False, "entries": final}
    out = PROJECT / "packets" / "reviewed" / "1116_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(path) for path in draft_paths], "output": str(out), "entry_count": len(final), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 198], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1116_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
