#!/usr/bin/env python3
"""Independent verifier for the promoted Malie Master title UI."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    audit_path = project / "audit" / "grpo_korean_ui_malie_master.json"
    graph_path = project / "audit" / "malie_master_grpo_consumer_graph.json"
    promotion_path = project / "audit" / "grpo_malie_master_runtime_promotion.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    promotion = json.loads(promotion_path.read_text(encoding="utf-8"))
    source_root = project / "extracted" / "grpo"
    source_png_root = project / "evidence" / "ui" / "grpo_png"
    trial = project / "runtime" / "trial_ko"
    tool = project / "adapter" / "UiAssetTool.exe"

    failures: list[str] = []
    archive_path = trial / "grpo.xfl"
    if sha(archive_path) != audit["output_archive"]["sha256"]:
        failures.append("trial archive hash does not equal Master archive")
    if promotion["verification"]["status"] != "PASS":
        failures.append("promotion audit is not PASS")

    records_by_name = {row["stable_id"].split("::")[1]: row for row in audit["records"]}
    if set(records_by_name) != set(audit["changed_entries"]):
        failures.append("record set does not equal changed-entry allowlist")
    if len(graph["state_families"]) != 8:
        failures.append("consumer graph does not contain eight state families")
    graph_assets: set[str] = set()
    for family in graph["state_families"]:
        graph_assets.add(family["normal_asset"])
        graph_assets.add(family["hover_or_selected_asset"])
        if family["family_id"] != "title-menu-6" and family["consumer_count"] < 1:
            failures.append(f"family has no consumer: {family['family_id']}")
    manifest_names = {f"{i:04d}.wcg" for i in range(1, 9)} | {f"{100+i:04d}.wcg" for i in range(1, 9)}
    if graph_assets != manifest_names:
        failures.append("consumer graph asset closure mismatch")

    # The locked state must be identical in the source tree and in a fresh
    # extraction of the promoted archive.
    with tempfile.TemporaryDirectory(prefix="fr-grpo-independent-") as temp_name:
        temp = Path(temp_name)
        extract_dir = temp / "extract"
        manifest = temp / "manifest.json"
        subprocess.run(
            [
                "python",
                str(project / "adapter" / "xfl_tool.py"),
                "extract",
                str(archive_path),
                str(extract_dir),
                "--manifest",
                str(manifest),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        extracted_manifest = json.loads(manifest.read_text(encoding="utf-8"))
        names = [entry["name"] for entry in extracted_manifest["entries"]]
        if names != [f"{i:04d}.wcg" for i in range(1, 9)] + [f"{100+i:04d}.wcg" for i in range(1, 9)]:
            failures.append("promoted archive name/order mismatch")
        if sha(extract_dir / "0106.wcg") != sha(source_root / "0106.wcg"):
            failures.append("locked 0106 changed in promoted archive")

    asset_results = []
    for name, record in sorted(records_by_name.items()):
        source_png = Image.open(source_png_root / name.replace(".wcg", ".png")).convert("RGBA")
        trial_wcg = trial / "grpo" / name
        if sha(trial_wcg) != record["output_wcg_sha256"]:
            failures.append(f"loose WCG hash mismatch: {name}")
            continue
        with tempfile.TemporaryDirectory(prefix="fr-wcg-independent-") as temp_name:
            decoded_path = Path(temp_name) / "decoded.png"
            subprocess.run(
                [str(tool), "wcg2png", str(trial_wcg), str(decoded_path)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            decoded = Image.open(decoded_path).convert("RGBA")
            if decoded.size != source_png.size:
                failures.append(f"decoded dimensions changed: {name}")
                continue
            src = np.asarray(source_png, dtype=np.uint8)
            out = np.asarray(decoded, dtype=np.uint8)
            mask_path = project / "staging" / "ui_master" / "png_patches" / name.replace(".wcg", ".mask.png")
            edit_mask = np.asarray(Image.open(mask_path).convert("L"), dtype=np.uint8) > 0
            protected = ~edit_mask
            delta = np.abs(src.astype(np.int16) - out.astype(np.int16))
            max_protected = int(delta[protected].max()) if protected.any() else 0
            if max_protected > 8:
                failures.append(f"protected pixel delta > 8: {name}: {max_protected}")
            source_bbox = source_png.getchannel("A").getbbox()
            output_bbox = decoded.getchannel("A").getbbox()
            if name.startswith("00") and source_bbox != output_bbox:
                failures.append(f"miniature alpha bbox changed: {name}")
            if name.startswith("01") and output_bbox and source_bbox and output_bbox[2] != source_bbox[2]:
                failures.append(f"large-label right edge changed: {name}")
            asset_results.append(
                {
                    "name": name,
                    "dimensions": list(decoded.size),
                    "source_alpha_bbox": list(source_bbox) if source_bbox else None,
                    "output_alpha_bbox": list(output_bbox) if output_bbox else None,
                    "max_protected_rgba_delta": max_protected,
                    "status": "PASS" if max_protected <= 8 else "FAIL",
                }
            )

    result = {
        "schema": "fairytale-requiem-grpo-malie-master-independent-validation-v1",
        "audit_inputs": {
            "master_audit": {"path": str(audit_path), "sha256": sha(audit_path)},
            "consumer_graph": {"path": str(graph_path), "sha256": sha(graph_path)},
            "runtime_promotion": {"path": str(promotion_path), "sha256": sha(promotion_path)},
        },
        "trial_archive": {"path": str(archive_path), "sha256": sha(archive_path)},
        "state_family_count": len(graph["state_families"]),
        "asset_results": asset_results,
        "failure_count": len(failures),
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }
    output = project / "audit" / "grpo_malie_master_independent_validation.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
