#!/usr/bin/env python3
"""Compact verifier for the Layer 1 Global Assoc theorem tail reductions.

This script verifies the proof-obligation layer behind the raw range theorem

    21 <= rawAssoc(A,B,d) <= 199,

where Assoc = 3 * rawAssoc.  It is intentionally narrower than the full Z(q)
histogram verifier: it checks only the finite compatibility reductions used in
the Global Assoc theorem proof skeleton.

Default checks:
  1. RRR analytic lemma and diagonal-class classification.
  2. Lower-tail cross-compatibility via one-table candidate reduction:
       RRR=9  -> rawCross >= 12
       RRR=11 -> rawCross >= 10
       RRR=13 -> rawCross >= 12
       RRR=19 -> rawCross >= 12
  3. Upper-tail global exclusion via half-block candidate reduction:
       rawAssoc >= 200 is infeasible.
  4. Upper endpoint check on constant diagonals:
       rawAssoc=199 occurs exactly 6 times, with vector (36,36,54,54).
  5. Optional endpoint-table consistency if Layer 1 v3 tables are present.

Optional heavier check:
  --full-class-upper verifies exact class-level upper cross bounds:
       RRR=9  -> rawCross <= 180
       RRR=11 -> rawCross <= 162
       RRR=13 -> rawCross <= 174
       RRR=19 -> rawCross <= 180
  This enumerates tens of millions of reduced candidates and is therefore not
  part of the default quick proof-obligation check.

The reduction is independent of the full 3^18 x 27 histogram.  It enumerates
all 3^9 one-table A/B assignments, applies necessary one-table/half-block
filters, then checks the resulting candidate pairs exactly under the normalized
master formula block decomposition.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np

S = (0, 1, 2)
N_TABLES = 3 ** 9
BLOCKS = ("RRS", "RSR", "RSS", "RST")

# vals[n, 3*a+e] is the value of the n-th S^9 table at (a,e).
# The enumeration order is irrelevant for the theorem; little-endian base-3 is
# convenient and matches the earlier reduction scripts.
VALS = np.zeros((N_TABLES, 9), dtype=np.int8)
_x = np.arange(N_TABLES, dtype=np.int64)
for _i in range(9):
    VALS[:, _i] = (_x % 3).astype(np.int8)
    _x //= 3
ROWS_ALL = np.arange(N_TABLES, dtype=np.int32)


def idx(a: int, e: int) -> int:
    return 3 * (a % 3) + (e % 3)


def comp(a: int, b: int) -> int:
    return (-a - b) % 3


def dstr_from_tuple(d: Tuple[int, int, int]) -> str:
    return "".join(str(int(x)) for x in d)


def parse_d(ds: str) -> np.ndarray:
    ds = str(ds).zfill(3)
    if len(ds) != 3 or any(ch not in "012" for ch in ds):
        raise ValueError(f"bad diagonal string: {ds!r}")
    return np.array([int(ch) for ch in ds], dtype=np.int8)


def m0_scalar(d: np.ndarray, a: int, e: int) -> int:
    a %= 3
    e %= 3
    return int(d[a]) if a == e else comp(a, e)


def m0_vec_scalar_a(d: np.ndarray, a: int, y: np.ndarray) -> np.ndarray:
    y16 = y.astype(np.int16)
    return np.where(y16 == a, int(d[a]), (-a - y16) % 3).astype(np.int8)


def m0_vec(d: np.ndarray, x: np.ndarray, f: int) -> np.ndarray:
    x16 = x.astype(np.int16)
    return np.where(x16 == f, d[x], (-x16 - f) % 3).astype(np.int8)


def rrr_formula(ds: str) -> int:
    d = [int(ch) for ch in ds.zfill(3)]
    E = sum(1 for i in S for j in S if i != j and d[i] == d[j])
    N = sum(1 for i in S for j in S if i != j and d[i] == j and d[j] == j)
    return 9 + E + 2 * N


def rrr_bruteforce(ds: str) -> int:
    d = parse_d(ds)
    total = 0
    for a, e, f in product(S, repeat=3):
        lhs = m0_scalar(d, m0_scalar(d, a, e), f)
        rhs = m0_scalar(d, a, m0_scalar(d, e, f))
        total += int(lhs == rhs)
    return total


def diagonal_class(ds: str) -> str:
    vals = [int(ch) for ch in ds.zfill(3)]
    p = len(set(vals))
    fixed = sum(1 for i, v in enumerate(vals) if i == v)
    if p == 1:
        return "constant"
    if p == 3:
        return "permutation"
    if fixed == 0:
        return "two_valued_no_fixed"
    return "two_valued_with_fixed"


def lower_target_for_rrr(raw_rrr: int) -> int:
    return {9: 12, 11: 10, 13: 12, 19: 12}[raw_rrr]


def upper_cross_bound_for_rrr(raw_rrr: int) -> int:
    return {9: 180, 11: 162, 13: 174, 19: 180}[raw_rrr]


def one_table_block_scores(ds: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return arrays (RRS, RSS_shift1, RSS_shift2) for all S^9 tables."""
    d = parse_d(ds)
    rrs = np.zeros(N_TABLES, dtype=np.int16)
    rss1 = np.zeros(N_TABLES, dtype=np.int16)
    rss2 = np.zeros(N_TABLES, dtype=np.int16)

    # RRS for one table T: M_T(M0(a,e), f) == M0(a, M_T(e,f)).
    for a, e, f in product(S, repeat=3):
        xy = m0_scalar(d, a, e)
        lhs = VALS[:, idx(xy, f)]
        yz = VALS[:, idx(e, f)]
        rhs = m0_vec_scalar_a(d, a, yz)
        rrs += (lhs == rhs)

    # RSS for b=t=1 and b=t=2 respectively.
    for sh, rss in ((1, rss1), (2, rss2)):
        for a, e, f in product(S, repeat=3):
            xy = VALS[:, idx(a, e)].astype(np.int16)
            lhs = VALS[ROWS_ALL, xy * 3 + f]
            yz = m0_scalar(d, (e - sh) % 3, (f - sh) % 3)
            rhs = VALS[:, idx(a, (sh + yz) % 3)]
            rss += (lhs == rhs)

    return rrs, rss1, rss2


