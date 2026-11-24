#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


SIZE = (1280, 720)
WHITE = (245, 245, 245, 255)
RED = (210, 35, 45, 255)
PARCHMENT = (205, 174, 112, 255)
DARK_BROWN = (73, 39, 29, 255)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def draw_multiline(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    face: ImageFont.FreeTypeFont,
    *,
    fill=WHITE,
    spacing: int = 5,
    stroke_width: int = 0,
    stroke_fill=None,
) -> None:
    draw.multiline_text(
        xy,
        text,
        font=face,
        fill=fill,
        spacing=spacing,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )


def parchment_panel(size: tuple[int, int], seed: int) -> Image.Image:
    width, height = size
    rng = np.random.default_rng(seed)
    base = np.empty((height, width, 4), dtype=np.uint8)
    noise = rng.normal(0, 7, (height, width, 1))
    color = np.array([205, 174, 112], dtype=np.float32).reshape(1, 1, 3)
    base[:, :, :3] = np.clip(color + noise, 0, 255).astype(np.uint8)
    base[:, :, 3] = 255
    image = Image.fromarray(base, "RGBA")
    draw = ImageDraw.Draw(image)
    draw.rectangle((2, 2, width - 3, height - 3), outline=(119, 68, 53, 255), width=3)
    return image


def callout(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    target: tuple[int, int],
    face: ImageFont.FreeTypeFont,
    *,
    side: str,
) -> None:
    x, y = xy
    draw_multiline(draw, (x, y), text, face, spacing=4)
    box = draw.multiline_textbbox((x, y), text, font=face, spacing=4)
    underline_y = box[3] + 4
    if side == "left":
        start = (box[2], underline_y)
        draw.line((box[0], underline_y, box[2], underline_y), fill=RED, width=2)
    else:
        start = (box[0], underline_y)
        draw.line((box[0], underline_y, box[2], underline_y), fill=RED, width=2)
    draw.line((start, target), fill=RED, width=2)
    tx, ty = target
    draw.ellipse((tx - 4, ty - 4, tx + 4, ty + 4), fill=RED)


