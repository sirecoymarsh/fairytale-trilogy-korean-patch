from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    211: "글쎄, 모르겠구나.^n본원은 네 분실물에 관여하지 않으며,^n요컨대 어떠한 책임도 지지 않는다.",
    212: "나",
    213: "그런가요…….",
    214: "의사",
    215: "그건 그렇고, 이야, 난감하군.^n이런 일이 있을 수 있나.",
    216: "의사",
    217: "동화 증후군이 발병했었는데,^n기억 상실로 깨끗이 사라졌다.",
    218: "의사",
    219: "아니, 사라졌다는 건 성급한 판단인가.^n잊어버려서 일시적으로 가라앉았을 뿐인지도──",
    220: "이윽고 의사 선생님은 탁 하고 자기 머리를 두드렸다.^n굉장히 좋은 소리가 났다.",
    221: "의사",
    222: "아, 그래.^n──자네, 그걸 가져와.",
    223: "눈짓하자 간호사 선생님이 선반에 늘어선 물건 중,^n커다란 병을 골라 이쪽으로 가져왔다.",
    224: "의사",
    225: "……이게 무엇으로 보이니?",
    226: "나는 보이는 그대로 대답했다.^n탁한 색의 물 너머에서,^n빛을 잃은 검은 눈이 이쪽을 보고 있다.",
    227: "나",
    228: "초록색 액체에 잠긴 곰 인형……이요.",
    229: "각도가 바뀌자 테디베어의 한쪽 눈이 떨어지려 하고,^n풀린 실과 단추가 떠오른 것이 보였다.^n──왜 인형에게 이런 짓을 하는 걸까?",
    230: "의사",
    231: "그렇구나…… 그렇게 보이는구나.^n그렇다면 너는 아직 동화 증후군에서 벗어나지 못한 모양이야.",
    232: "내 대답에 의사 선생님은 아쉽다는 듯 한숨을 쉬었다.^n간호사 선생님도 왠지 슬픈 얼굴로 커다란 병을 치웠다.",
    233: "나는 사물을 정상적으로 보지 못한다는 뜻일까.^n그렇다면 역시 내 머리 상태가 좋지 않은 것이다.",
    234: "나",
    235: "(그나저나 방금 그 병 안에 든 건 실제로 무엇이었을까.)",
    236: "의사",
    237: "음, 골치 아프군.^n머릿속이 새하얘졌으니,^n동화 증후군도 나았다는 기적은 일어나지 않았나.",
    238: "의사",
    239: "결국 어떤 계기로 기억이 돌아왔을 때,^n위험한 증상이 나타나면 우리 책임이 되고.^n다른 병원으로 옮길 수도 없나. 안 되겠지.",
    240: "의사 선생님은 혼잣말처럼 중얼거리며,^n미간을 문지른 채 고민하고 있다.",
    241: "나는 점차 왠지 미안한 기분이 들었다.^n어른이 아이 앞에서 이렇게까지 허둥대다니,^n상당히 몰린 것이 틀림없다.",
    242: "분명 어른에게는^n몸 상태나 계산, 시계바늘이 어긋나는 일이,^n하나하나 슬프고 돌이킬 수 없는 일이었던 것 같다.",
    243: "의사",
    244: "뭐, 이렇게 됐으니 어쩔 수 없지. 이미 시작한 일이야.^n당분간은 메디컬 초콜릿과 컬러풀 케이크를 처방하며^n상태를 지켜볼까…… 그래.",
    245: "하지만 이윽고 의사 선생님은 고개를 끄덕였다.^n슥슥 차트에 무언가를 적으면서,",
    246: "의사",
    247: "아무튼 너는 이곳에 있으렴.^n이제 가 봐도 좋아.",
    248: "의사",
    249: "아, 약도 처방할게요.",
    250: "나",
    251: "(약!)",
    252: "듣기만 해도 입안이 쓰게 느껴졌다.^n의자에서 뜨려던 엉덩이가 툭 하고 되돌아간다.",
    253: "분명 약은 그런 것이다.^n싫다, 정말 싫지만,^n마지막에는 반드시 먹어야만 하는 것.",
    254: "──왜 나는 약에 관해서는 기억하는 걸까.^n약 같은 건,^n잊어버린 편이 분명 행복했을 텐데!",
    255: "입안에 느껴지는 환상의 쓴맛을 씻으려 침이 서서히 고인다.^n나는 미지근하고 불쾌한 그것을 꿀꺽 삼키고,^n진찰실을 뒤로했다.",
    256: "──그런데.",
    257: "나",
    258: "어라……?",
    259: "내 방으로 돌아가는 길에,^n받은 종이봉투 속을 조심스레 들여다본 나는^n고개를 갸웃하게 되었다.",
    260: "한쪽은 투명한 플라스틱으로,^n약 모양을 따라 부풀어 있고,^n반대쪽 은박을 찢어 꺼내는 형태의 약.",
    261: "나",
    262: "(이거…… 이런 모양의 초콜릿이 있었지?)",
    263: "『초콜릿처럼 먹기 편한 약입니다』^n　은색 판에도 그런 글씨가 보인다.",
    264: "나",
    265: "………….",
    266: "주변을 둘러보고 아무도 없는 것을 확인한 뒤.",
    267: "나",
    268: "………….",
    269: "한 알만 입에 넣고 씹어 보니,^n분명 초콜릿 그 자체였다.",
    270: "나",
    271: "(──역시 낙원이야!)",
    272: "어디가 『낙원』인지는 전혀 모르겠지만,^n이 약에 관해서만큼은 틀림없이 낙원이다.",
    273: "나는 그런 생각을 하며 내 방으로 돌아갔다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1107.gsc" and item.get("slot") in TARGETS:
                rows[int(item["slot"])] = item
    if set(rows) != set(TARGETS):
        raise SystemExit("catalog mismatch")
    entries = []
    for index in sorted(TARGETS):
        source, target = str(rows[index]["source_text"]), TARGETS[index]
        if source.count("^n") != target.count("^n"):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": rows[index]["uid"], "source_text": source, "source_raw_sha256": rows[index]["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 전"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1107_slots_00211_00273_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1107_slots_00211_00273_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
