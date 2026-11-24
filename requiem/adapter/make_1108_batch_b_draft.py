from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    69: "나",
    70: "(뭘까. ──일기 같은 건가?)",
    71: "나",
    72: "──뭐야, 이거.",
    73: "한 차례 훑어보고 나는 그런 목소리를 흘리고 말았다.",
    74: "처음 부분은 아직 이해할 수 있다.^n누군가에게 설명하는 건지 스스로를 위한 메모인지,^n아무튼 이 『낙원』에 관한 기록이다.",
    75: "뒷부분은 히라가나뿐인 이상한 문장이고 글씨도 서툴다.^n천진하게, 순진하게, 아무 생각 없이,^n남이 시키는 대로 적은 듯한 인상이다.",
    76: "그런데도 내용은 왠지 수상쩍고,^n──그 부조화가 무척이나 기분 나쁘다.",
    77: "모두 중에 한 명, 죄지은 사람이──^n사람을 죽인 죄지은 사람이──",
    78: "나",
    79: "(모두라니 누구지?^n　너는 누구에게 이런 걸 쓰라는 말을 들었어?)",
    80: "나",
    81: "(너는──이 뒤에 어떻게 됐어?)",
    82: "분위기가 다른 앞부분과 뒷부분은,^n각각 다른 사람이 쓴 것일까.^n아니면──",
    83: "나",
    84: "………….",
    85: "섬뜩한 기분을 삼키고 나는 페이지를 더 넘겼다.",
    86: "나",
    87: "(이건…… 뭘까?)",
    88: "지금까지 중 가장 의미를 알 수 없는 페이지다.",
    89: "앨리스, 그레텔, 오데트＆오딜,^n라푼젤, 게르다──^n즉 지금 이 『낙원』에 있는 나 이외의 환자 이름이 적혀 있다.",
    90: "무슨 표처럼 선이 그어져 있는데,^n이 빈칸은 무엇을 위한 걸까?",
    91: "나",
    92: "(무언가를 적기 위해서겠지.^n　뭘까. 표?　차트?　답안지?)",
    93: "빈칸을 바라보고 있자니 머릿속 깊은 곳이 욱신거리는 듯──^n소중한 무언가가 빠진 듯 불안한 기분이 든다.",
    94: "무언가를 써넣고 싶다.^n기묘한 충동이지만 지금의 나는 무엇을 써야 할지^n전혀 짐작할 수 없다.",
    95: "나머지 페이지가 백지라는 것을 깨닫고,^n나는 고개를 갸웃하며 스케치북을 덮었다.",
    96: "나",
    97: "(이건…… 뭘까?)",
    98: "지금까지 중 가장 의미를 알 수 없는 페이지다.",
    99: "앨리스, 그레텔, 오데트＆오딜,^n라푼젤, 게르다──^n즉 지금 이 『낙원』에 있는 나 이외의 환자 이름이 적혀 있다.",
    100: "각각의 이름을 선이 둘러싸고 있고,^n그 안에는 기묘한 기호가 적힌 곳도 있다.",
    101: "그것을 바라보고 있자니 머릿속 깊은 곳이 욱신거리는 듯──^n소중한 무언가가 빠진 듯 불안한 기분이 든다.",
    102: "용기를 내어 계속 바라봐야 한다.",
    103: "아니, 한시라도 빨리 눈을 돌리고 달아나야 한다.",
    104: "서로 반대되는 충동이 양쪽에서 나를 몰아붙이는 듯하다.^n어느 쪽이 옳고 어느 쪽이 틀렸는지──^n애초에 정답 같은 것이 있기는 한지──",
    105: "나는 머리를 세차게 흔들어 두 생각을 모두 떨쳐 냈다.",
    106: "나머지 페이지에 적힌 것이 없음을 확인하고,^n스케치북을 덮었다.",
    156: "그저 스케치북을 찾아 들여다보았을 뿐인데,^n마음에 조금 안개가 낀 듯한 기분이었다.",
    157: "특히 『죄지은 사람이 있어』 『도망쳐야 해』라는 글.^n너무나 뜻을 알 수 없지만, 모르기 때문에 오히려^n위험해 보이는 분위기만은 전해져 온다.",
    158: "저 글은 시간을 넘어^n지금 이곳에 있는 나에게 경고하는 게 아닐까──^n그런 생각까지 들고 만다.",
    159: "　이곳에 오기 전 일을 기억했다면,^n『무슨 공포 소설도 아니고』라며 웃고,^n　전에 살던 사람이 두고 간 물건으로 신고했을지도 모른다.",
    160: "하지만 내 머릿속은 새하얀 만큼,^n이것저것 상상으로 채워야 하고, 그러다 보니,^n공포 소설 같은 일마저 눈앞의 현실처럼 느껴져──",
    161: "나",
    162: "(안 되겠다. 기분 전환하자.)",
    163: "나는 스케치북을 책상 위에 놓고,^n다시 밖으로 나가기로 했다.",
    164: "방으로 돌려보낼 때도 나 혼자였고,^n지금도 방문은 잠겨 있지 않으니, 이는^n자유롭게 돌아다녀도 된다는 뜻이겠지.",
    165: "그렇다면 아직 가 보지 않은 곳에 가는 것이^n기분을 바꾸기에 딱 좋을지도 모른다.",
    166: "나",
    167: "(아, 맞다. 도서관.)",
    168: "그 수기(?)에 도서관 이야기가 적혀 있었다.^n모두의 책에 관한 내용이 있어 행동의 이유를 알 수 있다고──",
    169: "나",
    170: "(모두의 『성서』인 그림책이^n　도서관에도 있다는 뜻인가.)",
    171: "지금 있는 환자들의 이야기는 대강 알고 있지만,^n다시 읽어 보는 것도 좋을지 모른다.",
    172: "어쩌면 나 자신을 알 단서가 될지도 모르고.",
    173: "나는 도서관으로 향하려고,^n다시 하얀 문손잡이를 돌렸다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1108.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1108_translatable_batch_b_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1108_translatable_batch_b_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "slots": sorted(TARGETS), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