def page_9901(bold: Path, regular: Path) -> Image.Image:
    image = Image.new("RGBA", SIZE, (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)
    title = font(bold, 36)
    body = font(regular, 19)
    note = font(bold, 16)
    panel_title = font(bold, 27)
    panel_text = font(bold, 16)
    panel_small = font(regular, 14)

    draw.text((25, 18), "「환경 설정 안내」", font=title, fill=WHITE)
    draw_multiline(
        draw,
        (28, 72),
        "게임 중 마우스 오른쪽 버튼으로 환경 설정을 열 수 있습니다.\n"
        "화면 표시, 글꼴, 재생 속도와 음량을 바꾸고 저장·불러오기를 할 수 있습니다.",
        body,
        spacing=6,
    )

    px, py, pw, ph = 355, 178, 570, 510
    panel = parchment_panel((pw, ph), 9901)
    image.alpha_composite(panel, (px, py))
    pdraw = ImageDraw.Draw(image)
    pdraw.text((px + 22, py + 16), "환경 설정", font=panel_title, fill=DARK_BROWN)

    rows = [
        ("글꼴 선택", "맑은 고딕"),
        ("화면 모드", "창 모드"),
        ("화면 효과", "켜짐"),
        ("문장 표시 속도", "보통"),
        ("읽지 않은 문장 넘기기", "멈춤"),
        ("자동 재생 속도", "65"),
        ("BGM", "켜짐"),
        ("효과음", "켜짐"),
        ("음성", "켜짐"),
        ("백그라운드 재생", "켜짐"),
        ("클릭 시 음성 정지", "켜짐"),
    ]
    row_y = py + 62
    for index, (label, value) in enumerate(rows):
        y = row_y + index * 31
        pdraw.text((px + 32, y), label, font=panel_text, fill=DARK_BROWN)
        pdraw.rounded_rectangle((px + 338, y - 2, px + 526, y + 24), radius=4, fill=(151, 74, 67, 230))
        pdraw.text((px + 352, y + 1), value, font=panel_small, fill=(255, 245, 230, 255))
        if label in {"자동 재생 속도", "BGM", "효과음", "음성"}:
            pdraw.line((px + 430, y + 12, px + 510, y + 12), fill=(70, 45, 35, 255), width=2)
            knob = px + 474 if label == "자동 재생 속도" else px + 490
            pdraw.ellipse((knob - 5, y + 7, knob + 5, y + 17), fill=(235, 228, 197, 255), outline=DARK_BROWN)
    buttons = ["저장", "불러오기", "게임으로", "타이틀로", "종료"]
    for index, label in enumerate(buttons):
        x = px + 22 + index * 106
        pdraw.rounded_rectangle((x, py + 454, x + 94, py + 487), radius=5, fill=(151, 74, 67, 235))
        bbox = pdraw.textbbox((0, 0), label, font=panel_small)
        pdraw.text((x + (94 - (bbox[2] - bbox[0])) / 2, py + 461), label, font=panel_small, fill=(255, 245, 230, 255))

    left = [
        ((35, 190), "창/전체 화면 표시를\n전환합니다.", (px + 350, py + 95)),
        ((35, 300), "화면 효과를\n켜거나 끕니다.", (px + 350, py + 126)),
        ((35, 410), "BGM·효과음·음성의\n재생과 음량을 설정합니다.", (px + 350, py + 250)),
        ((35, 545), "다른 창으로 전환해도\n소리를 계속 재생할지\n선택합니다.", (px + 350, py + 345)),
    ]
    right = [
        ((955, 174), "설치된 글꼴 중에서\n사용할 글꼴을 고릅니다.", (px + 515, py + 64)),
        ((955, 280), "문장 표시 속도를\n설정합니다.", (px + 515, py + 157)),
        ((955, 375), "넘기기 중 읽지 않은\n문장에서 멈출지\n설정합니다.", (px + 515, py + 188)),
        ((955, 485), "자동 재생 모드의\n진행 속도를 설정합니다.", (px + 515, py + 219)),
        ((955, 582), "클릭할 때 재생 중인\n음성을 멈출지 설정합니다.", (px + 515, py + 374)),
    ]
    for xy, text, target in left:
        callout(draw, xy, text, target, note, side="left")
    for xy, text, target in right:
        callout(draw, xy, text, target, note, side="right")
    return image


def page_9902(bold: Path, regular: Path) -> Image.Image:
    image = Image.new("RGBA", SIZE, (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)
    title = font(bold, 36)
    body = font(regular, 19)
    note = font(bold, 17)
    panel_text = font(bold, 18)
    list_text = font(regular, 19)

    draw.text((25, 18), "「글꼴 선택 안내」", font=title, fill=WHITE)
    draw_multiline(
        draw,
        (28, 72),
        "환경 설정에서 ‘글꼴 선택’을 누르면 글꼴 선택 창이 열립니다.\n"
        "PC에 설치된 글꼴 가운데 게임에서 사용할 수 있는 글꼴이 목록에 표시됩니다.",
        body,
        spacing=6,
    )

    px, py, pw, ph = 340, 185, 600, 500
    image.alpha_composite(parchment_panel((pw, ph), 9902), (px, py))
    draw.text((px + 22, py + 15), "환경 설정", font=font(bold, 27), fill=DARK_BROWN)
    draw.text((px + 40, py + 70), "글꼴 선택", font=panel_text, fill=DARK_BROWN)
    draw.rounded_rectangle((px + 205, py + 65, px + 545, py + 103), radius=5, fill=(151, 74, 67, 235))
    draw.text((px + 224, py + 72), "맑은 고딕", font=list_text, fill=(255, 245, 230, 255))

    wx1, wy1, wx2, wy2 = px + 100, py + 130, px + 500, py + 425
    draw.rounded_rectangle((wx1, wy1, wx2, wy2), radius=6, fill=(82, 54, 38, 255), outline=(220, 192, 142, 255), width=3)
    draw.text((wx1 + 18, wy1 + 14), "사용할 글꼴", font=panel_text, fill=(250, 232, 188, 255))
    choices = ["맑은 고딕", "나눔고딕", "Noto Sans KR", "바탕", "돋움", "굴림"]
    for index, label in enumerate(choices):
        y = wy1 + 56 + index * 34
        if index == 0:
            draw.rounded_rectangle((wx1 + 14, y - 3, wx2 - 48, y + 27), radius=4, fill=(151, 74, 67, 255))
        draw.text((wx1 + 26, y), label, font=list_text, fill=(255, 244, 215, 255))
    draw.rounded_rectangle((wx2 - 37, wy1 + 48, wx2 - 12, wy2 - 48), radius=8, fill=(185, 143, 89, 255))
    draw.polygon([(wx2 - 25, wy1 + 62), (wx2 - 33, wy1 + 78), (wx2 - 17, wy1 + 78)], fill=(65, 42, 30, 255))
    draw.polygon([(wx2 - 25, wy2 - 62), (wx2 - 33, wy2 - 78), (wx2 - 17, wy2 - 78)], fill=(65, 42, 30, 255))
    draw.ellipse((wx2 - 38, wy2 - 43, wx2 - 8, wy2 - 13), fill=(230, 215, 180, 255), outline=(65, 42, 30, 255), width=2)
    draw.line((wx2 - 32, wy2 - 37, wx2 - 14, wy2 - 19), fill=(65, 42, 30, 255), width=3)
    draw.line((wx2 - 14, wy2 - 37, wx2 - 32, wy2 - 19), fill=(65, 42, 30, 255), width=3)

    callout(draw, (48, 190), "현재 글꼴을 누르면\n선택 창이 열립니다.", (px + 410, py + 84), note, side="left")
    callout(draw, (50, 410), "목록에서 글꼴을 누르면\n바로 선택됩니다.", (wx1 + 170, wy1 + 72), note, side="left")
    callout(draw, (965, 275), "목록에 보이지 않는 글꼴은\n스크롤 버튼으로 찾습니다.", (wx2 - 25, wy1 + 150), note, side="right")
    callout(draw, (965, 505), "닫기 버튼을 누르면\n글꼴 선택 창을 닫습니다.", (wx2 - 23, wy2 - 28), note, side="right")
    return image


def page_9903(bold: Path, regular: Path) -> Image.Image:
    image = Image.new("RGBA", SIZE, (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)
    title = font(bold, 36)
    body = font(regular, 18)
    label = font(bold, 15)
    small = font(regular, 13)
    button = font(bold, 14)
    draw.text((25, 18), "「텍스트 조작 패널 안내」", font=title, fill=WHITE)
    draw_multiline(
        draw,
        (28, 72),
        "마우스 휠을 앞으로 굴리면 왼쪽 클릭이나 Enter 키와 같은 방식으로 문장을 진행합니다.\n"
        "아래 패널에서 되감기, 자동 진행, 저장·불러오기와 화면 표시를 조작할 수 있습니다.",
        body,
        spacing=6,
    )

    x1, y1, x2, y2 = 45, 175, 1235, 245
    draw.rounded_rectangle((x1, y1, x2, y2), radius=8, fill=(213, 184, 124, 255), outline=(113, 68, 47, 255), width=3)
    buttons = [
        ("검토", "Review"), ("뒤로", "Back"), ("앞으로", "Forward"), ("건너뛰기", "Skip"),
        ("다음", "Next"), ("자동", "Auto"), ("저장", "Save"), ("불러오기", "Load"),
        ("빠른 저장", "Q-Save"), ("빠른 불러오기", "Q-Load"), ("음성", "Voice"),
        ("설정", "Menu"), ("숨김", "Hide"),
    ]
    gap = 5
    bw = (x2 - x1 - 24 - gap * (len(buttons) - 1)) // len(buttons)
    for index, (ko, en) in enumerate(buttons):
        bx = x1 + 12 + index * (bw + gap)
        draw.rounded_rectangle((bx, y1 + 12, bx + bw, y2 - 12), radius=5, fill=(246, 222, 166, 255), outline=(89, 54, 38, 255), width=2)
        bbox = draw.textbbox((0, 0), ko, font=button)
        draw.text((bx + (bw - (bbox[2] - bbox[0])) / 2, y1 + 20), ko, font=button, fill=DARK_BROWN)
        eb = draw.textbbox((0, 0), en, font=small)
        draw.text((bx + (bw - (eb[2] - eb[0])) / 2, y1 + 42), en, font=small, fill=(96, 58, 43, 255))

    cards = [
        ("검토", "직전 선택지·장 시작 등\n이전 정지 지점으로 돌아갑니다."),
        ("뒤로 / 앞으로", "이미 읽은 문장을\n한 단계씩 되감거나 진행합니다."),
        ("건너뛰기", "문장과 화면을 빠르게 재생합니다.\n설정에 따라 미독 문장에서 멈춥니다."),
        ("다음", "다음 선택지·장 시작 등\n다음 정지 지점까지 진행합니다."),
        ("자동", "클릭하지 않아도\n게임을 자동으로 진행합니다."),
        ("저장 / 불러오기", "저장 화면 또는 불러오기 화면을\n엽니다."),
        ("빠른 저장 / 불러오기", "현재 위치를 빠르게 저장하고\n빠른 저장 지점으로 돌아갑니다."),
        ("음성", "표시 중인 대사를 다시 재생합니다.\n이전 대사는 먼저 되감아 주세요."),
        ("설정 / 숨김", "환경 설정을 열거나\n텍스트 상자를 숨깁니다."),
    ]
    card_w, card_h = 380, 126
    start_x, start_y = 45, 280
    for index, (name, desc) in enumerate(cards):
        col, row = index % 3, index // 3
        cx, cy = start_x + col * 405, start_y + row * 140
        draw.rounded_rectangle((cx, cy, cx + card_w, cy + card_h), radius=7, fill=(20, 20, 20, 255), outline=RED, width=2)
        draw.text((cx + 14, cy + 10), f"· {name}", font=label, fill=WHITE)
        draw_multiline(draw, (cx + 18, cy + 38), desc, small, fill=(225, 225, 225, 255), spacing=4)
    return image


def info_box(
    image: Image.Image,
    rect: tuple[int, int, int, int],
    text: str,
    face: ImageFont.FreeTypeFont,
) -> None:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(rect, radius=18, fill=(244, 213, 143, 242), outline=(151, 74, 67, 255), width=3)
    x1, y1, _, _ = rect
    draw_multiline(draw, (x1 + 18, y1 + 15), text, face, fill=(151, 66, 42, 255), spacing=5)
    image.alpha_composite(overlay)


def page_9904(source: Image.Image, bold: Path, regular: Path) -> Image.Image:
    image = source.convert("RGBA")
    draw = ImageDraw.Draw(image)
    title = font(bold, 36)
    box = font(bold, 18)
    day = font(bold, 28)

    draw.rectangle((0, 0, 470, 70), fill=(0, 0, 0, 255))
    draw.text((25, 18), "「낙원을 걷는 법」", font=title, fill=WHITE)
    draw.rounded_rectangle((145, 76, 340, 132), radius=12, fill=(240, 205, 128, 245), outline=(151, 74, 67, 255), width=2)
    draw.text((172, 88), "1일째 밤", font=day, fill=(186, 57, 35, 255))

    info_box(image, (465, 248, 820, 342), "읽은 이야기는\n‘눈’ 아이콘으로 표시됩니다.", box)
    info_box(image, (830, 235, 1235, 342), "‘나’의 방입니다.\n스케치북을 확인할 수 있습니다.", box)
    info_box(image, (48, 365, 425, 470), "도서관에서는\n책을 읽을 수 있습니다.", box)
    info_box(image, (545, 515, 1080, 630), "열쇠 표시 이야기를 끝까지 읽어야\n다음으로 진행할 수 있습니다.", box)
    draw.ellipse((513, 387, 581, 455), fill=(166, 56, 45, 245), outline=(238, 199, 123, 255), width=4)
    glyph = font(bold, 25)
    draw.text((529, 404), "책", font=glyph, fill=(255, 235, 185, 255))
    return image


def run(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def compare_png(expected: Path, actual: Path) -> dict[str, object]:
    a = np.asarray(Image.open(expected).convert("RGBA")).astype(np.int16)
    b = np.asarray(Image.open(actual).convert("RGBA")).astype(np.int16)
    if a.shape != b.shape:
        raise RuntimeError(f"decoded WCG shape mismatch: {a.shape} != {b.shape}")
    rgb_delta = np.abs(a[:, :, :3] - b[:, :, :3])
    alpha_equal = bool(np.array_equal(a[:, :, 3], b[:, :, 3]))
    return {
        "shape": list(a.shape),
        "alpha_equal": alpha_equal,
        "max_rgb_delta": int(rgb_delta.max()),
        "mean_rgb_delta": float(rgb_delta.mean()),
        "pixels_with_rgb_delta_over_8": int(np.any(rgb_delta > 8, axis=2).sum()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    source_root = project / "staging" / "runtime_improvements" / "operation_candidates"
    stage = project / "staging" / "runtime_improvements" / "help_pages_ko"
    png_root = stage / "png"
    wcg_root = stage / "wcg"
    decoded_root = stage / "decoded"
    for path in (png_root, wcg_root, decoded_root):
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True)
    tool = project / "adapter" / "UiAssetTool.exe"
    bold = Path(r"C:\Windows\Fonts\malgunbd.ttf")
    regular = Path(r"C:\Windows\Fonts\malgun.ttf")
    for required in (tool, bold, regular):
        if not required.exists():
            raise FileNotFoundError(required)

    pages = {
        "9901": page_9901(bold, regular),
        "9902": page_9902(bold, regular),
        "9903": page_9903(bold, regular),
        "9904": page_9904(Image.open(source_root / "grpe_9904.png"), bold, regular),
    }
    mask_path = stage / "full_mask.png"
    Image.new("RGB", SIZE, "white").save(mask_path)
    records: list[dict[str, object]] = []
    for stem, page in pages.items():
        source_wcg = source_root / f"grpe_{stem}.wcg"
        source_png = source_root / f"grpe_{stem}.png"
        output_png = png_root / f"{stem}.png"
        output_wcg = wcg_root / f"{stem}.wcg"
        decoded_png = decoded_root / f"{stem}.png"
        if not source_wcg.exists() or not source_png.exists():
            raise FileNotFoundError(stem)
        if Image.open(source_png).size != SIZE:
            raise RuntimeError(f"unexpected source size: {source_png}")
        page.save(output_png)
        patch_output = run(
            [str(tool), "wcg-apply-patch", str(source_wcg), str(output_png), str(mask_path), str(output_wcg)]
        )
        run([str(tool), "wcg2png", str(output_wcg), str(decoded_png)])
        comparison = compare_png(output_png, decoded_png)
        if not comparison["alpha_equal"] or comparison["pixels_with_rgb_delta_over_8"] != 0:
            raise RuntimeError(f"WCG decoded pixels differ beyond bound: {stem}: {comparison}")
        records.append(
            {
                "stable_id": f"grpe.xfl::{stem}.wcg",
                "source_wcg": str(source_wcg),
                "source_wcg_sha256": sha256_path(source_wcg),
                "output_png": str(output_png),
                "output_wcg": str(output_wcg),
                "output_wcg_sha256": sha256_path(output_wcg),
                "decoded_png": str(decoded_png),
                "decoded_comparison": comparison,
                "tool_output": patch_output.splitlines()[0] if patch_output else "",
            }
        )

    audit = {
        "schema": "fairytale-requiem-korean-help-pages-v1",
        "status": "PASS",
        "trigger": "runtime reproduction showed Japanese help pages from grpe 9901-9904",
        "translation_policy": "Codex internal model; draft followed by one review; no external MT/API",
        "font": {"regular": str(regular), "bold": str(bold)},
        "changed_entries": [f"{stem}.wcg" for stem in pages],
        "records": records,
        "checks": {
            "four_runtime_help_pages_localized": True,
            "dimensions_preserved_1280x720": True,
            "decoded_alpha_exact": True,
            "decoded_rgb_quantization_bounded_at_8": True,
            "source_archives_not_modified": True,
        },
    }
    audit_path = project / "audit" / "runtime_help_pages_improvement.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "stage": str(stage), "audit": str(audit_path), "records": records}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
