from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "도서관은 내가 있던 병동을 나와 정원을 가로질러,^n한참을 계속 걸어간 곳에 있었다.^n산책하기에 딱 좋은 거리일지도 모른다.",
    2: "마주친 어른에게 길을 물었는데,^n그중 몇 명은 벌써 내 증상을 알고 있었다.",
    3: "어른 A",
    4: "큰일이네.^n동화 증후군에 기억 상실까지 걸리다니.^n어느 쪽부터 치료해야 하나.",
    5: "나",
    6: "폐를 끼쳐 죄송합니다…….",
    7: "어른 A",
    8: "아니야, 신경 쓰지 마.^n좀처럼 없는 증례라 모두 오히려 기뻐하고 있어.",
    9: "어른 B",
    10: "이름──^n둘 다 떠오르지 않니?",
    11: "나",
    12: "둘 다요?",
    13: "어른 B",
    14: "진짜 이름과 임시 이름 말이야.",
    15: "나",
    16: "──둘 다 모르겠어요.",
    17: "어른 B",
    18: "다른 환자도 자신의 진짜 이름은 잊었지만,^n동화 속 이름만은 절대로 잊지 않아.^n새로운 자신을 좋아하니까 이름은 보물인 셈이지.",
    19: "어른 B",
    20: "그런데 너는 둘 다 잃어버린 거니.^n그건 참 곤란하겠구나…….",
    21: "나",
    22: "폐를 끼쳐 죄송합니다…….",
    23: "이렇게 큰일이라느니 곤란하다느니 하는 말을 들으니,^n당사자인 나보다 어른들이^n더 진지하게 고민하는 것 같아 미안해진다.",
    24: "나는 동정받을 때마다 연신 고개를 숙이고,^n걸음을 재촉해 달아나듯 도서관으로 향했다.",
    25: "나",
    26: "와아…….",
    27: "나는 크게 숨을 들이마셨다.",
    28: "도서관은 아름답고 넓었으며,^n오래된 책에서 흔히 나는 초콜릿 같은 달콤한 냄새가 났다.",
    29: "1층과 지하, 두 층에 걸쳐^n높은 책장이 빽빽이 놓여 있고,^n어느 책장에나 수많은 책이 꽂혀 있다.",
    30: "천천히 둘러보았지만 아무래도 1층은^n사전과 지도, 옛말로 쓰인 책자와 외국어 자료 같은^n어려운 책뿐이라 내게는 볼일이 없을 것 같다.",
    31: "지하에는 조금 더 가벼운 책이 많은 듯했다.^n계단을 내려간 정면 책장에는,^n낯익은 아동 문학 제목이 빼곡히 늘어서 있다.",
    32: "한 차례 책을 다 읽고 나서야 나는 퍼뜩 정신을 차렸다.^n──상당히 빠져 버렸는데 지금은 몇 시일까?",
    33: "꼬르륵 하고 배꼽시계가 울렸지만,^n깨어난 뒤 『약』 말고는 아무것도 먹지 않았으니^n전혀 참고가 되지 않는다.",
    34: "나",
    35: "(그나저나 그림책은 정말 오랜만에 읽었네.)",
    36: "마지막으로 읽은 책 한 권을 돌려놓으며 자연스럽게 생각했다.^n기억은 없지만 그렇게 생각했다는 건,^n아마 실제로도 그렇겠지.",
    37: "『이상한 나라의 앨리스』 『헨젤과 그레텔』^n『백조의 호수』 『라푼젤』 『눈의 여왕』──",
    38: "모두 기본 줄거리는 알고 있었지만,^n군데군데 흐릿하고 빠진 장면도 많았다.",
    39: "이번에 다시 읽으며 빈틈을 채웠고 새로 발견한 것도 있으니,^n기분 전환으로는 대성공이었다고 생각한다.",
    40: "그림책을 읽는 데도 뜻밖의 즐거움이 있었지만,^n이 도서관 자체가 무척 편안했다.^n──차라리 이곳에서 살고 싶을 정도로.",
    41: "나",
    42: "(뭐, 앞으로도 자주 와야지.)",
    43: "나는 아쉬움을 뒤로하고 도서관을 나섰다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1109.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1109_all_translatable_slots_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1109_all_translatable_slots_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
