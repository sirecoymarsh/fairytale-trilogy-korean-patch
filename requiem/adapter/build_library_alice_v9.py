from __future__ import annotations
from pathlib import Path
from PIL import Image
import hashlib, json
import numpy as np
import cv2

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
SOURCE_ROOT = PROJECT / "staging" / "ui_other_banks_audit_v1" / "exported_png" / "grpo_lib"
BASE = PROJECT / "staging" / "library_faithful_v2_review" / "book_0011"
OUT = PROJECT / "staging" / "library_per_book_rebuild_v9" / "alice"
TARGET = "\uc774\uc0c1\ud55c \ub098\ub77c\uc758 \uc568\ub9ac\uc2a4"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def load(path: Path) -> np.ndarray:
    return np.array(Image.open(path).convert("RGBA"))

def fit_hover_transform(normal: np.ndarray, hover: np.ndarray):
    opaque = (normal[..., 3] > 0) & (hover[..., 3] > 0)
    coeffs = []
    for channel in range(3):
        x = normal[..., channel][opaque].astype(np.float64)
        y = hover[..., channel][opaque].astype(np.float64)
        a, b = np.polyfit(x, y, 1)
        coeffs.append((float(a), float(b)))
    return coeffs

def transform_rgb(image: np.ndarray, coeffs, alpha: np.ndarray) -> np.ndarray:
    out = image.copy().astype(np.float32)
    for channel, (a, b) in enumerate(coeffs):
        out[..., channel] = out[..., channel] * a + b
    out = np.clip(out, 0, 255).astype(np.uint8)
    out[..., 3] = alpha
    return out

