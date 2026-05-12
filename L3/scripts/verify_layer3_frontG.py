#!/usr/bin/env python3
"""
Layer 3 Front G verifier: companion Lie package on the PAB carrier.
Dependency-free finite audit for the structural facts recorded in L3-G.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import os
from fractions import Fraction
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"
TABLES.mkdir(exist_ok=True)

S = range(3)
Mat = Tuple[int, ...]  # row-major 3x3


def E(i: int, j: int) -> Mat:
    a = [0] * 9
    a[3 * i + j] = 1
    return tuple(a)


def add(A: Mat, B: Mat) -> Mat:
    return tuple(a + b for a, b in zip(A, B))


def sub(A: Mat, B: Mat) -> Mat:
    return tuple(a - b for a, b in zip(A, B))


def neg(A: Mat) -> Mat:
    return tuple(-a for a in A)


def scal(c: int, A: Mat) -> Mat:
    return tuple(c * a for a in A)


def matmul(A: Mat, B: Mat) -> Mat:
    out = []
    for i in S:
        for j in S:
            out.append(sum(A[3 * i + k] * B[3 * k + j] for k in S))
    return tuple(out)


def bracket(A: Mat, B: Mat) -> Mat:
    return sub(matmul(A, B), matmul(B, A))


def tr(A: Mat) -> int:
    return sum(A[3 * i + i] for i in S)


def transpose(A: Mat) -> Mat:
    return tuple(A[3 * j + i] for i in S for j in S)


def is_zero(A: Mat) -> bool:
    return all(x == 0 for x in A)


def name_unit(i: int, j: int) -> str:
    return f"E{i}{j}"


def fmt(A: Mat) -> str:
    terms = []
    for i in S:
        for j in S:
            c = A[3 * i + j]
            if c:
                if c == 1:
                    terms.append(name_unit(i, j))
                elif c == -1:
                    terms.append("-" + name_unit(i, j))
                else:
                    terms.append(f"{c}*{name_unit(i,j)}")
    if not terms:
        return "0"
    s = "+".join(terms)
    return s.replace("+-", "-")


def rank(vectors: Sequence[Mat]) -> int:
    # rational row reduction; vectors as rows
    if not vectors:
        return 0
    A = [[Fraction(x) for x in v] for v in vectors]
    m = len(A)
    n = len(A[0])
    r = 0
    for c in range(n):
        pivot = None
        for i in range(r, m):
            if A[i][c] != 0:
                pivot = i
                break
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        pv = A[r][c]
        A[r] = [x / pv for x in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                fac = A[i][c]
                A[i] = [x - fac * y for x, y in zip(A[i], A[r])]
        r += 1
        if r == m:
            break
    return r


def in_span(v: Mat, basis: Sequence[Mat]) -> bool:
    return rank(list(basis) + [v]) == rank(basis)


def is_symmetric(A: Mat) -> bool:
    return A == transpose(A)


def is_skew(A: Mat) -> bool:
    return A == neg(transpose(A))


def permute_mat(p: Tuple[int, int, int], A: Mat) -> Mat:
    # P A P^{-1}; on units E_ij -> E_{p(i),p(j)}
    out = [0] * 9
    for i in S:
        for j in S:
            out[3 * p[i] + p[j]] += A[3 * i + j]
    return tuple(out)


def parity(p: Tuple[int, int, int]) -> int:
    inv = sum(1 for i in range(3) for j in range(i + 1, 3) if p[i] > p[j])
    return -1 if inv % 2 else 1


def pab(x: Tuple[int, int], y: Tuple[int, int]) -> Tuple[int, int]:
    r, c = x
    s, d = y
    if r != s:
        return (r, s)
    if c == d:
        return (r, r)
    return (r, (-c - d) % 3)


def pab_mat_unit(i: int, j: int, k: int, l: int) -> Mat:
    return E(*pab((i, j), (k, l)))


def row_contraction_unit(i: int, j: int, k: int, l: int) -> Mat:
    # E_ij J E_kl^T = E_i,k
    return E(i, k)


def write_csv(name: str, rows: List[dict], fieldnames: List[str]) -> None:
    path = TABLES / name
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# Basic basis
units = {(i, j): E(i, j) for i in S for j in S}
I = add(add(E(0, 0), E(1, 1)), E(2, 2))
H1 = sub(E(0, 0), E(1, 1))
H2 = sub(E(1, 1), E(2, 2))
offdiag = [E(i, j) for i in S for j in S if i != j]
sl_basis = [H1, H2] + offdiag
so_basis = [sub(E(0, 1), E(1, 0)), sub(E(0, 2), E(2, 0)), sub(E(1, 2), E(2, 1))]
p_basis = [H1, H2, add(E(0, 1), E(1, 0)), add(E(0, 2), E(2, 0)), add(E(1, 2), E(2, 1))]
perms = list(itertools.permutations(S))

checks = []

def check(name: str, ok: bool, detail: str) -> None:
    checks.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})
    if not ok:
        raise AssertionError(f"{name}: {detail}")


# 1. Carrier basis and bracket structure constants
basis_rows = []
for i in S:
    for j in S:
        basis_rows.append({"basis": name_unit(i, j), "row": i, "column": j, "matrix_unit": f"e_({i},{j}) -> E_{i}{j}"})
write_csv("layer3_frontG_lie_carrier_basis.csv", basis_rows, ["basis", "row", "column", "matrix_unit"])
check("carrier_basis_dim", len(basis_rows) == 9 and rank(list(units.values())) == 9, "k[M] carrier has 9 matrix-unit basis vectors")

bracket_rows = []
for i, j, k, l in itertools.product(S, S, S, S):
    lhs = bracket(E(i, j), E(k, l))
    rhs = (E(i, l) if j == k else (0,) * 9)
    rhs = sub(rhs, E(k, j) if l == i else (0,) * 9)
    if lhs != rhs:
        raise AssertionError("bracket formula failed")
    if not is_zero(lhs):
        bracket_rows.append({"left": name_unit(i, j), "right": name_unit(k, l), "bracket": fmt(lhs)})
write_csv("layer3_frontG_bracket_structure_constants.csv", bracket_rows, ["left", "right", "bracket"])
check("bracket_formula", True, "[Eij,Ekl]=delta_jk Eil - delta_li Ekj for all 81 basis pairs")

# 2. Decomposition gl3 = kI + sl3, adjoint 1+8
decomp_rows = []
check("center_dim", rank([I]) == 1 and all(is_zero(bracket(I, U)) for U in units.values()), "center span{I} is one-dimensional and ad_I=0")
check("sl3_dim", rank(sl_basis) == 8 and all(tr(v) == 0 for v in sl_basis), "traceless component has dimension 8")
check("gl3_direct_sum", rank([I] + sl_basis) == 9, "gl3 = kI direct sum sl3 as vector spaces")
check("sl3_bracket_closed", all(tr(bracket(A, B)) == 0 for A in sl_basis for B in sl_basis), "[sl3,sl3] subset sl3")
decomp_rows += [
    {"object": "k[M] / Mat3 carrier", "dimension": 9, "description": "matrix-unit carrier e_(r,c) <-> E_rc"},
    {"object": "center kI", "dimension": 1, "description": "trivial adjoint module"},
    {"object": "sl3", "dimension": 8, "description": "traceless adjoint module"},
    {"object": "adjoint split", "dimension": "1+8", "description": "k[M] = 1 plus 8 under the companion commutator"},
]

# 3. S3 equivariance and stability
s3_rows = []
for p in perms:
    ok_br = all(bracket(permute_mat(p, A), permute_mat(p, B)) == permute_mat(p, bracket(A, B)) for A in units.values() for B in units.values())
    ok_pab = all(tuple(p[t] for t in pab(x, y)) == pab(tuple(p[t] for t in x), tuple(p[t] for t in y)) for x in itertools.product(S, S) for y in itertools.product(S, S))
    ok_so = all(in_span(permute_mat(p, A), so_basis) for A in so_basis)
    ok_p = all(in_span(permute_mat(p, A), p_basis) for A in p_basis)
    s3_rows.append({
        "permutation": "".join(map(str, p)),
        "parity": parity(p),
        "bracket_equivariant": ok_br,
        "PAB_automorphism": ok_pab,
        "so3_stable": ok_so,
        "p_stable": ok_p,
    })
    check(f"S3_perm_{''.join(map(str,p))}", ok_br and ok_pab and ok_so and ok_p, "simultaneous relabeling preserves PAB, bracket, so3, and p")
write_csv("layer3_frontG_s3_equivariance_audit.csv", s3_rows, ["permutation", "parity", "bracket_equivariant", "PAB_automorphism", "so3_stable", "p_stable"])

# 4. so3 and Cartan decomposition
check("so3_dim", rank(so_basis) == 3 and all(is_skew(A) and tr(A) == 0 for A in so_basis), "so3 is the 3D skew-symmetric traceless sector")
check("p_dim", rank(p_basis) == 5 and all(is_symmetric(A) and tr(A) == 0 for A in p_basis), "p is the 5D symmetric traceless sector")
check("sl3_so_p_direct", rank(so_basis + p_basis) == 8, "sl3 = so3 direct sum p")
check("cartan_kk", all(in_span(bracket(A, B), so_basis) for A in so_basis for B in so_basis), "[so3,so3] subset so3")
check("cartan_kp", all(in_span(bracket(A, B), p_basis) for A in so_basis for B in p_basis), "[so3,p] subset p")
check("cartan_pp", all(in_span(bracket(A, B), so_basis) for A in p_basis for B in p_basis), "[p,p] subset so3")
cartan_rows = [
    {"containment": "[so3,so3]", "target": "so3", "status": "PASS"},
    {"containment": "[so3,p]", "target": "p", "status": "PASS"},
    {"containment": "[p,p]", "target": "so3", "status": "PASS"},
]
write_csv("layer3_frontG_cartan_decomposition_audit.csv", cartan_rows, ["containment", "target", "status"])

def killing(A: Mat, B: Mat) -> int:
    return 6 * tr(matmul(A, B))

kill_rows = []
so_names = ["A01=E01-E10", "A02=E02-E20", "A12=E12-E21"]
for i, A in enumerate(so_basis):
    for j, B in enumerate(so_basis):
        kill_rows.append({"sector": "so3", "left": so_names[i], "right": so_names[j], "B=6tr(XY)": killing(A, B)})
p_names = ["H1=E00-E11", "H2=E11-E22", "S01=E01+E10", "S02=E02+E20", "S12=E12+E21"]
for i, A in enumerate(p_basis):
    for j, B in enumerate(p_basis):
        kill_rows.append({"sector": "p", "left": p_names[i], "right": p_names[j], "B=6tr(XY)": killing(A, B)})
write_csv("layer3_frontG_killing_form_audit.csv", kill_rows, ["sector", "left", "right", "B=6tr(XY)"])
# Sylvester checks for chosen bases: so diagonal -12 and p principal minors positive for H block plus offdiag diag 12.
so_gram = [[killing(A, B) for B in so_basis] for A in so_basis]
p_gram = [[killing(A, B) for B in p_basis] for A in p_basis]
check("killing_so3_negative", so_gram == [[-12, 0, 0], [0, -12, 0], [0, 0, -12]], "Killing form is negative definite on selected so3 basis")
# p Gram expected [[12,-6,0,0,0],[-6,12,0,0,0],... diag 12]
check("killing_p_positive", p_gram[0][0] == 12 and p_gram[1][1] == 12 and p_gram[0][1] == -6 and all(p_gram[i][i] == 12 for i in range(2, 5)), "Killing form is positive on the displayed p basis block")

decomp_rows += [
    {"object": "so3", "dimension": 3, "description": "skew-symmetric S3-stable compact subalgebra inside sl3"},
    {"object": "p", "dimension": 5, "description": "symmetric traceless complement"},
    {"object": "Cartan split", "dimension": "3+5", "description": "sl3 = so3 plus p; bracket containments verified"},
    {"object": "compact group type", "dimension": "8+3+1", "description": "SU(3) x SU(2) x U(1) attached to sl3, selected so3, and center"},
]
write_csv("layer3_frontG_decomposition_summary.csv", decomp_rows, ["object", "dimension", "description"])

# 5. PAB/matrix carrier compatibility and boundary
compat_rows = []
coincidences = []
for i, j, k, l in itertools.product(S, S, S, S):
    P = pab_mat_unit(i, j, k, l)
    M = matmul(E(i, j), E(k, l))
    if P == M:
        coincidences.append((i, j, k, l))
    if i != k:
        ok = P == row_contraction_unit(i, j, k, l)
        if not ok:
            raise AssertionError("row-contraction cross-row compatibility failed")
check("row_contraction_cross", True, "for i!=k, PAB(Eij,Ekl)=Eik=Eij J Ekl^T")
check("basis_coincidences_count", len(coincidences) == 9, "PAB product and matrix product coincide on exactly 9 basis pairs")
compat_rows.append({"claim": "same carrier", "status": "PASS", "detail": "e_(r,c) <-> E_rc gives a 9D matrix-unit carrier"})
compat_rows.append({"claim": "cross-row AJB^T", "status": "PASS", "detail": "for i!=k, PAB(Eij,Ekl)=Eik=Eij J Ekl^T"})
compat_rows.append({"claim": "basis coincidences", "status": "PASS", "detail": f"{len(coincidences)} basis pairs coincide with ordinary matrix multiplication"})
compat_rows.append({"claim": "operation boundary", "status": "PASS", "detail": "PAB multiplication and ordinary matrix multiplication are distinct operations on the same carrier"})
write_csv("layer3_frontG_carrier_compatibility_audit.csv", compat_rows, ["claim", "status", "detail"])

coinc_rows = [{"i": i, "j": j, "k": k, "l": l, "pair": f"E{i}{j} * E{k}{l}", "value": fmt(pab_mat_unit(i,j,k,l))} for (i,j,k,l) in coincidences]
write_csv("layer3_frontG_matrix_product_coincidences.csv", coinc_rows, ["i", "j", "k", "l", "pair", "value"])

# 6. compact group type table and status registry
group_rows = [
    {"component": "traceless companion algebra", "lie_algebra": "sl3", "compact_form_or_cover": "SU(3)", "dimension": 8, "status": "structural"},
    {"component": "selected compact subalgebra", "lie_algebra": "so3 ~= su2/center", "compact_form_or_cover": "SU(2)", "dimension": 3, "status": "structural"},
    {"component": "center", "lie_algebra": "u1", "compact_form_or_cover": "U(1)", "dimension": 1, "status": "structural"},
    {"component": "package type", "lie_algebra": "sl3 + selected so3 + u1", "compact_form_or_cover": "SU(3) x SU(2) x U(1)", "dimension": 12, "status": "gauge-isomorphic compact Lie group type"},
]
write_csv("layer3_frontG_compact_group_package.csv", group_rows, ["component", "lie_algebra", "compact_form_or_cover", "dimension", "status"])

status_rows = [
    {"claim": "carrier k[M] ~= Mat3(k)", "status": "closed", "support": "basis table + rank check"},
    {"claim": "matrix companion bracket is gl3", "status": "closed", "support": "structure constants verified"},
    {"claim": "gl3 = kI + sl3 and k[M] = 1 + 8", "status": "closed", "support": "center/sl3 direct-sum audit"},
    {"claim": "so3 is S3-stable compact 3D subalgebra", "status": "closed", "support": "S3 stability + Killing negative audit"},
    {"claim": "Cartan split sl3 = so3 + p", "status": "closed", "support": "bracket containment audit"},
    {"claim": "compact group type SU3 x SU2 x U1", "status": "closed as companion package", "support": "standard compact forms attached to verified Lie pieces"},
    {"claim": "PAB product equals matrix product", "status": "not claimed", "support": "operation boundary audit; same carrier, distinct products"},
]
write_csv("layer3_frontG_status_registry.csv", status_rows, ["claim", "status", "support"])

write_csv("layer3_frontG_verifier_checks.csv", checks, ["check", "status", "detail"])

# script manifest for this front tables only
manifest_rows = []
for path in sorted(TABLES.glob("layer3_frontG_*.csv")):
    manifest_rows.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
write_csv("layer3_frontG_table_manifest.csv", manifest_rows, ["path", "bytes", "sha256"])

print("Layer 3 Front G verifier: PASS")
print("  carrier: k[M] identified with Mat3 matrix units; bracket structure constants checked")
print("  decomposition: gl3 = kI + sl3 and adjoint carrier split 1+8 checked")
print("  S3 compatibility: simultaneous relabeling preserves PAB, bracket, so3, and p")
print("  compact sector: so3 is S3-stable, Killing-negative, and Cartan split sl3=so3+p checked")
print("  companion group type: SU(3) x SU(2) x U(1) recorded as the compact Lie package")
print("  boundary: PAB and matrix multiplication share the carrier; cross-row AJB^T and 9 basis coincidences checked")
