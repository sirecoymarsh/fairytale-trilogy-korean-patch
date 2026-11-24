from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1316_slots_00001_00222_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")


CORRECTIONS = {
    5: "문을 두드리며 불러 봐도^n안에서는 아무 대답도 돌아오지 않았다.",
    8: "나와 그레텔은 조심스럽게 문을 열고^n방 안을 들여다봤지만,^n그녀의 모습은 그곳에 없었다.",
    11: "정적에 휩싸인 방 안에는^n온기라고는 전혀 없는 벽난로 속 가짜 불꽃만^n아른아른 춤추고 있었다.",
    12: "불꽃빛은 감시실 모니터를 통해 보았던^n그 끔찍한 광경을 떠올리게 했다.",
    15: "그 영상이 무언가의 착오가 아니었다는 증거처럼,^n바닥에는 찢겨 나간 게르다의 옷 조각이 흩어져 있었다.",
    18: "카펫에는 아직 마르지 않은 무언가의 얼룩이 있다.^n주변에 아직 짐승 같은 냄새가 감도는 듯해서^n구역질이 치밀어 올랐다.",
    23: "그레텔이 내 옷자락을 잡아당겼다.^n그 손은 떨림을 억누르려는 듯 차갑게 굳어 있었다.",
    24: "……게르다를 찾는다.^n평소처럼 의연하게 미소 짓는 게르다를 찾으리라고^n나도 그레텔도 생각하지 않았다.",
    25: "오히려 돌이킬 수 없이 산산이 부서진 잔해를 주워 모으는 듯한^n괴로운 결말이 기다리고 있으리라 생각한다.",
    26: "──그래도 가야 한다.^n어떤 모습이 되었든 게르다는 기다리고 있다.",
    29: "우리는 시설 곳곳을 뛰어다니며 게르다를 찾았지만,^n그녀를 발견하지 못했다.",
    31: "직원들도 짐작 가는 곳이 없는 모양이다.",
    32: "시설 건물을 나와 정원의 호수까지 온 우리는^n호숫가에 홀로 서 있던 오데트에게서^n마침내 게르다를 봤다는 이야기를 들을 수 있었다.",
    34: "게르다 씨라면 분명 봤어.^n조금 전 호수 건너편을 걷고 있었어.",
    38: "멀리서 봐서 정확하지는 않지만.^n분명…… 저쪽 숲을 향하고 있었어.",
    43: "게르다 씨, 모습이 조금 이상했어.^n비틀거리는 걸음으로…….^n어디 다치기라도 한 걸까?",
    46: "느긋하게 고개를 갸웃하는 오데트의 맑은 눈동자에서^n나는 시선을 피했다.",
    47: "──그런 일을 당한 건 게르다뿐일까.^n",
    52: "숲 가장자리까지 도착했지만^n아직 게르다는 찾지 못했다.",
    57: "어둠에 휩싸인 깊은 숲을 들여다보며^n그레텔은 겁에 질려 움츠러들었다.",
    58: "지난번 코미야에게 끌려갔던 일을 떠올린 걸까.^n아니면 『헨젤과 그레텔』 이야기 속에서^n부모에게 버림받은 일과 연결 짓는 걸까.",
    59: "나는 알 수 없다.^n하지만 왜 떠는지 물어봐야^n분명 그 아이를 더 무섭게 만들 뿐이다.",
    61: "(그렇다 해도…… 아무런 표식도 없이^n 밤의 숲으로 들어가는 건 역시 무모하지……)",
    62: "게르다도 분명 그렇게 생각할 것이다.^n",
    65: "아무래도 이대로 숲에 들어가는 건 위험해.^n게르다도 그렇게 생각하고 있으면 좋겠지만…….",
    70: "떨고 있는 그레텔을 안심시키려고 손을 잡았다.^n──그럴 생각이었는데 나도 왠지 마음이 진정됐다.",
    72: "차갑게 굳어 있던 그레텔의 손가락이 펴져^n조심스레 얽혀 오는 것을 느끼며,^n숲을 따라 걸음을 옮겼다.",
    74: "무너진 돌담과 녹슨 철책이 둘러싼 부지 안에^n수없이 늘어선 직사각형, 정사각형, 십자 모양 조형물 무리.^n그 너머에는 조금 길쭉하고 끝이 뾰족한 건물 한 채.",
    80: "병동 창문이나 정원 쪽에서는 숲 그림자에 가려져^n지금까지 알아채지 못한 모양이다.",
    81: "불도 켜지지 않고 외벽도 무너져 가는 담쟁이투성이 교회는^n버려진 지 상당한 세월이 지난 듯했다.",
    90: "썩어 가는 교회 지붕 위에 게르다가 있었다.",
    91: "찢어져 너덜너덜해진 옷을 입은 채,^n지붕 위에 세워진 십자가에 매달리듯 서 있었다.",
    92: "거의 누더기가 된 치마가^n깃발처럼 펄럭이며,^n지붕 위로 몰아치는 바람의 세기를 보여 준다.",
    95: "아래에서 필사적으로 불러 보지만 게르다는^n우리가 전혀 눈에 들어오지 않는 듯했다.",
    96: "구멍이 뚫린 듯 텅 빈 눈동자는^n풍경을 비추고 있어도 보고 있다고 할 수 없을 것이다.",
    99: "바람에 흩날린 머리카락 사이로^n색을 잃은 입술이 경련하듯 열리고 닫히는 것이 보인다.",
    104: "찾고 또 찾아도 당신의 그림자조차 보이지 않아…….^n나는 언젠가 닿을 수 있을까? 당신이 있는 곳에…….",
    107: "그것은 얼어붙을 듯한 목소리로 필사적으로 엮어 내는^n그녀의 마음속 비명이었다.",
    109: "^n그것은 내가 아는 『게르다』의 말이 아니었다.",
    111: "이 눈보라의 끝에……^n눈의 여왕 궁전에 정말 당신이 있는 거야?",
    112: "그녀의 비통한 마음을 담기에는^n너무도 공허한 『게르다』의 대사.",
    113: "모욕당하고, 쓰러지고, 짓밟히고──^n그래도 게르다니까 분명^n정면으로 맞서려 했을 것이다.",
    116: "게르다의 잔해에서^n이 세상에 희미하게 남아 있던 그림자 같은 게르다 자신이 빠져나와,^n기어가듯 떠나는──그 발걸음이 보이는 듯했다.",
    117: "고통과 오욕, 절망뿐인 현실에서^n눈보라 너머 희미한 희망이 반짝이는 『눈의 여왕』의 세계로.",
    120: "철조망으로 심장을 묶은 듯한 통증이 내 가슴을 덮쳤다.",
    123: "멍하니 올려다보기만 하던 내 곁에서 달려 나가,^n그레텔이 교회 지붕으로 이어진 사다리에 손을 걸었다.",
    126: "교회 지붕은 높이 솟아 보인다.^n저기서 떨어지면 무사하지 못할 것이다.",
    127: "게다가 교회 지붕은 심하게 낡은 듯했다.^n잘못 디뎌 지붕을 뚫으면 게르다와 함께 곤두박질친다.",
    132: "아니.^n가벼운 내가 가는 편이 덜 위험할 것 같아.",
    135: "확실히 몸무게가 가벼운 그레텔 쪽이^n지붕에 주는 부담은 작을 것이다.^n──하지만.",
    137: "(안 돼, 이 아이를──^n ……여동생을 위험하게 만들 수는 없어!)",
    140: "게르다가 갑자기 날뛰기라도 하면,^n네 힘으로는 감당할 수 없어.^n그러니 역시 내가──",
    142: "괜찮아, 맡겨 줘, 오빠.^n나는 정말 필요할 때면 힘이 솟아나니까.",
    143: "평소와 달리 힘찬 그녀의 말에 나는 어안이 벙벙해졌다.",
    144: "두려운 기색은 조금도 보이지 않고,^n오히려 이미 해낸 듯한 자신감까지 내비치며^n힘차게 고개를 끄덕이고 웃어 보인다.",
    147: "오빠는 아래에서 말을 걸어 줘.^n그동안 내가 게르다 씨를 꼭 막을 테니까.",
    148: " 잠시 내 안에서^n『불길한 예감』과 『그레텔에 대한 신뢰』가 팽팽히 맞섰다──",
    151: "그사이 그레텔은 몸을 돌렸다.^n마치 나무를 오르는 다람쥐처럼 재빨리^n사다리를 타고 올라가 버렸다.",
    154: "눈 깜짝할 사이 그레텔은 지붕 위에 도착했다.",
    155: "발밑이 삐걱이는 것을 느낀 그녀는 지붕을 밟아 뚫지 않도록^n배를 바닥에 붙이고 게르다가 있는 쪽으로 기어간다.",
    158: "게르다는 뒤에서 그레텔이 다가오는 것을 알아채지 못하고^n밤하늘을 향해 계속 중얼거렸다.",
    160: "게르다!^n진정해, 이제 다 괜찮으니까!",
    161: "주의를 돌리기 위해서도,^n그리고 마음을 진정시키기 위해서도,^n나는 게르다를 향해 외쳤다.",
    163: "게르다…….^n네 고통을 지금까지 알아채지 못해서,^n정말 미안해…….",
    165: "하지만…… 하지만 게르다.^n이제부터 너는 혼자가 아니야.^n나와 그레텔이 네 편이니까…….",
    167: " 그러니 돌아와 줘.^n『낙원』 같은 곳이 아니라 우리 곁으로.",
    168: "그 외침이 전해졌는지^n게르다의 시선이 내려와 내 모습을 붙잡았다.",
    169: "갑자기 눈동자에 빛이 돌아왔다.^n그녀의 얼굴에 환한 미소가 떠올랐다.",
    172: "통했다고 생각했다.^n게르다 안에 남은 그녀 자신이 외침에 답해 줬고,^n이제 틀림없이 돌아와 줄 거라고.",
    174: "게르다는, 자세가 곧고 옆얼굴이 아름다운 그 여자아이는^n영리하고 야무지며 아주 강한 마음을 지녔다.^n침착한 태도 안에 불꽃 같은 의지를 품고 있다.",
    176: "분명 시간이 걸리겠지만 세심하고 조심스럽게 그녀의 마음을 치유해서,^n언젠가 한 여자아이로서 행복한 인생을 걸을 수 있도록.^n그것을 위해서라면 나는 무엇이든 아끼지 않을 생각으로──",
    178: "아…… 찾았어, 카이!^n드디어 당신을……!!",
    181: "게르다가 가느다란 팔을 이쪽으로 뻗었다.^n십자가를 끌어안던 것을 멈추자 그 몸이 휘청 기울었다.",
    182: "등골에 오싹하고 차가운 것이 내달렸다.",
    184: "긴 여행이었어…….^n소중한 것을 모두 빼앗기고,^n혼자 추운 설원을 걸어왔어.",
    187: "내 잠깐의 희망과 힘없는 제지를 짓밟듯^n게르다가 한 걸음 앞으로 내디뎠다.",
    189: "아, 안 돼…… 그쪽으로 가면 안 돼…….",
    195: "길고 긴 괴로운 여행 끝에 『카이』를 찾았다고 믿으며,^n하얀 뺨을 장밋빛으로 물들이고 부드럽게 표정을 풀어,^n눈물을 글썽이며 웃는 게르다에게──",
    196: "나는 카이가 아니라고 말할 수는 없었다.",
    197: "너는 게르다가 아니라고.^n여기는 『눈의 여왕』의 세계가 아니라고.^n괴로운 현실로 돌아오라고 말할 수는 없었다.",
    202: "태엽 장치 인형처럼^n게르다가 다가온다.^n나를──『카이』를 끌어안아 얼어붙은 얼음에서 구하려고.",
    203: "행복을 향해 나아가는 그 발밑에서^n불길한 소리를 내며 지붕이 삐걱이고 무너진 건축 자재가 떨어진다.",
    204: "지붕 위에서는 그레텔이^n얼마 안 되는 거리를 애타게 좁히고 있을 것이다.",
    205: "하지만 조심성이라고는 없는 게르다의 걸음은 따라잡을 수 없다.^n분명 지금쯤 그것을 절감하고 있을 때라──",
    208: "그레텔이 비통하게 외치며^n몸을 크게 내민 순간,^n또다시 무너지는 소리가 났다.",
    210: "그만둬, ……────!!",
    211: "나는 눈앞의 그녀를 도저히 『게르다』라고 부르고 싶지 않았고,^n그렇다고 뭐라고 불러야 할지 알 리도 없어서 그저^n이를 가는 듯한 소리를 바보처럼 흘릴 뿐이었다.",
    215: "다음 순간 게르다의 몸이 가볍게 허공을 날았다.",
    218: "교회 지붕에서 허공으로 뛰어든 그녀의 몸은^n마치 한 조각 눈 결정으로 변하기라도 한 듯,^n부자연스러울 만큼 천천히 밤하늘을 춤추며 내려갔다──",
    219: "나도 그 광경을^n계절에 맞지 않는 눈이라도 본 듯 멍하니 입을 벌리고,^n그저 두 눈에 새길 수밖에 없었다.",
    221: "그레텔은 모 아니면 도라는 심정으로^n지붕을 박차고 뛰어들 듯 손을 뻗었다고 한다.",
    222: "하지만 뛰어드는 순간이 너무 늦었다.^n그 손은 게르다의 등에 스쳤을 뿐^n허망하게 허공을 움켜쥐었다.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    expected = set(range(1, 223))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1316_slots_00001_00222_draft":
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
            if item.get("file") != "1316.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(223, 281)):
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
        "scope": "1316_all_translatable_slots_reviewed_once",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 1,
        "review_policy": "every translatable slot received exactly one Codex review pass",
        "newly_reviewed_range": [1, 222],
        "new_review_change_count": len(changes),
        "new_review_changes": changes,
        "file_translation_complete": True,
        "lookup_slots_preserved": [223, 280],
        "release_ready": False,
        "entries": final,
    }
    output_path = PROJECT / "packets" / "reviewed" / "1316_all_translatable_slots_reviewed_once.json"
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {
        "schema": "fairytale-requiem-translation-review-audit-v1",
        "status": "PASS",
        "scope": output["scope"],
        "draft_inputs": [str(DRAFT)],
        "output": str(output_path),
        "entry_count": len(final),
        "review_passes_per_slot": 1,
        "newly_reviewed_slots": [1, 222],
        "new_review_change_count": len(changes),
        "checks": {
            "source_text_and_hash_match_catalog": True,
            "caret_token_order_preserved": True,
            "all_targets_strict_cp949": True,
            "no_kana_residue": True,
            "exactly_one_review_per_slot": True,
            "all_translatable_slots_covered": True,
            "lookup_slots_excluded": True,
            "lookup_range_223_280_preserved": True,
        },
        "output_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest().upper(),
    }
    audit_path = PROJECT / "audit" / "translation_review_1316_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
