from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1152_slots_00001_00135_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    2: "창문으로 조심스레 불어온 산들바람마저^n순식간에 짓무른 정체 속으로 삼켜 버릴 듯한,^n짙은 사향과 음란한 소리, 남녀의 체액이 풍기는 날것 같은 냄새.",
    4: "아…… 아앗, 아앙…….^n이, 이제 그 정도로…… 해 주세요. 부탁드려요.^n저, 아까부터 계속…… 제발요. 부탁드려요…….",
    5: "훌쩍이는 울음, 수치심 따위는 모조리 내던진 채 조르는 목소리──",
    7: "아, 아, 아앗…….^n아아, 그래요, 그래요. 빨리, 어서…….^n제발, 제 안, 에……!",
    11: "그것은 라푼젤이 오랫동안 애타게 바라던 것이었다.^n온몸을 쓰다듬고 핥고 실컷 희롱하면서도,^n아무리 애원해도 주지 않았던 단 하나의 확실한 감촉.",
    19: "라푼젤은 흐트러진 숨도 그대로인 채 손끝으로 아랫배를 어루만진다.^n뱃속을 뻔뻔스레 밀어 올리는 작열하는 감촉에,^n저절로 애틋한 미소가 떠올랐다.",
    20: "너무 오래 애태워져 당장이라도 녹아 흘러 사라질 듯했던^n자신의 육체가 이렇게 단단하고 따뜻한 중심을 얻어^n간신히 형태를 유지하고 있다.",
    28: "머금은 것에 미끈거리며 휘감기고,^n애태운 일을 나무라듯 단단히 끌어안아,^n더 깊은 곳으로 끌어들이는 복잡한 꿈틀거림을 보인다.",
    29: "『왕자』가 움찔 어깨를 떨며 숨을 길게 내쉬었다.",
    44: "연분홍빛 유두를 단단히 세우고,^n몸을 움직일 때마다 출렁이는 풍만한 가슴을^n『왕자』의 손이 거칠게 움켜쥔 것이다.",
    47: "봉긋한 살돌기를 집요하게 주무르는 손가락에 라푼젤은 항의의 목소리를 냈다.^n아까부터 장난스레 너무 많이 희롱당해,^n끝부분의 얇은 피부가 다 쓸려 버린 듯했다.",
    48: "욱신욱신 두려울 만큼 강한 저림이 피어나고,^n말뚝 하나만 박힌 채 내버려진 하체가^n거의 경련 같은 움직임으로 애타게 몸부림쳤다.",
    53: "정숙하지 못하다고는 생각한다. 하지만 이렇게 만든 것은 『왕자』다.^n게다가 라푼젤의 배 깊숙이 파고든 굳게 선 물건은^n잘게 떨리고 있으니, 이대로라면 그도 분명 괴로울 터였다.",
    56: "상대의 몸에 두른 다리 끝, 뒤꿈치로 허리를 재촉하듯 두드리며,^n깊숙이 박힌 것을 몸속에서 안타깝도록 조인다.",
    60: "『왕자』가 낮게 신음하며 입가를 풀었다.^n라푼젤의 뺨을 손바닥으로 진득하게 어루만지며 무언가를 속삭인다.",
    65: "열기와 단단함과 고동──라푼젤의 은밀한 곳이^n힘껏 휘감아 안고 있던 사랑스러운 감촉,^n그 모든 것이 물러나고, 사라져 간다.",
    83: "남자의 육봉이 거칠게 부드러운 살을 긁어 낼 때마다,^n여자의 깊은 통로는 몸부림치고 섬세한 주름은 꿈틀거리며,^n엄청난 양의 애액이 실금하듯 분비되어 물보라를 일으킨다.",
    91: "그것은 더할 나위 없이 행복한 한순간이어야 하는데.^n실제로 라푼젤의 윤기 흐르는 육체는 구석구석^n음란한 진액을 흘리며 기뻐하고 있는데도.",
    92: "어째서일까. 몸을 섞을수록 오히려 부족해진다.^n채워지는 족족 다시 굶주리고 마는 인간의 업일까.^n아니면──",
    96: "육체의 감각뿐만 아니라 말이.^n맹세가 담긴, 녹아내릴 듯 달콤한 말을 원한다.",
    99: "라푼젤은 열에 들뜬 듯 몇 번이고 되풀이했다.^n자신의 멍한 목소리가 더듬더듬 따라 하는 모습은 우스웠지만,^n몇 번이고 말하다 보면 자연스레 몸에 익을 터였다.",
    125: "그것이 『왕자』의 끝에서 쏟아진 엄청난 양의 정액임을^n깨달았을 때, 라푼젤은 약간의 우스움과 애틋함이^n찌르르하게 아랫배로 퍼지는 것을 느꼈다.",
    128: "흐트러진 호흡을 가다듬으며,^n꽉, 하고 경련하는 내벽을 조인다.",
    130: "이렇게 커다란 몸집으로 거친 짐승처럼 숨을 몰아쉬며,^n조금 전까지 실컷 배 속 깊은 곳을 괴롭혀 준 『왕자』가,^n어쩜 이렇게 순진한지. 어쩜 이렇게 사랑스러운지──",
    135: "외로움도, 불안도, 허무함도, 위화감도.^n눈을 감아 버리면, 자, 이제 아무것도 보이지 않는다.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1152_slots_00001_00135_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 136))
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
            if item.get("file") != "1152.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    expected_lookup = set(range(136, 194))
    if set(catalog) != expected or lookup != expected_lookup:
        raise SystemExit(f"catalog or lookup coverage mismatch: visible={len(catalog)} lookup={sorted(lookup)}")

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
        entry.update({
            "translator": "Codex internal model",
            "review_status": "reviewed_once",
            "reviewer": "Codex internal model single review pass",
            "notes": "초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료",
        })
        final_entries.append(entry)

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1152_all_translatable_slots_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "every translatable slot received exactly one Codex review pass",
        "newly_reviewed_range": [1, 135],
        "new_review_change_count": len(changes),
        "new_review_changes": changes,
        "file_translation_complete": True,
        "lookup_slots_preserved": [136, 193],
        "release_ready": False,
        "entries": final_entries,
    }
    out = PROJECT / "packets" / "reviewed" / "1152_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "draft_inputs": [str(DRAFT)],
        "output": str(out),
        "entry_count": len(final_entries),
        "review_passes_per_slot": 1,
        "newly_reviewed_slots": [1, 135],
        "new_review_change_count": len(changes),
        "checks": {
            "source_text_and_hash_match_catalog": True,
            "caret_token_order_preserved": True,
            "all_targets_strict_cp949": True,
            "no_kana_residue": True,
            "exactly_one_review_per_slot": True,
            "all_translatable_slots_covered": True,
            "lookup_slots_excluded": True,
            "lookup_range_136_193_preserved": True,
        },
        "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1152_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
