from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    71: "나",
    72: "(──그레텔?)",
    73: "나는 왠지 기세에 눌려 뒷걸음질할 뻔했다.",
    74: "이야기에 다음으로 필요한 물건인 빵을 가져온 게^n그렇게 기쁜 걸까.",
    75: "나",
    76: "자, 자. 이거 조약돌 대신 쓸 수 없을까?^n조금씩 떼어 떨어뜨리며 가면…….^n",
    77: "──으앗!",
    78: "덥석, 그레텔이 빵을 움켜쥔다.",
    79: "그레텔",
    80: "──!",
    81: "다음 순간에는 내 손에서 쏙 뽑아 갔다.",
    82: "그것은 받아 간다기보다^n낚아챈다고밖에는 표현할 수 없는 기세로──",
    83: "나",
    84: "왜, 왜 그래, 그레텔.^n",
    85: "아…… 아아아아아아!?",
    86: "그레텔",
    87: "……움냠. 꿀꺽꿀꺽꿀꺽꿀꺽…….",
    88: "나",
    89: "그, 그레텔…….",
    90: "빼앗은 빵을 당연하다는 듯 베어 무는 그레텔을^n나는 멍하니 지켜보았다.",
    91: "그레텔",
    92: "우물우물우물우물, 꿀꺽꿀꺽꿀꺽.^n냠냠냠냠, 냠냠냠냠.",
    93: "두 손으로 받쳐 든 빵을 위에서부터 베어 먹어 가는 모습이며,^n그에 따라 양쪽 볼이 엄청난 기세로 부풀어 올라,^n믿을 수 없을 만큼 부드럽게 우물거리며 변형되는 모습이며──",
    94: "다람쥐 같다고 하면 다람쥐에게 실례일 듯하다.",
    95: "볼주머니가 이제 한계 아닐까 걱정하기 시작할 무렵,^n그레텔은 일단 빵에서 입을 뗐다.",
    96: "그레텔",
    97: "우물, 우물, 꿀꺽…… 꿀꺽!",
    98: "우물우물 몇 번 턱과 볼을 움직이는 동안,^n탐스럽던 볼주머니는 눈에 띄게 줄어든다.",
    99: "꼴깍, 목을 울렸을 무렵에는 완전히 원래대로다.",
    100: "나",
    101: "(──어떤 구조인 걸까…….)",
    102: "처음에는 직원의 호의로 받은 귀한 빵이^n눈 깜짝할 사이 사라지는 것을 슬프게 지켜봤지만,^n점점 호기심이 앞서기 시작했다.",
    103: "나",
    104: "……맛있어?",
    105: "그레텔",
    106: "응!^n",
    107: "후아아아아…….^n",
    108: "──냠냠냠냠냠냠냠냠.",
    109: "그레텔은 아주 깊고──정말 행복한 듯한 한숨을 내쉬고,^n다시 빵을 베어 문다.",
    110: "절반 남은 빵이 우적우적 깎여 나가고,^n앳된 볼이 다시 울퉁불퉁하게 부풀어 오른다.",
    111: "그래, 다람쥐가 아니라 연필깎이 같아.",
    112: "그레텔",
    113: "냠뉴냠뉴냠뉴냠뉴냠뉴냠뉴냠뉴냠뉴…….",
    114: "나",
    115: "(……그나저나 정말 맛있게 먹네.)",
    116: "그 눈동자는 기쁨으로 반짝이면서도 어딘가 멍해서,^n빵을 향한 집착과 집중이 전해지는 듯하다.",
    117: "이윽고 그레텔이 아쉬운 듯^n마지막 한 조각을 입에 던져 넣을 무렵에는,^n나는 완전히 『뭐, 됐나』 하는 기분이 되어 있었다.",
    118: "그레텔",
    119: "응, 응, 응, 응…… 냠꿀꺽!^n",
    120: "후아아아아…….",
    121: "그레텔",
    122: "──────헉!",
    123: "마지막 한입을 삼키고 만족스럽게 숨을 돌린 뒤,^n그제야 그레텔은^n자기 실수를 깨달은 듯했다.",
    124: "그레텔",
    125: "아…… 아…….",
    126: "입가에 빵 조각을 붙인 채,^n자신의 텅 빈 손을 빤히 들여다본 뒤,^n슬쩍 눈을 치켜뜨고 나를 살폈다.",
    127: "나",
    128: "──잘 먹었습니다는?",
    129: "반사적으로 내 입에서 나온 것은 그런 말이었다.^n혼낼 생각도 없었고 예절을 가르칠 생각도 없었는데.",
    130: "그레텔",
    131: "자…… 자, 잘 먹었, 습니다…….^n……오, 오빠, 고마워…….",
    132: "그레텔",
    133: "미, 미안, 해…….",
    134: "나",
    135: "괜찮아, 신경 쓰지 마.^n배가 고팠구나.^n──저녁밥 안 먹었어?",
    136: "그레텔",
    137: "머, 먹었어…….",
    138: "나",
    139: "부족했어?",
    140: "그레텔",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1124.gsc" and item.get("slot") in TARGETS:
                rows[int(item["slot"])] = item
    if set(rows) != set(TARGETS):
        raise SystemExit("catalog mismatch")
    entries = []
    for index in sorted(TARGETS):
        source, target = str(rows[index]["source_text"]), TARGETS[index]
        if source.count("^n") != target.count("^n"):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": rows[index]["uid"], "source_text": source, "source_raw_sha256": rows[index]["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 전"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1124_slots_00071_00140_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1124_slots_00071_00140_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