def candidate_pairs_le(FA: np.ndarray, FB: np.ndarray, threshold: int) -> Tuple[np.ndarray, np.ndarray]:
    """All candidate pairs with FA[A] + FB[B] <= threshold."""
    ia_parts: List[np.ndarray] = []
    ib_parts: List[np.ndarray] = []
    for s in np.unique(FA):
        Aidx = np.nonzero(FA == s)[0].astype(np.int32)
        max_b = threshold - int(s)
        if max_b < 0:
            continue
        Bidx = np.nonzero(FB <= max_b)[0].astype(np.int32)
        if Aidx.size and Bidx.size:
            ia_parts.append(np.repeat(Aidx, Bidx.size))
            ib_parts.append(np.tile(Bidx, Aidx.size))
    if not ia_parts:
        return np.array([], dtype=np.int32), np.array([], dtype=np.int32)
    return np.concatenate(ia_parts), np.concatenate(ib_parts)


def candidate_pairs_ge(FA: np.ndarray, FB: np.ndarray, threshold: int) -> Tuple[np.ndarray, np.ndarray]:
    """All candidate pairs with FA[A] + FB[B] >= threshold."""
    ia_parts: List[np.ndarray] = []
    ib_parts: List[np.ndarray] = []
    for s in np.unique(FA):
        Aidx = np.nonzero(FA == s)[0].astype(np.int32)
        need_b = threshold - int(s)
        if need_b <= 0:
            Bidx = np.arange(N_TABLES, dtype=np.int32)
        else:
            Bidx = np.nonzero(FB >= need_b)[0].astype(np.int32)
        if Aidx.size and Bidx.size:
            ia_parts.append(np.repeat(Aidx, Bidx.size))
            ib_parts.append(np.tile(Bidx, Aidx.size))
    if not ia_parts:
        return np.array([], dtype=np.int32), np.array([], dtype=np.int32)
    return np.concatenate(ia_parts), np.concatenate(ib_parts)


