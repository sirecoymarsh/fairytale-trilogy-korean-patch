from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


SOURCE_TITLE = "フェアリーテイル・レクイエム"
TARGET_TITLE = "페어리테일 레퀴엠"
EXPECTED_OFFSET = 530086


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: patch_runtime_title.py BASE_EXE OUTPUT_EXE AUDIT_JSON")
    base_path, output_path, audit_path = map(Path, sys.argv[1:])
    source = SOURCE_TITLE.encode("cp932")
    target = TARGET_TITLE.encode("cp949")
    blob = bytearray(base_path.read_bytes())
    hits: list[int] = []
    pos = 0
    while True:
        pos = blob.find(source, pos)
        if pos < 0:
            break
        hits.append(pos)
        pos += 1
    if hits != [EXPECTED_OFFSET]:
        raise SystemExit(f"unexpected source title offsets: {hits!r}")
    if len(target) > len(source):
        raise SystemExit("target title does not fit source allocation")
    if blob[EXPECTED_OFFSET + len(source)] != 0:
        raise SystemExit("source title is not NUL terminated")

    replacement = target + b"\0" * (len(source) - len(target))
    before = bytes(blob)
    blob[EXPECTED_OFFSET : EXPECTED_OFFSET + len(source)] = replacement
    after = bytes(blob)
    changed = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
    allowed = list(range(EXPECTED_OFFSET, EXPECTED_OFFSET + len(source)))
    if not changed or not set(changed).issubset(allowed):
        raise SystemExit("unexpected title patch diff")
    if after[EXPECTED_OFFSET : EXPECTED_OFFSET + len(target)] != target:
        raise SystemExit("target title verification failed")
    if after.find(source) >= 0:
        raise SystemExit("source title still present after patch")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(after)
    audit = {
        "status": "PASS",
        "base_exe": str(base_path),
        "output_exe": str(output_path),
        "base_sha256": sha256(before),
        "output_sha256": sha256(after),
        "offset": EXPECTED_OFFSET,
        "allocation_bytes": len(source),
        "source_title": SOURCE_TITLE,
        "source_encoding": "cp932",
        "source_bytes_hex": source.hex().upper(),
        "target_title": TARGET_TITLE,
        "target_encoding": "cp949",
        "target_bytes_hex": target.hex().upper(),
        "changed_byte_count": len(changed),
        "changed_offsets": changed,
        "diff_allowlist": [EXPECTED_OFFSET, EXPECTED_OFFSET + len(source) - 1],
        "checks": {
            "unique_source_match": True,
            "nul_terminated_allocation": True,
            "target_fits_allocation": True,
            "only_title_allocation_changed": True,
            "target_bytes_exact": True,
            "source_bytes_removed": True,
        },
    }
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
