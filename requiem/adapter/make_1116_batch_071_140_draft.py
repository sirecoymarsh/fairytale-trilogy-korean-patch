from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    71: "아니, 아니, 흉보는 건 아니야.^n개성이지, 개성.",
    72: "의사",
    73: "자, 그럼 가슴 소리를 들어 볼게.",
    74: "의사 선생님의 팔이 앨리스의 가슴을 움켜쥐고,^n청진기 끝을 가져다 댔다.",
    75: "앨리스",
    76: "히야……!^n선생님, 늘 생각하는 건데 그거 차가워요.",
    77: "의사",
    78: "자, 참으렴.^n──음, 앨리스는 심장이 멀구나.^n여긴가? 아니면 여긴가?",
    79: "의사 선생님은 고개를 갸웃하며 청진기 끝을 몇 번이나 다시 댔다.",
    80: "새싹처럼 솟은 유두 둘레에 원을 그리기도 하고.^n세게 파묻어 풍만한 살을 일그러뜨리기도 하고.",
    81: "앨리스",
    82: "응, 으으응…… 히야……!^n선생님, 선생님, 간지러워요.",
    83: "의사",
    84: "미안해, 몸이 이상해지면 제대로 말하렴.^n배가 뜨거워진다든가, 숨이 막힌다든가.",
    85: "앨리스",
    86: "꺄아, 아, 히야……!^n괜찮아요, 간지러울 뿐이에요.^n──저기, 오늘은 제 심장을 그렇게 찾기 어려워요?",
    87: "의사",
    88: "음, 찾을 수가 없네.^n발육이 좋은 건 반가운 일이지만,^n매번 소리가 잘 안 들려서 곤란하단 말이지.",
    89: "의사",
    90: "이, 이, 이 가슴이 너무 커서 말이야.^n앨리스도 불편하겠네.^n이 정도면 어깨 같은 데가 무겁지 않아?",
    91: "의사 선생님의 손은 여전히^n이런저런 움직임으로 앨리스의 심장 소리를 찾는다.",
    92: "──이제 저 손놀림은 청진기를 댄다기보다,^n움켜쥐고, 주무르고, 마구 반죽하는 것 같다.^n의사 선생님의 숨이 거칠어진 건 기분 탓일까.",
    93: "　어느 쪽이든 내 의심은 화면 너머까지 닿지 않는다.^n　그리고 앨리스는 전혀 신경 쓰지 않고 고개를 갸웃하며,^n『가슴 때문에 어깨가 무거운지』를 생각하고 있다.",
    94: "앨리스",
    95: "가슴을 떼어 본 적이 없어서 모르겠어요.^n선생님도 뱃살이 얼마나 무거운지는^n모르시잖아요?",
    96: "의사",
    97: "아하하. 아, 그런가.^n그렇군, 그렇군.",
    98: "물컹……! 열 손가락을 깊이 파묻고,^n기괴한 모양으로 앨리스의 가슴을 일그러뜨리며^n의사 선생님은 웃는다.",
    99: "게다가 그 대답은 아무리 봐도 건성이라,^n지금 의사 선생님은 앨리스의 입이 아니라 가슴과^n대화하는 게 아닐까 하는 생각이 들었다.",
    100: "청진기는 조금 전부터 쓸모가 없어진 듯^n가슴팍에 축 늘어져 있다.",
    101: "의사",
    102: "──……후우. 하아.^n응. 좋아. 이 정도면 됐겠지.",
    103: "의사 선생님이 짐승처럼 숨을 내쉬며 손을 놓는다.^n그토록 일그러진 살이 돌아올지 걱정했지만,^n풀려난 순간 팡 소리가 날 듯한 기세로 부풀었다.",
    104: "앨리스",
    105: "아아, 다행이다. 끝났네요.^n저기 선생님, 어땠어요?^n오늘 제 가슴은 뭐라고 말하던가요?",
    106: "의사",
    107: "어? 어? 아…….^n으음, 그래, 행복한 듯한 울림이었어.",
    108: "앨리스",
    109: "어머, 그래요!^n그럼 오늘은 틀림없이 좋은 하루가 되겠네요.",
    110: "누가 들어도 건성인 대답인데,^n앨리스는 눈을 빛내며 만족스럽게 고개를 끄덕였다.",
    111: "의사",
    112: "자, 그럼.^n이번에는 그레텔 차례야.",
    113: "그레텔",
    114: "아…… 아…….",
    115: "의사 선생님이 양손의 손가락을 이상하게 구부린 채 돌아서자,^n그레텔은 유령과 마주친 듯 눈을 크게 뜨고^n온몸을 뻣뻣하게 굳혔다.",
    116: "의사",
    117: "자, 가슴을 보여 주렴.",
    118: "그레텔",
    119: "으, 으으으…….",
    120: "의사 선생님의 손이 다가오자,^n그레텔은 다리를 덜덜 떨며^n눈을 꼭 감았다.",
    121: "의사",
    122: "음, 그레텔은 부드럽구나.^n피부도 매끈매끈하고, 말랑말랑하고 보들보들하네.^n아, 건강해서 아주 좋다는 뜻이야.",
    123: "그레텔",
    124: "으, 으으…… 네, 네.",
    125: "의사",
    126: "그리고 눈 깜짝할 사이에 찾을 수 있네.^n그래, 그래. 여기, 여기.",
    127: "완만한 굴곡을 매끄럽게 미끄러져^n청진기가 도착한 곳은 분명 왼쪽 가슴이었다.",
    128: "하지만 얌전히 소리를 들을 기색은커녕,^n작은 유두를 걸어 올리듯 잘게 흔들린다.",
    129: "그레텔",
    130: "히윽……!^n아, 아, 안 돼요, 거긴…… 싫어.",
    131: "뒷걸음질하는 그레텔의 몸을 붙잡는 척하며,^n의사 선생님의 손가락이 반대쪽 유두를 꼬집는다.",
    132: "의사",
    133: "어라, 왜 그러니.^n심장이 엄청 두근두근 뛰고 있어.",
    134: "그레텔",
    135: "그, 그야, 그야 그야…….^n후아! 아, 아아, 우, 움직이지 마세요…….",
    136: "그레텔은 눈을 크게 뜨고 머리를 좌우로 흔들었다.^n바스락거리며 마른 잎 색깔의 머리카락이 흐트러진다.",
    137: "그레텔",
    138: "이, 이제…… 으, 부, 부끄러……워요.^n오…… 옷, 입고 싶어…… 입게 해 주세…….",
    139: "의사",
    140: "그래, 그래. 미안해. 한창 예민할 나이의 여자아이니까.^n하지만 조금만 더 참으렴. 딱 5초만.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1116.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1116_slots_00071_00140_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1116_slots_00071_00140_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
