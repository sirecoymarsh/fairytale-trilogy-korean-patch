from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "라푼젤",
    2: "안녕하세요, 할머님.^n오늘도 날씨는 좋지만 바람이 조금 강한 듯하네요.",
    3: "창가에서 이쪽을 돌아본 라푼젤은^n후드가 드리운 그림자 속에서 얌전히 미소 짓고 있었다.",
    4: "나",
    5: "……안녕.",
    6: "내 시선을 튕겨 내듯 안경 렌즈가 하얗게 빛난다.",
    7: "어젯밤에 본 정열적이고 『가감 없이 드러난』 얼굴이 거짓말 같다.^n라푼젤 자신도 잊어버린 게 아닐까 싶을 만큼.",
    8: "나는 내 가슴에 분명히 매달렸던 라푼젤의^n달아오른 체온과 기대어 온 무게를 떠올리려 했지만,^n잘되지 않는다. 지금 눈앞의 모습으로 덮여 간다.",
    9: "나",
    10: "……어젯밤에는, 그. 미안해.",
    11: "나는 라푼젤은 이해하지 못할^n사과의 말을 입에 담았다.^n그 말을 하려고 찾아온 셈이었으니까.",
    12: "라푼젤",
    13: "……!",
    14: "표정은 변하지 않았지만,^n그 뺨에서 순식간에 핏기가 가시는 것을 알 수 있었다.",
    15: "라푼젤",
    16: "무슨 말씀이신가요, 할머님.^n어젯밤은 평소와 똑같은──아무 일도 없는 고요한 밤이었어요.^n차라리 따분할 정도로요.",
    17: "나",
    18: "(……아아.)",
    19: "　내게는 진심 어린 사과지만 라푼젤에게는^n『할머님』이 밤의 그녀에 관해 넌지시 떠본 것으로^n　받아들일 수 있는 말이고.",
    20: "『왕자님』과 몰래 만난 비밀을^n들킨 게 아닐까 경계한 것이리라.",
    21: "라푼젤",
    22: "저는 이곳에서 나가지 않아요.^n그리고 할머님 말고는 아무도 이곳에 오지 않아요.^n──그렇지요? 알고 계시잖아요, 할머님.",
    23: "분명 말수도 늘었고,^n하지 않아도 될 말까지 해 버리는 걸 보니,^n아무래도 그녀는 거짓말에 서툰 모양이다.",
    24: "몰래 만남을 이어 가는 『라푼젤』 역할에는^n본래 어울리지 않는 사람일지도 모른다.",
    25: "너무 노골적이고 허술한 거짓말에^n내 가슴은 걷잡을 수 없이 답답해졌다.",
    26: "나",
    27: "(……나는 할머님이 아니야.)",
    28: "그런 반발심도 있었다.",
    29: "라푼젤",
    30: "왜 그러시나요, 할머님.^n아무 말도 없이 그런 곳에 계속 서 계시고…….",
    31: "대답할 말을 잃은 내 태도가^n라푼젤의 불안을 부추기고 만 듯했다.^n그녀가 안경 너머로 내 눈치를 흘끗거리는 게 보였다.",
    32: "나",
    33: "아니.^n그야 따분하겠다고 생각했을 뿐이야.^n이런 곳에 줄곧 있는 것보다 밖에 나가 보고 싶잖아.",
    34: "라푼젤",
    35: "………….^n정말 왜 그러시나요.^n오늘은 평소에 하지 않으시던 말씀만 하시고…….",
    36: "나",
    37: "(미안해, 혼란스럽게 해서.^n　하지만 할머니 역할 같은 건,^n　어떻게 해야 할지 모르겠고…….)",
    38: "나",
    39: "(오늘은 어제 일을 사과하러 왔을 뿐이고,^n　정말 그뿐인데…….)",
    40: "마음속으로 변명하다 보니 허무한 기분이 들기 시작했다.",
    41: "　애초에 저마다의 이야기에 빠져 있는 라푼젤들의^n『망상』에 맞춰 줄 의무 같은 건 내게 없다.",
    42: "라푼젤",
    43: "밖이라니요.^n저는 이제 와서 바라지 않아요.^n이곳에서 이렇게 살아갈 수 있는 것만으로 충분해요.",
    44: "라푼젤",
    45: "바깥세상에는 무엇이 있을지 모르니까요.^n무서워요.",
    46: "나",
    47: "어…….",
    48: "어쩐지 라푼젤의 말에 위화감을 느껴^n나는 그녀의 옆얼굴을 바라본다.",
    49: "거짓말에 서툰 그녀가 지금 입에 담은 말은^n진심처럼 들렸다.",
    50: "진짜 『라푼젤』이라면 동경했을 터인,^n탑의 창문에서 보이는 『바깥세상』.",
    51: "하지만 눈앞의 라푼젤이 그곳을 향해 보내는 시선은^n분명 빛바래고 평평했다.",
    52: "나",
    53: "라푼젤……?",
    54: "라푼젤",
    55: "네, 바깥은 제게 필요하지 않아요.^n그런 억지는 부리지 않을 테니 안심하세요.",
    56: "라푼젤",
    57: "──그저.",
    58: "라푼젤은 나를──『할머님』을 보았다.",
    59: "라푼젤",
    60: "다른 부탁 하나를 들어 주실 수 있을까요?",
    61: "나",
    62: "으…… 응.",
    63: "그리고 라푼젤이 입에 담은 『부탁』은^n여러 의미에서 예상 밖이었다.",
    64: "라푼젤의 방에서 나온 나는^n복도를 걷다가 처음 마주친 어른에게^n곧바로 말을 걸었다.",
    65: "의사",
    66: "뭐라고, 그림 도구? 유화?",
    67: "나",
    68: "네. 라푼젤이 그림을 그리고 싶대요.",
    69: "의사",
    70: "　흐음.^n『라푼젤』에 그런 장면이 있었던가.",
    71: "나",
    72: "없을 거예요.",
    73: "의사",
    74: "없어? 없지. 응. 없을 줄 알았어.^n그럼 뭐지? 대체 왜 그런 걸.",
    75: "나",
    76: "그저 그림을 그리고 싶은 것 아닐까요.",
    77: "의사",
    78: "그저, 말이지. 그렇군.^n본래의 그녀가 바라는 일일지도 모르겠네.^n낫기 시작했다는 뜻이려나.",
    79: "의사",
    80: "──뭐, 좋아. 전해 둘게.",
    81: "나",
    82: "네. 감사합니다.",
    83: "나",
    84: "(……본래의 그녀라.)",
    85: "라푼젤은 『라푼젤』의 가면을 쓰기 전에는^n그림 그리기를 취미로 삼던 소녀였을까.",
    86: "어느 쪽이든 어젯밤 밀어내 버린 것과,^n아까 쓸데없는 말을 꺼내 겁먹게 한 것에 대한^n보상이 되면 좋겠다.",
    87: "의사 선생님을 배웅하며 나는 그런 생각을 했다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1120.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1120_slots_00001_00087_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1120_slots_00001_00087_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
