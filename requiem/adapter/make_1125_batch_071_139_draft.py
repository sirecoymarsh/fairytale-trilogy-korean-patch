from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    71: "하, 하지만…… 그런 건 괜찮아.^n나, 괜찮다고 했어. 말했다고.^n나, 나는 혼자 할 테니까…… 할 수 있으니까.",
    72: "오딜",
    73: "그러니까 이제 듣기도 지겹다니까.^n너도 얼른 준비를 끝내고^n그 왕자님을 만나러 가고 싶잖아.",
    74: "오데트",
    75: "아……!",
    76: "오딜이 『왕자님』이라는 말을 입에 담은 순간,^n오데트는 작게 소리를 내며 온몸을 떨었다.",
    77: "가엾을 만큼 굳어 있던 어깨에서^n갑자기 힘이 빠지는 모습이 내게도 보였다.^n어쩐지 『녹아내리는』 듯 흐물흐물 풀리는 모습.",
    78: "오딜",
    79: "잠깐, 하기 어렵잖아. 똑바로 서.",
    80: "오딜",
    81: "정말이지, 이런 말 한마디에 발정하지 마.^n뭐, 그 『왕자님』은──『지크프리트』는,^n너한테는 기다리고 기다린 운명의 사람이겠지만.",
    82: "오데트",
    83: "후아, 아, 으…….",
    84: "오딜이 연달아 퍼붓는 핵심어와,^n타이츠 가장자리를 힘껏 다시 당기는 몸짓에,^n오데트는 마치 고삐를 당긴 듯 반응하고 있다.",
    85: "걷어 올린 치마를 쥔 손끝이 갈 곳 없이 꼼지락거리고,^n받침대 위에 올린 다리가 잘게 흔들린다.",
    86: "무언가 말하고 싶은 듯 입술이 떨리지만,^n흘러나오는 것은 요염하게 흐트러진 숨소리와,^n말이 되지 못한 끊어진 목소리뿐.",
    87: "오딜",
    88: "있잖아, 허리를 이상하게 움직이는 거 그만두지 않을래?^n난 왕자님이 아닌데.",
    89: "오데트",
    90: "우, 우, 움직이지 아……!^n빠, 빨리, 빨리 해 줘, 오딜.",
    91: "수치와 굴욕으로 크게 뜬 눈동자는^n초점을 잃고 촉촉이 젖어 부들부들 흔들리며,^n당장이라도 금빛이 되어 흘러나올 듯하다.",
    92: "오딜",
    93: "나도 얼른 끝내고 싶은데.^n누가 제멋대로 달아오르는 바람에 손이 빗나가잖아.",
    94: "오딜",
    95: "──이러고도 움직일 생각은 없었다니,^n정말…… 뭐랄까.^n기가 막힐 만큼 그거네, 너. 진짜배기야.",
    96: "오딜이 『진짜배기』를 뜻깊게 발음하는 것을 듣고,^n나는 낮에 막 알게 된 단어를 떠올렸다.^n",
    97: "──창녀.",
    98: "오데트",
    99: "아아, 아. 미, 미안…….^n……으…… 큭.",
    100: "오데트는 울먹이면서 입술을 다물고 목소리를 삼킨다.^n그녀가 몸속에서 생겨나는 충동과 필사적으로 싸우는 것이^n그 표정에서 전해져 온다.",
    101: "하지만 오딜은 그 노력을 비웃듯,^n귓가에 마지막 일격을 불어넣었다.",
    102: "오딜",
    103: "──정말 쉽게 반한다니까.",
    104: "오데트의 온몸이 다시^n거의 튀어 오르듯 움찔 떨렸다.",
    105: "오딜을 돌아보는 그 얼굴에 스친 것은^n한없이 『전율』에 가까운 무언가였다.",
    106: "오데트",
    107: "바, 반해……?^n아, 아니, 아니야, 나는…….",
    108: "오딜",
    109: "좋아하게 됐잖아.^n왕자님을. 지크프리트를.",
    110: "오데트",
    111: "아니야, 아니야.^n어, 어제 처음 만났고 그게 전부야.^n멋진 분이라고는 생각했지만 그런, 아…… 아니야.",
    112: "오딜",
    113: "숨겨도 소용없어. ──내가 누군 줄 알아?^n너에게 저주를 건 올빼미 악마 로트바르트의 딸이야.^n전부 훤히 보인다고…….",
    114: "오딜은 붉은 입술을 일그러뜨리며,^n손에 든 금속 장식을 달칵거리며 가지고 논다.",
    115: "그리고 이번에야말로 벨트를 채워 주는──척하다가^n장식 끝에 걸어 끼우려 한 것은,^n보기만 해도 부드러울 듯한 오데트의 허벅지 살이었다.",
    116: "오데트",
    117: "아파……!",
    118: "오딜",
    119: "봐, 손이 빗나갔잖아.",
    120: "악의가 선명하게 배어나는 몸짓.^n그런데도 오딜은 가엾다는 듯 시치미를 뗀다.",
    121: "오딜",
    122: "좋잖아, 서로 사랑하는 건 멋진 일이야.^n아버님의 저주도 영원한 사랑의 맹세로 풀리니까.^n토할 만큼 아름다운 이야기라고 생각해.",
    123: "오딜",
    124: "──다만 너는 데자뷔가 스쳐 가지만.^n관객인 나로서는 조금 물렸어.",
    125: "오데트",
    126: "──윽, 크……!^n………………으, 으…….",
    127: "오데트는 순간 눈을 크게 뜨며,^n무언가 따져 들려 했다.",
    128: "하지만 핏기를 잃은 입술은 말을 잊은 듯 열렸다 닫히고,^n이윽고 허무하게 다물렸다.",
    129: "마지막으로 그녀의 얼굴에 떠오른 것은,^n절망이나 체념 같은 것이었던 듯하다.^n──하지만 나는 잘 기억나지 않는다.",
    130: "정신을 차리자 나는 힘이 잘 들어가지 않는 다리를 억지로 움직여,^n그 흑백의 문에서 조금이라도 멀어지려 하고 있었다.",
    131: "──대체 나는 무엇 때문에 어떻게 충격받은 걸까.",
    132: "두서없는 생각으로 그런 것을 계속 고민한다.",
    133: "오데트가 『왕자』라는 말에 반응하며 보인^n발정한 표정과 몸의 떨림 때문인가.",
    134: "오딜의 말 곳곳에서 엿보이는,^n오데트가 쉽게 반한다는 점 때문인가.",
    135: "아니면 뒤에서 오데트를 붙잡은 오딜이^n눈을 가늘게 뜨며 지은 야만적인 미소 때문인지도 모른다.",
    136: "먹잇감을 붙잡은 짐승이 목덜미를 물기 직전,^n자기도 모르게 턱의 힘을 풀어 버리는──그런 종류의 미소였다.",
    137: "나",
    138: "………….",
    139: "나는 오싹하며 몸을 떨고,^n지금은 더는 아무것도 생각하지 않겠다고 마음먹었다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1125.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1125_slots_00071_00139_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1125_slots_00071_00139_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
