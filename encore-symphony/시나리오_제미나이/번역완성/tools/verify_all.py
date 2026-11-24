"""Validate translated Encore/Symphony v2 packets, restore canonical IDs, and build merged outputs."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = Path(r"Y:\AI\Codex\projects\fairytale-symphony-encore-ko\시나리오_제미나이")
OUT_DIR = BASE_DIR / "번역완성"

WORKS = {
    "Encore": ("앙코르", 39, 4122, "E"),
    "Symphony": ("심포니", 21, 2329, "S"),
}

CONTROL_RE = re.compile(r"\^(?:g[0-9]{3}|d[0-9]+|s[0-9]+|cy|ck|cr|n|m)")
RUBY_RE = re.compile(r"\|([^\[\]\|]+)\[([^\[\]\|]+)\]")
JP_RE = re.compile(r"[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]")
MAX_RUNTIME_WIDTH = 1000
SAFE_REFLOW_WIDTH = 992
MAX_DIALOGUE_LINES = 3

RUBY_WHITELIST = {
    "Encore": {
        "E1101-00032": 1,
        "E1101-00082": 1,
        "E1102-00053": 1,
        "E1102-00063": 1,
        "E1102-00280": 1,
        "E1107-00240": 1,
        "E1110-00009": 1,
        "E1111-00028": 2,
        "E1117-00091": 1,
        "E1203-00009": 1,
        "E1301-00010": 1,
        "E1301-00051": 1,
        "E1303-00041": 1,
        "E1303-00097": 1,
        "E1303-00099": 1,
        "E1304-00076": 1,
    },
    "Symphony": {
        "S1003-00002": 1,
        "S1005-00291": 1,
        "S1018-00132": 1,
        "S1018-00181": 1,
        "S1018-00187": 1,
    },
}

FORBIDDEN_GLOBAL = [
    ("회색 악마", "잿빛 악마"),
    ("회색악마", "잿빛 악마"),
    ("아리스", "앨리스"),
    ("겔다", "게르다"),
    ("라푼첼", "라푼젤"),
    ("그레테르", "그레텔"),
    ("오딜르", "오딜"),
    ("오디르", "오딜"),
    ("틴크", "팅크"),
    ("옛날이야기 증후군", "동화 증후군"),
    ("가시나무", "가시덤불"),
]

REPEAT_LOCK_GROUPS = {
    "Encore": [
        ["E1119-00125", "E1121-00374"],
        ["E1203-00060", "E1203-00063"],
        ["E1206-00193", "E1207-00027"],
        ["E1206-00195", "E1207-00028"],
        ["E1403-00031", "E1403-00073"],
    ],
    "Symphony": [
        ["S1001-00063", "S1001-00064", "S1001-00065"],
        ["S1002-00001", "S1004-00002"],
        ["S1003-00183", "S1018-00084"],
        ["S1007-00037", "S1011-00031"],
        ["S1007-00138", "S1008-00002"],
        ["S1011-00101", "S1012-00002"],
        ["S1013-00049", "S1014-00003"],
        ["S1013-00052", "S1014-00007"],
        ["S1013-00055", "S1014-00009"],
        ["S1013-00075", "S1014-00015"],
        ["S1013-00078", "S1014-00019"],
        ["S1013-00081", "S1014-00022"],
        ["S1013-00083", "S1014-00024"],
        ["S1013-00094", "S1014-00032"],
        ["S1013-00096", "S1014-00034"],
        ["S1013-00098", "S1014-00036"],
        ["S1013-00101", "S1014-00039"],
        ["S1013-00103", "S1014-00041"],
        ["S1014-00195", "S1015-00002"],
        ["S1019-00039", "S1019-00148"],
    ],
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def glyph_width(ch: str) -> int:
    return 16 if ord(ch) < 128 else 32


def display_text(text: str) -> str:
    text = RUBY_RE.sub(lambda m: m.group(1), text)
    return CONTROL_RE.sub(lambda m: "^n" if m.group(0) == "^n" else "", text)


def line_widths(text: str) -> list[int]:
    return [sum(glyph_width(ch) for ch in part) for part in display_text(text).split("^n")]


def required_runtime_lines(text: str, max_width: int = MAX_RUNTIME_WIDTH) -> int:
    return sum(0 if width == 0 else math.ceil(width / max_width) for width in line_widths(text))


def load_restorer(src_dir: Path):
    restorer_path = src_dir / "검수자료" / "응답_ID_복원.py"
    spec = importlib.util.spec_from_file_location("fairytale_id_restorer", restorer_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load restorer: {restorer_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_source_integrity(src_dir: Path) -> dict:
    manifest_path = src_dir / "검수자료" / "gemini" / "manifest.json"
    mf = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = mf["files_sha256"]
    mismatches = []
    for rel, exp_hash in expected.items():
        fpath = src_dir / rel
        if not fpath.is_file():
            mismatches.append(f"MISSING:{rel}")
        else:
            got = sha256_file(fpath)
            if got != exp_hash:
                mismatches.append(f"MODIFIED:{rel}")
    actual_files = {p.relative_to(src_dir).as_posix() for p in src_dir.rglob("*") if p.is_file()}
    extra = sorted(actual_files - set(expected) - {"검수자료/gemini/manifest.json"})
    return {
        "verified_files": len(expected),
        "mismatches": mismatches,
        "extra_files": extra,
        "ok": not mismatches and not extra,
    }


def resolve_packet_selection(all_pids: list[str], raw_args: list[str] | None) -> list[str]:
    if not raw_args:
        return all_pids
    if len(raw_args) == 1:
        token = raw_args[0].strip()
        for sep in ("..", "-", "~", ":"):
            if sep in token:
                a, b = [x.strip() for x in token.split(sep, 1)]
                if a in all_pids and b in all_pids:
                    i0, i1 = all_pids.index(a), all_pids.index(b)
                    return all_pids[min(i0, i1) : max(i0, i1) + 1]
        if token not in all_pids:
            raise ValueError(f"Unknown packet ID: {token}")
        return [token]
    if len(raw_args) == 2 and all(x in all_pids for x in raw_args):
        i0, i1 = all_pids.index(raw_args[0]), all_pids.index(raw_args[1])
        return all_pids[min(i0, i1) : max(i0, i1) + 1]
    selected = []
    for x in raw_args:
        if x not in all_pids:
            raise ValueError(f"Unknown packet ID: {x}")
        if x not in selected:
            selected.append(x)
    return selected


def check_line(work: str, row: dict, ko: str) -> list[str]:
    uid = row["id"]
    ja = row["ja"]
    errors: list[str] = []

    if not isinstance(ko, str) or not ko.strip():
        errors.append(f"{uid}: empty or non-string translation")
        return errors

    for bad_ws in ("\n", "\r", "\t", "\x00", "\ufffd"):
        if bad_ws in ko:
            errors.append(f"{uid}: forbidden control/whitespace {repr(bad_ws)}")

    low = ko.lower()
    if "```" in ko or re.search(r'(?:json|thought)\s*[\}\{]', low) or '{"packet"' in low:
        errors.append(f"{uid}: model response contamination")

    # CP949 check with explicit hint for the three known traps
    if "\u2014" in ko:
        errors.append(f"{uid}: CP949-invalid EM DASH '—' (u2014) found; use '─' (u2500)")
    if "\u30fb" in ko:
        errors.append(f"{uid}: CP949-invalid KATAKANA MIDDLE DOT '・' (u30fb) found; use '·' (u00b7)")
    if "\u301c" in ko:
        errors.append(f"{uid}: CP949-invalid WAVE DASH '〜' (u301c) found; use '~' or '～'")
    try:
        ko.encode("cp949", errors="strict")
    except UnicodeEncodeError as exc:
        bad_ch = ko[exc.start:exc.end]
        errors.append(f"{uid}: CP949 encode error on {repr(bad_ch)} (U+{ord(bad_ch[0]):04X})")

    # Japanese residue check
    jp_hits = JP_RE.findall(ko)
    if jp_hits:
        errors.append(f"{uid}: residual Japanese characters {jp_hits[:5]}")

    # Control code exact parity
    got_controls = CONTROL_RE.findall(ko)
    if got_controls != row["controls"]:
        errors.append(f"{uid}: control mismatch expected={row['controls']} got={got_controls}")
    stripped_ctrl = CONTROL_RE.sub("", ko)
    if "^" in stripped_ctrl:
        errors.append(f"{uid}: stray or malformed '^' control in {repr(ko)}")

    # Ruby whitelist check
    matches = list(RUBY_RE.finditer(ko))
    rem = RUBY_RE.sub("", ko)
    if any(c in rem for c in "|[]"):
        errors.append(f"{uid}: stray/malformed ruby bracket in {repr(ko)}")
    expected_ruby_cnt = RUBY_WHITELIST[work].get(uid, 0)
    if len(matches) != expected_ruby_cnt:
        errors.append(
            f"{uid}: ruby count mismatch expected={expected_ruby_cnt} got={len(matches)} ({[m.group(0) for m in matches]})"
        )

    # Layout width / 3-line limit check
    widths = line_widths(ko)
    needed = required_runtime_lines(ko)
    if needed > MAX_DIALOGUE_LINES or len(widths) > MAX_DIALOGUE_LINES or any(w > SAFE_REFLOW_WIDTH for w in widths):
        errors.append(
            f"{uid}: layout overflow needed={needed} segments={len(widths)} widths={widths} text={repr(ko)}"
        )

    # Forbidden terms & terminology locks
    for bad, good in FORBIDDEN_GLOBAL:
        if bad in ko:
            errors.append(f"{uid}: forbidden spelling '{bad}' (use '{good}')")
    if "かまど" in ja and "화덕" in ko:
        errors.append(f"{uid}: used '화덕' instead of '아궁이' for かまど")
    if "スノードーム" in ja and any(w in ko for w in ("스노우볼", "스노볼", "스노우 볼")):
        errors.append(f"{uid}: used snow-ball variant instead of '스노우 돔'")
    if "灰色の悪魔" in ja and "잿빛 악마" not in ko:
        errors.append(f"{uid}: missing required '잿빛 악마' for 灰色の悪魔")
    if "お伽話症候群" in ja and "동화 증후군" not in ko:
        errors.append(f"{uid}: missing required '동화 증후군' for お伽話症候群")
    if "パペット" in ja and "퍼핏" not in ko:
        errors.append(f"{uid}: missing required loanword '퍼핏' for パペット")
    if "おばあさま" in ja and "할머님" not in ko:
        errors.append(f"{uid}: missing required '할머님' for おばあさま")
    if "×××××" in ja and "×××××" not in ko:
        errors.append(f"{uid}: missing exact 5x '×××××'")
    elif "××××" in ja and "××××" not in ko:
        errors.append(f"{uid}: missing exact 4x '××××'")

    # Pronoun check in spoken dialogue (do not allow 그/그녀/그들 in dialogue lines)
    if row["kind"] == "발화" or (row["kind"] == "이어쓰기" and row["speaker"]):
        if re.search(r"(?<![가-힣])(?:그녀[가-힣]*|그들[가-힣]*|그의|그에게[가-힣]*)(?![가-힣])", ko):
            errors.append(f"{uid}: third-person pronoun '그/그녀/그들' in spoken dialogue: {repr(ko)}")

    return errors


def verify_work(work: str, raw_packet_args: list[str] | None, build_merged: bool) -> dict:
    short, expected_packet_count, expected_row_count, _ = WORKS[work]
    src_dir = BASE_DIR / short
    dst_dir = OUT_DIR / short
    orig_dir = dst_dir / "응답_원본"
    restored_dir = dst_dir / "응답_복원"
    orig_dir.mkdir(parents=True, exist_ok=True)
    restored_dir.mkdir(parents=True, exist_ok=True)

    integrity = verify_source_integrity(src_dir)
    if not integrity["ok"]:
        raise RuntimeError(f"{work} source integrity violated: {integrity}")

    labels_path = dst_dir / "labels.json"
    if not labels_path.is_file():
        raise FileNotFoundError(f"Missing labels.json: {labels_path}")
    labels_doc = json.loads(labels_path.read_text(encoding="utf-8"))

    pkg_idx = json.loads((src_dir / "검수자료" / "packet_index.json").read_text(encoding="utf-8"))
    packets_map = {p["packet"]: p["ids"] for p in pkg_idx["packets"]}
    all_pids = [p["packet"] for p in pkg_idx["packets"]]
    assert len(all_pids) == expected_packet_count

    catalog_rows = [
        json.loads(line)
        for line in (src_dir / "검수자료" / "catalog.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(catalog_rows) == expected_row_count
    by_id = {r["id"]: r for r in catalog_rows}

    restorer = load_restorer(src_dir)
    selected_pids = resolve_packet_selection(all_pids, raw_packet_args)

    failures: list[str] = []
    warnings: list[str] = []
    ko_by_id: dict[str, str] = {}
    packet_stats: list[dict] = []
    issues_all: list[dict] = []

    for pid in selected_pids:
        resp_path = orig_dir / f"{pid}.json"
        if not resp_path.is_file():
            failures.append(f"{pid}: missing response file {resp_path}")
            continue
        try:
            raw_json = json.loads(resp_path.read_text(encoding="utf-8-sig"), object_pairs_hook=restorer.unique_keys)
            canonical = restorer.restore(raw_json, packets_map)
        except Exception as exc:
            failures.append(f"{pid}: restore failed: {exc}")
            continue

        # Save canonical restored JSON cleanly (UTF-8, LF)
        out_restored = restored_dir / f"{pid}.json"
        out_restored.write_bytes((json.dumps(canonical, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

        pkt_errors = 0
        for item in canonical["lines"]:
            uid = item["id"]
            ko = item["ko"]
            ko_by_id[uid] = ko
            row_errs = check_line(work, by_id[uid], ko)
            if row_errs:
                pkt_errors += len(row_errs)
                failures.extend(row_errs)

        for iss in canonical.get("issues") or []:
            issues_all.append({"packet": pid, **iss})

        packet_stats.append({
            "packet": pid,
            "rows": len(canonical["lines"]),
            "errors": pkt_errors,
            "model": canonical.get("model"),
        })

    # Repeat-lock consistency check across verified lines
    for group in REPEAT_LOCK_GROUPS[work]:
        present = [(uid, ko_by_id[uid]) for uid in group if uid in ko_by_id]
        if len(present) >= 2 and len({ko for _, ko in present}) > 1:
            failures.append(
                f"REPEAT_MISMATCH {group}: translations differ -> " + " | ".join(f"{u}={repr(k)}" for u, k in present)
            )

    # Check identical-source same-speaker lines >= 10 chars as warnings
    same_src = defaultdict(list)
    for uid, ko in ko_by_id.items():
        r = by_id[uid]
        cleaned = re.sub(r"\s+|\^n", "", r["ja"])
        if len(cleaned) >= 10:
            same_src[(r["ja"], r["speaker"])].append((uid, ko))
    for (ja, sp), pairs in same_src.items():
        if len(pairs) >= 2 and len({k for _, k in pairs}) > 1:
            warnings.append(
                f"SAME_SOURCE_VARIATION speaker={sp or 'narration'}: "
                + " | ".join(f"{u}={repr(k)}" for u, k in pairs)
            )

    merged_path = None
    if build_merged and not failures and len(selected_pids) == expected_packet_count and len(ko_by_id) == expected_row_count:
        entries = []
        for r in catalog_rows:
            uid = r["id"]
            entries.append({
                "id": uid,
                "uid": f"scr.xfl::{r['scene']}.gsc::slot/{r['slot']:05d}",
                "scene": r["scene"],
                "slot": r["slot"],
                "kind": r["kind"],
                "speaker": r["speaker"],
                "speaker_id": r.get("speaker_id"),
                "branch": r["branch"],
                "packet": r["packet"],
                "controls": r["controls"],
                "source_ja": r["ja"],
                "source_sha256": r["source_sha256"],
                "target_ko": ko_by_id[uid],
            })
        merged_doc = {
            "schema": "fairytale-ko-merged-scenario-v1",
            "work": work,
            "title": short,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "translator_model": labels_doc.get("translator_model", "Orchestrator (Carbon) + Gemini 4 Hydrogen (High)"),
            "packet_count": expected_packet_count,
            "row_count": expected_row_count,
            "labels": labels_doc["labels"],
            "entries": entries,
            "issues": issues_all,
        }
        merged_path = dst_dir / f"{short}_번역통합.json"
        merged_path.write_bytes((json.dumps(merged_doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    return {
        "work": work,
        "title": short,
        "status": "PASS" if not failures else "FAIL",
        "selected_packets": len(selected_pids),
        "verified_packets": len(packet_stats),
        "verified_rows": len(ko_by_id),
        "expected_packets": expected_packet_count,
        "expected_rows": expected_row_count,
        "failure_count": len(failures),
        "warning_count": len(warnings),
        "failures": failures,
        "warnings": warnings,
        "source_integrity": integrity,
        "merged_path": str(merged_path) if merged_path else None,
        "merged_sha256": sha256_file(merged_path) if merged_path else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", choices=["Encore", "Symphony"])
    parser.add_argument("--packets", nargs="+", help="Packet range (e.g. E001 E009) or list")
    parser.add_argument("--all", action="store_true", help="Verify both Encore and Symphony")
    parser.add_argument("--build-merged", action="store_true", help="Write merged JSON and global verification report")
    args = parser.parse_args()

    if not args.all and not args.work:
        parser.error("Specify --work Encore|Symphony or --all")

    targets = ["Encore", "Symphony"] if args.all else [args.work]
    results = []
    any_fail = False
    for w in targets:
        pkts = None if args.all else args.packets
        res = verify_work(w, pkts, args.build_merged)
        results.append(res)
        if res["status"] != "PASS":
            any_fail = True

    if args.all or args.build_merged:
        report = {
            "schema": "fairytale-translation-verification-v1",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "overall_status": "FAIL" if any_fail else "PASS",
            "works": results,
        }
        if args.all:
            report_path = OUT_DIR / "verification_report.json"
            report_path.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    print(json.dumps(results if len(results) > 1 else results[0], ensure_ascii=False, indent=2))
    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
