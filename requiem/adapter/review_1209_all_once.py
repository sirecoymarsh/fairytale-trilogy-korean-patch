from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1209_slots_00001_00217_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    3: "등에 자잘하게 부딪치는 앨리스 목소리의 돌멩이.^n나는 알아차리지 못한 척 성큼성큼 복도를 걸었다.",
    5: "──왠지 기분이 좀 안 좋은 것 같아.",
    6: "조금 전까지 화기애애하게 이야기했는데,^n어설픈 변명을 남기고 갑자기 등을 돌려^n혼자 돌아가려 하다니 몹쓸 짓이라고 생각한다.",
    7: "앨리스는 아무 잘못도 없다.^n내가 멋대로 땅울림처럼 쿵쿵 쑤시는 심장을^n견디지 못하게 되었을 뿐이다.",
    11: "(나는 왜 이렇게 침울한 걸까)",
    14: "귀에 들어온 순간 납처럼 차갑고 무겁게 뱃속으로 떨어져,^n심장 박동을 불길하게 고조시킨 단어.",
    15: "앨리스는 애틋하게 그리워하며 입에 담은 말인데,^n내게는 마치 불길한 주문과 같다.",
    20: "빙빙 돌 뿐 갈 곳 없는 생각을 감당하지 못한 채,^n앨리스를 떼어 놓으려고 걸음을 재촉한다.",
    22: "저기요, 가지 마세요, 부탁이에요.^n당신의 발은 마치 무서운 괴물에게서 도망치는 것 같아요.^n제대로 저를 돌아보고 이야기해요.",
    25: "앨리스는 아주 정확한 말을 한 것인지도 모른다.^n나는 욱신거리는 가슴을 누르며 그렇게 생각했다.",
    27: "헉, 하아, 헉, 하아, 헉, 하아…….^n여기가 결승점이죠.^n따, 따, 따라잡았어요.",
    31: "헉, 하아, 헉, 하아, 헉, 하아…….^n이, 이 정도는 아무것도 아니에요.^n수, 술래잡기는 자신, 있어요.",
    38: "어린애 같은 내 마음의 목소리에 귀를 기울여 보니,^n아무래도 나는 앨리스가 애틋함과 그리움을 담아^n『가족』이라고 말한 것이 마음에 들지 않는 모양이다.",
    39: "그것만으로 여태 어느 때보다 앨리스가 멀게 느껴져,^n조금쯤 심술궂은 일을 당하게 해도 괜찮다고^n생각하고 만 듯하다.",
    43: "헉, 하아, 헉, 하아, 헉, 하아, 헉, 하아…….^n뭐, 뭐가 미안한 건가요.^n수, 술래잡기, 재, 재미있었어요.",
    48: "──하얀 방이라도 괜찮다면 쉬었다 가.",
    50: "네, 꼭 그러고 싶어요──후우, 후우.^n실례할, 게요.",
    52: "미안하게도 내 방에서는 차 한 잔조차 나오지 않는다.^n그래서 우리는 그저 입을 다문 채,^n앨리스의 가쁜 호흡이 가라앉기를 기다렸다.",
    55: "숨소리가 차분해질 즈음,^n앨리스는 치맛자락을 정성스레 털고 등을 펴며,^n새삼 진지한 모습으로 나를 올려다본다.",
    57: "그…… 아까는 도대체 왜 그러셨어요.^n기분이 좋지 않다고 하셨는데,^n어째서 갑자기 그렇게 되신 거예요?",
    61: "너와 이야기하다가 『가족』을 생각했더니,^n기분이 나빠졌어.",
    67: "다만 단서는 될지도 몰라.^n내 『가족』을 떠올리려 하면 뭐랄까,^n마음이 무거워지는 모양이야.",
    69: "분명 별로 화목하지 못한 가정이었겠지.",
    75: "네 말대로 머릿속 쓰레기통이^n제 역할을 잘해 주고 있네.",
    79: "응.^n괴롭고 힘든 일은 버리고,^n멋지고 즐거운 일만 채우면 된다고 했던가?",
    83: "그걸 제가 말했나요?^n어머나, 제가 꽤 좋은 말을 했네요.^n저는 그날의 제가 마음에 들어요.",
    85: "그러게.^n그러니 나도 싫은 일이라면 잊고 있는 것을 다행으로 여기고,^n이대로 머릿속에서 버려도 괜찮겠다고──",
    87: "네, 그래요!^n그리고 그 대신 멋진 『가족』을 떠올려서,^n가득 채우면 돼요.",
    92: "예를 들면 믿음직한 아빠와 다정한 엄마,^n개구지고 재미있는 오빠와 야무진 언니,^n그리고 귀엽고 영리한 반려동물──",
    100: "──제 가족에 관해 지금 머릿속 상자를^n바닥까지 뒤지고 있는데요…….",
    102: "이게 어찌 된 일일까요. 있어야 할 곳에서 보이지 않아요.",
    106: "그럴 리가요!^n저는 무엇 하나 잊은 기억이 없어요.",
    109: "여전한 앨리스식 말투에 나는 쓴웃음을 지을 수밖에 없다.",
    111: "그렇다면 순서대로,^n하나씩 떠올려 보는 것은 어때?",
    113: "네, 그러죠.^n상자를 뒤집는 것이 아니라,^n앞에 있는 것부터 하나씩 밖으로 꺼내면 되는 거군요.",
    115: "그래, 그래.^n그럼 어디 보자, 저…….^n앨리스가 이 『낙원』에 오기 조금 전쯤부터.",
    118: "앨리스는 망설임 없이 출발점을 정해 막힘없이 이야기하기 시작했다.^n그것은 『이상한 나라의 앨리스』 첫 장면이다.",
    120: "아, 저, 그건…… 그게 아니라…….^n그러면 토끼 굴에 떨어지기 전으로^n시곗바늘을 거꾸로 돌려 볼까?",
    121: "나는 황급히 말참견했다.^n앨리스에게 제대로 전달될 듯한 표현을 순간적으로 고른 것은,^n내가 생각해도 제법 잘한 일이다.",
    123: "네?^n──네. 시곗바늘을 거꾸로…… 해 볼게요.^n빙글, 빙글──",
    124: "앨리스는 눈을 감았다.^n눈꺼풀이 파르르 움직인 것은 어둠 속에서 거꾸로 도는 시곗바늘을^n쫓고 있기 때문일까.",
    126: "그러면 다시 둑 위네요.^n저는 언니 옆에서 따분해하고 있어요.^n언니는 삽화도 없이 글자뿐인 책을 읽고 있고요.",
    132: "──맞아요!^n적어도 따분해하고 있지는 않았다는 뜻이군요.",
    136: "그, 그때보다 한 시간 전의 너는?^n하루 전의 너는?",
    138: "그러니까, ……그러니까. 어. 어……?^n저기, 저기요, 저는…… 저는…….",
    142: "그럴 리가요!^n저는 기억상실이 아닌걸요.^n제 머릿속 상자에는 추억이 잔뜩 있고…….",
    147: "말이 끊긴 동시에 미동조차 멈춘 앨리스.^n마치 전원이 꺼진 듯한 변화에 말을 걸려다가,^n나는 깜짝 놀랐다.",
    150: "앨리스는 인형처럼 무표정했다.^n입술을 굳게 다물고 눈을 멍하니 뜬 채 허공을 응시하며,^n시간이 흐르는 것을 거부하는 듯했다.",
    151: "그 눈에는 평소의 은하수 같은 빛이 없다.^n균일하고 단조롭게 안쪽이 비쳐 보여 마치 유리구슬을^n박아 넣은 듯하다.",
    152: "그 무기질적인 눈동자에서 완전히 굳은 뺨과 입술 끝으로^n타고 흐르는 투명한 물방울──",
    154: "애, 애, 애, 앨리스.^n왜, 왜 그래. 눈물까지 흘리고.^n도대체 어째서…….",
    160: "앨리스는 감정을 죽이려 한 것인지,^n교과서를 읽어 내려가는 듯한 목소리로 내게 대답했다.",
    161: "하지만 그 목소리는 떨리고 있다.^n감추려는 듯 몇 번이나 눈을 깜빡일 때마다,^n눈에서 새로운 눈물방울이 타고 흐른다.",
    163: "저는 울고 있다고 생각하지 않는걸요.^n그러니 이건 눈물이 아니에요.",
    166: "어떡하지. 나는 어떻게 해야 할까.^n분명 앨리스의 여린 마음에서,^n특히 약하고 아픈 곳을 밟고 만 것이다.",
    167: "손수건은 찾을 수 없다.^n앨리스는 강한 척만 하며 위로하게 해 주지도 않는다.^n정말 어떻게 해야 할까.",
    171: "어린아이의 울음소리.^n허둥지둥 당황해 말문이 막힌 나.",
    176: "모호한 이미지에서 힌트를 얻어 나는 책상 서랍을 열었다.^n그 안에는 커다란 막대사탕이 굴러다니고 있었다.",
    178: "네. 저는 『달콤한』 사람이니까요.",
    180: "왠지──정말 왠지 모르게 남겨 두었다.^n화려한 포장지에도 달콤한 냄새에도 너무 익숙하지 않아,^n먹을 계기를 계속 놓치고 있었다.",
    186: "앨리스는 흠뻑 젖은 뺨에 미소를 피우며 받아 들고,^n포장지를 풀어 기쁜 듯 입에 가득 넣었다.",
    187: "그 표정은 평소처럼 밝고 명랑했으며,^n붉어진 코와 젖은 뺨만이 위화감을 풍기고 있다.^n마치 맑은 하늘과 빗방울이 어울리지 않는 여우비 같다.",
    193: "아아, 달아요. 달고 맛있어요.^n오늘의 제게는 이 단맛이 부족했던 걸지도 몰라요.^n망가진 눈에는 분명 좋은 약이에요.",
    194: "앨리스의 뺨이 오물오물 움직이는 것을 보며,^n나는 조금 전 되살아난 감촉을 되새겼다.",
    195: "누군가의 울음소리와 주머니 속 사탕.^n떠올릴 때마다 희미해지는 꿈보다도 덧없는 광경──",
    197: "(저건 내 기억일까.^n 오빠라고 불리고 있었는데……)",
    198: "그러고 보니 그레텔을 처음 만났을 때도^n『여동생』이라는 기억의 파편이 되살아났다.",
    203: "──『가족』.^n무심코 떠올리고 만 탓에 다시 가슴이 괴로워진다.",
    205: "(어째서지?^n 『여동생』만 생각하면 괜찮은데……)",
    206: "불길함에 불가해함까지 더해져 어지러울 것 같다.",
    209: "그…… 미안해요.^n저는 이만 돌아가 보려고 해요.",
    212: "당신과 더 많이 이야기하고 싶었어요.^n그런데 이렇게 갑자기 눈이 망가져 버리다니.",
    213: "앨리스는 눈가를 벅벅 문지르고,^n붉어진 눈꼬리로 미소를 지어 보였다.",
    215: "그럼 나중에 또 봐요.^n안녕히 계세요.",
    216: "그렇게 말하자마자 앨리스는 몸을 돌려,^n조금 빠른 걸음으로 방을 나갔다.^n늘 하던 인사조차 잊고서.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1209_slots_00001_00217_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 218))
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
            if item.get("file") != "1209.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(218, 276)):
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1209_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 217], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [218, 275], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1209_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 217], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_218_275_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1209_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
