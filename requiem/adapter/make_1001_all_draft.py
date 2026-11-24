from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
TARGETS = [
    None,
    "라푼젤 동작 테스트.",
    "컷인 연출 확인.",
    "막상 그렇게 되고 보니, 역시 그녀의 어깨와 팔은 부드럽고 유연해서,^n내가 몹시 난폭한 짓을 한 듯한 기분이 들어 손을 놓았다.",
    "한때 불쑥 덮친 충동의 폭풍이었는지,^n그녀는 더 이상 캔버스를 어찌할 생각은 없어 보였다.",
    "라푼젤 컷인 배치 테스트 종료.",
    "루트 점프 화면 연출 테스트",
    "──아직 나는 여기 있구나.",
    "라푼젤",
    "１２３４５６７８９０１２３４５６７８９０１２３４５６７８９０。^n１２３４５６７８９０１２３４５６７８９０１２３４５６７８９０！^n１２３４５６７８９０１２３４５６７８９０１２３４５６７８９０』",
    "|１２[루비]３４５６７８９０１２３４５６７８９０１２３４５６７８９０。^n１２３４５６７８９０１２３４５６７８９０１２３４５６７８９０！^n１２|３４[루비]５６７８９０１２３４５６７８９０１２３４５６７８|９０[루비]』",
    "난롯불이 일렁이는 어두운 실내에서,^n여러 개의 그림자가 소녀를 둘러싸고 있었다.",
    "남자들은 게르다에게 정액을 뿜었다.^n온천물에 몸을 담근 듯 충족된 한숨을 내쉬기도 하고,^n혹은 딸꾹질 같은 우스꽝스러운 소리를 내며 목을 울리기도 하면서.",
    "──부탁이야, 그만 울어.^n──있지. 단것 좋아하지?",
    "──고마워, 오빠.",
    "나",
    "(──? 또……)",
    "한 세트 종료.",
    "주인공 임베드＋히로인 스탠딩 CG 소형.",
    "앨리스 임베드＋주인공 바스트업 소형.",
    "그레텔 임베드＋주인공 바스트업 소형.",
    "오데트 임베드＋주인공 바스트업 소형.",
    "오딜 임베드＋주인공 바스트업 소형.",
    "오데트·오딜 임베드＋주인공 바스트업 소형.",
    "라푼젤 임베드＋주인공 바스트업 소형.",
    "게르다 임베드＋주인공 바스트업 소형.",
    "배경 임베드 스탠딩 CG＋바스트업 소형 테스트 종료.",
    "주인공 임베드＋히로인 스탠딩 CG 대형.",
    "앨리스 임베드＋주인공 바스트업 대형.",
    "그레텔 임베드＋주인공 바스트업 대형.",
    "오데트 임베드＋주인공 바스트업 대형.",
    "오딜 임베드＋주인공 바스트업 대형.",
    "오데트·오딜 임베드＋주인공 바스트업 대형.",
    "라푼젤 임베드＋주인공 바스트업 대형.",
    "게르다 임베드＋주인공 바스트업 대형.",
    "배경 임베드 스탠딩 CG＋바스트업 대형 테스트 종료.",
    "전신 스탠딩 CG 테스트.",
    "그림자→일반 색상 표시 테스트.",
    "왼쪽. 1명.",
    "왼쪽. 2명.",
    "왼쪽. 3명.",
    "오른쪽",
    "3명.",
    "2명.",
    "모든 패턴 확인.",
    "스탠딩 CG＋바스트업 테스트.",
    "바스트업 테스트.",
    "테스트.",
    "로드 위치마다 추적 변수가 제대로 처리되는지 확인.",
    "그레텔 표정 변경.",
    "게르다 제거.",
    "그레텔 진동.",
    "로드 위치마다 추적 변수가 제대로 처리되는지 확인.",
    "게르다 표정 변경.",
    "게르다 이동.",
    "그레텔 제거.",
    "화면 갱신 줌 업데이트 테스트.",
    "마스크 갱신보다 동적으로 업데이트하고 싶을 때 사용.",
    "두 번째 매개변수로 갱신 후의 초점을 변경.",
    "하단 왼쪽부터 1, 2, 3.^n중단 왼쪽부터 4, 5, 6(0도 중앙).^n하단 왼쪽부터 7, 8, 9.",
    "첫 번째 매개변수 0(현재 갱신)은 보기 좋지 않으므로 사용하지 않습니다.",
    "이어서 배경 슬라이드 로드 테스트입니다.",
    "이동 시 장면 전환 등에 쓸 만한 곳이 있으면 사용합시다.^n방향은 로드의 마지막 매개변수로 변경합니다.^n이것은 위에서 아래로.",
    "이것은 아래에서 위 방향.",
    "왼쪽에서 오른쪽 방향.",
    "오른쪽에서 왼쪽 방향.",
    "대형 배경·소형 배경 동시 표시. 이미 해당 소형 배경의 장소에 있을 때.",
    "대형 배경 표시 후 소형 배경 시차 표시. 이동해 온 느낌을 강조할 때.",
    "대형 배경·소형 배경·바스트업 동시 갱신. 『……라는 말이네요』처럼 앞 내용을 이어받아 처음부터 그 캐릭터가 그곳에 있음을 아는 장면 등에.",
    "모든 캐릭터에 만화 기호를 표시합니다.",
    "두 번째 매개변수를 0으로 설정하면 해제됩니다.",
    "테스트 종료.",
]


def main() -> int:
    expected = set(range(1, 72))
    if len(TARGETS) != 72:
        raise SystemExit(f"target count mismatch: {len(TARGETS) - 1}")
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1001.gsc" and int(item.get("slot", -1)) in expected:
                rows[int(item["slot"])] = item
    if set(rows) != expected:
        raise SystemExit("coverage mismatch")
    entries = []
    for slot in sorted(expected):
        row = rows[slot]
        source, target = str(row["source_text"]), str(TARGETS[slot])
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {slot}")
        if slot == 10 and (source.count("|") != target.count("|") or source.count("[") != target.count("[") or source.count("]") != target.count("]")):
            raise SystemExit("layout-test ruby markup mismatch at slot 10")
        target.encode("cp949", errors="strict")
        entries.append({"uid": row["uid"], "source_text": source, "source_raw_sha256": row["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 대기"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1001_slots_00001_00071_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    path = PROJECT / "packets" / "drafts" / "1001_slots_00001_00071_draft.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "entries": len(entries), "output": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
