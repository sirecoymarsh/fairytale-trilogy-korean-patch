from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "내 방──그 하얀 방으로 돌아갈 때 확인해 보니,^n역시 문은 밖에서만 잠글 수 있는 구조였다.",
    2: "안의 환자가 도망치지 못하게?^n아니면 환자가 난동을 부릴 때를 대비한 걸까.",
    3: "나",
    4: "(뭐, 『병실』이니까.^n　게다가 정신병원의.)",
    5: "막 깨어났을 때는 왠지 두려웠던 하얀 방이지만,^n이렇게 정체를 알고 나서 보니 여러모로 납득이 간다.",
    6: "여전히 쓸데없는 것이 너무 없어서^n어쩐지 마음이 놓이지 않지만.",
    7: "나",
    8: "(……맞다.^n　입원했다면 나름대로 직접 준비한 물건이^n　있지 않을까.)",
    9: "나는 잠옷과 수건, 시간을 보낼 책이나 퍼즐^n같은 것을 떠올리며 방의 가구를 조사했다.",
    10: "나",
    11: "(………….)",
    12: "나",
    13: "(──아무것도 없나.)",
    14: "붙박이 옷장에는 옷걸이만 걸려 있었다.^n세면실에는 이 『낙원』이 마련해 준^n칫솔과 수건, 컵 같은 것이 준비되어 있다.",
    15: "마치 호텔 같다.^n",
    16: "그리고 나는 아무것도 없이 훌쩍 떠나온 여행자 같다.",
    17: "하지만 마지막으로 살펴본 책상 서랍에서는,^n뜻밖의 것이 발견되었다.",
    18: "나",
    19: "(──스케치북과 크레용?)",
    20: "내 물건일까가 아니라,^n전에 살던 사람의 물건이겠다고 생각했다.",
    21: "내 물건이라면 무언가 떠오를 법한데^n전혀 감이 오지 않았고,^n──무엇보다도.",
    22: "스케치북의 내용에서 뭐랄까,^n조금 섬뜩한 느낌을 받았기 때문이다.",
    49: "표지를 넘기자 검은 크레용 선이 눈에 들어왔다.",
    50: "커튼과 침대, 책상과 의자──",
    51: "서투르고 단순한 선으로 그려진 것은^n아마 이 방의 스케치다.",
    52: "나",
    53: "(이렇게 보아도 어딘가 쓸쓸하고 허전한 방이네.)",
    54: "표지를 넘기자 검은 크레용 선이 눈에 들어왔다.",
    55: "서투르고 단순한 선으로 그려진 것은^n아마 이 방의 스케치다.",
    56: "커튼과 침대, 책상과 의자──^n그리고 몇 가지 가구.",
    57: "나",
    58: "(어라……?)",
    59: "실제로는 이 방에 없을 물건도 덧그려져 있다.^n아무것도 없는 방이라서,^n쓸쓸한 마음에 더한 걸까.",
    60: "나",
    61: "(그러게.^n　무언가 조금만 더 있으면 편안할 텐데.)",
    62: "나는 그런 생각을 하며,^n누군가가 상상의 세계에서 꾸며 준 가구를 바라본다.",
    63: "그러자 기묘하게 가슴이 술렁였다.",
    64: "나",
    65: "(──이거, 왠지 어디선가 본 기억이 있는 듯한…….)",
    66: "머리가 조여 오는 듯해 눈을 꽉 감았다.^n더는 도저히 보고 있을 수 없다.",
    67: "하지만 이런 상태가 된다는 것은,^n내게 중요한 기억과 이어져 있을지도 모른다.^n기분이 조금 진정되면 나중에 다시 한번 보자.",
    68: "그런 생각을 하며 나는 페이지를 넘겼다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1108.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1108_translatable_batch_a_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1108_translatable_batch_a_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "slots": sorted(TARGETS), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
