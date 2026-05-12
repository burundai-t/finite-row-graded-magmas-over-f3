#!/usr/bin/env python3
# verify_layer3_frontA.py
#
# Front L3-A verifier: structural spectral/Jordan proof audit for PAB left operators.
# It does not replace the proof; it checks the finite normal forms that the proof uses.

from __future__ import annotations

import csv
from pathlib import Path
from itertools import product
from typing import Dict, List, Tuple

import sympy as sp

S = (0, 1, 2)
M = tuple((r, c) for r in S for c in S)
IDX = {x: i for i, x in enumerate(M)}
N = len(M)
t = sp.Symbol("t")


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


def L_matrix(x: Tuple[int, int]) -> sp.Matrix:
    A = sp.zeros(N, N)
    for y in M:
        A[IDX[pab(x, y)], IDX[y]] = 1
    return A


def fiber_indices(r: int) -> List[int]:
    return [IDX[(r, c)] for c in S]


def fiber_block_B(x: Tuple[int, int]) -> sp.Matrix:
    r, _ = x
    L = L_matrix(x)
    inds = fiber_indices(r)
    return L.extract(inds, inds)


def fiber_block_map(x: Tuple[int, int]) -> Dict[int, int]:
    r, c = x
    return {d: pab(x, (r, d))[1] for d in S}


def charpoly_expr(A: sp.Matrix) -> sp.Expr:
    return sp.factor(A.charpoly(t).as_expr())


def nullity(A: sp.Matrix) -> int:
    return A.cols - A.rank()


def matrix_is_zero(A: sp.Matrix) -> bool:
    return all(v == 0 for v in A)


def vector_name(v: Tuple[int, int]) -> str:
    return f"e{v}"


def image_of_basis_under_matrix(A: sp.Matrix, y: Tuple[int, int]) -> Tuple[int, int] | str:
    col = A[:, IDX[y]]
    ones = [i for i, val in enumerate(col) if val == 1]
    if len(ones) == 1 and sum(int(val) for val in col) == 1:
        return M[ones[0]]
    return str(list(col))


