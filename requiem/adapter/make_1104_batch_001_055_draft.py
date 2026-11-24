from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "양쪽으로 열리는 문은 좌우가 검은색과 흰색으로 나뉘어 칠해져 있었다.^n검은 바탕에는 흰색으로, 흰 바탕에는 검은색으로 깃털 같은 무늬가 그려져 있다.",
    2: "왼쪽에는^n오딜",
    3: "오른쪽에는^n오데트^n라고 적힌 팻말이 걸려 있었다.",
    4: "노크하자 아무래도 철문이었던 모양인지,^n둔탁하고 무거운 소리가 울렸다.",
    5: "???",
    6: "──누구야?",
    7: "누구냐고.^n당연한 질문인데도 나는 완전히 기가 눌리고 말았다.^n그도 그럴 게, 뭐라고 해도 대답할 방법이 없으니까.",
    8: "나",
    9: "저, 저기요!^n조금 물어보고 싶은 게, 있는데요…….",
    10: "기어들어 가는 목소리로 그렇게 말을 건네는 것이 고작이었다.^n하지만 이름을 물었는데 대답하지 않는 사람은 너무 수상해서,^n보통은 경계하지 않을까.",
    11: "???",
    12: "──들어오지 그래?^n문을 사이에 두고 말하기 귀찮아.",
    13: "잔뜩 긴장했는데도 너무 쉽게 허락을 받아,^n나는 깊이 숨을 내쉬었다.",
    14: "넓다──너무나도 넓은 방이었다.^n등 뒤에서 닫힌 문소리가 깊은 울림으로 메아리칠 만큼.",
    15: "복도에서 본 구조와 달리 이 방은 바닥이 둥글고,^n천장도 돔 형태로 불룩 솟아 있었다.",
    16: "그 둥근 방 중앙에는 똑같이 원형인 넓은 장소가 있다.^n아니, 이건 광장이 아니라…….",
    17: "나",
    18: "(호수?)",
    19: "그런 인상이었다.^n물론 진짜는 아니다.",
    20: "물빛, 남색, 군청색.^n비치는 새틴과 빛나는 실크, 반짝이와 스팽글까지.^n엄청난 양의 천이 뒤엉켜 넓은 호수 표면을 표현하고 있다.",
    21: "천 하나하나는 고급스러워 보이고 아름다운데,^n셀 수 없이 얽혀 어지럽게 소용돌이치는 모습은^n탁한 물을 떠올리게 해, 빠지면 살아나지 못할 것만 같다.",
    22: "그 호숫가에는 검은 나무 장식물이 늘어서 있다.^n뒤틀린 가지를 어색하게 뻗은 실루엣은 몹시 불길해서,^n탄식이나 비명 같은 말만 떠올랐다.",
    23: "　이 흉측한 나무들은 아무래도 진열대인 듯,^n　하이힐과 목걸이, 숄 등이 걸려 있지만,^n『여자가 저주로 나무가 된 것』처럼밖에 보이지 않는다.",
    24: "호수와 물가, 나무 사이에 드문드문 흰 것이 보인다.^n자세히 살펴보니 백조 모양의 장식물이다.",
    25: "하나하나는 잘 만들어진 아름다운 백조지만,^n이 풍경 여기저기에 흩어져 꼼짝하지 않는 모습은,^n쓸쓸하고 또 어쩔 수 없이 섬뜩했다.",
    26: "어두운 숲속의 음울한 호수 풍경.^n전부 가짜인데, 어째서 이런 장소를 만든 걸까.",
    27: "유일하게 눈을 달래 줄 만한 것은,^n천장에서 호수 위로 매달린 커다란 새장이었다.^n금빛 우리의 섬세한 광채가 이 풍경 속에서는 눈부시다.",
    28: "하지만 왜 이런 것이 있지?^n새가 아니라 사람을 가둘 법한 크기다.^n아래에서는 덮어 둔 천에 가려 안이 보이지 않지만.",
    29: "???",
    30: "뭘 그렇게 두리번거려.^n묻고 싶은 게 있다며?",
    31: "영문을 알 수 없는 풍경을 둘러보고 있자니,^n어디선가 목소리가 들려왔다.^n아마 들어오라고 재촉해 준 사람일 것이다.",
    32: "목소리의 주인은 그 여운이 가시기도 전에^n나무 사이에서 모습을 드러냈다.",
    33: "금빛 머리카락이 공기를 머금고 부드럽게 퍼진다.^n반짝이며 부드러운 빛이 일렁여,^n흐린 하늘이 갑자기 갈라지고 햇살이 비친 듯했다.",
    34: "하얀 피부도 반듯한 이목구비도 무척 아름다운 사람이었다.^n다만 나를 보며 가늘어진 붉은 눈동자는 어딘가 너무 날카로워 무섭다.^n사나운 짐승처럼 빈틈이 없는 느낌이다.",
    35: "앞머리에 가려진 다른 한쪽 눈도 마찬가지로,^n불길한 루비 같은 빛을 띠고 있을까.",
    36: "???",
    37: "……처음 보는 얼굴이네.^n게다가──뭔지 알 수 없는 차림새야.^n회색에다 수수하고. 칙칙해 보여.",
    38: "초면인 나를 당당히 깔보며 피식 웃는다.^n화가 나지는 않았다.^n그런 말을 들어도 어쩔 수 없다고 생각했고──게다가 어쩐지.",
    39: "살짝 벌어진 입술 끝을 치켜올린 그 표정은,^n흐린 풍경 속에서 돋보여 아름답고 멋있으며,^n너무나도 잘 어울렸으니까.",
    40: "???",
    41: "뭐야. 무슨 말이라도 해 보지그래.^n아까 문 너머에서 이러쿵저러쿵 지저귀고 있었으니,^n말을 못 하는 건 아니잖아.",
    42: "???",
    43: "뭐, 말을 할 수 있다고 해도,^n누구냐고 묻는데 대답하지 않는 무례한 녀석인걸.^n──그래서, 넌 누구야?",
    44: "나",
    45: "아, 아아…….",
    46: "이 풍경과 그녀 자체에,^n턱 아래를 간질이는 듯한 목소리에,^n완전히 압도되었던 나는 그제야 정신을 차렸다.",
    47: "나",
    48: "저기, 미안해요.^n저, 저는 그게…… 이름을 댈 수가 없어요.^n이름이 없어서. 떠올릴 수 없어서…….",
    49: "???",
    50: "뭐?　기억이 안 나?^n",
    51: "──흐응, 그래.",
    52: "놀란 것은 아주 잠깐이었다.^n다음 순간에는 메뚜기를 가지고 노는 고양이 같은 표정이 되었다.^n내 불안은 분명 그녀에게 좋은 장난감이겠지.",
    53: "???",
    54: "그거 참 안됐네.^n상상도 못 하겠지만, 분명 불편하겠지.",
    55: "　똑같은 말인데도 앨리스와는 정반대인 듯한^n『안됐네』를 입에 담고,^n　그녀는 호숫가를 걷기 시작했다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1104.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1104_slots_00001_00055_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1104_slots_00001_00055_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