def cross_block_counts_for_pairs(
    ds: str,
    ia: np.ndarray,
    ib: np.ndarray,
    rrs: np.ndarray,
    rss1: np.ndarray,
    rss2: np.ndarray,
    chunk: int = 150_000,
) -> Dict[str, np.ndarray]:
    """Exact cross-block counts for selected (A,B) pairs."""
    d = parse_d(ds)
    out = {name: [] for name in BLOCKS}

    for start in range(0, len(ia), chunk):
        stop = min(start + chunk, len(ia))
        ia_sl = ia[start:stop]
        ib_sl = ib[start:stop]
        A = VALS[ia_sl]
        B = VALS[ib_sl]
        m = A.shape[0]
        rows = np.arange(m, dtype=np.int32)

        RRS = (rrs[ia_sl] + rrs[ib_sl]).astype(np.int16)
        RSS = (rss1[ia_sl] + rss2[ib_sl]).astype(np.int16)
        RSR = np.zeros(m, dtype=np.int16)
        RST = np.zeros(m, dtype=np.int16)

        for a, e, f in product(S, repeat=3):
            # RSR_1: b=1,t=0
            xA = A[:, idx(a, e)]
            lhs1 = m0_vec(d, xA, f)
            yz1 = B[:, idx((e - 1) % 3, (f - 1) % 3)].astype(np.int16)
            rhs1 = A[rows, 3 * a + ((1 + yz1) % 3)]
            RSR += (lhs1 == rhs1)

            # RSR_2: b=2,t=0
            xB = B[:, idx(a, e)]
            lhs2 = m0_vec(d, xB, f)
            yz2 = A[:, idx((e - 2) % 3, (f - 2) % 3)].astype(np.int16)
            rhs2 = B[rows, 3 * a + ((2 + yz2) % 3)]
            RSR += (lhs2 == rhs2)

            # RST_12: b=1,t=2
            rowA = A[:, idx(a, e)].astype(np.int16)
            lhs3 = B[rows, rowA * 3 + f]
            inner12 = A[:, idx((e - 1) % 3, (f - 1) % 3)].astype(np.int16)
            rhs3 = A[rows, 3 * a + ((1 + inner12) % 3)]
            RST += (lhs3 == rhs3)

            # RST_21: b=2,t=1
            rowB = B[:, idx(a, e)].astype(np.int16)
            lhs4 = A[rows, rowB * 3 + f]
            inner21 = B[:, idx((e - 2) % 3, (f - 2) % 3)].astype(np.int16)
            rhs4 = B[rows, 3 * a + ((2 + inner21) % 3)]
            RST += (lhs4 == rhs4)

        out["RRS"].append(RRS)
        out["RSR"].append(RSR)
        out["RSS"].append(RSS)
        out["RST"].append(RST)

    return {
        name: (np.concatenate(parts) if parts else np.array([], dtype=np.int16))
        for name, parts in out.items()
    }


def vector_counter(blocks: Dict[str, np.ndarray], mask: np.ndarray) -> Counter:
    if not mask.any():
        return Counter()
    vecs = zip(blocks["RRS"][mask], blocks["RSR"][mask], blocks["RSS"][mask], blocks["RST"][mask])
    return Counter(tuple(int(x) for x in v) for v in vecs)


def all_diagonals() -> List[str]:
    return ["".join(map(str, d)) for d in product(S, repeat=3)]


def expected_lower_equality(ds: str) -> Counter:
    cls = diagonal_class(ds)
    if cls == "constant":
        return Counter({(12, 0, 0, 0): 4})
    if cls == "two_valued_with_fixed" and ds in {"001", "020", "110", "122", "202", "211"}:
        return Counter({(12, 0, 0, 0): 1})
    if cls == "permutation" and ds in {"120", "201"}:
        return Counter({(2, 2, 4, 4): 6})
    if cls == "two_valued_no_fixed" and ds in {"100", "101", "121", "200", "220", "221"}:
        return Counter({(2, 2, 2, 4): 2})
    return Counter()


def check_rrr() -> Dict[str, object]:
    class_rrr = defaultdict(Counter)
    for ds in all_diagonals():
        formula = rrr_formula(ds)
        brute = rrr_bruteforce(ds)
        if formula != brute:
            raise AssertionError((ds, formula, brute))
        class_rrr[diagonal_class(ds)][formula] += 1
    expected = {
        "permutation": Counter({9: 6}),
        "two_valued_no_fixed": Counter({11: 6}),
        "two_valued_with_fixed": Counter({13: 12}),
        "constant": Counter({19: 3}),
    }
    if dict(class_rrr) != expected:
        raise AssertionError({k: dict(v) for k, v in class_rrr.items()})
    return {k: dict(v) for k, v in sorted(class_rrr.items())}


