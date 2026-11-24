from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    101: "그렇네요. 그래요. 그러니까…….^n회색 날개에 회색 꽁지깃──^n",
    102: "당신, 회색펠리컨 아닐까요?",
    103: "나",
    104: "……뭐?",
    105: "당당하게 단언한 앨리스를 보고 얼빠진 목소리가 새어 나왔다.^n너무 뜻밖의 결론이라^n선반버섯에서 미끄러져 떨어질 뻔했다.",
    106: "『진짜 앨리스』와 『머리가 가엾은 아이』 사이에서^n　흔들거리던 바늘이,^n　휙 하고 기세 좋게 뒤쪽으로 기울었다.",
    107: "앨리스",
    108: "네, 분명 그럴 거예요!^n언니와 함께 읽은 도감에서 봤는걸요.^n틀림없어요!",
    109: "나",
    110: "아, 아니야!^n나, 나는…….",
    111: "잠시 반박이 끊긴 것은 자신에 관해 아는 것이^n너무 없어서 자신감을 잃었기 때문이다.^n앨리스가 워낙 자신만만해서 더욱 그랬다.",
    112: "앨리스",
    113: "아니라고 해도요.^n회색이라고 해서 비둘기 같지는 않아요.^n구구 하고 울지 않잖아요?",
    114: "나",
    115: "아니, 그게 아니라니까. 새가 아니야.^n나는 인간이야. 그것만큼은 확실해, 봐.",
    116: "망설임 없이 나를 조류라고 단언한 앨리스에게^n증명이 될지는 모르겠지만,^n나는 손가락 다섯 개가 달린 손을 내밀어 보였다.",
    117: "그러자 앨리스는 놀란 듯 손으로 입가를 가렸다.",
    118: "앨리스",
    119: "정말이네요!　어머, 그랬군요.^n……미안해요. 인간은 너무나도 보기 드물어서요.^n특히 야옹도 꿀꿀도 하지 않고 말을 하는 인간은요.",
    120: "나",
    121: "그, 그래. 그렇구나…….",
    122: "앨리스",
    123: "그래도 인간인 걸 알아서 다행이네요.^n──뭐예요, 아무것도 모른다는 건 역시 거짓말이었네요.^n그럴 리 없다고 생각했어요!",
    124: "나",
    125: "으, 응…….^n보면 알 수 있는 건가 했는데…….^n나는 인간이고, 남자고, 제법 젊어.",
    126: "앨리스",
    127: "그렇게나 많이 알고 있다고요!?^n대단해요.^n",
    128: "그래요, 그래. 잘했어요. 이걸로 더 안심이네요.",
    129: "앨리스는 내 손을 꼭 쥐고 활짝 웃으며 축복해 주었다.^n그 손은 부드럽고 따뜻하다.^n가엾은 아이지만 분명 아주 착한 아이겠지.",
    130: "나",
    131: "……그러게.^n이제 이름이나 나이, 살던 곳 같은 걸^n떠올릴 수 있으면 좋겠는데…….",
    132: "무난하게 말하며 살며시 손을 빼냈다.^n그녀가 착한 아이라고 해도 지금의 나는^n좀 더 말이 통하는 누군가와 이야기하고 싶었다.",
    133: "나",
    134: "저기, 난 이제 슬슬 갈게.^n그러니까…… 초대해 줘서 고마워.^n또 마음이 내키면…….",
    135: "앨리스",
    136: "네, 언제든 원하는 때에 오세요.^n언제나 티타임이니까요.^n",
    137: "──아, 맞다.",
    138: "등을 돌린 순간 붙잡혔다.^n돌아본 내게 앨리스가 두 손에 올려 내민 것은^n알록달록한 막대사탕이었다.",
    139: "나",
    140: "이거…… 주는 거야?",
    141: "앨리스",
    142: "네. 나는 『달콤한』 인간이니까요.",
    143: "재치 있는 대사에 마땅한 답을 떠올리지 못한 채,^n나는 사탕을 받아 들었다.^n포장 안에서 민트와 딸기 향이 풍겨 왔다.",
    144: "나",
    145: "……고마워.",
    146: "감사의 말은 자연스럽게 나왔다.",
    147: "앨리스가 하는 말과 그녀에게 보이는 세계는^n너무나도 엉뚱해서 내가 이해하기 어려웠지만,^n그녀의 마음만큼은 처음부터 끝까지 고마웠으니까.",
    148: "복도로 나온 나는 아주 깊은 한숨을 내쉬었다.^n앨리스와 나눈 대화는^n생각했던 것보다 훨씬 나를 지치게 한 모양이다.",
    149: "나",
    150: "(자, 이제부터 어떻게 하지?)",
    151: "복도에는 인기척이 없다.^n샹들리에처럼 늘어진 그 아기용 장식이^n바람에 흔들려 서로 스치는 소리만 들린다.",
    152: "그래서 나는 걷기 시작했다.^n어쨌든 사람을 만나 이야기하고,^n설명할 수 없는 온갖 일에 멀쩡한 이유를 찾고 싶었다.",
    153: "아무와도 마주치지 못한다면,^n눈에 띄는 문을 하나씩 모조리 두드려 보는 것도^n방법일지 모른다.",
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1102_slots_00101_00153_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1102_slots_00101_00153_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
