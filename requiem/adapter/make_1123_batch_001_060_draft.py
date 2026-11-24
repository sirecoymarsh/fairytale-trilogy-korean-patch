from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "나",
    2: "(──어라.)",
    3: "낯선 것을 보고 나는 걸음을 멈췄다.",
    4: "털이 조금 흐트러진 검은 고양이였다.^n하품 같은 울음소리를 남기고 긴 꼬리를 살랑살랑 흔들며,^n복도 저편으로 달려가 버린다.",
    5: "나",
    6: "(방금 앨리스의 방에서 나온 것처럼 보였는데.)",
    7: "마침 들를 생각이던 참이다.^n그쪽으로 향하자 아니나 다를까 좌우 문이 어중간하게 열려,^n고양이 한 마리가 빠져나갈 만한 틈이 생겨 있었다.",
    8: "다음 순간 그 틈을 단숨에 밀어 열며^n앨리스가 뛰쳐나왔다.",
    9: "앨리스",
    10: "잠깐…… 어라? 어라아!?^n어디로 간 거예요. 아직 차 마실 시간이잖아요?",
    11: "앨리스",
    12: "──어머. 미안해요.",
    13: "간신히 문에 정면으로 부딪히는 것을 피한 내게^n앨리스는 어딘가 정신이 팔린 듯 사과한다.",
    14: "앨리스",
    15: "그게, 조금 서두르고 있었거든요.^n당신, 모자 장수를 보지 못했나요?^n바로 방금 나간 것 같은데요.",
    16: "앨리스",
    17: "정말이지, 언제나 차 마실 시간이라고^n늘 신이 나 떠드는 건 그 사람인데…….",
    18: "나",
    19: "모, 모자 장수……는 못 본 것 같아.^n고양이라면 지나갔지만…….",
    20: "앨리스",
    21: "고양이…….",
    22: "앨리스는 진지한 얼굴로 무언가 생각에 잠긴 듯했지만,^n이윽고 방 안으로 되돌아갔다.",
    23: "사각사각 펜을 놀리는 듯한 소리가 들려온다.",
    24: "나",
    25: "앨리스? 들어가도 돼?",
    26: "앨리스",
    27: "네, 들어오세요.^n다만 난 지금 조금 바빠요.^n아무 대접도 못 해 드리겠지만요.",
    28: "나",
    29: "그건 괜찮은데…….^n뭘 쓰고 있어?",
    30: "　앨리스는 버섯 모양 서랍장을 의자 대신 삼아^n(아마 『너무 큰 의자』를 쓸 수 없어서)^n　글 쓰는 책상에 바싹 붙어 있었다.",
    31: "앨리스",
    32: "문제예요. 수식이라고 해도 될까요.",
    33: "나",
    34: "문제? 수식?",
    35: "그 손가를 들여다보니 책상 위에는^n메모지와 공책 조각, 전단지 뒷면 같은 것들이^n뿌려 놓은 듯 어지럽게 겹쳐 있었다.",
    36: "크기와 재질도 제각각인 종이들이 서로를 가리고 있는^n두서없는 참상을 한 장의 캔버스 삼아,^n앨리스는 손에 든 깃펜을 종횡무진 휘두르고 있었다.",
    37: "잉크도 마르지 않은 가장 새로운 메모에 따르면.",
    38: "고양이＝모자 장수?^n고양이＋모자＝모자 고양이^n모자 고양이＝모자 장수",
    39: "앨리스",
    40: "……분명 고양이는 모자 장수가 아니에요.",
    41: "앨리스는 진지한 얼굴로 이쪽을 돌아본다.",
    42: "나",
    43: "응…… 그렇지.",
    44: "나는 무덤덤하게 고개를 끄덕일 수밖에 없다.",
    45: "앨리스",
    46: "──있잖아요. 예전에 모자 장수가 낸 문제가 있었는데,^n내가 마침내 풀어냈어요.^n머릿속에서 민트 사이다가 터진 듯한 번뜩임이었죠.",
    47: "나",
    48: "그, 그래.",
    49: "앨리스",
    50: "그래서 모처럼이니 답을 보여 주려고^n내 『엉망진창 다과회』에 초대했는데…….",
    51: "나",
    52: "엉망진창 다과회……?",
    53: "대접하려는 마음이 한 조각도 없을 듯한 모임이다.",
    54: "앨리스",
    55: "모자 장수는 계속 잠만 자는 거예요.^n차도 안 마시고 과자도 안 먹고.^n입에 댄 건 참치 키슈 정도였던가요.",
    56: "앨리스",
    57: "　내가 답을 선보여도 흐느적거리며 하품만 하고.^n『내가 그런 문제를 냈던가?』 하는 얼굴로 이쪽을 봐요.^n　내 고생은 대체 뭐였을까요?",
    58: "앨리스",
    59: "급기야 갑자기 달려 나가더니^n방을 뛰쳐나가 버렸고…….",
    60: "나",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1123.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1123_slots_00001_00060_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1123_slots_00001_00060_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
