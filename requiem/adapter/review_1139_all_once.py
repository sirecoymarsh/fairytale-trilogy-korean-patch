from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1139_slots_00001_00064_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    1: "낮에는 그렇게 날씨가 좋았는데,^n밤이 되자 탁한 구름이 낮게 드리워,^n금방이라도 떨어질 듯 무겁고 답답하다.",
    2: "그런 하늘이 호숫가에 다다르자 갑자기 맑게 갰다.",
    4: "호수에 반사된 빛의 알갱이로 수놓여, 무거운 밤 속에^n금빛 머리카락과 흰 피부가 아스라이 떠올라 있다.",
    14: "그렇지.^n오딜은 뭔가 말하지 않았어?",
    19: "──아무 말도요.^n다 함께 다과회를 했던 일을 조금…….",
    21: "평소보다 차가운 바람이 우리 사이를 스쳐 간다.^n오데트의 드레스에서 살갗의 그림자가 희미하게 비칠 정도로 얇은 소매가^n바람에 휘날려 팔랑팔랑 물결쳤다.",
    33: "오데트는 위태로운 걸음으로 앞으로 나아와,^n나와 그녀 사이의 얼마 안 되는 거리를 좁혔다.",
    34: "내 손을 잡으려 뻗은 손을, 닿기 직전 조심스레 거두었다.^n망설이듯 굽은 손끝은 잘게 떨리고 있었다.",
    36: "왕자님, 지크프리트 님.^n어떤 일이 있어도 저를 선택해 주시겠어요?",
    43: "대답한다기보다 외운 문구를 암송하면서,^n무거운 대사라고 생각했다.^n그녀에게 가짜 이름을 댔을 때 짊어진 무게다.",
    48: "저도 믿고 있어요.^n제가 당신을 사랑하듯,^n당신도 분명 저를 사랑해 주고 계시다고.",
    51: "미안해요, 조금 불안해졌어요.^n왜 그런 걸까요──저도 참 바보네요.",
    57: "백조 친구들의 이야기.^n다과회에 인간 모습으로 참석했을 때 먹고 싶었던 과자 이야기.^n오딜이 던진 심술과 맞닿은 유머 이야기.",
    59: "──아, 맞다. 얼마 전 당신이 말한 책을 빌렸어요.^n지금 읽고 있는 중이에요.^n저는 읽는 속도가 느리지만…… 아주 재미있어요.",
    61: "뭐였더라?",
    63: "분명 좋아하는 동화를 묻기에^n반사적으로 『피터 팬』이라고 대답했다.",
    64: "다음에 만날 때까지 다 읽어 둘게요, 하고 웃으며^n오데트는 자기 방으로 돌아갔다.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1139_slots_00001_00064_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 65))
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
            if item.get("file") != "1139.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(65, 123)):
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1139_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 64], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [65, 122], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1139_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 64], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_65_122_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1139_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
