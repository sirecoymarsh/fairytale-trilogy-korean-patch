from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    2: "그 『너무 큰 의자』 끝에 걸터앉은 채 흔들거리는^n앨리스와 그레텔의 다리였다.",
    6: "아니요, 어서 와요!^n『실례합니다』라고 인사하고 정말로 방해가 되는 경우는^n별로 없다고 생각해요.",
    14: "아니요, 그레텔의 상담을 들어주던 중이에요.",
    17: "앨리스의 설명을 뒷받침하듯 그레텔이 고개를 끄덕인다.^n둘 다 진지한 표정이었다.",
    22: "──그러고 보니 우리,^n이렇게 다리를 흔드는 데 정신이 팔려서,^n정작 상담은 전혀 진전이 없었네요.",
    24: "응……, 나도 모르게, 재미있어서…….",
    26: "내려가요, 그레텔.^n여기 있으면 아무래도 자꾸 다리를 흔들게 돼요.",
    31: "두 사람이 의자 등받이에 걸린^n원피스를 붙잡고 타고 내려오는 동안,^n나는 의자 위에서 보이는 광경을 상상하며 조금 부러워졌다.",
    32: "앨리스는 꽃잎에 몸을 기대고,^n그레텔은 버섯 스툴 위에,^n나는 처음과 마찬가지로 말굽버섯을 자리로 골랐다.",
    34: "상담하는 데 내가 있어도 돼?",
    41: "빵을 주머니에 넣어 두면,^n무슨 일이 생겼을 때 조금씩 떼어서 길잡이로 쓸 수 있잖아…….",
    46: "있잖아, 숲속 깊은 곳에 버려졌을 때 같은 경우에…….^n표식이 있으면 집으로 가는 길을 알 수 있으니까…….",
    49: "그런 예정이 있다니, 상당히 험난하네요…….",
    51: "응.^n아마 조만간, 또 버려질 테니까…….^n",
    56: "──알겠어요! 제가 빵을 잔뜩 구울게요.^n표식으로 쓸 수 있을 듯한 반짝반짝한 빵을요.",
    61: "(이야기 흐름이 틀어지는 건 좋지 않겠지, 아마)",
    63: "오히려 빵이 그렇게 많으면,^n애초에 아이들을 버리게 된 원인인 식량난이^n해결되어 버릴 것 같기도 하지만.",
    66: "아니야.^n앨리스가 구워 줬으면 하는 건 길잡이용이 아니라^n내가 먹을…… 빵이야.",
    72: "빵을 주머니에 숨겨 두기로 결심한 것까지는 좋았지만,^n그레텔은 아무래도 먹보라서,^n그만 빵을 먹어 버려 비축할 수가 없다.",
    73: "그러니 앨리스가 구운 맛있는 빵을 잔뜩 먹으면,^n상대적으로 맛이 떨어지는 식사용 빵을 남겨 둘 수^n있지 않을까──",
    75: "(하긴, 그 먹성을 보면……)",
    76: "나는 얼마 전,^n그레텔에게 빵을 주었던 때를 떠올렸다.",
    77: "홀린 듯 빵을 베어 물던 그레텔.^n무시무시한 기세로 자취를 감춘 빵.^n정신을 차리고 입가에 빵 부스러기를 묻힌 채 멍하니 있던 그레텔.",
    81: "나는 전에 없이 결연한 표정으로^n앨리스에게 호소하는 그레텔을 보았다.",
    84: "방금 꿀꺽, 그녀의 목울대가 움직였다.^n상상하다가 고인 침을 삼킨 것이겠지.",
    86: "알겠어요!^n그럼 든든하게 먹을 수 있는 빵을 잔뜩 구울게요.^n쿠키도 머핀도, 케이크도 구워요!",
    93: "저, 정말 기대돼.^n앨리스의 빵이랑 케이크…….^n잔뜩…….",
    95: "뺨은 행복한 빛으로 물들고 얼굴 전체가 녹아내릴 듯 풀어진다.^n왠지 그 모습 자체가 어떤 달콤한 과자처럼 보였다.",
    99: "그레텔은 소리도 내지 못한 채 단숨에 귀까지 새빨개졌다.^n두 주먹으로 배를 때려 너무 정직한 배를 혼낸다.",
    101: "그래서 나는 자연스럽게 고개를 돌리고,^n그레텔의 필사적인 반응에 터져 나오려는 웃음도 꾹 참으며,^n아무 일도 없었던 것처럼 넘기려고 했──는데.",
    104: "앨리스는 엉뚱한 방향에서 결정타를 날렸다.",
    108: "그레텔은^n머리카락 끝이 뺨을 때릴 만큼 세차게 고개를 젓는다.",
    113: "그래서 그레텔도 돼지가 되어 버리는 건 아닐까 했어요.",
    115: "──!?^n아, 안 변해.^n돼, 돼지가 되지는…… 않을 거야?",
    119: "앨리스의 반응은 지나치게 가벼웠다.^n오히려 그레텔의 불안을 부추길 만큼.",
    124: "통통 튀는 발걸음의 앨리스를,^n방금 받은 충격에 아직 발걸음이 불안한 그레텔이 뒤따른다.",
    128: "줄곧 참아 온 웃음을 그제야 조금 터뜨렸다.",
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
        PROJECT / "packets" / "drafts" / "1130_slots_00001_00065_draft.json",
        PROJECT / "packets" / "drafts" / "1130_slots_00066_00128_draft.json",
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
    expected = set(range(1, 129))
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
            if row.get("file") != "1130.gsc":
                continue
            index = int(row["slot"])
            if index in expected:
                catalog[index] = row
            elif "lookup_keys" in row.get("lanes", []):
                lookup_slots.add(index)
    if set(catalog) != expected or lookup_slots != set(range(129, 187)):
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

    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1130_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 128], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [129, 186], "release_ready": False, "entries": final}
    out = PROJECT / "packets" / "reviewed" / "1130_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(path) for path in draft_paths], "output": str(out), "entry_count": len(final), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 128], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "append_dialogue_slots_included": True, "lookup_slots_excluded": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    (PROJECT / "audit" / "translation_review_1130_complete.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
