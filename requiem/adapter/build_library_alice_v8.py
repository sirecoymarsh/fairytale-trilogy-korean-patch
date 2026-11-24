from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2, hashlib, json, numpy as np

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
SOURCE_ROOT = PROJECT / "staging" / "ui_other_banks_audit_v1" / "exported_png" / "grpo_lib"
OUT = PROJECT / "staging" / "library_per_book_rebuild_v8" / "alice"
FONT = Path(r"C:\Windows\Fonts\gulim.ttc")
SCALE = 4
BANDS = [(94,130),(130,166),(166,203),(203,239),(239,276),(276,312),(312,349),(349,386),(386,423)]
TARGET = "이상한나라의앨리스"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def make_old_text_mask(source: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(source[..., :3], cv2.COLOR_RGB2GRAY)
    core = np.zeros(gray.shape, np.uint8)
    for y0, y1 in BANDS:
        roi = np.zeros(gray.shape, np.uint8)
        roi[max(0,y0-2):min(gray.shape[0],y1+2), 55:98] = 1
        raw = ((gray < 185) & (roi > 0) & (source[...,3] > 0)).astype(np.uint8)
        count, labels, stats, _ = cv2.connectedComponentsWithStats(raw, 8)
        for index in range(1, count):
            area = int(stats[index, cv2.CC_STAT_AREA])
            x = int(stats[index, cv2.CC_STAT_LEFT])
            width = int(stats[index, cv2.CC_STAT_WIDTH])
            height = int(stats[index, cv2.CC_STAT_HEIGHT])
            if area >= 3 and x < 98 and x + width > 55 and height >= 2:
                core[labels == index] = 1
    mask = cv2.morphologyEx(core, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))
    mask = cv2.dilate(mask, np.ones((15,15),np.uint8), 1)
    full_roi = np.zeros(gray.shape, np.uint8)
    full_roi[90:434, 53:101] = 1
    bright_double_print = (gray > 198) & (full_roi > 0)
    near_core = cv2.dilate(core, np.ones((41,41),np.uint8), 1) > 0
    mask[(bright_double_print & near_core)] = 1
    mask = cv2.dilate(mask, np.ones((3,3),np.uint8), 1)
    mask[:90] = 0
    mask[434:] = 0
    mask[:, :53] = 0
    mask[:, 101:] = 0
    return mask.astype(np.uint8) * 255

def clean_source(source: np.ndarray, mask: np.ndarray) -> np.ndarray:
    rgb = source[..., :3].astype(np.float32)
    height, width = mask.shape
    x0, x1 = 50, 102
    span = x1 - x0
    left = rgb[:, 50:56].mean(axis=1)
    right = rgb[:, 96:102].mean(axis=1)
    for channel in range(3):
        left[:,channel] = cv2.GaussianBlur(left[:,channel].reshape(-1,1),(1,0),1.25).reshape(-1)
        right[:,channel] = cv2.GaussianBlur(right[:,channel].reshape(-1,1),(1,0),1.25).reshape(-1)
    weights = np.linspace(0.0,1.0,span,dtype=np.float32)[None,:,None]
    material = left[:,None,:]*(1.0-weights)+right[:,None,:]*weights
    # Reuse only the same paper face's side-margin material; no rectangle or foreign plate.
    clean = source.copy()
    owned = mask > 0
    full = rgb.copy()
    full[:,x0:x1,:] = material
    clean[owned,:3] = np.clip(full[owned],0,255).astype(np.uint8)
    return clean

