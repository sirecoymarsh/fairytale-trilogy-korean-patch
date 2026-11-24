from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "의사",
    2: "──응, 안색은 나쁘지 않군.^n몸 상태에는 대체로 문제없어.",
    3: "나",
    4: "네.",
    5: "나는 영 마음이 진정되지 않아 건성으로 대답한다.",
    6: "이 진찰실에서 약품 같은 냄새를 맡고 있으면 싫어도^n오늘 아침 모니터 너머로 본 광경이 떠오르고 만다.",
    7: "이곳에 불려 오는 것도 꺼려졌다.^n하지만 의사 선생님의 손놀림은 막힘없이 재빠르고,^n오히려 나쁜 인상을 품은 것이 미안할 정도다.",
    8: "나",
    9: "(이 사람은 어제 낮에 이야기한 것과 같은 의사 선생님이겠지.^n　──응, 아마 그럴 거야.)",
    10: "이곳 의사 선생님들은 흰 가운을 입고 풍채가 좋으며 안경을 쓴^n차림의 사람이 많아,^n인상이 너무 비슷해서 누가 누군지 알아보기 어렵다.",
    11: "알아보기 쉬운 사람은^n조금 기발한 차림에 분위기도 다른^n이케노 씨 정도다.",
    12: "나",
    13: "(오늘 아침 앨리스들을 진찰한 건 이 사람……^n　이 아니었나?)",
    14: "나",
    15: "(──애초에 그 사람은 정말 의사 선생님이었을까.)",
    16: "문득 그런 생각이 들어 나는 두려워졌다.",
    17: "정체 모를 누군가가 의사의 얼굴을 하고,^n제멋대로 진찰과 치료를 한다니──소름 끼친다.",
    18: "의사",
    19: "그래서 머리 쪽은 어떤가.^n뭔가 기억났나?",
    20: "나",
    21: "……아무것도요.",
    22: "나는 고개를 저었다.",
    23: "정확히 말하면 『여동생이 있었다는 것』을 어렴풋이 떠올렸으니,^n완전히 아무것도 아닌 건 아니지만.^n왠지 말하고 싶지 않았다.",
    24: "의사",
    25: "흠, 그런가.^n외상은 발견되지 않았고,^n뇌 검사도 지금까지 결과가 나온 것은 문제없어.",
    26: "의사",
    27: "그렇다면 심인성 문제…….^n불쾌한 일이 있어서 잊어버렸을 가능성이 크다는 얘기인데.",
    28: "나",
    29: "불쾌한 일…….",
    30: "의사",
    31: "그래. 계속 기억하고 있으면 심한 스트레스를 받아^n마음에 부담을 주는──^n그런 기억을 애지중지 품고 있을 필요는 없으니까.",
    32: "의사",
    33: "필요 없는 것, 해가 되는 것을 배제하는 건^n몸이나 마음이나 마찬가지야.",
    34: "나",
    35: "………….",
    36: "가슴 어딘가가 따끔거리며 가려운 정도의 불길함이 들었다.^n의사 선생님의 말이 옳은지도 모른다.",
    37: "의사",
    38: "원래 『동화 증후군』은 그런 병이야.^n강한 도피 행동과 변신 욕구가 합쳐진 것.",
    39: "나",
    40: "무슨 뜻인가요?",
    41: "의사",
    42: "불쾌한 기억에서 도망치고 싶다, 다른 내가 되고 싶다는 소망을,^n동화의 등장인물이 되어 이루는 거야.",
    43: "의사",
    44: "　예를 들어 양아버지에게 학대받던 여자아이가 빨간 모자가 되어,^n『늑대에게 잡아먹혔지만 구원받았어. 이제 괜찮아.』^n　라고 자신을 타이르며 마음의 상처를 가둬 두는 식이지.",
    45: "의사",
    46: "　예를 들어 반에서 괴롭힘을 당한 여자아이가 신데렐라가 되어,^n『하지만 언젠가 꼭 무도회에 가서 왕자님에게 선택받을 거야.』^n　하는 식으로 희망을 계속 품는다든가.",
    47: "나",
    48: "그럼 여기 있는 앨리스나 그레텔도요?",
    49: "나는 여섯 소녀의 얼굴을 차례로 떠올렸다.^n의사 선생님은 고개를 끄덕이는 대신 말을 고르는 모습이다.",
    50: "의사",
    51: "──어릴 때는 누구에게나 있는 일이야.^n다만 『낙원』에 올 정도의 아이는 마음의 상처가 커서,^n치유하는 데 시간이 걸리고 신중해야 하지.",
    52: "의사",
    53: "마음의 껍질에 틀어박혀 오랜 시간에 걸쳐 상처를 치유하고,^n강하게 살아갈 수 있도록 자신을 바꾸는 중이야.^n……번데기 같은 거지.",
    54: "나",
    55: "저도 그런 건가요?",
    56: "의사",
    57: "그럴지도 모르지.^n어느 쪽이든 아직 부드러운 번데기 껍질을^n억지로 뜯는 짓은 하지 않을 거야.",
    58: "의사",
    59: "우화할 때가 올 때까지 마음껏 푹 쉬게.",
    60: "나",
    61: "아…… 감사합니다.",
    62: "이제 가도 좋다는 의사 선생님의 몸짓을 따라^n허리를 들려던 참에,^n나는 묻는 걸 깜빡한 것이 떠올랐다.",
    63: "나",
    64: "저기, 하나 물어봐도 될까요?",
    65: "의사",
    66: "응? 무슨 일인가.",
    67: "나",
    68: "그, 제가 이런 말을 하는 것도 이상할지 모르지만…….^n환자들에게는^n이야기와 무관한 사물이나 사람이 어떻게 보이나요?",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1122.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1122_slots_00001_00068_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1122_slots_00001_00068_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
