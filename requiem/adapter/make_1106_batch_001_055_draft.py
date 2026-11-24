from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "복도를 돌아 시야 한구석에 나타난 순간부터,^n그 문의 맑디맑은 빛깔은 나를 부르는 듯했다.",
    2: "유리일까, 수정일까.",
    3: "투명한 얼음에 단단한 섬유 같은 서리가 뒤섞여,^n운모를 닮은 파란색과 보라색 반사를 반짝이고 있다.^n표면에 새겨진 눈 결정부터가 서늘하고 아름다운 문이다.",
    4: "그 표면에는^n게르다^n라고 적힌 명판이 걸려 있다.",
    5: "조심스럽게 노크한다.^n당연한 일이지만,^n문 표면은 보기만큼 차갑지 않다.",
    6: "???",
    7: "네.",
    8: "???",
    9: "……누구시죠.",
    10: "또렷한 목소리가 들리고 외짝 문이 싱겁게 열렸다.^n──불과 수십 센티미터의 틈만큼만.",
    11: "인형처럼 반듯한 하얀 얼굴과 신비롭게 빛나는 은백색 머리카락,^n올곧은──얼음처럼 맑고 아름다운 눈동자가,^n문틈으로 나를 살핀다.",
    12: "나",
    13: "저, 저기…….",
    14: "일부분만 보여서 알 수 없지만,^n분명 그녀는 자그마하고 나보다 나이가 많아 보이지도 않는다.^n기가 눌릴 만한 상대는 아닐 것이다.",
    15: "그런데도 나는 서늘하고 영리해 보이는 눈빛과,^n무슨 수를 써도 답할 수 없는 질문 앞에서 완전히 움츠러들어,^n한심하게도 우물거리며 말을 더듬었다.",
    16: "금방이라도 문이 쾅 닫히지 않을까──^n혼란스러운 머리 한구석에 그런 광경이 생생히 떠올라,^n제멋대로 각오하고 있었는데.",
    17: "???",
    18: "진정해. 괜찮아.^n천천히 해도 돼.",
    19: "차분한 목소리가 말을 건넸다.^n딱딱하고 진지한 말투인데도,^n나를 재촉하지 않으려 천천히 잇는다는 것이 전해진다.",
    20: "언제나처럼 새하얀 기억에 시달리던 의식과,^n빠르게 뛰던 심장이,^n스르르 진정되는 것을 느꼈다.",
    21: "나",
    22: "그…… 가, 갑자기 미안해.^n나, 조금 곤란한 일이 있어서…….",
    23: "???",
    24: "들어 볼게.",
    25: "대답은 단 한마디로 간결했다.^n군더더기가 없어 산뜻하다.",
    26: "그에 비해 내 설명은 더듬거리고 횡설수설한 데다,^n내용부터가 이러니 요점을 알 수 없는 부분도 많았다.",
    27: "그런데도 그녀는 지루해하거나 어이없어하는 기색 없이,^n말한 대로 그저 들어 주었다.",
    28: "???",
    29: "그렇구나…… 기억이 없는 거네.^n이름조차 모른다니 골치 아프겠어.",
    30: "???",
    31: "하지만 나는 너를 모르고 의사도 아니야.^n도와주고 싶어도 도와줄 수 없어.",
    32: "이야기를 다 들은 그녀가 말한 것은 역시나 지당한 내용이었다.^n불안해서 나도 모르게 여기저기 물으러 다녔지만,^n이런 문제에 답할 수 있는 사람이 흔할 리 없다.",
    33: "나",
    34: "(……응. 그런데 지금 뭐라고 했지?^n　의샤 선생님이 아니라서 모른다는 건,^n　의샤 선생님이라면 안다는 뜻인가?)",
    35: "나",
    36: "의샤 선생님……?^n은 어디에 가면 만날 수 있을까?",
    37: "???",
    38: "의사 선생님이라…….",
    39: "내 어설픈 발음을 고쳐 주면서,^n그녀의 뺨이 한순간 굳어지는 것을 나는 보았다.",
    40: "차가워 보여도 결코 차갑지 않은 그녀가,^n감정을 미처 감추지 못하고 드러낸 것.^n생각하고 싶지 않은 일을 억지로 떠올린 듯한──",
    41: "그것은 『경계』나 『불신』 같은 달갑지 않은 감정이다.^n그런 느낌이 들었다.",
    42: "???",
    43: "의사 선생님은…… 괜찮아.^n여기 있으면 곧 만나게 될 거야.",
    44: "나",
    45: "으, 응…….",
    46: "사실은 더 묻고 싶은 것이 있었다.^n지금까지 만난 아이들 중 가장 말이 통할 것 같다.",
    47: "진지하고 올곧은 눈빛이나 단정한 말투 같은 것에서,^n뭐랄까 단연 제대로 된 사람이라는 인상을 받는다.^n정말 고마울 정도로.",
    48: "하지만 끈기 있게 나를 상대해 준 그녀가^n이제는 문을 닫고 싶어 한다는 것을 눈치챘다.",
    49: "???",
    50: "빨리 기억해 내면 좋겠네.^n가능하다면 되도록 소중한 것부터.",
    51: "나",
    52: "소중한 것…….^n이름이나 가족 같은 거?",
    53: "???",
    54: "　그래, 그것도 소중하지만.^n『무엇을 하고 싶었는지』가 가장 중요하지 않을까.",
    55: "나",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1106.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1106_slots_00001_00055_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1106_slots_00001_00055_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
