from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CORRECTIONS = {
    6: "라푼젤 역시,^n『할머니』를 맞이할 생각으로 나를 불러들인 것이다.",
    10: "코를 확 찌르는 기름진 냄새.^n그 냄새는 라푼젤 손에 들린 팔레트 위에서^n붓으로 이리저리 뒤섞이는 물감에서 풍겨 왔다.",
    13: "그림 도구가 왔구나.",
    15: "네, 오늘 아침에 받았답니다.^n설마 이런 무리한 부탁까지 들어주실 줄은^n꿈에도 몰랐어요, 할머니.",
    21: "글쎄요, 무엇이 될는지…….^n저도 모르겠어요.^n그림을 그리고 싶어진 것부터 그저 순간적인 생각이었으니까요.",
    28: "아무것도 없는 흰 바탕에서 무언가를 찾듯 응시한다.^n그려야 할 형태를 찾는 순간, 깊은 호수 표면 같은 눈동자 밑바닥에도^n열정으로 굳건한 초점이 생길까.",
    46: "──무엇을.^n무엇을 보셨다고 말씀하시는 건가요.^n할머니…….",
    49: "도저히 끝까지 말할 수 없어 말을 흐린다.",
    58: "쉰 목소리, 감추지 못한 동요.^n연기가 서툴다는 사실에 짜증마저 났다.",
    62: "아니야, 나는 보고 말았어.^n분명히 너였어. 이 두 눈으로 봤어.",
    71: "내 말의 가시에 상처 입은 라푼젤은 붓을 떨어뜨린다.^n아무것도 쥐지 않은 손가락은 새하얗게 굳어 떨리고 있다.",
    76: "말씀을 어겨서 죄송해요.^n비밀을 숨기고, 모든 걸 들킨 뒤에도 얼버무리려 해서──",
    81: "하지만──할머니. 부디, 부디 용서해 주세요.^n저희 두 사람은 서로 사랑하고 있어요.^n부디 저와 그분을 갈라놓지 말아 주세요.",
    87: "그분의 눈빛도, 목소리도, 온기도──^n그분이 주시는 모든 것이 따뜻하고 선명해서.^n──이것이 행복이라고 저는 생각했어요.",
    94: "그리고 상관없다고 대답하려 했다.^n정말로 내게는 그런 걸 억지로 보여 준 게 불쾌할 뿐이고,^n라푼젤이 뭘 하든 그녀 마음이라고 생각했으니까.",
    102: "이 시설 사람과 연인 사이가 된 거라면,^n어떤 일을 맡은 사람이고 어떻게 만난 걸까?^n내가 묻고 싶은 건 그런 것이다.",
    105: "라푼젤은 조용히 고개를 들었다.^n새하얀 얼굴을 가로지르듯 머리카락 한 가닥이 흘러내려,^n왠지 지친 인상이었다.",
    109: "와, 왕자님이 그렇게 흔한 사람은 아니잖아.^n어…… 어느 나라의? 이름은 뭐야?",
    121: "모르는 분이 아니에요.^n제 온 마음을 다해 사랑하는 분이에요.^n그러니 저는…… 무엇을 바쳐도 상관없어요.",
    127: "저는 그분을 만날 때마다──^n사랑을 속삭여 주시면 충만해져서, 더는 아무것도 필요 없다고,^n……진심으로 그렇게 생각해요.",
    131: "나는 그것도 꼬집어 한마디 해 주리라,^n불안정한 그녀를 더 들쑤셔 보리라, 짓궂은 마음으로^n입을 열려다──문득 허무해졌다.",
    148: "어젯밤 본, 보기에도 부드러워 보이던 배.^n살집이 도톰한데도 우아한 곡선을 그리며 잘록했다.",
    158: "분명 남녀 쌍둥이를 낳지 않았던가…….",
    159: "배 위를 천천히 오가는 손을 보며,^n나는 그만 생각한 것을 입 밖에 내고 말았다.",
    173: "비밀을 지적했을 때보다^n훨씬 큰 충격을 받은 듯한 라푼젤에게,^n나는 어떻게 다가가야 할지 몰라졌다.",
    193: "『할 수』 있지만 『하지 않는』, 『할 수 없는』 거야.^n그런 설정──아니, 병세니까.",
    199: "그런데 오늘은 갑자기 밖으로 나왔다고.^n병세가 호전된 건지 악화된 건지──심상치 않아.^n일단 보고해야겠어.",
    201: "(이건…… 어쩌면이 아니라^n정말 큰일이 난 걸지도……)",
    209: "털어놓을 상대를 찾았다는 사실에 안도했지만,^n시작부터 나는 말을 더듬었다.",
    210: "경위를 이야기하자니 떳떳하지 못한 구석이 너무 많아,^n도저히 모든 걸 말할 수는 없다.",
    214: "──어떻게든 앞뒤가 맞게 전달한 것 같다.",
    216: "아하, 그렇구나…….",
    218: "그러니까 라푼젤은 『할머니』인 너에게^n임신한 걸 들켰다고 생각해서,^n탑에서 쫓겨나는 줄거리를 따른 거구나.",
    222: "뭐, 너무 마음 쓰지 마.^n『라푼젤』이 원래 그런 이야기였을 뿐이니까.",
    224: "게다가──이번 일은^n『없었던 일』로 돌아가지 않을까.",
    228: "어쨌든 내가 쓸데없는 말을 해서^n라푼젤을 공황에 빠뜨린 건 틀림없다.^n없던 일로 만들 수 있다면 그렇게 되길 바랐다.",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")


def slot(uid: str) -> int:
    match = re.search(r"slot/(\d+)$", uid)
    if not match: raise ValueError(uid)
    return int(match.group(1))


def main() -> int:
    draft_paths = [PROJECT / "packets" / "drafts" / name for name in (
        "1131_slots_00001_00080_draft.json", "1131_slots_00081_00160_draft.json", "1131_slots_00161_00231_draft.json")]
    entries = {}
    for path in draft_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("review_passes_completed") != 0: raise SystemExit(f"not draft: {path}")
        for entry in data["entries"]:
            index = slot(str(entry["uid"]))
            if index in entries: raise SystemExit(f"duplicate {index}")
            entries[index] = dict(entry)
    expected = set(range(1, 232))
    if set(entries) != expected: raise SystemExit("draft coverage mismatch")
    changes = []
    for index, target in CORRECTIONS.items():
        before = str(entries[index]["target_text"]); entries[index]["target_text"] = target
        if before != target: changes.append({"slot": index, "before": before, "after": target})
    catalog, lookup = {}, set()
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("file") != "1131.gsc": continue
            index = int(row["slot"])
            if index in expected: catalog[index] = row
            elif "lookup_keys" in row.get("lanes", []): lookup.add(index)
    if set(catalog) != expected or lookup != set(range(232, 290)): raise SystemExit("catalog or lookup mismatch")
    final = []
    for index in sorted(expected):
        entry = entries[index]; source, target = str(entry["source_text"]), str(entry["target_text"])
        if source != catalog[index]["source_text"] or entry["source_raw_sha256"] != catalog[index]["source_raw_sha256"]: raise SystemExit(f"source drift {index}")
        if CARET_RE.findall(source) != CARET_RE.findall(target): raise SystemExit(f"caret mismatch {index}")
        if JAPANESE_RE.search(target): raise SystemExit(f"Japanese residue {index}")
        target.encode("cp949", errors="strict")
        entry.update({"translator": "Codex internal model", "review_status": "reviewed_once", "reviewer": "Codex internal model single review pass", "notes": "초벌 번역 후 1차 문맥·문체·용어·코드 검수 완료"}); final.append(entry)
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1131_all_translatable_slots_reviewed_once", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 1, "review_policy": "every translatable slot received exactly one Codex review pass", "newly_reviewed_range": [1, 231], "new_review_change_count": len(changes), "new_review_changes": changes, "file_translation_complete": True, "lookup_slots_preserved": [232, 289], "release_ready": False, "entries": final}
    out = PROJECT / "packets" / "reviewed" / "1131_all_translatable_slots_reviewed_once.json"; out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"schema": "fairytale-requiem-translation-review-audit-v1", "status": "PASS", "scope": output["scope"], "draft_inputs": [str(x) for x in draft_paths], "output": str(out), "entry_count": len(final), "review_passes_per_slot": 1, "newly_reviewed_slots": [1, 231], "new_review_change_count": len(changes), "checks": {"source_text_and_hash_match_catalog": True, "caret_token_order_preserved": True, "all_targets_strict_cp949": True, "no_kana_residue": True, "exactly_one_review_per_slot": True, "all_translatable_slots_covered": True, "lookup_slots_excluded": True}, "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}
    (PROJECT / "audit" / "translation_review_1131_complete.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**audit, "changes": changes}, ensure_ascii=True, indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
