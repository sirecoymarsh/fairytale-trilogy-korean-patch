from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "갑자기 나타난 나선 계단을 오르고 또 올라,^n끝까지 다다른 곳에 그 문이 있었다.",
    2: "커튼이 달린 작은 창이 있는,^n어딘지 모르게 귀여운 문이다.",
    3: "금속 명판이 걸려 있고, 거기에는^n라푼젤^n이라고 새겨져 있다.",
    4: "???",
    5: "──들어오세요, 열려 있답니다.",
    6: "노크하자 그런 목소리가 돌아왔다.^n그뿐인데도 가슴이 한 번 크게 뛰는 것을 느꼈다.",
    7: "아름다운 여자의 목소리.^n하지만 그것뿐 아니라 뭐랄까──기품 있고 다정해 보여서,^n어쨌든 『느낌이 좋다』고 생각했다.",
    8: "나",
    9: "시, 실례하겠습니다.",
    10: "어쩐지 등이 곧게 펴지고 목소리도 살짝 뒤집혔다.",
    11: "등 뒤로 문을 닫으며 나는 크게 숨을 들이마셨다.^n──굉장히 좋은 향기가 난다.^n꽃 같기도 비누 같기도 한, 머리가 멍해지는 향기.",
    12: "벽과 바닥은 돌로 되어 있지만 섬세한 무늬의 러그와 태피스트리가^n덮여 있어 차가운 인상은 없다.",
    13: "방 중앙에는 망원경이 있고, 그 원통 끝은 아무래도^n돔 형태로 솟은 높은 천장에 그려진^n섬세한 천체도를 향하고 있다.",
    14: "결코 넓지는 않은, 조금 은신처 같은 천문대──^n분위기만큼은 그런 느낌이다.",
    15: "보기에는 가구가 적어서 무척 검소한 인상을 준다.^n이 방의 어디에서^n저토록 멋진 향기가 흘러나오는 걸까?",
    16: "???",
    17: "안녕하세요.^n오늘은 이렇게 날씨가 맑답니다.",
    18: "창가에서 이쪽을 돌아본 사람을 보고 단번에 납득했다.^n──이건 아름다운 여자에게서 나는 향기다.",
    19: "부드러운 미소를 띤 그 사람은,^n헐렁한 후드 망토로 온몸을 감싸고 있다.^n안경을 쓰고 방금 전까지 읽었을 책을 막 덮은 참이다.",
    20: "촌스러운 차림이었지만 촌스러운 사람이라고는 생각하지 않았다.^n편안한 생활을 위해 안경과 후드 망토를 걸쳤지만,^n그래도 미인의 분위기가 전해져 온다──그런 느낌이다.",
    21: "그녀는 안경 너머의 눈을 깜빡이며 나를 보고 있었지만,^n이윽고 손에 든 책을 덮고 안경을 치웠다.",
    22: "???",
    23: "──창가에 있으면 햇살이 포근하게 느껴져서^n이런 한낮부터 하품이 나올 정도예요.^n정말 좋은 날씨라 다행이에요, 고델 할머님.",
    24: "나",
    25: "네……?",
    26: "???",
    27: "날씨가 좋으면 허리 통증도 누그러지잖아요.^n하지만 이따가 제가 허리는 제대로 주물러 드릴게요.^n저녁이면 추워질지도 모르니까요. 그렇죠, 할머님.",
    28: "나",
    29: "할머님……?",
    30: "나는 주변을 둘러보았다.^n방 안에 있는 것은 그녀와 나, 단둘뿐.^n그리고 그녀의 눈동자는 똑바로 나를 향하고 있다.",
    31: "나",
    32: "저, 저는 할머님이 아니에요.",
    33: "나는 간신히 호소했다.^n성별도 나이도 정반대라니,^n어떤 의미에서는 회색펠리컨보다 훨씬 심각하게 다르다.",
    34: "하지만 그녀는 피식 웃으며 당연하다는 듯 나를 타일렀다.",
    35: "???",
    36: "어머, 할머님도 참 농담을.^n이 방에 찾아오는 분은 할머님뿐이에요.^n그걸 가장 잘 아는 분은 할머님이 아니신가요.",
    37: "나",
    38: "(으, 와…….)",
    39: "진심으로 이 나를 『할머님』이라고 부르는 모양이다.^n게다가 아무래도 아는 사람과 겹쳐 보는 식으로.",
    40: "나는 그 자리에서 달아나려다 가까스로 멈췄다.^n그녀의 아름다운 얼굴과 고요한 눈동자, 차분한 분위기 같은^n호감 가던 모든 것이 한꺼번에 왠지 오싹하게 느껴졌다.",
    41: "광기라는 것은 앨리스에게서도 느꼈지만,^n그쪽과 달리 이쪽은 웃어넘길 수 없다.^n솔직히 말하자면──무섭다.",
    42: "나",
    43: "저기…… 너는 누구야?",
    44: "등에 축축하게 땀을 흘리며,^n내가 물은 것은 그런 말이었다.^n종잡을 수 없는 그녀의 정체부터 알고 싶었다.",
    45: "???",
    46: "어머, 오늘은 왜 그러세요, 할머님.^n이렇게 날씨 좋은 날 몸이 안 좋으신 건 처음이에요.",
    47: "???",
    48: "저에 관해서 할머님이 모르는 일은 없으시잖아요.^n태어나자마자 저를 데려와,^n이곳에서 길러 주셨잖아요.",
    49: "???",
    50: "저기 보이는 밭. ──어머니가 너무나 먹고 싶어 한 탓에,^n할머님이 갓난아이인 저와 맞바꾸어 수확을 허락한^n저 채소에서 이름을 지어 주신 걸 잊으셨나요?",
    51: "나",
    52: "(──어라.^n　그건 혹시…….)",
    53: "엉뚱한 이야기인데도 짚이는 것이 있었다.^n아무것도 떠올리지 못할 머리가 기적처럼 돌아가서,^n어떤 기억 하나를 끌어낸다.",
    54: "나",
    55: "라푼젤!",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1105.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1105_slots_00001_00055_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1105_slots_00001_00055_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
