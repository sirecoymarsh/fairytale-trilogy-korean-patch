#!/usr/bin/env python3
"""Inspect, extract, rebuild, and verify codeX RScript XFL archives.

The adapter preserves entry order and raw 0x20-byte name fields.  Repacking is
deterministic; an unchanged contiguous archive should rebuild byte-identically.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path, PurePath


MAGIC = b"LB\x01\x00"
HEADER_SIZE = 12
ENTRY_SIZE = 0x28


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


@dataclass(frozen=True)
class Entry:
    index: int
    name: str
    raw_name: bytes
    relative_offset: int
    absolute_offset: int
    size: int


@dataclass(frozen=True)
class Archive:
    source: Path
    size: int
    table_size: int
    data_start: int
    entries: tuple[Entry, ...]


def parse_archive(path: Path) -> Archive:
    size = path.stat().st_size
    with path.open("rb") as handle:
        header = handle.read(HEADER_SIZE)
        if len(header) != HEADER_SIZE or header[:4] != MAGIC:
            raise ValueError("not a supported codeX RScript XFL archive")
        table_size, entry_count = struct.unpack_from("<II", header, 4)
        if table_size != entry_count * ENTRY_SIZE:
            raise ValueError(
                f"unexpected XFL table size: {table_size} != {entry_count} * {ENTRY_SIZE}"
            )
        data_start = HEADER_SIZE + table_size
        if data_start > size:
            raise ValueError("XFL table exceeds archive size")

        entries: list[Entry] = []
        seen_names: set[str] = set()
        for index in range(entry_count):
            row = handle.read(ENTRY_SIZE)
            if len(row) != ENTRY_SIZE:
                raise ValueError(f"truncated XFL table row {index}")
            raw_name = row[:0x20]
            encoded_name = raw_name.split(b"\0", 1)[0]
            name = encoded_name.decode("cp932", errors="strict")
            if not name:
                raise ValueError(f"empty XFL entry name at index {index}")
            if name in seen_names:
                raise ValueError(f"duplicate XFL entry name: {name!r}")
            seen_names.add(name)
            relative_offset, payload_size = struct.unpack_from("<II", row, 0x20)
            absolute_offset = data_start + relative_offset
            if absolute_offset + payload_size > size:
                raise ValueError(f"entry exceeds archive: {name!r}")
            entries.append(
                Entry(
                    index=index,
                    name=name,
                    raw_name=raw_name,
                    relative_offset=relative_offset,
                    absolute_offset=absolute_offset,
                    size=payload_size,
                )
            )

    ranges = sorted((e.absolute_offset, e.absolute_offset + e.size, e.name) for e in entries)
    for previous, current in zip(ranges, ranges[1:]):
        if current[0] < previous[1]:
            raise ValueError(f"overlapping XFL entries: {previous[2]!r}, {current[2]!r}")
    return Archive(path, size, table_size, data_start, tuple(entries))


def safe_output_path(root: Path, name: str) -> Path:
    pure = PurePath(name)
    if pure.is_absolute() or any(part in ("", ".", "..") for part in pure.parts):
        raise ValueError(f"unsafe XFL entry name: {name!r}")
    destination = root.joinpath(*pure.parts)
    resolved_root = root.resolve()
    resolved_destination = destination.resolve()
    if resolved_root != resolved_destination and resolved_root not in resolved_destination.parents:
        raise ValueError(f"entry escapes extraction root: {name!r}")
    return destination


def inspect_archive(archive: Archive, *, hash_payloads: bool) -> dict:
    entries: list[dict[str, object]] = []
    with archive.source.open("rb") as handle:
        for entry in archive.entries:
            item: dict[str, object] = {
                "index": entry.index,
                "name": entry.name,
                "raw_name_hex": entry.raw_name.hex().upper(),
                "relative_offset": entry.relative_offset,
                "absolute_offset": entry.absolute_offset,
                "size": entry.size,
            }
            if hash_payloads:
                handle.seek(entry.absolute_offset)
                item["sha256"] = sha256_bytes(handle.read(entry.size))
            entries.append(item)

    contiguous = True
    cursor = archive.data_start
    for entry in archive.entries:
        if entry.absolute_offset != cursor:
            contiguous = False
        cursor = entry.absolute_offset + entry.size
    no_trailing_bytes = cursor == archive.size
    return {
        "schema": "codex-rscript-xfl-manifest-v1",
        "archive": {
            "path": str(archive.source),
            "size": archive.size,
            "sha256": sha256_file(archive.source),
            "magic_hex": MAGIC.hex().upper(),
            "table_size": archive.table_size,
            "entry_count": len(archive.entries),
            "data_start": archive.data_start,
            "payloads_contiguous_in_table_order": contiguous,
            "no_trailing_bytes": no_trailing_bytes,
        },
        "entries": entries,
    }


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def extract_archive(archive: Archive, output_dir: Path, manifest_path: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = inspect_archive(archive, hash_payloads=True)
    with archive.source.open("rb") as handle:
        for entry, item in zip(archive.entries, manifest["entries"]):
            destination = safe_output_path(output_dir, entry.name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            handle.seek(entry.absolute_offset)
            payload = handle.read(entry.size)
            if len(payload) != entry.size:
                raise ValueError(f"short read for {entry.name!r}")
            if sha256_bytes(payload) != item["sha256"]:
                raise ValueError(f"payload hash drift while extracting {entry.name!r}")
            destination.write_bytes(payload)
            item["extracted_path"] = str(destination)
    write_json(manifest_path, manifest)
    return manifest


def repack_archive(input_dir: Path, manifest_path: Path, output_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest["entries"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payloads: list[bytes] = []
    for item in entries:
        source = safe_output_path(input_dir, item["name"])
        payloads.append(source.read_bytes())

    with output_path.open("wb") as handle:
        handle.write(MAGIC)
        handle.write(struct.pack("<II", len(entries) * ENTRY_SIZE, len(entries)))
        relative_offset = 0
        for item, payload in zip(entries, payloads):
            raw_name = bytes.fromhex(item["raw_name_hex"])
            if len(raw_name) != 0x20:
                raise ValueError(f"invalid raw name field for {item['name']!r}")
            handle.write(raw_name)
            handle.write(struct.pack("<II", relative_offset, len(payload)))
            relative_offset += len(payload)
        for payload in payloads:
            handle.write(payload)

    rebuilt = parse_archive(output_path)
    report = inspect_archive(rebuilt, hash_payloads=True)
    report["repack_source_manifest"] = str(manifest_path)
    report["deterministic_layout"] = "contiguous-table-order"
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    inspect_parser = sub.add_parser("inspect")
    inspect_parser.add_argument("archive", type=Path)
    inspect_parser.add_argument("--manifest", type=Path, required=True)
    inspect_parser.add_argument("--hash-payloads", action="store_true")

    extract_parser = sub.add_parser("extract")
    extract_parser.add_argument("archive", type=Path)
    extract_parser.add_argument("output_dir", type=Path)
    extract_parser.add_argument("--manifest", type=Path, required=True)

    repack_parser = sub.add_parser("repack")
    repack_parser.add_argument("input_dir", type=Path)
    repack_parser.add_argument("manifest", type=Path)
    repack_parser.add_argument("output", type=Path)
    repack_parser.add_argument("--report", type=Path, required=True)

    verify_parser = sub.add_parser("verify-roundtrip")
    verify_parser.add_argument("original", type=Path)
    verify_parser.add_argument("rebuilt", type=Path)
    verify_parser.add_argument("--report", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "inspect":
        result = inspect_archive(parse_archive(args.archive), hash_payloads=args.hash_payloads)
        write_json(args.manifest, result)
    elif args.command == "extract":
        result = extract_archive(parse_archive(args.archive), args.output_dir, args.manifest)
    elif args.command == "repack":
        result = repack_archive(args.input_dir, args.manifest, args.output)
        write_json(args.report, result)
    else:
        original_hash = sha256_file(args.original)
        rebuilt_hash = sha256_file(args.rebuilt)
        result = {
            "schema": "codex-rscript-xfl-roundtrip-v1",
            "original": {"path": str(args.original), "size": args.original.stat().st_size, "sha256": original_hash},
            "rebuilt": {"path": str(args.rebuilt), "size": args.rebuilt.stat().st_size, "sha256": rebuilt_hash},
            "byte_identical": original_hash == rebuilt_hash and args.original.stat().st_size == args.rebuilt.stat().st_size,
        }
        write_json(args.report, result)
        if not result["byte_identical"]:
            raise SystemExit(1)
    print(json.dumps(result.get("archive", result), ensure_ascii=True))


if __name__ == "__main__":
    main()
