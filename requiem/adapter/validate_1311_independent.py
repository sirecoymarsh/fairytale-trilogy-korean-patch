from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
MAP_PATH = PROJECT / "packets" / "reviewed" / "1311_all_translatable_slots_reviewed_once.json"
MANIFEST_PATH = PROJECT / "audit" / "gsc_build_1311_complete.json"
PROGRESS_PATH = PROJECT / "audit" / "translation_progress.json"
SOURCE_PATH = PROJECT / "extracted" / "scr" / "1311.gsc"
STAGE_PATH = PROJECT / "staging" / "translation_batches" / "1311_complete" / "scr" / "1311.gsc"
TRIAL_PATH = PROJECT / "runtime" / "trial_ko" / "scr" / "1311.gsc"
AUDIT_PATH = PROJECT / "audit" / "independent_validation_1311.json"
JAPANESE_RE = re.compile(r"[\u3040-\u30ff]")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_codec():
    module_path = PROJECT / "adapter" / "gsc_codec.py"
    spec = importlib.util.spec_from_file_location("gsc_codec_independent", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load gsc_codec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    mapping = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    progress = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
    entries = mapping["entries"]
    slots = {int(entry["uid"].rsplit("/", 1)[1]): entry for entry in entries}
    progress_row = next(row for row in progress["completed_files"] if row["file"] == "1311.gsc")

    codec = load_codec()
    source_raw = SOURCE_PATH.read_bytes()
    stage_raw = STAGE_PATH.read_bytes()
    source = codec.parse_gsc(source_raw)
    stage = codec.parse_gsc(stage_raw)

    checks = {
        "review_map_hash_matches_progress": sha256(MAP_PATH) == progress_row["review_map_sha256"],
        "review_map_hash_matches_manifest": sha256(MAP_PATH) == manifest["translation_map"]["sha256"],
        "build_manifest_hash_matches_progress": sha256(MANIFEST_PATH) == progress_row["build_manifest_sha256"],
        "review_passes_exactly_one": mapping["review_passes_completed"] == 1,
        "entry_count_exact": len(entries) == 22 and manifest["translation_map"]["entry_count"] == 22,
        "slot_coverage_exact": set(slots) == set(range(1, 23)),
        "all_status_reviewed_once": all(entry.get("review_status") == "reviewed_once" for entry in entries),
        "all_targets_strict_cp949": all(str(entry["target_text"]).encode("cp949", errors="strict") is not None for entry in entries),
        "no_kana_in_targets": all(not JAPANESE_RE.search(str(entry["target_text"])) for entry in entries),
        "lookup_range_declared": mapping["lookup_slots_preserved"] == [23, 80],
        "manifest_changed_slot_count_exact": manifest["changed_slot_count"] == 22 and manifest["files"][0]["changed_slot_count"] == 22,
        "manifest_roundtrip_true": manifest["files"][0]["no_change_roundtrip_byte_identical"] is True,
        "manifest_non_target_true": manifest["files"][0]["all_non_target_slots_identical"] is True,
        "source_roundtrip_byte_identical": codec.rebuild_gsc(source, source.strings) == source_raw,
        "command_section_identical": source.command == stage.command,
        "trailing_section_identical": source.trailing == stage.trailing,
        "string_count_identical": len(source.strings) == len(stage.strings) == 81,
        "all_target_slots_match_map": all(stage.strings[index] == str(entry["target_text"]).encode("cp949") for index, entry in slots.items()),
        "all_non_target_slots_identical": all(source.strings[index] == stage.strings[index] for index in set(range(81)) - set(slots)),
        "stage_hash_matches_manifest": sha256(STAGE_PATH) == manifest["files"][0]["output_sha256"],
        "trial_hash_matches_stage": sha256(TRIAL_PATH) == sha256(STAGE_PATH),
        "progress_units_match": progress["completed"]["reviewed_once_units"] == 9484 and progress["remaining"]["units"] == 19888,
        "progress_files_match": progress["completed"]["files"] == 75 and progress["remaining"]["files"] == 158,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {
        "schema": "fairytale-requiem-independent-validation-v1",
        "status": status,
        "file": "1311.gsc",
        "entry_count": len(entries),
        "review_map_sha256": sha256(MAP_PATH),
        "build_manifest_sha256": sha256(MANIFEST_PATH),
        "stage_sha256": sha256(STAGE_PATH),
        "trial_sha256": sha256(TRIAL_PATH),
        "checks": checks,
    }
    AUDIT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**result, "audit_path": str(AUDIT_PATH)}, ensure_ascii=True, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

