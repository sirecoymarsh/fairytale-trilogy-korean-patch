from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
SOURCE_ROOT = PROJECT / "staging" / "grpe_title_logo_korean_v1_assets" / "source" / "frames"
V1_EVIDENCE = PROJECT / "staging" / "grpe_title_logo_korean_v1_assets" / "evidence"
LETTER_ROOT = PROJECT / "staging" / "grpe_title_logo_korean_v3_generated_review"
OUT = PROJECT / "staging" / "grpe_title_logo_korean_v5_frame_guard_review"
CANDIDATES = OUT / "candidate_frames"
TEXT = "페어리테일 레퀴엠"
LETTER_BBOX = (149, 177, 1493, 782)
PLACED_SIZE = (280, 126)
PLACED_XY = (276, 154)
SAFE_TEXT_RECT = (268, 150, 565, 285)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def source_ink_mask(source: np.ndarray, v1_clean: np.ndarray) -> np.ndarray:
    rgb = source[..., :3]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    clean_gray = cv2.cvtColor(v1_clean[..., :3], cv2.COLOR_RGB2GRAY)
    roi = np.zeros(gray.shape, bool)
    roi[145:225, 258:582] = True
    roi[205:288, 292:580] = True
    # Neutral/dark Japanese ink. Warm red paper freckles and the red frame remain unowned.
    seed = roi & (gray < 188) & ((clean_gray.astype(np.int16) - gray.astype(np.int16)) > 28) & (hsv[..., 1] < 138)
    mask = seed.astype(np.uint8) * 255
    n, labels, stats, _ = cv2.connectedComponentsWithStats((mask > 0).astype(np.uint8), 8)
    keep = np.zeros(mask.shape, np.uint8)
    for index in range(1, n):
        x, y, w, h, area = [int(v) for v in stats[index]]
        if area >= 3 and w <= 120 and h <= 120:
            keep[labels == index] = 255
    keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    keep = cv2.dilate(keep, np.ones((5, 5), np.uint8), 1)
    keep[~roi] = 0
    return keep


def protected_components(source: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    h, w = source.shape[:2]
    star = np.zeros((h, w), np.uint8)
    sx0, sy0, sx1, sy1 = 246, 232, 318, 312
    gray = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2GRAY)
    star_seed = (gray[sy0:sy1, sx0:sx1] < 165).astype(np.uint8)
    n, labels, stats, centers = cv2.connectedComponentsWithStats(star_seed, 8)
    if n > 1:
        target = np.array([280 - sx0, 251 - sy0], np.float32)
        candidates = []
        for index in range(1, n):
            area = int(stats[index, cv2.CC_STAT_AREA])
            center = centers[index]
            distance = float(np.linalg.norm(center - target))
            if area >= 8:
                candidates.append((distance, -area, index))
        if candidates:
            keep = min(candidates)[2]
            component = (labels == keep).astype(np.uint8) * 255
            component = cv2.dilate(component, np.ones((5, 5), np.uint8), 1)
            star[sy0:sy1, sx0:sx1] = component

    hsv = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2HSV)
    ribbon = np.zeros((h, w), np.uint8)
    x0, y0, x1, y1 = 365, 267, 616, 342
    sub = hsv[y0:y1, x0:x1]
    red = ((sub[..., 1] > 70) & (((sub[..., 0] < 20) | (sub[..., 0] > 168))) & (sub[..., 2] > 42)).astype(np.uint8) * 255
    n, labels, stats, _ = cv2.connectedComponentsWithStats((red > 0).astype(np.uint8), 8)
    if n > 1:
        keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        red = (labels == keep).astype(np.uint8) * 255
    red = cv2.dilate(red, np.ones((13, 13), np.uint8), 1)
    ribbon[y0:y1, x0:x1] = red

    border = np.zeros((h, w), np.uint8)
    plaque = np.zeros((h, w), np.uint8)
    cv2.rectangle(plaque, (220, 120), (615, 315), 255, -1)
    interior = np.zeros((h, w), np.uint8)
    cv2.fillPoly(interior, [np.array([[242, 148], [585, 148], [599, 157], [599, 287], [589, 298], [242, 298], [234, 285], [234, 158]], np.int32)], 255)
    border[(plaque > 0) & (interior == 0)] = 255
    # Hard source-exact guards for all four sides. The v4 Japanese-removal ROI
    # reached into the top/right ornament; these guards close that ownership gap.
    border[118:148, 220:620] = 255
    border[118:320, 582:620] = 255
    border[118:320, 220:240] = 255
    border[292:320, 220:620] = 255
    return star, ribbon, border


