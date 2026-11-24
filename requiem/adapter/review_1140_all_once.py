from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1140_slots_00001_00085_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    1: "라푼젤은 막 잠에서 깨어난 참인 듯했다.",
    5: "라푼젤은 나를 보고 몇 번 눈을 깜빡였다.^n의아한 눈빛이었다.",
    9: "무언가 말하려다 라푼젤은 그때마다 말끝을 흐렸다.",
    12: "나는 무슨 말을 할지 망설이다 결국 무난한 말을 꺼냈다.^n지금 라푼젤은 분명 몹시 혼란스러울 것이다.",
    13: "생각대로 라푼젤은 이마에 손을 얹고 고개를 젓는다.^n머릿속에 꽉 찬 혼란이 출렁출렁 요동치는 듯한,^n무척 무거워 보이는 몸짓이었다.",
    21: "하지만 그런 전제가 이런 식으로 뒤집힌 라푼젤은,^n현실 세계를 있는 그대로 바라볼 수밖에 없다.",
    22: "분명 눈앞의 나는^n『낯은 익지만 모르는 소년』이라는,^n지극히 모순된 존재로 받아들여질 것이다.",
    24: "역시…… 역시 꿈이었나 봐요.^n안 돼요, 저…… 이런 시간에 잠들 생각은^n조금도 없었는데…….",
    25: "라푼젤은 떨리는 손으로 자기 머리카락을 끌어 모았다.^n방구석에서 길게 똬리를 튼^n밧줄 같은 감촉에 안도의 숨을 내쉰다.",
    27: "그래요, 머리카락은 그대로 기니까요.^n고델 할머님께 그분과의 일을 들켰다니.^n──꿈이에요. 전부 꿈이었던 거예요.",
    37: "나는…… 나는.^n──나도 모르니까 아무렇게나 생각해도 돼.^n어차피 꿈이니 사라질 테고.",
    40: "라푼젤은 나를 빤히 바라보았다.^n『사라지는 건가요?』 하고 호기심 어린 눈으로 묻듯이.",
    46: "네, 말씀해 보세요.",
    48: "꿈속에서, 화덕에서 시체가 나왔잖아.^n기억해?",
    50: "──네. 물론 기억하고말고요.^n연기가 자욱했죠. 불쾌한 냄새였어요.",
    56: "저는 아무것도 보지 못했어요.^n주방을 들여다보니 온통 연기 바다였거든요.",
    58: "제 뒤에 온 게르다는 들어갔지만,^n제게는 그런 용기가 없었어요.^n줄곧 문간에 서서 잠잠해지길 기다렸어요.",
    76: "나는──아마 라푼젤 자신보다도 강하게^n희미한 기억의 정체가 궁금했지만,^n지금 억지로 캐내 봐야 괴롭힐 뿐이라고 단념했다.",
    79: "고마워……요…….^n──있죠, 꿈 밖에서도 만날 수 있다면 멋지겠네요.",
    83: "그녀의 졸린 미소에는 경계심 하나 없는 천진한 친밀감이^n담겨 있어, 『라푼젤』이라는 가면 아래에서^n직접 내게 건네진 듯했기 때문이다.",
    85: "그건 어쩔 수 없는 일이지만, 역시 조금 쓸쓸하게 느껴졌다.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1140_slots_00001_00085_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 86))
    entries = {slot(str(entry["uid"])): dict(entry) for entry in draft["entries"]}
    if set(entries) != expected:
        raise SystemExit("draft coverage mismatch")
    changes = []
    for index, target in CORRECTIONS.items():
        before = str(entries[index]["target_text"])
        entries[index]["target_text"] = target
        if before != target:
            changes.append({"slot": index, "before": before, "after": target})
    catalog = {}
    lookup = set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1140.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(86, 144)):
        raise SystemExit("catalog or lookup coverage mismatch")
    final_entries = []
    for index in sorted(expected):
        entry = entries[index]
        source = str(entry["source_text"])
        target = str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift at slot {index}")
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {index}")
        if JAPANESE_RE.search(target):
            raise SystemExit(f"Japanese residue at slot {index}")
        target.encode("cp949", errors="strict")
        entry.update({"translator": "Codex internal model", "review_status": "reviewed_once", "reviewer": "Codex internal model single review pass", "notes": "초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"})
        final_entries.append(entry)
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1140_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 85], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [86, 143], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1140_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 85], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_86_143_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1140_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
