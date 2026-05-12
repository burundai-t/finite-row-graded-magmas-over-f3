#!/usr/bin/env python3
# verify_layer3_linearization_final.py
#
# Smoke verifier for Layer 3 v1: PAB linearization package.
# It checks the finite core used in layer3_linearization_v1.md and writes compact CSV tables.

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from itertools import product, permutations
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import sympy as sp

S = (0, 1, 2)
M = tuple((r, c) for r in S for c in S)
IDX = {x: i for i, x in enumerate(M)}
N = len(M)

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

def row_comp_op(x: Tuple[int, int], y: Tuple[int, int]) -> Tuple[int, int]:
    r1, c1 = x
    r2, c2 = y
    if r1 != r2:
        return (r1, comp(r1, r2))
    if c1 != c2:
        return (r1, comp(c1, c2))
    return (r1, r1)

def L_matrix(x: Tuple[int, int], op=pab) -> sp.Matrix:
    A = sp.zeros(N, N)
    for y in M:
        A[IDX[op(x, y)], IDX[y]] = 1
    return A

L = {x: L_matrix(x) for x in M}
I9 = sp.eye(N)
Z9 = sp.zeros(N, N)

def flat(A: sp.Matrix) -> List[int]:
    return [int(A[i, j]) for i in range(A.rows) for j in range(A.cols)]

def rank_of_mats(mats: Iterable[sp.Matrix]) -> int:
    rows = [flat(A) for A in mats]
    return sp.Matrix(rows).rank()

def restrict_to_fiber(A: sp.Matrix, r: int) -> sp.Matrix:
    inds = [IDX[(r, c)] for c in S]
    return A.extract(inds, inds)

def span_basis_closure(gens: List[sp.Matrix]) -> List[sp.Matrix]:
    basis: List[sp.Matrix] = []
    def add(A: sp.Matrix) -> bool:
        nonlocal basis
        if not basis:
            if A != sp.zeros(A.rows, A.cols):
                basis.append(A)
                return True
            return False
        before = rank_of_mats(basis)
        after = rank_of_mats(basis + [A])
        if after > before:
            basis.append(A)
            return True
        return False

    for G in gens:
        add(G)

    changed = True
    while changed:
        changed = False
        current = list(basis)
        for A in current:
            for B in current:
                if add(A * B):
                    changed = True
                    if len(basis) == gens[0].rows * gens[0].cols:
                        return basis
    return basis

def perm_matrix_for_map(domain: Tuple[Tuple[int,int], ...], f) -> sp.Matrix:
    n = len(domain)
    idx = {x: i for i, x in enumerate(domain)}
    P = sp.zeros(n, n)
    for x in domain:
        P[idx[f(x)], idx[x]] = 1
    return P

def cycle_type(p: Tuple[int, int, int]) -> Tuple[int, ...]:
    seen = set()
    lens = []
    for i in S:
        if i in seen:
            continue
        j = i
        Lc = 0
        while j not in seen:
            seen.add(j)
            Lc += 1
            j = p[j]
        lens.append(Lc)
    return tuple(sorted(lens, reverse=True))

def s3_decomposition_offdiag() -> Dict[str, int]:
    off = tuple((r, c) for r, c in M if r != c)
    chars_by_class = {(1,1,1): [], (3,): [], (2,1): []}
    for p in permutations(S):
        fixed = sum(1 for x in off if (p[x[0]], p[x[1]]) == x)
        chars_by_class[cycle_type(p)].append(fixed)
    chi = {
        "id": chars_by_class[(1,1,1)][0],
        "3cycle": chars_by_class[(3,)][0],
        "transposition": chars_by_class[(2,1)][0],
    }
    # Class order: id, 3cycle, transposition. Class sizes 1,2,3.
    irreps = {
        "triv": (1, 1, 1),
        "sign": (1, 1, -1),
        "std": (2, -1, 0),
    }
    x = (chi["id"], chi["3cycle"], chi["transposition"])
    sizes = (1, 2, 3)
    mults = {}
    for name, ch in irreps.items():
        mults[name] = sum(sizes[i] * x[i] * ch[i] for i in range(3)) // 6
    return {"chi_id": chi["id"], "chi_3cycle": chi["3cycle"], "chi_transposition": chi["transposition"], **mults}

