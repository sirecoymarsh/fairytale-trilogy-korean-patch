from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
TARGETS = [
    None,
    "의사",
    "응. 열은 없는──것 같은데.^n너, 어쩐지 안색이 좋지 않구나.",
    "나",
    "그런가요?",
    "간호사",
    "그래. 어쩐지 밤을 꼬박 새운 사람 같아.^n어제 잠을 잘 못 잤다든가?",
    "나",
    "그렇지는 않았는데요…….",
    "의사",
    "스트레스일지도 모르겠구나.^n기억이 없고 자신이 누구인지 모른다는 것은^n그 자체만으로 부담이 될 테니.",
    "간호사",
    "뭐, 어찌 되었든 약을 드릴게요.^n아주 달콤한 비스킷이지만 이건 약이니까요.^n너무 많이 먹으면 안 돼요. 자.",
    "나",
    "아, 네, 네…….",
    "묵직한 기름종이 꾸러미를 받아 들자 봉지 밖에서도^n고소하고 달콤한 냄새가 코끝을 간질인다.",
    "이 『낙원』의 약이 얼마나 사치스럽고 꿈으로 가득한지^n나름대로 익히 아는 내 입안이,^n성급하게 고인 침으로 젖는 것을 느꼈다.",
    "나",
    "(아아, 이것도 어차피 맛있겠지)",
    "나",
    "(그건 그렇고,^n 왜 항상 며칠 치를 한꺼번에 주는 걸까)",
    "필요할 때 필요한 만큼──예를 들면^n병원 식사 쟁반과 함께 내주면 좋을 텐데.",
    "적어도 조금은 약답게,^n달지도 맛있지도 않으면 좋을 텐데.",
    "전에 받았을 때는 참고 또 참았지만,^n결국 두 번 먹을 분량의 『약』이 간식이 되고 말았지.",
    "나",
    "(이건 약, 이건 약……)",
    "스스로에게 타이르며^n진찰실 둥근 의자에서 일어서려던──그때.",
    "앨리스",
    "선생님, 선생님!^n제발 도와주세요. 긴급 상황이에요!",
    "노크도 없이 진찰실 문이 열리고,^n눈물에 젖은 앨리스의 목소리가 울려 퍼졌다.",
    "앨리스",
    "제 눈이 망가져 버렸어요!^n선생님이라면 고칠 수 있죠?^n제가 말라붙어 죽지는 않겠죠?",
    "나",
    "앨리스!? 무슨 일이야?",
    "그 필사적인 표정과 목소리는 물론이고,^n그녀의 붉은 뺨이 흠뻑 젖어 있는 것이 신경 쓰여,^n나는 의자에서 엉덩이를 들었다.",
    "눈물로 가득해 녹아 버릴 듯한 앨리스의 붉은 눈과,^n내 시선이 마주친다.",
    "앨리스",
    "아…… 아.",
    "순간 앨리스는 그대로 굳었다.^n놀란 눈빛을 내게 보낸 채 얼어붙어,^n두 눈에서 흐르는 눈물만은 멈추지 않는다.",
    "나",
    "너 또 울고 있는 거야?^n──혹시 그때부터 계속 울고 있었다든가…….",
    "앨리스",
    "아, 아니에요. 아니에요, 이건…… 아니에요.",
    "앨리스는 무언가 말을 망설이며 고개를 돌린다.^n줄무늬 목도리를 눈가에 대고 벅벅 문지르지만,^n저렇게 세게 문지르면 눈꺼풀이 따갑지 않을까.",
    "나",
    "애, 앨리스?",
    "간호사",
    "자, 다음 환자분이 오셨으니,^n너는 네 방으로 돌아가도록 해요.",
    "간호사가 내 시선을 가로막듯 몸을 내밀었다.",
    "간호사",
    "앨리스는 숙녀니까,^n남자아이에게 보여 줄 수 없는 얼굴도 있는 거야.",
    "간호사",
    "너도 말이야, 나나시.^n절대로 보아서는 안 되는 여자아이의 모습이 있는 법이야.",
    "나",
    "(…………)",
    "간호사의 말을 듣자 눈치 없는 내 머리는^n모니터 너머로 두 번이나 본 라푼젤의 모습을^n떠올리고 만다.",
    "순간 숨이 답답해지고 뺨이 불타듯 붉어진다.",
    "──아아, 그렇구나. 확실히 이것은,^n여자아이에게 절대 보이고 싶지 않은 얼굴이다.",
    "그렇게 생각하니 앨리스의 수상한 행동을 전부 용서할 수 있을 듯해,^n나는 순순히 진찰실을 나가기로 했다.",
    "나",
    "………….",
    "나",
    "…………………….",
    "그대로 평소처럼 떠나려던 순간,^n나는 발길을 돌려 문 앞으로 돌아왔다.",
    "앨리스",
    "있잖아요, 있잖아요. 눈물이 멈추지 않아요.^n멈추어도 잠시 지나면 또 무언가 북받쳐 올라,^n여기서 홍수가 되어 넘쳐 버려요.",
    "간호사",
    "진정해, 앨리스. 괜찮아.",
    "문은 그리 두껍지 않고 주변은 조용해서,^n앨리스의 목소리가 잘 울린다.",
    "문에 살며시 몸을 기울이기만 해도,^n앨리스와 두 사람의 대화가 잘 들렸다.",
    "나",
    "(괜찮아, 들키지 않아.^n 저쪽은 막다른 길이고 이쪽에서 오면 금세 알 수 있어)",
    "이제는 변명할 여지조차 없을 만큼,^n훌륭하고 모범적이며 그림으로 그린 듯한 엿듣기다.",
    "앨리스",
    "저는요, 전에 제 눈물로 생긴 연못에 빠진 적이 있는데요,^n그때보다 훨씬 심한 수량과 수압이에요.",
    "앨리스",
    "제 몸이 그때와 달리 작지 않아서 다행이에요.^n자기 눈물로 생긴 연못에서 헤엄치는 경험은 한 번이면 충분하고,^n무엇보다 이 기세라면 연못은커녕 폭풍 치는 바다예요.",
    "의사",
    "흐음.^n처음 눈물을 흘리게 된 계기는 무엇이었니?",
    "앨리스",
    "그러니까요, 나무에 올라갔다가 떨어져서──",
    "의사",
    "뭐라고!? 다친 곳은?",
    "앨리스",
    "받아 주신 덕분에 괜찮았어요.^n『고양이 없는 웃음』을 놓친 건^n아주 큰 타격이었지만요…….",
    "앨리스의 이야기는 본론과 먼 곳에서 시작해,^n이곳저곳으로 샛길을 들렀다.",
    "게다가 이야기 도중마다 앨리스가 흐느껴 울어 그때마다 말이 멈춘다.^n모든 사정을 아는 나로서는^n답답하기 짝이 없다.",
    "긴장감 넘치던 엿듣기가^n완전히 따분하고 늘어지는 일로 바뀔 즈음,^n앨리스는 마침내 자초지종을 다 이야기했다.",
    "의사",
    "──미스미, 정리해 줄래?",
    "간호사",
    "저 나나시와 『가족』에 관해 이야기하던 중,^n자세한 일을 떠올릴 수 없었다.^n떠올리려 하자 눈물이 멈추지 않게 되었다.",
    "앨리스",
    "맞아요, 그런 일이에요. 제발 어떻게든 해 주세요, 선생님.^n저 죽지는 않겠죠?^n이대로 눈이 쪼그라들지는 않겠죠?",
    "앨리스는 훌쩍훌쩍 코를 들이마시며 호소한다.",
    "간호사",
    "들이마시면 안 돼요, 여자아이잖아.^n자, 흥 해요.",
    "주르륵, 하고 품위 없는 소리가 한숨 잦아든 뒤,^n의사 선생님의 온화한 목소리가 들렸다.",
    "의사",
    "……뭐, 자연히 멈출 테니 괜찮아.^n당분간 『가족』에 관해서는 생각하지 말고,^n영양가 있는 것을 많이 먹으며 푹 자도록 해.",
    "앨리스",
    "저는 무슨 병에 걸린 건가요?^n성홍열? 흑사병? 폐결핵?",
    "의사",
    "가벼운 감기야.^n그래, 약을 내줄게.^n미스미, 레인보 드롭스를 줘.",
    "간호사",
    "네.",
    "의사",
    "증상이 괴로우면 우선 바로 한 알.^n그다음부터는 식후에 한 알씩 먹도록 해.",
    "의사",
    "그래, 먹으면 졸릴 테니,^n잠들면 곤란한 곳에서는 먹지 말아야 해.",
    "앨리스",
    "네에.^n",
    "──와아, 예쁜 드롭스네요.",
    "간호사",
    "앨리스는 언제나 있는 만큼 전부 먹어 버리잖아.^n이건 사흘 치니까 꼭 사흘에 걸쳐 복용해야 해요.",
    "앨리스",
    "제가 참지 못하는 게 아니에요.^n약 쪽에서 『나를 먹어 줘』라고 말하며,^n일제히 제 입안으로 뛰어드는 거예요…….",
    "간호사",
    "어머, 앨리스도 참. 어쩔 수 없네.",
    "진찰을 마친 앨리스와^n마주쳐서는 절대로 안 되기에,^n나는 그쯤에서 조용히 물러나기로 했다.",
    "나",
    "(──나도 다음에는 저런 변명을 해 볼까)",
    "간호사가^n고양이와 장난치듯 즐겁게 웃는 목소리를 들으며,^n그런 생각을 마음에 품은 채.",
]


def main() -> int:
    expected = set(range(1, 123))
    if len(TARGETS) != 123:
        raise SystemExit(f"target count mismatch: {len(TARGETS)-1}")
    rows, lookup = {}, set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1210.gsc":
                continue
            slot = int(item["slot"])
            if slot in expected:
                rows[slot] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(slot)
    if set(rows) != expected or lookup != set(range(123, 181)):
        raise SystemExit("visible or lookup coverage mismatch")
    entries = []
    for slot in sorted(expected):
        row, target = rows[slot], str(TARGETS[slot])
        source = str(row["source_text"])
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {slot}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": row["uid"], "source_text": source, "source_raw_sha256": row["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 대기"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1210_slots_00001_00122_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1210_slots_00001_00122_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "entries": len(entries), "lookup_slots_preserved": [123, 180], "output": str(out), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
