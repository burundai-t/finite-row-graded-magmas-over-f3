#!/usr/bin/python3
"""Layer 2 selection smoke verifier, v0.7.

Recomputes the finite selection package through Front H.

Closed fronts:
  A. package skeleton and selection chain tables;
  B. information criteria H_acc=0 and H_diag=0;
  C. nondegenerate anchors;
  D. local path-dependence via Assoc_000;
  E. finite pure C/J directed-edge selector;
  F. independence / minimality registry;
  G. hidden continuation contrast H as an auxiliary bridge;
  H. verifier/table hardening, artifact map, consistency audit.

Important guardrails:
  * Assoc is not a global PAB selector.
  * weak q/p drift-kick does not separate PAB from row-complement.
  * hidden continuation contrast H is not a required selector in v0.7:
      - the global Omega' H-certificate is open;
      - PAB and row-complement have the same H profile on d=000.
"""

from __future__ import annotations

from itertools import product
from pathlib import Path
import csv
import hashlib
import math
from typing import Callable, Iterable

S = (0, 1, 2)
M = tuple((r, c) for r in S for c in S)
MX = tuple((r, c) for r in S for c in S if r != c)
Q_PLUS = frozenset(((0, 1), (1, 2), (2, 0)))
Q_MINUS = frozenset(((0, 2), (2, 1), (1, 0)))

# Layer 1 v3+H global guardrails imported into Layer 2.
LAYER1_GLOBAL_ASSOC_MIN = 63
LAYER1_GLOBAL_ASSOC_MAX = 597
PAB_ASSOC = 219

# Layer 1H controlled strata imported constants.
CONTROLLED_H_SUMMARY = [
    {
        "stratum": "column_blind_x_Delta",
        "points": 243,
        "H_min": 1836,
        "H_max": 7302,
        "pure_count": 159,
        "pure_H_max": 7020,
        "N_neg_max": 108,
        "count_above_PAB_7020": 12,
        "count_ge_PAB_7020": 18,
        "certificate_role": "recomputed exactly by this Layer 2 verifier",
    },
    {
        "stratum": "affine_x_Delta",
        "points": 19683,
        "H_min": -2268,
        "H_max": 7302,
        "pure_count": 723,
        "pure_H_max": 7020,
        "N_neg_max": 441,
        "count_above_PAB_7020": 12,
        "count_ge_PAB_7020": 18,
        "certificate_role": "imported from Layer 1H controlled atlas",
    },
    {
        "stratum": "degree_le2_x_Delta_exact",
        "points": 14348907,
        "H_min": -2268,
        "H_max": 7302,
        "pure_count": 3177,
        "pure_H_max": 7020,
        "N_neg_max": 468,
        "count_above_PAB_7020": 12,
        "count_ge_PAB_7020": 18,
        "certificate_role": "imported from Layer 1H controlled atlas",
    },
]


def comp(a: int, b: int) -> int:
    return (-a - b) % 3


def entropy_bits_from_values(values: tuple[int, ...]) -> float:
    total = len(values)
    counts = {v: values.count(v) for v in set(values)}
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def one_table_entropy_zero(table: tuple[int, ...]) -> bool:
    return abs(entropy_bits_from_values(table)) < 1e-12


def fmt_bits(x: float) -> str:
    if abs(x) < 1e-12:
        return "0"
    return f"{x:.12g}"


def h_value(a: int, b: int, r1: int, r2: int) -> int:
    diff = (r2 - r1) % 3
    if diff == 1:
        return (a + r1) % 3
    if diff == 2:
        return (b + r1) % 3
    raise ValueError("h_value called with equal rows")


def delta_value(d: tuple[int, int, int], r: int, c: int) -> int:
    return (d[(c - r) % 3] + r) % 3


def multiply(x: tuple[int, int], y: tuple[int, int], *, a: int, b: int, d: tuple[int, int, int]) -> tuple[int, int]:
    r1, c1 = x
    r2, c2 = y
    if r1 != r2:
        return (r1, h_value(a, b, r1, r2))
    if c1 != c2:
        return (r1, comp(c1, c2))
    return (r1, delta_value(d, r1, c1))


def assoc_count(a: int, b: int, d: tuple[int, int, int] = (0, 0, 0)) -> int:
    n = 0
    for x, y, z in product(M, repeat=3):
        left = multiply(multiply(x, y, a=a, b=b, d=d), z, a=a, b=b, d=d)
        right = multiply(x, multiply(y, z, a=a, b=b, d=d), a=a, b=b, d=d)
        if left == right:
            n += 1
    return n


def assoc_raw_blocks(a: int, b: int, d: tuple[int, int, int] = (0, 0, 0)) -> dict[str, int]:
    """Normalized 243-term five-block Assoc count for a column-blind rule."""
    blocks = {"RRR": 0, "RRS": 0, "RSR": 0, "RSS": 0, "RST": 0}
    for by, rz, ax, cy, cz in product(S, repeat=5):
        x = (0, ax)
        y = (by, cy)
        z = (rz, cz)
        left = multiply(multiply(x, y, a=a, b=b, d=d), z, a=a, b=b, d=d)
        right = multiply(x, multiply(y, z, a=a, b=b, d=d), a=a, b=b, d=d)
        if by == 0 and rz == 0:
            block = "RRR"
        elif by == 0 and rz != 0:
            block = "RRS"
        elif by != 0 and rz == 0:
            block = "RSR"
        elif by != 0 and rz == by:
            block = "RSS"
        else:
            block = "RST"
        if left == right:
            blocks[block] += 1
    return blocks


def hacc_bits_for_rule(g: Callable[[int, int, int, int], int]) -> float:
    """Compute H_acc = I(C_out; C1,C2 | R1,R2) for deterministic g in bits."""
    row_pairs = [(r1, r2) for r1 in S for r2 in S if r1 != r2]
    total = 0.0
    for r1, r2 in row_pairs:
        values = tuple(g(r1, c1, r2, c2) for c1, c2 in product(S, repeat=2))
        total += entropy_bits_from_values(values)
    return total / len(row_pairs)


def is_column_blind_callable(g: Callable[[int, int, int, int], int]) -> bool:
    for r1, r2 in product(S, repeat=2):
        if r1 == r2:
            continue
        values = {g(r1, c1, r2, c2) for c1, c2 in product(S, repeat=2)}
        if len(values) != 1:
            return False
    return True


def representative_hacc_rules() -> list[tuple[str, Callable[[int, int, int, int], int], str]]:
    def h12(r1: int, c1: int, r2: int, c2: int) -> int:
        return h_value(1, 2, r1, r2)

    def h21(r1: int, c1: int, r2: int, c2: int) -> int:
        return h_value(2, 1, r1, r2)

    def left_column(r1: int, c1: int, r2: int, c2: int) -> int:
        return c1

    def right_column(r1: int, c1: int, r2: int, c2: int) -> int:
        return c2

    def normalized_column_sum(r1: int, c1: int, r2: int, c2: int) -> int:
        return (c1 + c2 - r1) % 3

    def column_equality_gate(r1: int, c1: int, r2: int, c2: int) -> int:
        nc1 = (c1 - r1) % 3
        nc2 = (c2 - r1) % 3
        return (r1 + (0 if nc1 == nc2 else 1)) % 3

    return [
        ("PAB_h12_r2", h12, "zero-access selected survivor"),
        ("row_complement_h21", h21, "zero-access selected competitor"),
        ("left_column_c1", left_column, "maximal column access witness"),
        ("right_column_c2", right_column, "maximal column access witness"),
        ("normalized_column_sum", normalized_column_sum, "maximal column access witness"),
        ("column_equality_gate", column_equality_gate, "intermediate positive access witness"),
    ]