def absorption_matrix_and_transitions():
    off = tuple((r, c) for r, c in M if r != c)
    idx = {x: i for i, x in enumerate(off)}
    A = sp.zeros(len(off), len(off))
    for x in off:
        for y in off:
            if pab(x, y) == x:
                A[idx[x], idx[y]] = 1
    def C(x):
        r, c = x
        return (c, comp(r, c))
    def J(x):
        r, c = x
        return (c, r)
    PC = perm_matrix_for_map(off, C)
    PJ = perm_matrix_for_map(off, J)
    return off, A, PC, PJ, C, J

def enumerate_endomorphisms():
    # Any homomorphism respects rows through a map rho:S->S because f((r,c))^2=f((r,r)).
    # Enumerate the resulting 27 * 9^3 = 19683 candidates and check the homomorphism equation.
    endos = []
    for rho in product(S, repeat=3):
        row_maps_options = []
        for r in S:
            opts = []
            for vals in product(S, repeat=3):
                if vals[r] == rho[r]:
                    opts.append(vals)
            row_maps_options.append(opts)
        for phi0 in row_maps_options[0]:
            for phi1 in row_maps_options[1]:
                for phi2 in row_maps_options[2]:
                    phis = (phi0, phi1, phi2)
                    f = {}
                    for x in M:
                        r, c = x
                        f[x] = (rho[r], phis[r][c])
                    ok = True
                    for x in M:
                        if not ok:
                            break
                        for y in M:
                            if f[pab(x, y)] != pab(f[x], f[y]):
                                ok = False
                                break
                    if ok:
                        endos.append(f)
    return endos

def classify_endomorphism(f) -> str:
    image = set(f.values())
    if len(image) == 1:
        val = next(iter(image))
        if val in [(0,0), (1,1), (2,2)]:
            return f"constant_{val[0]}"
        return "constant_other"
    # automorphism: diagonal action of a permutation on both coordinates
    for p in permutations(S):
        if all(f[(r,c)] == (p[r], p[c]) for r,c in M):
            return "automorphism"
    return "other"

def hom_dim_for_endomorphism(f) -> int:
    # Constraint: T L_x = L_{f(x)} T for all x.
    # vec(T L_x - L_{f(x)}T) = (L_x.T ⊗ I - I ⊗ L_{f(x)}) vec(T).
    blocks = []
    for x in M:
        A = sp.kronecker_product(L[x].T, I9) - sp.kronecker_product(I9, L[f[x]])
        blocks.append(A)
    C = sp.Matrix.vstack(*blocks)
    return N*N - C.rank()

def mat_unit(i: int, j: int) -> sp.Matrix:
    A = sp.zeros(3,3)
    A[i,j] = 1
    return A

def verify_row_contraction() -> bool:
    J = sp.ones(3,3)
    for i, j, k, l in product(S, repeat=4):
        if i == k:
            continue
        lhs = mat_unit(i,j) * J * mat_unit(k,l).T
        rhs = mat_unit(i,k)
        if lhs != rhs:
            return False
    return True

def mat_mult_basis(x, y):
    r1, c1 = x
    r2, c2 = y
    if c1 == r2:
        return (r1, c2)
    return None

def count_matrix_product_coincidences() -> int:
    count = 0
    for x in M:
        for y in M:
            if mat_mult_basis(x,y) == pab(x,y):
                count += 1
    return count

