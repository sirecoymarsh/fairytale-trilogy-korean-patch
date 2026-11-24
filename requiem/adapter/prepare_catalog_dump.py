from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")


def load_codec():
    module_path = PROJECT / "adapter" / "gsc_codec.py"
    spec = importlib.util.spec_from_file_location("gsc_codec_prepare", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load gsc_codec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="GSC filename or stem, e.g. 1402 or 1402.gsc")
    args = parser.parse_args()
    filename = args.file if args.file.lower().endswith(".gsc") else f"{args.file}.gsc"
    stem = Path(filename).stem

    catalog_path = PROJECT / "catalog" / "scenario_catalog.jsonl"
    rows = []
    with catalog_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("file") == filename:
                rows.append(row)
    rows.sort(key=lambda row: int(row["slot"]))
    if not rows:
        raise SystemExit(f"no catalog rows for {filename}")

    codec = load_codec()
    source_path = PROJECT / "extracted" / "scr" / filename
    parsed = codec.parse_gsc(source_path.read_bytes())
    strings = [raw.decode("cp932", errors="strict") for raw in parsed.strings]
    if len(rows) != len(strings) or {int(row["slot"]) for row in rows} != set(range(len(strings))):
        raise SystemExit(
            f"catalog/string coverage mismatch: rows={len(rows)} strings={len(strings)}"
        )

    lookup_slots = [
        int(row["slot"])
        for row in rows
        if "pending_lookup_safety" in row.get("visibility_verdicts", [])
    ]
    visible_slots = [
        int(row["slot"])
        for row in rows
        if row.get("source_text")
        and "pending_lookup_safety" not in row.get("visibility_verdicts", [])
    ]

    work = PROJECT / "work"
    dump_path = work / f"{stem}_catalog_dump.json"
    inspect_path = work / f"{stem}_inspect.txt"
    dump_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    def span(slots: list[int]) -> str:
        return "none" if not slots else f"{min(slots)}..{max(slots)}"

    header = (
        f"rows={len(rows)} visible={len(visible_slots)} lookup={len(lookup_slots)} "
        f"visible_slots={span(visible_slots)} lookup_slots={span(lookup_slots)}"
    )
    lines = [header, *[f"{index:05d}\t{text}" for index, text in enumerate(strings)]]
    inspect_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "file": filename,
                "rows": len(rows),
                "visible": len(visible_slots),
                "lookup": len(lookup_slots),
                "visible_slots": [min(visible_slots), max(visible_slots)] if visible_slots else None,
                "lookup_slots": [min(lookup_slots), max(lookup_slots)] if lookup_slots else None,
                "catalog_dump": str(dump_path),
                "inspect": str(inspect_path),
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
