#!/usr/bin/env python3
from pathlib import Path
from fractions import Fraction
import csv
import os

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"

ORDER = ["B1", "B2", "B3", "I", "B5"]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def rows(name):
    with open(TABLES / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def f(x):
    return Fraction(x)


def mat(rows_):
    return tuple(tuple(Fraction(x) for x in row) for row in rows_)


def parse_matrix(text):
    return tuple(tuple(Fraction(x) for x in row.split()) for row in text.split(";"))


def zero():
    return mat([[0, 0, 0], [0, 0, 0], [0, 0, 0]])


def add(A, B):
    return tuple(tuple(A[i][j] + B[i][j] for j in range(3)) for i in range(3))


def sub(A, B):
    return tuple(tuple(A[i][j] - B[i][j] for j in range(3)) for i in range(3))


def scale(c, A):
    return tuple(tuple(Fraction(c) * A[i][j] for j in range(3)) for i in range(3))


def mul(A, B):
    return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def flat(A):
    return tuple(A[i][j] for i in range(3) for j in range(3))


def rank(vectors):
    A = [list(map(Fraction, v)) for v in vectors if any(v)]
    if not A:
        return 0
    m, n = len(A), len(A[0])
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
                factor = A[i][c]
                A[i] = [A[i][j] - factor * A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def solve(columns, vector):
    n = len(vector)
    m = len(columns)
    M = [[Fraction(columns[j][i]) for j in range(m)] + [Fraction(vector[i])] for i in range(n)]
    r = 0
    pivots = []
    for c in range(m):
        pivot = None
        for i in range(r, n):
            if M[i][c] != 0:
                pivot = i
                break
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(n):
            if i != r and M[i][c] != 0:
                factor = M[i][c]
                M[i] = [M[i][j] - factor * M[r][j] for j in range(m + 1)]
        pivots.append(c)
        r += 1
    for i in range(n):
        if all(M[i][c] == 0 for c in range(m)) and M[i][m] != 0:
            return None
    sol = [Fraction(0) for _ in range(m)]
    for row, c in enumerate(pivots):
        sol[c] = M[row][m]
    return tuple(sol)


def in_span(columns, A):
    return solve(columns, flat(A)) is not None


def rc(i):
    return divmod(i, 3)


def idx(r, c):
    return 3 * r + c


def complement(a, b):
    return 3 - a - b


def pab_mul(x, y):
    r1, c1 = rc(x)
    r2, c2 = rc(y)
    if r1 != r2:
        return idx(r1, r2)
    if c1 != c2:
        return idx(r1, complement(c1, c2))
    return idx(r1, r1)


def L_fiber(x, r=0):
    fiber = [idx(r, c) for c in range(3)]
    out = [[Fraction(0) for _ in range(3)] for _ in range(3)]
    for j_local, j_global in enumerate(fiber):
        img = pab_mul(x, j_global)
        if rc(img)[0] == r:
            i_local = fiber.index(img)
            out[i_local][j_local] = Fraction(1)
    return mat(out)


def expr(coeffs):
    parts = []
    for c, name in zip(coeffs, ORDER):
        if c == 0:
            continue
        if c == 1:
            parts.append(name)
        elif c == -1:
            parts.append("-" + name)
        else:
            parts.append(f"{c}*{name}")
    return "+".join(parts).replace("+-", "-") if parts else "0"


def closure_dimension(generators):
    basis = []
    basis_vecs = []
    for G in generators:
        if rank(basis_vecs + [flat(G)]) > rank(basis_vecs):
            basis.append(G)
            basis_vecs.append(flat(G))
    changed = True
    while changed:
        changed = False
        current = list(basis)
        for A in current:
            for B in current:
                P = mul(A, B)
                if rank(basis_vecs + [flat(P)]) > rank(basis_vecs):
                    basis.append(P)
                    basis_vecs.append(flat(P))
                    changed = True
    return rank(basis_vecs), basis


def check_structure_table(basis):
    structure = {(r["object"], r["property"]): r for r in rows("l3_fiber_algebra_5dim_structure.csv")}
    require(structure[("A5", "dimension")]["value"] == "5", "A5 dimension row mismatch")
    require(structure[("basis", "basis_order")]["value"] == "B1|B2|B3|I|B5", "basis order row mismatch")
    for name, B in basis.items():
        if (name, "matrix") in structure:
            require(parse_matrix(structure[(name, "matrix")]["value"]) == B, f"matrix row mismatch for {name}")
    require(structure[("center", "basis")]["value"] == "I", "center basis row mismatch")
    require(structure[("center", "dimension")]["value"] == "1", "center dimension row mismatch")
    require(structure[("Q", "square")]["value"] == "0", "Q square row mismatch")
    require(structure[("R", "square")]["value"] == "0", "R square row mismatch")
    require(structure[("radical", "dimension")]["value"] == "2", "radical dimension row mismatch")
    require(structure[("radical", "two_sided_ideal")]["value"] == "True", "radical ideal row mismatch")
    require(structure[("radical", "square_zero")]["value"] == "True", "radical square row mismatch")
    require(structure[("quotient", "dimension")]["value"] == "3", "quotient dimension row mismatch")
    require(structure[("quotient", "isomorphism_type")]["value"] == "k^3", "quotient type row mismatch")
    require(structure[("operator_boundary", "counterexamples_on_F0")]["value"] == "20/27", "F0 boundary row mismatch")
    require(structure[("operator_boundary", "counterexamples_all_fibers")]["value"] == "60/81", "all-fiber boundary row mismatch")


def main():
    B1 = L_fiber(0, 0)
    B2 = L_fiber(1, 0)
    B3 = L_fiber(2, 0)
    I = mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    B5 = mul(B2, B2)
    basis = {"B1": B1, "B2": B2, "B3": B3, "I": I, "B5": B5}
    basis_list = [basis[name] for name in ORDER]
    basis_cols = [flat(B) for B in basis_list]

    require(rank(basis_cols) == 5, "the displayed basis should be linearly independent of dimension 5")
    dim, closure_basis = closure_dimension([B1, B2, B3])
    require(dim == 5, "closure of same-fiber left translations should have dimension 5")
    require(all(in_span(basis_cols, A) for A in closure_basis), "closure should be contained in displayed span")

    check_structure_table(basis)

    table_rows = rows("l3_fiber_algebra_5dim_multiplication.csv")
    require(len(table_rows) == 25, "5D multiplication table should have 25 products")
    displayed = {(r["lhs"], r["rhs"]): r["product"] for r in table_rows}
    require(set(displayed) == {(a, b) for a in ORDER for b in ORDER}, "multiplication table index mismatch")
    for a in ORDER:
        for b in ORDER:
            coeffs = solve(basis_cols, flat(mul(basis[a], basis[b])))
            require(coeffs is not None, f"product {a}*{b} not in basis span")
            require(expr(coeffs) == displayed[(a, b)], f"product mismatch for {a}*{b}: {expr(coeffs)} != {displayed[(a,b)]}")

    Q = sub(B2, B3)
    R = add(add(B1, I), scale(-2, B5))
    require(Q == parse_matrix("0 0 0;-1 0 0;1 0 0"), "Q matrix mismatch")
    require(R == parse_matrix("0 0 0;0 1 1;0 -1 -1"), "R matrix mismatch")
    require(mul(Q, Q) == zero(), "Q^2 should be zero")
    require(mul(Q, R) == zero() and mul(R, Q) == zero() and mul(R, R) == zero(), "span{Q,R} should be square-zero")
    radical_cols = [flat(Q), flat(R)]
    require(rank(radical_cols) == 2, "radical candidate should have dimension 2")
    for A in basis_list:
        for N in (Q, R):
            require(in_span(radical_cols, mul(A, N)), "radical candidate should be a left ideal")
            require(in_span(radical_cols, mul(N, A)), "radical candidate should be a right ideal")

    # Center computation inside A5: solve [sum c_i B_i, B_j]=0 for all j.
    equations = []
    for C in basis_list:
        diffs = [flat(sub(mul(B, C), mul(C, B))) for B in basis_list]
        for entry in range(9):
            equations.append([d[entry] for d in diffs])
    require(5 - rank(equations) == 1, "center should be one-dimensional")
    require(all(mul(I, B) == B and mul(B, I) == B for B in basis_list), "I should be the algebra identity")

    # The quotient A5/span{Q,R} is k^3: three pairwise orthogonal idempotents modulo the radical.
    p0 = scale(Fraction(1, 2), sub(I, B1))
    pplus = scale(Fraction(1, 2), add(I, B1))
    p1 = scale(Fraction(1, 2), add(pplus, B2))
    p2 = scale(Fraction(1, 2), sub(pplus, B2))
    ps = [p0, p1, p2]
    require(add(add(p0, p1), p2) == I, "quotient idempotent lifts should sum to I")
    for i, P in enumerate(ps):
        require(in_span(radical_cols, sub(mul(P, P), P)), f"p{i} should be idempotent modulo the radical")
    for i in range(3):
        for j in range(i + 1, 3):
            require(in_span(radical_cols, mul(ps[i], ps[j])), f"p{i}p{j} should vanish modulo the radical")

    # Boundary check: z(z*w)=(z*w)z holds as a magma identity, but the naive restricted-operator commutator does not vanish.
    require(all(pab_mul(z, pab_mul(z, w)) == pab_mul(pab_mul(z, w), z) for z in range(9) for w in range(9)),
            "magma identity z(z*w)=(z*w)z should hold")
    failures_f0 = 0
    for z in range(3):
        for w in range(9):
            zw = pab_mul(z, w)
            if sub(mul(L_fiber(z, 0), L_fiber(zw, 0)), mul(L_fiber(zw, 0), L_fiber(z, 0))) != zero():
                failures_f0 += 1
    failures_all = 0
    for z in range(9):
        rz = rc(z)[0]
        for w in range(9):
            zw = pab_mul(z, w)
            if sub(mul(L_fiber(z, rz), L_fiber(zw, rz)), mul(L_fiber(zw, rz), L_fiber(z, rz))) != zero():
                failures_all += 1
    require(failures_f0 == 20, "expected 20/27 F0 commutator counterexamples")
    require(failures_all == 60, "expected 60/81 all-fiber commutator counterexamples")

    os.write(1, b"PASS verify_l3_fiber_algebra_5dim\n")


if __name__ == "__main__":
    main()
    os._exit(0)
