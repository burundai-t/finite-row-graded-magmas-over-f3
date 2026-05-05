#!/usr/bin/env python3
"""Manual Stage-6 H4 signed-cancellation classifier.

This runner streams the full 3^21 normal-coordinate landscape through a small
C++ core and aggregates only compact high-H signed-cancellation data. The
default H4 window is rawH >= 1171, i.e. H_tot > 7020, the region above the
closed pure frontier. Witness rows are separately captured for rawH >= 1217,
the known unrestricted H1 maximum.

Outputs are durable and resume-friendly:

* events.log
* chunks.csv
* chunk_pairs.csv      per-chunk (rawH, N_-) counts
* pair_counts.csv      cumulative (rawH, N_-) counts
* rawH_summary.csv     cumulative per-rawH signed summary
* witnesses.csv        captured high-boundary witnesses
* checkpoint.json
* summary.json
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
VERIFY_PATH = SCRIPT_DIR.parent / "verify_stage6_bundle.py"
CORE_SOURCE = SCRIPT_DIR / "h4_signed_core.cpp"
CORE_BINARY = SCRIPT_DIR / "h4_signed_core"
TOTAL_POINTS = 3**21
DEFAULT_PAIR_MIN_RAWH = 1171
DEFAULT_WITNESS_MIN_RAWH = 1217

OUTPUT_FILES = (
    "events.log",
    "chunks.csv",
    "chunk_pairs.csv",
    "pair_counts.csv",
    "rawH_summary.csv",
    "witnesses.csv",
    "checkpoint.json",
    "summary.json",
)

CHUNK_FIELDS = [
    "utc",
    "chunk_index",
    "start_index",
    "end_index",
    "points",
    "seconds_core",
    "seconds_wall",
    "min_rawH",
    "max_rawH",
    "min_H_tot",
    "max_H_tot",
    "min_index",
    "max_index",
    "min_word",
    "max_word",
    "min_count",
    "max_count",
    "min_N_neg",
    "max_N_neg_values",
    "high_points",
    "high_pure_points",
    "high_impure_points",
    "pair_count",
    "witness_count",
    "witness_overflow",
    "cumulative_points",
    "cumulative_high_points",
    "cumulative_high_pure_points",
    "cumulative_high_impure_points",
    "cumulative_min_rawH",
    "cumulative_max_rawH",
    "cumulative_max_count",
    "cumulative_max_N_neg_values",
    "stored_witnesses",
    "cumulative_witness_overflow",
    "next_index",
]

PAIR_FIELDS = [
    "utc",
    "chunk_index",
    "rawH",
    "H_tot",
    "N_neg",
    "count",
    "first_index",
    "first_word",
    "min_H_pos",
    "max_H_pos",
    "min_H_neg_abs",
    "max_H_neg_abs",
    "min_h_loc_min",
    "max_h_loc_min",
    "min_h_loc_max",
    "max_h_loc_max",
    "first_metrics_json",
]

CUM_PAIR_FIELDS = [field for field in PAIR_FIELDS if field not in ("utc", "chunk_index")]

RAWH_FIELDS = [
    "rawH",
    "H_tot",
    "count",
    "pure_count",
    "impure_count",
    "pair_count",
    "min_N_neg",
    "max_N_neg",
    "N_neg_values",
    "first_index",
    "first_word",
]

WITNESS_FIELDS = [
    "utc",
    "chunk_index",
    "index",
    "word",
    "rawH",
    "H_tot",
    "N_neg",
    "H_pos",
    "H_neg_abs",
    "h_loc_min",
    "h_loc_max",
    "metrics_json",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_verify_module():
    spec = importlib.util.spec_from_file_location("verify_stage6_for_h4", VERIFY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load verifier from {VERIFY_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def open_csv(path: Path, fields: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.is_file() and path.stat().st_size > 0
    f = path.open("a", encoding="utf-8", newline="")
    writer = csv.DictWriter(f, fieldnames=fields)
    if not exists:
        writer.writeheader()
        f.flush()
    return f, writer


def atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n")


def atomic_write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    tmp.replace(path)


def log_event(run_dir: Path, message: str) -> None:
    line = f"{utc_now()} {message}"
    print(line, flush=True)
    with (run_dir / "events.log").open("a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()


def clear_run_dir(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    for name in OUTPUT_FILES:
        path = run_dir / name
        if path.exists():
            path.unlink()


def existing_output_present(run_dir: Path) -> bool:
    return any((run_dir / name).exists() for name in OUTPUT_FILES)


def read_checkpoint(run_dir: Path) -> dict[str, Any] | None:
    path = run_dir / "checkpoint.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def positive_int(value: str) -> int:
    out = int(value)
    if out <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return out


def nonnegative_int(value: str) -> int:
    out = int(value)
    if out < 0:
        raise argparse.ArgumentTypeError("must be nonnegative")
    return out


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Stream exact Stage-6 H4 signed-cancellation classification.")
    ap.add_argument("--start-index", type=nonnegative_int, default=0, help="First full-landscape linear index")
    ap.add_argument("--end-index", type=nonnegative_int, default=0, help="Exclusive end index; 0 means 3^21")
    ap.add_argument("--shard-index", type=nonnegative_int, default=0, help="Optional shard index in [0, shard-count)")
    ap.add_argument("--shard-count", type=positive_int, default=1, help="Optional number of equal full-landscape shards")
    ap.add_argument("--chunk-size", type=positive_int, default=5_000_000, help="Points per C++ core call")
    ap.add_argument("--pair-min-rawH", type=int, default=DEFAULT_PAIR_MIN_RAWH, help="Aggregate (rawH,N_-) pairs for rawH at least this value")
    ap.add_argument("--witness-min-rawH", type=int, default=DEFAULT_WITNESS_MIN_RAWH, help="Store individual witnesses for rawH at least this value")
    ap.add_argument("--witness-limit-per-chunk", type=nonnegative_int, default=100000, help="Max stored witnesses per C++ chunk")
    ap.add_argument("--run-dir", type=Path, default=None, help="Output directory")
    ap.add_argument("--core-bin", type=Path, default=CORE_BINARY, help="Compiled C++ core path")
    ap.add_argument("--compiler", default="", help="C++ compiler path; default auto-detects clang++/g++")
    ap.add_argument("--compile-only", action="store_true", help="Compile the C++ core and exit")
    ap.add_argument("--no-compile", action="store_true", help="Do not compile even if the core is missing/stale")
    ap.add_argument("--self-test", action="store_true", help="Run C++ core self-checks against verify_stage6.py before the range")
    ap.add_argument("--self-test-only", action="store_true", help="Run self-checks and exit before range evaluation")
    ap.add_argument("--resume", action="store_true", help="Resume from checkpoint.json in run-dir")
    ap.add_argument("--force", action="store_true", help="Clear existing runner output files before starting")
    ap.add_argument("--dry-run", action="store_true", help="Print the plan and exit")
    ap.add_argument("--max-points", type=int, default=0, help="Optional cap for smoke runs; 0 means no cap")
    ap.add_argument("--time-limit-hours", type=float, default=0.0, help="Stop cleanly after this many hours; 0 means no cap")
    return ap


def shard_range(args: argparse.Namespace) -> tuple[int, int]:
    if args.shard_index >= args.shard_count:
        raise SystemExit("--shard-index must be smaller than --shard-count")
    shard_start = (TOTAL_POINTS * args.shard_index) // args.shard_count
    shard_end = (TOTAL_POINTS * (args.shard_index + 1)) // args.shard_count
    start = args.start_index
    end = args.end_index or TOTAL_POINTS
    if args.shard_count > 1:
        start = max(start, shard_start)
        end = min(end, shard_end)
    if end > TOTAL_POINTS:
        raise SystemExit(f"--end-index exceeds 3^21={TOTAL_POINTS}")
    if end <= start:
        raise SystemExit("empty range after applying start/end/shard options")
    return start, end


def default_run_dir(args: argparse.Namespace, start: int, end: int) -> Path:
    if args.shard_count > 1:
        return SCRIPT_DIR / f"h4_signed_shard_{args.shard_index}_of_{args.shard_count}"
    return SCRIPT_DIR / f"h4_signed_{start}_{end}"


def find_compiler(args: argparse.Namespace) -> str:
    if args.compiler:
        return args.compiler
    for name in ("clang++", "g++"):
        path = shutil.which(name)
        if path:
            return path
    raise SystemExit("no C++ compiler found; install clang++/g++ or pass --compiler")


def compile_core(args: argparse.Namespace, run_dir: Path) -> Path:
    core_bin = args.core_bin.resolve()
    if args.no_compile:
        if not core_bin.is_file():
            raise SystemExit(f"{core_bin} does not exist and --no-compile was passed")
        return core_bin
    stale = not core_bin.is_file() or core_bin.stat().st_mtime < CORE_SOURCE.stat().st_mtime
    if not stale:
        return core_bin
    compiler = find_compiler(args)
    core_bin.parent.mkdir(parents=True, exist_ok=True)
    cmd = [compiler, "-O3", "-std=c++17", str(CORE_SOURCE), "-o", str(core_bin)]
    log_event(run_dir, "compile " + " ".join(cmd))
    started = time.time()
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        raise SystemExit(f"core compile failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    log_event(run_dir, f"compile done seconds={time.time() - started:.3f} core={core_bin}")
    return core_bin


def run_core_json(core_bin: Path, args: list[str]) -> dict[str, Any]:
    proc = subprocess.run([str(core_bin)] + args, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"core failed code={proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return json.loads(proc.stdout)


def run_core_range(core_bin: Path, start: int, end: int, args: argparse.Namespace) -> dict[str, Any]:
    return run_core_json(
        core_bin,
        [
            "--start", str(start),
            "--end", str(end),
            "--pair-min-rawH", str(args.pair_min_rawH),
            "--witness-min-rawH", str(args.witness_min_rawH),
            "--witness-limit", str(args.witness_limit_per_chunk),
        ],
    )


def run_self_test(core_bin: Path, run_dir: Path) -> None:
    v = load_verify_module()
    words = [
        "111111111222222222000",
        "222222222111111111000",
        "000000000111111111220",
        "012120201012120201012",
        "000000000000000000000",
        "222222222222222222222",
    ]
    keys = [
        "rawI", "rawB", "rawH", "H_tot", "H_pos", "H_neg_abs", "N_neg",
        "h_loc_min", "h_loc_max", "H_RRR", "H_RRS", "H_RSR", "H_SRR", "H_DIST",
    ]
    for word in words:
        got = run_core_json(core_bin, ["--word", word])["metrics"]
        expected = v.h_metrics_reduced(word)
        mismatches = {k: (got.get(k), expected.get(k)) for k in keys if int(got.get(k)) != int(expected.get(k))}
        if mismatches:
            raise SystemExit(f"self-test mismatch for {word}: {mismatches}")
    log_event(run_dir, f"self-test PASS words={len(words)}")


def pair_key(rawH: int, N_neg: int) -> str:
    return f"{rawH}|{N_neg}"


def split_pair_key(key: str) -> tuple[int, int]:
    rawH_s, N_s = key.split("|", 1)
    return int(rawH_s), int(N_s)


def normalize_pair(pair: dict[str, Any]) -> dict[str, Any]:
    return {
        "rawH": int(pair["rawH"]),
        "H_tot": int(pair["H_tot"]),
        "N_neg": int(pair["N_neg"]),
        "count": int(pair["count"]),
        "first_index": int(pair["first_index"]),
        "first_word": str(pair["first_word"]),
        "min_H_pos": int(pair["min_H_pos"]),
        "max_H_pos": int(pair["max_H_pos"]),
        "min_H_neg_abs": int(pair["min_H_neg_abs"]),
        "max_H_neg_abs": int(pair["max_H_neg_abs"]),
        "min_h_loc_min": int(pair["min_h_loc_min"]),
        "max_h_loc_min": int(pair["max_h_loc_min"]),
        "min_h_loc_max": int(pair["min_h_loc_max"]),
        "max_h_loc_max": int(pair["max_h_loc_max"]),
        "first_metrics": dict(pair["first_metrics"]),
    }


def merge_pair(pairs: dict[str, dict[str, Any]], pair: dict[str, Any]) -> None:
    row = normalize_pair(pair)
    key = pair_key(row["rawH"], row["N_neg"])
    old = pairs.get(key)
    if old is None:
        pairs[key] = row
        return
    old["count"] = int(old["count"]) + row["count"]
    if row["first_index"] < int(old["first_index"]):
        old["first_index"] = row["first_index"]
        old["first_word"] = row["first_word"]
        old["first_metrics"] = row["first_metrics"]
    for field in ("H_pos", "H_neg_abs", "h_loc_min", "h_loc_max"):
        old[f"min_{field}"] = min(int(old[f"min_{field}"]), int(row[f"min_{field}"]))
        old[f"max_{field}"] = max(int(old[f"max_{field}"]), int(row[f"max_{field}"]))


def initial_totals() -> dict[str, Any]:
    return {
        "checked_points": 0,
        "high_points": 0,
        "high_pure_points": 0,
        "high_impure_points": 0,
        "min_rawH": None,
        "max_rawH": None,
        "min_count": 0,
        "max_count": 0,
        "min_word": "",
        "max_word": "",
        "min_index": 0,
        "max_index": 0,
        "min_metrics": {},
        "max_metrics": {},
        "max_N_neg_values": [],
        "stored_witnesses": 0,
        "witness_overflow": 0,
        "pairs": {},
    }


def result_max_N_values(result: dict[str, Any]) -> list[int]:
    max_rawH = int(result["max_rawH"])
    values = sorted({int(p["N_neg"]) for p in result.get("pairs", []) if int(p["rawH"]) == max_rawH})
    if values:
        return values
    return [int(result["max_metrics"]["N_neg"])]


def update_totals(totals: dict[str, Any], result: dict[str, Any]) -> None:
    totals["checked_points"] = int(totals["checked_points"]) + int(result["points"])
    totals["high_points"] = int(totals["high_points"]) + int(result["high_points"])
    totals["high_pure_points"] = int(totals["high_pure_points"]) + int(result["high_pure_points"])
    totals["high_impure_points"] = int(totals["high_impure_points"]) + int(result["high_impure_points"])
    totals["stored_witnesses"] = int(totals["stored_witnesses"]) + int(result["witness_count"])
    totals["witness_overflow"] = int(totals["witness_overflow"]) + int(result["witness_overflow"])

    if totals["min_rawH"] is None or int(result["min_rawH"]) < int(totals["min_rawH"]):
        totals["min_rawH"] = int(result["min_rawH"])
        totals["min_count"] = int(result["min_count"])
        totals["min_word"] = result["min_word"]
        totals["min_index"] = int(result["min_index"])
        totals["min_metrics"] = result["min_metrics"]
    elif int(result["min_rawH"]) == int(totals["min_rawH"]):
        totals["min_count"] = int(totals["min_count"]) + int(result["min_count"])

    if totals["max_rawH"] is None or int(result["max_rawH"]) > int(totals["max_rawH"]):
        totals["max_rawH"] = int(result["max_rawH"])
        totals["max_count"] = int(result["max_count"])
        totals["max_word"] = result["max_word"]
        totals["max_index"] = int(result["max_index"])
        totals["max_metrics"] = result["max_metrics"]
        totals["max_N_neg_values"] = result_max_N_values(result)
    elif int(result["max_rawH"]) == int(totals["max_rawH"]):
        totals["max_count"] = int(totals["max_count"]) + int(result["max_count"])
        values = set(int(x) for x in totals["max_N_neg_values"])
        values.update(result_max_N_values(result))
        totals["max_N_neg_values"] = sorted(values)

    for pair in result.get("pairs", []):
        merge_pair(totals["pairs"], pair)


def pair_rows(pairs: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in sorted(pairs, key=lambda k: (-split_pair_key(k)[0], split_pair_key(k)[1])):
        p = pairs[key]
        rows.append({
            "rawH": p["rawH"],
            "H_tot": p["H_tot"],
            "N_neg": p["N_neg"],
            "count": p["count"],
            "first_index": p["first_index"],
            "first_word": p["first_word"],
            "min_H_pos": p["min_H_pos"],
            "max_H_pos": p["max_H_pos"],
            "min_H_neg_abs": p["min_H_neg_abs"],
            "max_H_neg_abs": p["max_H_neg_abs"],
            "min_h_loc_min": p["min_h_loc_min"],
            "max_h_loc_min": p["max_h_loc_min"],
            "min_h_loc_max": p["min_h_loc_max"],
            "max_h_loc_max": p["max_h_loc_max"],
            "first_metrics_json": json.dumps(p["first_metrics"], sort_keys=True),
        })
    return rows


def rawH_summary_rows(pairs: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    tmp: dict[int, dict[str, Any]] = {}
    for p in pairs.values():
        rawH = int(p["rawH"])
        N_neg = int(p["N_neg"])
        row = tmp.setdefault(rawH, {
            "rawH": rawH,
            "H_tot": 6 * rawH,
            "count": 0,
            "pure_count": 0,
            "impure_count": 0,
            "pair_count": 0,
            "N_values": set(),
            "first_index": int(p["first_index"]),
            "first_word": p["first_word"],
        })
        row["count"] += int(p["count"])
        row["pair_count"] += 1
        row["N_values"].add(N_neg)
        if N_neg == 0:
            row["pure_count"] += int(p["count"])
        else:
            row["impure_count"] += int(p["count"])
        if int(p["first_index"]) < int(row["first_index"]):
            row["first_index"] = int(p["first_index"])
            row["first_word"] = p["first_word"]
    out = []
    for rawH in sorted(tmp, reverse=True):
        row = tmp[rawH]
        values = sorted(row["N_values"])
        out.append({
            "rawH": row["rawH"],
            "H_tot": row["H_tot"],
            "count": row["count"],
            "pure_count": row["pure_count"],
            "impure_count": row["impure_count"],
            "pair_count": row["pair_count"],
            "min_N_neg": values[0],
            "max_N_neg": values[-1],
            "N_neg_values": "/".join(str(x) for x in values),
            "first_index": row["first_index"],
            "first_word": row["first_word"],
        })
    return out


def checkpoint_payload(
    *,
    args: argparse.Namespace,
    run_dir: Path,
    status: str,
    start: int,
    end: int,
    next_index: int,
    next_chunk_index: int,
    totals: dict[str, Any],
    started_utc: str,
    started_time: float,
) -> dict[str, Any]:
    return {
        "status": status,
        "started_utc": started_utc,
        "updated_utc": utc_now(),
        "elapsed_seconds": round(time.time() - started_time, 3),
        "run_dir": str(run_dir),
        "start_index": start,
        "end_index": end,
        "next_index": next_index,
        "next_chunk_index": next_chunk_index,
        "remaining_points": max(0, end - next_index),
        "checked_points": int(totals["checked_points"]),
        "high_points": int(totals["high_points"]),
        "high_pure_points": int(totals["high_pure_points"]),
        "high_impure_points": int(totals["high_impure_points"]),
        "min_rawH": totals["min_rawH"],
        "max_rawH": totals["max_rawH"],
        "min_H_tot": None if totals["min_rawH"] is None else 6 * int(totals["min_rawH"]),
        "max_H_tot": None if totals["max_rawH"] is None else 6 * int(totals["max_rawH"]),
        "min_count": int(totals["min_count"]),
        "max_count": int(totals["max_count"]),
        "min_word": totals["min_word"],
        "max_word": totals["max_word"],
        "min_index": totals["min_index"],
        "max_index": totals["max_index"],
        "min_metrics": totals["min_metrics"],
        "max_metrics": totals["max_metrics"],
        "max_N_neg_values": [int(x) for x in totals["max_N_neg_values"]],
        "pair_count": len(totals["pairs"]),
        "pairs": totals["pairs"],
        "stored_witnesses": int(totals["stored_witnesses"]),
        "witness_overflow": int(totals["witness_overflow"]),
        "chunk_size": args.chunk_size,
        "pair_min_rawH": args.pair_min_rawH,
        "witness_min_rawH": args.witness_min_rawH,
        "witness_limit_per_chunk": args.witness_limit_per_chunk,
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "time_limit_hours": args.time_limit_hours,
    }


def write_outputs(
    *,
    args: argparse.Namespace,
    run_dir: Path,
    status: str,
    start: int,
    end: int,
    next_index: int,
    next_chunk_index: int,
    totals: dict[str, Any],
    started_utc: str,
    started_time: float,
) -> None:
    checkpoint = checkpoint_payload(
        args=args,
        run_dir=run_dir,
        status=status,
        start=start,
        end=end,
        next_index=next_index,
        next_chunk_index=next_chunk_index,
        totals=totals,
        started_utc=started_utc,
        started_time=started_time,
    )
    atomic_write_json(run_dir / "checkpoint.json", checkpoint)
    pairs = pair_rows(totals["pairs"])
    raw_rows = rawH_summary_rows(totals["pairs"])
    atomic_write_csv(run_dir / "pair_counts.csv", CUM_PAIR_FIELDS, pairs)
    atomic_write_csv(run_dir / "rawH_summary.csv", RAWH_FIELDS, raw_rows)
    summary = {
        k: checkpoint[k]
        for k in (
            "status", "start_index", "end_index", "next_index", "remaining_points",
            "checked_points", "high_points", "high_pure_points", "high_impure_points",
            "min_rawH", "max_rawH", "min_H_tot", "max_H_tot", "min_count", "max_count",
            "min_word", "max_word", "max_N_neg_values", "pair_count",
            "stored_witnesses", "witness_overflow", "pair_min_rawH", "witness_min_rawH",
        )
    }
    summary["rawH_values"] = [int(r["rawH"]) for r in raw_rows]
    atomic_write_json(run_dir / "summary.json", summary)


def restore_totals(checkpoint: dict[str, Any]) -> dict[str, Any]:
    totals = initial_totals()
    for key in totals:
        if key in checkpoint:
            totals[key] = checkpoint[key]
    totals["pairs"] = {str(k): normalize_pair(v) for k, v in dict(checkpoint.get("pairs", {})).items()}
    totals["max_N_neg_values"] = [int(x) for x in checkpoint.get("max_N_neg_values", [])]
    return totals


def max_N_values_text(values: list[int]) -> str:
    return "/".join(str(int(x)) for x in sorted(values))


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    start, end = shard_range(args)
    if args.max_points > 0:
        end = min(end, start + args.max_points)
    run_dir = (args.run_dir or default_run_dir(args, start, end)).resolve()

    if args.force and args.resume:
        raise SystemExit("--force and --resume are mutually exclusive")
    if args.force:
        clear_run_dir(run_dir)
    else:
        run_dir.mkdir(parents=True, exist_ok=True)
    if existing_output_present(run_dir) and not args.resume and not args.force and not args.compile_only:
        raise SystemExit(f"{run_dir} already contains runner output; pass --resume or choose a new --run-dir")

    plan = {
        "start_index": start,
        "end_index": end,
        "points": end - start,
        "chunk_size": args.chunk_size,
        "pair_min_rawH": args.pair_min_rawH,
        "witness_min_rawH": args.witness_min_rawH,
        "witness_limit_per_chunk": args.witness_limit_per_chunk,
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "run_dir": str(run_dir),
        "core_source": str(CORE_SOURCE),
        "core_bin": str(args.core_bin.resolve()),
    }
    log_event(run_dir, "plan " + json.dumps(plan, sort_keys=True))

    if args.dry_run:
        return 0

    core_bin = compile_core(args, run_dir)
    if args.compile_only:
        return 0
    if args.self_test or args.self_test_only:
        run_self_test(core_bin, run_dir)
    if args.self_test_only:
        return 0

    checkpoint = read_checkpoint(run_dir) if args.resume else None
    current = start
    chunk_index = 0
    totals = initial_totals()
    if checkpoint is not None:
        if int(checkpoint.get("start_index", start)) != start or int(checkpoint.get("end_index", end)) != end:
            raise SystemExit("checkpoint range does not match requested range")
        for key in ("chunk_size", "pair_min_rawH", "witness_min_rawH", "witness_limit_per_chunk", "shard_index", "shard_count"):
            if int(checkpoint.get(key, getattr(args, key))) != int(getattr(args, key)):
                raise SystemExit(f"checkpoint {key} does not match requested value")
        current = int(checkpoint.get("next_index", start))
        chunk_index = int(checkpoint.get("next_chunk_index", 0))
        totals = restore_totals(checkpoint)
        log_event(run_dir, f"resume next_index={current} chunk_index={chunk_index} checked_points={totals['checked_points']}")

    started_utc = utc_now()
    started_time = time.time()
    chunk_f, chunk_w = open_csv(run_dir / "chunks.csv", CHUNK_FIELDS)
    pair_f, pair_w = open_csv(run_dir / "chunk_pairs.csv", PAIR_FIELDS)
    witness_f, witness_w = open_csv(run_dir / "witnesses.csv", WITNESS_FIELDS)

    try:
        write_outputs(
            args=args,
            run_dir=run_dir,
            status="running",
            start=start,
            end=end,
            next_index=current,
            next_chunk_index=chunk_index,
            totals=totals,
            started_utc=started_utc,
            started_time=started_time,
        )

        while current < end:
            if args.time_limit_hours > 0 and (time.time() - started_time) >= args.time_limit_hours * 3600.0:
                log_event(run_dir, f"time limit reached before chunk at index {current}")
                write_outputs(
                    args=args,
                    run_dir=run_dir,
                    status="time_limit",
                    start=start,
                    end=end,
                    next_index=current,
                    next_chunk_index=chunk_index,
                    totals=totals,
                    started_utc=started_utc,
                    started_time=started_time,
                )
                return 0

            chunk_start = current
            chunk_end = min(end, chunk_start + args.chunk_size)
            wall_start = time.time()
            result = run_core_range(core_bin, chunk_start, chunk_end, args)
            wall_seconds = time.time() - wall_start
            chunk_max_N_values = result_max_N_values(result)
            update_totals(totals, result)
            current = chunk_end

            chunk_row = {
                "utc": utc_now(),
                "chunk_index": chunk_index,
                "start_index": chunk_start,
                "end_index": chunk_end,
                "points": result["points"],
                "seconds_core": round(float(result["seconds"]), 3),
                "seconds_wall": round(wall_seconds, 3),
                "min_rawH": result["min_rawH"],
                "max_rawH": result["max_rawH"],
                "min_H_tot": result["min_H_tot"],
                "max_H_tot": result["max_H_tot"],
                "min_index": result["min_index"],
                "max_index": result["max_index"],
                "min_word": result["min_word"],
                "max_word": result["max_word"],
                "min_count": result["min_count"],
                "max_count": result["max_count"],
                "min_N_neg": result["min_metrics"]["N_neg"],
                "max_N_neg_values": max_N_values_text(chunk_max_N_values),
                "high_points": result["high_points"],
                "high_pure_points": result["high_pure_points"],
                "high_impure_points": result["high_impure_points"],
                "pair_count": result["pair_count"],
                "witness_count": result["witness_count"],
                "witness_overflow": result["witness_overflow"],
                "cumulative_points": totals["checked_points"],
                "cumulative_high_points": totals["high_points"],
                "cumulative_high_pure_points": totals["high_pure_points"],
                "cumulative_high_impure_points": totals["high_impure_points"],
                "cumulative_min_rawH": totals["min_rawH"],
                "cumulative_max_rawH": totals["max_rawH"],
                "cumulative_max_count": totals["max_count"],
                "cumulative_max_N_neg_values": max_N_values_text(totals["max_N_neg_values"]),
                "stored_witnesses": totals["stored_witnesses"],
                "cumulative_witness_overflow": totals["witness_overflow"],
                "next_index": current,
            }
            chunk_w.writerow(chunk_row)
            chunk_f.flush()

            for pair in result.get("pairs", []):
                p = normalize_pair(pair)
                pair_w.writerow({
                    "utc": utc_now(),
                    "chunk_index": chunk_index,
                    "rawH": p["rawH"],
                    "H_tot": p["H_tot"],
                    "N_neg": p["N_neg"],
                    "count": p["count"],
                    "first_index": p["first_index"],
                    "first_word": p["first_word"],
                    "min_H_pos": p["min_H_pos"],
                    "max_H_pos": p["max_H_pos"],
                    "min_H_neg_abs": p["min_H_neg_abs"],
                    "max_H_neg_abs": p["max_H_neg_abs"],
                    "min_h_loc_min": p["min_h_loc_min"],
                    "max_h_loc_min": p["max_h_loc_min"],
                    "min_h_loc_max": p["min_h_loc_max"],
                    "max_h_loc_max": p["max_h_loc_max"],
                    "first_metrics_json": json.dumps(p["first_metrics"], sort_keys=True),
                })
            pair_f.flush()

            for item in result.get("witnesses", []):
                metrics = item["metrics"]
                witness_w.writerow({
                    "utc": utc_now(),
                    "chunk_index": chunk_index,
                    "index": item["index"],
                    "word": item["word"],
                    "rawH": metrics["rawH"],
                    "H_tot": metrics["H_tot"],
                    "N_neg": metrics["N_neg"],
                    "H_pos": metrics["H_pos"],
                    "H_neg_abs": metrics["H_neg_abs"],
                    "h_loc_min": metrics["h_loc_min"],
                    "h_loc_max": metrics["h_loc_max"],
                    "metrics_json": json.dumps(metrics, sort_keys=True),
                })
            witness_f.flush()

            chunk_index += 1
            status = "complete" if current >= end else "running"
            write_outputs(
                args=args,
                run_dir=run_dir,
                status=status,
                start=start,
                end=end,
                next_index=current,
                next_chunk_index=chunk_index,
                totals=totals,
                started_utc=started_utc,
                started_time=started_time,
            )
            log_event(
                run_dir,
                "CHUNK "
                f"index={chunk_index - 1} range=[{chunk_start},{chunk_end}) points={result['points']} "
                f"rawH=[{result['min_rawH']},{result['max_rawH']}] "
                f"high={result['high_points']} pure_high={result['high_pure_points']} "
                f"pairs={result['pair_count']} witnesses={result['witness_count']} "
                f"seconds_core={float(result['seconds']):.3f} next={current}",
            )

        log_event(
            run_dir,
            "COMPLETE "
            f"points={totals['checked_points']} rawH=[{totals['min_rawH']},{totals['max_rawH']}] "
            f"high={totals['high_points']} pure_high={totals['high_pure_points']} "
            f"max_count={totals['max_count']} max_N={max_N_values_text(totals['max_N_neg_values'])}",
        )
        return 0
    finally:
        chunk_f.close()
        pair_f.close()
        witness_f.close()


if __name__ == "__main__":
    raise SystemExit(main())
