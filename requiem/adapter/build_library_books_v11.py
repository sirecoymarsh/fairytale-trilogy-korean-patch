from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable
import hashlib
import json

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
SOURCE_ROOT = PROJECT / "staging" / "ui_other_banks_audit_v1" / "exported_png" / "grpo_lib"
OUT = PROJECT / "staging" / "library_books_rebuild_v11"
SCALE = 4


@dataclass(frozen=True)
class BookStyle:
    normal: str
    selected: str
    title: str
    chars: str
    design: str
    roi: tuple[int, int, int, int]
    condition: str
    dilation: int
    inpaint_radius: int
    font: str
    font_index: int
    font_size: int
    font_variation: str | None
    centers_y: tuple[float, ...]
    center_x: float
    slope: float
    color: tuple[int, int, int]
    stroke_width: int = 0
    stroke_color: tuple[int, int, int] | None = None
    shadow_offset: tuple[float, float] = (0.0, 0.0)
    shadow_color: tuple[int, int, int] | None = None
    shadow_blur: float = 0.0
    shadow_strength: float = 0.0
    glyph_blur: float = 0.0
    angles: tuple[float, ...] = ()


STYLES = (
    BookStyle(
        "0012", "0112", "헨젤과 그레텔", "헨젤과그레텔",
        "노란 책등의 굵고 높은 흑갈색 둥근 활자",
        (56, 32, 100, 410), "dark_yellow", 4, 3,
        r"C:\Windows\Fonts\malgunbd.ttf", 0, 30, None,
        (62, 120, 178, 256, 314, 372), 70.5, 0.017,
        (46, 24, 27), glyph_blur=0.10,
    ),
    BookStyle(
        "0013", "0113", "백조의 호수", "백조의호수",
        "갈색 고서 위의 작고 가는 금빛 붓글씨",
        (54, 108, 96, 289), "gold", 5, 3,
        r"C:\Windows\Fonts\batang.ttc", 2, 24, None,
        (128, 158, 188, 228, 258), 72.0, 0.017,
        (222, 164, 78),
        shadow_offset=(-0.6, -0.5), shadow_color=(116, 62, 30), shadow_blur=0.45, shadow_strength=0.35,
        glyph_blur=0.18, angles=(-1.0, 0.7, -0.5, 0.8, -0.7),
    ),
    BookStyle(
        "0014", "0114", "백조의 호수", "백조의호수",
        "청색 고서 위의 작고 가는 옅은 청백색 붓글씨",
        (53, 108, 97, 289), "pale_blue", 5, 3,
        r"C:\Windows\Fonts\batang.ttc", 2, 24, None,
        (128, 158, 188, 228, 258), 72.0, 0.017,
        (176, 205, 229),
        shadow_offset=(-0.5, -0.4), shadow_color=(46, 67, 110), shadow_blur=0.40, shadow_strength=0.32,
        glyph_blur=0.18, angles=(-1.0, 0.7, -0.5, 0.8, -0.7),
    ),
    BookStyle(
        "0015", "0115", "라푼젤", "라푼젤",
        "연두 책등을 따라 흐르는 부드러운 흰 손글씨",
        (50, 74, 101, 296), "light", 5, 3,
        r"C:\Windows\Fonts\gulim.ttc", 0, 34, None,
        (120, 185, 250), 66.0, 0.050,
        (236, 235, 202), stroke_width=1, stroke_color=(224, 225, 190),
        shadow_offset=(-0.8, -0.6), shadow_color=(105, 116, 62), shadow_blur=0.65, shadow_strength=0.34,
        glyph_blur=0.32, angles=(-2.0, 1.5, -1.0),
    ),
    BookStyle(
        "0016", "0116", "눈의 여왕", "눈의여왕",
        "기울어진 청록 책등의 단단하고 각진 짙은 남색 글자",
        (39, 105, 94, 263), "navy", 5, 3,
        r"C:\Windows\Fonts\NotoSerifKR-VF.ttf", 0, 29, "Black",
        (130, 165, 215, 250), 58.5, 0.105,
        (18, 43, 74), glyph_blur=0.10,
    ),
    BookStyle(
        "0017", "0117", "피터 팬", "피터팬",
        "붉은 라벨과 별 장식 사이의 노란 팝 활자",
        (59, 110, 94, 285), "yellow", 4, 3,
        r"C:\Windows\Fonts\gulim.ttc", 0, 31, None,
        (145, 195, 245), 76.0, 0.0,
        (247, 206, 31), stroke_width=1, stroke_color=(190, 76, 29),
        shadow_offset=(-0.8, -0.7), shadow_color=(132, 37, 33), shadow_blur=0.35, shadow_strength=0.50,
        glyph_blur=0.12,
    ),
    BookStyle(
        "0018", "0118", "오즈의 마법사", "오즈의마법사",
        "황갈색 고서 띠 위의 가늘고 긴 고전풍 먹갈색 활자",
        (54, 68, 98, 317), "dark_tan", 5, 3,
        r"C:\Windows\Fonts\malgunbd.ttf", 0, 27, None,
        (95, 135, 175, 220, 260, 300), 74.5, 0.0,
        (57, 37, 35), glyph_blur=0.10,
    ),
)


