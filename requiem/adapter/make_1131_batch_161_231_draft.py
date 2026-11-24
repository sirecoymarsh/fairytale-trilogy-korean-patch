from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TARGETS = {
    161: "라푼젤",
    162: "…………!",
    163: "라푼젤이 숨을 삼키며 비틀거렸다.",
    164: "나",
    165: "왜 그래, 라푼젤……?",
    166: "라푼젤",
    167: "……읏, 으…….",
    168: "말을 걸어도 라푼젤은 낮게 신음할 뿐.",
    169: "크게 뜬 눈으로 나를 보고 있다.^n나를 통해 지옥을 보는 듯 팽팽하게 긴장한 눈빛.",
    170: "내 뒤에 무언가 무서운 게 있나 생각해^n순간 소름이 돋을 만큼,^n라푼젤의 눈동자에는 공포가 응축되어 있었다.",
    171: "나",
    172: "(뭐, 뭐지. 왜 저러는 거지)",
    173: "비밀을 지적했을 때보다^n훨씬 큰 충격을 받은 듯한 라푼젤에게,^n나는 어떻게 대해야 할지 몰라졌다.",
    174: "나",
    175: "저, 저기…….",
    176: "라푼젤",
    177: "──읏!",
    178: "이윽고 비명 같은 가쁜 숨을 남기고,^n라푼젤은 몸을 홱 돌렸다.",
    179: "몸을 덮고 있던 후드가 벗겨져,^n펄럭이며 발밑에 떨어진다──",
    180: "그때 라푼젤은 이미 문 너머로 사라진 뒤였다.",
    181: "나",
    182: "(──왜 저러는 걸까, 라푼젤)",
    183: "뒤를 쫓아 나선계단을 내려가 복도로 돌아간다.",
    184: "라푼젤은 앞뒤 가리지 않을 기세로 달려간 듯,^n복도에는 그녀의 모습이 없다.",
    185: "대신,^n그녀를 보고 놀란 어른들이,^n아직도 멍하니 그녀가 달려간 쪽을 바라보고 있었다.",
    186: "직원",
    187: "대체 무슨 일이야.^n라푼젤이 방을 나오는 건 처음 봤어.",
    188: "직원",
    189: "그러게. 실제로 처음인 거 아냐?^n진찰도 목욕도 언제나 방에서 다 해결했잖아.",
    190: "직원",
    191: "네, 정말요?^n하지만 눈앞에서 문이 열리고 사람이 드나드는 건 봤을 테고,^n딱히 문을 잠가 두지도 않았잖아요.",
    192: "직원",
    193: "『할 수』 있지만 『하지 않는』, 『할 수 없는』 거야.^n그런 설정──아니, 병세니까.",
    194: "직원",
    195: "『자기를 위한 문이 아니다』──^n전에 그렇게 말했던가.",
    196: "직원",
    197: "하아…… 어렵네요.",
    198: "직원",
    199: "그런데 오늘은 갑자기 밖으로 나왔다고.^n병세가 호전된 건지 악화된 건지──보통 일이 아니야.^n일단 보고해야겠어.",
    200: "나",
    201: "(이건…… 혹시, 혹시고 뭐고^n큰일이 나 버린 건가……)",
    202: "오가는 대화를 들으며 라푼젤을 찾다가,^n나는 이케노 씨와 마주쳤다.",
    203: "이케노 씨는 이미 무슨 일이 있었는지 들은 듯,^n내게 몸을 숙여 소곤소곤 말을 걸었다.",
    204: "이케노",
    205: "──라푼젤이 나갔다던데…….^n너, 무슨 짓 했어?",
    206: "왜 원인이 내게 있다고 생각한 걸까.",
    207: "나",
    208: "했다고 하면 한 건가…….",
    209: "털어놓을 상대를 찾았다는 안도감에,^n하지만 시작부터 나는 말을 더듬었다.",
    210: "경위를 따라가면 너무나 떳떳하지 못해서,^n도저히 모든 걸 말할 수는 없다.",
    211: "나",
    212: "(어젯밤 본 건^n『한밤중에 라푼젤의 방으로 머리카락을 타고 들어가는 사람을 봤다』^n라고 바꾸어 말하면 어떻게든……)",
    213: "그 사실을 경솔하게 그녀에게 말한 것,^n무의식적으로 배를 쓰다듬는 그녀를 보고 『남녀 쌍둥이를 낳았던가』^n하고 중얼거리자, 아무래도 마지막 방아쇠를 당겨 버린 것.",
    214: "──어떻게든 앞뒤를 맞춰 전달한 것 같다.",
    215: "이케노",
    216: "아, 그렇구나…….",
    217: "이케노",
    218: "그러니까 라푼젤은 『할머니』인 너에게^n임신 사실을 들켰다고 생각해서,^n탑에서 쫓겨나는 줄거리를 따른 거구나.",
    219: "나",
    220: "역시 그런 건가요…….",
    221: "이케노",
    222: "뭐, 마음 쓰지 마.^n『라푼젤』이 원래 그런 이야기였을 뿐이니까.",
    223: "이케노",
    224: "게다가──이번 일은^n『없었던 일』이 되지 않을까.",
    225: "나",
    226: "……?^n그럴까요…….",
    227: "나는 그 말에 매달리듯 이케노 씨를 올려다보았다.",
    228: "어쨌든 내가 쓸데없는 말을 해서^n라푼젤을 공황 상태로 몰아넣은 건 틀림없다.^n없던 일로 만들 수 있다면 그렇게 되길 바랐다.",
    229: "이케노 씨는 방긋 웃으며,^n내게는 잘 이해되지 않는 말을 꺼냈다.",
    230: "이케노",
    231: "──아직 그 애의 머리카락은 긴 그대로니까.",
}
CARET_RE = re.compile(r"\^(?:n|d\d+)")


def main() -> int:
    rows = {}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item.get("file") == "1131.gsc" and item.get("slot") in TARGETS: rows[int(item["slot"])] = item
    if set(rows) != set(TARGETS): raise SystemExit("catalog mismatch")
    entries = []
    for index in sorted(TARGETS):
        source, target = str(rows[index]["source_text"]), TARGETS[index]
        if CARET_RE.findall(source) != CARET_RE.findall(target): raise SystemExit(f"caret mismatch {index}")
        target.encode("cp949", errors="strict")
        entries.append({"uid": rows[index]["uid"], "source_text": source, "source_raw_sha256": rows[index]["source_raw_sha256"], "target_text": target, "translator": "Codex internal model draft", "review_status": "draft_pending_single_review", "notes": "초벌 번역; 1차 검수 전"})
    output = {"schema": "fairytale-requiem-translation-map-v1", "scope": "1131_slots_00161_00231_draft", "semantic_source": "ja-JP", "target_language": "ko-KR", "target_encoding": "cp949", "translation_method": "Codex internal model only; no external MT/API", "review_passes_completed": 0, "release_ready": False, "entries": entries}
    out = PROJECT / "packets" / "drafts" / "1131_slots_00161_00231_draft.json"
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(out), "entries": len(entries), "sha256": hashlib.sha256(out.read_bytes()).hexdigest().upper()}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())
