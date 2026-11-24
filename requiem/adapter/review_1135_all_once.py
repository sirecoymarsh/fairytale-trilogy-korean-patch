from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT_PATH = (
    PROJECT / "packets" / "drafts" / "1135_slots_00001_00298_draft.json"
)
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")

CORRECTIONS = {
    9: "넓은 정원에서 꽃이 가장 많이 심긴 구역,^n그중에서도 장미 아치가 가장 아름답게 보이는 자리.",
    22: "요컨대 나는,^n어른들이 우리를 위해 열어 준 이 다과회에서^n노골적으로 비위를 맞추려는 기색만 느껴져 진절머리가 난다.",
    26: "이 캔디, 달아요.^n이 달콤함이 저를 응석받이로 만들어요!",
    34: "라푼젤은 쓴웃음을 지으며,^n시나몬 롤에서 그레텔의 입가에 묻은^n치즈 아이싱을 닦아 준다.",
    48: "예, 예…….^n이게 어쩌다 이렇게 된 걸까요.^n──저는…….",
    51: "왜 그래요, 눈을 뜬 채 꿈꾸는 것 같은 표정을 하고.",
    53: "눈을 뜬 채, 꿈을…….^n──네, 그럴지도 모르겠네요.^n이건 전부 꿈…….",
    54: "앨리스의 순진한 비유를 곧이곧대로 받아들이고,^n그걸로 모든 것을 납득하기로 한 모양이다.^n스스로에게 타이르듯 중얼거린다.",
    79: "너무 괴롭히지 말아 주세요, 오딜.^n모처럼 이렇게 행복하게 먹고 있는데.",
    89: "단것을 좋아하는 것도, 차를 좋아하는 것도,^n포근한 날씨나 가든 파티, 담소 같은 걸 좋아하는 것도,^n붙임성 좋고 심술궂지 않은 것도 전부 이쪽이야.",
    95: "흐음.^n두 사람은 거울 너머에서 온 것처럼 꼭 닮았는데.^n오딜은 어떻게 해서든 오데트가 될 수는 없나요?",
    100: "내뱉듯 말하는 오딜의 어조에는^n살을 태우는 듯한 실감이 배어 있었다.",
    104: "그녀가 거짓말을 한 게 아니라면,^n오딜은 『처음 보는 키』의 사람 그림자와 스쳐 지나갔다고 했다.",
    110: "……뭐야. 무슨 볼일이야?",
    116: "어른들이 마련한 이런 어린애 속이기식 비위 맞추기가^n보기 좋게 먹혀들었다는 건 조금 분하지만,^n그래도 고마운 건 고맙다.",
    131: "하지만 게르다의 심정도 아플 만큼 잘 알았다.^n만약 『무언가』가 있다면, 흐지부지되는 건 무섭다.",
    150: "결국 그렇게 된다면 어쩔 수 없지.^n하지만 지금 이 시점에는, 인간의 손이 닿는 범위에서도,^n아무것도 할 생각이 없어 보이니까.",
    155: "너희가 빵을 구운 게 이 일의 시작이었지.^n화덕에 불을 붙인 것도 너희니?",
    160: "그레텔은 양 볼 가득 욱여넣은 음식을^n꿀꺽 삼키며 고개를 끄덕인다.",
    175: "당신이 말한 환풍기가 어떻게 됐나 싶어^n다시 화덕에 다가갔어요.",
    177: "그런데 밖으로 당겨져 있던 트레이 위를 보니──",
    182: "그만큼 큰 화덕이야.^n많은 사람 몫의 요리를 한꺼번에 완성하니까.^n그러네…… 화덕보다는 소각로라는 인상을 받았어.",
    184: "내가 주방에 도착했을 때,^n이미 문간에는 라푼젤이 있었지.",
    186: "네, 연기가 너무 심해서…….^n저는 어찌해야 할지 몰랐어요.",
    188: "사람이 너무 많아져도 시야가 나빠 부딪힐 위험만 커질 뿐이야.^n사람을 불러 준 네 판단이 옳았다고 생각해.",
    191: "나도──결국 이 애 뒤를 따라 들어가서,^n연기 속을 헤매다 우연히 보게 됐어.",
    202: "너, 계속 문간에 서 있었어?",
    204: "어, 네. 어디론가 가는 것도 무서워서…….^n어쩌지도 못하고 누군가 지나가길 기다리고 있었어요.",
    206: "안에서 나간 사람은 없었지.",
    208: "네.^n제가 온 뒤 소동이 가라앉을 때까지는 아무도요.",
    212: "……읏.",
    217: "오딜이 말 이면에 내비친,^n『화덕 안에서 빠져나와 걸어서 주방을 나가는^n새까맣게 탄 시체』 같은 건.",
    226: "그 뒤 우리는 한 번 다시 파헤친 것을 도로 묻듯^n다과회를 계속 즐겼다.",
    227: "이번에는 게르다도 분위기에 맞췄다.^n아니, 한 번 분위기를 바꿔 버린 걸 마음에 두던 그녀가^n가장 적극적으로 자리를 부드럽게 만들려 했을지도 모른다.",
    234: "(지쳤네…….)",
    244: "즐거운 중에 미안하지만, 이제 해도 슬슬 기울었고, 그렇지?^n이 한 잔으로 건배하고 다과회는 마치는 걸로…….",
    253: "맛있어요…….^n다과회에 옥수수 수프라니 반칙이에요.^n반칙이란 건 맛있는 거군요.",
    257: "과자에 얼버무려지고 싶지는 않았지만,^n이 수프의 순한 맛에 속아 행복한 기분이 드는 건^n나쁘지 않다──그런 생각이 들었다.",
    259: "끝낸대.^n아쉽네. 조금만 더 있으면 네 시간이었는데.",
    272: "아무래도 우리 모두 함께^n잠의 느린 소용돌이에 휘말리고 있는 듯하다.",
    275: "어……? 왜……?^n아…….^n이건…… 이상해…….",
    277: "그제야 나는,^n이 비정상적인 졸음과 따뜻한 옥수수 수프의 부드러운 맛을^n연결 지어 생각했다.",
    279: "하얀 방의 하얀 침대.^n평소에 눈을 뜰 때와 다른 것은 창밖에 펼쳐진^n완전히 해가 진 풍경뿐이다.",
    281: "그럴 만도 하다.^n그 다과회 도중 나는 수면제를 탄 수프를 마시고^n강제로 잠든 사이에 옮겨졌으니까.",
    291: "(너무하잖아.^n끝낸다고 말해 줬으면 다들 얌전히 돌아갔을 텐데.)",
    294: "혼란 속에 혼란이 섞여 버렸달까.^n──그게 좋은 일인 걸까.",
}


