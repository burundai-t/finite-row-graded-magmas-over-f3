#!/usr/bin/env python3
"""Layer 1 v3 proof-skeleton checks.

This is a compact reproducibility/check script for the analytic-compression
block. It is not the global branch-and-bound solver. It checks only finite data
present in the final pack:
  * RRR depends only on the diagonal d and has values 9, 11, 13, 19;
  * the certified extremal loci have the claimed raw block patterns;
  * the min/max diagonal supports and orbit counts match the final tables;
  * the term-signature clues used in the skeleton are consistent.

Generated check artifacts are written under ../generated/proof_skeleton.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
import csv
import json

S = (0, 1, 2)
ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"
OUT = ROOT / "generated" / "proof_skeleton"


def digits(s: str) -> tuple[int, ...]:
    return tuple(int(ch) for ch in s.zfill(len(s)))


def parse_d(s: str) -> tuple[int, int, int]:
    return tuple(int(ch) for ch in s.zfill(3))  # type: ignore[return-value]


def table9(s: str):
    vals = digits(s)
    if len(vals) != 9:
        raise ValueError(f"expected 9 digits, got {s!r}")
    return {(a, e): vals[3 * a + e] for a in S for e in S}


def comp(a: int, b: int) -> int:
    return (-a - b) % 3


def M_value(t: int, a: int, e: int, A, B, d) -> int:
    if t == 1:
        return A[(a, e)]
    if t == 2:
        return B[(a, e)]
    if a == e:
        return d[a]
    return comp(a, e)


def block_name(b: int, t: int) -> str:
    if b == 0 and t == 0:
        return "RRR"
    if b == 0 and t != 0:
        return "RRS"
    if b != 0 and t == 0:
        return "RSR"
    if b != 0 and t == b:
        return "RSS"
    return "RST"


def raw_blocks(Astr: str, Bstr: str, dstr: str) -> dict[str, int]:
    A = table9(Astr)
    B = table9(Bstr)
    d = parse_d(dstr)
    counts = Counter()
    for b, t, a, e, f in product(S, repeat=5):
        lhs = M_value(t, M_value(b, a, e, A, B, d), f, A, B, d)
        inner = M_value((t - b) % 3, (e - b) % 3, (f - b) % 3, A, B, d)
        rhs = M_value(b, a, (b + inner) % 3, A, B, d)
        if lhs == rhs:
            counts[block_name(b, t)] += 1
    return {k: counts[k] for k in ("RRR", "RRS", "RSR", "RSS", "RST")}


def raw_rrr_for_d(dstr: str) -> int:
    z = "000000000"
    return raw_blocks(z, z, dstr)["RRR"]


def d_class(dstr: str) -> str:
    d = parse_d(dstr)
    p = len(set(d))
    fixed = sum(1 for i, v in enumerate(d) if i == v)
    if p == 1:
        return "constant"
    if p == 3:
        return "permutation"
    if fixed == 0:
        return "two-valued_no_fixed"
    return "two-valued_with_fixed"


def all_diagonal_rrr():
    rows = []
    for d in ("".join(map(str, x)) for x in product(S, repeat=3)):
        raw = raw_rrr_for_d(d)
        rows.append({"d": d, "d_class": d_class(d), "rawRRR": raw, "RRR": 3 * raw})
    return rows


def csv_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        yield from csv.DictReader(f)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    report: dict[str, object] = {}

    rrr_rows = all_diagonal_rrr()
    class_counter = defaultdict(Counter)
    for r in rrr_rows:
        class_counter[r["d_class"]][r["rawRRR"]] += 1
    expected_rrr = {
        "permutation": Counter({9: 6}),
        "two-valued_no_fixed": Counter({11: 6}),
        "two-valued_with_fixed": Counter({13: 12}),
        "constant": Counter({19: 3}),
    }
    assert dict(class_counter) == expected_rrr, dict(class_counter)
    report["RRR_classification"] = {k: dict(v) for k, v in class_counter.items()}

    sol_path = TABLES / "layer1_v3_extremal_loci_solutions.csv"
    rows = list(csv_rows(sol_path))
    assert len(rows) == 30
    mode_counts = Counter(r["mode"] for r in rows)
    assert mode_counts == {"min": 24, "max": 6}

    block_patterns = defaultdict(Counter)
    diag_support = defaultdict(Counter)
    for r in rows:
        got = raw_blocks(r["A"], r["B"], r["d"])
        expected = {}
        for part in r["raw_blocks"].split(";"):
            name, val = part.split(":")
            expected[name] = int(val)
        assert got == expected, (r["x21"], got, expected)
        block_patterns[r["mode"]][tuple(got[k] for k in ("RRR", "RRS", "RSR", "RSS", "RST"))] += 1
        diag_support[r["mode"]][r["d"].zfill(3)] += 1

    assert block_patterns["min"] == Counter({(11, 2, 2, 2, 4): 12, (9, 2, 2, 4, 4): 12})
    assert block_patterns["max"] == Counter({(19, 36, 36, 54, 54): 6})
    assert set(diag_support["min"]) == set("100 101 120 121 200 201 220 221".split())
    assert set(diag_support["max"]) == set("000 111 222".split())
    report["extremal_block_patterns"] = {k: {str(pk): v for pk, v in c.items()} for k, c in block_patterns.items()}
    report["diagonal_support"] = {k: dict(v) for k, v in diag_support.items()}

    orbit_path = TABLES / "layer1_v3_extremal_loci_orbits.csv"
    orbits = list(csv_rows(orbit_path))
    orbit_counts = Counter(r["mode"] for r in orbits)
    assert orbit_counts == {"min": 12, "max": 3}
    assert all(r["tau_fixed"] == "False" for r in orbits)
    report["orbit_counts"] = dict(orbit_counts)

    sig_path = TABLES / "layer1_v3_term_signature_summary.csv"
    sigs = list(csv_rows(sig_path))
    by = {(r["term_set"], r["block"]): r for r in sigs}
    assert int(by[("max_all", "RSS")]["always_terms"]) == 54
    assert int(by[("max_all", "RST")]["always_terms"]) == 54
    assert all(int(by[("min_all", b)]["always_terms"]) == 0 for b in ("RRS", "RSR", "RSS", "RST"))
    report["term_signature_highlights"] = {
        "max_RSS_always": by[("max_all", "RSS")]["always_terms"],
        "max_RST_always": by[("max_all", "RST")]["always_terms"],
        "min_cross_always": {b: by[("min_all", b)]["always_terms"] for b in ("RRS", "RSR", "RSS", "RST")},
    }

    with (OUT / "layer1_v3_rrr_classification.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["d", "d_class", "rawRRR", "RRR"])
        w.writeheader()
        w.writerows(rrr_rows)

    obligations = [
        {
            "side": "min",
            "statement": "rawRRR=9 => rawCross >= 12",
            "equality_locus": "permutation diagonals 120,201 inside M_63",
            "status": "V-certified target; hand proof open",
        },
        {
            "side": "min",
            "statement": "rawRRR=11 => rawCross >= 10",
            "equality_locus": "two-valued_no_fixed diagonals in M_63",
            "status": "V-certified target; hand proof open",
        },
        {
            "side": "max",
            "statement": "constant d => rawCross <= 180",
            "equality_locus": "constant diagonals 000,111,222 inside M_597",
            "status": "V-certified target; hand proof open",
        },
        {
            "side": "max",
            "statement": "nonconstant d => rawAssoc <= 189",
            "equality_locus": "none at raw 199",
            "status": "V-certified target; hand proof open",
        },
        {
            "side": "compatibility",
            "statement": "independent block extrema do not sum to global extrema",
            "equality_locus": "global extrema require compatible cross-block assignments",
            "status": "structural warning; use in proof narrative",
        },
    ]
    with (OUT / "layer1_v3_proof_obligations.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["side", "statement", "equality_locus", "status"])
        w.writeheader()
        w.writerows(obligations)

    with (OUT / "layer1_v3_proof_skeleton_check_output.json").open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)

    print("Layer 1 v3 final-pack proof-skeleton checks passed.")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
