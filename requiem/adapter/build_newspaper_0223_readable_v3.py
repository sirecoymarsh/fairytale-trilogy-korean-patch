from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2
import hashlib
import json
import numpy as np
import re

ROOT = Path(__file__).resolve().parent
INP = ROOT / 'review_input'
OUT = ROOT / 'work' / 'library_newspaper_0223_readable_v3'
FONT = Path(r'C:\Windows\Fonts\NotoSerifKR-VF.ttf')
SOURCE = INP / '0223_original.png'
BLANK = INP / 'storybook-authored-clean.png'
TRANS = ROOT / 'work' / 'grpo_lib_korean_pages_v3.json'
SCALE = 4


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def poly_mask(size: tuple[int, int], points: list[tuple[float, float]], scale: int = SCALE) -> Image.Image:
    w, h = size
    hi = Image.new('L', (w * scale, h * scale), 0)
    d = ImageDraw.Draw(hi)
    d.polygon([(round(x * scale), round(y * scale)) for x, y in points], fill=255)
    return hi.resize((w, h), Image.Resampling.LANCZOS)


def fit_blank_to_source(source: np.ndarray, blank: np.ndarray, exclusion: np.ndarray) -> np.ndarray:
    h, w = source.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    xn = (xx / max(w - 1, 1)) * 2.0 - 1.0
    yn = (yy / max(h - 1, 1)) * 2.0 - 1.0
    b = blank[..., :3].astype(np.float64) / 255.0
    s = source[..., :3].astype(np.float64) / 255.0
    feats = np.stack([
        b[..., 0], b[..., 1], b[..., 2],
        xn, yn, xn * yn, xn * xn, yn * yn,
        np.ones_like(xn),
    ], axis=-1)
    train = ~exclusion
    train[60:535, 265:860] = False
    train &= source[..., 3] > 0
    ys, xs = np.where(train)
    stride = max(1, len(ys) // 120000)
    ys, xs = ys[::stride], xs[::stride]
    X = feats[ys, xs]
    pred = np.empty_like(s)
    for c in range(3):
        coef, *_ = np.linalg.lstsq(X, s[ys, xs, c], rcond=None)
        pred[..., c] = np.tensordot(feats, coef, axes=([2], [0]))
    out = blank.copy()
    out[..., :3] = np.clip(pred * 255.0, 0, 255).astype(np.uint8)
    return out


def make_paper_texture(size: tuple[int, int], base: int, seed: int) -> Image.Image:
    w, h = size
    rng = np.random.default_rng(seed)
    fine = rng.normal(0, 2.7, (h, w)).astype(np.float32)
    coarse = rng.normal(0, 1.0, (h, w)).astype(np.float32)
    coarse = cv2.GaussianBlur(coarse, (0, 0), 5.0)
    yy = np.linspace(-1.0, 1.0, h, dtype=np.float32)[:, None]
    xx = np.linspace(-1.0, 1.0, w, dtype=np.float32)[None, :]
    tone = base + 2.0 * yy - 1.1 * xx + fine + 4.0 * coarse
    rgb = np.clip(tone, 0, 255).astype(np.uint8)
    arr = np.dstack([rgb, rgb, rgb, np.full_like(rgb, 255)])
    return Image.fromarray(arr, 'RGBA')


def font_with_weight(path: Path, size: int, weight_name: str | None = None) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(path), size)
    if weight_name:
        try:
            f.set_variation_by_name(weight_name)
        except Exception:
            pass
    return f


def normalize_vertical(text: str) -> str:
    paragraphs = [re.sub(r'\s+', '', p) for p in text.splitlines() if p.strip()]
    return '　'.join(paragraphs)


