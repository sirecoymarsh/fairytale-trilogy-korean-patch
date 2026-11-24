from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "오데트와 오딜의 방 앞에서 나는 문득 걸음을 멈췄다.^n──밤이 되었으니 오데트는 이미 깨어났을까.",
    2: "솔직히 오데트는 만나고 싶었지만,^n오딜과는 더 이야기하고 싶지 않았다.",
    3: "그녀가 오데트에게 품은 악의는^n접하고 있어서 기분 좋은 것이 아니다.",
    4: "나",
    5: "(오데트는 그렇게까지 험한 말을 듣는다는 걸^n　알고 있을까.^n　그…… 창녀라든가…….)",
    6: "나는 고민 끝에 주먹 뒤쪽을 톡…… 하고 살짝 갖다 대기만 하는^n어중간한 노크를 했다.",
    7: "나",
    8: "어…….",
    9: "대답은 없다.^n그 대신 주먹의 힘에 문이 움직였다.",
    10: "아무래도 제대로 닫히지 않았던 모양이다.",
    11: "나",
    12: "………….",
    13: "나는 다시 한번, 이번에는 안에 들리도록 문을 두드렸다.^n",
    14: "──역시 반응은 없다.",
    15: "그 대신.",
    16: "오딜",
    17: "언제까지 꾸물꾸물 꾸물꾸물.^n대체 뭘 그렇게 굼뜨게 구는 거야.",
    18: "오데트",
    19: "아…… 아, 오딜. 오면 안 돼…….",
    20: "무언가 심상치 않은 대화가 들려왔다.",
    21: "어이없음과 짜증 사이쯤인 듯한 오딜과,^n가느다란 목소리에 거부감을 담은 오데트.",
    22: "나는 무심코 문틈을 밀어 넓히며 안으로 들어갔다.",
    23: "몹시 무례한 짓을 저지르고 있다는 생각은^n완전히 안으로 들어간 뒤에야 따라잡았다.",
    24: "미안해하면서도 무의식중에^n등 뒤로 닫은 문에 빠져나갈 틈을 남긴 것은,^n들키지 않고 물러나기 위한 예방책이리라.",
    25: "오딜",
    26: "뭐야, 평소라면 얼른 나가서^n정원의 호수에서 달님과 이야기하고 있을 시간인데.^n언제까지 눌러앉아 있으면 음침해서 못 견디겠어.",
    27: "방 안으로 들어왔는데도 오딜의 목소리는 아직 멀다.",
    28: "나는 방이라고 하기에는 너무 넓은^n무대 장치 같은 전경을 한 바퀴 둘러보며,^n두 사람의 모습을 찾았다.",
    29: "오딜",
    30: "내게 밤이란^n여기서 혼자 있을 수 있는 귀중한 시간이거든.^n네 사정으로 팍팍 깎아 먹지 않을래?",
    31: "오데트",
    32: "미, 미안……해.^n조금 당황해서…….^n조, 조금만 더 있으면 돼…… 조금만 더, 오지 마.",
    33: "오딜",
    34: "새장이 끼익거리는 거, 귀에 거슬려.",
    35: "나",
    36: "(새장?)",
    37: "나는 오딜의 말에 맞춰 중앙의 『새장』을 올려다보았다.^n방 중앙에 자리 잡은 큰 나무의 꼭대기 가까운 굵은 가지에^n매달린 금빛 새장.",
    38: "아래에서는 안을 볼 수 없다.^n하지만 나무의 낮은 곳에서 뻗은 가지 위를 걸어가는^n오딜의 모습은 발견할 수 있었다.",
    39: "아무래도^n새장을 아래에서 받치듯 뻗은 그 가지가 통로가 되어,^n새장을 드나드는 데 쓰이는 모양이다.",
    40: "오데트",
    41: "시, 싫어……. 괜찮아, 괜찮으니까, 오딜.^n조금만 더 내버려 둬.^n곧 끝나. 끝날 거야…….",
    42: "오딜",
    43: "너 아까부터 그 말뿐이잖아.^n그러세요, 하고 내가 얼마나 기다렸을 것 같아?",
    44: "짜증이 앞서 말투도 다소 거칠어진 오딜의 목소리.^n나는 소리를 내지 않도록 조심하며 큰 나무로 다가간다.",
    45: "오데트가 걱정된다거나,^n오딜의 심술을 막으려는 건^n아니다.",
    46: "나는 그저 호기심에 져서^n비밀스러운 두 사람의 대화를 엿보려는 것이다.",
    47: "나",
    48: "(──그만두는 편이 좋아. 그만둬.^n　몰래 숨어 걷는 네 모습을 상상해 봐.^n　한심하고 추잡해.)",
    49: "나",
    50: "(들키면 어쩌려고.^n　분명 오딜에게 찍소리도 못 할 만큼 호되게 당하고,^n　오데트는 실망할 거야.)",
    51: "머릿속에서 그런 목소리가 들린다.^n처음부터 끝까지 옳은 말이라고 생각한다.^n그렇게 생각하면서도 내 발은 멈추지 않는다.",
    52: "검게 솟은 큰 나무 안은 속이 파여,^n나선형 계단이 되어 있었다.",
    53: "희미하게 빛나는 가짜 호수만이 광원이었지만,^n발밑을 확인하기에는 충분했다.",
    54: "오딜",
    55: "──그렇구나.^n평소보다 잔뜩 차려입느라 시간이 걸렸다고.",
    56: "오데트",
    57: "아, 아니야. 그런…… 그렇지 않아.^n그냥 왠지 손가락이 떨려서 이 장식이 채워지지 않아서…….",
    58: "두 사람의 대화를 들으며^n나는 계단을 끝까지 올라갔다.",
    59: "눈앞에는 아까 오딜이 건너던,^n새장 출입구로 이어지는 다리가 있다.",
    60: "그리 멀리 떨어진 것도 아니라,^n여기에 모습을 드러내면 새장 안의 두 사람에게도 들키겠지.^n게다가 대화를 엿듣기에는 여기로 충분하다.",
    61: "이것저것 견주어 본 내가 그렇게 계획을 세운 순간.",
    62: "오데트",
    63: "──꺄악!^n오, 오…… 오딜.",
    64: "오데트의 비명이 울려 퍼졌다.^n그 전후로 끼익끼익 새장이 삐걱거리는 소리가──",
    65: "새장은^n두 사람의 몸무게와 실랑이로 인한 흔들림에 삐걱거린 듯하다.",
    66: "발을 받침대에 올리고 치마를 걷어 올린 채,^n허벅지 중간까지 끌어올린 타이츠를^n벨트로 고정하려던 오데트와.",
    67: "그녀를 뒤에서 끌어안듯 하며^n지금 바로 내 눈앞에서^n오데트의 손으로부터 벨트 끝을 빼앗은 오딜과.",
    68: "오딜",
    69: "뭘 그렇게 겁탈이라도 당하는 여자처럼 비명을 지르고 그래.^n성가시니까 도와주겠다는 것뿐이잖아.^n고마워해도 모자랄 판에 꺄악은 무슨.",
    70: "오데트",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1125.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1125_slots_00001_00070_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1125_slots_00001_00070_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