def build_rows() -> Tuple[List[Dict[str, str]], List[Dict[str, str]], List[Dict[str, str]]]:
    I9 = sp.eye(N)
    Z9 = sp.zeros(N, N)
    fiber_rows: List[Dict[str, str]] = []
    operator_rows: List[Dict[str, str]] = []
    witness_rows: List[Dict[str, str]] = []

    for x in M:
        r, c = x
        typ = "diagonal" if r == c else "off_diagonal"
        u = "" if typ == "diagonal" else str(comp(r, c))
        B = fiber_block_B(x)
        Bmap = fiber_block_map(x)
        B2 = B**2
        B3 = B**3
        L = L_matrix(x)
        L2 = L**2
        L3 = L**3
        L4 = L**4

        if typ == "diagonal":
            expected_B_char = sp.factor((t - 1) ** 2 * (t + 1))
            expected_L_char = sp.factor(t**6 * (t - 1) ** 2 * (t + 1))
            expected_minpoly = "t*(t - 1)*(t + 1)"
            B_identity = "B^2=I"
            L_annihilator = "L^3=L"
            L3_eq_L_expected = True
            L4_eq_L2_expected = True
            alg0 = 6
            zero_jordan = "six J1(0); no J2(0)"
        else:
            expected_B_char = sp.factor(t * (t - 1) * (t + 1))
            expected_L_char = sp.factor(t**7 * (t - 1) * (t + 1))
            expected_minpoly = "t^2*(t - 1)*(t + 1)"
            B_identity = "B^3=B"
            L_annihilator = "L^4=L^2, L^3!=L"
            L3_eq_L_expected = False
            L4_eq_L2_expected = True
            alg0 = 7
            zero_jordan = "one J2(0) plus five J1(0)"

        B_char = charpoly_expr(B)
        L_char = charpoly_expr(L)
        assert sp.factor(B_char - expected_B_char) == 0, (x, B_char, expected_B_char)
        assert sp.factor(L_char - expected_L_char) == 0, (x, L_char, expected_L_char)
        assert L.rank() == 3, x
        assert nullity(L) == 6, x
        assert matrix_is_zero(L4 - L2), x
        assert matrix_is_zero(L3 - L) == L3_eq_L_expected, x
        assert matrix_is_zero(L4 - L2) == L4_eq_L2_expected, x

        if typ == "diagonal":
            assert matrix_is_zero(B2 - sp.eye(3)), x
            assert L2.rank() == 3, x
            assert nullity(L2) == 6, x
            # Since L has eigenvalues 0, 1, -1 and the annihilator is square-free,
            # the exact minimal polynomial is t(t-1)(t+1).
        else:
            assert matrix_is_zero(B3 - B), x
            assert not matrix_is_zero(B2 - sp.eye(3)), x
            assert B.rank() == 2, x
            assert L2.rank() == 2, x
            assert nullity(L2) == 7, x
            # t(t^2-1) does not annihilate L, but t^2(t^2-1) does.
            assert not matrix_is_zero(L3 - L), x
            # Witness y in the source fiber F_c.
            y = (c, 0)
            Ly = image_of_basis_under_matrix(L, y)
            L3y = image_of_basis_under_matrix(L3, y)
            assert Ly == (r, c), (x, y, Ly)
            assert L3y == (r, comp(r, c)), (x, y, L3y)
            witness_rows.append({
                "x": str(x),
                "source_witness_y_in_F_c": str(y),
                "L_x_y": str(Ly),
                "L_x_cubed_y": str(L3y),
                "conclusion": "L^3 != L; the t factor at 0 must be squared",
            })

        fiber_rows.append({
            "x": str(x),
            "type": typ,
            "row_r": str(r),
            "column_c": str(c),
            "third_u_if_offdiag": u,
            "B_column_map_d_to_output_column": ";".join(f"{d}->{Bmap[d]}" for d in S),
            "rank_B": str(B.rank()),
            "charpoly_B": str(B_char),
            "fiber_identity": B_identity,
            "eigenvectors_summary": (
                "diag: e_r fixed, other two swapped" if typ == "diagonal"
                else "offdiag: e_r+e_u (+1), e_r-e_u (-1), e_c-e_u (0)"
            ),
        })

        operator_rows.append({
            "x": str(x),
            "type": typ,
            "rank_L": str(L.rank()),
            "rank_L2": str(L2.rank()),
            "nullity_L": str(nullity(L)),
            "nullity_L2": str(nullity(L2)),
            "charpoly_L": str(L_char),
            "minimal_polynomial": expected_minpoly,
            "operator_identity": L_annihilator,
            "alg_mult_zero": str(alg0),
            "geom_mult_zero": "6",
            "zero_jordan_structure": zero_jordan,
        })

    return fiber_rows, operator_rows, witness_rows


def write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    tables = root / "tables"
    fiber_rows, operator_rows, witness_rows = build_rows()
    write_csv(tables / "layer3_frontA_fiber_block_normal_forms.csv", fiber_rows)
    write_csv(tables / "layer3_frontA_operator_spectral_proof_audit.csv", operator_rows)
    write_csv(tables / "layer3_frontA_offdiag_nonsemisimple_witnesses.csv", witness_rows)

    check_rows = [
        {"check": "all L_x have rank 3", "status": "PASS"},
        {"check": "diagonal B blocks satisfy B^2=I", "status": "PASS"},
        {"check": "off-diagonal B blocks satisfy B^3=B and rank 2", "status": "PASS"},
        {"check": "diagonal L_x satisfy L^3=L with minpoly t(t-1)(t+1)", "status": "PASS"},
        {"check": "off-diagonal L_x satisfy L^4=L^2 but L^3!=L", "status": "PASS"},
        {"check": "off-diagonal zero eigenspace has alg mult 7, geom mult 6", "status": "PASS"},
        {"check": "off-diagonal Jordan zero structure is one J2(0) plus five J1(0)", "status": "PASS"},
    ]
    write_csv(tables / "layer3_frontA_verifier_checks.csv", check_rows)

    print("Layer 3 Front A verifier: PASS")
    print("  fiber normal forms: diagonal B^2=I; off-diagonal B^3=B and rank(B)=2")
    print("  operator identities: diagonal L^3=L; off-diagonal L^4=L^2 and L^3!=L")
    print("  spectral split: diagonal minpoly t(t-1)(t+1); off-diagonal t^2(t-1)(t+1)")
    print("  Jordan split: off-diagonal has exactly one J2(0) block")


if __name__ == "__main__":
    main()
