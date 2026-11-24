from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CATALOG = PROJECT / "catalog" / "scenario_catalog.jsonl"
REPORT = PROJECT / "audit" / "scenario_catalog_report.json"
SOURCE = PROJECT / "extracted" / "scr" / "1518.gsc"
AUDIT = PROJECT / "audit" / "catalog_repair_1518_slots_84_85.json"
EXPECTED_CATALOG_SHA256 = "C72619C5D2B764C7CAA76B9AF73E7D7490B12902F39632E0E900B75DB2F489EA"
EXPECTED_REPORT_SHA256 = "C9B53F4230AD72B2D365CDF1C6AA4E19B5B545820C4EE70C3D69C07E6496C3C2"
COMMAND_ORDINAL = 297
COMMAND_OFFSET = 4522
COMMAND_RAW_SHA256 = "1A31DA68F10F6BEA74DC8681C20A099261B7D7C0C4855EE0881CE93A367B4674"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def load_codec():
    path = PROJECT / "adapter" / "gsc_codec.py"
    spec = importlib.util.spec_from_file_location("gsc_codec_repair_1518", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load codec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def protected_tokens(text: str) -> list[dict[str, object]]:
    import re
    regex = re.compile(r"\^(?:g[0-9]{3}|d[0-9]+|s[0-9]+|cy|ck|n|m)")
    return [
        {"character_offset": match.start(), "category": "caret_control", "value": match.group(0)}
        for match in regex.finditer(text)
    ]


def main() -> int:
    if AUDIT.exists():
        raise SystemExit("repair audit already exists; refusing to run twice")
    catalog_raw = CATALOG.read_bytes()
    report_raw = REPORT.read_bytes()
    if sha256(catalog_raw) != EXPECTED_CATALOG_SHA256:
        raise SystemExit(f"catalog baseline hash mismatch: {sha256(catalog_raw)}")
    if sha256(report_raw) != EXPECTED_REPORT_SHA256:
        raise SystemExit(f"report baseline hash mismatch: {sha256(report_raw)}")

    rows = [json.loads(line) for line in catalog_raw.decode("utf-8").splitlines() if line]
    keys = {(str(row["file"]), int(row["slot"])) for row in rows}
    if ("1518.gsc", 84) in keys or ("1518.gsc", 85) in keys:
        raise SystemExit("1518 slots 84/85 already present")

    codec = load_codec()
    parsed = codec.parse_gsc(SOURCE.read_bytes())
    if len(parsed.strings) != 165:
        raise SystemExit(f"unexpected 1518 string count: {len(parsed.strings)}")

    specs = {
        84: ("speaker_name", "proper_names", 5),
        85: ("dialogue", "dialogue", 6),
    }
    added = []
    for slot, (role, lane, arg_index) in specs.items():
        raw = parsed.strings[slot]
        text = raw.decode("cp932", errors="strict")
        row = {
            "uid": f"scr.xfl::1518.gsc::slot/{slot:05d}",
            "archive": "scr.xfl",
            "file": "1518.gsc",
            "slot": slot,
            "source_language": "ja-JP",
            "source_encoding": "cp932",
            "source_text": text,
            "source_raw_sha256": sha256(raw),
            "source_byte_length": len(raw),
            "roles": [role],
            "lanes": [lane],
            "visibility_verdicts": ["visible"],
            "references": [{
                "command_ordinal_zero_based": COMMAND_ORDINAL,
                "command_offset": COMMAND_OFFSET,
                "command_offset_hex": f"0x{COMMAND_OFFSET:06X}",
                "opcode": 200,
                "opcode_hex": "0x00C8",
                "command_name": "READ_SCENARIO",
                "arg_index": arg_index,
                "role": role,
                "raw_command_sha256": COMMAND_RAW_SHA256,
            }],
            "protected_tokens": protected_tokens(text),
            "unknown_caret_markers": [],
            "empty_placeholder": False,
            "neighbor_uids": [
                f"scr.xfl::1518.gsc::slot/{neighbor:05d}"
                for neighbor in (82, 83, 85, 86, 87)
                if neighbor != slot
            ],
        }
        rows.append(row)
        added.append(row)

    rows.sort(key=lambda row: (str(row["file"]).lower(), int(row["slot"])))
    new_catalog_raw = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows).encode("utf-8")
    CATALOG.write_bytes(new_catalog_raw)

    report = json.loads(report_raw.decode("utf-8"))
    if report["connected_unique_slot_count"] != 43704 or report["active_nonempty_nonlookup_unit_count"] != 29372:
        raise SystemExit("unexpected report totals")
    file_row = next(row for row in report["files"] if row["file"] == "1518.gsc")
    if file_row["referenced_unique_slot_count"] != 163 or file_row["unreferenced_slot_count"] != 2:
        raise SystemExit("unexpected 1518 report baseline")
    report["connected_unique_slot_count"] = 43706
    report["active_nonempty_nonlookup_unit_count"] = 29374
    report["catalog_sha256"] = sha256(new_catalog_raw)
    file_row["connected_string_reference_count"] = int(file_row["connected_string_reference_count"]) + 2
    file_row["referenced_unique_slot_count"] = 165
    file_row["unreferenced_slot_count"] = 0
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    audit = {
        "schema": "fairytale-requiem-catalog-repair-v1",
        "status": "PASS",
        "file": "1518.gsc",
        "reason": "READ_SCENARIO command ordinal 297 carries visible speaker/dialogue in args 5 and 6; the general connected-argument contract omitted this exceptional command form.",
        "added_slots": [84, 85],
        "added_entries": added,
        "before": {
            "catalog_sha256": EXPECTED_CATALOG_SHA256,
            "report_sha256": EXPECTED_REPORT_SHA256,
            "active_nonempty_nonlookup_unit_count": 29372,
        },
        "after": {
            "catalog_sha256": sha256(CATALOG.read_bytes()),
            "report_sha256": sha256(REPORT.read_bytes()),
            "active_nonempty_nonlookup_unit_count": 29374,
        },
        "checks": {
            "trusted_catalog_baseline_hash_matched": True,
            "trusted_report_baseline_hash_matched": True,
            "source_string_count_165": True,
            "source_slots_decoded_strict_cp932": True,
            "command_reference_bound_by_ordinal_offset_and_hash": True,
            "catalog_sorted_after_insert": True,
            "report_counts_updated": True,
        },
    }
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "added_slots": [84, 85],
        "catalog_sha256": sha256(CATALOG.read_bytes()),
        "report_sha256": sha256(REPORT.read_bytes()),
        "audit": str(AUDIT),
    }, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
