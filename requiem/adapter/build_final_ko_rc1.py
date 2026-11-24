from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
SOURCE = PROJECT / "runtime" / "trial_ko"
CANDIDATE = PROJECT / "runtime" / "final_ko_rc1"
AUDIT = PROJECT / "audit"

EXPECTED_KEY_HASHES = {
    "grpe.xfl": "1507AEF748969562C7EE730C4EEABEAA9737063BA1FB73E475FCAD1AE8E95178",
    "grpo.xfl": "D45A668DE5F04F5AC3DD7831072B779ABF24906151C81C6A3B691E6F5EFD3339",
    "grpo_ex.xfl": "688A19B76EDF2CA88866EDFC816164DE654607BE22F103BB2ECF040B510A2F10",
    "grpo_lib.xfl": "D37506519A79F483AFE2D20E4AB6E62CBC0E03FE572847EDB29279742B7217B2",
    "grpo_map.xfl": "49BF17585464E060FFC5195A247FE83932F804D7D83791EC7AC51825A6034C70",
    "grpo_skc.xfl": "D67769DF9153A5DC32161ABB8371290118CA0CE8DB64BB60E909B603F15FA9DF",
    "grps.xfl": "51AD7E68327C6F35D08E8A003CAD3C3336FCF43C1C9AF9F723310B3E3EBDD3F2",
    "scr.xfl": "C3FDAA6DEB4B00AD292B1BB272F2E7CA2664F1F3A54B1DCB9AD96F89962D3C1C",
    "\u30d5\u30a7\u30a2\u30ea\u30fc\u30c6\u30a4\u30eb\u30fb\u30ec\u30af\u30a4\u30a8\u30e0.exe": "E46F532811B3189669CCC74452A2BFB4F0F14362EF97E68018FC9CDC26B2B4F4",
    "mov/0001.mpg": "95EF695AD950C46E60508399B8CF116F255145AF6B74114C0E36AE44E315A536",
}

sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')

KST = timezone(timedelta(hours=9))
NOW = datetime.now(KST).isoformat(timespec="seconds")


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest().upper()


def tree_manifest(root: Path) -> list[dict]:
    rows: list[dict] = []
    files = sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: p.relative_to(root).as_posix().casefold())
    for idx, path in enumerate(files, 1):
        rel = path.relative_to(root).as_posix()
        size = path.stat().st_size
        digest = sha256_file(path)
        rows.append({"path": rel, "size": size, "sha256": digest})
        print(f"HASH {idx:03d}/{len(files):03d} {rel} {size} {digest}", flush=True)
    return rows


def rows_by_path(rows: list[dict]) -> dict[str, dict]:
    return {row["path"]: row for row in rows}


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if not SOURCE.is_dir():
    raise SystemExit(f"source build missing: {SOURCE}")
if CANDIDATE.exists():
    raise SystemExit(f"fresh candidate root already exists; refusing overwrite: {CANDIDATE}")

print("PHASE source_manifest", flush=True)
source_rows = tree_manifest(SOURCE)
source_map = rows_by_path(source_rows)

key_checks: list[dict] = []
for rel, expected in EXPECTED_KEY_HASHES.items():
    actual_row = source_map.get(rel)
    actual = actual_row["sha256"] if actual_row else None
    ok = actual == expected
    key_checks.append({"path": rel, "expected_sha256": expected, "actual_sha256": actual, "ok": ok})
if not all(row["ok"] for row in key_checks):
    write_json(AUDIT / "final_ko_rc1_preflight_failed.json", {
        "schema": "fairytale-requiem-final-build-preflight-v1",
        "created_at_kst": NOW,
        "status": "FAIL_KEY_HASH",
        "source_root": str(SOURCE),
        "key_checks": key_checks,
    })
    raise SystemExit("source key hash preflight failed")

print("PHASE copy", flush=True)
shutil.copytree(SOURCE, CANDIDATE, copy_function=shutil.copy2)

print("PHASE candidate_manifest", flush=True)
candidate_rows = tree_manifest(CANDIDATE)

source_map = rows_by_path(source_rows)
candidate_map = rows_by_path(candidate_rows)
path_set_equal = set(source_map) == set(candidate_map)
mismatches: list[dict] = []
for rel in sorted(set(source_map) | set(candidate_map), key=str.casefold):
    s = source_map.get(rel)
    d = candidate_map.get(rel)
    if s != d:
        mismatches.append({"path": rel, "source": s, "candidate": d})

save_rows = [r for r in candidate_rows if r["path"].startswith("save/")]
loose_help = [candidate_map.get(f"grpe/{n}.wcg") for n in (9901, 9902, 9903, 9904)]
loose_help_ok = all(loose_help)
status = "PASS_STATIC_RUNTIME_PENDING" if path_set_equal and not mismatches and loose_help_ok else "FAIL"