def lettering_layer(size: tuple[int, int]) -> tuple[Image.Image, np.ndarray]:
    alpha = Image.open(LETTER_ROOT / "lettering_alpha.png").convert("L").crop(LETTER_BBOX)
    chroma = Image.open(LETTER_ROOT / "source_chroma.png").convert("RGB").crop(LETTER_BBOX)
    alpha = alpha.resize(PLACED_SIZE, Image.Resampling.LANCZOS)
    alpha_array = np.array(alpha, np.float32)
    alpha_array = np.clip(alpha_array * (255.0 / 72.0), 0, 255).astype(np.uint8)
    alpha = Image.fromarray(alpha_array, "L")
    chroma = chroma.resize(PLACED_SIZE, Image.Resampling.LANCZOS)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    rgba = chroma.convert("RGBA")
    rgba.putalpha(alpha)
    layer.alpha_composite(rgba, PLACED_XY)
    target = np.array(layer.getchannel("A"))
    return layer, target


def restore_glyph_regions(source: np.ndarray, v1_clean: np.ndarray, old_mask: np.ndarray) -> np.ndarray:
    src = source[..., :3].astype(np.float32)
    donor = v1_clean[..., :3].astype(np.float32)
    old = old_mask > 0
    # Recover the source-authored reddish parchment cast from nearby untouched paper.
    delta = src - donor
    valid = (~old).astype(np.float32)
    # Exclude very dark non-paper pixels from the normalized tint field.
    gray = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2GRAY)
    valid *= (gray > 178).astype(np.float32)
    sigma = 12.0
    weight = cv2.GaussianBlur(valid, (0, 0), sigma)
    field = np.zeros_like(delta, np.float32)
    for channel in range(3):
        num = cv2.GaussianBlur(delta[..., channel] * valid, (0, 0), sigma)
        field[..., channel] = num / np.maximum(weight, 0.02)
    restored = np.clip(donor + field, 0, 255)

    clean = source.copy().astype(np.float32)
    distance = cv2.distanceTransform(old.astype(np.uint8), cv2.DIST_L2, 3)
    blend = np.clip(distance / 1.15, 0.0, 1.0)[..., None]
    clean[..., :3] = np.where(old[..., None], src * (1.0 - blend) + restored * blend, src)
    clean[..., 3] = source[..., 3]
    clean = np.clip(clean, 0, 255).astype(np.uint8)
    clean[~old] = source[~old]
    return clean


