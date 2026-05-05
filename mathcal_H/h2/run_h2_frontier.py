#!/usr/bin/env python3
"""Overnight H2 pure-frontier SMT runner for Stage 6.

This script is intentionally a streaming runner, not a theorem-table updater.
It processes depth-9 live frontier nodes with the pure high-H query

    pure constraints and rawH >= 1171

and writes durable CSV/TXT artifacts as it goes. It keeps only the generated
frontier domains and the current SMT context in memory; per-node results are
flushed to disk immediately and summarized through checkpoint.json.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import shutil
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
VERIFY_PATH = SCRIPT_DIR.parent / "verify_stage6_bundle.py"

OUTPUT_FILES = (
    "events.log",
    "nodes.csv",
    "chunks.csv",
    "windows.csv",
    "unknown.csv",
    "sat.csv",
    "checkpoint.json",
)

NODE_FIELDS = [
    "utc",
    "window_index",
    "chunk_index",
    "node_index",
    "answer",
    "seconds",
    "fixed_count",
    "fixed_signature",
    "reason",
]
CHUNK_FIELDS = [
    "utc",
    "window_index",
    "chunk_index",
    "offset",
    "end_offset",
    "nodes",
    "unsat",
    "sat",
    "unknown",
    "seconds",
    "cumulative_checked",
    "cumulative_unsat",
    "cumulative_sat",
    "cumulative_unknown",
    "next_offset",
]
WINDOW_FIELDS = [
    "utc",
    "window_index",
    "offset",
    "end_offset",
    "nodes",
    "unsat",
    "sat",
    "unknown",
    "build_seconds",
    "check_seconds",
    "elapsed_seconds",
    "next_offset",
]
UNKNOWN_FIELDS = [
    "utc",
    "window_index",
    "chunk_index",
    "node_index",
    "seconds",
    "fixed_signature",
    "reason",
]
SAT_FIELDS = [
    "utc",
    "window_index",
    "chunk_index",
    "node_index",
    "seconds",
    "fixed_signature",
    "witness",
    "metrics_json",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_verify_module():
    spec = importlib.util.spec_from_file_location("verify_stage6_for_overnight", VERIFY_PATH)
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


def processed_state_from_nodes(nodes_csv: Path, start_offset: int) -> tuple[int, Counter]:
    if not nodes_csv.is_file():
        return start_offset, Counter()
    answers_by_node: dict[int, str] = {}
    with nodes_csv.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            try:
                node_index = int(row["node_index"])
            except Exception:
                continue
            answers_by_node[node_index] = row.get("answer", "")
    next_offset = start_offset
    while next_offset in answers_by_node:
        next_offset += 1
    counts = Counter(answers_by_node[i] for i in range(start_offset, next_offset))
    return next_offset, counts


def checkpoint_payload(
    *,
    args: argparse.Namespace,
    run_dir: Path,
    next_offset: int,
    totals: Counter,
    status: str,
    frontier_total: int,
    effective_end: int,
    started_utc: str,
    elapsed_seconds: float,
) -> dict[str, Any]:
    checked = sum(totals.values())
    return {
        "status": status,
        "started_utc": started_utc,
        "updated_utc": utc_now(),
        "elapsed_seconds": round(elapsed_seconds, 3),
        "run_dir": str(run_dir),
        "depth": args.depth,
        "start_offset": args.start_offset,
        "end_offset": args.end_offset,
        "effective_end_offset": effective_end,
        "frontier_total": frontier_total,
        "next_offset": next_offset,
        "remaining_nodes": max(0, effective_end - next_offset),
        "checked_nodes": checked,
        "unsat_nodes": totals.get("unsat", 0),
        "sat_nodes": totals.get("sat", 0),
        "unknown_nodes": totals.get("unknown", 0),
        "chunk_size": args.chunk_size,
        "window_chunks": args.window_chunks,
        "window_nodes": args.chunk_size * args.window_chunks,
        "target_rawH": args.target_rawH,
        "timeout_ms": args.timeout_ms,
        "time_limit_hours": args.time_limit_hours,
    }


def write_checkpoint(
    *,
    args: argparse.Namespace,
    run_dir: Path,
    next_offset: int,
    totals: Counter,
    status: str,
    frontier_total: int,
    effective_end: int,
    started_utc: str,
    started_time: float,
) -> None:
    atomic_write_json(
        run_dir / "checkpoint.json",
        checkpoint_payload(
            args=args,
            run_dir=run_dir,
            next_offset=next_offset,
            totals=totals,
            status=status,
            frontier_total=frontier_total,
            effective_end=effective_end,
            started_utc=started_utc,
            elapsed_seconds=time.time() - started_time,
        ),
    )


def positive_int(value: str) -> int:
    out = int(value)
    if out <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return out


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Stream a long Stage-6 H2 depth-9 SMT frontier run to CSV/TXT artifacts.")
    ap.add_argument("--depth", type=int, default=9, help="Branch frontier depth; H2 production runs use depth 9")
    ap.add_argument("--start-offset", type=int, default=4860, help="First depth-9 live-frontier offset to process")
    ap.add_argument("--end-offset", type=int, default=18540, help="Exclusive live-frontier end offset; use 0 for frontier total")
    ap.add_argument("--chunk-size", type=positive_int, default=162, help="Chunk size for streaming summaries")
    ap.add_argument("--window-chunks", type=positive_int, default=8, help="Chunks per SMT context rebuild window")
    ap.add_argument("--timeout-ms", type=positive_int, default=300000, help="Z3 timeout per node check")
    ap.add_argument("--target-rawH", type=int, default=1171, help="RawH lower bound for pure high-H query")
    ap.add_argument("--run-dir", type=Path, default=None, help="Output directory; default is stage6/overnight_h2_<start>_<end>")
    ap.add_argument("--resume", action="store_true", help="Resume from checkpoint/nodes.csv in run-dir")
    ap.add_argument("--force", action="store_true", help="Clear existing run-dir output files before starting")
    ap.add_argument("--dry-run", action="store_true", help="Print the plan and exit without building Z3 context")
    ap.add_argument("--max-nodes", type=int, default=0, help="Optional cap for smoke runs; 0 means no cap")
    ap.add_argument("--time-limit-hours", type=float, default=0.0, help="Stop cleanly after this many hours; 0 means no wall-clock cap")
    ap.add_argument("--continue-after-sat", action="store_true", help="Continue after SAT instead of stopping at the first witness")
    ap.add_argument("--stop-on-unknown", action="store_true", help="Stop cleanly at the first UNKNOWN")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    if args.start_offset < 0:
        raise SystemExit("--start-offset must be nonnegative")
    if args.end_offset < 0:
        raise SystemExit("--end-offset must be nonnegative")
    if args.window_chunks <= 0 or args.chunk_size <= 0:
        raise SystemExit("--chunk-size and --window-chunks must be positive")

    end_label = args.end_offset if args.end_offset else "frontier"
    run_dir = args.run_dir or (SCRIPT_DIR / f"overnight_h2_{args.start_offset}_{end_label}")
    run_dir = run_dir.resolve()

    if args.force and args.resume:
        raise SystemExit("--force and --resume are mutually exclusive")
    if args.force:
        clear_run_dir(run_dir)
    else:
        run_dir.mkdir(parents=True, exist_ok=True)
    if existing_output_present(run_dir) and not args.resume and not args.force:
        raise SystemExit(f"{run_dir} already contains runner output; pass --resume or choose a new --run-dir")

    v = load_verify_module()
    frontier_total = int(v.BRANCH3_EXPECTED_D9["live_nodes"]) if args.depth == v.BRANCH3_REFERENCE_DEPTH else 0
    if args.end_offset == 0:
        if frontier_total <= 0:
            raise SystemExit("--end-offset 0 is only supported for the reference depth")
        args.end_offset = frontier_total
    if args.end_offset <= args.start_offset:
        raise SystemExit("--end-offset must be greater than --start-offset")
    if frontier_total and args.end_offset > frontier_total:
        raise SystemExit(f"--end-offset exceeds frontier total {frontier_total}")

    resume_checkpoint = read_checkpoint(run_dir) if args.resume else None
    totals = Counter()
    current_offset = args.start_offset
    if args.resume:
        current_offset, totals = processed_state_from_nodes(run_dir / "nodes.csv", args.start_offset)
        if resume_checkpoint is not None and int(resume_checkpoint.get("next_offset", current_offset)) != current_offset:
            log_event(
                run_dir,
                "resume adjusted next_offset from checkpoint="
                f"{resume_checkpoint.get('next_offset')} to nodes_csv_contiguous={current_offset}",
            )

    effective_end = args.end_offset
    if args.max_nodes > 0:
        effective_end = min(effective_end, current_offset + args.max_nodes)

    plan = {
        "depth": args.depth,
        "start_offset": current_offset,
        "end_offset": args.end_offset,
        "effective_end_offset": effective_end,
        "frontier_total": frontier_total,
        "chunk_size": args.chunk_size,
        "window_chunks": args.window_chunks,
        "window_nodes": args.chunk_size * args.window_chunks,
        "timeout_ms": args.timeout_ms,
        "target_rawH": args.target_rawH,
        "run_dir": str(run_dir),
    }
    log_event(run_dir, "plan " + json.dumps(plan, sort_keys=True))
    if args.dry_run:
        return 0

    started_utc = utc_now()
    started_time = time.time()

    log_event(run_dir, f"generating live frontier domains up to offset {effective_end}")
    gen_started = time.time()
    nodes = v.branch3_live_frontier_domains(args.depth, limit=effective_end)
    gen_seconds = time.time() - gen_started
    if len(nodes) < effective_end:
        raise SystemExit(f"frontier generation returned only {len(nodes)} nodes, expected at least {effective_end}")
    log_event(run_dir, f"generated {len(nodes)} domains in {gen_seconds:.3f}s")

    node_f, node_w = open_csv(run_dir / "nodes.csv", NODE_FIELDS)
    chunk_f, chunk_w = open_csv(run_dir / "chunks.csv", CHUNK_FIELDS)
    window_f, window_w = open_csv(run_dir / "windows.csv", WINDOW_FIELDS)
    unknown_f, unknown_w = open_csv(run_dir / "unknown.csv", UNKNOWN_FIELDS)
    sat_f, sat_w = open_csv(run_dir / "sat.csv", SAT_FIELDS)

    try:
        write_checkpoint(
            args=args,
            run_dir=run_dir,
            next_offset=current_offset,
            totals=totals,
            status="running",
            frontier_total=frontier_total,
            effective_end=effective_end,
            started_utc=started_utc,
            started_time=started_time,
        )

        window_nodes = args.chunk_size * args.window_chunks
        window_index = max(0, (current_offset - args.start_offset) // window_nodes)
        while current_offset < effective_end:
            if args.time_limit_hours > 0 and (time.time() - started_time) >= args.time_limit_hours * 3600.0:
                log_event(run_dir, f"time limit reached before window at offset {current_offset}")
                write_checkpoint(
                    args=args,
                    run_dir=run_dir,
                    next_offset=current_offset,
                    totals=totals,
                    status="time_limit",
                    frontier_total=frontier_total,
                    effective_end=effective_end,
                    started_utc=started_utc,
                    started_time=started_time,
                )
                return 0

            window_start = current_offset
            window_end = min(effective_end, window_start + window_nodes)
            log_event(run_dir, f"WINDOW {window_index} start offset={window_start} end={window_end}")
            window_started = time.time()
            ctx = v.smt1_global_onehot_pb_context(target_rawH=args.target_rawH, timeout_ms=args.timeout_ms)
            build_seconds = float(ctx["build_seconds"])
            z3 = ctx["z3"]
            solver = ctx["solver"]
            X = ctx["X"]
            log_event(
                run_dir,
                f"WINDOW {window_index} built context build={build_seconds}s assertions={ctx['assertions']} weighted_terms={ctx['weighted_terms']}",
            )

            window_counts = Counter()
            check_started = time.time()
            while current_offset < window_end:
                chunk_start = current_offset
                chunk_end = min(window_end, chunk_start + args.chunk_size)
                chunk_index = chunk_start // args.chunk_size
                chunk_started = time.time()
                chunk_counts = Counter()

                for node_index in range(chunk_start, chunk_end):
                    assumptions, fixed_count, fixed_signature = v.domain_assumptions_from_singletons(z3, X, nodes[node_index])
                    node_started = time.time()
                    ans = solver.check(assumptions)
                    seconds = round(time.time() - node_started, 3)
                    answer = str(ans)
                    reason = ""
                    witness = ""
                    metrics_json = ""

                    if ans == z3.unknown:
                        reason = solver.reason_unknown()
                    elif ans == z3.sat:
                        witness = v.smt1_model_word(z3, solver.model(), X)
                        metrics_json = json.dumps(v.h_metrics_reduced(witness), sort_keys=True)

                    row_common = {
                        "utc": utc_now(),
                        "window_index": window_index,
                        "chunk_index": chunk_index,
                        "node_index": node_index,
                        "seconds": seconds,
                        "fixed_signature": fixed_signature,
                    }
                    node_w.writerow({
                        **row_common,
                        "answer": answer,
                        "fixed_count": fixed_count,
                        "reason": reason,
                    })
                    node_f.flush()

                    if answer == "unknown":
                        unknown_w.writerow({**row_common, "reason": reason})
                        unknown_f.flush()
                        log_event(run_dir, f"UNKNOWN node={node_index} seconds={seconds} reason={reason} fixed={fixed_signature}")
                    elif answer == "sat":
                        sat_w.writerow({**row_common, "witness": witness, "metrics_json": metrics_json})
                        sat_f.flush()
                        log_event(run_dir, f"SAT node={node_index} seconds={seconds} witness={witness} metrics={metrics_json}")

                    totals[answer] += 1
                    window_counts[answer] += 1
                    chunk_counts[answer] += 1
                    current_offset = node_index + 1
                    write_checkpoint(
                        args=args,
                        run_dir=run_dir,
                        next_offset=current_offset,
                        totals=totals,
                        status="running",
                        frontier_total=frontier_total,
                        effective_end=effective_end,
                        started_utc=started_utc,
                        started_time=started_time,
                    )

                    if answer == "sat" and not args.continue_after_sat:
                        log_event(run_dir, "stopping after SAT witness; pass --continue-after-sat to keep running")
                        write_checkpoint(
                            args=args,
                            run_dir=run_dir,
                            next_offset=current_offset,
                            totals=totals,
                            status="sat_stop",
                            frontier_total=frontier_total,
                            effective_end=effective_end,
                            started_utc=started_utc,
                            started_time=started_time,
                        )
                        return 2
                    if answer == "unknown" and args.stop_on_unknown:
                        log_event(run_dir, "stopping after UNKNOWN; omit --stop-on-unknown to keep running")
                        write_checkpoint(
                            args=args,
                            run_dir=run_dir,
                            next_offset=current_offset,
                            totals=totals,
                            status="unknown_stop",
                            frontier_total=frontier_total,
                            effective_end=effective_end,
                            started_utc=started_utc,
                            started_time=started_time,
                        )
                        return 3
                    if args.time_limit_hours > 0 and (time.time() - started_time) >= args.time_limit_hours * 3600.0:
                        log_event(run_dir, f"time limit reached after node {node_index}")
                        write_checkpoint(
                            args=args,
                            run_dir=run_dir,
                            next_offset=current_offset,
                            totals=totals,
                            status="time_limit",
                            frontier_total=frontier_total,
                            effective_end=effective_end,
                            started_utc=started_utc,
                            started_time=started_time,
                        )
                        return 0

                chunk_seconds = round(time.time() - chunk_started, 3)
                chunk_w.writerow({
                    "utc": utc_now(),
                    "window_index": window_index,
                    "chunk_index": chunk_index,
                    "offset": chunk_start,
                    "end_offset": chunk_end,
                    "nodes": chunk_end - chunk_start,
                    "unsat": chunk_counts.get("unsat", 0),
                    "sat": chunk_counts.get("sat", 0),
                    "unknown": chunk_counts.get("unknown", 0),
                    "seconds": chunk_seconds,
                    "cumulative_checked": sum(totals.values()),
                    "cumulative_unsat": totals.get("unsat", 0),
                    "cumulative_sat": totals.get("sat", 0),
                    "cumulative_unknown": totals.get("unknown", 0),
                    "next_offset": current_offset,
                })
                chunk_f.flush()
                log_event(
                    run_dir,
                    "CHUNK "
                    f"offset={chunk_start} nodes={chunk_end - chunk_start} counts={dict(chunk_counts)} "
                    f"seconds={chunk_seconds} next={current_offset}",
                )

            check_seconds = time.time() - check_started
            window_elapsed = time.time() - window_started
            window_w.writerow({
                "utc": utc_now(),
                "window_index": window_index,
                "offset": window_start,
                "end_offset": window_end,
                "nodes": window_end - window_start,
                "unsat": window_counts.get("unsat", 0),
                "sat": window_counts.get("sat", 0),
                "unknown": window_counts.get("unknown", 0),
                "build_seconds": build_seconds,
                "check_seconds": round(check_seconds, 3),
                "elapsed_seconds": round(window_elapsed, 3),
                "next_offset": current_offset,
            })
            window_f.flush()
            log_event(
                run_dir,
                "WINDOW "
                f"{window_index} done nodes={window_end - window_start} counts={dict(window_counts)} "
                f"build={build_seconds}s checks={check_seconds:.3f}s elapsed={window_elapsed:.3f}s next={current_offset}",
            )
            del solver, X, ctx
            window_index += 1

        write_checkpoint(
            args=args,
            run_dir=run_dir,
            next_offset=current_offset,
            totals=totals,
            status="complete",
            frontier_total=frontier_total,
            effective_end=effective_end,
            started_utc=started_utc,
            started_time=started_time,
        )
        log_event(run_dir, f"COMPLETE next_offset={current_offset} totals={dict(totals)}")
        return 0
    finally:
        for f in (node_f, chunk_f, window_f, unknown_f, sat_f):
            f.close()


if __name__ == "__main__":
    raise SystemExit(main())
