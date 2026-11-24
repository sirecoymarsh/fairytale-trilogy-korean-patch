from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "안내받은 방의 문은 양쪽으로 열렸고,^n왼쪽은 붉은색, 오른쪽은 푸른색으로^n같은 무늬가 서로 다른 색으로 그려져 있었다.",
    2: "나",
    3: "(어쩐지 어디선가 본 것 같은……)",
    4: "그 한쪽에는^nＡｌｉｃｅ^n라고 적힌 팻말이 걸려 있다.",
    5: "문 너머에서 흘러나온 것은 역시나 달고 단 과자 향기.^n누가 봐도 여자아이의 방 같아서^n들어가기가 쑥스러웠다.",
    6: "앨리스는 슬며시 주눅 든 나를 눈치채지 못하고,^n방 안으로 춤추듯 들어가 양팔을 벌리며 돌아섰다.",
    7: "앨리스",
    8: "어서 와요!　자, 사양하지 말고요.",
    9: "조심조심 들어가다가 문득 깨달았다.^n아무래도 이 문은 바깥에서만 잠글 수 있는 모양이다.",
    10: "나",
    11: "……와아.",
    12: "──정말 엉터리인 방이다.^n그것이 내 첫인상이었다.",
    13: "가구는 색이나 분위기는커녕 크기마저 제각각이라,^n가령 의자는 너무 크고 침대는 너무 작다.^n사람과 거인과 난쟁이가 함께 사는 집 같다.",
    14: "그것만으로도 어질어질한데 물건까지 무척 많다.^n장난감 상자를 어질러 놓고 보석함을 뒤엎은 뒤,^n크리스마스 장식으로 마무리한 듯하다.",
    15: "앨리스",
    16: "다행이에요, 시곗바늘이 마침 티타임을 가리키네요.^n뭐, 언제나 그렇지만요.",
    17: "눈이 아프고 마음이 불편한 이 방에도^n앨리스는 무척 잘 어울렸다.^n과연 『이상한 나라의 앨리스』 본인을 자처할 만하다.",
    18: "앨리스",
    19: "자, 이 의자에 앉으세요.^n시계가 티타임만 가리키고 있어서^n준비라면 언제나 되어 있답니다.",
    20: "그렇게 말하며 천장에 박힐 만큼 거대한 의자의^n기둥 같은 다리를 톡톡 두드렸다.",
    21: "나",
    22: "이거, 의자야?^n너무 크잖아.",
    23: "앨리스",
    24: "네, 『너무 큰 의자』인걸요.^n언제나 높은 곳에서 거들먹거리며^n나를 앉지 못하게 해요. 심술궂은 의자예요.",
    25: "올려다보니 좌석 위에는 보통 크기의 탁자가 놓여 있었다.^n하지만 좌석이 너무 높아 뛰어도 손이 닿을 것 같지 않다.",
    26: "나",
    27: "어떻게 앉아야 하지?",
    28: "앨리스",
    29: "이 원피스가 그것 때문에 걸려 있는 거예요.^n차를 마실 때마다 기어오르는 건 조금 불편하지만…….",
    30: "나",
    31: "너, 늘 기어오르는 거야?",
    32: "앨리스",
    33: "네, 그래요. 차는 빠뜨릴 수 없으니까요.^n늘 이렇게 다리를 내던지듯 앉게 돼서^n조금 버릇없어 보이지만 어쩔 수 없어요.",
    34: "나는 의자 등에 걸린 『너무 큰 원피스』 자락을 붙잡고^n씩씩하게 올라가는 앨리스와 나를 상상했다.^n──재미있는 그림이지만 선뜻 내키지는 않는다.",
    35: "나",
    36: "……차는 됐어.^n그러면 둘이 의자 하나에 앉아야 하잖아.",
    37: "앨리스",
    38: "어머……!^n듣고 보니 그렇네요.",
    39: "그래서 결국 내가 자리를 잡은 곳은^n벽에서 자라난 선반버섯 같은 보라색 의자였다.",
    40: "앨리스는 커다란 꽃에 달린^n가짜 아침 이슬을 띄운 잎사귀 하나에^n조그맣게 걸터앉았다.",
    41: "나",
    42: "앨리스, 거기 놓인 건 뭐야?^n봉제 인형용?",
    43: "내가 곧장 화제로 꺼낸 것은 앨리스 발밑에 있는^n발판만 한 크기의 침대였다.",
    44: "앨리스는 『자신이 누군지 모르는 가엾은 나』를 위해^n차를 권해 준 모양이지만,^n지금 신경 쓰이는 것은 이 방의 온갖 물건이다. 누구라도 그럴 것이다.",
    45: "앨리스",
    46: "네, 그건 『너무 작은 침대』예요. 그것도 심술궂죠.^n신발을 신을 때 발을 올려놓기엔 딱 좋지만,^n자려고 하면 내 몸을 크게 만들어 버려요.",
    47: "앨리스",
    48: "　그래서 잘 때는 이쪽을 써요.^n『너무 큰 요람』.^n　여기에는 몸을 줄이면 쏙 들어가요. 딱 좋답니다.",
    49: "앨리스",
    50: "　──저 여행용 가방 말이야?",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1102.gsc" and item.get("slot") in TARGETS:
                rows[int(item["slot"])] = item
    if set(rows) != set(TARGETS):
        raise SystemExit("catalog slot mismatch")
    entries = []
    for index in sorted(TARGETS):
        source, target = str(rows[index]["source_text"]), TARGETS[index]
        if source.count("^n") != target.count("^n"):
            raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": rows[index]["uid"], "source_text": source, "source_raw_sha256": rows[index]["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 한 차례 검수 전"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1102_slots_00001_00050_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1102_slots_00001_00050_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
