from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    71: "내가 앨리스와 만나 느낀 『가엾다』는 감정을,^n지금 이 사람도 나에게 느끼는 걸까.^n그렇게 생각하니 무턱대고 반발하고 싶어졌다.",
    72: "그렇게 생각하면서도 말을 삼킨 건 정말 아무 이유도 없었다.^n──기억은 없지만 나는 늘 그렇게 해 온 것 같다.",
    73: "의사",
    74: "이야, 말귀를 잘 알아듣는 아이라 다행이네.",
    75: "의사 선생님은 내가 얌전히 다음 말을 기다리는 것을 보고^n무척 안심한 모양이다.^n몸이 간질거리는 듯한 칭찬을 건네고 이야기를 이었다.",
    76: "의사",
    77: "이곳에 있는 아이들은^n모두 똑같은 병을 앓고 있단다.^n──『동화 증후군』.",
    78: "나",
    79: "페어리테일 신드롬…….",
    80: "이번 말은 곱씹듯 입안에서 굴려 보아도^n기억에 없는 듯해 무슨 뜻인지 알 수 없었다.",
    81: "그보다 이 말을 꺼낼 때 보인,^n의사 선생님의 뜸을 들이는 듯한 말투가 신경 쓰였다.",
    82: "의사",
    83: "이건 말이지, 놀랍게도,^n자신을 동화 속 등장인물이라고^n굳게 믿어 버리는 병이란다.",
    84: "나",
    85: "(아, 그렇구나.^n　그래서 모두 그런 느낌이었던 거네.)",
    86: "의사",
    87: "………….",
    88: "나",
    89: "………….",
    90: "의사",
    91: "희귀해서 좀처럼 볼 수 없는 병이지만.^n이곳에는 그런 희귀한 환자만 모여 있단다.^n애초에 그런 곳이니까.",
    92: "몸을 불쑥 내밀며 덧붙이는 의사 선생님을 보고,^n여기서는 조금 더 놀랐어야 했다는 것을 깨달았다.^n──막 깨어난 탓인지 아직 요령을 잘 모르겠다.",
    93: "의사 선생님은 의사 선생님대로,^n크흠 하고 헛기침을 한 번 하고 이야기를 이었다.",
    94: "의사",
    95: "너도 만났으려나?^n모두 저마다 어울리는 옷을 입고,^n그럴듯하게 행동하니 금방 알 수 있을 거야.",
    96: "의사",
    97: "『이상한 나라의 앨리스』의 앨리스.",
    98: "의사",
    99: "『헨젤과 그레텔』의 그레텔.",
    100: "의사",
    101: "『백조의 호수』의 오데트와 오딜.",
    102: "의사",
    103: "『라푼젤』의 라푼젤.",
    104: "의사",
    105: "그리고 『눈의 여왕』의 게르다──",
    106: "의사",
    107: "현재 입원한 환자는 그 아이들뿐이야.",
    108: "한 명씩,^n만났던 여자아이들의 얼굴을 떠올리며 나는 고개를 끄덕였다.",
    109: "나",
    110: "(아, 오데트만 만나지 못했네.^n　오딜은 만났고 그 백조 장식물이^n　오데트라는 말이 사실이면 만난 셈이겠지만.)",
    111: "의사",
    112: "모두 원래는 평범하고 어디에나 있는,^n시시한 여자아이들이란다.",
    113: "의사",
    114: "그런데도──아니, 그렇기 때문에?^n자신을 이야기의 주인공이라고 굳게 믿게 된 거지.",
    115: "나",
    116: "그렇다면…….",
    117: "나는 나도 모르게 입을 열었다.^n마침 말을 멈춘 의사 선생님에게^n맞장구를 치는 모양새가 되었다.",
    118: "나",
    119: "앨리스는 진짜 앨리스가 아니라고요?^n그레텔도 오딜도,^n라푼젤도 게르다도──",
    120: "나",
    121: "모두 자신을^n이야기에서 나온 공주님이라고 굳게 믿는^n그냥 사람이라는 건가요?",
    122: "나",
    123: "(아니, 게르다만은 조금 달랐나.)",
    124: "문간에 서서 이쪽을 가만히 바라보던 모습을 떠올린다.^n이름을 말할 때도 오히려 게르다라는 울림에^n위화감을 느끼는 듯했다──",
    125: "하지만 의사 선생님은 무겁고 심각한 표정으로 고개를 끄덕였다.^n증상만 다를 뿐,^n그건 그것대로 병이라는 걸까?",
    126: "의사",
    127: "뭐, 공주인지는 각 이야기 나름이지만.^n요컨대 재미없는 결론은 그런 셈이지.",
    128: "의사",
    129: "그 아이들이 저마다 손에 든 책은 보았니?^n그것이 각자가 속한 이야기──^n그 아이들에게는 『성서』란다.",
    130: "나",
    131: "성서…….",
    132: "그래, 앨리스도 그렇게 말했다.^n잠시 생각해 뜻을 떠올리고는,^n참 거창한 말을 쓴다고 생각하고 말았다.",
    133: "게다가 그 생각이 얼굴에 드러난 모양이다.",
    134: "의사",
    135: "뭐, 원전이 희곡이든 민담이든,^n그저 어린이용 그림책에 붙이기에는 거창한 이름이지만,^n이해 못 할 일도 아니지.",
    136: "의사",
    137: "그만큼 그 아이들에게는 소중한 책이라는 뜻이야.^n무엇보다 그 책은 그 아이들 자신이니까.",
    138: "의사",
    139: "자신이 누구고 무엇을 위해 태어났는지,^n하늘의 신을 대신해 계시를 내려 준다는──^n결국 복음서 같은 것이니까.",
    140: "나",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1107.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1107_slots_00071_00140_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1107_slots_00071_00140_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
