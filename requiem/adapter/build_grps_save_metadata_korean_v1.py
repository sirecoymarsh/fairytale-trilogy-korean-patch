#!/usr/bin/env python3
"""Build deterministic Korean save-slot metadata assets in grps.xfl.

The build preserves every non-dt entry from the currently integrated trial
archive.  dt1 title plates keep the original thumbnail/chrome and replace only
the title slab.  dt2 day/time overlays keep every status icon and replace only
the Japanese text rectangle.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
TRIAL_ARCHIVE = PROJECT / "runtime" / "trial_ko" / "grps.xfl"
TOOL = PROJECT / "adapter" / "UiAssetTool.exe"
XFL_TOOL = PROJECT / "adapter" / "xfl_tool.py"
FONT = PROJECT / "tools" / "fonts" / "Gaegu-Bold.ttf"
TITLE_MAP = PROJECT / "staging" / "grpo_ex_title_translation_v1" / "grpo_ex_title_translation_postreviewed.json"
SOURCE_ROOT = PROJECT / "staging" / "grps_save_metadata_korean_v1_source"
ROOT_A = PROJECT / "staging" / "grps_save_metadata_korean_v1_a"
ROOT_B = PROJECT / "staging" / "grps_save_metadata_korean_v1_b"
AUDIT = PROJECT / "audit" / "grps_save_metadata_korean_v1_build.json"
CONTACT = PROJECT / "staging" / "grps_save_metadata_korean_v1_contact.png"

DT1_OWNED = (122, 49, 491, 69)
DT2_OWNED = (120, 10, 225, 45)


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def run(*args: object) -> str:
    p = subprocess.run([str(x) for x in args], check=True, capture_output=True, text=True)
    return p.stdout.strip()


def frozen_title_map() -> tuple[dict[str, str], dict[str, str]]:
    data = json.loads(TITLE_MAP.read_text(encoding="utf-8"))
    targets: dict[str, str] = {}
    sources: dict[str, str] = {}
    for row in data["scene_titles"]:
        code = str(row["code"])
        targets[code] = str(row["target_ko"])
        sources[code] = str(row["source_corrected"])
    specials = {str(row["normal_entry"]): row for row in data["special_titles"]}
    for code, entry in (("3000", "4000.wcg"), ("3300", "4300.wcg"), ("3600", "4600.wcg")):
        row = specials[entry]
        targets[code] = str(row["target_ko"])
        sources[code] = str(row["source_corrected"])
    return targets, sources


def prepare_source() -> dict[str, Any]:
    if SOURCE_ROOT.exists():
        shutil.rmtree(SOURCE_ROOT)
    extracted = SOURCE_ROOT / "extracted"
    png = SOURCE_ROOT / "png"
    extracted.mkdir(parents=True)
    png.mkdir(parents=True)
    manifest = SOURCE_ROOT / "manifest.json"
    run(sys.executable, XFL_TOOL, "extract", TRIAL_ARCHIVE, extracted, "--manifest", manifest)
    dt_files = sorted([p for p in extracted.glob("dt1_*.wcg")]) + sorted([p for p in extracted.glob("dt2_*.wcg")])
    if len(dt_files) != 652:
        raise ValueError(f"expected 652 dt entries, found {len(dt_files)}")
    for i, src in enumerate(dt_files, 1):
        run(TOOL, "wcg2png", src, png / f"{src.stem}.png")
        if i % 100 == 0:
            print(f"source_png={i}/{len(dt_files)}", flush=True)
    return {
        "archive_sha256": sha256_path(TRIAL_ARCHIVE),
        "archive_size": TRIAL_ARCHIVE.stat().st_size,
        "manifest": manifest,
        "extracted": extracted,
        "png": png,
        "dt_files": dt_files,
    }


def build_dt1_clean(png_root: Path, paths: list[Path]) -> tuple[Image.Image, dict[str, Any]]:
    stack = np.stack([np.array(Image.open(png_root / f"{p.stem}.png").convert("RGBA"), dtype=np.uint8) for p in paths])
    h, w = stack.shape[1:3]
    out = np.empty((h, w, 4), dtype=np.uint8)
    support = np.empty((h, w), dtype=np.uint16)
    # Every title plate was exported from the same PSD template.  At each fixed
    # coordinate, the real textured background is the darkest observed tuple;
    # Japanese title ink and antialiasing are strictly brighter.  We only use
    # this consensus inside DT1_OWNED, preserving each scene thumbnail/chrome.
    for y in range(DT1_OWNED[1], DT1_OWNED[3]):
        for x in range(DT1_OWNED[0], DT1_OWNED[2]):
            vals, counts = np.unique(stack[:, y, x, :], axis=0, return_counts=True)
            lum = vals[:, 0].astype(float) * 0.2126 + vals[:, 1].astype(float) * 0.7152 + vals[:, 2].astype(float) * 0.0722
            candidates = np.flatnonzero(lum == lum.min())
            k = int(candidates[np.argmax(counts[candidates])])
            out[y, x] = vals[k]
            support[y, x] = counts[k]
    # Outside the owned slab is unused in the donor.  Fill from the first source
    # solely to keep the donor image structurally complete.
    out[: DT1_OWNED[1]] = stack[0, : DT1_OWNED[1]]
    out[DT1_OWNED[3] :] = stack[0, DT1_OWNED[3] :]
    out[DT1_OWNED[1] : DT1_OWNED[3], : DT1_OWNED[0]] = stack[0, DT1_OWNED[1] : DT1_OWNED[3], : DT1_OWNED[0]]
    out[DT1_OWNED[1] : DT1_OWNED[3], DT1_OWNED[2] :] = stack[0, DT1_OWNED[1] : DT1_OWNED[3], DT1_OWNED[2] :]
    clean = Image.fromarray(out, "RGBA")
    clean.save(SOURCE_ROOT / "dt1_clean_title_slab.png")
    slab_support = support[DT1_OWNED[1] : DT1_OWNED[3], DT1_OWNED[0] : DT1_OWNED[2]]
    return clean, {
        "method": "same-coordinate darkest-observed tuple across 232 same-template state plates",
        "support_min": int(slab_support.min()),
        "support_p05": int(np.percentile(slab_support, 5)),
        "support_median": int(np.median(slab_support)),
    }


def fit_font(text: str, max_width: int, max_height: int, start: int) -> tuple[ImageFont.FreeTypeFont, tuple[int, int, int, int]]:
    for size in range(start, 9, -1):
        font = ImageFont.truetype(str(FONT), size=size)
        bbox = font.getbbox(text)
        if bbox[2] - bbox[0] <= max_width and bbox[3] - bbox[1] <= max_height:
            return font, bbox
    raise ValueError(f"text cannot fit: {text!r}")


def render_dt1(original: Image.Image, clean: Image.Image, text: str) -> tuple[Image.Image, dict[str, Any]]:
    out = original.copy().convert("RGBA")
    out.paste(clean.crop(DT1_OWNED), DT1_OWNED[:2])
    draw = ImageDraw.Draw(out)
    font, bbox = fit_font(text, DT1_OWNED[2] - DT1_OWNED[0] - 4, DT1_OWNED[3] - DT1_OWNED[1], 19)
    x = 123 - bbox[0]
    y = DT1_OWNED[1] + ((DT1_OWNED[3] - DT1_OWNED[1]) - (bbox[3] - bbox[1])) // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    return out, {"font_size": font.size, "text_bbox": [x + bbox[0], y + bbox[1], x + bbox[2], y + bbox[3]]}


def render_dt2(original: Image.Image, day: int, period: str) -> tuple[Image.Image, dict[str, Any]]:
    out = original.copy().convert("RGBA")
    # dt2 is a transparent text/icon overlay.  The text ends at x=212; all
    # status-flower families begin at x=235, so the protected icon is untouched.
    out.paste((0, 0, 0, 0), DT2_OWNED)
    label = f"{day}\uc77c\uc9f8 \u00b7 " + ("\ub0ae" if period == "day" else "\ubc24")
    draw = ImageDraw.Draw(out)
    font, bbox = fit_font(label, 100, 20, 20)
    x = 125 - bbox[0]
    y = 18 + (19 - (bbox[3] - bbox[1])) // 2 - bbox[1]
    draw.text((x, y), label, font=font, fill=(255, 255, 255, 255))
    if x + bbox[2] >= 230:
        raise ValueError(f"dt2 label approaches protected icon: {label}")
    return out, {"target": label, "font_size": font.size, "text_bbox": [x + bbox[0], y + bbox[1], x + bbox[2], y + bbox[3]]}


def build_one(root: Path, source: dict[str, Any], titles: dict[str, str], title_sources: dict[str, str], clean: Image.Image) -> dict[str, Any]:
    if root.exists():
        shutil.rmtree(root)
    work = root / "extracted"
    rendered = root / "rendered_png"
    encoded = root / "encoded_png"
    masks = root / "owned_masks"
    shutil.copytree(source["extracted"], work)
    rendered.mkdir(parents=True)
    encoded.mkdir(parents=True)
    masks.mkdir(parents=True)
    mask_paths = {}
    for key, rect in (("dt1", DT1_OWNED), ("dt2", DT2_OWNED)):
        mask = Image.new("RGB", (520, 80), "black")
        arr = np.array(mask)
        x1, y1, x2, y2 = rect
        arr[y1:y2, x1:x2] = 255
        mask = Image.fromarray(arr, "RGB")
        mask_paths[key] = masks / f"{key}_owned.png"
        mask.save(mask_paths[key])
    rows: list[dict[str, Any]] = []
    dt1 = sorted(work.glob("dt1_*.wcg"))
    dt2 = sorted(work.glob("dt2_*.wcg"))
    if set(p.stem[4:] for p in dt1) != set(titles):
        raise ValueError("dt1/title map coverage mismatch")
    for p in dt1:
        code = p.stem[4:]
        original_png = source["png"] / f"{p.stem}.png"
        original = Image.open(original_png).convert("RGBA")
        candidate, info = render_dt1(original, clean, titles[code])
        out_png = rendered / f"{p.stem}.png"
        candidate.save(out_png)
        before = np.array(original)
        after = np.array(candidate)
        outside = np.ones(before.shape[:2], dtype=bool)
        outside[DT1_OWNED[1] : DT1_OWNED[3], DT1_OWNED[0] : DT1_OWNED[2]] = False
        if not np.array_equal(before[outside], after[outside]):
            raise ValueError(f"dt1 outside-owned pixels changed: {p.name}")
        run(TOOL, "wcg-apply-patch", source["extracted"] / p.name, out_png, mask_paths["dt1"], p)
        encoded_png = encoded / out_png.name
        run(TOOL, "wcg2png", p, encoded_png)
        if not np.array_equal(np.array(Image.open(encoded_png).convert("RGBA"))[outside], after[outside]):
            # Direct original comparison is stronger here because dt1 background/chrome are opaque and lossless.
            raise ValueError(f"dt1 encoded outside-owned pixels changed: {p.name}")
        rows.append({"entry": p.name, "kind": "scene_title", "source_text": title_sources[code], "target_text": titles[code], **info})
    for p in dt2:
        suffix = p.stem[4:]
        family = int(suffix[0])
        day = int(suffix[1:3])
        period = "day" if suffix[3] == "1" else "night"
        if not (0 <= family <= 6 and 1 <= day <= 30 and suffix[3] in "12"):
            raise ValueError(f"unexpected dt2 code: {suffix}")
        original_png = source["png"] / f"{p.stem}.png"
        original = Image.open(original_png).convert("RGBA")
        candidate, info = render_dt2(original, day, period)
        out_png = rendered / f"{p.stem}.png"
        candidate.save(out_png)
        before = np.array(original)
        after = np.array(candidate)
        outside = np.ones(before.shape[:2], dtype=bool)
        outside[DT2_OWNED[1] : DT2_OWNED[3], DT2_OWNED[0] : DT2_OWNED[2]] = False
        if not np.array_equal(before[outside], after[outside]):
            raise ValueError(f"dt2 protected pixels changed: {p.name}")
        run(TOOL, "wcg-apply-patch", source["extracted"] / p.name, out_png, mask_paths["dt2"], p)
        encoded_png = encoded / out_png.name
        run(TOOL, "wcg2png", p, encoded_png)
        rows.append({"entry": p.name, "kind": "day_period", "icon_family": family, "day": day, "period": period, **info})
    out_archive = root / "grps.ko-save-metadata-v1.xfl"
    repack_report = root / "repack_report.json"
    run(sys.executable, XFL_TOOL, "repack", work, source["manifest"], out_archive, "--report", repack_report)
    print(f"built={root.name} entries={len(rows)} sha={sha256_path(out_archive)}", flush=True)
    return {"root": root, "work": work, "rendered": rendered, "encoded": encoded, "rows": rows, "archive": out_archive, "repack_report": repack_report}


def validate(source: dict[str, Any], a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    from xfl_tool import parse_archive
    if a["archive"].read_bytes() != b["archive"].read_bytes():
        raise ValueError("A/B archive rebuilds differ")
    src_arc = parse_archive(TRIAL_ARCHIVE)
    new_arc = parse_archive(a["archive"])
    if [e.name for e in src_arc.entries] != [e.name for e in new_arc.entries]:
        raise ValueError("archive entry order/name drift")
    expected = {e.name for e in src_arc.entries if e.name.startswith("dt1_") or e.name.startswith("dt2_")}
    changed: set[str] = set()
    with TRIAL_ARCHIVE.open("rb") as sf, a["archive"].open("rb") as nf:
        for se, ne in zip(src_arc.entries, new_arc.entries):
            sf.seek(se.absolute_offset); sb = sf.read(se.size)
            nf.seek(ne.absolute_offset); nb = nf.read(ne.size)
            if sb != nb:
                changed.add(se.name)
    if changed != expected:
        raise ValueError(f"strict delta mismatch: changed={len(changed)} expected={len(expected)}")
    # Reopen persisted A archive and prove WCG pixels equal the rendered PNGs.
    persisted = a["root"] / "persisted_reopen"
    if persisted.exists():
        shutil.rmtree(persisted)
    manifest = a["root"] / "persisted_manifest.json"
    run(sys.executable, XFL_TOOL, "extract", a["archive"], persisted, "--manifest", manifest)
    reopened_png = a["root"] / "persisted_png"
    reopened_png.mkdir()
    for i, name in enumerate(sorted(expected), 1):
        out = reopened_png / (Path(name).stem + ".png")
        run(TOOL, "wcg2png", persisted / name, out)
        target = a["encoded"] / out.name
        persisted_pixels = np.array(Image.open(out).convert("RGBA"))
        encoded_pixels = np.array(Image.open(target).convert("RGBA"))
        if not np.array_equal(persisted_pixels, encoded_pixels):
            raise ValueError(f"persisted WCG pixel mismatch: {name}")
        # Compare protected pixels against a source WCG saved through the exact
        # same WCG codec.  This removes format-inherent quantization from the
        # delta while proving the icon/thumbnail/chrome contract.
        control_wcg = a["root"] / "control_roundtrip" / name
        control_png = a["root"] / "control_png" / out.name
        control_wcg.parent.mkdir(exist_ok=True)
        control_png.parent.mkdir(exist_ok=True)
        run(TOOL, "wcg-roundtrip-pixels", source["extracted"] / name, control_wcg)
        run(TOOL, "wcg2png", control_wcg, control_png)
        control_pixels = np.array(Image.open(control_png).convert("RGBA"))
        rect = DT1_OWNED if name.startswith("dt1_") else DT2_OWNED
        x1, y1, x2, y2 = rect
        outside = np.ones(persisted_pixels.shape[:2], dtype=bool)
        outside[y1:y2, x1:x2] = False
        if not np.array_equal(persisted_pixels[outside], control_pixels[outside]):
            raise ValueError(f"persisted protected pixels changed: {name}")
        rendered_pixels = np.array(Image.open(a["rendered"] / out.name).convert("RGBA")).astype(int)
        max_error = np.abs(persisted_pixels.astype(int) - rendered_pixels).max(axis=(0, 1))
        if max_error[3] != 0 or max(max_error[:3]) > 1:
            raise ValueError(f"persisted target render drift: {name}: {max_error.tolist()}")
        if i % 100 == 0:
            print(f"persisted_reopen={i}/{len(expected)}", flush=True)
    return {
        "status": "PASS",
        "source_entry_count": len(src_arc.entries),
        "changed_entry_count": len(changed),
        "changed_entries_exact_allowlist": True,
        "non_target_entries_byte_identical": True,
        "entry_order_and_names_identical": True,
        "a_b_byte_identical": True,
        "persisted_wcg_pixel_reopen_exact": True,
        "protected_pixels_exact_against_same_codec_source_roundtrip": True,
        "rendered_target_rgb_error_max": 1,
        "rendered_target_alpha_exact": True,
        "output_sha256": sha256_path(a["archive"]),
        "output_size": a["archive"].stat().st_size,
    }


def make_contact(source: dict[str, Any], built: dict[str, Any]) -> None:
    selected = ["dt1_1101", "dt1_1102", "dt1_1110", "dt1_1701", "dt1_3300", "dt2_0011", "dt2_0012", "dt2_1011", "dt2_6012"]
    rows = []
    for stem in selected:
        for label, root in (("SOURCE", source["png"]), ("KOREAN", built["rendered"])):
            im = Image.open(root / f"{stem}.png").convert("RGBA")
            bg = Image.new("RGBA", im.size, (36, 36, 36, 255)); bg.alpha_composite(im)
            rows.append((stem, label, bg.convert("RGB")))
    sheet = Image.new("RGB", (1040, len(rows) * 90), (36, 36, 36))
    font = ImageFont.truetype(str(FONT), 18)
    for i, (stem, label, im) in enumerate(rows):
        sheet.paste(im.resize((1040, 160), Image.Resampling.NEAREST).crop((0, 35, 1040, 115)), (0, i * 90))
        ImageDraw.Draw(sheet).text((5, i * 90 + 2), f"{stem} {label}", font=font, fill=(255, 64, 64))
    sheet.save(CONTACT)


def main() -> None:
    for required in (TRIAL_ARCHIVE, TOOL, XFL_TOOL, FONT, TITLE_MAP):
        if not required.exists():
            raise FileNotFoundError(required)
    sys.path.insert(0, str(PROJECT / "adapter"))
    titles, title_sources = frozen_title_map()
    source = prepare_source()
    dt1_paths = sorted(source["extracted"].glob("dt1_*.wcg"))
    clean, clean_info = build_dt1_clean(source["png"], dt1_paths)
    a = build_one(ROOT_A, source, titles, title_sources, clean)
    b = build_one(ROOT_B, source, titles, title_sources, clean)
    verification = validate(source, a, b)
    make_contact(source, a)
    report = {
        "schema": "fairytale-requiem-grps-save-metadata-korean-v1",
        "status": "PASS",
        "delivery_state": "staging-only-game-running-not-installed",
        "source_archive": {"path": str(TRIAL_ARCHIVE), "sha256": source["archive_sha256"], "size": source["archive_size"]},
        "font": {"path": str(FONT), "sha256": sha256_path(FONT)},
        "translation_map": {"path": str(TITLE_MAP), "sha256": sha256_path(TITLE_MAP), "dt1_title_count": len(titles)},
        "owned_regions": {"dt1": list(DT1_OWNED), "dt2": list(DT2_OWNED)},
        "clean_title_slab": clean_info,
        "counts": {"dt1": 232, "dt2": 420, "total": 652},
        "build_a": {"archive": str(a["archive"]), "sha256": sha256_path(a["archive"]), "rows": a["rows"]},
        "build_b": {"archive": str(b["archive"]), "sha256": sha256_path(b["archive"])},
        "verification": verification,
        "contact_sheet": {"path": str(CONTACT), "sha256": sha256_path(CONTACT)},
    }
    AUDIT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "audit": str(AUDIT), "audit_sha256": sha256_path(AUDIT), **verification}, ensure_ascii=True))


if __name__ == "__main__":
    main()