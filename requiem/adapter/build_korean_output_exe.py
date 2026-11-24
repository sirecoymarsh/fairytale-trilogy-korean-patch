#!/usr/bin/env python3
"""Build a narrowly scoped CP949/Hangul-enabled Fairytale Requiem executable."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path


TRUSTED_SHA256 = "7C5392ABEF0810EC2CE3EC8C6318A566FCE854281BBD52C7C032A8D7477ECD66"
IMAGE_BASE = 0x400000
STUB_RVA = 0x756A2
STUB_VA = IMAGE_BASE + STUB_RVA
IS_DBCS_IAT_VA = 0x476070


@dataclass(frozen=True)
class Patch:
    name: str
    offset: int
    old: bytes
    new: bytes


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def rel32_call(source_va: int, target_va: int) -> bytes:
    return b"\xE8" + struct.pack("<i", target_va - (source_va + 5)) + b"\x90"


def parse_text_section(data: bytes) -> dict[str, int]:
    if data[:2] != b"MZ":
        raise ValueError("not an MZ executable")
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_offset:pe_offset + 4] != b"PE\0\0":
        raise ValueError("not a PE executable")
    coff = pe_offset + 4
    section_count = struct.unpack_from("<H", data, coff + 2)[0]
    optional_size = struct.unpack_from("<H", data, coff + 16)[0]
    table = coff + 20 + optional_size
    for index in range(section_count):
        header = table + index * 40
        if data[header:header + 8].rstrip(b"\0") == b".text":
            return {
                "header_offset": header,
                "virtual_size": struct.unpack_from("<I", data, header + 8)[0],
                "virtual_address": struct.unpack_from("<I", data, header + 12)[0],
                "raw_size": struct.unpack_from("<I", data, header + 16)[0],
                "raw_offset": struct.unpack_from("<I", data, header + 20)[0],
                "characteristics": struct.unpack_from("<I", data, header + 36)[0],
            }
    raise ValueError(".text section not found")


def build_patch_list(data: bytes) -> list[Patch]:
    text = parse_text_section(data)
    expected = {
        "virtual_size": 0x746A2,
        "virtual_address": 0x1000,
        "raw_size": 0x75000,
        "raw_offset": 0x1000,
        "characteristics": 0x60000020,
    }
    for key, value in expected.items():
        if text[key] != value:
            raise ValueError(f"unexpected .text {key}: 0x{text[key]:X} != 0x{value:X}")
    if text["virtual_address"] != text["raw_offset"]:
        raise ValueError("this patch requires RVA/raw identity for .text")

    patches = [
        Patch("default_font_ms_gothic_to_malgun_gothic", 0x81140, "ＭＳ ゴシック".encode("cp932"), b"Malgun Gothic"),
        Patch("secondary_font_ms_gothic_to_malgun_gothic", 0x81808, "ＭＳ ゴシック".encode("cp932"), b"Malgun Gothic"),
        Patch("default_font_ms_mincho_to_batang", 0x8218C, "ＭＳ 明朝".encode("cp932"), b"Batang\0\0\0"),
        Patch("force_special_acp_selector_to_cp949", 0x639E6, bytes.fromhex("FF 25 24 61 47 00"), bytes.fromhex("B8 B5 03 00 00 C3")),
        Patch("cp949_isdbcsleadbyteex_wrapper", STUB_RVA, b"\0" * 14, bytes.fromhex("C7 44 24 04 B5 03 00 00 FF 25 70 60 47 00")),
        Patch("extend_text_virtual_size_for_wrapper", text["header_offset"] + 8, struct.pack("<I", 0x746A2), struct.pack("<I", 0x746B0)),
    ]

    dbcs_call_vas = (0x424A23, 0x424AF8, 0x459181, 0x45927C, 0x4594DC)
    for index, va in enumerate(dbcs_call_vas, 1):
        patches.append(Patch(f"dbcs_lead_byte_call_{index}_to_cp949_wrapper", va - IMAGE_BASE, bytes.fromhex("FF 15 70 60 47 00"), rel32_call(va, STUB_VA)))

    charset_push_vas = (
        0x4039EF, 0x456989, 0x45C172, 0x45EC5D, 0x45EC9E, 0x45EFEA,
        0x45F028, 0x45F33D, 0x45F37E, 0x45F732, 0x45FA6E, 0x45FCD5,
    )
    for index, va in enumerate(charset_push_vas, 1):
        patches.append(Patch(f"createfonta_charset_{index}_shiftjis_to_hangul", va - IMAGE_BASE, bytes.fromhex("68 80 00 00 00"), bytes.fromhex("68 81 00 00 00")))
    return patches


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    source = args.source.read_bytes()
    source_hash = sha256(source)
    if source_hash != TRUSTED_SHA256:
        raise SystemExit(f"trusted baseline mismatch: {source_hash} != {TRUSTED_SHA256}")

    patches = build_patch_list(source)
    output = bytearray(source)
    occupied: set[int] = set()
    for patch in patches:
        if len(patch.old) != len(patch.new):
            raise ValueError(f"length-changing patch is forbidden: {patch.name}")
        actual = bytes(output[patch.offset:patch.offset + len(patch.old)])
        if actual != patch.old:
            raise ValueError(f"{patch.name}: old bytes mismatch at 0x{patch.offset:X}: {actual.hex()} != {patch.old.hex()}")
        span = set(range(patch.offset, patch.offset + len(patch.old)))
        if occupied & span:
            raise ValueError(f"overlapping patch range: {patch.name}")
        occupied |= span
        output[patch.offset:patch.offset + len(patch.new)] = patch.new

    changed = [i for i, (a, b) in enumerate(zip(source, output)) if a != b]
    allowed = {i for patch in patches for i in range(patch.offset, patch.offset + len(patch.old))}
    unexpected = sorted(set(changed) - allowed)
    if unexpected:
        raise ValueError(f"unexpected changed offsets: {unexpected[:20]}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)
    manifest = {
        "schema": "fairytale-requiem-korean-output-exe-v1",
        "purpose": "Enable deterministic CP949 Hangul output without changing scenario content.",
        "source": {"path": str(args.source), "size": len(source), "sha256": source_hash},
        "output": {"path": str(args.output), "size": len(output), "sha256": sha256(output)},
        "engine": {"product": "codeX RScript", "file_version": "1.11.0.3", "target_codepage": 949, "target_locale": "0x0412", "gdi_charset": 129, "default_fonts": ["Malgun Gothic", "Batang"]},
        "patches": [{"name": p.name, "offset": p.offset, "offset_hex": f"0x{p.offset:X}", "length": len(p.old), "old_hex": p.old.hex().upper(), "new_hex": p.new.hex().upper()} for p in patches],
        "actual_changed_byte_count": len(changed),
        "actual_changed_offsets": changed,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["output"], ensure_ascii=True))


if __name__ == "__main__":
    main()