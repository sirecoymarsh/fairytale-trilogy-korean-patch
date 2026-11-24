from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    76: "나",
    77: "어떤 사람이었어? 얼굴은?",
    78: "그레텔",
    79: "얼굴은──별로 기억나지 않아. 무서워서…….^n미, 미안, 해…….",
    80: "나",
    81: "괜찮아. 무서웠지.",
    82: "그레텔",
    83: "으, 흐윽, 으으…….^n왠지 나를 보면서 계속 웃었던 건 기억나.^n이, 입이 기분 나쁘고 이상한 냄새가 났어…….",
    84: "그레텔",
    85: "나, 나는 그만하라고 했는데.^n아, 아프니까 그렇게 당기지 말라고…….^n웃기만 하고 말을 들어주지 않았어……!",
    86: "그레텔의 떨림이 맞잡은 손으로 전해진다.^n나는 온기가 전해지도록 손에 더 힘을 주었다.",
    87: "나",
    88: "무사해서 다행이야. 이제 괜찮아.^n──자, 숲을 빠져나간다.",
    89: "그레텔",
    90: "응…… 응……!",
    91: "나무들이 듬성듬성해지자,^n부드러운 햇살이 우리의 피부를 따뜻하게 했다.",
    92: "그레텔은 눈물 어린 눈으로 고개를 끄덕이며,^n그제야 온몸의 힘을 뺀 듯했다.",
    93: "나",
    94: "그나저나 무섭네.^n이상한 사람이 몰래 들어온 걸까.",
    95: "그레텔",
    96: "──의사 선생님이었어.",
    97: "나",
    98: "어……?",
    99: "그레텔",
    100: "아, 어, 아니야. 아니었을지도 몰라.^n하얀 옷을 입어서 의사 선생님인 줄 알았는데…….",
    101: "그레텔",
    102: "분명 아닐 거야.^n그, 그런 짓은 안 해, 의사 선생님은.^n……안 해.",
    103: "나",
    104: "………….",
    105: "내 머릿속에 아주 잠깐^n오늘 아침에 본 진찰실의 광경이 스쳐 지나갔다.",
    106: "그레텔은 의사 선생님을 믿는 걸까.^n그렇다면 그건 역시 내가 잘못 본 것이거나,^n아니면 그게 제대로 된 진찰이었을까──",
    107: "어느 쪽이든 잊는 게 좋겠다고 생각했다.",
    108: "나",
    109: "……그래도 조약돌이 있어서 다행이네.",
    110: "그레텔",
    111: "응.^n이쪽 손은 붙잡혀 있었지만,^n이쪽 손은 자유로워서 주머니에서 떨어뜨릴 수 있었어…….",
    112: "그레텔",
    113: "이렇게 따라가서 숲에서 돌아올 수도 있었고…….^n",
    114: "저, 정말 대단해, 헨젤 오빠는.^n",
    115: "오빠가 가르쳐 주지 않았다면 나는 그대로…….",
    116: "나",
    117: "……그레텔.",
    118: "나",
    119: "내가 대단한 게 아니야.^n내가 생각해 낸 것도 아니고…….^n그레텔도 정말 잘했어.",
    120: "그레텔",
    121: "……응.",
    122: "그레텔은 나를 올려다보며,^n오늘 처음으로 미소를 보였다.^n코끝은 빨갛지만 좋은 미소였다.",
    123: "나",
    124: "(진짜 헨젤과 그레텔도^n　이런 느낌이었을까.)",
    125: "우리가 온 길과 돌아갈 길을 알려 주는 조약돌은^n햇빛을 받아 반짝반짝 빛나고 있었다.",
    126: "나는 지나가던 간호사에게^n그레텔이 자리에 없다는 것과 함께 주운 돌이^n그녀가 간 곳을 가리키듯 떨어져 있다고 호소했다.",
    127: "그레텔이 정말 실종된 것이라면,^n돌을 따라가는 것보다 훨씬 올바른 행동이라고 생각했기 때문이다.",
    128: "간호사",
    129: "응, 응, 응.^n어머, 그래, 그래, 응. 그렇구나.",
    130: "간호사는 적어도 겉으로는^n내 이야기를 진지하게 들어 주었다.",
    131: "그리고 이야기를 전부 듣고 나자^n방긋 웃으며 믿음직한 어른 특유의 미소를 지었다.",
    132: "간호사",
    133: "괜찮아, 찾아볼 테니까.^n그렇게 쉽게 병원 밖으로 빠져나갈 수도 없을 테고,^n그럴 이유도 없을 테니──금방 찾을 거야.",
    134: "간호사",
    135: "　그레텔은, 그레텔이잖아.^n　주머니에 조약돌이 있으면 그런 행동을 하고 마는 거야.^n『성서』에 그렇게 적혀 있으니까.",
    136: "나",
    137: "아…… 그런, 건가요.",
    138: "부풀어 올랐던 위기감이 빠르게 쪼그라든다.",
    139: "나는 잠깐이나마 『큰일』이라고 느껴,^n간호사의 일을 방해하고 만 것이^n부끄러웠다.",
    140: "간호사가 말한 대로^n시간은 조금 걸렸지만,^n그레텔은 무사히 돌아왔다.",
    141: "마주쳤을 때 말을 걸었는데도,^n어딘가 멍한 채 모르는 사람을 보듯^n나를 바라본 것이 마음에 걸렸지만──",
    142: "주워들은 바에 따르면,^n환자가 『누구를 누구로 인식하는지』는^n상당히 변덕스러운 모양이다.",
    143: "그레텔이 나를 『오빠』라고 믿은 건^n그 조약돌을 주웠던 한때뿐이었다.^n그뿐인 일이다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1118.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1118_slots_00076_00143_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1118_slots_00076_00143_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
