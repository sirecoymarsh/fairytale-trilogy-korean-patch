#!/usr/bin/env python3
"""Assemble an isolated P-drive Korean runtime trial for Fairytale Requiem."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ORIGINAL_MAIN_EXE_SHA256 = (
    "7C5392ABEF0810EC2CE3EC8C6318A566FCE854281BBD52C7C032A8D7477ECD66"
)
PATCHED_EXE_SHA256 = (
    "FB1860D9A13B97306F597A381C29A20F84521156CE4040BA81A2110678EDE8E7"
)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def same_volume_link_or_copy(source: Path, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if destination.is_dir():
            raise IsADirectoryError(destination)
        destination.unlink()
    try:
        os.link(source, destination)
        return "hardlink"
    except OSError:
        shutil.copy2(source, destination)
        return "copy"


def run(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    project_meta = json.loads((project / "project.json").read_text(encoding="utf-8"))
    game_root = Path(project_meta["game_root"])
    if not game_root.is_dir():
        raise FileNotFoundError(game_root)
    trial = project / "runtime" / "trial_ko"
    trial.mkdir(parents=True, exist_ok=True)

    inventory = json.loads((project / "audit" / "original_inventory.json").read_text(encoding="utf-8"))
    entries = inventory["entries"]
    main_exe_name = next(
        entry["path"]
        for entry in entries
        if entry["kind"] == "pe"
        and entry["size"] == 614400
        and entry["sha256"].upper() == ORIGINAL_MAIN_EXE_SHA256
    )

    # Create an isolated clone. Large immutable files are hard-linked only
    # because this same-volume tree never mutates them; every localized file is
    # replaced by newly allocated bytes below.
    methods: dict[str, str] = {}
    excluded = {main_exe_name, "scr.xfl", "grpo.xfl"}
    for entry in entries:
        relative = Path(entry["path"])
        if relative.as_posix() in excluded or entry["path"] in excluded:
            continue
        source = game_root / relative
        destination = trial / relative
        if entry["type"] == "dir":
            destination.mkdir(parents=True, exist_ok=True)
            methods[entry["path"]] = "directory"
            continue
        methods[entry["path"]] = same_volume_link_or_copy(source, destination)

    patched_exe_source = project / "staging" / "FairytaleRequiem_KoreanOutput.exe"
    trial_exe = trial / main_exe_name
    shutil.copy2(patched_exe_source, trial_exe)
    if sha256_path(trial_exe) != PATCHED_EXE_SHA256:
        raise RuntimeError("trial executable hash mismatch")
    methods[main_exe_name] = "localized_copy"

    # Build a trial scr.xfl containing only the reviewed 20-slot pilot.  Also
    # place the same GSC in loose scr/ to cover the engine's normal loose-file
    # override path proven by the sibling codeX RScript installation.
    scr_tree = project / "staging" / "runtime_trial_build" / "scr_rebuild_tree"
    if scr_tree.exists():
        shutil.rmtree(scr_tree)
    shutil.copytree(project / "extracted" / "scr", scr_tree)
    pilot_gsc = project / "staging" / "pilot" / "scr" / "1101.gsc"
    shutil.copy2(pilot_gsc, scr_tree / "1101.gsc")
    trial_scr = trial / "scr.xfl"
    scr_repack_report = project / "audit" / "runtime_trial_scr_repack.json"
    run(
        [
            sys.executable,
            str(project / "adapter" / "xfl_tool.py"),
            "repack",
            str(scr_tree),
            str(project / "audit" / "scr_xfl_manifest.json"),
            str(trial_scr),
            "--report",
            str(scr_repack_report),
        ]
    )
    loose_scr = trial / "scr"
    loose_scr.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pilot_gsc, loose_scr / "1101.gsc")
    methods["scr.xfl"] = "localized_repack"
    methods["scr/1101.gsc"] = "localized_loose_override"

    # Install the first-pass title/menu UI both as a rebuilt archive and loose
    # entry overrides.  The locked ??? entry is kept byte-identical.
    ui_manifest = json.loads(
        (project / "audit" / "grpo_korean_ui_first_pass.json").read_text(encoding="utf-8")
    )
    trial_grpo = trial / "grpo.xfl"
    shutil.copy2(Path(ui_manifest["output_archive"]["path"]), trial_grpo)
    loose_grpo = trial / "grpo"
    loose_grpo.mkdir(parents=True, exist_ok=True)
    ui_entry_root = project / "staging" / "ui_first_pass" / "grpo_entries"
    for name in ui_manifest["changed_entries"]:
        shutil.copy2(ui_entry_root / name, loose_grpo / name)
    methods["grpo.xfl"] = "localized_repack"
    methods["grpo/*"] = "15 localized loose overrides"

    # Never share mutable save files with the original installation.
    save_dir = trial / "save"
    if save_dir.exists():
        for item in save_dir.iterdir():
            if item.is_file():
                item.unlink()
    else:
        save_dir.mkdir(parents=True)
    methods["save"] = "isolated_empty_directory"

    allowlisted_changed = {
        "1101.gsc": sha256_path(pilot_gsc),
    }
    source_scr_manifest = json.loads(
        (project / "audit" / "scr_xfl_manifest.json").read_text(encoding="utf-8")
    )
    actual_scr_changes = []
    for entry in source_scr_manifest["entries"]:
        name = entry["name"]
        current_hash = sha256_path(scr_tree / name)
        if current_hash != entry["sha256"]:
            actual_scr_changes.append(name)
            if allowlisted_changed.get(name) != current_hash:
                raise RuntimeError(f"unexpected scr payload change: {name}")
    if actual_scr_changes != ["1101.gsc"]:
        raise RuntimeError(f"unexpected scr changed entries: {actual_scr_changes}")

    manifest = {
        "schema": "fairytale-requiem-korean-runtime-trial-v1",
        "delivery": "isolated P-drive runtime trial",
        "source_game": str(game_root),
        "trial_root": str(trial),
        "launch_exe": str(trial_exe),
        "original_game_policy": "read-only; no files changed",
        "copy_methods": methods,
        "localized_files": {
            main_exe_name: {
                "sha256": sha256_path(trial_exe),
                "purpose": "CP949 output and Korean font pipeline",
            },
            "scr.xfl": {
                "sha256": sha256_path(trial_scr),
                "changed_entries": actual_scr_changes,
            },
            "grpo.xfl": {
                "sha256": sha256_path(trial_grpo),
                "changed_entries": ui_manifest["changed_entries"],
            },
            "scr/1101.gsc": {"sha256": sha256_path(loose_scr / "1101.gsc")},
            "grpo/*": {
                "count": len(ui_manifest["changed_entries"]),
                "sha256": {
                    name: sha256_path(loose_grpo / name)
                    for name in ui_manifest["changed_entries"]
                },
            },
        },
        "translation_scope": {
            "scenario_reviewed_slots": 20,
            "scenario_file": "1101.gsc",
            "ui_first_pass_assets": len(ui_manifest["changed_entries"]),
            "remaining_scenario_is_original_japanese": True,
        },
        "runtime_status": "not_launched",
        "release_ready": False,
    }
    manifest_path = project / "audit" / "runtime_trial_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    project_meta["status"] = "runtime_trial_assembled_launch_pending"
    project_meta["requested_delivery"] = "full_korean_localization_internal_model_single_review"
    project_meta["patched_game_dir"] = str(trial)
    project_meta["launch_this_exe"] = str(trial_exe)
    project_meta["runtime_tested"] = False
    project_meta["release_ready"] = False
    (project / "project.json").write_text(
        json.dumps(project_meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "trial_root": str(trial),
                "launch_exe": str(trial_exe),
                "trial_exe_sha256": sha256_path(trial_exe),
                "scr_xfl_sha256": sha256_path(trial_scr),
                "grpo_xfl_sha256": sha256_path(trial_grpo),
                "manifest": str(manifest_path),
            },
            ensure_ascii=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
