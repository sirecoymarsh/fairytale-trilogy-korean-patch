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
OUT = PROJECT / "staging" / "grpe_title_logo_korean_v6_full_clean_frame_exact_review"
CANDIDATES = OUT / "candidate_frames"
TEXT = "페어리테일 레퀴엠"
LETTER_BBOX = (149, 177, 1493, 782)
PLACED_SIZE = (262, 118)
PLACED_XY = (291, 162)
SAFE_TEXT_RECT = (286, 158, 560, 284)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def source_ink_mask(source: np.ndarray, v1_clean: np.ndarray) -> np.ndarray:
    rgb = source[..., :3]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clean_gray = cv2.cvtColor(v1_clean[..., :3], cv2.COLOR_RGB2GRAY)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    roi = np.zeros(gray.shape, bool)
    roi[125:310, 220:620] = True
    seed = roi & (gray < 190) & ((clean_gray.astype(np.int16) - gray.astype(np.int16)) > 24) & (hsv[..., 1] < 138)
    mask = seed.astype(np.uint8) * 255
    n, labels, stats, _ = cv2.connectedComponentsWithStats((mask > 0).astype(np.uint8), 8)
    keep = np.zeros(mask.shape, np.uint8)
    for index in range(1, n):
        x, y, w, h, area = [int(v) for v in stats[index]]
        if area >= 2 and w <= 125 and h <= 125:
            keep[labels == index] = 255
    keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    keep = cv2.dilate(keep, np.ones((7, 7), np.uint8), 1)
    keep[~roi] = 0
    return keep

def protected_components(source: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    h, w = source.shape[:2]
    gray = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2GRAY)
    lab_image = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2LAB)

    star = np.zeros((h, w), np.uint8)
    sx0, sy0, sx1, sy1 = 246, 232, 318, 312
    star_seed = (gray[sy0:sy1, sx0:sx1] < 165).astype(np.uint8)
    n, labels, stats, centers = cv2.connectedComponentsWithStats(star_seed, 8)
    if n > 1:
        target = np.array([280 - sx0, 251 - sy0], np.float32)
        choices = []
        for index in range(1, n):
            area = int(stats[index, cv2.CC_STAT_AREA])
            if area >= 8:
                choices.append((float(np.linalg.norm(centers[index] - target)), -area, index))
        if choices:
            component = (labels == min(choices)[2]).astype(np.uint8) * 255
            component = cv2.dilate(component, np.ones((5, 5), np.uint8), 1)
            star[sy0:sy1, sx0:sx1] = component

    hsv = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2HSV)
    ribbon = np.zeros((h, w), np.uint8)
    x0, y0, x1, y1 = 365, 267, 616, 342
    sub = hsv[y0:y1, x0:x1]
    red = ((sub[..., 1] > 70) & (((sub[..., 0] < 20) | (sub[..., 0] > 168))) & (sub[..., 2] > 42)).astype(np.uint8) * 255
    n, labels, stats, _ = cv2.connectedComponentsWithStats((red > 0).astype(np.uint8), 8)
    if n > 1:
        red = (labels == (1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA])))).astype(np.uint8) * 255
    red = cv2.dilate(red, np.ones((13, 13), np.uint8), 1)
    ribbon[y0:y1, x0:x1] = red

    border = np.zeros((h, w), np.uint8)
    border[112:150, 214:622] = 255
    border[112:322, 214:260] = 255
    border[112:322, 574:622] = 255
    border[284:322, 214:622] = 255
    rim = np.zeros((h, w), bool)
    rim[112:162, 214:622] = True
    rim[112:322, 214:270] = True
    rim[112:322, 565:622] = True
    rim[275:322, 214:622] = True
    red_ornament = rim & (lab_image[..., 1] > 140)
    red_ornament = cv2.dilate(red_ornament.astype(np.uint8), np.ones((5, 5), np.uint8), 1)
    border[red_ornament > 0] = 255
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


