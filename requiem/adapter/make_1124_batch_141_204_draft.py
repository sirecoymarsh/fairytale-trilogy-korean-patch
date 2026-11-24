from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    141: "……응.",
    142: "그레텔은 여전히 어색한 표정으로 고개를 끄덕인다.",
    143: "그레텔",
    144: "우, 우리 집…… 가난한데 먹을 입만 많으니까,^n많이 먹지 못해도^n사치 부리면 안 된다고…… 엄마가.",
    145: "나",
    146: "아, 아아…….",
    147: "나",
    148: "(아니, 병원 식사니까 메뉴는 같을 테고,^n　충분한 양이 나오는 것 같은데.)",
    149: "나는 목구멍까지 나온 말을 삼켰다.",
    150: "　진심으로 슬픈 듯 중얼거리는 그레텔에게,^n『네 위가 클 뿐이야.』^n　라고 말할 수는 없었다.",
    151: "나",
    152: "(그렇다 해도 빵은 『새가 먹어 버리는』 걸로 되어 있으니,^n　불안하겠지.)",
    153: "나는 그렇게 생각했다.",
    154: "원래 이야기와는 다르지만,^n그레텔을 끌고 가려던 사람이 있었을지도 모르고,^n안전한 방향으로 바꾸는 편이 좋겠지.",
    155: "나",
    156: "정원에 갈까?",
    157: "그레텔",
    158: "……?",
    159: "나",
    160: "돌이라면 정원에도 있어.^n거기서 얼마든지 주워 오면 괜찮아.",
    161: "그레텔",
    162: "………….",
    163: "그레텔이 보인 것은 오직 당혹감이었다.",
    164: "불안이나 슬픔 대신 순수한 당혹감이 드러나,^n눈만 살짝 크게 뜬 무표정이 된다.",
    165: "나",
    166: "그레텔? 안 갈 거야?^n정 그러면 낮에 떨어뜨린 걸 회수하면 돼.",
    167: "내 부름에도 대답하지 않고,^n그레텔은 몇 번이나 눈을 깜박이다가…….",
    168: "그레텔",
    169: "………….",
    170: "이윽고 벽까지 뒷걸음질하더니 털썩 주저앉는다.^n이불이 얼굴과 손끝까지 깊이 덮어,^n그저 천 뭉치가 되었다.",
    171: "나",
    172: "……?",
    173: "나는 누비이불 껍데기에 틀어박힌 그레텔 때문에 당황했지만,^n그 뒤로 아무리 불러도 반응하지 않게 되어 버렸으므로,^n그대로 방을 나올 수밖에 없었다.",
    174: "나",
    175: "(……뭐였을까.^n　역시 이야기에서 벗어난 게 잘못이었나.)",
    176: "등 뒤로 문을 닫고 생각에 잠겨 있자,^n이케노 씨가 지나갔다.",
    177: "이케노",
    178: "무슨 일이니, 나나시 군.^n──아니, 이 방에서 나왔다는 건,^n지금은 헨젤인가?",
    179: "나",
    180: "아까까지는 그렇게 생각됐는데요…….^n──이제 잘린 걸까요.",
    181: "이케노",
    182: "잘려?",
    183: "이케노",
    184: "아, 확실히 그건 잘린 걸지도 모르겠네.",
    185: "이야기를 다 들은 이케노 씨는 깊은 한숨을 내쉬었다.",
    186: "나",
    187: "역시 좋지 않았죠.",
    188: "이케노",
    189: "음, 누가 봐도 정답은 빵이었지…….",
    190: "나는 그레텔이 마지막으로 보인 기묘한 무표정을 떠올린다.",
    191: "　그건 나 때문에 세계가 무너질 위기에 놓인 그레텔이^n　고민하고 혼란스러워하며 자문하던 얼굴이었겠지.^n『이 사람은 누구지?』라고.",
    192: "이케노",
    193: "아깝네. 너라면 좋은 오빠가 될 수 있을 것 같은데.",
    194: "이케노",
    195: "이야기를 충실히 따라가기보다,^n여동생의 안전을 생각해 다른 선택을 하다니,^n제법 오빠다운 판단이라고 생각하는데.",
    196: "나",
    197: "그런가요?^n하지만 그레텔이 싫어한다면 이제…….",
    198: "이케노",
    199: "　뭐, 그레텔에게는 눈치 없는 짓이지.^n『넌 그레텔이 아니야.』라는 말을 들은 것과 마찬가지니까.",
    200: "나",
    201: "그렇, 죠…….",
    202: "이케노 씨는 그 뒤로^n두어 마디 위로의 말을 건네고 떠나갔다.",
    203: "나도 언제까지고 우두커니 서 있을 수는 없다.",
    204: "예상 밖으로 풀이 죽은 자신을 어쩌지 못하면서도,^n다음에 갈 곳을 생각하기로 했다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1124.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1124_slots_00141_00204_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1124_slots_00141_00204_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
