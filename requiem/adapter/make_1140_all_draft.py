from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
TARGETS = {
    1: "라푼젤은 마침 막 잠에서 깬 듯했다.",
    2: "내가 방에 들어서자 졸린 눈을 비비며,^n침대 가장자리에서 발을 내리고 일어나려던 참이었다.",
    3: "라푼젤",
    4: "………….",
    5: "라푼젤은 나를 보고 몇 번 눈을 깜빡였다.^n신기하다는 듯한 눈이었다.",
    6: "눈을 깜빡이면 맞아야 할 초점이 맞지 않고,^n세상이 언제까지나 흐릿하게 보이는──그런 느낌.^n깊은 당혹감으로 가득한, 처음 보는 눈빛이었다.",
    7: "라푼젤",
    8: "당신은…….^n여기는…….^n저는…….",
    9: "무언가 말하려다 라푼젤은 그때마다 목소리를 끊었다.",
    10: "나",
    11: "진정해.^n하나씩 떠올리면 괜찮을 거야.",
    12: "나는 무슨 말을 할지 망설이다 결국 무난한 말로 정했다.^n지금 라푼젤은 분명 몹시 혼란스러울 것이다.",
    13: "생각대로 라푼젤은 이마에 손을 얹고 고개를 젓는다.^n머릿속에 꽉 찬 혼란이 출렁출렁 물결치는 듯한,^n무척 무거워 보이는 몸짓이었다.",
    14: "라푼젤",
    15: "어디서부터 어디까지가 꿈인가요?^n저는 이 방을 떠났을 텐데,^n어째서 다시 이곳에……?",
    16: "라푼젤",
    17: "그리고 당신은 누구시죠?^n할머님도…… 그분도 아니고…….^n하지만 저…… 아는 것 같아요. 그 목소리…….",
    18: "이야기 속에서 고델 할머니에게^n『탑에서 쫓겨난』 라푼젤.",
    19: "그런데도 이제 돌아올 수 없을 탑에 어느새 돌아와 있다.^n그 현실이 그녀를 몹시 혼란스럽게 해,^n『라푼젤』로서의 인식을 흐트러뜨리는 것이리라.",
    20: "지금까지는 이 병실에 틀어박혀,^n낮에 찾아오는 사람은 『할머님』, 밤에 찾아오는 사람은 『왕자님』으로^n구별하기만 하면 문제없었다.",
    21: "하지만 그런 전제를 이런 식으로 뒤집힌 라푼젤은,^n현실 세계를 있는 그대로 바라볼 수밖에 없다.",
    22: "분명 눈앞의 나는^n『본 기억은 있지만 모르는 소년』이라는,^n지극히 모순된 존재로 받아들여질 것이다.",
    23: "라푼젤",
    24: "역시…… 역시 꿈이었나 봐요.^n안 되겠네요, 저…… 이런 시간에 잘 생각은^n조금도 없었는데…….",
    25: "라푼젤은 떨리는 손으로 자기 머리카락을 끌어당겼다.^n방구석에서 길게 똬리를 튼^n밧줄 같은 감촉에 안도의 숨을 내쉰다.",
    26: "라푼젤",
    27: "그래요, 머리카락은 그대로 기니까요.^n고델 할머님께서 그분과의 일을 알아채셨다니.^n──꿈이에요. 전부 꿈이었던 거예요.",
    28: "『라푼젤』 본편에 따르면 고델 할머니는^n라푼젤을 쫓아낼 때 그녀의 머리카락을 잘라 버린다.",
    29: "그것이 아직 긴 그대로라는 건,^n그녀가 여전히 이곳 주민이라는 증명이 되는 것이리라.",
    30: "나",
    31: "(──뭐, 꿈으로 치부하는 게 가장 무난하지.)",
    32: "나",
    33: "있잖아, 라푼젤. 꿈 이야기를 해도 될까?",
    34: "라푼젤",
    35: "……네, 괜찮습니다만.^n결국 당신은 누구신 걸까요.",
    36: "나",
    37: "나는…… 나는.^n──나도 모르니까 적당히 생각해도 돼.^n어차피 꿈이니까 사라질 테고.",
    38: "라푼젤",
    39: "………….",
    40: "라푼젤은 나를 빤히 바라보았다.^n『사라지는 건가요?』 하고 신기한 듯 묻는 눈으로.",
    41: "나는 왠지 쑥스러워졌다.",
    42: "앨리스와 처음 만났을 때,^n『그녀가 나를 봄으로써 나라는 존재가 생겨난다』^n고 느꼈는데, 그 감각과 비슷할지도 모른다.",
    43: "나",
    44: "꿈 이야기, 해도 될까?",
    45: "라푼젤",
    46: "네, 말씀하세요.",
    47: "나",
    48: "꿈속에서 화덕에서 시체가 나왔잖아.^n기억해?",
    49: "라푼젤",
    50: "──네. 물론 기억하고 있어요.^n연기가 자욱했죠. 불쾌한 냄새였어요.",
    51: "나",
    52: "응. 그때 일 중에 떠오르는 건 없어?^n뭔가를 봤다든가, 신경 쓰였다든가.",
    53: "나",
    54: "예를 들면 사람의 시체를 봤다는 사람과,^n보지 못했다는 사람이 있는데, 넌 어느 쪽이야?",
    55: "라푼젤",
    56: "저는 아무것도 보지 못했어요.^n주방을 들여다보니 연기 바다였거든요.",
    57: "라푼젤",
    58: "제 뒤에 온 게르다는 들어갔지만,^n제게는 그런 용기가 없었어요.^n계속 문간에 서서 잠잠해지길 기다렸어요.",
    59: "나",
    60: "문간에 있었던 거지.^n누가 지나가지는 않았어?",
    61: "라푼젤",
    62: "아니요, 아무도요. 앨리스 일행의 말처럼^n새까맣게 탄 시체가 걷기 시작했다 해도,^n문간으로 도망친 건 아니겠네요.",
    63: "나",
    64: "그래…….",
    65: "특별히 새로운 정보는 없다.^n나는 그저 라푼젤을 혼란스럽게 하러 온 모양이다.",
    66: "라푼젤",
    67: "──다만.",
    68: "이만 가 볼까 생각하던 순간,^n라푼젤이 나직이 덧붙였다.",
    69: "라푼젤",
    70: "하지만 그 연기는…….^n그 연기가 마음에 걸려요.^n뭔가…… 전에도 이런 일이 있었던 듯한…….",
    71: "라푼젤",
    72: "아…… 머리, 가…….",
    73: "라푼젤은 두 손으로 머리를 감싸고 비틀거렸다.",
    74: "나",
    75: "미, 미안. 이제 무리하지 마.^n푹 쉬는 게 좋겠어.",
    76: "나는──아마 라푼젤 자신보다도 강하게^n희미한 기억의 정체가 궁금했지만,^n지금 억지로 캐내 봐야 괴롭힐 뿐이라고 단념했다.",
    77: "침대로 데려가 눕히자,^n라푼젤은 곧바로 잠의 바다로 노를 저어 나가면서,^n나른하게 나를 올려다보았다.",
    78: "라푼젤",
    79: "고마워요…….^n──있죠, 꿈 밖에서도 만날 수 있다면 멋지겠네요.",
    80: "나",
    81: "………….",
    82: "나는 그저 장난처럼 한 말에 보기 좋게 심장이 뛰었다.",
    83: "그녀의 졸린 미소에는 빈틈투성이인 천진한 친밀감이^n담겨 있어, 『라푼젤』의 가면 아래에서^n직접 내게 향한 것처럼 느껴졌기 때문이다.",
    84: "하지만 꿈 밖에서 라푼젤과 만날 때면,^n그녀는 다시 나를 『할머님』이나 『왕자님』에^n끼워 맞추려 하겠지.",
    85: "그건 어쩔 수 없는 일이지만, 역시 조금 쓸쓸했다.",
}


def main() -> int:
    expected = set(range(1, 86))
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1140.gsc" and int(item.get("slot", -1)) in expected:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1140_slots_00001_00085_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    path = PROJECT / "packets" / "drafts" / "1140_slots_00001_00085_draft.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "entries": len(entries), "output": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
