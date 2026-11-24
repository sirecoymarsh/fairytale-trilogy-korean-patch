from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1207_slots_00001_00159_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    2: "──들어오세요.^n문은 열려 있어요.",
    4: "평안하신가요, 라푼젤.",
    6: "어머, 평안하신가요.",
    7: "라푼젤은 조신하게 인사하는 앨리스를 바라보며^n온화한 미소를 지었다.",
    12: "오늘은 일어나자마자 한 번 오신 게 전부예요.^n당분간은 오시지 않을 것 같아요.^n──어서 와요, 앨리스.",
    15: "이 『낙원』을 잠시 산책하려 했을 뿐인데,^n할머니가 될 만큼 오랜 세월을 헤매고 만 건가 싶어^n자기 뺨을 꼼꼼히 쓰다듬었던 그때의 공포는.",
    18: "할머님은 오늘도 안 계시는군요.^n저는 늘 엇갈리기만 하네요.^n한 번 만나 뵙고 싶은데요.",
    22: "그건 곤란하겠네요!^n앞으로도 계속 엇갈리기를 빌어야겠어요.",
    28: "하지만 앨리스는 이것이야말로 『어른의 맛』임을 알고 있었고,^n그 맛을 맛있다고 느낄 수 있는 사람이 되고 싶어서,^n『맛있다』고 평하곤 했다.",
    29: "『맛있는』 것을 먹는 자신을 바라보며,^n라푼젤이 진심으로 행복한 듯 미소 짓는 것도^n앨리스의 가슴을 따뜻하게 했다.",
    33: "네, 정말 품격 높은 맛이네요.",
    37: "앨리스는 막 피기 시작한 꽃향기가 날 듯한 그 미소에^n넋을 놓고 빠져들었다.",
    39: "과자를 먹는 모습만 보아도 그렇다.^n앨리스라면 참지 못하고 한 번에 먹어 치울 과자를^n천천히 하나씩 소중한 듯 입에 넣는 모습이라든가.",
    43: "간호사 선생님에게 물어보니,^n『연기하는 것』과 『몸에 배는 것』의 차이라고 했다.",
    44: "어떻게 해야 몸에 밸까.^n라푼젤은 어떻게 몸에 익힌 걸까──",
    46: "왜 그래요, 앨리스.^n아무 말도 없이 그렇게 저를 빤히 바라보고.^n제게 어디 이상한 곳이라도 있나요?",
    50: "그리고서야 비로소 본론을 떠올렸다.",
    52: "있잖아요, 라푼젤.^n당신에게 묻고 싶은 게 있어서 왔어요.",
    54: "무엇인가요?",
    56: "그…… 그러니까…….^n어젯밤에 당신이 무엇을 하고 있었던 걸까 해서…….",
    62: "앨리스는 숙녀의 몸가짐으로 지니고 다니던 손수건을 내밀었다.",
    65: "어젯밤이라니…….^n무슨 말인지 모르겠어요.",
    66: "앨리스가 몸을 내밀어 손수건으로 닦고 있자,^n라푼젤의 갈라진 목소리가 들렸다.",
    69: "──보고 있었나요? 도대체 어떻게요.^n전에도 이런 일이 있었던 것 같아요…….",
    71: "네, 네.^n그 사람 방에 있는 별난 창문에,^n갑자기 당신 모습이 떠올랐어요.",
    72: "그렇군요, 하고 한숨과도 같은 목소리로 대답하며^n라푼젤은 두 눈을 질끈 감는다.",
    75: "그…… 놀랐어요.^n라푼젤이 그렇게나 정숙하지 못한……──",
    80: "그, 하지만 저는 나쁜 일이라고 생각하지 않았어요.^n이 탑 안에만 계속 있으면서 아는 사람이 할머님과 저 정도뿐이라면^n분명 재미없을 테니까요. 따분할 테니까요.",
    82: "그런 당신이 다른 누군가를 알고 있다니.^n그것도 왕자님이라니요.^n멋진 일이라고 생각했어요.",
    84: "……당신은 그렇게 말해 주는군요.",
    88: "네, 라푼젤은 행복해 보였는걸요.^n그렇죠?",
    90: "행복…….^n네, 그래요. 맞아요.^n행복이라는 것을 그분이 가르쳐 주셨어요…….",
    92: "고개를 끄덕이며 분홍빛 꽃처럼^n은은하게 물드는 라푼젤의 뺨을 보며,^n앨리스는 분명 잘못 본 거라고 자신에게 타일렀다.",
    94: "그, 제가 묻고 싶은 건,^n무엇을 하고 있었는지, 그게 어떤 일이었는지예요.",
    96: "무엇이라니, 그건, 그…….^n당신이 본 그대로예요…….",
    98: "아, 아, 아. 저기…… 그렇군요, 그…….^n여자의 몸은 그렇게 되는군요. 남자의 몸도…….^n수술과 암술인 거죠. 알고 있어요. 배웠으니까요.",
    101: "하지만 제가 알고 싶은 건 그런 게 아니라요.^n왜 그 일을 했는지가 궁금해요.^n당신은 어째서 그 일로 행복해졌는지, 그런 것 말이에요.",
    103: "아아…….^n네, 그런 것이라면 바로 대답할 수 있어요.",
    104: "라푼젤은 마침내 마음을 진정한 듯하다.^n등을 원래처럼 반듯하게 펴고 차분히 말했다.",
    106: "저와 그분──왕자님은,^n그렇게 서로 사랑하고 있었어요.",
    108: "제가 그분을 사랑하는 마음과,^n그분이 저를 사랑하는 마음을^n서로 전하고 확인하며 둘이서 행복에 잠겨 있었답니다.",
    115: "앨리스는 어젯밤 잠들지 못하고 몇 번이나 되뇌었던 말을^n다시 입안에서 굴렸다.",
    116: "기묘한 맛이다.^n아무리 핥아도 녹지 않는 사탕 같다.",
    118: "앨리스는 누군가를 사랑해 본 적이 있나요?^n누군가와 연정에 빠진 적은…….",
    121: "사탕이 두 개로 늘었다.^n통째로 삼킬 수밖에 없지만 목에 걸려 넘어가지 않는다.",
    122: "앨리스가 앉은 의자가 삐걱 소리를 낸 것은,^n어딘가에 『빠졌을』 때의 감각을 떠올리려^n앨리스가 엉덩이를 움직였기 때문이다.",
    124: "연정에는 『빠지는』 거군요.^n사랑에는 『빠진다』고 하지 않나요?",
    126: "그런 말은 들어 본 적 없어요.^n사랑에는…… 빠진다. 잠긴다.^n그렇게 말하곤 하나 봐요.",
    127: "빠진다. 잠긴다.^n앨리스의 의자가 다시 삐걱 울었다.^n머릿속으로 이런저런 계산을 시도했기 때문이다.",
    128: "연정은 분명 빠진 뒤보다 빠지는 순간이 중요하고,^n사랑은 아마 빠진 다음이 중요하며, 아무래도^n빠지는 곳은 자유롭지 못한 물속인 모양이다.",
    130: "연정에 빠질 때는 아프지 않나요? 허리를 찧는다든가…….^n사랑에 빠진 사람은 괴롭지 않나요?",
    132: "어머, 앨리스다운 질문이네요.^n전부 마음속에서 일어나는 일이에요.^n화가 난다거나 말이 헛나온다거나 하는 것처럼요.",
    136: "사랑과 연정은 어떻게 다른가요?^n라푼젤이 하는 것은 사랑이지, 연정은 아닌가요?",
    138: "글쎄요, 그건 사람마다 달라요.^n명확하게 대답할 수 있는 사람도 있을 테고,^n나눌 필요를 느끼지 않는 사람도 있겠죠──저도 그래요.",
    140: "그, 어젯밤에 본 것처럼 하면 사랑을 느낄 수 있나요?^n그렇게 정숙하지 못한 짓을 해야만 하나요?^n",
    143: "아니요, 괜찮아요. 정숙하지 못한 것은 사실이니까요.^n그렇군요, 정숙하지 못한 모습을 서로 보여 줄 수 있다는 것이,^n사랑의 증거 중 하나라고 할 수 있을까요.",
    148: "그렇게 어렵게 생각하지 않아도 언젠가는 알게 될 거예요.^n당신도 언젠가 사랑과 연정을 알게 되겠죠.^n그때 모든 것이 이어지며 답이 보일 거예요.",
    150: "연정의 함정에 떨어지고 사랑의 바다에 빠지고……?",
    154: "후후. 무서울지 즐거울지는 앨리스에게 달렸어요.^n하지만 괜찮아요. 연정도 사랑도 자신을 위해 하는 일이니까요.^n앨리스라면 분명 꿈처럼 즐거운 사랑을 할 거예요.",
    156: "그렇군요…….^n허리를 찧거나 물에 빠져 물을 마시지 않도록,^n지금부터 마음의 준비를 해 둘게요.",
    159: "인사를 하고 방과 과자의 맛을 다시 칭찬하며,^n평소처럼 떠날 때의 예의를 다하면서도,^n앨리스의 머릿속은 갓 태어난 계산식으로 넘쳐나고 있었다.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1207_slots_00001_00159_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 160))
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
            if item.get("file") != "1207.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(160, 218)):
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1207_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 159], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [160, 217], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1207_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 159], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_160_217_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1207_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
