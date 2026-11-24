from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    61: "게르다",
    62: "마음이 편치 않아야 할 풍경인데도,^n어째서 이렇게 익숙해져 버린 걸까, 나는.",
    63: "게르다는 혼잣말처럼 중얼거린다.",
    64: "──그녀 안에서는 무슨 일이 벌어지고 있는 걸까.^n역시 『동화 증후군』에서 깨어나기 시작한 걸까.",
    65: "하지만 그걸 묻기는 망설여졌다.^n분명 그런 건 의사 선생님이 해 줄 테니까.",
    66: "나",
    67: "그…… 낮에 네가 했던 말이 마음에 걸렸어.",
    68: "게르다",
    69: "낮에 내가?",
    70: "나",
    71: "　응.^n『무엇을 하고 싶었는지』를 떠올려야 한다고.^n　강한 소망이 있다면 망각과 싸워야 한다고 했잖아.",
    72: "게르다",
    73: "──응.^n그 말이 맞다고 생각해.",
    74: "나",
    75: "내게는 그런 게^n있었는지조차 알 수 없지만.^n게르다에게는 분명 있지?",
    76: "게르다",
    77: "어…….",
    78: "나",
    79: "그런 느낌이 들었어.^n네게 강한 소망이 있으니까 그렇게 생각하는 거라고.",
    80: "게르다는 눈을 감고 내 말을 곱씹듯 고개를 끄덕였다.",
    81: "게르다",
    82: "응, 맞아.^n아니──나도 너와 크게 다르지 않아.",
    83: "게르다",
    84: "내게는 『가야 할 곳』이 있었을 거야.",
    85: "게르다는 소리가 날 만큼 두 주먹을 세게 움켜쥐었다.",
    86: "나",
    87: "『가야 할 곳』──",
    88: "게르다",
    89: "──내게는 있어, 있었을 거야.^n이대로는 안 돼, 무언가 부족해.^n그렇게 생각하면서도 떠오르지 않아.",
    90: "나",
    91: "………….",
    92: "그건 『게르다』로서 품은 것일까.^n아니면 『게르다』의 가면을 쓰기 전, 본래의 그녀가 품은 것일까?",
    93: "장미꽃을──",
    94: "가지고 있다.",
    95: "가지고 있지 않다.",
    96: "어느 쪽이든 그녀가 게르다인 이상,^n나는 그 굳게 닫힌 기억을 풀어낼 실마리를 알고 있었다.",
    97: "이건 『눈의 여왕』 책에서 본 전개다.",
    98: "얼어붙은 마음으로 실종된 카이를 찾아 길을 떠난 게르다.^n처음 만난 노파는 게르다를 마음에 들어 해,^n영원히 곁에 두고자 기억을 지워 버린다.",
    99: "게르다가 기억을 되찾은 계기는^n카이와의 유대를 상징하며,^n그 때문에 노파가 잊게 했던 『장미』의 존재였다.",
    100: "게르다",
    101: "……!^n그건…….",
    102: "내가 주머니에서 꺼낸 장미를 보고,^n게르다는 눈을 크게 떴다.",
    103: "무심코 뻗은 듯한 손이^n닿기 직전에 무례하다는 걸 깨닫고 멈춘다.",
    104: "나는 반쯤 포기한 듯 손가락을 오므리는 그 손에^n장미 줄기를 쥐여 주었다.",
    105: "게르다",
    106: "아…….",
    107: "눈의 결정 같은 게르다의 눈동자가 흔들렸다.^n장미가 떨리는 건 그것을 든 게르다의 손이 떠는 바람에^n그 진동이 전해져서일까.",
    108: "게르다",
    109: "『장미꽃, 향기로운 골짜기에──』",
    110: "나",
    111: "……!",
    112: "가쁜 숨을 거듭 내쉬는 게르다의 입술 사이에서 갑자기^n그런 한 구절이 흘러나왔다.",
    113: "──들어 본 기억이 있다. 아니, 본 기억인가.",
    114: "『눈의 여왕』에 쓰여 있었다.^n　게르다가 카이와 흥얼거리던 추억의 구절이다.",
    115: "게르다",
    116: "──읏!",
    117: "게르다는 자기도 모르게 흥얼거린 자기 자신에게^n깜짝 놀란 듯 숨을 삼켰다.",
    118: "손에서 장미가 미끄러져 떨어진다.",
    119: "게르다는 텅 빈 손바닥을 바라보다가,^n이윽고 그 손으로 얼굴을 가렸다.",
    120: "게르다",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1114.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1114_slots_00061_00120_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1114_slots_00061_00120_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
