from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    81: "하지만──할머니. 부디, 부디 용서해 주세요.^n저희는 서로 사랑하고 있어요.^n부디 저와 그분을 갈라놓지 말아 주세요.",
    82: "나",
    83: "………….",
    84: "라푼젤",
    85: "말씀을 지키지 않은 것에 화가 나시는 건 당연해요.^n하지만 이 탑 안의 세계밖에 모르는 제게는^n모든 것이 너무 눈부셨어요.",
    86: "라푼젤",
    87: "그분의 눈빛도, 목소리도, 온기도──^n주어지는 모든 것이 따뜻하고 선명해서.^n──이것이 행복이라고 저는 생각했어요.",
    88: "나",
    89: "(그런 말을 나한테 해 봐야)",
    90: "왠지 이번에는 흥이 식는 기분이 들었다.",
    91: "나",
    92: "(라푼젤에게는,^n밤에 찾아온 사람이면 누구나 『왕자님』인데)",
    93: "그렇게 생각하니,^n라푼젤의 애절한 호소는 더없이 공허했다.",
    94: "그리고 상관없다고 대답하려 했다.^n정말로 내게는 억지로 보게 된 것이 민폐일 뿐이고,^n라푼젤이 뭘 하든 그녀 마음이라고 생각했으니까.",
    95: "하지만 고개를 숙인 채 떨고 있는 그녀를 보니,^n무관심하려 했던 이것저것이 신경 쓰였다.",
    96: "나",
    97: "있잖아…… 그 사람은 누구야?",
    98: "라푼젤",
    99: "왕자님…… 존귀하신 분이에요.^n그분의 나라로 함께 돌아가면 저를 왕비로──^n그렇게 말씀해 주셨어요.",
    100: "나",
    101: "그런 걸 묻는 게 아니라…….^n그 왕자님이라는 사람, 누구야?",
    102: "이 시설 사람과 사랑하는 사이가 된 거라면,^n어떤 일을 맡은 사람이고 어떻게 만난 걸까?^n내가 묻고 싶은 건 그런 것이다.",
    103: "라푼젤",
    104: "………….",
    105: "라푼젤은 조용히 고개를 들었다.^n새하얀 얼굴을 가로지르듯 머리카락 한 올이 흐트러져 있어,^n왠지 지친 인상이었다.",
    106: "라푼젤",
    107: "왕자님은 왕자님이에요, 할머니.",
    108: "나",
    109: "와, 왕자님이라니, 그렇게 쉽게 있는 사람이 아니잖아.^n어…… 어느 나라의? 이름은 뭐야?",
    110: "라푼젤에게 닿지 않을 질문임을 알면서도,^n나는 입에 담지 않을 수 없다.",
    111: "그러지 않으면 안 그래도 불확실한 내가^n동화 세계에 휘둘려 버릴 것만 같다.",
    112: "아니면 나는 상식적이고 참견 잘하는 어른처럼^n그녀를 타이르고 싶었던 건지도 모른다.",
    113: "라푼젤",
    114: "그건…….^n제가 아는 것이 없어서…….^n분명 설명을 들어도 이해하지 못할 거예요.",
    115: "라푼젤은 살며시 시선을 돌렸다.^n미약하지만 거절의 뜻이 담긴 몸짓이었다.",
    116: "그녀 안에 있는 작은 모형 정원 같은 세계가,^n내 거리낌 없고 멋없는 질문에 무너지려 하고 있다.^n긴 속눈썹이 괴로운 듯 떨리고 있다.",
    117: "하지만 이상하게 나는 망설이지 않는다.^n나도 나름대로 어딘가 필사적이었다.",
    118: "나",
    119: "네 자유이긴 하지만.^n그런 일은 잘 알지도 못하는 사람이랑 하는 게 아니야.",
    120: "라푼젤",
    121: "모르는 분이 아니에요.^n제 마음보다 더 사랑하는 분이에요.^n그러니 저는…… 무엇을 바쳐도 상관없어요.",
    122: "나",
    123: "정말 진심으로 그렇게 생각한다면 됐지만…….^n내 눈에는 그렇게 보이지 않았어.",
    124: "라푼젤",
    125: "어째서 그렇게 생각하시나요?^n물론 저는 진심으로 그분을 사모하고 있어요.",
    126: "라푼젤",
    127: "저는 그분을 만날 때마다──^n사랑을 속삭여 받고, 충만해져, 더는 아무것도 필요 없다고,^n……진심으로 그렇게 생각해요.",
    128: "라푼젤",
    129: "할머니, 다른 말씀은 무엇이든 따를게요.^n그러니 이것만은. 이것만은 부디 들어주세요.^n그분과 저를 갈라놓지 마세요──",
    130: "격정을 억누르듯 떨기도 하고,^n사랑을 나누던 때를 떠올린 듯 황홀하게 속삭이기도 하는,^n몹시 불안정한 목소리였다.",
    131: "나는 그것도 꼬집어 한마디 해 주리라,^n불안정한 그녀를 더 찔러 보리라, 짓궂은 마음으로^n입을 열려다──문득 허무해졌다.",
    132: "나",
    133: "(──이제 그만하자)",
    134: "라푼젤의 말이 나를 향하지 않듯,^n내 말도 그녀가 있는 곳에는 닿지 않는다.^n서로 엇갈릴 뿐이다.",
    135: "현실과 망상, 우리는 서로 다른 세계에 산다.^n애초에 제대로 대화를 주고받을 사이가 아니다.",
    136: "나",
    137: "(상관없잖아.^n라푼젤이 누구를 만나든, 이상한 짓을 하든.^n나랑은 관계없어)",
    138: "나는 깊이 한숨을 내쉬었다.",
    139: "요컨대 나는,^n그녀가 말하는 『사랑』에서 수상쩍음을 느껴^n걱정하고 말았지만.",
    140: "하지만 그것이야말로 멋없는 참견이겠지.^n애초에 라푼젤이 살아가는 『라푼젤』의 세계가^n아주 거대한 거짓이니까.",
    141: "나",
    142: "(너무 몰아붙였나)",
    143: "치솟았던 열기가 가라앉음에 따라,^n응어리가 후회로 바뀌어 가는 것을 느꼈다.",
    144: "라푼젤",
    145: "………….",
    146: "라푼젤은 라푼젤대로,^n창백한 얼굴로 무언가 골똘히 생각하는 듯하다.",
    147: "문득 라푼젤의 두 손이 배를 따라^n쓰다듬듯 움직인다는 걸 깨달았다.",
    148: "어젯밤 본, 보기에도 부드러워 보이던 배.^n포동포동 살집이 있는데도 우아한 곡선을 그리며 잘록했다.",
    149: "옷 위로 그곳을 쓰다듬는 움직임은,^n마치 몸속 깊은 곳을 걱정하고 소중히 여기는 듯해서──",
    150: "나",
    151: "(아, 그렇구나)",
    152: "분명 『라푼젤』 원작에서,^n고델 할멈이 두 사람의 밀회를 알아챈^n계기는 라푼젤의 임신이었다.",
    153: "나",
    154: "(전에 읽은 건 달랐던 것 같지만,^n도서관에 있는 『라푼젤』은 그랬지)",
    155: "나",
    156: "(라푼젤은 아이를 밴 채 탑에서 쫓겨나,^n오랫동안 황야를 헤매고……)",
    157: "나",
    158: "분명 남녀 쌍둥이를 낳았던가…….",
    159: "배 위를 천천히 오가는 손을 보며,^n나는 그만 생각한 것을 입에 내고 말았다.",
    160: "그러자 그 움직임이 딱 멈췄다.",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1131.gsc" and item.get("slot") in TARGETS: rows[int(item["slot"])] = item
    if set(rows) != set(TARGETS): raise SystemExit("catalog mismatch")
    entries = []
    for index in sorted(TARGETS):
        source, target = str(rows[index]["source_text"]), TARGETS[index]
        if CARET_RE.findall(source) != CARET_RE.findall(target): raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": rows[index]["uid"], "source_text": source, "source_raw_sha256": rows[index]["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 전"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1131_slots_00081_00160_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1131_slots_00081_00160_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())
