#!/usr/bin/env python3
"""Manual optimized H1 evaluator runner for Stage 6.

This is a streaming exact evaluator for the unrestricted H1 range target. It
does not use SMT. A small C++ core evaluates rawH exactly over linear chunks of
the full 3^21 normal-coordinate landscape, while this Python wrapper handles
compilation, durable logs, CSV summaries, checkpoint/resume, and sharding.

Default counterexample thresholds:

    upper: rawH >= 1218  (H_tot > 7302)
    lower: rawH <= -379  (H_tot < -2268)

If either violation appears, H1 should be replaced by a corrected theorem with
the emitted witness. If a full range finishes with zero violations, the run is
an exact H1 closure artifact.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import shutil
import subprocess
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
VERIFY_PATH = SCRIPT_DIR.parent / "verify_stage6_bundle.py"
CORE_SOURCE = SCRIPT_DIR / "h1_eval_core.cpp"
CORE_BINARY = SCRIPT_DIR / "h1_eval_core"
TOTAL_POINTS = 3**21
DEFAULT_UPPER_TARGET_RAWH = 1218
DEFAULT_LOWER_TARGET_RAWH = -379

OUTPUT_FILES = (
    "events.log",
    "chunks.csv",
    "violations.csv",
    "checkpoint.json",
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
    "upper_violations",
    "lower_violations",
    "cumulative_points",
    "cumulative_upper_violations",
    "cumulative_lower_violations",
    "cumulative_min_rawH",
    "cumulative_max_rawH",
    "cumulative_min_word",
    "cumulative_max_word",
    "next_index",
]

VIOLATION_FIELDS = [
    "utc",
    "chunk_index",
    "query",
    "count_in_chunk",
    "first_index",
    "witness",
    "rawH",
    "H_tot",
    "metrics_json",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_verify_module():
    spec = importlib.util.spec_from_file_location("verify_stage6_for_h1_eval", VERIFY_PATH)
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


def log_event(run_dir: Path, message: str) -> None:
    line = f"{utc_now()} {message}"
    print(line, flush=True)
    with (run_dir / "events.log").open("a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def clear_run_dir(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    for name in OUTPUT_FILES:
        p = run_dir / name
        if p.exists():
            p.unlink()


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
    ap = argparse.ArgumentParser(description="Stream exact Stage-6 H1 range evaluation through a C++ core.")
    ap.add_argument("--start-index", type=nonnegative_int, default=0, help="First full-landscape linear index")
    ap.add_argument("--end-index", type=nonnegative_int, default=0, help="Exclusive end index; 0 means 3^21")
    ap.add_argument("--shard-index", type=nonnegative_int, default=0, help="Optional shard index in [0, shard-count)")
    ap.add_argument("--shard-count", type=positive_int, default=1, help="Optional number of equal full-landscape shards")
    ap.add_argument("--chunk-size", type=positive_int, default=1_000_000, help="Points per C++ core call")
    ap.add_argument("--upper-target-rawH", type=int, default=DEFAULT_UPPER_TARGET_RAWH, help="Upper counterexample threshold")
    ap.add_argument("--lower-target-rawH", type=int, default=DEFAULT_LOWER_TARGET_RAWH, help="Lower counterexample threshold")
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
    ap.add_argument("--continue-after-violation", action="store_true", help="Continue after a threshold violation")
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
        return SCRIPT_DIR / f"h1_eval_shard_{args.shard_index}_of_{args.shard_count}"
    return SCRIPT_DIR / f"h1_eval_{start}_{end}"


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
    stale = (
        not core_bin.is_file()
        or core_bin.stat().st_mtime < CORE_SOURCE.stat().st_mtime
    )
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
            "core failed with code "
            f"{proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return json.loads(proc.stdout)


def run_core_range(core_bin: Path, start: int, end: int, args: argparse.Namespace) -> dict[str, Any]:
    return run_core_json(
        core_bin,
        [
            "--start", str(start),
            "--end", str(end),
            "--upper-target", str(args.upper_target_rawH),
            "--lower-target", str(args.lower_target_rawH),
        ],
    )


def run_self_test(core_bin: Path, run_dir: Path) -> None:
    v = load_verify_module()
    words = [
        "111111111222222222000",
        "222222222111111111000",
        "000000000000000000000",
        "012012012120120120201",
        "222222222222222222222",
    ]
    keys = [
        "rawI", "rawB", "rawH", "H_tot", "N_neg", "h_loc_min", "h_loc_max",
        "H_RRR", "H_RRS", "H_RSR", "H_SRR", "H_DIST",
    ]
    for word in words:
        got = run_core_json(core_bin, ["--word", word])["metrics"]
        expected = v.h_metrics_reduced(word)
        mismatches = {k: (got.get(k), expected.get(k)) for k in keys if int(got.get(k)) != int(expected.get(k))}
        if mismatches:
            raise SystemExit(f"self-test mismatch for {word}: {mismatches}")
    log_event(run_dir, f"self-test PASS words={len(words)}")


def initial_totals() -> dict[str, Any]:
    return {
        "checked_points": 0,
        "upper_violations": 0,
        "lower_violations": 0,
        "min_rawH": None,
        "max_rawH": None,
        "min_word": "",
        "max_word": "",
        "min_index": 0,
        "max_index": 0,
    }


def update_totals(totals: dict[str, Any], result: dict[str, Any]) -> None:
    totals["checked_points"] = int(totals["checked_points"]) + int(result["points"])
    totals["upper_violations"] = int(totals["upper_violations"]) + int(result["upper_violations"])
    totals["lower_violations"] = int(totals["lower_violations"]) + int(result["lower_violations"])
    if totals["min_rawH"] is None or int(result["min_rawH"]) < int(totals["min_rawH"]):
        totals["min_rawH"] = int(result["min_rawH"])
        totals["min_word"] = result["min_word"]
        totals["min_index"] = int(result["min_index"])
    if totals["max_rawH"] is None or int(result["max_rawH"]) > int(totals["max_rawH"]):
        totals["max_rawH"] = int(result["max_rawH"])
        totals["max_word"] = result["max_word"]
        totals["max_index"] = int(result["max_index"])


def checkpoint_payload(
    *,
    args: argparse.Namespace,
    run_dir: Path,
    status: str,
    start: int,
    end: int,
    next_index: int,
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
        "remaining_points": max(0, end - next_index),
        "checked_points": int(totals["checked_points"]),
        "upper_violations": int(totals["upper_violations"]),
        "lower_violations": int(totals["lower_violations"]),
        "min_rawH": totals["min_rawH"],
        "max_rawH": totals["max_rawH"],
        "min_H_tot": None if totals["min_rawH"] is None else 6 * int(totals["min_rawH"]),
        "max_H_tot": None if totals["max_rawH"] is None else 6 * int(totals["max_rawH"]),
        "min_word": totals["min_word"],
        "max_word": totals["max_word"],
        "min_index": totals["min_index"],
        "max_index": totals["max_index"],
        "chunk_size": args.chunk_size,
        "upper_target_rawH": args.upper_target_rawH,
        "lower_target_rawH": args.lower_target_rawH,
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "time_limit_hours": args.time_limit_hours,
    }


def write_checkpoint(**kwargs: Any) -> None:
    atomic_write_json(kwargs["run_dir"] / "checkpoint.json", checkpoint_payload(**kwargs))


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
        "upper_target_rawH": args.upper_target_rawH,
        "lower_target_rawH": args.lower_target_rawH,
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
    totals = initial_totals()
    if checkpoint is not None:
        if int(checkpoint.get("start_index", start)) != start or int(checkpoint.get("end_index", end)) != end:
            raise SystemExit("checkpoint range does not match requested range")
        for key in ("chunk_size", "upper_target_rawH", "lower_target_rawH", "shard_index", "shard_count"):
            if int(checkpoint.get(key, getattr(args, key))) != int(getattr(args, key)):
                raise SystemExit(f"checkpoint {key} does not match requested value")
        current = int(checkpoint.get("next_index", start))
        for key in totals:
            if key in checkpoint:
                totals[key] = checkpoint[key]
        log_event(run_dir, f"resume next_index={current} checked_points={totals['checked_points']}")

    started_utc = utc_now()
    started_time = time.time()
    chunk_f, chunk_w = open_csv(run_dir / "chunks.csv", CHUNK_FIELDS)
    violation_f, violation_w = open_csv(run_dir / "violations.csv", VIOLATION_FIELDS)

    try:
        write_checkpoint(
            args=args,
            run_dir=run_dir,
            status="running",
            start=start,
            end=end,
            next_index=current,
            totals=totals,
            started_utc=started_utc,
            started_time=started_time,
        )

        chunk_index = 0 if current == start else int((current - start) // args.chunk_size)
        while current < end:
            if args.time_limit_hours > 0 and (time.time() - started_time) >= args.time_limit_hours * 3600.0:
                log_event(run_dir, f"time limit reached before chunk at index {current}")
                write_checkpoint(
                    args=args,
                    run_dir=run_dir,
                    status="time_limit",
                    start=start,
                    end=end,
                    next_index=current,
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
            update_totals(totals, result)
            current = chunk_end

            row = {
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
                "upper_violations": result["upper_violations"],
                "lower_violations": result["lower_violations"],
                "cumulative_points": totals["checked_points"],
                "cumulative_upper_violations": totals["upper_violations"],
                "cumulative_lower_violations": totals["lower_violations"],
                "cumulative_min_rawH": totals["min_rawH"],
                "cumulative_max_rawH": totals["max_rawH"],
                "cumulative_min_word": totals["min_word"],
                "cumulative_max_word": totals["max_word"],
                "next_index": current,
            }
            chunk_w.writerow(row)
            chunk_f.flush()

            if int(result["upper_violations"]):
                metrics = result["first_upper_metrics"]
                violation_w.writerow({
                    "utc": utc_now(),
                    "chunk_index": chunk_index,
                    "query": "upper",
                    "count_in_chunk": result["upper_violations"],
                    "first_index": result["first_upper_index"],
                    "witness": result["first_upper_word"],
                    "rawH": metrics["rawH"],
                    "H_tot": metrics["H_tot"],
                    "metrics_json": json.dumps(metrics, sort_keys=True),
                })
                violation_f.flush()
            if int(result["lower_violations"]):
                metrics = result["first_lower_metrics"]
                violation_w.writerow({
                    "utc": utc_now(),
                    "chunk_index": chunk_index,
                    "query": "lower",
                    "count_in_chunk": result["lower_violations"],
                    "first_index": result["first_lower_index"],
                    "witness": result["first_lower_word"],
                    "rawH": metrics["rawH"],
                    "H_tot": metrics["H_tot"],
                    "metrics_json": json.dumps(metrics, sort_keys=True),
                })
                violation_f.flush()

            status = "running"
            if int(totals["upper_violations"]) or int(totals["lower_violations"]):
                status = "violation_found"
            write_checkpoint(
                args=args,
                run_dir=run_dir,
                status=status,
                start=start,
                end=end,
                next_index=current,
                totals=totals,
                started_utc=started_utc,
                started_time=started_time,
            )
            log_event(
                run_dir,
                "CHUNK "
                f"index={chunk_index} range=[{chunk_start},{chunk_end}) points={result['points']} "
                f"rawH=[{result['min_rawH']},{result['max_rawH']}] "
                f"violations upper={result['upper_violations']} lower={result['lower_violations']} "
                f"seconds_core={float(result['seconds']):.3f} next={current}",
            )

            if status == "violation_found" and not args.continue_after_violation:
                log_event(run_dir, "stopping after H1 threshold violation; pass --continue-after-violation to keep scanning")
                return 2

            chunk_index += 1

        write_checkpoint(
            args=args,
            run_dir=run_dir,
            status="complete",
            start=start,
            end=end,
            next_index=current,
            totals=totals,
            started_utc=started_utc,
            started_time=started_time,
        )
        log_event(
            run_dir,
            "COMPLETE "
            f"points={totals['checked_points']} rawH=[{totals['min_rawH']},{totals['max_rawH']}] "
            f"violations upper={totals['upper_violations']} lower={totals['lower_violations']}",
        )
        return 0
    finally:
        chunk_f.close()
        violation_f.close()


if __name__ == "__main__":
    raise SystemExit(main())
