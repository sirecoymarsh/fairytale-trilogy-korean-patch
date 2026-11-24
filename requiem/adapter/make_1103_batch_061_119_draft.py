from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    61: "침묵이 귀를 찌른다.^n앨리스와는 다른 의미로 대화가 되지 않을지도 모르겠다…….",
    62: "나",
    63: "……아.",
    64: "가죽 표지의 책이 내 발밑에 떨어져 있다.^n그러고 보니 그녀가 넘어졌을 때 담요 그늘에서 미끄러져 나와^n이쪽으로 굴러온 것이 있었다. 분명 이 책이다.",
    65: "주워서 그녀가 겁먹지 않을 만큼 거리를 둔 채 건네자,^n여자아이는 『고마워』라는 모양으로 입술을 움직이며 받아 들었다.",
    66: "나",
    67: "헨젤과 그레텔…….",
    68: "???",
    69: "──!?",
    70: "나는 건네는 순간 보인 책 제목을 입에 담았을 뿐이다.^n그 유명한 동화라고 생각해서, 정말 아무렇지도 않게.",
    71: "하지만 여자아이는 튕겨 나가듯 고개를 들었다.^n처음으로 눈과 눈이 마주쳤다.",
    72: "???",
    73: "헨젤 오빠?",
    74: "나",
    75: "어.",
    76: "잠시 지나서야 비로소,^n그녀가 내게 『물어본』 것임을 깨달았다.",
    77: "내가 헨젤이 아니냐고.",
    78: "나",
    79: "(게다가 헨젤 『오빠』…….^n　그렇다면 이 아이도 앨리스와 마찬가지로──)",
    80: "나",
    81: "너는 그레텔이야?",
    82: "그레텔",
    83: "──!^n",
    84: "……!　……!",
    85: "경솔한 질문이었다.^n여자아이──그레텔은 눈을 환히 빛내며 물기 어린 눈동자로 나를 보았다.",
    86: "아까까지의 경계가 거짓말처럼 똑바로 내 눈을 바라보며,^n──개였다면 분명 떨어져 나갈 만큼 꼬리를 흔들었을 상태다.",
    87: "나",
    88: "아, 아니, 저기. 나는 그게, 헨젤이 아니라…….",
    89: "그레텔",
    90: "네…….",
    91: "나",
    92: "아, 그러니까…… 사실 나도 몰라.^n나는 조금, 그게, 기억이 없거든.^n이름도 가족도 전부 떠오르지 않아.",
    93: "개라면 단숨에 귀를 늘어뜨리고 고개를 숙였을 만큼^n풀이 죽어 버린 모습이 너무나 안쓰러워서,^n나는 순간 그렇게 대답하고 있었다.",
    94: "『아니야』가 아니라,^n『모르겠어』라고.",
    95: "──그래, 실제로 나는 내가 누군지 모른다.^n그렇다면 내가 『헨젤』일 가능성도 제로는 아니다.",
    96: "그레텔",
    97: "기억이 안 나……?^n이름도…… 가족도…….",
    98: "멍하니 내가 한 말을 되뇌는 그레텔.^n그 얼굴을 보고 있으니 문득 이상하다는 생각이 들었다.",
    99: "나",
    100: "──너는 모르는 거야?^n여동생이니까 오빠가 어떻게 생겼는지^n알 수 있지 않아?",
    101: "그레텔",
    102: "………….",
    103: "그레텔은 뭐라 말할 수 없는 얼굴로 내게서 시선을 돌렸다.",
    104: "『알지만 모르겠다』^n　내가 느낀 것은 그런 기묘한 뉘앙스였다.",
    105: "어쩌면 아까 내가 헨젤임을 긍정했다면,^n정말로 나는 『헨젤』이 될 수 있었는지도 모른다.",
    106: "나",
    107: "(하지만…… 그렇게 무책임한 말은 할 수 없지.)",
    108: "그레텔",
    109: "………….",
    110: "나",
    111: "갑자기 방해해서 미안해.^n이제 슬슬 가 볼게.",
    112: "나는 최대한 부드럽게 말을 건넸다.^n그레텔이 『오빠일지도, 남일지도 모르는』 남자와^n단둘이 있는 상황에 당황하고 겁먹은 것이 전해졌기 때문이다.",
    113: "사실은 여러 가지를 물어보고 싶었지만,^n이 이상 부담을 주는 것은 가엾다.",
    114: "나",
    115: "그…… 오빠를 찾으면 좋겠네.",
    116: "문을 닫으며 그렇게 말하자,^n그레텔은 주워 든 담요로 몸을 돌돌 감싸면서,",
    117: "그레텔",
    118: "………….",
    119: "다시 한번 입 모양만으로 『고마워』라고 전했다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1103.gsc" and item.get("slot") in TARGETS:
                rows[int(item["slot"])] = item
    if set(rows) != set(TARGETS):
        raise SystemExit("catalog mismatch")
    entries = []
    for index in sorted(TARGETS):
        source, target = str(rows[index]["source_text"]), TARGETS[index]
        if source.count("^n") != target.count("^n"):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entries.append(
            {
                "uid": rows[index]["uid"],
                "source_text": source,
                "source_raw_sha256": rows[index]["source_raw_sha256"],
                "target_text": target,
                "translator": "Codex internal model draft",
                "review_status": "draft_pending_single_review",
                "notes": "초벌 번역; 1차 검수 전",
            }
        )
    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1103_slots_00061_00119_draft",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 0,
        "release_ready": False,
        "entries": entries,
    }
    out = PROJECT / "packets" / "drafts" / "1103_slots_00061_00119_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
