from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1203_slots_00001_00228_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    1: "해가 질 때까지는 내키는 대로 거닐며 시간을 때웠다.",
    5: "종잡을 수 없이 물결치는 재즈를 들으며,^n『도대체 나는 뭘 하고 있는 걸까』 하고^n몇 번이나 생각했다.",
    8: "파고들수록 불길하고 불가해해지는 수많은 수수께끼에,^n나는 질려 버렸는지도 모른다.",
    14: "나직이 내뱉은 말은,^n무언가를 시험하는 듯하면서도 농담 같은 뜬금없는 인사였다.",
    21: "저예요, 앨리스예요.^n자꾸 찾아와서 미안해요.",
    25: "그게, 저, 죄송하지만^n어서 문을 열어 주셨으면 해요!^n제가 짐을 너무 많이 안았어요.",
    30: "내 눈높이에 나타난 것은^n앨리스의 반짝이는 눈이 아니라 커다란 바구니와^n그 위에 산더미처럼 쌓인 온갖 물건들이었다.",
    31: "대충 보기만 해도 사과와 오렌지, 말린 꽃,^n천구의, 습도계, 낡은 열쇠 꾸러미, 정체 모를 금속 도구,^n새틴 주머니, 털실 뭉치, 전구 가랜드로 보이는 것까지──",
    33: "저, 저기, 지금은 인사할 수가 없어요.^n예의에 어긋나지만 이대로 들어가도 될까요?^n제가 이대로 문을 통과할 수 있을까요?",
    36: "제법 무거워 내려놓을 때는 움직임이 거칠어질 수밖에 없다.^n순간 그렇게 생각해 침대 위에 내려놓았다.^n──아니, 쏟아 놓았다는 편이 맞다.",
    39: "앨리스의 의도를 반쯤 눈치채고도,^n나는 망연히 묻지 않을 수 없었다.",
    42: "이거요? 이건 아이스크림을 뜨는 스쿱이에요.",
    43: "은빛 도구를 뻑뻑하게 만지작거려 보인 뒤에는,^n이것은 향주머니, 이것은 옛날 영화 엽서라며^n하나씩 설명을 덧붙이는 앨리스에게 나는 깊은 한숨을 내쉬었다.",
    47: "당신 방에 장식할 만한 건 없을까요?",
    57: "아마 그곳에는 답답한 표정을 짓는^n회색펠리컨이라도 비치고 있겠지.",
    63: "응, 알았어.^n그래서 이걸 어떻게 하지?",
    66: "이건 아이스크림을 동그랗게 뜰 때 편리해요.",
    70: "아이스크림만 있으면 유용할 거예요.",
    76: "그리고 이것도요. 석궁이라고 하나요?^n이건──조금 위험한 물건이라 저는 좋아하지 않아요.^n하지만 남자분들은 좋아하시죠?",
    80: "글쎄요. 기억은 나지 않지만,^n제 방에 있었다는 건 그런 인연이 있었다는 뜻이겠죠.^n조금 낡기는 했어도 화살은 날아가지 않을까요?",
    86: "이건 거꾸로 가는 회중시계예요.^n태엽을 아무리 감아도 시간은 자꾸만 되돌아갈 뿐이죠.^n이것만 있다면 그 토끼 씨도 서두르지 않아도 될 텐데요.",
    88: "변덕스러운 미니 피아노예요.^n이렇게 쳐도 소리가 나지 않다가 잊을 만하면 띵 하고 울려요.^n마치 번개의 빛과 소리 같아요.",
    89: "앨리스의 설명이 시시하면 시시할수록,^n더욱 매력적으로 보이는 것은 어째서일까.",
    107: "세포 하나하나가 굳어지고 팔 전체가 당기는 느낌.^n내 머릿속 깊은 곳에서 일어나는 뿌리 깊은 거부 반응.",
    108: "경고와 비슷한──느낌이 든다.^n실제로 그것은 『그만두는 게 좋아』라고 내게 타이르는 듯하다.",
    116: "(……그래. 나는 그런 사람이야)",
    118: "잔잔한 수면에 돌이 떨어지고 퍼져 나간 물결이 덧없이 사라진다──^n그런 찰나의 환상 같은 동요였다.",
    122: "──앨리스, 고마워. 마음은 정말 기뻐.^n하지만 마음만 받을게.",
    128: "이렇게 많이 가져와 줬는데 미안하지만,^n네 보물을 내가 받을 수는 없어.",
    130: "그런 건 신경 쓰지 마세요.^n여기 있는 건 하나하나 모두 제가 정말 좋아하는 것들이지만,^n그렇기 때문에 당신이 받아 주셨으면 해서──",
    138: "──네, 물론이죠.^n저라면 언제든지요. 아까워하며 내주지 않을 일은 없어요.^n그리고 지금 당신에게 억지로 떠맡길 생각도 없답니다…….",
    140: "힐끗 시선을 보내자,^n앨리스는 그림책을 찢긴 아이처럼^n꿈이 깨진 침울한 표정을 짓고 있었다.",
    144: "──사실 나는^n그녀가 그런 표정을 짓는 이유를 알고 있는 게 아닐까.",
    152: "내 방에 두었다가,^n필요 없는 것만 돌려주는 건 어떨까?",
    156: "그런데도 앨리스는 조용히 미소 지으며 고개를 끄덕였다.",
    159: "아무렇게나 밀어 넣어서는 도저히 담을 수 없는 물건들을,^n여기저기 조정하며 어떻게든 집어넣는다.",
    160: "집어넣었다기보다 손잡이로 물건들을 고정하고,^n틈새에 가느다란 물건을 밀어 넣는 식으로^n간신히 균형을 유지했다는 편이 옳겠지만.",
    166: "이 소리가 알리는 것은 내 방 모니터의 작동.^n그리고 저 모니터가 비추는 것은 거의 언제나^n여자아이들이 이상한 일을 당하는 모습을 몰래 찍은──",
    173: "눈을 돌렸지만 새된 목소리는 가차 없이 내 귀를 때렸다.",
    176: "『아, 앗, 아, 아앙, 하, 격렬해…….^n 후아, 아아앗, 아, 아앙……』",
    178: "네, 아, 네에……?^n라푼젤? 어째서요?^n와, 와아. 무…… 무엇을 하는 걸까요.",
    184: "가끔 저 모니터가 저절로 켜져서^n다른 장소의 모습을 비춰.^n언제나 저런 이상한 장면뿐이야…….",
    188: "조심스럽게 고개를 들자,^n앨리스는 눈과 입을 멍하니 벌리고 뺨을 사과처럼 붉힌 채,^n라푼젤의 음란한 모습을 넋 놓고 바라보고 있다.",
    190: "대담하게 벌린 다리 사이로 복잡한 여성의 기관이 열리고,^n단순한 남성의 기관을 받아들이고 있다──^n기괴하게 맞닿은 살과 살.",
    194: "라푼젤은 무엇을 하는 걸까요.^n가짜 거북이처럼 눈물을 흘리면서요.^n상대분은 누구죠?",
    198: "『후아아, 하, 응, 아아아아……!^n 네, 멋져요…… 멋져요, 왕자님……!^n 기, 기분, 좋아, 좋아요……』",
    202: "그렇군요. 멋진 일을 하고 있는 거네요.^n상대는 왕자님이고요.",
    204: "망설이는 기색도 없이 모니터 속 광경을 바라보고 있다.^n별과 꿈을 흩뿌린 듯한 눈에 꿈틀대는 두 육체를 비추며,^n천진하게 눈을 깜빡이고 있다.",
    206: "본래라면 앨리스가 느껴야 할,^n라푼젤이 누군가 보고 있음을 알면 느낄 법한^n민망함을 나 혼자 대신 짊어진 기분이다.",
    210: "그런가요?^n그러니까 라푼젤은 어른인 거군요.^n세상에…… 이건 정말 놀랐어요. 놀랐답니다, 저.",
    213: "어쩔 수 없었다고 해도 『훔쳐보고 있었다』는^n꺼림칙한 점을 지적받지 않는 것은 다행이지만,^n이건 이것대로 어색하다.",
    220: "──네, 네, 그래요. 네, 알아요.^n이대로 바라보는 건 숙녀답지 못한 짓이죠.^n수, 숙녀답지 못한 건 안 돼요.",
    222: "문간으로 향하는 우리의 등을,^n라푼젤의 비명 같은 목소리가 떨리게 했다.",
    224: "『앗, 아, 아앗…… 꺄우우! 응!^n 아아…… 왕자님, 왕자, 니임……!^n 사랑하고 있어요, 사랑해, 사랑…… 아아앗!』",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1203_slots_00001_00228_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 229))
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
            if item.get("file") != "1203.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(229, 287)):
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1203_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 228], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [229, 286], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1203_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 228], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_229_286_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1203_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
