from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
TARGETS = [
    None,
    "진찰이라고 해도 별다른 일을 하는 것은 아니다.^n체온과 맥박과 혈압을 재고 몇 가지 문진을 받을 뿐이다.",
    "──뭔가 기억난 것은 있니?^n──곤란하거나 불편한 일, 해 보고 싶은 일은 있니?",
    "그런 질문에 계속 『아니요』라고 대답하다 보면 금세 끝난다.",
    "의사",
    "아, 그렇지.^n어제 일 말인데.",
    "나",
    "……네?",
    "하지만 오늘은^n평소처럼 의자에서 일어나려던 순간^n익숙한 흐름이 깨졌다.",
    "나는 삐걱 소리를 내며 다시 앉아 고개를 갸웃한다.^n의사 선생님은 그런 나를 보고 조금 놀란 듯했다.",
    "의사",
    "어제 일 말이야, 그, 있잖아…….^n화덕에서 새까맣게 탄 시체가 나왔다느니 아니었다느니, 그런 일 있었지.",
    "나",
    "아아…… 네.",
    "의사 선생님은 말을 잇기 전에 나를 유심히 바라보았다.^n『대사건』에 대한 내 반응이 미적지근한 것을 의아해하는 듯하다.",
    "나 자신도 어딘가 남의 일처럼 여기는 자신에게 놀랐다.^n적어도 어젯밤 잠들 때는 끔찍한 광경을 상상하고^n벌벌 떨었는데.",
    "친해진 여자아이들 중에 『범인』이 있지 않을까 하는^n상상까지 하며 제멋대로 낙담했는데.",
    "의사",
    "조사해 봤는데, 그, 문제는 없었어.^n사람 시체 같은 건 어디에도 없었고, 뭐랄까,^n외부 기관에 연락할 만큼 큰 사건도 아니었지.",
    "나",
    "──그렇군요.^n자세한 내용을 물어봐도 될까요?",
    "의사",
    "아니, 묻지 않는 게 좋겠지.",
    "나",
    "알겠습니다.",
    "선뜻 고개를 끄덕이며 일어서는 나를,^n의사 선생님은 다시 한번 놀란 눈으로 바라보았다.",
    "묻지 않은 것은 관심이 없어서라기보다,^n물어도 소용없다고 생각했기 때문이다.",
    "하지만 내 그런 반응이^n의사 선생님에게는 뜻밖──이라기보다 성에 차지 않는 듯하다.",
    "──어차피 알려 줄 생각도 없으면서,^n왜 물어봐 주기를 바라는 듯한 표정을 짓는 걸까?^n나는 속으로 조금 웃었다.",
    "솔직히 말하면 어제 사건이 무엇이었는지,^n어른들의 세계에서 어떻게 마무리되었는지^n관심이 없는 것은 아니다.",
    "하지만 그것을 위해 헛되이 들이받고,^n『너희는 모르는 편이 좋은 일이야』 같은^n어른들의 상투적인 말에 어울려 줄 생각은 없다.",
    "나",
    "(좀 더 다른 일을 생각하자.^n 그래, 좀 더 다른 일을)",
    "앨리스",
    "저는 그래도 괜찮다고 생각해요.^n싫은 일은 전부 버리고,^n대신 멋진 것만 모으면 되는 거예요.",
    "오늘 아침 앨리스의 목소리가 문득 머릿속 한구석을 스쳤다.",
]


def main() -> int:
    expected = set(range(1, 36))
    if len(TARGETS) != 36:
        raise SystemExit("target count mismatch")
    rows, lookup = {}, set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1202.gsc":
                continue
            slot = int(item["slot"])
            if slot in expected:
                rows[slot] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(slot)
    if set(rows) != expected or lookup != set(range(36, 94)):
        raise SystemExit("visible or lookup coverage mismatch")
    entries = []
    for slot in sorted(expected):
        row, target = rows[slot], str(TARGETS[slot])
        source = str(row["source_text"])
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {slot}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": row["uid"], "source_text": source, "source_raw_sha256": row["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 대기"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1202_slots_00001_00035_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1202_slots_00001_00035_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "entries": len(entries), "lookup_slots_preserved": [36, 93], "output": str(out), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
