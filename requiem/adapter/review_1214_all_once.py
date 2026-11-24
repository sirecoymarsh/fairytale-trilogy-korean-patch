from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1214_slots_00001_00339_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    11: "앨리스는 그 들것 위에^n누운 채로 실려 온 모양이었다.^n마치 대형 사고 현장에서 구조된 중상자처럼.",
    34: "이대로 영원히 누워 지내는 앨리스가 되어 주면^n짜증 날 일도 없고 살겠네.",
    44: "괜찮아, 괜찮아. 무슨 말을 해도 못 듣고, 안 닿고, 못 알아먹어.^n그런 구제 불능의 못난 인간이니까^n이런 데서 환자님 노릇이나 하는 거잖아.",
    46: " 온종일 아무 걱정도 없이 즐거워서 좋았겠쪄요.^n 나도 망상의 세계로 도망치고 싶다고.^n『낙원』에서 가슴 큰 애랑 하하호호 놀고 싶다고.",
    52: "어라, 오늘은 인간의 말을 알아들어?^n세상에, 놀라워라! 열심히 진화했쪄요.",
    63: "쉬야나 응가가 하고 싶어지면 누르세용.^n가위바위보에서 이긴 놈이 달려와 도와줄 테니까.",
    76: "……아아……. 당신이었네요.^n미안해요, 이런 꼴이라서.",
    86: "이렇게 된 원인이 있을 테니 숨김없이 말하라고──^n그야말로 엄한 말투로 물으셨어요.^n결국 저는 숨기고 말았지만요.",
    109: "하지만 잠시 뒤 나는^n그 괴로움에서 벗어나려는 생각이 뜻밖에도 옳음을 깨달았다.",
    137: "앨리스. 분명 때가 온 것 같아.^n진실을 떠올리고, 그 진실과 마주할 때가.",
    145: "괜찮아, 무서워하지 마, 앨리스.^n분명 이건 네가 원하던 일이야.",
    185: "괴로워 보여서 도왔다.^n약해진 모습을 보고 싶지 않아 잠깐의 위안을 주었다.^n",
    188: "그 이상한 일기장을 가득 채울 때까지^n마음껏 놀고, 즐기고, 웃고,^n그런 뒤여도 분명 늦지 않다.",
    190: " 그건 네 성서이고, 네 이야기이며,^n『네 이야기가 무엇이든 적혀 있는』 책이지.^n 그렇지?",
    201: "여기에 적힌 이야기는 이미 지나가 버렸어요.^n이제는…… 이제는 깨어나기만 하면 돼요.^n제게 남은 삶은 이제 이것뿐이에요.",
    214: "기운 붉은 해에 비쳐 납작하게 누운 긴 그림자.^n휘청휘청 공허하게 헤매는 때 묻은 신발.^n가늘고 금방이라도 끊길 듯한 숨소리.",
    223: "어른이 들으면 눈살을 찌푸릴 만한 생각일 것이다.^n하지만 나는 아이니까 괜찮다.^n나밖에는 그녀를 위해 그런 생각을 해 줄 수 없다.",
    249: "그저 갑자기 혈색을 되찾아 가는 앨리스의 뺨을 보고,^n더욱 정신없이 말을 찾았던 것은 기억난다.^n",
    272: "제가 준 과자는 돌고 돌아 제가 받아 버렸고,^n제 보물은 당신 방에 어울리지 않았고,^n나무를 타도 손이 닿지 않아 떨어져 버렸어요…….",
    289: "앨리스가 이 한순간에 밑바닥에서 생명의 절정으로 회복했다──^n아니, 오히려 그곳까지 치솟았음을 이해하려면^n조금 더 시간이 필요했다.",
    295: "그리고 대개 해야 할 일을 끝내고 나면^n오늘이라는 날은 조금도 남아 있지 않아요.",
    327: "그게…… 말이죠.^n당신은 아직 알아서는 안 돼요.^n제가 삼켜도 될까요?",
    335: "음, 꿀꺽…….^n",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1214_slots_00001_00339_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 340))
    entries = {slot(str(entry["uid"])): dict(entry) for entry in draft["entries"]}
    if set(entries) != expected:
        raise SystemExit("draft coverage mismatch")
    changes = []
    for index, target in CORRECTIONS.items():
        before = str(entries[index]["target_text"])
        entries[index]["target_text"] = target
        if before != target:
            changes.append({"slot": index, "before": before, "after": target})
    catalog, lookup = {}, set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1214.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(340, 398)):
        raise SystemExit("catalog or lookup coverage mismatch")
    final_entries = []
    for index in sorted(expected):
        entry = entries[index]
        source, target = str(entry["source_text"]), str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift at slot {index}")
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {index}")
        if JAPANESE_RE.search(target):
            raise SystemExit(f"Japanese residue at slot {index}")
        target.encode("cp949", errors="strict")
        entry.update({"translator": "Codex internal model", "review_status": "reviewed_once", "reviewer": "Codex internal model single review pass", "notes": "초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"})
        final_entries.append(entry)
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1214_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 339], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [340, 397], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1214_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 339], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_340_397_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1214_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
