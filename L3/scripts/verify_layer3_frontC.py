#!/usr/bin/env python3
"""
Layer 3 Front C verifier: closed form for Hom_{e_r}.

This verifier checks the exact finite claims behind the formula

    Hom_{e_r} = { u eps^T : u in Fix(L_{(r,r)}) }

where eps is the total augmentation functional and

    Fix(L_{(r,r)}) = span{ e_(r,r), sum_{c != r} e_(r,c) }.

It also audits the automorphism intertwiner dimensions and writes CSV tables.
"""

from __future__ import annotations

import csv
import os
from itertools import permutations
from typing import Dict, Iterable, List, Sequence, Tuple

S = (0, 1, 2)
M = [(r, c) for r in S for c in S]
IDX = {x: i for i, x in enumerate(M)}
N = len(M)


def complement(a: int, b: int) -> int:
    return (-a - b) % 3


def pab(x: Tuple[int, int], y: Tuple[int, int]) -> Tuple[int, int]:
    r1, c1 = x
    r2, c2 = y
    if r1 != r2:
        return (r1, r2)
    if c1 != c2:
        return (r1, complement(c1, c2))
    return (r1, r1)


def zero_matrix(rows: int, cols: int) -> List[List[int]]:
    return [[0 for _ in range(cols)] for _ in range(rows)]


