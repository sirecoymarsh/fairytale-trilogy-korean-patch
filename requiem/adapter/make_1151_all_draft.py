from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
TARGETS = {
    1: "방으로 돌아오자마자 저녁 식사가 들어왔다.",
    2: "호박 수프와 우유죽,^n그리고 정체를 알 수 없는 분홍색 액체.^n걸쭉하게 혀에 들러붙는 듯한, 지나치게 단 음료다.",
    3: "어른",
    4: "오랜만에 하는 식사니까,^n배가 놀라지 않을 메뉴란다.^n내일 점심부터는 평범한 식사가 나올 거야.",
    5: "나",
    6: "아…… 네.",
    7: "내가 몹시 실망한 얼굴을 했던 모양이다.^n다정하게 타이르는 말을 듣자 얼굴이 달아오르는 게 느껴졌다.",
    8: "약이 약답지 않았으니,^n식사도 병원식답지 않을지 모른다고^n마음 한구석으로 기대했던 것이다.",
    9: "그런 메뉴였으니 식사는 금세 끝나 버렸다.",
    10: "나",
    11: "(──심심하네.)",
    12: "이 방에는 시계가 없지만,^n목욕이나 소등 시간까지는 꽤 남은 듯하다.",
    13: "나는 망설임 없이 나가기로 했다.^n낮에 이야기한 『환자들』과 다시 한번 이야기해 보고 싶다.",
}


def main() -> int:
    expected = set(range(1, 14))
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1151.gsc" and int(item.get("slot", -1)) in expected:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1151_slots_00001_00013_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    path = PROJECT / "packets" / "drafts" / "1151_slots_00001_00013_draft.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "entries": len(entries), "output": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
