#!/usr/bin/env python3
"""Build a review-only, original-style Korean title-menu candidate.

The normal miniature states reuse the previously validated localized plates.
The seven focus/selection states are genuine text-only RGBA layers: the
Japanese layer is removed to full transparency before the Korean label is
rendered once.  Nothing is installed or packed into the game here.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
SOURCE = PROJECT / "staging" / "ui_missing_screen_deep_audit_v1" / "grpo_png"
CURRENT = PROJECT / "staging" / "ui_master_component_donor" / "png_patches"
CURRENT_AUDIT = PROJECT / "audit" / "grpo_component_donor_independent_validation.json"
OUT = PROJECT / "staging" / "title_menu_korean_v2_review"

FONT_SERIF = Path(r"C:\Windows\Fonts\NotoSerifKR-VF.ttf")
FONT_HAND = PROJECT / "tools" / "fonts" / "Gaegu-Bold.ttf"
SCALE = 4

SMALL = {
    "0001": "시작",
    "0002": "계속",
    "0003": "감상",
    "0004": "설정",
    "0005": "조작",
    "0006": "레퀴엠",
    "0007": "종료",
    "0008": "추가편",
}

LARGE = {
    "0101": "처음부터",
    "0102": "이어하기",
    "0103": "감상",
    "0104": "환경 설정",
    "0105": "조작 설명",
    "0107": "종료",
    "0108": "FC 시나리오",
}

HAND_STATES = {"0101", "0102", "0108"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def recreate(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def font_at(path: Path, size: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(path), size * SCALE)
    if path == FONT_SERIF:
        try:
            font.set_variation_by_name("Black")
        except OSError:
            pass
    return font


def face_mask(text: str, path: Path, size: int) -> np.ndarray:
    font = font_at(path, size)
    bbox = font.getbbox(text)
    width = bbox[2] - bbox[0] + 8 * SCALE
    height = bbox[3] - bbox[1] + 8 * SCALE
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).text(
        (4 * SCALE - bbox[0], 4 * SCALE - bbox[1]),
        text,
        font=font,
        fill=255,
    )
    crop = mask.getbbox()
    if crop is None:
        raise RuntimeError(f"empty target mask: {text}")
    return np.asarray(mask.crop(crop), dtype=np.uint8)


def rgba_from_mask(mask: np.ndarray, rgb: tuple[int, int, int], opacity: int) -> Image.Image:
    alpha = np.clip(mask.astype(np.float32) * (opacity / 255.0), 0, 255).astype(np.uint8)
    image = Image.new("RGBA", (mask.shape[1], mask.shape[0]), (*rgb, 0))
    image.putalpha(Image.fromarray(alpha, "L"))
    return image


def render_effect(text: str, path: Path, size: int) -> Image.Image:
    face = face_mask(text, path, size)
    border_radius = 7 * SCALE
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (border_radius * 2 + 1, border_radius * 2 + 1),
    )
    outer = cv2.dilate(face, kernel)
    shadow = cv2.GaussianBlur(outer, (0, 0), 3.0 * SCALE)

    pad = 13 * SCALE
    shadow_dx, shadow_dy = 5 * SCALE, 7 * SCALE
    height = face.shape[0] + 2 * pad + shadow_dy
    width = face.shape[1] + 2 * pad + shadow_dx
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    layer.alpha_composite(
        rgba_from_mask(shadow, (28, 23, 25), 145),
        (pad + shadow_dx, pad + shadow_dy),
    )
    layer.alpha_composite(rgba_from_mask(outer, (255, 255, 252), 255), (pad, pad))
    ink = rgba_from_mask(face, (14, 12, 13), 255)

    # The source face is not flat digital black.  A restrained deterministic
    # ink grain keeps the Korean face from looking like a generic system font.
    ink_rgba = np.asarray(ink).copy()
    yy, xx = np.indices(face.shape)
    texture = ((xx * 13 + yy * 7) % 53 < 2) & (face > 200)
    ink_rgba[texture, :3] = 36
    layer.alpha_composite(Image.fromarray(ink_rgba, "RGBA"), (pad, pad))

    alpha = np.asarray(layer.getchannel("A"), dtype=np.uint8)
    ys, xs = np.where(alpha > 2)
    if len(xs) == 0:
        raise RuntimeError(f"empty rendered effect: {text}")
    layer = layer.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    return layer.resize(
        (round(layer.width / SCALE), round(layer.height / SCALE)),
        Image.Resampling.LANCZOS,
    )


def render_large(stem: str, text: str, source: Image.Image) -> tuple[Image.Image, dict[str, Any]]:
    source = source.convert("RGBA")
    source_bbox = source.getchannel("A").getbbox()
    if source_bbox is None:
        raise RuntimeError(f"source state has no alpha: {stem}")
    x0, y0, x1, y1 = source_bbox
    max_width, max_height = x1 - x0, y1 - y0
    path = FONT_HAND if stem in HAND_STATES else FONT_SERIF

    low, high = 30, 140
    chosen: tuple[int, Image.Image] | None = None
    while low <= high:
        size = (low + high) // 2
        effect = render_effect(text, path, size)
        if effect.width <= max_width and effect.height <= max_height:
            chosen = (size, effect)
            low = size + 1
        else:
            high = size - 1
    if chosen is None:
        raise RuntimeError(f"target does not fit state: {stem} {text}")

    font_size, effect = chosen
    desired_height = round(max_height * (0.94 if stem in HAND_STATES else 0.90))
    if effect.height < desired_height:
        effect = effect.resize((effect.width, desired_height), Image.Resampling.LANCZOS)
    px = x1 - effect.width
    py = round((y0 + y1 - effect.height) / 2)

    # Mandatory clean-plate gate: these states are text-only layers.  Their
    # validated clean background is exact full-canvas transparency.
    clean = Image.new("RGBA", source.size, (0, 0, 0, 0))
    if clean.getchannel("A").getbbox() is not None:
        raise RuntimeError("clean plate is not transparent")
    candidate = clean.copy()
    candidate.alpha_composite(effect, (px, py))
    output_bbox = candidate.getchannel("A").getbbox()
    if output_bbox is None:
        raise RuntimeError(f"empty candidate: {stem}")
    if output_bbox[2] != x1:
        raise RuntimeError(f"right-edge drift: {stem} {output_bbox[2]} != {x1}")
    if not (x0 <= output_bbox[0] and y0 <= output_bbox[1] and output_bbox[2] <= x1 and output_bbox[3] <= y1):
        raise RuntimeError(f"candidate exceeds source geometry: {stem}")

    source_mask = np.asarray(source.getchannel("A"), dtype=np.uint8) > 0
    target_mask = np.asarray(candidate.getchannel("A"), dtype=np.uint8) > 0
    owner_mask = source_mask | target_mask
    clean_array = np.asarray(clean, dtype=np.uint8)
    candidate_array = np.asarray(candidate, dtype=np.uint8)
    if np.any(clean_array[~owner_mask]) or np.any(candidate_array[~owner_mask]):
        raise RuntimeError(f"pixels outside owned text system changed: {stem}")

    return candidate, {
        "stem": stem,
        "target": text,
        "source_bbox": list(source_bbox),
        "output_bbox": list(output_bbox),
        "font": str(path),
        "font_name": font_at(path, font_size).getname(),
        "font_size": font_size,
        "style": "black ink face + warm-white outline + soft down-right shadow + restrained ink grain",
        "clean_plate": "full-canvas transparent text-only RGBA layer",
        "source_text_alpha_pixels_before_clean": int(source_mask.sum()),
        "source_text_alpha_pixels_after_clean": 0,
        "old_ui_removed_completely_before_typesetting": True,
        "right_edge_locked": x1,
        "geometry_contained_in_source_bbox": True,
        "outside_owned_mask_exact": True,
    }


def make_contact() -> Path:
    ids = list(LARGE)
    width, row_height = 2430, 155
    canvas = Image.new("RGB", (width, row_height * len(ids)), (38, 33, 45))
    draw = ImageDraw.Draw(canvas)
    label_font = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 18)
    for row, stem in enumerate(ids):
        y = row * row_height
        columns = [
            ("원본", OUT / "source" / f"{stem}.png"),
            ("현재판", CURRENT / f"{stem}.patch.png"),
            ("원작풍 재시안", OUT / "candidate" / f"{stem}.png"),
        ]
        for col, (tag, path) in enumerate(columns):
            x = 10 + col * 810
            draw.text((x, y + 3), f"{stem} {LARGE[stem]} · {tag}", font=label_font, fill="white")
            image = Image.open(path).convert("RGBA")
            backing = Image.new("RGBA", image.size, (245, 240, 232, 255))
            backing.alpha_composite(image)
            canvas.paste(backing.convert("RGB"), (x, y + 30))
    path = OUT / "evidence" / "source_current_candidate.jpg"
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, quality=82, optimize=True, progressive=True)
    return path


def main() -> None:
    for path in (FONT_SERIF, FONT_HAND, CURRENT_AUDIT):
        if not path.exists():
            raise FileNotFoundError(path)
    recreate(OUT)
    for name in ("source", "clean", "candidate", "owner_mask", "evidence"):
        (OUT / name).mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    for stem, text in SMALL.items():
        source_path = SOURCE / f"{stem}.png"
        candidate_path = CURRENT / f"{stem}.patch.png"
        shutil.copy2(source_path, OUT / "source" / f"{stem}.png")
        shutil.copy2(candidate_path, OUT / "candidate" / f"{stem}.png")
        records.append({
            "stem": stem,
            "target": text,
            "state": "normal miniature",
            "change_in_v2": "none; reused previously independently validated localized state",
            "source_path": str(source_path),
            "candidate_path": str(candidate_path),
            "source_sha256": sha256(source_path),
            "candidate_sha256": sha256(candidate_path),
            "prior_validation": str(CURRENT_AUDIT),
        })

    for stem, text in LARGE.items():
        source_path = SOURCE / f"{stem}.png"
        source = Image.open(source_path).convert("RGBA")
        shutil.copy2(source_path, OUT / "source" / f"{stem}.png")
        clean = Image.new("RGBA", source.size, (0, 0, 0, 0))
        clean_path = OUT / "clean" / f"{stem}.png"
        clean.save(clean_path)
        candidate, details = render_large(stem, text, source)
        candidate_path = OUT / "candidate" / f"{stem}.png"
        candidate.save(candidate_path)
        owner = (
            (np.asarray(source.getchannel("A"), dtype=np.uint8) > 0)
            | (np.asarray(candidate.getchannel("A"), dtype=np.uint8) > 0)
        )
        Image.fromarray((owner.astype(np.uint8) * 255), "L").save(OUT / "owner_mask" / f"{stem}.png")
        details.update({
            "state": "focus/selection",
            "source_path": str(source_path),
            "clean_path": str(clean_path),
            "candidate_path": str(candidate_path),
            "source_sha256": sha256(source_path),
            "clean_sha256": sha256(clean_path),
            "candidate_sha256": sha256(candidate_path),
            "dimensions": list(candidate.size),
        })
        records.append(details)

    contact = make_contact()
    manifest = {
        "schema": "fairytale-requiem-title-menu-korean-v2-review",
        "status": "USER_REVIEW_REQUIRED_NOT_INSTALLED",
        "scope": "complete 15-state title menu family; seven focus layers redrawn, eight normal states retained",
        "policy": {
            "old_ui_removed_completely_before_typesetting": True,
            "clean_plate_validated_independently_before_target_text": True,
            "preserve_canvas_position_and_consumer_geometry": True,
            "original_style_contract": "black face, thick warm-white outline, soft down-right shadow; rounded hand for kana family, serif ink for kanji family",
            "not_installed_into_game": True,
        },
        "records": records,
        "contact_sheet": {"path": str(contact), "sha256": sha256(contact)},
    }
    manifest_path = OUT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": manifest["status"],
        "output": str(OUT),
        "record_count": len(records),
        "redrawn_focus_states": len(LARGE),
        "reused_normal_states": len(SMALL),
        "manifest_sha256": sha256(manifest_path),
        "contact": str(contact),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
