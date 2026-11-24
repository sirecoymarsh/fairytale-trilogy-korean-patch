from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
TARGETS = [
    None,
    "나",
    "(아아, 피곤하다)",
    "등 뒤로 문을 닫고 나는 깊이 숨을 내쉬었다.",
    "그 뒤 앨리스와 함께 밤의 정원을 산책했다.^n물론 모니터에 비친 것에 대한 기억을^n희미하게 만들기 위해서였다.",
    "도중에 오데트를 만나 서서 이야기를 나누기도 하고,^n장미 생울타리가 미로처럼 얽힌 곳에서^n술래잡기 흉내를 내기도 했다──",
    "완전히 지워 낼 수는 없었지만,^n나름대로 기분을 전환할 수 있었다고 생각한다.^n적어도 나는.",
    "앨리스는 아무 일도 없었던 듯 행동하면서도,^n때때로 안절부절못하는 모습을 보였다.",
    "무언가에 정신이 팔려 있을 때는 순순히 잊고 있지만,^n머릿속에 여유가 생기면 되살아나는 거품 같은 명멸을^n반복했던 것 같다.",
    "혐오감보다는 호기심이 자극된 듯했다.^n뭐, 그것이 나를 경멸하는 형태로 나타나지 않았다는 건^n내게는 다행이었겠지.",
    "나",
    "(………………자자)",
    "나는 재빨리 잠자리에 들 준비를 마쳤다.",
    "침대에 들어가려던 참에,^n그 옆에 그대로 놓여 있던^n바구니를 어떻게 처리할지 난감해졌다.",
    "나",
    "………….",
    "고민 끝에 옷장에 밀어 넣기로 했다.^n침대 밑에 두었다가 청소하는 아주머니에게 보이면^n분명 부끄러워질 것 같다.",
    "나",
    "(역시 이건 이대로 앨리스에게 돌려주자)",
    "질감도 색도 인상도 제각각인 잡동사니가^n하얀 옷장 문 안에 갇혀 가는 모습을 보며,^n나는 그렇게 결심했다.",
    "혼자 있으면 잡동사니에 설레던 기분보다,^n마음 깊은 곳의 무기질적인 『경고』가 훨씬 강하게 느껴진다.",
    "──너에게는 필요 없어──",
    "──너와는 인연이 없어──",
    "나",
    "………….",
    "아무것도 장식하고 싶지 않은 것은 내 자유고,^n딱히 죄책감을 느낄 필요도 없다.",
    "앨리스도 분명 자기가 좋아하는 인형의 집 한 방에^n취향에 맞지 않는 가구를 멋대로 들여놓으면,^n불쾌하지 않을까.",
    "나는 침대에 눕기 전에,^n방 안 풍경을 한 바퀴 둘러보았다.",
    "깨끗하고 쓸데없는 물건이 없으며 말끔하고,^n이곳에 사는 나 자신의 냄새조차 느껴지지 않는,^n허전하지만 마음이 편해지는 방.",
    "처음에는 마음이 놓이지 않았지만,^n이건 이것대로 괜찮고 이 방은 이 모습으로 완성된 거라며^n──그런 자랑스러움마저 느낀다.",
    "나는 살짝 미소 짓고 불을 껐다.",
]


def main() -> int:
    expected = set(range(1, 31))
    if len(TARGETS) != 31:
        raise SystemExit("target count mismatch")
    rows, lookup = {}, set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1205.gsc":
                continue
            slot = int(item["slot"])
            if slot in expected:
                rows[slot] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(slot)
    if set(rows) != expected or lookup != set(range(31, 89)):
        raise SystemExit("visible or lookup coverage mismatch")
    entries = []
    for slot in sorted(expected):
        row, target = rows[slot], str(TARGETS[slot])
        source = str(row["source_text"])
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {slot}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": row["uid"], "source_text": source, "source_raw_sha256": row["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 대기"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1205_slots_00001_00030_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1205_slots_00001_00030_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "entries": len(entries), "lookup_slots_preserved": [31, 88], "output": str(out), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
