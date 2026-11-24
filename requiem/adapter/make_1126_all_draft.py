from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "어젯밤과는 다른 쪽으로 발길을 돌려 정원을 산책했다.",
    2: "오늘도 달이 아름다운 좋은 밤이다.^n형형색색의 식물과 다양한 풍경을 지닌 정원은 끝없이 넓어서,^n전체를 파악하려면 아직 한참은 걸릴 듯했다.",
    3: "나",
    4: "(응?)",
    5: "병동으로 돌아왔을 때, 나는 기묘한 광경을 목격했다.",
    6: "라푼젤이 사는 탑──^n꼭대기 층 창문에서 늘어뜨린 두 가닥의 머리카락을 꽉 붙잡고,^n탑의 벽을 오르는 사람이 있다.",
    7: "어제의 나처럼.",
    8: "나",
    9: "아……!",
    10: "그 사람은 대놓고 다리를 떨면서도,^n어떻게든 벽을 끝까지 올라갔다.^n라푼젤의 방 창문으로 굴러 들어가더니 사라졌다.",
    11: "얼굴은 보이지 않았지만,^n의사 선생님들과 비슷한 또래의 남자였던 것 같다.",
    12: "나",
    13: "(……저건)",
    14: "어젯밤 내 가슴에 매달렸던 라푼젤의 무게와,^n뜨거운 숨결을 떠올린다.",
    15: "밤에 창문으로 찾아오는 사람을 왕자님이라고 믿는 라푼젤은,^n그러니까 방금 굴러 들어간 남자도──",
    16: "나",
    17: "(──그만두자)",
    18: "나는 세차게 고개를 저으며,^n팔과 가슴에 남은 감촉을 잊으려 했다.",
    19: "내가 관여할 일이 아니다.^n나는 아무것도 보지 못했다.",
    20: "하지만 필사적인 모습으로 창문에 매달려 굴러 들어가던^n꼴사납게 버둥거리던 엉덩이와 다리라는 우스꽝스러운 광경은,^n좀처럼 머릿속에서 지워지지 않을 것 같았다.",
    21: "나에게 밀쳐져 슬픈 듯 눈을 크게 떴던^n어젯밤 라푼젤의 표정도──",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")


def main() -> int:
    rows: dict[int, dict] = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1126.gsc" and item.get("slot") in TARGETS:
                rows[int(item["slot"])] = item
    if set(rows) != set(TARGETS):
        raise SystemExit("catalog mismatch")

    entries = []
    for index in sorted(TARGETS):
        source = str(rows[index]["source_text"])
        target = TARGETS[index]
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entries.append({
            "uid": rows[index]["uid"],
            "source_text": source,
            "source_raw_sha256": rows[index]["source_raw_sha256"],
            "target_text": target,
            "translator": "Codex internal model draft",
            "review_status": "draft_pending_single_review",
            "notes": "초벌 번역; 1차 검수 전",
        })

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1126_slots_00001_00021_draft",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 0,
        "release_ready": False,
        "entries": entries,
    }
    out = PROJECT / "packets" / "drafts" / "1126_slots_00001_00021_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "output": str(out),
        "entries": len(entries),
        "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper(),
    }, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
