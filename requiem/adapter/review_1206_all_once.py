from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1206_slots_00001_00066_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    2: "어머, 어머어머어머.^n바로 어제 그러고서 벌써, 세상에…….",
    4: "어젯밤 앨리스가 내 방에 찾아왔을 때를 그대로 재현한 모습이다.^n나는 일어나자마자 헝클어진 머리를 대충 누르기만 하고^n바구니를 안아 앨리스의 방으로 찾아왔다.",
    5: "이곳 직원에게 도움을 받을까도 생각했지만,^n나 혼자 옮기기로 한 것은 앨리스가 느꼈던 무게를^n나도 느껴 보며 나름대로 매듭짓기 위해서였다.",
    7: "어서 오세요.^n얼른 들어오세요.",
    12: "……그럴 것 같았어요.",
    14: "왜냐하면 조금 전까지 작아진 당신이^n이 바구니 안에 길을 잃고 들어가서,^n호된 일을 겪는 꿈을 꾸었거든요.",
    15: "어떻게 말을 꺼내야 할지 한참 망설였지만,^n앨리스는 쓴웃음 한 번으로 끝내 줄 모양이다.",
    16: "꿈은 앨리스의 무의식이 투영된 것일까.^n그렇다면 제법 정확하게 내 본심을 꿰뚫어 본 셈이다.",
    18: "당연히 방은 어질러지지만,^n이것도 정리 과정의 하나인 걸까.",
    19: "어쩌다 보니 그 작업을 도우면서,^n나는 미리 준비해 둔 사과를 입에 담았다.",
    21: "……미안해, 역시 그…….^n나는 아무것도 없는 편이 마음이 편해.",
    23: "그렇군요. 물론 그래도 괜찮아요.^n당신은 흰색을 좋아하시는 거네요.",
    27: "나는 아마 흰색이라는 색을 좋아하는 게 아니다.^n아무것도 없는 하얀 방을 좋아한다기보다,^n무언가가 있는 색깔 있는 방이 내게 맞지 않을 뿐이다.",
    30: "……응. 벽도 천장도 흰색 그대로면 좋다고 생각하긴 해.^n나중에 마음이 변할지도 모르지만 적어도 지금은.",
    32: "어머나, 세상에. 흰색을 그렇게 좋아하신다니!^n네, 그렇게나 좋아하시는데 물들이려 하다니,^n제가 정말 실례했어요.",
    34: "저는 아직 멀었군요.^n아직 흰색의 매력을 모르겠어요.^n더욱 정진해야겠어요.",
    39: "아니에요! 대단한 일이에요.^n부끄럽지만 저는 흰색이 색이 아니라고 생각했어요.^n빨강에서 빨강을, 파랑에서 파랑을 뺀 색이 흰색이라고…….",
    41: "하지만 그 뺄셈은 틀렸어요.^n왜냐하면 공기는 하얗지 않으니까요.^n그것은 『무』라는 색이에요.",
    43: "그러니까 흰색은 바로 흰색이라는 색인 거예요!",
    49: "있잖아요, 제가 흰색을 만지고 싶어지면,^n또 찾아와도 될까요?",
    53: "앨리스는 새까맣게 탄 시체를 잊었듯이^n그 일도 잊어버린 걸까.",
    55: "(어느 쪽이든 의식해서 어색해지는 것보다는 낫겠지)",
    64: "내 방을 바꿀 생각은 없었지만,^n앨리스의 알록달록한 방에 찾아와^n빼곡하게 놓인 보물들을 바라보는 것은 제법 즐거우니까.",
    65: "앨리스가 『흰색의 매력』을 이해하려 하듯,^n나도 『흰색이 아닌 것들의 매력』을 알고 싶은 걸까?",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1206_slots_00001_00066_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 67))
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
            if item.get("file") != "1206.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(67, 125)):
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1206_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 66], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [67, 124], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1206_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 66], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_67_124_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1206_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
