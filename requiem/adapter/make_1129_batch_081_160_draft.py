from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    81: "이것도 자네 눈에는 무엇으로 보이지?^n곰 인형?^n──아니야. 포르말린에 담근 개구리야.",
    82: "의사",
    83: "정말 자네들은 금세 착각하곤 하지.^n불쾌한 것을 귀여운 것으로, 잔혹한 일을 행복한 것으로,^n시시한 것을 즐거운 것으로.",
    84: "게르다",
    85: "거짓말이에요, 인형이잖아요!^n저를 환자로 몰아가려는 거죠?",
    86: "의사",
    87: "이야기를 듣게.^n잘 생각해 봐. 치료하지 않고 돌려보내면,^n망상이 점점 부풀어 큰일이 날 수 있어.",
    88: "의사",
    89: "망상에 사로잡혀 터무니없는 일──^n살인이든 강도든,^n자기 이야기에 맞는다고 생각하면 쉽게 저질러 버리지.",
    90: "의사",
    91: "의붓아버지라는 늑대의 배를 가른 빨간 모자,^n수면제를 대량으로 먹고 영원히 깨어나지 못한 잠자는 숲속의 공주,^n제 발을 잘라 버린 『빨간 구두』의 카렌──",
    92: "의사",
    93: "카이를 빼앗은 눈의 여왕으로 여기고,^n짝사랑하던 상대의 약혼자를 냉동실에 가둔 게르다도,^n이 아저씨는 알고 있단다.",
    94: "게르다",
    95: "……읏. ……!",
    96: "이따금 몸을 내밀어 끼어들려는 게르다의 말을 가로막고,^n폭포처럼 쏟아지는 일방적인 의사 선생님의 연설이었다.",
    97: "의사",
    98: "……이건 무서운 병이란다.",
    99: "마지막에는 다시 부드러운 말투로 돌아와 덧붙인다.",
    100: "게르다는 새하얗게 질린 얼굴로, 포기한 듯 다시 의자에 앉았다.",
    101: "의사",
    102: "알겠나?",
    103: "게르다",
    104: "──네. 말대꾸해서 죄송합니다.",
    105: "이마를 짚은 채 게르다는 무미건조하게 중얼거린다.^n완전히 꺾여 대꾸할 말도 찾지 못해 사과할 수밖에 없지만,^n그래도 반발심은 뿌리 깊게 남은 듯했다.",
    106: "게르다",
    107: "그럼 이만 실례하겠습니다.",
    108: "게르다는 고개를 숙이고 일어선다.",
    109: "방 안을 채우던 긴장이 풀리고,^n곁에 있던 간호사가 크게 한숨을 내쉬는 모습이,^n모니터 너머로도 보였다.",
    110: "어서 게르다를 내보내고,^n원래의 화기애애한 분위기로 돌아가고 싶다는^n속마음이 들려오는 듯하다.",
    111: "이상하게도 정작 게르다의 얼굴에도^n말싸움에서 진 분함이 아니라,^n방에서 나갈 수 있다는 안도감이 떠오른 듯했다.",
    112: "생각해 보면 이렇게 정면으로 달려들어도^n어른들이 순순히 응할 리 없다.^n영리한 게르다라면 그 정도는 잘 알고 있을 터.",
    113: "방금의 말다툼은 어쩌면,^n다른 무언가를 감추기 위한 한 편의 연극이었을지도 모른다──^n──왠지 나는 그렇게 생각했다.",
    114: "──아니나 다를까.",
    115: "의사",
    116: "잠깐, 게르다 양.",
    117: "게르다",
    118: "……!",
    119: "붙잡힌 순간,^n게르다는 아까보다 훨씬 궁지에 몰린 표정을 지었다.",
    120: "의사",
    121: "자네, 아무래도 오늘 열이 나는 것 같지 않나.",
    122: "게르다",
    123: "……그런가요? 저는 아무렇지도 않은데요.^n잠이 부족해서일지도 몰라요.^n경험상 잠들면 나아요.",
    124: "의사",
    125: "음, 그렇게 가벼운 열의 오름세가 아닌 것 같은데.^n뭐, 괜찮아. 약을 놓아 줄 테니까.",
    126: "게르다",
    127: "──!^n아뇨, 괜찮습니다.^n",
    128: "그런 건…… 없어도…….",
    129: "강한 어조로 거절하려 했지만,^n어딘가에서는 헛된 저항이라고 포기하고 있었던 것이겠지.",
    130: "다가온 간호사에게 팔을 붙잡히자,^n게르다는 체념한 듯 눈을 감았다.",
    131: "간호사",
    132: "그럼 진찰대 위에서 네발로 엎드려 주세~요.",
    133: "게르다",
    134: "……읏…….",
    135: "간호사",
    136: "미안해요, 조금만 더 기다려 주세요.^n금방 끝날 테니까요.",
    137: "게르다",
    138: "윽……읏…….",
    139: "간호사가 아기를 달래듯 말하자,^n게르다는 입가를 떨었다.",
    140: "진찰대 위로 끌어 올려 네발로 엎드리게 하고,^n치마를 집어 올리고 속옷을 내리고──",
    141: "거기까지는 간호사의 손놀림이 척척 빨랐는데,^n주사를 준비하는 단계에 이르자 갑자기 굼떠진 듯했다.",
    142: "주사기를 떨어뜨리고, 약을 잘못 꺼내고,^n약을 넣었다 싶더니 쓰면 안 되는 주사기였고.",
    143: "의사",
    144: "마키무라 양도 참 안 되겠구먼.^n주사 한 대 놓는 데 시간을 얼마나 쓰는 건가.",
    145: "간호사",
    146: "죄송해요, 선생님.^n조금만, 조금만 더요.",
    147: "실수를 연발하는 간호사와 질린 의사 선생님의^n늘어지는 대화를 들으며, 게르다는^n아침 햇살 아래 맨엉덩이를 치켜든 채 떨 수밖에 없다.",
    148: "갓 껍질을 벗긴 삶은 달걀처럼 매끈하고 둥근 엉덩이가^n옅게 붉어져, 부끄러운 듯 꼼지락거린다.",
    149: "게르다",
    150: "……빨리해 주세요.",
    151: "들끓는 열뿐 아니라,^n얼음처럼 차가운 기운도 느껴지는 목소리였다.",
    152: "게르다의 분노는,^n자기에게 이런 자세를 강요하는 의사 선생님들은 물론,^n속절없이 부끄러워하는 자기 자신에게도 향한 듯했다.",
    153: "간호사",
    154: "미안해요.^n제가 덜렁이라서…….",
    155: "게르다",
    156: "애초에 먹는 약으로는 안 되나요?",
    157: "의사",
    158: "역시 직장으로 흡수하는 편이 약효가 좋거든.",
    159: "간호사",
    160: "미안해요. 이런 자세는 부끄럽죠.^n개처럼 네발로 엎드려 엉덩이를 다 드러내고.^n이 아침부터 여자애가 취할 자세는 아니죠.",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")


def main() -> int:
    rows: dict[int, dict] = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1129.gsc" and item.get("slot") in TARGETS:
                rows[int(item["slot"])] = item
    if set(rows) != set(TARGETS):
        raise SystemExit("catalog mismatch")
    entries = []
    for index in sorted(TARGETS):
        source = str(rows[index]["source_text"])
        target = TARGETS[index]
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entries.append({
            "uid": rows[index]["uid"],
            "source_text": source,
            "source_raw_sha256": rows[index]["source_raw_sha256"],
            "target_text": target,
            "translator": "Codex internal model draft",
            "review_status": "draft_pending_single_review",
            "notes": "초벌 번역; 1차 검수 전",
        })
    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1129_slots_00081_00160_draft",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 0,
        "release_ready": False,
        "entries": entries,
    }
    out = PROJECT / "packets" / "drafts" / "1129_slots_00081_00160_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "output": str(out),
        "entries": len(entries),
        "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper(),
    }, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
