from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    69: "자기 망상 속에서 마음대로 살아가는 그녀들이지만,^n말을 걸면 내용을 제대로 이해하고^n나름대로 대답해 준다.",
    70: "때로는 앨리스처럼 자신의 세계를 무시하면서까지^n나를 걱정해 주기도 한다.",
    71: "망상의 세계에 사는 그녀들은 자기 머리 바깥──^n의사 선생님과 간호사들의 존재나 진찰 같은 행위를^n어떻게 받아들이는 걸까?",
    72: "의사",
    73: "그건 오랫동안 우리도 의문을 품은 부분이라,^n아직 확증을 얻은 것은 아니지만.",
    74: "의사",
    75: "보고 있지만 보지 않는다.^n듣고 있지만 듣지 않는다.^n──라는 게 맞는 듯해.",
    76: "나",
    77: "아…….",
    78: "갑자기 신기한 시를 암송해 준 듯한 기분이 들어,^n나는 고개를 갸웃했다.",
    79: "의사",
    80: "음, 얼마 전에도 쿠라시나 군과 이야기했는데.^n우리는 무대 뒤편의 스태프가 아닐까 하고.",
    81: "나",
    82: "무대 뒤편이요?",
    83: "의사",
    84: "그녀들은 배우고 우리는 스태프라는 거야.^n무대 뒤에서 기다리다가 배우가 돌아오면 수건이나 물을 건네지.^n때로는 옷을 갈아입는 걸 돕고 화장을 고쳐 줘.",
    85: "의사",
    86: "무대 뒤에서 스태프의 보살핌을 받은 배우는 출연할 때 마음을 바꾸고,^n배역에 완전히 몰입해 무대로 나가.^n무대 위에서 그 역할로서의 삶을 다하는 거지.",
    87: "의사",
    88: "즉 그녀들에게는 무대 위가 진짜 삶이라는 거야.",
    89: "나",
    90: "그…… 그렇군요…….",
    91: "나는 그렇게 애매하게 맞장구치는 것이 고작이었다.^n알 것 같기도, 모를 것 같기도 했다.",
    92: "의사",
    93: "──그렇게 생각하면 아쉽군.^n그 아이들 하나하나가^n본래는 훌륭한 배우가 될 수 있었을지도 몰라.",
    94: "의사 선생님의 말에 무언가 걸리는 것을 느끼며,^n나는 이번에야말로 진찰실을 뒤로했다.",
    95: "나는 내 방을 향해 복도를 걷기 시작했다.",
    96: "방에 돌아가도^n심심함을 견디지 못해 다시 산책하러 나가겠지만,^n기분을 전환하는 계기는 필요하니까.",
    97: "이케노",
    98: "안녕, 나나시 군.^n진찰은 끝났니?",
    99: "나",
    100: "아…….",
    101: "모퉁이에서 이케노 씨와 마주쳤다.",
    102: "나",
    103: "아, 네.^n이제 방으로 돌아가려던 참이에요.",
    104: "이케노",
    105: "마침 잘됐네!^n자, 이거.",
    106: "이케노 씨는 한쪽 팔에 안고 있던^n반듯하게 개킨 천 뭉치를 내게 내밀었다.",
    107: "나",
    108: "뭔가요?",
    109: "이케노",
    110: "네 옷이야.^n낮이고 밤이고 늘 지급된 환자복만 입으면 재미없잖아.",
    111: "나",
    112: "아니, 저는 이대로도 딱히…….",
    113: "회색 환자복이 세련됐다고 하기는 확실히 어렵다.",
    114: "하지만 넉넉하게 입을 수 있어 편하고,^n아침저녁으로 풀 먹인 옷이 배달되고,^n나는 제법 마음에 드는데.",
    115: "나",
    116: "(뭐, 이 옷 때문에 앨리스가^n　나를 회색 펠리컨으로 본 거지만…….)",
    117: "이케노",
    118: "애초에 그렇게 흐릿한 옷만 입고 있으니까,^n넌 더더욱 자기 자신이라는 것을 붙잡지 못하는 거야.^n나는 그렇게 생각해.",
    119: "나",
    120: "아, 네…….",
    121: "이케노",
    122: "이제 겉모습부터 시작해 볼까!^n이거라면 행복한 왕자든 푸른 수염 공작이든,^n그럴듯하게 보일 거야!",
    123: "이케노 씨의 미소에 눌려,^n나는 거절하지도 못하고 옷을 받았다.",
    124: "나",
    125: "(──행복한 왕자도 푸른 수염 공작도,^n　둘 다 싫은데…….)",
    126: "나",
    127: "(──흐음, 이런 옷이구나.)",
    128: "치수라도 잰 듯 딱 맞는다.",
    129: "디자인도 뭐랄까, 거창하지만 나쁘지 않다.^n──고 생각한다.",
    130: "거울이 없어서 내게 어울리는지는 모르겠지만.",
    131: "나",
    132: "(뭐, 계속 환자 같은 차림인 것도 그러니…….^n　좋아, 이걸로.)",
    133: "예쁜 드레스를 입은 앨리스나 라푼젤 앞에 나섰을 때,^n환자복의 촌스러움으로 상대의 세계를 망치는 듯해서^n주눅 들 때도 있었다.",
    134: "　이거라면 이케노 씨가 말했듯,^n『그럴듯하게 보인다』^n　는 느낌이 든다.",
    135: "　다만 이케노 씨가 말한 또 하나의^n『겉모습부터 시작한다』는 의미는^n도무지 알 수 없었다.",
    136: "　평소보다 단정한 옷차림으로 바꿔도 내 안에서는^n『내가 누구인가』에 관한 단서 따위가^n조금도 솟아나지 않았기 때문이다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1122.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1122_slots_00069_00136_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1122_slots_00069_00136_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
