from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1201_slots_00001_00207_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    4: "기억은 없어도 『동화 증후군』이 상당히 이상한 병이고,^n이곳에 사는 여자아이들이나 그녀들과 주고받는 대화 역시^n현실과 상당히 동떨어져 있다는 것쯤은 알 수 있으니까.",
    6: "그래서 눈을 떴는데도 여전히 이곳에 있다는 사실이^n무척 이상하고, 너무나도 막막하다.",
    15: "저예요. 앨리스랍니다!",
    25: "안녕하신가요.^n",
    26: "글쎄요, 있었다면 있었다고 할 수 있을까요.",
    28: "아침에 일어나 창밖의 해님을 보고 있는데,^n그러고 보니 당신 방에 찾아온 적이 없다는^n생각이 들었답니다.",
    38: "실례하겠습니다…….",
    40: "──와아!^n얘기는 들었지만 정말 하얗네요.^n그리고 그…… 실례일지도 모르지만, 정말 아무것도 없군요.",
    46: "아무것도 없는 건 아니지만…… 정작 중요한 게 없잖아요.^n과자는요? 모자는요? 찻잔 세트는요?",
    47: "얼굴을 굳힌 채 홱 돌아서더니 쉴 새 없이 질문을 퍼붓는다.",
    59: "그래요, 장미가 좋겠어요.^n그것도 아주, 격렬하고, 무시무시하고, 곤두박질치듯 새빨간 장미.",
    69: "그래!^n머릿속이 새하얗기 때문에 방도 새하얀 백지인 거야.^n그러니 분명 딱 좋게 느껴지는 거야.",
    74: "하지만 앨리스에게는 그렇지 않은 모양이다.^n커다란 보석 같은 눈이 동그랗게 뜨이고,^n그 눈동자가 눈에 띄게 촉촉해진다.",
    76: "그럴 수가, 그런 일이…….^n여, 여기가 당신 머릿속인가요?^n이렇게 하얗고, 아무것도 없는 방이요?",
    80: "그렇다면 더더욱 꾸며 봐야 해요.^n이 방에 재미있는 무언가를 장식하면,^n당신의 머릿속에도 재미있는 무언가가 생기지 않을까요?",
    86: "(게다가 이런 아이이기 때문에야말로^n 믿을 수 있다고 생각했지)",
    93: "앨리스가 본 것에 관해 좀 더 자세히 듣고 싶다.^n앨리스 자신이 하룻밤을 보내고 어떻게 생각하는지도 포함해,^n가능한 한 부담을 주지 않으면서.",
    100: "──아아! 맞아요!^n어제는 『엉망진창 다과회』가 있었죠.",
    102: "엉망진창 다과회…… 아, 응.",
    108: "화덕……? 무슨 일이 있었나요?^n화덕이라면 요리할 때 자주 쓰는데요.",
    112: "아아, 분명 연기가 자욱했던 기억은 나요.^n",
    119: "앨리스는 비명 같은 소리를 내며 입가를 가렸다.^n얼굴이 순식간에 새파래져 도저히 연기하는 것으로는 보이지 않는다.",
    122: "왠지 차분히 생각하는 성격은 아닌 것 같고,^n여러 일을 쉽게 잊을 것 같다고도 생각했다.",
    125: "무서운 기억을 봉인하려 한 결과인지도 모르지만,^n오히려 내가 오싹해질 만큼^n지나치게 태평하다.",
    127: "그 새까맣게 탄 분도 가엾고, 그걸 봤다는^n어제의 저도 참 딱하네요…….^n오늘의 저는 그런 일을 모르니 분명 행복하겠죠.",
    129: "게다가 앨리스는 두려운 듯 다시 내 방을 둘러보며^n이런 말을 중얼거렸다.",
    131: "──그렇군요, 그런 거예요.^n잊는 건 나쁜 것만은 아니에요.^n머릿속 쓰레기통은 분명 신이 주신 선물이에요.",
    140: "저는 그래도 괜찮다고 생각해요.^n싫은 일은 전부 버리고,^n대신 멋진 것만 모으면 되는 거예요.",
    144: "어엿한 숙녀가 되고 싶다면 그러면 안 된다고^n누군가 제게 말한 적이 있어요.",
    146: "사교계는 답답하고, 멋을 부리려면 인내가 필요하고,^n과자도 너무 많이 먹으면 안 돼요.^n즐거운 일만 누려도 되는 건 어린아이일 때뿐이라고요.",
    149: "찌릿, 하고 머릿속 깊은 곳에서 불꽃이 튄다.",
    163: "앨리스의 손에서 느껴지는 온기가 손끝에서 손바닥과 팔을 타고^n은은히 스며들어 온다.",
    165: "재미있는 일뿐이면 제가 잠들기 어려워져요.^n기쁜 일뿐이면 제가 감사 인사를 깜빡해요.^n그래서 미리 못을 박는 거예요. 예절 교육이에요. 저는 알아요.",
    167: "일찍 자고 일찍 일어나며 감사 인사만 제대로 할 수 있다면,^n멋진 일뿐이어도 상관없어요.",
    171: "앨리스가 말하는 한없이 달콤하고 어린애다운 자기 편한 주장에^n기가 막힌 건지, 겁을 먹은 건지, 마음이 움직인 건지.",
    173: "그러니 보물을 방에 장식해요.^n",
    181: "내 목소리는 돌처럼 딱딱했다.^n이런 잿빛 목소리를 가진 사람이^n앨리스가 말한 것 같은 방에서 살 수 있을 리 없다.",
    187: "어머, 그렇네요!^n미안해요, 너무 오래 실례했네요.",
    189: "문손잡이에 손을 얹은 채 빙그르르 돌아보더니,^n왜인지 흠흠, 하고 헛기침을 한다.",
    192: "네. 저, 즐거운 시간이었어요.^n이 하얀 방이 너무 하얘서 깜짝 놀랐지만,^n",
    195: "이 방에 사는 당신이라는 존재에도 더욱 흥미가 생겼어요.^n긴 인생을 살다 보면 하얀 방에서 지낼 때도 있는 법이죠, 네.^n",
    199: "갑자기, 그것도 억지로 내 방을 칭찬하기 시작한 건^n앨리스 머릿속의 가정 방문 안내서에^n그런 대목이 있었기 때문일까.",
    202: "그녀의 쉴 새 없는 재잘거림과 화려하고 독기 어린 드레스,^n쉴 새 없이 달라지는 표정.^n정신없이 몰아친 앨리스의 여운이 방을 더욱 넓어 보이게 한다.",
    207: "그런 생각을 멍하니 하면서,^n나는 진찰 시간까지 선잠을 잤다.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1201_slots_00001_00207_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 208))
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
            if item.get("file") != "1201.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(208, 266)):
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1201_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 207], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [208, 265], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1201_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 207], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_208_265_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1201_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
