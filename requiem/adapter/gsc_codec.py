#!/usr/bin/env python3
"""Minimal deterministic codec for codeX RScript GSC string-table rebuilding.

This module deliberately exposes only structural data and raw string bytes.  It
does not decode, print, or otherwise inspect scenario prose.
"""

from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


@dataclass(frozen=True)
class GscParts:
    source: bytes
    header: tuple[int, ...]
    command: bytes
    offsets: tuple[int, ...]
    strings: tuple[bytes, ...]
    trailing: bytes
    file_length_mode: str
    has_leading_dummy_string: bool

    @property
    def header_length(self) -> int:
        return self.header[1]

    @property
    def command_length(self) -> int:
        return self.header[2]

    @property
    def declaration_length(self) -> int:
        return self.header[3]

    @property
    def definition_length(self) -> int:
        return self.header[4]

    @property
    def visible_string_count(self) -> int:
        return len(self.strings) - (1 if self.has_leading_dummy_string else 0)


def parse_gsc(data: bytes) -> GscParts:
    if len(data) < 20:
        raise ValueError("GSC is too short")
    header_length = struct.unpack_from("<I", data, 4)[0]
    if header_length < 20 or header_length % 4:
        raise ValueError("invalid GSC header length")
    if len(data) < header_length:
        raise ValueError("truncated GSC header")
    header = struct.unpack_from(f"<{header_length // 4}I", data, 0)
    if len(header) not in (7, 9):
        raise ValueError(f"unsupported codeX RScript GSC header shape: {len(header)} integers")
    if header[0] == len(data):
        file_length_mode = "modern-actual-length"
    elif header[0] + header[-1] == len(data):
        file_length_mode = "legacy-length-minus-final-field"
    else:
        raise ValueError("unrecognized codeX RScript GSC file-length field")

    command_start = header_length
    declaration_start = command_start + header[2]
    definition_start = declaration_start + header[3]
    definition_end = definition_start + header[4]
    if definition_end > len(data):
        raise ValueError("declared GSC sections exceed the file")
    if header[3] % 4:
        raise ValueError("GSC string declaration length is not divisible by four")

    command = data[command_start:declaration_start]
    declaration = data[declaration_start:definition_start]
    definition = data[definition_start:definition_end]
    trailing = data[definition_end:]
    offsets = struct.unpack(f"<{len(declaration) // 4}I", declaration)
    if not offsets:
        raise ValueError("empty GSC string declaration table")
    if offsets[0] != 0:
        raise ValueError("first GSC string offset is not zero")
    if tuple(sorted(offsets)) != offsets or len(set(offsets)) != len(offsets):
        raise ValueError("GSC string offsets are not strictly increasing")
    if offsets[-1] >= len(definition):
        raise ValueError("last GSC string offset is outside its section")

    strings: list[bytes] = []
    for index, start in enumerate(offsets):
        end = offsets[index + 1] if index + 1 < len(offsets) else len(definition)
        segment = definition[start:end]
        if not segment or segment[-1] != 0:
            raise ValueError("GSC string is not NUL-terminated")
        if b"\0" in segment[:-1]:
            raise ValueError("GSC string contains an embedded NUL")
        strings.append(segment[:-1])

    leading_dummy = (
        len(offsets) >= 2
        and offsets[0] == 0
        and offsets[1] == 1
        and strings[0] == b""
    )
    return GscParts(
        source=data,
        header=header,
        command=command,
        offsets=offsets,
        strings=tuple(strings),
        trailing=trailing,
        file_length_mode=file_length_mode,
        has_leading_dummy_string=leading_dummy,
    )


def rebuild_gsc(parts: GscParts, strings: tuple[bytes, ...]) -> bytes:
    """Rebuild from parsed sections while preserving every non-string section."""

    if len(strings) != len(parts.strings):
        raise ValueError("GSC string count changes are not allowed")

    offsets: list[int] = []
    definition = bytearray()
    for raw in strings:
        if b"\0" in raw:
            raise ValueError("replacement GSC strings may not contain NUL")
        offsets.append(len(definition))
        definition.extend(raw)
        definition.append(0)

    declaration = struct.pack(f"<{len(offsets)}I", *offsets)
    if len(declaration) != parts.declaration_length:
        raise ValueError("GSC declaration-table byte length changed")

    delta = len(definition) - parts.definition_length
    header = list(parts.header)
    header[0] += delta
    header[4] = len(definition)
    output = (
        struct.pack(f"<{len(header)}I", *header)
        + parts.command
        + declaration
        + bytes(definition)
        + parts.trailing
    )
    if parts.file_length_mode == "modern-actual-length":
        valid_length = len(output) == header[0]
    else:
        valid_length = len(output) == header[0] + header[-1]
    if not valid_length:
        raise ValueError("rebuilt GSC file length violates the source length mode")
    return output


def structural_fingerprint(parts: GscParts) -> dict[str, object]:
    return {
        "file_length_mode": parts.file_length_mode,
        "header": list(parts.header),
        "command_sha256": sha256(parts.command),
        "command_bytes": len(parts.command),
        "declaration_bytes": parts.declaration_length,
        "definition_bytes": parts.definition_length,
        "trailing_sha256": sha256(parts.trailing),
        "trailing_bytes": len(parts.trailing),
        "table_slot_count": len(parts.strings),
        "visible_slot_count": parts.visible_string_count,
        "has_leading_dummy_string": parts.has_leading_dummy_string,
    }
