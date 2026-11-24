from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib, importlib.util, json

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
WORK = Path(r"C:\Users\CadriacLord\Documents\Codex\2026-08-12\search-ms-displayname-20pc-20-20")
SRC = PROJECT / "staging/grpe_title_logo_korean_v1_assets/source/frames"
DONOR = PROJECT / "staging/grpe_title_logo_korean_v1_assets/evidence"
OUT = PROJECT / "staging/grpe_title_logo_korean_v10_centered_review"
CAND = OUT / "candidate_frames"

spec = importlib.util.spec_from_file_location("v7", WORK / "build_title_logo_redraw_v7.py")
v7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v7)

v7.PLACED_XY = (285, 162)  # move 6 px left from v9
v7.SAFE_TEXT_RECT = (280, 158, 554, 284)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def detect(source: np.ndarray, donor: np.ndarray, protected: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    gray = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2GRAY)
    dgray = cv2.cvtColor(donor[..., :3], cv2.COLOR_RGB2GRAY)
    hsv = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2HSV)
    delta = dgray.astype(np.int16) - gray.astype(np.int16)
    roi = np.zeros(gray.shape, bool)
    roi[132:231, 248:594] = True
    roi[196:294, 268:598] = True
    core = roi & (((delta > 16) & (gray < 208) & (hsv[..., 1] < 150)) | ((gray < 148) & (hsv[..., 1] < 110)))
    core[protected] = False
    core[145:170, 248:254] = False  # true top-left frame pixels, not logo ink
    owner = cv2.dilate(core.astype(np.uint8) * 255, np.ones((13, 13), np.uint8), 1)
    owner[~roi] = 0
    owner[145:170, 248:254] = 0
    owner[protected] = 0
    return owner, core.astype(np.uint8) * 255


def erase(source: np.ndarray, donor: np.ndarray, owner: np.ndarray, star: np.ndarray, ribbon: np.ndarray) -> np.ndarray:
    # Suppress protected dark ornament edges only in the inpaint input; the exact
    # source ornaments are restored after the old lettering has been erased.
    guard = cv2.dilate(((star > 0) | (ribbon > 0)).astype(np.uint8), np.ones((41, 41), np.uint8), 1)
    gy, gx = np.where(guard > 0)
    paper = donor[..., :3].copy()
    paper[gy, gx] = donor[np.maximum(gy - 70, 0), gx, :3]
    working = source[..., :3].copy()
    working[gy, gx] = paper[gy, gx]
    filled = cv2.inpaint(working, owner, 6, cv2.INPAINT_TELEA)
    restored = np.clip(filled.astype(np.float32) * 0.75 + paper.astype(np.float32) * 0.25, 0, 255).astype(np.uint8)
    clean = source.copy()
    clean[owner > 0, :3] = restored[owner > 0]
    clean[..., 3] = source[..., 3]
    return clean