def save_state(stem: str, source: np.ndarray, clean: np.ndarray, candidate: np.ndarray,
               old_mask: np.ndarray, target_mask: np.ndarray, state: str):
    d = OUT / stem
    d.mkdir(parents=True, exist_ok=True)
    files = {
        "source": d / "source.png",
        "mask": d / "old_text_mask.png",
        "target_mask": d / "target_text_mask.png",
        "clean": d / "clean.png",
        "candidate": d / "candidate.png",
    }
    Image.fromarray(source, "RGBA").save(files["source"])
    Image.fromarray(old_mask.astype(np.uint8) * 255, "L").save(files["mask"])
    Image.fromarray(target_mask.astype(np.uint8) * 255, "L").save(files["target_mask"])
    Image.fromarray(clean, "RGBA").save(files["clean"])
    Image.fromarray(candidate, "RGBA").save(files["candidate"])

    clean_changed = np.any(clean != source, axis=2)
    candidate_changed = np.any(candidate != source, axis=2)
    face = np.zeros(old_mask.shape, bool)
    face[82:433, 49:102] = True
    rows_full = int(np.count_nonzero(np.mean(clean_changed[:, 49:102], axis=1) > 0.90))
    cols_full = int(np.count_nonzero(np.mean(clean_changed[82:433, :], axis=0) > 0.90))
    validation = {
        "dimensions": [int(source.shape[1]), int(source.shape[0])],
        "alpha_geometry_byte_exact": bool(np.array_equal(source[...,3], clean[...,3]) and np.array_equal(source[...,3], candidate[...,3])),
        "clean_changes_only_old_glyph_mask": bool(np.all(~clean_changed | old_mask)),
        "candidate_changes_only_old_or_target_glyph_mask": bool(np.all(~candidate_changed | old_mask | target_mask)),
        "protected_pixels_byte_exact": bool(np.array_equal(source[~(old_mask | target_mask)], candidate[~(old_mask | target_mask)])),
        "old_text_mask_pixels": int(old_mask.sum()),
        "target_text_mask_pixels": int(target_mask.sum()),
        "clean_changed_face_ratio": float(clean_changed[face].mean()),
        "full_width_changed_rows": rows_full,
        "full_height_changed_columns": cols_full,
        "rectangular_plate_detected": bool(rows_full > 0 or cols_full > 0),
    }
    return {
        "stem": stem,
        "state": state,
        "target": TARGET,
        "design_profile": "alice_round_burgundy_source_glyph_surgery",
        "files": {key: str(value) for key, value in files.items()},
        "sha256": {key: sha(value) for key, value in files.items()},
        "validation": validation,
    }

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    normal_source = load(SOURCE_ROOT / "0011.png")
    hover_source = load(SOURCE_ROOT / "0111.png")
    donor_clean = load(BASE / "clean" / "0011.png")
    donor_candidate = load(BASE / "candidate" / "0011.png")
    old_mask = np.array(Image.open(BASE / "removed_text_mask" / "0011.png").convert("L")) > 0
    target_mask = np.any(donor_candidate != donor_clean, axis=2)

    # Match the donor paper to the untouched source around every connected source-glyph
    # component, then feather only inside the glyph-shaped ownership mask.
    def glyph_surgery(source, material, mask, core):
        corrected = material.astype(np.float32).copy()
        count, labels = cv2.connectedComponents(mask.astype(np.uint8), 8)
        face = np.zeros(mask.shape, np.uint8)
        face[80:435, 49:103] = 1
        for label in range(1, count):
            component = labels == label
            expanded = cv2.dilate(component.astype(np.uint8), np.ones((11,11), np.uint8), 1) > 0
            ring = expanded & ~mask & (face > 0) & (source[...,3] > 0)
            if np.count_nonzero(ring) < 12:
                continue
            delta = np.median(source[ring,:3].astype(np.float32) - material[ring,:3].astype(np.float32), axis=0)
            corrected[component,:3] += delta
        corrected = np.clip(corrected, 0, 255)
        distance = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 3)
        blend = np.clip(distance / 2.2, 0.0, 1.0)
        guaranteed_core = cv2.dilate(core.astype(np.uint8), np.ones((3,3), np.uint8), 1) > 0
        blend[guaranteed_core] = 1.0
        clean = source.copy().astype(np.float32)
        a = blend[...,None]
        clean[...,:3] = source[...,:3].astype(np.float32) * (1.0-a) + corrected[...,:3] * a
        clean[...,3] = source[...,3]
        clean = np.clip(clean,0,255).astype(np.uint8)
        clean[~mask] = source[~mask]
        return clean

    gray = cv2.cvtColor(normal_source[...,:3], cv2.COLOR_RGB2GRAY)
    roi = np.zeros(old_mask.shape, bool)
    roi[86:433, 54:99] = True
    core = (gray < 150) & roi & (normal_source[...,3] > 0)
    normal_clean = glyph_surgery(normal_source, donor_clean, old_mask, core)
    target_delta = donor_candidate[...,:3].astype(np.int16) - donor_clean[...,:3].astype(np.int16)
    normal_candidate = normal_clean.copy()
    normal_rgb = normal_candidate[...,:3].astype(np.int16)
    normal_rgb[target_mask] += target_delta[target_mask]
    normal_candidate[...,:3] = np.clip(normal_rgb,0,255).astype(np.uint8)

    coeffs = fit_hover_transform(normal_source, hover_source)
    hover_clean_material = transform_rgb(donor_clean, coeffs, hover_source[...,3])
    hover_target_material = transform_rgb(donor_candidate, coeffs, hover_source[...,3])
    hover_clean = glyph_surgery(hover_source, hover_clean_material, old_mask, core)
    hover_delta = hover_target_material[...,:3].astype(np.int16) - hover_clean_material[...,:3].astype(np.int16)
    hover_candidate = hover_clean.copy()
    hover_rgb = hover_candidate[...,:3].astype(np.int16)
    hover_rgb[target_mask] += hover_delta[target_mask]
    hover_candidate[...,:3] = np.clip(hover_rgb,0,255).astype(np.uint8)

    records = [
        save_state("0011", normal_source, normal_clean, normal_candidate, old_mask, target_mask, "normal"),
        save_state("0111", hover_source, hover_clean, hover_candidate, old_mask, target_mask, "hover_or_selected"),
    ]
    manifest = {
        "schema": "fairytale-requiem-library-per-book-alice-v9",
        "status": "USER_REVIEW_REQUIRED_NOT_INSTALLED",
        "supersedes": "library_per_book_rebuild_v8 (REJECTED_FLAT_PLATE)",
        "book": "alice",
        "target": TARGET,
        "rules": {
            "old_text_removed_before_typesetting": True,
            "clean_changes_restricted_to_source_glyph_shape": True,
            "no_rectangular_plate": True,
            "normal_and_selected_built_as_pair": True,
            "installed": False,
        },
        "hover_affine_rgb": coeffs,
        "records": records,
    }
    path = OUT / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(path), "records": [r["validation"] for r in records]}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()


