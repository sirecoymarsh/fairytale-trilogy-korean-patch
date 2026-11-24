from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "오딜", 2: "──병이라고 해도 이런 것밖에 없어.", 3: "게르다", 4: "충분해. 고마워.",
    5: "그런 대화가 들려와 나는 걸음을 멈췄다.",
    6: "오데트 일행의 방 문틈으로 모습을 드러낸 오딜이,^n문간에 선 게르다를 상대하는 중이었다.",
    7: "오딜", 8: "가느다란 병이라 꽃병으로는 안 어울리지 않아?", 9: "게르다",
    10: "한 송이뿐이니까…….^n", 11: "봐, 이걸로 괜찮아.",
    12: "오딜에게 건네받은 유리병의 가느다란 목에,^n게르다는 곧장 가지고 있던 장미 줄기를 꽂았다.",
    13: "나", 14: "(저건 혹시……)",
    15: "장난삼아 정원에서 꺾은 장미를, 장난삼아 건넨 건,^n분명 그저께 밤이었던가.",
    16: "너무 많은 일이 있었기 때문인지,^n훨씬 옛날 일처럼 느껴지기도 하지만.",
    17: "게르다", 18: "──좀 더 일찍 찾아봤어야 했어.^n모처럼 받은 건데…….",
    19: "게르다는 꽃잎을 살며시 쓰다듬으며 후회하고 있다.",
    20: "여기서도,^n활짝 핀 장미꽃잎이 완전히 메말라^n시들기 시작한 것이 보였다.",
    21: "오딜", 22: "장미야 정원에 얼마든지 피어 있잖아.^n그 시들어 가는 게 그렇게 소중해?",
    23: "게르다", 24: "응, 소중해.",
    25: "꽃병을 감싼 두 손에 힘이 들어간다.^n그 하얀 손끝을 보며 나는 오늘 아침 일을 떠올렸다.",
    26: "누군가와 몸을 섞는 라푼젤의 모습을 보게 되어,^n몸을 웅크리고 버틴 밤과 빛바랜 아침.",
    27: "끈적하게 식은땀을 머금은 환자복을 벗어 던졌을 때의 최악인 기분과,^n모니터 너머로 보게 된 게르다의 진찰 모습.",
    28: "멋대로 짐작한 것일지도 모르지만,^n아름다운 것을 소중히 여기고 싶은 그 마음은 알 것 같았다.",
    29: "게르다", 30: "이건 겨우 손에 넣은 거야.^n──나는 정원에서 장미를 찾지 못했어.^n꽤 많이 돌아다녔는데도.",
    31: "오딜", 32: "마치 『게르다』가 마법사 할머니에게^n망각의 마법에 걸렸던 것처럼?^n뭐, 넌 『게르다』니까.",
    33: "게르다", 34: "………….^n그냥 못 보고 지나쳤을 뿐이야.",
    35: "게르다는 오딜의 히죽거리는 웃음에^n살짝 눈을 가늘게 뜨기만 하고 담담하게 넘겼다.",
    36: "게르다", 37: "오딜, 넌 왜 오데트와 똑같이 생겼어?",
    38: "갑자기 대화 흐름에 맞지 않는 질문을 던진 것은,^n게르다 나름의 반격이었을까.",
    39: "오딜", 40: "오딜이니까.",
    41: "당연히 『오딜』인 자신에게 의문을 품지 않는^n오딜에게는 아무 의미도 없는 질문이다.^n어깨를 으쓱하며 내뱉는다.",
    42: "게르다", 43: "오데트로 변장해 지크프리트에게 거짓 맹세를 하게 한,^n로트바르트의 딸…….",
    44: "오딜", 45: "그래, 그래. 뭐야, 알고 있잖아.^n닮지 않으면 속일 수 없으니까 그년으로 변신한 거야.^n──하, 겉모습만 변신해도 속는 왕자도 참 왕자답지.",
    46: "게르다", 47: "말도 안 돼. 그냥 쌍둥이 자매잖아?", 48: "나", 49: "(아……)",
    50: "그건 어렴풋이 나도 생각했던 일이다.^n사실은 쌍둥이고, 꼭 닮은 외모를 『변신했다』는 설정에^n이용하는 것이라고.",
    51: "나", 52: "(하지만 분명 소용없어, 게르다)",
    53: "오딜", 54: "뭐? 무슨 소리야.^n그런 건 『성서』에 안 쓰여 있는데. 제대로 읽었어?",
    55: "게르다", 56: "──넌 정말 네가 오딜이라고 생각해?", 57: "오딜", 58: "생각하고 말고 할 것도 없지.",
    59: "나는 끈질기게 묻는 게르다 때문에 조마조마했다.^n오딜에게서 다른 대답이 돌아오리라고^n어째서 기대할 수 있는 걸까?",
    60: "아니나 다를까 오딜은 엇나가는 대화에 완전히 질린 듯^n깊은 한숨을 쉬며 귀찮다는 듯 머리카락 끝을 만지작거린다.",
    61: "오딜", 62: "난 오딜이니까.^n오히려 넌 왜 네가 게르다라는 걸 인정하지 않아?",
    63: "게르다", 64: "……그냥 그렇게 느껴지지 않으니까.",
    65: "게르다", 66: "이상한 걸 물어서 미안해.^n병은 큰 도움이 됐어. 고마워.",
    67: "게르다는 마침내 포기한 듯,^n잘라 내듯 대화를 끝냈다.",
    68: "마지막으로 노골적인 경멸의 눈길을 보내고,^n오딜은 문을 닫는다.",
    69: "게르다", 70: "………….",
    71: "게르다는 한동안 손에 든 장미를 바라보다,^n이윽고 무언가를 떨쳐 내듯 걷기 시작했다.",
    72: "나", 73: "(……아)", 74: "게르다", 75: "아…….",
    76: "내가 있는 쪽으로 다가온 그녀와 당연히 얼굴을 마주하게 된다.",
    77: "엿들었다기보다 자연스럽게 귀에 들어왔다고^n생각했기 때문에,^n몸을 숨겨야겠다는 발상은 떠오르지 않았다.",
    78: "나는 그다지 떳떳하지 못하다고 느끼지 않았고,^n게르다 역시 들었는지를 묻는 기색은 없었다.",
    79: "그저 갓 만든 꽃병을 들어 올려,^n지쳐 가는 장미의 얼굴을 내게 보여 준다.",
    80: "게르다", 81: "……고마워.^n나 나름대로 소중히 하기로 했어.",
    82: "나", 83: "그렇구나…….", 84: "무슨 말을 해야 좋을지 모르겠다.",
    85: "게르다와 카이가 장미 화분을 기른다는^n『눈의 여왕』 도입부가 떠올라,^n결과적으로 그대로 흘러간다는 사실을 얄궂게 느꼈기 때문이다.",
    86: "그런 내 심정을 꿰뚫어 본 듯 게르다는 미소 지었다.",
    87: "게르다", 88: "이건 『카이』가 아니라 네가 준 선물이니까.^n네 배려에 고마워하며, 나도 나 자신으로서 소중히 할 거야.^n그뿐이야.",
    89: "나", 90: "응. 그러네.", 91: "나도 비슷한 미소를 지으며 대답했다.",
    92: "언제나 긴장을 놓지 않고 살아가는 게르다.",
    93: "조금이라도 그 위안이 되었다면,^n그날 밤 내가 부린 변덕은^n분명 좋은 일이었을 것이다.",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1132.gsc" and item.get("slot") in TARGETS: rows[int(item["slot"])] = item
    if set(rows) != set(TARGETS): raise SystemExit("catalog mismatch")
    entries = []
    for index in sorted(TARGETS):
        source, target = str(rows[index]["source_text"]), TARGETS[index]
        if CARET_RE.findall(source) != CARET_RE.findall(target): raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": rows[index]["uid"], "source_text": source, "source_raw_sha256": rows[index]["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 전"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1132_slots_00001_00093_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1132_slots_00001_00093_draft.json"; out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
