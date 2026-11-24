from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "문 앞에 서자 희미하게^n흐느끼는 소리가 들려왔다.",
    2: "나",
    3: "(그레텔?　울고 있는 거야?)",
    4: "노크하자 소리가 뚝 그쳤다.^n──기다려 보았지만 아무리 지나도 대답이 없다.",
    5: "실례인 줄 알면서도 문을 열었다.",
    6: "그레텔",
    7: "……읏, ……!",
    8: "휴지를 코에 대고,^n힘을 주던 순간의 그레텔과 눈이 마주쳤다.",
    9: "나",
    10: "미, 미안해. 들어와 버려서.^n우는 소리가 들려서 신경 쓰였어.",
    11: "그레텔은 아무 말 없이 담요를 두른 등을 돌렸다.^n누비천으로 만든 이글루 같은 모습이,^n조심스럽게 코를 푸는 소리가 날 때마다 움찔거렸다.",
    12: "이윽고 눈물을 멈춘 그레텔은 겨우 내 쪽을 돌아보고,^n담요로 몸을 감싼 채 다가왔다.",
    13: "작은 나무 의자를 살며시 이쪽으로 밀었다.",
    14: "나",
    15: "아, 고마워.^n그러니까…… 괜찮아?",
    16: "그레텔",
    17: "응…….",
    18: "작게 고개를 끄덕인 뒤, 기다리게 해서 미안하다는 듯한^n말을 덧붙인 모양이다.",
    19: "나",
    20: "기다린 건 상관없어.^n그보다 울고 있었던 것 같은데.",
    21: "그레텔",
    22: "……으…….",
    23: "막 마른 붉은 눈이 내 말에 금세 다시 젖어 간다.",
    24: "잘못 물었나 싶어 초조해하자,^n그레텔은 작은 입술을 꾹 다물고 마음을 다잡아,^n일그러지려는 뺨을 억지로 굳힌 듯했다.",
    25: "나",
    26: "묻지 않는 편이 좋을까.",
    27: "그레텔은 잠시 망설이다 고개를 저었다.",
    28: "되살아난 슬픔의 파도에 띄엄띄엄 끊기면서도,^n가느다란 목소리가 전한 이야기는 이랬다.",
    29: "　아무래도 그녀는 한밤중에^n『아버지와 어머니가 자신들을 버릴 의논을 하는 것』을^n　들어 버린 적이 있다고 한다.",
    30: "그 일이 문득 떠올라서──^n결국 옛일을 떠올리며 울고 있었던 모양이다.",
    31: "나",
    32: "(그 대화라는 건…… 환청이라는 거겠지.^n　그런 병이니 어쩔 수 없겠지만.)",
    33: "그래도 눈가가 새빨개진 채^n어깨를 들썩이며 울음을 참는 그레텔을 보니,^n환청이라고 치부할 마음은 들지 않는다.",
    34: "나",
    35: "그…… 뭐라고 해야 좋을지는 모르겠지만,^n기, 기운 내.",
    36: "그레텔",
    37: "……읏, 으으…….",
    38: "나",
    39: "어, 그러니까…….",
    40: "나는 새로운 화제를 찾았다.^n그러다 그레텔의 담요 틈에서^n삐져나온 무언가가 눈에 들어왔다.",
    41: "나",
    42: "그건 뭐야?",
    43: "그레텔",
    44: "아…….",
    45: "그레텔은 담요 속에서 끌어안고 있던 그것을^n내게 보이도록 들어 올렸다.",
    46: "빼꼼 고개를 내민 것은^n어리숙한 표정의 테디베어였다.",
    47: "그레텔",
    48: "──주웠어.",
    49: "나",
    50: "주웠다고?　어디서?",
    51: "그레텔",
    52: "쓰레기장…….",
    53: "애착이 깊은 것인지,^n말이 부족한 그녀답지 않게 자세한 설명이 이어졌다.",
    54: "이 병동 뒤편에 있는 쓰레기장.^n잡동사니뿐이지만 재미있는 것도 떨어져 있어서,^n가끔 들여다보러 간다고 한다.",
    55: "오늘도 산책 삼아 지나가다 그와 눈이 마주친 모양이다.",
    56: "　화면이 깨져 그저 상자가 된 브라운관 텔레비전 안에,^n　시든 꽃을 안고 누운 그는,^n『버리지 마』라고 단추 눈으로 호소해 왔다고 한다.",
    57: "그레텔",
    58: "씻겨 줬, 지만 처음부터 별로 더럽지 않았고…….^n어디도 찢어지지 않고 깨끗한 채였는데…….^n그런데도 버려져 있었어.",
    59: "그레텔",
    60: "버, 버, 버려져서…….^n──에으, 윽, 우우으으…….",
    61: "그레텔",
    62: "히윽──!",
    63: "화제를 완전히 바꿨다고 생각했는데,^n그 단어가 그레텔의 슬픔을^n다시 불러내고 만 모양이다.",
    64: "애초에 이 테디베어를 주운 일로^n그레텔 자신의 처지를 겹쳐 보고,^n싫은 일을 떠올렸는지도 모른다.",
    65: "나",
    66: "지, 진정해.^n네가 주웠으니 이제 괜찮아.^n그렇지. 잘됐잖아.",
    67: "그레텔",
    68: "……읏, ……으윽.^n으응. ……응.",
    69: "어떻게든 눈물을 참은 그레텔은,^n인형을 꽉 끌어안고 어깨를 떨고 있다.",
    70: "나",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1111.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1111_slots_00001_00070_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1111_slots_00001_00070_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
