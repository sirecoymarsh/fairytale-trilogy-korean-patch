from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "???",
    2: "여기 있었구나.^n어디에도 없어서 찾아다녔잖아.",
    3: "갑자기 말을 걸어와 나는 흠칫 몸을 떨었다.",
    4: "앨리스 이후 복도에서 누군가와 마주친 적이 없어서,^n완전히 방심하고 있었다.^n뱃속 깊은 곳이 울릴 듯 굵고 낮은 목소리다.",
    5: "뒤돌아보자 머리 하나만큼 높은 곳에서,^n입꼬리를 씨익 치켜올렸지만 그다지 즐거워 보이지 않는 미소가^n나를 내려다보고 있었다.",
    6: "나",
    7: "(──어른이다.)",
    8: "나는 아주 자연스럽게 그렇게 생각했다.^n모든 것을 잊었어도 이 생물의 이름은 안다.",
    9: "어른",
    10: "나는 간호사야. 간·호·사. 알겠어?",
    11: "나는 잠시 망설이다 고개를 끄덕였다.^n솔직히 말해 기억나지 않지만,^n모른다고 대답하면 귀찮아질 것 같다.",
    12: "간호사",
    13: "이야, 깜짝 놀랐어.^n슬슬 깨어나려나 하고 기다린 지 이틀 반이야.^n방심하게 되지. 가장 허를 찔리기 좋은 때잖아.",
    14: "간호사",
    15: "깨어난 데다 비틀비틀 어디론가 가 버리다니.^n이 형이 걱정했잖아.",
    16: "푸르게 남은 수염 자국과 이중턱은,^n내가 보기에도 그림으로 그린 듯한 『아저씨』다.^n하지만 나는 고개를 숙인 채 죄송하다고만 말했다.",
    17: "간호사",
    18: "그럼 이 형을 따라와 줄래?^n묻고 싶은 게 여러 가지 있거든. 응?",
    19: "나는 여전히 고개를 숙인 채 턱이 가슴에 닿도록 당겨 끄덕인다.",
    20: "그렇게 끌려간 곳은 『진찰실』이었다.^n지금까지 찾아간 방과는 다른,^n깨끗한 흰 미닫이문에 그렇게 적혀 있다.",
    21: "나",
    22: "(으악…….)",
    23: "안에서 흘러나온 공기를 한 번 들이마신 순간,^n나는 나도 모르게 얼굴을 찌푸렸다.",
    24: "　코를 찌르는 톡 쏘는 냄새.^n　무슨 냄새인지는 잘 떠오르지 않지만,^n『불길한 예감』만은 절실하게 든다.",
    25: "안으로 들어가 권유받은 둥근 의자에 앉아^n흰옷을 입은 아저씨(두 번째)와 마주하자,^n불안은 점점 커졌다.",
    26: "아저씨 뒤의 책상에 붙은 흑백 사진이며,^n선반에 빼곡히 늘어선 병이며,^n책상 위에 놓인 금속 부품 달린 튜브며.",
    27: "　그런 것들을 바라보고 있자니,^n『아프지만 참아야 해』 『잘 참았네, 장하다』^n　그런 목소리가 되살아나는 듯한──",
    28: "아저씨",
    29: "안녕. 드디어 깨어난 모양이구나.^n모두 걱정하고 있었단다.",
    30: "나",
    31: "죄송합니다. 폐를 끼쳤습니다.",
    32: "내 입이 멋대로 움직여 그런 말을 내뱉었다.^n입에 익었네, 하고 남의 일처럼 생각한다.",
    33: "아저씨",
    34: "아니야, 괜찮단다.^n우리 아저씨들은 걱정하는 것이 일이니까.",
    35: "나",
    36: "저기, 여기는 어디인가요?^n그리고 당신은 누구신가요?",
    37: "아저씨",
    38: "아, 아저씨가 소개도 안 해서 미안하구나.^n아저씨는 의샤 선생님이란다.",
    39: "나",
    40: "의샤 선생님.",
    41: "게르다의 말을 떠올렸다.^n이 사람이 내 기억을 어떻게 해 줄 사람일까.",
    42: "의샤",
    43: "그리고 이곳은 병원이야.^n──하지만 낙원이라고 부르는 사람이 더 많으려나.",
    44: "나",
    45: "병원.^n낙원?",
    46: "그대로 따라 말하고 곧바로 떠올랐다.",
    47: "나",
    48: "(낙원…… 낙원!)",
    49: "머릿속에서 퍼즐 조각이^n딱 맞춰진 듯한 기분마저 들었다.",
    50: "그래!　분명 그런 말이었다.^n아름답고 행복한 장소를 그렇게 부른다.^n마치 낙원 같다는 식으로──",
    51: "의샤",
    52: "그리고 너는 이곳으로 실려 온 환자란다.^n환자는 곧 병자.^n병이 있어서 치료하려고 입원한 거야.",
    53: "기억의 자물쇠 하나가 풀리자 이것저것 꺼낼 수 있었다.^n병원, 환자, 병자, 입원…… 그래, 간호사는 간호사고,^n눈앞의 이 사람은 의샤 선생님이 아니라 의사 선생님이다.",
    54: "뜻을 떠올린 건 좋지만,^n그것을 모두 합쳐 생각하면 결국,^n나는 병자이고 입원할 정도의 환자인 모양이다.",
    55: "나",
    56: "(하지만 나는 아무 데도 아프지 않은 것 같은데.^n　다친 곳도 보이지 않고,^n　그렇게 오래 걸을 만큼 건강하고.)",
    57: "의사",
    58: "──병이라고 해도 몸이 아니라 머리 쪽이란다.",
    59: "내 손바닥과 무릎을 보며 그런 생각을 하자,^n의사 선생님은 조금 안됐다는 듯 말을 이었다.",
    60: "나",
    61: "머리…… 병이요?",
    62: "의사",
    63: "그렇지. 몸 상태가 어긋나듯 머리 상태도 이상해질 수 있어.^n게다가 몸과 달리 고치려면 한참 애를 먹는단다.",
    64: "의사",
    65: "애초에 이상한지 아닌지를 판단하는 머리 자체가^n이상한 것이니, 자신이 이상하다는 사실조차 좀처럼 알지 못해.^n그게 골치 아픈 점이지.",
    66: "　의사 선생님은 말을 멈추고 나를 가만히 바라보았다.^n『내 머리가 이상할 리 없어!』^n　하고 소리치며 흥분하지 않을지 지켜보았겠지.",
    67: "나",
    68: "………….",
    69: "사실 간발의 차로 참았을 뿐, 나는 불만이 가득했다.",
    70: "내 머리, 지금 이렇게 생각하는 내 머리가 이상하다니,^n몸에 맞지 않는 옷처럼 기분 나쁘다.^n엄청나게 무례한 거짓말로밖에 느껴지지 않는다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1107.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1107_slots_00001_00070_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1107_slots_00001_00070_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
