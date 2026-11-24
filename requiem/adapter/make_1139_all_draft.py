from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
TARGETS = {
    1: "낮에는 그렇게 날씨가 좋았는데,^n밤이 되자 탁한 구름이 완전히 내려앉아,^n금방이라도 떨어질 듯 무겁게 짓누른다.",
    2: "그것이 호숫가에 다다른 순간 갑자기 걷혔다.",
    3: "달빛은 언제나 오데트를 지켜보고 있는 것일까.^n그런 생각이 들 만큼 오데트는 아름다웠다.",
    4: "호수에 반사된 빛 알갱이에 물들어, 무거운 밤 속에^n금빛 머리카락과 흰 피부가 아스라이 떠오른다.",
    5: "오데트",
    6: "──낮에 그런 일이 있었군요. 무서워요.",
    7: "내 이야기를 다 들은 오데트는 나직이 중얼거렸다.^n어딘가 실감이 나지 않는 말투였지만 그럴 만도 하다.",
    8: "나",
    9: "오데트는 아무것도 몰라──기억나지 않지?",
    10: "오데트는 백조 조형물의 모습으로^n다과회 자리에 있기는 했지만, 그렇다고 무언가를 알 리는 없다.^n알았다면 동화가 아니라 괴담이다.",
    11: "오데트",
    12: "네. 저는 낮 동안에는 백조니까요…….^n낮에 있었던 일은 아무것도 몰라요.",
    13: "나",
    14: "그렇지.^n오딜은 뭐라고 하지 않았어?",
    15: "오데트",
    16: "…………!",
    17: "아무 뜻 없이 던진 내 질문에 왜인지 오데트는 크게 몸을 떨었다.^n싫은 일을 떠올린 듯 뺨이 굳어 있다.",
    18: "오데트",
    19: "──아무 말도.^n다 함께 다과회를 했던 일을 조금…….",
    20: "오데트는 떨리는 어깨를 멈추려 스스로를 끌어안았다.",
    21: "평소보다 차가운 바람이 우리 사이를 스쳐 간다.^n오데트의 드레스에서 살갗의 그림자가 희미하게 비칠 만큼 얇은 소매가^n바람에 휘날려 팔랑팔랑 물결쳤다.",
    22: "나",
    23: "……돌아갈까. 춥기도 하고 감기에 걸릴지도 몰라.",
    24: "오데트",
    25: "네…….",
    26: "오데트는 고개를 들어 나를 보았다.^n차가운 바람보다 더 가차 없는 무언가에 휘말려 떠내려갈 듯,^n필사적으로 매달리는 듯한 눈빛이었다.",
    27: "나",
    28: "왜 그래, 오데트.^n무슨 일이 있으면 말해 줘.",
    29: "오데트",
    30: "──불길한 예감이 들어요.",
    31: "나",
    32: "오데트……?",
    33: "오데트는 불안정한 걸음으로 앞으로 나아와,^n나와 그녀 사이의 얼마 안 되는 거리를 좁혔다.",
    34: "내 손을 잡으려 들었던 손을 닿기 직전 조심스레 거둔다.^n망설이듯 굽은 손끝은 잘게 떨리고 있었다.",
    35: "오데트",
    36: "왕자님, 지크프리트 님.^n무슨 일이 있어도 저를 선택해 주실 건가요?",
    37: "나",
    38: "무, 무슨 말을…….",
    39: "나는 되물으려던 말을 끊었다.^n오데트에게는 『올바른』 말 이외에는 분명 닿지 않는다.",
    40: "백조의 저주를 풀기 위해서는 영원한 사랑을 맹세해야 한다.^n그러니 『지크프리트』는,^n연회 자리에서 오데트를 반려자로 맞겠다고 약속하는 것이다.",
    41: "나",
    42: "『──맹세할게. 나는 너를 선택하겠어.』",
    43: "대답한다기보다 외운 문구를 읊으며,^n무거운 대사라고 생각했다.^n그녀에게 가짜 이름을 댔을 때 짊어진 것이다.",
    44: "오데트",
    45: "고마워요…….^n고마워요, 지크프리트 님.",
    46: "하지만 오데트를 보고 있으면 진심으로 후회 따위 없다고 생각하게 된다.^n빛을 품은 꽃봉오리가 갑자기 벌어져,^n부드러운 빛을 내며 피어나는──그런 미소다.",
    47: "오데트",
    48: "저도 믿고 있어요.^n제가 당신을 생각하듯,^n당신도 분명 저를 생각해 주고 계시다고.",
    49: "오데트는 기도하듯 『성서』를 끌어안았다.",
    50: "오데트",
    51: "미안해요, 조금 불안해졌어요.^n왜일까요──저도 참 바보네요.",
    52: "오데트",
    53: "왕자님을 만나면 이것도 말하고 저것도 말해야지 하고^n계속 생각하고 있었는데요.^n",
    54: "──에취!",
    55: "오데트가 평소의 얼굴로 돌아온 순간 재채기가 나왔다.^n우리는 이번에야말로 병동으로 돌아가려고 걷기 시작했다.",
    56: "돌아가는 길에 오데트는^n『말하려고 했던 것』의 일부를 내게 들려주었다.",
    57: "백조 친구들의 이야기.^n다과회에 인간 모습으로 참석했을 때 먹고 싶었던 과자 이야기.^n오딜이 던진 심술 직전의 유머 이야기.",
    58: "오데트",
    59: "──맞다, 얼마 전 당신이 말한 책을 빌렸어요.^n지금 읽고 있는 중이에요.^n저는 읽는 속도가 느리지만…… 아주 재미있어요.",
    60: "나",
    61: "뭐였지?",
    62: "──아.",
    63: "분명 좋아하는 동화를 묻기에^n무심코 『피터 팬』이라고 대답했다.",
    64: "다음에 만날 때까지 다 읽어 둘게요, 하고 웃으며^n오데트는 자기 방으로 돌아갔다.",
}


def main() -> int:
    expected = set(range(1, 65))
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1139.gsc" and int(item.get("slot", -1)) in expected:
                rows[int(item["slot"])] = item
    if set(rows) != expected or set(TARGETS) != expected:
        raise SystemExit("coverage mismatch")
    entries = []
    for slot in sorted(expected):
        row = rows[slot]
        source = str(row["source_text"])
        target = TARGETS[slot]
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {slot}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": row["uid"], "source_text": source, "source_raw_sha256": row["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 전"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1139_slots_00001_00064_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    path = PROJECT / "packets" / "drafts" / "1139_slots_00001_00064_draft.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "entries": len(entries), "output": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
