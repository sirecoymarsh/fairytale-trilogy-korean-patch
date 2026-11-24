from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    61: "(그러니까 아마 아까 그 고양이가 앨리스 안에서^n『모자 장수』 역할을 맡고 있었던 거겠지…….)",
    62: "나는 뒤늦게 사정을 파악했다.",
    63: "내가 회색 펠리컨으로 보일 정도니,^n고양이가 모자 장수로 보여도 이상하지 않다.^n앨리스는 그런 세계의 주민이다.",
    64: "나",
    65: "그런데 어떤 문제야?",
    66: "앨리스",
    67: "『까마귀와 글 쓰는 책상은 왜 닮았는가』예요.",
    68: "나",
    69: "아아…….",
    70: "역시 『이상한 나라의 앨리스』에 나온 수수께끼라고^n나는 떠올렸다.",
    71: "눈앞의 앨리스가 말한 대로,^n다과회 도중 모자 장수가 낸 문제다.",
    72: "나",
    73: "(하지만 그건 엉터리 수수께끼라,^n　작품 속에 제대로 된 답은 없었던 것 같은데.)",
    74: "　앨리스의 손밑에는,^n『까마귀＝글 쓰는 책상』『까마귀＋글자＝?』『글 쓰는 책상×검은 깃털』",
    75: "나",
    76: "──풀었다니…… 답이 뭔데?",
    77: "앨리스는 기다렸다는 듯 가슴을 펴고,^n겹겹이 쌓인 종이 아래 드러난 글 쓰는 책상의^n표면을 가리켰다.",
    78: "자세히 보니 검은 잉크 방울이 튄 흔적이 있다.",
    79: "앨리스",
    80: "　까마귀도 글 쓰는 책상도,^n『둘 다 검은 것이 날아다녀요』──",
    81: "나",
    82: "……오……!",
    83: "평소 같은 엉뚱한 답에 대비하던 나는^n생각보다 그럴듯한 답에 감탄하고 말았다.",
    84: "나",
    85: "재치 있네.",
    86: "앨리스",
    87: "재치 있다는 건 『좋다』는 뜻인가요?^n이걸로 정답이라고 할 수 있을까요?",
    88: "나",
    89: "응, 정답 중 하나라고 생각해!",
    90: "앨리스",
    91: "정말요? 해냈어요!",
    92: "앨리스의 목소리가 들뜬다.^n안 그래도 별이 가득한 밤하늘처럼 반짝이던 눈동자가,^n거의 빅뱅 같은 빛을 내며 기쁨으로 반짝인다.",
    93: "앨리스",
    94: "아아, 해냈군요, 나.^n이 이상한 세계에서 제대로 된 답을 찾아낸 건^n처음일지도 몰라요…….",
    95: "크게 기뻐하면서도 지쳐 보이는 것은,^n실제로 앨리스가 쉬지 않고 문제에 도전했기 때문이겠지.^n휘갈겨 쓴 수식과 문자열의 폭풍이 그것을 보여 준다.",
    96: "『까마귀는 날 수 있다, 글 쓰는 책상은 날 수 없다.』^n",
    97: "『글 쓰는 책상에서는 글을 쓸 수 있다, 까마귀는 못 쓴다?』^n",
    98: "『↑경우에 따라서는 쓸 수 있다?』",
    99: "나",
    100: "(아…….)",
    101: "의미가 있는 듯 없는 수많은 메모 속에서^n나는 신경 쓰이는 것을 발견했다.",
    102: "『사람－기억＝잊는다.』^n",
    103: "『사람＋기억＝떠올린다.』^n",
    104: "『잊는다＋떠올린다＝평범한 사람』",
    105: "『(사람－기억)＋(사람＋기억)＝사람이 2명……?』^n",
    106: "『2명＝평범한 사람?』",
    107: "『사람－이름＝?』^n",
    108: "『사람＋이름＝이름 있는 사람＝당연한 사람』^n",
    109: "『당연한 사람－이름＝당연하지 않은 사람』",
    110: "『당연하지 않은 사람＋이름＝멀쩡한 사람』^n",
    111: "『멀쩡한 사람－이름＝멀쩡하지 않은 사람!?』^n",
    112: "『멀쩡하지 않은 사람＝위험!?』",
    113: "나",
    114: "(뭐야, 이 결론…….)",
    115: "현기증이 날 듯한 시행착오의 흔적이 남아 있었다.^n몇 번인가 다시 시작해 같은 결론에 다다르려다,^n마구 휘갈겨 지운 곳도 있다.",
    116: "그것은 무언가를 위해 끝없이 헤맨 앨리스의 사고다.",
    117: "나",
    118: "앨리스, 이건?",
    119: "앨리스",
    120: "당신이 기억을 잃었다는 사실을^n나 나름대로 심각하게 받아들이고 어떻게든 해 보려고 했어요.^n수학이라면 웬만한 문제는 풀 수 있을 테니까요.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1123.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1123_slots_00061_00120_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1123_slots_00061_00120_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
