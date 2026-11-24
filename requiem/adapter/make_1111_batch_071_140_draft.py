from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    71: "(어라, ……이거…….)",
    72: "가슴이 조여 오는 듯한 기분에,^n나는 몇 번이고 눈을 깜빡였다.^n──그것은 그리움이었다.",
    73: "머릿속 깊고 깊은 곳에 소중히 간직된 채 잠들어 있던 무언가가,^n꿈틀거리며 돌아누웠다.^n그런 느낌이 든다.",
    74: "그것은 그레텔이 나를 바라보며,^n떨리는 뺨에 미소를 띤 순간,^n한층 확실하게 몸을 움직였다.",
    75: "그레텔",
    76: "고마워, 오빠……──^n",
    77: "──아, 미, 미안……!",
    78: "나",
    79: "(──!　아…….)",
    80: "나는 크게 숨을 삼켰다.^n그레텔이 자신도 모르게 입에 담은 그 울림.",
    81: "──……빠.",
    82: "──오빠.",
    83: "천진한 목소리가 알 리 없는 기억 속에서 나를 불렀다.",
    84: "나는 길을 잃지 않도록^n작고도 작은 손을 꼭 잡고 있었다.",
    85: "혹은 쪼그려 앉아 눈을 맞추고,^n무언가를 타이르고 있었다.",
    86: "혹은 흐느껴 우는 머리를 쓰다듬으며,^n울다 지쳐 잠들 때까지 줄곧 곁에 있었다.",
    87: "그레텔",
    88: "오빠?　──가 아니었지.^n그러니까, 그러니까, 아, 아우…….",
    89: "그레텔이 말을 걸어서──라기보다^n뭐라고 불러야 할지 몰라 더듬는 목소리를 듣고,^n나는 정신을 차렸다.",
    90: "그레텔",
    91: "──괘, 괜찮……아요?^n머리, 아파요?",
    92: "나",
    93: "으…… 아니.^n아프지 않아.",
    94: "나는 어느새 머리 양옆에 대고 있던 손을 내렸다.",
    95: "안에서 넘쳐 나오는 것을 막으려 했던 걸까.^n아니면 차라리 내 손으로 긁어내려 했던 걸까.^n머리에 파고든 손톱 자국이 욱신욱신 아팠다.",
    96: "나",
    97: "(방금 그건 내 기억인가?)",
    98: "다시 떠올려 보려 했을 때는 『나 자신의 일』로서^n미칠 듯 나를 휩쓸고 농락하던 기억의 해일이,^n이미 『그런 장면을 보았다』는 정보로 가라앉아 있었다.",
    99: "꿈에서 깨어난 뒤,^n생생하게 나를 휘둘렀을 꿈이^n엉터리일 뿐인 환상의 조각이 되어 버리듯.",
    100: "하지만 그것만으로도 충분했다.^n그 기억은 내 과거를 말해 주었다.",
    101: "내게는 여동생이 있었다──",
    102: "나",
    103: "아무것도 아니야. 괜찮아.",
    104: "그레텔",
    105: "으…… 응.",
    106: "그레텔은 걱정스러운 듯 나를 바라본다.^n아직 붉은 눈은 우는 것조차 잊고,^n그저 한결같이 나를 걱정하고 있다.",
    107: "찌릿 하고 머릿속 깊은 곳이 아픈 것은,^n내 진짜 『여동생』도 가끔 이런 눈을 했기 때문일까.",
    108: "나",
    109: "그…… 너야말로 괜찮아?^n이제 진정됐어?",
    110: "그레텔",
    111: "으, 읏…….^n──괘, 괜찮아, 괜찮아.",
    112: "──괜찮아 보이지 않는다.^n흐트러지려는 숨을 삼키며 필사적으로 얼버무리고 있지만.",
    113: "나",
    114: "그래, 괜찮아.^n아무도 너를 버리지 않을 거야.",
    115: "그레텔",
    116: "──으, ……으으…….",
    117: "그레텔은 눈을 꼭 감았다.^n고여 있던 눈물방울이 굴러떨어진다.",
    118: "나",
    119: "(──아차.^n　방금 말은 절대 해선 안 되는 거였어.)",
    120: "내가 한 말은 사실이지만.^n이 『낙원』에는 그레텔의 부모 역할을 맡은 사람이 없으니,^n누가 그녀를 버릴 일도 없지만.",
    121: "『헨젤과 그레텔』의 내용을 믿고 있는^n　그레텔에게는 아무 의미도 없다.",
    122: "나",
    123: "아…… 아─…….^n그, 그러니까.",
    124: "나는 그레텔의 두 팔에 턱을 얹은 테디베어와^n함께 안긴 『성서』를 바라보았다.",
    125: "필사적으로 다시 일어서려던 그녀가 왜 상처받았는지,^n어떻게 하면 그 상처를 달랠 수 있는지 나는 알고 있다.",
    126: "그렇다면──",
    127: "나는 망설이며 입을 열었다.",
    128: "상심한 그레텔에게 나는…….",
    129: "『조약돌을 주우러 가자』고 말한다.",
    130: "　건넬 말을 찾지 못한다.",
    131: "나는 아무래도 『오빠』였던 모양이다.",
    132: "지금도 흐느낌을 죽이는 그레텔의 목소리를 듣고 있자니,^n점점 애달픈 기분이 든다.^n가슴이 괴로워 함께 울 것 같을 정도로.",
    133: "──차라리 나누면 돼.",
    134: "나",
    135: "『좋은 방법이 있어, 그레텔.』",
    136: "그렇게 말을 꺼낸 내 목소리에는 아까까지 없던 힘이 있었다.^n자신감에 찬 『오빠』의 목소리.",
    137: "그레텔",
    138: "네…….",
    139: "무언가를 느낀 것인지 그레텔이 고개를 들었다.",
    140: "나",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1111.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1111_slots_00071_00140_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1111_slots_00071_00140_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
