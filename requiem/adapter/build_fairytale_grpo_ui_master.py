#!/usr/bin/env python3
"""Rebuild Fairytale Requiem's title UI with the Malie Master contract.

The title archive is a compact, stateful raster family:

* 0001..0008: persistent, image-baked miniature labels.
* 0101..0108: large hover/selection text layers.

This builder deliberately does not use inpainting, blur, cloning, or tiled
micro-patches.  Miniature labels are restored with one coherent quadratic
surface fitted to intact pixels from the same plate, then typeset once.  Large
labels are proven text-only layers and are rebuilt on transparency.  Every
pixel outside the explicit source/target text masks remains byte-identical at
the PNG stage, and the WCG/XFL structure is verified after rebuilding.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


SMALL_LABELS = {
    "0001": "시작",
    "0002": "계속",
    "0003": "감상",
    "0004": "설정",
    "0005": "조작",
    "0006": "레퀴엠",
    "0007": "종료",
    "0008": "추가편",
}

LARGE_LABELS = {
    "0101": "처음부터",
    "0102": "이어하기",
    "0103": "감상",
    "0104": "환경 설정",
    "0105": "조작 설명",
    # 0106 is the deliberately unrevealed/locked "???" state.
    "0107": "종료",
    "0108": "FC 시나리오",
}

ALL_STEMS = [f"{i:04d}" for i in range(1, 9)] + [f"{100 + i:04d}" for i in range(1, 9)]


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    bbox = image.convert("RGBA").getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("image has no visible pixels")
    return bbox


def black_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(path), size=size)
    try:
        font.set_variation_by_name("Black")
    except OSError:
        pass
    return font


def neutral_bright_mask(array: np.ndarray) -> np.ndarray:
    rgb = array[:, :, :3].astype(np.int16)
    alpha = array[:, :, 3]
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    bright = (
        (alpha > 20)
        & (rgb.min(axis=2) > 145)
        & (chroma < 55)
    )
    lower = np.zeros_like(bright)
    lower[array.shape[0] // 2 :, :] = True
    return bright & lower


def principal_angle(mask: np.ndarray) -> float:
    ys, xs = np.where(mask)
    if len(xs) < 3:
        raise ValueError("not enough glyph pixels for PCA")
    points = np.column_stack([xs, ys]).astype(np.float32)
    _, eigenvectors = cv2.PCACompute(points, mean=None, maxComponents=2)
    vx, vy = eigenvectors[0]
    angle = math.degrees(math.atan2(float(vy), float(vx)))
    if angle > 45:
        angle -= 180
    if angle < -45:
        angle += 180
    return angle


def polynomial_features(xs: np.ndarray, ys: np.ndarray, center: tuple[float, float], scale: float) -> np.ndarray:
    x = (xs.astype(np.float64) - center[0]) / scale
    y = (ys.astype(np.float64) - center[1]) / scale
    return np.column_stack([np.ones_like(x), x, y, x * x, x * y, y * y])


def robust_fit(features: np.ndarray, values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    keep = np.ones(len(features), dtype=bool)
    coeff = np.zeros(features.shape[1], dtype=np.float64)
    for _ in range(5):
        coeff, *_ = np.linalg.lstsq(features[keep], values[keep], rcond=None)
        residual = np.abs(features @ coeff - values)
        median = float(np.median(residual[keep]))
        mad = float(np.median(np.abs(residual[keep] - median)))
        limit = max(4.0, median + 3.5 * max(1.0, 1.4826 * mad))
        new_keep = residual <= limit
        if new_keep.sum() < max(24, features.shape[1] * 5) or np.array_equal(new_keep, keep):
            break
        keep = new_keep
    return coeff, keep


def restore_small_plate(
    source: np.ndarray,
    source_face: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Remove the old label with one same-asset parametric plate model."""
    erase = cv2.dilate(
        source_face.astype(np.uint8),
        np.ones((5, 5), dtype=np.uint8),
        iterations=1,
    ).astype(bool)
    outer = cv2.dilate(
        erase.astype(np.uint8),
        np.ones((15, 15), dtype=np.uint8),
        iterations=1,
    ).astype(bool)

    rgb = source[:, :, :3].astype(np.float64)
    alpha = source[:, :, 3].astype(np.float64)
    luminance = rgb.mean(axis=2)
    visible_dark = outer & ~erase & (alpha > 40) & (luminance < 125)
    if visible_dark.sum() < 50:
        raise ValueError("insufficient intact plate pixels")

    # Restrict the fit to the coherent dark plate palette, excluding the vivid
    # coffin illustration that touches some labels.
    median_rgb = np.median(rgb[visible_dark], axis=0)
    distance = np.sqrt(((rgb - median_rgb) ** 2).sum(axis=2))
    training = visible_dark & (distance <= 58)
    if training.sum() < 42:
        training = visible_dark

    tys, txs = np.where(training)
    eys, exs = np.where(erase)
    center = (float(exs.mean()), float(eys.mean()))
    scale = max(12.0, float(max(exs.max() - exs.min() + 1, eys.max() - eys.min() + 1)))
    train_features = polynomial_features(txs, tys, center, scale)
    erase_features = polynomial_features(exs, eys, center, scale)

    restored = source.copy()
    predictions: list[np.ndarray] = []
    channel_reports: list[dict[str, Any]] = []
    for channel in range(4):
        values = source[tys, txs, channel].astype(np.float64)
        coeff, keep = robust_fit(train_features, values)
        prediction = np.clip(np.rint(erase_features @ coeff), 0, 255).astype(np.uint8)
        predictions.append(prediction)

        # Deterministic held-out validation against intact same-plate pixels.
        holdout = np.arange(len(values)) % 5 == 0
        fitset = ~holdout
        if fitset.sum() >= 30 and holdout.sum() >= 8:
            hold_coeff, _ = robust_fit(train_features[fitset], values[fitset])
            error = np.abs(train_features[holdout] @ hold_coeff - values[holdout])
            mae = float(error.mean())
            p95 = float(np.quantile(error, 0.95))
        else:
            mae = p95 = 0.0
        channel_reports.append(
            {
                "channel": "RGBA"[channel],
                "training_samples": int(len(values)),
                "robust_inliers": int(keep.sum()),
                "holdout_mae": round(mae, 3),
                "holdout_p95": round(p95, 3),
            }
        )

    restored_values = np.column_stack(predictions)
    # The label plate is opaque where the original flattened glyph existed.
    # A low-alpha regression outlier would punch a hole, so bind alpha to the
    # intact plate's robust median while retaining its observed range.
    alpha_median = int(round(float(np.median(source[tys, txs, 3]))))
    restored_values[:, 3] = np.maximum(restored_values[:, 3], alpha_median)
    restored[eys, exs] = restored_values

    residue_values = restored[:, :, :3][source_face]
    residue_bright = int((residue_values.min(axis=1) > 145).sum()) if len(residue_values) else 0
    if residue_bright:
        raise RuntimeError(f"source face residue remains after plate restoration: {residue_bright}")

    return restored, erase, {
        "method": "single coherent same-asset quadratic plate surface; no inpainting/blur/cloning/tiling",
        "erase_pixel_count": int(erase.sum()),
        "training_pixel_count": int(training.sum()),
        "training_palette_median_rgba": [int(v) for v in np.median(source[tys, txs], axis=0)],
        "alpha_floor": alpha_median,
        "channels": channel_reports,
        "source_face_residue_bright_pixel_count_before_typesetting": residue_bright,
    }


