from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    1: "실제로 나는 마음속으로^n온갖 것들을 밀쳐 내고 있었던 것 같다.",
    8: "막 잠에서 깬 멍하고 모든 게 멀게만 느껴지는 기분을 이용해서,^n잊지도 외면하지도 않고,^n그저 무난하게 애매한 채로 넘기면 된다.",
    13: "아무것도 하지 않아도,^n누군가 기름 묻은 손을 뻗어 옷에 문질러 묻히고 간다.",
    21: "등을 향해 나를 불러 세우듯 그 소리가 울렸다.",
    29: "누가 무슨 목적으로 이러는지, 거기에 악의가 있는지 없는지,^n사실은 아무것도 모르지만,^n나는 약이 오를 누군가를 떠올리며 유쾌해졌다.",
    30: "그래서 계속 등을 돌린 채 문 쪽으로 걸어가,^n순조롭게 문손잡이를 잡았──는데.",
    46: "영리한 그녀답게 말투도 표정도 아슬아슬하게 예의의 선을 지키고 있다.^n다만 곳곳에서 폭발 직전의 불신이,^n냄비 뚜껑 사이로 새는 김처럼 언뜻언뜻 드러난다.",
    50: "이렇게 골치 아픈 병은 없으면 좋겠다고,^n우리 아저씨들도 늘 생각한단다.",
    65: "하지만 아직 거짓된 가면이 벗겨지기 시작했을 뿐이지.^n본래의 자신을 온전히 기억해 내지 못하면^n나았다고 할 수는 없어.",
    81: "이것도 자네 눈에는 무엇으로 보이지?^n곰 봉제인형?^n──아니야. 포르말린에 담근 개구리야.",
    87: "내 말을 듣게.^n잘 생각해 봐. 치료하지 않고 돌려보내면,^n망상이 점점 부풀어 큰일이 날 수 있어.",
    96: "이따금 몸을 내밀어 끼어들려는 게르다의 말을 가로막고,^n폭포처럼 쏟아 내는 일방적인 의사 선생님의 연설이었다.",
    105: "이마를 짚은 채 게르다는 담담히 중얼거린다.^n완전히 꺾여 대꾸할 말도 찾지 못해 사과할 수밖에 없지만,^n그래도 반발심은 뿌리 깊게 남은 듯했다.",
    123: "……그런가요? 저는 아무렇지도 않은데요.^n잠이 부족해서일지도 몰라요.^n제 경험상 잠을 자면 낫습니다.",
    125: "음, 그렇게 가볍게 볼 만한 열의 오름세가 아닌데.^n뭐, 괜찮아. 약을 놓아 줄 테니까.",
    148: "갓 껍질을 벗긴 삶은 달걀처럼 매끈하고 둥근 엉덩이가^n옅게 붉어져, 부끄러운 듯 움찔거리고 있다.",
    160: "미안해요. 이런 자세는 부끄럽죠.^n개처럼 네발로 엎드려 엉덩이를 다 드러내고.^n아침부터 여자애가 취할 자세는 아니죠.",
    164: "자, 오래 기다리셨죠.",
    175: "게르다의 손끝이 가늘게 떨리며 진찰대를 파고든다.",
    204: "자, 약이 듬뿍 들어 있어요.^n시간이 조금 걸리지만 참아 주세요.^n약효가 아주 좋은 약이니까요.",
    218: "게르다는 한마디도 하지 않고,^n도와주려는 손을 뿌리치듯 진찰대에서 내려와,^n날카로운 발소리를 울리며 모니터 밖으로 사라졌다.",
    232: "그걸 보고 만 나보다,^n그런 식으로 스스로를 변호하려는 내가 더 추하다고 생각한다.",
    236: "──나는 이렇게 이 느낌에 익숙해지는 걸까.",
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
        PROJECT / "packets" / "drafts" / "1129_slots_00001_00080_draft.json",
        PROJECT / "packets" / "drafts" / "1129_slots_00081_00160_draft.json",
        PROJECT / "packets" / "drafts" / "1129_slots_00161_00237_draft.json",
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
    expected = set(range(1, 238))
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
            if row.get("file") != "1129.gsc":
                continue
            index = int(row["slot"])
            if index in expected:
                catalog[index] = row
            elif "lookup_keys" in row.get("lanes", []):
                lookup_slots.add(index)
    if set(catalog) != expected or lookup_slots != set(range(238, 296)):
        raise SystemExit("catalog or lookup coverage mismatch")

    final = []
    for index in sorted(expected):
        entry = entries[index]
        source, target = str(entry["source_text"]), str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift {index}")
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret token mismatch {index}")
        if JAPANESE_RE.search(target):
            raise SystemExit(f"Japanese residue {index}")
        target.encode("cp949", errors="strict")
        entry.update({"translator": "Codex internal model", "review_status": "reviewed_once", "reviewer": "Codex internal model single review pass", "notes": "초벌 번역 후 1차 문맥·문체·용어·코드 검수 완료"})
        final.append(entry)

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1129_all_translatable_slots_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "every translatable slot received exactly one Codex review pass",
        "newly_reviewed_range": [1, 237],
        "new_review_change_count": len(changes),
        "new_review_changes": changes,
        "file_translation_complete": True,
        "lookup_slots_preserved": [238, 295],
        "release_ready": False,
        "entries": final,
    }
    out = PROJECT / "packets" / "reviewed" / "1129_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"],
        "draft_inputs": [str(path) for path in draft_paths], "output": str(out), "entry_count": len(final),
        "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 237], "new_review_change_count": len(changes),
        "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True},
        "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper(),
    }
    (PROJECT / "audit" / "translation_review_1129_complete.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
