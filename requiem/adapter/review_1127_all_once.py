from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    1: "게르다의 방을 찾아가니, 그녀는 차를 준비하는 중이었다.",
    3: "찻잔과 받침 세트는,^n고맙게도 두 사람 몫이 준비되어 있었다.",
    6: "티포트에 부은 뜨거운 물속에서^n찻잎이 천천히 춤추는 모습을 바라보며,^n게르다는 어째선지 변명하듯 중얼거렸다.",
    14: "맛있다.^n이런 건 마음이 놓이네. 고마워.",
    16: "아니, 내가 더 고마워.^n이렇게 차를 우려 보고 싶어진 것도 네 덕분이야.",
    17: "옆 나무 상자에 앉아,^n똑같이 찻잔을 든 게르다가 미소 짓는다.",
    18: "하얀 도자기 같은 그녀의 뺨이 살며시^n봄꽃 같은 빛으로 물드는 모습을 보니,^n나도 왠지 마음이 따뜻해졌다.",
    22: "솔직히 처음 발견했을 때는^n내 취향을 꿰뚫어 본 것 같아서 기분 나빴어.^n실제로 차를 우려 본 건 처음이야.",
    25: "그렇게 우리는 다시 사소한 이야기를 주고받았다.",
    26: "어떤 찻잎을 좋아하는지, 어떤 잼을 좋아하는지,^n어떤 과자를 좋아하는지──^n그런 작은 행복을 이야기하는, 아무에게도 해가 되지 않는 대화.",
    27: "나에게도 게르다에게도,^n바로 이런 사소한 일상이 필요하다고 생각한다.",
    29: "──그러고 보니 옷이 달라졌네.",
    31: "응. 이케노 씨한테 받았어.^n갑자기 떠맡기듯 주더라고…….",
    34: "게르다는 무척 진지한 말투로 내 옷이 잘 어울린다고 칭찬했다.",
    39: "이케노 씨…… 이케노 씨구나.^n그분, 특이하지.^n다른 의사 선생님들과는 느낌이 달라.",
    43: "다른 의사 선생님들은 『너는 게르다가 아니야』라고 하면서도,^n나를 억지로 게르다로 만들려는 것 같아.^n이케노 씨는 그 반대야.",
    45: "그게…… 내가 이상한 소리를 한다고 생각하겠지만.",
    48: "이케노 씨는 『어떤 배역에도 어울리도록』──그러니까^n『동화 증후군』을 고치기는커녕, 수많은 이야기에 맞추라며^n내게 이 옷을 건넸다.",
    54: "한 손에 잔을 든 채^n다른 손을 입가에 댔기 때문에,^n잔이 받침 위에서 달그락하고 튀었다.",
    58: "응……. 미안해.^n왠지 오한이 느껴져서.",
    62: "감기라니…… 싫네.^n하지만 이렇게 오한이 드는 걸 보면, 그럴지도 모르겠어.",
    69: "게르다는 아주 잠깐 무방비한 표정으로 나를 보았다.^n내 배려가 고맙기는 해도,^n내가 떠나는 건 외로웠던 모양이다.",
    70: "하지만 다음 순간에는 평소처럼^n모범생 그 자체인 빈틈없는 표정으로 돌아와,^n아무 일도 아니라는 듯 고개를 끄덕였다.",
    72: "그러네. 심해지면 안 좋으니까.^n일찍 침대에 들어가서 푹 자야겠어.",
    74: "그릇은 내가 치워 둘게.",
    76: "정말? 그건…… 큰 도움이 되겠어.^n미안하지만 부탁해도 될까?",
    78: "응.^n복도 카트에 두거나, 안 보이면 주방에 가져다 놓으면,^n씻어서 방으로 가져다주는 거였지?",
    81: "그릇을 올린 쟁반을 들고 나가려는 나를 위해,^n게르다는 문을 열어 둔 채 잡아 주었다.",
    89: "아마 나보다 게르다가 더 불안할 것이다.^n게르다는 나와는 다른 의미로 『자기가 누군지 모르는』 것이다.",
    92: "그게…… 몸조리 잘해.^n의사 선생님께 약을 받으면 되지 않을까?^n모처럼 여기는 병원이니까.",
    95: "게르다는 눈에 띄게 얼굴이 굳었다.^n그녀의 불신과 경계가 얼마나 뿌리 깊은지 전해져,^n나는 방금 내뱉은 실언을 후회했다.",
    100: "게르다는 한동안 말을 머뭇거렸지만,^n이윽고 고개를 들고 말했다.",
    102: "내가 몸이 안 좋다는 건 아무에게도 말하지 말아 줘.",
    106: "그래서 나는 그녀의 눈을 똑바로 바라보며 고개를 끄덕인다.^n내가 자기 편이라는 사실을 충분히 믿게 하지 않으면, 게르다는 다시^n경계의 벽을 쌓아 올릴 것 같았기 때문이다.",
    107: "모처럼 마음을 열어 준 게르다를^n다시 혼자 남겨 두고 싶지 않았다.",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_paths = [
        PROJECT / "packets" / "drafts" / "1127_slots_00001_00055_draft.json",
        PROJECT / "packets" / "drafts" / "1127_slots_00056_00107_draft.json",
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
    expected = set(range(1, 108))
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
            if row.get("file") != "1127.gsc":
                continue
            index = int(row["slot"])
            if index in expected:
                catalog[index] = row
            elif "lookup_keys" in row.get("lanes", []):
                lookup_slots.add(index)
    if set(catalog) != expected:
        raise SystemExit("catalog coverage mismatch")
    if lookup_slots != set(range(108, 166)):
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
        "scope": "1127_all_translatable_slots_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "every translatable slot received exactly one Codex review pass",
        "newly_reviewed_range": [1, 107],
        "new_review_change_count": len(changes),
        "new_review_changes": changes,
        "file_translation_complete": True,
        "lookup_slots_preserved": [108, 165],
        "release_ready": False,
        "entries": final,
    }
    out = PROJECT / "packets" / "reviewed" / "1127_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "draft_inputs": [str(path) for path in draft_paths],
        "output": str(out),
        "entry_count": len(final),
        "review_passes_per_slot": 1,
        "newly_reviewed_slots": [1, 107],
        "new_review_change_count": len(changes),
        "checks": {
            "source_text_and_hash_match_catalog": True,
            "caret_token_order_preserved": True,
            "all_targets_strict_cp949": True,
            "exactly_one_review_per_slot": True,
            "all_translatable_slots_covered": True,
            "lookup_slots_excluded": True,
        },
        "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1127_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
