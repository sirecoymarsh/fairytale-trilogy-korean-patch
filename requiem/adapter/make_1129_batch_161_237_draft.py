from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    161: "게르다",
    162: "뭐……!",
    163: "간호사",
    164: "자, 오래 기다리셨습니다.",
    165: "간호사는 극채색 액체로 가득 찬 커다란 주사기를,^n쿵 소리가 날 듯 게르다의 눈앞에 내밀었다.^n원래도 싫어하던 주사가 더욱 무서워질 광경이다.",
    166: "게르다",
    167: "……, …….",
    168: "그래도 게르다는 입술을 꽉 다물고,^n동요를 드러내지 않으려 표정을 굳혔다.^n그 모습이 오히려 비장했다.",
    169: "간호사",
    170: "그럼 약 넣을게요.^n선생님, 부탁드려요.",
    171: "간호사는 게르다의 허리를 톡톡 두드린 뒤,^n엉덩이에 두 손을 대고 물컹, 둥근 살을 좌우로 벌린다.",
    172: "분명 게르다의 뒤에 선 의사 선생님에게는^n여자아이가 가장 싫어할 듯한,^n무척 외설스러운 광경이 보일 것이다.",
    173: "게르다",
    174: "크……읏……!",
    175: "게르다의 손끝이 가늘게 떨리며 진찰대에 박힌다.",
    176: "의사",
    177: "자, 그럼 움직이지 말게.",
    178: "간호사",
    179: "엉덩이에 힘 빼 주세요.^n주사기가 제대로 들어가지 않으면 오히려 아프니까요.",
    180: "게르다",
    181: "빨리, 읏, 빨리해 주세요……!",
    182: "게르다의 목소리가 아주 조금 떨렸다.^n굳은 의지가 벌어진 틈에서 새어 나온 그녀의 비명이었다.",
    183: "하지만 의사 선생님은 움직이기 전 잠시 뜸을 들였다.^n주사기를 들고 끝을 갖다 대는 몸짓도 공연히 느릿느릿했다.",
    184: "갖다 댄 뒤에도, 꾸욱, 꾸욱^n애태우듯 주사기를 위아래로 움직인다.",
    185: "의사",
    186: "음, 힘이 너무 들어가서 이래서는 좀처럼…….",
    187: "게르다",
    188: "──아……읏……!",
    189: "노골적인 고통의 신음을 내며 게르다의 온몸이 흔들렸다.",
    190: "활처럼 뒤로 젖혀져 일어나려던 게르다의 등을,^n간호사가 황급히 눌러 제압한다.",
    191: "간호사",
    192: "안 돼요, 게르다 씨. 얌전히 힘을 빼세요.",
    193: "의사",
    194: "움직이면 안 돼. 움직이면.^n가만히 있으면 금방 끝나니까.",
    195: "게르다",
    196: "빨리…… 빨리, 끝내 줘요……!",
    197: "간호사",
    198: "미안해요. 이 주사기가 워낙 굵기도 하고,^n항문은 억지로 벌리려 하면 아프거든요.^n그래도 생각보다 잘 늘어나니까 괜찮아요. 조금만 참아요.",
    199: "의사",
    200: "좋아, 푹 하고.",
    201: "게르다",
    202: "으응……! 우, 크윽…….",
    203: "간호사",
    204: "자, 약이 듬뿍 들어가고 있어요.^n시간이 조금 걸리지만 참아 주세요.^n약효가 아주 좋은 약이니까요.",
    205: "주사기 안에서 검은 고무가 천천히 앞으로 나아간다.^n극채색 액체가 밀려 나와 게르다의 몸속으로 사라져 간다.^n잔인할 만큼 신중하고 길게.",
    206: "게르다는 이를 악물고 견뎠지만,^n이윽고 견디지 못한 듯 입을 크게 벌리고,^n괴로운 숨을 거듭 내쉬었다.",
    207: "게르다",
    208: "으, 읏…… 후우, 후우, 후웃…….^n하아, 하아, 하아, 하아, 하……!",
    209: "게르다",
    210: "우……읏…… 크……!^n──으, 이제, 그만해……!",
    211: "식은땀을 흘리며 부들부들 떠는 하반신과,^n절망적으로 어두운 게르다의 눈빛이,^n몸속의 차가운 압박감을 호소하는 듯하다.",
    212: "게르다",
    213: "──크윽……!",
    214: "이윽고 내용물을 완전히 토해 낸 주사기가^n불쾌한 소리를 내며 뽑히자,^n게르다의 팔다리가 털썩 무너졌다.",
    215: "간호사",
    216: "──자, 끝났어요.^n잘 참았어요.",
    217: "흘러나온 약을 닦고 속옷을 아무렇게나 올려 주며,^n간호사가 마음에도 없는 위로를 건넨다.",
    218: "게르다는 한마디도 하지 않고,^n자기를 돌보려는 손을 뿌리치듯 진찰대에서 내려와,^n날카로운 발소리를 울리며 모니터 밖으로 사라졌다.",
    219: "문을 거세게 닫는 소리는,^n터질 듯한 게르다의 마음이 지르는 비명 같았다.",
    220: "남겨진 의사와 간호사가 저마다^n적의로 가득한 게르다의 태도를 불평하기 시작했을 때,^n모니터의 전원이 꺼졌다.",
    221: "나",
    222: "………….",
    223: "동시에 나는 정신을 차렸다.^n하얀 방 한가운데 우두커니 서서,^n모니터를 뚫어지게 보던 나 자신을 깨닫는다.",
    224: "나",
    225: "(──뭘 하고 있는 거야, 나)",
    226: "전반은 그렇다 쳐도, 후반은 지켜볼 필요가 없었다.",
    227: "고개만 살짝 돌려도 보지 않을 수 있었다.^n그야말로 처음 생각한 대로 이 방을 나가면 됐다.",
    228: "씁쓸한 것이 가슴속에서 치밀어 오른다.^n그 어두운 죄책감보다, 그것을 중화하듯 솟아난^n또 하나의 감정이 더 불쾌했다.",
    229: "──어쩔 수 없었어.^n──멍하니 있는 사이에 억지로 보게 된 거야.^n──내가 스스로 보러 간 게 아니라 눈앞에 멋대로 나타난 거야.",
    230: "──그런 걸 보여 주면 관심이 없어도 보게 되잖아.^n──남자니까 원래 그렇게 되어 있는 거야.",
    231: "──아무도 모르면 괜찮아.^n──입 다물고 있으면 없었던 일로 만들 수 있어.",
    232: "그걸 보고 만 나보다,^n그런 식으로 자신을 감싸려는 내가 더 추하다고 생각한다.",
    233: "하지만 그렇게 나를 감싸는 내가 없다면,^n도저히 버텨 낼 수 없을 거라는 생각도 들었다.",
    234: "나",
    235: "(아아, 싫다)",
    236: "──나는 이렇게 이 감각에 익숙해지는 걸까.",
    237: "나는 지긋지긋한 기분을 떨쳐 버리듯,^n내 방을 뒤로했다.",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")


def main() -> int:
    rows: dict[int, dict] = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1129.gsc" and item.get("slot") in TARGETS:
                rows[int(item["slot"])] = item
    if set(rows) != set(TARGETS):
        raise SystemExit("catalog mismatch")
    entries = []
    for index in sorted(TARGETS):
        source = str(rows[index]["source_text"])
        target = TARGETS[index]
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entries.append({
            "uid": rows[index]["uid"],
            "source_text": source,
            "source_raw_sha256": rows[index]["source_raw_sha256"],
            "target_text": target,
            "translator": "Codex internal model draft",
            "review_status": "draft_pending_single_review",
            "notes": "초벌 번역; 1차 검수 전",
        })
    output = {
        "schema": "fairytale-requiem-translation-map-v1",
        "scope": "1129_slots_00161_00237_draft",
        "semantic_source": "ja-JP",
        "target_language": "ko-KR",
        "target_encoding": "cp949",
        "translation_method": "Codex internal model only; no external MT/API",
        "review_passes_completed": 0,
        "release_ready": False,
        "entries": entries,
    }
    out = PROJECT / "packets" / "drafts" / "1129_slots_00161_00237_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "output": str(out),
        "entries": len(entries),
        "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper(),
    }, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
