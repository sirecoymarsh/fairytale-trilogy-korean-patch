from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "꿈을 꾼 것 같지만 거의 기억나지 않는다.",
    2: "밤사이 나는 몇 번이나 얕은 잠에서 깨어나,^n푸른 어둠에 물든 하얀 방을 보았다.",
    3: "그럴 때마다 생각했다.^n──꿈이 아니었구나.",
    4: "그래도 새벽녘에는 기분 좋은 파도에 휩쓸려,^n다시 잠의 바다에 빠져들기 시작했던 것 같다.",
    5: "나",
    6: "──!?",
    7: "그래서 갑자기 울려 퍼진 소리에^n심장이 멎는 줄 알 만큼 깜짝 놀랐다.",
    8: "나",
    9: "(어…… 뭐야. 무슨 소리지?)",
    10: "나",
    11: "(뻐꾸기시계……?)",
    12: "시간이 될 때마다 문을 열고 인사하는^n하얀 뻐꾸기의 모습을 떠올린다.",
    13: "하지만 텅 빈 내 병실에는^n그런 것이 없었을 텐데.",
    14: "나",
    15: "………….",
    16: "무거운 눈꺼풀을 비비며 몸을 일으킨다.^n커튼을 젖히자 상쾌한 아침 햇살이 비쳐 들었다.",
    17: "나",
    18: "어…… 어!?",
    19: "방을 한 바퀴 둘러본 나는 내 눈을 의심했다.",
    20: "어제는 분명 아무것도 없었던 벽에^n커다란 뻐꾸기시계──처럼 생긴 장치가 있다.",
    21: "뻐꾸기시계는 마지막 울음소리를 남기고^n문 안으로 사라지는 참이었다.",
    22: "나는 멍하니 입을 벌린 채 그쪽으로 다가갔다.",
    23: "나",
    24: "(뭐지, 이거.^n　모니터……?)",
    25: "도무지 알 수가 없었다.",
    26: "아무리 봐도 모니터로밖에 보이지 않는 것이^n왜 갑자기 나타났는지.^n뻐꾸기시계 같은 디자인에 무슨 의미가 있는지.",
    27: "왜 지금 뻐꾸기가 울었는지.^n애초에 내가 줄곧 자고 있던 이 방에^n어떻게 이런 물건을 설치했는지.",
    28: "나",
    29: "(아직도 꿈을 꾸고 있다든가…….)",
    30: "꿈인지 확인하려고 자기 뺨을 꼬집는 짓을^n정말로 해 보는 건 처음이다.",
    31: "평범하게 아프다.^n하지만 이 통증마저 꿈속 일이 아닐까 하는 생각까지 든다.",
    32: "그때 모니터에 빛이 들어왔다.^n깔끔하고 반짝이는 모니터처럼 보이는데도,^n한동안 지지직거리며 잡음이 흘렀다.",
    33: "나",
    34: "하아……!?",
    35: "이윽고 화면에 비친 것을 보고,^n나는 얼빠진 소리를 흘렸다.",
    36: "어제 끌려갔던 진찰실 안.^n어딘가에 설치된 카메라가 찍은 영상일까.",
    37: "앨리스",
    38: "『……네, 난 원래 몸이 따뜻해.^n　그러니까 그 정도면 딱 좋아요, 선생님.^n　열이 나는 건 아니야.』",
    39: "그 『초록색 액체에 잠긴 테디 베어』가 늘어선^n선반 앞에 앨리스와 그레텔이 서 있다.",
    40: "평소 옷을 벗고 팬티만 걸친 모습으로.",
    41: "두 사람의 새하얀 피부가 쾅 하고 내 머리를 내리친다.^n나는, ──나는 대체 무엇을 보고 있는 거지?",
    42: "의사",
    43: "음, 확실히 늘 높은 편이고 본인이 그렇다면…….^n하지만 몸이 안 좋아지면 바로 말해야 한다.",
    44: "앨리스",
    45: "네, 알고 있어요, 선생님.",
    46: "진찰이라는 것이겠지.^n앨리스는 부끄러운 기색도 없이,^n오히려 자랑스럽게 가슴을 내미는 듯한 자세다.",
    47: "크고 무거워 보이는 그 가슴의 살이^n흘러넘치거나 늘어지지 않고^n팽팽하고 둥글게 솟아 있는 것이 신기했다.",
    48: "의사",
    49: "그레텔은 괜찮아 보이는구나. 체온은 정상이고.",
    50: "그레텔",
    51: "으, 으…….",
    52: "반대로 그레텔은^n당장이라도 부끄러움에 사라질 듯 새빨간 얼굴로,^n안절부절못하며 가슴을 가리려 팔을 꼼지락거리고 있다.",
    53: "의사",
    54: "아, 안 돼. 가리면 안 되지.^n제대로 보여 주렴.",
    55: "그레텔",
    56: "으아…….",
    57: "의사 선생님의 말에 그레텔은 흠칫 몸을 떨었다.^n굳게 다문 입술로 비명 같은 소리를 흘리면서,^n팔을 옮겨 가슴을 드러낸다.",
    58: "앨리스와 달리 굴곡 없는 몸이었다.^n어디를 만져도 부드러울 듯한 살집에,^n가슴께만 다른 곳보다 아주 조금 도톰하다.",
    59: "앳된 가슴인데도^n그 끝이 분홍빛으로 물들어 뾰족하게 솟은 모습이^n왠지 균형에 맞지 않았다.",
    60: "나",
    61: "──읏.",
    62: "나는 어느새 손을 세게 움켜쥐고 있었다.^n조금만 움직여도 손바닥이 흠뻑^n차가운 땀에 젖은 게 느껴진다.",
    63: "나",
    64: "(왜 이런 게. 어째서.^n　이 모니터는 내게 이걸 보여 주려고 나타난 거야?^n　어째서. 무슨 의미라도 있는 거야?)",
    65: "나는 눈을 돌릴 수 없었다.^n어젯밤 라푼젤이 내게 바싹 다가왔을 때와 똑같은,^n거미줄 같은 무언가가 온몸을 옭아매고 있다.",
    66: "의사",
    67: "이야, 너희는 참 대조적이구나.^n앨리스는 발육이 좋네.^n그레텔은 늦은 편이고.",
    68: "그레텔",
    69: "──읏!^n으, 크으……!",
    70: "의사",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1116.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1116_slots_00001_00070_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1116_slots_00001_00070_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