def check_lower_tail(score_cache: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]) -> Dict[str, object]:
    rows = []
    by_class = defaultdict(lambda: Counter())
    total_excl_candidates = 0
    total_target_candidates = 0
    total_target_feasible = 0

    for ds in all_diagonals():
        raw_rrr = rrr_formula(ds)
        cls = diagonal_class(ds)
        target = lower_target_for_rrr(raw_rrr)
        rrs, rss1, rss2 = score_cache[ds]
        FA = rrs + rss1
        FB = rrs + rss2

        # Exclude rawCross <= target-1.
        ia, ib = candidate_pairs_le(FA, FB, target - 1)
        blocks = cross_block_counts_for_pairs(ds, ia, ib, rrs, rss1, rss2)
        cross = blocks["RRS"] + blocks["RSR"] + blocks["RSS"] + blocks["RST"]
        bad = int(np.sum(cross <= target - 1))
        if bad:
            raise AssertionError(f"lower exclusion failed for d={ds}: {bad} pairs with cross <= {target-1}")

        # Check equality rawCross == target and equality block vectors.
        ia2, ib2 = candidate_pairs_le(FA, FB, target)
        blocks2 = cross_block_counts_for_pairs(ds, ia2, ib2, rrs, rss1, rss2)
        cross2 = blocks2["RRS"] + blocks2["RSR"] + blocks2["RSS"] + blocks2["RST"]
        eq_mask = cross2 == target
        got_vecs = vector_counter(blocks2, eq_mask)
        exp_vecs = expected_lower_equality(ds)
        if got_vecs != exp_vecs:
            raise AssertionError(f"lower equality mismatch for d={ds}: got={got_vecs}, expected={exp_vecs}")

        row = {
            "d": ds,
            "class": cls,
            "rawRRR": raw_rrr,
            "target_cross": target,
            "exclusion_candidates": int(len(ia)),
            "exclusion_feasible": bad,
            "target_candidates": int(len(ia2)),
            "target_feasible": int(eq_mask.sum()),
            "target_vectors": dict((str(k), v) for k, v in got_vecs.items()),
        }
        rows.append(row)
        by_class[cls]["exclusion_candidates"] += int(len(ia))
        by_class[cls]["target_candidates"] += int(len(ia2))
        by_class[cls]["target_feasible"] += int(eq_mask.sum())
        total_excl_candidates += int(len(ia))
        total_target_candidates += int(len(ia2))
        total_target_feasible += int(eq_mask.sum())

    # Totals from the reduction report; these catch accidental changes in the prefilter.
    expected_totals = {
        "exclusion_candidates": 123_310,
        "target_candidates": 249_478,
        "target_feasible": 42,
    }
    got_totals = {
        "exclusion_candidates": total_excl_candidates,
        "target_candidates": total_target_candidates,
        "target_feasible": total_target_feasible,
    }
    if got_totals != expected_totals:
        raise AssertionError((got_totals, expected_totals))

    return {"totals": got_totals, "by_class": {k: dict(v) for k, v in sorted(by_class.items())}, "rows": rows}