def make_contact(source: Image.Image, previous: Image.Image, clean: Image.Image, candidate: Image.Image) -> Path:
    crop = (170, 80, 660, 380)
    images = [im.convert("RGB").crop(crop) for im in (source, previous, clean, candidate)]
    labels = ["원본", "이전 재작업본", "원문 제거", "축소·질감 복원본"]
    sheet = Image.new("RGB", (1000, 700), (34, 31, 37))
    font = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 22)
    draw = ImageDraw.Draw(sheet)
    positions = [(5, 42), (505, 42), (5, 372), (505, 372)]
    for image, label, (x, y) in zip(images, labels, positions):
        sheet.paste(image, (x, y))
        draw.text((x + 6, y - 33), label, font=font, fill=(248, 248, 248))
    path = OUT / "contact.png"
    sheet.save(path)
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    CANDIDATES.mkdir(parents=True, exist_ok=True)
    sources = sorted(SOURCE_ROOT.glob("*.png"))
    if len(sources) != 8:
        raise RuntimeError(f"expected 8 frames, found {len(sources)}")
    layer, target_alpha = lettering_layer((1280, 720))
    tx, ty = np.where(target_alpha > 0)[1], np.where(target_alpha > 0)[0]
    target_bbox = [int(tx.min()), int(ty.min()), int(tx.max()) + 1, int(ty.max()) + 1]
    sx0, sy0, sx1, sy1 = SAFE_TEXT_RECT
    if not (target_bbox[0] >= sx0 and target_bbox[1] >= sy0 and target_bbox[2] <= sx1 and target_bbox[3] <= sy1):
        raise AssertionError({"target_bbox": target_bbox, "safe": SAFE_TEXT_RECT})

    records = []
    first_images = None
    for index, source_path in enumerate(sources):
        source_image = Image.open(source_path).convert("RGBA")
        source = np.array(source_image)
        v1_clean_path = V1_EVIDENCE / f"clean_{index:02d}.png"
        v1_clean = np.array(Image.open(v1_clean_path).convert("RGBA"))
        old_mask = source_ink_mask(source, v1_clean)
        clean = restore_glyph_regions(source, v1_clean, old_mask)
        candidate_image = Image.fromarray(clean, "RGBA")
        candidate_image.alpha_composite(layer)
        candidate = np.array(candidate_image)

        star, ribbon, border = protected_components(source)
        protected = (star > 0) | (ribbon > 0) | (border > 0)
        # Source ornaments always win over the lettering layer.
        candidate[protected] = source[protected]
        target_effective = (target_alpha > 0) & ~protected
        owned = (old_mask > 0) | target_effective
        candidate[~owned] = source[~owned]
        candidate_image = Image.fromarray(candidate, "RGBA")

        stem = f"title_logo_v5_{index:02d}.png"
        out_path = CANDIDATES / stem
        candidate_image.save(out_path)
        frame_dir = OUT / f"frame_{index:02d}"
        frame_dir.mkdir(parents=True, exist_ok=True)
        Image.fromarray(clean, "RGBA").save(frame_dir / "clean.png")
        Image.fromarray(old_mask, "L").save(frame_dir / "old_text_mask.png")
        Image.fromarray((target_effective.astype(np.uint8) * 255), "L").save(frame_dir / "target_text_mask.png")

        clean_diff = np.any(source != clean, axis=2)
        final_diff = np.any(source != candidate, axis=2)
        row_widths = clean_diff.sum(axis=1)
        longest_runs = []
        for row in clean_diff:
            padded = np.pad(row.astype(np.int8), (1, 1))
            edges = np.flatnonzero(np.diff(padded))
            longest_runs.append(int(np.max(edges[1::2] - edges[::2])) if len(edges) else 0)
        validation = {
            "dimensions": [1280, 720],
            "alpha_exact": bool(np.array_equal(source[..., 3], clean[..., 3]) and np.array_equal(source[..., 3], candidate[..., 3])),
            "source_exact_outside_old_and_target": bool(np.array_equal(source[~owned], candidate[~owned])),
            "clean_exact_outside_source_glyphs": bool(np.array_equal(source[old_mask == 0], clean[old_mask == 0])),
            "red_border_exact": bool(np.array_equal(source[border > 0], candidate[border > 0])),
            "star_exact": bool(np.array_equal(source[star > 0], candidate[star > 0])),
            "ribbon_exact": bool(np.array_equal(source[ribbon > 0], candidate[ribbon > 0])),
            "old_text_mask_pixels": int(np.count_nonzero(old_mask)),
            "target_text_pixels": int(np.count_nonzero(target_effective)),
            "changed_pixels": int(np.count_nonzero(final_diff)),
            "max_clean_changed_width_per_row": int(row_widths.max()),
            "max_contiguous_clean_run": int(max(longest_runs)),
            "rows_with_plate_width_contiguous_run": int(np.count_nonzero(np.array(longest_runs) > 200)),
            "rectangular_clean_plate_detected": bool(np.count_nonzero(np.array(longest_runs) > 200) > 5),
            "target_bbox": target_bbox,
            "safe_text_rect": list(SAFE_TEXT_RECT),
        }
        if not all([
            validation["alpha_exact"],
            validation["source_exact_outside_old_and_target"],
            validation["clean_exact_outside_source_glyphs"],
            validation["red_border_exact"],
            validation["star_exact"],
            validation["ribbon_exact"],
            not validation["rectangular_clean_plate_detected"],
        ]):
            raise AssertionError(validation)
        records.append({
            "frame": index,
            "source": str(source_path),
            "clean": str(frame_dir / "clean.png"),
            "candidate": str(out_path),
            "sha256": sha(out_path),
            "validation": validation,
        })
        if index == 0:
            previous = Image.open(LETTER_ROOT / "candidate_frames" / "title_logo_v3_00.png").convert("RGBA")
            first_images = (source_image, previous, Image.fromarray(clean, "RGBA"), candidate_image)

    contact = make_contact(*first_images)
    manifest = {
        "schema": "fairytale-requiem-title-logo-redraw-v5",
        "status": "USER_REVIEW_REQUIRED_NOT_INSTALLED",
        "supersedes": "grpe_title_logo_korean_v4_source_texture_review (top/right frame guard incomplete)",
        "target": TEXT,
        "design": {
            "lettering": "retains the accepted custom fairy-tale calligraphy, scaled to the original red-border interior",
            "placed_xy": list(PLACED_XY),
            "placed_size": list(PLACED_SIZE),
            "frame_guard": {"top": [220, 118, 620, 148], "right": [582, 118, 620, 320], "left": [220, 118, 240, 320], "bottom": [220, 292, 620, 320]},
            "safe_text_rect": list(SAFE_TEXT_RECT),
            "surface": "source parchment retained pixel-exact outside Japanese glyphs; glyph holes restored from the existing clean donor with source-derived reddish cast",
            "protected": ["red ornamental border", "four-point star", "English red ribbon"],
        },
        "contact": str(contact),
        "frame_count": len(records),
        "installed": False,
        "records": records,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path = OUT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifest": str(manifest_path),
        "contact": str(contact),
        "target_bbox": target_bbox,
        "frame_count": len(records),
        "all_checks": all(all(v for k, v in r["validation"].items() if isinstance(v, bool)) for r in records),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


