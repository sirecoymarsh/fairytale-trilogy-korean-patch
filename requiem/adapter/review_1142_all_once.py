from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1142_all_107_visible_slots_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
LOOKUP_SLOTS = set(range(25, 28)) | set(range(50, 53)) | set(range(88, 98)) | set(range(124, 182))
CORRECTIONS = {
    4: "나는 불빛을 낮춘 방 안,^n어둠 속에서도 희게 빛나는 침대에 누워,^n잘 잠들게 해 달라고 무언가에 빌었다.",
    6: "수면제가 들었을 때의 멍한 느낌도 계속 남아 있었고,^n여러 가지가 상쇄되어 잠들 수 있지 않을까 기대했다.",
    16: "쿵! 하고 폭발할 듯한 심장에 조종당하듯 몸을 일으킨다.^n얼굴에 손을 대 보니 이마에는 차가운 땀이 흠뻑 배어 있었다.",
    20: "상상 속의 『나』는,^n도움을 요청받는 바깥사람이기도 하고,^n속수무책으로 타서 사라지는 피해자 본인이기도 했다.",
    21: "고막은 아직도 단말마의 비명이 내리꽂히는 듯했고,^n목구멍은 죽는 순간까지 계속 외친 듯 따끔거리는 것 같아서,^n나는 어둠 속에서 한동안 몸을 웅크린 채 떨었다.",
    24: "이미 오래전부터 이상했을 터인 머리로 나는 두려워했다.",
    35: "이 『낙원』은 어딘가 이상하다,^n『낙원』이라기에는 너무 뒤틀렸다고 몇 번이나 생각했다.",
    36: "돌이켜 보면 가장 처음 섬뜩함을 느낀 건^n스케치북에 휘갈겨 쓴 글이었다.",
    37: "여기는 위험한 곳.^n모두 사이에 죄인이 있다.",
    40: "그건 머리가 이상한 사람이 남긴 의미 없는 메모가 아니라,^n누군가의 경고였던 걸까.",
    42: "(──모두 사이에 죄인이…….^n그녀들이라는 건 지금 이곳에 있는 환자들?)",
    46: "나는 조용히 자문했다.^n아무도 믿지 못하는 나 자신을 그렇게 나무랄 생각으로.",
    49: "그런데도 내 뜻대로 되지 않는 『나』는,^n너무나 당연하다는 듯 막힘없이 답하기 시작했다.",
    53: "빵과 과자를 만들어 굽고 있던 앨리스.^n그 순간 앨리스에게 중요했던 건^n『빵을 굽는 것』뿐이었을지도 모른다.",
    54: "만약 장난으로 화덕 안에 들어가 있던 사람이 있어도,^n『커다란 칠면조네』 정도로 단정 짓고^n불을 붙이려 했을지도 모른다.",
    57: "어쩌면 그건 그녀가 『성서』에 충실하고자^n벌인 행동이 아니었을까?",
    58: "오데트는 무관하겠지.^n낮에는 자신이 『백조』라고 믿는다.",
    61: "그건 그렇고, 그녀와 스쳐 지나간 『무언가』는 대체 뭐였을까.^n뭔가를 잘못 본 건지, 아니면 그 자체가 거짓말인지.^n그것도 아니면──",
    64: "하지만 누군가를 방해물인 고델 할머니라고 믿었다면,^n죽였다고 해도 이상하지 않다.^n──그런 해석도 성립한다.",
    65: "게르다는 나보다 뒤늦게 주방에 나타났다.",
    66: "그 연기 속에서 주방 안쪽의 화덕에 닿는 건^n내 경험상 쉽지 않았던 것 같다.^n게다가 모두가 연기를 걷으려 하던 흐름 속에서는 부자연스럽다.",
    67: "그런데도 게르다는 곧장 화덕으로 향해,^n『시체』를 목격했다고 했다.",
    68: "게르다의 증언 어딘가에 거짓말이 있는 걸까.^n아니면 연기 속에서 다른 무언가를 하고 있었던 걸까.",
    73: "(──의심한다기보다.^n여기엔 믿을 수 있는 사람이 없어.)",
    75: "(그래, 믿을 수 있는 사람이, 아무도…….)",
    76: "나는 눈을 감고 가쁜 숨을 거듭 내쉬었다.^n어느새 눈꺼풀 안에 번지기 시작한 눈물이 눈을 따갑게 했다.",
    82: "(그래. 누구든 닥치는 대로 의심할 필요는 없어.^n그 아이들 중 정말 죄인이 있다 해도,^n한 명뿐. 한 명뿐이니까.)",
    85: "누가 범인인지보다 누구를 믿을 수 있는지.^n그게 더 중요한 것 아닐까.",
    86: "나는 타 버릴 듯 달아오른 사고 회로를 일부러 반대 방향으로 돌렸다.",
    87: "그중 결백하다고 할 수 있는, 믿을 만한 사람은……",
    98: "앨리스가 이상한 여자아이인 건 분명하다.^n가장 『평범함』에서 동떨어져 있다고 생각한다.",
    103: "그녀가 나를 헨젤이라고 부르는 이상,^n그레텔이 혼자서 이야기를 먼저 진행했다고 보기는 어렵다──^n라는 건 억지에 불과할까?",
    111: "게다가 『성서』를 따라 탑을 뛰쳐나간 라푼젤은^n『성서』에 없는 짓은 하지 않을 것 같다.",
    115: "그러니 나는 게르다를, 게르다의 제정신을 계속 믿기로 하자.",
    117: "『답』을 의식한 순간, 잠의 급류가 한꺼번에 몰려든다.^n하지만 나는 평온한 마음으로 물살에 휩쓸렸다.",
    119: "진실이 어떤 모습인지보다,^n기댈 곳 없는 내가 누군가를 믿고 있다는^n그 사실, 그 실감이 중요하다.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1142_all_107_visible_slots_draft":
        raise SystemExit("unexpected draft")
    entries = {slot(str(entry["uid"])): dict(entry) for entry in draft["entries"]}
    if len(entries) != 107:
        raise SystemExit("draft entry count mismatch")
    changes = []
    for index, target in CORRECTIONS.items():
        if index not in entries:
            raise SystemExit(f"correction outside visible scope: {index}")
        before = str(entries[index]["target_text"])
        entries[index]["target_text"] = target
        if before != target:
            changes.append({"slot": index, "before": before, "after": target})

    catalog = {}
    actual_lookup = set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1142.gsc":
                continue
            index = int(item["slot"])
            if item.get("source_text") and "lookup_keys" not in item.get("lanes", []):
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                actual_lookup.add(index)
    if set(catalog) != set(entries):
        raise SystemExit("visible catalog coverage mismatch")
    if actual_lookup != LOOKUP_SLOTS:
        raise SystemExit("lookup slot set mismatch")

    final_entries = []
    for index in sorted(entries):
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

    reviewed_slots = sorted(entries)
    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1142_all_translatable_slots_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "every translatable slot received exactly one Codex review pass",
        "newly_reviewed_slots": reviewed_slots,
        "new_review_change_count": len(changes),
        "new_review_changes": changes,
        "file_translation_complete": True,
        "lookup_slots_preserved": sorted(LOOKUP_SLOTS),
        "lookup_slot_ranges": [[25, 27], [50, 52], [88, 97], [124, 181]],
        "release_ready": False,
        "entries": final_entries,
    }
    out = PROJECT / "packets" / "reviewed" / "1142_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "draft_inputs": [str(DRAFT)],
        "output": str(out),
        "entry_count": len(final_entries),
        "review_passes_per_slot": 1,
        "newly_reviewed_slots": reviewed_slots,
        "new_review_change_count": len(changes),
        "lookup_slot_count": len(LOOKUP_SLOTS),
        "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "noncontiguous_lookup_set_preserved": True},
        "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1142_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
