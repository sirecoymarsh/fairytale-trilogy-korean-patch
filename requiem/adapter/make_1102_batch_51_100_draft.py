from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    51: "　아, 저건 말이죠.^n『나를 먹어』 쿠키와 『나를 마셔』 병을^n　가둬 둔 거예요. 먹어라, 마셔라 시끄러워서요.",
    52: "앨리스",
    53: "처음에는 영문을 몰라서^n시키는 대로 해 버렸더니,^n커졌다 작아졌다 하며 정말 고생했어요.",
    54: "앨리스",
    55: "그 덕분에 지금은 특별히 뭘 먹지 않아도^n커졌다 작아졌다 하는──^n그런 몸이 되어 버렸어요.",
    56: "버섯 탁자, 망가진 목마,^n서랍장에서 넘쳐흐르는 형형색색의 과자.",
    57: "의미가 있을 듯 없고, 없을 듯 있으며,^n불합리한데도 묘하게 합리적인 앨리스의 설명을 듣다 보니,^n나는 두 가지 마음에 갈가리 찢길 것 같았다.",
    58: "『이 아이는 정말 그 『앨리스』일지도 모른다.』^n　라는 생각과,",
    59: "『이 아이는 안 되겠다. 있을 수 없는 일을 믿고 있다.』^n　라는 생각이다.",
    60: "　아무리 생각해도 옳은 것은 뒤쪽이라고 생각한다.^n　하는 말이 너무 엉망진창이고,^n『앨리스』는 이런 성격이 아니었던 것 같으니까.",
    61: "하지만 내가 좋아하는 것은 앞쪽이었다.^n눈앞의 아이가 진짜 앨리스라면 그저 멋진 일이다.^n그래서 아무래도 믿고 싶은 마음을 버릴 수 없다.",
    62: "나",
    63: "(아니, 그래도. 머리가 좀 그렇다고 해도,^n　자신에 관해 아무것도 모르는 나보다는 훨씬 나을 거야.)",
    64: "결국 그런 시시한 결론에 다다랐다.^n앨리스의 방에서 들떠 있던 마음도^n이제야 슬슬 가라앉은 모양이다.",
    65: "앨리스",
    66: "……있죠. 차 없는 다과회라 죄송하지만.^n이제 슬슬 본론으로 들어가도 될까요?",
    67: "에헴, 하고 일부러 티 나게 헛기침한 뒤 앨리스가 말했다.",
    68: "앨리스",
    69: "당신, 자신이 누군지 모른다고 했죠.^n아직도 모르겠나요?",
    70: "나",
    71: "응…….^n정신을 차려 보니 하얀 방에 눕혀져 있었어.",
    72: "앨리스",
    73: "하얀 방──그건 눈이 아프겠네요.",
    74: "분명 눈부실 정도였지만 이 방보다는 낫겠지.^n",
    75: "──그렇게 생각하다가 깨달았다.",
    76: "이 방이 앨리스에게 꼭 어울리고 그녀 자신을 나타내는 것처럼,^n그 하얀 방은 아무것도 모르고 이해하지 못하는^n나 자신의 상징이 아니었을까.",
    77: "한번 그렇게 생각하고 나니,^n막 눈을 뜬 나를 몰아세우던 흰빛이 머릿속에 되살아나,^n쉴 새 없이 질문을 퍼붓는 듯했다.",
    78: "이름, 나이. 어디에 살았는지, 가족이 있었는지.^n",
    79: "무엇을 좋아하고 싫어했는지, 무엇을 잘하고 못했는지.^n",
    80: "대체 어떤 사정으로 이런 일이 벌어졌는지.",
    81: "그리고 나는 마음속으로^n그 질문에 맞서 용감히 입을 열지만──",
    82: "앨리스",
    83: "다른 건 없나요?^n그렇게 눈 아픈 일밖에 기억하지 못한다니 안됐네요.",
    84: "나",
    85: "……………….^n──응.^n모르겠어. 이제 정말 아무것도.",
    86: "금세 툭 하고 포기할 수 있었다.^n애초에 모른다는 것조차 떠올릴 수 없을 만큼 기억나지 않는다.",
    87: "보통 이럴 때는 좀 더 『큰일이야!』 하는 기분이 들어^n당황하게 되는지도 모른다.",
    88: "하지만 나라는 존재는 이미 당연하게 이곳에 있고,^n아무것도 모른다는 사실도 내 안에서는 당연한 일이라,^n뭐랄까, 어쩔 수 없다는 마음이 더 강하다.",
    89: "새삼스레 제 손바닥을 바라보며,^n하아, 하고 깊이 한숨 쉬는 것이 고작이었다.",
    90: "앨리스",
    91: "괜찮아요, 괜찮아요!^n세상에는 안다고 생각해도 모르는 것투성이예요.^n모른다면 알아내면 되는 거예요.",
    92: "앨리스는 몸을 내밀어 내 얼굴을 들여다보았다.^n전체적으로는 도무지 알 수 없는 말이었지만,^n분명 나를 격려하는 것이겠지.",
    93: "나",
    94: "으, 응…… 고마워.",
    95: "앨리스",
    96: "네, 그래요.^n당신이 몰라도 내가 알아내 줄게요!",
    97: "나",
    98: "뭐?",
    99: "앨리스",
    100: "간단해요.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1102.gsc" and item.get("slot") in TARGETS:
                rows[int(item["slot"])] = item
    if set(rows) != set(TARGETS):
        raise SystemExit("catalog mismatch")
    entries = []
    for index in sorted(TARGETS):
        source, target = str(rows[index]["source_text"]), TARGETS[index]
        if source.count("^n") != target.count("^n"):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": rows[index]["uid"], "source_text": source, "source_raw_sha256": rows[index]["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 한 차례 검수 전"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1102_slots_00051_00100_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1102_slots_00051_00100_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