def text_layer(size: tuple[int,int], hover: bool) -> Image.Image:
    width, height = size
    hi = Image.new("L", (width*SCALE, height*SCALE), 0)
    draw = ImageDraw.Draw(hi)
    font = ImageFont.truetype(str(FONT), 32*SCALE, index=0)
    center_x = 76*SCALE
    for char, (y0, y1) in zip(TARGET, BANDS):
        box = draw.textbbox((0,0), char, font=font, stroke_width=2*SCALE)
        tw, th = box[2]-box[0], box[3]-box[1]
        y = ((y0+y1)/2)*SCALE - th/2 - box[1]
        x = center_x - tw/2 - box[0]
        draw.text((x,y), char, font=font, fill=255, stroke_width=2*SCALE, stroke_fill=255)
    glyph = hi.resize((width,height), Image.Resampling.LANCZOS)
    glyph = glyph.filter(ImageFilter.GaussianBlur(0.22 if hover else 0.16))
    if hover:
        shadow_alpha = glyph.filter(ImageFilter.GaussianBlur(0.58)).transform(
            (width,height), Image.Transform.AFFINE, (1,0,-1.0,0,1,-1.0),
            resample=Image.Resampling.BICUBIC
        ).point(lambda v: int(v*0.62))
        core_alpha = glyph.point(lambda v: int(v*0.78))
        shadow_color=(194,184,184,0)
        core_color=(126,105,105,0)
    else:
        shadow_alpha = glyph.filter(ImageFilter.GaussianBlur(0.52)).transform(
            (width,height), Image.Transform.AFFINE, (1,0,-1.0,0,1,-1.0),
            resample=Image.Resampling.BICUBIC
        ).point(lambda v: int(v*0.80))
        core_alpha = glyph
        shadow_color=(128,82,82,0)
        core_color=(52,25,27,0)
    layer=Image.new("RGBA",(width,height),(0,0,0,0))
    shadow=Image.new("RGBA",(width,height),shadow_color); shadow.putalpha(shadow_alpha)
    core=Image.new("RGBA",(width,height),core_color); core.putalpha(core_alpha)
    layer.alpha_composite(shadow)
    layer.alpha_composite(core)
    return layer

def build(stem: str, hover: bool) -> dict:
    source_path = SOURCE_ROOT / f"{stem}.png"
    source_img = Image.open(source_path).convert("RGBA")
    source = np.array(source_img)
    mask_source = np.array(Image.open(SOURCE_ROOT / "0011.png").convert("RGBA"))
    mask = make_old_text_mask(mask_source)
    clean = clean_source(source, mask)
    clean_img = Image.fromarray(clean, "RGBA")
    layer = text_layer(source_img.size, hover)
    candidate_img = clean_img.copy()
    candidate_img.alpha_composite(layer)
    candidate = np.array(candidate_img)

    state_dir = OUT / stem
    state_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "source": state_dir / "source.png",
        "mask": state_dir / "old_text_mask.png",
        "clean": state_dir / "clean.png",
        "candidate": state_dir / "candidate.png",
    }
    source_img.save(files["source"])
    Image.fromarray(mask, "L").save(files["mask"])
    clean_img.save(files["clean"])
    candidate_img.save(files["candidate"])

    outside = mask == 0
    clean_outside_exact = bool(np.array_equal(source[outside], clean[outside]))
    source_alpha_exact = bool(np.array_equal(source[...,3], clean[...,3]) and np.array_equal(source[...,3], candidate[...,3]))
    # Dark legacy ink must be absent from the clean plate in the owned region.
    gray_src = cv2.cvtColor(source[...,:3], cv2.COLOR_RGB2GRAY)
    gray_clean = cv2.cvtColor(clean[...,:3], cv2.COLOR_RGB2GRAY)
    legacy_core = (gray_src < 105) & (mask > 0)
    legacy_dark_remaining = float(np.mean(gray_clean[legacy_core] < 105)) if np.any(legacy_core) else 0.0

    return {
        "stem": stem,
        "state": "hover_or_selected" if hover else "normal",
        "target": "이상한 나라의 앨리스",
        "design_profile": "alice_round_burgundy_double_print",
        "files": {key:str(value) for key,value in files.items()},
        "sha256": {key:sha(value) for key,value in files.items()},
        "validation": {
            "dimensions": list(source_img.size),
            "outside_old_text_mask_byte_exact": clean_outside_exact,
            "alpha_geometry_byte_exact": source_alpha_exact,
            "old_text_mask_pixels": int(np.count_nonzero(mask)),
            "legacy_dark_remaining_ratio_after_clean": legacy_dark_remaining,
        },
    }

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records=[build("0011",False),build("0111",True)]
    manifest={
        "schema":"fairytale-requiem-library-per-book-alice-v8",
        "status":"USER_REVIEW_REQUIRED_NOT_INSTALLED",
        "book":"alice",
        "target":"이상한 나라의 앨리스",
        "rules":{
            "book_specific_design":True,
            "old_text_removed_before_typesetting":True,
            "no_rectangular_plate":True,
            "normal_and_selected_built_as_pair":True,
            "installed":False,
        },
        "records":records,
    }
    path=OUT/"manifest.json"
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"manifest":str(path),"records":[r["validation"] for r in records]},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