def check_upper_global_and_endpoint(score_cache: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]) -> Dict[str, object]:
    rows = []
    total_candidates = 0
    total_feasible = 0

    for ds in all_diagonals():
        raw_rrr = rrr_formula(ds)
        cls = diagonal_class(ds)
        cross_ge = 200 - raw_rrr
        # RSR has two 27-term halves and RST has two 27-term halves, hence the
        # unfiltered remainder has maximum 108. If rawCross >= cross_ge, then
        # (RRS_A+RSS_A)+(RRS_B+RSS_B) >= cross_ge - 108.
        pref = cross_ge - 108
        rrs, rss1, rss2 = score_cache[ds]
        FA = rrs + rss1
        FB = rrs + rss2
        ia, ib = candidate_pairs_ge(FA, FB, pref)
        blocks = cross_block_counts_for_pairs(ds, ia, ib, rrs, rss1, rss2)
        cross = blocks["RRS"] + blocks["RSR"] + blocks["RSS"] + blocks["RST"]
        feasible = int(np.sum(cross >= cross_ge))
        if feasible:
            raise AssertionError(f"upper global exclusion failed for d={ds}: {feasible} pairs with cross >= {cross_ge}")
        rows.append({
            "d": ds,
            "class": cls,
            "rawRRR": raw_rrr,
            "cross_ge_for_raw_ge_200": cross_ge,
            "prefilter_threshold": pref,
            "candidate_pairs": int(len(ia)),
            "feasible_pairs": feasible,
            "max_cross_seen": int(cross.max()) if len(cross) else None,
        })
        total_candidates += int(len(ia))
        total_feasible += feasible

    if total_candidates != 514_356 or total_feasible != 0:
        raise AssertionError((total_candidates, total_feasible))

    endpoint_rows = []
    endpoint_total = 0
    endpoint_vec_total = Counter()
    for ds in ("000", "111", "222"):
        rrs, rss1, rss2 = score_cache[ds]
        FA = rrs + rss1
        FB = rrs + rss2
        ia, ib = candidate_pairs_ge(FA, FB, 72)  # 180 - 108
        blocks = cross_block_counts_for_pairs(ds, ia, ib, rrs, rss1, rss2)
        cross = blocks["RRS"] + blocks["RSR"] + blocks["RSS"] + blocks["RST"]
        eq_mask = cross == 180
        ge181 = int(np.sum(cross >= 181))
        vecs = vector_counter(blocks, eq_mask)
        expected_vecs = Counter({(36, 36, 54, 54): 2})
        if int(eq_mask.sum()) != 2 or ge181 != 0 or vecs != expected_vecs:
            raise AssertionError((ds, int(eq_mask.sum()), ge181, vecs))
        endpoint_rows.append({
            "d": ds,
            "candidate_pairs": int(len(ia)),
            "cross_eq_180": int(eq_mask.sum()),
            "cross_ge_181": ge181,
            "vectors": {str(k): v for k, v in vecs.items()},
        })
        endpoint_total += int(eq_mask.sum())
        endpoint_vec_total.update(vecs)

    if endpoint_total != 6 or endpoint_vec_total != Counter({(36, 36, 54, 54): 6}):
        raise AssertionError((endpoint_total, endpoint_vec_total))

    return {
        "global_exclusion": {"candidate_pairs": total_candidates, "feasible_pairs": total_feasible, "rows": rows},
        "constant_endpoint": {"total_points": endpoint_total, "vectors": {str(k): v for k, v in endpoint_vec_total.items()}, "rows": endpoint_rows},
    }


def check_full_class_upper(score_cache: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]) -> Dict[str, object]:
    rows = []
    total_candidates = 0
    for ds in all_diagonals():
        raw_rrr = rrr_formula(ds)
        bound = upper_cross_bound_for_rrr(raw_rrr)
        pref = (bound + 1) - 108
        rrs, rss1, rss2 = score_cache[ds]
        FA = rrs + rss1
        FB = rrs + rss2
        ia, ib = candidate_pairs_ge(FA, FB, pref)
        blocks = cross_block_counts_for_pairs(ds, ia, ib, rrs, rss1, rss2)
        cross = blocks["RRS"] + blocks["RSR"] + blocks["RSS"] + blocks["RST"]
        bad = int(np.sum(cross >= bound + 1))
        if bad:
            raise AssertionError(f"class upper bound failed for d={ds}: {bad} pairs with cross >= {bound+1}")
        rows.append({
            "d": ds,
            "class": diagonal_class(ds),
            "rawRRR": raw_rrr,
            "cross_bound": bound,
            "prefilter_threshold": pref,
            "candidate_pairs": int(len(ia)),
            "feasible_above_bound": bad,
        })
        total_candidates += int(len(ia))
    return {"candidate_pairs": total_candidates, "rows": rows}


def table9(s: str) -> Dict[Tuple[int, int], int]:
    vals = [int(ch) for ch in str(s).strip().zfill(9)]
    if len(vals) != 9:
        raise ValueError(s)
    return {(a, e): vals[3 * a + e] for a in S for e in S}


def M_value(t: int, a: int, e: int, A: Dict[Tuple[int, int], int], B: Dict[Tuple[int, int], int], d: Tuple[int, int, int]) -> int:
    if t == 1:
        return A[(a, e)]
    if t == 2:
        return B[(a, e)]
    return d[a] if a == e else comp(a, e)


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