def restore_complete_face(source: np.ndarray, v1_clean: np.ndarray, old_mask: np.ndarray,
                          protected: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    src = source[..., :3].astype(np.float32)
    donor = v1_clean[..., :3].astype(np.float32)
    gray = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2GRAY)
    lab_image = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2LAB)
    old = (old_mask > 0) & ~protected

    face = np.zeros(old.shape, np.uint8)
    polygon = np.array([[242, 145], [585, 145], [600, 157], [600, 287],
                        [588, 300], [241, 300], [231, 286], [231, 158]], np.int32)
    cv2.fillPoly(face, [polygon], 255)
    face_bool = face > 0

    # Reapply the original low-frequency reddish cast to the coherent clean donor.
    delta = src - donor
    valid = face_bool & ~old & (gray > 178) & ~protected
    weight = cv2.GaussianBlur(valid.astype(np.float32), (0, 0), 12.0)
    field = np.zeros_like(delta, np.float32)
    for channel in range(3):
        num = cv2.GaussianBlur(delta[..., channel] * valid.astype(np.float32), (0, 0), 12.0)
        field[..., channel] = num / np.maximum(weight, 0.02)
    restored = np.clip(donor + field, 0, 255)

    clean = source.copy().astype(np.float32)
    distance = cv2.distanceTransform(face_bool.astype(np.uint8), cv2.DIST_L2, 3)
    blend = np.clip(distance / 12.0, 0.0, 1.0)[..., None]
    clean[..., :3] = np.where(face_bool[..., None], src * (1.0 - blend) + restored * blend, src)

    # Restore the source-authored red freckles and stains, never neutral/dark old glyphs.
    red_texture = face_bool & (lab_image[..., 1] >= 134) & (gray > 165) & ~old & ~protected
    clean[red_texture, :3] = src[red_texture]

    # Close any old-glyph pixels that extend outside the coherent face polygon.
    clean[old, :3] = restored[old]
    clean[..., 3] = source[..., 3]
    clean = np.clip(clean, 0, 255).astype(np.uint8)
    clean[protected] = source[protected]
    owned_clean = face_bool | old
    clean[~owned_clean] = source[~owned_clean]
    return clean, (owned_clean.astype(np.uint8) * 255), (red_texture.astype(np.uint8) * 255)

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
        star, ribbon, border = protected_components(source)
        protected = (star > 0) | (ribbon > 0) | (border > 0)
        old_mask[protected] = 0
        clean, clean_owner_mask, red_texture_mask = restore_complete_face(source, v1_clean, old_mask, protected)
        candidate_image = Image.fromarray(clean, "RGBA")
        candidate_image.alpha_composite(layer)
        candidate = np.array(candidate_image)

        # Source ornaments always win over the lettering layer.
        candidate[protected] = source[protected]
        target_effective = (target_alpha > 0) & ~protected
        owned = (clean_owner_mask > 0) | target_effective
        candidate[~owned] = source[~owned]
        candidate_image = Image.fromarray(candidate, "RGBA")

        stem = f"title_logo_v6_{index:02d}.png"
        out_path = CANDIDATES / stem
        candidate_image.save(out_path)
        frame_dir = OUT / f"frame_{index:02d}"
        frame_dir.mkdir(parents=True, exist_ok=True)
        Image.fromarray(clean, "RGBA").save(frame_dir / "clean.png")
        Image.fromarray(old_mask, "L").save(frame_dir / "old_text_mask.png")
        Image.fromarray(clean_owner_mask, "L").save(frame_dir / "clean_owner_mask.png")
        Image.fromarray(red_texture_mask, "L").save(frame_dir / "red_texture_mask.png")
        Image.fromarray((target_effective.astype(np.uint8) * 255), "L").save(frame_dir / "target_text_mask.png")

        clean_diff = np.any(source != clean, axis=2)
        final_diff = np.any(source != candidate, axis=2)
        clean_gray = cv2.cvtColor(clean[..., :3], cv2.COLOR_RGB2GRAY)
        old_effective = (old_mask > 0) & ~protected
        clean_old_dark = int(np.count_nonzero(old_effective & (clean_gray < 165)))
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
            "clean_exact_outside_owned_face": bool(np.array_equal(source[clean_owner_mask == 0], clean[clean_owner_mask == 0])),
            "red_border_exact": bool(np.array_equal(source[border > 0], candidate[border > 0])),
            "star_exact": bool(np.array_equal(source[star > 0], candidate[star > 0])),
            "ribbon_exact": bool(np.array_equal(source[ribbon > 0], candidate[ribbon > 0])),
            "old_text_mask_pixels": int(np.count_nonzero(old_mask)),
            "clean_old_logo_dark_pixels": clean_old_dark,
            "previous_logo_residue_zero": bool(clean_old_dark == 0),
            "red_texture_pixels_restored_exact": int(np.count_nonzero(red_texture_mask)),
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
            validation["clean_exact_outside_owned_face"],
            validation["red_border_exact"],
            validation["star_exact"],
            validation["ribbon_exact"],
            validation["previous_logo_residue_zero"],
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
        "schema": "fairytale-requiem-title-logo-redraw-v6",
        "status": "USER_REVIEW_REQUIRED_NOT_INSTALLED",
        "supersedes": "grpe_title_logo_korean_v5_frame_guard_review (frame intrusion and previous-logo residue)",
        "target": TEXT,
        "design": {
            "lettering": "retains the accepted custom fairy-tale calligraphy, scaled to the original red-border interior",
            "placed_xy": list(PLACED_XY),
            "placed_size": list(PLACED_SIZE),
            "frame_guard": {"top": [214, 112, 622, 150], "right": [574, 112, 622, 322], "left": [214, 112, 260, 322], "bottom": [214, 284, 622, 322], "red_ornament_lab_a_min": 141},
            "safe_text_rect": list(SAFE_TEXT_RECT),
            "surface": "complete plaque interior rebuilt from one coherent clean donor, then source-derived red cast and exact red freckles restored; previous logo removed before Korean lettering",
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


