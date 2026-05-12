#!/usr/bin/env python3
# verify_layer3_frontB_envelope.py
#
# Layer 3 Front B verifier:
# structural classification of the PAB left-operator composition envelope.
#
# No external dependencies.

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

S = (0, 1, 2)
M = tuple((r, c) for r in S for c in S)
IDX = {x: i for i, x in enumerate(M)}

def comp(a: int, b: int) -> int:
    return (-a - b) % 3

def pab(x: Tuple[int, int], y: Tuple[int, int]) -> Tuple[int, int]:
    r1, c1 = x
    r2, c2 = y
    if r1 != r2:
        return (r1, r2)
    if c1 != c2:
        return (r1, comp(c1, c2))
    return (r1, r1)

def L_map(x: Tuple[int, int]) -> Tuple[int, ...]:
    return tuple(IDX[pab(x, y)] for y in M)

def compose(f: Tuple[int, ...], g: Tuple[int, ...]) -> Tuple[int, ...]:
    """Composition f after g."""
    return tuple(f[g[i]] for i in range(len(g)))

def target_row(f: Tuple[int, ...]) -> int:
    rows = {M[f[i]][0] for i in range(len(M))}
    if len(rows) != 1:
        raise ValueError(f"not a row-target map: rows={rows}")
    return next(iter(rows))

def normalized_type(f: Tuple[int, ...]) -> Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]:
    """Normalize a row-r map by subtracting r from both source and output columns.
    The result is a triple of unary maps for source-row offsets 0,1,2."""
    r = target_row(f)
    blocks = []
    for q in S:
        source_row = (r + q) % 3
        vals = []
        for a in S:
            source_col = (r + a) % 3
            out_col = M[f[IDX[(source_row, source_col)]]][1]
            vals.append((out_col - r) % 3)
        blocks.append(tuple(vals))
    return tuple(blocks)  # type: ignore

def map_from_normalized_type(r: int, typ) -> Tuple[int, ...]:
    images = []
    for s, c in M:
        q = (s - r) % 3
        a = (c - r) % 3
        out_col = (r + typ[q][a]) % 3
        images.append(IDX[(r, out_col)])
    return tuple(images)

def const_func(a: int) -> Tuple[int, int, int]:
    return (a, a, a)

def beta(t: int) -> Tuple[int, int, int]:
    # Same-row block of L_(r,r+t), normalized to target row r.
    return tuple(0 if a == t else comp(t, a) for a in S)

def ucompose(f, g):
    return tuple(f[g[i]] for i in S)

FUNC_NAMES = {
    (0, 0, 0): "K0",
    (1, 1, 1): "K1",
    (2, 2, 2): "K2",
    (0, 1, 2): "I",
    (0, 2, 1): "S=beta0",
    (2, 0, 0): "P20=beta1",
    (1, 0, 0): "P10=beta2",
    (0, 1, 1): "P01",
    (0, 2, 2): "P02",
}
def fname(f) -> str:
    return FUNC_NAMES.get(tuple(f), "".join(map(str, f)))

def triple_str(t) -> str:
    return "|".join("".join(map(str, f)) for f in t)

def function_matrix_vector(f: Tuple[int, int, int]) -> List[int]:
    # 3x3 deterministic matrix vectorized by output row then input column.
    return [1 if f[x] == out else 0 for out in S for x in S]

def type_vector(typ) -> List[int]:
    v = []
    for block in typ:
        v.extend(function_matrix_vector(block))
    return v

