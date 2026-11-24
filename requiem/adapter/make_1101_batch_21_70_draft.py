from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")


TARGETS = {
    21: "끼익, 하고 몸을 일으키자 그 아래에서 침대가 삐걱거렸다.",
    22: "몸을 일으켜 바라봐도 세계는 여전히 하얬다.^n하지만 눈을 가늘게 뜨고 하나하나 윤곽을 확인하자,^n그것은 의미가 있는 흰빛임을 알 수 있었다.",
    23: "하얀 벽, 천장, 문.^n하얀 침대와 시트와 담요, 하얀 책상과 하얀 의자.^n하얀 빛이 넘쳐흐르는 창과 하얀 커튼.",
    24: "먼지도 얼룩도 보이지 않는다.^n청소가 잘된, 쓸데없는 물건 하나 없는 깔끔한 방이다.^n──그런데도 이 불편함은 대체 뭘까?",
    25: "분명, 그래, 그거다.^n너무나도 화려한 꿈을 꾸고 있었으니, 역시나^n이 반듯한 흰빛이 나를 나무라는 듯한 기분이 든 것이다.",
    26: "그렇게 필사적으로 자신을 타일렀지만,^n돌기 시작한 머릿속은 또 다른 의문과^n그 답을 떠올리고 말았다.",
    27: "──그런데, 여기는 어디일까?",
    28: "모르겠다.^n하지만 마치── 같다.",
    29: "가장 중요한 곳에 버젓이 벌레 먹은 구멍이 뚫려 있다.^n그런데도 팽팽히 펴져 있던 등줄기로 오싹한 감각이 내달렸다.",
    30: "──무섭다.^n──새하얗고, 깨끗하고, 안전해 보이는 이 방이 어째선지 두렵다.",
    31: "하얀 침대에서 일어나 하얀 슬리퍼를 꿰어 신었다.^n하얀 문손잡이를 돌려 하얀 문을 열었다.",
    32: "잠겨 있지는 않다──^n애초에 잠글 수도 없는 모양이다.",
    33: "문 너머의 광경을 보자 절로 안도의 한숨이 새어 나왔다.",
    34: "역시 처음 방은 짓궂은 장난이었던 모양이다.^n그렇게 모든 것이 하얗고 거의 아무것도 없던 방이라니──",
    35: "구불구불 이어진 복도에는^n당연하다는 듯 색이 있었다.^n푹신한 붉은 융단, 크림빛 벽.",
    36: "벽에는 마치 아이의 낙서 같은 무늬가──^n아니, 아마 정말로 아이가 한 낙서겠지.^n손이 닿는 높이까지 온 힘을 다해 크레용을 문지른 흔적이 있다.",
    37: "제멋대로 그어진 그것은 ‘얼룩’일지도 모르지만,^n흰색을 너무 많이 본 눈에는 위안이었다.",
    38: "다음으로 천장에서 늘어진 따뜻한 색의 불빛이 눈에 들어왔다.^n샹들리에인 줄 알았지만 자세히 보니 아닌 것도 같다.",
    39: "꽃과 과일, 물고기와 조개 모양의 얇은 판들이 이어져,^n불빛을 받아 반짝반짝 빛나고 있었다.^n희미한 바람에 흔들리며 찰랑찰랑 소리를 낸다.",
    40: "아, 마치 그거다.^n뭐라고 부르더라, 아기 침대 위에 매달려서^n빙글빙글 돌아가는 그것.",
    41: "지금 가슴에 치민 것은 그리움일까.^n아기 침대에 누운 채 질리지도 않고 바라보았던 기억,^n그건 분명 누구에게나 있는 기억이고…….",
    42: "그래, 누구에게나 있는 기억…….",
    43: "………….",
    44: "──뭘까.^n왜 심장이 쿵쿵 뛰는 걸까.",
    45: "조금만 더. 조금만 더 있으면.^n무언가 좋지 않은 곳에 다다를 것만 같은…….",
    46: "???",
    47: "기다려!　기다려, 토끼야!^n",
    48: "──꺄악!",
    49: "고요에 익숙해진 귀에는 아플 만큼 다급한 목소리.^n무언가 생각할 새도 없이 쿵 하고 부딪혀 앞으로 고꾸라졌다.",
    50: "으앗, 하고 입에서 새어 나온 소리를 제 귀로 듣고,^n내가 이런 목소리를 내는구나, 하고 생각했다.",
    51: "???",
    52: "뭐, 뭐, 뭐야……?",
    53: "부딪혀 온 누군가도 내 몸에 튕겨 나가^n두세 걸음 뒤로 물러났다.",
    54: "가벼운 감촉이었다.^n달고 또 단, 일부러 그런 듯 지독히 단 과자 냄새가 났다.",
    55: "???",
    56: "미안해요, 너무 서두르다 보니.^n다친 데는 없나요?",
    57: "노래하듯 운율을 타는 목소리.^n선명한 색채에 눈을 빼앗겨 바로 말이 나오지 않았다.",
    58: "꽃처럼, 공작처럼, 보석처럼.^n눈이 즐거운 것만 떠오르게 하는 화려한 드레스.^n마치 꿈속에서 튀어나온 듯한 차림이다.",
    59: "유난히 반짝이는, 무서울 만큼 아름다운 눈동자.^n생각하고 느낀 모든 것이 하나하나 별이 되어^n빽빽하게 서로를 밀어내며 빛나는 것만 같다.",
    60: "그 신비한 빛깔의 눈으로 머리끝부터 발끝까지 찬찬히 바라보자,^n어쩐지 부끄러워져 피부가 따끔따끔 달아올랐다.^n내가 이곳에 있다는 사실을 싫어도 깨닫게 된다.",
    61: "마치 ‘나’라는 존재가^n그녀의 시선이 닿는 순간 태어나고 있는 듯한──^n그런 기분이다.",
    62: "???",
    63: "어머나, 무슨 일이죠? 대답이 없다니.",
    64: "???",
    65: "내가 전나무한테라도 말을 걸고 있는 걸까요.^n하긴 크리스마스도 아닌데 초대받을 리 없으니,^n대답할 리도 없겠죠.",
    66: "나",
    67: "아…….",
    68: "그제야 겨우 정신을 차렸다.^n부딪힌 상대를 내버려 두다니 실례잖아.",
    69: "나",
    70: "괘……, 괜찮아.^n나, 나야말로 미안해.",
}


