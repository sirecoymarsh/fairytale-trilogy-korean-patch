from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    76: "그 말에 나는 피부를 어루만지는 바람의 다정함을 깨달았다.^n깊은 숲의 향기를 실어 오며 머리카락 사이에 고인^n무거운 열기를 휘감아 가져간다.",
    77: "나",
    78: "……응, 그러게.^n구름도 없고 별도 아름답네.",
    79: "나",
    80: "모처럼 보름달이 떴는데 맑아서 다행이야.",
    81: "오데트",
    82: "응. 나는 이런 밤이 좋아.",
    83: "　천진하게 고개를 끄덕이는 그녀를 보고 깨달았다.^n　느슨하게 늘어진 소매 사이에 숨기듯^n『백조의 호수』 책을 안고 있다.",
    84: "나",
    85: "그…… 갑자기 말을 걸어서 미안해.^n너는 오데트 맞지?",
    86: "오데트",
    87: "응, 맞아.^n──어머, 우리 어디선가 만났던가?",
    88: "아니, 하고 고개를 저으려다 멈췄다.",
    89: "나",
    90: "만났다면 만났……다고 해야 하나.^n낮에 오딜에게 소개받았거든.",
    91: "오데트",
    92: "오딜에게. 그랬구나.^n그…… 그런 모습이라 미안해.",
    93: "오데트는 죄스러운 듯 눈을 내리깔았다.^n나는 낮에 백조 『오데트』를 소개받았을 때를^n떠올리고 있었다.",
    94: "　장식물의 머리를 아무렇게나 두드리며,^n『얼빠진 모습』이라고 내뱉던 오딜.",
    95: "자기 아버지가 백조로 바꿨다고 하는 생명을,^n그녀는 진심으로 비웃는 듯했다.",
    96: "분명 내게 던진 『안됐네』라는 조소를,^n오딜은 평소에도 오데트에게 던지고 있겠지.",
    97: "그건 짐작일 뿐이지만 거의 확신에 가까웠다.",
    98: "나",
    99: "오딜은…… 심술궂네.",
    100: "뱃속 부근에 부글부글 쌓인 열기를,^n나는 무심코 입 밖에 내고 말았다.",
    101: "오데트는 한순간 눈을 크게 떴다가,^n천천히 고개를 저었다.",
    102: "오데트",
    103: "말이 거칠 뿐이야.^n네게 무례한 말을 했다면^n그──미안해.",
    104: "나",
    105: "왜 네가 사과해.",
    106: "오데트",
    107: "오딜은 심한 말만 하지만 영리하고 강하고,^n멋진 점도 많다는 걸 아니까.^n싫어하지 않았으면 해.",
    108: "나",
    109: "………….",
    110: "오데트가 오딜에게 미움받기 싫은 게 아닐까.^n왠지 그런 생각이 들었다.",
    111: "오데트가 지으려는 미소는 완전히 실패해서,^n그녀다운 천진함 대신 눈치를 보는 듯한 비굴함이 배어 있었고,^n뱃속에 쌓인 것이 가라앉기는커녕 짜증이 났다.",
    112: "머릿속 깊은 곳에서 정체 모를 무언가가 꿈틀대는 것을 느꼈다.^n──혹시 내 과거와 공명하는 걸까.",
    113: "나",
    114: "　오딜은 백조인 네 머리를 두드렸어.^n『얼빠진 모습』이라고도 했고.",
    115: "나도 모르게 그런 말을 해 버렸다.^n어딘가 예상은 했지만 오데트의 얼굴을 스친 것은^n분노가 아니라 깊은 슬픔이었다.",
    116: "오데트",
    117: "──나를 위해 화내 준 거구나.^n고마워.",
    118: "오데트",
    119: "하지만 나는 괜찮아.^n낮의 일…… 백조로 있는 동안의 일은,^n전혀 기억하지 못하거든.",
    120: "오데트",
    121: "아, 그러니까,^n낮에 너와 만났던 일도 몰라.^n미안해.",
    122: "나",
    123: "으, 응…….",
    124: "오데트가 그렇게 받아들였다면 됐다.^n내가 할 수 있는 해결은 그 정도뿐이다.",
    125: "그래도 신경 쓰이는 것은 『백조의 호수』를 『성서』로 삼는^n그녀가 악역인 오딜을 멀리하지 않는다는 점──^n오히려 감싸고 있다는 점이다.",
    126: "나",
    127: "그, 너와 오딜은 꼭 닮았는데,^n어떤 관계야?",
    128: "오데트",
    129: "관계는…….^n──오딜의 아버지가,^n내게 백조가 되는 저주를 걸었어.",
    130: "오데트",
    131: "오딜이 나와 똑같은 얼굴인 것은…….",
    132: "말을 잇다 말고 오데트는 고개를 숙였다.^n푸른 그림자에 갇힌 얼굴이 괴롭게 일그러져 있었다.",
    133: "『백조의 호수』 줄거리를 따르면,^n　오딜이 오데트와 똑같은 얼굴인 것은,^n　오데트의 행복을 가로막기 위해서다.",
    134: "내가 묻고 싶었던 것은 그런 뜻이 아니었지만,^n오딜을 미워하지 못하는 오데트를 괴롭히는 것은,^n내가 바라던 일이 아니었다.",
    135: "나",
    136: "아, 그러니까, 그…….^n──힘들겠네. 백조가 된다니.^n어떤 기분일까.",
    137: "화제를 돌리자 예상대로 오데트는 구원받은 듯 고개를 들었다.^n글쎄, 하고 잠시 말을 골랐다.",
    138: "오데트",
    139: "아침 햇빛을 보면 참을 수 없이 졸려져서,^n눈을 감았다가 다시 뜨면 벌써 밤이야.^n그동안은 몸도 마음도 백조라서 아무것도 기억하지 못해.",
    140: "오데트",
    141: "밤도 좋지만,^n햇볕 아래서 산책할 수 없는 건 조금 쓸쓸해.",
    142: "나",
    143: "그러게.^n이 호수도 맑은 날 오면 분명 아름다울 거야.",
    144: "오데트",
    145: "응, 분명 그렇겠지.^n언젠가 보트라도 탈 수 있다면 즐거울 텐데.",
    146: "오데트는 먼 눈길을 수면으로 던졌다.^n비친 보름달은 왠지 멀어지는 듯했다.",
    147: "나",
    148: "저주가 풀리면 좋겠다.",
    149: "오데트",
    150: "──응. 고마워.^n그런 날이 오면 좋겠지만…….",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1112.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1112_slots_00076_00150_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1112_slots_00076_00150_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