COHERENT_DONORS = {
    "0012": (30, 410, 456, 565, 25.0),
    "0013": (108, 290, 350, 560, 24.5),
    "0014": (108, 290, 350, 560, 24.5),
    "0015": (80, 295, 505, 560, 24.0),
    "0016": (105, 265, 300, 550, 24.0),
    "0018": (76, 345, 360, 560, 25.5),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_rgba(path: Path) -> np.ndarray:
    return np.array(Image.open(path).convert("RGBA"))


def source_ink_mask(source: np.ndarray, style: BookStyle) -> np.ndarray:
    x0, y0, x1, y1 = style.roi
    rgb = source[..., :3].astype(np.int16)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    gray = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2GRAY)
    roi = np.zeros(gray.shape, bool)
    roi[y0:y1, x0:x1] = True
    if style.condition == "dark_yellow":
        seed = (gray < 178) & (r < 185)
    elif style.condition == "dark_tan":
        seed = gray < 118
    elif style.condition == "gold":
        seed = (r > 145) & (g > 112) & ((r - b) > 55) & ((g - b) > 28)
    elif style.condition == "pale_blue":
        seed = (r > 85) & (g > 105) & (b > 128)
    elif style.condition == "light":
        seed = (r > 128) & (g > 138) & (b > 105) & (gray > 138)
    elif style.condition == "navy":
        seed = (r < 75) & (g < 105) & (b < 125) & (gray < 105)
    elif style.condition == "yellow":
        seed = (r > 155) & (g > 95) & (b < 110) & ((r - b) > 80)
    else:
        raise ValueError(style.condition)
    mask = (seed & roi & (source[..., 3] > 0)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    mask = cv2.dilate(mask, np.ones((style.dilation, style.dilation), np.uint8), 1)
    mask[~roi] = 0
    return mask


def clean_source(
    source: np.ndarray, glyph_mask: np.ndarray, style: BookStyle
) -> tuple[np.ndarray, np.ndarray]:
    donor_spec = COHERENT_DONORS.get(style.normal)
    if donor_spec is None:
        bgr = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2BGR)
        restored = cv2.inpaint(bgr, glyph_mask, style.inpaint_radius, cv2.INPAINT_TELEA)
        clean = source.copy()
        owned = glyph_mask > 0
        clean[owned, :3] = cv2.cvtColor(restored, cv2.COLOR_BGR2RGB)[owned]
        clean[..., 3] = source[..., 3]
        return clean, glyph_mask

    target_y0, target_y1, donor_y0, donor_y1, half_width = donor_spec
    height, width = glyph_mask.shape
    yy, xx = np.indices((height, width), dtype=np.float32)
    target_center = style.center_x + style.slope * (yy - style.centers_y[0])
    donor_y = donor_y0 + (yy - target_y0) * (donor_y1 - donor_y0) / max(1, target_y1 - target_y0)
    donor_center = style.center_x + style.slope * (donor_y - style.centers_y[0])
    donor_x = xx - target_center + donor_center
    source_rgb = source[..., :3]
    remapped = cv2.remap(
        source_rgb, donor_x.astype(np.float32), donor_y.astype(np.float32),
        interpolation=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT_101,
    ).astype(np.float32)
    face = (yy >= target_y0) & (yy < target_y1) & (np.abs(xx - target_center) <= half_width) & (source[...,3] > 0)

    # Match the single donor surface to the untouched left/right fibres on every row.
    edge = face & (np.abs(xx - target_center) >= half_width - 4.0) & (glyph_mask == 0)
    row_delta = np.zeros((height, 3), np.float32)
    for y in range(target_y0, target_y1):
        samples = edge[y]
        if np.count_nonzero(samples) >= 2:
            row_delta[y] = np.median(source_rgb[y, samples].astype(np.float32) - remapped[y, samples], axis=0)
    row_delta = cv2.GaussianBlur(row_delta[:,None,:], (1,0), sigmaX=0, sigmaY=7.0)[:,0,:]
    remapped += row_delta[:,None,:]
    remapped = np.clip(remapped, 0, 255)

    distance = cv2.distanceTransform(face.astype(np.uint8), cv2.DIST_L2, 3)
    blend = np.clip(distance / 3.0, 0.0, 1.0)[...,None]
    clean = source.copy().astype(np.float32)
    clean[...,:3] = source_rgb.astype(np.float32) * (1.0 - blend) + remapped * blend
    clean[...,3] = source[...,3]
    clean = np.clip(clean, 0, 255).astype(np.uint8)
    clean[~face] = source[~face]
    return clean, face.astype(np.uint8) * 255


