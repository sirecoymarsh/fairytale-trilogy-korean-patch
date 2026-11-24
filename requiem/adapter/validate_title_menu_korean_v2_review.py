#!/usr/bin/env python3
"""Independent static checks for the review-only title menu v2 candidate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
ROOT = PROJECT / "staging" / "title_menu_korean_v2_review"
MANIFEST = ROOT / "manifest.json"
REPORT = PROJECT / "audit" / "title_menu_korean_v2_review_validation.json"
LARGE = {"0101", "0102", "0103", "0104", "0105", "0107", "0108"}
SMALL = {"0001", "0002", "0003", "0004", "0005", "0006", "0007", "0008"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    checks: list[dict[str, object]] = []
    records = {record["stem"]: record for record in manifest["records"]}
    if set(records) != LARGE | SMALL:
        errors.append("state family is not exactly the expected 15 states")
    if manifest.get("status") != "USER_REVIEW_REQUIRED_NOT_INSTALLED":
        errors.append("candidate is not marked review-only")
    if not manifest.get("policy", {}).get("not_installed_into_game"):
        errors.append("manifest does not prohibit game installation")

    for stem in sorted(LARGE):
        source_path = ROOT / "source" / f"{stem}.png"
        clean_path = ROOT / "clean" / f"{stem}.png"
        candidate_path = ROOT / "candidate" / f"{stem}.png"
        with Image.open(source_path) as image:
            source = image.convert("RGBA")
        with Image.open(clean_path) as image:
            clean = image.convert("RGBA")
        with Image.open(candidate_path) as image:
            candidate = image.convert("RGBA")
        if source.size != clean.size or source.size != candidate.size or source.size != (800, 120):
            errors.append(f"{stem}: dimensions changed")
        source_bbox = source.getchannel("A").getbbox()
        clean_bbox = clean.getchannel("A").getbbox()
        target_bbox = candidate.getchannel("A").getbbox()
        if source_bbox is None or target_bbox is None:
            errors.append(f"{stem}: empty source or target")
            continue
        if clean_bbox is not None:
            errors.append(f"{stem}: clean plate is not completely transparent")
        if not (
            source_bbox[0] <= target_bbox[0]
            and source_bbox[1] <= target_bbox[1]
            and target_bbox[2] <= source_bbox[2]
            and target_bbox[3] <= source_bbox[3]
        ):
            errors.append(f"{stem}: target exceeds source placement envelope")
        if target_bbox[2] != source_bbox[2]:
            errors.append(f"{stem}: authored right edge moved")
        sa = np.asarray(source, dtype=np.uint8)
        ca = np.asarray(clean, dtype=np.uint8)
        ta = np.asarray(candidate, dtype=np.uint8)
        owner = (sa[:, :, 3] > 0) | (ta[:, :, 3] > 0)
        if np.any(ca[~owner]) or np.any(ta[~owner]):
            errors.append(f"{stem}: pixels outside text owner mask changed")
        record = records.get(stem, {})
        if record.get("source_text_alpha_pixels_after_clean") != 0:
            errors.append(f"{stem}: source residue count is not zero")
        if sha256(source_path) != record.get("source_sha256"):
            errors.append(f"{stem}: source hash mismatch")
        if sha256(clean_path) != record.get("clean_sha256"):
            errors.append(f"{stem}: clean hash mismatch")
        if sha256(candidate_path) != record.get("candidate_sha256"):
            errors.append(f"{stem}: candidate hash mismatch")
        checks.append({
            "stem": stem,
            "dimensions": list(source.size),
            "source_bbox": list(source_bbox),
            "target_bbox": list(target_bbox),
            "clean_alpha_bbox": clean_bbox,
            "right_edge_exact": target_bbox[2] == source_bbox[2],
            "contained": True,
            "outside_owner_exact": True,
        })

    for stem in sorted(SMALL):
        record = records.get(stem, {})
        source_path = ROOT / "source" / f"{stem}.png"
        candidate_path = ROOT / "candidate" / f"{stem}.png"
        if sha256(source_path) != record.get("source_sha256"):
            errors.append(f"{stem}: reused source hash mismatch")
        if sha256(candidate_path) != record.get("candidate_sha256"):
            errors.append(f"{stem}: reused candidate hash mismatch")
        with Image.open(source_path) as source, Image.open(candidate_path) as candidate:
            if source.size != candidate.size or source.size != (150, 150):
                errors.append(f"{stem}: miniature dimensions changed")

    report = {
        "schema": "fairytale-requiem-title-menu-korean-v2-independent-validation",
        "status": "PASS" if not errors else "FAIL",
        "review_only": True,
        "installed": False,
        "state_count": len(records),
        "large_redrawn_count": len(LARGE),
        "small_reused_count": len(SMALL),
        "manifest_sha256": sha256(MANIFEST),
        "checks": checks,
        "errors": errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
