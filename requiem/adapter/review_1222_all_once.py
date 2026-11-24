from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1222_slots_00001_00088_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")


CORRECTIONS = {
    5: " 알몸으로 서로 껴안는 듯한^n 의식 따위──둘 다 굳이 치르지 않아도 상관없다고 생각하지만,^n『성서』에 어떻게 적어야 할지는 모른다.",
    7: "하지만 『행복하게 살았습니다』로 끝날 리가 없다.",
    14: "약한 소리를 하며 엎드린 내 위로 앨리스가 올라탔다.",
    20: "지금이 아니어도 되잖아…….^n다음 기회로 미루자. 그다음에.",
    23: "불과 어제 일인데, 앨리스는 벌써 『성서』를 펼치며^n가슴을 쭉 폈다. 새 페이지까지 써 온 모양이다.",
    25: "신데렐라의 못된 의붓언니가 뒤꿈치를 잘라 내고^n유리 구두를 억지로 신었어요.^n그대로 신데렐라인 척 밀어붙일 생각이에요.",
    31: "들키지 않을 승산이 있으니 그렇게 했겠죠?^n실제로 왕자님은 알아차리지 못하고 데리러 가고 있어요.^n이대로라면 전혀 닮지도 않은 꽝을 떠안게 될 거예요!",
    35: "내키지 않아 해 봐야 결국 앨리스 뜻대로 된다.^n나는 그것을 지겹도록 잘 알고 있었다.",
    36: "앨리스가 고집이 세고 제멋대로라서라기보다,^n나는──나만이 아니라 이 『낙원』의 모든 주민이,^n앨리스에게 약하다.",
    37: "필사적으로 무언가를 호소하는 말을 듣고 있다 보면,^n무엇이든 이루어 주고 싶어진다.",
    39: "석궁이나 보물 지도, 어떤 동물의 가죽 같은 것.^n페인트를 마구 칠해 더없이 붉어진 흰 장미 같은 것.",
    46: "억지 부리지 마.^n네가 올라탄 채로는 준비할 수 없잖아.",
    51: "졸린 것을 들킨 내가 신음하자,^n앨리스는 화사한 웃음소리를 터뜨렸다.",
    52: "나는 체념하고 무거운 눈꺼풀을 억지로 열었다.",
    53: "──세상이 하얗다.^n티 없이 새롭고 갓 태어난 빛으로 가득하다.",
    54: "한때 앨리스와 나를 붙잡을 뻔한 『옅은 그림자 같은 기억』은,^n너무나 눈부신 이 빛을 받아^n얼룩처럼 비참하게 사라지려 한다.",
    55: " 앨리스가 바라던 것,^n『즐거운 나날』이 『결코 끝나지 않는 일』은^n 앞으로도 이런 빛 속에서 이어져 가겠지.",
    57: "『성서』가 한 고비를 맞았더라도,^n 다음 페이지에 새로운 장을 써 넣으면 된다.",
    58: "끝나지 않는 즐거운 이야기를 살아간다.^n우리는 그러기 위해 태어났다.",
    60: "어이, 앨리스 군, 나나시 군.^n서두르지 않으면 왕자님의 마차가 와 버려!",
    64: "──두 손 들었다.^n정말 정말 지쳐 움직이고 싶지 않지만,^n어떻게든 움직여야만 한다.",
    67: "부탁이에요, 빨리 가야 해요.^n불쌍한 신데렐라가 이제 다시는 왕자님을^n만나지 못할지도 몰라요.",
    69: "있죠, 당신도 싫잖아요?^n누군가의 계략으로 정말 좋아하는 사람과 갈라지고,^n그 사람이 남의 것이 되어 다시는 만나지 못한다니…….",
    72: "따끔, 하고.^n어째서인지 가슴 깊은 곳이 타들어 가는 느낌에 단번에 잠이 깼다.",
    73: "나도 모르게 몸을 일으키는 바람에^n튕겨 나갈 뻔한 앨리스는^n황급히 날뛰는 말을 다루듯 자세를 바로잡았다.",
    77: "자, 어서 가요.^n지금이라면 분명 제시간에 갈 수 있어요!",
    78: "앨리스에게 팔을 끌리는 대로,^n나는 침대에서 내려와 문을 빠져나왔다.",
    79: "앨리스에게 이끌려 오늘의 모험을 향해 달리는 내 발밑으로^n따끔따끔 타들어 가는 『무언가』가 후드득 떨어지는 것을 느낀다.^n마치 헨젤과 그레텔이 길잡이로 흘린 빵 부스러기처럼.",
    81: "(──이상하네. 아무것도 생각할 게 없는데)",
    82: "가슴 깊은 곳에 한순간 나타난 『그림자』를──^n머뭇거리며 물어 오는 불안에 찬 누군가의 목소리를,^n나는 알고도 모른 척했다.",
    83: "──그런데 이 『낙원』은 대체,^n누구를 위한 어떤 곳이었지?",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    expected = set(range(1, 89))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1222_slots_00001_00088_draft":
        raise SystemExit("unexpected draft")

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
            if item.get("file") != "1222.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(89, 147)):
        raise SystemExit("catalog/lookup mismatch")

    final = []
    for index in sorted(expected):
        entry = entries[index]
        source = str(entry["source_text"])
        target = str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift {index}")
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch {index}")
        if JAPANESE_RE.search(target):
            raise SystemExit(f"Japanese residue {index}")
        target.encode("cp949", errors="strict")
        entry.update(
            {
                "translator": "Codex internal model",
                "review_status": "reviewed_once",
                "reviewer": "Codex internal model single review pass",
                "notes": "초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료",
            }
        )
        final.append(entry)

    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1222_all_translatable_slots_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "every translatable slot received exactly one Codex review pass",
        "newly_reviewed_range": [1, 88],
        "new_review_change_count": len(changes),
        "new_review_changes": changes,
        "file_translation_complete": True,
        "lookup_slots_preserved": [89, 146],
        "release_ready": False,
        "entries": final,
    }
    output_path = PROJECT / "packets" / "reviewed" / "1222_all_translatable_slots_reviewed_once.json"
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "draft_inputs": [str(DRAFT)],
        "output": str(output_path),
        "entry_count": len(final),
        "review_passes_per_slot": 1,
        "newly_reviewed_slots": [1, 88],
        "new_review_change_count": len(changes),
        "checks": {
            "source_text_and_hash_match_catalog": True,
            "caret_token_order_preserved": True,
            "all_targets_strict_cp949": True,
            "no_kana_residue": True,
            "exactly_one_review_per_slot": True,
            "all_translatable_slots_covered": True,
            "lookup_slots_excluded": True,
            "lookup_range_89_146_preserved": True,
        },
        "output_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1222_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