def slot_from_uid(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT_PATH.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0:
        raise SystemExit("input is not an unreviewed draft")
    if draft.get("scope") != "1135_slots_00001_00298_draft":
        raise SystemExit("unexpected draft scope")

    expected = set(range(1, 299))
    entries: dict[int, dict] = {}
    for source_entry in draft["entries"]:
        entry = dict(source_entry)
        slot = slot_from_uid(str(entry["uid"]))
        if slot in entries:
            raise SystemExit(f"duplicate draft slot {slot}")
        entries[slot] = entry
    if set(entries) != expected:
        raise SystemExit("draft coverage mismatch")
    if not set(CORRECTIONS).issubset(expected):
        raise SystemExit("correction outside review scope")

    changes = []
    for slot, target in CORRECTIONS.items():
        before = str(entries[slot]["target_text"])
        entries[slot]["target_text"] = target
        if before != target:
            changes.append({"slot": slot, "before": before, "after": target})

    catalog: dict[int, dict] = {}
    lookup_slots: set[int] = set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1135.gsc":
                continue
            slot = int(item["slot"])
            if slot in expected:
                catalog[slot] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup_slots.add(slot)
    if set(catalog) != expected:
        raise SystemExit("catalog coverage mismatch")
    if lookup_slots != set(range(299, 357)):
        raise SystemExit("lookup slot range mismatch")

    final_entries = []
    for slot in sorted(expected):
        entry = entries[slot]
        catalog_entry = catalog[slot]
        source = str(entry["source_text"])
        target = str(entry["target_text"])
        if source != catalog_entry["source_text"]:
            raise SystemExit(f"source text drift at slot {slot}")
        if entry["source_raw_sha256"] != catalog_entry["source_raw_sha256"]:
            raise SystemExit(f"source hash drift at slot {slot}")
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret token mismatch at slot {slot}")
        if JAPANESE_RE.search(target):
            raise SystemExit(f"Japanese kana residue at slot {slot}")
        target.encode("cp949", errors="strict")
        entry.update(
            {
                "translator": "Codex internal model",
                "review_status": "reviewed_once",
                "reviewer": "Codex internal model single review pass",
                "notes": "초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료",
            }
        )
        final_entries.append(entry)

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1135_all_translatable_slots_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "every translatable slot received exactly one Codex review pass",
        "newly_reviewed_range": [1, 298],
        "new_review_change_count": len(changes),
        "new_review_changes": changes,
        "file_translation_complete": True,
        "lookup_slots_preserved": [299, 356],
        "release_ready": False,
        "entries": final_entries,
    }
    out_path = (
        PROJECT
        / "packets"
        / "reviewed"
        / "1135_all_translatable_slots_reviewed_once.json"
    )
    out_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "draft_inputs": [str(DRAFT_PATH)],
        "output": str(out_path),
        "entry_count": len(final_entries),
        "review_passes_per_slot": 1,
        "newly_reviewed_slots": [1, 298],
        "new_review_change_count": len(changes),
        "checks": {
            "source_text_and_hash_match_catalog": True,
            "caret_token_order_preserved": True,
            "all_targets_strict_cp949": True,
            "no_kana_residue": True,
            "exactly_one_review_per_slot": True,
            "all_translatable_slots_covered": True,
            "lookup_slots_excluded": True,
            "lookup_range_299_356_preserved": True,
        },
        "output_sha256": hashlib.sha256(out_path.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1135_complete.json"
    audit_path.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                **audit,
                "audit_path": str(audit_path),
                "changes": changes,
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