def verify_identities() -> Dict[str, bool]:
    res = {}
    res["I1"] = all(pab(pab(x,y), pab(x,y)) == pab(x,x) for x in M for y in M)
    res["I2"] = all(pab(pab(x,x), pab(y,y)) == pab(pab(x,y), pab(y,x)) for x in M for y in M)
    res["I3"] = all(pab(pab(x,x), pab(y,x)) == pab(pab(x,y), pab(y,y)) for x in M for y in M)
    res["star"] = all(pab(z, pab(z,w)) == pab(pab(z,w), z) for z in M for w in M)
    return res

def H_total(op) -> Tuple[int, int, int, int]:
    Htot = 0
    Hplus = 0
    Hminus = 0
    Nminus = 0
    for x in M:
        for y in M:
            for z in M:
                I_mis = 0
                B_mis = 0
                xy = op(x,y)
                yz = op(y,z)
                xyz_left = op(xy,z)
                xyz_right = op(x,yz)
                for w in M:
                    if op(xy, op(z,w)) != op(x, op(yz,w)):
                        I_mis += 1
                    if op(xyz_left, w) != op(xyz_right, w):
                        B_mis += 1
                h = 2 * (I_mis - B_mis)
                Htot += h
                if h > 0:
                    Hplus += h
                elif h < 0:
                    Hminus += -h
                    Nminus += 1
    return Htot, Hplus, Hminus, Nminus

def free_counts(max_size: int):
    # Dynamic programming on already-induced functions. A word is represented by
    # a function M x M -> M encoded as a tuple of 81 element indices. Since
    # composition only depends on the induced functions of the two subwords,
    # using distinct functions at each lower size is exact and much faster than
    # recursively evaluating all words.
    arg_pairs = tuple((a, b) for a in M for b in M)
    pab_idx = [[IDX[pab(M[i], M[j])] for j in range(N)] for i in range(N)]

    f_x = tuple(IDX[a] for a, b in arg_pairs)
    f_y = tuple(IDX[b] for a, b in arg_pairs)

    funcs_by_size = {1: {f_x, f_y}}
    word_counts = {1: 2}
    seen = set()
    rows = []
    for n in range(1, max_size + 1):
        if n > 1:
            funcs = set()
            words = 0
            for k in range(1, n):
                words += word_counts[k] * word_counts[n-k]
                for f in funcs_by_size[k]:
                    for g in funcs_by_size[n-k]:
                        funcs.add(tuple(pab_idx[f[i]][g[i]] for i in range(len(arg_pairs))))
            funcs_by_size[n] = funcs
            word_counts[n] = words
        funcs_n = funcs_by_size[n]
        new = funcs_n - seen
        seen |= funcs_n
        rows.append({"size": n, "words": word_counts[n], "new_functions": len(new), "total_distinct": len(seen)})
    return rows

