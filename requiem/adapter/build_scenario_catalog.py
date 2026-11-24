#!/usr/bin/env python3
"""Build a stable, context-bearing catalog from codeX RScript GSC files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gsc_codec import parse_gsc


KNOWN_CARET_RE = re.compile(r"\^(?:g[0-9]{3}|d[0-9]+|s[0-9]+|cy|ck|n|m)")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*(?:\d+|\*)?(?:\.(?:\d+|\*))?[hlLzjt]*[diuoxXfFeEgGaAcspn%]")
BRACE_RE = re.compile(r"\{[A-Za-z_][A-Za-z0-9_.:-]*\}")


@dataclass(frozen=True)
class Command:
    ordinal: int
    offset: int
    opcode: int
    name: str
    fmt: str
    args: tuple[int, ...]
    raw: bytes


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_commands(command_bytes: bytes, formats: dict[int, tuple[str, str]]) -> list[Command]:
    commands: list[Command] = []
    position = 0
    while position < len(command_bytes):
        start = position
        if position + 2 > len(command_bytes):
            raise ValueError(f"truncated opcode at 0x{start:X}")
        opcode = struct.unpack_from("<H", command_bytes, position)[0]
        position += 2
        if opcode in formats:
            fmt, name = formats[opcode]
        elif opcode & 0xF000 == 0xF000:
            fmt, name = "hh", ""
        elif opcode & 0xF000 == 0:
            fmt, name = "", ""
        else:
            fmt, name = "hhh", ""
        arg_size = struct.calcsize("<" + fmt)
        if position + arg_size > len(command_bytes):
            raise ValueError(f"truncated args at 0x{start:X} for opcode 0x{opcode:04X}")
        args = struct.unpack_from("<" + fmt, command_bytes, position) if fmt else ()
        position += arg_size
        commands.append(Command(len(commands), start, opcode, name, fmt, tuple(int(v) for v in args), command_bytes[start:position]))
    if position != len(command_bytes):
        raise ValueError("command parse did not terminate exactly")
    return commands


def role_for(opcode: int, arg_index: int) -> tuple[str, str, str]:
    if opcode == 0x51 and arg_index == 4:
        return "speaker_name", "proper_names", "visible"
    if opcode == 0x51 and arg_index == 5:
        return "dialogue", "dialogue", "visible"
    if opcode == 0x52 and arg_index == 4:
        return "append_dialogue", "dialogue", "visible"
    if opcode == 0x0E and arg_index == 1:
        return "choice_prompt", "choices", "visible"
    if opcode == 0x0E and 7 <= arg_index <= 11:
        return f"choice_option_{arg_index - 6}", "choices", "visible"
    if opcode == 0x20 and arg_index == 0:
        return "overlay_or_draw_text", "runtime_generated_text", "pending_runtime_visibility"
    if opcode == 0x0F and arg_index == 1:
        return "string_argument_0x0f", "runtime_generated_text", "pending_runtime_visibility"
    if opcode == 0x79 and arg_index == 1:
        return "directory_or_lookup_key", "lookup_keys", "pending_lookup_safety"
    return f"opcode_0x{opcode:04x}_arg_{arg_index}", "unknown", "pending_runtime_visibility"


def protected_tokens(text: str) -> list[dict[str, Any]]:
    matches: list[tuple[int, str, str]] = []
    for category, regex in (("caret_control", KNOWN_CARET_RE), ("printf", PRINTF_RE), ("brace_placeholder", BRACE_RE)):
        for match in regex.finditer(text):
            matches.append((match.start(), category, match.group(0)))
    for index, char in enumerate(text):
        if ord(char) < 0x20 or ord(char) == 0x7F:
            matches.append((index, "c0_control", f"U+{ord(char):04X}"))
    matches.sort()
    return [{"character_offset": offset, "category": category, "value": value} for offset, category, value in matches]


def unknown_carets(text: str) -> list[dict[str, Any]]:
    known_starts = {m.start() for m in KNOWN_CARET_RE.finditer(text)}
    return [
        {
            "character_offset": i,
            "following_codepoint": f"U+{ord(text[i + 1]):04X}" if i + 1 < len(text) else "END",
        }
        for i, char in enumerate(text)
        if char == "^" and i not in known_starts
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    script_root = project / "extracted" / "scr"
    config_path = project / "adapter" / "command_formats.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    formats = {int(row["opcode"]): (row["format"], row["name"]) for row in config["commands"]}
    connected = {int(row["opcode"]): tuple(int(v) for v in row["arg_indices"]) for row in config["connected_string_args"]}

    records: dict[tuple[str, int], dict[str, Any]] = {}
    appearances: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    referenced_by_file: dict[str, set[int]] = defaultdict(set)
    command_counts: Counter[int] = Counter()
    role_counts: Counter[str] = Counter()
    file_summaries: list[dict[str, Any]] = []
    parse_failures: list[dict[str, str]] = []
    invalid_refs: list[dict[str, Any]] = []

    for path in sorted(script_root.glob("*.gsc"), key=lambda p: p.name.lower()):
        try:
            parts = parse_gsc(path.read_bytes())
            commands = parse_commands(parts.command, formats)
        except Exception as exc:
            parse_failures.append({"file": path.name, "error": f"{type(exc).__name__}: {exc}"})
            continue
        file_role_refs = 0
        for command in commands:
            command_counts[command.opcode] += 1
            for declared_index in connected.get(command.opcode, ()):
                resolved_index = declared_index if declared_index >= 0 else len(command.args) + declared_index
                if not 0 <= resolved_index < len(command.args):
                    invalid_refs.append({"file": path.name, "command_offset": command.offset, "opcode": command.opcode, "declared_arg_index": declared_index, "reason": "argument_index_out_of_range"})
                    continue
                slot_index = command.args[resolved_index]
                if not 0 <= slot_index < len(parts.strings):
                    invalid_refs.append({"file": path.name, "command_offset": command.offset, "opcode": command.opcode, "arg_index": resolved_index, "slot": slot_index, "slot_count": len(parts.strings), "reason": "slot_index_out_of_range"})
                    continue
                raw = parts.strings[slot_index]
                text = raw.decode("cp932", errors="strict")
                role, lane, verdict = role_for(command.opcode, resolved_index)
                uid = f"scr.xfl::{path.name}::slot/{slot_index:05d}"
                key = (path.name, slot_index)
                if key not in records:
                    records[key] = {
                        "uid": uid,
                        "archive": "scr.xfl",
                        "file": path.name,
                        "slot": slot_index,
                        "source_language": "ja-JP",
                        "source_encoding": "cp932",
                        "source_text": text,
                        "source_raw_sha256": sha256(raw),
                        "source_byte_length": len(raw),
                        "roles": [],
                        "lanes": [],
                        "visibility_verdicts": [],
                        "references": [],
                        "protected_tokens": protected_tokens(text),
                        "unknown_caret_markers": unknown_carets(text),
                        "empty_placeholder": text == "",
                    }
                record = records[key]
                ref = {
                    "command_ordinal_zero_based": command.ordinal,
                    "command_offset": command.offset,
                    "command_offset_hex": f"0x{command.offset:06X}",
                    "opcode": command.opcode,
                    "opcode_hex": f"0x{command.opcode:04X}",
                    "command_name": command.name,
                    "arg_index": resolved_index,
                    "role": role,
                    "raw_command_sha256": sha256(command.raw),
                }
                record["references"].append(ref)
                if role not in record["roles"]:
                    record["roles"].append(role)
                if lane not in record["lanes"]:
                    record["lanes"].append(lane)
                if verdict not in record["visibility_verdicts"]:
                    record["visibility_verdicts"].append(verdict)
                appearances[path.name].append((command.ordinal, slot_index, uid))
                referenced_by_file[path.name].add(slot_index)
                role_counts[role] += 1
                file_role_refs += 1
        file_summaries.append({
            "file": path.name,
            "sha256": sha256(path.read_bytes()),
            "command_count": len(commands),
            "string_slot_count": len(parts.strings),
            "connected_string_reference_count": file_role_refs,
            "referenced_unique_slot_count": len(referenced_by_file[path.name]),
            "unreferenced_slot_count": len(parts.strings) - len(referenced_by_file[path.name]),
        })

    for filename, items in appearances.items():
        ordered: list[str] = []
        for _, _, uid in sorted(items):
            if not ordered or ordered[-1] != uid:
                ordered.append(uid)
        positions: dict[str, list[int]] = defaultdict(list)
        for index, uid in enumerate(ordered):
            positions[uid].append(index)
        for uid, indices in positions.items():
            filename2, slot_text = uid.split("::slot/")
            file_name = filename2.split("::")[-1]
            record = records[(file_name, int(slot_text))]
            neighbors: list[str] = []
            for index in indices:
                for neighbor_index in (index - 2, index - 1, index + 1, index + 2):
                    if 0 <= neighbor_index < len(ordered) and ordered[neighbor_index] != uid and ordered[neighbor_index] not in neighbors:
                        neighbors.append(ordered[neighbor_index])
            record["neighbor_uids"] = neighbors[:8]

    catalog = sorted(records.values(), key=lambda row: (row["file"].lower(), row["slot"]))
    for record in catalog:
        record["roles"].sort()
        record["lanes"].sort()
        record["visibility_verdicts"].sort()
    catalog_path = project / "catalog" / "scenario_catalog.jsonl"
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    with catalog_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in catalog:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    active = [row for row in catalog if not row["empty_placeholder"] and "pending_lookup_safety" not in row["visibility_verdicts"]]
    unknown_markers = sum(len(row["unknown_caret_markers"]) for row in catalog)
    report = {
        "schema": "fairytale-requiem-scenario-catalog-v1",
        "script_file_count": len(file_summaries),
        "parse_failure_count": len(parse_failures),
        "command_count": sum(command_counts.values()),
        "command_opcode_counts": {f"0x{k:04X}": v for k, v in sorted(command_counts.items())},
        "connected_string_reference_count": sum(role_counts.values()),
        "connected_unique_slot_count": len(catalog),
        "active_nonempty_nonlookup_unit_count": len(active),
        "role_reference_counts": dict(sorted(role_counts.items())),
        "unknown_caret_marker_count": unknown_markers,
        "invalid_reference_count": len(invalid_refs),
        "catalog_path": str(catalog_path),
        "catalog_sha256": sha256(catalog_path.read_bytes()),
        "format_contract_sha256": sha256(config_path.read_bytes()),
        "parse_failures": parse_failures,
        "invalid_references": invalid_refs,
        "files": file_summaries,
    }
    write_json(project / "audit" / "scenario_catalog_report.json", report)
    print(json.dumps({
        "script_file_count": report["script_file_count"],
        "parse_failure_count": report["parse_failure_count"],
        "connected_unique_slot_count": report["connected_unique_slot_count"],
        "active_nonempty_nonlookup_unit_count": report["active_nonempty_nonlookup_unit_count"],
        "unknown_caret_marker_count": report["unknown_caret_marker_count"],
        "invalid_reference_count": report["invalid_reference_count"],
        "catalog_sha256": report["catalog_sha256"],
    }, ensure_ascii=True))
    if parse_failures or invalid_refs:
        raise SystemExit(1)


if __name__ == "__main__":
    main()