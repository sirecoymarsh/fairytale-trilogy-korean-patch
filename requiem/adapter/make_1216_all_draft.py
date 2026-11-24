from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
TARGETS = [
    None,
    "그 뒤 한동안 나는 앨리스를 보지 못했다.",
    "방으로 찾아가도 문이 활짝 열려 있을 때는^n언제나 자리를 비웠고, 닫혀 있을 때는 노크 소리에^n졸린 목소리가 대답해서 방해하지 않을 수 없었다.",
    "목격담을 들어 보면 정원과 오락실,^n내가 모르는 여러 장소를 뛰어다니고 있다는 사실은^n짐작할 수 있었지만, 무엇 때문인지는 아무도 몰랐다.",
    "그렇다고 나도^n그리 적극적으로 찾아다닌 것은 아니다.",
    "그 일 이후 앨리스와 얼굴을 마주하기가^n어색하게 느껴졌기에, 이렇게 자연스럽게 만나지 않아도 되는 건^n쓸쓸한 한편 마음이 편하기도 했다.",
    "그 이유는 아주 단순하다.",
    "앨리스",
    "아, 그리고 이게 가장 중요하네요.^n──당신에게 제 마음을 전할 준비를 해야 해요!",
    "나",
    "(그 말은…….^n 역시 그 말은)",
    "그때는 앨리스가 회복한 것이 그저 기뻐서,^n말실수를 해 버린 경솔함과 둘러대는 모습에^n훈훈하게 쓴웃음을 짓는 것으로 끝났지만.",
    "시간이 지나면서 그녀가 입에 담은 말이^n서서히 머릿속으로 스며들어 왔다.",
    "『이렇게 빨리! 나는 사랑을 알게 되었을지도 모른다.^n 어제까지만 해도 내 심장은 도감에 실릴 법한^n 징그러운 고깃덩어리였다』",
    "『하지만 지금은 분명 예쁜 하트 모양!』",
    "『아니, 분명 이건 『연정』 쪽이겠지.^n 왜냐하면 나는 툭, 하고 연정에 빠졌으니까』",
    "내 머릿속에서^n앨리스의 일기에 적힌 내용과 이어지고 말았을 때는^n부끄러워서 몸부림치고 싶어졌다.",
    "나",
    "(으으…….^n 왜 내가 이런 기분을 느껴야 하는 거야)",
    "솔직히 기분 나쁘지는 않다.^n앨리스는 귀여운 여자아이이고,^n상당히 별나기는 해도 익숙해지면 매력적이다.",
    "하지만 뭐랄까, 어떻게 말해야 할까.^n기쁨보다 당혹감이 강하다.^n그리고 당혹감보다 압도적으로 낯부끄러움이 앞선다.",
    "이렇게 간지럽고 낯간지러운 기분이 드는 건^n본래 앨리스 쪽이어야 하지 않을까.",
    "호감을 털어놓기도 전에 바보같이 들켜 버리고,^n모르는 척하는 상대에게 새삼 고백하다니,^n나라면 견딜 수 없다. 너무 꼴사나워서.",
    "나 자신도 뭐랄까,^n달콤한 고문을 받는 기분이다.",
    "나",
    "(그나저나 앨리스는^n 왜 그렇게 바쁘게 다니는 걸까?)",
    "주의를 돌리려고 그런 생각을 해 보지만,^n물론 답을 알 리가 없다.",
]


def main() -> int:
    expected = set(range(1, 27))
    if len(TARGETS) != 27:
        raise SystemExit(f"target count mismatch: {len(TARGETS)-1}")
    rows, lookup = {}, set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1216.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                rows[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(rows) != expected or lookup != set(range(27, 85)):
        raise SystemExit("visible or lookup coverage mismatch")
    entries = []
    for index in sorted(expected):
        row, target = rows[index], str(TARGETS[index])
        source = str(row["source_text"])
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {index}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": row["uid"], "source_text": source, "source_raw_sha256": row["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 대기"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1216_slots_00001_00026_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1216_slots_00001_00026_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "entries": len(entries), "lookup_slots_preserved": [27, 84], "output": str(out), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
