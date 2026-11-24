from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(r"P:\AI\Codex\projects\fairytale-requiem-ko")
OUTPUT = PROJECT / "review_sensitive_content"
CLASSIFIED = [
    "1215", "1302", "1315", "1325", "1327", "1404", "1416", "1417",
    "1418", "1420", "1421", "1422", "1501", "1504", "1505", "1506",
    "1510", "1511", "1512", "1513", "1514", "1515", "1516", "1517",
    "1518", "1523", "1524", "1603", "1607", "1608", "1609", "1610",
    "1611", "1613", "1616", "1617", "1618", "1619", "1620", "1621",
    "1623", "1701", "1702", "1703", "1704", "1705", "1706", "1707",
    "1708", "1709", "1710", "1711", "1712", "1713", "1714", "1715",
    "1716", "1717", "1718", "1719", "1720", "1721", "1722", "1723",
    "1724", "1725", "1726", "1727", "1728", "1729", "1730", "1731",
    "1732", "1733", "1734", "1801", "1802", "1803", "1804", "1805",
    "1808", "1812", "1813", "1821", "1910",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_records() -> dict[str, dict]:
    records: dict[str, dict] = {}
    for path in sorted((PROJECT / "audit").glob("*sensitive_content_*.json")):
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        file = str(row.get("file", ""))
        if file:
            row["record_path"] = str(path.relative_to(PROJECT)).replace("\\", "/")
            records[file] = row
    return records


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "files").mkdir(parents=True, exist_ok=True)
    records = load_records()
    wanted = {f"{stem}.gsc" for stem in CLASSIFIED}
    rows_by_file: dict[str, list[dict]] = {file: [] for file in sorted(wanted)}
    with (PROJECT / "catalog" / "scenario_catalog.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            file = str(row.get("file", ""))
            if file not in wanted:
                continue
            if "lookup_keys" in row.get("lanes", []):
                continue
            text = str(row.get("source_text", ""))
            if not text:
                continue
            rows_by_file[file].append({
                "file": file,
                "slot": int(row["slot"]),
                "uid": str(row["uid"]),
                "source_text": text,
                "source_raw_sha256": str(row["source_raw_sha256"]),
            })

    master_rows = []
    manifest_files = []
    for file in sorted(rows_by_file):
        rows = sorted(rows_by_file[file], key=lambda item: item["slot"])
        record = records.get(file, {})
        reason = str(record.get(
            "reason",
            "Previously classified as sensitive during scenario review; held for the user's direct include/exclude decision.",
        ))
        status = str(record.get("status", "PENDING_USER_DIRECT_REVIEW"))
        record_path = str(record.get("record_path", ""))
        text_path = OUTPUT / "files" / f"{Path(file).stem}_source_review.txt"
        chunks = [
            f"FILE: {file}",
            f"STATUS: {status}",
            f"CLASSIFICATION_REASON: {reason}",
            f"AUDIT_RECORD: {record_path or '(legacy classification; no dedicated record)'}",
            "USER_DECISION: [ ] INCLUDE  [ ] EXCLUDE  [ ] PARTIAL",
            "USER_NOTES:",
            "",
        ]
        for row in rows:
            chunks.extend([
                f"[{row['slot']:05d}] {row['uid']}",
                row["source_text"],
                "",
            ])
            master_rows.append({
                **row,
                "classification_status": status,
                "classification_reason": reason,
                "audit_record": record_path,
                "user_decision": "",
                "user_notes": "",
            })
        text_path.write_text("\n".join(chunks), encoding="utf-8")
        manifest_files.append({
            "file": file,
            "visible_nonempty_slots": len(rows),
            "first_slot": rows[0]["slot"] if rows else None,
            "last_slot": rows[-1]["slot"] if rows else None,
            "classification_status": status,
            "classification_reason": reason,
            "audit_record": record_path or None,
            "source_review_file": str(text_path.relative_to(OUTPUT)).replace("\\", "/"),
            "source_review_sha256": sha256(text_path),
            "translation_map_created": bool(record.get("translation_map_created", False)),
            "trial_modified": bool(record.get("trial_modified", False)),
        })

    tsv_path = OUTPUT / "sensitive_scene_slots_for_review.tsv"
    fields = [
        "file", "slot", "uid", "source_text", "source_raw_sha256",
        "classification_status", "classification_reason", "audit_record",
        "user_decision", "user_notes",
    ]
    with tsv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(master_rows)

    decision_path = OUTPUT / "file_decisions.tsv"
    with decision_path.open("w", encoding="utf-8-sig", newline="") as handle:
        fields2 = ["file", "visible_nonempty_slots", "classification_reason", "decision_INCLUDE_EXCLUDE_PARTIAL", "included_slot_ranges", "notes"]
        writer = csv.DictWriter(handle, fieldnames=fields2, delimiter="\t")
        writer.writeheader()
        for item in manifest_files:
            writer.writerow({
                "file": item["file"],
                "visible_nonempty_slots": item["visible_nonempty_slots"],
                "classification_reason": item["classification_reason"],
                "decision_INCLUDE_EXCLUDE_PARTIAL": "",
                "included_slot_ranges": "",
                "notes": "",
            })

    manifest = {
        "schema": "fairytale-requiem-sensitive-review-bundle-v1",
        "status": "AWAITING_USER_DIRECT_REVIEW",
        "updated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "policy": "Separated from the Korean trial build; no translation, review pass, build, or trial modification is performed until the user decides.",
        "classified_file_count": len(manifest_files),
        "classified_visible_nonempty_slot_count": len(master_rows),
        "master_tsv": tsv_path.name,
        "master_tsv_sha256": sha256(tsv_path),
        "decision_template": decision_path.name,
        "decision_template_sha256": sha256(decision_path),
        "files": manifest_files,
    }
    manifest_path = OUTPUT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    readme = f"""# 민감 분류 장면 직접 검토 묶음

- 분류 파일: **{len(manifest_files)}개**
- 원문 슬롯: **{len(master_rows)}개**
- 현재 상태: 본 한국어 시험판과 분리, 번역·빌드 미반영

## 검토 방법

1. `file_decisions.tsv`에서 파일별로 `INCLUDE`, `EXCLUDE`, `PARTIAL`을 적습니다.
2. `PARTIAL`이면 `included_slot_ranges`에 예: `1-24,80-92`처럼 적습니다.
3. 세부 원문은 `files/<번호>_source_review.txt` 또는 `sensitive_scene_slots_for_review.tsv`에서 확인합니다.
4. 수정 의견은 `notes` 또는 슬롯별 `user_notes` 열에 적습니다.

이 묶음의 원문은 원본 게임에서 읽어 온 검토 자료이며, 현재 시험판 GSC에는 반영되지 않았습니다.
"""
    (OUTPUT / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "output": str(OUTPUT),
        "files": len(manifest_files),
        "visible_nonempty_slots": len(master_rows),
        "manifest_sha256": sha256(manifest_path),
    }, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
