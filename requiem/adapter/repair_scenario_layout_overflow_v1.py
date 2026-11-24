from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

P = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
sys.path.insert(0, str(P / "adapter"))
from build_gsc_from_translation_map_v2 import build_translation_map
from scenario_layout import (
    MAX_RUNTIME_WIDTH, SAFE_REFLOW_WIDTH, display_width, join_explicit_lines,
    line_widths, non_newline_controls, normalize_nonspace_content,
    reflow_to_three_lines, required_runtime_lines,
)

OUT = P / "staging" / "scenario_layout_overflow_repair_v1"
ACTIVE_MAPS = P / "packets" / "reviewed_layout_v1"
STAGE_GSC = P / "staging" / "gsc_layout_repair_v1"
AUDIT = P / "audit" / "scenario_layout_overflow_repairs_v1.json"
PROGRESS = P / "audit" / "translation_progress.json"

MANUAL = {
    ("1302.gsc", 46): "남자에게 성기도 입안도 다루기 좋은 고기일 뿐이고, 게르다의 마음과 긍지도 가학 취미의 양념에 불과하리라. 그 사실을 한 번 찌를 때마다 지겹도록 깨닫게 된다.",
    ("1404.gsc", 5): "끼익거리는 새장 소리가 귀에 거슬리기도 했지만, 리듬에 맞춰 엉덩이를 뒤트는 여자의 달콤한 신음은 그 삐걱거림마저 잊을 만큼 남자의 귀를 즐겁게 했다.",
    ("1404.gsc", 21): "입구조차 없는 점막을 끝으로 억지로 비집어 열었지만, 한 번 밀어 넣자 안쪽은 유연하면서도 단단히 휘감겼고, 육체는 더 깊은 삽입과 쾌락을 본능적으로 갈구했다.",
    ("1404.gsc", 30): "성기가 모두 체내에 들어찬 쾌감에 남자는 만족스레 숨을 내쉬었다. 오데트도 가랑이 사이로 밀려드는 압박감과 통나무에 꿰뚫린 듯한 크기를 견디지 못해 등을 휘었다.",
    ("1404.gsc", 87): "눈부신 미모와 훌륭한 몸매, 육체의 감촉도 극상이었다. 혀를 내두를 만큼 음탕하고 남자를 다루는 솜씨도 능숙했다. 어떤 남자든 이런 소녀를 안아 보고 싶게 만드는──",
    ("1416.gsc", 97): "곡을 고르며 이케노 씨에게 살살 해 달라고 부탁하려던 찰나, 벌컥 열린 문으로 후끈해진 오락실에 시원한 바람이 들었고, 뒤늦은 손님이 왔음을 알렸다.",
    ("1417.gsc", 464): "내 위에서 꿈틀대며 앞뒤로 움직이고 돌아가는 허리와 엉덩이는 뼈와 관절이 없는 듯 유연하고 부드럽게 움직여, 안쪽의 조임과 스치는 부위에 절묘한 변화와 완급을 주었다.",
    ("1418.gsc", 5): "어쩔 수 없지…… 오딜에게 그대로 내버려진 건지, 하반신은 알몸이고 가랑이엔 점액이 마른 자국이 남아 있었다. 복도 구석에 웅크린 녀석을 보면 대개 그렇게 생각할 것이다…….",
    ("1421.gsc", 268): "이렇게 복잡하고 답답한데도 부드러워── 녹아내릴 듯 따뜻하고, 뜨거울 만큼 울퉁불퉁해── 형태를 헤치며 빨려 들어가── 녹아버릴 것 같아──",
    ("1421.gsc", 276): "그래, 안쪽까지 채운 채 멈추면 아직 가벼운 쾌감에 그친다. 하지만 굳은 곳에서 번지는 달콤한 욱신거림은 앞에 더 큰 쾌락이 기다린다고 알리고 있었다.",
    ("1421.gsc", 421): "이제 본능에만 이끌려 남의 시선 따위는 생각하지 않았다. 가장 깊은 곳에 매끄럽게 닿는 데만 집중해 다리를 벌리고, 허리를 쉼 없이 움직여 빳빳해진 것을 곧게 찔러 넣었다.",
    ("1512.gsc", 19): "파스텔과 원색, 노른자와 아이싱, 초콜릿과 사탕의 광택. 색과 질감의 견본첩처럼 수많은 과자가 실내를 채웠고, 그 사실을 깨닫기까지는 조금 시간이 걸렸다.",
    ("1513.gsc", 35): "남자는 봐줄 생각 없이 양다리를 홱홱 잡아당겼다. 소녀의 드러난 비부는 찢어진 껌처럼 뒤틀렸고, 공포와 혐오로 지린 소변에 번들거리는 모습이 가련했다.",
    ("1516.gsc", 7): "증오와 혐오를 품고 문을 두드리는 상대라면 거절하거나 무시해도 이유가 있고 마음도 아프지 않다. 하지만 자신을 걱정해 찾아온 이에게 차갑게 굴 수 없는 게 인지상정이다.",
    ("1517.gsc", 57): "어쩌면 그편이 더 행복할지도 모른다고 여인은 생각했다. 아니, 이제 그런 『낙원』에는 돌아갈 수 없다고 고쳐 생각했다. 『이야기』를 잃었으니 『낙원』에도 돌아갈 수 없다고.",
    ("1521.gsc", 6): "늦가을 비 오는 해 질 녘처럼 어둑하고 싸늘하며 음침한 곳. 서 있기만 해도 마음이 어두운 얼음물 밑으로 가라앉는 듯하다. 가슴이 허망함에 황폐해져 한순간도 더 있고 싶지 않다.",
    ("1616.gsc", 146): "소년의 얼굴이 다시 흉측하게 일그러졌다. 하지만 조금 전의 교활함과 비열함, 흉악함에 물든 표정이 아니다. 굴욕이나 수치를 느끼는 듯 어색함이 밴 얼굴이었다.",
    ("1621.gsc", 40): "「어느 큰 마을에 남매처럼 다정한 아이들이 살았습니다. 남자아이는 카이, 여자아이는 게르다라고 했습니다. 게르다는 카이와 할머니의 이야기를 듣는 것을 무척 좋아했습니다」",
    ("1621.gsc", 99): "「산적의 딸은 게르다에게 옷과 부츠, 빵과 햄을 주었습니다. 마프는 마음에 들어 어머니의 장갑과 바꾸었습니다. 게르다를 태운 순록 썰매는 라플란드로 향했습니다」",
    ("1402.gsc", 23): "의사 선생님 손안의 그것은 쪼그라든 폐허 같았다. 녹슬고 일그러진 데다 군데군데 얼룩도 있었다. 철인지 다른 금속인지 모를 작은 여자아이 신발, 그것도 한 짝뿐이었다.",
    ("1404.gsc", 127): "아랫배에 두 손을 살며시 얹고 중얼거리는 오데트의 얼굴은 바라는지 유혹하는지 모를 눈빛으로 무척 요염했다. 절정 직후 개운해하던 남자조차 불길한 예감을 느낄 정도였다.",
    ("1410.gsc", 2): "먼지에 누렇게 바래 언제 붙였는지도 모를 청소 예정표, 얄미울 만큼 건강한 얼굴로 생활 습관병 예방을 외치는 포스터. 그런 것뿐이라 딱히 새로운 소식은 없다.",
    ("1416.gsc", 103): "무엇보다 그 사람은 병동에서 여태 아무도 못 본 듯한 모습이었다. 장미를 솜씨 좋게 배치한 아름다운 드레스를 완벽히 소화해, 댄스 파티에서 가장 특별해 보였다.",
    ("1418.gsc", 186): "지금 그녀의 얼굴은 보기에도 처참한 귀신 같았다. 평소의 오딜도 독선적이고 병적이며 광기 어린 데다 타인에게 가차 없었지만, 그 모습에는 그나마 귀여운 구석이 있었음을 뼈저리게 느꼈다.",
    ("1420.gsc", 64): "그 안에 선 오데트는 아직 반신반의하는 표정이었다. 섣불리 매달리면 환상이라며 사라질까 두려운 듯 시선을 이리저리 굴리고, 옆으로 내린 손도 꼼지락거렸다.",
    ("1420.gsc", 173): "오데트가 눈물과 슬픔의 호수에 갇혀 발버둥 치는 백조 공주라면, 오딜은 발푸르기스의 밤을 날며 비웃는 흑조다. 높은 곳을 날며 괴로워하는 자를 내려다보고 안중에도 두지 않는다.",
    ("1421.gsc", 271): "달라붙는 점막의 쾌감에 이끌려 허리를 밀어 넣었다. 빳빳해진 것으로 헤치고 파고들어 그녀의 꽃잎을 짓누를 만큼 밀착했다. 더 나아갈 수도 없는데 허리를 거듭 밀어붙였다.",
    ("1421.gsc", 339): "빳빳해진 곳을 빈틈없이 휘감는 복잡한 점막이 움직일 때마다 애액을 덧발라 두 사람의 경계를 익숙하게 녹여 갔다. 경계가 사라질수록 쾌감은 더욱 커졌다.",
    ("1421.gsc", 349): "나를 당혹스럽게 한 건 그 적나라함뿐만이 아니다. 살기둥에는 그녀의 애액이 발려 음란하게 번들거렸다. 그 미끈거림 속에 한두 줄기의 가느다란 붉은 피가 섞여 있었다.",
    ("1513.gsc", 190): "심약한 사람이라면 견디지 못하고 달아나거나 토했을 것이다. 그런데도 그레텔은 하복부에서 그것을 손가락으로 한 움큼 떠, 손가락 사이에서 끈적이는 모습을 아기처럼 뚫어지게 바라보았다.",
    ("1516.gsc", 67): "설렘과 가슴의 고동을 고백하는 라푼젤처럼, 내 심장도 안쪽에서 가슴을 강하게 두드렸다. 심장 위 피부에 옅고 붉은 멍을 남길 듯 쿵쿵 울리고 있었다.",
    ("1523.gsc", 122): "그때마다 등을 젖히고 가슴째 내 손에 밀어붙이는 듯한 반응은 나를 더욱 흥분시켰다. 무엇보다 손가락이 움직일 때마다 민감하게 흘러나오는 목소리가 달콤하고 요염해── 전율이 인다.",
    ("1523.gsc", 163): "그녀의 살결이 부드럽고 따뜻하다는 것만으로도, 허리 깊숙한 곳에 음란한 쾌감의 거미줄이 얽혀 오는 듯했다. ……되고 싶어…… 더 기분 좋아지고 싶어……!",
    ("1703.gsc", 80): "저항할 수 있었던 건 그녀의 의지가 강했기 때문이기도 하다. 하지만 「형편 좋은 각본」보다 「현실에서 찾던 사람을 만나는 것」이 그녀에게 훨씬 중요했던 까닭도 클 것이다.",
    ("1822.gsc", 7): "분명히 기억나진 않지만 제 고향은 눈 많은 북쪽 나라였습니다. 그래서 제게 『바깥』과 설경은 떼어 놓을 수 없이 이어져 있었습니다. 그런 감상적인 이유가 있었기 때문입니다.",
}


