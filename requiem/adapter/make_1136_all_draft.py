from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")

TARGETS = {
    1: "모퉁이를 막 돌려던 순간,^n그 너머에 모여 있는 흰 가운들을 발견하고,^n나는 반사적으로 걸음을 멈췄다.",
    2: "모두 똑같이 곤란한 표정으로 무언가를 속삭이고 있다.^n이렇게 되면 누가 의사 선생님이고 간호사 선생님이며,^n그 밖의 직원인지 나는 구별할 수 없다.",
    3: "이케노",
    4: "어째서…… 어쩌다 그런 일이…….^n대체 누가 한 짓이란 말인가.",
    5: "이케노 씨만은 여전히 알아보기 쉽다.^n몹시 초췌한 표정 탓인지,^n평소와 인상이 꽤 달라 보였지만.",
    6: "직원",
    7: "저 아이들 중 누군가겠지.^n우리가 그런 짓을 할 리가 없어.^n그럴 이유도 없고.",
    8: "직원",
    9: "어떻게 하죠?",
    10: "직원",
    11: "내버려 두는 수밖에 없겠죠.",
    12: "이케노",
    13: "하지만 그러면 그 아이가 편히 눈감지 못해!",
    14: "이케노",
    15: "불에 타 죽다니, 얼마나 괴로웠을까,^n얼마나 뜨거웠을까…….",
    16: "직원",
    17: "자자, 불에 타 죽었다고 단정할 순 없어요, 이케노 씨.^n제 생각엔 죽은 뒤에 태워졌을 가능성이 더 큽니다.",
    18: "직원",
    19: "오히려 언제 죽어도 이상하지 않은 상태였잖아요.^n그 영 미심쩍은 모습을 보면요.^n화장하는 수고를 덜었다고 생각하면 되죠, 그렇죠?",
    20: "이케노",
    21: "…………. 저는 무덤을 만들고 오겠습니다.",
    22: "이케노 씨는 견디지 못한 듯 눈가를 가리고 그 자리를 떠났다.",
    23: "나도,^n엿듣고 있다는 걸 들키면 곤란하다는 사실을 깨닫고,^n그곳을 떠나기로 했다.",
    24: "나",
    25: "(역시 누군가 죽었어.^n여기 사람들은 어떻게든 덮으려 하고 있어.)",
    26: "나는 생각보다 동요하지 않는 모양이었다.^n모두 머리 한구석으로 예상했던 일인지도 모른다.",
    27: "나",
    28: "(──그래도 저런 이케노 씨는 처음 봤어.)",
    29: "언제나 싱글벙글 기분 좋아 보이던 얼굴을 일그러뜨리고,^n눈을 새빨갛게 물들이고──떠날 때는 정말로 울고 있었던 것 같다.",
    30: "대체 사라져 버린 시체는 누구의 것이었을까.",
}


def main() -> int:
    expected = set(range(1, 31))
    if set(TARGETS) != expected:
        raise SystemExit("target coverage mismatch")

    rows: dict[int, dict] = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1136.gsc" and int(item.get("slot", -1)) in expected:
                rows[int(item["slot"])] = item
    if set(rows) != expected:
        raise SystemExit("catalog coverage mismatch")

    entries = []
    for slot in sorted(expected):
        row = rows[slot]
        source = str(row["source_text"])
        target = TARGETS[slot]
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret token mismatch at slot {slot}")
        target.encode("cp949", errors="strict")
        entries.append(
            {
                "uid": row["uid"],
                "source_text": source,
                "source_raw_sha256": row["source_raw_sha256"],
                "target_text": target,
                "translator": "Codex internal model draft",
                "review_status": "draft_pending_single_review",
                "notes": "초벌 번역; 1차 검수 전",
            }
        )

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1136_slots_00001_00030_draft",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 0,
        "release_ready": False,
        "entries": entries,
    }
    out_path = PROJECT / "packets" / "drafts" / "1136_slots_00001_00030_draft.json"
    out_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "output": str(out_path),
                "entries": len(entries),
                "sha256": hashlib.sha256(out_path.read_bytes()).hexdigest().upper(),
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