def write_csv(path: Path, rows: List[dict]):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]), help="Layer 3 package root")
    parser.add_argument("--free-max", type=int, default=9, help="Recompute free-magma counts through this level (default: 9)")
    args = parser.parse_args()

    root = Path(args.root)
    tables = root / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    checks = []

    # L-operator core.
    span_dim = rank_of_mats(L.values())
    checks.append(("dim_span_Lx", span_dim == 9, span_dim))

    rank_rows = []
    spectral_rows = []
    for x in M:
        A = L[x]
        r = x[0]
        image_ok = True
        allowed = {IDX[(r,c)] for c in S}
        for col in range(N):
            nz = {i for i in range(N) if A[i,col] != 0}
            if not nz.issubset(allowed):
                image_ok = False
        checks.append((f"image_L_{x}_in_F_row", image_ok, ""))
        rank_rows.append({"x": str(x), "type": "diagonal" if x[0] == x[1] else "off_diagonal", "rank": A.rank()})
        checks.append((f"rank_L_{x}", A.rank() == 3, A.rank()))

        is_diag = x[0] == x[1]
        cubic_zero = (A**3 - A) == Z9
        quartic_zero = (A**4 - A**2) == Z9
        eigenvals = A.eigenvals()
        eig_summary = ";".join(f"{ev}:{mult}" for ev, mult in sorted(eigenvals.items(), key=lambda kv: str(kv[0])))
        if is_diag:
            checks.append((f"diag_minpoly_cubic_{x}", cubic_zero, ""))
            checks.append((f"diag_not_smaller_rank_{x}", (A**2 - A) != Z9 and (A**2 + A) != Z9, ""))
            minpoly = "t(t-1)(t+1)"
            zero_alg = eigenvals.get(sp.Integer(0), 0)
            zero_geo = N - A.rank()
            j2zero = 0
        else:
            checks.append((f"offdiag_quartic_{x}", quartic_zero, ""))
            checks.append((f"offdiag_not_cubic_{x}", not cubic_zero, ""))
            minpoly = "t^2(t-1)(t+1)"
            zero_alg = eigenvals.get(sp.Integer(0), 0)
            zero_geo = N - A.rank()
            j2zero = (N - (A**2).rank()) - zero_geo
            checks.append((f"offdiag_one_J2_zero_{x}", j2zero == 1, j2zero))
        spectral_rows.append({
            "x": str(x),
            "type": "diagonal" if is_diag else "off_diagonal",
            "eigenvalues": eig_summary,
            "minimal_polynomial": minpoly,
            "zero_alg_mult": zero_alg,
            "zero_geom_mult": zero_geo,
            "J2_blocks_at_zero": j2zero,
        })

    write_csv(tables / "layer3_operator_rank_table.csv", rank_rows)
    write_csv(tables / "layer3_operator_spectrum_table.csv", spectral_rows)

    # Global associative envelope under composition.
    # This is the accurate v1 formulation: the full composition monoid generated by all L_x
    # has 51 elements and its linear span decomposes into three 9-dimensional row-target
    # components W_r = {T : Im(T) subset F_r}.
    op_set = {tuple(flat(A)) for A in L.values()}
    changed = True
    while changed:
        changed = False
        current = [sp.Matrix(N, N, list(v)) for v in op_set]
        for A0 in current:
            for B0 in current:
                C0 = tuple(flat(A0 * B0))
                if C0 not in op_set:
                    op_set.add(C0)
                    changed = True
    envelope = [sp.Matrix(N, N, list(v)) for v in op_set]
    closure_size = len(envelope)
    envelope_dim = rank_of_mats(envelope)
    checks.append(("composition_monoid_size", closure_size == 51, closure_size))
    checks.append(("composition_envelope_span_dim", envelope_dim == 27, envelope_dim))

    envelope_rows = []
    W_by_row = {}
    for r in S:
        allowed = {IDX[(r,c)] for c in S}
        Wr = []
        for A0 in envelope:
            ok = True
            for col in range(N):
                nz = {i for i in range(N) if A0[i,col] != 0}
                if not nz.issubset(allowed):
                    ok = False
                    break
            if ok:
                Wr.append(A0)
        W_by_row[r] = Wr
        dim_wr = rank_of_mats(Wr)
        envelope_rows.append({"row": r, "monoid_elements_in_Wr": len(Wr), "dim_Wr": dim_wr})
        checks.append((f"W_{r}_dim", dim_wr == 9, dim_wr))
    # Left-row absorption of the envelope: W_r W_s subset W_r.
    absorption_rows = []
    for r in S:
        allowed = {IDX[(r,c)] for c in S}
        for s in S:
            ok = True
            for A0 in W_by_row[r]:
                for B0 in W_by_row[s]:
                    C0 = A0 * B0
                    for col in range(N):
                        nz = {i for i in range(N) if C0[i,col] != 0}
                        if not nz.issubset(allowed):
                            ok = False
                            break
                    if not ok:
                        break
                if not ok:
                    break
            absorption_rows.append({"left_W": r, "right_W": s, "product_subset_left_W": ok})
            checks.append((f"W_{r}_times_W_{s}_subset_W_{r}", ok, ""))
    write_csv(tables / "layer3_envelope_decomposition.csv", envelope_rows)
    write_csv(tables / "layer3_envelope_absorption_law.csv", absorption_rows)

    # S3 representation and absorption matrix.
    rep = s3_decomposition_offdiag()
    write_csv(tables / "layer3_s3_offdiag_character.csv", [rep])
    checks.append(("S3_offdiag_character_corrected", (rep["chi_id"], rep["chi_3cycle"], rep["chi_transposition"]) == (6,0,0), rep))
    checks.append(("S3_offdiag_decomposition", (rep["triv"], rep["sign"], rep["std"]) == (1,1,2), rep))

    off, Aabs, PC, PJ, Cmap, Jmap = absorption_matrix_and_transitions()
    checks.append(("A_abs_equals_C_plus_J_transpose", Aabs == (PC + PJ).T, ""))
    evals = Aabs.eigenvals()
    eval_rows = [{"eigenvalue": str(ev), "multiplicity": mult} for ev, mult in sorted(evals.items(), key=lambda kv: str(kv[0]))]
    write_csv(tables / "layer3_absorption_spectrum.csv", eval_rows)
    checks.append(("A_abs_spectrum", Counter({str(k): v for k, v in evals.items()}) == Counter({"2":1, "0":3, "-1":2}), evals))
    transition_rows = []
    for x in off:
        transition_rows.append({"x": str(x), "C(x)": str(Cmap(x)), "J(x)": str(Jmap(x)), "absorbed_neighbors": str([y for y in off if pab(x,y)==x])})
    write_csv(tables / "layer3_absorption_transitions.csv", transition_rows)

    # Endomorphisms and Hom dimensions.
    endos = enumerate_endomorphisms()
    class_counts = Counter(classify_endomorphism(f) for f in endos)
    checks.append(("endomorphism_count", len(endos) == 9, len(endos)))
    checks.append(("endomorphism_classes", class_counts["automorphism"] == 6 and sum(v for k,v in class_counts.items() if k.startswith("constant_")) == 3, dict(class_counts)))

    hom_rows = []
    for idx_e, f in enumerate(endos):
        cls = classify_endomorphism(f)
        dim = hom_dim_for_endomorphism(f)
        hom_rows.append({"endomorphism_index": idx_e, "class": cls, "hom_dim": dim})
        if cls == "automorphism":
            checks.append((f"hom_dim_auto_{idx_e}", dim == 1, dim))
        elif cls.startswith("constant_"):
            checks.append((f"hom_dim_constant_{idx_e}", dim == 2, dim))
    write_csv(tables / "layer3_endomorphism_hom_table.csv", hom_rows)
    checks.append(("total_Hom_dimension", sum(row["hom_dim"] for row in hom_rows) == 12, sum(row["hom_dim"] for row in hom_rows)))

    # Row contraction and matrix-product comparison.
    checks.append(("row_contraction_AJBt_cross_basis", verify_row_contraction(), ""))
    coincidences = count_matrix_product_coincidences()
    checks.append(("matrix_product_coincidences", coincidences == 9, coincidences))
    write_csv(tables / "layer3_mat3_bridge_table.csv", [
        {"claim": "cross-row AJB^T formula on basis", "value": verify_row_contraction()},
        {"claim": "PAB/matrix-product basis coincidences", "value": coincidences},
    ])

    # Identities.
    ids = verify_identities()
    write_csv(tables / "layer3_identity_audit.csv", [{"identity": k, "holds": v} for k, v in ids.items()])
    for k, v in ids.items():
        checks.append((f"identity_{k}", v, ""))

    # Hidden continuation contrast for PAB and row-complement.
    H_pab = H_total(pab)
    H_comp = H_total(row_comp_op)
    write_csv(tables / "layer3_H_bridge_pab_comp.csv", [
        {"point": "PAB", "H_tot": H_pab[0], "H_plus": H_pab[1], "H_minus": H_pab[2], "N_minus": H_pab[3]},
        {"point": "row_complement", "H_tot": H_comp[0], "H_plus": H_comp[1], "H_minus": H_comp[2], "N_minus": H_comp[3]},
    ])
    checks.append(("H_PAB_profile", H_pab == (7020,7020,0,0), H_pab))
    checks.append(("H_row_complement_same_profile", H_comp == (7020,7020,0,0), H_comp))

    # Free magma smoke count.
    max_free = args.free_max
    fc = free_counts(max_free)
    write_csv(tables / "layer3_free_magma_counts_smoke.csv", fc)
    expected = {
        1: (2, 2, 2),
        2: (4, 4, 6),
        3: (16, 12, 18),
        4: (80, 18, 36),
        5: (448, 50, 86),
        6: (2688, 52, 138),
        7: (16896, 106, 244),
        8: (109824, 32, 276),
        9: (732160, 80, 356),
    }
    for row in fc:
        n = row["size"]
        checks.append((f"free_count_size_{n}", (row["words"], row["new_functions"], row["total_distinct"]) == expected[n], row))

    # Status registry.
    status_rows = [
        {"claim": "dim span{L_x}=9", "status": "checked", "value": span_dim},
        {"claim": "rank L_x=3 for all x", "status": "checked", "value": "all"},
        {"claim": "diagonal minpoly t(t-1)(t+1)", "status": "checked", "value": "3 operators"},
        {"claim": "off-diagonal minpoly t^2(t-1)(t+1)", "status": "checked", "value": "6 operators"},
        {"claim": "composition envelope span decomposes into three W_r of dimension 9 and W_r W_s subset W_r", "status": "checked", "value": "monoid size 51; span dim 27"},
        {"claim": "S3 character on M^x is (6,0,0)", "status": "checked", "value": str((rep["chi_id"], rep["chi_3cycle"], rep["chi_transposition"]))},
        {"claim": "A_abs=(C+J)^T spectrum {2,0,0,0,-1,-1}", "status": "checked", "value": str(evals)},
        {"claim": "End(M)=6 automorphisms + 3 constants", "status": "checked", "value": len(endos)},
        {"claim": "sum dim Hom_phi=12", "status": "checked", "value": sum(row["hom_dim"] for row in hom_rows)},
        {"claim": "cross-row formula AJB^T", "status": "checked", "value": "basis"},
        {"claim": "I1,I2,I3,star", "status": "checked", "value": str(ids)},
        {"claim": "H profile PAB=row-complement=(7020,7020,0,0)", "status": "checked", "value": str(H_pab)},
        {"claim": f"free magma counts through level {max_free}", "status": "checked", "value": "dynamic function-DP"},
    ]
    write_csv(tables / "layer3_status_registry.csv", status_rows)

    check_rows = [{"check": name, "passed": bool(ok), "detail": str(detail)} for name, ok, detail in checks]
    write_csv(tables / "layer3_verifier_checks.csv", check_rows)

    failures = [row for row in check_rows if not row["passed"]]
    if failures:
        print("Layer 3 linearization verifier v1: FAIL")
        for f in failures[:20]:
            print("  FAIL:", f["check"], f["detail"])
        raise SystemExit(1)

    print("Layer 3 linearization verifier v1.1: PASS")
    print("  operator core: dim span{L_x}=9, rank=3, spectra/minpolys/Jordan checked")
    print("  associative envelope: monoid size 51, span dim 27, W_r dimensions 9")
    print("  S3/absorption: corrected character (6,0,0), A_abs=(C+J)^T, spectrum checked")
    print("  End/Hom: 9 endomorphisms, Hom dimensions 6*1+3*2=12 checked")
    print("  Mat_3 bridge: AJB^T cross-row formula and 9 basis coincidences checked")
    print("  identities and H-bridge: I1/I2/I3/star and PAB/competitor H profile checked")
    print(f"  free magma smoke: counts checked through level {max_free}")

if __name__ == "__main__":
    main()