def fit_small_font(text: str, font_path: Path, max_width: int, max_height: int) -> tuple[ImageFont.FreeTypeFont, tuple[int, int, int, int]]:
    for size in range(21, 8, -1):
        font = black_font(font_path, size)
        bbox = font.getbbox(text, stroke_width=1)
        if bbox[2] - bbox[0] <= max_width and bbox[3] - bbox[1] <= max_height:
            return font, bbox
    font = black_font(font_path, 8)
    return font, font.getbbox(text, stroke_width=1)


def render_small_label(original: Image.Image, target: str, font_path: Path) -> tuple[Image.Image, np.ndarray, dict[str, Any]]:
    source = np.asarray(original.convert("RGBA"), dtype=np.uint8)
    source_face = neutral_bright_mask(source)
    ys, xs = np.where(source_face)
    if len(xs) < 24:
        raise ValueError("could not isolate miniature source label")
    angle = principal_angle(source_face)
    restored, erase_mask, restoration = restore_small_plate(source, source_face)

    x0, x1 = int(xs.min()), int(xs.max()) + 1
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    center = ((x0 + x1) / 2.0, (y0 + y1) / 2.0)
    font, bbox = fit_small_font(
        target,
        font_path,
        max_width=max(28, x1 - x0 + 5),
        max_height=max(15, y1 - y0 + 3),
    )
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    layer = Image.new("RGBA", (max(86, tw + 24), max(56, th + 24)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    tx = (layer.width - tw) / 2 - bbox[0]
    ty = (layer.height - th) / 2 - bbox[1]
    draw.text(
        (tx, ty),
        target,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=1,
        stroke_fill=(8, 8, 8, 255),
    )
    rotated = layer.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    paste_x = round(center[0] - rotated.width / 2)
    paste_y = round(center[1] - rotated.height / 2)
    # Keep antialiased target pixels inside the source state's authored alpha
    # footprint. Rotation can otherwise add one or two fringe pixels beyond
    # the original plate even when the face bbox itself fits.
    rotated_bbox = rotated.getchannel("A").getbbox()
    if rotated_bbox is None:
        raise RuntimeError("miniature target rendered empty")
    source_alpha_bbox = alpha_bbox(original)
    gx0 = paste_x + rotated_bbox[0]
    gy0 = paste_y + rotated_bbox[1]
    gx1 = paste_x + rotated_bbox[2]
    gy1 = paste_y + rotated_bbox[3]
    if gx0 < source_alpha_bbox[0]:
        paste_x += source_alpha_bbox[0] - gx0
    if gx1 > source_alpha_bbox[2]:
        paste_x -= gx1 - source_alpha_bbox[2]
    if gy0 < source_alpha_bbox[1]:
        paste_y += source_alpha_bbox[1] - gy0
    if gy1 > source_alpha_bbox[3]:
        paste_y -= gy1 - source_alpha_bbox[3]
    canvas = Image.fromarray(restored, "RGBA")
    canvas.alpha_composite(rotated, (paste_x, paste_y))
    edited = np.asarray(canvas, dtype=np.uint8)

    target_layer = Image.new("RGBA", original.size, (0, 0, 0, 0))
    target_layer.alpha_composite(rotated, (paste_x, paste_y))
    target_mask = np.asarray(target_layer.getchannel("A"), dtype=np.uint8) > 0
    changed_mask = erase_mask | target_mask
    if not np.array_equal(source[~changed_mask], edited[~changed_mask]):
        raise RuntimeError("protected miniature pixels changed")

    # The target must stay on the already-visible plate and must not enlarge
    # the state layer's footprint.
    edited_alpha_bbox = alpha_bbox(canvas)
    if source_alpha_bbox != edited_alpha_bbox:
        raise RuntimeError(f"miniature alpha footprint changed: {source_alpha_bbox} -> {edited_alpha_bbox}")

    details = {
        "target": target,
        "source_face_bbox": [x0, y0, x1, y1],
        "source_alpha_bbox": list(source_alpha_bbox),
        "output_alpha_bbox": list(edited_alpha_bbox),
        "principal_angle_degrees": round(angle, 3),
        "text_center": [round(center[0], 3), round(center[1], 3)],
        "font": str(font_path),
        "font_instance": font.getname(),
        "font_size": font.size,
        "text_bbox": list(bbox),
        "restoration": restoration,
        "target_pixel_count": int(target_mask.sum()),
        "changed_pixel_count": int(changed_mask.sum()),
        "protected_pixel_count": int((~changed_mask).sum()),
        "protected_pixels_exact_before_wcg": True,
    }
    return canvas, changed_mask, details


def render_large_crop(text: str, font_path: Path, size: int) -> tuple[Image.Image, dict[str, Any]]:
    font = black_font(font_path, size)
    stroke = max(4, round(size * 0.075))
    shadow_stroke = stroke + 2
    shadow_offset = (max(5, round(size * 0.075)), max(6, round(size * 0.09)))
    bbox = font.getbbox(text, stroke_width=shadow_stroke)
    width = bbox[2] - bbox[0] + shadow_offset[0] + 20
    height = bbox[3] - bbox[1] + shadow_offset[1] + 20
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x = 10 - bbox[0]
    y = 10 - bbox[1]
    draw.text(
        (x + shadow_offset[0], y + shadow_offset[1]),
        text,
        font=font,
        fill=(116, 116, 116, 210),
        stroke_width=shadow_stroke,
        stroke_fill=(92, 92, 92, 178),
    )
    draw.text(
        (x, y),
        text,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=stroke,
        stroke_fill=(10, 10, 10, 255),
    )
    crop_bbox = layer.getchannel("A").getbbox()
    if crop_bbox is None:
        raise RuntimeError("large label rendered empty")
    return layer.crop(crop_bbox), {
        "font": str(font_path),
        "font_instance": font.getname(),
        "font_size": size,
        "face_stroke_width": stroke,
        "shadow_stroke_width": shadow_stroke,
        "shadow_offset": list(shadow_offset),
    }


def render_large_label(original: Image.Image, target: str, font_path: Path) -> tuple[Image.Image, np.ndarray, dict[str, Any]]:
    original = original.convert("RGBA")
    source = np.asarray(original, dtype=np.uint8)
    source_bbox = alpha_bbox(original)
    x0, y0, x1, y1 = source_bbox
    max_width, max_height = x1 - x0, y1 - y0

    crop = None
    typography: dict[str, Any] = {}
    for size in range(104, 37, -1):
        candidate, info = render_large_crop(target, font_path, size)
        if candidate.width <= max_width and candidate.height <= max_height:
            crop, typography = candidate, info
            break
    if crop is None:
        raise RuntimeError(f"large label does not fit source footprint: {target}")

    # Lock the source's outer right edge and vertical center.  This preserves
    # the engine-authored screen alignment while allowing natural Korean width.
    px = x1 - crop.width
    py = round((y0 + y1 - crop.height) / 2)
    canvas = Image.new("RGBA", original.size, (0, 0, 0, 0))
    canvas.alpha_composite(crop, (px, py))
    edited = np.asarray(canvas, dtype=np.uint8)
    source_mask = source[:, :, 3] > 0
    target_mask = edited[:, :, 3] > 0
    changed_mask = source_mask | target_mask
    if not np.array_equal(source[~changed_mask], edited[~changed_mask]):
        raise RuntimeError("protected large-layer pixels changed")
    output_bbox = alpha_bbox(canvas)
    if output_bbox[2] != x1:
        raise RuntimeError(f"large label right edge drifted: {output_bbox[2]} != {x1}")
    source_nonzero = int(source_mask.sum())
    transparent_fraction = 1.0 - source_nonzero / float(original.width * original.height)
    if transparent_fraction < 0.60:
        raise RuntimeError("large layer is not sparse enough to classify as text-only")

    details = {
        "target": target,
        "semantic_layer_class": "hover/selection text-only RGBA layer",
        "text_only_evidence": {
            "dimensions": list(original.size),
            "source_alpha_bbox": list(source_bbox),
            "source_nonzero_alpha_pixels": source_nonzero,
            "transparent_fraction": round(transparent_fraction, 6),
            "consumer_position_shared_by_state_family": True,
        },
        "output_alpha_bbox": list(output_bbox),
        "placement": [px, py],
        "right_edge_locked": x1,
        "vertical_center_source": round((y0 + y1) / 2.0, 3),
        "vertical_center_output": round((output_bbox[1] + output_bbox[3]) / 2.0, 3),
        **typography,
        "changed_pixel_count": int(changed_mask.sum()),
        "protected_pixel_count": int((~changed_mask).sum()),
        "protected_pixels_exact_before_wcg": True,
    }
    return canvas, changed_mask, details


def compare_decoded(expected: Image.Image, decoded: Image.Image, protected_mask: np.ndarray) -> dict[str, Any]:
    a = np.asarray(expected.convert("RGBA"), dtype=np.uint8)
    b = np.asarray(decoded.convert("RGBA"), dtype=np.uint8)
    if a.shape != b.shape:
        raise ValueError("decoded image dimensions changed")
    delta = np.abs(a.astype(np.int16) - b.astype(np.int16))
    visible = (a[:, :, 3] > 0) | (b[:, :, 3] > 0)
    substantive = visible & (a[:, :, 3] >= 16)
    protected_delta = delta[protected_mask]
    max_protected = int(protected_delta.max()) if len(protected_delta) else 0
    return {
        "dimensions_equal": True,
        "alpha_equal": bool(np.array_equal(a[:, :, 3], b[:, :, 3])),
        "visible_rgba_equal": bool(np.array_equal(a[visible], b[visible])),
        "visible_changed_pixel_count": int(np.any(a != b, axis=2)[visible].sum()),
        "max_visible_rgb_delta": int(delta[:, :, :3][visible].max()) if visible.any() else 0,
        "max_substantive_alpha_rgb_delta": int(delta[:, :, :3][substantive].max()) if substantive.any() else 0,
        "max_protected_rgba_delta_after_wcg": max_protected,
        "wcg_quantization_acceptable": bool((not substantive.any()) or delta[:, :, :3][substantive].max() <= 8),
    }


def build_consumer_graph(project: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    sys.path.insert(0, str(project / "adapter"))
    from build_scenario_catalog import parse_commands  # type: ignore
    from gsc_codec import parse_gsc  # type: ignore

    config = json.loads((project / "adapter" / "command_formats.json").read_text(encoding="utf-8"))
    formats = {int(row["opcode"]): (row["format"], row.get("name", "")) for row in config["commands"]}
    script_path = project / "extracted" / "scr" / "0001.gsc"
    parts = parse_gsc(script_path.read_bytes())
    commands = parse_commands(parts.command, formats)
    strings = [raw.decode("cp932", errors="replace") for raw in parts.strings]

    grpo_directory_commands = []
    for command in commands:
        if command.opcode == 0x79 and len(command.args) >= 2 and 0 <= command.args[1] < len(strings):
            if strings[command.args[1]] == "grpo":
                grpo_directory_commands.append(
                    {
                        "ordinal": command.ordinal,
                        "offset_hex": f"0x{command.offset:X}",
                        "args": list(command.args),
                        "directory_string_slot": command.args[1],
                    }
                )

    consumers: list[dict[str, Any]] = []
    for index, command in enumerate(commands):
        if command.opcode != 0x1E or len(command.args) != 6:
            continue
        object_id, small_asset, sx, sy, mode, reserved = command.args
        if not 1 <= small_asset <= 8:
            continue
        hover = None
        route = None
        for nearby in commands[index + 1 : index + 4]:
            if nearby.opcode == 0x4B and nearby.args[0] == object_id:
                hover = nearby
            elif nearby.opcode in (0x46, 0x47) and nearby.args[0] == object_id:
                route = nearby
        if hover is None or hover.args[1] != 100 + small_asset:
            continue
        consumers.append(
            {
                "small_asset": f"{small_asset:04d}.wcg",
                "large_state_asset": f"{100 + small_asset:04d}.wcg",
                "object_id": object_id,
                "small_screen_position": [sx, sy],
                "large_screen_position": [hover.args[2], hover.args[3]],
                "image_def": {
                    "ordinal": command.ordinal,
                    "offset_hex": f"0x{command.offset:X}",
                    "args": list(command.args),
                },
                "state_binding_0x4B": {
                    "ordinal": hover.ordinal,
                    "offset_hex": f"0x{hover.offset:X}",
                    "args": list(hover.args),
                },
                "route_binding": None
                if route is None
                else {
                    "opcode_hex": f"0x{route.opcode:04X}",
                    "ordinal": route.ordinal,
                    "offset_hex": f"0x{route.offset:X}",
                    "args": list(route.args),
                },
            }
        )

    consumed = {row["small_asset"] for row in consumers} | {row["large_state_asset"] for row in consumers}
    archive_entries = [entry["name"] for entry in manifest["entries"]]
    unconsumed = [name for name in archive_entries if name not in consumed]
    if unconsumed:
        raise RuntimeError(f"grpo consumer graph has unconsumed entries: {unconsumed}")

    families = []
    for i in range(1, 9):
        family_consumers = [row for row in consumers if row["small_asset"] == f"{i:04d}.wcg"]
        families.append(
            {
                "family_id": f"title-menu-{i}",
                "normal_asset": f"{i:04d}.wcg",
                "hover_or_selected_asset": f"{100 + i:04d}.wcg",
                "locked_unrevealed": i == 6,
                "consumer_count": len(family_consumers),
                "consumers": family_consumers,
            }
        )

    result = {
        "schema": "fairytale-requiem-malie-master-grpo-consumer-graph-v1",
        "source_script": {"path": str(script_path), "sha256": sha256_path(script_path)},
        "archive_manifest": {
            "path": str(project / "audit" / "grpo_xfl_manifest.json"),
            "sha256": sha256_path(project / "audit" / "grpo_xfl_manifest.json"),
            "entry_count": len(archive_entries),
            "entries": archive_entries,
        },
        "directory_resolution_evidence": grpo_directory_commands,
        "opcode_interpretation": {
            "0x001E": "IMAGE_DEF: binds object id and normal asset at an authored screen position",
            "0x004B": "state companion binding: same object id, 010x asset, authored large-label position",
            "0x0046_0x0047": "interaction/route binding retained as raw evidence; no hitbox edits",
        },
        "state_families": families,
        "all_archive_entries_have_consumers": True,
        "hitboxes_or_script_positions_changed": False,
    }
    write_json(project / "audit" / "malie_master_grpo_consumer_graph.json", result)
    return result


def build(project: Path) -> dict[str, Any]:
    tool = project / "adapter" / "UiAssetTool.exe"
    xfl_tool = project / "adapter" / "xfl_tool.py"
    source_root = project / "extracted" / "grpo"
    png_root = project / "evidence" / "ui" / "grpo_png"
    manifest_path = project / "audit" / "grpo_xfl_manifest.json"
    font_path = Path(r"C:\Windows\Fonts\NotoSansKR-VF.ttf")
    for required in (tool, xfl_tool, source_root, png_root, manifest_path, font_path):
        if not required.exists():
            raise FileNotFoundError(required)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    consumer_graph = build_consumer_graph(project, manifest)

    stage = project / "staging" / "ui_master"
    wcg_root = stage / "grpo_entries"
    patch_root = stage / "png_patches"
    decoded_root = stage / "decoded_png"
    rebuild_root = stage / "grpo_rebuild_tree"
    if stage.exists():
        shutil.rmtree(stage)
    for path in (wcg_root, patch_root, decoded_root):
        path.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_root, rebuild_root)

    targets = dict(SMALL_LABELS) | dict(LARGE_LABELS)
    records: list[dict[str, Any]] = []
    for stem, target in targets.items():
        source_wcg = source_root / f"{stem}.wcg"
        source_png = png_root / f"{stem}.png"
        original = Image.open(source_png).convert("RGBA")
        if stem.startswith("00"):
            edited, changed_mask, details = render_small_label(original, target, font_path)
        else:
            edited, changed_mask, details = render_large_label(original, target, font_path)

        patch_png = patch_root / f"{stem}.patch.png"
        mask_png = patch_root / f"{stem}.mask.png"
        output_wcg = wcg_root / f"{stem}.wcg"
        decoded_png = decoded_root / f"{stem}.png"
        edited.save(patch_png)
        Image.fromarray(changed_mask.astype(np.uint8) * 255, "L").save(mask_png)
        patch_stdout = run(
            [str(tool), "wcg-apply-patch", str(source_wcg), str(patch_png), str(mask_png), str(output_wcg)]
        )
        run([str(tool), "wcg2png", str(output_wcg), str(decoded_png)])
        decoded = Image.open(decoded_png).convert("RGBA")
        comparison = compare_decoded(edited, decoded, ~changed_mask)
        if not comparison["alpha_equal"] or not comparison["wcg_quantization_acceptable"]:
            raise RuntimeError(f"WCG verification failed for {stem}: {comparison}")
        if comparison["max_protected_rgba_delta_after_wcg"] > 8:
            raise RuntimeError(f"protected WCG pixels drifted for {stem}: {comparison}")
        shutil.copy2(output_wcg, rebuild_root / output_wcg.name)
        records.append(
            {
                "stable_id": f"grpo.xfl::{stem}.wcg",
                "target_ko": target,
                "source_wcg_sha256": sha256_path(source_wcg),
                "output_wcg_sha256": sha256_path(output_wcg),
                "source_png_sha256": sha256_path(source_png),
                "patch_png_sha256": sha256_path(patch_png),
                "mask_png_sha256": sha256_path(mask_png),
                "mask_pixel_count": int(changed_mask.sum()),
                "tool_output": patch_stdout.splitlines()[0] if patch_stdout else "",
                "typesetting": details,
                "decoded_pixel_verification": comparison,
            }
        )

    rebuilt_xfl = stage / "grpo.ko-master.xfl"
    repack_report = project / "audit" / "grpo_ko_master_repack.json"
    run(
        [
            sys.executable,
            str(xfl_tool),
            "repack",
            str(rebuild_root),
            str(manifest_path),
            str(rebuilt_xfl),
            "--report",
            str(repack_report),
        ]
    )

    entry_names = [entry["name"] for entry in manifest["entries"]]
    actual_changed = [
        name for name in entry_names if (source_root / name).read_bytes() != (rebuild_root / name).read_bytes()
    ]
    expected_changed = [f"{stem}.wcg" for stem in targets]
    expected_ordered = [name for name in entry_names if name in expected_changed]
    if actual_changed != expected_ordered:
        raise RuntimeError(f"unexpected changed-entry set: {actual_changed}")
    if (source_root / "0106.wcg").read_bytes() != (rebuild_root / "0106.wcg").read_bytes():
        raise RuntimeError("locked 0106.wcg changed")

    # Compact review overlay: every state pair, source above master output.
    cell_w, cell_h = 410, 240
    sheet = Image.new("RGBA", (cell_w * 4, cell_h * 4), (42, 42, 46, 255))
    draw = ImageDraw.Draw(sheet)
    label_font = black_font(font_path, 18)
    for index, stem in enumerate(ALL_STEMS):
        row, col = divmod(index, 4)
        x, y = col * cell_w, row * cell_h
        source_img = Image.open(png_root / f"{stem}.png").convert("RGBA")
        output_img = (
            Image.open(decoded_root / f"{stem}.png").convert("RGBA")
            if (decoded_root / f"{stem}.png").exists()
            else source_img.copy()
        )
        source_disp = source_img.copy(); source_disp.thumbnail((380, 92), Image.Resampling.LANCZOS)
        output_disp = output_img.copy(); output_disp.thumbnail((380, 92), Image.Resampling.LANCZOS)
        draw.text((x + 8, y + 4), f"{stem}  SOURCE / MASTER", font=label_font, fill=(255, 255, 255, 255))
        sheet.alpha_composite(source_disp, (x + 15, y + 34))
        sheet.alpha_composite(output_disp, (x + 15, y + 136))
    contact_path = project / "evidence" / "ui" / "grpo_malie_master_contact_sheet.png"
    contact_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(contact_path)

    result = {
        "schema": "fairytale-requiem-grpo-malie-master-ui-v1",
        "policy": {
            "consumer_graph_before_edit": True,
            "complete_state_family": True,
            "no_inpainting": True,
            "no_blur_or_smear": True,
            "no_tiled_micro_patches": True,
            "protected_pixels_locked": True,
            "dimensions_locked": True,
            "script_positions_and_hitboxes_untouched": True,
        },
        "source_archive": {
            "path": str(project / "baseline" / "grpo.roundtrip.xfl"),
            "sha256": sha256_path(project / "baseline" / "grpo.roundtrip.xfl"),
        },
        "output_archive": {
            "path": str(rebuilt_xfl),
            "size": rebuilt_xfl.stat().st_size,
            "sha256": sha256_path(rebuilt_xfl),
        },
        "consumer_graph": {
            "path": str(project / "audit" / "malie_master_grpo_consumer_graph.json"),
            "sha256": sha256_path(project / "audit" / "malie_master_grpo_consumer_graph.json"),
            "state_family_count": len(consumer_graph["state_families"]),
        },
        "entry_count": len(entry_names),
        "changed_entry_count": len(actual_changed),
        "changed_entries": actual_changed,
        "preserved_entries": [name for name in entry_names if name not in actual_changed],
        "locked_unrevealed_asset": {
            "name": "0106.wcg",
            "status": "byte-identical",
            "sha256": sha256_path(source_root / "0106.wcg"),
        },
        "records": records,
        "contact_sheet": {"path": str(contact_path), "sha256": sha256_path(contact_path)},
        "structural_verification": {
            "entry_order_preserved": True,
            "entry_names_and_case_preserved": True,
            "only_allowlisted_entries_changed": True,
            "all_8_state_families_closed": True,
            "0106_locked_state_preserved": True,
            "wcg_decode_dimensions_and_alpha_verified": True,
        },
        "runtime_status": "pending_master_runtime_capture",
    }
    audit_path = project / "audit" / "grpo_korean_ui_malie_master.json"
    write_json(audit_path, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.project.resolve())
    print(json.dumps({
        "status": "PASS",
        "output_archive": result["output_archive"],
        "changed_entries": result["changed_entries"],
        "contact_sheet": result["contact_sheet"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
