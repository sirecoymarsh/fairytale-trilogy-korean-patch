from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    141: "(앨리스와 오딜도 그런 말을 했지.^n　자신의 이야기가 적혀 있고,^n　자신에 관해 알고 싶으면 그걸 보면 된다고.)",
    142: "의사",
    143: "뭐, 옆에서 보면 우습긴 하지만.^n결국 놀이에 불과하니까.^n덧없는 꿈이라는 거지.",
    144: "그때는 자신에 대해 모든 것을 아는 그 아이들이^n부럽다고 생각했지만──",
    145: "의사 선생님의 이런 말투를 보니,^n그렇게 좋은 일만은 아니었는지도 모른다.",
    146: "의사",
    147: "그러니 너도 그 아이들이 하는 말을 듣고,^n이상하다거나 괴상하다거나 그럴 리 없다는 말을^n해서는 안 돼.",
    148: "의사",
    149: "심술을 부려서 성서를 억지로 빼앗는 것도^n물론 안 된단다. 분명 갑자기 머리가 뜯겨 나간 것과^n똑같은 기분이 들 테니까.",
    150: "내 눈을 들여다보며 의사 선생님은 말했다.^n부드러운 말투지만 실수하지 않도록^n머릿속 깊이 새겨 넣어야 한다는 의지가 느껴진다.",
    151: "하지만 나는 네, 하고 건성으로 대답했다.^n애초에 그다지 재미있는 일이라고 생각하지도 않았으니까.",
    152: "의사",
    153: "너도 실수로 인형 머리를 뽑아 버리고,^n몹시 미안해진 적이 있지 않니?",
    154: "나",
    155: "(어땠더라.^n　있었던 것 같기도, 아닌 것 같기도.)",
    156: "──그래도 그런 일이 생긴 뒤,^n빠진 머리 끝에 달린 인형의 눈이 빤히 바라본다면,^n분명 어색할 것이다.",
    157: "그렇게 생각한 나는 이번에는 의사 선생님의 눈을 똑바로 보며^n네, 하고 고개를 끄덕였다.",
    158: "의사",
    159: "좋아.",
    160: "의사",
    161: "자, 이제 네 이야기다.^n너는 이곳에 막 왔으니,^n아저씨는 너에 대해 아무것도 몰라.",
    162: "의사",
    163: "뭐, 조금은 알지만,^n우선 네 이야기를 들어 보자꾸나.",
    164: "의사",
    165: "너, 너는 누구니. 누구라고 생각하는 거지?^n어떤 이야기의──어라.",
    166: "의사",
    167: "너, 『성서』를 가지고 있지 않구나?",
    168: "나",
    169: "아…….",
    170: "텅 빈 내 두 손을 보며 의사 선생님은 고개를 갸웃했다.",
    171: "아, 그러고 보니 그랬다.^n나 자신도 거의 잊고 있던 일이지만──",
    172: "나",
    173: "사실은, 그게…….",
    174: "나는 그제야 이름도 과거도 잃어버린^n내 불행에 관해 이야기할 수 있었다.^n사실 가장 먼저 말했어야 했다고 뒤늦게 깨달으면서.",
    175: "의사",
    176: "뭐라고!　기억이 없어!?^n너, 그게 정말이니?",
    177: "의사 선생님은 소리친 뒤 말문이 막힌 채 나를 바라보았다.^n눈을 휘둥그레 뜨고 입을 떡 벌린 모습이,^n나무로 깎은 민속 인형 같다.",
    178: "나",
    179: "………….",
    180: "이렇게까지 놀란다는 건 굉장히 드문 일인 모양이다.^n저 선반에 빼곡한 어려워 보이는 책을 아무리 찾아도,^n나오지 않는 일인지도 모른다.",
    181: "의사 선생님의 경악한 얼굴을 보며 그런 생각을 하니,^n나는 상황에 맞지 않게 유쾌한 기분이 들고 말았다.^n서둘러 느슨해지려는 입술을 다잡았다.",
    182: "웃는 건 실례다.^n아마 나는 심각한 상황에 놓였고,^n의사 선생님은 나를 위해 놀라고 걱정해 주고 있는데.",
    183: "의사",
    184: "이거 난감하군…… 음.^n우선 이것저것 이야기해 주렴.",
    185: "그 뒤로 나는 어디서부터 기억이 없는지,^n짐작 가는 것은 없는지 여러 가지 질문을 받았다.",
    186: "하지만 그때까지 이미 머릿속을 샅샅이 뒤진 나다.^n다시 시도한들 결과가 달라지지 않는다.",
    187: "애가 탄 의사 선생님은,^n방구석에서 먼지를 뒤집어쓰고 있던 전신거울을 가져오게 해,^n거기에 내 모습을 비추었다.",
    188: "의사",
    189: "이게 너란다. 거울을 볼 때마다 만났을 테지?",
    190: "의사",
    191: "자, 말을 걸어 보렴.^n늘 하던 것처럼 자연스럽게 자신에게 좋은 아침이라고.^n그러면 무언가 떠오를지도…….",
    192: "의사 선생님의 말이 흐릿하게 끊긴다.",
    193: "나",
    194: "(나, 이렇게 생겼구나!)",
    195: "그런 생각을 훤히 드러낸 채,^n거울 속 자신을 뚫어져라 바라보는 나를 보고,^n소용없다는 것을 알아챈 모양이다.",
    196: "의사",
    197: "──역시 떠오르지 않니?",
    198: "나",
    199: "죄송해요…….",
    200: "의사",
    201: "괜찮아, 괜찮아.^n사과할 것 없단다.",
    202: "그 뒤 손에 든 차트에^n무언가를 벅벅 적던 의사 선생님은 이윽고,^n하아, 하고 크게 한숨을 내쉬며 머리를 감쌌다.",
    203: "의사",
    204: "『가짜인 너』에 대해서도 기억나지 않니?^n　그러니까 너는 동화 증후군을 앓고 있었으니,^n　자신을 『누군가』라고 믿었을 텐데.",
    205: "나",
    206: "모르겠어요.^n본래의 나조차 떠오르지 않는데,^n본래가 아닌 나 같은 건…….",
    207: "그래, 그래, 하고 의사 선생님은 다정하게 맞장구를 친다.",
    208: "나",
    209: "맞다, 그──내 『성서』가 있다면 적어도^n가짜인 내가 누구인지는 알 수 있겠죠.^n제 『성서』가 어딘가에 떨어져 있지는 않았나요?",
    210: "의사",
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1107_slots_00141_00210_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1107_slots_00141_00210_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
