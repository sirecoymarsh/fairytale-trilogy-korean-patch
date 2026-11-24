from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    71: "나는 화를 내기보다 멍해졌다.^n오딜은 대체 누구 이야기를 하는 걸까?",
    72: "오딜",
    73: "그 여자에 관해서라면 너보다 내가 더 잘 알아.^n믿지 않겠다면 상관없지만, 뭐, 다시 한번 충고할게.^n네가 아니라 내 마음의 평화를 위해서 말이야.",
    74: "오딜",
    75: "오데트는──그 여자는,^n남자를 실컷 이용한 뒤 버리는 창녀야.^n엮이지 않는 편이 좋아.",
    76: "그제야 오딜이 한 말의 뜻이^n내 머릿속에 스며들기 시작했다.^n마치 독이 배어드는 듯 불쾌한 이해였다.",
    77: "뺨이 확 달아올랐다.^n나를 분노하게 한 건 오딜의 저속한 말이 아니었다.^n그녀의 가엾다는 듯한 미소였다.",
    78: "오데트와 같은 얼굴이 그 아름다움은 그대로인 채,^n이토록 사악하게 일그러질 수 있다는 사실이──^n믿을 수 없고 믿고 싶지 않은 『충고』를 뒷받침하는 듯해서.",
    79: "오딜",
    80: "그 여자의 말을 진지하게 듣거나, 이야기에 맞장구치거나,^n뭔가 해 주려 하는 건 위험해.",
    81: "오딜",
    82: "──하물며 왕자 역할을 자청할 생각은 하지 마.",
    83: "오딜의 『충고』에 나는…….",
    84: "이미 자신이 지크프리트라고 밝힌다.",
    85: "밝히지 않고 시선을 피한다.",
    86: "나",
    87: "나는──지크프리트야.^n물론 진짜는 아니지만 오데트에게는 그렇게 밝혔어.",
    88: "오딜",
    89: "……!?",
    90: "오딜은 붉은 외눈을 크게 떴다.^n그녀답지 않게 꾸민 데 없는 순수한 놀라움이었다.",
    91: "하지만 다음 순간에는 평소처럼^n빈틈없는 눈빛으로 돌아와 있었다.^n붉은 입술을 옆으로 누운 초승달처럼 치켜올리며,",
    92: "오딜",
    93: "──이미 늦었구나.",
    94: "나",
    95: "내 눈에는 오데트가 그런 사람으로 보이지 않았어.",
    96: "오딜",
    97: "지금까지 지겹도록 들어 온 말이네.",
    98: "오딜의 도발에도 나는 움츠러들지 않았다.",
    99: "오딜의 미소를 보고도 어젯밤 호숫가에서 본,^n달빛을 두른 채 눈을 내리깐 오데트의^n금방이라도 사라질 듯 슬픈 모습은 지워지지 않는다.",
    100: "오딜의 충고가 옳아서 내가 놀아나는 것뿐이라 해도,^n그 사실을 깨달았을 때 손을 떼면 된다.^n내가 『지크프리트』라고 밝힌 것은 어디까지나 역할놀이일 뿐이다.",
    101: "오딜",
    102: "뭐, 네 마음대로 해.^n",
    103: "──정말이지, 매번. 남자들은 왜 이렇게 멍청한 걸까.^n내 입장도 좀 생각해 줬으면 좋겠네.",
    104: "일부러 티 나게 한숨을 쉬는 오딜에게 등을 돌리고,^n나는 방을 뒤로했다.",
    105: "떠나기 직전 한 번만 돌아보니 오딜의 모습은 사라지고,^n그녀가 있던 자리에 놓인 백조 『오데트』가^n동그란 눈망울로 나를 배웅하고 있었다.",
    106: "나",
    107: "………….",
    108: "나는 오딜에게서 시선을 피했다.",
    109: "오데트에게 『지크프리트』라고 밝힌^n바로 어젯밤의 기억.",
    110: "그때는 그러겠다고 생각하기도 전에 말이 튀어나왔다.^n오데트의 괴로움을 씻어 주고 구원이 될 수 있다면──^n그런 생각을 했었다.",
    111: "하지만 그것은 어디까지 진심이었을까.^n열에 들뜬 채 품었을 뿐인 얄팍한 충동이 아니었을까.",
    112: "실제로 그 열기를 떠올리려 해도 내 마음은 고요할 뿐이다.^n운명적이라고 느꼈던 모든 기억이 순식간에 빛바래어,^n방금 전까지 피었던 꽃이 시들어 떨어지는 듯하다.",
    113: "오딜",
    114: "어머나, 아무 말도 안 해?^n네 안색을 보니 『내가 지크프리트가 되겠다』고^n말할 것 같은 모습이었는데──",
    115: "오딜",
    116: "그 정도로 바보는 아니었네.^n여기서 멈춰 서서 정말 다행이야.",
    117: "나",
    118: "나는…….",
    119: "나는 이렇게 애매하고 쉽게 흔들리며,^n성실하지 못한 사람이었던가.",
    120: "지금이라면 아직 수습할 수 있지 않을까.^n지금이라면 아직──",
    121: "오딜",
    122: "──들었지, 오데트.^n이 꼬마는 네가 늘 낚는 남자들보다^n아주 조금은 더 영리했던 모양이야.",
    123: "오딜은 갑자기 목소리를 높였다.^n멀리 있는 누군가에게 외치듯 내는 목소리에 나는 숨을 삼킨다.",
    124: "나",
    125: "(혹시──아니, 틀림없이,^n　오데트는 이 방에 있어.)",
    126: "대답하듯 끼익 하고 무언가 삐걱거렸다.^n방 한가운데 매달린 새장의 창살.",
    127: "나",
    128: "(……오데트. 거기서 듣고 있었어?)",
    129: "오딜은 곁에 놓인 백조 『오데트』를^n아무렇게나 툭툭 두드린다.^n시선도 『그녀』에게 둔 채 목소리만 더욱 먼 곳으로 향하며,",
    130: "오딜",
    131: "왕자님을 원한다면 다른 사람을 찾아봐.^n괜찮아, 너라면 금방 붙잡을 수 있잖아.",
    132: "──대답은 없다.^n새장 안은 고요하고 백조 장식물은 말하지 않는다.",
    133: "그저 끼익 하고 딱 한 번,^n힘없이 새장이 삐걱거리는 소리가 났다.",
    134: "나",
    135: "(……오데트, 미안해.)",
    136: "나",
    137: "(이런 기분을 겪게 할 거였다면,^n　처음부터 지크프리트라고 하지 말았어야 했어.)",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1119.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1119_slots_00071_00137_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1119_slots_00071_00137_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
