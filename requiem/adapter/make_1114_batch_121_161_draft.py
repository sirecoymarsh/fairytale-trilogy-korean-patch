from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    121: "어째서…….^n나는 달라. 다르다고.",
    122: "손가락 사이로 짜내는 목소리는 격렬한 갈등으로 잠겨 있었다.",
    123: "게르다",
    124: "조금만 더 하면 기억날 것 같은데…… 아무것도 떠오르지 않아.",
    125: "게르다는 분한 듯 삐걱거리는 목소리로 혼잣말을 내뱉더니^n문득 움켜쥔 주먹을 풀었다.",
    126: "게르다",
    127: "──하지만 그게 나을지도 몰라.^n이 머리에 떠오르는 것이 기억인지, 전혀 다른 무언가인지,^n이제 나도 모르겠어…….",
    128: "어딘가 힘없이 중얼거리며,^n게르다는 편 두 손으로 자기 이마를 감쌌다.",
    129: "그대로 움직이지 않게 된 그녀를^n나는 어쩔 줄 몰라 하며 들여다보았다.",
    130: "낮에 만났을 때는 의연하고 흔들림 없어 보였던 게르다가,^n이토록 쉽게 약해진 모습이 그저 무서워서.",
    131: "나",
    132: "괘, 괜찮아?^n누구라도 불러올까, 게르다──",
    133: "게르다",
    134: "게르다가 아니야……!",
    135: "게르다는 큰 소리를 지르며 머리를 좌우로 흔들었다.^n손바닥 아래의 얼굴은 괴로운 듯 일그러져 있다.",
    136: "게르다",
    137: "나는 게르다가 아니야…….^n……아니, 나는 게르다야…….",
    138: "나는 실언을 수습하려고 입을 열었다.^n하지만 뭐라고 말해야 할지 알 수 없었다.",
    139: "그 대신 나는^n묻지 않기로 마음먹었던 것을^n그만 불쑥 입에 올리고 말았다.",
    140: "나",
    141: "있잖아, 너 혹시 병이 낫기 시작한 거야?",
    142: "게르다는 어깨를 떨며 얼굴을 들어 나를 보았다.^n은빛 머리카락이 선명해 보일 만큼^n그 안색은 푸르스름하고 창백했다.",
    143: "게르다",
    144: "──무슨 말이야?",
    145: "나",
    146: "　그렇잖아. 넌 자신이 게르다가 아니라고 생각해.^n『성서』도 저런 곳에 내버려 두고,^n　다른 아이들처럼 늘 손에 들고 다니지도 않잖아.",
    147: "게르다",
    148: "아…… 그건…….",
    149: "후우, 깊은 한숨을 내쉬고^n게르다는 벽난로 위의 『성서』로 시선을 돌렸다.",
    150: "동요에 동요를 거듭한 끝에,^n도리어 마음을 가라앉히려는 듯하다.",
    151: "게르다",
    152: "──무서워. 저걸 보고 있으면.^n내가 내가 아니게 될 것 같아서 현기증이 나.",
    153: "게르다",
    154: "차라리 불태워 버리면 편해질까.^n하지만──그것도 무서워.",
    155: "어딘가 생기를 잃은 모습으로 눈을 감는 게르다를 보고,^n나는 이제야 강한 죄책감을 느꼈다.",
    156: "나",
    157: "──미안해. 널 혼란스럽게 해서.",
    158: "게르다",
    159: "사과하지 마.^n나도 내가 이렇게 불안정하다는 게 부끄러워.",
    160: "게르다는 씩씩하게 대답했지만,^n더는 그녀의 허세에 기대서는 안 된다고 생각했다.",
    161: "나는 일어나 다시 한번 사과의 말을 남기고,^n게르다의 방을 뒤로했다.",
}


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1114.gsc" and item.get("slot") in TARGETS:
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
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1114_slots_00121_00161_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1114_slots_00121_00161_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
