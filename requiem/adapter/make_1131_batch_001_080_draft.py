from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "지금 라푼젤과 얼굴을 마주하기는 껄끄럽다고 생각하면서도,^n왜 나는 찾아갈 마음이 들었을까.",
    2: "그녀의 방 문을 두드리기 직전이 되어서야,^n갑자기 제정신이 든 듯 그런 의문이 떠올랐다.",
    3: "하지만 이미 늦었다.^n뭔가를 생각하기도 전에 주먹이 문을 두드려 버렸으니까.",
    4: "라푼젤",
    5: "어서 들어오세요.",
    6: "라푼젤 역시,^n『할머니』를 맞이할 생각으로 나를 부르고 있었다.",
    7: "라푼젤",
    8: "할머니. 안녕하세요.",
    9: "라푼젤의 방은 지난번과 다른 냄새로 가득했다.",
    10: "코를 확 찌르는 기름진 냄새.^n그 냄새는 라푼젤 손에 들린 팔레트 위에서^n붓으로 이리저리 개어지는 물감에서 풍겨 왔다.",
    11: "전의 달콤한 꽃향기는 완전히 묻혀 버렸지만,^n나는 이쪽이 더 좋은지도 모른다.^n알록달록하고 즐거운 시간의 냄새다.",
    12: "나",
    13: "왔구나, 그림 도구.",
    14: "라푼젤",
    15: "네, 오늘 아침에 받았답니다.^n설마 이런 어리광을 들어주실 줄은^n꿈에도 몰랐어요, 할머니.",
    16: "살짝 자리를 옮겨,^n라푼젤이 마주한 캔버스를 들여다본다.",
    17: "하얀 캔버스 가장자리에 콕콕^n시험 삼아 칠한 물감만 묻었을 뿐, 아직 아무것도 그려지지 않았다.^n밑그림 같은 것도 보이지 않는다.",
    18: "나",
    19: "뭘 그릴 거야?",
    20: "라푼젤",
    21: "글쎄요, 무엇이 될는지…….^n저도 모르겠어요.^n그림을 그리고 싶어진 것부터 그저 순간의 생각이었으니까요.",
    22: "모호한 말을 하면서도 라푼젤은 즐거워 보인다.",
    23: "지금은 내가 『할머니』이기 때문에 얼버무린 걸까.^n아니면 정말 라푼젤 자신도 모르는 걸까.",
    24: "나",
    25: "………….",
    26: "조심스레 살피니,^n라푼젤의 시선은 캔버스에 꽂혀 있었다.",
    27: "기품 있고 나른하며 어딘가 우수에 잠긴,^n정처 없이 먼 곳을 헤매는 듯 투명한 눈빛이,^n평소와 달리 열기를 띤 듯하다.",
    28: "아무것도 없는 흰 바탕에서 무언가를 찾듯 응시한다.^n그려야 할 형태를 찾는 순간, 깊은 호수 표면 같은 눈동자 밑바닥에도^n정열적으로 흔들리지 않는 초점이 생길까.",
    29: "나",
    30: "(…………)",
    31: "머릿속에 어젯밤 보았던 그녀의 모습이 떠올랐다.",
    32: "몸의 열기와 마음의 열기에 취해 있었다.^n몇 번이고 사랑을 고백했다.^n그런데도 그 눈동자는 어딘가 공허하고 먼 곳을 헤매는 듯한──",
    33: "나",
    34: "……!",
    35: "나는 고개를 저어 그 영상을 쫓아내려 했다.^n하지만 늦었다.",
    36: "질끈 감은 눈꺼풀 안에서 영상은 더욱 선명해지고,^n귓속에서 들리는 빠른 심장 박동도 점점 슬픈 울림으로 변해──",
    37: "──정신을 차렸을 때.^n나는 말할 생각이 없던 것을 입에 담고 있었다.",
    38: "나",
    39: "라푼젤.^n어젯밤 네가 하던 일을 보고 말았어.",
    40: "나 자신도 놀랄 만큼 아무렇지 않고 대수롭지 않은,^n혼잣말 같은 울림.",
    41: "하지만 라푼젤에게는 단죄였을 것이다.",
    42: "라푼젤",
    43: "──읏.",
    44: "휙 숨을 들이마시는 소리가 났다.^n그대로 내쉬는 것조차 두렵다는 듯 삼킨 채,^n천천히 고개만 돌려 나를 바라보았다.",
    45: "라푼젤",
    46: "──무엇을.^n무엇을 보셨다고, 말씀하시는 건가요.^n할머니…….",
    47: "나",
    48: "그게, 그러니까.^n『왕자님』과 네가, 저 침대에서, 그…….",
    49: "도저히 끝까지 말할 수 없어 말을 더듬는다.",
    50: "터무니없는 말을 내뱉고 말았다.^n이제야 그런 생각이 부풀어 오른다.",
    51: "라푼젤",
    52: "그, 그런 분은 모릅니다.^n무언가 잘못 보신 게 아닌지요……?",
    53: "라푼젤",
    54: "피곤하신 게 아닐까요, 할머니.^n제가 누구와도 만날 수 없다는 사실은,^n할머니께서 누구보다 잘 아시잖아요?",
    55: "나",
    56: "………….",
    57: "하지만 라푼젤의 노골적인 발뺌이^n내 죄책감을 지워 간다.",
    58: "쉰 목소리, 감추지 못한 동요.^n연기가 서툰 것에 짜증마저 났다.",
    59: "──왜.^n마음속으로 라푼젤에게 물으며, 손은 저절로 주먹을 쥐었다.",
    60: "──왜.^n──왜 『어젯밤 일은 꿈이었나』라고^n생각하게 해 주지 않는 거야……!",
    61: "나",
    62: "아니, 보고 말았어, 나는.^n분명히 너였어. 이 두 눈으로 봤어.",
    63: "뱃속에 서서히 스며드는 감정을,^n나는 그대로 그녀에게 내던진다.",
    64: "나 자신도 가슴이 아플 만큼 차가운 목소리였다.",
    65: "나",
    66: "무언가 잘못 본 거였으면 좋았겠지.^n나도 보고 싶지 않았어. 볼 생각도 없었고.",
    67: "나",
    68: "──왜 그런 걸 봐야 했던 거야.^n그런 일은 알고 싶지 않았어……!",
    69: "라푼젤",
    70: "……읏……!",
    71: "내 말의 가시에 상처 입은 라푼젤은 붓을 떨어뜨린다.^n빈 손가락은 새하얗게 굳어 떨리고 있다.",
    72: "라푼젤",
    73: "………….^n죄송해요. 죄송해요, 할머니.",
    74: "잠시 후 라푼젤의 떨리는 목소리가 울렸다.",
    75: "라푼젤",
    76: "말씀을 어겨서 죄송해요.^n비밀을 숨기고, 모든 걸 들킨 뒤에도 얼버무리려 해서──",
    77: "라푼젤",
    78: "저를 키워 주신 할머니를 이렇게까지 배신하다니.^n저는 정말, 정말 죄 많은 사람이에요…….",
    79: "라푼젤은 참회하듯 고개를 숙이지만,^n내 마음에 닿을 리 없다.^n나는 『할머니』가 아니니까.",
    80: "라푼젤",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1131.gsc" and item.get("slot") in TARGETS:
                rows[int(item["slot"])] = item
    if set(rows) != set(TARGETS): raise SystemExit("catalog mismatch")
    entries = []
    for index in sorted(TARGETS):
        source, target = str(rows[index]["source_text"]), TARGETS[index]
        if CARET_RE.findall(source) != CARET_RE.findall(target): raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": rows[index]["uid"], "source_text": source, "source_raw_sha256": rows[index]["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 전"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1131_slots_00001_00080_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1131_slots_00001_00080_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())