def make_font(style: BookStyle) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(style.font, style.font_size * SCALE, index=style.font_index)
    if style.font_variation:
        try:
            font.set_variation_by_name(style.font_variation)
        except Exception:
            pass
    return font


def render_glyph_alpha(size: tuple[int, int], style: BookStyle) -> Image.Image:
    width, height = size
    canvas = Image.new("L", (width * SCALE, height * SCALE), 0)
    font = make_font(style)
    for index, (char, center_y) in enumerate(zip(style.chars, style.centers_y)):
        angle = style.angles[index] if index < len(style.angles) else 0.0
        temp_size = int((style.font_size + 20) * SCALE)
        temp = Image.new("L", (temp_size, temp_size), 0)
        draw = ImageDraw.Draw(temp)
        stroke = style.stroke_width * SCALE
        bbox = draw.textbbox((0, 0), char, font=font, stroke_width=stroke)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            ((temp_size - tw) / 2 - bbox[0], (temp_size - th) / 2 - bbox[1]),
            char,
            font=font,
            fill=255,
            stroke_width=stroke,
            stroke_fill=255,
        )
        if angle:
            temp = temp.rotate(angle, Image.Resampling.BICUBIC, expand=False)
        center_x = style.center_x + style.slope * (center_y - style.centers_y[0])
        x = int(center_x * SCALE - temp_size / 2)
        y = int(center_y * SCALE - temp_size / 2)
        canvas.paste(ImageChops.lighter(canvas.crop((x, y, x + temp_size, y + temp_size)), temp), (x, y))
    glyph = canvas.resize((width, height), Image.Resampling.LANCZOS)
    if style.glyph_blur:
        glyph = glyph.filter(ImageFilter.GaussianBlur(style.glyph_blur))
    return glyph


def text_layer(size: tuple[int, int], style: BookStyle) -> Image.Image:
    width, height = size
    glyph = render_glyph_alpha(size, style)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    if style.shadow_color and style.shadow_strength > 0:
        shadow_alpha = glyph.filter(ImageFilter.GaussianBlur(style.shadow_blur))
        dx, dy = style.shadow_offset
        shadow_alpha = shadow_alpha.transform(
            size,
            Image.Transform.AFFINE,
            (1, 0, -dx, 0, 1, -dy),
            resample=Image.Resampling.BICUBIC,
        ).point(lambda value: int(value * style.shadow_strength))
        shadow = Image.new("RGBA", size, (*style.shadow_color, 0))
        shadow.putalpha(shadow_alpha)
        layer.alpha_composite(shadow)
    if style.stroke_width and style.stroke_color:
        expanded = glyph.filter(ImageFilter.MaxFilter(style.stroke_width * 2 + 1))
        stroke_only = np.maximum(np.array(expanded, np.int16) - np.array(glyph, np.int16), 0).astype(np.uint8)
        stroke = Image.new("RGBA", size, (*style.stroke_color, 0))
        stroke.putalpha(Image.fromarray(stroke_only, "L"))
        layer.alpha_composite(stroke)
    core = Image.new("RGBA", size, (*style.color, 0))
    core.putalpha(glyph)
    layer.alpha_composite(core)
    return layer


def fit_hover_transform(normal: np.ndarray, selected: np.ndarray) -> list[tuple[float, float]]:
    opaque = (normal[..., 3] > 0) & (selected[..., 3] > 0)
    coefficients = []
    for channel in range(3):
        x = normal[..., channel][opaque].astype(np.float64)
        y = selected[..., channel][opaque].astype(np.float64)
        a, b = np.polyfit(x, y, 1)
        coefficients.append((float(a), float(b)))
    return coefficients


def transform_state(image: np.ndarray, coefficients: list[tuple[float, float]], alpha: np.ndarray) -> np.ndarray:
    result = image.copy().astype(np.float32)
    for channel, (a, b) in enumerate(coefficients):
        result[..., channel] = result[..., channel] * a + b
    result = np.clip(result, 0, 255).astype(np.uint8)
    result[..., 3] = alpha
    return result


