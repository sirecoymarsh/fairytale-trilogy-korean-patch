from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "가능하다면 게르다와는 다시 한번 이야기를 나누고 싶었다.",
    2: "게르다에게는 시간 낭비일 뿐이고,^n민폐가 될지도 모르지만──",
    3: "환자인데도 『성서』를 지니지 않고,^n자신이 게르다라는 사실도 좀처럼 인정하지 않던^n그런 태도의 그녀.",
    4: "나",
    5: "(혹시 게르다는^n『동화 증후군』이 낫기 시작한 걸까.)",
    6: "게르다",
    7: "──네.",
    8: "나",
    9: "아, 저기, 안녕.^n그…….",
    10: "댈 이름이 없다는 건 이럴 때 불편하다.",
    11: "게르다",
    12: "……낮에 왔던 사람?",
    13: "나",
    14: "으, 응.",
    15: "곧바로 문이 열리고 게르다가 얼굴을 내밀었다.",
    16: "나",
    17: "미안해, 자꾸 찾아와서.",
    18: "게르다",
    19: "괜찮아.^n그 뒤로 뭔가 기억났어?",
    20: "나",
    21: "구체적으로는 아무것도.^n가끔 기억의 그림자 같은 게 스쳐 지나가지만,^n이름 같은 중요한 건 전혀…….",
    22: "게르다",
    23: "그렇구나.^n역시 그렇게 간단히 되찾을 수 있는 건 아니네.",
    24: "나",
    25: "그런가 봐…….",
    26: "고개를 끄덕이며 나는 쉴 새 없이 생각했다.",
    27: "무슨 이야기를 할까.^n무슨 이야기를 해야 게르다가 오래 대화해 줄까.",
    28: "게르다가 다른 환자들과 다른 점은^n자기 세계에 나를 끌어들이지 않는다는 것이다.",
    29: "헨젤도, 고델 할머니도 아닌,^n기억을 잃고 『낙원』에 내던져진 사람이라고^n제대로 이해한 채 이야기를 나눠 준다.",
    30: "그런 만큼 『잘 모르는 이성』인 내게^n무방비한 태도를 보이지는 않지만.",
    31: "게르다",
    32: "──서서 이야기하기도 그러니 들어와.",
    33: "나",
    34: "어?",
    35: "이번에도 문간에서 상대해 줄 거라 생각했던 나는,^n게르다가 선뜻 들어오라고 권하자 놀라서^n그녀의 얼굴을 빤히 바라보았다.",
    36: "게르다",
    37: "나도 너와 이야기해 보고 싶었어.^n자, 들어와.^n별다른 대접은 못 해 주지만.",
    38: "나",
    39: "──고마워.^n그럼 실례할게.",
    40: "게르다의 방에는 두 가지 모습이 있었다.",
    41: "한쪽은 아늑해 보이는 북쪽 나라의 방이다.^n창밖에는 맑은 밤하늘이 보이지만,^n창틀에는 얼어붙은 눈이 들러붙어 있다. 가짜일 테지.",
    42: "벽난로 안에는 역시 가짜인 불이 붉게 타오르고,^n그 앞에는 흔들의자가 하나 놓여 있다.^n보기만 해도 온기로 가득 찰 것 같은 광경이다.",
    43: "게르다의 『성서』인 『눈의 여왕』은^n벽난로 위에 놓여 있었다.",
    44: "게르다",
    45: "──마음이 편치 않은 방이지.^n나도 이쪽만 사용해.",
    46: "게르다의 권유를 받아,^n벽난로 곁에 쌓인 나무 상자 하나에 걸터앉았다.^n게르다도 다른 상자에 앉았고 흔들의자는 비어 있었다.",
    47: "나",
    48: "저쪽은 보기만 해도 추워 보이니까.^n왠지 신기한 풍경이네.",
    49: "나는 따뜻한 방의 창밖으로^n눈보라를 바라보는 듯한 기분으로 반대편을 쳐다보았다.",
    50: "몸서리칠 만큼 아름답고,^n그렇기에 마음속 깊은 곳부터 얼어붙을 듯한^n온통 눈뿐인 풍경이었다.",
    51: "밤의 푸른빛을 머금은 눈보라가 옆으로 몰아치는 벽지.^n불안정하게 솟아올라 설산의 비탈을 표현한 카펫.",
    52: "저쪽에는 조명이 전혀 없다.^n이쪽 벽난로의 빛이 닿는 곳은 기껏해야 두 세계의 경계까지고,^n그 너머는 걸쭉하고 짙은 어둠에 갇혀 있다.",
    53: "벽이 막혀 있어야 할 끝조차 보이지 않는 어둠은,^n눈의 세계에 펼쳐진 끝없는 여정을 보여 주는 듯하다.",
    54: "나",
    55: "대단하네.^n정말 『눈의 여왕』 속 세상이야.",
    56: "게르다",
    57: "그러게…….",
    58: "이쪽은 『눈의 여왕』 원작에서^n게르다가 소꿉친구 카이와 지냈던 따뜻한 방을^n본뜬 것이리라.",
    59: "흔들의자는 두 사람에게 여러 이야기를 들려주었던^n둘이 무척 사랑한 할머니의 지정석이라,^n아마 그래서 비워 둔 것이리라.",
    60: "저쪽은 물론^n게르다가 카이를 찾아 떠난 얼음의 세계.^n추위가 혹독한 북쪽 나라의 험난한 설경일 것이다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1114.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1114_slots_00001_00060_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1114_slots_00001_00060_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
