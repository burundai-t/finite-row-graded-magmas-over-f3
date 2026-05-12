#!/usr/bin/env python3
"""Verify fixed-diagonal endpoint data in the compact Layer 1 final pack.

The old stage script read layer1_v3_extremal_diagonal_probe.csv from the old stage tree.
That probe table is intentionally not part of the compact final pack. This
cleanup version verifies the same endpoint facts from the included final tables:
  * tables/layer1_v3_fixed_diagonal_summary.csv;
  * tables/layer1_v3_extremal_loci_solutions.csv.
"""
from __future__ import annotations

import csv
from collections import Counter
from itertools import product
from pathlib import Path

S = (0, 1, 2)
M = tuple(product(S, S))
BLOCK_NAMES = ("RRR", "RRS", "RSR", "RSS", "RST")
ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"
GENERATED = ROOT / "generated" / "extremal_diagonal_probe"
OUT = GENERATED / "layer1_v3_extremal_diagonal_witnesses.csv"
SUMMARY = GENERATED / "layer1_v3_extremal_diagonal_probe_summary.txt"


def comp(a: int, b: int) -> int:
    return (-a - b) % 3


def parse_table(s: str) -> tuple[int, ...]:
    if len(s) != 9 or any(ch not in "012" for ch in s):
        raise ValueError(f"bad table: {s!r}")
    return tuple(map(int, s))


def tab_get(T: tuple[int, ...], a: int, e: int) -> int:
    return T[3 * (a % 3) + (e % 3)]


def mval(A: tuple[int, ...], B: tuple[int, ...], d: tuple[int, ...], b: int, a: int, e: int) -> int:
    b %= 3
    a %= 3
    e %= 3
    if b == 0:
        return d[a] if a == e else comp(a, e)
    if b == 1:
        return tab_get(A, a, e)
    return tab_get(B, a, e)


def mult(A: tuple[int, ...], B: tuple[int, ...], d: tuple[int, ...], x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    r1, c1 = x
    r2, c2 = y
    if r1 == r2:
        if c1 == c2:
            return (r1, (r1 + d[(c1 - r1) % 3]) % 3)
        return (r1, comp(c1, c2))
    b = (r2 - r1) % 3
    a = (c1 - r1) % 3
    e = (c2 - r1) % 3
    return (r1, (r1 + mval(A, B, d, b, a, e)) % 3)


def assoc_direct(A: tuple[int, ...], B: tuple[int, ...], d: tuple[int, ...]) -> int:
    count = 0
    for x, y, z in product(M, repeat=3):
        if mult(A, B, d, mult(A, B, d, x, y), z) == mult(A, B, d, x, mult(A, B, d, y, z)):
            count += 1
    return count


def block_label(b: int, t: int) -> str:
    if b == 0 and t == 0:
        return "RRR"
    if b == 0 and t != 0:
        return "RRS"
    if b != 0 and t == 0:
        return "RSR"
    if b != 0 and t == b:
        return "RSS"
    return "RST"


def assoc_master_raw_blocks(A: tuple[int, ...], B: tuple[int, ...], d: tuple[int, ...]) -> tuple[int, dict[str, int]]:
    raw = 0
    blocks = {name: 0 for name in BLOCK_NAMES}
    for b, t, a, e, f in product(S, repeat=5):
        xy = mval(A, B, d, b, a, e)
        lhs = mval(A, B, d, t, xy, f)
        yz = mval(A, B, d, (t - b) % 3, (e - b) % 3, (f - b) % 3)
        rhs = mval(A, B, d, b, a, (b + yz) % 3)
        if lhs == rhs:
            raw += 1
            blocks[block_label(b, t)] += 1
    return raw, blocks


def read_csv(name: str) -> list[dict[str, str]]:
    with (TABLES / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def verify_row(row: dict[str, str]) -> dict[str, object]:
    A_s, B_s, d_s = row["A"], row["B"], row["d"]
    A, B, d = parse_table(A_s), parse_table(B_s), tuple(map(int, d_s))
    raw_expected = int(row["raw"])
    direct = assoc_direct(A, B, d)
    raw, blocks = assoc_master_raw_blocks(A, B, d)
    if direct != 3 * raw or raw != raw_expected:
        raise AssertionError((row["mode"], row["x21"], direct, raw, raw_expected))
    return {
        "kind": f"{row['mode']}_raw{raw}",
        "d": d_s,
        "diag_class": row["d_class"],
        "A": A_s,
        "B": B_s,
        "x21": row["x21"],
        "raw_assoc": raw,
        "assoc": direct,
        "raw_blocks": ";".join(f"{k}={blocks[k]}" for k in BLOCK_NAMES),
        "assoc_blocks": ";".join(f"{k}={3 * blocks[k]}" for k in BLOCK_NAMES),
    }


def main() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    fixed = read_csv("layer1_v3_fixed_diagonal_summary.csv")
    solutions = read_csv("layer1_v3_extremal_loci_solutions.csv")

    min_reps = [r["d"] for r in fixed if int(r["min_assoc"]) == 63]
    max_reps = [r["d"] for r in fixed if int(r["max_assoc"]) == 597]
    assert min_reps == ["100", "101", "120", "121"]
    assert max_reps == ["000", "111"]

    min_members = set()
    max_members = set()
    for r in fixed:
        members = set(r["diagonal_orbit_members"].split(";"))
        if int(r["min_assoc"]) == 63:
            min_members.update(members)
        if int(r["max_assoc"]) == 597:
            max_members.update(members)
    assert min_members == set("100 101 120 121 200 201 220 221".split())
    assert max_members == set("000 111 222".split())

    witness_rows = [verify_row(r) for r in solutions]
    counts = Counter((r["mode"], r["d"]) for r in solutions)
    assert sum(1 for r in solutions if r["mode"] == "min") == 24
    assert sum(1 for r in solutions if r["mode"] == "max") == 6
    assert set(d for (mode, d), _ in counts.items() if mode == "min") == min_members
    assert set(d for (mode, d), _ in counts.items() if mode == "max") == max_members

    fieldnames = ["kind", "d", "diag_class", "A", "B", "x21", "raw_assoc", "assoc", "raw_blocks", "assoc_blocks"]
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(witness_rows)

    text = []
    text.append("Layer 1 v3 final-pack extremal diagonal endpoint verification")
    text.append(f"global-min representative diagonals raw=21: {min_reps}")
    text.append(f"global-min all diagonal members raw=21: {sorted(min_members)}")
    text.append(f"global-max representative diagonals raw=199: {max_reps}")
    text.append(f"global-max all diagonal members raw=199: {sorted(max_members)}")
    text.append(f"independently verified listed endpoint witnesses: {len(witness_rows)}")
    text.append("all direct 9^3 and master 3^5 checks agree")
    SUMMARY.write_text("\n".join(text) + "\n", encoding="utf-8")
    print(SUMMARY.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
