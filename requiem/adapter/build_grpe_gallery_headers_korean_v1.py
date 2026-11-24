#!/usr/bin/env python3
"""Localize the CG/scene/BGM gallery header plates in grpe.xfl.

The source uses three full-screen WCG backgrounds (9001-9003).  Only the
white title glyphs inside the authored black crayon plates are replaced.
All other archive payloads are copied byte-for-byte from the frozen source.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import xfl_tool


ROOT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
SOURCE = ROOT / "runtime" / "trial_ko" / "grpe.xfl"
TOOL = ROOT / "adapter" / "UiAssetTool.exe"
FONT = ROOT / "tools" / "fonts" / "Gaegu-Bold.ttf"
AUDIT = ROOT / "audit" / "grpe_gallery_headers_korean_v1_build.json"
SOURCE_SHA256 = "435991C6C44473C5F6AFCAE2902481FBBF4B40EC942B2EC12E95AD7EF390DE94"

TARGETS = {
    "9001": {"text": "\uac10\uc0c1", "font_size": 64, "roi": (145, 18, 282, 118)},
    "9002": {"text": "\uc7a5\uba74 \uac10\uc0c1", "font_size": 60, "roi": (25, 18, 345, 118)},
    "9003": {"text": "\uac10\uc0c1", "font_size": 64, "roi": (200, 18, 335, 118)},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def run(*args: object) -> None:
    subprocess.run([str(x) for x in args], check=True, stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE, creationflags=0x08000000)


def white_glyph_mask(rgba: np.ndarray, roi: tuple[int, int, int, int]) -> np.ndarray:
    rgb = rgba[:, :, :3].astype(np.int16)
    lum = rgb.mean(axis=2)
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    x1, y1, x2, y2 = roi
    owned = np.zeros(rgba.shape[:2], dtype=bool)
    owned[y1:y2, x1:x2] = True
    raw = (lum > 130) & (chroma < 75) & owned
    return np.array(
        Image.fromarray((raw * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))
    ) > 0


def darkest_authored_pixel(images: dict[str, np.ndarray], key: str, x: int, y: int) -> np.ndarray:
    # Prefer the same coordinate from siblings: their white glyphs occupy
    # different places while the underlying crayon plate is authored alike.
    same = [im[y, x] for k, im in images.items() if k != key]
    dark = [p for p in same if float(p[:3].mean()) < 105]
    if dark:
        return min(dark, key=lambda p: int(p[0]) + int(p[1]) + int(p[2]))
    # Where sibling glyphs overlap, use the closest genuinely dark pixel from
    # the target plate.  This is a direct authored-pixel donor, not inpainting.
    target = images[key]
    h, w = target.shape[:2]
    for radius in range(1, 15):
        candidates: list[np.ndarray] = []
        for dx, dy in ((-radius, 0), (radius, 0), (0, -radius), (0, radius),
                       (-radius, -radius), (radius, -radius),
                       (-radius, radius), (radius, radius)):
            xx, yy = x + dx, y + dy
            if 0 <= xx < w and 0 <= yy < h:
                p = target[yy, xx]
                if float(p[:3].mean()) < 105:
                    candidates.append(p)
        if candidates:
            return min(candidates, key=lambda p: int(p[0]) + int(p[1]) + int(p[2]))
    return np.array([5, 3, 4, target[y, x, 3]], dtype=np.uint8)


def render(images: dict[str, np.ndarray], key: str, stage: Path) -> tuple[Path, Path, dict]:
    original = images[key]
    spec = TARGETS[key]
    source_mask = white_glyph_mask(original, spec["roi"])
    clean = original.copy()
    for y, x in zip(*np.where(source_mask)):
        clean[y, x, :3] = darkest_authored_pixel(images, key, int(x), int(y))[:3]

    canvas = Image.fromarray(clean, "RGBA")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(str(FONT), spec["font_size"])
    text = spec["text"]
    x1, y1, x2, y2 = spec["roi"]
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=1)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (x1 + x2 - tw) // 2 - bbox[0]
    ty = (y1 + y2 - th) // 2 - bbox[1] - 1
    draw.text((tx, ty), text, font=font, fill=(255, 255, 255, 255),
              stroke_width=1, stroke_fill=(218, 218, 218, 255))

    result = np.array(canvas)
    owned = np.any(result != original, axis=2)
    patch = stage / "candidate_png" / f"{key}.png"
    mask = stage / "owned_masks" / f"{key}.png"
    patch.parent.mkdir(parents=True, exist_ok=True)
    mask.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(patch)
    Image.fromarray((owned * 255).astype(np.uint8)).save(mask)
    oy, ox = np.where(owned)
    return patch, mask, {
        "entry": f"{key}.wcg",
        "target_ko": text,
        "source_glyph_pixels": int(source_mask.sum()),
        "owned_pixels": int(owned.sum()),
        "owned_bbox": [int(ox.min()), int(oy.min()), int(ox.max()) + 1, int(oy.max()) + 1],
        "text_bbox": [tx + bbox[0], ty + bbox[1], tx + bbox[2], ty + bbox[3]],
        "protected_pixels_exact_before_persist": bool(np.array_equal(result[~owned], original[~owned])),
        "alpha_exact_before_persist": bool(np.array_equal(result[:, :, 3], original[:, :, 3])),
    }


def write_archive(archive: xfl_tool.Archive, replacements: dict[str, bytes], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    sizes = {e.name: len(replacements[e.name]) if e.name in replacements else e.size
             for e in archive.entries}
    with SOURCE.open("rb") as src, output.open("wb") as dst:
        dst.write(xfl_tool.MAGIC)
        dst.write(struct.pack("<II", len(archive.entries) * xfl_tool.ENTRY_SIZE,
                              len(archive.entries)))
        offset = 0
        for entry in archive.entries:
            dst.write(entry.raw_name)
            dst.write(struct.pack("<II", offset, sizes[entry.name]))
            offset += sizes[entry.name]
        for entry in archive.entries:
            if entry.name in replacements:
                dst.write(replacements[entry.name])
            else:
                src.seek(entry.absolute_offset)
                remaining = entry.size
                while remaining:
                    chunk = src.read(min(8 * 1024 * 1024, remaining))
                    if not chunk:
                        raise RuntimeError(f"short source read: {entry.name}")
                    dst.write(chunk)
                    remaining -= len(chunk)


def build(tag: str, archive: xfl_tool.Archive, replacements: dict[str, bytes]) -> dict:
    out = ROOT / "staging" / f"grpe_gallery_headers_korean_v1_{tag}" / "grpe.ko-gallery-headers-v1.xfl"
    write_archive(archive, replacements, out)
    parsed = xfl_tool.parse_archive(out)
    checks = {
        "entry_names_and_order_exact": [e.name for e in parsed.entries] == [e.name for e in archive.entries],
        "entry_count_exact": len(parsed.entries) == len(archive.entries),
        "archive_contiguous_no_trailing": parsed.entries[-1].absolute_offset + parsed.entries[-1].size == out.stat().st_size,
    }
    return {"tag": tag, "path": str(out), "size": out.stat().st_size,
            "sha256": sha256(out), "checks": checks}


def main() -> None:
    if sha256(SOURCE) != SOURCE_SHA256:
        raise RuntimeError("frozen grpe source hash mismatch")
    archive = xfl_tool.parse_archive(SOURCE)
    by_name = {e.name: e for e in archive.entries}
    stage = ROOT / "staging" / "grpe_gallery_headers_korean_v1_assets"
    if stage.exists():
        shutil.rmtree(stage)
    (stage / "source_wcg").mkdir(parents=True)
    (stage / "source_png").mkdir(parents=True)

    images: dict[str, np.ndarray] = {}
    with SOURCE.open("rb") as src:
        for key in TARGETS:
            entry = by_name[f"{key}.wcg"]
            src.seek(entry.absolute_offset)
            wcg = stage / "source_wcg" / f"{key}.wcg"
            wcg.write_bytes(src.read(entry.size))
            png = stage / "source_png" / f"{key}.png"
            run(TOOL, "wcg2png", wcg, png)
            images[key] = np.array(Image.open(png).convert("RGBA"))

    replacements: dict[str, bytes] = {}
    records: dict[str, dict] = {}
    for key in TARGETS:
        patch, mask, record = render(images, key, stage)
        original_wcg = stage / "source_wcg" / f"{key}.wcg"
        control_wcg = stage / "control_wcg" / f"{key}.wcg"
        output_wcg = stage / "output_wcg" / f"{key}.wcg"
        control_wcg.parent.mkdir(parents=True, exist_ok=True)
        output_wcg.parent.mkdir(parents=True, exist_ok=True)
        run(TOOL, "wcg-roundtrip-pixels", original_wcg, control_wcg)
        run(TOOL, "wcg-apply-patch", original_wcg, patch, mask, output_wcg)
        control_png = stage / "control_png" / f"{key}.png"
        output_png = stage / "output_png" / f"{key}.png"
        control_png.parent.mkdir(parents=True, exist_ok=True)
        output_png.parent.mkdir(parents=True, exist_ok=True)
        run(TOOL, "wcg2png", control_wcg, control_png)
        run(TOOL, "wcg2png", output_wcg, output_png)
        control = np.array(Image.open(control_png).convert("RGBA"))
        persisted = np.array(Image.open(output_png).convert("RGBA"))
        owned = np.array(Image.open(mask).convert("L")) > 0
        record.update({
            "source_wcg_sha256": sha256(original_wcg),
            "output_wcg_sha256": sha256(output_wcg),
            "persisted_protected_pixels_exact_vs_same_codec_control": bool(np.array_equal(persisted[~owned], control[~owned])),
            "persisted_alpha_exact": bool(np.array_equal(persisted[:, :, 3], images[key][:, :, 3])),
        })
        if not record["persisted_protected_pixels_exact_vs_same_codec_control"] or not record["persisted_alpha_exact"]:
            raise RuntimeError(f"persisted pixel validation failed: {key}")
        replacements[f"{key}.wcg"] = output_wcg.read_bytes()
        records[key] = record

    a = build("a", archive, replacements)
    b = build("b", archive, replacements)
    checks = {
        "source_hash_frozen": sha256(SOURCE) == SOURCE_SHA256,
        "replacement_entries_exact": sorted(replacements) == ["9001.wcg", "9002.wcg", "9003.wcg"],
        "all_entry_build_checks": all(a["checks"].values()) and all(b["checks"].values()),
        "a_b_byte_identical": a["sha256"] == b["sha256"],
        "all_persisted_protected_pixels_exact": all(r["persisted_protected_pixels_exact_vs_same_codec_control"] for r in records.values()),
        "all_persisted_alpha_exact": all(r["persisted_alpha_exact"] for r in records.values()),
    }
    report = {
        "schema": "fairytale-requiem-grpe-gallery-headers-korean-build-v1",
        "status": "PASS_STATIC_RUNTIME_PENDING" if all(checks.values()) else "FAIL",
        "completed_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": {"path": str(SOURCE), "sha256": sha256(SOURCE), "entry_count": len(archive.entries)},
        "font": {"path": str(FONT), "sha256": sha256(FONT)},
        "records": records,
        "build_a": a,
        "build_b": b,
        "checks": checks,
    }
    AUDIT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "sha256": a["sha256"],
                      "changed_entries": sorted(replacements)}, ensure_ascii=False))
    if report["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

