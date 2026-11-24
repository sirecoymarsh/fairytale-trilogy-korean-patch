from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    1: "사실 밤 산책을 나가기로 마음먹고,^n가장 먼저 머리에 떠오른 곳이 이 정원이었다.",
    2: "발목에 닿는 풀의 높이는 제각각인데,^n둘러보면 초록색 카펫처럼 보이는 넓은 초원.",
    3: "망루처럼 높이 솟은 나무 한 그루와,^n낙엽을 빙글빙글 가지고 노는 귀여운 개울과,^n멀리서 조금 푸르게 보이는 검은 숲.",
    4: "평온한 밤이었다.^n잠소리 같은 벌레 울음을 들으며,^n얼마나 걸었을까.",
    5: "나는 어느새 장미 생울타리가 만든^n아담한 미로에 도착해 있었다.",
    6: "생울타리 전체는 잠든 듯 보였지만,^n짙은 초록에 돋보이는 꽃은 늦게까지 깨어 있듯^n우아한 향기를 풍기고 있다.",
    7: "빨간 장미와 하얀 장미.^n분명 그런 제목의 동화도 있었지──",
    8: "나",
    9: "………….",
    10: "나는 걸음을 멈췄다.",
    11: "이쪽으로 유난히 당당하게 뻗은 가지 끝에,^n말을 걸듯 피어난 빨간 장미가 있다.",
    12: "　목소리가 들리는 듯했다.^n　앨리스의 『나를 먹어』가 아니라,^n『나를 꺾어 줘』──",
    13: "나도 이 『낙원』에 물들기 시작한 걸까.",
    14: "나",
    15: "(하지만 이 장미를 보고 있자니 뭐랄까.^n　이상한 기분이 드네.)",
    16: "하얀 장미에는 아무것도 느끼지 못하는데,^n빨간 장미를 보면 가슴속에서 일렁이는 것이 있다.",
    17: "그것은 실체를 얻을 듯한 기척을 풍기지만,^n금세 사라지고 만다.",
    18: "빨간 장미는 내 과거와 이어져 있는 걸까.",
    19: "나",
    20: "………….",
    21: "나는 주위를 둘러보았다.^n──아무도 없다.",
    22: "나는 빨간 장미 가지를…….",
    23: "아무것도 하지 않는다.",
    24: "꺾었다.",
    25: "톡 하고 가지가 낸 가느다란 소리를 듣고^n나는 갑자기 죄책감을 느꼈다.",
    26: "나는 옷에 달린 커다란 주머니에 장미를 살며시 밀어 넣고,^n조금 빠른 걸음으로 산책을 계속했다.",
    27: "나",
    28: "(……그건 좋지 않겠지.)",
    29: "정원을 돌보는 사람이 슬퍼할 것이다.",
    30: "게다가 애초에 손에 넣어서 뭘 할 것인가.^n가지고 있는 모습을 들키면^n분명 혼날 테고.",
    31: "나",
    32: "(자세히 보니 가시투성이고.)",
    33: "나는 뻗으려던 손을 거두고 밤 산책을 계속했다.",
    34: "너무 멀리 가면 돌아오기도 귀찮다.^n나는 산책 기분을 충분히 즐긴 뒤,^n병동 근처까지 돌아왔다.",
    35: "──목소리를 깨달은 것은 그때였다.",
    36: "여자의 목소리.^n어디선가 들은 적이 있다.",
    37: "조신하고 차분하며 기품 있고,^n제비가 날아간 자취처럼 아름다운 억양으로,^n귀 안쪽을 부드럽게 씻는 듯한 기분 좋은 목소리.",
    38: "환상처럼 들리던 그것은,^n병동에 다가가 벽을 따라 걸을수록^n점점 크고 선명해졌다.",
    39: "나",
    40: "(아…….)",
    41: "이윽고 도착한 곳은,^n병동 끝에 붙여 지은 탑 아래였다.",
    42: "이 돌탑 안은,^n전망대처럼 꾸민 병실을 제외하면 거의 나선 계단이라는 것을,^n낮에 올라가 본 나는 알고 있다.",
    43: "나",
    44: "(라푼젤 병실 아래…….^n　그렇다면 이건 라푼젤의 목소리인가?)",
    45: "그렇게 생각하며 올려다보자 전망대 창문에서^n덩굴과 뒤섞여 벽을 타고 흐르는 금빛 줄기가 보였다.",
    46: "창문에서 내려온 것이 땅에 닿기 직전 다시 올라가,^n창문 옆 갈고리에 걸린 뒤 다시 아래를 향한다.^n그런 상태로 세 줄이 나란히 늘어져 있다.",
    47: "나",
    48: "(라푼젤의 머리카락…….^n　이거 진짜야?)",
    49: "동화 『라푼젤』의 라푼젤은,^n자신이 갇혀 자란 탑의 창문에서^n자기 머리카락을 늘어뜨린다.",
    50: "아래에서 올라오는 사람이 사다리로 쓰게 하려고.^n낮에는 고델 할머니가, 밤에는 밀회 상대인 왕자가,^n라푼젤의 머리카락을 타고 드나든다.",
    51: "　처음 『라푼젤』을 읽었을 때 줄거리보다^n『머리카락을 타고 탑에 오른다』는 표현에 깜짝 놀랐었다.",
    52: "머리카락으로 사람 몸무게를 버틴다니 생각만 해도 아플 것 같다.^n두피째 뽑혀 버리는 것 아닐까.",
    53: "왜 그런 짓을…… 하고,^n어린이용 동화를 진지하게 고민했던 나지만,^n생각해 보니 제법 잘 만든 방식인 듯하다.",
    54: "고델 할머니는 라푼젤을 가둬 두려면,^n라푼젤 자신은 쓸 수 없는 사다리를^n마련해야 했던 것이다.",
    55: "나",
    56: "(그나저나 그렇군. 이런 식으로 늘어뜨린 건가.)",
    57: "나는 눈앞에 뻗은 세 줄의 머리카락 중 하나를 당겨 보았다.",
    58: "이렇게 구불구불 창문과 지면 바로 위를 왕복하는 머리카락도,^n예상 밖이었다.",
    59: "내 머릿속에는 완전히,^n한 줄로 늘어진 머리카락에만 매달려 기어오르는 모습이^n자리 잡고 있었다.",
    60: "나",
    61: "(그렇구나. 땅에서 올라가는 머리카락과,^n　갈고리에 걸려 내려가는 머리카락을 잡으면,^n　몸무게를 갈고리만으로 지탱할 수 있겠어──)",
    62: "왕복하는 머리카락 중 두 번째와 세 번째 줄을 양손으로 잡고,^n발은 탑 벽을 딛고 기어오른다──^n올라가는 사람에게도 고마운 구조라고 감탄했다.",
    63: "감탄하고 나자 또 다른 마음이^n무럭무럭 일어나기 시작했다.",
    64: "나",
    65: "(──올라가 보고 싶어.)",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1113.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1113_slots_00001_00065_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1113_slots_00001_00065_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
