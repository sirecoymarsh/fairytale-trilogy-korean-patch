from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
TARGETS = [
    None,
    "앨리스",
    "어머, 어머어머어머.^n바로 어제 그러고서 벌써, 세상에…….",
    "가려진 시야 너머로 앨리스의 당황한 목소리가 들린다.",
    "어젯밤 앨리스가 내 방에 찾아왔을 때를 그대로 재현한 모습이다.^n나는 일어나자마자 헝클어진 머리를 대충 누르기만 하고^n바구니를 안아 앨리스의 방으로 찾아왔다.",
    "이곳 직원에게 도움을 받을까도 생각했지만,^n나 혼자 옮기기로 한 것은 앨리스가 느꼈던 무게를^n나도 느껴 보려는 나름의 책임감이었다.",
    "앨리스",
    "어서 오세요.^n빨리 들어오세요.",
    "앨리스는 바구니를 받으려 손을 댔지만,^n나는 건네지 않고 조심조심 방으로 들어갔다.",
    "방 중앙의 빈 곳에 살며시 바구니를 내려놓는다.",
    "뒤돌아보니 앨리스가 조용히 미소 짓고 있었다.^n아주 조금 평소보다 어른스러워 보인다.",
    "앨리스",
    "……이렇게 될 것 같았어요.",
    "앨리스",
    "왜냐하면 조금 전까지 작아진 당신이^n이 바구니 안에 길을 잃고 들어가서,^n끔찍한 일을 겪는 꿈을 꾸었거든요.",
    "어떻게 말을 꺼내야 할지 한참 망설였지만,^n앨리스는 쓴웃음 한 번으로 끝내 줄 모양이다.",
    "꿈은 앨리스의 무의식이 투영된 것일까.^n그렇다면 제법 정확하게 내 본심을 꿰뚫어 본 셈이다.",
    "앨리스는 바구니 속 물건을 꺼내^n하나씩 바닥에 늘어놓는다.",
    "당연히 방은 어질러지지만,^n정리 과정의 하나인 걸까.",
    "왠지 모르게 그 작업을 도우며,^n나는 미리 준비한 사과를 입에 담았다.",
    "나",
    "……미안해, 역시 그…….^n아무것도 없는 편이 마음이 편해, 나는.",
    "앨리스",
    "그렇군요. 물론 그래도 괜찮아요.^n당신은 흰색을 좋아하는 거네요.",
    "나",
    "흰색을 좋아한다……기보다.",
    "나는 말끝을 흐렸다.",
    "나는 아마 흰색이라는 색을 좋아하는 게 아니다.^n아무것도 없는 하얀 방이 좋은 게 아니라,^n무언가가 있는 색깔 있는 방이 내게 맞지 않을 뿐.",
    "하지만 그 말을 그대로 앨리스에게 전할 생각은 들지 않았다.",
    "나",
    "……응. 벽도 천장도 흰색 그대로면 좋다고 생각해.^n나중에 마음이 변할지도 모르지만 적어도 지금은.",
    "앨리스",
    "어머나, 세상에. 흰색을 그렇게 좋아하신다니!^n네, 그렇게나 좋아하시는데 물들이려 하다니,^n제가 정말 실례했어요.",
    "앨리스",
    "저는 아직 멀었군요.^n아직 흰색의 매력을 모르겠어요.^n더욱 정진해야겠어요.",
    "앨리스는 고민스러운 듯 한숨을 쉰다.^n그 진지한 표정이 재미있어 나는 하마터면 웃음을 터뜨릴 뻔했다.",
    "나",
    "그렇게 대단한 일은 아니야.",
    "앨리스",
    "아니에요! 대단한 일이에요.^n부끄럽지만 저는 흰색이 색이 아니라고 생각했어요.^n빨강에서 빨강을, 파랑에서 파랑을 뺀 색, 그것이 흰색이라고…….",
    "앨리스",
    "하지만 그 뺄셈은 틀렸어요.^n왜냐하면 공기는 하얗지 않으니까요.^n그것은 『무』라는 색이에요.",
    "앨리스",
    "그러니까 흰색은 흰색이라는 색인 거예요!",
    "열변을 토하며 앨리스는 무의식중에 힘을 준 모양이다.^n마침 손에 쥐고 있던 오리 장난감이 삑 하고 울었다.",
    "나",
    "으, 응.",
    "내 건성 대답에도 아랑곳하지 않고,^n앨리스는 오리를 내려놓으며 몸을 내민다.",
    "앨리스",
    "있잖아요, 제가 흰색을 만지고 싶어지면,^n또 찾아와도 될까요?",
    "나",
    "그…… 그건 물론이지.",
    "순간 어젯밤 앨리스와 함께 보고 만^n모니터 속 광경이 머릿속을 스쳤다.",
    "앨리스는 새까맣게 탄 시체를 잊었듯이^n그 일도 잊은 걸까.",
    "나",
    "(어느 쪽이든 의식해서 어색해지는 것보다는 낫겠지)",
    "나",
    "나도 가끔 이 방에 놀러 와도 될까?",
    "안도하며 묻자 앨리스는 활짝 웃으며 고개를 끄덕였다.",
    "앨리스",
    "네, 물론이죠!",
    "나",
    "………….",
    "빈말로 한 소리는 아니었다.",
    "내 방을 바꿀 생각은 없었지만,^n앨리스의 알록달록한 방에 찾아와^n빼곡하게 놓인 보물들을 바라보는 것은 제법 즐거우니까.",
    "앨리스가 『흰색의 매력』을 이해하려 하듯,^n나도 『흰색이 아닌 것들의 매력』을 알고 싶은 걸까?",
    "여전히 바닥이 보이지 않는 바구니를 뒤적이며,^n그런 생각을 했다.",
]


def main() -> int:
    expected = set(range(1, 67))
    if len(TARGETS) != 67:
        raise SystemExit("target count mismatch")
    rows, lookup = {}, set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1206.gsc":
                continue
            slot = int(item["slot"])
            if slot in expected:
                rows[slot] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(slot)
    if set(rows) != expected or lookup != set(range(67, 125)):
        raise SystemExit("visible or lookup coverage mismatch")
    entries = []
    for slot in sorted(expected):
        row, target = rows[slot], str(TARGETS[slot])
        source = str(row["source_text"])
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {slot}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": row["uid"], "source_text": source, "source_raw_sha256": row["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 대기"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1206_slots_00001_00066_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1206_slots_00001_00066_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "entries": len(entries), "lookup_slots_preserved": [67, 124], "output": str(out), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
