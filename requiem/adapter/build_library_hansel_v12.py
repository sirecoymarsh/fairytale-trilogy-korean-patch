from __future__ import annotations

from pathlib import Path
import hashlib
import json

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
SOURCE_ROOT = PROJECT / "staging" / "ui_other_banks_audit_v1" / "exported_png" / "grpo_lib"
OUT = PROJECT / "staging" / "library_books_rebuild_v12" / "hansel_gretel"
FONT = PROJECT / "tools" / "fonts" / "Gaegu-Bold.ttf"
TITLE = "헨젤과 그레텔"
CHARS = tuple(TITLE.replace(" ", ""))
SCALE = 4


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(path: Path) -> np.ndarray:
    return np.array(Image.open(path).convert("RGBA"))


def raw_source_ink(source: np.ndarray) -> np.ndarray:
    rgb = source[..., :3].astype(np.int16)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    gray = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2GRAY)
    roi = np.zeros(gray.shape, bool)
    roi[28:414, 53:102] = True
    # The source title is the low-luminance, red-brown ink on the yellow spine.
    # Keep this as a glyph detector; never promote the ROI itself to an owned mask.
    seed = roi & (source[..., 3] > 0) & (gray < 174) & (r < 182) & (g < 150)
    mask = seed.astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    mask = cv2.dilate(mask, np.ones((4, 4), np.uint8), 1)
    mask[~roi] = 0
    return mask


