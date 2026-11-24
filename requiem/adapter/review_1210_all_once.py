from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
DRAFT = PROJECT / "packets" / "drafts" / "1210_slots_00001_00122_draft.json"
CARET_RE = re.compile(r"\^(?:n|m|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")
CORRECTIONS = {
    2: "응. 열은 없는──것 같은데.^n너, 어쩐지 안색이 좋지 않구나.",
    6: "그래. 어쩐지 밤을 꼬박 새운 사람 같아.^n어제 잠을 잘 못 잤다든가?",
    10: "스트레스일지도 모르겠구나.^n기억이 없고 자신이 누구인지 모른다는 것은^n그 자체만으로 부담이 될 테니.",
    12: "뭐, 어찌 되었든 약을 드릴게요.^n아주 달콤한 비스킷이지만 이건 약이니까요.^n너무 많이 먹으면 안 돼요. 자.",
    15: "묵직한 기름종이 꾸러미를 받아 들자 봉지 밖에서도^n고소하고 달콤한 냄새가 코끝을 간질인다.",
    16: "이 『낙원』의 약이 얼마나 사치스럽고 꿈으로 가득한지^n나름대로 익히 아는 내 입안이,^n성급하게 고인 침으로 젖는 것을 느꼈다.",
    18: "(아아, 이것도 어차피 맛있겠지)",
    20: "(그건 그렇고,^n 왜 항상 며칠 치를 한꺼번에 주는 걸까)",
    21: "필요할 때 필요한 만큼──예를 들면^n병원 식사 쟁반과 함께 내주면 좋을 텐데.",
    23: "전에 받았을 때는 참고 또 참았지만,^n결국 두 번 먹을 분량의 『약』이 간식이 되고 말았지.",
    28: "선생님, 선생님!^n제발 도와주세요. 긴급 상황이에요!",
    31: "제 눈이 망가져 버렸어요!^n선생님이라면 고칠 수 있죠?^n제가 말라붙어 죽지는 않겠죠?",
    34: "그 필사적인 표정과 목소리는 물론이고,^n그녀의 붉은 뺨이 흠뻑 젖어 있는 것이 신경 쓰여,^n나는 의자에서 엉덩이를 들었다.",
    35: "눈물로 가득해 녹아 버릴 듯한 앨리스의 붉은 눈과,^n내 시선이 마주친다.",
    38: "순간 앨리스는 그대로 굳었다.^n놀란 눈빛을 내게 보낸 채 얼어붙어,^n두 눈에서 흐르는 눈물만은 멈추지 않는다.",
    43: "앨리스는 무언가 말을 망설이며 고개를 돌린다.^n줄무늬 목도리를 눈가에 대고 벅벅 문지르지만,^n저렇게 세게 문지르면 눈꺼풀이 따갑지 않을까.",
    47: "자, 다음 환자분이 오셨으니,^n너는 네 방으로 돌아가도록 해요.",
    50: "앨리스는 숙녀니까,^n남자아이에게 보여 줄 수 없는 얼굴도 있는 거야.",
    52: "너도 말이야, 나나시.^n절대로 보아서는 안 되는 여자아이의 모습이 있는 법이야.",
    55: "간호사의 말을 듣자 눈치 없는 내 머리는^n모니터 너머로 두 번이나 본 라푼젤의 모습을^n떠올리고 만다.",
    57: "──아아, 그렇구나. 확실히 이것은,^n여자아이에게 절대 보이고 싶지 않은 얼굴이다.",
    58: "그렇게 생각하니 앨리스의 수상한 행동을 전부 용서할 수 있을 듯해,^n나는 순순히 진찰실을 나가기로 했다.",
    63: "그대로 평소처럼 떠나려던 순간,^n나는 발길을 돌려 문 앞으로 돌아왔다.",
    65: "있잖아요, 있잖아요. 눈물이 멈추지 않아요.^n멈추어도 잠시 지나면 또 무언가 북받쳐 올라,^n여기서 홍수가 되어 넘쳐 버려요.",
    69: "문에 살며시 몸을 기울이기만 해도,^n앨리스와 두 사람의 대화가 잘 들렸다.",
    72: "이제는 변명할 여지조차 없을 만큼,^n훌륭하고 모범적이며 그림으로 그린 듯한 엿듣기다.",
    74: "저는요, 전에 제 눈물로 생긴 연못에 빠진 적이 있는데요,^n그때보다 훨씬 심한 수량과 수압이에요.",
    76: "제 몸이 그때와 달리 작지 않아서 다행이에요.^n자기 눈물로 생긴 연못에서 헤엄치는 경험은 한 번이면 충분하고,^n무엇보다 이 기세라면 연못은커녕 폭풍 치는 바다예요.",
    84: "받아 주신 덕분에 괜찮았어요.^n『고양이 없는 웃음』을 놓친 건^n아주 큰 타격이었지만요…….",
    85: "앨리스의 이야기는 본론과 먼 곳에서 시작해,^n이곳저곳으로 샛길을 들렀다.",
    86: "게다가 이야기 도중마다 앨리스가 흐느껴 울어 그때마다 말이 멈춘다.^n모든 사정을 아는 나로서는^n답답하기 짝이 없다.",
    87: "긴장감 넘치던 엿듣기가^n완전히 따분하고 늘어지는 일로 바뀔 즈음,^n앨리스는 마침내 자초지종을 다 이야기했다.",
    91: "저 나나시와 『가족』에 관해 이야기하던 중,^n자세한 일을 떠올릴 수 없었다.^n떠올리려 하자 눈물이 멈추지 않게 되었다.",
    93: "맞아요, 그런 일이에요. 제발 어떻게든 해 주세요, 선생님.^n저 죽지는 않겠죠?^n이대로 눈이 쪼그라들지는 않겠죠?",
    96: "들이마시면 안 돼요, 여자아이잖아.^n자, 흥 해요.",
    97: "푸우우웅, 하는 품위 없는 소리가 잦아든 뒤,^n의사 선생님의 온화한 목소리가 들렸다.",
    99: "……뭐, 자연히 멈출 테니 괜찮아.^n당분간 『가족』에 관해서는 생각하지 말고,^n영양가 있는 것을 많이 먹으며 푹 자도록 해.",
    103: "가벼운 감기야.^n그래, 약을 내줄게.^n미스미, 레인보 드롭스를 줘.",
    107: "증상이 괴로우면 우선 바로 한 알.^n그다음부터는 식후에 한 알씩 먹도록 해.",
    109: "그래, 먹으면 졸릴 테니,^n잠들면 곤란한 곳에서는 먹지 말아야 해.",
    114: "앨리스는 언제나 있는 만큼 전부 먹어 버리잖아.^n이건 사흘 치니까 꼭 사흘에 걸쳐 복용해야 해요.",
    116: "제가 참지 못하는 게 아니에요.^n약 쪽에서 『나를 마셔 줘』라고 말하며,^n일제히 제 입안으로 뛰어드는 거예요…….",
    119: "진찰을 마친 앨리스와^n마주쳐서는 절대로 안 되기에,^n나는 그쯤에서 조용히 물러나기로 했다.",
    122: "간호사가^n고양이와 장난치듯 즐겁게 웃는 목소리를 들으며,^n그런 생각을 마음에 품은 채.",
}


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match:
        raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    if draft.get("review_passes_completed") != 0 or draft.get("scope") != "1210_slots_00001_00122_draft":
        raise SystemExit("unexpected draft")
    expected = set(range(1, 123))
    entries = {slot(str(entry["uid"])): dict(entry) for entry in draft["entries"]}
    if set(entries) != expected:
        raise SystemExit("draft coverage mismatch")
    changes = []
    for index, target in CORRECTIONS.items():
        before = str(entries[index]["target_text"])
        entries[index]["target_text"] = target
        if before != target:
            changes.append({"slot": index, "before": before, "after": target})
    catalog, lookup = {}, set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") != "1210.gsc":
                continue
            index = int(item["slot"])
            if index in expected:
                catalog[index] = item
            elif "lookup_keys" in item.get("lanes", []):
                lookup.add(index)
    if set(catalog) != expected or lookup != set(range(123, 181)):
        raise SystemExit("catalog or lookup coverage mismatch")
    final_entries = []
    for index in sorted(expected):
        entry = entries[index]
        source, target = str(entry["source_text"]), str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]:
            raise SystemExit(f"source drift at slot {index}")
        if CARET_RE.findall(source) != CARET_RE.findall(target):
            raise SystemExit(f"caret mismatch at slot {index}")
        if JAPANESE_RE.search(target):
            raise SystemExit(f"Japanese residue at slot {index}")
        target.encode("cp949", errors="strict")
        entry.update({"translator": "Codex internal model", "review_status": "reviewed_once", "reviewer": "Codex internal model single review pass", "notes": "초벌 번역 후 1차 문맥·문체·용어·제어 코드 검수 완료"})
        final_entries.append(entry)
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1210_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 122], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [123, 180], "release_ready": False, "entries": final_entries}
    out = PROJECT / "packets" / "reviewed" / "1210_all_translatable_slots_reviewed_once.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(DRAFT)], "output": str(out), "entry_count": len(final_entries), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 122], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True, "lookup_range_123_180_preserved": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    audit_path = PROJECT / "audit" / "translation_review_1210_complete.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "audit_path": str(audit_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
