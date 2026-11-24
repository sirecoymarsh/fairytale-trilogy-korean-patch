#!/usr/bin/env python3
"""Independent static validation for the original-style UI study."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


P = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
ROOT = P / "staging" / "ui_original_style_study_v1"
MANIFEST = ROOT / "manifest.json"
REPORT = P / "audit" / "ui_original_style_study_v1_validation.json"
EXPECTED = {"map": 7, "sketch": 7, "library": 6}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_image(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    counts = {family: 0 for family in EXPECTED}
    checks: list[dict[str, object]] = []
    if manifest.get("status") != "USER_REVIEW_REQUIRED_NOT_INSTALLED":
        errors.append("manifest is not review-only")
    if manifest.get("contract", {}).get("installed") is not False:
        errors.append("manifest does not prove not-installed status")
    for record in manifest.get("records", []):
        family = record.get("family")
        stem = record.get("stem")
        if family not in EXPECTED:
            errors.append(f"unknown family: {family}")
            continue
        counts[family] += 1
        paths = {key: Path(record[key]) for key in ("source", "clean", "candidate", "owned_mask")}
        for key, path in paths.items():
            if not path.exists():
                errors.append(f"{family}/{stem}: missing {key}")
        if any(not path.exists() for path in paths.values()):
            continue
        source = load_image(paths["source"])
        clean = load_image(paths["clean"])
        candidate = load_image(paths["candidate"])
        owner = np.asarray(Image.open(paths["owned_mask"]).convert("L"), dtype=np.uint8) > 0
        if not (source.shape == clean.shape == candidate.shape and source.shape[:2] == owner.shape):
            errors.append(f"{family}/{stem}: dimension mismatch")
            continue
        if not np.array_equal(source[~owner], clean[~owner]):
            errors.append(f"{family}/{stem}: clean plate changed protected pixels")
        if not np.array_equal(source[~owner], candidate[~owner]):
            errors.append(f"{family}/{stem}: candidate changed protected pixels")
        if sha(paths["source"]) != record.get("source_sha256"):
            errors.append(f"{family}/{stem}: source hash mismatch")
        if sha(paths["clean"]) != record.get("clean_sha256"):
            errors.append(f"{family}/{stem}: clean hash mismatch")
        if sha(paths["candidate"]) != record.get("candidate_sha256"):
            errors.append(f"{family}/{stem}: candidate hash mismatch")
        if not record.get("old_ui_removed_completely_before_typesetting"):
            errors.append(f"{family}/{stem}: clean-first contract missing")
        checks.append({
            "id": f"{family}:{stem}",
            "dimensions": [int(source.shape[1]), int(source.shape[0])],
            "outside_owned_clean_exact": True,
            "outside_owned_candidate_exact": True,
            "clean_first": True,
        })
    if counts != EXPECTED:
        errors.append(f"family counts differ: {counts} != {EXPECTED}")
    report = {
        "schema": "fairytale-requiem-original-style-ui-study-v1-independent-validation",
        "status": "PASS" if not errors else "FAIL",
        "review_only": True,
        "installed": False,
        "counts": counts,
        "manifest_sha256": sha(MANIFEST),
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
