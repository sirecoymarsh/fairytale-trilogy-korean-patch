from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1211_slots_00001_00265_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    23: "아까 그 아이와 스쳐 지나갔거든.^n어쩐지 멍하니 정신이 빠진 채, 휘청휘청 걷고 있었어.",
    25: "괜, 괜찮을까요?",
    30: "간호사는 예쁘고 좋은 향기가 나는 여자였지만,^n그 말투와 하는 소리에 나는 조금 짜증이 났다.",
    45: "너무 어른 취향이라 앨리스와는 어울리지 않는다고 생각했지만,^n실은 좋은 줄도 모르는 것을 어른 흉내를 내며 좋아해 보는^n그런 심리라면 나도 잘 안다.",
    55: "──어머, 안녕하신가요.^n점심때 뵌 뒤로 처음이네요. 몸은 어떠세요?",
    73: "흔히…… 있나.",
    82: "그, 그건 참…… 봉변이었네.",
    94: "나 자신도 참지 못했으면서, 하는 생각도 들지만…….",
    111: "『혀』를 대신해 말하는 건지, 꾸며 낸 목소리로 반성하는 앨리스.^n 나는 진심으로 어이가 없었지만, 동시에 안도했다.",
    115: "그래서 나는 즐거운 화젯거리를 찾아 앨리스의 손에^n늘어놓은 트럼프 카드들을 들여다보았다.",
    120: "네, 이건…….^n이를테면 잠깐 하는 기분 전환이에요.",
    131: "긴 여름날, 꼬박 하루 걸려 만든 파이를 도둑맞다니,^n정말 안됐어요.^n도둑의 목을 치고 싶어지는 것도 당연하죠.",
    141: " 그리폰은 굳이 자기 이름까지 적고 있는 거예요.^n『재판 도중 자기 이름을 잊으면 곤란하잖아』라면서요.^n 저도 모르게 말해 버렸죠. 바보 같다고.",
    146: "느닷없이 몸이 거대해지기 시작한 앨리스에게 화가 나^n건너편으로 가 버리는 겨울잠쥐.^n두 번째 증인인 여자 요리사.",
    161: "네, 정말 뜻밖의 인물이었어요. 저도 깜짝 놀랐죠.^n저와는 아무 상관도 없는데 왜 여기 불려 왔을까,^n지루해 죽겠다며 완전히 방심하고 있었거든요.",
    163: " 그런데 흰토끼가 이런 말을 꺼내는 거예요.^n『증인 앨리스』라고──",
    164: " ^n^m──『피고인 앨리스』──",
    170: "어디에서 나온 누구의 목소리인가.^n남자인지 여자인지, 노인인지 아이인지.^n아니, 애초에 『목소리』였는지도 의심스러웠다.",
    171: "그저 앨리스의 목소리를 지우고, 압도하고, 짓눌러 버린 그 울림에서^n지독하고 역겨운 악의만큼은 느낄 수 있었다.",
    193: "그 허망한 감촉은 우리에게 분수를 가르치는 듯했다.^n우리는 마물의 배 속에서 소화되기를 기다릴 수밖에 없는^n무력한 먹잇감일 뿐이라고──.",
    194: " ^n^m──『피고인 앨리스』.",
    204: "앨리스는 증거품으로 『성서』를 내밀려 했던 것이리라.^n기세 좋게 양손에 든 물건을 들어 올리다가 당황한 목소리를 흘렸다.",
    216: "아, 아아, 아아아…… 그만해요, 그만해…….^n아니에요, 저는 그런 뜻이 아니었어요.",
    232: " 마치 대파된 차체에서 회수되어,^n『마지막의 마지막』을 전하는 블랙박스 녹음을^n 듣고 있는 것처럼──",
    242: "나는 여운이 사라진 뒤^n두근두근 뛰는 새 심장의 잔잔한 고동을 듣고,^n안도의 숨을 내쉬었다.",
    245: "저것도 『피고인 앨리스』의 죄를 고발하는 『목소리』의 일종이다.^n그런 느낌이 들었다.",
    250: "(앨리스만이 아니야.^n 나도 분명 그런 순간을 알고 있어)",
    254: "그 검은 마물은 아마 원래 세계로 돌아갔으리라.^n아마 우리를 옥죄어 비명을 쥐어짜고,^n배가 무거울 만큼 가득 채웠기 때문에.",
    263: "마치 앨리스를 에워싸듯.^n배심원으로, 증인으로, 방청객으로,^n피고인 앨리스를 규탄하듯.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1211_slots_00001_00265_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 266))
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
            if item.get("file") != "1211.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(266, 324)):
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1211_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 265], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [266, 323], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1211_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 265], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_266_323_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1211_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
