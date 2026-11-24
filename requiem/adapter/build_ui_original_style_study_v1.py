#!/usr/bin/env python3
"""Build review-only original-style studies for map, sketchbook, and library UI."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


P = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
OUT = P / "staging" / "ui_original_style_study_v1"
WORK = Path(r"C:\Users\CadriacLord\Documents\Codex\2026-08-12\search-ms-displayname-20pc-20-20\work")

MAP_SOURCE = P / "staging" / "ui_other_banks_audit_v1" / "exported_png" / "grpo_map"
MAP_CLEAN = P / "staging" / "grpo_map_korean_ui_v4_a" / "clean_png"
MAP_CURRENT = P / "staging" / "grpo_map_korean_ui_v4_a" / "wcg_reopen_png"
MAP_AUDIT = P / "audit" / "grpo_map_korean_ui_v4_a.json"

SK_SOURCE = P / "staging" / "ui_other_banks_audit_v1" / "exported_png" / "grpo_skc"
SK_CURRENT = P / "staging" / "grpo_skc_korean_ui_v3_a" / "wcg_reopen_png"
SK_NOTE_CLEAN = P / "staging" / "grpo_skc_korean_ui_v3_a" / "clean_png" / "notebook-authored-clean.png"
SK_STRINGS = WORK / "grpo_skc_korean_strings.json"

LIB_SOURCE = P / "staging" / "ui_other_banks_audit_v1" / "exported_png" / "grpo_lib"
LIB_CURRENT = P / "staging" / "grpo_lib_korean_ui_v3_a" / "wcg_reopen_png"
LIB_PAGE_CLEAN = P / "staging" / "grpo_lib_korean_ui_v3_a" / "clean_png" / "storybook-authored-clean.png"
LIB_TEXT = WORK / "grpo_lib_korean_pages_v3.json"

SERIF = Path(r"C:\Windows\Fonts\NotoSerifKR-VF.ttf")
GAEGU = P / "tools" / "fonts" / "Gaegu-Bold.ttf"
POOR = P / "tools" / "fonts" / "PoorStory-Regular.ttf"

MAP_IDS = ["0001", "0002", "0019", "0020", "2010", "2041", "2181"]
SKETCH_IDS = ["0001", "0101", "0202", "0301", "0401", "0501", "0801"]
LIBRARY_IDS = ["0011", "0111", "0015", "0115", "0201", "0223"]

SPINE = {
    11: "이상한 나라의 앨리스",
    12: "헨젤과 그레텔",
    13: "백조의 호수",
    14: "백조의 호수",
    15: "라푼젤",
    16: "눈의 여왕",
    17: "피터 팬",
    18: "오즈의 마법사",
}
ROIS = {
    11: (43, 90, 110, 470), 12: (38, 45, 115, 470),
    13: (40, 78, 112, 430), 14: (40, 78, 112, 430),
    15: (45, 70, 124, 335), 16: (45, 52, 122, 410),
    17: (42, 125, 110, 425), 18: (44, 52, 116, 510),
}
SPINE_FILL = {
    11: (62, 29, 29), 12: (65, 31, 31), 13: (242, 181, 92),
    14: (225, 238, 255), 15: (225, 227, 193), 16: (28, 46, 64),
    17: (245, 192, 5), 18: (48, 36, 41),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def reset_output() -> None:
    resolved = OUT.resolve()
    staging = (P / "staging").resolve()
    if staging not in resolved.parents:
        raise RuntimeError(f"unsafe output path: {resolved}")
    if OUT.exists():
        shutil.rmtree(OUT)
    for family in ("map", "sketch", "library"):
        for kind in ("source", "current", "clean", "candidate", "owned_mask"):
            (OUT / family / kind).mkdir(parents=True, exist_ok=True)
    (OUT / "evidence").mkdir(parents=True, exist_ok=True)


def rgba(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)


def save_rgba(array: np.ndarray, path: Path) -> None:
    Image.fromarray(array.astype(np.uint8), "RGBA").save(path)


def variable_font(path: Path, size: int, variation: str | None = None) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(path), size)
    if variation:
        try:
            font.set_variation_by_name(variation)
        except OSError:
            pass
    return font


def fit_font(path: Path, text: str, max_size: int, min_size: int, max_width: int,
             stroke: int = 0, variation: str | None = None) -> ImageFont.FreeTypeFont:
    for size in range(max_size, min_size - 1, -1):
        font = variable_font(path, size, variation)
        bbox = font.getbbox(text, stroke_width=stroke)
        if bbox[2] - bbox[0] <= max_width:
            return font
    raise RuntimeError(f"text does not fit: {text}")


def composite_text(base: np.ndarray, text: str, font: ImageFont.FreeTypeFont,
                   xy: tuple[float, float], fill: tuple[int, int, int, int],
                   anchor: str = "mm", stroke: int = 0,
                   stroke_fill: tuple[int, int, int, int] | None = None,
                   distress: bool = False) -> tuple[np.ndarray, np.ndarray, list[int]]:
    layer = Image.new("RGBA", (base.shape[1], base.shape[0]), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.text(xy, text, font=font, fill=fill, anchor=anchor,
              stroke_width=stroke, stroke_fill=stroke_fill)
    if distress:
        arr = np.asarray(layer).copy()
        alpha = arr[:, :, 3]
        yy, xx = np.indices(alpha.shape)
        holes = (((xx * 17 + yy * 29 + (xx * yy) % 31) % 97) < 4) & (alpha > 180)
        flecks = (((xx * 7 + yy * 11) % 71) < 2) & (alpha > 210)
        arr[holes, 3] = 55
        arr[flecks, :3] = np.maximum(arr[flecks, :3] * 0.65, 0).astype(np.uint8)
        layer = Image.fromarray(arr, "RGBA")
    mask = np.asarray(layer.getchannel("A"), dtype=np.uint8) > 0
    canvas = Image.fromarray(base, "RGBA")
    canvas.alpha_composite(layer)
    out = np.asarray(canvas, dtype=np.uint8)
    ys, xs = np.where(mask)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    return out, mask, bbox


def prepare_record(family: str, stem: str, source: np.ndarray, current: np.ndarray,
                   clean: np.ndarray, candidate: np.ndarray, owned: np.ndarray,
                   meta: dict[str, Any]) -> dict[str, Any]:
    if not (source.shape == current.shape == clean.shape == candidate.shape):
        raise RuntimeError(f"dimension drift: {family}/{stem}")
    if not np.array_equal(source[~owned], clean[~owned]):
        raise RuntimeError(f"clean plate changed protected pixels: {family}/{stem}")
    target_delta = np.any(candidate != clean, axis=2)
    final_owner = owned | target_delta
    if not np.array_equal(source[~final_owner], candidate[~final_owner]):
        raise RuntimeError(f"candidate changed protected pixels: {family}/{stem}")
    root = OUT / family
    paths = {
        "source": root / "source" / f"{stem}.png",
        "current": root / "current" / f"{stem}.png",
        "clean": root / "clean" / f"{stem}.png",
        "candidate": root / "candidate" / f"{stem}.png",
        "owned_mask": root / "owned_mask" / f"{stem}.png",
    }
    save_rgba(source, paths["source"])
    save_rgba(current, paths["current"])
    save_rgba(clean, paths["clean"])
    save_rgba(candidate, paths["candidate"])
    Image.fromarray((final_owner.astype(np.uint8) * 255), "L").save(paths["owned_mask"])
    return {
        "family": family,
        "stem": stem,
        "source": str(paths["source"]),
        "current": str(paths["current"]),
        "clean": str(paths["clean"]),
        "candidate": str(paths["candidate"]),
        "owned_mask": str(paths["owned_mask"]),
        "dimensions": [int(source.shape[1]), int(source.shape[0])],
        "old_ui_removed_completely_before_typesetting": True,
        "outside_owned_mask_exact": True,
        "source_sha256": sha(paths["source"]),
        "clean_sha256": sha(paths["clean"]),
        "candidate_sha256": sha(paths["candidate"]),
        **meta,
    }


def build_map(records: list[dict[str, Any]]) -> None:
    audit = load(MAP_AUDIT)
    by_stem = {Path(row["entry"]).stem: row for row in audit["records"]}
    for stem in MAP_IDS:
        row = by_stem[stem]
        source = rgba(MAP_SOURCE / f"{stem}.png")
        current = rgba(MAP_CURRENT / f"{stem}.png")
        clean = rgba(MAP_CLEAN / f"{stem}.png")
        owned = np.any(source != clean, axis=2)
        target = row["target_ko"]
        kind = row["kind"]
        if kind == "date":
            font = fit_font(SERIF, target, 51, 31, 205, 1, "Black")
            candidate, target_mask, bbox = composite_text(
                clean, target, font, (192, 38), (174, 35, 3, 255),
                stroke=1, stroke_fill=(116, 23, 0, 255), distress=True,
            )
            style = "rough red storybook print with dark-red keyline"
        else:
            font = fit_font(SERIF, target, 18, 10, 184, 1, "SemiBold")
            candidate, target_mask, bbox = composite_text(
                clean, target, font, (110, 214), (34, 29, 27, 255),
                stroke=1, stroke_fill=(247, 244, 236, 235), distress=True,
            )
            style = "small dark ink serif on the original theatre-card strip"
        records.append(prepare_record(
            "map", stem, source, current, clean, candidate, owned,
            {"target": target, "kind": kind, "font": str(font.path),
             "font_size": font.size, "target_bbox": bbox, "style": style,
             "clean_plate_source": row["clean_png"],
             "prior_clean_validation": "coherent_source_face_residue_pixels=0"},
        ))


def sketch_tab_clean(source: np.ndarray, active: bool) -> tuple[np.ndarray, np.ndarray]:
    gray = source[:, :, :3].mean(2)
    roi = np.zeros(gray.shape, bool)
    roi[34:82, 30:180] = True
    threshold = 160 if active else 210
    face = roi & (source[:, :, 3] > 200) & (gray < threshold)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(face.astype(np.uint8), 8)
    glyph = np.zeros(face.shape, bool)
    for index in range(1, count):
        x, y, width, height, area = map(int, stats[index])
        if area >= 2 and height >= 2:
            glyph |= labels == index
    avoid = cv2.dilate(glyph.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    base = source.copy()
    erase = np.zeros(glyph.shape, bool)
    claimed = np.zeros(glyph.shape, bool)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(glyph.astype(np.uint8), 8)
    offsets: list[tuple[int, int]] = []
    for distance in range(8, 121, 4):
        offsets.extend([(-distance, 0), (distance, 0), (0, -distance), (0, distance)])
    for index in range(1, count):
        segment = labels == index
        owned = cv2.dilate(segment.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~claimed
        ys, xs = np.where(owned)
        ring = cv2.dilate(owned.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~owned & ~avoid
        reference = np.median(source[ring].astype(float), axis=0)
        best = None
        for dx, dy in offsets:
            yy, xx = ys + dy, xs + dx
            if yy.min() < 12 or yy.max() >= 102 or xx.min() < 12 or xx.max() >= 188:
                continue
            if avoid[yy, xx].any() or not np.array_equal(source[yy, xx, 3], source[ys, xs, 3]):
                continue
            donor = source[yy, xx]
            score = float(np.abs(donor.astype(float) - reference).mean()) + .002 * (abs(dx) + abs(dy))
            candidate = (score, dx, dy, donor)
            if best is None or candidate[:3] < best[:3]:
                best = candidate
        if best is None:
            raise RuntimeError("no coherent tab donor")
        base[ys, xs] = best[3]
        erase |= owned
        claimed |= owned
    if (glyph & ~erase).any():
        raise RuntimeError("tab glyph closure failed")
    return base, erase


def band_clean(source: np.ndarray, y0: int) -> tuple[np.ndarray, np.ndarray]:
    band = np.zeros(source.shape[:2], bool)
    band[y0:] = True
    pixels = source[y0:].reshape(-1, 4)
    values, counts = np.unique(pixels, axis=0, return_counts=True)
    background = values[int(np.argmax(counts))]
    erase = band & np.any(source != background, axis=2)
    base = source.copy()
    base[erase] = background
    return base, erase


def build_sketch(records: list[dict[str, Any]]) -> None:
    strings = load(SK_STRINGS)
    tab_targets = strings["tabs"]
    memory = strings["memory"]
    route = strings["route"]
    for stem in SKETCH_IDS:
        source = rgba(SK_SOURCE / f"{stem}.png")
        current = rgba(SK_CURRENT / f"{stem}.png")
        number = int(stem)
        if stem in ("0001", "0101"):
            clean, owned = sketch_tab_clean(source, number < 100)
            target = tab_targets[f"{stem}.wcg"]
            font = fit_font(POOR, target, 28, 18, 148)
            fill = (32, 31, 28, 255) if number < 100 else (178, 176, 168, 255)
            candidate, _, bbox = composite_text(clean, target, font, (105, 57), fill, distress=True)
            kind = "tab"
            style = "casual hand-lettered sketchbook tab"
        elif stem == "0202":
            clean = rgba(SK_NOTE_CLEAN)
            owned = np.any(source != clean, axis=2)
            target = strings["notes"]["0202.wcg"]
            font = fit_font(POOR, target, 25, 18, 720)
            candidate, _, bbox = composite_text(clean, target, font, (640, 352), (38, 35, 31, 255))
            kind = "notebook"
            style = "small graphite-like handwritten note"
        elif stem in ("0301", "0401"):
            clean, owned = band_clean(source, 126)
            target = memory[0]
            font = fit_font(SERIF, target, 20, 12, 142, variation="Black")
            fill = (16, 15, 14, 255) if stem == "0301" else (227, 52, 52, 255)
            candidate, _, bbox = composite_text(clean, target, font, (75, 137), fill, distress=True)
            kind = "memory_label"
            style = "compact storybook serif, black/red paired state"
        else:
            is_route = number >= 800
            clean, owned = band_clean(source, 230 if is_route else 158)
            item = route[0] if is_route else memory[0]
            target = (f"루트 클리어 「{item}」 획득" if is_route else f"기억의 조각 「{item}」 획득")
            font = fit_font(SERIF, target, 31, 19, 620, variation="SemiBold")
            candidate, _, bbox = composite_text(
                clean, target, font, (330, 267 if is_route else 190),
                (30, 27, 24, 255), distress=True,
            )
            kind = "route_acquire" if is_route else "memory_acquire"
            style = "thin dark book-serif caption without generic heavy outline"
        records.append(prepare_record(
            "sketch", stem, source, current, clean, candidate, owned,
            {"target": target, "kind": kind, "font": str(font.path),
             "font_size": font.size, "target_bbox": bbox, "style": style},
        ))


def spine_face(number: int, source: np.ndarray) -> np.ndarray:
    x0, y0, x1, y1 = ROIS[number]
    rgb = source[:, :, :3]
    r, g, b = [rgb[:, :, channel] for channel in range(3)]
    roi = np.zeros(source.shape[:2], bool)
    roi[y0:y1, x0:x1] = True
    opaque = source[:, :, 3] > 35
    if number in (11, 12): mask = (r < 125) & (g < 85) & (b < 85)
    elif number == 13: mask = (r > 195) & (g > 120) & (b < 125)
    elif number == 14: mask = (r > 82) & (g > 115) & (b > 165)
    elif number == 15: mask = (r > 170) & (g > 170) & (b > 115)
    elif number == 16: mask = (r < 58) & (g < 95) & (b < 105)
    elif number == 17: mask = (r > 190) & (g > 125) & (b < 85)
    else: mask = (r < 82) & (g < 68) & (b < 70)
    mask &= roi & opaque
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    face = np.zeros(mask.shape, bool)
    for index in range(1, count):
        _, _, width, height, area = map(int, stats[index])
        if area >= 2 and width <= 46 and height <= 48:
            face |= labels == index
    return face


def spine_clean(number: int, source: np.ndarray, face: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x0, y0, x1, y1 = ROIS[number]
    roi = np.zeros(face.shape, bool)
    roi[y0:y1, x0:x1] = True
    erase = roi & (source[:, :, 3] > 20)
    base = source.copy()
    dark_text = number in (11, 12, 16, 18)
    values = source[y0:y1, x0:x1, :3][source[y0:y1, x0:x1, 3] > 20].astype(np.float32)
    if number == 17:
        red = (values[:, 0] > 1.25 * values[:, 1]) & (values[:, 0] > 1.25 * values[:, 2])
        pool = values[red]
    else:
        luminance = values.mean(1)
        cutoff = np.percentile(luminance, 40 if dark_text else 70)
        pool = values[luminance >= cutoff] if dark_text else values[luminance <= cutoff]
    color = np.median(pool, axis=0)
    height = max(1, y1 - y0 - 1)
    for y in range(y0, y1):
        xs = np.where(erase[y])[0]
        factor = .96 + .08 * ((y - y0) / height)
        base[y, xs, :3] = np.clip(np.rint(color * factor), 0, 255).astype(np.uint8)
    if (face & ~erase).any():
        raise RuntimeError("spine face is not inside erase region")
    return base, erase


def draw_vertical_spine(clean: np.ndarray, raw: int, target: str) -> tuple[np.ndarray, np.ndarray, list[int], ImageFont.FreeTypeFont]:
    number = raw % 100
    x0, y0, x1, y1 = ROIS[number]
    chars = [character for character in target if character != " "]
    max_height = y1 - y0 - 12
    for size in range(31, 14, -1):
        font = variable_font(SERIF, size, "Black")
        step = round(size * 1.06)
        height = step * len(chars)
        if height <= max_height:
            break
    y = (y0 + y1 - height) // 2
    mask = Image.new("L", (clean.shape[1], clean.shape[0]), 0)
    draw = ImageDraw.Draw(mask)
    center = (x0 + x1) // 2
    for index, character in enumerate(chars):
        draw.text((center, y + index * step), character, font=font, fill=255, anchor="ma")
    alpha = np.asarray(mask, dtype=np.uint8)
    coverage = alpha.astype(np.float32) / 255
    out = clean.copy()
    color = np.asarray(SPINE_FILL[number], dtype=np.float32)
    if raw >= 100:
        background = np.median(clean[y0:y1, x0:x1, :3][clean[y0:y1, x0:x1, 3] > 20], axis=0)
        color = color * .42 + background * .58
    out[:, :, :3] = np.rint(out[:, :, :3] * (1 - coverage[:, :, None]) + color * coverage[:, :, None]).astype(np.uint8)
    ys, xs = np.where(alpha > 0)
    return out, alpha > 0, [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1], font


def paragraphs(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def wrap(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = word if not current else current + " " + word
        if font.getlength(candidate) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines


def draw_storybook(clean: np.ndarray, text: dict[str, str]) -> tuple[np.ndarray, np.ndarray, list[int], int]:
    out = clean.copy()
    total = np.zeros(clean.shape[:2], bool)
    bboxes: list[list[int]] = []
    sizes: list[int] = []
    for side, bounds in {"L": (30, 24, 518, 575), "R": (590, 24, 1078, 575)}.items():
        x0, y0, x1, y1 = bounds
        source_text = text[side]
        for size in range(18, 10, -1):
            font = variable_font(SERIF, size, "Medium")
            ascent, descent = font.getmetrics()
            line_height = ascent + descent + max(1, round(size * .12))
            groups = [wrap(part, font, x1 - x0) for part in paragraphs(source_text)]
            paragraph_gap = max(2, round(size * .38))
            height = sum(len(group) * line_height for group in groups) + max(0, len(groups) - 1) * paragraph_gap
            if height <= y1 - y0:
                break
        layer = Image.new("L", (clean.shape[1], clean.shape[0]), 0)
        draw = ImageDraw.Draw(layer)
        y = y0
        for group_index, group in enumerate(groups):
            for line in group:
                draw.text((x0, y), line, font=font, fill=255, anchor="la")
                y += line_height
            if group_index + 1 < len(groups):
                y += paragraph_gap
        alpha = np.asarray(layer, dtype=np.uint8)
        coverage = alpha.astype(np.float32) / 255
        color = np.array([27, 23, 19], dtype=np.float32)
        out[:, :, :3] = np.rint(out[:, :, :3] * (1 - coverage[:, :, None]) + color * coverage[:, :, None]).astype(np.uint8)
        mask = alpha > 0
        total |= mask
        ys, xs = np.where(mask)
        bboxes.append([int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1])
        sizes.append(size)
    bbox = [min(box[0] for box in bboxes), min(box[1] for box in bboxes),
            max(box[2] for box in bboxes), max(box[3] for box in bboxes)]
    return out, total, bbox, min(sizes)


def vertical_columns(text: str, size: tuple[int, int], font_size: int = 11) -> Image.Image:
    font = variable_font(SERIF, font_size, "Medium")
    layer = Image.new("RGBA", size, (213, 211, 204, 255))
    draw = ImageDraw.Draw(layer)
    draw.rectangle((1, 1, size[0] - 2, size[1] - 2), outline=(72, 70, 66, 255), width=2)
    chars = [character for character in text if not character.isspace()]
    line_capacity = max(8, (size[1] - 30) // (font_size + 2))
    columns = [chars[index:index + line_capacity] for index in range(0, len(chars), line_capacity)]
    x = size[0] - 18
    for column in columns[: max(1, (size[0] - 20) // (font_size + 5))]:
        y = 14
        for character in column:
            draw.text((x, y), character, font=font, fill=(43, 40, 37, 255), anchor="ma")
            y += font_size + 2
        x -= font_size + 6
    return layer


def build_newspaper(clean: np.ndarray, text: dict[str, str]) -> tuple[np.ndarray, np.ndarray, list[int]]:
    base = Image.fromarray(clean, "RGBA")
    back = vertical_columns(text["R"], (285, 375), 10).rotate(3.0, Image.Resampling.BICUBIC, expand=True)
    front = vertical_columns(text["L"], (305, 405), 10)
    fd = ImageDraw.Draw(front)
    title = "『낙원』 의사 3명 중태"
    title_font = variable_font(SERIF, 16, "Black")
    fd.rectangle((250, 4, 300, 401), fill=(221, 219, 212, 255))
    y = 14
    for character in title:
        if character.isspace():
            y += 6
            continue
        fd.text((276, y), character, font=title_font, fill=(22, 20, 18, 255), anchor="ma")
        y += 18
    front = front.rotate(-3.2, Image.Resampling.BICUBIC, expand=True)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.alpha_composite(back, (294, 92))
    layer.alpha_composite(front, (465, 96))
    base.alpha_composite(layer)
    candidate = np.asarray(base, dtype=np.uint8)
    mask = np.asarray(layer.getchannel("A"), dtype=np.uint8) > 0
    ys, xs = np.where(mask)
    return candidate, mask, [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def build_library(records: list[dict[str, Any]]) -> None:
    text_doc = load(LIB_TEXT)["pages"]
    for stem in LIBRARY_IDS:
        source = rgba(LIB_SOURCE / f"{stem}.png")
        current = rgba(LIB_CURRENT / f"{stem}.png")
        raw = int(stem)
        if raw < 200:
            number = raw % 100
            face_source = source if raw < 100 else rgba(LIB_SOURCE / f"{number:04d}.png")
            face = spine_face(number, face_source)
            clean, owned = spine_clean(number, source, face)
            target = SPINE[number]
            candidate, _, bbox, font = draw_vertical_spine(clean, raw, target)
            kind = "book_spine_title"
            style = "vertical Korean book-serif matching the authored spine color and fade state"
            font_size = font.size
        else:
            clean = rgba(LIB_PAGE_CLEAN)
            owned = np.any(source != clean, axis=2)
            target = "동화책 본문" if stem != "0223" else "신문 기사"
            if stem == "0223":
                candidate, _, bbox = build_newspaper(clean, text_doc[stem])
                font_size = 10
                kind = "newspaper_story_page"
                style = "two overlapping newspaper sheets with vertical Korean columns"
            else:
                candidate, _, bbox, font_size = draw_storybook(clean, text_doc[stem])
                kind = "storybook_page"
                style = "dark compact Korean book-serif with original margins and two-column rhythm"
        records.append(prepare_record(
            "library", stem, source, current, clean, candidate, owned,
            {"target": target, "kind": kind, "font": str(SERIF),
             "font_size": font_size, "target_bbox": bbox, "style": style},
        ))


def make_contacts(records: list[dict[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    label_font = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 17)
    for family in ("map", "sketch", "library"):
        family_records = [record for record in records if record["family"] == family]
        rows: list[Image.Image] = []
        for record in family_records:
            images = [Image.open(record[key]).convert("RGBA") for key in ("source", "current", "candidate")]
            scale = min(620 / images[0].width, 360 / images[0].height, 1.0)
            size = (max(1, round(images[0].width * scale)), max(1, round(images[0].height * scale)))
            thumbs = [image.resize(size, Image.Resampling.LANCZOS) for image in images]
            row = Image.new("RGB", (size[0] * 3 + 40, size[1] + 34), (38, 33, 45))
            draw = ImageDraw.Draw(row)
            for index, (tag, image) in enumerate(zip(("원본", "현재", "재시안"), thumbs)):
                x = 5 + index * (size[0] + 15)
                draw.text((x, 4), f"{record['stem']} {tag}", font=label_font, fill="white")
                backing = Image.new("RGBA", image.size, (245, 240, 232, 255))
                backing.alpha_composite(image)
                row.paste(backing.convert("RGB"), (x, 30))
            rows.append(row)
        width = max(row.width for row in rows)
        height = sum(row.height for row in rows)
        contact = Image.new("RGB", (width, height), (38, 33, 45))
        y = 0
        for row in rows:
            contact.paste(row, (0, y))
            y += row.height
        path = OUT / "evidence" / f"{family}_source_current_candidate.jpg"
        contact.save(path, quality=78, optimize=True, progressive=True)
        result[family] = str(path)
    return result


def main() -> None:
    for path in (MAP_AUDIT, SK_STRINGS, LIB_TEXT, SERIF, GAEGU, POOR, SK_NOTE_CLEAN, LIB_PAGE_CLEAN):
        if not path.exists():
            raise FileNotFoundError(path)
    reset_output()
    records: list[dict[str, Any]] = []
    build_map(records)
    build_sketch(records)
    build_library(records)
    contacts = make_contacts(records)
    manifest = {
        "schema": "fairytale-requiem-original-style-ui-study-v1",
        "status": "USER_REVIEW_REQUIRED_NOT_INSTALLED",
        "scope": {
            "map_representatives": len(MAP_IDS),
            "sketch_representatives": len(SKETCH_IDS),
            "library_representatives": len(LIBRARY_IDS),
            "full_expansion_after_style_approval": {"map": 88, "sketch": 69, "library": 49, "total": 206},
        },
        "contract": {
            "old_ui_removed_completely_before_typesetting": True,
            "clean_plate_inspected_as_independent_artifact": True,
            "original_canvas_position_and_protected_artwork_preserved": True,
            "no_generic_malgun_heavy_outline_style": True,
            "review_only": True,
            "installed": False,
        },
        "records": records,
        "contacts": contacts,
    }
    manifest_path = OUT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": manifest["status"],
        "output": str(OUT),
        "item_count": len(records),
        "family_counts": {family: sum(record["family"] == family for record in records)
                          for family in ("map", "sketch", "library")},
        "manifest_sha256": sha(manifest_path),
        "contacts": contacts,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
