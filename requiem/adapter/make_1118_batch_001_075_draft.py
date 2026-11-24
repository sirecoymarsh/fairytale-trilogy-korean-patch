from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "나",
    2: "(……없는 건가.)",
    3: "한동안 기다려도 대답이 없다.",
    4: "다시 한번 문을 두드리고 충분히 기다렸지만,^n내게 답한 것은 정적뿐이었다.",
    5: "나",
    6: "──미안해, 열게.",
    7: "나는 큰맘 먹고 문을 열어 보았다.",
    8: "나",
    9: "아…….",
    10: "──있다.^n그렇게 생각해 부르려던 나는 목소리를 삼켰다.",
    11: "누비이불이 놓여 있는 걸 보고,^n당연히 그 안에도 무언가 있으리라 착각한 것이다.^n찾아올 때마다 그녀가 이불째 부스럭거리며 움직여 나를 맞았으니까.",
    12: "하지만 자세히 보니 안은 비어 있었다.",
    13: "나",
    14: "(그레텔…… 무사하면 좋겠는데.)",
    15: "무심코 떠올린 생각에 흠칫했다.^n왜 그런 생각을 한 걸까.",
    16: "물론 그녀는 무사할 것이다.^n이곳은 『낙원』이고,^n환자를 소중히 여기는 의사 선생님과 간호사들뿐이니까.",
    17: "동시에 그런 생각이 『공허한 말』처럼 느껴지는 나도 있었다.^n모니터 너머로 들은 의사 선생님의 숨소리는^n몇 번을 떠올려도 불쾌했고──",
    18: "　게다가 방금 전까지 사람이 싸여 있었던 듯한 모양으로^n　그 자리에 남겨진 이불은,^n『부재』라는 사실을 호소하는 듯해서 불안해졌다.",
    19: "나",
    20: "(──너무 깊이 생각하는 거겠지, 그런…….)",
    21: "나",
    22: "──어라.",
    23: "방문을 닫았을 때,^n나는 발밑에 떨어진 것을 발견했다.^n문간 앞에 데굴 구른 그것은 낯이 익었다.",
    24: "하얗고 반짝이는 조약돌이다.^n어젯밤 그레텔과 함께 주워 모았다.",
    25: "나",
    26: "(왜 이런 곳에 떨어져 있지?^n　주머니에서 흘러나온 건가.)",
    27: "그렇게 생각하면서도 어떤 예감이 들어 주변을 둘러보니,^n조금 떨어진 곳에 하나가 더 놓여 있었다.",
    28: "나",
    29: "………….",
    30: "다가가자 더 멀리 또 하나.^n열 걸음도 걷기 전에 다시 하나가 더──",
    31: "복도 카펫 위에 제각각 거리를 두고^n아무래도 떨어진 게 아니라 놓여 있는 듯하다.",
    32: "나",
    33: "(──이건.)",
    34: "나는 드문드문 이어지는 그 돌을──",
    35: "따라가기로 했다.",
    36: "따라가지 않기로 했다.",
    37: "생각하기도 전에 내 발은 걷기 시작했다.",
    38: "조약돌이 어떤 상황을 뜻하는지는 모른다.^n그저 그레텔의 역할놀이 때문에 놓인 것일지도 모른다.^n──하지만 견딜 수 없을 만큼 불길한 예감이 들었다.",
    39: "조약돌은 복도 끝에서 계단을 내려가,^n건물 밖으로 이어졌다.",
    40: "정원으로 나오자 추적은 훨씬 어려워졌다.^n하얗고 예쁜 조약돌이라 어떻게든 찾아 따라갈 수 있었지만,^n어디에나 있을 법한 돌이었다면 놓쳤을 것이다.",
    41: "초원을 가로질러 개울을 뛰어넘고,^n관목 사이를 누비며 장미 아치 아래를 지나──",
    42: "돌은 이윽고 좁은 외길을 따라가기 시작했다.^n그리고 그 길은^n어느새 눈앞에 나타난 숲속으로 사라진다.",
    43: "나",
    44: "(그레텔……!^n　이런 숲속에 있는 거야?)",
    45: "높은 나뭇가지들은 앞다투듯 하늘을 가로지르고,^n저마다 무수한 잎이 무성하게 자라 있어,^n거의 지붕이나 다름없다.",
    46: "한낮인데도 빛이 희미하다.^n발을 들이려면 약간의 용기가 필요했다.",
    47: "나",
    48: "(우와, 꽤 깊네…….^n　병원인데 이렇게 큰 숲이 있다니.)",
    49: "길게 느껴졌을 뿐,^n실제로는 그리 많은 시간이 지나지 않았을지도 모른다.",
    50: "하지만 그렇게 생각할 수 있었던 건 안전한 곳으로 돌아온 뒤였고,^n당시의 나는 해가 기울 만큼 오래 걸었다고 느꼈다.",
    51: "돌아갈까 하고 몇 번이나 생각했다.^n하지만 되돌아가는 데도 다른 종류의 용기가 필요해서,^n나는 어떻게든 계속 앞으로 나아갔다.",
    52: "나",
    53: "──아!",
    54: "얼마 남지 않은 기력마저 꺾이려던 그때,^n그레텔의 모습을 발견했다.",
    55: "나",
    56: "그레텔…….",
    57: "어두컴컴한 숲속에서,^n안 그래도 작은 모습은 한층 더 작아 보였다.",
    58: "고개를 숙인 채 힘없이 터벅터벅 걷고 있다.^n지금까지 내가 한 것과 반대로^n조약돌을 따라 이쪽으로 돌아오던 중인 듯했다.",
    59: "나",
    60: "그레텔!",
    61: "내 부름에 튕기듯 얼굴을 든다.^n그 눈동자는 불안감에 젖어 있었다.",
    62: "그레텔",
    63: "오빠…….^n──오빠!!",
    64: "얼굴을 일그러뜨린 그레텔이^n부딪치듯 내 가슴으로 뛰어들었다.",
    65: "그레텔",
    66: "오빠, 오빠아……!^n으, 으에…… 우와아아아앙……!",
    67: "내 가슴팍이 순식간에 뜨거운 눈물로 젖어 간다.^n가느다란 어깨의 떨림과 흐느낌이 멎을 때까지,^n나는 작은 머리를 계속 토닥토닥 쓰다듬었다.",
    68: "역시 어딘가 그리운 감촉이었다.",
    69: "나",
    70: "……대체 무슨 일이 있었어?",
    71: "잠시 뒤 진정한 그레텔과 함께^n왔던 길을 되짚으며 나는 자초지종을 물었다.",
    72: "그레텔은 차가운 손가락으로 내 손을 꼭 잡고 있다.^n무언가의 여파로 손이 빠질 것 같을 때마다,^n아플 만큼 힘을 주어 매달렸다.",
    73: "그레텔",
    74: "데, ……끌려갔어.^n지, 집에 갑자기 누가 와서 팔을 붙잡고…….",
    75: "집이라는 건 그레텔의 병실을 말하는 것이겠지.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1118.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1118_slots_00001_00075_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1118_slots_00001_00075_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
