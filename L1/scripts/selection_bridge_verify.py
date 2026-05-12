#!/usr/bin/env python3
"""Verify Layer 1 final-pack facts used by the Layer 2 selection bridge.

This compact version reads only ../tables. It replaces the old Block-05 stage
inputs with checks derived from the final Z(q), column-blind, extremal-tail and
selection-bridge claim tables.
"""
from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"
G = 3 ** 18
OMEGA = 3 ** 21


def read_csv(name: str) -> list[dict[str, str]]:
    with (TABLES / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def entropy_bits(d: str) -> float:
    counts = Counter(d)
    n = len(d)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def idempotents(d: str) -> int:
    return 3 * sum(int(ch) == i for i, ch in enumerate(d))


def expand_orbit_members(rows: list[dict[str, str]], predicate) -> set[str]:
    out: set[str] = set()
    for r in rows:
        if predicate(r):
            out.update(r["diagonal_orbit_members"].split(";"))
    return out


def main() -> None:
    zq = read_csv("layer1_v3_Zq_full_assoc_distribution.csv")
    triples = [(int(r["raw"]), int(r["assoc"]), int(r["count"])) for r in zq]
    assert sum(c for _, _, c in triples) == OMEGA
    assert triples[0] == (21, 63, 24)
    assert triples[-1] == (199, 597, 6)

    cb = read_csv("layer1_v3_column_blind_d000_table.csv")
    assert len(cb) == 9
    assert 9 / G == 9 / (3 ** 18)
    nontriv = [r for r in cb if int(r["trivial"]) == 0]
    assert len(nontriv) == 6
    min_assoc = min(int(r["assoc"]) for r in nontriv)
    assert min_assoc == 219
    min_rows = {(int(r["a"]), int(r["b"])) for r in nontriv if int(r["assoc"]) == min_assoc}
    assert min_rows == {(1, 2), (2, 1)}

    pab = next(r for r in cb if (int(r["a"]), int(r["b"])) == (1, 2))
    comp = next(r for r in cb if (int(r["a"]), int(r["b"])) == (2, 1))
    for key in ["assoc", "idempotents", "Hdiag_bits", "block_RRR", "block_RRS", "block_RSR", "block_RSS", "block_RST"]:
        assert pab[key] == comp[key], key
    assert pab["assoc"] == "219"

    ext = read_csv("layer1_v3_extremal_hacc_feature_summary.csv")
    by_mode = {r["mode"]: r for r in ext}
    assert int(by_mode["min"]["points"]) == 24
    assert int(by_mode["min"]["S3_orbits"]) == 12
    assert int(by_mode["min"]["column_blind_points"]) == 0
    assert int(by_mode["max"]["points"]) == 6
    assert int(by_mode["max"]["S3_orbits"]) == 3
    assert int(by_mode["max"]["column_blind_points"]) == 0
    assert "100" in by_mode["min"]["diagonals"] and "000" in by_mode["max"]["diagonals"]

    fixed = read_csv("layer1_v3_fixed_diagonal_summary.csv")
    min_support = expand_orbit_members(fixed, lambda r: int(r["min_assoc"]) == 63)
    max_support = expand_orbit_members(fixed, lambda r: int(r["max_assoc"]) == 597)
    assert min_support == set("100 101 120 121 200 201 220 221".split())
    assert max_support == set("000 111 222".split())
    assert Counter(idempotents(d) for d in min_support) == Counter({0: 8})
    assert all(abs(entropy_bits(d)) < 1e-12 for d in max_support)

    claims = read_csv("layer1_v3_selection_bridge_claims.csv")
    claim_ids = {r["claim_id"] for r in claims}
    assert {"B05-C1", "B05-C2", "B05-C3", "B05-C4"}.issubset(claim_ids)

    selection_chain_totals = [
        OMEGA,
        9 * 27,
        6 * 27,
        2 * 27,
        1 * 27,
        1 * 3,
        1,
    ]
    assert selection_chain_totals == [3 ** 21, 243, 162, 54, 27, 3, 1]

    print("Layer 1 v3 final-pack selection-bridge checks passed.")


if __name__ == "__main__":
    main()
