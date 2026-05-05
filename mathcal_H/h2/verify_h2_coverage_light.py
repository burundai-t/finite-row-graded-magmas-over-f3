#!/usr/bin/env python3
"""
Lightweight static coverage verifier for the S6-H2 pure-frontier certificate pack.

This script does not rerun the SMT solver.  It audits the accepted raw H2
artifacts for coverage, consistency, and absence of SAT/UNKNOWN/unresolved
leaves on the documented depth-9 frontier [0,18540).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Iterable, List, Dict, Any

EXPECTED_FRONTIER_START = 0
EXPECTED_FRONTIER_END = 18_540
EXPECTED_TAIL_START = 4_860
EXPECTED_TAIL_NODES = EXPECTED_FRONTIER_END - EXPECTED_TAIL_START

REQUIRED_RAW_FILES = [
    "checkpoint.json",
    "segments.csv",
    "nodes.csv",
    "chunks.csv",
    "windows.csv",
    "unknown.csv",
    "sat.csv",
    "audit_report.json",
    "audit_rerun.csv",
    "events.log",
]


def die(message: str) -> None:
    print(f"FAIL H2 coverage light: {message}", file=sys.stderr)
    raise SystemExit(1)


def as_int(row: Dict[str, str], key: str) -> int:
    try:
        return int(row[key])
    except Exception as exc:  # noqa: BLE001
        die(f"expected integer column {key!r} in row {row!r}: {exc}")


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        die(f"missing file: {path}")
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        die(f"missing file: {path}")
    return json.loads(path.read_text())


def assert_consecutive(rows: Iterable[Dict[str, str]], start_key: str, end_key: str,
                       expected_start: int, expected_end: int, label: str) -> int:
    cursor = expected_start
    total = 0
    for idx, row in enumerate(rows):
        a = as_int(row, start_key)
        b = as_int(row, end_key)
        if a != cursor:
            die(f"{label}: gap/overlap at row {idx}: expected start {cursor}, got {a}")
        if b <= a:
            die(f"{label}: nonpositive interval at row {idx}: [{a},{b})")
        cursor = b
        total += b - a
    if cursor != expected_end:
        die(f"{label}: expected end {expected_end}, got {cursor}")
    return total


def assert_no_data_rows(path: Path, label: str) -> None:
    rows = read_csv(path)
    if rows:
        die(f"{label}: expected no data rows, found {len(rows)}")


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    raw = script_dir / "raw"
    if not raw.is_dir():
        die(f"raw directory not found next to script: {raw}")

    for name in REQUIRED_RAW_FILES:
        if not (raw / name).exists():
            die(f"missing raw artifact: {name}")

    segments = read_csv(raw / "segments.csv")
    if not segments:
        die("segments.csv has no data rows")
    seg_total = assert_consecutive(
        segments, "start_offset", "end_offset",
        EXPECTED_FRONTIER_START, EXPECTED_FRONTIER_END,
        "segments.csv",
    )
    certified_unsat = sat = unknown = unresolved = nodes = 0
    for idx, row in enumerate(segments):
        start = as_int(row, "start_offset")
        end = as_int(row, "end_offset")
        n = as_int(row, "nodes")
        if n != end - start:
            die(f"segments.csv row {idx}: nodes {n} != interval length {end-start}")
        nodes += n
        certified_unsat += as_int(row, "certified_unsat")
        sat += as_int(row, "sat")
        unknown += as_int(row, "unknown")
        unresolved += as_int(row, "unresolved")
    if seg_total != EXPECTED_FRONTIER_END or nodes != EXPECTED_FRONTIER_END:
        die(f"segments total mismatch: interval={seg_total}, nodes={nodes}")
    if certified_unsat != EXPECTED_FRONTIER_END:
        die(f"certified_unsat total {certified_unsat} != {EXPECTED_FRONTIER_END}")
    if sat or unknown or unresolved:
        die(f"segments contain sat={sat}, unknown={unknown}, unresolved={unresolved}")

    assert_no_data_rows(raw / "sat.csv", "sat.csv")
    assert_no_data_rows(raw / "unknown.csv", "unknown.csv")

    checkpoint = read_json(raw / "checkpoint.json")
    audit_report = read_json(raw / "audit_report.json")
    if checkpoint.get("status") != "complete":
        die(f"checkpoint status is {checkpoint.get('status')!r}, expected 'complete'")
    if checkpoint.get("frontier_total") != EXPECTED_FRONTIER_END:
        die("checkpoint frontier_total mismatch")
    for key, expected in [
        ("start_offset", EXPECTED_TAIL_START),
        ("end_offset", EXPECTED_FRONTIER_END),
        ("effective_end_offset", EXPECTED_FRONTIER_END),
        ("next_offset", EXPECTED_FRONTIER_END),
        ("checked_nodes", EXPECTED_TAIL_NODES),
        ("unsat_nodes", EXPECTED_TAIL_NODES),
        ("sat_nodes", 0),
        ("unknown_nodes", 0),
        ("remaining_nodes", 0),
        ("target_rawH", 1171),
    ]:
        if checkpoint.get(key) != expected:
            die(f"checkpoint {key}={checkpoint.get(key)!r}, expected {expected!r}")

    if audit_report.get("status") != "PASS":
        die(f"audit_report status is {audit_report.get('status')!r}, expected 'PASS'")
    if audit_report.get("checkpoint_status") != "complete":
        die("audit_report checkpoint_status mismatch")
    if audit_report.get("start_offset") != EXPECTED_TAIL_START or audit_report.get("end_offset") != EXPECTED_FRONTIER_END:
        die("audit_report tail interval mismatch")
    if audit_report.get("checked_nodes") != EXPECTED_TAIL_NODES:
        die("audit_report checked_nodes mismatch")
    if audit_report.get("counts", {}).get("unsat") != EXPECTED_TAIL_NODES:
        die("audit_report unsat count mismatch")
    if audit_report.get("errors") not in ([], None):
        die(f"audit_report errors not empty: {audit_report.get('errors')!r}")

    nodes_rows = read_csv(raw / "nodes.csv")
    if len(nodes_rows) != EXPECTED_TAIL_NODES:
        die(f"nodes.csv has {len(nodes_rows)} rows, expected {EXPECTED_TAIL_NODES}")
    seen = []
    for row in nodes_rows:
        if row.get("answer") != "unsat":
            die(f"nodes.csv non-unsat answer at node {row.get('node_index')}: {row.get('answer')!r}")
        seen.append(as_int(row, "node_index"))
    if seen != list(range(EXPECTED_TAIL_START, EXPECTED_FRONTIER_END)):
        die("nodes.csv node_index values are not exactly consecutive [4860,18540)")

    chunks = read_csv(raw / "chunks.csv")
    chunk_total = assert_consecutive(chunks, "offset", "end_offset", EXPECTED_TAIL_START, EXPECTED_FRONTIER_END, "chunks.csv")
    if chunk_total != EXPECTED_TAIL_NODES:
        die("chunks.csv total mismatch")
    for idx, row in enumerate(chunks):
        n = as_int(row, "nodes")
        if n != as_int(row, "end_offset") - as_int(row, "offset"):
            die(f"chunks.csv row {idx}: nodes length mismatch")
        if as_int(row, "unsat") != n or as_int(row, "sat") != 0 or as_int(row, "unknown") != 0:
            die(f"chunks.csv row {idx}: expected all-unsat with no sat/unknown")

    windows = read_csv(raw / "windows.csv")
    window_total = assert_consecutive(windows, "offset", "end_offset", EXPECTED_TAIL_START, EXPECTED_FRONTIER_END, "windows.csv")
    if window_total != EXPECTED_TAIL_NODES:
        die("windows.csv total mismatch")
    for idx, row in enumerate(windows):
        n = as_int(row, "nodes")
        if n != as_int(row, "end_offset") - as_int(row, "offset"):
            die(f"windows.csv row {idx}: nodes length mismatch")
        if as_int(row, "unsat") != n or as_int(row, "sat") != 0 or as_int(row, "unknown") != 0:
            die(f"windows.csv row {idx}: expected all-unsat with no sat/unknown")

    rerun = read_csv(raw / "audit_rerun.csv")
    if not rerun:
        die("audit_rerun.csv has no rows")
    for idx, row in enumerate(rerun):
        if row.get("expected_answer") != "unsat" or row.get("rerun_answer") != "unsat":
            die(f"audit_rerun row {idx}: expected/rerun answer mismatch")
        if as_int(row, "mismatch") != 0:
            die(f"audit_rerun row {idx}: mismatch != 0")

    print(
        "PASS S6-H2 coverage light: "
        f"segments=[{EXPECTED_FRONTIER_START},{EXPECTED_FRONTIER_END}), "
        f"certified_unsat={certified_unsat}, SAT=0, UNKNOWN=0, unresolved=0, "
        f"tail_nodes={len(nodes_rows)}, chunks={len(chunks)}, windows={len(windows)}, "
        f"rerun_rows={len(rerun)}"
    )


if __name__ == "__main__":
    main()
