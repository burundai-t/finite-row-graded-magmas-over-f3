#!/usr/bin/env python3
"""Layer 3 Front E verifier: structural compression of the 630-state binary presentation.

The verifier reads the Front D canonical representatives and multiplication table,
then checks the Front E factor theorem

    T_2(PAB) ~= {x,y}-owner x S_21 x U_15

with the precise multiplication law in factor coordinates. It also writes the
Front E structural tables used by the v1.6 note.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"
TABLES.mkdir(exist_ok=True)

S3 = range(3)
M = [(r, c) for r in S3 for c in S3]
IDX = {(r, c): 3 * r + c for r, c in M}
ROW = [r for r, _ in M]
COL = [c for _, c in M]
DOMAIN = [(i, j) for i in range(9) for j in range(9)]
RX = [M[i][0] for i, _ in DOMAIN]
RY = [M[j][0] for _, j in DOMAIN]


def comp(a: int, b: int) -> int:
    return (-a - b) % 3


def fiber_mul(a: int, b: int) -> int:
    """Normalized one-row PAB column product in row 0."""
    return 0 if a == b else comp(a, b)


def pab_mul(i: int, j: int) -> int:
    r1, c1 = M[i]
    r2, c2 = M[j]
    if r1 != r2:
        return IDX[(r1, r2)]
    if c1 != c2:
        return IDX[(r1, comp(c1, c2))]
    return IDX[(r1, r1)]


PAB_TABLE = [pab_mul(i, j) for i in range(9) for j in range(9)]


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sig_from_string(s: str) -> Tuple[int, ...]:
    return tuple(ord(ch) - 48 for ch in s.strip())


def row_owner(sig: Sequence[int]) -> str:
    out_rows = [ROW[v] for v in sig]
    ok_x = all(out_rows[k] == RX[k] for k in range(81))
    ok_y = all(out_rows[k] == RY[k] for k in range(81))
    if ok_x and not ok_y:
        return "x"
    if ok_y and not ok_x:
        return "y"
    if ok_x and ok_y:
        return "both"
    return "other"


def block_string(sig: Sequence[int], owner: str, delta: int) -> str:
    """Return normalized block column map.

    For owner x: owner row is r_x=0 and other y row is delta.
    For owner y: owner row is r_y=0 and other x row is delta.

    The table is indexed by (owner_column, other_column) in lexicographic order.
    """
    out: List[str] = []
    for a, b in itertools.product(S3, repeat=2):
        if owner == "x":
            i = IDX[(0, a)]
            j = IDX[(delta % 3, b)]
        elif owner == "y":
            i = IDX[(delta % 3, b)]
            j = IDX[(0, a)]
        else:
            raise ValueError(owner)
        out.append(str(COL[sig[i * 9 + j]]))
    return "".join(out)


def factor(sig: Sequence[int]) -> Tuple[str, str, str, str, str]:
    """Return owner, same-row S map, plus block, minus block, plus unary u."""
    owner = row_owner(sig)
    same = block_string(sig, owner, 0)
    plus = block_string(sig, owner, 1)
    minus = block_string(sig, owner, 2)
    # Front E theorem: cross blocks depend only on the owner column.
    u = plus[0] + plus[3] + plus[6]
    return owner, same, plus, minus, u


def block_deps(block: str) -> str:
    # block is indexed by (owner column, other column). Return dependence bits owner/other.
    bits = []
    for coord in [0, 1]:
        groups: Dict[int, set[str]] = defaultdict(set)
        yes = False
        for a, b in itertools.product(S3, repeat=2):
            key = b if coord == 0 else a
            groups[key].add(block[a * 3 + b])
            if len(groups[key]) > 1:
                yes = True
        bits.append("1" if yes else "0")
    return "".join(bits)


def phi_unary(u: str) -> str:
    """Cross-block reversal: phi(u)(c) = -u(-c)."""
    vals = [int(ch) for ch in u]
    return "".join(str((-vals[(-c) % 3]) % 3) for c in S3)


def unary_to_block(u: str) -> str:
    return "".join(u[a] for a, _b in itertools.product(S3, repeat=2))


def star_map(s: str, t: str, swap_t: bool = False) -> str:
    out = []
    for a, b in itertools.product(S3, repeat=2):
        lhs = int(s[a * 3 + b])
        rhs = int(t[b * 3 + a] if swap_t else t[a * 3 + b])
        out.append(str(fiber_mul(lhs, rhs)))
    return "".join(out)


def star_unary(u: str, v: str) -> str:
    return "".join(str(fiber_mul(int(a), int(b))) for a, b in zip(u, v))


def swapped_signature(sig: Sequence[int]) -> Tuple[int, ...]:
    return tuple(sig[j * 9 + i] for i, j in DOMAIN)


def load_mult(path: Path) -> List[List[int]]:
    with path.open(newline="", encoding="utf-8") as f:
        rdr = csv.reader(f)
        header = next(rdr)
        rows = [[int(x) for x in row[1:]] for row in rdr]
    return rows


def arity_projection(arity: int, k: int) -> bytes:
    return bytes(tup[k] for tup in itertools.product(range(9), repeat=arity))


def pointwise_product(f: bytes, g: bytes) -> bytes:
    return bytes(PAB_TABLE[a * 9 + b] for a, b in zip(f, g))


def ternary_smoke(max_size: int = 6) -> List[Dict[str, int]]:
    levels: List[set[bytes]] = [set() for _ in range(max_size + 1)]
    all_seen: set[bytes] = set()
    for k in range(3):
        sig = arity_projection(3, k)
        levels[1].add(sig)
        all_seen.add(sig)
    rows = [{"arity": 3, "size": 1, "new_functions": len(levels[1]), "cumulative_functions": len(all_seen)}]
    for size in range(2, max_size + 1):
        new: set[bytes] = set()
        for a in range(1, size):
            b = size - a
            for f in levels[a]:
                for g in levels[b]:
                    h = pointwise_product(f, g)
                    if h not in all_seen:
                        new.add(h)
        levels[size] = new
        all_seen.update(new)
        rows.append({"arity": 3, "size": size, "new_functions": len(new), "cumulative_functions": len(all_seen)})
    return rows


def main() -> None:
    reps_path = TABLES / "layer3_frontD_canonical_representatives.csv"
    mult_path = TABLES / "layer3_frontD_binary_clone_multiplication_table.csv"
    reps_raw = read_csv(reps_path)
    reps = []
    for r in reps_raw:
        sig = sig_from_string(r["function_signature_base9_on_M2"])
        reps.append({
            "id": int(r["id"]),
            "minimal_size": int(r["minimal_size"]),
            "representative": r["representative"],
            "sig": sig,
            "sha256_signature": r.get("sha256_signature", ""),
        })
    reps.sort(key=lambda r: r["id"])

    mult = load_mult(mult_path)
    factors = [factor(r["sig"]) for r in reps]
    owner = [f[0] for f in factors]
    same_map = [f[1] for f in factors]
    plus_block = [f[2] for f in factors]
    minus_block = [f[3] for f in factors]
    unary = [f[4] for f in factors]

    checks: List[Dict[str, object]] = []
    checks.append({"check": "frontD_representative_count", "result": len(reps) == 630, "detail": f"rows={len(reps)}"})
    checks.append({"check": "frontD_multiplication_shape", "result": len(mult) == 630 and all(len(row) == 630 for row in mult), "detail": f"rows={len(mult)}"})
    owner_counts = Counter(owner)
    checks.append({"check": "leftmost_owner_split", "result": owner_counts == {"x": 315, "y": 315}, "detail": dict(owner_counts)})

    S21 = sorted(set(same_map[i] for i in range(630) if owner[i] == "x"))
    U15 = sorted(set(unary[i] for i in range(630) if owner[i] == "x"))
    S21_y = sorted(set(same_map[i] for i in range(630) if owner[i] == "y"))
    U15_y = sorted(set(unary[i] for i in range(630) if owner[i] == "y"))
    checks.append({"check": "S21_count", "result": len(S21) == 21 and S21 == S21_y, "detail": f"x={len(S21)}, y={len(S21_y)}"})
    checks.append({"check": "U15_count", "result": len(U15) == 15 and U15 == U15_y, "detail": f"x={len(U15)}, y={len(U15_y)}"})

    S_idx = {s: i for i, s in enumerate(S21)}
    U_idx = {u: i for i, u in enumerate(U15)}
    # Every owner sector is exactly S21 x U15.
    pairs_x = {(same_map[i], unary[i]) for i in range(630) if owner[i] == "x"}
    pairs_y = {(same_map[i], unary[i]) for i in range(630) if owner[i] == "y"}
    all_pairs = {(s, u) for s in S21 for u in U15}
    checks.append({"check": "owner_x_factor_product", "result": pairs_x == all_pairs, "detail": f"pairs={len(pairs_x)}=21*15"})
    checks.append({"check": "owner_y_factor_product", "result": pairs_y == all_pairs, "detail": f"pairs={len(pairs_y)}=21*15"})

    # Cross blocks are unary in owner column and minus is phi(plus).
    cross_ok = True
    for i in range(630):
        if plus_block[i] != unary_to_block(unary[i]):
            cross_ok = False
            break
        if minus_block[i] != unary_to_block(phi_unary(unary[i])):
            cross_ok = False
            break
    checks.append({"check": "cross_unary_phi_law", "result": cross_ok, "detail": "plus=u(owner_col), minus=phi(u)(owner_col), phi(u)(c)=-u(-c)"})

    # S21 and U15 are closed under the normalized fiber operation.
    S_closed = all(star_map(s, t) in S_idx for s in S21 for t in S21)
    U_closed = all(star_unary(u, v) in U_idx for u in U15 for v in U15)
    checks.append({"check": "S21_closed", "result": S_closed, "detail": "21x21 table closes"})
    checks.append({"check": "U15_closed", "result": U_closed, "detail": "15x15 table closes"})

    # Factorized multiplication law for the 630x630 table.
    coded = [(0 if owner[i] == "x" else 1, S_idx[same_map[i]], U_idx[unary[i]]) for i in range(630)]
    id_by_factor = {(owner[i], S_idx[same_map[i]], U_idx[unary[i]]): i for i in range(630)}
    S_same = [[S_idx[star_map(s, t, False)] for t in S21] for s in S21]
    S_swap = [[S_idx[star_map(s, t, True)] for t in S21] for s in S21]
    U_star = [[U_idx[star_unary(u, v)] for v in U15] for u in U15]
    const_111 = U_idx["111"]
    factor_mult_ok = True
    factor_mult_fail = ""
    for i in range(630):
        oi, si, ui = coded[i]
        for j in range(630):
            oj, sj, uj = coded[j]
            sk = S_same[si][sj] if oi == oj else S_swap[si][sj]
            uk = U_star[ui][uj] if oi == oj else const_111
            pred = id_by_factor[("x" if oi == 0 else "y", sk, uk)]
            if pred != mult[i][j]:
                factor_mult_ok = False
                factor_mult_fail = f"i={i},j={j},pred={pred},actual={mult[i][j]}"
                break
        if not factor_mult_ok:
            break
    checks.append({"check": "factorized_630_multiplication", "result": factor_mult_ok, "detail": factor_mult_fail or "630x630 table reproduced from S21/U15 factor law"})

    # Variable swap involution.
    sig_to_id = {r["sig"]: r["id"] for r in reps}
    swap_rows = []
    swap_ok = True
    fixed = 0
    visited = set()
    two_cycles = 0
    for r in reps:
        sid = sig_to_id.get(swapped_signature(r["sig"]))
        if sid is None:
            swap_ok = False
        if sid == r["id"]:
            fixed += 1
        if r["id"] not in visited:
            visited.add(r["id"])
            visited.add(sid)
            if sid != r["id"]:
                two_cycles += 1
        swap_rows.append({"id": r["id"], "swap_id": sid, "minimal_size": r["minimal_size"], "swap_minimal_size": reps[sid]["minimal_size"] if sid is not None else ""})
    checks.append({"check": "variable_swap_orbits", "result": swap_ok and fixed == 0 and two_cycles == 315, "detail": f"fixed={fixed}, two_cycles={two_cycles}"})

    # Arity-3 smoke counts through size 6.
    ternary_rows = ternary_smoke(6)
    expected_ternary = [
        {"arity": 3, "size": 1, "new_functions": 3, "cumulative_functions": 3},
        {"arity": 3, "size": 2, "new_functions": 9, "cumulative_functions": 12},
        {"arity": 3, "size": 3, "new_functions": 45, "cumulative_functions": 57},
        {"arity": 3, "size": 4, "new_functions": 207, "cumulative_functions": 264},
        {"arity": 3, "size": 5, "new_functions": 1131, "cumulative_functions": 1395},
        {"arity": 3, "size": 6, "new_functions": 4182, "cumulative_functions": 5577},
    ]
    checks.append({"check": "ternary_growth_smoke_size6", "result": ternary_rows == expected_ternary, "detail": f"final={ternary_rows[-1]['cumulative_functions']}"})

    # Tables.
    write_csv(TABLES / "layer3_frontE_owner_split.csv", [
        {"owner": k, "count": owner_counts[k]} for k in ["x", "y"]
    ], ["owner", "count"])

    S_rows = []
    for idx_s, s in enumerate(S21):
        S_rows.append({
            "S_id": idx_s,
            "same_row_map": s,
            "dependencies_owner_other": block_deps(s),
            "image_size": len(set(s)),
            "occurrences_per_owner": sum(1 for i in range(630) if owner[i] == "x" and same_map[i] == s),
        })
    write_csv(TABLES / "layer3_frontE_S21_same_row_maps.csv", S_rows, ["S_id", "same_row_map", "dependencies_owner_other", "image_size", "occurrences_per_owner"])

    U_rows = []
    for idx_u, u in enumerate(U15):
        U_rows.append({
            "U_id": idx_u,
            "unary_map_u012": u,
            "plus_block": unary_to_block(u),
            "phi_u012": phi_unary(u),
            "minus_block": unary_to_block(phi_unary(u)),
            "image_size": len(set(u)),
            "occurrences_per_owner": sum(1 for i in range(630) if owner[i] == "x" and unary[i] == u),
        })
    write_csv(TABLES / "layer3_frontE_U15_cross_unary_maps.csv", U_rows, ["U_id", "unary_map_u012", "plus_block", "phi_u012", "minus_block", "image_size", "occurrences_per_owner"])

    index_rows = []
    for i, r in enumerate(reps):
        index_rows.append({
            "id": i,
            "owner": owner[i],
            "S_id": S_idx[same_map[i]],
            "U_id": U_idx[unary[i]],
            "same_row_map": same_map[i],
            "unary_map_u012": unary[i],
            "minimal_size": r["minimal_size"],
            "representative": r["representative"],
        })
    write_csv(TABLES / "layer3_frontE_630_factorization_index.csv", index_rows, ["id", "owner", "S_id", "U_id", "same_row_map", "unary_map_u012", "minimal_size", "representative"])

    profile_counter: Counter[Tuple[str, str, Tuple[int, int, int]]] = Counter()
    for i in range(630):
        deps = (block_deps(same_map[i]), block_deps(plus_block[i]), block_deps(minus_block[i]))
        imgs = (len(set(same_map[i])), len(set(plus_block[i])), len(set(minus_block[i])))
        profile_counter[(owner[i], "/".join(deps), imgs)] += 1
    profile_rows = []
    for (own, deps, imgs), count in sorted(profile_counter.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
        profile_rows.append({"owner": own, "block_dependencies_same_plus_minus": deps, "block_image_sizes_same_plus_minus": str(imgs), "count": count})
    write_csv(TABLES / "layer3_frontE_profile_distribution.csv", profile_rows, ["owner", "block_dependencies_same_plus_minus", "block_image_sizes_same_plus_minus", "count"])

    write_csv(TABLES / "layer3_frontE_swap_orbit_audit.csv", swap_rows, ["id", "swap_id", "minimal_size", "swap_minimal_size"])

    # Small operation tables.
    write_csv(TABLES / "layer3_frontE_S21_operation_table.csv", [
        {"lhs_S_id": i, **{f"rhs_{j}": S_same[i][j] for j in range(21)}} for i in range(21)
    ], ["lhs_S_id"] + [f"rhs_{j}" for j in range(21)])
    write_csv(TABLES / "layer3_frontE_S21_swap_operation_table.csv", [
        {"lhs_S_id": i, **{f"rhs_{j}": S_swap[i][j] for j in range(21)}} for i in range(21)
    ], ["lhs_S_id"] + [f"rhs_{j}" for j in range(21)])
    write_csv(TABLES / "layer3_frontE_U15_operation_table.csv", [
        {"lhs_U_id": i, **{f"rhs_{j}": U_star[i][j] for j in range(15)}} for i in range(15)
    ], ["lhs_U_id"] + [f"rhs_{j}" for j in range(15)])

    write_csv(TABLES / "layer3_frontE_factorization_summary.csv", [
        {"quantity": "binary_term_functions", "value": 630, "formula": "2*21*15"},
        {"quantity": "owner_sectors", "value": 2, "formula": "leftmost variable in {x,y}"},
        {"quantity": "same_row_factor", "value": 21, "formula": "|S21|"},
        {"quantity": "cross_unary_factor", "value": 15, "formula": "|U15|"},
        {"quantity": "swap_orbits", "value": 315, "formula": "free x/y involution"},
        {"quantity": "ternary_smoke_cumulative_size6", "value": ternary_rows[-1]["cumulative_functions"], "formula": "arity 3 through size 6 only"},
    ], ["quantity", "value", "formula"])

    write_csv(TABLES / "layer3_frontE_ternary_growth_smoke.csv", ternary_rows, ["arity", "size", "new_functions", "cumulative_functions"])

    status_rows = [
        {"claim": "T2 factorization", "status": "closed", "detail": "T2 = {x,y}-owner x S21 x U15, hence 630=2*21*15"},
        {"claim": "leftmost row source", "status": "closed", "detail": "row of every binary term is row of its leftmost variable"},
        {"claim": "cross-block unary collapse", "status": "closed", "detail": "cross blocks ignore the other column and are paired by phi(u)(c)=-u(-c)"},
        {"claim": "factorized multiplication", "status": "closed", "detail": "630x630 Front D table reproduced from 21x21/15x15 factor tables plus owner law"},
        {"claim": "binary stabilization", "status": "imported from Front D", "detail": "630 functions, no new binary functions after size 15"},
        {"claim": "all-arity free algebra", "status": "open", "detail": "ternary smoke grows to 5577 functions by size 6; no all-arity finite/infinite theorem claimed"},
    ]
    write_csv(TABLES / "layer3_frontE_status_registry.csv", status_rows, ["claim", "status", "detail"])

    manifest_files = [
        "layer3_frontE_owner_split.csv",
        "layer3_frontE_S21_same_row_maps.csv",
        "layer3_frontE_U15_cross_unary_maps.csv",
        "layer3_frontE_630_factorization_index.csv",
        "layer3_frontE_profile_distribution.csv",
        "layer3_frontE_swap_orbit_audit.csv",
        "layer3_frontE_S21_operation_table.csv",
        "layer3_frontE_S21_swap_operation_table.csv",
        "layer3_frontE_U15_operation_table.csv",
        "layer3_frontE_factorization_summary.csv",
        "layer3_frontE_ternary_growth_smoke.csv",
        "layer3_frontE_status_registry.csv",
    ]
    manifest_rows = []
    for name in manifest_files:
        p = TABLES / name
        manifest_rows.append({"file": f"tables/{name}", "exists": p.exists(), "bytes": p.stat().st_size if p.exists() else 0, "sha256": sha256_file(p) if p.exists() else ""})
    write_csv(TABLES / "layer3_frontE_table_manifest.csv", manifest_rows, ["file", "exists", "bytes", "sha256"])

    write_csv(TABLES / "layer3_frontE_verifier_checks.csv", checks, ["check", "result", "detail"])

    if not all(str(row["result"]) == "True" for row in checks):
        for row in checks:
            print(f"{row['check']}: {row['result']} :: {row['detail']}")
        raise SystemExit("Layer 3 Front E verifier: FAIL")

    print("Layer 3 Front E verifier: PASS")
    print("  binary compression: |T2| = 2 * 21 * 15 = 630 checked")
    print("  owner split: 315 x-owner and 315 y-owner functions; variable swap has 315 two-cycles")
    print("  factor theorem: each owner sector is S21 x U15, cross-minus = phi(cross-plus)")
    print("  multiplication compression: 630x630 table reproduced from 21x21 and 15x15 factor tables")
    print("  arity-growth guardrail: ternary smoke through size 6 reaches 5577 functions; all-arity status remains open")


if __name__ == "__main__":
    main()
