#!/usr/bin/env python3
"""Build CP949 GSC loose files from a stable UID translation map."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from gsc_codec import parse_gsc, rebuild_gsc


UID_RE = re.compile(r"^scr\.xfl::([^:]+\.gsc)::slot/([0-9]+)$", re.IGNORECASE)
CARET_RE = re.compile(r"\^(?:g[0-9]{3}|d[0-9]+|s[0-9]+|cy|ck|n|m)")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    mapping = json.loads(args.map.read_text(encoding="utf-8"))
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

    args.output_dir.mkdir(parents=True, exist_ok=True)
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
            source_tokens = CARET_RE.findall(old_text)
            target_tokens = CARET_RE.findall(target_text)
            if source_tokens != target_tokens:
                raise ValueError(f"caret token mismatch: {entry['uid']} {source_tokens!r} != {target_tokens!r}")
            if "\0" in target_text:
                raise ValueError(f"NUL in target text: {entry['uid']}")
            new = target_text.encode("cp949", errors="strict")
            strings[slot] = new
            changes.append({"uid": entry["uid"], "slot": slot, "source_raw_sha256": sha256(old), "target_raw_sha256": sha256(new), "source_byte_length": len(old), "target_byte_length": len(new), "length_delta": len(new) - len(old), "caret_tokens": source_tokens})

        output = rebuild_gsc(parts, tuple(strings))
        reparsed = parse_gsc(output)
        if reparsed.command != parts.command:
            raise ValueError(f"command section changed: {filename}")
        if reparsed.trailing != parts.trailing:
            raise ValueError(f"trailing section changed: {filename}")
        if len(reparsed.strings) != len(parts.strings):
            raise ValueError(f"string count changed: {filename}")
        for index, (before, after) in enumerate(zip(parts.strings, reparsed.strings)):
            if index in occupied_slots:
                if after != strings[index]:
                    raise ValueError(f"target slot did not survive reparse: {filename} slot {index}")
            elif before != after:
                raise ValueError(f"non-target slot changed: {filename} slot {index}")
        output_path = args.output_dir / filename
        output_path.write_bytes(output)
        files.append({"file": filename, "source_path": str(source_path), "output_path": str(output_path), "source_size": len(source), "output_size": len(output), "source_sha256": sha256(source), "output_sha256": sha256(output), "changed_slot_count": len(changes), "changed_slots": changes, "command_sha256": sha256(parts.command), "trailing_sha256": sha256(parts.trailing), "string_slot_count": len(parts.strings), "no_change_roundtrip_byte_identical": True, "all_non_target_slots_identical": True})

    manifest = {"schema": "fairytale-requiem-gsc-build-v1", "translation_map": {"path": str(args.map), "sha256": sha256(args.map.read_bytes()), "entry_count": len(entries)}, "target_encoding": "cp949", "delivery_state": "staging-only", "mixed_encoding_warning": "Only allowlisted translated slots are CP949; untouched Japanese CP932 display slots in a pilot file are not release-ready.", "file_count": len(files), "changed_slot_count": sum(row["changed_slot_count"] for row in files), "files": files}
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file_count": manifest["file_count"], "changed_slot_count": manifest["changed_slot_count"], "manifest_sha256": sha256(args.manifest.read_bytes())}, ensure_ascii=True))


if __name__ == "__main__":
    main()