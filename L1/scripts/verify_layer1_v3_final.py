#!/usr/bin/env python3
from __future__ import annotations

import csv
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"

def read_csv(name: str):
    with (TABLES / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main():
    zq = read_csv("layer1_v3_Zq_full_assoc_distribution.csv")
    triples = [(int(r["raw"]), int(r["assoc"]), int(r["count"])) for r in zq]

    assert len(triples) == 167
    assert all(assoc == 3 * raw for raw, assoc, _ in triples)

    total = sum(c for _, _, c in triples)
    assert total == 3 ** 21

    assert triples[0] == (21, 63, 24)
    assert triples[-1] == (199, 597, 6)

    sum_assoc = sum(a * c for _, a, c in triples)
    mean_assoc = Fraction(sum_assoc, total)
    assert mean_assoc == Fraction(245, 1)

    sum_raw = sum(r * c for r, _, c in triples)
    sum_raw_sq = sum(r * r * c for r, _, c in triples)
    mean_raw = Fraction(sum_raw, total)
    var_raw = Fraction(sum_raw_sq, total) - mean_raw * mean_raw
    var_assoc = 9 * var_raw
    assert var_assoc == Fraction(27820, 27)

    max_coeff = max(c for _, _, c in triples)
    modes = [(r, a) for r, a, c in triples if c == max_coeff]
    assert max_coeff == 426_317_976
    assert modes == [(79, 237)]

    fixed = read_csv("layer1_v3_fixed_diagonal_summary.csv")
    assert len(fixed) == 15
    assert sum(int(r["diagonal_orbit_size"]) for r in fixed) == 27
    assert all(int(r["points"]) == 3 ** 18 for r in fixed)

    min_reps = {r["d"] for r in fixed if int(r["min_assoc"]) == 63}
    max_reps = {r["d"] for r in fixed if int(r["max_assoc"]) == 597}
    assert min_reps == {"100", "101", "120", "121"}
    assert max_reps == {"000", "111"}

    orbits = read_csv("layer1_v3_extremal_loci_orbits.csv")
    min_orbits = [r for r in orbits if r["mode"] == "min"]
    max_orbits = [r for r in orbits if r["mode"] == "max"]
    assert len(min_orbits) == 12
    assert len(max_orbits) == 3
    assert all(r["orbit_size_in_solution_set"] == "2" for r in min_orbits + max_orbits)

    cb = read_csv("layer1_v3_column_blind_d000_table.csv")
    assert len(cb) == 9
    cb_min = [r for r in cb if r["trivial"] == "0" and int(r["assoc"]) == 219]
    assert {(r["a"], r["b"]) for r in cb_min} == {("1", "2"), ("2", "1")}

    print("Layer 1 v3 final pack checks passed.")

if __name__ == "__main__":
    main()
