#!/usr/bin/env python3
"""Verify the target Windows font and CP949 GDI glyph path."""

from __future__ import annotations

import ctypes
import json
from ctypes import wintypes
from pathlib import Path

from fontTools.ttLib import TTFont


HANGUL_START = 0xAC00
HANGUL_END = 0xD7A3
HANGUL_CHARSET = 129
GGO_METRICS = 0
GDI_ERROR = 0xFFFFFFFF


class FIXED(ctypes.Structure):
    _fields_ = [("fract", wintypes.WORD), ("value", wintypes.SHORT)]


class MAT2(ctypes.Structure):
    _fields_ = [("eM11", FIXED), ("eM12", FIXED), ("eM21", FIXED), ("eM22", FIXED)]


class GLYPHMETRICS(ctypes.Structure):
    _fields_ = [
        ("gmBlackBoxX", wintypes.UINT),
        ("gmBlackBoxY", wintypes.UINT),
        ("gmptGlyphOrigin", wintypes.POINT),
        ("gmCellIncX", wintypes.SHORT),
        ("gmCellIncY", wintypes.SHORT),
    ]


def fixed_one() -> FIXED:
    return FIXED(0, 1)


def fixed_zero() -> FIXED:
    return FIXED(0, 0)


def main() -> None:
    font_path = Path(r"C:\Windows\Fonts\malgun.ttf")
    font = TTFont(font_path, lazy=True)
    cmap = font.getBestCmap()
    missing = [cp for cp in range(HANGUL_START, HANGUL_END + 1) if cp not in cmap]
    font.close()

    gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
    gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
    gdi32.CreateCompatibleDC.restype = wintypes.HDC
    gdi32.CreateFontA.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPCSTR,
    ]
    gdi32.CreateFontA.restype = wintypes.HANDLE
    gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
    gdi32.SelectObject.restype = wintypes.HGDIOBJ
    gdi32.GetGlyphOutlineA.argtypes = [
        wintypes.HDC,
        wintypes.UINT,
        wintypes.UINT,
        ctypes.POINTER(GLYPHMETRICS),
        wintypes.DWORD,
        wintypes.LPVOID,
        ctypes.POINTER(MAT2),
    ]
    gdi32.GetGlyphOutlineA.restype = wintypes.DWORD
    gdi32.GetGlyphOutlineW.argtypes = list(gdi32.GetGlyphOutlineA.argtypes)
    gdi32.GetGlyphOutlineW.restype = wintypes.DWORD
    gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
    gdi32.DeleteObject.restype = wintypes.BOOL
    gdi32.DeleteDC.argtypes = [wintypes.HDC]
    gdi32.DeleteDC.restype = wintypes.BOOL

    hdc = gdi32.CreateCompatibleDC(None)
    if not hdc:
        raise ctypes.WinError(ctypes.get_last_error())
    hfont = gdi32.CreateFontA(
        -24,
        0,
        0,
        0,
        400,
        0,
        0,
        0,
        HANGUL_CHARSET,
        0,
        0,
        5,
        0,
        b"Malgun Gothic",
    )
    if not hfont:
        raise ctypes.WinError(ctypes.get_last_error())
    old = gdi32.SelectObject(hdc, hfont)

    mat = MAT2(fixed_one(), fixed_zero(), fixed_zero(), fixed_one())
    glyph_results = []
    for character in ("가", "한", "힣"):
        encoded = character.encode("cp949")
        variants = {}
        for byte_order in ("little", "big"):
            packed = int.from_bytes(encoded, byte_order)
            metrics = GLYPHMETRICS()
            result = gdi32.GetGlyphOutlineA(
                hdc,
                packed,
                GGO_METRICS,
                ctypes.byref(metrics),
                0,
                None,
                ctypes.byref(mat),
            )
            variants[byte_order] = {
                "packed_uint": packed,
                "gdi_result": result,
                "success": result != GDI_ERROR,
                "black_box": [metrics.gmBlackBoxX, metrics.gmBlackBoxY],
                "cell_advance": [metrics.gmCellIncX, metrics.gmCellIncY],
            }
        wide_metrics = GLYPHMETRICS()
        wide_result = gdi32.GetGlyphOutlineW(
            hdc,
            ord(character),
            GGO_METRICS,
            ctypes.byref(wide_metrics),
            0,
            None,
            ctypes.byref(mat),
        )
        wide = {
            "gdi_result": wide_result,
            "success": wide_result != GDI_ERROR,
            "black_box": [wide_metrics.gmBlackBoxX, wide_metrics.gmBlackBoxY],
            "cell_advance": [wide_metrics.gmCellIncX, wide_metrics.gmCellIncY],
        }
        glyph_results.append(
            {
                "codepoint": f"U+{ord(character):04X}",
                "cp949_hex": encoded.hex().upper(),
                "ansi_variants": variants,
                "unicode_reference": wide,
                "matching_byte_orders": [
                    order
                    for order, result in variants.items()
                    if result["success"]
                    and result["black_box"] == wide["black_box"]
                    and result["cell_advance"] == wide["cell_advance"]
                ],
            }
        )

    if old:
        gdi32.SelectObject(hdc, old)
    gdi32.DeleteObject(hfont)
    gdi32.DeleteDC(hdc)

    report = {
        "font_path": str(font_path),
        "hangul_syllable_count": HANGUL_END - HANGUL_START + 1,
        "missing_hangul_syllables": len(missing),
        "gdi_charset": HANGUL_CHARSET,
        "glyph_results": glyph_results,
        "pass": not missing
        and all(
            item["unicode_reference"]["success"] and item["matching_byte_orders"]
            for item in glyph_results
        ),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
