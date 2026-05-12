#!/usr/bin/env python3
"""Verify the compact final-pack Z(q) tables.

This version is self-contained inside layer1_final_pack: it reads only files from
../tables and no longer expects the old Block-04 stage filenames.
"""
from __future__ import annotations

import csv
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"
FULL = TABLES / "layer1_v3_Zq_full_assoc_distribution.csv"
FIXED = TABLES / "layer1_v3_fixed_diagonal_summary.csv"


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    full = read_csv(FULL)
    fixed = read_csv(FIXED)

    triples = [(int(r["raw"]), int(r["assoc"]), int(r["count"])) for r in full]
    assert len(triples) == 167
    assert all(assoc == 3 * raw for raw, assoc, _ in triples)

    points = sum(count for _, _, count in triples)
    assert points == 3 ** 21

    raw_min, assoc_min, count_min = triples[0]
    raw_max, assoc_max, count_max = triples[-1]
    assert (raw_min, assoc_min, count_min) == (21, 63, 24)
    assert (raw_max, assoc_max, count_max) == (199, 597, 6)

    sum_raw = sum(raw * count for raw, _, count in triples)
    sum_assoc = sum(assoc * count for _, assoc, count in triples)
    sum_raw_sq = sum(raw * raw * count for raw, _, count in triples)
    mean_raw = Fraction(sum_raw, points)
    mean_assoc = Fraction(sum_assoc, points)
    var_raw = Fraction(sum_raw_sq, points) - mean_raw * mean_raw
    var_assoc = 9 * var_raw

    assert mean_raw == Fraction(245, 3)
    assert mean_assoc == Fraction(245, 1)
    assert var_raw == Fraction(27820, 243)
    assert var_assoc == Fraction(27820, 27)

    max_coeff = max(count for _, _, count in triples)
    modes = [(raw, assoc) for raw, assoc, count in triples if count == max_coeff]
    assert max_coeff == 426_317_976
    assert modes == [(79, 237)]

    raw_values = {raw for raw, _, _ in triples}
    missing = [r for r in range(21, 200) if r not in raw_values]
    assert missing == [182, 184, 186, 188, 190, 191, 192, 194, 195, 196, 197, 198]

    assert len(fixed) == 15
    assert sum(int(r["diagonal_orbit_size"]) for r in fixed) == 27
    assert all(int(r["points"]) == 3 ** 18 for r in fixed)

    min_support = ";".join(r["d"] for r in fixed if int(r["min_assoc"]) == 63)
    max_support = ";".join(r["d"] for r in fixed if int(r["max_assoc"]) == 597)
    assert min_support == "100;101;120;121"
    assert max_support == "000;111"

    print("Layer 1 v3 final-pack Z(q) checks passed.")


if __name__ == "__main__":
    main()
