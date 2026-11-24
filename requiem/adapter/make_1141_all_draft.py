from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
TARGETS = {
    1: "내가 방에 들어갔을 때 게르다는 침대에 누워 있었다.",
    2: "나를 보고 몸을 일으키려 했지만 말렸다.^n초췌한 얼굴과 좋지 않은 안색이 마음에 걸렸기 때문이다.",
    3: "나",
    4: "아, 됐어. 그대로 누워 있어.^n……아직 약기운이 남았을지도 몰라.",
    5: "게르다",
    6: "약……?",
    7: "게르다가 힘없이 되묻는다.^n노크에 답하는 목소리에 힘이 없던 터라 예상했지만,^n역시 기진맥진한 듯하다.",
    8: "어젯밤부터 이어진 몸 상태, 오늘 아침의 진찰,^n새까맣게 탄 시체 목격, 수면제──^n그럴 만하다고 생각한다.",
    9: "나",
    10: "수면제 말이야.^n다과회 마지막에 마신 수프에 들어 있었어…….",
    11: "게르다",
    12: "뭐……!",
    13: "게르다",
    14: "──아, 아아, 맞아.^n우리는 정원에서 차를 마시다가 수프를 마시니 졸려졌고……!",
    15: "다시 몸을 눕히려던 게르다는^n갑자기 용수철 장치처럼 벌떡 일어났다.",
    16: "자기 옷 여기저기를 털듯 살피며,^n무언가를 확인하는 눈치다.",
    17: "나",
    18: "왜, 왜 그래?",
    19: "게르다",
    20: "잠든 동안 무슨 짓을 당했나 싶어서.^n의사 선생님들은 왜 우리를 재웠어?^n이유가 있었을 거 아니야?",
    21: "나",
    22: "아마 그 자리를 끝내고 방으로 옮기려고 그랬던 것 같아…….^n나도 정신을 차려 보니 내 방에 있었어.",
    23: "게르다",
    24: "뭐야, 그게. 굳이 재우지 않아도 되잖아!^n역시 이 『낙원』은 이상해.^n뭔가 나쁜 목적이 있다고밖에는 생각할 수 없어.",
    25: "게르다가 드물게 이성을 잃은 채 노골적으로 불신을 입에 담는다.",
    26: "그 모습을 보니^n오늘 아침 보게 된 그녀의 진찰 모습이 떠올랐다.^n게르다가 경계심을 키우는 것도 당연하다.",
    27: "이번 일에 한해서는,^n어쩐지 정말 아무 일도 당하지 않은 것 같지만,^n그렇게 말해도 게르다는 진정하지 않겠지.",
    28: "나는 원래 어른이란^n귀찮은 일을 해결하려고 그런 수단을 고르기 마련이라고^n체념했으니 나름대로 납득했을 뿐이고.",
    29: "게르다에게는 내 짐작 따위 아무 근거도 되지 않고,^n섣불리 달래려다가는,^n이 『낙원』과 함께 나까지 싫어하게 될 뿐이다.",
    30: "나",
    31: "──게르다, 그, 안색이 안 좋아.^n감기, 아직 낫지 않은 거 아니야…….",
    32: "대신 나는 그런 말을 꺼냈다.^n실제로 동요 때문이라고 보기에는 게르다의 안색이 너무 칙칙해서,^n무척 걱정스럽기는 했다.",
    33: "사실은 화덕 안의 새까맣게 탄 시체에 관해 묻고 싶었다.^n하지만 그런 무서운 이야기는,^n게르다를 더욱 불안정하게 만들 뿐이다.",
    34: "나",
    35: "사실은 너와 여러 이야기를 하고 싶었어.^n하지만 그리 기분 좋은 이야기는 아니고…….",
    36: "게르다",
    37: "나는 딱히…… 괜찮아. 그렇게 약하지 않아.",
    38: "나",
    39: "걱정돼서 그래, 게르다.^n다음에 기회를 봐서 이야기하자. 응?",
    40: "나",
    41: "그, 오늘은 여러 일이 있었잖아…….^n따뜻하게 하고 푹 자.",
    42: "게르다",
    43: "………….",
    44: "게르다는 한동안 나를 바라보다가,^n이윽고 온몸의 힘을 풀고 침대에 걸터앉았다.",
    45: "게르다",
    46: "그래. 여러 일이 있었으니까.^n조금 진정해야겠어.",
    47: "나",
    48: "응, 그게 좋겠어.^n그럼 잘 자.",
    49: "게르다",
    50: "그래, 내일 봐.",
    51: "얼음 무늬가 새겨진 문을 보며 나는 잠시 생각에 잠겼다.",
    52: "나",
    53: "(다시 이야기할 기회가 생기면 듣고 싶지만…….^n다시 들추는 것도 좋지 않으려나.)",
    54: "나",
    55: "(우선 게르다의 몸이 나은 뒤에.^n상태를 보면서 이야기하자.)",
}


def main() -> int:
    expected = set(range(1, 56))
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1141.gsc" and int(item.get("slot", -1)) in expected:
                rows[int(item["slot"])] = item
    if set(rows) != expected or set(TARGETS) != expected:
        raise SystemExit("coverage mismatch")
    entries = []
    for slot in sorted(expected):
        row = rows[slot]
        source = str(row["source_text"])
        target = TARGETS[slot]
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {slot}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": row["uid"], "source_text": source, "source_raw_sha256": row["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 전"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1141_slots_00001_00055_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    path = PROJECT / "packets" / "drafts" / "1141_slots_00001_00055_draft.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "entries": len(entries), "output": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