def persist_state(
    style: BookStyle,
    stem: str,
    state: str,
    source: np.ndarray,
    clean: np.ndarray,
    candidate: np.ndarray,
    old_mask: np.ndarray,
    target_mask: np.ndarray,
) -> dict:
    folder = OUT / style.normal / stem
    folder.mkdir(parents=True, exist_ok=True)
    paths = {
        "source": folder / "source.png",
        "clean": folder / "clean.png",
        "candidate": folder / "candidate.png",
        "old_text_mask": folder / "old_text_mask.png",
        "target_text_mask": folder / "target_text_mask.png",
    }
    Image.fromarray(source, "RGBA").save(paths["source"])
    Image.fromarray(clean, "RGBA").save(paths["clean"])
    Image.fromarray(candidate, "RGBA").save(paths["candidate"])
    Image.fromarray(old_mask, "L").save(paths["old_text_mask"])
    Image.fromarray(target_mask, "L").save(paths["target_text_mask"])
    owned = (old_mask > 0) | (target_mask > 0)
    clean_changed = np.any(source != clean, axis=2)
    candidate_changed = np.any(source != candidate, axis=2)
    validation = {
        "dimensions": [int(source.shape[1]), int(source.shape[0])],
        "alpha_geometry_byte_exact": bool(
            np.array_equal(source[..., 3], clean[..., 3])
            and np.array_equal(source[..., 3], candidate[..., 3])
        ),
        "clean_changes_only_source_glyph_mask": bool(np.all(~clean_changed | (old_mask > 0))),
        "candidate_protected_pixels_byte_exact": bool(np.array_equal(source[~owned], candidate[~owned])),
        "old_text_mask_pixels": int(np.count_nonzero(old_mask)),
        "target_text_mask_pixels": int(np.count_nonzero(target_mask)),
        "changed_pixels": int(np.count_nonzero(candidate_changed)),
    }
    return {
        "book_id": style.normal,
        "stem": stem,
        "state": state,
        "title": style.title,
        "design": style.design,
        "files": {key: str(value) for key, value in paths.items()},
        "sha256": {key: sha256(value) for key, value in paths.items()},
        "validation": validation,
    }


def build_book(style: BookStyle) -> list[dict]:
    normal_source = load_rgba(SOURCE_ROOT / f"{style.normal}.png")
    selected_source = load_rgba(SOURCE_ROOT / f"{style.selected}.png")
    old_mask = source_ink_mask(normal_source, style)
    normal_clean, old_mask = clean_source(normal_source, old_mask, style)
    layer = text_layer((normal_source.shape[1], normal_source.shape[0]), style)
    normal_candidate_image = Image.fromarray(normal_clean, "RGBA")
    normal_candidate_image.alpha_composite(layer)
    normal_candidate = np.array(normal_candidate_image)
    target_mask = (np.array(layer.getchannel("A")) > 0).astype(np.uint8) * 255

    coefficients = fit_hover_transform(normal_source, selected_source)
    transformed_clean = transform_state(normal_clean, coefficients, selected_source[..., 3])
    transformed_candidate = transform_state(normal_candidate, coefficients, selected_source[..., 3])
    owned = (old_mask > 0) | (target_mask > 0)
    selected_clean = selected_source.copy()
    selected_clean[old_mask > 0] = transformed_clean[old_mask > 0]
    selected_candidate = selected_source.copy()
    selected_candidate[owned] = transformed_candidate[owned]

    return [
        persist_state(style, style.normal, "normal", normal_source, normal_clean, normal_candidate, old_mask, target_mask),
        persist_state(style, style.selected, "hover_or_selected", selected_source, selected_clean, selected_candidate, old_mask, target_mask),
    ]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for style in STYLES:
        records.extend(build_book(style))
    manifest = {
        "schema": "fairytale-requiem-library-books-v11",
        "status": "USER_REVIEW_REQUIRED_NOT_INSTALLED",
        "scope": "BOOK_SPINES_ONLY_EXCLUDES_NEWSPAPER_AND_STORY_PAGES",
        "accepted_reference": str(PROJECT / "staging" / "library_per_book_rebuild_v10" / "alice" / "manifest.json"),
        "book_count": len(STYLES),
        "state_count": len(records),
        "rules": {
            "book_specific_typography": True,
            "source_glyph_removed_before_typesetting": True,
            "no_rectangular_backing_plate": True,
            "protected_pixels_exact": True,
            "normal_selected_pair": True,
            "installed": False,
        },
        "records": records,
    }
    path = OUT / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(path), "book_count": len(STYLES), "state_count": len(records)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
