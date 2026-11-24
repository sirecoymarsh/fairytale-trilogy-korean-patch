from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "앨리스의 방 앞에서 나는 잠시 망설였다.",
    2: "재미있고 친절한 여자아이라고 생각한다.^n하지만 정신없고 엉뚱해서,^n함께 있으면 피곤하기도 하다.",
    3: "나",
    4: "(조금 더 이야기해 보고 싶기는 한데…….)",
    5: "앨리스",
    6: "꺄아……!^n아…… 아, 아, 앗.",
    7: "앨리스",
    8: "이럴 수가, 이럴 수가.^n대체 오늘은 무슨 날이에요.",
    9: "나",
    10: "──!?",
    11: "문 너머에서 울려 온 앨리스의 목소리는,^n놀라고 괴로워하고 어쩔 줄 몰라 하다가 마침내 진심 어린 탄식으로 바뀌었다.",
    12: "나",
    13: "괘, 괜찮아!?",
    14: "앨리스",
    15: "사, 살려 주세요!",
    16: "나는 마음을 다잡고 문을 열었다.",
    17: "앨리스의 방에는 두꺼운 커튼을 닫아 만든 어둠과,^n형형색색의 조명이 서로 맞서며,^n방 전체가 희미하게 빛나는 듯한 기묘한 밤이 찾아와 있었다.",
    18: "언뜻 보면 어두워 낮보다 차분한 인상이지만,^n자세히 보면 버섯 갓과 꽃의 이슬, 늘어놓은 병이 빛나고 있어,^n낮보다 화려하다. ──아니, 독기가 넘친다.",
    19: "앨리스",
    20: "사, 살려 주세요, 살려 주세요!",
    21: "도움을 청하는 앨리스에게 바로 달려가지 않은 이유는,^n우선 방의 모습에 한눈을 팔았기 때문이다.",
    22: "앨리스",
    23: "부탁이에요.^n이건 저 혼자서는 어쩔 수 없어요!",
    24: "나",
    25: "뭐…… 앗!?",
    26: "또 하나는 앨리스가 예상보다 훨씬^n기묘한 모습으로 나를 기다리고 있었기 때문이다.",
    27: "앨리스",
    28: "살려 주세요!^n제 몸이 커져 버렸어요!",
    29: "설마 엉덩이로 맞이할 줄이야.",
    30: "화려하게 뒤집힌 치마와,^n거기서 뻗어 나온 엉덩이와 다리는,^n흐트러진 꽃과 시든 꽃술 같았다.",
    31: "앨리스는──^n가운데가 둘로 갈라진 인형의 집에 팔다리가 붙잡혀,^n끼어 꼼짝도 할 수 없는 모양이었다.",
    32: "나",
    33: "대체 뭘 어떻게 하면 이렇게 되는 거야…….",
    34: "나는 우선 어이없다는 듯 한숨을 쉬었다.",
    35: "그러다 앨리스의 엉덩이가──살구색이 비칠 만큼 팽팽해진 속옷이,^n앨리스의 흐느낌에 맞춰 움찔움찔 떨리는 것을 깨닫고,^n황급히 시선을 돌렸다.",
    36: "나",
    37: "저기…… 뭘 하고 있는 거야, 앨리스.",
    38: "앨리스",
    39: "저…… 이 집에 심부름하러 왔어요.^n토끼 씨 부탁으로요.^n아무래도 저를 하녀로 착각한 모양이에요.",
    40: "앨리스",
    41: "　아아, 왜 저는 부탁을 받아들인 걸까요.^n　메리 앤이라는 이름도 아닌데,^n『착각해 줘서 다행이야』라니…….",
    42: "앨리스",
    43: "『이제 당당하게 이 집에 드나들 수 있어』라고^n　어째서 생각해 버린 걸까요.",
    44: "앨리스",
    45: "무엇보다 거기에 작은 병이 있었다고,^n어째서 마셔 버린 걸까요!",
    46: "앨리스",
    47: "지금까지 무언가를 먹거나 마실 때마다^n커졌다 작아졌다 했으니, 이번에도^n머리 한구석에서는 생각했을 텐데…….",
    48: "나",
    49: "어, 어어어…….",
    50: "대략적인 사정은 알았다──모르면서도 알기는 했지만,^n내 입에서는 여전히 한숨만 새어 나온다.",
    51: "내게 보이는 앨리스의 상태를 무심코 지적하려다,^n입을 다물었다.",
    52: "나",
    53: "(인형의 집에 억지로 몸을 밀어 넣고^n『커졌어』라고 소란을 피우는 것으로밖에 보이지 않는다는^n　말은──)",
    54: "나",
    55: "(할 수 없겠지, 응.^n　의사 선생님도 모두가 보는 세계를 무너뜨리는 짓은^n　하지 말아 달라고 했고…….)",
    56: "나",
    57: "그러니까…… 어떻게 하면 돼?^n잡아 빼면 될까.",
    58: "앨리스",
    59: "그렇게 하면 집이 무너지지 않을까요…….^n토끼 씨가 살 곳을 잃으면 불쌍해요.",
    60: "나",
    61: "이대로면 너도 불쌍한데.",
    62: "앨리스",
    63: "그래요. 저도 그렇게 생각해요!",
    64: "마음을 다잡고 다시 살펴보자,^n앨리스는 팔자눈썹을 더욱 늘어뜨리고,^n울음을 참고 있는 듯했다.",
    65: "나",
    66: "(이거, 혼자서 어떻게든 할 수 있지 않을까.)",
    67: "인형의 집 창문과 문에 붙잡힌 것은,^n한쪽 손과 한쪽 다리뿐이다.",
    68: "곡예 같은 자세라 복잡해 보이지만,^n진정하면 혼자 빠져나올 수 있을 것 같다.",
    69: "나",
    70: "(문제는 아마 앨리스가 진정할 수 없다는 거야.)",
    71: "그러다 문득 떠오르는 것이 있어,^n그녀 옆에 떨어진 『성서』를 주워 들었다.",
    72: "　이건 앨리스가 『성서』──^n『이상한 나라의 앨리스』를 따라 한 행동이니^n『성서』를 따르면 앨리스 안에서도 원래대로 돌아올지 모른다.",
    73: "해당 페이지를 찾아 읽었다.",
    74: "앨리스의 말대로 흰토끼에게 하녀로 오해받아 심부름을 갔다가,^n방 안에서 병의 내용물을 마셔 거대해지고 집 안에 빽빽하게^n갇혔다──고 적혀 있다.",
    75: "나",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1110.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1110_slots_00001_00075_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1110_slots_00001_00075_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