def contact(source: Image.Image, rejected: Image.Image, clean: Image.Image, candidate: Image.Image) -> Path:
    crop = (170, 80, 660, 380)
    sheet = Image.new("RGB", (1000, 700), (34, 31, 37))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 22)
    labels = ["원본", "v9 우측 치우침", "이전 로고 획 전체 제거", "v10 균형 조정"]
    pos = [(5, 42), (505, 42), (5, 372), (505, 372)]
    for im, label, (x, y) in zip((source, rejected, clean, candidate), labels, pos):
        sheet.paste(im.convert("RGB").crop(crop), (x, y))
        draw.text((x + 6, y - 33), label, font=font, fill="white")
    path = OUT / "contact.png"
    sheet.save(path)
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    CAND.mkdir(parents=True, exist_ok=True)
    sources = sorted(SRC.glob("*.png"))
    if len(sources) != 8:
        raise RuntimeError(f"expected 8 frames, got {len(sources)}")
    layer, target_alpha = v7.lettering_layer((1280, 720))
    yy, xx = np.where(target_alpha > 0)
    target_bbox = [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1]
    sx0, sy0, sx1, sy1 = v7.SAFE_TEXT_RECT
    if not (target_bbox[0] >= sx0 and target_bbox[1] >= sy0 and target_bbox[2] <= sx1 and target_bbox[3] <= sy1):
        raise AssertionError({"target_bbox": target_bbox, "safe": v7.SAFE_TEXT_RECT})

    records, first = [], None
    for index, path in enumerate(sources):
        source_image = Image.open(path).convert("RGBA")
        source = np.array(source_image)
        donor = np.array(Image.open(DONOR / f"clean_{index:02d}.png").convert("RGBA"))
        star, ribbon, border = v7.protected_components(source)
        residue_seed = np.zeros(source.shape[:2], np.uint8)
        gray = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2GRAY)
        hsv = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2HSV)
        x0, y0, x1, y1 = 548, 274, 576, 283
        small = ((gray[y0:y1, x0:x1] < 190) & (hsv[y0:y1, x0:x1, 1] < 140)).astype(np.uint8)
        n, labels, stats, _ = cv2.connectedComponentsWithStats(small, 8)
        if n > 1:
            component = (labels == (1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA])))).astype(np.uint8) * 255
            residue_seed[y0:y1, x0:x1] = component
        residue_owner = cv2.dilate(residue_seed, np.ones((5, 5), np.uint8), 1)
        ribbon[residue_owner > 0] = 0
        protected = (star > 0) | (ribbon > 0) | (border > 0)
        owner, core = detect(source, donor, protected)
        owner[residue_owner > 0] = 255
        core[residue_seed > 0] = 255
        clean = erase(source, donor, owner, star, ribbon)
        first_gray = cv2.cvtColor(clean[..., :3], cv2.COLOR_RGB2GRAY)
        dark_seed = ((core > 0) & (first_gray < 165)).astype(np.uint8)
        if np.any(dark_seed):
            repair = (cv2.dilate(dark_seed, np.ones((5, 5), np.uint8), 1) > 0) & (owner > 0)
            clean[repair, :3] = donor[repair, :3]
        clean[protected] = source[protected]
        candidate_image = Image.fromarray(clean, "RGBA")
        candidate_image.alpha_composite(layer)
        candidate = np.array(candidate_image)
        candidate[protected] = source[protected]
        target = (target_alpha > 0) & ~protected
        owned = (owner > 0) | target
        candidate[~owned] = source[~owned]
        candidate_image = Image.fromarray(candidate, "RGBA")

        out_path = CAND / f"title_logo_v10_{index:02d}.png"
        candidate_image.save(out_path)
        frame_dir = OUT / f"frame_{index:02d}"
        frame_dir.mkdir(parents=True, exist_ok=True)
        Image.fromarray(clean, "RGBA").save(frame_dir / "clean.png")
        Image.fromarray(owner, "L").save(frame_dir / "old_text_owner.png")
        Image.fromarray(core, "L").save(frame_dir / "old_text_core.png")
        Image.fromarray(target.astype(np.uint8) * 255, "L").save(frame_dir / "target_text_mask.png")

        clean_diff = np.any(clean != source, axis=2)
        exact_source = np.all(clean == source, axis=2)
        clean_gray = cv2.cvtColor(clean[..., :3], cv2.COLOR_RGB2GRAY)
        core_b, owner_b = core > 0, owner > 0
        runs = []
        for row in clean_diff:
            edge = np.flatnonzero(np.diff(np.pad(row.astype(np.int8), (1, 1))))
            runs.append(int(np.max(edge[1::2] - edge[::2])) if len(edge) else 0)
        retained = int(np.count_nonzero(core_b & exact_source))
        residual = int(np.count_nonzero(core_b & (clean_gray < 165)))
        validation = {
            "alpha_exact": bool(np.array_equal(source[..., 3], clean[..., 3]) and np.array_equal(source[..., 3], candidate[..., 3])),
            "source_exact_outside_old_and_target": bool(np.array_equal(source[~owned], candidate[~owned])),
            "clean_exact_outside_glyph_owner": bool(np.array_equal(source[~owner_b], clean[~owner_b])),
            "red_border_exact": bool(np.array_equal(source[border > 0], candidate[border > 0])),
            "star_exact": bool(np.array_equal(source[star > 0], candidate[star > 0])),
            "ribbon_exact": bool(np.array_equal(source[ribbon > 0], candidate[ribbon > 0])),
            "old_core_coverage_ratio": float(np.count_nonzero(core_b & owner_b) / max(1, np.count_nonzero(core_b))),
            "retained_source_core_pixels": retained,
            "residual_dark_core_pixels": residual,
            "previous_logo_core_removed": bool(retained == 0 and residual == 0),
            "old_text_core_pixels": int(np.count_nonzero(core)),
            "old_text_owner_pixels": int(np.count_nonzero(owner)),
            "target_text_pixels": int(np.count_nonzero(target)),
            "max_contiguous_clean_run": int(max(runs)),
            "rows_with_plate_width_contiguous_run": int(np.count_nonzero(np.asarray(runs) > 200)),
            "rectangular_clean_plate_detected": bool(np.count_nonzero(np.asarray(runs) > 200) > 5),
            "target_bbox": target_bbox,
        }
        required = [validation[k] for k in ("alpha_exact", "source_exact_outside_old_and_target", "clean_exact_outside_glyph_owner", "red_border_exact", "star_exact", "ribbon_exact", "previous_logo_core_removed")]
        required += [validation["old_core_coverage_ratio"] == 1.0, not validation["rectangular_clean_plate_detected"]]
        if not all(required):
            raise AssertionError({"frame": index, **validation})
        records.append({"frame": index, "source": str(path), "clean": str(frame_dir / "clean.png"), "candidate": str(out_path), "sha256": digest(out_path), "validation": validation})
        if index == 0:
            rejected = Image.open(PROJECT / "staging/grpe_title_logo_korean_v9_ribbon_residue_removed_review/candidate_frames/title_logo_v9_00.png").convert("RGBA")
            first = (source_image, rejected, Image.fromarray(clean, "RGBA"), candidate_image)

    contact_path = contact(*first)
    all_checks = all(all(value for value in (r["validation"]["alpha_exact"], r["validation"]["source_exact_outside_old_and_target"], r["validation"]["clean_exact_outside_glyph_owner"], r["validation"]["red_border_exact"], r["validation"]["star_exact"], r["validation"]["ribbon_exact"], r["validation"]["previous_logo_core_removed"], not r["validation"]["rectangular_clean_plate_detected"])) for r in records)
    manifest = {
        "schema": "fairytale-requiem-title-logo-redraw-v10", "status": "USER_REVIEW_REQUIRED_NOT_INSTALLED",
        "supersedes": "v9 (Korean lettering sat slightly right of the plaque visual center)", "target": v7.TEXT,
        "design": {"placed_xy": list(v7.PLACED_XY), "placed_size": list(v7.PLACED_SIZE), "surface": "glyph-shaped old-logo removal and texture inpainting; the final dash above the red ribbon is separately removed; Korean lettering shifted 6 px left for visual balance; no rectangular plate", "protected": ["red ornamental frame", "four-point star", "English ribbon"]},
        "contact": str(contact_path), "frame_count": len(records), "installed": False, "records": records,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path = OUT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "contact": str(contact_path), "target_bbox": target_bbox, "frame_count": len(records), "all_checks": all_checks}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
