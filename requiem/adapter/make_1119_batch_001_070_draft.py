from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "낮에는 『백조』로 지내는 오데트는,^n해가 질 때까지 어떻게 시간을 보낼까.",
    2: "그런 호기심이^n나를 오데트와 오딜의 방 앞에 세웠다.",
    3: "나",
    4: "(아마 그 방 어딘가에서 잠들어 있겠지만.)",
    5: "속으로 그렇게 짐작하며 문을 두드리려 주먹을 든 순간.",
    6: "나",
    7: "──으앗!",
    8: "문이 열리는가 싶더니,^n틈새로 누군가의 손이 뻗어 나와 내 팔을 붙잡았다.",
    9: "나",
    10: "어, 뭐, 뭐야……!?",
    11: "사정없이 파고드는 손가락의 힘에 움츠러든 사이,^n나는 세게 끌려가 방 안으로 나뒹굴었다.",
    12: "나",
    13: "아, 아야야…….^n",
    14: "갑자기 무슨 짓이야!",
    15: "나는 붙잡힌 팔을 빼내며^n눈앞에 선 오딜에게 항의했다.",
    16: "오딜",
    17: "잠깐 하고 싶은 말이 있었거든.",
    18: "나",
    19: "그냥 평범하게 불러 세우면 되잖아…….",
    20: "오딜",
    21: "이왕이면 재미있는 쪽이 좋잖아. 뭐든지.",
    22: "나",
    23: "재미없었어.",
    24: "오딜",
    25: "거울이 있어서 네 얼굴을 볼 수 있었다면 좋았을 텐데.",
    26: "오딜은 활짝, 최대한 기품 있게 웃어 보인다.^n하지만 내게는 그 가면 뒤에서^n끈적하고 검은 안개가 피어오르는 듯 보였다.",
    27: "오데트와 똑같은 얼굴이 오데트와는 다르게 일그러지는 모습은^n신기하고, 기괴하고, 불쾌하다.",
    28: "나",
    29: "……하고 싶은 말이 뭔데?",
    30: "오딜",
    31: "너, 그 뒤로 오데트를 만났지?",
    32: "나",
    33: "만났어. 그게 뭐?",
    34: "오딜",
    35: "역시 그랬네.^n어젯밤 이 방에 나타난 네 안색을 보고 난,^n아아, 또인가 싶었거든.",
    36: "나",
    37: "또라니, 뭐가?",
    38: "오딜",
    39: "………….",
    40: "오딜은 드물게 입을 다물었다.^n붉은 눈동자가 나를 바라보다가 문득 비껴가고,^n그녀는 무언가 골똘히 생각하는 모습이었다.",
    41: "──어차피 못된 일을 꾸미고 있을 것이다.^n──아마 오데트의 마음을 찢어 놓을 만한 일을.",
    42: "내 안의 고집스러운 내가 잔뜩 경계하며 속삭인다.",
    43: "동시에 이상하기도 했다.^n이제 막 만나 잘 알지도 못하는 두 소녀 중,^n한쪽을 싫어하고 다른 한쪽 편을 드는 내 마음이.",
    44: "오딜",
    45: "너, 그 애한테 반했지?",
    46: "나",
    47: "뭐……!",
    48: "오딜이 마침내 침묵을 끝내나 했더니,^n입에 담은 것은 터무니없는 말이었다.",
    49: "나",
    50: "무, 무슨 소리를 하는 거야.^n우리는 어제 처음 만났을 뿐이라고?",
    51: "오딜",
    52: "아아, 여자를 다뤄 본 적이 없구나.^n뭐든 전부 서툴러.",
    53: "오딜은 더없이 얄미운 몸짓으로 어깨를 으쓱했다.",
    54: "그리고 다음 순간 문득 정색하는가 싶더니,^n소리 없이 가까이 다가와 낮은 목소리로 속삭였다.",
    55: "오딜",
    56: "──그 애는 조심해.",
    57: "나",
    58: "어…….",
    59: "오딜",
    60: "그 여자는 호수는커녕 늪 같은 여자니까.^n귀엽다, 무력하다, 순수하다, 가련하다──그 여자의 모자람을^n그런 식으로 받아들이고 헤벌쭉하는 놈들이 많았지만…….",
    61: "오딜",
    62: "전부 변변찮은 결말을 맞았지.^n남자에게 매달리고 남자를 파멸시켜야만 구원받는^n구제 불능의 창녀. 그게 그 여자야.",
    63: "나",
    64: "……창녀?",
    65: "오딜",
    66: "음탕하고 불쌍한 여자라는 뜻이야.^n남자에게 달라붙어, 빠뜨리고, 탐하고, 모조리 빨아먹으며,^n자기가 행복해질 생각밖에 하지 않지.",
    67: "오딜",
    68: "상대를 붙잡아 둘 수 있다면 다리를 벌리는 것도 마다하지 않아.^n사랑은 한 조각도 없어도 그런 척은 할 수 있어.^n미끼로 눈앞에 매달아 보이는 것도 말이야.",
    69: "나",
    70: "……오데트는 달라.",
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1119_slots_00001_00070_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1119_slots_00001_00070_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
