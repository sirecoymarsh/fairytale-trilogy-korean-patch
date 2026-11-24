from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    141: "『주머니에 조약돌을 넣고,^n　끌려가는 길에 떨어뜨리면,^n　돌아오는 길을 알 수 있잖아.』",
    142: "그레텔",
    143: "네……, 네……?",
    144: "나",
    145: "──가자. 자.",
    146: "나는 힘차게 일어나 그레텔을 재촉했다.",
    147: "조심스럽게 일어선 그레텔의 몸에서^n담요가 미끄러져 내린다.",
    148: "나는 미리 슬리퍼를 벗어 두고,^n그레텔의 방 안쪽에 있는 또 하나의 문에 손을 댔다.",
    149: "여자아이들의 병실 크기는 제각각이지만,^n그레텔의 방은 너무 좁았다.^n계속 신경 쓰였었다.",
    150: "생각대로 문을 열자 그곳에는^n『뒷마당』이 펼쳐져 있었다.",
    151: "잔디 카펫과 나무 울타리.^n사방을 둘러싼 벽지에는 울창한 숲이 그려져 있다.",
    152: "불을 켜자 푸르고 희미한 조명이 들어왔다.^n분명 『헨젤과 그레텔』에서 뒷마당을 찾는 때는^n언제나 밤이기 때문이다. 천장은 별이 뜬 밤하늘을 본떴다.",
    153: "그레텔",
    154: "아……!^n도, 돌.",
    155: "　가짜 잔디 위에는,^n　역시 가짜인 하얀 돌이 흩어져 있었다.^n『달빛』을 반사해 반짝반짝 빛난다.",
    156: "나",
    157: "주워 두자.^n그러면 안심할 수 있잖아.",
    158: "그레텔",
    159: "──!^n응……!",
    160: "눈물 자국이 안쓰러운 뺨을 귀여운 장밋빛으로 물들이고,^n그레텔은 힘껏 고개를 끄덕였다.",
    161: "　그렇게 우리는,^n『뒷마당』에 흩어진 조약돌을 주워 모았다.",
    162: "그레텔의 옷에는 밖에서 티 나지 않는^n커다란 주머니가 있다.^n그것이 빵빵해질 때까지 둘이 모은 조약돌을 채워 넣었다.",
    163: "나",
    164: "이제 숲속 깊이 끌려가도 괜찮아.^n길을 알려 주는 표식이 될 테니까.",
    165: "그레텔",
    166: "응!",
    167: "볼일을 마치고 『뒷마당』에서 돌아갈 때,^n등 뒤에서 그레텔의 목소리가 들렸다.",
    168: "그레텔",
    169: "고, 고마워…….^n그──",
    170: "오, 오빠……?",
    171: "뒤돌아보니 그레텔의 눈동자는^n아까와는 다른 빛깔의 눈물로 젖어 있었다.",
    172: "──아마 나는 후회하지 않을 것 같다.",
    173: "나",
    174: "응, 천만에.^n──그레텔.",
    175: "나",
    176: "그런 얼굴 하지 마. 괜찮으니까…….^n너를 버릴 사람은 『낙원』에 없어.",
    177: "가엾지만 내 여동생은 이 아이가 아니다.",
    178: "나는 되도록 공허하게 들리지 않도록,^n말과 어조를 골라 그레텔에게 전했다.",
    179: "나",
    180: "의사 선생님도 간호사 선생님도 있잖아.^n버림받을 것 같으면 막아 줄 거야.",
    181: "내게는 진짜 여동생이 있었고 이 아이의 오빠가 될 수 없다.^n어중간한 친절은 오히려 잔혹하다.",
    182: "『동화 증후군』만 나으면,^n　버림받을 공포와 슬픔에서도 벗어날 수 있다.",
    183: "그런데 내가 『헨젤』을 자처한다면,^n망상에 협력하는 사람이 늘어,^n그녀의 증상을 악화시킬지도 모른다.",
    184: "그러니 이게 옳다.^n이것이 그녀에게 가장 좋은 일이다.",
    185: "그레텔",
    186: "응, 그래…… 그렇지.",
    187: "그레텔답지 않게 또렷한 목소리가 대답했다.^n목의 떨림을 억누르려고 일부러 힘주어 발음한 목소리였다.",
    188: "그레텔",
    189: "괜찮아. 나, 괜찮아.^n그러니까…….^n고마워. 미안해…….",
    190: "나",
    191: "……읏.",
    192: "손끝이 하얘질 만큼 세게 『성서』를 움켜쥐고 있다.",
    193: "내게 웃어 보이는 그 얼굴에는 아까까지의 그늘이 없다.^n하지만 지금까지 중 가장 안쓰러운 표정이었다.",
    194: "나",
    195: "저기, 그레텔…….",
    196: "그레텔",
    197: "졸려……졌어.^n그러니까, 저기…….^n혼자 있고, 싶어.",
    198: "나",
    199: "………….",
    200: "　그레텔은 내게 마음을 닫았다.^n『혹시나』라는 기대를 버리고 응석 부리는 것도 포기한 채,^n　강한 척하고 꾸며 내며 거리를 두었다.",
    201: "나",
    202: "응, 알았어.^n──그…… 좋은 꿈 꿔.",
    203: "이것이 최선이라고는 생각한다.",
    204: "하지만 그레텔의 방문을 등 뒤로 닫은 뒤,^n참고 있던 것이 터져 나온 듯,^n억눌러 죽인 흐느낌이 새어 나오는 것을 들었을 때.",
    205: "나는 분명 후회했다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1111.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1111_slots_00141_00205_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1111_slots_00141_00205_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
