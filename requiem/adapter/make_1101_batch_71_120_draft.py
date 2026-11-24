from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")


TARGETS = {
    71: "???",
    72: "어머! 어머나, 이렇게 정중하게 인사해 주시다니.^n",
    73: "전나무가 말을 했다는 건,^n분명 이제 슬슬 크리스마스가 온다는 뜻이겠죠.",
    74: "나",
    75: "──나는 전나무가 아니야.",
    76: "???",
    77: "그래요?^n그럼 대체 당신은 누구죠?",
    78: "나",
    79: "………….",
    80: "곧장 대답하려 했지만 입에서 숨만 새어 나오는 것이 느껴졌다.^n이게 무슨 일일까.^n──답을 찾을 수 없다.",
    81: "???",
    82: "왜 그래요, 또 입을 다물고.^n북극곰도 이것보다는 말을 잘하겠어요.^n",
    83: "──아, 아아!　혹시…….",
    84: "???",
    85: "알아요!　알고 있으니 괜찮아요.^n이제 와서 이런 일로 설교를 듣고 싶지는 않아요.^n그래요, 이름을 듣고 싶을 때는 먼저 자신부터.",
    86: "???",
    87: "나는 앨리스예요.^n처음 뵙겠어요. 안녕하신가요.",
    88: "드레스 자락을 들어 올리고 온몸을 낮춰,^n소녀는 어쩐지 거창한 인사를 했다.",
    89: "나",
    90: "앨리스…….",
    91: "　이렇게 꼭 어울리는 이름도 드물겠다고 생각했다.^n　내 이름은 떠오르지 않는데도,^n『이상한 나라의 앨리스』라는 이야기는 어렴풋이 안다.",
    92: "치마의 트럼프 무늬, 줄무늬 체셔 고양이 같은 목도리.^n어쩐지 그럴듯한 차림이다.^n무엇보다 한 손에 들린 책의 제목은──",
    93: "나",
    94: "너도 『이상한 나라의 앨리스』를 좋아하는구나.",
    95: "앨리스",
    96: "──?^n그건 내 별명이에요.^n다들 나를 그렇게 불러요.",
    97: "나",
    98: "어…….^n하지만 그 책은.",
    99: "앨리스",
    100: "이거요?　이건 나의 『성경』.^n나에 관한 이야기가 쓰여 있어요.^n내가 어떤 소녀이고 앞으로 어떤 일을 겪게 될지.",
    101: "나",
    102: "………….",
    103: "　그 순간 나는 어째서인지,^n『이 아이는 이야기 속에서 빠져나온 앨리스야!』^n　라고 믿어 버렸다.",
    104: "　아니, 아니, 그럴 리가.^n　여기서는 이렇게 생각해야겠지.^n",
    105: "『정말 가엾은 아이구나.』 하고.",
    106: "앨리스",
    107: "그래서, 당신은 누구죠?",
    108: "나",
    109: "어……, 그러니까…….",
    110: "나",
    111: "──미안. 모르겠어.",
    112: "앨리스",
    113: "어머!　모른다고요?^n그건──참 안됐네요…….",
    114: "앨리스는 손으로 입가를 가리며 우아하게 놀라더니, 나를 유심히 바라보았다.",
    115: "이럴 수가.^n오히려 내가 『가엾은 아이』처럼 보이잖아.",
    116: "앨리스",
    117: "모른다…… 자신이 누군지 모른다…….^n그런 일이 있을 수 있나.^n요즘은 장미도 고양이도 자기가 장미다, 고양이다 하고 시끄러울 정도인데.",
    118: "나",
    119: "저기…….",
    120: "앨리스",
}


def main() -> int:
    rows: dict[int, dict[str, object]] = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1101.gsc" and item.get("slot") in TARGETS:
                rows[int(item["slot"])] = item
    if set(rows) != set(TARGETS):
        raise SystemExit("catalog slot mismatch")
    entries = []
    for slot in sorted(TARGETS):
        source = str(rows[slot]["source_text"])
        target = TARGETS[slot]
        if source.count("^n") != target.count("^n"):
            raise SystemExit(f"caret count mismatch at slot {slot}")
        target.encode("cp949", errors="strict")
        entries.append({
            "uid": rows[slot]["uid"],
            "source_text": source,
            "source_raw_sha256": rows[slot]["source_raw_sha256"],
            "target_text": target,
            "translator": "Codex internal model draft",
            "review_status": "draft_pending_single_review",
            "notes": "초벌 번역; 한 차례 검수 전",
        })
    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "opening_1101_slots_00071_00120_draft",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 0,
        "release_ready": False,
        "entries": entries,
    }
    out = PROJECT / "packets" / "drafts" / "1101_slots_00071_00120_draft.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
