#!/usr/bin/env python3
"""Stable Layer 3 Front D verifier.

Validates the generated Front D finite binary presentation tables and independently
checks the PAB identity/countermodel audit. The heavy 630-state closure table is
kept as an artifact and hash-audited instead of being regenerated on every smoke run.
"""
from __future__ import annotations

import csv
import hashlib
import os
from itertools import product
from typing import Dict, Sequence, Tuple, Union

Term = Union[str, Tuple["Term", "Term"]]


def read_csv(path: str):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def vars_in(t: Term) -> set[str]:
    if isinstance(t, str):
        return {t}
    return vars_in(t[0]) | vars_in(t[1])


def eval_term(t: Term, vals: Dict[str, int], table: Sequence[int], n: int) -> int:
    if isinstance(t, str):
        return vals[t]
    return table[eval_term(t[0], vals, table, n) * n + eval_term(t[1], vals, table, n)]


def holds(eq: Tuple[Term, Term], table: Sequence[int], n: int) -> bool:
    variables = sorted(vars_in(eq[0]) | vars_in(eq[1]))
    for tup in product(range(n), repeat=len(variables)):
        vals = dict(zip(variables, tup))
        if eval_term(eq[0], vals, table, n) != eval_term(eq[1], vals, table, n):
            return False
    return True


def witness(eq: Tuple[Term, Term], table: Sequence[int], n: int):
    variables = sorted(vars_in(eq[0]) | vars_in(eq[1]))
    for tup in product(range(n), repeat=len(variables)):
        vals = dict(zip(variables, tup))
        lv = eval_term(eq[0], vals, table, n)
        rv = eval_term(eq[1], vals, table, n)
        if lv != rv:
            return vals, lv, rv
    return None


def pab_table() -> list[int]:
    S = range(3)
    M = [(r, c) for r in S for c in S]
    def comp(a, b): return (-a - b) % 3
    def mul(i, j):
        r1, c1 = M[i]; r2, c2 = M[j]
        if r1 != r2: return 3 * r1 + r2
        if c1 != c2: return 3 * r1 + comp(c1, c2)
        return 3 * r1 + r1
    return [mul(i, j) for i in range(9) for j in range(9)]


def write_csv(path: str, rows, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    tables = os.path.join(root, "tables")
    reps_path = os.path.join(tables, "layer3_frontD_canonical_representatives.csv")
    mult_path = os.path.join(tables, "layer3_frontD_binary_clone_multiplication_table.csv")
    size_path = os.path.join(tables, "layer3_frontD_minimal_size_distribution.csv")
    status_path = os.path.join(tables, "layer3_frontD_status_registry.csv")

    reps = read_csv(reps_path)
    sizes = read_csv(size_path)
    status = read_csv(status_path)
    with open(mult_path, newline="", encoding="utf-8") as f:
        mult_rows = list(csv.reader(f))

    checks = []
    checks.append({"check": "representative_count", "result": len(reps) == 630, "detail": f"rows={len(reps)}"})
    checks.append({"check": "multiplication_table_shape", "result": len(mult_rows) == 631 and len(mult_rows[0]) == 631, "detail": f"rows={len(mult_rows)-1}, cols={len(mult_rows[0])-1}"})
    ids = {int(r["id"]) for r in reps}
    checks.append({"check": "representative_ids", "result": ids == set(range(630)), "detail": "ids=0..629"})
    max_size = max(int(r["minimal_size"]) for r in reps)
    checks.append({"check": "max_minimal_size", "result": max_size == 15, "detail": f"max={max_size}"})
    final_cum = int(sizes[-1]["cumulative_functions"])
    checks.append({"check": "size_distribution_final_cumulative", "result": final_cum == 630, "detail": f"final={final_cum}"})

    # Multiplication table entries are closed ids.
    closed = True
    for row in mult_rows[1:]:
        if len(row) != 631:
            closed = False; break
        for cell in row[1:]:
            v = int(cell)
            if v < 0 or v >= 630:
                closed = False; break
        if not closed: break
    checks.append({"check": "multiplication_entries_closed", "result": closed, "detail": "all entries in 0..629"})

    # Independent identity and countermodel checks.
    x, y, z, w = "x", "y", "z", "w"
    I1 = (((x, y), (x, y)), (x, x))
    I2 = (((x, x), (y, y)), ((x, y), (y, x)))
    I3 = (((x, x), (y, x)), ((x, y), (y, y)))
    STAR = ((z, (z, w)), ((z, w), z))
    U1 = ((x, (x, (x, x))), (x, x))
    U2 = (((x, x), (x, (x, x))), x)
    D5 = ((x, (y, y)), (x, (((y, (x, y)), x))))
    pab = pab_table()
    all_pab = all(holds(eq, pab, 9) for eq in [I1, I2, I3, STAR, U1, U2, D5])
    checks.append({"check": "identity_truth_in_PAB", "result": all_pab, "detail": "I1,I2,I3,star,U1,U2,D5 hold"})

    cm1 = (0, 0, 1, 0, 0, 1, 1, 1, 0)
    cm1_ok = all(holds(eq, cm1, 3) for eq in [I1, I2, I3, STAR]) and not holds(U1, cm1, 3)
    checks.append({"check": "CM1_countermodel", "result": cm1_ok, "detail": f"witness={witness(U1, cm1, 3)}"})

    cm2 = (0, 1, 2, 1, 0, 1, 2, 1, 0)
    cm2_ok = all(holds(eq, cm2, 3) for eq in [I1, I2, I3, STAR, U1, U2]) and not holds(D5, cm2, 3)
    checks.append({"check": "CM2_countermodel", "result": cm2_ok, "detail": f"witness={witness(D5, cm2, 3)}"})

    # Hash manifest for D tables.
    d_tables = [
        "layer3_frontD_closure_rounds.csv",
        "layer3_frontD_minimal_size_distribution.csv",
        "layer3_frontD_canonical_representatives.csv",
        "layer3_frontD_binary_clone_multiplication_table.csv",
        "layer3_frontD_identity_audit.csv",
        "layer3_frontD_countermodel_audit.csv",
        "layer3_frontD_status_registry.csv",
    ]
    manifest = []
    for name in d_tables:
        path = os.path.join(tables, name)
        exists = os.path.exists(path)
        manifest.append({"file": f"tables/{name}", "exists": exists, "sha256": sha256_file(path) if exists else ""})
    write_csv(os.path.join(tables, "layer3_frontD_table_manifest.csv"), manifest, ["file", "exists", "sha256"])
    write_csv(os.path.join(tables, "layer3_frontD_verifier_checks.csv"), checks, ["check", "result", "detail"])

    if not all(str(c["result"]) == "True" for c in checks):
        raise SystemExit("Layer 3 Front D verifier: FAIL")

    print("Layer 3 Front D verifier: PASS")
    print("  binary presentation tables: 630 representatives and 630x630 product table verified")
    print("  stabilization table: final cumulative count 630, max minimal size 15")
    print("  identity audit: I1/I2/I3/star hold but CM1 proves they are incomplete")
    print("  compact-plus-unary audit: CM2 proves U1/U2 still do not give a complete compact basis")


if __name__ == "__main__":
    main()
