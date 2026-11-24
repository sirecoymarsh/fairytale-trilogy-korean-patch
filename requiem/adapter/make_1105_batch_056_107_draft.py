from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    56: "내가 말한 것은 동화 제목이었다.^n그런데도 그녀는 『정답』이라는 듯^n활짝 미소 지었다.",
    57: "라푼젤",
    58: "네, 맞아요.^n──할머님도 참, 역시 알고 계셨잖아요.^n몸조심하세요.",
    59: "앨리스가 자신을 『앨리스』라고 믿는 것처럼,^n그녀 역시 『라푼젤』이라는 자각이 있다.^n그런 뜻일까.",
    60: "나",
    61: "아, 아니, 나는 그게…… 네 말을 듣고 짐작했을 뿐이야.^n사실은 할머님 같은 게 아니야.",
    62: "라푼젤",
    63: "어머, 아직도 그런 말씀을…….^n",
    64: "어쩔 수 없네요.^n할머님 마음이 풀릴 때까지 제가 맞춰 드릴게요.",
    65: "라푼젤은 우아한 손짓으로 둥근 의자를 권했다.^n나는 그 하얀 손끝에 조종당하듯 털썩 걸터앉았다.",
    66: "나",
    67: "저, 기억이 없어요.^n정신을 차려 보니 하얀 방의 침대 위에 누워 있었고…….^n이름도 살던 곳도 가족도 아무것도 모르겠어요.",
    68: "나",
    69: "왜 여기에 있는지, 어떻게 해야 하는지──^n그게, 어쨌든 곤란해.",
    70: "라푼젤",
    71: "……그렇군요. 그건 불안하시겠어요.",
    72: "라푼젤에게 나는 아직^n골치 아픈 치매가 생겨 버린 할머님이다.",
    73: "그런데도 라푼젤은 어이없다는 기색 없이,^n오히려 진심으로 동정하며 고개를 끄덕였다.",
    74: "라푼젤",
    75: "그러게요.^n제가 아는 한 어제 낮에 오셨을 때는,^n평소와 다름없는 할머님이셨어요.",
    76: "라푼젤",
    77: "성함이라면 제가 바로 답해 드릴 수 있어요.^n할머님은 고델 할머님이세요.^n자. 괜찮으시면 이것을 보시겠어요?",
    78: "그러면서 라푼젤은 방금 덮은 책을 집어 들어,^n표지가 보이도록 내게 내밀었다.",
    79: "──『라푼젤』.^n그녀 자신의 이름이 동화 제목으로 그곳에 적혀 있다.",
    80: "나",
    81: "그건…….",
    82: "라푼젤",
    83: "『성서』랍니다.^n　제 이야기가 무엇이든 적혀 있어요.^n",
    84: "　──앗.",
    85: "자랑스럽게 보여 주던 라푼젤은 다음 순간,^n무언가를 깨닫고 눈에 띄게 당황했다.",
    86: "라푼젤",
    87: "그──어디까지나 제 『성서』니까요.^n할머님께 보여 드릴 수 없는 페이지도 있지만──^n이름 부분을 살짝 보여 드리는 정도라면…….",
    88: "나",
    89: "(──아, 그렇구나.)",
    90: "노골적으로 굳어 있는 라푼젤의 표정을 보며,^n나는 마음속으로 납득했다.",
    91: "라푼젤은 분명 라푼젤이 고델 할머니를^n배신하고 결별하는 이야기다.",
    92: "『고델 할머니』 본인에게 그 전개를 들키면^n　배신이 드러나고 만다.^n　이야기 전체가 어긋나고 말겠지.",
    93: "그래서 나는,",
    94: "나",
    95: "그건 괜찮아요.",
    96: "손을 내저어 그녀를 안심시켰다.",
    97: "라푼젤",
    98: "그러신가요……?　사양하지 않으셔도 괜찮아요.^n할머님도 자신의 이름조차 모르시면^n불안하시잖아요.",
    99: "마음씨 착한 라푼젤은 눈에 띄게 안도하면서도^n할머님을 걱정하는 것을 잊지 않았다.",
    100: "하지만 나는 작별을 고하며 자리에서 일어났다.^n더 있어 봐야 라푼젤에게 쓸데없는 신경만 쓰게 할 뿐,^n의미가 없다고 생각했기 때문이다.",
    101: "나",
    102: "괜찮아요. 마음만 받을게요…….^n그…… 저는 이제 가 볼게요.",
    103: "라푼젤",
    104: "어머, 벌써 가시려고요?^n저는 아직 허리도 어깨도 봐 드리지 못했는데요.",
    105: "그렇게 말하며 나를 뒤쫓듯 일어난 라푼젤의^n망토 자락에서 무언가가 흘러나왔다.",
    106: "단단히 땋여,^n바닥 위에 길게 똬리를 튼 밧줄 같은 것.",
    107: "그것은 『라푼젤』이라는 이야기의 상징인 동시에,^n라푼젤이 품은 배신의 비밀과도 깊이 얽힌,^n그녀 자신의 길고 긴 금빛 머리카락이었다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1105.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1105_slots_00056_00107_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1105_slots_00056_00107_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
