from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1208_slots_00001_00274_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    3: "넓은 정원이지만 장미원 한쪽으로 곧장 향하면^n앨리스가 있는 곳은 금세 알 수 있었다.",
    5: "자, 어서요! 지금이라면 아직 늦지 않았어요.^n제발요. 왕이 언제나 중재해 주리라는 보장은 없어요.^n여러분의 목이 날아가는 모습 따위 저는 보고 싶지 않아요.",
    8: "앨리스는 몸을 내밀어 필사적인 표정으로 계속 애원한다.^n그 앞에서는 빗자루를 든 청소부 아저씨가^n난처한 표정으로 머리를 긁고 있었다.",
    13: "청소가 끝나지 않은 곳은 문제의 장미원뿐인가…….^n곤란하네. 아직 그 아이가 있으려나.",
    15: "글쎄. 오늘은 꽤나 집착하고 있었으니까…….^n이렇게 된 이상 그냥 빨간 페인트를 가져가는 게 빠를지도 몰라.^n정말 골칫거리라니까, 이번 앨리스는.",
    17: "역대 앨리스 중에서도,^n밝다고 할지 말괄량이라고 할지 독특하잖아.^n골칫덩이 앨리스야.",
    19: "지금까지 중 가장 재미있긴 하지만.^n나도 모르게 휘말리고 만다니까.",
    23: "(앨리스……?^n 도대체 정원에서 뭘 하고 있는 거지?)",
    28: "다, 당신!^n마침 잘 오셨어요. 이 카드 병사분께도^n이대로는 위험하다고 전해 주세요.",
    32: "보시다시피 카드 병사분들이^n실수로 흰 장미를 심어 버린 모양이에요.^n붉은 여왕이 지나가면 뭐라고 할 것 같아요!?",
    34: "『당장 목을 쳐라!』라고 할 거예요.",
    37: "그러니 적어도 빨간 페인트를 준비해서^n장미꽃을 모조리 칠하면 좋겠어요.^n지금부터 닥치는 대로 시작하면 분명 늦지 않을 거예요.",
    40: "나는 이제는 익숙해진 당혹감과 무력감에 휩싸여^n또다시 말을 잃었다.",
    45: "또 무슨 이상한 짓을 벌이고 있겠지 하는^n기가 막힌 마음이 그 무게 그대로 호기심으로 바뀌었던^n──그 기묘한 마음의 변화를 되짚어 본다.",
    47: "그러니 부탁해요. 당신도 말해 주세요.^n여러분은 위험하다고요.^n몸통과 헤어지는 것보다는 페인트 냄새가 나는 편이 낫다고요.",
    50: "건성으로 대답하며 시선을 돌리자 빗자루를 든 아저씨는^n손주들이 노는 모습을 보는 듯 흐뭇한 눈빛으로^n그저 싱글벙글 우리를 바라보고 있다.",
    52: "뭐야, 자네도 흰 장미를 빨갛게 칠해 줬으면 하나?",
    57: "그렇게 당황하고 있는 사이, 여느 때처럼 앨리스의 머릿속에서는^n정보와 정보가 이상한 방식으로 이어진 듯하다.^n갑자기 숨을 헉 들이마시더니 미안한 표정을 짓는다.",
    61: "흰색을 좋아하시는 당신께는 더없이 불쾌한 이야기겠죠.^n",
    66: "──그래, 알았다, 알았어.^n앨리스의 마음은 잘 전해졌단다.^n흰 장미를 빨갛게 만들면 모두 해결돼. 간단한 일이지.",
    71: "그래, 정말이야.^n지금 페인트를 가지러 갔으니 도착하는 대로 칠할게.^n앨리스는 걱정하지 않아도 돼. 괜찮아.",
    78: "(……역시 직원이야. 능숙하게 둘러대네)",
    83: "네! 좋은 제안이에요.^n어쩌면 그 애도 만날 수 있을 테니까요.",
    90: "코 안쪽이 찡하게 뜨거워지는 것을 느끼며 돌아보니,^n페인트 통을 든 정원사들이^n흰 장미를 빨갛게 칠하고 있었다.",
    96: "(그렇다 해도 왠지 즐거워 보이네.^n 콧노래까지 부르는 것 같아)",
    97: "큰 붓과 작은 붓을 나눠 쓰면서,^n척척 대충 칠하다가도 때로는 사사삭 섬세하게.^n모두 일요일의 아마추어 화가처럼 의기양양한 옆모습을 하고 있다.",
    99: "복도에서 우연히 들은 대화로 엿볼 수 있었던,^n직원들이 앨리스를 흐뭇하게 여기는 마음도.",
    101: "(아무래도 앨리스에게 마음이 움직여,^n 이제 그녀가 걱정하지 않도록 다시 칠한 걸까……)",
    102: "그렇다면 굉장히 응석을 받아 주는 셈이다.",
    103: "조금 앞서 걷는 앨리스의 가벼운 발걸음과 들뜬 콧노래,^n바람을 타고 전해지는 아주 달콤한 과자 냄새를 느끼고 있자니,^n그 이유를 아주 조금은 알 것도──같다.",
    112: "거목의 멋진 가지와 촘촘한 잎 무리가 보일 만큼 가까워지자,^n앨리스는 팔을 뻗어 나를 제지했다.",
    117: "머릿속 한구석으로는 아직 조금 전의 『빨간 흰 장미』를^n생각하고 있었기에,^n내 반응은 몇 박자 늦었다.",
    125: "만족스러운 미소, 비웃음, 억지웃음, 쓴웃음──^n히죽히죽, 씨익씨익, 생글생글, 싱글싱글──",
    126: "어느 종류인지 알 수 없고 어떻게 보아도 이상하지 않은,^n기묘한 미소.",
    131: "야옹, 하는 울음소리가 울려 퍼졌나 싶더니,^n다음 순간에는 나무줄기를 재빨리 달려 내려가는 날렵한 그림자.",
    134: "나는 몇 번이나 눈을 깜빡였다.^n처음 바라보았던 나무 위에 충격적인 고양이의 미소가^n아직도 달라붙어 있는 듯했다.",
    138: "『앨리스』에게 길을 알려 주고 사라졌다가 금세 다시 나타나며,^n이번에는 꼬리 끝부터 차례로 사라지나 했더니^n온몸이 사라진 뒤에도 『미소』만 남았다는──",
    142: "내 마음속에서 메마른 목소리가 당황한 내게 경고한다.",
    146: "──아주 잠깐 재채기라도 한 얼굴이,^n우연히 미소 같은 인상으로 눈에 새겨졌을 뿐이야.",
    150: "오늘은 무척 빨리 가 버렸네요.^n평소에는 이런저런 이야기를 즐겁게 들려주는데요.",
    155: "(나도 『동화 증후군』 환자야.^n 우연히 기억이 없어서,^n 거짓 역할에 빠지지 않고 있을 뿐이고)",
    157: "(그러니 남의 말에 조금 휘말려 환각을 보더라도,^n 어느 정도는 어쩔 수 없는 일이야, 분명──)",
    163: "그래요. 나무 위에 남아 있잖아요.^n『고양이 없는 웃음』──저는 저걸 노리고 있었어요.^n기다려요. 지금 가져올 테니까요!",
    164: "나는 온갖 충격에 넋을 잃은 채,^n거목으로 달려간 앨리스가 나무줄기에 매달리는 모습을 바라보았다.",
    176: "쉿. 꼭 말을 해야겠다면,^n그 입은 스스로 막고 계세요.^n부탁이니 지금은 조용히 해요. 네?",
    180: "옷차림부터 나무 타기에 알맞지 않고,^n몸놀림을 보아도 날렵하다고 할 수 없는 앨리스는,^n오직 신중함만을 무기 삼아 조심조심 나무를 올라간다.",
    181: "몇 번이나 자세가 무너지고 흔들린 가지에서 나뭇잎이 흩날릴 때마다,^n내 마음의 표면도 깎여 나가^n함께 떨어지는 듯한 기분이 들었다.",
    185: "조금 전까지 고양이가 앉아 있던──^n그리고 앨리스에게는 아직 『고양이 없는 웃음』이^n남아 있는 듯한 가지를 향해 있는 힘껏 손을 뻗는다.",
    190: "나는 나무로 달려가,^n무모한 앨리스의 바로 아래에서 두 팔을 벌리고 만일에 대비했다.",
    199: "다음 순간 내 두 팔과 어깨는^n여자아이 한 명의 무게를 받아 내며^n뜯겨 나갈 듯 아파 왔다.",
    205: "무, 무사하지?^n다행이다…….",
    208: "처음의 충격이 가라앉고 나니 앨리스의 무게는 그리 대단하지 않았다.^n무겁기는 해도 어떻게든 받칠 수 있다.",
    209: "나는 멍하니 자기 손을 바라보는 앨리스를 안은 채,^n가쁜 호흡을 간신히 가다듬었다.",
    213: "『고양이 없는 웃음』이요!^n전부까지는 아니어도 절반만이라도 갖고 싶었어요.^n오늘이야말로 가져와서 당신에게 주려고 했는데!",
    216: "나는 앨리스를 유심히 바라보았다.^n앨리스는 조금만 더 하면 됐는데, 하고 말하는 듯한 표정으로^n아무것도 없는 손끝을 바라보고 있다.",
    220: "『고양이 없는 웃음』이요.^n당신에게 필요하다고 생각했어요.",
    222: "──저는요, 당신에게 무언가 부족하다고 생각했어요.^n당신이 옷을 갈아입어도, 당신에게 흰색이라는 색이 있음을^n알게 되어도 무언가 부족한 느낌이었어요.",
    224: "그게 뭔지 깨달았어요.^n당신에게는 『미소』가 부족해요!",
    228: "당신은 좀처럼 웃지 않잖아요.",
    232: "게다가 여기서 앨리스가 말하는 『미소』란^n얼굴 근육이 웃는 모양을 만드는 것을 뜻하지는 않으리라.",
    233: "앨리스가 처음으로 내 방을 방문했을 때 머릿속을 스친,^n『아무것도 필요 없어』, 『얻어서는 안 돼』라는^n다급한 심정.",
    234: "앨리스가 잡동사니를 가져왔을 때,^n석궁에 손을 뻗은 순간의^n나 자신을 밀어내는 듯한 『경고』.",
    239: "앨리스는 그것을 자기 체중을 버티는 한계의 신호로^n받아들인 모양이다.^n황급히 고개를 숙이고 몸부림치듯 스스로 땅에 내려섰다.",
    241: "미안해요. 덕분에 살았어요, 고마워요.",
    243: "그런 뒤 옷 여기저기에 붙은 나뭇잎과 나무 부스러기를 털고,^n흐트러진 치맛자락을 정돈한 뒤,^n그녀는 나를 똑바로 바라본다.",
    245: "저, 한 가지 기억난 게 있어요.^n──가족에 관한 일이에요.",
    251: "짧고 아무렇지도 않은 말인데,^n뱃속이 묵직하게 무거워진다.",
    255: "저는 막내라 늘 응석을 받아 주기만 했고 게으름뱅이였으며,^n공부도 운동도 정말 못하고,^n요리는 그럭저럭하지만 바느질이나 정리는 형편없었어요.",
    257: "부끄럽지만 다이나가 저보다 먼저^n화장실 훈련을 마쳤을 정도로, 그게…….^n저는 여러모로 부족했어요.",
    258: "뺨을 붉히고 머뭇거리며 몸을 꼬면서,^n앨리스가 말하는 것은 누구의 가족 이야기일까.",
    262: "하지만 원작에서 앨리스가 공부도 운동도 집안일도 못하는 아이라거나,^n화장실 훈련이 끝나지 않아 실수가 잦다거나,^n그런 묘사는 없었던 것 같다.",
    264: "하지만 그래도 괜찮다는 말을 들었어요.^n너는 모두를 웃게 만드는 특별하고 귀중한 재능이 있어.^n그러니 괜찮다고요.",
    266: "그래서 저는 웃지 않는 당신에게 미소를 선물하고 싶어요.",
    270: "막 피어난 꽃처럼 활짝 웃는 앨리스가^n한없이 멀게 느껴져 가슴이 괴롭다.",
    271: "무엇보다 계속 세차게 뛰는 심장이^n집요하게 그 『경고』를 호소하고 있었다.",
    272: "앨리스가 애틋하게 입에 담은 『가족』이라는 단어는,^n내 심장을 납으로 바꾸어 차가운 피를 내보내는 듯하다.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1208_slots_00001_00274_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 275))
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
            if item.get("file") != "1208.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(275, 333)):
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1208_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 274], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [275, 332], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1208_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 274], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_275_332_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1208_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
