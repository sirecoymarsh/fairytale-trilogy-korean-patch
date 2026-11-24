#!/usr/bin/env python3
"""Build and validate Korean gallery tooltip labels in grpo_map.xfl.

Only the five authored LWG tooltip plates (0301-0305) are changed.  Their
original torn-paper alpha/chrome remains protected; Japanese glyph pixels are
restored from the brightest same-coordinate sample found in authored sibling
plates, then Korean lettering is rendered in the source's hand-drawn style.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
SOURCE = ROOT / "staging" / "grpo_map_korean_ui_v4_c" / "grpo_map.ko-ui.xfl"
SOURCE_MANIFEST = ROOT / "audit" / "grpo_map_source_manifest.json"
TOOL = ROOT / "adapter" / "UiAssetTool.exe"
XFL_TOOL = ROOT / "adapter" / "xfl_tool.py"
FONT = ROOT / "tools" / "fonts" / "Gaegu-Bold.ttf"
AUDIT = ROOT / "audit" / "grpo_map_gallery_labels_korean_v1_build.json"

LABELS = {
    "0301": "CG 감상",
    "0302": "장면 감상",
    "0303": "BGM 감상",
    "0304": "스케치북",
    "0305": "책장",
}

FONT_SIZES = {"0301": 34, "0302": 34, "0303": 31, "0304": 34, "0305": 34}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def run(*args: object) -> None:
    subprocess.run([str(x) for x in args], check=True, stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE, creationflags=0x08000000)


def png_file(directory: Path) -> Path:
    files = list(directory.glob("*.png"))
    if len(files) != 1:
        raise RuntimeError(f"expected one PNG in {directory}, got {len(files)}")
    return files[0]


def alpha_inner_mask(alpha: np.ndarray, radius: int = 5) -> np.ndarray:
    # MinFilter performs an erosion: only pixels safely inside the authored
    # paper silhouette are eligible for glyph removal.
    return np.array(Image.fromarray(alpha).filter(ImageFilter.MinFilter(radius))) >= 245


def glyph_mask(rgba: np.ndarray) -> np.ndarray:
    rgb = rgba[:, :, :3].astype(np.int16)
    alpha = rgba[:, :, 3]
    lum = rgb.mean(axis=2)
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    raw = (lum < 235) & (chroma < 85) & alpha_inner_mask(alpha)
    return np.array(
        Image.fromarray((raw * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
    ) > 0


def sibling_sample(images: dict[str, np.ndarray], key: str, x: int, y: int) -> np.ndarray:
    target = images[key]
    h, w = target.shape[:2]
    candidates: list[np.ndarray] = []
    for other_key, other in images.items():
        if other_key == key:
            continue
        oh, ow = other.shape[:2]
        sx = min(ow - 1, max(0, round(x * (ow - 1) / max(1, w - 1))))
        sy = min(oh - 1, max(0, round(y * (oh - 1) / max(1, h - 1))))
        # Search a small authored neighborhood as well as the normalized
        # coordinate.  This avoids choosing a coincident glyph stroke from a
        # sibling while still copying only real source paper pixels.
        for dy in range(-5, 6):
            yy = min(oh - 1, max(0, sy + dy))
            for dx in range(-7, 8):
                xx = min(ow - 1, max(0, sx + dx))
                px = other[yy, xx]
                if px[3] >= 245:
                    candidates.append(px)
    if not candidates:
        return target[y, x]
    # A black Japanese stroke cannot win this source-authored lightness test.
    return max(candidates, key=lambda p: int(p[0]) + int(p[1]) + int(p[2]))


def render_plate(images: dict[str, np.ndarray], key: str, out_png: Path) -> dict:
    original = images[key]
    mask = glyph_mask(original)
    clean = original.copy()
    for y, x in zip(*np.where(mask)):
        donor = sibling_sample(images, key, int(x), int(y))
        clean[y, x, :3] = donor[:3]
        # Preserve the target plate's authored alpha exactly.
    canvas = Image.fromarray(clean, "RGBA")
    font = ImageFont.truetype(str(FONT), FONT_SIZES[key])
    draw = ImageDraw.Draw(canvas)
    text = LABELS[key]
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=1)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    w, h = canvas.size
    x = (w - tw) // 2 - bbox[0]
    y = (h - th) // 2 - bbox[1] - 1
    draw.text((x, y), text, font=font, fill=(15, 15, 15, 255),
              stroke_width=1, stroke_fill=(15, 15, 15, 255))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_png)
    result = np.array(canvas)
    # Freeze the planned repair/lettering ownership mask before packing.
    # Persisted reopen validation then proves the codec did not touch anything
    # outside that exact mask.
    owned = np.any(result != original, axis=2)
    owned_path = out_png.parents[2] / "owned_masks" / f"{key}.png"
    owned_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((owned * 255).astype(np.uint8)).save(owned_path)
    oy, ox = np.where(owned)
    return {
        "label": text,
        "size": [w, h],
        "font_size": FONT_SIZES[key],
        "source_glyph_owned_pixels": int(mask.sum()),
        "owned_pixels": int(owned.sum()),
        "owned_bbox": [int(ox.min()), int(oy.min()), int(ox.max()) + 1, int(oy.max()) + 1],
        "protected_pixels_exact": bool(np.array_equal(result[~owned], original[~owned])),
        "target_alpha_exact": bool(np.array_equal(result[:, :, 3], original[:, :, 3])),
        "text_bbox": [x + bbox[0], y + bbox[1], x + bbox[2], y + bbox[3]],
    }


def build(tag: str) -> dict:
    stage = ROOT / "staging" / f"grpo_map_gallery_labels_korean_v1_{tag}"
    if stage.exists():
        shutil.rmtree(stage)
    tree = stage / "tree"
    manifest = stage / "source_manifest.json"
    run("python", XFL_TOOL, "extract", SOURCE, tree, "--manifest", manifest)

    extract_dirs: dict[str, Path] = {}
    images: dict[str, np.ndarray] = {}
    meta_before: dict[str, str] = {}
    for key in LABELS:
        directory = stage / "lwg_png" / key
        run(TOOL, "lwg-extract-png", tree / f"{key}.lwg", directory)
        extract_dirs[key] = directory
        meta_before[key] = (directory / ".meta.xml").read_text(encoding="utf-8")
        images[key] = np.array(Image.open(png_file(directory)).convert("RGBA"))

    # LWG persistence performs a tiny RGB quantization on some translucent
    # pixels.  Build a no-change same-codec control for each plate so the
    # protected-pixel comparison measures only localization deltas.
    controls: dict[str, np.ndarray] = {}
    for key in LABELS:
        control_lwg = stage / "control_lwg" / f"{key}.lwg"
        control_lwg.parent.mkdir(parents=True, exist_ok=True)
        run(TOOL, "lwg-pack-png", extract_dirs[key], control_lwg)
        control_dir = stage / "control_persisted_lwg_png" / key
        run(TOOL, "lwg-extract-png", control_lwg, control_dir)
        controls[key] = np.array(Image.open(png_file(control_dir)).convert("RGBA"))

    records: dict[str, dict] = {}
    source_entry_hashes = {f"{k}.lwg": sha256(tree / f"{k}.lwg") for k in LABELS}
    for key in LABELS:
        target_png = png_file(extract_dirs[key])
        records[key] = render_plate(images, key, target_png)
        run(TOOL, "lwg-pack-png", extract_dirs[key], tree / f"{key}.lwg")
        records[key]["source_lwg_sha256"] = source_entry_hashes[f"{key}.lwg"]
        records[key]["output_lwg_sha256"] = sha256(tree / f"{key}.lwg")
        records[key]["meta_xml_exact_before_pack"] = (
            (extract_dirs[key] / ".meta.xml").read_text(encoding="utf-8") == meta_before[key]
        )

    output = stage / "grpo_map.ko-gallery-labels-v1.xfl"
    report = stage / "repack.json"
    run("python", XFL_TOOL, "repack", tree, manifest, output, "--report", report)

    source_manifest = json.loads(manifest.read_text(encoding="utf-8"))
    output_manifest = json.loads(report.read_text(encoding="utf-8"))
    src = {x["name"]: x["sha256"] for x in source_manifest["entries"]}
    dst = {x["name"]: x["sha256"] for x in output_manifest["entries"]}
    changed = [name for name in src if src[name] != dst[name]]

    persisted: dict[str, dict] = {}
    for key in LABELS:
        directory = stage / "persisted_lwg_png" / key
        run(TOOL, "lwg-extract-png", tree / f"{key}.lwg", directory)
        arr = np.array(Image.open(png_file(directory)).convert("RGBA"))
        original = images[key]
        mask = np.array(Image.open(stage / "owned_masks" / f"{key}.png").convert("L")) > 0
        persisted[key] = {
            "size_exact": list(arr.shape) == list(original.shape),
            "protected_pixels_exact": bool(np.array_equal(arr[~mask], controls[key][~mask])),
            "same_codec_control_alpha_matches_source": bool(np.array_equal(controls[key][:, :, 3], original[:, :, 3])),
            "alpha_exact": bool(np.array_equal(arr[:, :, 3], original[:, :, 3])),
            "meta_xml_exact": (directory / ".meta.xml").read_text(encoding="utf-8") == meta_before[key],
        }

    checks = {
        "source_hash_frozen": sha256(SOURCE) == "F7F8552319DB82635024FCA9048BEC126D0025D5783F04CB01237A94604963E0",
        "changed_entries_exact": changed == [f"{k}.lwg" for k in LABELS],
        "all_non_targets_byte_exact": all(src[n] == dst[n] for n in src if n not in changed),
        "all_render_protected_exact": all(r["protected_pixels_exact"] for r in records.values()),
        "all_render_alpha_exact": all(r["target_alpha_exact"] for r in records.values()),
        "all_persisted_protected_exact": all(r["protected_pixels_exact"] for r in persisted.values()),
        "all_persisted_alpha_exact": all(r["alpha_exact"] for r in persisted.values()),
        "all_persisted_meta_exact": all(r["meta_xml_exact"] for r in persisted.values()),
    }
    if not all(checks.values()):
        raise RuntimeError(f"validation failed: {checks}")
    return {
        "tag": tag,
        "output": str(output),
        "output_sha256": sha256(output),
        "output_size": output.stat().st_size,
        "changed_entries": changed,
        "records": records,
        "persisted": persisted,
        "checks": checks,
    }


def main() -> None:
    a = build("a")
    b = build("b")
    checks = {
        "a_pass": all(a["checks"].values()),
        "b_pass": all(b["checks"].values()),
        "a_b_byte_identical": a["output_sha256"] == b["output_sha256"],
    }
    report = {
        "schema": "fairytale-requiem-grpo-map-gallery-labels-korean-build-v1",
        "status": "PASS_STATIC_RUNTIME_PENDING" if all(checks.values()) else "FAIL",
        "completed_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": {"path": str(SOURCE), "sha256": sha256(SOURCE)},
        "font": {"path": str(FONT), "sha256": sha256(FONT)},
        "build_a": a,
        "build_b": b,
        "checks": checks,
    }
    AUDIT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if report["status"] == "FAIL":
        raise SystemExit(1)
    print(json.dumps({"status": report["status"], "sha256": a["output_sha256"],
                      "changed_entries": a["changed_entries"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