def main() -> int:
    rows: dict[int, dict[str, object]] = {}
    catalog = PROJECT / "catalog" / "scenario_catalog.jsonl"
    with catalog.open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1101.gsc" and item.get("slot") in TARGETS:
                rows[int(item["slot"])] = item
    if set(rows) != set(TARGETS):
        raise SystemExit(f"catalog slot mismatch: {sorted(set(TARGETS) - set(rows))}")

    entries: list[dict[str, object]] = []
    for slot in sorted(TARGETS):
        source = str(rows[slot]["source_text"])
        target = TARGETS[slot]
        if source.count("^n") != target.count("^n"):
            raise SystemExit(f"caret count mismatch at slot {slot}")
        target.encode("cp949", errors="strict")
        entries.append(
            {
                "uid": rows[slot]["uid"],
                "source_text": source,
                "source_raw_sha256": rows[slot]["source_raw_sha256"],
                "target_text": target,
                "translator": "Codex internal model draft",
                "review_status": "draft_pending_single_review",
                "notes": "초벌 번역; 한 차례 검수 전",
            }
        )
    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "opening_1101_slots_00021_00070_draft",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 0,
        "release_ready": False,
        "entries": entries,
    }
    out = PROJECT / "packets" / "drafts" / "1101_slots_00021_00070_draft.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