def donor_clean(source: np.ndarray, old_mask: np.ndarray) -> tuple[np.ndarray, list[dict]]:
    """Restore each connected glyph group from one same-book, constant-offset donor."""
    h, w = old_mask.shape
    binary = (old_mask > 0).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, 8)
    clean = source.copy().astype(np.float32)
    source_rgb = source[..., :3].astype(np.float32)
    source_alpha = source[..., 3]
    ink = raw_source_ink(source) > 0
    records: list[dict] = []

    for label in range(1, count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area < 5:
            continue
        owned = labels == label
        ys, xs = np.where(owned)
        ring = cv2.dilate(owned.astype(np.uint8), np.ones((7, 7), np.uint8), 1).astype(bool) & ~owned
        ring &= (source_alpha > 0) & ~ink
        rys, rxs = np.where(ring)
        cy = int(round(float(ys.mean())))
        candidate_offsets: set[tuple[int, int]] = set()
        # Search same-row fibres away from the vertical title.
        for dx in range(-55, 56, 5):
            if abs(dx) >= 20:
                candidate_offsets.add((dx, 0))
        # Search clean upper/lower same-book bands. Each connected component
        # receives exactly one constant donor displacement.
        for target_cy in (38, 438, 470, 505, 535):
            for dx in range(-30, 31, 5):
                candidate_offsets.add((dx, target_cy - cy))

        best = None
        for dx, dy in sorted(candidate_offsets):
            dys, dxs = ys + dy, xs + dx
            drys, drxs = rys + dy, rxs + dx
            if (dys.min() < 0 or dys.max() >= h or dxs.min() < 0 or dxs.max() >= w or
                    drys.min() < 0 or drys.max() >= h or drxs.min() < 0 or drxs.max() >= w):
                continue
            contamination = float(ink[dys, dxs].sum()) / max(1, owned.sum())
            if contamination > 0.0 or np.any(source_alpha[dys, dxs] == 0):
                continue
            valid = source_alpha[drys, drxs] > 0
            if valid.sum() < 8:
                continue
            target_ring = source_rgb[rys[valid], rxs[valid]]
            donor_ring = source_rgb[drys[valid], drxs[valid]]
            delta = np.median(target_ring - donor_ring, axis=0)
            matched_ring = np.clip(donor_ring + delta, 0, 255)
            edge_error = float(np.mean(np.abs(target_ring - matched_ring)))
            texture_error = float(np.mean(np.abs(np.std(target_ring, axis=0) - np.std(donor_ring, axis=0))))
            delta_penalty = float(np.mean(np.abs(delta)))
            score = edge_error + texture_error * 0.35 + delta_penalty * 0.12 + abs(dx) * 0.003 + abs(dy) * 0.004
            if best is None or score < best[0]:
                best = (score, dx, dy, delta)

        if best is None:
            raise RuntimeError(f"No clean coherent donor for glyph component {label}")
        score, dx, dy, delta = best
        matched_pixels = np.clip(source_rgb[ys + dy, xs + dx] + delta, 0, 255)
        # Feather only inside the glyph-owned mask. No enclosing face/rectangle changes.
        distance = cv2.distanceTransform(owned.astype(np.uint8), cv2.DIST_L2, 3)
        alpha_pixels = np.clip(distance[ys, xs] / 0.9, 0.0, 1.0)[:, None]
        clean[ys, xs, :3] = source_rgb[ys, xs] * (1.0 - alpha_pixels) + matched_pixels * alpha_pixels
        records.append({
            "component": int(label),
            "pixels": area,
            "offset": [int(dx), int(dy)],
            "edge_score": round(float(score), 4),
            "rgb_correction": [round(float(v), 3) for v in delta],
        })

    clean[..., 3] = source[..., 3]
    clean = np.clip(clean, 0, 255).astype(np.uint8)
    clean[old_mask == 0] = source[old_mask == 0]
    return clean, records

def render_text(size: tuple[int, int]) -> Image.Image:
    width, height = size
    canvas = Image.new("L", (width * SCALE, height * SCALE), 0)
    font = ImageFont.truetype(str(FONT), 46 * SCALE)
    centers_y = (61, 119, 177, 255, 313, 371)
    angles = (-1.4, 0.8, -0.7, 1.0, -0.9, 1.2)
    for char, center_y, angle in zip(CHARS, centers_y, angles):
        box = 60 * SCALE
        glyph = Image.new("L", (box, box), 0)
        draw = ImageDraw.Draw(glyph)
        bbox = draw.textbbox((0, 0), char, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((box - tw) / 2 - bbox[0], (box - th) / 2 - bbox[1]), char, font=font, fill=255)
        glyph = glyph.rotate(angle, Image.Resampling.BICUBIC, expand=False)
        center_x = 74.0 + 0.010 * (center_y - centers_y[0])
        x = int(center_x * SCALE - box / 2)
        y = int(center_y * SCALE - box / 2)
        prior = canvas.crop((x, y, x + box, y + box))
        canvas.paste(ImageChops.lighter(prior, glyph), (x, y))
    alpha = canvas.resize((width, height), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(0.12))
    layer = Image.new("RGBA", (width, height), (48, 26, 25, 0))
    layer.putalpha(alpha)
    return layer


def fit_state(normal: np.ndarray, selected: np.ndarray) -> list[tuple[float, float]]:
    opaque = (normal[..., 3] > 0) & (selected[..., 3] > 0)
    out = []
    for channel in range(3):
        x = normal[..., channel][opaque].astype(np.float64)
        y = selected[..., channel][opaque].astype(np.float64)
        a, b = np.polyfit(x, y, 1)
        out.append((float(a), float(b)))
    return out


def apply_state(image: np.ndarray, coeffs: list[tuple[float, float]], alpha: np.ndarray) -> np.ndarray:
    out = image.astype(np.float32).copy()
    for channel, (a, b) in enumerate(coeffs):
        out[..., channel] = out[..., channel] * a + b
    out = np.clip(out, 0, 255).astype(np.uint8)
    out[..., 3] = alpha
    return out


def persist(stem: str, state: str, source: np.ndarray, clean: np.ndarray, candidate: np.ndarray,
            old_mask: np.ndarray, target_mask: np.ndarray) -> dict:
    folder = OUT / stem
    folder.mkdir(parents=True, exist_ok=True)
    files = {
        "source": folder / "source.png",
        "clean": folder / "clean.png",
        "candidate": folder / "candidate.png",
        "old_text_mask": folder / "old_text_mask.png",
        "target_text_mask": folder / "target_text_mask.png",
    }
    Image.fromarray(source, "RGBA").save(files["source"])
    Image.fromarray(clean, "RGBA").save(files["clean"])
    Image.fromarray(candidate, "RGBA").save(files["candidate"])
    Image.fromarray(old_mask, "L").save(files["old_text_mask"])
    Image.fromarray(target_mask, "L").save(files["target_text_mask"])
    clean_diff = np.any(source != clean, axis=2)
    final_diff = np.any(source != candidate, axis=2)
    owned = (old_mask > 0) | (target_mask > 0)
    row_widths = clean_diff.sum(axis=1)
    count, _, stats, _ = cv2.connectedComponentsWithStats(clean_diff.astype(np.uint8), 8)
    components = [int(s[cv2.CC_STAT_AREA]) for s in stats[1:]]
    validation = {
        "dimensions": [int(source.shape[1]), int(source.shape[0])],
        "alpha_geometry_byte_exact": bool(np.array_equal(source[..., 3], clean[..., 3]) and np.array_equal(source[..., 3], candidate[..., 3])),
        "clean_changes_only_glyph_mask": bool(np.all(~clean_diff | (old_mask > 0))),
        "candidate_protected_pixels_byte_exact": bool(np.array_equal(source[~owned], candidate[~owned])),
        "old_text_mask_pixels": int(np.count_nonzero(old_mask)),
        "target_text_mask_pixels": int(np.count_nonzero(target_mask)),
        "clean_changed_pixels": int(np.count_nonzero(clean_diff)),
        "clean_connected_components": int(count - 1),
        "largest_clean_component": max(components, default=0),
        "max_changed_width_in_any_row": int(row_widths.max()),
        "rectangular_plate_detected": bool(np.count_nonzero(row_widths > 45) > 10),
        "source_pixels_exact_outside_glyphs": bool(np.array_equal(source[~(old_mask > 0)], clean[~(old_mask > 0)])),
        "final_changes_only_old_or_target_ink": bool(np.all(~final_diff | owned)),
    }
    if not all([
        validation["alpha_geometry_byte_exact"],
        validation["clean_changes_only_glyph_mask"],
        validation["candidate_protected_pixels_byte_exact"],
        validation["source_pixels_exact_outside_glyphs"],
        validation["final_changes_only_old_or_target_ink"],
        not validation["rectangular_plate_detected"],
    ]):
        raise AssertionError(validation)
    return {
        "stem": stem,
        "state": state,
        "title": TITLE,
        "files": {key: str(path) for key, path in files.items()},
        "sha256": {key: sha(path) for key, path in files.items()},
        "validation": validation,
    }


def make_contact(records: list[dict]) -> Path:
    labels = ["원본", "원문 제거", "한국어"]
    normal = [Image.open(records[0]["files"][key]).convert("RGBA") for key in ("source", "clean", "candidate")]
    selected = [Image.open(records[1]["files"][key]).convert("RGBA") for key in ("source", "clean", "candidate")]
    cell_w, cell_h = 220, 620
    sheet = Image.new("RGB", (cell_w * 3, cell_h * 2), (42, 38, 45))
    font = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 20)
    draw = ImageDraw.Draw(sheet)
    for row, images in enumerate((normal, selected)):
        for col, image in enumerate(images):
            x = col * cell_w + (cell_w - image.width) // 2
            y = row * cell_h + 38
            bg = Image.new("RGBA", image.size, (225, 225, 225, 255))
            bg.alpha_composite(image)
            sheet.paste(bg.convert("RGB"), (x, y))
            draw.text((col * cell_w + 12, 9), f"{labels[col]} · {'기본' if row == 0 else '선택'}", font=font, fill=(245, 245, 245))
    path = OUT / "contact.png"
    sheet.save(path)
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    normal_source = load(SOURCE_ROOT / "0012.png")
    selected_source = load(SOURCE_ROOT / "0112.png")
    old_mask = raw_source_ink(normal_source)
    normal_clean, donors = donor_clean(normal_source, old_mask)
    layer = render_text((normal_source.shape[1], normal_source.shape[0]))
    normal_candidate_image = Image.fromarray(normal_clean, "RGBA")
    normal_candidate_image.alpha_composite(layer)
    normal_candidate = np.array(normal_candidate_image)
    target_mask = (np.array(layer.getchannel("A")) > 0).astype(np.uint8) * 255

    coeffs = fit_state(normal_source, selected_source)
    selected_clean_x = apply_state(normal_clean, coeffs, selected_source[..., 3])
    selected_candidate_x = apply_state(normal_candidate, coeffs, selected_source[..., 3])
    old = old_mask > 0
    owned = old | (target_mask > 0)
    selected_clean = selected_source.copy()
    selected_clean[old] = selected_clean_x[old]
    selected_candidate = selected_source.copy()
    selected_candidate[owned] = selected_candidate_x[owned]

    records = [
        persist("0012", "normal", normal_source, normal_clean, normal_candidate, old_mask, target_mask),
        persist("0112", "hover_or_selected", selected_source, selected_clean, selected_candidate, old_mask, target_mask),
    ]
    contact = make_contact(records)
    manifest = {
        "schema": "fairytale-requiem-library-hansel-gretel-v12",
        "status": "USER_REVIEW_REQUIRED_NOT_INSTALLED",
        "supersedes": "library_books_rebuild_v11/0012 (REJECTED_RECTANGULAR_DONOR_SLAB)",
        "title": TITLE,
        "method": "book-specific glyph-component surgery with one coherent same-book donor offset per component",
        "rules": {
            "alice_face_not_reused": True,
            "no_rectangular_face_or_backing_plate": True,
            "source_exact_outside_old_and_target_glyphs": True,
            "normal_selected_pair": True,
            "installed": False,
        },
        "donors": donors,
        "hover_affine_rgb": coeffs,
        "contact": str(contact),
        "records": records,
    }
    path = OUT / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(path), "contact": str(contact), "validation": [r["validation"] for r in records]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
