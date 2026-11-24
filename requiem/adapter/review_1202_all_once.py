from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1202_slots_00001_00035_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    1: "진찰이라고 해도 별다른 일을 하지는 않는다.^n체온과 맥박과 혈압을 재고 몇 가지 문진을 받을 뿐이다.",
    2: "──뭔가 기억난 건 있니?^n──곤란하거나 불편한 일, 해 보고 싶은 일은 있니?",
    3: "그런 질문에 줄곧 『아니요』라고 대답하다 보면 금세 끝난다.",
    8: "하지만 오늘은^n평소처럼 의자에서 일어나려던 순간^n익숙한 흐름이 깨졌다.",
    9: "나는 삐걱 소리를 내며 다시 앉아 고개를 갸웃했다.^n의사 선생님은 그런 나를 보고 조금 놀란 듯했다.",
    11: "어제 일 말이야, 그, 있잖아…….^n화덕에서 새까맣게 탄 시체가 나왔다느니 아니었다느니, 그런 일 있었지.",
    14: "의사 선생님은 말을 잇기 전에 나를 유심히 바라보았다.^n『대사건』에 보이는 내 반응이 미적지근해 의아한 듯하다.",
    15: "나 자신도 어딘가 남의 일처럼 여기는 스스로에게 놀랐다.^n적어도 어젯밤 잠들 때는 끔찍한 광경을 상상하고^n벌벌 떨었는데.",
    18: "조사해 봤는데, 그, 문제는 없었어.^n사람 시체 같은 건 어디에도 없었고, 뭐랄까,^n외부 기관에 연락할 만큼 큰 사건도 아니었지.",
    22: "아니, 묻지 않는 편이 좋겠지.",
    25: "선뜻 고개를 끄덕이며 일어서는 나를,^n의사 선생님은 다시 한번 놀란 눈으로 바라보았다.",
    27: "하지만 내 그런 반응이^n의사 선생님에게는 뜻밖──이라기보다 성에 차지 않는 듯하다.",
    29: "솔직히 말하면 어제 사건이 무엇이었는지,^n어른들의 세계에서 어떻게 결말이 났는지^n관심이 없는 것은 아니다.",
    30: "하지만 그것을 알아내겠다고 헛되이 들이받으며,^n『너희는 모르는 편이 좋은 일이야』 같은^n어른들의 상투적인 말에 어울려 줄 생각은 없다.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1202_slots_00001_00035_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 36))
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
            if item.get("file") != "1202.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(36, 94)):
        raise SystemExit("catalog or lookup coverage mismatch")
    final_entries = []
    for index in sorted(expected):
        entry = entries[index]
        source, target = str(entry["source_text"]), str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift at slot {index}")
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {index}")
        if JAPANESE_RE.search(target):
            raise SystemExit(f"Japanese residue at slot {index}")
        target.encode("cp949", errors="strict")
        entry.update({"translator": "Codex internal model", "review_status": "reviewed_once", "reviewer": "Codex internal model single review pass", "notes": "초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"})
        final_entries.append(entry)
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1202_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 35], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [36, 93], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1202_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 35], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_36_93_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1202_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
