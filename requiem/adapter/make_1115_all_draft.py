from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "나",
    2: "(역시 피곤하네.)",
    3: "여기저기 돌아다니고, 목욕하고, 다시 돌아다니고.^n눈 깜짝할 사이에 소등 시간이 되었다.",
    4: "나는 오늘 하루 동안 그럭저럭 완성된^n머릿속 지도를 따라 내 방으로 돌아왔다.",
    5: "???",
    6: "안녕.",
    7: "나",
    8: "……?",
    9: "그때 내 방 앞에서 누군가 나를 불러 세웠다.",
    10: "뒤를 돌아보니 키가 큰 남자가 서 있다.^n흰 가운을 입었고 가슴에는 의사 선생님이나 간호사들과^n똑같은 명찰이 달려 있었다.",
    11: "즉 이 사람도 『낙원』의 직원이자^n어른들 무리에 속한 한 명이다.^n──그런데도 왠지 이 사람은 조금 다른 느낌이 들었다.",
    12: "어째서일까. 붙임성 좋은 미소 때문인가?^n아니면 주렁주렁 늘어진 장신구에서^n장난기가 느껴지기 때문인가?",
    13: "???",
    14: "안녕, 나나시 군.^n이제 자려던 참이니?^n오늘 하루 수고했어.",
    15: "나",
    16: "네, 고맙습니다…….^n당신은?",
    17: "???",
    18: "나?^n나는…… 어디 보자.",
    19: "그저 이름이나 직책을 물었을 뿐인데,^n남자는 고개를 갸웃하며 뭔가 고민스러운 표정을 짓는다.",
    20: "???",
    21: "음, 나는 말이지.^n네가 정해 주지 않으면 아무것도 될 수 없어.^n네가 자신을 모르는 것처럼 나도 모르거든.",
    22: "나",
    23: "무슨 뜻인가요?",
    24: "???",
    25: "내 역할 말이야.^n넌 자신이 『누구』인지 모르는 모양이니,^n내가 누구인지도 알 수 없는 거지.",
    26: "나",
    27: "………….",
    28: "어른이란 좀 더 남이 알아듣도록^n제대로 말하는 생물이 아니었던가.",
    29: "나는 아마 앨리스를 볼 때와 마찬가지로^n──그러니까 의심스러운 마음을 조금도 감추지 않은 눈으로^n그를 마주 보았을 것이다.",
    30: "하지만 그는 신경 쓰는 기색도 없이 온화하게 웃었다.",
    31: "???",
    32: "예를 들면 말이야. 앨리스에게 나는^n체셔 고양이이자 모자 장수이자 겨울잠쥐이자 삼월 토끼야──^n그 아이에게는 여러 가지가 필요하니까.",
    33: "???",
    34: "그레텔에게는 돌아갈 때 도와주는 오리 씨.^n오빠가 되기에는 너무 늙었고, 아빠가 되기에는 너무 젊거든.",
    35: "???",
    36: "라푼젤과 오데트에게는^n왕자님이 될 뻔했지만 거절했어.^n그것만은 안 되거든.",
    37: "???",
    38: "게르다…… 그 아이도 아직^n자기가 누구인지 모르니까 말이야.^n까마귀나 순록이 될 마음의 준비는 돼 있지만.",
    39: "나",
    40: "아…….",
    41: "한바탕 이야기를 듣고 나서야 나는 겨우 이해했다.",
    42: "환자들을 상대할 때^n그가 맡는 역할에 관한 이야기였던 모양이다.",
    43: "나",
    44: "(환자의 망상에 맞춰 주는 일을 담당하는^n　의사나 간호사라는 뜻인가.)",
    45: "처음에 한 이해할 수 없는 말은, 나라는 환자에게 기억이 없어^n어느 이야기의 누구를 연기했는지 알 수 없으니^n자기가 맡을 역할도 모른다는 뜻이었던 모양이다.",
    46: "──처음부터 알아듣기 쉽게 제대로 설명하면 될 텐데.",
    47: "휘둘린 것은 불만이었지만,^n재미있는 사람이라는 생각은 들었다.^n적어도 의사 선생님보다는 좋아질 것 같다.",
    48: "그는 내가 알아서 이해한 게 기분 좋았는지^n쉴 새 없이 이야기를 이어 갔다.",
    49: "???",
    50: "지금은 이곳에 없지만,^n도로시의 세 시종을 혼자 맡은 적도 있어.",
    51: "???",
    52: "클라라에게는 생쥐였던가.^n가구야 공주 때는 한심한 구혼자 다섯 명을^n혼자서 맡았다가 후회했지.",
    53: "나",
    54: "『오즈의 마법사』에 『호두까기 인형』──",
    55: "???",
    56: "그래, 거기에 『다케토리 이야기』까지.^n가구야 공주였던 아이는 정말 선택이 고풍스러웠지.^n그런 아이는 전에도 후에도 그 아이뿐이었어.",
    57: "???",
    58: "──뭐, 네가 『누군가』를 연기하고 싶어져서^n내가 맡을 수 있는 역할이 생기면 뭐든 말해 줘.^n왕자님과 공주님만 아니면 무엇이든 해 보일 테니까.",
    59: "나",
    60: "아…… 네. 그때는 꼭 부탁드릴게요.",
    61: "나도 참, 무슨 대답을 하고 있는 건지.",
    62: "하지만 그는 신경 쓰는 기색이 없었다.^n그럼 잘 자, 하며 손을 흔들고 걸어가려 한다.",
    63: "그 모습을 향해 고개 숙여 인사하고^n내 병실로 돌아가려던 바로 그때.",
    64: "???",
    65: "아, 미안!^n제대로 된 자기소개를 깜빡했네.",
    66: "그는 다시 돌아서서 가슴의 명찰을 가리켰다.",
    67: "이케노",
    68: "나는 이케노. 일단 의사야.^n네 담당의는 아니지만, 네 소문을 듣고^n조금 이야기해 보고 싶어졌거든.",
    69: "이케노",
    70: "『동화 증후군』에 기억 상실까지 겹친 건^n　나도 처음 들어 봤어.^n　귀중한 증례라는 거지. 알아?",
    71: "나",
    72: "알아요…….",
    73: "이케노",
    74: "아하하, 그런 표정 짓지 마.^n뭐, 분명 힘든 하루였겠지.^n푹 자렴.",
    75: "흰 가운 자락을 가볍게 휘날리며,^n이케노 씨는 이번에야말로 걸어갔다.",
    76: "나",
    77: "(──아마 의사 선생님들 사이에서도^n　이상한 사람 취급을 받겠지.)",
    78: "나는 쓸데없는 오지랖에 불과한 생각을 하며^n병실로 돌아갔다.",
    79: "침대에 드러눕자^n무서울 만큼 거센 기세로 졸음이 밀려왔다.",
    80: "여러 일이 있었고, 너무나 많은 일이 있었던 하루라^n되짚어 곱씹으며 잠들 생각이었지만,^n이렇게 강한 잠귀신을 상대로 이길 리가 없다.",
    81: "나는 거의 추락하는 속도로 잠의 소용돌이에 빨려 들어갔다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1115.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1115_slots_00001_00081_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1115_slots_00001_00081_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
