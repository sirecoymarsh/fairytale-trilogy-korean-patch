from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "정신없다든가, 말이 통하지 않는다든가, 피곤하다든가,^n만날 때마다 뼈저리게 느끼면서도^n왜 나는 또 찾아온 걸까.",
    2: "빨강과 파랑으로 복잡한 무늬가 그려진 문을 두드리려다,^n나는 잠시 생각한다.",
    3: "──재미있으니까. 질리지 않으니까. 심심하지 않으니까.^n그 밖의 답을 찾을 수 있을 리 없었다.",
    4: "나",
    5: "(아…….^n　이 문양, 낯이 익다 했더니.^n　마술 같은 데서 자주 보는 카드 뒷면 무늬인가.)",
    6: "앨리스",
    7: "네에.",
    8: "앨리스의 병실에는 먼저 온 손님이 있는 듯했다.",
    9: "나",
    10: "어, 이케노 씨.",
    11: "이케노",
    12: "쉬잇.",
    13: "케이크 같은 화장대 앞에 놓인^n버섯 같은 스툴에 앉은 이케노 씨는,^n입 앞에 집게손가락을 세웠다.",
    14: "이케노",
    15: "나는 이케노가 아니야. ──지금은.",
    16: "앨리스",
    17: "소개할게요. 애벌레 씨예요.",
    18: "앨리스",
    19: "온통 이해할 수 없는 말씀만 하시면서 잘난 체하고,^n걸핏하면 화내고, 말투는 퉁명스럽고, 심술궂고,^n신경에 거슬릴 때도 있지만──",
    20: "앨리스",
    21: "물담배를 너무 많이 피워서 어쩔 수 없다고,^n난 요즘 그렇게 생각하기로 했어요.",
    22: "나",
    23: "그…… 그래…….",
    24: "『소개』의 대부분이 불평불만인 건^n　아무리 생각해도 드문 경우인 듯하다.",
    25: "아작아작 소리가 났다.^n보니 물담배 대신인 듯한 담배 모양 초콜릿을^n이케노 씨가 진지한 얼굴로 깨물고 있었다.",
    26: "나",
    27: "저기, 진찰 중이신가요?^n그럼 저는 나중에 다시 올게요.",
    28: "작은 목소리로 말을 걸자,^n이케노 씨는 입을 오므린 채 우물우물 대답한다.",
    29: "이케노",
    30: "아니, 땡땡이치──연구하고 있을 뿐이야.^n앨리스는 워낙 온갖 등장인물과 대화하는 이야기라,^n누군가 상대해 주지 않으면 심심해하거든.",
    31: "나",
    32: "그, 그렇군요.",
    33: "나",
    34: "(땡땡이라고 말하려 했지.)",
    35: "앨리스",
    36: "그리고 있죠, 애벌레 씨.^n이 잿빛 옷을 입은 이쪽 분은, 이쪽 분은──",
    37: "앨리스",
    38: "──곤란하네요. 소개할 이름이 없어요.^n구멍에 떨어질 때 잃어버린 거였던가요?",
    39: "나",
    40: "잊어버린 거야.",
    41: "앨리스",
    42: "잊어버렸대요.^n그리고 이래 봬도 회색 펠리컨 씨가 아니라,^n사람이래요.",
    43: "나",
    44: "(『이래 봬도』라니?)",
    45: "이케노",
    46: "사람이라고? 그런 것치고는 꽤 작구나.^n게다가 이름을 잊다니, 들어 본 적도 없어.",
    47: "　평소와는 다른 말투였다. 그 나름의 『애벌레』 말투겠지.^n『작다』는 것도 애벌레가 본 사람의 크기를 말하는 것이고──",
    48: "그건 알고 있었지만 순간,^n작아진 우리가 작은 버섯 위에서 이야기하는 듯한^n불안한 착각에 사로잡혔다.",
    49: "축척이 이상한 이 방 때문이라고 생각한다.",
    50: "앨리스",
    51: "이름뿐 아니라 가족도, 기르는 고양이의 이름도,^n어디에서 왔는지도, 어디로 가야 하는지도,^n지금까지의 추억도──전부 잃어버렸대요.",
    52: "이케노",
    53: "말도 안 돼.^n그렇게 모든 걸 잊어버리다니.",
    54: "심술궂은 『애벌레』를 연기하면서도,^n이케노 씨는 히죽히죽 웃고 있다.",
    55: "앨리스",
    56: "하지만 정말 그런걸요!^n",
    57: "그렇죠?",
    58: "나",
    59: "으, 응.",
    60: "앨리스",
    61: "……당신도 나처럼 몇 번인가 변해 버린 거군요.^n아니, 이렇게 모든 걸 잊고 있으니,^n분명 비교할 수 없을 만큼 많이 변했을 거예요.",
    62: "나",
    63: "변했다니?",
    64: "앨리스",
    65: "구멍에 떨어진 뒤로 나는^n커졌다가 작아졌다가 하며 너무 불안정해서,^n10분도 같은 모습으로 있을 수 없었어요.",
    66: "앨리스",
    67: "그럴 때마다 조금씩 내가 변해 버렸다고 생각해요.^n오늘 아침의 나와 지금의 나는 달라요.^n오늘 아침에는 내가 더 제대로 되어 있었는걸요!",
    68: "나",
    69: "(어제부터 이런 느낌이었지만…….)",
    70: "앨리스",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1117.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1117_slots_00001_00070_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1117_slots_00001_00070_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
