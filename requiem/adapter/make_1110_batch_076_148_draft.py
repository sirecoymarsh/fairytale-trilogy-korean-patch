from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    76: "(음…… 토끼들은 집 안에 조약돌을 던진다.^n　케이크로 변한 그것을 먹은 앨리스는,^n　이번에는 쭉쭉 작아진다, 인가.)",
    77: "나는 내 주머니를 뒤졌다.",
    78: "나",
    79: "앨리스, 입 벌려.",
    80: "앨리스",
    81: "네……?^n──아──────…….",
    82: "앨리스는 내 의도를 알아채지 못한 듯했지만,^n입을 벌려 주었다.^n어째서인지 덤으로 목소리까지 계속 내고 있다.",
    83: "나",
    84: "조약돌이지만 너한테는 작아지는 케이크가 될 거야.^n자.",
    85: "나는 의사 선생님에게 받은 그 『약』──^n설탕으로 굳힌 초콜릿으로밖에 보이지 않는 그것을,^n앨리스의 입에 던져 넣었다.",
    86: "앨리스",
    87: "아────────……음!?　으므므므!?",
    88: "　황급히 입을 다문 앨리스.^n　그 뺨이 오물오물 움직여,^n『약』을 맛보고 있다는 것을 알 수 있다.",
    89: "앨리스",
    90: "아……!^n꺄, 와, 아…… 와아!",
    91: "그러고는 엉뚱한 소리를 지르며 앨리스가 엉덩이를 꿈틀거렸다.^n위로 치켜올리듯 흔들 때마다,^n팬티의 주름이 보기 민망한 모양을 이룬다.",
    92: "머릿속에서는 『작아지고』 있는 걸까──^n나는 황급히 시선을 돌렸다.",
    93: "앨리스",
    94: "──빠졌어요!　빠져나왔어요, 저!",
    95: "잠시 뒤 앨리스가 풀려나는 우스꽝스러운 소리와,^n튀어 오를 듯한 환호성이 들렸다.",
    96: "앨리스",
    97: "고마워요, 고마워요!",
    98: "앨리스",
    99: "다행이에요. 이번에야말로 원래 크기로…….^n불편함 없이 살아갈 수 있는 어엿한 숙녀에게 어울리는^n딱 좋은 크기로──",
    100: "앨리스",
    101: "어머, 어머, 어머어머어머!?",
    102: "당황한 목소리에 나는 앨리스를 바라보았다.",
    103: "어딘가로 빨려 들어가는 듯한 목소리를 듣고,^n이번에는 너무 작아진 것이 아닐까 생각한 나는^n상당히 그녀에게 휘둘린 모양이다.",
    104: "앨리스는 인형의 집 앞에 털썩 주저앉아 있었다.",
    105: "나와 눈이 마주치자 그녀는 흠칫 온몸을 떨었다.^n뭐랄까 도망칠 때를 놓쳐 곤란하다는 듯한^n멋쩍은 얼굴을 하고 있다.",
    106: "앨리스",
    107: "저, 저기, 고마워요…….^n그──^n상당히 효과가 강한 케이크네요.",
    108: "나",
    109: "뭐?",
    110: "앨리스",
    111: "작아진 것은 좋지만 너무 작아진 모양이에요…….",
    112: "앨리스",
    113: "당신,^n전에 만났을 때는 그렇게 크지 않았잖아요.^n저, 저기…… 밟지 말아 주세요. 부탁이에요.",
    114: "나",
    115: "뭐…… 아니, 앉아 있어서 그런 것 아니야?^n자.",
    116: "손을 내밀자 앨리스는 노골적으로 겁먹은 얼굴이 되어,^n앉은 채로 질질 뒤로 물러났다.",
    117: "앨리스",
    118: "저, 저, 저, 저기, 괘, 괜찮아요.^n저 혼자 일어설 수 있으니까…….^n미안해요, 지금은 커다란 당신이 무서워요.",
    119: "앨리스",
    120: "당신이 보기에는^n지금의 저는 개미나 애벌레 같은 존재잖아요.",
    121: "나",
    122: "그렇지는 않지만…….^n아…… 알았어.",
    123: "나는 문득 생각나 아직 펼쳐져 있던 『성서』의^n다음 페이지를 넘겼다.",
    124: "내용에 따르면 케이크로 너무 작아진 앨리스는,^n집을 나온 뒤 보통 크기의 강아지라는 괴물과 마주쳐,^n몹시 무서운 경험을 하는 모양이다.",
    125: "나",
    126: "(원, 고생이네.)",
    127: "문간으로 물러나자 앨리스는 여전히 앉은 채^n노골적으로 안도한 표정을 지었다.",
    128: "은인에게 이런 태도라니──^n하지만 짜증이 난다기보다 가엾다.",
    129: "복도로 나오자 마침 간호사 선생님이 지나가던 참이었다.",
    130: "간호사",
    131: "어머, 앨리스와 이야기하고 있었니?^n조금 특이한 데가 있지만 나쁜 아이는 아니란다.",
    132: "이 간호사 선생님은 여자다.",
    133: "내가 방금 겪은 일을 털어놓자,^n간호사 선생님은 아, 하고 맞장구치며 난감한 얼굴을 했다.",
    134: "간호사",
    135: "　지금 앨리스는 말이지,^n『이상한 나라의 앨리스 증후군』도 함께 앓고 있어.",
    136: "간호사",
    137: "『이상한 나라의 앨리스 증후군』은 『동화 증후군』과 별개로,^n　눈에 보이는 물건의 크기가 불안정해지는 병이야.^n　물건이 말도 안 되게 커 보이거나 작아 보이지.",
    138: "나",
    139: "아, 그래서.",
    140: "　앨리스가 인형의 집에 끼어 움직이지 못하고,^n　빠져나온 뒤 『거대한』 나를 무서워했던 것은,^n『성서』 때문만이 아니라 실제로 그렇게 보였기 때문이구나.",
    141: "간호사",
    142: "정말이지 『이상한 나라의 앨리스 증후군』 때문에^n원래도 깊은 증상이 한 단계 더 까다로워졌어.",
    143: "간호사",
    144: "본인이 매일 즐거워 보이는 게 그나마 다행일까.",
    145: "나",
    146: "(즐거워 보인다, 라…….)",
    147: "분명 진심으로 곤란해하고 진심으로 겁먹었던 앨리스지만,^n마음 깊은 곳에서는 즐기고 있는지도 모른다.",
    148: "그녀의 병실 전구 장식처럼,^n늘 반짝이는 앨리스의 눈동자를 떠올리며,^n나는 진심으로 납득했다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1110.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1110_slots_00076_00148_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1110_slots_00076_00148_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
