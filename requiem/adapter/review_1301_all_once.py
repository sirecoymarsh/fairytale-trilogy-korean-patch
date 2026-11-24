from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1301_slots_00001_00156_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")


CORRECTIONS = {
    2: "으으…… 그만……^n그, 그만해 줘어…….",
    3: "하룻밤이 지나 그레텔의 상태를 살피려고^n복도를 걷던 내 귀에,^n거의 쉬어 버린 울음소리가 들려왔다.",
    5: "이건…… 그레텔의 목소리야?",
    6: "빠른 걸음으로 그쪽을 향하자 복도 끝에^n몸을 움츠린 그레텔이 보였다.",
    9: "있잖니, 그레텔아.^n오빠는 찾았니?^n응, 찾았어?",
    10: "어른 주제에 묘하게 어린애 같은,^n몹시 기분 나쁜 말투였다.",
    12: "의사는 그레텔의 어깨며 허리를 마구 만지면서,^n볼에 안경이 파묻힐 것만큼 둥그런 얼굴로^n히죽거리고 있다.",
    16: "역시 못 찾았지이?^n어쩌면 오빠 같은 건 애초에 없었던 거 아니니이?",
    27: "도망칠 곳도 없이 육중한 그림자에 뒤덮인 채,^n누가 봐도 그레텔은 겁에 질렸는데,^n의사는 들러붙어 일방적으로 말을 걸었다.",
    29: "어라, 왜 그러니, 그레텔.^n아직도 이런 더러운 봉제 인형을 가지고 있니이?",
    30: "의사는 그레텔이 꼭 끌어안은^n테디베어를 발견했다.",
    36: " 그레텔은 움츠러든 채로도,^n『싫어』라는 최대한의 의지를 담아^n 작게 고개를 저었다.",
    44: "오히려 기름기에 흐려진 안경 너머로,^n그 눈을 황홀한 듯 가늘게 뜨고 있었다.",
    48: "그레텔은 얼굴을 엉망으로 일그러뜨리며 달려들었지만,^n의사는 빼앗은 인형을 홱 들어 그레텔에게서 멀리했다.",
    49: "그레텔이 있는 힘껏 발돋움할 때마다,^n의사의 뱃살이 출렁거린다.^n춤추듯 움직이는 그 꼴이 어찌나 얄미운지──",
    53: "그후…… 그후휴…….^n그, 그레텔은 조그맣네에.^n으깨 버리고 싶어질 만큼…….",
    58: "나는 뚱뚱한 의사에게 살금살금 다가가^n빈틈을 노려 그의 팔에서 인형을 낚아챘다.",
    59: "그리고 그레텔이 그의 시야에서 벗어날 수 있도록^n두 사람 사이에 끼어들었다.",
    63: "뭐야? 넌 누구냐?^n너 같은 꼬맹이가 있었나?^n누구야, 너?",
    66: "대답하려 해도 내게는 이름이 없다.^n고작 이런 일로 기세가 꺾이는 내가 한심했다.",
    68: "아, 그러고 보니 들은 적 있군.^n이름조차 기억 못 하는 이상한 꼬맹이가 있다더니.^n네가 그 녀석이냐.",
    69: "의사는 반쯤 화난 얼굴, 반쯤 히죽대는 얼굴로,^n나를 품평하듯 위아래로 훑어봤다.",
    73: "뭐, 네놈 따위는 아무래도 상관없지만.^n모처럼 남매끼리 스킨십하는데 방해하면 안 되지?",
    75: "자, 그레텔.^n소중히 간직해.",
    76: "나는 의사가 떠들게 내버려 둔 채 그레텔에게 돌아서서,^n그녀의 손에 단짝 테디베어를 돌려줬다.",
    91: "잠깐, 코미야 씨,^n당신 지금 뭐 하고 있는 겁니까!?",
    94: "우와, 코미야 씨, 또예요?^n당신에게 그 『자격』은 없다고 얼마 전에 혼났잖아요.",
    97: "코미야라고 불린 의사는 직원들에게 대꾸했지만,^n내게 달려들려는 모습을 보이자 곧바로 제압당했다.",
    100: "게다가 『또』라니.",
    102: "멋대로 손대지 말라고 들었죠?^n규칙을 어기면 어떻게 되는지도 설명했죠?",
    106: "놔, 놓으라고, 이 자식들아!^n계획이, 비전이, 시뮬레이션이이!^n저, 저 꼬맹이가 헨젤이라니, 먼저 플래그를 세우다니!",
    112: "코미야 일행이 사라지기를 기다렸다가,^n나는 내 등 뒤에 숨어 있던 그레텔에게 돌아섰다.",
    115: "인형을 꼭 끌어안은 채,^n그레텔은 내 가슴에 톡, 하고 이마를 댔다.",
    116: "아직 공포가 가시지 않은 불안정한 숨소리와^n몸의 떨림이 전해져 온다.",
    124: "그레텔은 떨면서,^n내게 무언가를 호소하려는 듯했다.",
    126: "뭔가 있으면 내게 말해 보렴.",
    127: "떨리는 그레텔의 어깨에 살며시 손을 얹고,^n최대한 『오빠』답게 웃어 보였다.",
    132: "나는 그제야 이해하고 그렇게 중얼거렸다.",
    133: "충분히 그러고도 남을 사람 같았다.^n오히려 다른 범인이 있다면 더 골치 아프리라 싶을 만큼,^n그 『납치 사건』의 범인 인상과 꼭 맞아떨어진다.",
    137: "그 말을 한 순간, 내 머리를 또 그 통증이 덮쳤다.",
    139: "(옛날에…… 나는 『여동생』에게 같은 말을 한 적이^n 있는 것 같아……)",
    140: "그런 확신에 가까운 감각이 솟아올랐다.",
    143: "그레텔이 눈물을 글썽이며 웃었다.^n연약하고 필사적으로 보였지만,^n아마 억지로 지어낸 웃음은 아니었을 것이다.",
    148: "그것은 아무도 믿을 수 없는 세상 밑바닥에 남은,^n유일한 마음의 위안이자 유일한 내 편이었다.",
    151: "나는 정말 헨젤이 되어 가고 있는 걸까.",
    152: "──모르겠다.^n나 자신에 관한 일인데도 지금의 나는^n자신 있게 단언할 수 있는 게 거의 없다.",
    155: "나는 잠시뿐인 여동생의 머리를 살며시 쓰다듬으며 마음먹었다.",
    156: "아무것도 알 수 없는 이 상황에서 단 하나,^n이 마음만큼은 진짜이니까.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    expected = set(range(1, 157))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1301_slots_00001_00156_draft":
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
            if item.get("file") != "1301.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(157, 215)):
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
        "scope": "1301_all_translatable_slots_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "every translatable slot received exactly one Codex review pass",
        "newly_reviewed_range": [1, 156],
        "new_review_change_count": len(changes),
        "new_review_changes": changes,
        "file_translation_complete": True,
        "lookup_slots_preserved": [157, 214],
        "release_ready": False,
        "entries": final,
    }
    output_path = PROJECT / "packets" / "reviewed" / "1301_all_translatable_slots_reviewed_once.json"
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "draft_inputs": [str(DRAFT)],
        "output": str(output_path),
        "entry_count": len(final),
        "review_passes_per_slot": 1,
        "newly_reviewed_slots": [1, 156],
        "new_review_change_count": len(changes),
        "checks": {
            "source_text_and_hash_match_catalog": True,
            "caret_token_order_preserved": True,
            "all_targets_strict_cp949": True,
            "no_kana_residue": True,
            "exactly_one_review_per_slot": True,
            "all_translatable_slots_covered": True,
            "lookup_slots_excluded": True,
            "lookup_range_157_214_preserved": True,
        },
        "output_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1301_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