manifest = {
    "schema": "fairytale-requiem-final-build-candidate-v1",
    "created_at_kst": NOW,
    "status": status,
    "delivery_stage": "FINAL_BUILD_CANDIDATE_ONLY",
    "patch_packaging": "DEFERRED_UNTIL_FINAL_BUILD_RUNTIME_APPROVAL",
    "source_root": str(SOURCE),
    "candidate_root": str(CANDIDATE),
    "file_count": len(candidate_rows),
    "total_bytes": sum(r["size"] for r in candidate_rows),
    "path_set_equal": path_set_equal,
    "byte_identity_mismatch_count": len(mismatches),
    "mismatches": mismatches,
    "key_hash_checks": key_checks,
    "loose_help_overrides_present": loose_help_ok,
    "test_save_files": {
        "included_for_user_runtime_test": True,
        "count": len(save_rows),
        "later_patch_payload_policy": "EXCLUDE",
        "files": save_rows,
    },
    "runtime_qa": "PENDING",
    "files": candidate_rows,
}
write_json(AUDIT / "final_ko_rc1_manifest.json", manifest)

surface_inventory = {
    "schema": "fairytale-requiem-surface-inventory-v2",
    "created_at_kst": NOW,
    "bound_candidate": {
        "root": str(CANDIDATE),
        "manifest": str(AUDIT / "final_ko_rc1_manifest.json"),
        "status": status,
    },
    "overall": "PASS_STATIC_RUNTIME_PENDING" if status == "PASS_STATIC_RUNTIME_PENDING" else "FAIL",
    "policy": {
        "patch_packaging": "DEFERRED_UNTIL_FINAL_BUILD_RUNTIME_APPROVAL",
        "test_saves": "INCLUDED_IN_BUILD_FOR_USER_TEST_ONLY; EXCLUDE_FROM_LATER_PATCH",
        "original_staff_credits": "PRESERVE_ORIGINAL_ATTRIBUTION",
        "kinetic_cutin_text": "DEFERRED_BY_USER_FOR_LATER_INCREMENTAL_WORK",
    },
    "lanes": [
        {
            "id": "scenario_core",
            "surface": "본편 대사·독백·선택지·시스템 문구",
            "storage": "scr.xfl",
            "coverage": {"script_files": 233, "translation_units": 29376},
            "status": "PASS_STATIC_RUNTIME_PENDING",
            "evidence": ["audit/scenario_global_independent_validation_v2.json", "audit/scr_ko_full_v2_build.json"],
        },
        {
            "id": "scenario_runtime_format_repairs",
            "surface": "진행 중 반복되던 텍스트 형식 오류 원인 문자열",
            "storage": "scr.xfl",
            "coverage": {"script_files": 4, "repaired_slots": 7, "files": [1614, 1701, 1702, 1728]},
            "status": "PASS_STATIC_RUNTIME_PENDING",
            "evidence": ["audit/scenario_runtime_text_format_repairs_v1.json", "audit/scenario_global_independent_validation_v2.json"],
        },
        {
            "id": "sensitive_scenarios",
            "surface": "성인·민감 장면",
            "storage": "scr.xfl",
            "status": "INCLUDED_IN_MAIN_BUILD_RUNTIME_PENDING",
            "separate_review_bundle": "REBUILD_AT_PATCH_STAGE_FROM_FINAL_APPROVED_BYTES",
        },
        {
            "id": "title_logo",
            "surface": "타이틀 로고 8개 애니메이션 상태",
            "storage": "grpe.xfl::9101.lwg",
            "status": "PASS_STATIC_RUNTIME_PENDING",
            "evidence": ["audit/grpe_title_logo_korean_v1_independent_validation.json", "audit/grpe_title_logo_korean_v1_runtime_install.json"],
        },
        {
            "id": "title_menu",
            "surface": "시작·계속·감상·설정·종료 및 보조 상태",
            "storage": "grpo.xfl",
            "coverage": {"localized_states": 15},
            "status": "PASS_STATIC_RUNTIME_PENDING",
            "evidence": ["audit/grpo_component_donor_runtime_promotion.json"],
        },
        {
            "id": "gallery_hub_and_map",
            "surface": "CG 감상·장면 감상·BGM 감상·스케치북·책장 및 날짜·장소",
            "storage": "grpo_map.xfl",
            "coverage": {"date_location_surfaces": 88, "gallery_labels": 5},
            "status": "PASS_STATIC_RUNTIME_PENDING",
            "evidence": ["audit/grpo_map_korean_ui_v4_runtime_promotion.json", "audit/grpo_map_gallery_labels_korean_v1_build.json"],
        },
        {
            "id": "gallery_headers",
            "surface": "CG 감상·장면 감상·BGM 감상 화면 제목",
            "storage": "grpe.xfl::9001-9003",
            "coverage": {"localized_headers": 3},
            "status": "PASS_STATIC_RUNTIME_PENDING",
            "evidence": ["audit/grpe_gallery_headers_korean_v1_build.json"],
        },
        {
            "id": "save_load_config_panels",
            "surface": "저장·불러오기·환경 설정·조작 패널 및 저장 메타데이터",
            "storage": "grps.xfl",
            "coverage": {"save_metadata_changes": 652},
            "status": "PASS_STATIC_RUNTIME_PENDING",
            "evidence": ["audit/grps_compane_confscrn_savescrn_runtime_promotion.json", "audit/grps_save_metadata_korean_v1_independent_validation.json"],
        },
        {
            "id": "title_and_route_surfaces",
            "surface": "장·일자 제목 및 관련 화면",
            "storage": "grpo_ex.xfl",
            "coverage": {"localized_surfaces": 462},
            "status": "PASS_STATIC_RUNTIME_PENDING",
            "evidence": ["audit/grpo_ex_korean_titles_v2_runtime_promotion.json"],
        },
        {
            "id": "sketchbook_routes",
            "surface": "스케치북 탭·페이지·추억·루트",
            "storage": "grpo_skc.xfl",
            "coverage": {"localized_surfaces": 69},
            "status": "PASS_STATIC_RUNTIME_PENDING",
            "evidence": ["audit/grpo_skc_korean_ui_v3_runtime_promotion.json"],
        },
        {
            "id": "library_surfaces",
            "surface": "책등·이야기 페이지·신문",
            "storage": "grpo_lib.xfl",
            "coverage": {"localized_surfaces": 49},
            "status": "PASS_STATIC_RUNTIME_PENDING",
            "evidence": ["audit/grpo_lib_korean_ui_v3_runtime_promotion.json"],
        },
        {
            "id": "help_pages",
            "surface": "환경 설정·글꼴·텍스트 조작·게임 안내 4면",
            "storage": "grpe/9901.wcg-9904.wcg",
            "coverage": {"localized_pages": 4},
            "status": "PASS_STATIC_RUNTIME_PENDING",
            "evidence": ["staging/current_help_pages_review"],
        },
        {
            "id": "opening_movie",
            "surface": "오프닝 영상 한국어 가사 자막",
            "storage": "mov/0001.mpg",
            "status": "PASS_STATIC_RUNTIME_PENDING",
            "evidence": ["audit/opening_movie_korean_subtitles_v2_build.json", "audit/opening_movie_korean_subtitles_v2_runtime_install.json"],
        },
        {
            "id": "nontext_ui_archives",
            "surface": "배경·선택 효과·후처리·연출 효과 계열",
            "storage": "grpo_bg.xfl, grpo_sel.xfl, grpo_pp.xfl, grpo_ef.xfl",
            "status": "PASS_NO_CONFIRMED_VISIBLE_TEXT_TARGETS",
        },
        {
            "id": "kinetic_cutin_text",
            "surface": "화면에 탄막처럼 펼쳐지는 연출 글자",
            "storage": "grpo_cu.xfl (confirmed example: 5022.wcg)",
            "status": "DEFERRED_BY_USER",
            "reason": "사용자가 현재 작업 완료 후 차근차근 별도 처리하기로 지정",
        },
        {
            "id": "original_staff_credit_plate",
            "surface": "원 제작진 크레디트 정지 화면",
            "storage": "grpe.xfl::3022.wcg",
            "status": "PRESERVED_ORIGINAL_ATTRIBUTION",
            "reason": "제작진 고유 표기와 원작 미술을 그대로 보존",
        },
        {
            "id": "ending_credit_movies",
            "surface": "엔딩 제작진 크레디트 영상",
            "storage": "mov/0011.mpg, mov/0012.mpg, mov/0013.mpg",
            "status": "PRESERVED_ORIGINAL_ATTRIBUTION",
            "reason": "사용자가 요청한 오프닝 자막 범위와 분리하고 원 제작진 표기를 보존",
        },
        {
            "id": "original_documents",
            "surface": "원본 설명서·ReadMe·설문 링크",
            "storage": "top-level documents",
            "status": "PRESERVED_NON_RUNTIME_DOCUMENTATION",
        },
        {
            "id": "runtime_gate",
            "surface": "오프닝·타이틀·갤러리·저장·대사 진행 통합 확인",
            "storage": str(CANDIDATE),
            "status": "PENDING",
        },
    ],
}
write_json(AUDIT / "surface_inventory_v2.json", surface_inventory)

print(json.dumps({
    "status": status,
    "candidate_root": str(CANDIDATE),
    "file_count": len(candidate_rows),
    "total_bytes": sum(r["size"] for r in candidate_rows),
    "save_file_count": len(save_rows),
    "manifest": str(AUDIT / "final_ko_rc1_manifest.json"),
    "surface_inventory": str(AUDIT / "surface_inventory_v2.json"),
}, ensure_ascii=False, indent=2), flush=True)

if status != "PASS_STATIC_RUNTIME_PENDING":
    raise SystemExit(2)


