from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "비틀비틀 걷다가^n오딜의 방 앞을 지나쳤지만,^n나는 그대로 지나가기로 했다.",
    2: "또 그런 식으로 놀림받는다고 생각하니 내키지 않는다.^n그 심술궂은 붉은 눈동자는 내 불행을 즐기는 것 같다.",
    3: "그런 생각을 하며 빠른 걸음으로^n흑백의 문 앞을 지나던 때였다.",
    4: "등 뒤에서 문이 열리는 소리가 났다.",
    5: "반사적으로 돌아본 것은,^n머리 한구석에서 아직 오딜을 생각했기 때문이겠지.^n마음을 놓을 수 없고 빈틈을 보이기 싫은 상대라고.",
    6: "???",
    7: "………….",
    8: "하지만 내 눈에 들어온 것은──",
    9: "???",
    10: "……후아암.",
    11: "입을 크게 벌리고 방심한 하품을 한 번.",
    12: "잠이 덜 깬 눈을 어린아이처럼 벅벅 문지른다.^n손을 뗐을 때는 눈꼬리가 온통 빨개져 있었다.",
    13: "긴 속눈썹이 소리라도 날 듯 깜빡거리지만,^n그래도 멍한 눈동자 그대로,^n그녀는 천천히 걷기 시작한다.",
    14: "비틀비틀, 흔들흔들,^n넓은 복도를 지그재그로 걷던 발걸음은,^n한 번 넘어질 뻔했다가 가까스로 균형을 되찾았다.",
    15: "그 모습이 복도 저편으로 사라졌을 때,^n나는 병아리의 아장걸음을 지켜보는 듯한 기분이^n되어 있었음을 깨달았다.",
    16: "나",
    17: "(……방금 그 아이는…….)",
    18: "아름다운 여자아이였다고 생각한다.^n부드러워 보이는 금빛 머리카락과 그 빛에 감싸인 하얀 얼굴,^n달빛을 가둔 듯한 금빛 눈동자까지.",
    19: "나",
    20: "(아…….)",
    21: "나는 그제야,^n그녀가 오딜과 똑같은 얼굴이었음을 깨달았다.",
    22: "똑같은 이목구비, 피부와 머리색, 키.^n앞머리 모양과 눈동자 색, 드레스만 다르다.",
    23: "──그런데도 두 사람은 너무나 닮지 않았다.",
    24: "나는 노크도 대충 하고 오딜의 방에 들어갔다.",
    25: "오딜",
    26: "──뭐야.^n대답도 기다리지 않고 무례하긴.",
    27: "가짜 호숫가에도 완전히 『밤』이 찾아왔다.^n어둠을 두르고 더욱 섬뜩해진 나무 중 하나에,^n오딜이 기대어 있었다.",
    28: "핏빛 눈동자는 어두운 밤에도 요염하고 불길하다.^n언젠가 본 적이 있는지, 나는 커다란 붉은 보름달을 떠올렸다.",
    29: "──역시 똑같이 생겼는데도 닮지 않았다.",
    30: "나",
    31: "저기, 방금 방을 나간 아이는…….",
    32: "오딜",
    33: "아, 오데트 말이지.^n매일 이 시간에 외출해.",
    34: "나",
    35: "오데트.^n오데트라면 그 백조 말이야?",
    36: "나는 주변을 둘러보았다.^n낮에 소개받은 『오데트』는 없다.^n호수 곳곳에 있던 백조 장식물도 한 마리 남김없이 사라졌다.",
    37: "오딜",
    38: "말했잖아.^n저 녀석들은 백조가 되는 저주를 받았다고.^n밤 동안만 저주가 약해져서 인간으로 돌아올 수 있어.",
    39: "나",
    40: "그럴 리가.",
    41: "오딜",
    42: "말도 안 돼?　저주란 원래 그런 거잖아.^n불만이 있으면 저주를 건 우리 아버지께 말해.^n너도 돼지 같은 것으로 변해 버릴지 모르지만.",
    43: "여러 의미로 웃지 못할 농담을 하고,^n오딜은 입가를 비틀었다.",
    44: "『우리 아버지』라는 것은,^n『백조의 호수』의 악역 오딜의 아버지인^n　부엉이 악마 로트바르트를 말하는 것이겠지.",
    45: "물론 그런 인물도 그런 저주도 없다.^n이 방의 주인인 오데트와 오딜이 그렇게 믿을 뿐이다.",
    46: "오데트는 낮 동안 어딘가에 숨어 있다가,^n밤이 되면 백조를 치우고 나타난다──^n그렇게 『백조의 호수』를 성립시키는 것이다.",
    47: "나는 인사도 대충 하고 방을 나왔다.^n오딜의 얼굴을 보는 동안 기억 속 오데트의 얼굴과^n겹쳐 가는 것이 왠지 견딜 수 없이 아깝게 느껴졌다.",
    48: "후아암 하고 무방비하게 하품하던 옆얼굴과,^n금빛 머리카락을 흔들며 비틀비틀 작아져 가던 뒷모습이,^n아직도 눈 안쪽에 남아 있다.",
    49: "그것이 사라지기 전에 다시 한번 그녀를 보고 싶었다.",
    50: "어떻게든 오데트를 찾아 따라잡을 수 있었던 것은,^n그녀의 걸음이 느린 덕분이다.",
    51: "정원에서 꽃을 밟지 않으려 치맛자락을 들고 살금살금 걸으며,^n수면의 보름달을 쫓아 개울을 따라갔다.",
    52: "그 불안한 발걸음은 마침내 호숫가에서 멈췄다.",
    53: "오데트",
    54: "………….",
    55: "오데트는 우두커니 선 채,^n호수 한가운데 떠 있는 보름달을 가만히 바라보고 있다.",
    56: "산들바람이 불고 초목이 소곤소곤 이야기를 나눴다.^n검푸른 거울 같은 수면에서 그녀의 모습도 잔물결에 찢어진다.",
    57: "──오데트는 무엇을 하려고 여기까지 온 걸까.",
    58: "　두 사람의 방에는 가짜 호수가 있고,^n『백조의 호수』 무대로는 충분했다.^n　왜 굳이 여기까지 올 필요가 있었을까.",
    59: "나",
    60: "저, 저기…….",
    61: "오데트",
    62: "후에……?",
    63: "마음을 다잡고 말을 걸자,^n오데트는 조금 얼빠진 소리를 내며 뒤돌아보았다.",
    64: "달빛을 닮은 눈동자가 나를 보았다.",
    65: "호수에 떠 있는 일그러진 보름달보다,^n훨씬 다정하고 부드러운 투명한 눈빛이었다.",
    66: "나를 비추며 눈을 깜빡이는 모습은 천진해서,^n그러고 보니,^n무엇을 보여 줘도 신기해하는 아기의 눈과 닮았다.",
    67: "나",
    68: "저기──안녕.",
    69: "오데트",
    70: "안녕.",
    71: "어색하게 인사하자,^n그녀는 활짝 미소 지으며 답했다.",
    72: "나보다 조금 나이가 많아 보이는데도,^n붙임성이 좋고 경계심이라고는 전혀 없는 모습이다.",
    73: "오데트",
    74: "좋은 밤이네. 달이 동그랗고──^n바람도 기분 좋아.",
    75: "오데트는 눈을 감고,^n아름다운 음악에 귀를 기울이듯 말했다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1112.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1112_slots_00001_00075_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1112_slots_00001_00075_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
