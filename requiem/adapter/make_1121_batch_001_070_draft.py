from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "문을 두드리자 대답 대신 문이 열렸다.",
    2: "게르다",
    3: "……또 너구나.",
    4: "나직이 중얼거린 게르다는 그리 놀란 모습이 아니었다.^n아마 찾아온 사람이 나라는 것은^n어딘가에서 예상하고 있었으리라.",
    5: "가짜 벽난로 곁에서 우리는 나란히 나무 상자 위에 앉는다.",
    6: "한동안 침묵 속에^n벽난로에서 울리는 가짜 불꽃 소리가 메아리쳤다.",
    7: "게르다는 입술을 다문 채 깊은 생각에 잠긴 듯하다.^n시선은 무언가를 가려내듯 허공에 고정되어 있었다.",
    8: "게르다는 나와 이렇게 이야기하게 된 것을^n후회하는 걸까.^n왠지 그런 생각이 들었다.",
    9: "게르다",
    10: "──왜 또 나를 찾아왔어?",
    11: "나",
    12: "너와 좀 더 이야기하고 싶어서.",
    13: "게르다",
    14: "………….",
    15: "내 솔직한 대답에 게르다는 어색한 듯 숨을 삼켰다.",
    16: "게르다",
    17: "──그건 영광이지만 분명히 말할게.^n내게 기대도 곤란해.^n나는 내 일만으로도 벅차.",
    18: "그 목소리는 말만큼 매섭지 않았다.^n온 힘을 다해 밀어내기보다,^n등을 돌리고 두세 걸음 거리를 두는 듯한 겁먹은 거절.",
    19: "나",
    20: "알고 있어.^n기대고 말고 할 것도 없이 내 문제는 내가 해결할 수밖에 없고.",
    21: "나",
    22: "하지만 민폐라면…….",
    23: "게르다",
    24: "민폐는 아니야.^n그저…….",
    25: "게르다는 말을 흐렸다.^n오늘의 그녀에게는 평소의 시원스러운 태도가 없다.",
    26: "게르다는 다시 오랫동안 입을 다물었다.^n나도 침묵한 채 그녀가 이야기를 시작하기를 기다렸다.",
    27: "게르다",
    28: "──있잖아, 이 『낙원』을 어떻게 생각해?",
    29: "이윽고 게르다가 꺼낸 것은 그런 질문이었다.^n주변을 꺼리는 듯한 작은 목소리로,^n어떻게든 해석할 수 있는 애매한 방식으로.",
    30: "나",
    31: "………….",
    32: "왜 그런 걸 묻는 걸까 싶으면서도,",
    33: "나",
    34: "(──아아, 역시.)",
    35: "하고 마음속 깊이 고개를 끄덕이는 나도 있었다.",
    36: "분명 게르다는 거듭 망설이다가,^n중요한 경계를 넘는 듯한 결심을 품고 내게 물은 것이다.",
    37: "거짓말해서는 안 된다.^n내가 생각한 그대로를 전해야 해──",
    38: "게르다의 불신에…….",
    39: "『잘 모르겠어.』",
    40: "『이상한 곳이라고 생각해.』",
    41: "나",
    42: "이렇게 신세 지고 있으면서 할 말은 아니지만,^n──이상한 곳이라고 생각해.",
    43: "내 중얼거림에 게르다는 화들짝 얼굴을 들었다.",
    44: "게르다",
    45: "이상하다니? 어떻게 이상해?",
    46: "나",
    47: "잘 설명할 수는 없지만, 뭔가 앞뒤가 맞지 않는 느낌이 들어.",
    48: "내 머릿속에 오늘 아침 본 광경이 되살아난다.",
    49: "모니터 너머의 앨리스와 그레텔.^n실이라도 늘어질 듯 끈적한 의사 선생님의 목소리.^n그걸 내게 보여 준 『누군가』의 의도.",
    50: "나",
    51: "……윽.",
    52: "나는 참지 못하고 거칠게 숨을 내쉰다.",
    53: "갈 곳 없는 나 자신을 위해^n생각하지 않으려 했던 온갖 것이^n한꺼번에 밀려드는 느낌이 들었다.",
    54: "팔을 문지르니 꺼끌꺼끌할 만큼 소름이 돋아 있었다.",
    55: "게르다",
    56: "너…… 무슨 일이 있었어?",
    57: "나",
    58: "……윽.",
    59: "보고 만 것과 그때 생겨난 감각을^n게르다에게 모조리 털어놓고 싶었지만,^n꾹 참았다.",
    60: "여자아이에게──아니, 사람에게 할 이야기가 아니다.",
    61: "게르다",
    62: "……말할 수 없어?",
    63: "나",
    64: "모르는 편이 좋아.^n게르다야말로 무슨 일 있었어?",
    65: "게르다",
    66: "모르는 편이 좋아.",
    67: "같은 말로 되받고 게르다가 깊은 한숨을 내쉬었다.",
    68: "나",
    69: "그렇다고 해서^n빠져나간다거나, 도망친다거나, 말대꾸한다거나──^n아직 그렇게까지 결심할 수는 없지만.",
    70: "게르다",
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1121_slots_00001_00070_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1121_slots_00001_00070_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
