from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    131: "두 사람의 몸무게를 지탱하며 균형을 잡으려면,^n라푼젤의 깊고 아름답게 잘록한 허리에 팔을 감아^n힘껏 끌어당길 수밖에 없었다.",
    132: "아니면 그것은 착각이고,^n라푼젤을 끌어안기 위한^n핑계였는지도 모른다.",
    133: "어느 쪽이든,^n내 팔은 나도 모르는 사이 움직여,^n그저 정신없이 힘을 주고──",
    134: "서로 온기를 나눌 만큼 단단히 포옹하고 있었다.",
    135: "라푼젤",
    136: "아아……!",
    137: "라푼젤이 흘린 목소리는 기쁨에 찬 울림으로^n내 가슴께를 간지럽게 떨었다.",
    138: "라푼젤",
    139: "왕자님, 아아, 나의 왕자님──^n오늘 밤도 만날 수 있어 다행이에요.",
    140: "라푼젤",
    141: "사랑해요.^n당신을 만날 수 있는 것이 제 유일한 기쁨이에요.^n사랑해요. 사랑해요…….",
    142: "나",
    143: "아…….",
    144: "아마 라푼젤은,^n다음으로 내 입술을 원했던 것 같다.",
    145: "내 뺨에 손을 대고 진심으로 사랑스럽다는 듯 눈을 가늘게 뜨며,^n부끄러운 듯 살며시 얼굴을 가까이 가져왔다.",
    146: "나",
    147: "(아, ──아.)",
    148: "하지만 나는,^n그녀의 눈동자에 비친 내 그림자가 이쪽으로 다가오는 것을 보고,^n어째서인지 갑자기 온몸의 체온이 내려감을 느꼈다.",
    149: "얼음 같은 온도의 응어리.^n그것은 두려움이었는지도 모른다.^n가슴이 아프고 괴로워져 완전히 짓눌렸다.",
    150: "나",
    151: "──읏, 미안해!",
    152: "나는 라푼젤의 어깨를 잡아 떼어 내며,^n뒤로 뛰어 물러났다.",
    153: "라푼젤",
    154: "네……!?　아…….",
    155: "라푼젤은,^n미칠 듯한 나에 대한 집착과 그것을 갑자기 빼앗긴 충격으로^n금이 간 듯한 눈을 하고 있었다.",
    156: "사랑해요, 사랑해요──",
    157: "그녀의 정열적인 속삭임은^n아직도 내 귓속에서 소용돌이치는데,^n나 자신도 참 너무한 짓이라고 생각한다.",
    158: "나",
    159: "으, 으…….",
    160: "나",
    161: "──미안해!",
    162: "나는 라푼젤의 어깨를 잡아 떼어 내며,^n뒤로 뛰어 물러났다.",
    163: "라푼젤",
    164: "네……!?　아…….",
    165: "라푼젤은 아직도 나른하게 젖은 눈동자에^n거절당한 슬픔을 띠고 나를 보았다.^n마음이 아팠다.",
    166: "라푼젤",
    167: "왜 그러세요, 왕──",
    168: "나",
    169: "미안해, 나는 아니야.^n너는 사람을 잘못 봤어.^n──미안해, 미안합니다.",
    170: "묻는 라푼젤의 말을 가로막고 멋대로 사과만 늘어놓는다.^n나는 『왕자님』이 아니다.",
    171: "라푼젤",
    172: "네, 무…….",
    173: "나",
    174: "미안해, 그…….^n자, 잘 자.^n내, 내일 또 보자!",
    175: "어색하게 말을 흩뿌리는 내 목소리는^n볼품없이 뒤집히고 발음만 허무할 만큼 밝아서,^n마치 어린아이의 마지막 허세 같았다.",
    176: "문으로 곧장 달아났다.^n라푼젤의 얼굴을 볼 용기가 없었다.",
    177: "나",
    178: "(내가 밤에 머리카락을 타고 나타나서,^n『왕자님』이라고 생각한 거구나…….)",
    179: "『라푼젤』 원작에 따르면,^n　그녀는 고델 할머니에게 탑 위에 갇혀^n　다른 사람과 떨어져 지낸다.",
    180: "그녀의 보금자리에 나타나는 것은 원래,^n고델 할머니와^n몰래 드나들게 된 『왕자님』뿐이다.",
    181: "하지만 이 『낙원』의 환자인 가짜 라푼젤의 방에는^n의사와 간호사 선생님도 드나드니──^n그녀는 그 모순을 해결하려고 인식을 비틀고 있는 것이겠지.",
    182: "즉,^n낮에 찾아오는 사람을 『고델 할머니』,^n밤에 오는 사람을 『왕자님』으로 여기는 것이다.",
    183: "나",
    184: "(아아…… 경솔했어.)",
    185: "내가 머리카락 사다리를 올라 보고 싶다는^n바보 같은 호기심에 움직인 탓에,^n라푼젤에게 상처를 주고 말았다.",
    186: "밤에 몰래 찾아오는 『왕자님』만을 마음의 버팀목으로 삼는^n그녀의 마음을 가지고 논 셈이다──",
    187: "나",
    188: "(내일 제대로 사과하자.)",
    189: "터덜터덜 복도를 걸으며 나는 한숨을 쉬었다.",
    190: "물론 내일 낮에 찾아가도,^n나는 『고델 할머니』로 보일 테니,^n사과의 말은 라푼젤의 마음에 닿지 않겠지만.",
    191: "이 답답한 마음을 조금이라도 어떻게 할 수 있다면,^n이제는 자기만족이라도 상관없다.",
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1113_slots_00131_00191_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1113_slots_00131_00191_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
