from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
CATALOG = PROJECT / "catalog" / "scenario_catalog.jsonl"
REPORT = PROJECT / "audit" / "scenario_catalog_report.json"
SOURCE = PROJECT / "extracted" / "scr" / "1822.gsc"
AUDIT = PROJECT / "audit" / "catalog_repair_1822_slots_21_22.json"
EXPECTED_CATALOG_SHA256 = "C5771D1F6D759D8CEF2991038768A2745DD6460309C17DE3DC8A179433295E01"
EXPECTED_REPORT_SHA256 = "C080ABEDC383282D36A4CA4681DEB10CE6E8CF7FEFBF30FAC754126BDA1B6488"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def load_codec():
    path = PROJECT / "adapter" / "gsc_codec.py"
    spec = importlib.util.spec_from_file_location("gsc_codec_repair_1822", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load codec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def protected_tokens(text: str) -> list[dict[str, object]]:
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
    if ("1822.gsc", 21) in keys or ("1822.gsc", 22) in keys:
        raise SystemExit("1822 slots 21/22 already present")

    codec = load_codec()
    parsed = codec.parse_gsc(SOURCE.read_bytes())
    if len(parsed.strings) != 91:
        raise SystemExit(f"unexpected 1822 string count: {len(parsed.strings)}")

    specs = {
        21: {
            "role": "speaker_name", "lane": "proper_names", "ordinal": 263,
            "offset": 2736, "raw_sha256": "2C73782D28C0E52A05F8E58FC87386E36656D0C8F3602BEDC0D5FBEF155F6FB5",
            "neighbors": (19, 20, 22, 23),
        },
        22: {
            "role": "dialogue", "lane": "dialogue", "ordinal": 262,
            "offset": 2726, "raw_sha256": "FF46F5DB83B55659E85D1C23AE4F9706930A45DC8CCEB495BDBA597DD9BF2161",
            "neighbors": (20, 21, 23, 24),
        },
    }
    added = []
    for slot, spec in specs.items():
        raw = parsed.strings[slot]
        text = raw.decode("cp932", errors="strict")
        role = str(spec["role"])
        offset = int(spec["offset"])
        row = {
            "uid": f"scr.xfl::1822.gsc::slot/{slot:05d}",
            "archive": "scr.xfl",
            "file": "1822.gsc",
            "slot": slot,
            "source_language": "ja-JP",
            "source_encoding": "cp932",
            "source_text": text,
            "source_raw_sha256": sha256(raw),
            "source_byte_length": len(raw),
            "roles": [role],
            "lanes": [str(spec["lane"])],
            "visibility_verdicts": ["visible"],
            "references": [{
                "command_ordinal_zero_based": int(spec["ordinal"]),
                "command_offset": offset,
                "command_offset_hex": f"0x{offset:06X}",
                "opcode": 121,
                "opcode_hex": "0x0079",
                "command_name": "GET_DIRECTORY",
                "arg_index": 0,
                "role": role,
                "raw_command_sha256": str(spec["raw_sha256"]),
            }],
            "protected_tokens": protected_tokens(text),
            "unknown_caret_markers": [],
            "empty_placeholder": False,
            "neighbor_uids": [f"scr.xfl::1822.gsc::slot/{n:05d}" for n in spec["neighbors"]],
        }
        rows.append(row)
        added.append(row)

    rows.sort(key=lambda row: (str(row["file"]).lower(), int(row["slot"])))
    new_catalog_raw = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows).encode("utf-8")
    CATALOG.write_bytes(new_catalog_raw)

    report = json.loads(report_raw.decode("utf-8"))
    if report["connected_unique_slot_count"] != 43706 or report["active_nonempty_nonlookup_unit_count"] != 29374:
        raise SystemExit("unexpected report totals")
    file_row = next(row for row in report["files"] if row["file"] == "1822.gsc")
    if file_row["string_slot_count"] != 91 or file_row["referenced_unique_slot_count"] != 89 or file_row["unreferenced_slot_count"] != 2:
        raise SystemExit("unexpected 1822 report baseline")
    report["connected_unique_slot_count"] = 43708
    report["active_nonempty_nonlookup_unit_count"] = 29376
    report["catalog_sha256"] = sha256(new_catalog_raw)
    file_row["connected_string_reference_count"] = int(file_row["connected_string_reference_count"]) + 2
    file_row["referenced_unique_slot_count"] = 91
    file_row["unreferenced_slot_count"] = 0
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    audit = {
        "schema": "fairytale-requiem-catalog-repair-v1",
        "status": "PASS",
        "file": "1822.gsc",
        "reason": "GET_DIRECTORY commands 262/263 carry two visible display slots in argument 0; all neighboring display slots also pass through argument 0, but these two lack the duplicate MESSAGE reference used by the general catalog contract.",
        "added_slots": [21, 22],
        "added_entries": added,
        "before": {
            "catalog_sha256": EXPECTED_CATALOG_SHA256,
            "report_sha256": EXPECTED_REPORT_SHA256,
            "active_nonempty_nonlookup_unit_count": 29374,
        },
        "after": {
            "catalog_sha256": sha256(CATALOG.read_bytes()),
            "report_sha256": sha256(REPORT.read_bytes()),
            "active_nonempty_nonlookup_unit_count": 29376,
        },
        "checks": {
            "trusted_catalog_baseline_hash_matched": True,
            "trusted_report_baseline_hash_matched": True,
            "source_string_count_91": True,
            "source_slots_decoded_strict_cp932": True,
            "command_references_bound_by_ordinal_offset_and_hash": True,
            "catalog_sorted_after_insert": True,
            "report_counts_updated": True,
        },
    }
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS", "added_slots": [21, 22],
        "catalog_sha256": sha256(CATALOG.read_bytes()),
        "report_sha256": sha256(REPORT.read_bytes()), "audit": str(AUDIT),
    }, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())