from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1141_slots_00001_00055_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    2: "나를 보고 몸을 일으키려 했지만 만류했다.^n초췌한 얼굴과 좋지 않은 안색이 마음에 걸렸기 때문이다.",
    7: "게르다가 힘없이 되묻는다.^n노크에 답하던 목소리부터 힘이 없어서 예상은 했지만,^n역시 기진맥진한 듯하다.",
    8: "어젯밤부터 이어진 몸의 이상과 오늘 아침의 진찰,^n새까맣게 탄 시체 목격, 수면제──^n그럴 만하다고 생각한다.",
    15: "다시 몸을 눕히려던 게르다는^n갑자기 용수철이라도 달린 듯 벌떡 일어났다.",
    16: "자기 옷을 털듯 몸 여기저기를 살피며,^n무언가를 확인하는 눈치다.",
    22: "아마 그 자리를 끝내고 우리를 방으로 옮기려고 그랬던 것 같아…….^n나도 정신을 차려 보니 내 방에 있었어.",
    24: "뭐야, 그게. 굳이 재우지 않아도 되잖아!^n역시 이 『낙원』은 이상해.^n뭔가 나쁜 목적이 있다고밖에는 생각할 수 없어.",
    25: "게르다가 드물게 이성을 잃은 채 거리낌 없이 불신을 입에 담는다.",
    26: "그 모습을 보니^n오늘 아침 보게 된 그녀의 진찰 모습이 떠올랐다.^n게르다가 경계심을 키우는 것도 당연하다.",
    28: "나는 원래 어른이란^n귀찮은 일을 해결하려고 그런 수단을 고르기 마련이라고^n체념했기에 나름대로 납득했을 뿐이고.",
    29: "게르다에게는 내 짐작 따위 아무 근거도 되지 않고,^n섣불리 달래려다가는,^n이 『낙원』과 함께 나까지 싫어하게 될 뿐이다.",
    31: "──게르다, 그, 안색이 안 좋아.^n감기, 아직 안 나은 거 아니야…….",
    32: "대신 나는 그런 말을 꺼냈다.^n실제로 동요 탓이라고 보기에는 게르다의 안색이 지나치게 탁해서,^n무척 걱정스럽기는 했다.",
    35: "사실은 너와 여러 가지를 이야기하고 싶었어.^n하지만 그리 기분 좋은 이야기는 아니고…….",
    41: "그, 오늘은 여러 일이 있었잖아…….^n몸 따뜻하게 하고 푹 자.",
    44: "게르다는 한동안 나를 바라보다가,^n이윽고 온몸의 힘을 풀고 침대 가장자리에 걸터앉았다.",
    53: "(다시 이야기할 기회가 생기면 듣고 싶지만…….^n다시 꺼내는 것도 좋지 않으려나.)",
    55: "(우선 게르다의 몸이 나은 뒤에.^n상태를 봐 가며 이야기하자.)",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1141_slots_00001_00055_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 56))
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
            if item.get("file") != "1141.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(56, 114)):
        raise SystemExit("catalog or lookup coverage mismatch")
    final_entries = []
    for index in sorted(expected):
        entry = entries[index]
        source = str(entry["source_text"])
        target = str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift at slot {index}")
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {index}")
        if JAPANESE_RE.search(target):
            raise SystemExit(f"Japanese residue at slot {index}")
        target.encode("cp949", errors="strict")
        entry.update({"translator": "Codex internal model", "review_status": "reviewed_once", "reviewer": "Codex internal model single review pass", "notes": "초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"})
        final_entries.append(entry)
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1141_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 55], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [56, 113], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1141_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 55], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_56_113_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1141_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
