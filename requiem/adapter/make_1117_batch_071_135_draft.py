from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    71: "기억하고 있었을 『부지런한 작은 벌』조차^n흥얼거릴 수가 없어요.^n외우려 하면 전혀 다른 내용이 되어 버려요!",
    72: "심각한 얼굴로 한숨을 내쉬어 보이는 앨리스는^n원래라면 우스워야 했다.^n하지만 나는 조금도 웃을 수 없었다.",
    73: "나",
    74: "나는 구멍에 떨어지지 않았어.^n변하지도 않았고.",
    75: "앨리스",
    76: "떨어진 것도 변한 것도,^n그것째로 잊어버린 거예요.",
    77: "나는 입만 뻐끔거렸다.^n어째서 반박하지 못하는 걸까. 분하다.",
    78: "이케노",
    79: "………….",
    80: "이케노 씨는 그런 우리를 아랑곳하지 않고,^n펼친 채 한 손에 든 책을 슬쩍 보았다.",
    81: "나",
    82: "(『이상한 나라의 앨리스』인가.^n　　앨리스의 상대를 하려고 가져왔구나.)",
    83: "이케노",
    84: "　흠, 그런가.^n　그렇다면,^n『윌리엄 아버지는 늙으셨네』를 불러 보거라.",
    85: "앨리스",
    86: "어디 보자…….",
    87: "아니, 나는 괜찮아요.^n노래가 조금 엉터리가 되더라도,^n어떻게든 될 테니까요.",
    88: "이케노",
    89: "……!",
    90: "앨리스의 대답에 이케노 씨는^n누가 봐도 놀란 기색으로 눈을 크게 떴다.",
    91: "나",
    92: "왜 그러세요?",
    93: "이케노",
    94: "아니…….",
    95: "앨리스",
    96: "나보다 이 사람을 어떻게든 도와주세요!^n기억하는 것보다 기억하지 못하는 게 더 많잖아요.",
    97: "앨리스",
    98: "꾸물거리고 있다가는,^n얼마 안 되는 『기억하는 것』마저 잊어버릴 거예요!",
    99: "이케노",
    100: "………….",
    101: "이케노 씨는 한동안 긴장한 모습으로 책을 바라보다가,^n이윽고 탁 소리를 내며 책을 덮었다.",
    102: "이케노",
    103: "──괜찮아.^n그가 이 이상 무언가를 잊어버릴 일은 없으니까.",
    104: "그 말은 분명 『애벌레』의 것이 아니었다.",
    105: "앨리스",
    106: "정말요? 정말이죠, 애벌레 씨?",
    107: "절반은 안도하고, 절반은 아직 확답이 부족하다는 듯^n앨리스가 이케노 씨에게 바싹 다가선다.",
    108: "이케노 씨는 입가에 간신히 남은^n담배 모양 초콜릿을 와작와작 깨물면서,^n몇 번이나 『괜찮아』라고 되풀이했다.",
    109: "나와 이케노 씨는 함께 앨리스의 방에서 나왔다.^n달램을 받고 진정한 앨리스는^n갑자기 졸음이 밀려온 듯 낮잠에 들어 버렸기 때문이다.",
    110: "나",
    111: "저기, 이케노 씨.^n아까 그건…….",
    112: "이케노",
    113: "아, 놀랐어.^n엉터리 『윌리엄 아버지』를 암송하는 장면인데,^n설마 앨리스가 『성서』에서 벗어난 행동을 하다니.",
    114: "이케노 씨는 손에 든 『이상한 나라의 앨리스』로^n시선을 떨군 채 중얼거린다.",
    115: "나",
    116: "그럼 앨리스는 조금씩 낫기 시작했다는 뜻인가요?",
    117: "이케노",
    118: "　그렇게 극적인 변화는 아니야…….^n『본래의 그녀』가 하고 싶은 일이^n『성서』의 전개를 뛰어넘은 거라고 생각해.",
    119: "이케노",
    120: "좀처럼 있는 일은 아니야.",
    121: "이케노 씨는 다정한 눈으로 나를 본다.",
    122: "이케노",
    123: "『앨리스』는 아까도 말했지만 대화하는 등장인물이 많고,^n　정신없이 흘러가는 이야기라 우리도 만날 때마다^n　서로 다른 존재로 인식되는 경우가 많아.",
    124: "이케노",
    125: "모자 장수에 삼월 토끼, 체셔 고양이──^n나는 같은 이름으로 불린 적이 한 번도 없어.",
    126: "이케노",
    127: "그런 앨리스가 너는 잘 기억하는 것 같더군.^n뭐였지? 회색 펠리컨?",
    128: "나",
    129: "아, 네. 처음 만났을 때 그렇게 불렸어요.",
    130: "이케노",
    131: "역시 그랬구나.^n──앨리스는 네가 걱정되는 거야.",
    132: "나",
    133: "………….",
    134: "나는 무슨 말을 해야 할지 알 수 없었다.",
    135: "그저 앨리스가 깨어날 즈음 다시 찾아와^n또 그녀와 이야기하리라 마음먹었다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1117.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1117_slots_00071_00135_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1117_slots_00071_00135_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