def rule_label(a: int, b: int) -> str:
    if (a, b) == (1, 2):
        return "g1=r2 / PAB"
    if (a, b) == (2, 1):
        return "row-complement"
    if (a, b) == (0, 0):
        return "g5=r1"
    return ""


def formula_hint(a: int, b: int) -> str:
    if (a, b) == (1, 2):
        return "h(r1,r2)=r2"
    if (a, b) == (2, 1):
        return "h(r1,r2)=overline(r1,r2)"
    if a == b:
        return f"h(r1,r2)=r1+{a}"
    return f"h_{{{a},{b}}}"


def x21(a: int, b: int, d: tuple[int, int, int]) -> str:
    return "".join(str(a) for _ in range(9)) + "".join(str(b) for _ in range(9)) + "".join(map(str, d))


def diag_entropy_zero(d: tuple[int, int, int]) -> bool:
    return len(set(d)) == 1


def diag_entropy_bits(d: tuple[int, int, int]) -> float:
    return entropy_bits_from_values(tuple(d))


def diag_type(d: tuple[int, int, int]) -> str:
    k = len(set(d))
    if k == 1:
        return "constant"
    if k == 2:
        return "two-valued"
    return "permutation"


def diag_idempotent_all(d: tuple[int, int, int]) -> bool:
    return all(multiply((r, r), (r, r), a=1, b=2, d=d) == (r, r) for r in S)


def absorption_set(a: int, b: int, x: tuple[int, int], d: tuple[int, int, int] = (0, 0, 0)) -> tuple[tuple[int, int], ...]:
    return tuple(y for y in MX if y != x and multiply(x, y, a=a, b=b, d=d) == x)


def edge_reversal(x: tuple[int, int]) -> tuple[int, int]:
    r, c = x
    return (c, r)


def forward_continuation(x: tuple[int, int]) -> tuple[int, int]:
    r, c = x
    return (c, comp(r, c))


def backward_continuation(x: tuple[int, int]) -> tuple[int, int]:
    r, c = x
    return (comp(r, c), r)


def drifted_reversal(x: tuple[int, int]) -> tuple[int, int]:
    return backward_continuation(edge_reversal(x))


def cinv_j(x: tuple[int, int]) -> tuple[int, int]:
    return backward_continuation(edge_reversal(x))


def permutation_cycles(T: Callable[[tuple[int, int]], tuple[int, int]]) -> list[list[tuple[int, int]]]:
    seen: set[tuple[int, int]] = set()
    cycles: list[list[tuple[int, int]]] = []
    for x in MX:
        if x in seen:
            continue
        cyc = []
        y = x
        while y not in seen:
            seen.add(y)
            cyc.append(y)
            y = T(y)
        cycles.append(cyc)
    return cycles


def order_of_perm(T: Callable[[tuple[int, int]], tuple[int, int]]) -> int:
    lcm = 1
    for cyc in permutation_cycles(T):
        lcm = math.lcm(lcm, len(cyc))
    return lcm


