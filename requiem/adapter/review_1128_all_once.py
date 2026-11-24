from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    10: "나는 힐끗 책상을 바라보았다.^n그 위에 그대로 놓인 스케치북의 내용이 머리를 스친다.",
    11: "이 안에 죄인이 한 명 있다──^n언젠가 보았던, 소름 끼칠 만큼 유치한 글씨도 되살아난다.",
    13: "(조금 더 위기의식을 가져야 할까)",
    19: "뭐, 됐어. 나는 그렇게 생각하며 잠자리에 들기로 했다.",
    20: "모든 걸 지금 당장 해결할 필요는 없다.^n그런, 졸음에 맡긴 게으름뱅이 같은 생각으로 모든 일을 잘라 내는 게^n가장 편했다.",
    21: "불을 끄려고 손을 뻗은, 바로 그때.",
    25: "머릿속 대부분을 채우고 있던 기분 좋은 잠의 상상을^n단숨에 날려 버리는 듯한 소리.",
    26: "울림만큼은 경쾌하고 태평한,^n시간을 알리는 뻐꾸기 울음소리──",
    27: "내 시선은 저절로 벽으로 빨려들었다.^n잠자리를 준비하는 동안에도 되도록 눈에 들어오지 않게 조심했던^n그 불길한 모니터로.",
    28: "아무 일도 없기를 그렇게 간절히 빌었건만.^n그런 나를 비웃듯 전원이 들어왔다.",
    36: "하반신에는 속옷조차 걸치지 않았다.^n긴 다리는 부끄러워하는 기색도 없이 대담하게 벌어져,^n이쪽을 향해 사타구니까지 훤히 드러내고 있다.",
    37: "벌어진 골짜기에는 젖은 복숭앗빛 살이 있었다.^n정육점에 진열된 고기와 같은 색으로, 미끈미끈 빛나고 있다.",
    38: "그것은 세로로 쩍 갈라져 부드럽게 벌어져,^n더 칙칙한 색의 단단해 보이는 살덩이를 받아들이고 있다.^n분명 다른 누군가의 신체 일부다.",
    40: "『아, 뜨거……워요.^n하아……, 이렇게, 깊숙한 곳까지 닿아서…….』",
    42: "그 목소리에 희미하게 겹치는 소리가 있다.^n남자의 굵은 숨소리다.",
    43: "남자 쪽도 괴로운 듯 숨이 흐트러져 있지만,^n분명 괴로운 건 아니겠지.",
    46: "아아, 그렇구나. 나는 마음속으로 중얼거렸다.^n놀라움에 달아올랐던 머리가 순식간에 식어 가는 게 느껴졌다.",
    48: "머리카락을 타고 나타난 『왕자님』과 라푼젤이,^n잠깐의 밀회를 나누고 있다──라고 하기에는 너무 곱게 포장한 말이다.",
    49: "몸을 서로 부딪치며,^n라푼젤의 여자로서의 부위에 『왕자님』의 남자로서의 부위를 넣고,^n교미하고 있다.",
    52: "『아…… 사랑하고, 있어요. 사랑해요…… 진심으로.^n아, 아앗아앗아, 하…… 흐아아아아!』",
    57: "모르고 지냈던 것, 언젠가는 더 온화한 방식으로 알게 되었을 것을^n이런 식으로 알게 되다니.^n──너무하다.",
    59: "(넌, 이래도 괜찮아?)",
    63: "그녀의 표정을 보고 있으면,^n야하다거나 음란하다거나, 그런 생각을 뛰어넘어^n밀려오는 감정이 있었다.",
    67: "가슴속에 투명한 감정이 가득 넘쳐,^n딱 한 방울만 밖으로 흘러나온다.^n──내 마음에 일어난 변화는 그런 느낌이었다.",
    71: "나는 스스로 거의 확신하고 있는 『무언가』에 당혹스러워하며,^n살며시 눈을 돌렸다.",
    78: "몇 번이고 형태를 따라 그리듯 사랑을 입에 담고,^n벌린 다리로 휘감아 유혹하고, 아양을 떨며, 매달리는 그 모습이,^n어른들이 꾸며 내는 복잡한 거짓말과 닮았다고 느꼈기 때문이다.",
    79: "더는 보고 있을 수 없어서, 나는 살며시 눈을 돌렸다.",
    83: "끝날 줄 모르는 라푼젤의 비명을 향해,^n나는 마음속으로 말한다.",
    84: "모니터 속 세계를 밀쳐 내고,^n광경도 소리도 닿지 않는 먼 곳으로 떠밀어 버리고,^n혼자 있고 싶다. 편안히 잠들고 싶다.",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_paths = [
        PROJECT / "packets" / "drafts" / "1128_slots_00001_00045_draft.json",
        PROJECT / "packets" / "drafts" / "1128_slots_00046_00085_draft.json",
    ]
    entries: dict[int, dict] = {}
    for path in draft_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("review_passes_completed") != 0:
            raise SystemExit(f"not an unreviewed draft: {path}")
        for entry in data["entries"]:
            index = slot(str(entry["uid"]))
            if index in entries:
                raise SystemExit(f"duplicate draft slot {index}")
            entries[index] = dict(entry)
    expected = set(range(1, 86))
    if set(entries) != expected:
        raise SystemExit("draft coverage mismatch")

    changes = []
    for index, target in CORRECTIONS.items():
        before = str(entries[index]["target_text"])
        entries[index]["target_text"] = target
        if before != target:
            changes.append({"slot": index, "before": before, "after": target})

    catalog: dict[int, dict] = {}
    lookup_slots = set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("file") != "1128.gsc":
                continue
            index = int(row["slot"])
            if index in expected:
                catalog[index] = row
            elif "lookup_keys" in row.get("lanes", []):
                lookup_slots.add(index)
    if set(catalog) != expected:
        raise SystemExit("catalog coverage mismatch")
    if lookup_slots != set(range(86, 144)):
        raise SystemExit("lookup-slot range mismatch")

    final = []
    for index in sorted(expected):
        entry = entries[index]
        source = str(entry["source_text"])
        target = str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift {index}")
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret token mismatch {index}")
        if JAPANESE_RE.search(target):
            raise SystemExit(f"Japanese residue {index}")
        target.encode("cp949", errors="strict")
        entry.update({
            "translator": "Codex internal model",
            "review_status": "reviewed_once",
            "reviewer": "Codex internal model single review pass",
            "notes": "초벌 번역 후 1차 문맥·문체·용어·코드 검수 완료",
        })
        final.append(entry)

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1128_all_translatable_slots_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "every translatable slot received exactly one Codex review pass",
        "newly_reviewed_range": [1, 85],
        "new_review_change_count": len(changes),
        "new_review_changes": changes,
        "file_translation_complete": True,
        "lookup_slots_preserved": [86, 143],
        "release_ready": False,
        "entries": final,
    }
    out = PROJECT / "packets" / "reviewed" / "1128_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "draft_inputs": [str(path) for path in draft_paths],
        "output": str(out),
        "entry_count": len(final),
        "review_passes_per_slot": 1,
        "newly_reviewed_slots": [1, 85],
        "new_review_change_count": len(changes),
        "checks": {
            "source_text_and_hash_match_catalog": True,
            "caret_token_order_preserved": True,
            "all_targets_strict_cp949": True,
            "no_kana_residue": True,
            "exactly_one_review_per_slot": True,
            "all_translatable_slots_covered": True,
            "choice_slots_included": True,
            "lookup_slots_excluded": True,
        },
        "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1128_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