def raw_blocks_from_strings(Astr: str, Bstr: str, dstr: str) -> Dict[str, int]:
    A = table9(Astr)
    B = table9(Bstr)
    d = tuple(int(ch) for ch in str(dstr).zfill(3))
    counts = Counter()
    for b, t, a, e, f in product(S, repeat=5):
        lhs = M_value(t, M_value(b, a, e, A, B, d), f, A, B, d)
        inner = M_value((t - b) % 3, (e - b) % 3, (f - b) % 3, A, B, d)
        rhs = M_value(b, a, (b + inner) % 3, A, B, d)
        if lhs == rhs:
            counts[block_name(b, t)] += 1
    return {k: counts[k] for k in ("RRR", "RRS", "RSR", "RSS", "RST")}


def maybe_check_endpoint_table(root: Path) -> Dict[str, object] | None:
    sol_path = root / "tables" / "layer1_v3_extremal_loci_solutions.csv"
    if not sol_path.exists():
        return None
    rows = []
    with sol_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 30:
        raise AssertionError(f"expected 30 endpoint rows, got {len(rows)}")
    modes = Counter(r["mode"] for r in rows)
    if modes != Counter({"min": 24, "max": 6}):
        raise AssertionError(modes)
    patterns = defaultdict(Counter)
    for r in rows:
        got = raw_blocks_from_strings(r["A"], r["B"], r["d"])
        raw = sum(got.values())
        if r["mode"] == "min" and raw != 21:
            raise AssertionError((r, got))
        if r["mode"] == "max" and raw != 199:
            raise AssertionError((r, got))
        patterns[r["mode"]][tuple(got[k] for k in ("RRR", "RRS", "RSR", "RSS", "RST"))] += 1
    expected_patterns = {
        "min": Counter({(11, 2, 2, 2, 4): 12, (9, 2, 2, 4, 4): 12}),
        "max": Counter({(19, 36, 36, 54, 54): 6}),
    }
    if dict(patterns) != expected_patterns:
        raise AssertionError(patterns)
    return {"rows": len(rows), "modes": dict(modes), "patterns": {k: {str(pk): v for pk, v in c.items()} for k, c in patterns.items()}}


def write_report(report: Dict[str, object], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Global Assoc theorem tail reductions.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1] if Path(__file__).parent.name == "scripts" else Path.cwd(),
                        help="Layer 1 package root; used only for optional endpoint-table check and default report path.")
    parser.add_argument("--report", type=Path, default=None, help="Optional JSON report path.")
    parser.add_argument("--skip-endpoint-table", action="store_true", help="Do not check tables/layer1_v3_extremal_loci_solutions.csv even if present.")
    parser.add_argument("--full-class-upper", action="store_true", help="Also verify exact class-level upper cross bounds; heavier than default.")
    args = parser.parse_args()

    print("[1/5] Checking RRR formula and diagonal classes...")
    report: Dict[str, object] = {"RRR_classification": check_rrr()}

    print("[2/5] Building one-table block scores for all 27 diagonals...")
    score_cache = {ds: one_table_block_scores(ds) for ds in all_diagonals()}

    print("[3/5] Checking lower-tail candidate reductions...")
    report["lower_tail"] = check_lower_tail(score_cache)

    print("[4/5] Checking upper global exclusion and constant endpoints...")
    report["upper_tail"] = check_upper_global_and_endpoint(score_cache)

    if args.full_class_upper:
        print("[optional] Checking exact class-level upper cross bounds...")
        report["full_class_upper"] = check_full_class_upper(score_cache)

    if not args.skip_endpoint_table:
        print("[5/5] Checking endpoint table consistency if available...")
        endpoint_report = maybe_check_endpoint_table(args.root)
        report["endpoint_table"] = endpoint_report if endpoint_report is not None else "not present"
    else:
        print("[5/5] Endpoint table check skipped.")
        report["endpoint_table"] = "skipped"

    if args.report is None:
        args.report = args.root / "generated" / "global_assoc_tail_reduction_verify_report.json"
    write_report(report, args.report)

    print("PASS: Global Assoc tail-reduction proof obligations verified.")
    print(f"Report: {args.report}")
    print(json.dumps({
        "lower_totals": report["lower_tail"]["totals"],
        "upper_global": report["upper_tail"]["global_exclusion"],
        "upper_endpoint": report["upper_tail"]["constant_endpoint"],
    }, indent=2, sort_keys=True)[:2500])


if __name__ == "__main__":
    main()