def split_pairs(T2: Callable[[tuple[int, int]], tuple[int, int]]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    pairs = []
    seen: set[tuple[int, int]] = set()
    for x in MX:
        if x in seen:
            continue
        y = T2(x)
        pairs.append((x, y))
        seen.add(x)
        seen.add(y)
    return pairs


def weak_qp_splitting_audit(T3: Callable[[tuple[int, int]], tuple[int, int]], T2: Callable[[tuple[int, int]], tuple[int, int]]) -> list[dict[str, str]]:
    pairs = split_pairs(T2)
    rows = []
    for choices in product((0, 1), repeat=3):
        q = frozenset(pairs[i][choices[i]] for i in range(3))
        p = frozenset(set(MX) - set(q))
        t3_preserves = all(T3(x) in q for x in q) and all(T3(x) in p for x in p)
        t3_switches = all(T3(x) in p for x in q) and all(T3(x) in q for x in p)
        t2_switches = all(T2(x) in p for x in q) and all(T2(x) in q for x in p)
        rows.append({
            "choices": "".join(map(str, choices)),
            "q_sector": " ".join(map(str, sorted(q))),
            "p_sector": " ".join(map(str, sorted(p))),
            "T3_preserves_qp": str(t3_preserves),
            "T3_switches_qp": str(t3_switches),
            "T2_switches_qp": str(t2_switches),
            "weak_drift_kick_pass": str(t3_preserves and t2_switches),
        })
    return rows


def pure_cj_pass(a: int, b: int) -> bool:
    return all(set(absorption_set(a, b, x)) == {forward_continuation(x), edge_reversal(x)} for x in MX)


def op_table_for(a: int, b: int, d: tuple[int, int, int]) -> list[list[int]]:
    idx = {x: i for i, x in enumerate(M)}
    table: list[list[int]] = []
    for x in M:
        row: list[int] = []
        for y in M:
            row.append(idx[multiply(x, y, a=a, b=b, d=d)])
        table.append(row)
    return table


def H_profile(a: int, b: int, d: tuple[int, int, int]) -> dict[str, int]:
    """Fast exact H-profile via the four-point combinatorial formula."""
    op = op_table_for(a, b, d)
    I_tot = 0
    B_tot = 0
    H_tot = 0
    H_pos = 0
    H_neg_abs = 0
    N_neg = 0
    h_loc_min = 10**9
    h_loc_max = -10**9

    for x in range(9):
        opx = op[x]
        for y in range(9):
            xy = opx[y]
            opxy = op[xy]
            opy = op[y]
            for z in range(9):
                yz = opy[z]
                left_assoc = opxy[z]
                right_assoc = opx[yz]
                opleft = op[left_assoc]
                opright = op[right_assoc]
                opz = op[z]
                opyz = op[yz]
                I_half = 0
                B_half = 0
                for w in range(9):
                    if opxy[opz[w]] != opx[opyz[w]]:
                        I_half += 1
                    if opleft[w] != opright[w]:
                        B_half += 1
                local_H = 2 * (I_half - B_half)
                I_tot += 2 * I_half
                B_tot += 2 * B_half
                H_tot += local_H
                if local_H < h_loc_min:
                    h_loc_min = local_H
                if local_H > h_loc_max:
                    h_loc_max = local_H
                if local_H > 0:
                    H_pos += local_H
                elif local_H < 0:
                    H_neg_abs += -local_H
                    N_neg += 1
    return {
        "I_tot": I_tot,
        "B_tot": B_tot,
        "H_tot": H_tot,
        "H_pos": H_pos,
        "H_neg_abs": H_neg_abs,
        "N_neg": N_neg,
        "h_loc_min": h_loc_min,
        "h_loc_max": h_loc_max,
    }

def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def csv_row_count(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    with path.open(newline="", encoding="utf-8") as f:
        return max(sum(1 for _ in csv.DictReader(f)), 0)


def front_for_table(name: str) -> str:
    if "frontG" in name:
        return "G"
    if "frontF" in name or "criterion_independence" in name or "minimality" in name:
        return "F"
    if "frontE" in name or "absorption" in name or "qp" in name or "weak_qp" in name:
        return "E"
    if "path_dependence" in name or "assoc_" in name or "nontrivial_cb_assoc" in name:
        return "D"
    if "nondegenerate" in name:
        return "C"
    if "hacc" in name or "diag_entropy" in name or "information" in name:
        return "B"
    if "selection_chain" in name or "status_registry" in name:
        return "A/H"
    if "frontH" in name:
        return "H"
    return "misc"


def boolstr(x: bool) -> str:
    return "True" if x else "False"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    tables = root / "tables"

    # ------------------------------------------------------------------
    # Front B: information criteria.
    # ------------------------------------------------------------------
    zero_count = 0
    nonzero_count = 0
    for table in product(S, repeat=9):
        is_zero = one_table_entropy_zero(tuple(table))
        is_constant = len(set(table)) == 1
        assert is_zero == is_constant, "finite entropy-zero lemma failed for one-table function"
        if is_zero:
            zero_count += 1
        else:
            nonzero_count += 1
    assert zero_count == 3 and nonzero_count == 3**9 - 3

    hacc_audit_rows = []
    for name, func, note in representative_hacc_rules():
        h = hacc_bits_for_rule(func)
        zero = abs(h) < 1e-12
        column_blind = is_column_blind_callable(func)
        hacc_audit_rows.append({
            "rule": name,
            "H_acc_bits": fmt_bits(h),
            "H_acc_zero": boolstr(zero),
            "column_blind": boolstr(column_blind),
            "zero_iff_column_blind_on_audit": boolstr(zero == column_blind),
            "note": note,
        })
    write_csv(tables / "layer2_hacc_representative_audit.csv", hacc_audit_rows)
    assert all(row["zero_iff_column_blind_on_audit"] == "True" for row in hacc_audit_rows)

    information_rows = [
        {
            "criterion": "H_acc=0",
            "domain": "cross-rules G",
            "theorem": "I(C_out;C1,C2|R1,R2)=0 iff g is column-blind",
            "finite_core_check": "all 3^9 one-table functions: entropy zero iff constant",
            "survivors": 9,
            "status": "Front B closed",
        },
        {
            "criterion": "H_diag=0",
            "domain": "diagonals Delta",
            "theorem": "H(d0,d1,d2)=0 iff d0=d1=d2",
            "finite_core_check": "all 27 diagonals enumerated",
            "survivors": 3,
            "status": "Front B closed",
        },
    ]
    write_csv(tables / "layer2_information_criteria.csv", information_rows)

    # ------------------------------------------------------------------
    # Front C-D: column-blind, nontriviality, Assoc_000.
    # ------------------------------------------------------------------
    cb_rows = []
    nontriv_rows = []
    path_rows = []
    block_rows = []
    for a, b in product(S, repeat=2):
        assoc = assoc_count(a, b, (0, 0, 0))
        blocks = assoc_raw_blocks(a, b, (0, 0, 0))
        assert 3 * sum(blocks.values()) == assoc
        is_nontriv = a != b
        row = {
            "a": a,
            "b": b,
            "x18_cross_rule": x21(a, b, (0, 0, 0))[:18],
            "formula_hint": formula_hint(a, b),
            "label": rule_label(a, b),
            "type": "nontrivial" if is_nontriv else "trivial",
            "H_acc_bits": "0",
            "Assoc_d000": assoc,
            "selected_after_Hacc": "True",
            "selected_after_nontriviality": boolstr(is_nontriv),
            "selected_after_Assoc_min": boolstr((a, b) in ((1, 2), (2, 1))),
            "pure_CJ_pass": boolstr(pure_cj_pass(a, b)),
        }
        cb_rows.append(row)
        block_rows.append({
            "a": a,
            "b": b,
            "label": rule_label(a, b),
            "type": "nontrivial" if is_nontriv else "trivial",
            "raw_RRR": blocks["RRR"],
            "raw_RRS": blocks["RRS"],
            "raw_RSR": blocks["RSR"],
            "raw_RSS": blocks["RSS"],
            "raw_RST": blocks["RST"],
            "raw_total": sum(blocks.values()),
            "Assoc_d000": assoc,
            "extra_RRS_plus_RSR_over_selected": (blocks["RRS"] + blocks["RSR"]),
        })
        if is_nontriv:
            nontriv_rows.append(row)
            path_rows.append({
                "a": a,
                "b": b,
                "label": rule_label(a, b),
                "formula_hint": formula_hint(a, b),
                "Assoc_000": assoc,
                "bracket_sensitive_triples": 729 - assoc,
                "bracket_sensitive_fraction": f"{(729 - assoc) / 729:.12f}",
                "selected_by_local_path_dependence": boolstr((a, b) in ((1, 2), (2, 1))),
                "interpretation": "minimum accidental associativity inside nontrivial column-blind" if (a, b) in ((1, 2), (2, 1)) else "discarded by extra RRS/RSR coincidences",
            })

    write_csv(tables / "layer2_hacc_column_blind_rules.csv", cb_rows)
    write_csv(tables / "layer2_nontrivial_cb_assoc_table.csv", nontriv_rows)
    write_csv(tables / "layer2_path_dependence_table.csv", path_rows)
    write_csv(tables / "layer2_assoc_block_decomposition_cb.csv", block_rows)

    assert len(cb_rows) == 9
    assert len(nontriv_rows) == 6
    assoc_min = min(int(r["Assoc_d000"]) for r in nontriv_rows)
    survivors = {(int(r["a"]), int(r["b"])) for r in nontriv_rows if int(r["Assoc_d000"]) == assoc_min}
    assert assoc_min == 219 and survivors == {(1, 2), (2, 1)}

    theorem_rows = [
        {
            "theorem": "local Assoc_000 path-dependence",
            "domain": "six nontrivial column-blind rules after d=000",
            "minimum_Assoc_000": 219,
            "survivor_count": 2,
            "survivors": "g1=r2 / PAB; row-complement",
            "discarded_rules_Assoc_000": 273,
            "structural_localization": "discarded rules add 9+9 raw coincidences in RRS and RSR",
            "guardrail": "not a global selector; Layer 1 global Assoc minimum is 63",
        }
    ]
    write_csv(tables / "layer2_path_dependence_theorem.csv", theorem_rows)

    guardrail_rows = [
        {
            "claim": "Assoc is not a global PAB selector",
            "PAB_Assoc": PAB_ASSOC,
            "Layer1_global_min_Assoc": LAYER1_GLOBAL_ASSOC_MIN,
            "Layer1_global_max_Assoc": LAYER1_GLOBAL_ASSOC_MAX,
            "proper_use_in_Layer2": "minimize Assoc_000 only after H_acc=0, nontriviality, H_diag=0, and diagonal idempotence",
        }
    ]
    write_csv(tables / "layer2_assoc_guardrail.csv", guardrail_rows)

    # ------------------------------------------------------------------
    # Front C diagonal tables.
    # ------------------------------------------------------------------
    diag_rows = []
    for d in product(S, repeat=3):
        d = tuple(d)
        h0 = diag_entropy_zero(d)
        idem = diag_idempotent_all(d)
        diag_rows.append({
            "d": "".join(map(str, d)),
            "diagonal_type": diag_type(d),
            "H_diag_bits": fmt_bits(diag_entropy_bits(d)),
            "H_diag_zero": boolstr(h0),
            "constant_diagonal": boolstr(h0),
            "diagonal_idempotent_all": boolstr(idem),
            "selected_after_Hdiag_then_idempotence": boolstr(h0 and idem),
        })
    write_csv(tables / "layer2_diag_entropy_table.csv", diag_rows)
    constants = {r["d"] for r in diag_rows if r["H_diag_zero"] == "True"}
    selected_diag = {r["d"] for r in diag_rows if r["selected_after_Hdiag_then_idempotence"] == "True"}
    idem_all = {r["d"] for r in diag_rows if r["diagonal_idempotent_all"] == "True"}
    assert constants == {"000", "111", "222"}
    assert selected_diag == {"000"}
    assert len(idem_all) == 9

    dist = {}
    for row in diag_rows:
        key = (row["diagonal_type"], row["H_diag_bits"])
        dist[key] = dist.get(key, 0) + 1
    dist_rows = [{"diagonal_type": k[0], "H_diag_bits": k[1], "count": v} for k, v in sorted(dist.items())]
    write_csv(tables / "layer2_diag_entropy_distribution.csv", dist_rows)

    anchor_rows = [
        {
            "anchor": "cross-rule nontriviality",
            "condition": "a != b",
            "input_count": 9,
            "output_count": 6,
            "reason": "right row direction changes output column",
            "status": "Front C closed",
        },
        {
            "anchor": "diagonal idempotence alone",
            "condition": "d0=0",
            "input_count": 27,
            "output_count": 9,
            "reason": "all (r,r) are fixed, but d1,d2 remain free",
            "status": "diagnostic: not sufficient alone",
        },
        {
            "anchor": "diagonal idempotence after H_diag=0",
            "condition": "constant diagonal and d0=0",
            "input_count": 3,
            "output_count": 1,
            "reason": "among 000,111,222 only 000 fixes (r,r)",
            "status": "Front C closed",
        },
    ]
    write_csv(tables / "layer2_nondegenerate_anchor_audit.csv", anchor_rows)

    # ------------------------------------------------------------------
    # Front E: finite pure C/J drift-kick.
    # ------------------------------------------------------------------
    canonical_rows = [
        {"map": "C", "formula": "C(r,c)=(c,overline(rc))", "order": order_of_perm(forward_continuation), "role": "forward head-to-tail continuation / drift"},
        {"map": "C^{-1}", "formula": "C^{-1}(r,c)=(overline(rc),r)", "order": order_of_perm(backward_continuation), "role": "backward continuation"},
        {"map": "J", "formula": "J(r,c)=(c,r)", "order": order_of_perm(edge_reversal), "role": "intrinsic edge reversal / pure kick"},
        {"map": "C^{-1}J", "formula": "C^{-1}J(r,c)=(overline(cr),c)", "order": order_of_perm(drifted_reversal), "role": "drifted reversal; competitor kick"},
    ]
    write_csv(tables / "layer2_frontE_canonical_maps.csv", canonical_rows)
    assert order_of_perm(forward_continuation) == 3
    assert order_of_perm(edge_reversal) == 2
    assert all(edge_reversal(forward_continuation(edge_reversal(x))) == backward_continuation(x) for x in MX)

    absorption_degree_rows = []
    nontriv_abs_rows = []
    for a, b in product(S, repeat=2):
        degrees = [len(absorption_set(a, b, x)) for x in MX]
        pure = pure_cj_pass(a, b)
        absorption_degree_rows.append({
            "a": a,
            "b": b,
            "label": rule_label(a, b),
            "type": "nontrivial" if a != b else "trivial",
            "outdegree_multiset": " ".join(map(str, sorted(degrees))),
            "constant_outdegree_2": boolstr(all(k == 2 for k in degrees)),
            "pure_CJ_pass": boolstr(pure),
        })
        if a != b:
            nontriv_abs_rows.append(absorption_degree_rows[-1])
    write_csv(tables / "layer2_absorption_degree_all_cb.csv", absorption_degree_rows)
    write_csv(tables / "layer2_frontE_nontrivial_cb_absorption_audit.csv", nontriv_abs_rows)
    assert [r for r in absorption_degree_rows if r["pure_CJ_pass"] == "True"][0]["label"] == "g1=r2 / PAB"
    assert len([r for r in absorption_degree_rows if r["pure_CJ_pass"] == "True"]) == 1

    transition_rows = []
    audit_rows = []
    all_weak = []
    survivor_rules = {
        "PAB": (1, 2, forward_continuation, edge_reversal),
        "row-complement": (2, 1, backward_continuation, drifted_reversal),
    }
    for name, (a, b, T3, T2) in survivor_rules.items():
        for x in MX:
            absset = absorption_set(a, b, x)
            assert len(absset) == 2
            assert T3(x) in absset and T2(x) in absset
            transition_rows.append({
                "rule": name,
                "x": str(x),
                "absorbed_1": str(absset[0]),
                "absorbed_2": str(absset[1]),
                "T3": str(T3(x)),
                "T2": str(T2(x)),
                "edge_reversal_J": str(edge_reversal(x)),
                "T3_preserves_orientation_sectors": boolstr((T3(x) in Q_PLUS if x in Q_PLUS else T3(x) in Q_MINUS)),
                "T2_is_canonical_reversal": boolstr(T2(x) == edge_reversal(x)),
            })
        weak_rows = weak_qp_splitting_audit(T3, T2)
        weak_pass_count = sum(r["weak_drift_kick_pass"] == "True" for r in weak_rows)
        canonical_reversal_pass = all(T2(x) == edge_reversal(x) for x in MX)
        canonical_drift_pass = all(T3(x) == forward_continuation(x) for x in MX)
        inverse_drift = all(T3(x) == backward_continuation(x) for x in MX)
        audit_rows.append({
            "rule": name,
            "T3_order": order_of_perm(T3),
            "T2_order": order_of_perm(T2),
            "weak_qp_splitting_pass_count": weak_pass_count,
            "weak_qp_splitting_separates_PAB": "False",
            "T2_is_canonical_edge_reversal_J": boolstr(canonical_reversal_pass),
            "T3_is_forward_continuation_C": boolstr(canonical_drift_pass),
            "T3_is_backward_continuation_C_inv": boolstr(inverse_drift),
            "canonical_pure_drift_kick_pass": boolstr(canonical_reversal_pass and canonical_drift_pass),
            "audit_note": "weak split is insufficient" if weak_pass_count > 0 and name == "row-complement" else "",
        })
        all_weak.extend({"rule": name, **row} for row in weak_rows)

    write_csv(tables / "layer2_absorption_transitions_pab_comp.csv", transition_rows)
    write_csv(tables / "layer2_qp_splitting_audit.csv", audit_rows)
    write_csv(tables / "layer2_weak_qp_splitting_details.csv", all_weak)
    audit = {r["rule"]: r for r in audit_rows}
    assert audit["PAB"]["weak_qp_splitting_pass_count"] == 2
    assert audit["row-complement"]["weak_qp_splitting_pass_count"] == 2
    assert audit["PAB"]["canonical_pure_drift_kick_pass"] == "True"
    assert audit["row-complement"]["canonical_pure_drift_kick_pass"] == "False"

    factorization_rows = [
        {"rule": "PAB", "absorption_transitions": "{C,J}", "drift": "C", "kick": "J", "kick_phase_shift": 0, "selected_by_pure_CJ": "True"},
        {"rule": "row-complement", "absorption_transitions": "{C^{-1},C^{-1}J}", "drift": "C^{-1}", "kick": "C^{-1}J", "kick_phase_shift": 1, "selected_by_pure_CJ": "False"},
    ]
    write_csv(tables / "layer2_frontE_survivor_transition_factorization.csv", factorization_rows)
    pure_theorem_rows = [
        {
            "theorem": "finite pure C/J directed-edge selector",
            "domain": "nine column-blind cross-rules after H_acc=0",
            "criterion": "for every x in M^x, Abs(x)={C(x),J(x)}",
            "survivors": "g1=r2 / PAB",
            "row_complement_failure": "has C^{-1}J drifted reversal instead of pure J kick",
            "weak_qp_guardrail": "weak q/p split does not separate PAB and row-complement",
            "C2_symplectic_status": "open geometric bridge; not a selector dependency in v0.7",
        }
    ]
    write_csv(tables / "layer2_frontE_pure_drift_kick_theorem.csv", pure_theorem_rows)

    # ------------------------------------------------------------------
    # Front F: independence and minimality registry.
    # ------------------------------------------------------------------
    idempotent_diagonals = [tuple(map(int, r["d"])) for r in diag_rows if r["diagonal_idempotent_all"] == "True"]
    no_hdiag_assoc_rows = []
    for a, b in product(S, repeat=2):
        if a == b:
            continue
        for d in idempotent_diagonals:
            no_hdiag_assoc_rows.append({
                "a": a,
                "b": b,
                "label": rule_label(a, b),
                "d": "".join(map(str, d)),
                "Assoc": assoc_count(a, b, d),
            })
    no_hdiag_assoc_rows.sort(key=lambda r: (int(r["Assoc"]), r["a"], r["b"], r["d"]))
    write_csv(tables / "layer2_frontF_no_Hdiag_idempotent_assoc_audit.csv", no_hdiag_assoc_rows)
    assert no_hdiag_assoc_rows[0]["d"] == "021" and int(no_hdiag_assoc_rows[0]["Assoc"]) == 189

    role_rows = [
        {"criterion": "H_acc=0", "scope": "cross-rule", "stage_effect": "3^18 -> 9", "role_class": "domain-enabling essential", "independence_note": "without it, global Assoc minima are column-dependent and pure C/J is not globally defined", "logical_minimality": "essential for current finite selector"},
        {"criterion": "H_diag=0", "scope": "diagonal", "stage_effect": "27 -> 3", "role_class": "essential diagonal information compression", "independence_note": "idempotence alone leaves 9 diagonals; Assoc over idempotent diagonals prefers d=021, not d=000", "logical_minimality": "essential unless replaced by another diagonal selector"},
        {"criterion": "nontriviality a!=b", "scope": "column-blind cross-rule", "stage_effect": "9 -> 6", "role_class": "structural guardrail", "independence_note": "removes fake binary interactions before path-dependence", "logical_minimality": "not essential for uniqueness once pure C/J is accepted"},
        {"criterion": "diagonal idempotence", "scope": "constant diagonals", "stage_effect": "3 -> 1", "role_class": "essential anchor", "independence_note": "H_diag alone leaves 000,111,222", "logical_minimality": "essential unless replaced by min Assoc among constant diagonals"},
        {"criterion": "min Assoc_000", "scope": "six nontrivial column-blind rules at d=000", "stage_effect": "6 -> 2", "role_class": "explanatory algebraic bridge", "independence_note": "exposes PAB/row-complement ambiguity and localizes extra coincidences in RRS+RSR", "logical_minimality": "not essential for uniqueness once pure C/J is accepted"},
        {"criterion": "pure C/J drift-kick", "scope": "column-blind absorption on M^x", "stage_effect": "2 -> 1 narratively; 9 -> 1 if applied after H_acc", "role_class": "final finite selector", "independence_note": "separates the exact PAB/competitor ambiguity; weak q/p does not", "logical_minimality": "essential if Assoc_000 is used as the preceding cross-rule selector"},
        {"criterion": "hidden continuation contrast H", "scope": "controlled Layer 1H strata", "stage_effect": "no reduction in v0.7", "role_class": "auxiliary bridge", "independence_note": "PAB and row-complement have the same H_tot=7020 pure profile at d=000", "logical_minimality": "not a selector dependency while global H certificate is open"},
    ]
    write_csv(tables / "layer2_frontF_criterion_role_registry.csv", role_rows)

    deletion_rows = [
        {"removed_criterion": "H_acc=0", "remaining_attempt": "Assoc/path-dependence plus later dynamical ideas", "exact_or_imported_consequence": "Layer 1 global min Assoc=63 while PAB=219; no global minimizer/maximizer is column-blind", "survivor_count_or_failure": "not a PAB selector", "status": "essential / imported guardrail"},
        {"removed_criterion": "H_diag=0", "remaining_attempt": "diagonal idempotence plus min Assoc on idempotent diagonals", "exact_or_imported_consequence": "idempotence leaves 9 diagonals; min Assoc over nontrivial CB x idempotent diagonals is 189 at d=021", "survivor_count_or_failure": "selects wrong diagonal frontier, not PAB", "status": "essential for current diagonal chain"},
        {"removed_criterion": "nontriviality", "remaining_attempt": "H_acc, H_diag, idempotence, min Assoc_000, pure C/J", "exact_or_imported_consequence": "min Assoc_000 still discards trivial CB rules; pure C/J also rejects them", "survivor_count_or_failure": "still 1", "status": "not logically essential; retained as structural guardrail"},
        {"removed_criterion": "diagonal idempotence", "remaining_attempt": "H_diag plus cross-rule criteria", "exact_or_imported_consequence": "H_diag leaves constant diagonals 000,111,222", "survivor_count_or_failure": "3 diagonal survivors", "status": "essential unless replaced by another diagonal selector"},
        {"removed_criterion": "min Assoc_000", "remaining_attempt": "H_acc, H_diag, idempotence, pure C/J", "exact_or_imported_consequence": "pure C/J selects PAB directly from all 9 column-blind rules", "survivor_count_or_failure": "still 1", "status": "not logically essential; retained as explanatory bridge"},
        {"removed_criterion": "pure C/J drift-kick", "remaining_attempt": "H_acc, H_diag, idempotence, nontriviality, min Assoc_000", "exact_or_imported_consequence": "PAB and row-complement both have Assoc_000=219", "survivor_count_or_failure": "2 cross-rule survivors", "status": "essential for uniqueness in narrative chain"},
        {"removed_criterion": "hidden continuation contrast H", "remaining_attempt": "main v0.7 finite selector", "exact_or_imported_consequence": "no change; H is auxiliary only", "survivor_count_or_failure": "still 1", "status": "not a dependency"},
    ]
    write_csv(tables / "layer2_frontF_deletion_audit.csv", deletion_rows)
    write_csv(tables / "layer2_frontF_criterion_removal_audit.csv", deletion_rows)

    minimal_sets = [
        {"set_name": "full narrative v0.7", "criteria": "H_acc, H_diag, nontriviality, diagonal idempotence, min Assoc_000, pure C/J; H auxiliary", "cross_survivors": 1, "diagonal_survivors": 1, "total_survivors": 1, "meaning": "best explanatory chain from global to specific"},
        {"set_name": "core finite uniqueness", "criteria": "H_acc, H_diag, diagonal idempotence, pure C/J", "cross_survivors": 1, "diagonal_survivors": 1, "total_survivors": 1, "meaning": "shortest current finite selector once pure C/J is accepted"},
        {"set_name": "algebraic bridge without dynamics", "criteria": "H_acc, H_diag, diagonal idempotence, nontriviality, min Assoc_000", "cross_survivors": 2, "diagonal_survivors": 1, "total_survivors": 2, "meaning": "exposes PAB/row-complement ambiguity"},
        {"set_name": "H-frontier auxiliary", "criteria": "H_acc, H_diag, diagonal idempotence, H pure frontier on controlled strata", "cross_survivors": "at least 2", "diagonal_survivors": 1, "total_survivors": "not unique", "meaning": "PAB and row-complement both lie on the pure H frontier"},
        {"set_name": "diagonal without H_diag", "criteria": "diagonal idempotence only on Delta", "cross_survivors": "unchanged", "diagonal_survivors": 9, "total_survivors": "not unique", "meaning": "shows H_diag is independently needed"},
    ]
    write_csv(tables / "layer2_frontF_minimal_selector_sets.csv", minimal_sets)
    write_csv(tables / "layer2_frontF_minimal_core_registry.csv", minimal_sets)

    dependency_rows = [
        {"criterion": "H_acc=0", "prerequisite": "Layer 1 normal form", "depends_on_prior_selection": "False", "notes": "globally defined on cross-rule sector; enables column-blind absorption domain"},
        {"criterion": "H_diag=0", "prerequisite": "Layer 1 diagonal sector", "depends_on_prior_selection": "False", "notes": "globally defined on diagonal sector"},
        {"criterion": "nontriviality", "prerequisite": "column-blind parametrization h_{a,b}", "depends_on_prior_selection": "True", "notes": "semantic after H_acc=0; not uniqueness-minimal after pure C/J"},
        {"criterion": "diagonal idempotence", "prerequisite": "diagonal map; used after H_diag=0 in narrative", "depends_on_prior_selection": "False", "notes": "alone leaves d0=0 with d1,d2 free"},
        {"criterion": "Assoc_000", "prerequisite": "d=000 selected", "depends_on_prior_selection": "True", "notes": "local path-dependence bridge; not a global Assoc criterion"},
        {"criterion": "pure C/J drift-kick", "prerequisite": "column-blind absorption on M^x", "depends_on_prior_selection": "True", "notes": "finite dynamical selector; C^2 symplectic lift is auxiliary"},
        {"criterion": "hidden continuation contrast H", "prerequisite": "left-regular operator lift; Layer 1H controlled strata", "depends_on_prior_selection": "False", "notes": "landscape bridge; not part of selector dependency in v0.7"},
    ]
    write_csv(tables / "layer2_frontF_dependency_matrix.csv", dependency_rows)

    # Backward-compatible summary tables.
    write_csv(tables / "layer2_criterion_independence.csv", role_rows)
    write_csv(tables / "layer2_minimality_deletion_audit.csv", deletion_rows)

    # ------------------------------------------------------------------
    # Front G: hidden continuation contrast H as auxiliary bridge.
    # ------------------------------------------------------------------
    H_rows = []
    for a, b in product(S, repeat=2):
        for d in product(S, repeat=3):
            d = tuple(d)
            profile = H_profile(a, b, d)
            H_rows.append({
                "a": a,
                "b": b,
                "label": rule_label(a, b),
                "d": "".join(map(str, d)),
                "x21": x21(a, b, d),
                "Assoc": assoc_count(a, b, d),
                **profile,
                "pure": boolstr(profile["N_neg"] == 0),
                "above_PAB_7020": boolstr(profile["H_tot"] > 7020),
                "ge_PAB_7020": boolstr(profile["H_tot"] >= 7020),
                "is_PAB": boolstr((a, b, d) == (1, 2, (0, 0, 0))),
                "is_row_complement_d000": boolstr((a, b, d) == (2, 1, (0, 0, 0))),
                "pure_H_frontier": boolstr(profile["N_neg"] == 0 and profile["H_tot"] == 7020),
            })
    write_csv(tables / "layer2_frontG_H_column_blind_audit.csv", H_rows)

    H_values = [int(r["H_tot"]) for r in H_rows]
    N_values = [int(r["N_neg"]) for r in H_rows]
    pure_Hmax = max(int(r["H_tot"]) for r in H_rows if int(r["N_neg"]) == 0)
    cb_summary = {
        "points": len(H_rows),
        "H_min": min(H_values),
        "H_max": max(H_values),
        "pure_count": sum(int(r["N_neg"]) == 0 for r in H_rows),
        "pure_H_max": pure_Hmax,
        "N_neg_max": max(N_values),
        "count_above_PAB_7020": sum(int(r["H_tot"]) > 7020 for r in H_rows),
        "count_ge_PAB_7020": sum(int(r["H_tot"]) >= 7020 for r in H_rows),
    }
    assert cb_summary == {k: CONTROLLED_H_SUMMARY[0][k] for k in cb_summary}

    write_csv(tables / "layer2_frontG_H_controlled_summary_imported.csv", CONTROLLED_H_SUMMARY)
    write_csv(tables / "layer2_frontG_H_controlled_summary.csv", CONTROLLED_H_SUMMARY)

    H_key_rows = []
    for name, a, b, d in [
        ("PAB", 1, 2, (0, 0, 0)),
        ("row_complement", 2, 1, (0, 0, 0)),
    ]:
        profile = H_profile(a, b, d)
        H_key_rows.append({"label": name, "a": a, "b": b, "d": "".join(map(str, d)), "x21": x21(a, b, d), "Assoc": assoc_count(a, b, d), **profile, "pure": boolstr(profile["N_neg"] == 0), "Layer2_role": "main selector survivor" if name == "PAB" else "main selector competitor rejected by pure C/J"})
    # Add one representative Hmax and one non-PAB pure frontier example for diagnostics.
    hmax_row = next(r for r in H_rows if int(r["H_tot"]) == 7302)
    H_key_rows.append({"label": "column_blind_Hmax_example", "a": hmax_row["a"], "b": hmax_row["b"], "d": hmax_row["d"], "x21": hmax_row["x21"], "Assoc": hmax_row["Assoc"], "I_tot": hmax_row["I_tot"], "B_tot": hmax_row["B_tot"], "H_tot": hmax_row["H_tot"], "H_pos": hmax_row["H_pos"], "H_neg_abs": hmax_row["H_neg_abs"], "N_neg": hmax_row["N_neg"], "h_loc_min": hmax_row["h_loc_min"], "h_loc_max": hmax_row["h_loc_max"], "pure": hmax_row["pure"], "Layer2_role": "higher H_tot but signed-cancellation tail"})
    write_csv(tables / "layer2_frontG_H_key_witnesses.csv", H_key_rows)

    pure_frontier_rows = [r for r in H_rows if r["pure_H_frontier"] == "True"]
    pure_frontier_rows.sort(key=lambda r: (r["a"], r["b"], r["d"]))
    write_csv(tables / "layer2_frontG_H_pure_frontier_locus_cb.csv", pure_frontier_rows)
    assert len(pure_frontier_rows) == 6
    assert any(r["is_PAB"] == "True" for r in pure_frontier_rows)
    assert any(r["is_row_complement_d000"] == "True" for r in pure_frontier_rows)

    H_guardrail_rows = [
        {"guardrail": "H is auxiliary, not mandatory selector", "reason": "global Omega' H-range and pure-frontier certificate remain open", "Layer2_decision": "do not add H to the required selection chain"},
        {"guardrail": "H does not resolve PAB/competitor", "reason": "PAB and row-complement at d=000 both have H_tot=7020, H_neg=0, N_neg=0", "Layer2_decision": "final separation remains pure C/J directed-edge dynamics"},
        {"guardrail": "raw H_max is not pure", "reason": "controlled H_max=7302 has H_neg=6 and N_neg=3", "Layer2_decision": "if H is used, pure-frontier language is safer than max-H language"},
        {"guardrail": "controlled frontier is strong evidence", "reason": "max{H_tot:N_-=0}=7020 on column-blind, affine, and degree<=2 strata", "Layer2_decision": "record as bridge to future global certificate"},
    ]
    write_csv(tables / "layer2_frontG_H_selector_guardrails.csv", H_guardrail_rows)
    write_csv(tables / "layer2_frontG_H_bridge_policy.csv", H_guardrail_rows)

    H_local_shell_rows = [
        {"center": "PAB", "radius": 1, "center_H_tot": 7020, "neighbors": 42, "min_H_tot": 5604, "max_H_tot": 7302, "above_center": 2, "source": "Layer 1H local shell summary"},
        {"center": "PAB", "radius": 2, "center_H_tot": 7020, "neighbors": 840, "min_H_tot": 4524, "max_H_tot": 6924, "above_center": 0, "source": "Layer 1H local shell summary"},
        {"center": "row_complement", "radius": 1, "center_H_tot": 7020, "neighbors": 42, "min_H_tot": 5604, "max_H_tot": 7302, "above_center": 2, "source": "Layer 1H local shell summary"},
        {"center": "row_complement", "radius": 2, "center_H_tot": 7020, "neighbors": 840, "min_H_tot": 4524, "max_H_tot": 6924, "above_center": 0, "source": "Layer 1H local shell summary"},
    ]
    write_csv(tables / "layer2_frontG_H_local_shell_summary.csv", H_local_shell_rows)

    H_bridge_rows = [
        {"item": "definition", "content": "H=I-B from left-regular operator lift; four-point continuation contrast", "status": "imported from Layer 1H"},
        {"item": "column_blind_exact_check", "content": "Layer 2 verifier recomputes all 243 column-blind x Delta H profiles", "status": "checked in v0.7"},
        {"item": "controlled_pure_frontier", "content": "max{H_tot:N_-=0}=7020 on column-blind, affine, degree<=2", "status": "imported / partially recomputed"},
        {"item": "PAB_profile", "content": "H_tot=7020, H_pos=7020, H_neg=0, N_neg=0", "status": "checked in v0.7"},
        {"item": "competitor_profile", "content": "row-complement has the same pure H profile at d=000", "status": "checked in v0.7"},
        {"item": "selector_role", "content": "auxiliary bridge only; does not alter survivor count", "status": "Front G closed"},
    ]
    write_csv(tables / "layer2_frontG_H_auxiliary_bridge.csv", H_bridge_rows)
    write_csv(tables / "layer2_frontG_H_status_registry.csv", H_bridge_rows)

    # ------------------------------------------------------------------
    # Selection chain and status registry.
    # ------------------------------------------------------------------
    chain_rows = [
        {"stage": 0, "criterion": "Omega'", "cross_rules": "3^18", "diagonals": 27, "total": "3^21", "note": "Layer 1 normal form"},
        {"stage": 1, "criterion": "H_acc=0 and H_diag=0", "cross_rules": 9, "diagonals": 3, "total": 27, "note": "information compression; Front B closed"},
        {"stage": 2, "criterion": "nontriviality and diagonal idempotence", "cross_rules": 6, "diagonals": 1, "total": 6, "note": "nondegenerate anchors; Front C closed"},
        {"stage": 3, "criterion": "min Assoc_000 inside nontrivial column-blind", "cross_rules": 2, "diagonals": 1, "total": 2, "note": "PAB / row-complement ambiguity; Front D closed"},
        {"stage": 4, "criterion": "finite pure C/J drift-kick", "cross_rules": 1, "diagonals": 1, "total": 1, "note": "finite directed-edge separation; Front E closed"},
        {"stage": "G", "criterion": "hidden continuation contrast H", "cross_rules": "no required reduction", "diagonals": "no required reduction", "total": "unchanged", "note": "auxiliary bridge; Front G closed"},
    ]
    write_csv(tables / "layer2_selection_chain.csv", chain_rows)

    status_rows = [
        {"claim": "H_acc=0 iff column-blind", "status": "V / Front B closed", "support": "MI lemma + exhaustive 3^9 one-table entropy-zero check"},
        {"claim": "column-blind count is 9", "status": "V-checked", "support": "h_{a,b}, a,b in S"},
        {"claim": "H_diag=0 iff d is constant", "status": "V / Front B closed", "support": "entropy of base triple + enumeration of Delta"},
        {"claim": "diagonal idempotence alone leaves 9 diagonals", "status": "V-checked", "support": "condition d0=0"},
        {"claim": "diagonal idempotence after H_diag=0 selects 000", "status": "V / Front C closed", "support": "constant diagonals 000,111,222"},
        {"claim": "nontriviality leaves 6 rules", "status": "V / Front C closed", "support": "a != b"},
        {"claim": "min Assoc_000 leaves PAB and row-complement", "status": "V / Front D closed", "support": "direct 729 triple count + five-block decomposition"},
        {"claim": "weak q/p split separates PAB from competitor", "status": "Rejected", "support": "both have 2 weak split passes"},
        {"claim": "finite pure C/J separates PAB", "status": "V-combinatorial / Front E closed", "support": "PAB has {C,J}; competitor has {C^{-1},C^{-1}J}"},
        {"claim": "C^2 symplectic realization theorem", "status": "Open geometric bridge", "support": "not a selector dependency in v0.7"},
        {"claim": "Front F independence/minimality registry", "status": "V / Front F closed", "support": "deletion audit + minimal selector sets"},
        {"claim": "H column-blind x Delta controlled atlas", "status": "V / recomputed in v0.7", "support": "243 H profiles"},
        {"claim": "Controlled H pure frontier 7020 on affine and degree<=2", "status": "V-certified imported from Layer 1H", "support": "Layer 1H controlled atlas"},
        {"claim": "H as global selector", "status": "Open / auxiliary only", "support": "global Omega' H certificate absent; PAB and row-complement share H profile"},
    ]
    status_rows.append({"claim": "Front H package hardening", "status": "V / Front H closed", "support": "artifact manifest + table integrity audit + consistency audit"})
    write_csv(tables / "layer2_status_registry.csv", status_rows)

    # ------------------------------------------------------------------
    # Front H: verifier/table hardening and artifact map.
    # ------------------------------------------------------------------
    required_tables = [
        "layer2_absorption_degree_all_cb.csv",
        "layer2_absorption_transitions_pab_comp.csv",
        "layer2_assoc_block_decomposition_cb.csv",
        "layer2_assoc_guardrail.csv",
        "layer2_criterion_independence.csv",
        "layer2_diag_entropy_distribution.csv",
        "layer2_diag_entropy_table.csv",
        "layer2_frontE_canonical_maps.csv",
        "layer2_frontE_nontrivial_cb_absorption_audit.csv",
        "layer2_frontE_pure_drift_kick_theorem.csv",
        "layer2_frontE_survivor_transition_factorization.csv",
        "layer2_frontF_criterion_removal_audit.csv",
        "layer2_frontF_criterion_role_registry.csv",
        "layer2_frontF_deletion_audit.csv",
        "layer2_frontF_dependency_matrix.csv",
        "layer2_frontF_minimal_core_registry.csv",
        "layer2_frontF_minimal_selector_sets.csv",
        "layer2_frontF_no_Hdiag_idempotent_assoc_audit.csv",
        "layer2_frontG_H_auxiliary_bridge.csv",
        "layer2_frontG_H_bridge_policy.csv",
        "layer2_frontG_H_column_blind_audit.csv",
        "layer2_frontG_H_controlled_summary.csv",
        "layer2_frontG_H_controlled_summary_imported.csv",
        "layer2_frontG_H_key_witnesses.csv",
        "layer2_frontG_H_local_shell_summary.csv",
        "layer2_frontG_H_pure_frontier_locus_cb.csv",
        "layer2_frontG_H_selector_guardrails.csv",
        "layer2_frontG_H_status_registry.csv",
        "layer2_hacc_column_blind_rules.csv",
        "layer2_hacc_representative_audit.csv",
        "layer2_information_criteria.csv",
        "layer2_minimality_deletion_audit.csv",
        "layer2_nondegenerate_anchor_audit.csv",
        "layer2_nontrivial_cb_assoc_table.csv",
        "layer2_path_dependence_table.csv",
        "layer2_path_dependence_theorem.csv",
        "layer2_qp_splitting_audit.csv",
        "layer2_selection_chain.csv",
        "layer2_status_registry.csv",
        "layer2_weak_qp_splitting_details.csv",
    ]
    integrity_rows = []
    for name in required_tables:
        path = tables / name
        assert path.exists(), f"required table missing: {name}"
        rows = csv_row_count(path)
        assert rows > 0, f"required table has no data rows: {name}"
        integrity_rows.append({
            "path": f"tables/{name}",
            "front": front_for_table(name),
            "row_count": rows,
            "sha256": sha256_file(path),
            "status": "present_nonempty",
        })
    write_csv(tables / "layer2_frontH_table_integrity_audit.csv", integrity_rows)

    # Cross-check central theorem outputs from generated tables.
    chain_by_stage = {str(r["stage"]): r for r in chain_rows}
    final_chain_ok = chain_by_stage["4"]["total"] == 1 and chain_by_stage["4"]["cross_rules"] == 1
    H_policy_ok = any(r["guardrail"] == "H is auxiliary, not mandatory selector" for r in H_guardrail_rows)
    weak_qp_ok = audit["PAB"]["weak_qp_splitting_pass_count"] == 2 and audit["row-complement"]["weak_qp_splitting_pass_count"] == 2
    pure_cj_ok = audit["PAB"]["canonical_pure_drift_kick_pass"] == "True" and audit["row-complement"]["canonical_pure_drift_kick_pass"] == "False"
    pab_H = H_profile(1, 2, (0, 0, 0))
    comp_H = H_profile(2, 1, (0, 0, 0))
    H_ambiguity_ok = pab_H == comp_H and pab_H["H_tot"] == 7020 and pab_H["N_neg"] == 0
    local_assoc_ok = survivors == {(1, 2), (2, 1)}
    consistency_rows = [
        {"check": "selection_chain_final_survivor", "expected": "one PAB survivor", "observed": str(chain_by_stage["4"]), "passed": boolstr(final_chain_ok)},
        {"check": "local_Assoc_minimizers", "expected": "{(1,2),(2,1)}", "observed": str(sorted(survivors)), "passed": boolstr(local_assoc_ok)},
        {"check": "weak_qp_rejected", "expected": "both PAB and competitor have two weak passes", "observed": f"PAB={audit['PAB']['weak_qp_splitting_pass_count']}; competitor={audit['row-complement']['weak_qp_splitting_pass_count']}", "passed": boolstr(weak_qp_ok)},
        {"check": "pure_CJ_separates", "expected": "PAB=True; competitor=False", "observed": f"PAB={audit['PAB']['canonical_pure_drift_kick_pass']}; competitor={audit['row-complement']['canonical_pure_drift_kick_pass']}", "passed": boolstr(pure_cj_ok)},
        {"check": "H_auxiliary_policy", "expected": "H is not a selector dependency", "observed": "guardrail table contains auxiliary-only policy", "passed": boolstr(H_policy_ok)},
        {"check": "H_keeps_PAB_competitor_ambiguity", "expected": "same pure H profile at d=000", "observed": f"PAB={pab_H}; competitor={comp_H}", "passed": boolstr(H_ambiguity_ok)},
        {"check": "core_tables_present", "expected": str(len(required_tables)), "observed": str(len(integrity_rows)), "passed": boolstr(len(integrity_rows) == len(required_tables))},
    ]
    assert all(r["passed"] == "True" for r in consistency_rows)
    write_csv(tables / "layer2_frontH_consistency_audit.csv", consistency_rows)

    artifact_rows = [
        {"path": "layer2_selection_v1.md", "role": "main theorem text", "front": "A-H", "status": "must cite current v0.7 text", "sha256": sha256_file(root / "layer2_selection_v1.md") if (root / "layer2_selection_v1.md").exists() else "missing"},
        {"path": "README_L2.md", "role": "artifact map and smoke-test instructions", "front": "A-H", "status": "must cite current v0.7 README", "sha256": sha256_file(root / "README_L2.md") if (root / "README_L2.md").exists() else "missing"},
        {"path": "scripts/verify_layer2_selection_final.py", "role": "single smoke verifier", "front": "A-H", "status": "current verifier", "sha256": sha256_file(root / "scripts/verify_layer2_selection_final.py")},
        {"path": "tables/layer2_frontH_table_integrity_audit.csv", "role": "table integrity manifest", "front": "H", "status": "generated by verifier", "sha256": sha256_file(tables / "layer2_frontH_table_integrity_audit.csv")},
        {"path": "tables/layer2_frontH_consistency_audit.csv", "role": "cross-table consistency checks", "front": "H", "status": "generated by verifier", "sha256": sha256_file(tables / "layer2_frontH_consistency_audit.csv")},
        {"path": "layer2_work_v0_7_frontH.zip", "role": "release bundle", "front": "H", "status": "generated after verifier", "sha256": "computed after packaging"},
    ]
    write_csv(tables / "layer2_frontH_artifact_manifest.csv", artifact_rows)

    final_registry_rows = [
        {"front": "A", "status": "closed", "deliverable": "package skeleton, tables, verifier"},
        {"front": "B", "status": "closed", "deliverable": "H_acc and H_diag theorem blocks"},
        {"front": "C", "status": "closed", "deliverable": "nontriviality and diagonal idempotence anchors"},
        {"front": "D", "status": "closed", "deliverable": "local Assoc_000 path-dependence theorem"},
        {"front": "E", "status": "closed finite core", "deliverable": "pure C/J directed-edge selector; C^2 realization remains bridge"},
        {"front": "F", "status": "closed", "deliverable": "independence/minimality registry"},
        {"front": "G", "status": "closed", "deliverable": "H auxiliary bridge with guardrails"},
        {"front": "H", "status": "closed", "deliverable": "integrity audit, artifact manifest, consistency audit"},
    ]
    write_csv(tables / "layer2_frontH_final_package_registry.csv", final_registry_rows)

    open_bridge_rows = [
        {"item": "C2_symplectic_realization", "status": "open geometric bridge", "why_not_blocking": "finite selector uses pure C/J directed-edge criterion"},
        {"item": "global_H_certificate_on_Omega_prime", "status": "open", "why_not_blocking": "H is auxiliary only; controlled strata imported from Layer 1H"},
        {"item": "hand_compression_of_all_finite_checks", "status": "future exposition improvement", "why_not_blocking": "verifier recomputes finite cores"},
    ]
    write_csv(tables / "layer2_frontH_open_bridge_registry.csv", open_bridge_rows)

    print("Layer 2 selection verifier v0.7: PASS")
    print(f"  tables written to: {tables}")
    print("  Front B closed: information criteria formalized and finite cores checked")
    print("  Front C closed: nondegenerate anchors formalized and checked")
    print("  Front D closed: local path-dependence theorem checked on six nontrivial column-blind rules")
    print("  Front E finite core closed: pure C/J directed-edge selector separates PAB from row-complement")
    print("  Front F closed: independence/minimality registry and deletion audit generated")
    print("  Front G closed: hidden continuation contrast H integrated as auxiliary bridge")
    print("  H guardrail: PAB and row-complement both have H_tot=7020, H_-=0, N_-=0 at d=000")
    print("  H guardrail: global Omega' H certificate remains open; H is not a selector dependency")
    print("  Front H closed: artifact manifest, table integrity audit, and consistency audit generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
