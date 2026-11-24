#!/usr/bin/env python3
"""Independently verify the Fairytale Requiem CP949 executable delta."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

import pefile


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def text_section(data: bytes) -> dict[str, int]:
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if data[:2] != b"MZ" or data[pe_offset:pe_offset + 4] != b"PE\0\0":
        raise ValueError("invalid PE signature")
    coff = pe_offset + 4
    count = struct.unpack_from("<H", data, coff + 2)[0]
    optional_size = struct.unpack_from("<H", data, coff + 16)[0]
    table = coff + 20 + optional_size
    for index in range(count):
        header = table + index * 40
        if data[header:header + 8].rstrip(b"\0") == b".text":
            return {"header_offset": header, "virtual_size": struct.unpack_from("<I", data, header + 8)[0], "virtual_address": struct.unpack_from("<I", data, header + 12)[0], "raw_size": struct.unpack_from("<I", data, header + 16)[0], "raw_offset": struct.unpack_from("<I", data, header + 20)[0], "characteristics": struct.unpack_from("<I", data, header + 36)[0]}
    raise ValueError(".text section not found")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("patched", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.read_bytes()
    patched = args.patched.read_bytes()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    failures: list[str] = []

    if len(source) != len(patched): failures.append("file size changed")
    if sha256(source) != manifest["source"]["sha256"]: failures.append("source hash mismatch")
    if sha256(patched) != manifest["output"]["sha256"]: failures.append("patched hash mismatch")

    allowed: set[int] = set()
    for patch in manifest["patches"]:
        offset = int(patch["offset"]); old = bytes.fromhex(patch["old_hex"]); new = bytes.fromhex(patch["new_hex"])
        allowed.update(range(offset, offset + int(patch["length"])))
        if source[offset:offset + len(old)] != old: failures.append(f"{patch['name']}: source bytes mismatch")
        if patched[offset:offset + len(new)] != new: failures.append(f"{patch['name']}: patched bytes mismatch")
    actual = {i for i, (a, b) in enumerate(zip(source, patched)) if a != b}
    if actual - allowed: failures.append(f"unexpected changed offsets: {sorted(actual - allowed)[:20]}")
    if sorted(actual) != manifest["actual_changed_offsets"]: failures.append("changed-offset manifest mismatch")

    section = text_section(patched)
    if section["virtual_size"] != 0x746B0: failures.append(".text VirtualSize mismatch")
    if not section["characteristics"] & 0x20000000: failures.append(".text is not executable")
    if patched[0x756A2:0x756B0] != bytes.fromhex("C7 44 24 04 B5 03 00 00 FF 25 70 60 47 00"): failures.append("CP949 DBCS wrapper mismatch")
    if patched[0x63A22:0x63A28] != bytes.fromhex("B8 12 04 00 00 C3"): failures.append("built-in CP949 to Korean locale mapping missing")
    if patched[0x81140:0x8114D] != b"Malgun Gothic": failures.append("primary Malgun Gothic patch mismatch")
    if patched[0x81808:0x81815] != b"Malgun Gothic": failures.append("secondary Malgun Gothic patch mismatch")
    if patched[0x8218C:0x82195] != b"Batang\0\0\0": failures.append("Batang patch mismatch")
    for needle, label in (("ＭＳ ゴシック".encode("cp932"), "MS Gothic CP932"), ("ＭＳ 明朝".encode("cp932"), "MS Mincho CP932")):
        if needle in patched: failures.append(f"residual default font bytes: {label}")
    try:
        pe = pefile.PE(data=patched, fast_load=False)
        if pe.FILE_HEADER.Machine != 0x14C: failures.append("patched PE is not i386")
    except Exception as exc:
        failures.append(f"PE parse failed: {type(exc).__name__}: {exc}")

    report = {"schema": "fairytale-requiem-korean-output-exe-verification-v1", "source_sha256": sha256(source), "patched_sha256": sha256(patched), "source_size": len(source), "patched_size": len(patched), "allowlisted_patch_count": len(manifest["patches"]), "actual_changed_byte_count": len(actual), "unexpected_changed_byte_count": len(actual - allowed), "text_section": section, "failures": failures, "pass": not failures}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True))
    if failures: raise SystemExit(1)


if __name__ == "__main__":
    main()