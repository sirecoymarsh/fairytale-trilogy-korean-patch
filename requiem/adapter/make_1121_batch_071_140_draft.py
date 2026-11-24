from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    71: "알아. 갈 곳 따위 없잖아.^n게다가 이곳은 꽤 경비가 삼엄해.^n나는 몇 번 실패해서 끌려 돌아왔어.",
    72: "나",
    73: "어?",
    74: "게르다가 아무렇지 않게 한 말에 나는 소리를 흘렸다.^n그건──탈출한 적이 있다는 뜻인가?",
    75: "대놓고 물어도 될지 망설이자,^n게르다는 고민에 빠진 옆얼굴로 눈을 감았다.",
    76: "게르다",
    77: "나는…… 무서워.",
    78: "게르다",
    79: "나는 분명 이상한 걸지도 몰라.^n나 자신도 어이없을 만큼 생각이 정리되지 않고 뒤죽박죽이야.^n치료가 필요할지도 모르지.",
    80: "게르다",
    81: "하지만 이곳에 있으면^n이상한 머리가 점점 더 이상해지는 것 같아서,^n──무서워.",
    82: "나",
    83: "게르다…….",
    84: "무심코 그녀를 부른 뒤 나는 후회했다.^n그 호칭은 괴로워하는 그녀를^n더욱 혼란스럽게 할 뿐인지도 모른다.",
    85: "게르다",
    86: "나는, ……나는 게르다인 걸까?",
    87: "아니나 다를까 게르다는 뺨을 굳히고 머리를 좌우로 흔들었다.^n내가 부른 그 이름을 머릿속에서 몰아내려는 몸짓.",
    88: "나",
    89: "미안해.",
    90: "게르다",
    91: "괜찮아. 다른 이름은 떠오르지도 않으니까.^n",
    92: "──그래, 그렇네.",
    93: "게르다는 체념한 듯 고개를 끄덕였다.",
    94: "게르다",
    95: "불편할 테니 『게르다』라고 불러도 돼.^n다만 『눈의 여왕』 속 『게르다』가 아니라, 그냥 『게르다』야.",
    96: "나",
    97: "응, 알았어.",
    98: "그 뒤로 한동안 우리는 시시한 대화를 나눴다.^n아침 식사, 도서관, 정원, 날씨,^n그리고 내 병실 이야기.",
    99: "게르다",
    100: "흐음. 네 병실은 평범한 병원 같은 방이구나.",
    101: "나",
    102: "응. 여기서는 오히려 드물지도 몰라.",
    103: "게르다",
    104: "그러게. 방마다 쓸데없이 공들여 꾸며 놔서…….^n나도 너처럼 아무것도 없는 방이면 됐을 텐데.",
    105: "나",
    106: "하지만 너무 하얀 것도 마음이 편치 않아.",
    107: "　──이렇게 눈치 보지 않아도 되는 시시한^n『평범한 대화』는 오랜만인 것 같다.",
    108: "적어도 깨어난 뒤로는 남의 망상에 맞춰 주기만 했으니까──",
    109: "슬슬 돌아가려고 일어서자,^n게르다는 문까지 배웅하러 나왔다.",
    110: "게르다",
    111: "저기, ──고마워.",
    112: "나",
    113: "어, 뭐가?",
    114: "게르다",
    115: "누구에게도 말할 수 없는 이야기를 들어줘서.^n용기를 내 털어놓기를 잘했어.",
    116: "나",
    117: "그건 나도 마찬가지야.^n──또 올게.",
    118: "닫혀 가는 문틈으로 마지막 말을 던지자,^n게르다는 눈을 크게 뜨더니 다음 순간 활짝 미소 지었다.",
    119: "나",
    120: "──깨어난 지 얼마 안 돼서 잘 모르겠어.",
    121: "나는 뱃속 깊은 곳에서 솟아나는 온갖 감정을 꾹 누르고,^n애매한 대답을 했다.",
    122: "왜냐하면──사실대로 이야기하면 인정해야 한다.^n이상한 곳에 흘러들어 온 나를,^n그런데도 어디에도 갈 수 없는 나를.",
    123: "나",
    124: "이상한 곳이긴 하지만,^n이상하다고 느끼는 내 마음이 어디까지 옳은지도 모르겠어.",
    125: "나",
    126: "왜냐하면 나는──우리는, 머리가 이상한 것 같으니까.",
    127: "무릎 위에 놓인 게르다의 손이 주먹을 쥐는 것을 보고,^n나는 눈을 돌렸다.",
    128: "게르다",
    129: "……그렇구나.",
    130: "대답은 짧고 다독이듯 다정한 울림이었다.",
    131: "그런데도 내 가슴께에 욱 하고 통증이 달렸다.",
    132: "좋은 일인지 나쁜 일인지는 모른다.^n──나는 지금을 바꿀지도 모르는 스위치를^n모르는 척한 것이다.",
    133: "그건 그것대로 어쩔 수 없는 일이겠지.^n앞이 보이지 않게 되는 건 몹시 두려운 일이니까.",
    134: "게르다",
    135: "잊어버린 것을 빨리 떠올리면 좋겠네.^n한시라도 빨리 이곳을 나가 원래 생활로──",
    136: "돌아가는 나를 문간에서 배웅하며,^n게르다는 그런 말을 건네주었다.",
    137: "게르다의 태도에 달라진 점은 없지만,^n그녀가 변하려 하지 않는 나를 존중한 것과^n원래의 거리로 돌아가려는 것은 어렴풋이 알 수 있었다.",
    138: "나",
    139: "(나는 내 생각밖에 하지 않는구나.)",
    140: "닫혀 가는 문을 바라보며,^n내 가슴이 다시 욱신거렸다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1121.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1121_slots_00071_00140_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1121_slots_00071_00140_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
