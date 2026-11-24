from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "오늘 아침에 보여진 진찰실의 광경과,^n끌려간 그레텔을 데려온 낮의 기억.",
    2: "　게다가 아까 의사 선생님과 나눈 대화에서 떠오른^n『가짜 의사가 섞여 들어온 것은 아닐까』라는 생각 때문에,^n　나는 조금 불안한 마음으로 그레텔의 방으로 향했다.",
    3: "나",
    4: "(아니, 너무 깊이 생각하는 거겠지만.^n",
    5: "　──나는 걱정이 많고 과보호하는 오빠였던 걸까.)",
    6: "그레텔",
    7: "……헨젤 오빠?",
    8: "가느다란 목소리가^n문 너머에서 꿰뚫어 본 듯 나를 불렀다.",
    9: "나",
    10: "으, 응. 들어가도 돼?",
    11: "응, 하는 그레텔의 목소리를 듣고 문손잡이에 손을 댄다.",
    12: "그레텔은 찾아온 사람이 내가 아니어도,^n나라고 믿고 그렇게 부르는 걸까──^n어쩐지 부끄럽게 여기며 방에 들어갔다.",
    13: "그레텔",
    14: "오…… 오빠!",
    15: "그레텔은 역시 이불을 뒤집어쓰고 있었다.^n자락을 끌며 소라게처럼 질질^n문간에 선 나를 향해 걸어온다.",
    16: "나",
    17: "그레텔?^n대체 왜 그래. 또 무슨 일 있었어?",
    18: "눈동자 가득 눈물이 고여 금방이라도 쏟아질 듯한 것을 보고,^n아까의 불길한 예감이 되살아났다.",
    19: "그렇지만 그레텔의 촉촉한 눈동자는^n이 방을 찾을 때마다 마주치는 것 같기도 하다.",
    20: "그레텔",
    21: "저, 저기 있잖아…… 낮에 돌을 떨어뜨린 채 줍지 않고^n돌아와 버렸잖아…….",
    22: "그레텔은^n몇 번을 봐도 가슴이 조여 올 듯 가련한 눈빛으로,^n머뭇거리며 이야기를 시작했다.",
    23: "나",
    24: "아, 주우면서 돌아오기도 귀찮았고,^n중간부터 돌아가는 길을 알았으니 쓸모도 없어졌지.",
    25: "그레텔",
    26: "응…….^n하지만 또 그런 일이 생길까 봐 무서워서.^n나, 어제처럼 돌을 주워 두자고 생각하고…….",
    27: "나",
    28: "아아…….",
    29: "나는 『뒷문』으로 이어지는 문을 바라본다.^n일찌감치 이야기의 윤곽이 보이기 시작했다.",
    30: "그레텔",
    31: "그, 그랬더니 자, 자물쇠가…….^n저 문, 잠겨 있어서 안 열리고…….",
    32: "그레텔",
    33: "어…… 어, 언제 누, 누가…….",
    34: "그레텔은 가슴께의 『헨젤과 그레텔』을^n매달리듯 강하게 끌어안았다.",
    35: "　이 전개는 그녀의 그 『성서』에 적혀 있었다.^n『다음 날에는 뒤뜰로 가는 문이 잠겨 있어,^n　돌을 주울 수 없었습니다.』",
    36: "그레텔",
    37: "혹시──아, 아빠와 엄마가?^n돌이 있으면 우리가 돌아와 버리니까……?",
    38: "나",
    39: "(혹시 그레텔이 스스로 문을 잠갔다든가…….)",
    40: "어깨를 움츠리고 온몸을 떠는 그레텔을 안쓰럽게 여기면서도,^n나는 그런 생각을 하고 말았다.",
    41: "나",
    42: "(하지만 이렇게 두려워하는 걸 보면──^n　적어도 의식적으로 한 일은 아니겠지.)",
    43: "그레텔",
    44: "어…… 어떡하지, 오빠.^n이래서는 조약돌을 주우러 갈 수 없어…….",
    45: "훌쩍 코를 들이마시며 그레텔이 중얼거린다.^n이대로라면 느슨한 눈물샘이 완전히 풀려 버리는 것도^n시간문제일지 모른다.",
    46: "나",
    47: "(음, 어떡하지.^n　굳이 뒤뜰에 가지 않아도 정원에서 얼마든지 주울 수 있잖아.^n　낮에 떨어뜨린 걸 회수해도 되고.)",
    48: "나",
    49: "(하지만 아마 그레텔이 원하는 건^n　그런 게 아니라…….)",
    50: "나는 어쩔 줄 모르는 그레텔에게──",
    51: "조약돌이 없다면…….",
    52: "빵이다.",
    53: "아니, 조약돌이라면 다른 곳에도…….",
    54: "나",
    55: "(뭐, 여기서는 그거겠지.)",
    56: "나는 마땅한 흐름을 타기로 했다.",
    57: "나",
    58: "잠깐만 기다려, 그레텔.",
    59: "그레텔",
    60: "어……? 오빠?",
    61: "그레텔",
    62: "……!",
    63: "나",
    64: "기다렸지.",
    65: "운이 좋게도 그 뒤 곧바로^n저녁 식사 쟁반을 치우는 직원을 찾을 수 있었다.",
    66: "　이유도 말하지 않고 빵을 달라고 한 내게 아무것도 묻지 않고,^n『한창 자랄 나이니까』 하는 표정으로 응해 준 것도^n　무척 고마웠다.",
    67: "나",
    68: "그레텔, 빵을 얻어 왔어.^n너도 아까 먹었지.^n저녁 스튜에 딸려 나온 나머지인데──",
    69: "털썩, 하는 소리가 났다.^n그레텔의 어깨에서 이불이, 손에서는 『성서』가^n바닥으로 미끄러져 떨어진 것이다.",
    70: "그레텔은 작은 손을 내게 뻗고,^n할 말이 있는 듯 눈을 반짝이고 입을 뻐끔거리며^n불안한 걸음으로 이쪽을 향해 온다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1124.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1124_slots_00001_00070_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1124_slots_00001_00070_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
