from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    catalog_rows = [json.loads(line) for line in (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8")]
    total_units = sum(bool(row["source_text"]) and "lookup_keys" not in row.get("lanes", []) for row in catalog_rows)
    translatable_files = len({row["file"] for row in catalog_rows if bool(row["source_text"]) and "lookup_keys" not in row.get("lanes", [])})

    completed = []
    completed_units = 0
    for path in sorted((PROJECT / "packets" / "reviewed").glob("*_all_translatable_slots_reviewed_once.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not data.get("file_translation_complete") or data.get("review_passes_completed") != 1:
            continue
        entries = data["entries"]
        filename = str(entries[0]["uid"]).split("::")[1]
        manifest_path = PROJECT / "audit" / f"gsc_build_{filename.removesuffix('.gsc')}_complete.json"
        completed.append(
            {
                "file": filename,
                "reviewed_units": len(entries),
                "review_map": str(path.relative_to(PROJECT)).replace("\\", "/"),
                "review_map_sha256": sha256(path),
                "build_manifest": str(manifest_path.relative_to(PROJECT)).replace("\\", "/"),
                "build_manifest_sha256": sha256(manifest_path),
            }
        )
        completed_units += len(entries)

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    progress = {
        "schema": "fairytale-requiem-translation-progress-v1",
        "status": "IN_PROGRESS",
        "updated_utc": now,
        "translation_method": "Codex internal model for general files; local Gemma 4 26B for sensitive files; no external API",
        "review_policy": "draft translation followed by exactly one recorded review pass per translated slot (Codex or local Gemma)",
        "target_encoding": "cp949",
        "catalog": {
            "translatable_nonempty_nonlookup_units": total_units,
            "translatable_files": translatable_files,
        },
        "completed": {
            "reviewed_once_units": completed_units,
            "files": len(completed),
            "unit_percent": round(completed_units * 100 / total_units, 4),
            "file_percent": round(len(completed) * 100 / translatable_files, 4),
        },
        "remaining": {
            "units": total_units - completed_units,
            "files": translatable_files - len(completed),
        },
        "completed_files": completed,
        "runtime": {
            "title_menu_help_ui_tested": True,
            "title_window_korean_verified": True,
            "scenario_runtime_regression_pending_until_later_milestone": True,
            "trial_directory": str(PROJECT / "runtime" / "trial_ko"),
        },
        "release_ready": False,
    }
    progress_path = PROJECT / "audit" / "translation_progress.json"
    progress_path.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    project_path = PROJECT / "project.json"
    project = json.loads(project_path.read_text(encoding="utf-8"))
    project.update(
        {
            "updated_utc": now,
            "status": "scenario_translation_in_progress",
            "game_root": r"Y:\GAME\H Games\FairyTale Requiem\フェアリーテイル・レクイエム",
            "game_root_policy": "read_only_until_explicit_install",
            "patched_game_dir": str(PROJECT / "runtime" / "trial_ko"),
            "launch_this_exe": str(PROJECT / "runtime" / "trial_ko" / "フェアリーテイル・レクイエム.exe"),
            "runtime_tested": True,
            "runtime_ui_tested": True,
            "translated_scenarios_runtime_tested": False,
            "translation_progress": "audit/translation_progress.json",
            "translated_units_reviewed_once": completed_units,
            "translation_unit_total": total_units,
            "completed_translatable_files": [row["file"] for row in completed],
            "release_ready": False,
        }
    )
    project_path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "progress": str(progress_path), "completed_units": completed_units, "total_units": total_units, "completed_files": len(completed), "total_files": translatable_files, "progress_sha256": sha256(progress_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
