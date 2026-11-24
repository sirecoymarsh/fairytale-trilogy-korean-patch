from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    141: "그레텔",
    142: "응, 으응…… 네, 네.^n오, 5초…….",
    143: "그레텔은 안도의 숨을 내쉬고 스스로에게 되뇐다.",
    144: "의사",
    145: "자, 다서엇,",
    146: "네에엣,",
    147: "세에에에엣.^n",
    148: "^d2……두우우우우울.^n",
    149: "^d2…………하아아아아아아아나.",
    150: "그레텔",
    151: "응, 으응…….^n──어?",
    152: "의사",
    153: "………….",
    154: "그레텔",
    155: "후아, 아, 시, 싫…….^n……으, 왜요.^n벌써 5초, 지났…… 히야!",
    156: "의사",
    157: "^d3──제에로.",
    158: "마지막으로 유두를 꼬집은 손가락에 꽉 힘을 주고,^n의사 선생님은 두 손을 놓았다.",
    159: "의사",
    160: "음, 그레텔은 심박수가 빠르구나.^n나중에 고혈압이나 심장병을 조심하렴.",
    161: "그레텔은 의사 선생님의 말을 거의 듣지 않는다.^n뒤쪽 바구니에 놓인 옷에 달려들어,^n몸에 걸치느라 필사적이다.",
    162: "앨리스",
    163: "고혈압…… 심장병!^n왠지 위험한 이름의 병이네.^n그레텔, 조심해야 해.",
    164: "그레텔",
    165: "으으…….",
    166: "그레텔은 눈물을 글썽이며 천천히 옷을 입는 앨리스를 본다.^n병이 무서워 떠는 마음은 기껏해야 절반이고,^n나머지 절반은 『정말일까?』라고 호소하는 듯하다.",
    167: "앨리스",
    168: "선생님, 선생님.^n고혈압이나 심장병에는^n어떤 과자가 잘 들어요?",
    169: "의사",
    170: "과자는 별로 좋지 않단다.^n역시 채소를 먹어야지.^n그리고 규칙적인 생활과 적당한 운동.",
    171: "앨리스",
    172: "그레텔, 들었어?^n다음 간식은 당근 케이크로 하자.",
    173: "의사",
    174: "아니, 아니, 그러니까 과자는 좋지 않",
    175: "뚝.",
    176: "갑자기 눈앞에 있던 세계가 모조리 사라졌다.^n모니터의 전원이 꺼진 것이다.",
    177: "나는 몇 번이나 눈을 깜박였다.^n꿈에서 깨어난 듯한 기분이었다.^n미지근한 방 안 공기. 식어 가는 땀.",
    178: "나",
    179: "(방금 건 뭐였을까…….)",
    180: "나",
    181: "(앨리스와 그레텔이 진찰실에서…….^n　──진찰을 받고 있었던 거지.^n　그저 그것뿐이고…….)",
    182: "나는 필사적으로 자신을 타일렀다.",
    183: "그래.^n의사 선생님은 제대로 자기 일을 했을 뿐이고,^n수상쩍은 짓은 하나도 없었다.",
    184: "나",
    185: "(그렇다 해도.^n　왜 진찰실에 카메라가 있는 거지?^n　왜 그 영상이 내 방으로 흘러온 거야?)",
    186: "나",
    187: "(아니야, 뭔가 잘못된…… 거겠지.^n　그래. 분명 기계 고장 같은 거야.)",
    188: "떠오르는 의문에 어떻게든 이유를 붙여^n정리하고 나면 또 다른 불신이 덮쳐 오고.",
    189: "그래도^n내가 눈을 돌리지 않고 그 광경을 계속 보았다는 사실만큼은^n도저히 얼버무릴 수 없다.",
    190: "나",
    191: "(──기분 나빠.)",
    192: "나는 심한 현기증을 느끼며 이마를 짚었다.",
    193: "배달된 아침밥을 다 먹을 무렵에는^n어떻게든 충격에서 벗어나 있었다.",
    194: "티 없이 맑은 햇살과,^n반사광으로 사방이 빛나는 듯한 이 방과,^n김을 피워 올리는 우유죽과.",
    195: "모든 것이 단 하루 만에 『일상』이 되어 있었다.^n그것은 『아무 일도 아니었어』라고 귓가에 속삭이며,^n방금 벌어진 일을 꿈이나 환상처럼 느끼게 했다.",
    196: "──그걸로 괜찮다고 생각한다.",
    197: "이 『낙원』에서 떳떳하지 못한 기척을 느껴도,^n내 자신이 역겹다는 생각이 들어도,^n나는 『낙원』에서도 내 몸에서도 도망칠 수 없다.",
    198: "나는 되도록 모니터를 보지 않으며 일어나,^n오전 산책을 나가기로 했다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1116.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1116_slots_00141_00198_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1116_slots_00141_00198_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
