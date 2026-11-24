from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
TARGETS = [
    None,
    "맑은 밤하늘에 진주 같은 달이 빛나고 있다.",
    "상쾌한 밤이었지만 마음은 개운하지 않았다.^n우리는 말없이 정처 없이 계속 걸었다.",
    "──그 후.^n",
    "──그 불가해한 어둠의 폭풍에 삼켜져 붕괴의 소리를 들은 후.",
    "나는 우선 넋을 잃은 앨리스를 위해^n의사 선생님을 불러야겠다고 생각했다.",
    "앨리스",
    "잠깐!",
    "하지만 앨리스는 그것을 거부했다.",
    "사실 그녀는 아직 넋을 놓고 있고 싶었을 것이다.^n거센 충격의 여파가 사라진 뒤,^n천천히 회복하고 싶었을 것이다.",
    "그 상태에서 억지로 정신을 차려야 할 만큼^n내 행동이 싫었다는 뜻이다.",
    "앨리스",
    "방금 있었던 일은 아무에게도 말하지 말아 줘요.",
    "나",
    "하지만…….",
    "너 또 울고 있잖아, 하고 말하려던 내 앞에서^n앨리스는 조용히 눈가를 닦았다.",
    "앨리스",
    "괜찮으니까요. 부탁이에요.",
    "그렇게 말하며 나를 바라보는 앨리스의 눈에는^n더는 새로운 눈물이 맺히려 하지 않았다.",
    "의지의 힘으로 눈물을 멈춘 것이다.^n그 어린아이처럼 모든 것을 숨김없이 드러내던 앨리스가.",
    "내가 할 수 있는 일은 이렇게^n밤의 정원 산책이라는 얄팍한 기분 전환에^n그녀를 데리고 나오는 정도였다.",
    "나",
    "아까 그건…… 대체 뭐였을까.",
    "앨리스",
    "………….",
    "나",
    "──그것도 분명 약 때문이야.^n앨리스에게 잘난 척하며 그런 말을 했지만,^n사실 나도 무심코 너무 많이 먹어 버리거든…….",
    "나",
    "그래서 눈을 뜬 채 나쁜 꿈을 꾸는 거야.^n이렇게 되면 싫겠다고 생각한 일이야말로^n꿈속에서는 생생하잖아.",
    "나",
    "그저 그것뿐이었어.^n그게 다야.",
    "아프고 괴롭기만 한 내 주장을^n듣고 있는지 아닌지.",
    "앨리스는 갑자기 걸음을 멈췄다.",
    "앨리스",
    "──저 말이에요.^n깨달았다기보다 떠올렸어요.^n모든 일에는 끝이 있다는 것을.",
    "그곳은 낮에 청소부 아저씨들이^n끈적한 붉은 페인트를 마구 칠해 놓은 흰 장미 앞이었다.",
    "앨리스",
    "여러 동물이 사람처럼 말하고,^n몸이 커졌다 작아졌다 하며,^n트럼프 인간들이 이리저리 돌아다니고──",
    "앨리스",
    "정말 이상한 세계잖아요!^n",
    "……라고 생각했지만요.",
    "앨리스",
    "제가 생각했던 것보다 훨씬 더 이상한 세계예요.^n머리가 이상한 저를 이상한 채로 응석받이처럼 받아 주다니.",
    "나",
    "앨리스, 그건…….",
    "자기 광기도, 그 광기를 풀어놓은 채 기르는 『낙원』도^n제대로 인식하고 있다는 뜻일까.",
    "나",
    "(그러니까 너는 제정신으로 돌아온 거야?^n 『동화 증후군』이 나은 거야?)",
    "무례하게 물으려던 입을 나는 황급히 다물었다.",
    "앨리스",
    "──진짜 저는^n저기서 언니에게 기대어 잠들어 있어요.",
    "앨리스는 빙그르르 돌아서더니,^n이번에는 멀리 보이는 큰 나무를 가리켰다.",
    "낮에 우리가 체셔 고양이를 목격하고,^n앨리스가 『고양이 없는 웃음』을 손에 넣으려고^n나무 타기를 시도했던 바로 그 큰 나무다.",
    "앨리스",
    "분명 이제 곧 저는 눈을 뜰 거예요.^n언니의 무릎 위에서요.^n그리고 차 마실 시간에 맞추어 달려가는 거예요…….",
    "앨리스",
    "그 발걸음 그대로 어른이 되어,^n이 세계를 잊어버리는 거예요.",
    " 앨리스가 입에 담은 것은^n『이상한 나라의 앨리스』의 마지막 장면이다.",
    "앨리스는 자기 이야기의 끝을 예감하는 걸까.^n아니면 스스로 끝낼 생각인 걸까.",
    " 결말까지 줄거리를 전부 연기한 뒤,^n『성서』를 덮고 두 번 다시 펼치지 않을 생각인 걸까.",
    "나",
    "………….",
    "나는 두려움이 밀려와 그녀의 이름조차 부를 수 없었다.",
    "그녀의 마음에 닿을 만한 말은 떠오르지 않는다.^n나는 진짜 그녀에 대해 아무것도 모른다.",
    "앨리스는 마지막으로 빛을 잃은 눈길을^n가만히 『붉은 흰 장미』에 두었다.",
    "앨리스",
    "……불쌍한 짓을 했네요.^n제 억지 때문에…….",
    "살며시 마른 페인트 위를 덧그리는 손끝도,^n밤바람에 사라질 듯한 중얼거림도,^n어른스러운 그늘이 배어나는 옆얼굴도.",
    "지금의 앨리스는 어느 것 하나 앨리스답지 않았다.",
    "그날 밤, 나는 좀처럼 잠들지 못했다.",
    "쉴 새 없이 뒤척이고,^n떠오르는 생각을 닥치는 대로 몰아내고,^n간신히 졸음이 찾아와도 의식을 놓기가 두려워지고.",
    "나",
    "(──그건 대체 무엇이었을까)",
    "오래전 어느 화목한 가족이 사고를 당했다.^n홀로 살아남은 여자아이는 그 비극을 견디지 못해,^n망상의 세계로 도망쳐 앨리스가 되었다──",
    "그 어둠 속에서 겪은 일을 이어 보면,^n자연스럽게 그런 줄거리가 된다.",
    " 이해할 수 없는 건, 아마 앨리스의 머릿속에서 일어난^n『봉인했던 끔찍한 과거가 되살아난다』는 현상에,^n 어째서 곁에 있었을 뿐인 내가 휘말렸는가 하는 점이다.",
    "남의 백일몽 속으로 빨려 들어가다니,^n참으로 이상하고 있을 수 없는 이야기라고 생각한다.",
    "나",
    "(하지만 직접 겪어 버렸으니 어쩔 수 없지)",
    "기억을 잃은 채 정신을 차리니 이 『낙원』에 있었다는^n처지부터가 이미 현실이니 받아들일 수밖에 없다.^n이것도 마찬가지다.",
    "나",
    "(아니면 내 머리도 이상해지기 시작한 걸까)",
    "원래부터 여러 단계에 걸쳐 미쳐 있는데,^n그건 곤란한데…… 하고,^n남 일처럼 나는 한숨을 쉬었다.",
    "어찌 되었든 가장 마음에 걸리는 건 그게 아니다.",
    " ^n^m──『피고인 앨리스』──",
    "고막에 달라붙어 축축하게 썩어 들어가는 듯한^n음습한 목소리가 머릿속에서 떠나지 않는다.",
    "왜 『피고인』인 걸까.",
    "그 목소리가 본래 앨리스의 것이었다 해도,^n지나치게 격렬한 탄핵이라고 생각한다.",
    "혼자만 살아남았다는 죄책감이^n그런 자학적인 말을 고르게 한 걸까.",
    "나",
    "(참…… 섬뜩한 목소리였어)",
    "나는 부르르 등골을 떨며^n다시 몸을 뒤척였다.",
    "──앨리스는 어떻게 지내고 있을까.",
    "축척이 뒤죽박죽이고 장난감 상자를 뒤엎은 듯한 그 방은^n지금 앨리스의 눈에 어떻게 비칠까.",
    "그런 생각을 두서없이 이어 가며,^n나는 긴 밤을 보냈다.",
]


def main() -> int:
    expected = set(range(1, 95))
    if len(TARGETS) != 95:
        raise SystemExit(f"target count mismatch: {len(TARGETS)-1}")
    rows, lookup = {}, set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1212.gsc":
                continue
            slot = int(item["slot"])
            if slot in expected:
                rows[slot] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(slot)
    if set(rows) != expected or lookup != set(range(95, 153)):
        raise SystemExit("visible or lookup coverage mismatch")
    entries = []
    for slot in sorted(expected):
        row, target = rows[slot], str(TARGETS[slot])
        source = str(row["source_text"])
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {slot}: {CARET_RE.findall(source)} != {CARET_RE.findall(target)}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": row["uid"], "source_text": source, "source_raw_sha256": row["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 대기"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1212_slots_00001_00094_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1212_slots_00001_00094_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "entries": len(entries), "lookup_slots_preserved": [95, 152], "output": str(out), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