def matmul(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    rows = len(A)
    mid = len(B)
    cols = len(B[0])
    out = zero_matrix(rows, cols)
    for i in range(rows):
        Ai = A[i]
        for k in range(mid):
            aik = Ai[k]
            if aik:
                Bk = B[k]
                for j in range(cols):
                    out[i][j] += aik * Bk[j]
    return out


def matsub(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    return [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


def mat_eq(A: List[List[int]], B: List[List[int]]) -> bool:
    return A == B


def rank_mod(mat: List[List[int]], p: int = 1000003) -> int:
    """Exact Gaussian rank over F_p."""
    A = [[x % p for x in row] for row in mat if any(x % p for x in row)]
    if not A:
        return 0
    m = len(A)
    n = len(A[0])
    rank = 0
    row = 0
    for col in range(n):
        pivot = None
        for i in range(row, m):
            if A[i][col] % p:
                pivot = i
                break
        if pivot is None:
            continue
        A[row], A[pivot] = A[pivot], A[row]
        inv = pow(A[row][col], p - 2, p)
        A[row] = [(val * inv) % p for val in A[row]]
        for i in range(m):
            if i != row and A[i][col] % p:
                factor = A[i][col]
                A[i] = [(A[i][j] - factor * A[row][j]) % p for j in range(n)]
        rank += 1
        row += 1
        if row == m:
            break
    return rank


def matrix_rank_int(mat: List[List[int]]) -> int:
    return rank_mod(mat, 1000003)


# Left translations.
L: Dict[Tuple[int, int], List[List[int]]] = {}
for x in M:
    mat = zero_matrix(N, N)
    for y in M:
        mat[IDX[pab(x, y)]][IDX[y]] = 1
    L[x] = mat


def permutation_matrix(perm: Tuple[int, int, int]) -> List[List[int]]:
    P = zero_matrix(N, N)
    for x in M:
        image = (perm[x[0]], perm[x[1]])
        P[IDX[image]][IDX[x]] = 1
    return P


def outer(u: Sequence[int], v: Sequence[int]) -> List[List[int]]:
    return [[u[i] * v[j] for j in range(len(v))] for i in range(len(u))]


def transpose(A: List[List[int]]) -> List[List[int]]:
    return [list(row) for row in zip(*A)]


def hom_constraint_matrix(phi: Dict[Tuple[int, int], Tuple[int, int]]) -> List[List[int]]:
    """Build row-major equations for T L_x = L_{phi(x)} T."""
    rows: List[List[int]] = []
    for x in M:
        Lx = L[x]
        Lphi = L[phi[x]]
        # Every scalar equation at output row a and input column b.
        for a in range(N):
            for b in range(N):
                row = [0] * (N * N)
                # (T Lx)[a,b] = sum_j T[a,j] Lx[j,b].
                for j in range(N):
                    if Lx[j][b]:
                        row[a * N + j] += Lx[j][b]
                # (Lphi T)[a,b] = sum_i Lphi[a,i] T[i,b].
                for i in range(N):
                    if Lphi[a][i]:
                        row[i * N + b] -= Lphi[a][i]
                rows.append(row)
    return rows


def constant_phi(r: int) -> Dict[Tuple[int, int], Tuple[int, int]]:
    return {x: (r, r) for x in M}


def automorphism_phi(perm: Tuple[int, int, int]) -> Dict[Tuple[int, int], Tuple[int, int]]:
    return {x: (perm[x[0]], perm[x[1]]) for x in M}


def basis_u_diag(r: int) -> List[int]:
    u = [0] * N
    u[IDX[(r, r)]] = 1
    return u


def basis_u_offsum(r: int) -> List[int]:
    u = [0] * N
    for c in S:
        if c != r:
            u[IDX[(r, c)]] = 1
    return u


def augmentation() -> List[int]:
    return [1] * N


def check_intertwiner(T: List[List[int]], phi: Dict[Tuple[int, int], Tuple[int, int]]) -> bool:
    for x in M:
        lhs = matmul(T, L[x])
        rhs = matmul(L[phi[x]], T)
        if lhs != rhs:
            return False
    return True


def mat_to_flat(T: List[List[int]]) -> List[int]:
    return [T[i][j] for i in range(N) for j in range(N)]


def vector_support(v: Sequence[int]) -> str:
    supp = []
    for i, val in enumerate(v):
        if val:
            supp.append(f"{M[i]}:{val}")
    return "; ".join(supp) if supp else "0"


def row_label(x: Tuple[int, int]) -> str:
    return f"({x[0]},{x[1]})"


def find_collapse_tree() -> List[Dict[str, str]]:
    """Spanning tree for relation generated by x*y ~ x'*y."""
    edges = []
    for y in M:
        # pick one witness left operand for each output from source y
        output_to_left: Dict[Tuple[int, int], Tuple[int, int]] = {}
        for x in M:
            output_to_left.setdefault(pab(x, y), x)
        outs = list(output_to_left)
        for i, a in enumerate(outs):
            for b in outs[i + 1:]:
                edges.append((a, b, y, output_to_left[a], output_to_left[b]))
    base = (0, 0)
    seen = {base}
    table: List[Dict[str, str]] = []
    changed = True
    while changed and len(seen) < len(M):
        changed = False
        for a, b, y, x_a, x_b in edges:
            if a in seen and b not in seen:
                seen.add(b)
                table.append({
                    "new_vertex": row_label(b),
                    "previous_vertex": row_label(a),
                    "source_y": row_label(y),
                    "left_for_previous": row_label(x_a),
                    "left_for_new": row_label(x_b),
                    "difference": f"e_{row_label(b)} - e_{row_label(a)} = (L_{row_label(x_b)} - L_{row_label(x_a)}) e_{row_label(y)}",
                })
                changed = True
            elif b in seen and a not in seen:
                seen.add(a)
                table.append({
                    "new_vertex": row_label(a),
                    "previous_vertex": row_label(b),
                    "source_y": row_label(y),
                    "left_for_previous": row_label(x_b),
                    "left_for_new": row_label(x_a),
                    "difference": f"e_{row_label(a)} - e_{row_label(b)} = (L_{row_label(x_a)} - L_{row_label(x_b)}) e_{row_label(y)}",
                })
                changed = True
            if len(seen) == len(M):
                break
    if len(seen) != len(M):
        raise AssertionError("collapse graph is not connected")
    return table


def write_csv(path: str, rows: List[Dict[str, object]], fieldnames: Sequence[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main() -> None:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    tables = os.path.join(root, "tables")
    os.makedirs(tables, exist_ok=True)

    eps = augmentation()

    # Exact formula basis for constants.
    formula_rows: List[Dict[str, object]] = []
    fixed_rows: List[Dict[str, object]] = []
    dimension_rows: List[Dict[str, object]] = []
    check_rows: List[Dict[str, object]] = []

    all_constant_ok = True
    for r in S:
        phi = constant_phi(r)
        u0 = basis_u_diag(r)
        u1 = basis_u_offsum(r)
        T0 = outer(u0, eps)
        T1 = outer(u1, eps)
        ok0 = check_intertwiner(T0, phi)
        ok1 = check_intertwiner(T1, phi)
        indep_rank = matrix_rank_int([mat_to_flat(T0), mat_to_flat(T1)])
        C = hom_constraint_matrix(phi)
        constraint_rank = rank_mod(C)
        dim_upper = N * N - constraint_rank
        formula_rows.append({
            "constant_endomorphism": f"e_{r}",
            "formula": "T = u eps^T",
            "epsilon": "total augmentation: eps(e_x)=1 for all x",
            "basis_1_u": vector_support(u0),
            "basis_2_u": vector_support(u1),
            "closed_form": f"u in span{{e_({r},{r}), " + "+".join([f"e_({r},{c})" for c in S if c != r]) + "}",
            "dimension": 2,
        })
        fixed_rows.append({
            "r": r,
            "idempotent": row_label((r, r)),
            "fixed_space": f"Fix(L_({r},{r}))",
            "basis_1": f"e_({r},{r})",
            "basis_2": "+".join([f"e_({r},{c})" for c in S if c != r]),
            "dimension": 2,
            "reason": "L_(r,r) maps into F_r and swaps the two off-diagonal columns inside F_r",
        })
        dimension_rows.append({
            "endomorphism": f"e_{r}",
            "type": "constant",
            "constraint_rank_mod_1000003": constraint_rank,
            "dimension_upper_bound": dim_upper,
            "formula_lower_bound": indep_rank,
            "dimension": 2,
            "formula_checks": f"basis intertwiners {ok0} {ok1}; independent rank {indep_rank}",
        })
        check_rows.append({
            "check": f"Hom_e{r}_basis_1_intertwines",
            "result": ok0,
            "detail": f"T=e_({r},{r}) eps^T",
        })
        check_rows.append({
            "check": f"Hom_e{r}_basis_2_intertwines",
            "result": ok1,
            "detail": f"T=(offsum in row {r}) eps^T",
        })
        check_rows.append({
            "check": f"Hom_e{r}_constraint_dimension",
            "result": dim_upper == 2 and indep_rank == 2,
            "detail": f"rank={constraint_rank}, dim_upper={dim_upper}, formula_rank={indep_rank}",
        })
        all_constant_ok = all_constant_ok and ok0 and ok1 and (dim_upper == 2) and (indep_rank == 2)

    # Automorphism audit.
    perm_rows: List[Dict[str, object]] = []
    all_auto_ok = True
    for perm in permutations(S):
        phi = automorphism_phi(perm)
        P = permutation_matrix(perm)
        C = hom_constraint_matrix(phi)
        constraint_rank = rank_mod(C)
        dim_upper = N * N - constraint_rank
        p_ok = check_intertwiner(P, phi)
        perm_rows.append({
            "endomorphism": "phi_" + "".join(map(str, perm)),
            "type": "automorphism",
            "permutation": "".join(map(str, perm)),
            "constraint_rank_mod_1000003": constraint_rank,
            "dimension_upper_bound": dim_upper,
            "generator": "P_rho",
            "generator_intertwines": p_ok,
            "dimension": 1,
        })
        dimension_rows.append({
            "endomorphism": "phi_" + "".join(map(str, perm)),
            "type": "automorphism",
            "constraint_rank_mod_1000003": constraint_rank,
            "dimension_upper_bound": dim_upper,
            "formula_lower_bound": 1 if p_ok else 0,
            "dimension": 1,
            "formula_checks": f"P_rho intertwines {p_ok}",
        })
        check_rows.append({
            "check": "Hom_phi_" + "".join(map(str, perm)) + "_dimension",
            "result": dim_upper == 1 and p_ok,
            "detail": f"rank={constraint_rank}, dim_upper={dim_upper}, P_rho={p_ok}",
        })
        all_auto_ok = all_auto_ok and p_ok and (dim_upper == 1)

    # Collapse tree proof audit: T kills ker epsilon.
    tree_rows = find_collapse_tree()
    # Verify the 8 tree differences are rank 8 and augmentation-zero.
    diff_matrix: List[List[int]] = []
    for row in tree_rows:
        new = tuple(map(int, row["new_vertex"].strip("()").split(",")))
        prev = tuple(map(int, row["previous_vertex"].strip("()").split(",")))
        v = [0] * N
        v[IDX[new]] = 1
        v[IDX[prev]] = -1
        diff_matrix.append(v)
    tree_rank = matrix_rank_int(diff_matrix)
    tree_aug_zero = all(sum(v) == 0 for v in diff_matrix)
    check_rows.append({
        "check": "collapse_tree_generates_kernel_epsilon",
        "result": tree_rank == 8 and tree_aug_zero and len(tree_rows) == 8,
        "detail": f"tree_edges={len(tree_rows)}, rank={tree_rank}, augmentation_zero={tree_aug_zero}",
    })

    # End/Hom total summary.
    total_dim = 6 * 1 + 3 * 2
    summary_rows = [{
        "quantity": "sum_dim_Hom_phi_over_End",
        "value": total_dim,
        "formula": "6*1 + 3*2",
        "status": "checked",
    }, {
        "quantity": "constant_Hom_closed_form",
        "value": "Hom_e_r = Fix(L_(r,r)) tensor epsilon",
        "formula": "{u eps^T : u in span(e_(r,r), sum_{c!=r} e_(r,c))}",
        "status": "checked",
    }, {
        "quantity": "orientation_guardrail",
        "value": "target freedom, source augmentation",
        "formula": "not source row-fiber functionals",
        "status": "checked",
    }]

    status_rows = [{
        "front": "L3-C",
        "claim": "Closed form for Hom_{e_r}",
        "status": "closed",
        "support": "rank audit + explicit formula basis + collapse-tree proof lemma",
    }, {
        "front": "L3-C",
        "claim": "dim Hom_{e_r}=2 for r=0,1,2",
        "status": "closed",
        "support": "constraint rank 79 over F_1000003 and 2 formula basis elements",
    }, {
        "front": "L3-C",
        "claim": "Hom_{phi_rho}=R P_rho for automorphisms",
        "status": "retained/checked",
        "support": "constraint rank 80 and permutation generator",
    }, {
        "front": "L3-C",
        "claim": "sum dim Hom_phi = 12",
        "status": "closed",
        "support": "6 automorphisms of dimension 1 plus 3 constants of dimension 2",
    }]

    write_csv(os.path.join(tables, "layer3_frontC_hom_constant_formula.csv"), formula_rows,
              ["constant_endomorphism", "formula", "epsilon", "basis_1_u", "basis_2_u", "closed_form", "dimension"])
    write_csv(os.path.join(tables, "layer3_frontC_fixed_space_basis.csv"), fixed_rows,
              ["r", "idempotent", "fixed_space", "basis_1", "basis_2", "dimension", "reason"])
    write_csv(os.path.join(tables, "layer3_frontC_intertwiner_dimension_audit.csv"), dimension_rows,
              ["endomorphism", "type", "constraint_rank_mod_1000003", "dimension_upper_bound", "formula_lower_bound", "dimension", "formula_checks"])
    write_csv(os.path.join(tables, "layer3_frontC_automorphism_hom_audit.csv"), perm_rows,
              ["endomorphism", "type", "permutation", "constraint_rank_mod_1000003", "dimension_upper_bound", "generator", "generator_intertwines", "dimension"])
    write_csv(os.path.join(tables, "layer3_frontC_collapse_tree.csv"), tree_rows,
              ["new_vertex", "previous_vertex", "source_y", "left_for_previous", "left_for_new", "difference"])
    write_csv(os.path.join(tables, "layer3_frontC_summary.csv"), summary_rows,
              ["quantity", "value", "formula", "status"])
    write_csv(os.path.join(tables, "layer3_frontC_verifier_checks.csv"), check_rows,
              ["check", "result", "detail"])
    write_csv(os.path.join(tables, "layer3_frontC_status_registry.csv"), status_rows,
              ["front", "claim", "status", "support"])

    all_checks_ok = all(str(row["result"]) == "True" for row in check_rows)
    if not (all_constant_ok and all_auto_ok and all_checks_ok):
        raise SystemExit("Layer 3 Front C verifier: FAIL")

    print("Layer 3 Front C verifier: PASS")
    print("  constant intertwiners: Hom_e_r = {u eps^T : u in Fix(L_(r,r))}, dim 2")
    print("  fixed space: span{e_(r,r), sum_{c!=r} e_(r,c)} for each r")
    print("  collapse lemma: differences of left translations generate ker(eps), so every Hom_e_r factors through eps")
    print("  automorphism intertwiners: Hom_phi_rho = R P_rho, dim 1")
    print("  total Hom dimension: 6*1 + 3*2 = 12")


if __name__ == "__main__":
    main()
