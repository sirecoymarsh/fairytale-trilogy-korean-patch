#!/usr/bin/env python3
"""Build CP949 GSC files while allowing audited ^n-only layout repairs."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from gsc_codec import parse_gsc, rebuild_gsc
from scenario_layout import MAX_RUNTIME_WIDTH, non_newline_controls, required_runtime_lines, line_widths

UID_RE = re.compile(r"^scr\.xfl::([^:]+\.gsc)::slot/([0-9]+)$", re.IGNORECASE)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def build_translation_map(project: Path, map_path: Path, output_dir: Path, manifest_path: Path) -> dict:
    project = project.resolve()
    mapping = json.loads(map_path.read_text(encoding="utf-8"))
    entries = mapping["entries"]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: set[str] = set()
    for entry in entries:
        uid = str(entry["uid"])
        if uid in seen:
            raise ValueError(f"duplicate translation UID: {uid}")
        seen.add(uid)
        match = UID_RE.fullmatch(uid)
        if not match:
            raise ValueError(f"unsupported UID: {uid}")
        grouped[match.group(1)].append(entry | {"_slot": int(match.group(2))})

    output_dir.mkdir(parents=True, exist_ok=True)
    files: list[dict[str, Any]] = []
    for filename in sorted(grouped, key=str.lower):
        source_path = project / "extracted" / "scr" / filename
        source = source_path.read_bytes()
        parts = parse_gsc(source)
        if rebuild_gsc(parts, parts.strings) != source:
            raise ValueError(f"no-change GSC round trip is not byte-identical: {filename}")
        strings = list(parts.strings)
        changes: list[dict[str, Any]] = []
        occupied_slots: set[int] = set()
        for entry in sorted(grouped[filename], key=lambda row: row["_slot"]):
            slot = int(entry["_slot"])
            if slot in occupied_slots:
                raise ValueError(f"duplicate slot ownership: {filename} slot {slot}")
            occupied_slots.add(slot)
            if not 0 <= slot < len(strings):
                raise ValueError(f"slot out of range: {filename} slot {slot}")
            old = strings[slot]
            old_text = old.decode("cp932", errors="strict")
            if old_text != entry["source_text"]:
                raise ValueError(f"source text mismatch: {entry['uid']}")
            expected_hash = str(entry.get("source_raw_sha256", sha256(old))).upper()
            if sha256(old) != expected_hash:
                raise ValueError(f"source raw hash mismatch: {entry['uid']}")
            target_text = str(entry["target_text"])
            if non_newline_controls(old_text) != non_newline_controls(target_text):
                raise ValueError(f"non-newline control mismatch: {entry['uid']}")
            if "\0" in target_text:
                raise ValueError(f"NUL in target text: {entry['uid']}")
            if (filename.lower(), slot) != ("1001.gsc", 10):
                needed = required_runtime_lines(target_text)
                if needed > 3:
                    raise ValueError(f"runtime layout overflow: {entry['uid']} requires {needed} lines; widths={line_widths(target_text)}")
            new = target_text.encode("cp949", errors="strict")
            strings[slot] = new
            changes.append({
                "uid": entry["uid"], "slot": slot,
                "source_raw_sha256": sha256(old), "target_raw_sha256": sha256(new),
                "source_byte_length": len(old), "target_byte_length": len(new),
                "length_delta": len(new) - len(old),
                "source_non_newline_controls": non_newline_controls(old_text),
                "target_non_newline_controls": non_newline_controls(target_text),
                "target_line_widths": line_widths(target_text),
                "target_required_runtime_lines": required_runtime_lines(target_text),
            })
        output = rebuild_gsc(parts, tuple(strings))
        reparsed = parse_gsc(output)
        if reparsed.command != parts.command or reparsed.trailing != parts.trailing:
            raise ValueError(f"non-string section changed: {filename}")
        if len(reparsed.strings) != len(parts.strings):
            raise ValueError(f"string count changed: {filename}")
        for index, (before, after) in enumerate(zip(parts.strings, reparsed.strings)):
            if index in occupied_slots:
                if after != strings[index]:
                    raise ValueError(f"target slot did not survive reparse: {filename} slot {index}")
            elif before != after:
                raise ValueError(f"non-target slot changed: {filename} slot {index}")
        output_path = output_dir / filename
        output_path.write_bytes(output)
        files.append({
            "file": filename, "source_path": str(source_path), "output_path": str(output_path),
            "source_size": len(source), "output_size": len(output),
            "source_sha256": sha256(source), "output_sha256": sha256(output),
            "changed_slot_count": len(changes), "changed_slots": changes,
            "command_sha256": sha256(parts.command), "trailing_sha256": sha256(parts.trailing),
            "string_slot_count": len(parts.strings),
            "no_change_roundtrip_byte_identical": True, "all_non_target_slots_identical": True,
        })
    manifest = {
        "schema": "fairytale-requiem-gsc-build-v2-layout-aware",
        "translation_map": {"path": str(map_path), "sha256": sha256(map_path.read_bytes()), "entry_count": len(entries)},
        "target_encoding": "cp949", "delivery_state": "staging-only",
        "layout_contract": {"runtime_max_width": MAX_RUNTIME_WIDTH, "max_dialogue_lines": 3, "newline_reflow_allowed": True},
        "file_count": len(files), "changed_slot_count": sum(row["changed_slot_count"] for row in files), "files": files,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    manifest = build_translation_map(args.project, args.map, args.output_dir, args.manifest)
    print(json.dumps({"file_count": manifest["file_count"], "changed_slot_count": manifest["changed_slot_count"], "manifest_sha256": sha256(args.manifest.read_bytes())}, ensure_ascii=True))

if __name__ == "__main__":
    main()
