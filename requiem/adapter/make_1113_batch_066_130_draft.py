from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    66: "나 자신도 어이없을 만큼 바보 같은 충동이었지만,^n단순하고 소박한 만큼 억누르기 어려웠다.",
    67: "모처럼 이런 동화투성이의 이상한 세계에 던져졌다.^n즐길 수 있는 부분은 즐겨야지.",
    68: "결국 그런 생각에 등을 떠밀려,^n나는 두 줄의 머리카락을 꽉 잡았다.",
    69: "각오는 했지만,^n아래에서 올려다볼 때보다 훨씬^n길고 높고 괴로운 여정이었다.",
    70: "나",
    71: "──읏, 하아, 헉…….^n시…… 실례합니다!",
    72: "어떻게든 끝까지 올라간 나는,^n거친 숨을 몰아쉬며 라푼젤의 창문 안으로 굴러 들어갔다.",
    73: "사실은 먼저 말을 건 뒤 그러고 싶었지만,^n그럴 여유가 없었다.",
    74: "구르면서 낮에 맡았던 꽃 같은 향기를 느끼고,^n역시 라푼젤의 방이라고 확신했다.",
    75: "숨을 고르며 고개를 드니,^n상당히 어두운 인상이었다.",
    76: "광원은 창문으로 들어오는 달빛과 침대 옆 램프뿐이다.",
    77: "그 희미한 빛 속에 별이 뜬 밤하늘을 본뜬 둥근 천장과 카펫,^n늘어진 천이 어렴풋이 떠올라,^n정원에서 본 밤의 초원을 재현한 듯하다.",
    78: "낮에 보았을 때는 소박한 집이라는 느낌이었는데,^n밤에는 어딘가 비밀스럽고 은신처 같은 분위기가 있다.",
    79: "나",
    80: "(라푼젤은 없는 건가.)",
    81: "정적 속에서 달콤한 향기를 맡으며^n죄책감에 짓눌릴 것 같던 순간,^n침대의 천개 같은 천을 사르르 헤치고 그녀가 나타났다.",
    82: "라푼젤",
    83: "안녕하세요.",
    84: "나",
    85: "아…….",
    86: "어두운 방 안에,^n매끄럽고 하얀 뺨이 떠오른다.^n어째서인지 내 심장이 쿵 하고 한 번 뛰었다.",
    87: "낮에 만났을 때 쓰고 있던,^n머리부터 온몸을 덮는 후드도 검은테 안경도 벗었다.",
    88: "그래서일까.^n지금의 라푼젤은 『고스란히 드러나 있다』고,^n왠지 강하게 느꼈다.",
    89: "나",
    90: "저, 저기…… 갑자기 미안해.^n나는──",
    91: "라푼젤",
    92: "오늘 밤은 일찍 오셨네요, 왕자님.^n이렇게 달이 아직 젊은 시간에.",
    93: "나",
    94: "뭐…….",
    95: "내가 놀라움을 입에 담기도 전에,^n어둠 속에 빛나는 라푼젤의 얼굴이 가까워졌다.",
    96: "나",
    97: "……아…….",
    98: "머릿속이 새하얘졌다.",
    99: "라푼젤이 가깝다.^n숨결이 입술을 간질여 등골이 오싹 떨렸다.",
    100: "눈동자는 금방이라도 흘러넘칠 만큼 젖어,^n깊은 바다 같은 표면에 나만을 비추고 있다.",
    101: "눈 깜빡이는 시간조차 아깝다는 듯한 격렬한 열기가 전해져 온다.",
    102: "라푼젤",
    103: "하지만 아무리 일찍 와 주셔도,^n그래도 밤은 짧아요──그런 생각이 들어요.",
    104: "라푼젤",
    105: "낮 동안 기다리고 기다리며 애타게 기다리는데,^n밤은 언제나 한순간에 지나가 버려요.",
    106: "들뜨고 잠긴 목소리는 거미줄 같다.",
    107: "휘감겨 꼼짝 못 하게 되고,^n고치 속에 갇힌다──^n달콤하게 마비된 머리 한구석에 위험한 예감이 들었다.",
    108: "하지만 나는 이제 손끝 하나 움직일 수 없다.^n눈도 귀도 피부도 라푼젤을 느끼는 데만 집중한 채,^n내 말 따위는 듣지 않는다.",
    109: "틈조차 아깝다는 듯 밀착한 라푼젤의 몸은,^n내 체온에 녹아 버릴 듯^n나른하고 다정한 부드러움으로──",
    110: "라푼젤",
    111: "저기, 왕자님. 그러니.^n적어도 할 수 있는 만큼 함께 있어요.",
    112: "라푼젤",
    113: "제가 길고 긴 낮의 지루함에 지지 않을 만큼^n즐거운 추억을──^n받고 싶어요.",
    114: "라푼젤이 속삭이며 내 가슴을 쓰다듬는다.^n팔에 소름이 돋는 것을 느꼈다.",
    115: "향기도 감촉도 말도 온기도,^n모든 것이 달콤하고 미칠 듯하다.^n차라리 정신을 잃는 편이 편할 것 같을 정도로.",
    116: "라푼젤",
    117: "왕자님, 왜 그러세요?^n아직 그럴 마음이 들지 않으세요?",
    118: "라푼젤",
    119: "밤이 깊지 않은 것은 알고 있어요.^n하지만──분명 괜찮아요. 할머님은 오지 않아요.",
    120: "라푼젤",
    121: "그러니 부디 저를 안아 주세요.^n저는 계속 기다리고 있었어요.^n길고 긴 낮 동안 줄곧──",
    122: "그렇죠, 하고 거의 숨결 같은 목소리를 흘리며,^n내게 밀착한 몸이──촉촉하고 따뜻한 무게가^n조르듯 꿈틀거렸다.",
    123: "아마 그녀도 이제 한계일 것이다.^n자기만 몸을 밀착하고 있는 이 상황이,^n부끄럽고 애가 타서 견딜 수 없어서.",
    124: "눈꼬리에 눈물까지 살짝 고인 채 움직이지 않는 나를 원망했다.",
    125: "나는 라푼젤을…….",
    126: "끌어안았다.",
    127: "밀쳐 냈다.",
    128: "나는 가쁘게 숨을 쉬었다.^n──왜 이렇게 숨이 막히는 걸까.^n좀 더 평범하고 자연스럽고 건강한 공기를 마시고 싶었다.",
    129: "하지만 아무리 깊고 빠르고 필사적으로 숨을 쉬어도,^n꽃에서 풍기는 독 같은 달콤한 향기에서 벗어날 수 없다.^n혀끝에서 머리로 퍼져 심한 현기증만 일으킬 뿐.",
    130: "발밑이 휘청거렸다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1113.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1113_slots_00066_00130_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1113_slots_00066_00130_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
