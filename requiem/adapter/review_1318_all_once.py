from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1318_slots_00001_00186_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")


CORRECTIONS = {
    48: "──그런 수작에 속을 것 같으냐.",
    65: " 이런, 이런. 곤란하군.^n『악질 환자에게 시달리는 선량한 의사 선생님』은^n 눈썹을 늘어뜨리고 고개를 저었다.",
    74: "게르다 사건을 거짓말로 덧칠해^n우리를 얼버무려 속이려는 속셈이 뻔히 보였다.",
    82: "아무튼 그 이야기는 접어 두고.^n둘 다 아직도 그 환각을 보니?",
    98: "그 말은…….^n우리에게 자살 욕구가 있다는 뜻인가요?",
    105: "『사람을 죽이는 꿈』이란 말이지,^n『지금의 자신에서 다른 자신으로 변하고 싶다』고^n 바라는 본인의 심층 심리가 드러난 것이라고들 한단다.",
    111: "잘 모르겠지만…… 아마 그런 것 같아요.",
    119: "그만하세요!^n괴로워하잖아요!",
    120: "그레텔은 이 이야기가 나오면 창백해져 떨기 시작하고,^n그녀에게만 나타나는 악몽을 응시하는 듯한^n멍한 눈빛이 되어 버린다.",
    155: "나는 일련의 사건 탓에 완전히 맥이 빠져,^n이런 과자 하나를 두고 달려드는 것도^n우스운 일처럼 느껴지기 시작했다.",
    161: "나는 아예 될 대로 되라는 심정으로,^n내민 도넛을 한입 베어 물었다.",
    177: "티 파티가 강제로 끝났을 때의 일이^n싫어도 떠올랐다.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    expected = set(range(1, 187))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1318_slots_00001_00186_draft":
        raise SystemExit("unexpected draft")
    entries = {slot(str(entry["uid"])): dict(entry) for entry in draft["entries"]}
    if set(entries) != expected:
        raise SystemExit("draft coverage mismatch")
    changes = []
    for index, target in CORRECTIONS.items():
        before = str(entries[index]["target_text"])
        entries[index]["target_text"] = target
        if before != target:
            changes.append({"slot": index, "before": before, "after": target})

    catalog = {}
    lookup = set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1318.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(187, 245)):
        raise SystemExit("catalog/lookup mismatch")

    final = []
    for index in sorted(expected):
        entry = entries[index]
        source = str(entry["source_text"])
        target = str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift {index}")
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch {index}")
        if JAPANESE_RE.search(target):
            raise SystemExit(f"Japanese residue {index}")
        target.encode("cp949", errors="strict")
        entry.update({
            "translator": "Codex internal model",
            "review_status": "reviewed_once",
            "reviewer": "Codex internal model single review pass",
            "notes": "초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료",
        })
        final.append(entry)

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1318_all_translatable_slots_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "every translatable slot received exactly one Codex review pass",
        "newly_reviewed_range": [1, 186],
        "new_review_change_count": len(changes),
        "new_review_changes": changes,
        "file_translation_complete": True,
        "lookup_slots_preserved": [187, 244],
        "release_ready": False,
        "entries": final,
    }
    output_path = PROJECT / "packets" / "reviewed" / "1318_all_translatable_slots_reviewed_once.json"
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "draft_inputs": [str(DRAFT)],
        "output": str(output_path),
        "entry_count": len(final),
        "review_passes_per_slot": 1,
        "newly_reviewed_slots": [1, 186],
        "new_review_change_count": len(changes),
        "checks": {
            "source_text_and_hash_match_catalog": True,
            "caret_token_order_preserved": True,
            "all_targets_strict_cp949": True,
            "no_kana_residue": True,
            "exactly_one_review_per_slot": True,
            "all_translatable_slots_covered": True,
            "lookup_slots_excluded": True,
            "lookup_range_187_244_preserved": True,
        },
        "output_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1318_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
