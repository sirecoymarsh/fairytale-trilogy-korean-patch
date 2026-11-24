from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "나는 산장에서 떼어 온 듯한 소박한 나무문과 마주쳤다.^n다른 문보다 작아서, 내가 간신히 허리를 굽히지 않고 지나갈 정도였다.",
    2: "가까이 다가가 보니,^n그레텔^n이라고 적힌 나무 팻말이 걸려 있었다.",
    3: "???",
    4: "………….",
    5: "안에서 대답하는 목소리가 들린 것도 같고, 아닌 것도 같았다.^n하지만 바스락거리며 무언가 움직이는 소리는 들렸다.^n누군가 있는 모양이다.",
    6: "나",
    7: "저, 저기…….^n갑자기 미안한데요. 들어가도 될까요?",
    8: "???",
    9: "엇!?　아, 아, 아우…….^n",
    10: "──네, 들어오세요…….",
    11: "겁먹은 듯한 작은 목소리로 대답이 돌아왔다.^n그다지 반갑진 않지만 어쩔 수 없다는 느낌일까.",
    12: "마음에 걸렸지만,^n허락까지 받고 그냥 가는 것도 실례다.^n나는 마음을 다잡고 문손잡이를 돌렸다.",
    13: "나",
    14: "(──어?)",
    15: "안은 무척 좁았다.^n문에 어울리게 어디를 보아도 나무로 된 방──^n아니, 방보다는 오두막이라는 느낌이다.",
    16: "이층 침대에 장롱과 선반. 가구는 이것뿐이다.^n어느 것이나 벽과 천장, 바닥처럼^n닳고 빛바랜 목재로 만들어져 있다.",
    17: "방을 가로질러 호를 그린 밧줄에 널린 빨래도,^n벽의 조각보 같은 태피스트리도, 침대 위 침구도,^n모두 맥락 없이 덧댄 천 조각투성이였다.",
    18: "　정말, 정말 실례라고 생각하지만,^n『초라하다』거나 『허름하다』거나^n　그런 생각이 들고 말았다.",
    19: "나",
    20: "(──그런데 아무도 없나?)",
    21: "먼저 인사를 하려고 둘러보았지만,^n좁은 오두막 어디에도 사람 모습은 없었다.",
    22: "자세히 보니 오두막 안쪽,^n내가 들어온 문 정면에 문이 하나 더 있다.^n혹시 저쪽으로 가 버린 걸까.",
    23: "???",
    24: "………….",
    25: "나",
    26: "으악.",
    27: "시야 끝에서 갑자기 천 뭉치가 움직여 나도 모르게 소리쳤다.^n쥐라도 나올 것 같다고 생각하던 참이라,^n더욱 깜짝 놀랐다.",
    28: "???",
    29: "………….",
    30: "나",
    31: "아…… 저기…….",
    32: "자세히 보니 그 천은 아무래도 담요인 듯하다.^n빙 둘러 감긴 부분에 틈이 나 있고,^n그 사이로 한 쌍의 눈이 이쪽을 가만히 살피고 있었다.",
    33: "──다행이다. 아무래도 인간인 모양이다.",
    34: "나",
    35: "저, 저기…… 미안해.^n갑자기 들어와 버려서…….",
    36: "???",
    37: "………….",
    38: "나",
    39: "(뭐지. 경계하는 건가?^n　갑자기 들어왔으니 당연하려나.)",
    40: "???",
    41: "………….^n",
    42: "──꺅.",
    43: "아마 다른 문으로 달아날지, 이쪽으로 다가올지,^n망설이고 있었겠지.^n조금씩 움직이던 천 뭉치가 자락을 밟고 앞으로 고꾸라졌다.",
    44: "나",
    45: "와, 괘, 괜찮아?",
    46: "펼쳐진 천 표면에서 안의 사람이 밀어 올린 혹이^n출구를 찾아 좌우로 헤맨다.^n이윽고 이쪽 천을 홱 들어 올리며 기어 나왔다.",
    47: "???",
    48: "──아.",
    49: "나",
    50: "저기…….^n처, 처음 뵙겠습니다.",
    51: "목소리와 행동을 보고 예상은 했지만,^n그 정체는 자그마한 여자아이였다.",
    52: "물기 어린 커다란 눈동자와 팔자눈썹, 금세라도 울 듯한 뺨.^n내 시선을 피하듯 가느다란 어깨를 더욱 움츠리고^n부러질 듯한 팔로 자기 몸을 끌어안는다.",
    53: "그저 바라볼 뿐인데도 괴롭히는 것 같아 주저하게 되었다.^n하지만 내가 시선을 돌리기 전에 그녀가 떨리는 입술을 열었다.",
    54: "???",
    55: "처, 처음 뵙…….",
    56: "작은 몸의 작은 성대에서 태어난 목소리는,^n역시 금방이라도 사라질 듯 작았다.^n아니, 실제로 끝이 흐려지며 사라지고 말았다.",
    57: "???",
    58: "………….",
    59: "나",
    60: "………….",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1103.gsc" and item.get("slot") in TARGETS:
                rows[int(item["slot"])] = item
    if set(rows) != set(TARGETS):
        raise SystemExit("catalog mismatch")
    entries = []
    for index in sorted(TARGETS):
        source, target = str(rows[index]["source_text"]), TARGETS[index]
        if source.count("^n") != target.count("^n"):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entries.append(
            {
                "uid": rows[index]["uid"],
                "source_text": source,
                "source_raw_sha256": rows[index]["source_raw_sha256"],
                "target_text": target,
                "translator": "Codex internal model draft",
                "review_status": "draft_pending_single_review",
                "notes": "초벌 번역; 1차 검수 전",
            }
        )
    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1103_slots_00001_00060_draft",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 0,
        "release_ready": False,
        "entries": entries,
    }
    out = PROJECT / "packets" / "drafts" / "1103_slots_00001_00060_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
