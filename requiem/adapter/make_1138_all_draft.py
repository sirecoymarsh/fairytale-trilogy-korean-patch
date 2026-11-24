from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
TARGETS = {
    1: "나",
    2: "안녕, 그레텔. 기분은 어때?",
    3: "또 반쯤 울면서 담요를 뒤집어쓴^n모습을 상상했지만, 그러지는 않았다.",
    4: "그레텔",
    5: "오빠…….",
    6: "뒤돌아 내 모습을 발견하자,^n그레텔은 조금 안도한 듯 이쪽으로 다가왔다.",
    7: "안색은 그리 좋지 않고,^n표정도 어두워 보였지만,^n울거나 허둥대는 기색은 없다.",
    8: "나",
    9: "괜찮아?",
    10: "그레텔",
    11: "……응. 조금 무섭지만…….",
    12: "담요를 뒤집어쓰지 않고 끝자락만 쥐는 데 그치고 있다.^n『조금 무서운』 정도라서일까.",
    13: "그레텔",
    14: "그런데 무섭다기보다 이상하다는 느낌이야.^n그러니까…… 괜찮아.",
    15: "나",
    16: "이상해?",
    17: "그레텔",
    18: "──응.",
    19: "나",
    20: "무서우면 억지로 떠올리지 않아도 되지만,^n그때 그레텔은 뭔가 봤어?",
    21: "그레텔",
    22: "그때…….",
    23: "나",
    24: "화덕에서 새까맣게 탄 시체가 나왔을 때.",
    25: "그레텔",
    26: "………….",
    27: "그레텔은 살며시 시선을 피했다.^n떳떳하지 못하다거나 얼버무리고 싶다거나 하는 기색은 없었다.",
    28: "그레텔 자신도 본 것 때문에 당황하고 있다.^n무엇을 봤는지 모르니 설명할 수 없다──^n그런 인상이었다.",
    29: "나",
    30: "(어쨌든 말해 줄 것 같지는 않네.)",
    31: "나",
    32: "뭐, 생각보다 괜찮아 보여서 다행이야.^n오늘은 일찍 자고 잊는 편이 좋아.",
    33: "그레텔에게 등을 돌리고 방을 나서려던 순간.",
    34: "그레텔",
    35: "저기…… 그건…….^n그건 뭐였을까.",
    36: "그레텔이 가냘프게 중얼거리는 소리가 들렸다.",
    37: "나는 고개만 돌려 뒤를 보았다.^n그레텔은 곁에 두었던 인형을 끌어당기며^n기억을 더듬는 듯했다.",
    38: "그레텔",
    39: "나…… 내가 본 건…….^n──앨리스와는 다른 거야.",
    40: "나",
    41: "그렇구나…….",
    42: "앨리스가 본 『새까맣게 탄 사람의 시체』는 보지 않았다.^n대신 훨씬 기묘한 것을 보았다.^n그런 뜻일까.",
    43: "나",
    44: "고마워, 그레텔.^n잘 자.",
    45: "그레텔",
    46: "………….",
    47: "그레텔은 봉제인형의 손을 잡은 채^n깊이 생각에 잠긴 듯,^n내 인사에도 반응하지 않았다.",
}


def main() -> int:
    expected = set(range(1, 48))
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1138.gsc" and int(item.get("slot", -1)) in expected:
                rows[int(item["slot"])] = item
    if set(rows) != expected or set(TARGETS) != expected:
        raise SystemExit("coverage mismatch")
    entries = []
    for slot in sorted(expected):
        row = rows[slot]
        source = str(row["source_text"])
        target = TARGETS[slot]
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {slot}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": row["uid"], "source_text": source, "source_raw_sha256": row["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 전"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1138_slots_00001_00047_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    path = PROJECT / "packets" / "drafts" / "1138_slots_00001_00047_draft.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "entries": len(entries), "output": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
