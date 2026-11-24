from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    56: "무엇을 하고 싶었는지…….",
    57: "???",
    58: "하고 싶은 게 아무것도 없었다면 떠올리지 않아도 돼.^n하지만 무언가를 간절히 바랐다면 망각과 싸워야 해.",
    59: "담담하던 목소리에 기묘한 열기가 깃드는 것을 느꼈다.^n──이건 정말로 나를 위한 말일까.",
    60: "다음 순간,^n그녀는 말실수를 깨달은 듯 작게 숨을 삼키고 시선을 돌렸다.",
    61: "???",
    62: "내가 말해 줄 수 있는 건 이 정도일까.^n미안하지만 다른 도움이 될 만한 건…….",
    63: "나",
    64: "저, 저기!^n미안한데 두 가지만 물어봐도 될까.",
    65: "???",
    66: "……?^n그래, 말해.",
    67: "수를 정해 둔 것이 좋았는지도 모른다.^n그녀는 문틈을 그대로 유지한 채 고개를 끄덕여 주었다.",
    68: "나",
    69: "첫 번째.^n너, 다른 아이들처럼 『성서』는 안 가지고 있어?",
    70: "지금까지 만난 아이들은 모두 한 손에 『성서』를 들고 있었다.^n각자 주인공으로 나오는 이야기의 그림책이다.",
    71: "그것을 『자신의 과거와 미래를 보여 주는 이야기』로 여기며,^n무척이나 소중하게 품고 있다.",
    72: "　오딜의 말로는,^n『이것만 있으면 자신에 대해 무엇이든 알 수 있다』고.",
    73: "하지만 그녀의 두 손은 아무것도 들지 않은 채,^n살며시 문 가장자리에 놓여 있다.",
    74: "???",
    75: "──아, 『성서』 말이지.^n가지고는 있지만…… 나는 늘 들고 다니지 않아도 괜찮으니까.",
    76: "분명 뭔가 의미가 있어 보이는 대답이라,^n이것저것 캐묻고 싶었지만 꾹 참았다.^n질문 개수는 내가 정해 버렸다.",
    77: "나",
    78: "그렇구나…… 그럼 두 번째.^n네 이름을 알려 줄 수 있을까.",
    79: "???",
    80: "──!",
    81: "몸이 떨리면서 은빛 머리카락도 흔들렸다.^n아주 간단한 질문인데도 그녀는 분명^n지금까지와는 다른 동요를 보이고 있었다.",
    82: "???",
    83: "이, 름…….^n내…….",
    84: "나",
    85: "으, 응.^n나는 댈 이름도 없는데 너만 이름을 말하게 해서,^n그…… 미안하지만.",
    86: "???",
    87: "──읏.^n나, 나는…….",
    88: "그녀는 한 손을 들어 이마를 감쌌다.^n삐걱거리는 머리를 누르는 듯한 몸짓.^n정말로 아픔을 견디는지 몇 번이고 고개를 좌우로 흔든다.",
    89: "???",
    90: "나는, ──게르다.^n……아니, 달라.^n게르다가 아니야…….",
    91: "나",
    92: "뭐……?",
    93: "게르다?",
    94: "미안해.^n나, 이만 가 볼게.",
    95: "멈춰 선 내 앞에서 이번에야말로 문은 닫혔다.^n그 짧은 순간 보인 게르다의 고통스럽게 일그러진 얼굴이,^n가시처럼 따끔따끔 내 가슴을 아프게 했다.",
    96: "나",
    97: "(잘 모르겠지만 괴롭게 해서 미안해…….)",
    98: "얼음 문을 향해 마음속으로 사과했다.",
    99: "나는 다시 복도를 걸으며 두서없이 생각을 이어 갔다.",
    100: "나",
    101: "(게르다에 얼음 같은 문──^n　그녀의 『성서』는 그건가.)",
    102: "　어릴 때가 아니라 어느 정도 어른이 되어 다시 읽었을 때^n『좋다』고 생각했던 그 동화.",
    103: "『눈의 여왕』──",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1106.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1106_slots_00056_00103_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1106_slots_00056_00103_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
