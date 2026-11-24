from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    121: "앨리스",
    122: "난 알고 있어요. 모르는 곳에는 대입하면,^n깔끔하게 풀린다고요.^n그래서 많이 대입해 봤어요.",
    123: "앨리스",
    124: "하지만 난 아직 수학의 모든 것을 모르니까,^n잘 알 수 없는 식이 되어 버렸어요.^n그래서 먼저 모자 장수의 연습 문제를 풀어 본 거예요.",
    125: "나",
    126: "그렇구나…….",
    127: "　낮에 이케노 씨와 나눈 대화가 떠올랐다.^n『앨리스는 나를 걱정한다』고.",
    128: "『성서』에 있던 애벌레와의 대화를 무시하고,^n　이번에도 풀지 못한 채 내버려 둔 엉터리 수수께끼에 도전했다.^n　──그건 역시 나를 걱정해 줬기 때문이겠지.",
    129: "나",
    130: "고마워, 앨리스.",
    131: "감사는 자연스럽게 흘러나왔다.^n앨리스의 마음은 무척 알아보기 어렵지만,^n그만큼 전해졌을 때 순수하게 가슴에 스며든다.",
    132: "하지만 그런 내 마음도 모른 채.",
    133: "앨리스",
    134: "후아아…… 아.^n아아, 머릿속이 누가처럼…….",
    135: "앨리스는 하품으로 답했다.^n손끝까지 곧게 젖힌 손을 우아하게 갖다 대도,^n여유롭게 삐져나올 만큼 커다란 하품이다.",
    136: "앨리스",
    137: "머리란…… 너무 많이 쓰면…… 녹는군요…….^n문제를 풀어서…… 녹은 걸까요…….",
    138: "이미 절반 이상은 잠꼬대 같은 발음이다.^n책상에 엎어지려는 것을 내가 황급히 막았다.",
    139: "나",
    140: "아, 안 돼.^n자려면 침대에서. 알겠지?",
    141: "앨리스",
    142: "안 돼…… 침대…… 크기가 안 맞아……요.",
    143: "나",
    144: "(그랬지.)",
    145: "나는 그녀의 잠자리인 요람으로 가도록 재촉하며,^n일어서는 앨리스에게 손을 빌려준다.",
    146: "앨리스",
    147: "으…… 뉴웅…….",
    148: "비틀비틀 일어서는 앨리스.^n그때 무거워 보이는 눈꺼풀이 나를 보고 크게 뜨였다.",
    149: "졸린 듯 몇 번이나 눈을 깜박이며,^n내 차림을 위아래로 살펴본다.^n그러고 보니 이 옷을 입고 만나는 것은 처음이었다.",
    150: "앨리스",
    151: "……어머. 털이 달라졌네요.",
    152: "나",
    153: "털이 아니라 옷이야.",
    154: "앨리스",
    155: "그래요…… 후아아.",
    156: "앨리스는 어느 쪽이든 상관없다는 듯 하품한다.^n아직도 내가 사람으로 보이지 않는 걸까.",
    157: "앨리스",
    158: "──아아, 그래도 아주 잘 어울려요.^n다행이다…….",
    159: "앨리스",
    160: "난 말이에요. 당신을 만났을 때부터,^n당신에게는 분명 무언가 부족하다고 생각했어요.^n물론 기억과 이름이 부족하지만 그것만이 아니라…….",
    161: "나",
    162: "(기억과 이름 말고도 내게 부족한 것?)",
    163: "앨리스가 하는 실없는 말 중 하나겠지.^n그렇게 생각하면서도 나는 왠지 마음에 걸렸다.",
    164: "요람에 도착하자^n당장이라도 쓰러지고 싶다는 기색을 보이면서도,^n앨리스는 마지막 힘으로 말을 남겼다.",
    165: "앨리스",
    166: "하지만 그 옷으로 아주 조금 채워진 것 같아요.^n……괜찮아요, 수식만 있으면 분명…… 다른 무언가도…….",
    167: "앨리스",
    168: "후, 냐, 아.",
    169: "갑자기 힘이 풀려 등을 대고 시트에 쓰러진다.^n그 반동으로 튀어 오른 다리도 마침 요람 안에 들어가,^n제법 그럴듯한 잠자는 모습이 되었다.",
    170: "나는 잠자리 구석에 흐트러진 채 뭉쳐 있는 이불을 집어,^n앨리스를 덮어 준 뒤 방을 나왔다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1123.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1123_slots_00121_00170_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1123_slots_00121_00170_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