def draw_vertical_text(
    layer: Image.Image,
    text: str,
    *,
    first_x: float,
    top: float,
    bottom: float,
    col_pitch: float,
    advance: float,
    font_size: int,
    fill: tuple[int, int, int, int],
    max_cols: int,
    stroke_width: int = 0,
    stroke_fill: tuple[int, int, int, int] | None = None,
    weight: str | None = None,
) -> dict:
    draw = ImageDraw.Draw(layer)
    font = font_with_weight(FONT, font_size * SCALE, weight)
    chars = list(normalize_vertical(text))
    idx = 0
    rows = int((bottom - top) // advance)
    for col in range(max_cols):
        x = (first_x - col * col_pitch) * SCALE
        for row in range(rows):
            if idx >= len(chars):
                return {'chars': len(chars), 'placed': idx, 'remaining': 0, 'rows': rows, 'cols_used': col + 1}
            ch = chars[idx]
            idx += 1
            y = (top + row * advance) * SCALE
            bbox = draw.textbbox((0, 0), ch, font=font, stroke_width=stroke_width * SCALE)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            px = x - tw / 2 - bbox[0]
            py = y + (advance * SCALE - th) / 2 - bbox[1]
            draw.text(
                (px, py), ch, font=font, fill=fill,
                stroke_width=stroke_width * SCALE,
                stroke_fill=stroke_fill or fill,
            )
    return {'chars': len(chars), 'placed': idx, 'remaining': len(chars) - idx, 'rows': rows, 'cols_used': max_cols}


def draw_vertical_segment(layer: Image.Image, text: str, x: float, top: float, bottom: float, size: int, advance: float) -> dict:
    return draw_vertical_text(
        layer, text, first_x=x, top=top, bottom=bottom,
        col_pitch=0, advance=advance, font_size=size,
        fill=(25, 25, 24, 255), max_cols=1,
        stroke_width=0, weight='Black',
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for sub in ['source', 'clean', 'candidate', 'owned_mask', 'paper_mask', 'evidence']:
        (OUT / sub).mkdir(exist_ok=True)

    source_im = Image.open(SOURCE).convert('RGBA')
    blank_im = Image.open(BLANK).convert('RGBA')
    w, h = source_im.size
    if (w, h) != (1126, 600) or blank_im.size != source_im.size:
        raise SystemExit(f'unexpected dimensions: source={source_im.size}, blank={blank_im.size}')

    # Measured directly from the authored clipping; both pieces retain the slight clockwise skew.
    front_points = [(300.0, 70.0), (824.0, 74.0), (824.0, 301.0), (302.0, 296.0)]
    back_points = [(346.0, 289.0), (824.0, 293.0), (824.0, 511.0), (346.0, 519.0)]
    front_mask = poly_mask((w, h), front_points)
    back_mask = poly_mask((w, h), back_points)
    union_arr = np.maximum(np.array(front_mask), np.array(back_mask)).astype(np.uint8)
    union_mask = Image.fromarray(union_arr, 'L')

    # Owned area includes the original clipping and its complete shadow. Outside it remains byte-identical.
    owned_core = cv2.dilate((union_arr > 8).astype(np.uint8) * 255, np.ones((31, 31), np.uint8))
    owned_soft = cv2.GaussianBlur(owned_core, (0, 0), 4.0)
    owned_arr = (owned_soft > 1).astype(np.uint8) * 255
    owned_mask = Image.fromarray(owned_arr, 'L')

    source = np.array(source_im)
    blank = np.array(blank_im)
    corrected_blank = fit_blank_to_source(source, blank, owned_arr > 0)
    clean = source.copy().astype(np.float32)
    a = (owned_soft.astype(np.float32) / 255.0)[..., None]
    clean[..., :3] = source[..., :3] * (1.0 - a) + corrected_blank[..., :3] * a
    clean[..., 3] = source[..., 3]
    clean = np.clip(clean, 0, 255).astype(np.uint8)
    clean[owned_arr == 0] = source[owned_arr == 0]
    clean_im = Image.fromarray(clean, 'RGBA')

    candidate = clean_im.copy()
    shadow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    shadow_alpha = union_mask.filter(ImageFilter.GaussianBlur(4.2))
    shadow_alpha = shadow_alpha.transform((w, h), Image.Transform.AFFINE, (1, 0, -2, 0, 1, -4), resample=Image.Resampling.BILINEAR)
    shadow_alpha = shadow_alpha.point(lambda v: int(v * 0.38))
    shadow.putalpha(shadow_alpha)
    shadow_color = Image.new('RGBA', (w, h), (50, 46, 39, 255))
    shadow_color.putalpha(shadow_alpha)
    candidate.alpha_composite(shadow_color)

    back_tex = make_paper_texture((w, h), 213, 22301)
    back_tex.putalpha(back_mask)
    candidate.alpha_composite(back_tex)
    front_tex = make_paper_texture((w, h), 208, 22302)
    front_tex.putalpha(front_mask)
    candidate.alpha_composite(front_tex)

    # Rebuild the two authored clipping outlines instead of laying down rectangular label plates.
    outline = Image.new('RGBA', (w * SCALE, h * SCALE), (0, 0, 0, 0))
    od = ImageDraw.Draw(outline)
    od.line([(int(x*SCALE), int(y*SCALE)) for x, y in back_points + [back_points[0]]], fill=(72, 72, 69, 205), width=4)
    od.line([(int(x*SCALE), int(y*SCALE)) for x, y in front_points + [front_points[0]]], fill=(70, 70, 67, 220), width=4)
    outline = outline.resize((w, h), Image.Resampling.LANCZOS)
    candidate.alpha_composite(outline)

    trans = json.loads(TRANS.read_text(encoding='utf-8'))['pages']['0223']
    l_lines = [line for line in trans['L'].splitlines() if line.strip()]
    body_left = '\n'.join(l_lines[1:])
    body_right = trans['R']

    text_layer = Image.new('RGBA', (w * SCALE, h * SCALE), (0, 0, 0, 0))
    td = ImageDraw.Draw(text_layer)
    title_font = font_with_weight(FONT, 21 * SCALE, 'Black')
    body_font = font_with_weight(FONT, 14 * SCALE, 'Medium')
    title = '“낙원” 의사 3명 중태… 범인은 원숭이!?'

    def wrap_pixels(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
        wrapped: list[str] = []
        for paragraph in [x.strip() for x in text.splitlines() if x.strip()]:
            line = ''
            for ch in paragraph:
                trial = line + ch
                if not line or td.textlength(trial, font=font) <= max_width:
                    line = trial
                else:
                    wrapped.append(line.rstrip())
                    line = ch.lstrip()
            if line:
                wrapped.append(line.rstrip())
        return wrapped

    title_xy = (316 * SCALE, 80 * SCALE)
    td.text(title_xy, title, font=title_font, fill=(24, 24, 23, 255))
    title_width = float(td.textlength(title, font=title_font) / SCALE)
    if title_width > 492:
        raise SystemExit(f'title overflow: {title_width}')
    td.line([(316*SCALE, 113*SCALE), (808*SCALE, 113*SCALE)], fill=(72,72,69,210), width=2*SCALE)

    top_lines = wrap_pixels(body_left, body_font, 490 * SCALE)
    bottom_lines = wrap_pixels(body_right, body_font, 446 * SCALE)
    top_x, top_y, top_step = 316*SCALE, 122*SCALE, 18*SCALE
    bottom_x, bottom_y, bottom_step = 359*SCALE, 312*SCALE, 19*SCALE
    if top_y + len(top_lines)*top_step > 289*SCALE:
        raise SystemExit(f'top article overflow: {len(top_lines)} lines')
    if bottom_y + len(bottom_lines)*bottom_step > 509*SCALE:
        raise SystemExit(f'bottom article overflow: {len(bottom_lines)} lines')
    for i,line in enumerate(top_lines):
        td.text((top_x, top_y+i*top_step), line, font=body_font, fill=(35,35,33,255))
    for i,line in enumerate(bottom_lines):
        td.text((bottom_x, bottom_y+i*bottom_step), line, font=body_font, fill=(38,38,36,255))

    title_stat = {'text': title, 'x': 316, 'y': 80, 'width': title_width, 'remaining': 0}
    top_body = {'lines': len(top_lines), 'placed_chars': sum(len(x) for x in top_lines), 'remaining': 0, 'direction': 'left-to-right horizontal'}
    bottom_body = {'lines': len(bottom_lines), 'placed_chars': sum(len(x) for x in bottom_lines), 'remaining': 0, 'direction': 'left-to-right horizontal'}

    text_layer = text_layer.resize((w, h), Image.Resampling.LANCZOS)
    candidate.alpha_composite(text_layer)
    candidate_arr = np.array(candidate)
    candidate_arr[owned_arr == 0] = source[owned_arr == 0]
    candidate = Image.fromarray(candidate_arr, 'RGBA')

    paths = {
        'source': OUT / 'source' / '0223.png',
        'clean': OUT / 'clean' / '0223.png',
        'candidate': OUT / 'candidate' / '0223.png',
        'owned_mask': OUT / 'owned_mask' / '0223.png',
        'paper_mask': OUT / 'paper_mask' / '0223.png',
    }
    source_im.save(paths['source'])
    clean_im.save(paths['clean'])
    candidate.save(paths['candidate'])
    owned_mask.save(paths['owned_mask'])
    union_mask.save(paths['paper_mask'])

    # Native-scale evidence: source / rejected / clean plate / faithful v2.
    rejected = Image.open(INP / '0223_rejected.png').convert('RGBA')
    panel_w = w
    evidence = Image.new('RGB', (panel_w * 2, h * 2), 'white')
    for idx, im in enumerate([source_im, rejected, clean_im, candidate]):
        x = (idx % 2) * panel_w
        y = (idx // 2) * h
        evidence.paste(im.convert('RGB'), (x, y))
    evidence.save(OUT / 'evidence' / '0223_source_rejected_clean_v2.jpg', quality=90, optimize=True)

    source_np = np.array(source_im)
    candidate_np = np.array(candidate)
    outside = owned_arr == 0
    outside_exact = bool(np.array_equal(source_np[outside], candidate_np[outside]))
    source_dark_equal_on_paper = np.all(source_np[..., :3] == np.array(candidate)[..., :3], axis=2) & (np.mean(source_np[..., :3], axis=2) < 120) & (union_arr > 220)
    old_dark_exact_pixels = int(source_dark_equal_on_paper.sum())
    paper_bbox = list(Image.fromarray((union_arr > 8).astype(np.uint8) * 255).getbbox())
    clean_source_exact_ratio = float(np.mean(np.all(source_np[union_arr > 220] == np.array(clean_im)[union_arr > 220], axis=1)))

    manifest = {
        'schema': 'fairytale-requiem-library-newspaper-readable-v3',
        'status': 'USER_REVIEW_REQUIRED_NOT_INSTALLED',
        'surface': 'grpo_lib/0223',
        'importance': 'critical_readable_story_item',
        'contract': {
            'old_newspaper_removed_before_rebuild': True,
            'clean_plate_is_independent_artifact': True,
            'no_rectangular_label_overpaint': True,
            'original_two_piece_silhouette_rebuilt': True,
            'korean_horizontal_reading_layout': True,
            'full_korean_article_text_placed': True,
            'installed': False,
        },
        'geometry': {
            'canvas': [w, h],
            'front_points': front_points,
            'back_points': back_points,
            'paper_bbox': paper_bbox,
        },
        'typesetting': {
            'headline': title_stat,
            'top_article': top_body,
            'bottom_article': bottom_body,
            'font': str(FONT),
        },
        'validation': {
            'outside_owned_mask_byte_exact': outside_exact,
            'source_paper_exact_ratio_after_clean': clean_source_exact_ratio,
            'exact_old_dark_source_pixels_retained_inside_paper': old_dark_exact_pixels,
            'all_text_regions_fit_without_overflow': all(x['remaining'] == 0 for x in [title_stat, top_body, bottom_body]),
        },
        'files': {k: str(v) for k, v in paths.items()},
        'sha256': {k: sha256(v) for k, v in paths.items()},
        'target_headline': title,
        'article': {'top': body_left, 'bottom': body_right},
    }
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest['validation'] | {'output': str(OUT)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

