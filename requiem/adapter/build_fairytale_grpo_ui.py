#!/usr/bin/env python3
"""Create the first-pass Korean title/menu UI for Fairytale Requiem.

The builder keeps the original WCG containers, replaces only explicit pixel
masks, rebuilds grpo.xfl from the trusted table manifest, and records the exact
changed-entry allowlist.  This is the deliberately single UI drafting pass;
further visual changes are deferred until an actual runtime launch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


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
    # 0106 intentionally remains the locked/unrevealed marker "???".
    "0107": "종료",
    "0108": "FC 시나리오",
}


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


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


def fit_font(
    text: str,
    font_path: Path,
    max_width: int,
    max_height: int,
    max_size: int,
    min_size: int,
    stroke_width: int,
) -> tuple[ImageFont.FreeTypeFont, tuple[int, int, int, int]]:
    for size in range(max_size, min_size - 1, -1):
        font = ImageFont.truetype(str(font_path), size=size)
        bbox = font.getbbox(text, stroke_width=stroke_width)
        if bbox[2] - bbox[0] <= max_width and bbox[3] - bbox[1] <= max_height:
            return font, bbox
    font = ImageFont.truetype(str(font_path), size=min_size)
    return font, font.getbbox(text, stroke_width=stroke_width)


def build_large_label(
    original: Image.Image,
    target: str,
    font_path: Path,
) -> tuple[Image.Image, dict[str, object]]:
    original = original.convert("RGBA")
    x0, y0, x1, y1 = alpha_bbox(original)
    # Preserve the right-edge alignment used by the original title screen.
    right_edge = min(original.width - 2, x1)
    center_y = (y0 + y1) / 2
    max_width = min(390, right_edge - 385)
    font, bbox = fit_font(
        target,
        font_path,
        max_width=max_width,
        max_height=78,
        max_size=72,
        min_size=38,
        stroke_width=7,
    )
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    x = round(right_edge - width - bbox[0] - 18)
    y = round(center_y - height / 2 - bbox[1] - 3)
    canvas = Image.new("RGBA", original.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    # Soft gray drop shadow, heavy black outline, and white face mirror the
    # Japanese bitmap's visual hierarchy without reusing its glyph pixels.
    draw.text(
        (x + 7, y + 8),
        target,
        font=font,
        fill=(115, 115, 115, 205),
        stroke_width=8,
        stroke_fill=(92, 92, 92, 170),
    )
    draw.text(
        (x, y),
        target,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=7,
        stroke_fill=(12, 12, 12, 255),
    )
    return canvas, {
        "target": target,
        "source_alpha_bbox": [x0, y0, x1, y1],
        "text_position": [x, y],
        "font": str(font_path),
        "font_size": font.size,
        "text_bbox": list(bbox),
    }


def white_text_mask(array: np.ndarray) -> np.ndarray:
    rgb = array[:, :, :3]
    alpha = array[:, :, 3]
    white = (
        (alpha > 20)
        & (rgb[:, :, 0] > 155)
        & (rgb[:, :, 1] > 155)
        & (rgb[:, :, 2] > 155)
        & ((rgb.max(axis=2) - rgb.min(axis=2)) < 48)
    )
    # Only the lower label strip contains white English lettering.
    lower = np.zeros_like(white)
    lower[array.shape[0] // 2 :, :] = True
    white &= lower
    return white


def principal_angle(mask: np.ndarray) -> float:
    ys, xs = np.where(mask)
    if len(xs) < 3:
        return 0.0
    points = np.column_stack([xs, ys]).astype(np.float32)
    _, eigenvectors = cv2.PCACompute(points, mean=None, maxComponents=2)
    vx, vy = eigenvectors[0]
    angle = math.degrees(math.atan2(float(vy), float(vx)))
    if angle > 45:
        angle -= 180
    if angle < -45:
        angle += 180
    return angle


def build_small_label(
    original: Image.Image,
    target: str,
    font_path: Path,
) -> tuple[Image.Image, np.ndarray, dict[str, object]]:
    original = original.convert("RGBA")
    source = np.asarray(original, dtype=np.uint8)
    white = white_text_mask(source)
    ys, xs = np.where(white)
    if len(xs) < 10:
        raise ValueError("could not locate the English label pixels")
    angle = principal_angle(white)
    # Cover anti-aliasing around the white face; the underlying dark strip is
    # reconstructed with OpenCV inpainting while all other pixels stay intact.
    erase_mask = cv2.dilate(
        (white.astype(np.uint8) * 255),
        np.ones((5, 5), dtype=np.uint8),
        iterations=1,
    )
    rgb = cv2.cvtColor(source, cv2.COLOR_RGBA2RGB)
    erased_rgb = cv2.inpaint(rgb, erase_mask, 3, cv2.INPAINT_TELEA)
    erased = np.dstack([erased_rgb, source[:, :, 3]]).astype(np.uint8)
    canvas = Image.fromarray(erased, "RGBA")

    x0, x1 = int(xs.min()), int(xs.max()) + 1
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    center = ((x0 + x1) / 2, (y0 + y1) / 2)
    max_width = max(34, x1 - x0 + 8)
    max_height = max(18, y1 - y0 + 4)
    font, bbox = fit_font(
        target,
        font_path,
        max_width=max_width,
        max_height=max_height,
        max_size=19,
        min_size=10,
        stroke_width=1,
    )
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    text_layer = Image.new("RGBA", (max(80, tw + 20), max(48, th + 20)), (0, 0, 0, 0))
    td = ImageDraw.Draw(text_layer)
    tx, ty = (text_layer.width - tw) / 2 - bbox[0], (text_layer.height - th) / 2 - bbox[1]
    td.text(
        (tx, ty),
        target,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=1,
        stroke_fill=(10, 10, 10, 255),
    )
    rotated = text_layer.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    paste_x = round(center[0] - rotated.width / 2)
    paste_y = round(center[1] - rotated.height / 2)
    canvas.alpha_composite(rotated, (paste_x, paste_y))
    edited = np.asarray(canvas, dtype=np.uint8)
    changed = np.any(source != edited, axis=2)
    return canvas, changed, {
        "target": target,
        "source_white_bbox": [x0, y0, x1, y1],
        "source_principal_angle_degrees": round(angle, 3),
        "text_center": [round(center[0], 2), round(center[1], 2)],
        "font": str(font_path),
        "font_size": font.size,
        "changed_pixel_count": int(changed.sum()),
    }


def make_full_mask(size: tuple[int, int]) -> Image.Image:
    return Image.new("L", size, 255)


def compare_decoded(expected: Image.Image, decoded: Image.Image) -> dict[str, object]:
    a = np.asarray(expected.convert("RGBA"), dtype=np.uint8)
    b = np.asarray(decoded.convert("RGBA"), dtype=np.uint8)
    if a.shape != b.shape:
        raise ValueError("decoded image dimensions changed")
    alpha_equal = np.array_equal(a[:, :, 3], b[:, :, 3])
    visible = (a[:, :, 3] > 0) | (b[:, :, 3] > 0)
    visible_equal = np.array_equal(a[visible], b[visible])
    delta = np.abs(a.astype(np.int16) - b.astype(np.int16))
    max_visible_rgb_delta = int(delta[:, :, :3][visible].max()) if visible.any() else 0
    substantive = visible & (a[:, :, 3] >= 16)
    max_substantive_rgb_delta = (
        int(delta[:, :, :3][substantive].max()) if substantive.any() else 0
    )
    return {
        "dimensions_equal": True,
        "alpha_equal": bool(alpha_equal),
        "visible_rgba_equal": bool(visible_equal),
        "visible_changed_pixel_count": int(np.any(a != b, axis=2)[visible].sum()),
        "max_visible_rgb_delta": max_visible_rgb_delta,
        "max_substantive_alpha_rgb_delta": max_substantive_rgb_delta,
        "wcg_quantization_acceptable": bool(max_substantive_rgb_delta <= 8),
    }


def build(project: Path) -> dict[str, object]:
    tool = project / "adapter" / "UiAssetTool.exe"
    xfl_tool = project / "adapter" / "xfl_tool.py"
    source_root = project / "extracted" / "grpo"
    png_root = project / "evidence" / "ui" / "grpo_png"
    manifest_path = project / "audit" / "grpo_xfl_manifest.json"
    stage = project / "staging" / "ui_first_pass"
    wcg_root = stage / "grpo_entries"
    patch_root = stage / "png_patches"
    decoded_root = stage / "decoded_png"
    rebuilt_root = stage / "grpo_rebuild_tree"
    for path in (wcg_root, patch_root, decoded_root):
        path.mkdir(parents=True, exist_ok=True)
    if rebuilt_root.exists():
        shutil.rmtree(rebuilt_root)
    shutil.copytree(source_root, rebuilt_root)

    font = Path(r"C:\Windows\Fonts\malgunbd.ttf")
    for required in (tool, xfl_tool, source_root, png_root, manifest_path, font):
        if not required.exists():
            raise FileNotFoundError(required)

    records: list[dict[str, object]] = []
    targets = dict(SMALL_LABELS) | dict(LARGE_LABELS)
    for stem, target in targets.items():
        source_wcg = source_root / f"{stem}.wcg"
        source_png = png_root / f"{stem}.png"
        original = Image.open(source_png).convert("RGBA")
        if stem.startswith("00"):
            edited, changed_mask, details = build_small_label(original, target, font)
            mask = Image.fromarray(changed_mask.astype(np.uint8) * 255, "L")
        else:
            edited, details = build_large_label(original, target, font)
            mask = make_full_mask(original.size)
        patch_png = patch_root / f"{stem}.patch.png"
        mask_png = patch_root / f"{stem}.mask.png"
        output_wcg = wcg_root / f"{stem}.wcg"
        decoded_png = decoded_root / f"{stem}.png"
        edited.save(patch_png)
        mask.save(mask_png)
        patch_stdout = run(
            [str(tool), "wcg-apply-patch", str(source_wcg), str(patch_png), str(mask_png), str(output_wcg)]
        )
        run([str(tool), "wcg2png", str(output_wcg), str(decoded_png)])
        decoded = Image.open(decoded_png).convert("RGBA")
        comparison = compare_decoded(edited, decoded)
        if not comparison["alpha_equal"] or not comparison["wcg_quantization_acceptable"]:
            raise RuntimeError(f"WCG decoded pixels differ from edited PNG: {stem}: {comparison}")
        shutil.copy2(output_wcg, rebuilt_root / output_wcg.name)
        records.append(
            {
                "stable_id": f"grpo.xfl::{stem}.wcg",
                "source_label": source_wcg.name,
                "target_ko": target,
                "source_wcg_sha256": sha256_path(source_wcg),
                "output_wcg_sha256": sha256_path(output_wcg),
                "source_png_sha256": sha256_path(source_png),
                "patch_png_sha256": sha256_path(patch_png),
                "mask_pixel_count": int((np.asarray(mask) > 0).sum()),
                "decoded_pixel_verification": comparison,
                "tool_output": patch_stdout.splitlines()[0] if patch_stdout else "",
                "typesetting": details,
            }
        )

    rebuilt_xfl = stage / "grpo.ko-first-pass.xfl"
    repack_report = project / "audit" / "grpo_ko_first_pass_repack.json"
    run(
        [
            sys.executable,
            str(xfl_tool),
            "repack",
            str(rebuilt_root),
            str(manifest_path),
            str(rebuilt_xfl),
            "--report",
            str(repack_report),
        ]
    )

    source_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entry_names = [entry["name"] for entry in source_manifest["entries"]]
    expected_changed = [f"{stem}.wcg" for stem in targets]
    actual_changed: list[str] = []
    for name in entry_names:
        if (source_root / name).read_bytes() != (rebuilt_root / name).read_bytes():
            actual_changed.append(name)
    if actual_changed != [name for name in entry_names if name in expected_changed]:
        raise RuntimeError(f"unexpected changed-entry set: {actual_changed}")

    # Assemble a contact sheet for runtime-reference only; no second offline UI
    # revision is performed from it, per the user's requested workflow.
    sheet = Image.new("RGBA", (900, 16 * 180), (36, 36, 40, 255))
    sheet_draw = ImageDraw.Draw(sheet)
    y = 10
    label_font = ImageFont.truetype(str(font), size=18)
    for stem in list(SMALL_LABELS) + list(LARGE_LABELS):
        if stem in targets:
            image = Image.open(decoded_root / f"{stem}.png").convert("RGBA")
        else:
            image = Image.open(png_root / f"{stem}.png").convert("RGBA")
        display = image.copy()
        display.thumbnail((760, 140), Image.Resampling.LANCZOS)
        sheet_draw.text((10, y + 55), f"{stem}  {targets.get(stem, '원본 유지')}", font=label_font, fill="white")
        sheet.alpha_composite(display, (130, y))
        y += 170
    sheet = sheet.crop((0, 0, sheet.width, y + 10))
    sheet_path = project / "evidence" / "ui" / "grpo_ko_first_pass_contact_sheet.png"
    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(sheet_path)

    result = {
        "schema": "fairytale-requiem-grpo-korean-ui-first-pass-v1",
        "policy": "single offline drafting pass; next changes only after runtime evidence",
        "source_archive": {
            "path": str(project / "baseline" / "grpo.roundtrip.xfl"),
            "sha256": "F3B6FAF5FB462E3E349F5B5833C71E1214440ADE5F5A4C7B7F7C1C87588F9314",
        },
        "output_archive": {
            "path": str(rebuilt_xfl),
            "size": rebuilt_xfl.stat().st_size,
            "sha256": sha256_path(rebuilt_xfl),
        },
        "entry_count": len(entry_names),
        "changed_entry_count": len(actual_changed),
        "changed_entries": actual_changed,
        "preserved_entry_count": len(entry_names) - len(actual_changed),
        "locked_unrevealed_asset": "0106.wcg kept byte-identical as ???",
        "records": records,
        "contact_sheet": str(sheet_path),
        "contact_sheet_sha256": sha256_path(sheet_path),
        "structural_verification": {
            "entry_order_preserved": True,
            "entry_names_and_case_preserved": True,
            "only_allowlisted_entries_changed": True,
            "decoded_output_matches_edited_pixels_with_bounded_wcg_quantization": True,
        },
        "runtime_status": "not_tested",
    }
    output_manifest = project / "audit" / "grpo_korean_ui_first_pass.json"
    output_manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.project.resolve())
    print(
        json.dumps(
            {
                "output_archive": result["output_archive"],
                "changed_entry_count": result["changed_entry_count"],
                "changed_entries": result["changed_entries"],
                "contact_sheet": result["contact_sheet"],
            },
            ensure_ascii=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