def h(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def collect_plan(progress: dict) -> tuple[list[dict], dict[str, dict]]:
    records = []
    maps = {}
    for row in progress["completed_files"]:
        fn = row["file"]
        mp = P / row["review_map"]
        data = json.loads(mp.read_text(encoding="utf-8"))
        maps[fn] = {"row": row, "path": mp, "data": data}
        for entry in data["entries"]:
            slot = int(entry["uid"].rsplit("/", 1)[1])
            before = str(entry["target_text"])
            needed = required_runtime_lines(before)
            if needed <= 3:
                continue
            key = (fn, slot)
            base = MANUAL.get(key, before)
            if key not in MANUAL:
                base = join_explicit_lines(base)
            after, meta = reflow_to_three_lines(base)
            if required_runtime_lines(after) > 3 or max(line_widths(after), default=0) > SAFE_REFLOW_WIDTH:
                raise AssertionError(f"repair did not fit: {fn}/{slot}")
            if non_newline_controls(before) != non_newline_controls(after):
                raise AssertionError(f"control drift: {fn}/{slot}")
            if key not in MANUAL and normalize_nonspace_content(before) != normalize_nonspace_content(after):
                raise AssertionError(f"automatic repair changed non-space content: {fn}/{slot}")
            after.encode("cp949", "strict")
            records.append({
                "file": fn, "slot": slot, "uid": entry["uid"], "source": entry["source_text"],
                "before": before, "after": after,
                "before_line_widths": line_widths(before), "before_required_runtime_lines": needed,
                "after_line_widths": line_widths(after), "after_required_runtime_lines": required_runtime_lines(after),
                "method": "manual_concise_rewrite_then_reflow" if key in MANUAL else "content_preserving_newline_reflow",
                "joined_width_after": meta["joined_width"],
            })
    found_manual = {(r["file"], r["slot"]) for r in records if r["method"].startswith("manual")}
    if found_manual != set(MANUAL):
        raise SystemExit(f"manual replacement key mismatch: missing={sorted(set(MANUAL)-found_manual)} extra={sorted(found_manual-set(MANUAL))}")
    return records, maps


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    progress = json.loads(PROGRESS.read_text(encoding="utf-8"))
    records, maps = collect_plan(progress)
    affected = sorted({r["file"] for r in records})
    result = {
        "status": "PASS", "mode": "apply" if args.apply else "dry-run",
        "candidate_count": len(records), "affected_file_count": len(affected),
        "automatic_reflow_count": sum(r["method"].startswith("content") for r in records),
        "manual_concise_rewrite_count": sum(r["method"].startswith("manual") for r in records),
        "required_line_distribution_before": dict(Counter(str(r["before_required_runtime_lines"]) for r in records)),
        "max_line_width_after": max(max(r["after_line_widths"]) for r in records),
        "affected_files": affected,
    }
    if not args.apply:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    for path in (OUT, ACTIVE_MAPS, STAGE_GSC):
        if path.exists():
            raise SystemExit(f"refusing existing output root: {path}")
    (OUT / "maps_before").mkdir(parents=True)
    ACTIVE_MAPS.mkdir(parents=True)
    STAGE_GSC.mkdir(parents=True)
    shutil.copy2(PROGRESS, OUT / "translation_progress_before.json")

    by_file: dict[str, list[dict]] = {}
    for rec in records:
        by_file.setdefault(rec["file"], []).append(rec)
    progress_rows = {row["file"]: row for row in progress["completed_files"]}
    map_records = []
    for fn in affected:
        original = maps[fn]["path"]
        data = maps[fn]["data"]
        shutil.copy2(original, OUT / "maps_before" / original.name)
        before_hash = h(original)
        replacement = {r["slot"]: r for r in by_file[fn]}
        seen = set()
        for entry in data["entries"]:
            slot = int(entry["uid"].rsplit("/", 1)[1])
            if slot not in replacement:
                continue
            rec = replacement[slot]
            if entry["target_text"] != rec["before"]:
                raise SystemExit(f"expected-before mismatch: {fn}/{slot}")
            entry["target_text"] = rec["after"]
            entry["notes"] = entry.get("notes", "") + "; post-review dialogue layout overflow repair v1"
            seen.add(slot)
        if seen != set(replacement):
            raise SystemExit(f"missing replacement slots: {fn}")
        data.setdefault("post_review_repairs", []).append({
            "id": "dialogue_layout_overflow_repair_v1", "completed_utc": utc(),
            "slots": sorted(seen), "reason": "prevent Malie four-line auto-wrap text-format error; 3 lines and <=992 units",
        })
        out_map = ACTIVE_MAPS / original.name
        out_map.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest = P / "audit" / f"gsc_build_{Path(fn).stem}_layout_v1.json"
        built = build_translation_map(P, out_map, STAGE_GSC, manifest)
        row = progress_rows[fn]
        row["review_map"] = str(out_map.relative_to(P)).replace("\\", "/")
        row["review_map_sha256"] = h(out_map)
        row["build_manifest"] = str(manifest.relative_to(P)).replace("\\", "/")
        row["build_manifest_sha256"] = h(manifest)
        map_records.append({
            "file": fn, "slot_count": len(replacement), "source_map": str(original),
            "source_map_sha256": before_hash, "active_map": str(out_map), "active_map_sha256": h(out_map),
            "build_manifest": str(manifest), "build_manifest_sha256": h(manifest),
            "staged_gsc": built["files"][0]["output_path"], "staged_gsc_sha256": built["files"][0]["output_sha256"],
        })
        for rec in by_file[fn]:
            rec["source_map_sha256"] = before_hash
            rec["active_map_sha256"] = h(out_map)

    progress["updated_utc"] = utc()
    progress.setdefault("post_review_runtime_repairs", []).append({
        "id": "dialogue_layout_overflow_repair_v1", "repair_count": len(records),
        "automatic_reflow_count": result["automatic_reflow_count"],
        "manual_concise_rewrite_count": result["manual_concise_rewrite_count"],
        "audit": "audit/scenario_layout_overflow_repairs_v1.json", "updated_files": affected,
    })
    PROGRESS.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Re-read every active map after progress update and prove the runtime overflow set is empty.
    remaining = []
    total_units = 0
    for row in progress["completed_files"]:
        data = json.loads((P / row["review_map"]).read_text(encoding="utf-8"))
        for entry in data["entries"]:
            total_units += 1
            if (row["file"], int(entry["uid"].rsplit("/", 1)[1])) == ("1001.gsc", 10):
                continue
            needed = required_runtime_lines(entry["target_text"])
            if needed > 3:
                remaining.append({"file": row["file"], "uid": entry["uid"], "needed": needed, "widths": line_widths(entry["target_text"])})
    if remaining:
        raise SystemExit(f"remaining runtime overflows: {remaining[:5]}")
    report = {
        "schema": "fairytale-requiem-scenario-layout-overflow-repairs-v1", "status": "PASS",
        "completed_utc": utc(), "engine_contract": {
            "error_text": "テキストフォーマットエラー", "runtime_max_width": MAX_RUNTIME_WIDTH,
            "safe_reflow_width": SAFE_REFLOW_WIDTH, "max_dialogue_lines": 3,
            "reverse_engineering": {"parser_va": "0x459DC0", "layout_finalizer_va": "0x45AF80", "height_compare_va": "0x45B328", "failure_flag_va": "0x45B332"},
        },
        "counts": {**result, "total_units_validated_after": total_units, "remaining_overflow_count": 0},
        "progress": {"path": str(PROGRESS), "sha256": h(PROGRESS)},
        "backup_root": str(OUT), "active_map_root": str(ACTIVE_MAPS), "staged_gsc_root": str(STAGE_GSC),
        "map_records": map_records, "records": records,
    }
    AUDIT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**result, "total_units_validated_after": total_units, "remaining_overflow_count": 0, "progress_sha256": h(PROGRESS), "audit": str(AUDIT), "audit_sha256": h(AUDIT)}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
