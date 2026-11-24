from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    56: "???",
    57: "이름을 댈 이름이 없다면 어쩔 수 없지.^n난 있으니까 말해 둘게.^n──나는 오딜.",
    58: "오딜",
    59: "이 아이가 오데트야.",
    60: "그러고는 호수와 지면의 경계에 있던 백조 장식물 곁으로 가서,^n가볍게 두드려 가리켰다.^n자세히 보니 그 백조만 왕관을 쓰고 있었다.",
    61: "나",
    62: "오딜……과. 오데트?",
    63: "오딜",
    64: "그래. 오데트야.",
    65: "오딜",
    66: "밤이 되면 조금은 나은 모습이 되지만,^n유감스럽게도 지금은 낮이잖아.^n이 얼빠진 모습이나 한번 봐 줘.",
    67: "툭툭 백조의 몸통을 두드린다.^n속이 빈 것인지 얼빠진 소리가 났다.",
    68: "진심인지 농담인지 알 수 없어 오딜을 바라보았지만,^n여전히 요염하게 웃고 있을 뿐이다.^n내 당황을 즐기고 있다는 것만은 전해졌다.",
    69: "나",
    70: "그, 묻고 싶은 건 내 기억에 관한 거야.^n왜 이렇게 됐는지, 어떻게 해야 하는지,^n아무것도 몰라서…….",
    71: "오딜",
    72: "이상한 소리를 하네.^n그런 건 『성서』를 읽으면 알 수 있잖아.",
    73: "필사적인 호소를 가로막듯 말하니, 나는 당황할 수밖에 없었다.",
    74: "나",
    75: "『성서』?",
    76: "그러고 보니 앨리스도 그런 말을 했었다.^n분명 한 손에 들고 있던 책을…….",
    77: "오딜",
    78: "그래, 누구나 가지고 있어.",
    79: "오딜은 내 머릿속을 읽은 듯,^n손에 든 책을 자랑하듯 보여 주었다.",
    80: "검은 가죽 표지에 『백조의 호수』라고 쓰인 것이 보였다.",
    81: "나",
    82: "(──『백조의 호수』는 분명 발레 아니었나?)",
    83: "오딜",
    84: "네가 어떤 인간이고, 앞으로 누구를 만나며,^n어떻게 해야 하는지 전부 적혀 있어.^n──잃어버리다니, 얼빠진 짓이네.",
    85: "나",
    86: "잃어버린…… 걸까.",
    87: "오딜",
    88: "가지고 있지 않다면 잃어버린 거겠지.^n꽤나 축 처진 불쌍한 얼굴을 하고 있지만,^n과거도 미래도 책 한 권만 찾으면 어떻게든 되는 거야.",
    89: "그럴 리가 없다는 생각은 사라지지 않지만,^n그랬으면 좋겠다는 마음도 부풀어 올라,^n마음속이 엉망진창이다.",
    90: "그야말로 이 음울한 숲을 헤매는 듯한 기분이^n그저 『내 책』을 찾는 것만으로 후련해진다면,^n이보다 쉬운 일은 없다.",
    91: "그래, 이제야 희망의 빛을 찾았다고 생각했는데.",
    92: "오딜",
    93: "하지만 지금쯤 불에 타거나 찢기거나 낙서투성이가 됐을지도──^n후후, 충분히 있을 법한 일이네.",
    94: "오딜은 태연하게 내 희망에 흠집을 낸다.^n목을 울리며 웃기까지 했다.",
    95: "오딜",
    96: "아하하, 걸작이야!　『성서』를 놓친 것 하나 때문에,^n과거와 미래까지 바뀌어 버리다니.^n자신의 얼빠진 정도를 저주하는 게 좋겠네.",
    97: "나는 그녀를 노려보려──^n불안을 감추기 위해 화를 내려고 했지만,^n붉은 눈동자에 응시당해 결국 시선을 돌리고 말았다.",
    98: "오딜에게는 『성서』가 있다.^n자신이 누구고 어떤 과거가 있으며, 앞으로 무엇을 해야 하는지,^n──전부 알고 있다고 한다.",
    99: "지금의 나에게는 그것이 터무니없이 부러우면서도,^n도저히 손에 넣지 못할 아득한 희망처럼 느껴져,^n정면으로 그녀의 눈동자와 맞설 수 없었다.",
    100: "나",
    101: "……고마워. 참고가 됐어.",
    102: "딱딱한 목소리로 겨우 말하고 등을 돌렸다.",
    103: "오딜",
    104: "찾으면 좋겠네.^n소중하고 소중한, 너 자신을 말이야.",
    105: "들뜬 목소리가 가차 없이 쫓아온다.",
    106: "문 너머로 도망쳐,^n기분을 전환하려고 심호흡을 해 보아도,^n나는 어쩔 수 없이 비참한 기분이었다.",
    107: "내 『성서』는 어디로 간 걸까.^n그것만 있으면 분명 모든 일이 잘 풀릴 텐데.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1104.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1104_slots_00056_00107_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1104_slots_00056_00107_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