def rank_q(rows: List[List[int]]) -> int:
    if not rows:
        return 0
    A = [[Fraction(x) for x in row] for row in rows]
    m, n = len(A), len(A[0])
    r = 0
    for c in range(n):
        piv = None
        for i in range(r, m):
            if A[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        pv = A[r][c]
        A[r] = [x / pv for x in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                fac = A[i][c]
                A[i] = [A[i][j] - fac * A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r

def solve_q(basis_cols: List[List[int]], y: List[int]):
    # Solve basis_cols * x = y over Q. basis_cols are column vectors.
    m, n = len(y), len(basis_cols)
    A = [[Fraction(basis_cols[j][i]) for j in range(n)] + [Fraction(y[i])] for i in range(m)]
    r = 0
    pivcols = []
    for c in range(n):
        piv = None
        for i in range(r, m):
            if A[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        pv = A[r][c]
        A[r] = [x / pv for x in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                fac = A[i][c]
                A[i] = [A[i][j] - fac * A[r][j] for j in range(n + 1)]
        pivcols.append(c)
        r += 1
    for i in range(r, m):
        if all(A[i][c] == 0 for c in range(n)) and A[i][n] != 0:
            return None
    sol = [Fraction(0) for _ in range(n)]
    for row, c in enumerate(pivcols):
        sol[c] = A[row][n]
    return sol

def frac_str(x: Fraction) -> str:
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator}"

def write_csv(path: Path, rows: List[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

def enumerate_closure():
    gens = [(L_map(x), x) for x in M]
    seen: Dict[Tuple[int, ...], Tuple[int, str]] = {}
    q = deque()
    for f, x in gens:
        name = f"L{x[0]}{x[1]}"
        if f not in seen:
            seen[f] = (1, name)
            q.append(f)
    while q:
        f = q.popleft()
        length, word = seen[f]
        for g, x in gens:
            h = compose(f, g)
            if h not in seen:
                seen[h] = (length + 1, f"{word} L{x[0]}{x[1]}")
                q.append(h)
    return seen

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    root = Path(args.root)
    tables = root / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    checks = []

    # Actual closure.
    closure = enumerate_closure()
    checks.append(("actual_closure_size_51", len(closure) == 51, len(closure)))

    actual_by_row = defaultdict(list)
    actual_types_by_row = defaultdict(set)
    rep_row0 = {}
    for f, (ln, word) in closure.items():
        r = target_row(f)
        typ = normalized_type(f)
        actual_by_row[r].append(f)
        actual_types_by_row[r].add(typ)
        if r == 0:
            if typ not in rep_row0 or ln < rep_row0[typ][0]:
                rep_row0[typ] = (ln, word)
    for r in S:
        checks.append((f"actual_row_{r}_has_17_elements", len(actual_by_row[r]) == 17, len(actual_by_row[r])))
        checks.append((f"actual_row_{r}_has_17_types", len(actual_types_by_row[r]) == 17, len(actual_types_by_row[r])))

    # Unary same-row semigroup.
    betas = [beta(t) for t in S]
    U = set(betas)
    frontier = list(betas)
    while frontier:
        new = []
        for f in frontier:
            for b in betas:
                for h in (ucompose(f, b), ucompose(b, f)):
                    if h not in U:
                        U.add(h)
                        new.append(h)
        frontier = new
    U = sorted(U)
    expected_U = {
        (0,1,2), (0,2,1), (2,0,0), (1,0,0), (0,1,1), (0,2,2)
    }
    checks.append(("unary_semigroup_size_6", len(U) == 6, len(U)))
    checks.append(("unary_semigroup_expected", set(U) == expected_U, sorted(U)))
    checks.append(("restricted_same_row_span_dim_5", rank_q([function_matrix_vector(f) for f in U]) == 5, rank_q([function_matrix_vector(f) for f in U])))

    unary_rows = []
    for t, b in enumerate(betas):
        unary_rows.append({
            "kind": "generator_beta",
            "name": f"beta_{t}",
            "function": "".join(map(str,b)),
            "image_size": len(set(b)),
            "note": f"same-row block of L_(r,r+{t})"
        })
    for f in U:
        unary_rows.append({
            "kind": "unary_semigroup_element",
            "name": fname(f),
            "function": "".join(map(str,f)),
            "image_size": len(set(f)),
            "note": "in <beta_0,beta_1,beta_2>"
        })
    write_csv(tables / "layer3_frontB_unary_semigroup.csv", unary_rows)

    # Predicted normal forms.
    predicted = set()
    origin = defaultdict(list)
    for a in S:
        typ = (const_func(a), const_func(a), const_func(a))
        predicted.add(typ)
        origin[typ].append(("constant", f"K{a}", "", ""))
    for g in U:
        for t in S:
            typ = (ucompose(g, beta(t)), const_func(g[1]), const_func(g[2]))
            predicted.add(typ)
            origin[typ].append(("nonconstant", fname(g), f"beta_{t}", f"g(1)={g[1]},g(2)={g[2]}"))

    checks.append(("predicted_type_count_17", len(predicted) == 17, len(predicted)))
    nonconst_count = sum(1 for typ in predicted if not (typ[0] == typ[1] == typ[2] and len(set(typ[0])) == 1))
    checks.append(("predicted_nonconstant_count_14", nonconst_count == 14, nonconst_count))

    sorted_types = sorted(predicted)
    type_id = {typ: i for i, typ in enumerate(sorted_types)}

    # Check predicted against actual rows and actual maps.
    for r in S:
        checks.append((f"predicted_equals_actual_types_row_{r}", actual_types_by_row[r] == predicted, ""))
        predicted_maps = {map_from_normalized_type(r, typ) for typ in predicted}
        actual_maps = set(actual_by_row[r])
        checks.append((f"predicted_equals_actual_maps_row_{r}", predicted_maps == actual_maps, ""))

    # Normal form table.
    nf_rows = []
    for typ in sorted_types:
        tid = type_id[typ]
        is_constant = typ[0] == typ[1] == typ[2] and len(set(typ[0])) == 1
        origins = origin[typ]
        min_len, word = rep_row0.get(typ, ("", ""))
        prefix_entries = []
        for kind, g, t, note in origins:
            if kind == "nonconstant":
                prefix_entries.append(f"{g};{t};{note}")
            else:
                prefix_entries.append(g)
        nf_rows.append({
            "type_id": tid,
            "kind": "constant" if is_constant else "nonconstant",
            "same_row_function": "".join(map(str, typ[0])),
            "same_row_name": fname(typ[0]),
            "cross_plus_function": "".join(map(str, typ[1])),
            "cross_plus_value": typ[1][0],
            "cross_minus_function": "".join(map(str, typ[2])),
            "cross_minus_value": typ[2][0],
            "normalized_type": triple_str(typ),
            "prefix_last_descriptions": " || ".join(prefix_entries),
            "min_word_length_row0": min_len,
            "representative_word_row0": word,
        })
    write_csv(tables / "layer3_frontB_monoid_17_normal_forms.csv", nf_rows)

    # Row component counts.
    row_rows = []
    for r in S:
        vectors = [type_vector(typ) for typ in actual_types_by_row[r]]
        # normalized vectors have same rank; maps into row r have same rank.
        dim = rank_q(vectors)
        row_rows.append({
            "target_row": r,
            "actual_monoid_elements": len(actual_by_row[r]),
            "actual_normalized_types": len(actual_types_by_row[r]),
            "predicted_normal_forms": len(predicted),
            "dim_W_r": dim,
        })
        checks.append((f"dim_W_{r}_is_9", dim == 9, dim))
    write_csv(tables / "layer3_frontB_row_component_counts.csv", row_rows)

    # Full envelope rank.
    all_vectors = []
    # Full 9x9 map vector; here use deterministic 9-output matrix flattened.
    def full_matrix_vec(fmap):
        arr = []
        for out in range(9):
            for inp in range(9):
                arr.append(1 if fmap[inp] == out else 0)
        return arr
    for f in closure:
        all_vectors.append(full_matrix_vec(f))
    full_dim = rank_q(all_vectors)
    checks.append(("full_envelope_dim_27", full_dim == 27, full_dim))

    # W_r W_s subset W_r.
    product_rows = []
    for r in S:
        for s in S:
            ok = True
            for A in actual_by_row[r]:
                for B in actual_by_row[s]:
                    C = compose(A, B)
                    if target_row(C) != r:
                        ok = False
                        break
                if not ok:
                    break
            product_rows.append({"left_W": r, "right_W": s, "product_target_row": r, "subset_left_W": ok})
            checks.append((f"W_{r}_W_{s}_subset_W_{r}", ok, ""))
    write_csv(tables / "layer3_frontB_cross_row_products.csv", product_rows)

    # Right action table by generator target offset and beta index.
    action_rows = []
    for typ in sorted_types:
        tid = type_id[typ]
        f0, f1, f2 = typ
        cross_values = {1: f1[0], 2: f2[0]}
        for q in S:
            for t in S:
                if q == 0:
                    out_typ = (ucompose(f0, beta(t)), const_func(f0[1]), const_func(f0[2]))
                    formula = "(f∘beta_t, kappa_f(1), kappa_f(2))"
                else:
                    a = cross_values[q]
                    out_typ = (const_func(a), const_func(a), const_func(a))
                    formula = f"constant collapse to K{a}"
                action_rows.append({
                    "input_type_id": tid,
                    "input_type": triple_str(typ),
                    "right_generator_target_offset": q,
                    "right_generator_beta": t,
                    "formula": formula,
                    "output_type_id": type_id[out_typ],
                    "output_type": triple_str(out_typ),
                })
                checks.append((f"right_action_type_{tid}_{q}_{t}_closed", out_typ in predicted, ""))
    write_csv(tables / "layer3_frontB_type_right_action.csv", action_rows)

    # Basis rank and expansions.
    # Symmetric basis: constants K0,K1,K2; generators G0,G1,G2; and three two-step same-row types.
    basis_triples = [
        (const_func(0), const_func(0), const_func(0)),
        (const_func(1), const_func(1), const_func(1)),
        (const_func(2), const_func(2), const_func(2)),
        (beta(0), const_func(1), const_func(2)),
        (beta(1), const_func(1), const_func(2)),
        (beta(2), const_func(1), const_func(2)),
        (ucompose(beta(0), beta(0)), const_func(beta(0)[1]), const_func(beta(0)[2])),
        (ucompose(beta(1), beta(1)), const_func(beta(1)[1]), const_func(beta(1)[2])),
        (ucompose(beta(2), beta(1)), const_func(beta(2)[1]), const_func(beta(2)[2])),
    ]
    # Last three are Q0=(I,2,1), Q1=(P02,0,0), Q2=(P01,0,0)
    basis_ids = [type_id[t] for t in basis_triples]
    basis_vecs = [type_vector(t) for t in basis_triples]
    basis_rank = rank_q(basis_vecs)
    checks.append(("chosen_basis_rank_9", basis_rank == 9, {"basis_ids": basis_ids, "rank": basis_rank}))

    basis_rows = []
    basis_names = ["K0", "K1", "K2", "G0", "G1", "G2", "Q0=L00L00", "Q1=L01L01", "Q2=L02L01"]
    for name, typ, tid in zip(basis_names, basis_triples, basis_ids):
        basis_rows.append({
            "basis_name": name,
            "type_id": tid,
            "normalized_type": triple_str(typ),
            "same_row_name": fname(typ[0]),
            "cross_plus": typ[1][0],
            "cross_minus": typ[2][0],
        })
    write_csv(tables / "layer3_frontB_Wr_basis.csv", basis_rows)

    expansion_rows = []
    for typ in sorted_types:
        sol = solve_q(basis_vecs, type_vector(typ))
        checks.append((f"type_{type_id[typ]}_expands_in_basis", sol is not None, ""))
        row = {
            "type_id": type_id[typ],
            "normalized_type": triple_str(typ),
        }
        for name, coeff in zip(basis_names, sol):
            row[name] = frac_str(coeff)
        expansion_rows.append(row)
    write_csv(tables / "layer3_frontB_basis_expansion.csv", expansion_rows)

    # Guardrail: restricted same-row closure is smaller.
    guard_rows = [
        {
            "object": "restricted same-row unary semigroup <beta_0,beta_1,beta_2>",
            "elements": len(U),
            "span_dim": rank_q([function_matrix_vector(f) for f in U]),
            "interpretation": "not Mat_3; this is the old A_r guardrail",
        },
        {
            "object": "full row-target component W_r",
            "elements": len(predicted),
            "span_dim": basis_rank,
            "interpretation": "dimension-9 object used by Layer 3 v1.2",
        },
        {
            "object": "full composition envelope E",
            "elements": len(closure),
            "span_dim": full_dim,
            "interpretation": "E = W_0 direct-sum W_1 direct-sum W_2",
        },
    ]
    write_csv(tables / "layer3_frontB_restricted_same_row_guardrail.csv", guard_rows)

    # Status registry.
    status_rows = [
        {"claim": "composition closure has 51 maps", "status": "checked", "value": len(closure)},
        {"claim": "each target row contains 17 maps", "status": "checked", "value": str({r: len(actual_by_row[r]) for r in S})},
        {"claim": "unary same-row semigroup has 6 maps", "status": "checked", "value": len(U)},
        {"claim": "restricted same-row span dimension is 5", "status": "checked", "value": rank_q([function_matrix_vector(f) for f in U])},
        {"claim": "normal-form theorem: 3 constants + 14 nonconstant types per row", "status": "checked", "value": len(predicted)},
        {"claim": "dim W_r=9 for r=0,1,2", "status": "checked", "value": str([row["dim_W_r"] for row in row_rows])},
        {"claim": "dim E=27", "status": "checked", "value": full_dim},
        {"claim": "W_r W_s subset W_r", "status": "checked", "value": "all 9 row products"},
        {"claim": "chosen 9-element basis spans all 17 row types", "status": "checked", "value": str(basis_ids)},
    ]
    write_csv(tables / "layer3_frontB_status_registry.csv", status_rows)

    check_rows = [{"check": name, "passed": bool(ok), "detail": str(detail)} for name, ok, detail in checks]
    write_csv(tables / "layer3_frontB_verifier_checks.csv", check_rows)

    failures = [r for r in check_rows if not r["passed"]]
    if failures:
        print("Layer 3 Front B verifier: FAIL")
        for f in failures[:20]:
            print("  FAIL:", f["check"], f["detail"])
        raise SystemExit(1)

    print("Layer 3 Front B verifier: PASS")
    print("  composition closure: |Mon<L_x>|=51, split as 3 rows x 17 normal forms")
    print("  unary core: <beta_0,beta_1,beta_2> has 6 maps and restricted span dimension 5")
    print("  normal forms: per row = 3 constants + 14 nonconstant prefix-beta types")
    print("  envelope dimensions: dim W_r=9 for all r, dim E=27")
    print("  multiplication law: W_r W_s subset W_r, with right-action table generated")
    print("  guardrail: dimension-9 object is W_r, not the restricted same-row closure")

if __name__ == "__main__":
    main()
