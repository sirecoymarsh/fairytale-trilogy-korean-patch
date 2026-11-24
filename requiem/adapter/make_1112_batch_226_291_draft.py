from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    226: "오데트",
    227: "모두 멋진 이야기네.^n지금의 『낙원』에는 거기서 뛰쳐나온^n앨리스 씨들이 있어요.",
    228: "나",
    229: "──응, 모두 만났어.",
    230: "오데트",
    231: "그래요!　모두 귀엽고 멋지죠.^n저는 지금도 만날 때마다 두근거려요.^n그 이야기 속 그 사람이구나 하고.",
    232: "　나 자신도 환자라 할 말은 아니지만,^n　자칭 『동화 속 등장인물』이 동화를 읽고 동경하며,^n『본인』끼리 만난다는 건 어딘가 초현실적으로 느껴진다.",
    233: "나",
    234: "오데트도 그렇지……?",
    235: "오데트",
    236: "으…… 응.",
    237: "어째서인지 오데트는 말끝을 흐리며 고개를 끄덕였다.^n말투를 고쳐 화제를 돌린다.",
    238: "오데트",
    239: "저기, 왕자님은 어떤 이야기를 좋아하세요?^n저는 아직 읽지 않은 책이 아주 많아요.",
    240: "나",
    241: "뭐?　그러니까…… 글쎄.",
    242: "그렇게 고민할 필요도 없이,^n머릿속에 문득 떠오른 것이 있다.",
    243: "나",
    244: "아, 맞다.^n피터 팬을 좋아하는 것 같아.",
    245: "오데트",
    246: "피터 팬!^n저는 아직 읽지 않았어요.^n언제나 집었다가 돌려놔요. 무서워 보여서…….",
    247: "나",
    248: "뭐, 무섭지 않아.",
    249: "오데트",
    250: "정말요?　무섭지 않아요?^n──그렇다면 읽어 볼까.",
    251: "고민하는 오데트 곁에서,^n나도 속으로 고개를 갸웃하고 있었다.",
    252: "　아무 망설임 없이 툭 튀어나온^n『피터 팬』이라는 대답.^n　내 본래 『성서』가 그것이었을까.",
    253: "　하지만 생각하면 생각할수록^n『나답지 않다』는 느낌도 든다.",
    254: "장난꾸러기에 난폭하고 외로움을 타는 영원한 소년.^n──연기하려면 피곤할 것 같다.^n그렇다면 그저 좋아했을 뿐일까.",
    255: "오데트",
    256: "……왕자님?^n지크프리트 님, 무슨 일 있으세요?",
    257: "오데트가 말을 걸어 퍼뜩 정신을 차렸다.",
    258: "그랬다.^n지금의 내게는 『지크프리트』라는 역할이 있다.",
    259: "아무것도 아니라고 고개를 저으며^n나는 마음에 그 이름을 새기듯 자신에게 되뇌었다.",
    260: "나",
    261: "그게…… 모르겠어.",
    262: "나",
    263: "내게는 모든 기억이 없어.^n내 이름이 무엇이고 어떤 사람이었는지.^n아무것도 몰라.",
    264: "나는 결국 솔직하게 대답하기로 했다.",
    265: "말을 이으면 이을수록 그러길 잘했다고 느낀다.^n오데트를 구하고 싶은 마음이 진짜라 해도,^n아무것도 기억나지 않는데 그런 이름을 대는 것은 무책임하지 않을까.",
    266: "오데트",
    267: "네……!",
    268: "오데트는 충격을 받은 듯,^n금빛 머리카락을 물결치며 나를 보았다.",
    269: "나",
    270: "『성서』도──있었겠지만 찾지 못했어.^n　그, 어디선가 보면 알려 줘.",
    271: "오데트",
    272: "네, 네. 그건 물론이죠.^n하지만 큰일이네요. 기억이 없다니…….^n그저 백조가 되는 저보다 훨씬 힘들 것 같아요.",
    273: "나",
    274: "그, 그런가?",
    275: "오데트",
    276: "그래요, 네. ──역시 그래요.^n조금 상상하기만 해도 무섭고 괴로워서,^n어떻게 해야 할지 모르게 되는걸요.",
    277: "잠시 눈을 감고 『기억이 없는』 상태를 상상한 듯한^n오데트는 불안한 듯 눈살을 찌푸리며 나를 본다.",
    278: "나",
    279: "　그럴까. 그렇게 무섭거나 괴롭지는 않아.^n『없는 것』이 당연하면 『있는 것』의 고마움을^n　잘 모르는 걸지도 몰라.",
    280: "오데트",
    281: "──당신은 강하군요. 대단해요.",
    282: "오데트",
    283: "분명 괜찮을 거예요.^n잊은 것은 지금뿐이고 언젠가 떠올릴 수 있어요.",
    284: "오데트",
    285: "당신을 기억하는 사람이 있을지도 모르고,^n잃어버린 『성서』가 발견될지도 모르고.^n저도 찾아볼게요. 노력할게요.",
    286: "나",
    287: "──고마워.",
    288: "필사적으로 말을 고르는 것이 전해져,^n나는 그 마음이 기뻤다.",
    289: "동시에 이토록 나를 걱정해 주는^n그녀 자신의 행복을 생각하니 마음이 무거워졌다.",
    290: "이 『낙원』의 어른들, 의사와 간호사 선생님들이^n하루빨리 오데트의 병을 고쳐 주면 좋겠다.",
    291: "그렇게 바라며 나는 오데트와 함께^n짙은 구름에 갇혀 가는 보름달을 바라보았다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1112.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1112_slots_00226_00291_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1112_slots_00226_00291_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
