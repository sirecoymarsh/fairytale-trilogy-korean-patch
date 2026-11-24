from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    151: "혼잣말 같은 그 목소리는 힘이 없었다.",
    152: "　그녀는 구원을 믿지 않는 걸까.^n『성서』에서는 언젠가 왕자님이 나타나^n　불행한 오데트 공주를 구하는 줄거리일 텐데.",
    153: "『내게 그런 것이 찾아올 리 없어』라고,^n　굳어진 옆얼굴은 그렇게 말하는 듯했다.",
    154: "그리고 그것이 사실임을 나는 알고 있다.^n왕자님은 없다.^n그 역할을 맡은 사람이 없다.",
    155: "오딜은 앞으로도 오데트를 계속 비웃고,^n미운 상대를 미워하지 못하는 마음은 계속 상처받겠지.",
    156: "──오데트는 어쩌면^n그런 자신의 운명을 알고 있을지도 모른다.",
    157: "오데트",
    158: "그런데 완전히 묻는 걸 잊었는데, 너는 누구야?",
    159: "오데트는 부자연스럽게 밝은 말투로 바꾸어^n그렇게 물었다.^n시선은 아직 먼 수면을 헤매고 있다.",
    160: "오데트",
    161: "의사 선생님도 간호사 선생님도 아닌 것 같고.^n그런데 『성서』도 가지고 있지 않네.",
    162: "나",
    163: "아…….",
    164: "나는 말을 더듬었다.",
    165: "　지금까지처럼 대답하면 된다.^n　기억이 없고 이름도 모른다.^n『성서』는 분명 있었겠지만 그것도 기억나지 않는다고.",
    166: "그런데도 입이 제대로 움직이지 않은 것은,^n또 하나의 대답이 머리 한구석에 생겼기 때문이다.^n처음에는 조심스럽던 그것이 여름 구름처럼 부풀어 오른다.",
    167: "저주를 풀 『구원』을 이토록 먼 눈으로^n계속 기다리는 오데트.^n그녀에게 그것을 주려면 어떤 이름을 말하면 된다.",
    168: "　오데트 공주를 만난 순간 사랑에 빠지고,^n『영원한 사랑의 맹세』를 나누어 저주를 풀려 했던 왕자님.^n　──지크프리트 왕자.",
    169: "나는 오데트에게…….",
    170: "솔직하게 말한다.",
    171: "지크프리트라고 말한다.",
    172: "나",
    173: "나, 나는…….",
    174: "나",
    175: "──지크프리트.",
    176: "내가 그렇게 이름을 댄 것은 대체 무엇 때문이었을까.",
    177: "모든 것을 포기한 오데트의 근심 어린 얼굴인가.^n아니면 눈을 가늘게 뜨고 입가를 비트는 오딜의,^n초승달처럼 날카로운 미소에 대한 반발인가.",
    178: "오데트",
    179: "네…….",
    180: "오데트가 숨을 삼키고 기세 좋게 나를 바라보았다.",
    181: "정체 모를 먼 환상을 쫓던 눈동자의 초점이,^n갑자기 선명하게 맺힌다.",
    182: "──바로 이 나에게.",
    183: "오데트",
    184: "지크프리트…….^n지크프리트 왕자님……?",
    185: "달아나고 싶을 만큼 부끄러운 호칭이었다.",
    186: "하지만 나는 견뎠다.^n오데트의 뺨이 안쪽에서 배어 나오듯^n장밋빛으로 물들었기 때문이다.",
    187: "오데트",
    188: "왕자님…….^n계속, 계속 기다리고 있었어요.",
    189: "오데트",
    190: "『성서』는 당신 이야기를 알려 주었지만,^n　어딘가에서는 믿지 않았어요.^n　제게 구원 같은 건 오지 않는다고 생각했어요…….",
    191: "오데트",
    192: "하지만 사실 당신을 보았을 때,^n혹시 그렇지 않을까 생각했어요.^n이 가슴의 두근거림──지크프리트 님.",
    193: "오데트",
    194: "다행이에요. 드디어 만났어요…….",
    195: "나",
    196: "………….",
    197: "금빛 눈동자가 젖어 내 모습을 비춘 채 흔들렸다.^n분명 내 눈에서도 똑같은 일이 일어나고 있다.",
    198: "떨리는 목소리를 듣고 있자니,^n가슴이 조여 오는 듯한 기분이 들었다.^n티끌 하나 없는 깊은 애정이 전해졌기 때문이다.",
    199: "『어느 밤, 사냥을 나간 지크프리트 왕자는^n　숲속 깊은 곳에서 오데트 공주를 만납니다.^n　두 사람은 한순간에 사랑에 빠졌습니다.』",
    200: "『성서』에 쓰인 대로 오데트는 사랑에 빠졌다.",
    201: "줄거리대로 자신의 마음을 비틀어 버리는 것,^n그것이 바로 『동화 증후군』의 광기겠지.^n하지만 그렇기에 그 마음은 순수하고 확실하다.",
    202: "나",
    203: "그──^n님 같은 건 붙이지 않아도 돼.^n왕자님이라는 것도 간지럽고.",
    204: "오데트",
    205: "네…… 하지만.^n왕자님은 왕자님이고…….^n제대로 부르지 않으면 제가 실례하는 게 아닐까요.",
    206: "나",
    207: "음…… 그렇다면 편한 대로 불러.",
    208: "오데트",
    209: "네.",
    210: "오데트는 천진하게 웃으며,^n튀어 오르듯 가벼운 발걸음으로 내게 바싹 다가왔다.",
    211: "──나는 잔혹한 짓을 했는지도 모른다.^n오데트와 막 만난 나는 그녀를 가엾게 여겨^n구하고 싶다고 생각했지만 사랑하지는 않았으니까.",
    212: "　하지만 오데트의^n『세상에서 단 한 명뿐인 자기편을 향한 미소』를 보고 있자니,^n　변덕이 운명으로 바뀌어 갈 듯했다.",
    213: "오데트",
    214: "저기, 왕자님, 지크프리트 님.^n저곳을 아세요?",
    215: "개울을 따라왔던 길을 되짚는 도중,^n오데트는 나무 너머로 보이는 건물을 가리켰다.^n도서관이다.",
    216: "오데트",
    217: "책이 아주 많아요.^n저는 책 읽는 걸 좋아해서 자주 가요.",
    218: "나",
    219: "응, 한 번 가 봤어. 오늘 낮에.",
    220: "오데트",
    221: "그렇군요.^n왕자님은 어떤 책을 읽으세요?",
    222: "나",
    223: "오늘은 『이상한 나라의 앨리스』와 『헨젤과 그레텔』,^n그 밖에도 여러 가지 읽었어.",
    224: "그러고 보니 『동화 증후군』 환자들은,^n다른 이야기나 다른 환자를 어떻게 생각할까.",
    225: "슬쩍 살펴보자,^n오데트가 웃으며 고개를 끄덕이는 참이었다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1112.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1112_slots_00151_00225_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1112_slots_00151_00225_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
