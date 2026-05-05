#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import random
import sys
import time
import types
import zipfile
from collections import Counter
from itertools import combinations, product
from pathlib import Path

S = (0, 1, 2)
BLOCK_ORDER = ("RRR", "RRS", "RSR", "SRR", "DIST")
BLOCK_CONDITIONS = {
    "RRR": "b=0,t=0",
    "RRS": "b=0,t!=0",
    "RSR": "b!=0,t=0",
    "SRR": "b=t!=0",
    "DIST": "b!=0,t!=0,t!=b",
}
METRIC_FIELDS = [
    "rawI", "rawB", "rawH", "I_tot", "B_tot", "H_tot",
    "H_pos", "H_neg_abs", "N_neg", "h_loc_min", "h_loc_max",
    "H_RRR", "H_RRS", "H_RSR", "H_SRR", "H_DIST",
]
RESULT_FIELDS = [
    "stage", "result_id", "kind", "block", "object", "count", "formula",
    "classification", "status", "notes",
]

ENGINE0_PURE_FRONTIER_WITNESSES = (
    "000000000111111111222",
    "000000000222222222111",
    "111111111000000000222",
    "111111111222222222000",
    "222222222000000000111",
    "222222222111111111000",
)
H3_PAB_WORD = "111111111222222222000"
H3_ROW_COMPLEMENT_WORD = "222222222111111111000"
H3_GUARDRAIL_WITNESSES = (
    ("PAB", H3_PAB_WORD),
    ("row_complement", H3_ROW_COMPLEMENT_WORD),
)
H3_EXPECTED_WITNESS_METRICS = {
    "H_tot": 7020,
    "rawH": 1170,
    "N_neg": 0,
    "H_RRR": 756,
    "H_RRS": 1512,
    "H_RSR": 2160,
    "H_SRR": 0,
    "H_DIST": 2592,
}

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = SCRIPT_DIR.parent
DEFAULT_TABLE = SCRIPT_DIR / "stage6_math_results.csv"
OMEGA_PRIME_POINTS = 3**21

H1_FINAL_RUN_DIR = SCRIPT_DIR / "h1" / "raw"
H1_EXPECTED_RANGE = {
    "start_index": 0,
    "end_index": OMEGA_PRIME_POINTS,
    "checked_points": OMEGA_PRIME_POINTS,
    "chunk_size": 5000000,
    "chunks": 2093,
    "upper_target_rawH": 1218,
    "lower_target_rawH": -379,
    "upper_violations": 0,
    "lower_violations": 0,
    "min_rawH": -378,
    "max_rawH": 1217,
    "min_H_tot": -2268,
    "max_H_tot": 7302,
    "min_word": "012120201012120201012",
    "max_word": "000000000111111111220",
    "min_count": 8,
    "max_count": 12,
    "rerun": "sample",
    "rerun_chunks": 8,
}
H1_EXPECTED_MIN_METRICS = {
    "rawI": 1242,
    "rawB": 1620,
    "rawH": -378,
    "H_tot": -2268,
    "N_neg": 432,
    "H_RRR": 0,
    "H_RRS": -648,
    "H_RSR": 0,
    "H_SRR": 0,
    "H_DIST": -1620,
}
H1_EXPECTED_MAX_METRICS = {
    "rawI": 1525,
    "rawB": 308,
    "rawH": 1217,
    "H_tot": 7302,
    "N_neg": 3,
    "H_RRR": 930,
    "H_RRS": 1512,
    "H_RSR": 2268,
    "H_SRR": 0,
    "H_DIST": 2592,
}

H4_FINAL_RUN_DIR = SCRIPT_DIR / "h4" / "raw"
H4_EXPECTED_RANGE = {
    "start_index": 0,
    "end_index": OMEGA_PRIME_POINTS,
    "checked_points": OMEGA_PRIME_POINTS,
    "chunk_size": 5000000,
    "chunks": 2093,
    "pair_min_rawH": 1171,
    "witness_min_rawH": 1217,
    "min_rawH": -378,
    "max_rawH": 1217,
    "min_H_tot": -2268,
    "max_H_tot": 7302,
    "min_word": "012120201012120201012",
    "max_word": "000000000111111111220",
    "min_count": 8,
    "max_count": 12,
    "high_points": 12,
    "high_pure_points": 0,
    "high_impure_points": 12,
    "pair_count": 1,
    "rawH_values": [1217],
    "max_N_neg_values": [3],
    "stored_witnesses": 12,
    "witness_overflow": 0,
    "rerun": "sample",
    "rerun_chunks": 8,
}
H4_EXPECTED_PAIR = {
    "rawH": 1217,
    "H_tot": 7302,
    "N_neg": 3,
    "count": 12,
    "first_index": 265731,
    "first_word": "000000000111111111220",
    "min_H_pos": 7308,
    "max_H_pos": 7308,
    "min_H_neg_abs": 6,
    "max_H_neg_abs": 6,
    "min_h_loc_min": -2,
    "max_h_loc_min": -2,
    "min_h_loc_max": 18,
    "max_h_loc_max": 18,
}
H4_EXPECTED_WITNESSES = (
    "000000000111111111220",
    "000000000111111111221",
    "000000000222222222101",
    "000000000222222222121",
    "111111111000000000220",
    "111111111000000000221",
    "111111111222222222100",
    "111111111222222222200",
    "222222222000000000101",
    "222222222000000000121",
    "222222222111111111100",
    "222222222111111111200",
)


def fail(msg: str) -> None:
    print(f"FAIL {msg}")
    raise SystemExit(1)


def numpy_available() -> bool:
    try:
        import numpy  # type: ignore  # noqa: F401
    except Exception:
        return False
    return True


def bundled_python_executable() -> Path | None:
    candidates = (
        Path(os.environ["STAGE6_PYTHON"]) if os.environ.get("STAGE6_PYTHON") else None,
        Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "python" / "bin" / "python3",
    )
    current = Path(sys.executable).resolve()
    for candidate in candidates:
        if candidate is None or not candidate.is_file():
            continue
        if candidate.resolve() != current:
            return candidate
    return None


def ensure_numpy_or_reexec(needs_numpy: bool) -> None:
    if not needs_numpy or numpy_available():
        return
    bundled = bundled_python_executable()
    if bundled is not None:
        print(f"INFO numpy unavailable under {sys.executable}; re-running with {bundled}", flush=True)
        os.execv(str(bundled), [str(bundled)] + sys.argv)


def comp(a: int, e: int) -> int:
    return (-a - e) % 3


def idx(a: int, e: int) -> int:
    return 3 * (a % 3) + (e % 3)


def family(s: int) -> str:
    return {0: "C", 1: "A", 2: "B"}[s % 3]


def parse_x21(x: str | list[int] | tuple[int, ...]) -> list[int]:
    vals = [int(c) for c in x] if isinstance(x, str) else [int(v) for v in x]
    if len(vals) != 21:
        raise ValueError("x21 length must be 21")
    return [v % 3 for v in vals]


def x21_from_parts(A: list[int], B: list[int], d: list[int]) -> str:
    return "".join(str(int(v) % 3) for v in list(A) + list(B) + list(d))


def mtab(x: str | list[int] | tuple[int, ...]) -> list[int]:
    vals = parse_x21(x)
    M = [0] * 27
    for a, e in product(S, S):
        i = idx(a, e)
        M[i] = vals[18 + a] if a == e else comp(a, e)
        M[9 + i] = vals[i]
        M[18 + i] = vals[9 + i]
    return M


def mv(M: list[int], s: int, a: int, e: int) -> int:
    return M[(s % 3) * 9 + (a % 3) * 3 + (e % 3)]


def block_id(b: int, t: int) -> str:
    if b == 0 and t == 0:
        return "RRR"
    if b == 0:
        return "RRS"
    if t == 0:
        return "RSR"
    if t == b:
        return "SRR"
    return "DIST"


# ---------------------------------------------------------------------------
# S6-RED: signatures and distance formula
# ---------------------------------------------------------------------------


def left_signature(M: list[int], c: int) -> tuple[int, ...]:
    return tuple(mv(M, u, c, ell) for u, ell in product(S, S))


def continuation_signature(M: list[int], s: int, alpha: int, z: int) -> tuple[int, ...]:
    return tuple(
        mv(M, s, alpha, (s + mv(M, u - s, z - s, ell - s)) % 3)
        for u, ell in product(S, S)
    )


def distance(sig1: tuple[int, ...], sig2: tuple[int, ...]) -> int:
    if len(sig1) != len(sig2):
        raise ValueError("signature lengths differ")
    return sum(1 for x, y in zip(sig1, sig2) if x != y)


def signature_banks(M: list[int]) -> tuple[dict[int, tuple[int, ...]], dict[tuple[int, int, int], tuple[int, ...]]]:
    L = {c: left_signature(M, c) for c in S}
    C = {(s, alpha, z): continuation_signature(M, s, alpha, z) for s, alpha, z in product(S, S, S)}
    return L, C


def distance_banks(M: list[int]) -> tuple[dict[tuple[int, int], int], dict[tuple[tuple[int, int, int], tuple[int, int, int]], int]]:
    L, C = signature_banks(M)
    DL = {(c, cp): distance(L[c], L[cp]) for c, cp in product(S, S)}
    triples = list(product(S, S, S))
    DC = {(g, gp): distance(C[g], C[gp]) for g, gp in product(triples, triples)}
    return DL, DC


def local_direct_record(M: list[int], b: int, t: int, a: int, e: int, f: int) -> dict[str, int | str]:
    dI = dB = 0
    xy = mv(M, b, a, e)
    yz = mv(M, t - b, e - b, f - b)
    zR = (b + yz) % 3
    epL = mv(M, t, xy, f)
    epR = mv(M, b, a, zR)
    for u, ell in product(S, S):
        zw = (t + mv(M, u - t, f - t, ell - t)) % 3
        rhs_inner = (b + mv(M, u - b, yz, ell - b)) % 3
        if mv(M, t, xy, zw) != mv(M, b, a, rhs_inner):
            dI += 1
        if mv(M, u, epL, ell) != mv(M, u, epR, ell):
            dB += 1
    return {
        "block": block_id(b, t), "b": b, "t": t, "a": a, "e": e, "f": f,
        "xy": xy, "yz": yz, "zR": zR, "epL": epL, "epR": epR,
        "dI": dI, "dB": dB, "h": 2 * (dI - dB),
    }


def local_reduced_record_with_banks(
    M: list[int],
    DL: dict[tuple[int, int], int],
    DC: dict[tuple[tuple[int, int, int], tuple[int, int, int]], int],
    b: int, t: int, a: int, e: int, f: int,
) -> dict[str, int | str]:
    xy = mv(M, b, a, e)
    yz = mv(M, t - b, e - b, f - b)
    zR = (b + yz) % 3
    epL = mv(M, t, xy, f)
    epR = mv(M, b, a, zR)
    dI = DC[((t % 3, xy % 3, f % 3), (b % 3, a % 3, zR))]
    dB = DL[(epL, epR)]
    return {
        "block": block_id(b, t), "b": b, "t": t, "a": a, "e": e, "f": f,
        "xy": xy, "yz": yz, "zR": zR, "epL": epL, "epR": epR,
        "dI": dI, "dB": dB, "h": 2 * (dI - dB),
    }


def local_reduced_records(x: str) -> list[dict[str, int | str]]:
    M = mtab(x)
    DL, DC = distance_banks(M)
    return [
        local_reduced_record_with_banks(M, DL, DC, b, t, a, e, f)
        for b, t, a, e, f in product(S, S, S, S, S)
    ]


# ---------------------------------------------------------------------------
# S6-CERT-IF: engine-neutral one-hot certificate interface
# ---------------------------------------------------------------------------


def onehot(v: int) -> tuple[int, int, int]:
    v %= 3
    return tuple(1 if r == v else 0 for r in S)  # type: ignore[return-value]


def assert_onehot(bits: tuple[int, int, int], label: str) -> None:
    if len(bits) != 3 or sum(bits) != 1 or any(b not in (0, 1) for b in bits):
        fail(f"{label} is not one-hot: {bits}")


def onehot_value(bits: tuple[int, int, int]) -> int:
    assert_onehot(bits, "onehot_value")
    return next(i for i, b in enumerate(bits) if b)


def onehot_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return 0 if onehot_value(a) == onehot_value(b) else 1


def shift_onehot(bits: tuple[int, int, int], k: int) -> tuple[int, int, int]:
    # Output is one-hot for input value + k mod 3.
    return tuple(bits[(r - k) % 3] for r in S)  # type: ignore[return-value]


def read_with_left_onehot(Y: dict[tuple[int, int, int], tuple[int, int, int]], s: int, left: tuple[int, int, int], right_const: int) -> tuple[int, int, int]:
    out = [0, 0, 0]
    for x in S:
        if left[x]:
            y = Y[(s % 3, x, right_const % 3)]
            out = [out[r] + y[r] for r in S]
    ans = tuple(out)  # type: ignore[assignment]
    assert_onehot(ans, "read_with_left_onehot")
    return ans


def read_with_right_onehot(Y: dict[tuple[int, int, int], tuple[int, int, int]], s: int, left_const: int, right: tuple[int, int, int]) -> tuple[int, int, int]:
    out = [0, 0, 0]
    for yv in S:
        if right[yv]:
            z = Y[(s % 3, left_const % 3, yv)]
            out = [out[r] + z[r] for r in S]
    ans = tuple(out)  # type: ignore[assignment]
    assert_onehot(ans, "read_with_right_onehot")
    return ans


def certificate_interface_banks(x: str) -> tuple[
    dict[tuple[int, int, int], tuple[int, int, int]],
    dict[tuple[int, int, int], tuple[int, int, int]],
    dict[tuple[int, int, int, int, int], tuple[int, int, int]],
    dict[tuple[int, int], int],
    dict[tuple[int, int, int, int, int, int], int],
]:
    M = mtab(x)
    # mu/R bank: one-hot output of every constant table read M_s(a,e).
    Y = {(s, a, e): onehot(mv(M, s, a, e)) for s, a, e in product(S, S, S)}

    L = {(c, u, ell): Y[(u, c, ell)] for c, u, ell in product(S, S, S)}

    C: dict[tuple[int, int, int, int, int], tuple[int, int, int]] = {}
    for s, alpha, z, u, ell in product(S, S, S, S, S):
        inner = Y[((u - s) % 3, (z - s) % 3, (ell - s) % 3)]
        shifted = shift_onehot(inner, s)
        C[(s, alpha, z, u, ell)] = read_with_right_onehot(Y, s, alpha, shifted)

    DL: dict[tuple[int, int], int] = {}
    for c, cp in product(S, S):
        DL[(c, cp)] = sum(onehot_distance(L[(c, u, ell)], L[(cp, u, ell)]) for u, ell in product(S, S))

    DC: dict[tuple[int, int, int, int, int, int], int] = {}
    for s, alpha, z, sp, alphap, zp in product(S, S, S, S, S, S):
        DC[(s, alpha, z, sp, alphap, zp)] = sum(
            onehot_distance(C[(s, alpha, z, u, ell)], C[(sp, alphap, zp, u, ell)])
            for u, ell in product(S, S)
        )
    return Y, L, C, DL, DC


def local_certificate_interface_records(x: str) -> list[dict[str, int | str]]:
    Y, _L, _C, DL, DC = certificate_interface_banks(x)
    rows: list[dict[str, int | str]] = []
    for b, t, a, e, f in product(S, S, S, S, S):
        xy_oh = Y[(b % 3, a % 3, e % 3)]
        yz_oh = Y[((t - b) % 3, (e - b) % 3, (f - b) % 3)]
        zR_oh = shift_onehot(yz_oh, b)
        epL_oh = read_with_left_onehot(Y, t, xy_oh, f)
        epR_oh = read_with_right_onehot(Y, b, a, zR_oh)
        dI = sum(
            xy_oh[xy] * zR_oh[zR] * DC[(t % 3, xy, f % 3, b % 3, a % 3, zR)]
            for xy, zR in product(S, S)
        )
        dB = sum(
            epL_oh[epL] * epR_oh[epR] * DL[(epL, epR)]
            for epL, epR in product(S, S)
        )
        xy = onehot_value(xy_oh)
        yz = onehot_value(yz_oh)
        zR = onehot_value(zR_oh)
        epL = onehot_value(epL_oh)
        epR = onehot_value(epR_oh)
        rows.append({
            "block": block_id(b, t), "b": b, "t": t, "a": a, "e": e, "f": f,
            "xy": xy, "yz": yz, "zR": zR, "epL": epL, "epR": epR,
            "dI": dI, "dB": dB, "h": 2 * (dI - dB),
        })
    return rows



# ---------------------------------------------------------------------------
# S6-CERT-ENGINE-1: sound partial-domain interval engine
# ---------------------------------------------------------------------------

BIT = (1, 2, 4)
ALL_MASK = 7
Q_LIST = list(product(S, S, S, S, S))
PAIR_LIST = list(product(S, S))
TRIPLE_LIST = list(product(S, S, S))
DIAG_FIRST_VAR_ORDER = (18, 19, 20) + tuple(range(18))


def mask_values(mask: int) -> list[int]:
    return [i for i in S if mask & BIT[i]]


def mask_from_values(vals) -> int:
    out = 0
    for v in vals:
        out |= BIT[int(v) % 3]
    return out


def shift_mask(mask: int, k: int) -> int:
    k %= 3
    if k == 0:
        return mask & ALL_MASK
    if k == 1:
        return (((mask << 1) & ALL_MASK) | ((mask >> 2) & 1)) & ALL_MASK
    return (((mask << 2) & ALL_MASK) | ((mask >> 1) & 3)) & ALL_MASK


def singleton_mask_value(mask: int) -> int:
    vals = mask_values(mask)
    if len(vals) != 1:
        raise ValueError(f"mask is not singleton: {mask}")
    return vals[0]


def domain_from_x21(x: str | list[int] | tuple[int, ...]) -> tuple[int, ...]:
    return tuple(BIT[v] for v in parse_x21(x))


def root_domain() -> tuple[int, ...]:
    return (ALL_MASK,) * 21


def domain_is_full(dom: tuple[int, ...]) -> bool:
    return all(int(m).bit_count() == 1 for m in dom)


def x21_from_domain(dom: tuple[int, ...]) -> str:
    if not domain_is_full(dom):
        raise ValueError("domain is not a full assignment")
    return "".join(str(singleton_mask_value(int(m))) for m in dom)


def restrict_domain(dom: tuple[int, ...], index: int, value: int) -> tuple[int, ...]:
    out = list(dom)
    out[index] = BIT[value % 3]
    return tuple(out)


def domain_cell(dom: tuple[int, ...], s: int, a: int, e: int) -> int:
    s %= 3
    a %= 3
    e %= 3
    if s == 1:
        return int(dom[3 * a + e])
    if s == 2:
        return int(dom[9 + 3 * a + e])
    if a == e:
        return int(dom[18 + a])
    return BIT[comp(a, e)]


def mask_mismatch_interval(mask1: int, mask2: int) -> tuple[int, int]:
    lower = 1 if (mask1 & mask2) == 0 else 0
    upper = 0 if int(mask1).bit_count() == 1 and mask1 == mask2 else 1
    return lower, upper


class DomainIntervalContext:
    """Precomputed interval data for one partial normal-form domain."""

    def __init__(self, dom: tuple[int, ...]):
        if len(dom) != 21:
            raise ValueError("domain must have 21 ternary masks")
        self.dom = tuple(int(m) & ALL_MASK for m in dom)
        if any(m == 0 for m in self.dom):
            raise ValueError("empty coordinate domain")
        self.cell = {(s, a, e): domain_cell(self.dom, s, a, e) for s, a, e in product(S, S, S)}

        L = {(c, u, ell): self.cell[(u, c, ell)] for c, u, ell in product(S, S, S)}
        C: dict[tuple[int, int, int, int, int], int] = {}
        for s, alpha, z, u, ell in product(S, S, S, S, S):
            inner = self.cell[((u - s) % 3, (z - s) % 3, (ell - s) % 3)]
            C[(s, alpha, z, u, ell)] = self.read(s, BIT[alpha], shift_mask(inner, s))

        self.DL_interval: dict[tuple[int, int], tuple[int, int]] = {}
        for c, cp in PAIR_LIST:
            lower = upper = 0
            for u, ell in PAIR_LIST:
                lo, hi = mask_mismatch_interval(L[(c, u, ell)], L[(cp, u, ell)])
                lower += lo
                upper += hi
            self.DL_interval[(c, cp)] = (lower, upper)

        self.DC_interval: dict[tuple[tuple[int, int, int], tuple[int, int, int]], tuple[int, int]] = {}
        for g in TRIPLE_LIST:
            s, alpha, z = g
            for gp in TRIPLE_LIST:
                sp, alphap, zp = gp
                lower = upper = 0
                for u, ell in PAIR_LIST:
                    lo, hi = mask_mismatch_interval(C[(s, alpha, z, u, ell)], C[(sp, alphap, zp, u, ell)])
                    lower += lo
                    upper += hi
                self.DC_interval[(g, gp)] = (lower, upper)

    def read(self, s: int, left_mask: int, right_mask: int) -> int:
        out = 0
        for x in mask_values(left_mask):
            for y in mask_values(right_mask):
                out |= self.cell[(s % 3, x, y)]
        return out


def local_domain_interval(ctx: DomainIntervalContext, b: int, t: int, a: int, e: int, f: int) -> dict[str, int | bool | str]:
    xy = ctx.cell[(b % 3, a % 3, e % 3)]
    yz = ctx.cell[((t - b) % 3, (e - b) % 3, (f - b) % 3)]
    zR = shift_mask(yz, b)
    epL = ctx.read(t, xy, BIT[f % 3])
    epR = ctx.read(b, BIT[a % 3], zR)

    dI_min, dI_max = 99, -1
    for r in mask_values(xy):
        for z in mask_values(zR):
            lo, hi = ctx.DC_interval[((t % 3, r, f % 3), (b % 3, a % 3, z))]
            dI_min = min(dI_min, lo)
            dI_max = max(dI_max, hi)

    dB_min, dB_max = 99, -1
    for r in mask_values(epL):
        for s in mask_values(epR):
            lo, hi = ctx.DL_interval[(r, s)]
            dB_min = min(dB_min, lo)
            dB_max = max(dB_max, hi)

    h_min = 2 * (dI_min - dB_max)
    h_max = 2 * (dI_max - dB_min)
    impossible = dI_max < dB_min
    forced = dI_min >= dB_max
    return {
        "block": block_id(b, t), "b": b, "t": t, "a": a, "e": e, "f": f,
        "xy_mask": xy, "yz_mask": yz, "zR_mask": zR, "epL_mask": epL, "epR_mask": epR,
        "dI_min": dI_min, "dI_max": dI_max, "dB_min": dB_min, "dB_max": dB_max,
        "h_min": h_min, "h_max": h_max,
        "pure_impossible": impossible, "pure_forced": forced,
    }


def partial_node_bounds(dom: tuple[int, ...]) -> dict[str, int]:
    ctx = DomainIntervalContext(dom)
    h_lower = h_upper = 0
    local_impossible = local_forced = 0
    block_lower = {b: 0 for b in BLOCK_ORDER}
    block_upper = {b: 0 for b in BLOCK_ORDER}
    for q in Q_LIST:
        rec = local_domain_interval(ctx, *q)
        h_min = int(rec["h_min"])
        h_max = int(rec["h_max"])
        block = str(rec["block"])
        h_lower += h_min
        h_upper += h_max
        block_lower[block] += h_min
        block_upper[block] += h_max
        local_impossible += 1 if bool(rec["pure_impossible"]) else 0
        local_forced += 1 if bool(rec["pure_forced"]) else 0
    ans = {
        "H_lower": 3 * h_lower,
        "H_upper": 3 * h_upper,
        "local_impossible": local_impossible,
        "local_forced": local_forced,
        "local_unresolved": 243 - local_forced,
    }
    for block in BLOCK_ORDER:
        ans[f"H_{block}_lower"] = 3 * block_lower[block]
        ans[f"H_{block}_upper"] = 3 * block_upper[block]
    return ans


def iter_domain_completions(dom: tuple[int, ...]):
    free = [(i, mask_values(int(m))) for i, m in enumerate(dom) if int(m).bit_count() > 1]
    fixed = [singleton_mask_value(int(m)) if int(m).bit_count() == 1 else None for m in dom]
    for vals in product(*[v for _, v in free]):
        cur = list(fixed)
        for (i, _choices), val in zip(free, vals):
            cur[i] = val
        yield "".join(str(int(v)) for v in cur)


def column_blind_stage6_points() -> list[str]:
    return [column_blind_x21(a, b, d) for a, b in product(S, S) for d in product(S, S, S)]


def radius_one_points(x: str) -> list[str]:
    x = "".join(str(v) for v in parse_x21(x))
    out = [x]
    for i, ch in enumerate(x):
        for val in "012":
            if val != ch:
                out.append(x[:i] + val + x[i + 1:])
    return out


def exact_metric_summary(xs: list[str]) -> dict[str, int | str]:
    metrics = [(x, h_metrics_reduced(x)) for x in xs]
    pure = [(x, m) for x, m in metrics if int(m["N_neg"]) == 0]
    if not metrics:
        raise ValueError("empty metric summary")
    H_min = min(int(m["H_tot"]) for _, m in metrics)
    H_max = max(int(m["H_tot"]) for _, m in metrics)
    pure_max = max((int(m["H_tot"]) for _, m in pure), default=-10**9)
    pure_frontier_count = sum(1 for _, m in pure if int(m["H_tot"]) == pure_max)
    all_max_N_neg_values = sorted({int(m["N_neg"]) for _, m in metrics if int(m["H_tot"]) == H_max})
    return {
        "points": len(xs),
        "H_min": H_min,
        "H_max": H_max,
        "pure_count": len(pure),
        "pure_max": pure_max,
        "pure_frontier_count": pure_frontier_count,
        "all_max_count": sum(1 for _, m in metrics if int(m["H_tot"]) == H_max),
        "all_max_N_neg_values": "/".join(str(v) for v in all_max_N_neg_values),
    }


def engine1_reference_summaries() -> dict[str, dict[str, int | str]]:
    pab = "111111111222222222000"
    comp_x = "222222222111111111000"
    return {
        "root": partial_node_bounds(root_domain()),
        "PAB_leaf": partial_node_bounds(domain_from_x21(pab)),
        "row_complement_leaf": partial_node_bounds(domain_from_x21(comp_x)),
        "column_blind_x_Delta": exact_metric_summary(column_blind_stage6_points()),
        "radius1_PAB": exact_metric_summary(radius_one_points(pab)),
        "radius1_row_complement": exact_metric_summary(radius_one_points(comp_x)),
    }


def deterministic_partial_domains() -> list[tuple[str, tuple[int, ...]]]:
    bases = [
        ("PAB_diag_free", "111111111222222222000", (18, 19, 20)),
        ("PAB_cross_pair_free", "111111111222222222000", (0, 2, 9, 10)),
        ("comp_diag_free", "222222222111111111000", (18, 19, 20)),
        ("zero_mixed_free", "000000000000000000000", (0, 9, 18, 20)),
        ("sample1_mixed_free", deterministic_samples(1)[0], (1, 7, 13, 19)),
        ("sample2_mixed_free", deterministic_samples(2)[1], (2, 5, 11, 17)),
    ]
    out = []
    for label, x, free_indices in bases:
        dom = list(domain_from_x21(x))
        for i in free_indices:
            dom[i] = ALL_MASK
        out.append((label, tuple(dom)))
    return out


# ---------------------------------------------------------------------------
# S6-BRANCH-0: first branch/frontier scout
# ---------------------------------------------------------------------------

BRANCH0_MAX_DEPTH = 4
BRANCH0_SHELL_RADIUS = 2
BRANCH0_SHELL_POINTS_PER_CENTER = sum(__import__("math").comb(21, k) * (2 ** k) for k in range(BRANCH0_SHELL_RADIUS + 1))
BRANCH0_SHELL_TOTAL_POINTS = BRANCH0_SHELL_POINTS_PER_CENTER * len(ENGINE0_PURE_FRONTIER_WITNESSES)


def hamming_ball_points(center: str, radius: int):
    """Return all x21 words in the Hamming ball of the requested radius."""
    np = require_numpy()
    arr = np.array(parse_x21(center), dtype=np.int8)
    rows = []
    for k in range(radius + 1):
        for inds in combinations(range(21), k):
            choices = [[v for v in S if v != int(arr[i])] for i in inds]
            for vals in product(*choices):
                cur = arr.copy()
                for i, val in zip(inds, vals):
                    cur[i] = val
                rows.append(cur)
    return np.stack(rows, axis=0)


def branch0_frontier_shell_summary(radius: int = BRANCH0_SHELL_RADIUS) -> dict[str, int | str]:
    """Exact shell audit around the six controlled pure-frontier witnesses.

    The calculation is streamed center-by-center to avoid creating a large
    global batch. The six centers are pairwise far enough that the current
    radius-two balls are disjoint; the verifier checks this by counting distinct
    x21 words.
    """
    np = require_numpy()
    per_center = []
    words_seen: set[str] = set()
    H_min = 10**9
    H_max = -10**9
    pure_count = 0
    pure_max = -10**9
    pure_frontier_count = 0
    pure_gt_7020_count = 0
    H_eq_7302_N_neg_values: set[int] = set()
    points = 0

    for center in ENGINE0_PURE_FRONTIER_WITNESSES:
        Xc = hamming_ball_points(center, radius)
        points += int(Xc.shape[0])
        words_seen.update("".join(str(int(v)) for v in row) for row in Xc)
        m = engine0_metrics_batch(Xc)
        H = m["H_tot"]
        N = m["N_neg"]
        pure = N == 0
        center_pure_max = int(H[pure].max()) if bool(np.any(pure)) else -10**9
        center_pure_frontier_count = int(np.sum((H == center_pure_max) & pure)) if center_pure_max > -10**9 else 0
        center_pure_gt = int(np.sum((H > 7020) & pure))
        center_N_values = tuple(sorted({int(x) for x in N[H == 7302]}))
        per_center.append({
            "center": center,
            "points": int(Xc.shape[0]),
            "H_min": int(H.min()),
            "H_max": int(H.max()),
            "pure_count": int(np.sum(pure)),
            "pure_max": center_pure_max,
            "pure_frontier_count": center_pure_frontier_count,
            "pure_gt_7020_count": center_pure_gt,
            "H_eq_7302_N_neg_values": center_N_values,
        })
        H_min = min(H_min, int(H.min()))
        H_max = max(H_max, int(H.max()))
        pure_count += int(np.sum(pure))
        if center_pure_max > pure_max:
            pure_max = center_pure_max
            pure_frontier_count = center_pure_frontier_count
        elif center_pure_max == pure_max:
            pure_frontier_count += center_pure_frontier_count
        pure_gt_7020_count += center_pure_gt
        H_eq_7302_N_neg_values |= set(center_N_values)

    return {
        "radius": radius,
        "centers": len(ENGINE0_PURE_FRONTIER_WITNESSES),
        "points_per_center": int(per_center[0]["points"]),
        "points": points,
        "distinct_points": len(words_seen),
        "H_min": H_min,
        "H_max": H_max,
        "pure_count": pure_count,
        "pure_max": pure_max,
        "pure_frontier_count": pure_frontier_count,
        "pure_gt_7020_count": pure_gt_7020_count,
        "H_eq_7302_N_neg_values": "/".join(str(x) for x in sorted(H_eq_7302_N_neg_values)),
        "per_center_points": "/".join(str(r["points"]) for r in per_center),
        "per_center_pure_count": "/".join(str(r["pure_count"]) for r in per_center),
        "per_center_pure_frontier_count": "/".join(str(r["pure_frontier_count"]) for r in per_center),
    }


def branch0_interval_depth_scout(max_depth: int = BRANCH0_MAX_DEPTH) -> list[dict[str, int]]:
    """Census of the current interval-pruning power in diagonal-first order."""
    rows: list[dict[str, int]] = []
    nodes = [root_domain()]
    for depth in range(0, max_depth + 1):
        imp = ub = prunable = 0
        H_lower_min = 10**9
        H_lower_max = -10**9
        H_upper_min = 10**9
        H_upper_max = -10**9
        forced_min = 10**9
        forced_max = -10**9
        for dom in nodes:
            b = partial_node_bounds(dom)
            imp_flag = int(b["local_impossible"] > 0)
            ub_flag = int(b["H_upper"] <= 7020)
            imp += imp_flag
            ub += ub_flag
            prunable += int(bool(imp_flag or ub_flag))
            H_lower_min = min(H_lower_min, int(b["H_lower"]))
            H_lower_max = max(H_lower_max, int(b["H_lower"]))
            H_upper_min = min(H_upper_min, int(b["H_upper"]))
            H_upper_max = max(H_upper_max, int(b["H_upper"]))
            forced_min = min(forced_min, int(b["local_forced"]))
            forced_max = max(forced_max, int(b["local_forced"]))
        rows.append({
            "depth": depth,
            "nodes": len(nodes),
            "pure_impossible_nodes": imp,
            "upper_pruned_nodes": ub,
            "prunable_nodes": prunable,
            "H_lower_min": H_lower_min,
            "H_lower_max": H_lower_max,
            "H_upper_min": H_upper_min,
            "H_upper_max": H_upper_max,
            "forced_min": forced_min,
            "forced_max": forced_max,
        })
        if depth < max_depth:
            idx = DIAG_FIRST_VAR_ORDER[depth]
            nxt = []
            for dom in nodes:
                for val in mask_values(dom[idx]):
                    nxt.append(restrict_domain(dom, idx, val))
            nodes = nxt
    return rows


def branch0_expected_interval_scout() -> list[dict[str, int]]:
    return [
        {"depth": 0, "nodes": 1, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -13050, "H_lower_max": -13050, "H_upper_min": 13086, "H_upper_max": 13086, "forced_min": 0, "forced_max": 0},
        {"depth": 1, "nodes": 3, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -12972, "H_lower_max": -12918, "H_upper_min": 13020, "H_upper_max": 13044, "forced_min": 0, "forced_max": 0},
        {"depth": 2, "nodes": 9, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -12834, "H_lower_max": -12678, "H_upper_min": 12870, "H_upper_max": 13002, "forced_min": 0, "forced_max": 0},
        {"depth": 3, "nodes": 27, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -12636, "H_lower_max": -11160, "H_upper_min": 12636, "H_upper_max": 12816, "forced_min": 0, "forced_max": 0},
        {"depth": 4, "nodes": 81, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -12606, "H_lower_max": -11028, "H_upper_min": 12612, "H_upper_max": 12810, "forced_min": 0, "forced_max": 0},
    ]


# ---------------------------------------------------------------------------
# S6-BRANCH-1: deeper interval scout and order diagnostic
# ---------------------------------------------------------------------------

BRANCH1_MAX_DEPTH = 8
BRANCH1_INTERLEAVE_AB_ORDER = tuple(i for pair in zip(range(9), range(9, 18)) for i in pair) + tuple(range(18, 21))
BRANCH1_ORDER_NAMES = ("diag_first", "interleave_AB_diag_last")


def branch1_order(order_name: str) -> tuple[int, ...]:
    if order_name == "diag_first":
        return DIAG_FIRST_VAR_ORDER
    if order_name == "interleave_AB_diag_last":
        return BRANCH1_INTERLEAVE_AB_ORDER
    raise ValueError(f"unknown S6-BRANCH-1 order: {order_name}")


def fixed_order_interval_depth_scout(order: tuple[int, ...], max_depth: int) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    nodes = [root_domain()]
    for depth in range(max_depth + 1):
        imp = ub = prunable = 0
        H_lower_min = 10**9
        H_lower_max = -10**9
        H_upper_min = 10**9
        H_upper_max = -10**9
        forced_min = 10**9
        forced_max = -10**9
        for dom in nodes:
            b = partial_node_bounds(dom)
            imp_flag = int(b["local_impossible"] > 0)
            ub_flag = int(b["H_upper"] <= 7020)
            imp += imp_flag
            ub += ub_flag
            prunable += int(bool(imp_flag or ub_flag))
            H_lower_min = min(H_lower_min, int(b["H_lower"]))
            H_lower_max = max(H_lower_max, int(b["H_lower"]))
            H_upper_min = min(H_upper_min, int(b["H_upper"]))
            H_upper_max = max(H_upper_max, int(b["H_upper"]))
            forced_min = min(forced_min, int(b["local_forced"]))
            forced_max = max(forced_max, int(b["local_forced"]))
        rows.append({
            "depth": depth,
            "nodes": len(nodes),
            "pure_impossible_nodes": imp,
            "upper_pruned_nodes": ub,
            "prunable_nodes": prunable,
            "H_lower_min": H_lower_min,
            "H_lower_max": H_lower_max,
            "H_upper_min": H_upper_min,
            "H_upper_max": H_upper_max,
            "forced_min": forced_min,
            "forced_max": forced_max,
        })
        if depth < max_depth:
            idx = order[depth]
            nodes = [
                restrict_domain(dom, idx, val)
                for dom in nodes
                for val in mask_values(dom[idx])
            ]
    return rows


def branch1_interval_depth_scout(order_name: str, max_depth: int = BRANCH1_MAX_DEPTH) -> list[dict[str, int]]:
    """Deeper interval-pruning census for a fixed coordinate order."""
    return fixed_order_interval_depth_scout(branch1_order(order_name), max_depth)


def branch1_expected_interval_scout(order_name: str) -> list[dict[str, int]]:
    if order_name == "diag_first":
        return [
            {"depth": 0, "nodes": 1, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -13050, "H_lower_max": -13050, "H_upper_min": 13086, "H_upper_max": 13086, "forced_min": 0, "forced_max": 0},
            {"depth": 1, "nodes": 3, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -12972, "H_lower_max": -12918, "H_upper_min": 13020, "H_upper_max": 13044, "forced_min": 0, "forced_max": 0},
            {"depth": 2, "nodes": 9, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -12834, "H_lower_max": -12678, "H_upper_min": 12870, "H_upper_max": 13002, "forced_min": 0, "forced_max": 0},
            {"depth": 3, "nodes": 27, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -12636, "H_lower_max": -11160, "H_upper_min": 12636, "H_upper_max": 12816, "forced_min": 0, "forced_max": 0},
            {"depth": 4, "nodes": 81, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -12606, "H_lower_max": -11028, "H_upper_min": 12612, "H_upper_max": 12810, "forced_min": 0, "forced_max": 0},
            {"depth": 5, "nodes": 243, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -12576, "H_lower_max": -10824, "H_upper_min": 12540, "H_upper_max": 12798, "forced_min": 0, "forced_max": 1},
            {"depth": 6, "nodes": 729, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -12444, "H_lower_max": -10098, "H_upper_min": 11808, "H_upper_max": 12762, "forced_min": 0, "forced_max": 24},
            {"depth": 7, "nodes": 2187, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -12372, "H_lower_max": -9792, "H_upper_min": 11682, "H_upper_max": 12708, "forced_min": 0, "forced_max": 27},
            {"depth": 8, "nodes": 6561, "pure_impossible_nodes": 81, "upper_pruned_nodes": 0, "prunable_nodes": 81, "H_lower_min": -12228, "H_lower_max": -9234, "H_upper_min": 11460, "H_upper_max": 12666, "forced_min": 0, "forced_max": 28},
        ]
    if order_name == "interleave_AB_diag_last":
        return [
            {"depth": 0, "nodes": 1, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -13050, "H_lower_max": -13050, "H_upper_min": 13086, "H_upper_max": 13086, "forced_min": 0, "forced_max": 0},
            {"depth": 1, "nodes": 3, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -13038, "H_lower_max": -13038, "H_upper_min": 13086, "H_upper_max": 13086, "forced_min": 0, "forced_max": 0},
            {"depth": 2, "nodes": 9, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -13026, "H_lower_max": -13026, "H_upper_min": 13086, "H_upper_max": 13086, "forced_min": 0, "forced_max": 0},
            {"depth": 3, "nodes": 27, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -13014, "H_lower_max": -12984, "H_upper_min": 13068, "H_upper_max": 13086, "forced_min": 0, "forced_max": 0},
            {"depth": 4, "nodes": 81, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -13002, "H_lower_max": -12942, "H_upper_min": 13050, "H_upper_max": 13086, "forced_min": 0, "forced_max": 0},
            {"depth": 5, "nodes": 243, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -12978, "H_lower_max": -12252, "H_upper_min": 12456, "H_upper_max": 13074, "forced_min": 0, "forced_max": 0},
            {"depth": 6, "nodes": 729, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -12942, "H_lower_max": -11034, "H_upper_min": 11070, "H_upper_max": 13050, "forced_min": 0, "forced_max": 9},
            {"depth": 7, "nodes": 2187, "pure_impossible_nodes": 0, "upper_pruned_nodes": 0, "prunable_nodes": 0, "H_lower_min": -12882, "H_lower_max": -10896, "H_upper_min": 10974, "H_upper_max": 13044, "forced_min": 0, "forced_max": 10},
            {"depth": 8, "nodes": 6561, "pure_impossible_nodes": 8, "upper_pruned_nodes": 0, "prunable_nodes": 8, "H_lower_min": -12768, "H_lower_max": -10758, "H_upper_min": 10878, "H_upper_max": 13026, "forced_min": 0, "forced_max": 12},
        ]
    raise ValueError(f"unknown S6-BRANCH-1 order: {order_name}")


# ---------------------------------------------------------------------------
# S6-BRANCH-2: greedy adaptive order scout
# ---------------------------------------------------------------------------

BRANCH2_GREEDY_DEPTH = 6
BRANCH2_GREEDY_EXPECTED_PREFIX = (20, 19, 18, 17, 16, 15)
BRANCH2_GREEDY_TAIL_B_ORDER = (20, 19, 18, 17, 16, 15, 14, 13)
BRANCH2_GREEDY_TAIL_A_ORDER = (20, 19, 18, 8, 7, 6, 5, 4)


def branch2_nodes_stats(nodes: list[tuple[int, ...]]) -> dict[str, int]:
    imp = ub = prunable = 0
    H_upper_min = 10**9
    H_upper_max = -10**9
    forced_sum = 0
    forced_max = 0
    for dom in nodes:
        b = partial_node_bounds(dom)
        imp_flag = int(b["local_impossible"] > 0)
        ub_flag = int(b["H_upper"] <= 7020)
        imp += imp_flag
        ub += ub_flag
        prunable += int(bool(imp_flag or ub_flag))
        H_upper_min = min(H_upper_min, int(b["H_upper"]))
        H_upper_max = max(H_upper_max, int(b["H_upper"]))
        forced_sum += int(b["local_forced"])
        forced_max = max(forced_max, int(b["local_forced"]))
    return {
        "nodes": len(nodes),
        "prunable_nodes": prunable,
        "pure_impossible_nodes": imp,
        "upper_pruned_nodes": ub,
        "H_upper_min": H_upper_min,
        "H_upper_max": H_upper_max,
        "forced_sum": forced_sum,
        "forced_max": forced_max,
    }


def branch2_score(stats: dict[str, int]) -> tuple[int, int, int, int, int, int]:
    return (
        stats["prunable_nodes"],
        stats["pure_impossible_nodes"],
        stats["upper_pruned_nodes"],
        stats["forced_sum"],
        -stats["H_upper_max"],
        -stats["H_upper_min"],
    )


def branch2_greedy_prefix(depth_limit: int = BRANCH2_GREEDY_DEPTH) -> tuple[tuple[int, ...], list[dict[str, int]]]:
    nodes = [root_domain()]
    remaining = set(range(21))
    chosen: list[int] = []
    rows: list[dict[str, int]] = []
    for depth in range(depth_limit):
        best: tuple[tuple[int, int, int, int, int, int], int, dict[str, int]] | None = None
        for idx in sorted(remaining):
            children = [
                restrict_domain(dom, idx, val)
                for dom in nodes
                for val in mask_values(dom[idx])
            ]
            stats = branch2_nodes_stats(children)
            candidate = (branch2_score(stats), idx, stats)
            if best is None or candidate > best:
                best = candidate
        if best is None:
            raise RuntimeError("empty greedy candidate set")
        _score, idx, stats = best
        rows.append({"depth": depth + 1, "chosen_index": idx, **stats})
        chosen.append(idx)
        remaining.remove(idx)
        nodes = [
            restrict_domain(dom, idx, val)
            for dom in nodes
            for val in mask_values(dom[idx])
        ]
    return tuple(chosen), rows


def branch2_expected_tail_scout(order: tuple[int, ...]) -> dict[str, int]:
    return fixed_order_interval_depth_scout(order, 8)[-1]


# ---------------------------------------------------------------------------
# S6-BRANCH-3: bounded frontier branch-and-prune runner
# ---------------------------------------------------------------------------

BRANCH3_TARGET_H = 7020
BRANCH3_REFERENCE_DEPTH = 9
BRANCH3_GREEDY_B_FIRST_ORDER = (20, 19, 18) + tuple(range(17, -1, -1))
BRANCH3_ORDER_NAMES = ("greedy_B_first",)
BRANCH3_EXPECTED_D9 = {
    "reached_depth": 9,
    "total_generated": 29280,
    "total_pruned_nodes": 981,
    "total_pure_impossible_pruned": 981,
    "total_upper_pruned": 0,
    "live_nodes": 18540,
    "live_H_upper_min": 10620,
    "live_H_upper_max": 12528,
    "live_forced_min": 0,
    "live_forced_max": 62,
}


def branch3_order(order_name: str = "greedy_B_first") -> tuple[int, ...]:
    if order_name == "greedy_B_first":
        return BRANCH3_GREEDY_B_FIRST_ORDER
    raise ValueError(f"unknown S6-BRANCH-3 order: {order_name}")


def branch3_prune_flags(bound: dict[str, int], target_H: int = BRANCH3_TARGET_H) -> tuple[int, int, int]:
    pure_impossible = int(bound["local_impossible"] > 0)
    upper_pruned = int(bound["H_upper"] <= target_H)
    return pure_impossible, upper_pruned, int(bool(pure_impossible or upper_pruned))


def branch3_frontier_bound_stats(live: list[tuple[tuple[int, ...], dict[str, int]]]) -> dict[str, int]:
    if not live:
        return {
            "live_nodes": 0,
            "live_H_upper_min": 0,
            "live_H_upper_max": 0,
            "live_forced_min": 0,
            "live_forced_max": 0,
        }
    bounds = [b for _dom, b in live]
    return {
        "live_nodes": len(live),
        "live_H_upper_min": min(int(b["H_upper"]) for b in bounds),
        "live_H_upper_max": max(int(b["H_upper"]) for b in bounds),
        "live_forced_min": min(int(b["local_forced"]) for b in bounds),
        "live_forced_max": max(int(b["local_forced"]) for b in bounds),
    }


def branch3_frontier_runner(
    max_depth: int = BRANCH3_REFERENCE_DEPTH,
    order_name: str = "greedy_B_first",
    target_H: int = BRANCH3_TARGET_H,
    max_generated_nodes: int = 0,
    time_limit_seconds: float = 0.0,
) -> dict[str, object]:
    """Run a bounded branch frontier with sound interval pruning.

    The runner keeps only live nodes. A child is pruned when either a local
    pure inequality is impossible on the node or the interval upper bound is
    already at most the pure-frontier target.
    """
    if max_depth < 0:
        raise ValueError("max_depth must be nonnegative")
    order = branch3_order(order_name)
    if max_depth > len(order):
        raise ValueError(f"max_depth={max_depth} exceeds order length {len(order)}")

    start = time.monotonic()
    root = root_domain()
    live: list[tuple[tuple[int, ...], dict[str, int]]] = [(root, partial_node_bounds(root))]
    rows: list[dict[str, int]] = []
    total_generated = 0
    total_pruned = 0
    total_pure_impossible = 0
    total_upper_pruned = 0
    status = "complete"

    for depth in range(max_depth):
        if not live:
            break
        idx = order[depth]
        live_next: list[tuple[tuple[int, ...], dict[str, int]]] = []
        generated = pruned = pure_impossible = upper_pruned = 0
        H_upper_min = 10**9
        H_upper_max = -10**9
        forced_min = 10**9
        forced_max = -10**9
        stopped = False

        for dom, _bound in live:
            for val in mask_values(dom[idx]):
                if max_generated_nodes > 0 and total_generated >= max_generated_nodes:
                    status = "max_generated_nodes"
                    stopped = True
                    break
                if time_limit_seconds > 0.0 and time.monotonic() - start >= time_limit_seconds:
                    status = "time_limit_seconds"
                    stopped = True
                    break

                child = restrict_domain(dom, idx, val)
                bound = partial_node_bounds(child)
                generated += 1
                total_generated += 1
                H_upper_min = min(H_upper_min, int(bound["H_upper"]))
                H_upper_max = max(H_upper_max, int(bound["H_upper"]))
                forced_min = min(forced_min, int(bound["local_forced"]))
                forced_max = max(forced_max, int(bound["local_forced"]))

                imp_flag, ub_flag, prune_flag = branch3_prune_flags(bound, target_H)
                pure_impossible += imp_flag
                upper_pruned += ub_flag
                pruned += prune_flag
                if prune_flag:
                    continue
                live_next.append((child, bound))
            if stopped:
                break

        total_pruned += pruned
        total_pure_impossible += pure_impossible
        total_upper_pruned += upper_pruned
        live_stats = branch3_frontier_bound_stats(live_next)
        rows.append({
            "depth": depth + 1,
            "branch_index": idx,
            "parents": len(live),
            "generated": generated,
            "pruned_nodes": pruned,
            "pure_impossible_nodes": pure_impossible,
            "upper_pruned_nodes": upper_pruned,
            "live_nodes": live_stats["live_nodes"],
            "generated_H_upper_min": H_upper_min if generated else 0,
            "generated_H_upper_max": H_upper_max if generated else 0,
            "generated_forced_min": forced_min if generated else 0,
            "generated_forced_max": forced_max if generated else 0,
            "live_H_upper_min": live_stats["live_H_upper_min"],
            "live_H_upper_max": live_stats["live_H_upper_max"],
            "live_forced_min": live_stats["live_forced_min"],
            "live_forced_max": live_stats["live_forced_max"],
        })
        live = live_next
        if stopped:
            break

    frontier_stats = branch3_frontier_bound_stats(live)
    reached_depth = rows[-1]["depth"] if rows else 0
    return {
        "order_name": order_name,
        "order_prefix": ",".join(str(i) for i in order[:reached_depth]),
        "target_H": target_H,
        "requested_depth": max_depth,
        "reached_depth": reached_depth,
        "status": status,
        "elapsed_seconds": round(time.monotonic() - start, 3),
        "total_generated": total_generated,
        "total_pruned_nodes": total_pruned,
        "total_pure_impossible_pruned": total_pure_impossible,
        "total_upper_pruned": total_upper_pruned,
        **frontier_stats,
        "rows": rows,
    }


# ---------------------------------------------------------------------------
# S6-BOUND-1: pure-aware SMT node evaluator
# ---------------------------------------------------------------------------

BOUND1_REFERENCE_DEPTH = 9
BOUND1_REFERENCE_SAMPLE_LIMIT = 20
BOUND1_TARGET_RAW_H = 1171
BOUND1_NODE_TIMEOUT_MS = 5000
BOUND1_EXPECTED_SAMPLE = {
    "depth": 9,
    "sampled_nodes": 20,
    "unsat_nodes": 20,
    "sat_nodes": 0,
    "unknown_nodes": 0,
    "fixed_coordinates_per_node": 9,
}


def branch3_live_frontier_domains(
    max_depth: int,
    order_name: str = "greedy_B_first",
    target_H: int = BRANCH3_TARGET_H,
    limit: int = 0,
) -> list[tuple[int, ...]]:
    """Return live frontier domains after branch3 interval pruning."""
    if max_depth < 0:
        raise ValueError("max_depth must be nonnegative")
    order = branch3_order(order_name)
    if max_depth > len(order):
        raise ValueError(f"max_depth={max_depth} exceeds order length {len(order)}")
    live = [root_domain()]
    for depth in range(max_depth):
        idx = order[depth]
        nxt: list[tuple[int, ...]] = []
        for dom in live:
            for val in mask_values(dom[idx]):
                child = restrict_domain(dom, idx, val)
                bound = partial_node_bounds(child)
                _imp, _ub, prune = branch3_prune_flags(bound, target_H)
                if prune:
                    continue
                nxt.append(child)
                if limit > 0 and depth == max_depth - 1 and len(nxt) >= limit:
                    return nxt
        live = nxt
        if limit > 0 and depth == max_depth - 1:
            return live[:limit]
    return live[:limit] if limit > 0 else live


def domain_assumptions_from_singletons(z3, X, dom: tuple[int, ...]) -> tuple[list[object], int, str]:
    assumptions: list[object] = []
    fixed_parts: list[str] = []
    for i, mask in enumerate(dom):
        if int(mask).bit_count() == 1:
            value = singleton_mask_value(int(mask))
            assumptions.append(X[i][value])
            fixed_parts.append(f"{i}={value}")
    return assumptions, len(assumptions), ",".join(fixed_parts)


def bound1_smt_node_probe(
    depth: int = BOUND1_REFERENCE_DEPTH,
    sample_limit: int = BOUND1_REFERENCE_SAMPLE_LIMIT,
    target_rawH: int = BOUND1_TARGET_RAW_H,
    timeout_ms: int = BOUND1_NODE_TIMEOUT_MS,
) -> dict[str, object]:
    """Probe live branch nodes with the exact pure high-H SMT formula.

    The global formula is built once. Each branch node is then checked through
    assumptions fixing the singleton coordinates of that partial domain.
    """
    started = time.time()
    ctx = smt1_global_onehot_pb_context(target_rawH=target_rawH, timeout_ms=timeout_ms)
    z3 = ctx["z3"]
    solver = ctx["solver"]
    X = ctx["X"]
    nodes = branch3_live_frontier_domains(depth, limit=sample_limit)
    results = []
    counts = Counter()
    check_started = time.time()
    for dom in nodes:
        assumptions, fixed_count, fixed_signature = domain_assumptions_from_singletons(z3, X, dom)
        ans = solver.check(assumptions)
        answer = str(ans)
        counts[answer] += 1
        rec: dict[str, object] = {
            "answer": answer,
            "fixed_count": fixed_count,
            "fixed_signature": fixed_signature,
        }
        if ans == z3.sat:
            word = smt1_model_word(z3, solver.model(), X)
            rec["witness"] = word
            rec["metrics"] = h_metrics_reduced(word)
        elif ans == z3.unknown:
            rec["reason"] = solver.reason_unknown()
        results.append(rec)
    check_seconds = time.time() - check_started
    fixed_counts = sorted({int(r["fixed_count"]) for r in results})
    return {
        "depth": depth,
        "sample_limit": sample_limit,
        "sampled_nodes": len(nodes),
        "target_rawH": target_rawH,
        "timeout_ms": timeout_ms,
        "encoding": ctx["encoding"],
        "build_seconds": ctx["build_seconds"],
        "check_seconds": round(check_seconds, 3),
        "elapsed_seconds": round(time.time() - started, 3),
        "assertions": ctx["assertions"],
        "weighted_terms": ctx["weighted_terms"],
        "unsat_nodes": counts.get("unsat", 0),
        "sat_nodes": counts.get("sat", 0),
        "unknown_nodes": counts.get("unknown", 0),
        "fixed_count_min": min(fixed_counts) if fixed_counts else 0,
        "fixed_count_max": max(fixed_counts) if fixed_counts else 0,
        "results": results,
    }


# ---------------------------------------------------------------------------
# S6-BOUND-2 / S6-CERT-PACK-0: batched SMT node pack
# ---------------------------------------------------------------------------

BOUND2_REFERENCE_DEPTH = 9
BOUND2_REFERENCE_BATCH_LIMIT = 81
BOUND2_NODE_TIMEOUT_MS = 5000
BOUND2_EXPECTED_BATCH = {
    "depth": 9,
    "batch_nodes": 81,
    "unique_signatures": 81,
    "cache_hits": 0,
    "unsat_nodes": 81,
    "sat_nodes": 0,
    "unknown_nodes": 0,
    "certified_unsat_entries": 81,
}


def branch3_live_frontier_domain_chunk(
    depth: int,
    chunk_offset: int = 0,
    chunk_limit: int = BOUND2_REFERENCE_BATCH_LIMIT,
) -> list[tuple[int, ...]]:
    if chunk_offset < 0:
        raise ValueError("chunk_offset must be nonnegative")
    if chunk_limit < 0:
        raise ValueError("chunk_limit must be nonnegative")
    cap = 0 if chunk_limit == 0 else chunk_offset + chunk_limit
    nodes = branch3_live_frontier_domains(depth, limit=cap)
    return nodes[chunk_offset:] if chunk_limit == 0 else nodes[chunk_offset:chunk_offset + chunk_limit]


def bound2_smt_batch_pack(
    depth: int = BOUND2_REFERENCE_DEPTH,
    batch_limit: int = BOUND2_REFERENCE_BATCH_LIMIT,
    batch_offset: int = 0,
    target_rawH: int = BOUND1_TARGET_RAW_H,
    timeout_ms: int = BOUND2_NODE_TIMEOUT_MS,
) -> dict[str, object]:
    """Evaluate a batch of interval-live nodes and return a compact pack summary."""
    started = time.time()
    ctx = smt1_global_onehot_pb_context(target_rawH=target_rawH, timeout_ms=timeout_ms)
    z3 = ctx["z3"]
    solver = ctx["solver"]
    X = ctx["X"]
    nodes = branch3_live_frontier_domain_chunk(depth, batch_offset, batch_limit)
    cache: dict[str, dict[str, object]] = {}
    results: list[dict[str, object]] = []
    counts = Counter()
    cache_hits = 0
    check_started = time.time()

    for local_index, dom in enumerate(nodes):
        node_index = batch_offset + local_index
        assumptions, fixed_count, fixed_signature = domain_assumptions_from_singletons(z3, X, dom)
        cached = cache.get(fixed_signature)
        if cached is not None:
            cache_hits += 1
            rec = {**cached, "node_index": node_index, "cache": "hit"}
        else:
            ans = solver.check(assumptions)
            answer = str(ans)
            rec = {
                "node_index": node_index,
                "answer": answer,
                "fixed_count": fixed_count,
                "fixed_signature": fixed_signature,
                "cache": "miss",
            }
            if ans == z3.sat:
                word = smt1_model_word(z3, solver.model(), X)
                rec["witness"] = word
                rec["metrics"] = h_metrics_reduced(word)
            elif ans == z3.unknown:
                rec["reason"] = solver.reason_unknown()
            cache[fixed_signature] = {k: v for k, v in rec.items() if k != "node_index"}
        counts[str(rec["answer"])] += 1
        results.append(rec)

    certified_entries = [
        {
            "node_index": int(rec["node_index"]),
            "fixed_signature": str(rec["fixed_signature"]),
            "query": f"pure_and_rawH_ge_{target_rawH}",
            "answer": "UNSAT",
        }
        for rec in results
        if rec["answer"] == "unsat"
    ]
    fixed_counts = sorted({int(r["fixed_count"]) for r in results})
    return {
        "pack_kind": "assumption_unsat_node_pack",
        "depth": depth,
        "batch_offset": batch_offset,
        "batch_limit": batch_limit,
        "batch_nodes": len(nodes),
        "next_offset": batch_offset + len(nodes),
        "frontier_total": BRANCH3_EXPECTED_D9["live_nodes"] if depth == BRANCH3_REFERENCE_DEPTH else "",
        "target_rawH": target_rawH,
        "timeout_ms": timeout_ms,
        "encoding": ctx["encoding"],
        "build_seconds": ctx["build_seconds"],
        "check_seconds": round(time.time() - check_started, 3),
        "elapsed_seconds": round(time.time() - started, 3),
        "assertions": ctx["assertions"],
        "weighted_terms": ctx["weighted_terms"],
        "unique_signatures": len(cache),
        "cache_hits": cache_hits,
        "unsat_nodes": counts.get("unsat", 0),
        "sat_nodes": counts.get("sat", 0),
        "unknown_nodes": counts.get("unknown", 0),
        "certified_unsat_entries": len(certified_entries),
        "noncertified_nodes": counts.get("sat", 0) + counts.get("unknown", 0),
        "fixed_count_min": min(fixed_counts) if fixed_counts else 0,
        "fixed_count_max": max(fixed_counts) if fixed_counts else 0,
        "first_signature": str(results[0]["fixed_signature"]) if results else "",
        "last_signature": str(results[-1]["fixed_signature"]) if results else "",
        "results": results,
        "pack_entries": certified_entries,
    }


# S6-BOUND-3 / S6-CERT-PACK-1: resumable chunk accounting

BOUND3_REFERENCE_DEPTH = 9
BOUND3_REFERENCE_CHUNK_OFFSET = 0
BOUND3_REFERENCE_CHUNK_LIMIT = 162
BOUND3_FRONTIER_TOTAL_D9 = BRANCH3_EXPECTED_D9["live_nodes"]
BOUND3_REFERENCE_CHUNK_COUNT = (BOUND3_FRONTIER_TOTAL_D9 + BOUND3_REFERENCE_CHUNK_LIMIT - 1) // BOUND3_REFERENCE_CHUNK_LIMIT
BOUND3_EXPECTED_CHUNK = {
    "depth": 9,
    "batch_offset": 0,
    "batch_limit": 162,
    "batch_nodes": 162,
    "next_offset": 162,
    "frontier_total": 18540,
    "chunk_count": 115,
    "unique_signatures": 162,
    "cache_hits": 0,
    "unsat_nodes": 162,
    "sat_nodes": 0,
    "unknown_nodes": 0,
    "certified_unsat_entries": 162,
}

BOUND4_EXPECTED_CHUNK = {
    "depth": 9,
    "batch_offset": 162,
    "batch_limit": 162,
    "batch_nodes": 162,
    "next_offset": 324,
    "frontier_total": 18540,
    "chunk_count": 115,
    "unique_signatures": 162,
    "cache_hits": 0,
    "unsat_nodes": 162,
    "sat_nodes": 0,
    "unknown_nodes": 0,
    "certified_unsat_entries": 162,
    "cumulative_certified_unsat_entries": 324,
}

BOUND5_REFERENCE_DEPTH = 9
BOUND5_REFERENCE_START_OFFSET = 0
BOUND5_REFERENCE_CHUNK_LIMIT = 162
BOUND5_REFERENCE_CHUNKS = 2
BOUND5_EXPECTED_RUN = {
    "depth": 9,
    "start_offset": 0,
    "chunk_limit": 162,
    "chunks_requested": 2,
    "chunks_completed": 2,
    "total_nodes": 324,
    "next_offset": 324,
    "frontier_total": 18540,
    "unique_signatures": 324,
    "cache_hits": 0,
    "unsat_nodes": 324,
    "sat_nodes": 0,
    "unknown_nodes": 0,
    "certified_unsat_entries": 324,
}

BOUND6_EXPECTED_RUN = {
    "depth": 9,
    "start_offset": 324,
    "chunk_limit": 162,
    "chunks_requested": 4,
    "chunks_completed": 4,
    "total_nodes": 648,
    "next_offset": 972,
    "frontier_total": 18540,
    "unique_signatures": 648,
    "cache_hits": 0,
    "unsat_nodes": 635,
    "sat_nodes": 0,
    "unknown_nodes": 13,
    "certified_unsat_entries": 635,
    "cumulative_checked_nodes": 972,
    "cumulative_certified_unsat_entries": 959,
    "chunk_unsat_profile": "156/159/158/162",
    "chunk_unknown_profile": "6/3/4/0",
}

UNKNOWN1_TARGETED_ROWS = (
    (364, "12=1,13=1,14=1,15=1,16=1,17=1,18=0,19=0,20=0"),
    (365, "12=2,13=1,14=1,15=1,16=1,17=1,18=0,19=0,20=0"),
    (373, "12=1,13=1,14=2,15=1,16=1,17=1,18=0,19=0,20=0"),
    (392, "12=2,13=1,14=1,15=2,16=1,17=1,18=0,19=0,20=0"),
    (448, "12=1,13=2,14=1,15=1,16=2,17=1,18=0,19=0,20=0"),
    (476, "12=2,13=2,14=1,15=2,16=2,17=1,18=0,19=0,20=0"),
    (616, "12=1,13=1,14=2,15=1,16=1,17=2,18=0,19=0,20=0"),
    (644, "12=2,13=1,14=2,15=2,16=1,17=2,18=0,19=0,20=0"),
    (647, "12=2,13=2,14=2,15=2,16=1,17=2,18=0,19=0,20=0"),
    (697, "12=1,13=1,14=2,15=1,16=2,17=2,18=0,19=0,20=0"),
    (700, "12=1,13=2,14=2,15=1,16=2,17=2,18=0,19=0,20=0"),
    (728, "12=2,13=2,14=2,15=2,16=2,17=2,18=0,19=0,20=0"),
)
UNKNOWN1_REPLAY_NODE_IDS = "/".join(str(node_index) for node_index, _sig in UNKNOWN1_TARGETED_ROWS)
BOUND7_NODE_TIMEOUT_MS = 60000
BOUND7_EXPECTED_TARGETED = {
    "depth": 9,
    "source_start_offset": 324,
    "source_chunk_limit": 162,
    "source_chunks": 4,
    "source_next_offset": 972,
    "source_total_nodes": 648,
    "source_replay_unsat_nodes": 636,
    "source_replay_unknown_nodes": 12,
    "targeted_nodes": 12,
    "targeted_timeout_ms": 60000,
    "unsat_nodes": 12,
    "sat_nodes": 0,
    "unknown_nodes": 0,
    "targeted_certified_unsat_entries": 12,
    "closed_segment_certified_unsat_entries": 648,
    "cumulative_checked_nodes": 972,
    "cumulative_certified_unsat_entries": 972,
}

BOUND8_EXPECTED_RUN = {
    "depth": 9,
    "start_offset": 972,
    "chunk_limit": 162,
    "chunks_requested": 8,
    "chunks_completed": 8,
    "total_nodes": 1296,
    "next_offset": 2268,
    "frontier_total": 18540,
    "unique_signatures": 1296,
    "cache_hits": 0,
    "unsat_nodes": 1296,
    "sat_nodes": 0,
    "unknown_nodes": 0,
    "certified_unsat_entries": 1296,
    "cumulative_checked_nodes": 2268,
    "cumulative_certified_unsat_entries": 2268,
    "timeout_ms": 300000,
    "chunk_unsat_profile": "162/162/162/162/162/162/162/162",
    "chunk_unknown_profile": "0/0/0/0/0/0/0/0",
}

BOUND9_EXPECTED_RUN = {
    "depth": 9,
    "start_offset": 2268,
    "chunk_limit": 162,
    "chunks_requested": 8,
    "chunks_completed": 8,
    "total_nodes": 1296,
    "next_offset": 3564,
    "frontier_total": 18540,
    "unique_signatures": 1296,
    "cache_hits": 0,
    "unsat_nodes": 1296,
    "sat_nodes": 0,
    "unknown_nodes": 0,
    "certified_unsat_entries": 1296,
    "cumulative_checked_nodes": 3564,
    "cumulative_certified_unsat_entries": 3564,
    "timeout_ms": 300000,
    "chunk_unsat_profile": "162/162/162/162/162/162/162/162",
    "chunk_unknown_profile": "0/0/0/0/0/0/0/0",
}

BOUND10_EXPECTED_RUN = {
    "depth": 9,
    "start_offset": 3564,
    "chunk_limit": 162,
    "chunks_requested": 8,
    "chunks_completed": 8,
    "total_nodes": 1296,
    "next_offset": 4860,
    "frontier_total": 18540,
    "unique_signatures": 1296,
    "cache_hits": 0,
    "unsat_nodes": 1296,
    "sat_nodes": 0,
    "unknown_nodes": 0,
    "certified_unsat_entries": 1296,
    "cumulative_checked_nodes": 4860,
    "cumulative_certified_unsat_entries": 4860,
    "timeout_ms": 300000,
    "chunk_unsat_profile": "162/162/162/162/162/162/162/162",
    "chunk_unknown_profile": "0/0/0/0/0/0/0/0",
}

BOUND11_FINAL_RUN_DIR = SCRIPT_DIR / "h2" / "raw"
BOUND11_EXPECTED_RUN = {
    "depth": 9,
    "start_offset": 4860,
    "end_offset": 18540,
    "chunk_size": 162,
    "window_chunks": 8,
    "window_nodes": 1296,
    "chunks_completed": 85,
    "windows_completed": 11,
    "total_nodes": 13680,
    "frontier_total": 18540,
    "target_rawH": 1171,
    "timeout_ms": 300000,
    "unsat_nodes": 13680,
    "sat_nodes": 0,
    "unknown_nodes": 0,
    "certified_unsat_entries": 13680,
    "next_offset": 18540,
    "rerun": "all",
}
CERTPACK_FINAL_EXPECTED = {
    "depth": 9,
    "frontier_total": 18540,
    "certified_unsat_entries": 18540,
    "sat_nodes": 0,
    "unresolved_nodes": 0,
    "target_rawH": 1171,
    "pure_frontier_H_max": 7020,
}
CERTPACK_FINAL_SEGMENTS = (
    ("CERTPACK1", 0, 162, 162),
    ("CERTPACK2", 162, 324, 162),
    ("CERTPACK5", 324, 972, 648),
    ("CERTPACK6", 972, 2268, 1296),
    ("CERTPACK7", 2268, 3564, 1296),
    ("CERTPACK8", 3564, 4860, 1296),
    ("CERTPACK9", 4860, 18540, 13680),
)


def bound3_smt_chunk_pack(
    depth: int = BOUND3_REFERENCE_DEPTH,
    chunk_offset: int = BOUND3_REFERENCE_CHUNK_OFFSET,
    chunk_limit: int = BOUND3_REFERENCE_CHUNK_LIMIT,
    target_rawH: int = BOUND1_TARGET_RAW_H,
    timeout_ms: int = BOUND2_NODE_TIMEOUT_MS,
) -> dict[str, object]:
    summary = bound2_smt_batch_pack(
        depth=depth,
        batch_limit=chunk_limit,
        batch_offset=chunk_offset,
        target_rawH=target_rawH,
        timeout_ms=timeout_ms,
    )
    frontier_total = summary["frontier_total"]
    if isinstance(frontier_total, int) and chunk_limit > 0:
        summary["chunk_count"] = (frontier_total + chunk_limit - 1) // chunk_limit
        summary["chunk_index"] = chunk_offset // chunk_limit
    else:
        summary["chunk_count"] = ""
        summary["chunk_index"] = ""
    summary["pack_kind"] = "resumable_assumption_unsat_node_pack"
    return summary


def bound5_smt_multi_chunk_pack(
    depth: int = BOUND5_REFERENCE_DEPTH,
    start_offset: int = BOUND5_REFERENCE_START_OFFSET,
    chunk_limit: int = BOUND5_REFERENCE_CHUNK_LIMIT,
    chunks: int = BOUND5_REFERENCE_CHUNKS,
    target_rawH: int = BOUND1_TARGET_RAW_H,
    timeout_ms: int = BOUND2_NODE_TIMEOUT_MS,
) -> dict[str, object]:
    """Run several resumable chunks with one reusable SMT context."""
    if chunks <= 0:
        raise ValueError("chunks must be positive")
    if chunk_limit <= 0:
        raise ValueError("chunk_limit must be positive")
    started = time.time()
    total_limit = chunk_limit * chunks
    nodes = branch3_live_frontier_domain_chunk(depth, start_offset, total_limit)
    ctx = smt1_global_onehot_pb_context(target_rawH=target_rawH, timeout_ms=timeout_ms)
    z3 = ctx["z3"]
    solver = ctx["solver"]
    X = ctx["X"]
    cache: dict[str, dict[str, object]] = {}
    results: list[dict[str, object]] = []
    counts = Counter()
    cache_hits = 0
    chunk_counts = [Counter() for _ in range(chunks)]
    chunk_nodes = [0 for _ in range(chunks)]
    check_started = time.time()

    for local_index, dom in enumerate(nodes):
        node_index = start_offset + local_index
        chunk_index = min(local_index // chunk_limit, chunks - 1)
        assumptions, fixed_count, fixed_signature = domain_assumptions_from_singletons(z3, X, dom)
        cached = cache.get(fixed_signature)
        if cached is not None:
            cache_hits += 1
            rec = {**cached, "node_index": node_index, "chunk_index": chunk_index, "cache": "hit"}
        else:
            ans = solver.check(assumptions)
            answer = str(ans)
            rec = {
                "node_index": node_index,
                "chunk_index": chunk_index,
                "answer": answer,
                "fixed_count": fixed_count,
                "fixed_signature": fixed_signature,
                "cache": "miss",
            }
            if ans == z3.sat:
                word = smt1_model_word(z3, solver.model(), X)
                rec["witness"] = word
                rec["metrics"] = h_metrics_reduced(word)
            elif ans == z3.unknown:
                rec["reason"] = solver.reason_unknown()
            cache[fixed_signature] = {k: v for k, v in rec.items() if k not in ("node_index", "chunk_index")}
        answer = str(rec["answer"])
        counts[answer] += 1
        chunk_counts[chunk_index][answer] += 1
        chunk_nodes[chunk_index] += 1
        results.append(rec)

    certified_entries = [
        {
            "node_index": int(rec["node_index"]),
            "chunk_index": int(rec["chunk_index"]),
            "fixed_signature": str(rec["fixed_signature"]),
            "query": f"pure_and_rawH_ge_{target_rawH}",
            "answer": "UNSAT",
        }
        for rec in results
        if rec["answer"] == "unsat"
    ]
    chunk_summaries = []
    for i in range(chunks):
        offset = start_offset + i * chunk_limit
        count = chunk_nodes[i]
        chunk_summaries.append({
            "chunk_index": i,
            "offset": offset,
            "limit": chunk_limit,
            "nodes": count,
            "next_offset": offset + count,
            "unsat_nodes": chunk_counts[i].get("unsat", 0),
            "sat_nodes": chunk_counts[i].get("sat", 0),
            "unknown_nodes": chunk_counts[i].get("unknown", 0),
        })
    fixed_counts = sorted({int(r["fixed_count"]) for r in results})
    return {
        "pack_kind": "multi_chunk_assumption_unsat_node_pack",
        "depth": depth,
        "start_offset": start_offset,
        "chunk_limit": chunk_limit,
        "chunks_requested": chunks,
        "chunks_completed": sum(1 for n in chunk_nodes if n > 0),
        "total_nodes": len(nodes),
        "next_offset": start_offset + len(nodes),
        "frontier_total": BRANCH3_EXPECTED_D9["live_nodes"] if depth == BRANCH3_REFERENCE_DEPTH else "",
        "target_rawH": target_rawH,
        "timeout_ms": timeout_ms,
        "encoding": ctx["encoding"],
        "build_seconds": ctx["build_seconds"],
        "check_seconds": round(time.time() - check_started, 3),
        "elapsed_seconds": round(time.time() - started, 3),
        "assertions": ctx["assertions"],
        "weighted_terms": ctx["weighted_terms"],
        "unique_signatures": len(cache),
        "cache_hits": cache_hits,
        "unsat_nodes": counts.get("unsat", 0),
        "sat_nodes": counts.get("sat", 0),
        "unknown_nodes": counts.get("unknown", 0),
        "certified_unsat_entries": len(certified_entries),
        "noncertified_nodes": counts.get("sat", 0) + counts.get("unknown", 0),
        "fixed_count_min": min(fixed_counts) if fixed_counts else 0,
        "fixed_count_max": max(fixed_counts) if fixed_counts else 0,
        "chunk_summaries": chunk_summaries,
        "results": results,
        "pack_entries": certified_entries,
    }


def assumptions_from_fixed_signature(X, fixed_signature: str) -> list[object]:
    assumptions: list[object] = []
    for part in fixed_signature.split(","):
        index_s, value_s = part.split("=")
        index = int(index_s)
        value = int(value_s)
        if not (0 <= index < len(X) and value in S):
            raise ValueError(f"invalid fixed signature part {part!r}")
        assumptions.append(X[index][value])
    return assumptions


def bound7_smt_unknown_tail_closure(
    target_rawH: int = BOUND1_TARGET_RAW_H,
    timeout_ms: int = BOUND7_NODE_TIMEOUT_MS,
) -> dict[str, object]:
    """Recheck the replay-extracted UNKNOWN tail with a larger per-node timeout."""
    started = time.time()
    ctx = smt1_global_onehot_pb_context(target_rawH=target_rawH, timeout_ms=timeout_ms)
    z3 = ctx["z3"]
    solver = ctx["solver"]
    X = ctx["X"]
    results: list[dict[str, object]] = []
    counts = Counter()
    check_started = time.time()

    for node_index, fixed_signature in UNKNOWN1_TARGETED_ROWS:
        t0 = time.time()
        assumptions = assumptions_from_fixed_signature(X, fixed_signature)
        ans = solver.check(assumptions)
        answer = str(ans)
        counts[answer] += 1
        rec: dict[str, object] = {
            "node_index": node_index,
            "answer": answer,
            "fixed_count": len(assumptions),
            "fixed_signature": fixed_signature,
            "seconds": round(time.time() - t0, 3),
        }
        if ans == z3.sat:
            word = smt1_model_word(z3, solver.model(), X)
            rec["witness"] = word
            rec["metrics"] = h_metrics_reduced(word)
        elif ans == z3.unknown:
            rec["reason"] = solver.reason_unknown()
        results.append(rec)

    certified_entries = [
        {
            "node_index": int(rec["node_index"]),
            "fixed_signature": str(rec["fixed_signature"]),
            "query": f"pure_and_rawH_ge_{target_rawH}",
            "answer": "UNSAT",
        }
        for rec in results
        if rec["answer"] == "unsat"
    ]
    fixed_counts = sorted({int(r["fixed_count"]) for r in results})
    check_times = [float(r["seconds"]) for r in results]
    return {
        "pack_kind": "targeted_unknown_tail_unsat_pack",
        "depth": BOUND7_EXPECTED_TARGETED["depth"],
        "source_start_offset": BOUND7_EXPECTED_TARGETED["source_start_offset"],
        "source_chunk_limit": BOUND7_EXPECTED_TARGETED["source_chunk_limit"],
        "source_chunks": BOUND7_EXPECTED_TARGETED["source_chunks"],
        "source_next_offset": BOUND7_EXPECTED_TARGETED["source_next_offset"],
        "source_total_nodes": BOUND7_EXPECTED_TARGETED["source_total_nodes"],
        "source_replay_unsat_nodes": BOUND7_EXPECTED_TARGETED["source_replay_unsat_nodes"],
        "source_replay_unknown_nodes": BOUND7_EXPECTED_TARGETED["source_replay_unknown_nodes"],
        "target_rawH": target_rawH,
        "timeout_ms": timeout_ms,
        "encoding": ctx["encoding"],
        "build_seconds": ctx["build_seconds"],
        "check_seconds": round(time.time() - check_started, 3),
        "elapsed_seconds": round(time.time() - started, 3),
        "assertions": ctx["assertions"],
        "weighted_terms": ctx["weighted_terms"],
        "targeted_nodes": len(results),
        "unsat_nodes": counts.get("unsat", 0),
        "sat_nodes": counts.get("sat", 0),
        "unknown_nodes": counts.get("unknown", 0),
        "targeted_certified_unsat_entries": len(certified_entries),
        "closed_segment_certified_unsat_entries": (
            BOUND7_EXPECTED_TARGETED["source_replay_unsat_nodes"] + len(certified_entries)
        ),
        "cumulative_checked_nodes": BOUND7_EXPECTED_TARGETED["cumulative_checked_nodes"],
        "cumulative_certified_unsat_entries": (
            BOUND3_EXPECTED_CHUNK["certified_unsat_entries"]
            + BOUND4_EXPECTED_CHUNK["certified_unsat_entries"]
            + BOUND7_EXPECTED_TARGETED["source_replay_unsat_nodes"]
            + len(certified_entries)
        ),
        "fixed_count_min": min(fixed_counts) if fixed_counts else 0,
        "fixed_count_max": max(fixed_counts) if fixed_counts else 0,
        "max_check_seconds": round(max(check_times), 3) if check_times else 0.0,
        "node_ids": UNKNOWN1_REPLAY_NODE_IDS,
        "results": results,
        "pack_entries": certified_entries,
    }


# ---------------------------------------------------------------------------
# S6-BOUND-11 / S6-CERT-PACK-FINAL: audited H2 closure pack
# ---------------------------------------------------------------------------

CERTPACK_FINAL_REQUIRED_FILES = (
    "checkpoint.json",
    "nodes.csv",
    "chunks.csv",
    "windows.csv",
    "unknown.csv",
    "sat.csv",
    "audit_report.json",
    "audit_rerun.csv",
)


def certpack_read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def certpack_read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def certpack_int(row: dict[str, str], key: str, label: str) -> int:
    try:
        return int(row[key])
    except Exception as exc:
        raise ValueError(f"{label}: invalid integer field {key}={row.get(key)!r}") from exc


def certpack_float(row: dict[str, str], key: str, label: str) -> float:
    try:
        return float(row[key])
    except Exception as exc:
        raise ValueError(f"{label}: invalid float field {key}={row.get(key)!r}") from exc


def fixed_signature_from_domain(dom: tuple[int, ...]) -> tuple[int, str]:
    parts: list[str] = []
    for i, mask in enumerate(dom):
        if int(mask).bit_count() == 1:
            parts.append(f"{i}={singleton_mask_value(int(mask))}")
    return len(parts), ",".join(parts)


def certpack_answer_counts(
    nodes_by_index: dict[int, dict[str, str]],
    start_offset: int,
    end_offset: int,
) -> Counter:
    return Counter(nodes_by_index[i].get("answer", "") for i in range(start_offset, end_offset) if i in nodes_by_index)


def certpack_validate_chunks(
    rows: list[dict[str, str]],
    nodes_by_index: dict[int, dict[str, str]],
    start_offset: int,
    end_offset: int,
) -> None:
    expected_next = start_offset
    cumulative: Counter = Counter()
    for row_no, row in enumerate(rows, start=2):
        offset = certpack_int(row, "offset", f"chunks.csv:{row_no}")
        row_end = certpack_int(row, "end_offset", f"chunks.csv:{row_no}")
        nodes = certpack_int(row, "nodes", f"chunks.csv:{row_no}")
        if offset != expected_next:
            fail(f"S6-CERT-PACK-FINAL chunks.csv:{row_no} offset {offset} != expected {expected_next}")
        if nodes != row_end - offset:
            fail(f"S6-CERT-PACK-FINAL chunks.csv:{row_no} nodes {nodes} != interval length {row_end - offset}")
        counts = certpack_answer_counts(nodes_by_index, offset, row_end)
        for answer, field in (("unsat", "unsat"), ("sat", "sat"), ("unknown", "unknown")):
            got = certpack_int(row, field, f"chunks.csv:{row_no}")
            if got != counts.get(answer, 0):
                fail(f"S6-CERT-PACK-FINAL chunks.csv:{row_no} {field} {got} != nodes.csv count {counts.get(answer, 0)}")
        cumulative.update(counts)
        cumulative_checked = certpack_int(row, "cumulative_checked", f"chunks.csv:{row_no}")
        if cumulative_checked != sum(cumulative.values()):
            fail(f"S6-CERT-PACK-FINAL chunks.csv:{row_no} cumulative_checked {cumulative_checked} != expected {sum(cumulative.values())}")
        for answer, field in (
            ("unsat", "cumulative_unsat"),
            ("sat", "cumulative_sat"),
            ("unknown", "cumulative_unknown"),
        ):
            got = certpack_int(row, field, f"chunks.csv:{row_no}")
            if got != cumulative.get(answer, 0):
                fail(f"S6-CERT-PACK-FINAL chunks.csv:{row_no} {field} {got} != expected {cumulative.get(answer, 0)}")
        next_offset = certpack_int(row, "next_offset", f"chunks.csv:{row_no}")
        if next_offset != row_end:
            fail(f"S6-CERT-PACK-FINAL chunks.csv:{row_no} next_offset {next_offset} != end_offset {row_end}")
        expected_next = row_end
    if expected_next != end_offset:
        fail(f"S6-CERT-PACK-FINAL chunks coverage ended at {expected_next}, expected {end_offset}")


def certpack_validate_windows(
    rows: list[dict[str, str]],
    nodes_by_index: dict[int, dict[str, str]],
    start_offset: int,
    end_offset: int,
) -> None:
    expected_next = start_offset
    for row_no, row in enumerate(rows, start=2):
        offset = certpack_int(row, "offset", f"windows.csv:{row_no}")
        row_end = certpack_int(row, "end_offset", f"windows.csv:{row_no}")
        nodes = certpack_int(row, "nodes", f"windows.csv:{row_no}")
        if offset != expected_next:
            fail(f"S6-CERT-PACK-FINAL windows.csv:{row_no} offset {offset} != expected {expected_next}")
        if nodes != row_end - offset:
            fail(f"S6-CERT-PACK-FINAL windows.csv:{row_no} nodes {nodes} != interval length {row_end - offset}")
        counts = certpack_answer_counts(nodes_by_index, offset, row_end)
        for answer, field in (("unsat", "unsat"), ("sat", "sat"), ("unknown", "unknown")):
            got = certpack_int(row, field, f"windows.csv:{row_no}")
            if got != counts.get(answer, 0):
                fail(f"S6-CERT-PACK-FINAL windows.csv:{row_no} {field} {got} != nodes.csv count {counts.get(answer, 0)}")
        next_offset = certpack_int(row, "next_offset", f"windows.csv:{row_no}")
        if next_offset != row_end:
            fail(f"S6-CERT-PACK-FINAL windows.csv:{row_no} next_offset {next_offset} != end_offset {row_end}")
        expected_next = row_end
    if expected_next != end_offset:
        fail(f"S6-CERT-PACK-FINAL windows coverage ended at {expected_next}, expected {end_offset}")


def certpack_validate_sat_unknown_logs(
    run_dir: Path,
    nodes_by_index: dict[int, dict[str, str]],
    target_rawH: int,
) -> None:
    unknown_rows = certpack_read_csv(run_dir / "unknown.csv")
    sat_rows = certpack_read_csv(run_dir / "sat.csv")
    unknown_nodes = {int(row["node_index"]) for row in unknown_rows if row.get("node_index")}
    sat_nodes = {int(row["node_index"]) for row in sat_rows if row.get("node_index")}
    expected_unknown = {i for i, row in nodes_by_index.items() if row.get("answer") == "unknown"}
    expected_sat = {i for i, row in nodes_by_index.items() if row.get("answer") == "sat"}
    if unknown_nodes != expected_unknown:
        fail(f"S6-CERT-PACK-FINAL unknown.csv nodes do not match nodes.csv UNKNOWN set")
    if sat_nodes != expected_sat:
        fail(f"S6-CERT-PACK-FINAL sat.csv nodes do not match nodes.csv SAT set")
    for row_no, row in enumerate(sat_rows, start=2):
        witness = row.get("witness", "")
        if not witness:
            fail(f"S6-CERT-PACK-FINAL sat.csv:{row_no} missing witness")
        metrics = h_metrics_reduced(witness)
        if int(metrics["N_neg"]) != 0 or int(metrics["rawH"]) < target_rawH:
            fail(f"S6-CERT-PACK-FINAL sat.csv:{row_no} witness violates query metrics: {metrics}")


def certpack_validate_full_rerun(
    rows: list[dict[str, str]],
    start_offset: int,
    end_offset: int,
) -> dict[str, object]:
    starts = []
    for i, row in enumerate(rows):
        try:
            if int(row.get("node_index", "")) == start_offset:
                starts.append(i)
        except Exception:
            continue
    if not starts:
        fail("S6-CERT-PACK-FINAL audit_rerun.csv has no segment starting at the expected start offset")
    segment = rows[starts[-1]:]
    expected_nodes = end_offset - start_offset
    if len(segment) != expected_nodes:
        fail(f"S6-CERT-PACK-FINAL final audit_rerun segment has {len(segment)} rows, expected {expected_nodes}")
    seen: set[int] = set()
    max_seconds = 0.0
    total_seconds = 0.0
    for row_no, row in enumerate(segment, start=starts[-1] + 2):
        node_index = certpack_int(row, "node_index", f"audit_rerun.csv:{row_no}")
        if node_index in seen:
            fail(f"S6-CERT-PACK-FINAL audit_rerun.csv duplicate node_index {node_index}")
        seen.add(node_index)
        if not (start_offset <= node_index < end_offset):
            fail(f"S6-CERT-PACK-FINAL audit_rerun.csv node_index {node_index} out of range")
        if row.get("expected_answer") != "unsat" or row.get("rerun_answer") != "unsat":
            fail(f"S6-CERT-PACK-FINAL audit_rerun.csv node {node_index} is not UNSAT/UNSAT")
        if row.get("mismatch") not in ("0", "", "False", "false"):
            fail(f"S6-CERT-PACK-FINAL audit_rerun.csv node {node_index} has mismatch={row.get('mismatch')!r}")
        seconds = float(row.get("seconds") or 0.0)
        max_seconds = max(max_seconds, seconds)
        total_seconds += seconds
    missing = sorted(set(range(start_offset, end_offset)) - seen)
    if missing:
        fail(f"S6-CERT-PACK-FINAL audit_rerun.csv missing nodes; first missing={missing[:10]}")
    return {
        "rerun_rows": len(segment),
        "rerun_max_seconds": round(max_seconds, 3),
        "rerun_sum_seconds": round(total_seconds, 3),
    }


def certpack_final_static_coverage() -> dict[str, object]:
    expected_next = 0
    total = 0
    for name, start, end, certified in CERTPACK_FINAL_SEGMENTS:
        if start != expected_next:
            fail(f"S6-CERT-PACK-FINAL static segment {name} starts at {start}, expected {expected_next}")
        if certified != end - start:
            fail(f"S6-CERT-PACK-FINAL static segment {name} certified {certified} != interval length {end - start}")
        total += certified
        expected_next = end
    frontier_total = CERTPACK_FINAL_EXPECTED["frontier_total"]
    if expected_next != frontier_total or total != frontier_total:
        fail(f"S6-CERT-PACK-FINAL static coverage ended at {expected_next} with total {total}, expected {frontier_total}")
    return {
        "segments": len(CERTPACK_FINAL_SEGMENTS),
        "certified_unsat_entries": total,
        "start_offset": 0,
        "end_offset": expected_next,
    }


def certpack_final_audit(run_dir: Path = BOUND11_FINAL_RUN_DIR) -> dict[str, object]:
    run_dir = Path(run_dir)
    for name in CERTPACK_FINAL_REQUIRED_FILES:
        if not (run_dir / name).is_file():
            fail(f"S6-CERT-PACK-FINAL missing required file {run_dir / name}")

    checkpoint = certpack_read_json(run_dir / "checkpoint.json")
    report = certpack_read_json(run_dir / "audit_report.json")
    expected = BOUND11_EXPECTED_RUN
    start_offset = int(checkpoint.get("start_offset", -1))
    end_offset = int(checkpoint.get("effective_end_offset", -1))
    total_nodes = expected["total_nodes"]

    checks = {
        "status": "complete",
        "depth": expected["depth"],
        "start_offset": expected["start_offset"],
        "effective_end_offset": expected["end_offset"],
        "frontier_total": expected["frontier_total"],
        "next_offset": expected["next_offset"],
        "checked_nodes": total_nodes,
        "unsat_nodes": expected["unsat_nodes"],
        "sat_nodes": expected["sat_nodes"],
        "unknown_nodes": expected["unknown_nodes"],
        "target_rawH": expected["target_rawH"],
        "timeout_ms": expected["timeout_ms"],
        "chunk_size": expected["chunk_size"],
        "window_chunks": expected["window_chunks"],
        "window_nodes": expected["window_nodes"],
    }
    for key, value in checks.items():
        if checkpoint.get(key) != value:
            fail(f"S6-CERT-PACK-FINAL checkpoint {key}={checkpoint.get(key)!r}, expected {value!r}")
    if int(checkpoint.get("remaining_nodes", -1)) != 0:
        fail("S6-CERT-PACK-FINAL checkpoint remaining_nodes must be 0")

    if report.get("status") != "PASS" or report.get("rerun") != expected["rerun"]:
        fail(f"S6-CERT-PACK-FINAL audit_report status/rerun mismatch: {report}")
    if report.get("errors") != []:
        fail(f"S6-CERT-PACK-FINAL audit_report has errors: {report.get('errors')}")
    if int(report.get("checked_nodes", -1)) != total_nodes:
        fail(f"S6-CERT-PACK-FINAL audit_report checked_nodes mismatch: {report}")
    if dict(report.get("counts", {})) != {"unsat": total_nodes}:
        fail(f"S6-CERT-PACK-FINAL audit_report counts mismatch: {report.get('counts')}")

    node_rows = certpack_read_csv(run_dir / "nodes.csv")
    if len(node_rows) != total_nodes:
        fail(f"S6-CERT-PACK-FINAL nodes.csv has {len(node_rows)} rows, expected {total_nodes}")
    nodes_by_index: dict[int, dict[str, str]] = {}
    for row_no, row in enumerate(node_rows, start=2):
        node_index = certpack_int(row, "node_index", f"nodes.csv:{row_no}")
        if node_index in nodes_by_index:
            fail(f"S6-CERT-PACK-FINAL nodes.csv duplicate node_index {node_index}")
        if not (start_offset <= node_index < end_offset):
            fail(f"S6-CERT-PACK-FINAL nodes.csv node_index {node_index} out of range")
        if row.get("answer") != "unsat":
            fail(f"S6-CERT-PACK-FINAL nodes.csv node {node_index} answer {row.get('answer')!r} is not unsat")
        if certpack_int(row, "fixed_count", f"nodes.csv:{row_no}") != 9:
            fail(f"S6-CERT-PACK-FINAL nodes.csv node {node_index} fixed_count is not 9")
        nodes_by_index[node_index] = row
    missing_nodes = sorted(set(range(start_offset, end_offset)) - set(nodes_by_index))
    if missing_nodes:
        fail(f"S6-CERT-PACK-FINAL nodes.csv missing nodes; first missing={missing_nodes[:10]}")

    domains = branch3_live_frontier_domains(BRANCH3_REFERENCE_DEPTH)
    if len(domains) != expected["frontier_total"]:
        fail(f"S6-CERT-PACK-FINAL generated frontier has {len(domains)} nodes, expected {expected['frontier_total']}")
    for node_index in range(start_offset, end_offset):
        fixed_count, fixed_signature = fixed_signature_from_domain(domains[node_index])
        if fixed_count != 9:
            fail(f"S6-CERT-PACK-FINAL generated node {node_index} fixed_count {fixed_count} != 9")
        if nodes_by_index[node_index].get("fixed_signature") != fixed_signature:
            fail(f"S6-CERT-PACK-FINAL node {node_index} fixed_signature mismatch")

    chunk_rows = certpack_read_csv(run_dir / "chunks.csv")
    window_rows = certpack_read_csv(run_dir / "windows.csv")
    if len(chunk_rows) != expected["chunks_completed"]:
        fail(f"S6-CERT-PACK-FINAL chunks.csv has {len(chunk_rows)} rows, expected {expected['chunks_completed']}")
    if len(window_rows) != expected["windows_completed"]:
        fail(f"S6-CERT-PACK-FINAL windows.csv has {len(window_rows)} rows, expected {expected['windows_completed']}")
    certpack_validate_chunks(chunk_rows, nodes_by_index, start_offset, end_offset)
    certpack_validate_windows(window_rows, nodes_by_index, start_offset, end_offset)
    certpack_validate_sat_unknown_logs(run_dir, nodes_by_index, expected["target_rawH"])
    rerun_summary = certpack_validate_full_rerun(certpack_read_csv(run_dir / "audit_rerun.csv"), start_offset, end_offset)

    return {
        "run_dir": str(run_dir.resolve()),
        "start_offset": start_offset,
        "end_offset": end_offset,
        "checked_nodes": total_nodes,
        "unsat_nodes": total_nodes,
        "sat_nodes": 0,
        "unknown_nodes": 0,
        "frontier_total": len(domains),
        "chunks": len(chunk_rows),
        "windows": len(window_rows),
        "timeout_ms": expected["timeout_ms"],
        "target_rawH": expected["target_rawH"],
        **rerun_summary,
    }


# ---------------------------------------------------------------------------
# S6-H1: audited unrestricted H range closure
# ---------------------------------------------------------------------------

H1_REQUIRED_FILES = (
    "checkpoint.json",
    "chunks.csv",
    "violations.csv",
    "audit_report.json",
    "audit_rerun.csv",
)


def h1_validate_chunks(rows: list[dict[str, str]], checkpoint: dict[str, object]) -> dict[str, object]:
    start = int(checkpoint["start_index"])
    end = int(checkpoint["end_index"])
    expected_next = start
    cumulative_points = 0
    cumulative_upper = 0
    cumulative_lower = 0
    global_min: int | None = None
    global_max: int | None = None
    global_min_word = ""
    global_max_word = ""
    global_min_count = 0
    global_max_count = 0
    total_core_seconds = 0.0

    for pos, row in enumerate(rows):
        label = f"h1 chunks.csv:{pos + 2}"
        if certpack_int(row, "chunk_index", label) != pos:
            fail(f"S6-H1 {label} chunk_index mismatch")
        row_start = certpack_int(row, "start_index", label)
        row_end = certpack_int(row, "end_index", label)
        points = certpack_int(row, "points", label)
        if row_start != expected_next:
            fail(f"S6-H1 {label} start_index {row_start} != expected {expected_next}")
        if points != row_end - row_start:
            fail(f"S6-H1 {label} points {points} != interval length {row_end - row_start}")
        if certpack_int(row, "next_index", label) != row_end:
            fail(f"S6-H1 {label} next_index != end_index")
        min_rawH = certpack_int(row, "min_rawH", label)
        max_rawH = certpack_int(row, "max_rawH", label)
        min_count = certpack_int(row, "min_count", label)
        max_count = certpack_int(row, "max_count", label)
        if certpack_int(row, "min_H_tot", label) != 6 * min_rawH:
            fail(f"S6-H1 {label} min_H_tot != 6*min_rawH")
        if certpack_int(row, "max_H_tot", label) != 6 * max_rawH:
            fail(f"S6-H1 {label} max_H_tot != 6*max_rawH")
        if len(row.get("min_word", "")) != 21 or len(row.get("max_word", "")) != 21:
            fail(f"S6-H1 {label} endpoint word length mismatch")

        cumulative_points += points
        cumulative_upper += certpack_int(row, "upper_violations", label)
        cumulative_lower += certpack_int(row, "lower_violations", label)
        total_core_seconds += certpack_float(row, "seconds_core", label)
        if global_min is None or min_rawH < global_min:
            global_min = min_rawH
            global_min_word = row["min_word"]
            global_min_count = min_count
        elif min_rawH == global_min:
            global_min_count += min_count
        if global_max is None or max_rawH > global_max:
            global_max = max_rawH
            global_max_word = row["max_word"]
            global_max_count = max_count
        elif max_rawH == global_max:
            global_max_count += max_count

        expected_cumulative = {
            "cumulative_points": cumulative_points,
            "cumulative_upper_violations": cumulative_upper,
            "cumulative_lower_violations": cumulative_lower,
            "cumulative_min_rawH": global_min,
            "cumulative_max_rawH": global_max,
        }
        for key, expected in expected_cumulative.items():
            if certpack_int(row, key, label) != int(expected):
                fail(f"S6-H1 {label} {key} mismatch")
        if row.get("cumulative_min_word") != global_min_word:
            fail(f"S6-H1 {label} cumulative_min_word mismatch")
        if row.get("cumulative_max_word") != global_max_word:
            fail(f"S6-H1 {label} cumulative_max_word mismatch")
        expected_next = row_end

    if expected_next != end:
        fail(f"S6-H1 chunks coverage ended at {expected_next}, expected {end}")
    if cumulative_points != int(checkpoint["checked_points"]):
        fail("S6-H1 chunks cumulative points disagree with checkpoint")
    if cumulative_upper != int(checkpoint["upper_violations"]) or cumulative_lower != int(checkpoint["lower_violations"]):
        fail("S6-H1 chunks violation totals disagree with checkpoint")
    if global_min != int(checkpoint["min_rawH"]) or global_max != int(checkpoint["max_rawH"]):
        fail("S6-H1 chunks extrema disagree with checkpoint")
    if global_min_word != checkpoint["min_word"] or global_max_word != checkpoint["max_word"]:
        fail("S6-H1 chunks endpoint words disagree with checkpoint")

    return {
        "chunks": len(rows),
        "checked_points": cumulative_points,
        "upper_violations": cumulative_upper,
        "lower_violations": cumulative_lower,
        "min_rawH": global_min,
        "max_rawH": global_max,
        "min_H_tot": None if global_min is None else 6 * global_min,
        "max_H_tot": None if global_max is None else 6 * global_max,
        "min_word": global_min_word,
        "max_word": global_max_word,
        "min_count": global_min_count,
        "max_count": global_max_count,
        "total_core_seconds": round(total_core_seconds, 3),
    }


def h1_validate_audit_rerun(rows: list[dict[str, str]], expected_rows: int) -> dict[str, object]:
    if len(rows) < expected_rows:
        fail(f"S6-H1 audit_rerun.csv has {len(rows)} rows, expected at least {expected_rows}")
    segment = rows[-expected_rows:] if expected_rows else []
    max_seconds = 0.0
    total_seconds = 0.0
    for row_no, row in enumerate(segment, start=len(rows) - len(segment) + 2):
        if row.get("mismatch") not in ("0", "", "False", "false"):
            fail(f"S6-H1 audit_rerun.csv:{row_no} mismatch={row.get('mismatch')!r}")
        seconds = float(row.get("seconds") or 0.0)
        max_seconds = max(max_seconds, seconds)
        total_seconds += seconds
        if row.get("expected_min_rawH") != row.get("rerun_min_rawH"):
            fail(f"S6-H1 audit_rerun.csv:{row_no} min_rawH mismatch")
        if row.get("expected_max_rawH") != row.get("rerun_max_rawH"):
            fail(f"S6-H1 audit_rerun.csv:{row_no} max_rawH mismatch")
        if row.get("expected_upper_violations") != row.get("rerun_upper_violations"):
            fail(f"S6-H1 audit_rerun.csv:{row_no} upper_violations mismatch")
        if row.get("expected_lower_violations") != row.get("rerun_lower_violations"):
            fail(f"S6-H1 audit_rerun.csv:{row_no} lower_violations mismatch")
    return {
        "rerun_rows": len(segment),
        "rerun_max_seconds": round(max_seconds, 3),
        "rerun_sum_seconds": round(total_seconds, 3),
    }


def h1_eval_audit(run_dir: Path = H1_FINAL_RUN_DIR) -> dict[str, object]:
    run_dir = Path(run_dir)
    for name in H1_REQUIRED_FILES:
        if not (run_dir / name).is_file():
            fail(f"S6-H1 missing required file {run_dir / name}")

    checkpoint = certpack_read_json(run_dir / "checkpoint.json")
    report = certpack_read_json(run_dir / "audit_report.json")
    expected = H1_EXPECTED_RANGE
    checks = {
        "status": "complete",
        "start_index": expected["start_index"],
        "end_index": expected["end_index"],
        "next_index": expected["end_index"],
        "checked_points": expected["checked_points"],
        "chunk_size": expected["chunk_size"],
        "upper_target_rawH": expected["upper_target_rawH"],
        "lower_target_rawH": expected["lower_target_rawH"],
        "upper_violations": expected["upper_violations"],
        "lower_violations": expected["lower_violations"],
        "min_rawH": expected["min_rawH"],
        "max_rawH": expected["max_rawH"],
        "min_H_tot": expected["min_H_tot"],
        "max_H_tot": expected["max_H_tot"],
        "min_word": expected["min_word"],
        "max_word": expected["max_word"],
    }
    for key, value in checks.items():
        if checkpoint.get(key) != value:
            fail(f"S6-H1 checkpoint {key}={checkpoint.get(key)!r}, expected {value!r}")
    if int(checkpoint.get("remaining_points", -1)) != 0:
        fail("S6-H1 checkpoint remaining_points must be 0")

    if report.get("status") != "PASS":
        fail(f"S6-H1 audit_report status mismatch: {report}")
    if report.get("errors") != []:
        fail(f"S6-H1 audit_report has errors: {report.get('errors')}")
    for key in ("checked_points", "chunks", "upper_violations", "lower_violations", "min_count", "max_count"):
        if int(report.get(key, -1)) != int(expected.get(key, report.get(key, -1))):
            fail(f"S6-H1 audit_report {key}={report.get(key)!r}, expected {expected.get(key)!r}")
    if report.get("range_rawH") != [expected["min_rawH"], expected["max_rawH"]]:
        fail(f"S6-H1 audit_report range_rawH mismatch: {report.get('range_rawH')}")
    if report.get("range_H_tot") != [expected["min_H_tot"], expected["max_H_tot"]]:
        fail(f"S6-H1 audit_report range_H_tot mismatch: {report.get('range_H_tot')}")

    chunk_rows = certpack_read_csv(run_dir / "chunks.csv")
    if len(chunk_rows) != expected["chunks"]:
        fail(f"S6-H1 chunks.csv has {len(chunk_rows)} rows, expected {expected['chunks']}")
    chunk_summary = h1_validate_chunks(chunk_rows, checkpoint)
    violation_rows = certpack_read_csv(run_dir / "violations.csv")
    if violation_rows:
        fail(f"S6-H1 violations.csv must be header-only for the default thresholds, got {len(violation_rows)} rows")

    min_metrics = h_metrics_reduced(str(checkpoint["min_word"]))
    max_metrics = h_metrics_reduced(str(checkpoint["max_word"]))
    for key, value in H1_EXPECTED_MIN_METRICS.items():
        if int(min_metrics[key]) != value:
            fail(f"S6-H1 min witness metric {key}={min_metrics[key]}, expected {value}")
    for key, value in H1_EXPECTED_MAX_METRICS.items():
        if int(max_metrics[key]) != value:
            fail(f"S6-H1 max witness metric {key}={max_metrics[key]}, expected {value}")

    rerun_summary = h1_validate_audit_rerun(certpack_read_csv(run_dir / "audit_rerun.csv"), expected["rerun_chunks"])
    return {
        "run_dir": str(run_dir.resolve()),
        "checked_points": chunk_summary["checked_points"],
        "chunks": chunk_summary["chunks"],
        "min_rawH": chunk_summary["min_rawH"],
        "max_rawH": chunk_summary["max_rawH"],
        "min_H_tot": chunk_summary["min_H_tot"],
        "max_H_tot": chunk_summary["max_H_tot"],
        "min_word": chunk_summary["min_word"],
        "max_word": chunk_summary["max_word"],
        "min_count": chunk_summary["min_count"],
        "max_count": chunk_summary["max_count"],
        "upper_violations": chunk_summary["upper_violations"],
        "lower_violations": chunk_summary["lower_violations"],
        "total_core_seconds": chunk_summary["total_core_seconds"],
        "elapsed_seconds": float(checkpoint["elapsed_seconds"]),
        "rerun": expected["rerun"],
        **rerun_summary,
    }


# ---------------------------------------------------------------------------
# S6-H4: audited signed-cancellation frontier classification
# ---------------------------------------------------------------------------

H4_REQUIRED_FILES = (
    "checkpoint.json",
    "chunks.csv",
    "chunk_pairs.csv",
    "pair_counts.csv",
    "rawH_summary.csv",
    "witnesses.csv",
    "audit_report.json",
    "audit_rerun.csv",
)


def h4_parse_int_list(text: str) -> list[int]:
    if not text:
        return []
    return [int(x) for x in str(text).split("/") if x != ""]


def h4_validate_chunk_summary(rows: list[dict[str, str]], checkpoint: dict[str, object]) -> dict[str, object]:
    expected = H4_EXPECTED_RANGE
    if len(rows) != expected["chunks"]:
        fail(f"S6-H4 chunks.csv has {len(rows)} rows, expected {expected['chunks']}")
    expected_next = expected["start_index"]
    total_points = 0
    high_points = 0
    high_pure_points = 0
    high_impure_points = 0
    global_min: int | None = None
    global_max: int | None = None
    global_max_count = 0
    global_max_N: set[int] = set()
    total_core_seconds = 0.0
    for pos, row in enumerate(rows):
        label = f"h4 chunks.csv:{pos + 2}"
        if certpack_int(row, "chunk_index", label) != pos:
            fail(f"S6-H4 {label} chunk_index mismatch")
        row_start = certpack_int(row, "start_index", label)
        row_end = certpack_int(row, "end_index", label)
        points = certpack_int(row, "points", label)
        if row_start != expected_next:
            fail(f"S6-H4 {label} start_index {row_start} != expected {expected_next}")
        if points != row_end - row_start:
            fail(f"S6-H4 {label} points mismatch")
        if certpack_int(row, "next_index", label) != row_end:
            fail(f"S6-H4 {label} next_index mismatch")
        min_rawH = certpack_int(row, "min_rawH", label)
        max_rawH = certpack_int(row, "max_rawH", label)
        if certpack_int(row, "min_H_tot", label) != 6 * min_rawH:
            fail(f"S6-H4 {label} min_H_tot != 6*min_rawH")
        if certpack_int(row, "max_H_tot", label) != 6 * max_rawH:
            fail(f"S6-H4 {label} max_H_tot != 6*max_rawH")
        chunk_high = certpack_int(row, "high_points", label)
        chunk_pure = certpack_int(row, "high_pure_points", label)
        chunk_impure = certpack_int(row, "high_impure_points", label)
        if chunk_high != chunk_pure + chunk_impure:
            fail(f"S6-H4 {label} high_points != pure+impure")
        total_points += points
        high_points += chunk_high
        high_pure_points += chunk_pure
        high_impure_points += chunk_impure
        total_core_seconds += certpack_float(row, "seconds_core", label)
        if global_min is None or min_rawH < global_min:
            global_min = min_rawH
        if global_max is None or max_rawH > global_max:
            global_max = max_rawH
            global_max_count = certpack_int(row, "max_count", label)
            global_max_N = set(h4_parse_int_list(row.get("max_N_neg_values", "")))
        elif max_rawH == global_max:
            global_max_count += certpack_int(row, "max_count", label)
            global_max_N.update(h4_parse_int_list(row.get("max_N_neg_values", "")))
        expected_next = row_end
    if expected_next != expected["end_index"]:
        fail(f"S6-H4 chunks coverage ended at {expected_next}, expected {expected['end_index']}")
    checks = {
        "checked_points": total_points,
        "high_points": high_points,
        "high_pure_points": high_pure_points,
        "high_impure_points": high_impure_points,
        "min_rawH": global_min,
        "max_rawH": global_max,
        "max_count": global_max_count,
    }
    for key, value in checks.items():
        if int(checkpoint[key]) != int(value):
            fail(f"S6-H4 chunks {key}={value}, checkpoint has {checkpoint[key]}")
        if int(value) != int(expected[key]):
            fail(f"S6-H4 chunks {key}={value}, expected {expected[key]}")
    if sorted(global_max_N) != expected["max_N_neg_values"]:
        fail(f"S6-H4 chunks max_N_neg_values={sorted(global_max_N)}, expected {expected['max_N_neg_values']}")
    return {
        **checks,
        "chunks": len(rows),
        "total_core_seconds": round(total_core_seconds, 3),
        "max_N_neg_values": sorted(global_max_N),
    }


def h4_validate_audit_rerun(rows: list[dict[str, str]], expected_rows: int) -> dict[str, object]:
    if len(rows) < expected_rows:
        fail(f"S6-H4 audit_rerun.csv has {len(rows)} rows, expected at least {expected_rows}")
    segment = rows[-expected_rows:] if expected_rows else []
    max_seconds = 0.0
    total_seconds = 0.0
    for row_no, row in enumerate(segment, start=len(rows) - len(segment) + 2):
        if row.get("mismatch") not in ("0", "", "False", "false"):
            fail(f"S6-H4 audit_rerun.csv:{row_no} mismatch={row.get('mismatch')!r}")
        seconds = float(row.get("seconds") or 0.0)
        max_seconds = max(max_seconds, seconds)
        total_seconds += seconds
        for key in ("min_rawH", "max_rawH", "high_points", "high_pure_points", "high_impure_points"):
            if row.get(f"expected_{key}") != row.get(f"rerun_{key}"):
                fail(f"S6-H4 audit_rerun.csv:{row_no} {key} mismatch")
        if row.get("expected_pair_signature") != row.get("rerun_pair_signature"):
            fail(f"S6-H4 audit_rerun.csv:{row_no} pair signature mismatch")
    return {
        "rerun_rows": len(segment),
        "rerun_max_seconds": round(max_seconds, 3),
        "rerun_sum_seconds": round(total_seconds, 3),
    }


def h4_classifier_audit(run_dir: Path = H4_FINAL_RUN_DIR) -> dict[str, object]:
    run_dir = Path(run_dir)
    for name in H4_REQUIRED_FILES:
        if not (run_dir / name).is_file():
            fail(f"S6-H4 missing required file {run_dir / name}")

    checkpoint = certpack_read_json(run_dir / "checkpoint.json")
    report = certpack_read_json(run_dir / "audit_report.json")
    expected = H4_EXPECTED_RANGE
    checks = {
        "status": "complete",
        "start_index": expected["start_index"],
        "end_index": expected["end_index"],
        "next_index": expected["end_index"],
        "checked_points": expected["checked_points"],
        "chunk_size": expected["chunk_size"],
        "pair_min_rawH": expected["pair_min_rawH"],
        "witness_min_rawH": expected["witness_min_rawH"],
        "min_rawH": expected["min_rawH"],
        "max_rawH": expected["max_rawH"],
        "min_H_tot": expected["min_H_tot"],
        "max_H_tot": expected["max_H_tot"],
        "min_word": expected["min_word"],
        "max_word": expected["max_word"],
        "min_count": expected["min_count"],
        "max_count": expected["max_count"],
        "high_points": expected["high_points"],
        "high_pure_points": expected["high_pure_points"],
        "high_impure_points": expected["high_impure_points"],
        "pair_count": expected["pair_count"],
        "stored_witnesses": expected["stored_witnesses"],
        "witness_overflow": expected["witness_overflow"],
    }
    for key, value in checks.items():
        if checkpoint.get(key) != value:
            fail(f"S6-H4 checkpoint {key}={checkpoint.get(key)!r}, expected {value!r}")
    if checkpoint.get("max_N_neg_values") != expected["max_N_neg_values"]:
        fail(f"S6-H4 checkpoint max_N_neg_values mismatch: {checkpoint.get('max_N_neg_values')}")
    if int(checkpoint.get("remaining_points", -1)) != 0:
        fail("S6-H4 checkpoint remaining_points must be 0")

    if report.get("status") != "PASS" or report.get("errors") != []:
        fail(f"S6-H4 audit_report status/errors mismatch: {report}")
    if report.get("expect_default_h4") is not True:
        fail("S6-H4 audit_report must be produced with --expect-default-h4")
    for key in ("checked_points", "chunks", "high_points", "high_pure_points", "high_impure_points", "max_count", "pair_count", "witness_rows"):
        expected_key = "stored_witnesses" if key == "witness_rows" else key
        if int(report.get(key, -1)) != int(expected[expected_key]):
            fail(f"S6-H4 audit_report {key}={report.get(key)!r}, expected {expected[expected_key]!r}")
    if report.get("range_rawH") != [expected["min_rawH"], expected["max_rawH"]]:
        fail(f"S6-H4 audit_report range_rawH mismatch: {report.get('range_rawH')}")
    if report.get("range_H_tot") != [expected["min_H_tot"], expected["max_H_tot"]]:
        fail(f"S6-H4 audit_report range_H_tot mismatch: {report.get('range_H_tot')}")
    if report.get("rawH_values") != expected["rawH_values"]:
        fail(f"S6-H4 audit_report rawH_values mismatch: {report.get('rawH_values')}")
    if int(report.get("rerun_chunks", 0)) < expected["rerun_chunks"]:
        fail(f"S6-H4 audit_report rerun_chunks={report.get('rerun_chunks')}, expected at least {expected['rerun_chunks']}")
    if int(report.get("verified_witnesses", 0)) != expected["stored_witnesses"]:
        fail("S6-H4 audit_report must verify all witnesses")

    chunk_summary = h4_validate_chunk_summary(certpack_read_csv(run_dir / "chunks.csv"), checkpoint)

    pair_rows = certpack_read_csv(run_dir / "pair_counts.csv")
    if len(pair_rows) != 1:
        fail(f"S6-H4 pair_counts.csv must contain exactly one row, got {len(pair_rows)}")
    pair_row = pair_rows[0]
    for key, value in H4_EXPECTED_PAIR.items():
        got: object = pair_row.get(key, "")
        if key != "first_word":
            got = int(got)
        if got != value:
            fail(f"S6-H4 pair_counts {key}={got!r}, expected {value!r}")

    raw_rows = certpack_read_csv(run_dir / "rawH_summary.csv")
    if len(raw_rows) != 1:
        fail(f"S6-H4 rawH_summary.csv must contain exactly one row, got {len(raw_rows)}")
    raw_row = raw_rows[0]
    raw_checks = {
        "rawH": 1217,
        "H_tot": 7302,
        "count": 12,
        "pure_count": 0,
        "impure_count": 12,
        "pair_count": 1,
        "min_N_neg": 3,
        "max_N_neg": 3,
        "first_index": 265731,
    }
    for key, value in raw_checks.items():
        if certpack_int(raw_row, key, "h4 rawH_summary.csv:2") != value:
            fail(f"S6-H4 rawH_summary {key} mismatch")
    if raw_row.get("N_neg_values") != "3" or raw_row.get("first_word") != H4_EXPECTED_PAIR["first_word"]:
        fail(f"S6-H4 rawH_summary qualitative fields mismatch: {raw_row}")

    witness_rows = certpack_read_csv(run_dir / "witnesses.csv")
    witness_words = tuple(row["word"] for row in witness_rows)
    if witness_words != H4_EXPECTED_WITNESSES:
        fail(f"S6-H4 witness word list mismatch: {witness_words}")
    expected_metrics = {
        **H1_EXPECTED_MAX_METRICS,
        "H_pos": 7308,
        "H_neg_abs": 6,
        "h_loc_min": -2,
        "h_loc_max": 18,
    }
    for row_no, row in enumerate(witness_rows, start=2):
        metrics = h_metrics_reduced(row["word"])
        for key, value in expected_metrics.items():
            if int(metrics[key]) != value:
                fail(f"S6-H4 witnesses.csv:{row_no} metric {key}={metrics[key]}, expected {value}")
        for key in ("rawH", "H_tot", "N_neg", "H_pos", "H_neg_abs", "h_loc_min", "h_loc_max"):
            if certpack_int(row, key, f"h4 witnesses.csv:{row_no}") != int(metrics[key]):
                fail(f"S6-H4 witnesses.csv:{row_no} emitted {key} mismatch")

    rerun_summary = h4_validate_audit_rerun(certpack_read_csv(run_dir / "audit_rerun.csv"), expected["rerun_chunks"])
    return {
        "run_dir": str(run_dir.resolve()),
        "checked_points": chunk_summary["checked_points"],
        "chunks": chunk_summary["chunks"],
        "min_rawH": chunk_summary["min_rawH"],
        "max_rawH": chunk_summary["max_rawH"],
        "min_H_tot": expected["min_H_tot"],
        "max_H_tot": expected["max_H_tot"],
        "high_points": chunk_summary["high_points"],
        "high_pure_points": chunk_summary["high_pure_points"],
        "high_impure_points": chunk_summary["high_impure_points"],
        "pair_count": expected["pair_count"],
        "max_count": expected["max_count"],
        "max_N_neg_values": expected["max_N_neg_values"],
        "witness_rows": len(witness_rows),
        "total_core_seconds": chunk_summary["total_core_seconds"],
        "elapsed_seconds": float(checkpoint["elapsed_seconds"]),
        "rerun": expected["rerun"],
        **rerun_summary,
    }


# ---------------------------------------------------------------------------
# Global metric assembly
# ---------------------------------------------------------------------------


def h_metrics_from_rows(rows: list[dict[str, int | str]]) -> dict[str, int]:
    rawI = sum(int(r["dI"]) for r in rows)
    rawB = sum(int(r["dB"]) for r in rows)
    rawH = rawI - rawB
    H = [int(r["h"]) for r in rows]
    blocks = {b: 0 for b in BLOCK_ORDER}
    for r in rows:
        blocks[str(r["block"])] += int(r["h"])
    return {
        "rawI": rawI,
        "rawB": rawB,
        "rawH": rawH,
        "I_tot": 6 * rawI,
        "B_tot": 6 * rawB,
        "H_tot": 6 * rawH,
        "H_pos": 3 * sum(h for h in H if h > 0),
        "H_neg_abs": 3 * sum(-h for h in H if h < 0),
        "N_neg": 3 * sum(1 for h in H if h < 0),
        "h_loc_min": min(H),
        "h_loc_max": max(H),
        "H_RRR": 3 * blocks["RRR"],
        "H_RRS": 3 * blocks["RRS"],
        "H_RSR": 3 * blocks["RSR"],
        "H_SRR": 3 * blocks["SRR"],
        "H_DIST": 3 * blocks["DIST"],
    }


def h_metrics_reduced(x: str) -> dict[str, int]:
    return h_metrics_from_rows(local_reduced_records(x))


def h_metrics_certificate_interface(x: str) -> dict[str, int]:
    return h_metrics_from_rows(local_certificate_interface_records(x))


# ---------------------------------------------------------------------------
# Static support/read-pattern summaries for S6-RED
# ---------------------------------------------------------------------------


def M_support(s: int, X_vals: set[int], Y_vals: set[int], X_cells: set[tuple] | None = None, Y_cells: set[tuple] | None = None) -> tuple[set[int], set[tuple]]:
    s %= 3
    cells = set(X_cells or set()) | set(Y_cells or set())
    vals: set[int] = set()
    if s == 1:
        for x, y in product(X_vals, Y_vals):
            cells.add(("A", x % 3, y % 3))
        vals = set(S)
    elif s == 2:
        for x, y in product(X_vals, Y_vals):
            cells.add(("B", x % 3, y % 3))
        vals = set(S)
    else:
        for x, y in product(X_vals, Y_vals):
            if x % 3 == y % 3:
                cells.add(("d", x % 3))
                vals.update(S)
            else:
                vals.add(comp(x, y))
    return vals, cells


def left_signature_support(c: int) -> set[tuple]:
    cells: set[tuple] = set()
    for u, ell in product(S, S):
        _, cs = M_support(u, {c}, {ell})
        cells |= cs
    return cells


def continuation_signature_support(s: int, alpha: int, z: int) -> set[tuple]:
    cells: set[tuple] = set()
    for u, ell in product(S, S):
        inner_vals, inner_cells = M_support(u - s, {(z - s) % 3}, {(ell - s) % 3})
        outer_second_vals = {(s + v) % 3 for v in inner_vals}
        _, outer_cells = M_support(s, {alpha % 3}, outer_second_vals, set(), inner_cells)
        cells |= outer_cells
    return cells


def support_class(cells: set[tuple]) -> tuple[str, str, int]:
    off = "".join(sorted({c[0] for c in cells if c[0] in ("A", "B")})) or "none"
    diag = "yes" if any(c[0] == "d" for c in cells) else "no"
    return off, diag, len(cells)


def front_read_pattern(b: int, t: int) -> tuple[str, str, str, str, str]:
    roles = (family(b), family(t - b), family(t), family(b))
    fam_set = "".join(sorted(set(roles)))
    return (*roles, fam_set)


def cert_if_census() -> dict[str, int]:
    x_blocks = 21
    mu_blocks = 27
    l_blocks = 3 * 9
    c_inner_blocks = 27 * 9
    c_shift_blocks = 27 * 9
    c_blocks = 27 * 9
    local_scalar_blocks = 243 * 5  # xy, yz, zR=b+yz, epL, epR
    ternary_blocks_total = x_blocks + mu_blocks + l_blocks + c_inner_blocks + c_shift_blocks + c_blocks + local_scalar_blocks
    dl_entries = 3 * 3
    dc_entries = 27 * 27
    dl_comparisons = dl_entries * 9
    dc_comparisons = dc_entries * 9
    comparisons_total = dl_comparisons + dc_comparisons
    return {
        "normal_coordinate_blocks": x_blocks,
        "normal_coordinate_booleans": 3 * x_blocks,
        "mu_table_read_blocks": mu_blocks,
        "mu_table_read_booleans": 3 * mu_blocks,
        "left_signature_blocks": l_blocks,
        "left_signature_booleans": 3 * l_blocks,
        "continuation_inner_blocks": c_inner_blocks,
        "continuation_shift_blocks": c_shift_blocks,
        "continuation_blocks": c_blocks,
        "continuation_booleans": 3 * c_blocks,
        "continuation_aux_blocks": c_inner_blocks + c_shift_blocks,
        "local_scalar_blocks": local_scalar_blocks,
        "local_scalar_booleans": 3 * local_scalar_blocks,
        "ternary_onehot_blocks_total": ternary_blocks_total,
        "ternary_onehot_booleans_total": 3 * ternary_blocks_total,
        "DL_entries": dl_entries,
        "DC_entries": dc_entries,
        "distance_entries_total": dl_entries + dc_entries,
        "DL_position_comparisons": dl_comparisons,
        "DC_position_comparisons": dc_comparisons,
        "distance_position_comparisons_total": comparisons_total,
        "distance_mismatch_booleans_if_linearized": comparisons_total,
        "distance_overlap_booleans_if_linearized": 3 * comparisons_total,
        "DC_selector_cases": 243 * 9,
        "DL_selector_cases": 243 * 9,
        "selector_cases_total": 243 * 18,
        "selected_local_distance_vars": 243 * 2,
        "local_h_vars": 243,
        "pure_inequalities": 243,
        "block_sum_vars": 5,
        "global_objective_vars": 1,
    }



# ---------------------------------------------------------------------------
# S6-CERT-ENGINE-0: exact vectorized evaluator on controlled finite domains
# ---------------------------------------------------------------------------

ENGINE0_EXPECTED = {
    "column_blind_x_Delta": {
        "points": 243,
        "H_min": 1836,
        "H_max": 7302,
        "H_max_count": 12,
        "pure_count": 159,
        "pure_max": 7020,
        "pure_max_count": 6,
        "H_gt_7020_count": 12,
        "H_gt_7020_pure_count": 0,
        "H_eq_7302_N_neg": 3,
    },
    "affine_x_Delta": {
        "points": 19683,
        "H_min": -2268,
        "H_max": 7302,
        "H_max_count": 12,
        "pure_count": 723,
        "pure_max": 7020,
        "pure_max_count": 6,
        "H_gt_7020_count": 12,
        "H_gt_7020_pure_count": 0,
        "H_eq_7302_N_neg": 3,
    },
}


def require_numpy():
    try:
        import numpy as np  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        fail(
            "S6-CERT-ENGINE-0/S6-BRANCH-0 requires numpy for the vectorized evaluator. "
            f"Install numpy, pass --skip-engine0 --skip-branch0, or set STAGE6_PYTHON to a Python with numpy. Original error: {exc}"
        )
    return np


def engine0_comp_table():
    np = require_numpy()
    C = np.zeros((3, 3), dtype=np.int8)
    for a, e in product(S, S):
        C[a, e] = comp(a, e)
    return C


def engine0_points_from_x21_words(xs: list[str] | tuple[str, ...]):
    np = require_numpy()
    return np.array([[int(c) for c in x] for x in xs], dtype=np.int8)


def engine0_column_blind_points():
    np = require_numpy()
    X = []
    for a, b in product(S, S):
        for d in product(S, S, S):
            X.append([a] * 9 + [b] * 9 + list(d))
    return np.array(X, dtype=np.int8)


def engine0_affine_functions():
    funcs: list[list[int]] = []
    for c0, cx, cy in product(S, S, S):
        funcs.append([(c0 + cx * a + cy * e) % 3 for a, e in product(S, S)])
    return funcs


def engine0_affine_points():
    np = require_numpy()
    funcs = engine0_affine_functions()
    X = []
    for A in funcs:
        for B in funcs:
            for d in product(S, S, S):
                X.append(list(A) + list(B) + list(d))
    return np.array(X, dtype=np.int8)


def engine0_metrics_batch(X):
    """Vectorized exact S6-RED evaluator for a finite batch of x21 points.

    This is not a numerical relaxation: all operations are finite F3 table reads,
    exact Hamming distances, and exact local pure inequalities.
    """
    np = require_numpy()
    X = np.asarray(X, dtype=np.int8)
    if X.ndim != 2 or X.shape[1] != 21:
        fail(f"engine0_metrics_batch expects an array of shape (n,21), got {X.shape}")
    n = X.shape[0]
    ar = np.arange(n)
    Ctab = engine0_comp_table()
    pairs = [(u, ell) for u in S for ell in S]
    triples = [(s, alpha, z) for s in S for alpha in S for z in S]
    q_list = [(b, t, a, e, f) for b in S for t in S for a in S for e in S for f in S]
    q_blocks = []
    for b, t, _a, _e, _f in q_list:
        q_blocks.append(BLOCK_ORDER.index(block_id(b, t)))

    M = np.empty((n, 3, 3, 3), dtype=np.int8)
    for a, e in product(S, S):
        if a == e:
            M[:, 0, a, e] = X[:, 18 + a]
        else:
            M[:, 0, a, e] = Ctab[a, e]
        M[:, 1, a, e] = X[:, 3 * a + e]
        M[:, 2, a, e] = X[:, 9 + 3 * a + e]

    L = np.empty((n, 3, 9), dtype=np.int8)
    for c in S:
        for pi, (u, ell) in enumerate(pairs):
            L[:, c, pi] = M[:, u, c, ell]

    K = np.empty((n, 27, 9), dtype=np.int8)
    for gi, (s, alpha, z) in enumerate(triples):
        for pi, (u, ell) in enumerate(pairs):
            inner = M[:, (u - s) % 3, (z - s) % 3, (ell - s) % 3]
            second = (s + inner) % 3
            K[:, gi, pi] = M[ar, s, alpha, second]

    DL = np.empty((n, 3, 3), dtype=np.int16)
    for c, cp in product(S, S):
        DL[:, c, cp] = np.sum(L[:, c, :] != L[:, cp, :], axis=1)

    rawI = np.zeros(n, dtype=np.int32)
    rawB = np.zeros(n, dtype=np.int32)
    h_sum = np.zeros(n, dtype=np.int32)
    n_neg = np.zeros(n, dtype=np.int32)
    h_min = np.full(n, 999, dtype=np.int32)
    h_max = np.full(n, -999, dtype=np.int32)
    block_sums = np.zeros((n, 5), dtype=np.int32)

    for qi, (b, t, a, e, f) in enumerate(q_list):
        xy = M[:, b, a, e]
        yz = M[:, (t - b) % 3, (e - b) % 3, (f - b) % 3]
        zR = (b + yz) % 3
        epL = M[ar, t, xy, f]
        epR = M[ar, b, a, zR]
        dB = DL[ar, epL, epR]
        g1 = 9 * t + 3 * xy + f
        g2 = 9 * b + 3 * a + zR
        dI = np.sum(K[ar, g1, :] != K[ar, g2, :], axis=1).astype(np.int32)
        h = 2 * (dI - dB.astype(np.int32))
        rawI += dI
        rawB += dB.astype(np.int32)
        h_sum += h
        n_neg += (h < 0)
        h_min = np.minimum(h_min, h)
        h_max = np.maximum(h_max, h)
        block_sums[:, q_blocks[qi]] += h

    return {
        "rawI": rawI,
        "rawB": rawB,
        "rawH": rawI - rawB,
        "H_tot": 3 * h_sum,
        "N_neg": 3 * n_neg,
        "h_loc_min": h_min,
        "h_loc_max": h_max,
        "H_blocks": 3 * block_sums,
    }


def engine0_summarize_points(X) -> dict[str, object]:
    np = require_numpy()
    metrics = engine0_metrics_batch(X)
    H = metrics["H_tot"]
    N = metrics["N_neg"]
    pure = N == 0
    gt = H > 7020
    if not bool(np.any(pure)):
        fail("engine0_summarize_points found no pure points in the domain")
    pure_max = int(H[pure].max())
    pure_frontier = pure & (H == pure_max)
    H_max = int(H.max())
    H_max_mask = H == H_max
    return {
        "points": int(X.shape[0]),
        "H_min": int(H.min()),
        "H_max": H_max,
        "H_max_count": int(np.sum(H_max_mask)),
        "pure_count": int(np.sum(pure)),
        "pure_max": pure_max,
        "pure_max_count": int(np.sum(pure_frontier)),
        "H_gt_7020_count": int(np.sum(gt)),
        "H_gt_7020_pure_count": int(np.sum(gt & pure)),
        "H_eq_7302_N_neg_values": tuple(sorted({int(x) for x in N[H == 7302]})),
        "pure_frontier_witnesses": tuple(
            "".join(str(int(v)) for v in row)
            for row in X[pure_frontier]
        ),
    }


def engine0_check_summary(label: str, summary: dict[str, object]) -> None:
    expected = ENGINE0_EXPECTED[label]
    for key, value in expected.items():
        if key == "H_eq_7302_N_neg":
            got = summary.get("H_eq_7302_N_neg_values")
            if got != (value,):
                fail(f"S6-CERT-ENGINE-0 {label} expected H=7302 N_neg values {(value,)}, got {got}")
        else:
            got = summary.get(key)
            if got != value:
                fail(f"S6-CERT-ENGINE-0 {label} expected {key}={value}, got {got}")
    if tuple(summary.get("pure_frontier_witnesses", ())) != ENGINE0_PURE_FRONTIER_WITNESSES:
        fail(f"S6-CERT-ENGINE-0 {label} pure frontier witness list mismatch")


def verify_engine0_kernel_against_reduced() -> None:
    xs = list(ENGINE0_PURE_FRONTIER_WITNESSES) + deterministic_samples(16)
    X = engine0_points_from_x21_words(xs)
    metrics = engine0_metrics_batch(X)
    for i, x in enumerate(xs):
        ref = h_metrics_reduced(x)
        for field in ("rawI", "rawB", "rawH", "H_tot", "N_neg", "h_loc_min", "h_loc_max"):
            got = int(metrics[field][i])
            if got != int(ref[field]):
                fail(f"S6-CERT-ENGINE-0 kernel mismatch {field} for x21={x}: got {got}, expected {ref[field]}")
        block_fields = ["H_RRR", "H_RRS", "H_RSR", "H_SRR", "H_DIST"]
        for j, field in enumerate(block_fields):
            got = int(metrics["H_blocks"][i, j])
            if got != int(ref[field]):
                fail(f"S6-CERT-ENGINE-0 kernel block mismatch {field} for x21={x}: got {got}, expected {ref[field]}")
    print(f"PASS S6-CERT-ENGINE-0 vectorized kernel agrees with S6-RED metrics for {len(xs)} points")


def verify_engine0_column_blind() -> None:
    X = engine0_column_blind_points()
    summary = engine0_summarize_points(X)
    engine0_check_summary("column_blind_x_Delta", summary)
    print(
        "PASS S6-CERT-ENGINE-0 column_blind_x_Delta: "
        f"points={summary['points']} range=[{summary['H_min']},{summary['H_max']}] "
        f"pure_max={summary['pure_max']} pure_frontier_count={summary['pure_max_count']}"
    )


def verify_engine0_affine() -> None:
    X = engine0_affine_points()
    summary = engine0_summarize_points(X)
    engine0_check_summary("affine_x_Delta", summary)
    print(
        "PASS S6-CERT-ENGINE-0 affine_x_Delta: "
        f"points={summary['points']} range=[{summary['H_min']},{summary['H_max']}] "
        f"pure_max={summary['pure_max']} pure_frontier_count={summary['pure_max_count']}"
    )

# ---------------------------------------------------------------------------
# S6-SMT-0: finite-domain SMT interface smoke
# ---------------------------------------------------------------------------

SMT0_COLUMN_BLIND_GT_RAW_H = 1171
SMT0_COLUMN_BLIND_FRONTIER_RAW_H = 1170


def require_z3():
    try:
        import z3  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        fail(
            "S6-SMT-0 requires z3-solver for the finite-domain SMT interface. "
            "Install it in the project venv with: .venv/bin/python -m pip install z3-solver. "
            f"Original error: {exc}"
        )
    return z3


def smt0_select3(z3, selector, vals):
    return z3.If(selector == 0, vals[0], z3.If(selector == 1, vals[1], vals[2]))


def smt0_column_blind_query(target_rawH: int, timeout_ms: int = 10000) -> dict[str, object]:
    """Check column-blind pure feasibility with an exact finite-domain SMT model.

    This is intentionally a small solver-interface smoke test, not the global
    Omega-prime certificate. It verifies that the SMT encoding reproduces the
    known controlled pure frontier boundary.
    """
    z3 = require_z3()
    solver = z3.Solver()
    solver.set(timeout=timeout_ms)

    A = z3.Int("A_const")
    B = z3.Int("B_const")
    d = [z3.Int(f"d_{i}") for i in S]
    for var in [A, B, *d]:
        solver.add(var >= 0, var <= 2)

    def mod3(expr):
        return expr % 3

    def neq01(left, right):
        return z3.If(left != right, z3.IntVal(1), z3.IntVal(0))

    def m0(left, right):
        rows = []
        for a in S:
            cols = []
            for e in S:
                cols.append(d[a] if a == e else z3.IntVal(comp(a, e)))
            rows.append(smt0_select3(z3, right, cols))
        return smt0_select3(z3, left, rows)

    def M(s, left, right):
        s %= 3
        if s == 1:
            return A
        if s == 2:
            return B
        return m0(left, right)

    diffs = []
    for b, t, a, e, f in Q_LIST:
        xy = M(b, z3.IntVal(a), z3.IntVal(e))
        yz = M(t - b, z3.IntVal((e - b) % 3), z3.IntVal((f - b) % 3))
        zR = mod3(b + yz)
        epL = M(t, xy, z3.IntVal(f))
        epR = M(b, z3.IntVal(a), zR)

        dI_terms = []
        dB_terms = []
        for u, ell in PAIR_LIST:
            zw = mod3(t + M(u - t, z3.IntVal((f - t) % 3), z3.IntVal((ell - t) % 3)))
            rhs_inner = mod3(b + M(u - b, yz, z3.IntVal((ell - b) % 3)))
            dI_terms.append(neq01(M(t, xy, zw), M(b, z3.IntVal(a), rhs_inner)))
            dB_terms.append(neq01(M(u, epL, z3.IntVal(ell)), M(u, epR, z3.IntVal(ell))))

        dI = z3.Sum(dI_terms)
        dB = z3.Sum(dB_terms)
        solver.add(dI >= dB)
        diffs.append(dI - dB)

    rawH = z3.Sum(diffs)
    solver.add(rawH >= target_rawH)

    ans = solver.check()
    out: dict[str, object] = {"target_rawH": target_rawH, "answer": str(ans)}
    if ans == z3.sat:
        model = solver.model()
        a_val = model.evaluate(A).as_long()
        b_val = model.evaluate(B).as_long()
        d_val = tuple(model.evaluate(di).as_long() for di in d)
        x = column_blind_x21(a_val, b_val, d_val)
        out["witness"] = x
        out["metrics"] = h_metrics_reduced(x)
    elif ans == z3.unknown:
        out["reason"] = solver.reason_unknown()
    return out


def smt0_column_blind_summary() -> dict[str, object]:
    gt = smt0_column_blind_query(SMT0_COLUMN_BLIND_GT_RAW_H)
    frontier = smt0_column_blind_query(SMT0_COLUMN_BLIND_FRONTIER_RAW_H)
    return {"gt": gt, "frontier": frontier}


# ---------------------------------------------------------------------------
# S6-SMT-1: optional global SMT long-run interface
# ---------------------------------------------------------------------------

SMT1_GLOBAL_GT_RAW_H = 1171


def smt1_global_onehot_pb_context(target_rawH: int = SMT1_GLOBAL_GT_RAW_H, timeout_ms: int = 600000) -> dict[str, object]:
    """Build the reusable global pure high-H onehot-PB SMT context."""
    z3 = require_z3()
    started = time.time()
    X = [[z3.Bool(f"x_{i}_{a}") for a in S] for i in range(21)]
    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    for row in X:
        solver.add(z3.PbEq([(bit, 1) for bit in row], 1))

    def const_oh(a: int):
        return tuple(z3.BoolVal(i == a) for i in S)

    def shift_oh(oh, k: int):
        return tuple(oh[(r - k) % 3] for r in S)

    def cell_oh(s: int, a: int, e: int):
        s %= 3
        a %= 3
        e %= 3
        if s == 1:
            return tuple(X[3 * a + e])
        if s == 2:
            return tuple(X[9 + 3 * a + e])
        if a == e:
            return tuple(X[18 + a])
        return const_oh(comp(a, e))

    def M_oh(s: int, left, right):
        return tuple(
            z3.Or(*[
                z3.And(left[a], right[e], cell_oh(s, a, e)[val])
                for a in S
                for e in S
            ])
            for val in S
        )

    def neq_bool(left, right):
        return z3.Not(z3.Or(*[z3.And(left[i], right[i]) for i in S]))

    weighted_terms = []
    for b, t, a, e, f in Q_LIST:
        xy = M_oh(b, const_oh(a), const_oh(e))
        yz = M_oh(t - b, const_oh((e - b) % 3), const_oh((f - b) % 3))
        zR = shift_oh(yz, b)
        epL = M_oh(t, xy, const_oh(f))
        epR = M_oh(b, const_oh(a), zR)

        local_terms = []
        for u, ell in PAIR_LIST:
            zw = shift_oh(M_oh(u - t, const_oh((f - t) % 3), const_oh((ell - t) % 3)), t)
            rhs_inner = shift_oh(M_oh(u - b, yz, const_oh((ell - b) % 3)), b)
            i_bit = neq_bool(M_oh(t, xy, zw), M_oh(b, const_oh(a), rhs_inner))
            b_bit = neq_bool(M_oh(u, epL, const_oh(ell)), M_oh(u, epR, const_oh(ell)))
            local_terms.append((i_bit, 1))
            local_terms.append((b_bit, -1))
            weighted_terms.append((i_bit, 1))
            weighted_terms.append((b_bit, -1))
        solver.add(z3.PbGe(local_terms, 0))
    solver.add(z3.PbGe(weighted_terms, target_rawH))

    build_seconds = time.time() - started
    return {
        "z3": z3,
        "solver": solver,
        "X": X,
        "encoding": "onehot-pb",
        "target_rawH": target_rawH,
        "timeout_ms": timeout_ms,
        "build_seconds": round(build_seconds, 3),
        "assertions": len(solver.assertions()),
        "weighted_terms": len(weighted_terms),
    }


def smt1_model_word(z3, model, X) -> str:
    return "".join(
        str(next(i for i, bit in enumerate(X[j]) if z3.is_true(model.evaluate(bit))))
        for j in range(21)
    )


def smt1_global_onehot_pb_query(target_rawH: int = SMT1_GLOBAL_GT_RAW_H, timeout_ms: int = 600000) -> dict[str, object]:
    """Run the optional global pure high-H SMT query.

    This is a long-run interface, not a default verifier obligation. The result
    can be SAT, UNSAT, or UNKNOWN. Only SAT witnesses are promoted to exact
    finite metrics here.
    """
    started = time.time()
    ctx = smt1_global_onehot_pb_context(target_rawH=target_rawH, timeout_ms=timeout_ms)
    z3 = ctx["z3"]
    solver = ctx["solver"]
    X = ctx["X"]
    ans = solver.check()
    elapsed_seconds = time.time() - started
    out: dict[str, object] = {
        "encoding": ctx["encoding"],
        "target_rawH": ctx["target_rawH"],
        "timeout_ms": ctx["timeout_ms"],
        "answer": str(ans),
        "build_seconds": ctx["build_seconds"],
        "elapsed_seconds": round(elapsed_seconds, 3),
        "assertions": ctx["assertions"],
        "weighted_terms": ctx["weighted_terms"],
    }
    if ans == z3.sat:
        model = solver.model()
        word = smt1_model_word(z3, model, X)
        out["witness"] = word
        out["metrics"] = h_metrics_reduced(word)
    elif ans == z3.unknown:
        out["reason"] = solver.reason_unknown()
    return out


# ---------------------------------------------------------------------------
# Unified mathematical results table
# ---------------------------------------------------------------------------


def result_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    def add(stage: str, rid: str, kind: str, block: str, obj: str, count: int | str, formula: str, classification: str, status: str, notes: str) -> None:
        rows.append({
            "stage": stage,
            "result_id": rid,
            "kind": kind,
            "block": block,
            "object": obj,
            "count": str(count),
            "formula": formula,
            "classification": classification,
            "status": status,
            "notes": notes,
        })

    for block in BLOCK_ORDER:
        bt = [(b, t) for b, t in product(S, S) if block_id(b, t) == block]
        add(
            "S6-BD", f"BD-{block}", "block_decomposition", block, "Q_" + block,
            len(bt) * 27,
            f"H_{block}=3*sum_{{q in Q_{block}}} h_q; Nneg_{block}=3*#{{q in Q_{block}:h_q<0}}",
            BLOCK_CONDITIONS[block], "done_v0_2_formula", "retained from the v0_2 block decomposition",
        )
    add(
        "S6-BD", "BD-PURE", "constraint_system", "ALL", "local_purity_constraints", 243,
        "N_-=0 iff h(b,t,a,e,f)>=0 for all (b,t,a,e,f) in F3^5",
        "finite_local_inequalities", "done_v0_2_formula", "input interface for Stage-6 certificate",
    )

    add("S6-RED", "RED-L", "reusable_subexpression", "ALL", "L_c", 3,
        "L_c(u,ell)=M_u(c,ell)", "left_translation_signature;9-vector", "done_v0_3_reduction",
        "used only through D_L(c,c')=dist(L_c,L_c')")
    add("S6-RED", "RED-C", "reusable_subexpression", "ALL", "C_{s,alpha,z}", 27,
        "C_{s,alpha,z}(u,ell)=M_s(alpha,s+M_{u-s}(z-s,ell-s))", "continuation_signature;9-vector", "done_v0_3_reduction",
        "used only through D_C between two continuation signatures")
    add("S6-RED", "RED-DL", "distance_bank", "ALL", "D_L", 9,
        "D_L(c,c')=#{(u,ell):L_c(u,ell)!=L_c'(u,ell)}", "ordered_3x3_distance_bank", "done_v0_3_reduction",
        "symmetric; diagonal entries are zero; ordered interface is kept for certificate convenience")
    add("S6-RED", "RED-DC", "distance_bank", "ALL", "D_C", 729,
        "D_C(s,a,z;s',a',z')=dist(C_{s,a,z},C_{s',a',z'})", "ordered_27x27_distance_bank", "done_v0_3_reduction",
        "symmetric; diagonal entries are zero; ordered interface is kept for certificate convenience")
    add("S6-RED", "RED-HLOCAL", "local_formula", "ALL", "h_q", 243,
        "h_q=2*(D_C(t,xy,f;b,a,b+yz)-D_L(epL,epR))", "distance_difference_constraint", "done_v0_3_reduction",
        "xy=M_b(a,e); yz=M_{t-b}(e-b,f-b); zR=b+yz; epL=M_t(xy,f); epR=M_b(a,zR)")

    left_counter = Counter(support_class(left_signature_support(c)) for c in S)
    for (off, diag, n), count in sorted(left_counter.items()):
        add("S6-RED", f"RED-L-SUPPORT-{off}-{diag}-{n}", "support_profile", "ALL", "L_c", count,
            "support(L_c)=A[c,*] union B[c,*] union {d_c}", f"offdiag={off};diag={diag};cells={n}", "done_v0_3_reduction",
            "exact possible support of one left-translation signature")
    cont_counter = Counter(support_class(continuation_signature_support(s, alpha, z)) for s, alpha, z in product(S, S, S))
    for (off, diag, n), count in sorted(cont_counter.items(), key=lambda kv: (kv[0][2], kv[0][0], kv[0][1])):
        add("S6-RED", f"RED-C-SUPPORT-{off}-{diag}-{n}", "support_profile", "ALL", "C_{s,alpha,z}", count,
            "support(C_{s,alpha,z}) computed from the nested M_s expression", f"offdiag={off};diag={diag};cells={n}", "done_v0_3_reduction",
            "exact possible support profile; counts over all 27 continuation signatures")

    pattern_counter: Counter[tuple[str, str, str, str, str, str]] = Counter()
    for b, t, a, e, f in product(S, S, S, S, S):
        xy_f, yz_f, epL_f, epR_f, fam_set = front_read_pattern(b, t)
        pattern_counter[(block_id(b, t), xy_f, yz_f, epL_f, epR_f, fam_set)] += 1
    for (block, xy_f, yz_f, epL_f, epR_f, fam_set), count in sorted(pattern_counter.items(), key=lambda kv: (BLOCK_ORDER.index(kv[0][0]), kv[0][1:])):
        add("S6-RED", f"RED-FRONT-{block}-{xy_f}{yz_f}{epL_f}{epR_f}", "front_read_pattern", block, "xy/yz/epL/epR", count,
            f"xy:{xy_f}; yz:{yz_f}; epL:{epL_f}; epR:{epR_f}", f"front_read_family_set={fam_set}", "done_v0_3_reduction",
            "classification of the four scalar table reads before the mixed signature-distance lookup")
    family_counter = Counter(front_read_pattern(b, t)[-1] for b, t, a, e, f in product(S, S, S, S, S))
    for fam_set, count in sorted(family_counter.items()):
        add("S6-RED", f"RED-CONSTRAINT-FRONT-{fam_set}", "constraint_class", "ALL", "h_q", count,
            "front scalar reads followed by D_C-D_L lookup", f"front_read_family_set={fam_set}", "done_v0_3_reduction",
            "not a primitive one-table theorem; final dependence remains mixed through L/C signatures")
    add("S6-RED", "RED-CONSTRAINT-MIXED", "constraint_class", "ALL", "h_q", 243,
        "h_q=2*(continuation_distance-left_translation_distance)", "mixed_signature_distance", "done_v0_3_reduction",
        "after exact simplification, every local pure inequality uses the L/C mixed interface; no primitive A-only or B-only inequality is claimed")

    c = cert_if_census()
    add("S6-CERT-IF", "CERT-X", "certificate_variable", "ALL", "x21 coordinate one-hot blocks", c["normal_coordinate_blocks"],
        "X_{i,v} in {0,1}; sum_v X_{i,v}=1 for i=0..20", f"booleans={c['normal_coordinate_booleans']}", "done_v0_4_certificate_interface",
        "ternary one-hot encoding of the 21 normal-form coordinates A,B,d")
    add("S6-CERT-IF", "CERT-MU", "certificate_variable", "ALL", "mu_{s,a,e,v}=1 iff M_s(a,e)=v", c["mu_table_read_blocks"],
        "mu encodes every constant table read M_s(a,e)", f"booleans={c['mu_table_read_booleans']}", "done_v0_4_certificate_interface",
        "s=1/s=2 alias A/B cells; s=0 uses diagonal variables or fixed complement")
    add("S6-CERT-IF", "CERT-L", "certificate_variable", "ALL", "lambda_{c,u,ell,v}", c["left_signature_blocks"],
        "lambda_{c,u,ell,v}=mu_{u,c,ell,v}", f"booleans={c['left_signature_booleans']}", "done_v0_4_certificate_interface",
        "27 left-signature coordinates, each ternary one-hot")
    add("S6-CERT-IF", "CERT-C-AUX", "certificate_variable", "ALL", "continuation inner/shift auxiliaries", c["continuation_aux_blocks"],
        "inner=M_{u-s}(z-s,ell-s); shifted=s+inner", f"booleans={3*c['continuation_aux_blocks']}", "done_v0_4_certificate_interface",
        "explicit one-hot auxiliaries for constructing continuation signatures")
    add("S6-CERT-IF", "CERT-C", "certificate_variable", "ALL", "kappa_{s,alpha,z,u,ell,v}", c["continuation_blocks"],
        "kappa_{s,alpha,z,u,ell,v}=1 iff C_{s,alpha,z}(u,ell)=v", f"booleans={c['continuation_booleans']}", "done_v0_4_certificate_interface",
        "243 continuation-signature coordinates, each ternary one-hot")
    add("S6-CERT-IF", "CERT-DL", "distance_bank", "ALL", "D_L", c["DL_entries"],
        "D_L(c,c')=sum_{u,ell} [lambda_c(u,ell)!=lambda_c'(u,ell)]", f"position_comparisons={c['DL_position_comparisons']}", "done_v0_4_certificate_interface",
        "ordered 3x3 Hamming-distance bank")
    add("S6-CERT-IF", "CERT-DC", "distance_bank", "ALL", "D_C", c["DC_entries"],
        "D_C(g,g')=sum_{u,ell} [kappa_g(u,ell)!=kappa_g'(u,ell)]", f"position_comparisons={c['DC_position_comparisons']}", "done_v0_4_certificate_interface",
        "ordered 27x27 Hamming-distance bank for g=(s,alpha,z)")
    add("S6-CERT-IF", "CERT-LOCAL", "local_interface", "ALL", "xy,yz,zR,epL,epR", c["local_scalar_blocks"],
        "xy=M_b(a,e); yz=M_{t-b}(e-b,f-b); zR=b+yz; epL=M_t(xy,f); epR=M_b(a,zR)", f"booleans={c['local_scalar_booleans']}", "done_v0_4_certificate_interface",
        "five derived ternary scalars for each local q")
    add("S6-CERT-IF", "CERT-SELECT-DC", "selector_layer", "ALL", "selected D_C(q)", c["DC_selector_cases"],
        "Theta^C_{q,r,z}=1 iff xy_q=r and zR_q=z; select D_C((t,r,f),(b,a,z))", "9_cases_per_q", "done_v0_4_certificate_interface",
        "engine-neutral selector for dI_q")
    add("S6-CERT-IF", "CERT-SELECT-DL", "selector_layer", "ALL", "selected D_L(q)", c["DL_selector_cases"],
        "Theta^L_{q,r,s}=1 iff epL_q=r and epR_q=s; select D_L(r,s)", "9_cases_per_q", "done_v0_4_certificate_interface",
        "engine-neutral selector for dB_q")
    add("S6-CERT-IF", "CERT-PURE", "constraint_system", "ALL", "pure inequalities", c["pure_inequalities"],
        "dI_q>=dB_q for all q in F3^5", "exact_Nneg_zero_interface", "done_v0_4_certificate_interface",
        "equivalent to h_q>=0 for all q")
    add("S6-CERT-IF", "CERT-OBJ", "objective_interface", "ALL", "H_tot and block sums", c["block_sum_vars"] + c["global_objective_vars"],
        "H_tot=6*sum_q(dI_q-dB_q); H_beta=3*sum_{q in Q_beta} h_q", "linear_after_selected_distances", "done_v0_4_certificate_interface",
        "objective interface for H1/H2 certificate engines")
    add("S6-CERT-IF", "CERT-CENSUS-TERNARY", "interface_size", "ALL", "canonical ternary one-hot layer", c["ternary_onehot_blocks_total"],
        "X + mu + lambda + continuation auxiliaries + kappa + local scalar blocks", f"booleans={c['ternary_onehot_booleans_total']}", "done_v0_4_certificate_interface",
        "symbolic portable interface; aliases can be inlined by a solver")
    add("S6-CERT-IF", "CERT-CENSUS-DIST", "interface_size", "ALL", "distance comparison layer", c["distance_position_comparisons_total"],
        "DL/DC Hamming position comparisons", f"mismatch_booleans_if_linearized={c['distance_mismatch_booleans_if_linearized']};overlap_booleans_if_linearized={c['distance_overlap_booleans_if_linearized']}", "done_v0_4_certificate_interface",
        "SAT/MILP linearizations may use these or more compact table constraints")

    add("S6-CERT-ENGINE-0", "ENGINE0-KERNEL", "certificate_engine", "ALL", "vectorized exact S6-RED evaluator", 243,
        "evaluates all h_q, H_tot, N_-, and block sums from finite F3 table reads", "exact_batch_evaluator", "done_v0_5_controlled_engine",
        "used for exact controlled-domain certificates; not a relaxation")
    for domain, title in [("column_blind_x_Delta", "column-blind x Delta"), ("affine_x_Delta", "affine x Delta")]:
        e = ENGINE0_EXPECTED[domain]
        add("S6-CERT-ENGINE-0", f"ENGINE0-{domain}-RANGE", "controlled_domain_certificate", "ALL", title, e["points"],
            f"H_tot range=[{e['H_min']},{e['H_max']}]; H_tot=7302 count={e['H_max_count']}", "exact_controlled_domain", "done_v0_5_controlled_engine",
            f"every H_tot=7302 point has N_-={e['H_eq_7302_N_neg']}")
        add("S6-CERT-ENGINE-0", f"ENGINE0-{domain}-PURE", "controlled_pure_certificate", "ALL", title, e["pure_count"],
            f"max{{H_tot:N_-=0}}={e['pure_max']}; pure frontier count={e['pure_max_count']}", "controlled_pure_frontier", "done_v0_5_controlled_engine",
            f"H_tot>7020 count={e['H_gt_7020_count']}; pure among H_tot>7020={e['H_gt_7020_pure_count']}")
    add("S6-CERT-ENGINE-0", "ENGINE0-PURE-WITNESSES", "controlled_witness_set", "ALL", "controlled pure frontier x21 words", len(ENGINE0_PURE_FRONTIER_WITNESSES),
        ";".join(ENGINE0_PURE_FRONTIER_WITNESSES), "controlled_frontier_witnesses", "done_v0_5_controlled_engine",
        "six symbol-shifted column-blind frontier witnesses; includes PAB and row-complement")

    e1 = engine1_reference_summaries()
    root = e1["root"]
    add("S6-CERT-ENGINE-1", "ENGINE1-INTERVAL-KERNEL", "partial_domain_engine", "ALL", "mask-valued S6-RED interval evaluator", 243,
        "for a partial domain D, computes dI_min/dI_max, dB_min/dB_max, h_min/h_max for every q", "sound_interval_relaxation", "done_v0_6_interval_engine",
        "branch-ready over the 21 ternary coordinates; not a complete global certificate")
    add("S6-CERT-ENGINE-1", "ENGINE1-ROOT-BOUND", "root_interval_bound", "ALL", "unrestricted Omega-prime root node", 243,
        f"H_tot interval=[{root['H_lower']},{root['H_upper']}]; impossible={root['local_impossible']}; forced={root['local_forced']}; unresolved={root['local_unresolved']}",
        "sound_but_not_tight", "done_v0_6_interval_engine", "root upper bound is intentionally a relaxation, so no global theorem is claimed")
    for label, rid, title in [
        ("PAB_leaf", "ENGINE1-PAB-LEAF", "PAB full assignment"),
        ("row_complement_leaf", "ENGINE1-ROWCOMP-LEAF", "row-complement full assignment"),
    ]:
        leaf = e1[label]
        add("S6-CERT-ENGINE-1", rid, "exact_leaf_bound", "ALL", title, 243,
            f"H_tot interval=[{leaf['H_lower']},{leaf['H_upper']}]; impossible={leaf['local_impossible']}; forced={leaf['local_forced']}",
            "leaf_exact_interval", "done_v0_6_interval_engine", "full assignments collapse the interval engine to the exact S6-RED value")
    for label, rid, title in [
        ("radius1_PAB", "ENGINE1-RADIUS1-PAB", "Hamming radius <=1 shell around PAB"),
        ("radius1_row_complement", "ENGINE1-RADIUS1-ROWCOMP", "Hamming radius <=1 shell around row-complement"),
    ]:
        shell = e1[label]
        add("S6-CERT-ENGINE-1", rid, "local_shell_certificate", "ALL", title, shell["points"],
            f"H_tot range=[{shell['H_min']},{shell['H_max']}]; pure_count={shell['pure_count']}; pure_max={shell['pure_max']}; pure_frontier_count={shell['pure_frontier_count']}",
            f"H_max_N_neg_values={shell['all_max_N_neg_values']}", "done_v0_6_interval_engine", "local shell certificate only; it is not a global Omega-prime frontier theorem")
    add("S6-CERT-ENGINE-1", "ENGINE1-SOUNDED-SUBCUBES", "soundness_audit", "ALL", "deterministic partial-domain subcubes", len(deterministic_partial_domains()),
        "for each test subcube, interval h_q/H_tot bounds enclose exact enumeration and pure_impossible/pure_forced flags are checked", "finite_subcube_soundness", "done_v0_6_interval_engine",
        "verification obligation for the interval pruning layer")

    for scout in branch0_expected_interval_scout():
        depth = scout["depth"]
        add("S6-BRANCH-0", f"BRANCH0-SCOUT-D{depth}", "branch_interval_depth_census", "ALL", f"diagonal-first depth {depth} nodes", scout["nodes"],
            f"H_lower_range=[{scout['H_lower_min']},{scout['H_lower_max']}]; H_upper_range=[{scout['H_upper_min']},{scout['H_upper_max']}]; prunable={scout['prunable_nodes']}",
            f"pure_impossible={scout['pure_impossible_nodes']};upper_le_7020={scout['upper_pruned_nodes']};forced_range=[{scout['forced_min']},{scout['forced_max']}]", "done_v0_7_branch0",
            "interval branch-node scout only; shows the current relaxation is sound but too weak for a global proof")
    add("S6-BRANCH-0", "BRANCH0-SCOUT-BARRIER", "branch_diagnostic", "ALL", "current interval relaxation", sum(r["nodes"] for r in branch0_expected_interval_scout()),
        "no node is prunable by pure-impossible or H_upper<=7020 through diagonal-first depth 4", "branch_bounds_too_weak", "done_v0_7_branch0",
        "this is a positive diagnostic for the next increment: stronger pure-aware bounds are needed")
    add("S6-BRANCH-0", "BRANCH0-FRONTIER-R2", "local_shell_certificate", "ALL", "six radius<=2 balls around controlled pure-frontier witnesses", BRANCH0_SHELL_TOTAL_POINTS,
        "H_tot range=[4524,7302]; pure_count=444; pure_max=7020; pure_frontier_count=6; pure_gt_7020=0", "exact_disjoint_hamming_balls;H_eq_7302_N_neg=3", "done_v0_7_branch0",
        "each radius<=2 ball has 883 points, 74 pure points, unique pure frontier center, and no pure point above 7020")

    add("S6-SMT-0", "SMT0-CB-ENCODING", "solver_interface", "ALL", "column-blind x Delta SMT variables", 5,
        "A_const,B_const,d0,d1,d2 in F3; exact local pure inequalities encoded in Z3", "finite_domain_smt_smoke", "done_v0_8_smt0",
        "solver-interface smoke only; not the global Omega-prime certificate")
    add("S6-SMT-0", "SMT0-CB-PURE-GT7020", "controlled_smt_certificate", "ALL", "column-blind pure H_tot>7020 query", 243,
        "pure constraints plus rawH>=1171 is UNSAT", "z3_unsat_controlled_boundary", "done_v0_8_smt0",
        "reproduces the controlled pure frontier upper bound H_tot<=7020 on column-blind x Delta")
    add("S6-SMT-0", "SMT0-CB-FRONTIER7020", "controlled_smt_witness", "ALL", "column-blind pure H_tot>=7020 boundary query", 1,
        "pure constraints plus rawH>=1170 is SAT; witness has H_tot=7020,N_-=0", "z3_sat_frontier_witness", "done_v0_8_smt0",
        "checks the SMT encoding is not vacuous at the controlled pure frontier")
    add("S6-SMT-1", "SMT1-GLOBAL-ONEHOT-PB", "optional_solver_interface", "ALL", "global one-hot pseudo-Boolean SMT runner", 21,
        "x_i in F3 encoded as 63 Booleans; 243 local pure PB constraints; optional rawH target", "global_long_run_interface", "ready_v0_9_smt1",
        "not run by default; intended for controlled long-run attempts at pure H_tot>7020")
    add("S6-SMT-1", "SMT1-GLOBAL-PURE-GT7020", "optional_global_query", "ALL", "global pure H_tot>7020 query", 243,
        "optional query: pure constraints plus rawH>=1171", "global_target_query_open", "target_open",
        "runner may return SAT, UNSAT, or UNKNOWN; no global theorem is claimed from timeout diagnostics")

    b1_diag = branch1_expected_interval_scout("diag_first")[-1]
    b1_int = branch1_expected_interval_scout("interleave_AB_diag_last")[-1]
    add("S6-BRANCH-1", "BRANCH1-DIAG-FIRST-D8", "optional_branch_depth_census", "ALL", "diagonal-first depth 8 nodes", b1_diag["nodes"],
        f"H_lower_range=[{b1_diag['H_lower_min']},{b1_diag['H_lower_max']}]; H_upper_range=[{b1_diag['H_upper_min']},{b1_diag['H_upper_max']}]; prunable={b1_diag['prunable_nodes']}",
        f"pure_impossible={b1_diag['pure_impossible_nodes']};upper_le_7020={b1_diag['upper_pruned_nodes']};forced_range=[{b1_diag['forced_min']},{b1_diag['forced_max']}]",
        "ready_v0_10_branch1", "optional deep scout; first observed pruning by pure-impossible nodes")
    add("S6-BRANCH-1", "BRANCH1-INTERLEAVE-D8", "optional_branch_depth_census", "ALL", "interleaved A/B depth 8 nodes", b1_int["nodes"],
        f"H_lower_range=[{b1_int['H_lower_min']},{b1_int['H_lower_max']}]; H_upper_range=[{b1_int['H_upper_min']},{b1_int['H_upper_max']}]; prunable={b1_int['prunable_nodes']}",
        f"pure_impossible={b1_int['pure_impossible_nodes']};upper_le_7020={b1_int['upper_pruned_nodes']};forced_range=[{b1_int['forced_min']},{b1_int['forced_max']}]",
        "ready_v0_10_branch1", "optional deep scout; order comparison for interval pruning")
    add("S6-BRANCH-1", "BRANCH1-ORDER-COMPARISON", "branch_order_diagnostic", "ALL", "depth 8 order comparison", len(BRANCH1_ORDER_NAMES),
        "diag_first prunable=81 versus interleave_AB_diag_last prunable=8 at depth 8", "branch_order_matters", "ready_v0_10_branch1",
        "both are pure-impossible pruning only; no H_upper<=7020 pruning yet")
    add("S6-BRANCH-2", "BRANCH2-GREEDY-PREFIX-D6", "adaptive_branch_order_diagnostic", "ALL", "greedy interval-score prefix through depth 6", len(BRANCH2_GREEDY_EXPECTED_PREFIX),
        "chosen_order=20,19,18,17,16,15; nodes=729; prunable=0; H_upper_range=[11808,12762]; forced_sum=2702",
        "greedy_score_prefers_diagonal_then_crossrow_tail", "ready_v0_11_branch2",
        "adaptive score uses prunable/pure-impossible/upper-pruned/forced/H_upper lexicographic priority")
    add("S6-BRANCH-2", "BRANCH2-GREEDY-TAIL-B-D8", "adaptive_branch_tail_diagnostic", "ALL", "greedy B-tail depth 8 continuation", 6561,
        "order=20,19,18,17,16,15,14,13; prunable=81; pure_impossible=81; H_upper_range=[11460,12666]",
        "greedy_tail_recovers_depth8_pruning", "ready_v0_11_branch2",
        "same pure-impossible pruning count as diagonal-first depth-8 scout")
    add("S6-BRANCH-2", "BRANCH2-GREEDY-TAIL-A-D8", "adaptive_branch_tail_diagnostic", "ALL", "greedy A-tail depth 8 continuation", 6561,
        "order=20,19,18,8,7,6,5,4; prunable=81; pure_impossible=81; H_upper_range=[11520,12660]",
        "symmetric_greedy_tail_recovers_depth8_pruning", "ready_v0_11_branch2",
        "A-tail and B-tail continuations both reach pure-impossible pruning by depth 8")
    add("S6-BRANCH-3", "BRANCH3-RUNNER", "optional_branch_and_bound_runner", "ALL", "bounded greedy-B-first frontier runner", len(BRANCH3_GREEDY_B_FIRST_ORDER),
        "order=20,19,18,17,...,0; target_H=7020; prune=pure_impossible or H_upper<=7020; supports depth/node/time caps",
        "bounded_frontier_pruning_interface", "ready_v0_12_branch3",
        "not run by default; turns the branch scout into a live-frontier runner")
    add("S6-BRANCH-3", "BRANCH3-GREEDY-B-D9", "optional_frontier_prune_smoke", "ALL", "greedy-B-first live frontier through depth 9", BRANCH3_EXPECTED_D9["live_nodes"],
        "depth=9; generated=29280; cumulative_pruned=981; pure_impossible=981; upper_le_7020=0; live=18540; H_upper_live=[10620,12528]; forced_live=[0,62]",
        "frontier_pruning_not_enough_yet", "ready_v0_12_branch3",
        "reference bounded run; no global theorem is claimed because every live node still has H_upper>7020")
    add("S6-BOUND-1", "BOUND1-SMT-NODE-EVAL", "pure_aware_node_evaluator", "ALL", "reusable SMT context with branch-node assumptions", BOUND1_EXPECTED_SAMPLE["fixed_coordinates_per_node"],
        "global formula=pure constraints plus rawH>=1171; node fixed by singleton-coordinate assumptions; query answers SAT/UNSAT/UNKNOWN",
        "pure_aware_compatibility_evaluator", "ready_v0_13_bound1",
        "not run by default; strengthens interval live nodes using the exact onehot-PB compatibility model")
    add("S6-BOUND-1", "BOUND1-D9-FIRST20-UNSAT", "optional_node_smt_probe", "ALL", "first 20 S6-BRANCH-3 depth-9 live nodes", BOUND1_EXPECTED_SAMPLE["sampled_nodes"],
        "depth=9; sampled=20; UNSAT=20; SAT=0; UNKNOWN=0; fixed_coordinates=9; target_rawH>=1171",
        "smt_prunes_interval_live_nodes", "ready_v0_13_bound1",
        "every sampled interval-live node has no pure H_tot>7020 completion under the exact SMT encoding")
    add("S6-BOUND-2", "BOUND2-BATCH-D9-FIRST81", "optional_batched_node_smt_probe", "ALL", "first 81 S6-BRANCH-3 depth-9 live nodes", BOUND2_EXPECTED_BATCH["batch_nodes"],
        "depth=9; batch=81; unique_signatures=81; cache_hits=0; UNSAT=81; SAT=0; UNKNOWN=0; fixed_coordinates=9; target_rawH>=1171",
        "batched_smt_prunes_interval_live_nodes", "ready_v0_14_bound2",
        "reuses one SMT context and records cache/answer counts for a larger interval-live node batch")
    add("S6-CERT-PACK-0", "CERTPACK0-UNSAT-NODE-SCHEMA", "certificate_pack_schema", "ALL", "assumption UNSAT node pack", BOUND2_EXPECTED_BATCH["certified_unsat_entries"],
        "entry=(node_index,fixed_signature,query=pure_and_rawH_ge_1171,answer=UNSAT); certified=81; noncertified=0",
        "compact_unsat_node_pack", "ready_v0_14_certpack0",
        "schema is recorded in the active table; no separate manifest/log file is created")
    add("S6-BOUND-3", "BOUND3-CHUNK-D9-O0-L162", "optional_chunked_node_smt_probe", "ALL", "S6-BRANCH-3 depth-9 live-node chunk offset 0 limit 162", BOUND3_EXPECTED_CHUNK["batch_nodes"],
        "depth=9; frontier_total=18540; chunk_offset=0; chunk_limit=162; next_offset=162; chunks=115; UNSAT=162; SAT=0; UNKNOWN=0",
        "resumable_smt_chunk_pruning", "ready_v0_15_bound3",
        "extends BOUND2 with explicit offset/limit/next-offset accounting for resumable frontier packs")
    add("S6-CERT-PACK-1", "CERTPACK1-RESUMABLE-CHUNK-SCHEMA", "certificate_pack_schema", "ALL", "resumable assumption UNSAT chunk pack", BOUND3_EXPECTED_CHUNK["certified_unsat_entries"],
        "chunk=(depth=9,offset=0,limit=162,next=162,total=18540); entry=(global_node_index,fixed_signature,query,answer); certified=162; noncertified=0",
        "resumable_unsat_node_pack", "ready_v0_15_certpack1",
        "chunk accounting remains in the active table/verifier interface; no separate package file is created")
    add("S6-BOUND-4", "BOUND4-CHUNK-D9-O162-L162", "optional_chunked_node_smt_probe", "ALL", "S6-BRANCH-3 depth-9 live-node chunk offset 162 limit 162", BOUND4_EXPECTED_CHUNK["batch_nodes"],
        "depth=9; frontier_total=18540; chunk_offset=162; chunk_limit=162; next_offset=324; chunks=115; UNSAT=162; SAT=0; UNKNOWN=0",
        "second_resumable_smt_chunk_pruning", "ready_v0_16_bound4",
        "second consecutive depth-9 SMT chunk; keeps the same resumable pack interface")
    add("S6-CERT-PACK-2", "CERTPACK2-SECOND-CHUNK", "certificate_pack_chunk", "ALL", "second resumable assumption UNSAT chunk", BOUND4_EXPECTED_CHUNK["certified_unsat_entries"],
        "chunk=(depth=9,offset=162,limit=162,next=324,total=18540); certified=162; cumulative_certified=324; SAT=0; UNKNOWN=0",
        "second_resumable_unsat_node_pack", "ready_v0_16_certpack2",
        "records the second chunk result in the active table; no separate package file is created")
    add("S6-BOUND-5", "BOUND5-MULTICHUNK-D9-O0-L162-C2", "optional_multi_chunk_smt_probe", "ALL", "one-context two-chunk S6-BRANCH-3 depth-9 run", BOUND5_EXPECTED_RUN["total_nodes"],
        "depth=9; start_offset=0; chunk_limit=162; chunks=2; next_offset=324; total=324; UNSAT=324; SAT=0; UNKNOWN=0; context_builds=1",
        "one_context_multi_chunk_pruning", "ready_v0_17_bound5",
        "performance runner for longer/full passes; reuses one SMT context across multiple chunks")
    add("S6-CERT-PACK-3", "CERTPACK3-MULTICHUNK-SCHEMA", "certificate_pack_schema", "ALL", "multi-chunk assumption UNSAT pack", BOUND5_EXPECTED_RUN["certified_unsat_entries"],
        "run=(depth=9,start=0,limit=162,chunks=2,next=324,total=18540); certified=324; noncertified=0",
        "multi_chunk_unsat_node_pack", "ready_v0_17_certpack3",
        "schema supports longer/full passes without creating a separate package file")
    add("S6-BOUND-6", "BOUND6-MULTICHUNK-D9-O324-L162-C4", "optional_multi_chunk_smt_probe", "ALL", "one-context four-chunk S6-BRANCH-3 depth-9 run from offset 324", BOUND6_EXPECTED_RUN["total_nodes"],
        "depth=9; start_offset=324; chunk_limit=162; chunks=4; next_offset=972; total=648; UNSAT=635; SAT=0; UNKNOWN=13; chunk_UNSAT=156/159/158/162; chunk_UNKNOWN=6/3/4/0",
        "one_context_multi_chunk_finds_unknown_tail", "ready_v0_18_bound6",
        "larger pass shows the next frontier segment is mixed: mostly UNSAT, with UNKNOWN nodes requiring stronger handling")
    add("S6-CERT-PACK-4", "CERTPACK4-MIXED-MULTICHUNK", "certificate_pack_chunk", "ALL", "mixed multi-chunk SMT result", BOUND6_EXPECTED_RUN["certified_unsat_entries"],
        "run=(depth=9,start=324,limit=162,chunks=4,next=972,total=18540); certified=635; unknown=13; cumulative_checked=972; cumulative_certified=959; SAT=0",
        "mixed_unsat_unknown_node_pack", "ready_v0_18_certpack4",
        "records both certified UNSAT entries and the noncertified UNKNOWN tail for the next strengthening step")
    add("S6-UNKNOWN-1", "UNKNOWN1-D9-O324-REPLAY12", "unknown_tail_extraction", "ALL", "replayed UNKNOWN depth-9 node signatures", BOUND7_EXPECTED_TARGETED["source_replay_unknown_nodes"],
        f"replay=(depth=9,start=324,limit=162,chunks=4,next=972,total=648,timeout_ms=5000); replay_UNSAT=636; replay_UNKNOWN=12; SAT=0; node_ids={UNKNOWN1_REPLAY_NODE_IDS}",
        "timeout_boundary_unknown_tail", "ready_v0_19_unknown1",
        "same segment as BOUND6; replay closed one prior timeout-boundary node and exposed the 12 signatures used by BOUND7")
    add("S6-BOUND-7", "BOUND7-D9-O324-UNKNOWN12-T60S", "targeted_unknown_smt_closure", "ALL", "targeted depth-9 UNKNOWN tail rerun", BOUND7_EXPECTED_TARGETED["targeted_nodes"],
        "targeted_nodes=12; per_node_timeout_ms=60000; UNSAT=12; SAT=0; UNKNOWN=0; fixed_coordinates=9; target_rawH>=1171",
        "targeted_timeout_closure", "ready_v0_20_bound7",
        "all replay-extracted UNKNOWN signatures close UNSAT under the larger per-node timeout; no high-H pure completion is found")
    add("S6-CERT-PACK-5", "CERTPACK5-CLOSED-D9-O324-O972", "certificate_pack_chunk", "ALL", "closed depth-9 segment after targeted UNKNOWN rerun", BOUND7_EXPECTED_TARGETED["closed_segment_certified_unsat_entries"],
        "segment=(depth=9,start=324,next=972,total=648); replay_certified=636; targeted_certified=12; certified=648; cumulative_checked=972; cumulative_certified=972; SAT=0; unresolved=0",
        "closed_multichunk_unsat_pack", "ready_v0_20_certpack5",
        "combines the replayed segment with the targeted UNKNOWN closure; historical BOUND6 remains recorded as the first mixed run")
    add("S6-BOUND-8", "BOUND8-WIDE-D9-O972-L162-C8-T300S", "optional_wide_multi_chunk_smt_probe", "ALL", "wide one-context depth-9 run from offset 972", BOUND8_EXPECTED_RUN["total_nodes"],
        "depth=9; start_offset=972; chunk_limit=162; chunks=8; next_offset=2268; total=1296; timeout_ms=300000; UNSAT=1296; SAT=0; UNKNOWN=0; chunk_UNSAT=162/162/162/162/162/162/162/162",
        "wide_timeout_multi_chunk_pruning", "ready_v0_21_bound8",
        "uses a broader front and five-minute per-node timeout; the entire segment closes UNSAT with no UNKNOWN tail")
    add("S6-CERT-PACK-6", "CERTPACK6-WIDE-D9-O972-O2268", "certificate_pack_chunk", "ALL", "wide closed depth-9 segment", BOUND8_EXPECTED_RUN["certified_unsat_entries"],
        "segment=(depth=9,start=972,next=2268,total=1296); certified=1296; cumulative_checked=2268; cumulative_certified=2268; SAT=0; unresolved=0",
        "wide_closed_unsat_pack", "ready_v0_21_certpack6",
        "extends the certified depth-9 prefix through offset 2268 using the wider high-timeout pass")
    add("S6-BOUND-9", "BOUND9-WIDE-D9-O2268-L162-C8-T300S", "optional_wide_multi_chunk_smt_probe", "ALL", "wide one-context depth-9 run from offset 2268", BOUND9_EXPECTED_RUN["total_nodes"],
        "depth=9; start_offset=2268; chunk_limit=162; chunks=8; next_offset=3564; total=1296; timeout_ms=300000; UNSAT=1296; SAT=0; UNKNOWN=0; chunk_UNSAT=162/162/162/162/162/162/162/162",
        "wide_timeout_multi_chunk_pruning", "ready_v0_22_bound9",
        "continues the broader five-minute timeout profile; the second wide segment also closes UNSAT with no UNKNOWN tail")
    add("S6-CERT-PACK-7", "CERTPACK7-WIDE-D9-O2268-O3564", "certificate_pack_chunk", "ALL", "second wide closed depth-9 segment", BOUND9_EXPECTED_RUN["certified_unsat_entries"],
        "segment=(depth=9,start=2268,next=3564,total=1296); certified=1296; cumulative_checked=3564; cumulative_certified=3564; SAT=0; unresolved=0",
        "wide_closed_unsat_pack", "ready_v0_22_certpack7",
        "extends the certified depth-9 prefix through offset 3564 using the same wide high-timeout pass")
    add("S6-BOUND-10", "BOUND10-WIDE-D9-O3564-L162-C8-T300S", "optional_wide_multi_chunk_smt_probe", "ALL", "wide one-context depth-9 run from offset 3564", BOUND10_EXPECTED_RUN["total_nodes"],
        "depth=9; start_offset=3564; chunk_limit=162; chunks=8; next_offset=4860; total=1296; timeout_ms=300000; UNSAT=1296; SAT=0; UNKNOWN=0; chunk_UNSAT=162/162/162/162/162/162/162/162",
        "wide_timeout_multi_chunk_pruning", "ready_v0_23_bound10",
        "continues the broader five-minute timeout profile; the third wide segment closes UNSAT with no UNKNOWN tail")
    add("S6-CERT-PACK-8", "CERTPACK8-WIDE-D9-O3564-O4860", "certificate_pack_chunk", "ALL", "third wide closed depth-9 segment", BOUND10_EXPECTED_RUN["certified_unsat_entries"],
        "segment=(depth=9,start=3564,next=4860,total=1296); certified=1296; cumulative_checked=4860; cumulative_certified=4860; SAT=0; unresolved=0",
        "wide_closed_unsat_pack", "ready_v0_23_certpack8",
        "extends the certified depth-9 prefix through offset 4860 using the same wide high-timeout pass")
    add("S6-BOUND-11", "BOUND11-OVERNIGHT-D9-O4860-O18540", "overnight_frontier_smt_run", "ALL", "overnight H2 tail run", BOUND11_EXPECTED_RUN["total_nodes"],
        "depth=9; start_offset=4860; end_offset=18540; chunk_size=162; window_chunks=8; timeout_ms=300000; target_rawH>=1171; UNSAT=13680; SAT=0; UNKNOWN=0",
        "streaming_high_timeout_tail_closure", "ready_v0_24_bound11",
        "manual overnight runner closed the remaining depth-9 live frontier tail and streamed durable CSV/checkpoint artifacts")
    add("S6-CERT-PACK-9", "CERTPACK9-OVERNIGHT-D9-O4860-O18540", "certificate_pack_chunk", "ALL", "audited overnight depth-9 tail segment", BOUND11_EXPECTED_RUN["certified_unsat_entries"],
        "segment=(depth=9,start=4860,next=18540,total=13680); certified=13680; cumulative_checked=18540; cumulative_certified=18540; SAT=0; unresolved=0; audit=PASS; rerun=all",
        "audited_overnight_unsat_pack", "ready_v0_24_certpack9",
        "audit_h2_overnight.py verified coverage/signatures/counts and reran the full tail with no mismatches")
    add("S6-CERT-PACK-FINAL", "CERTPACK-FINAL-D9-H2-COVERAGE", "final_certificate_pack_audit", "ALL", "full depth-9 H2 coverage condition", CERTPACK_FINAL_EXPECTED["certified_unsat_entries"],
        "coverage=[0,18540); no_gap=1; no_overlap=1; query=pure_and_rawH_ge_1171; certified_unsat=18540; SAT=0; unresolved=0; generated_depth9_frontier=18540",
        "full_h2_certificate_condition", "ready_v0_25_certpack_final",
        "combines the certified prefix through offset 4860 with the audited overnight tail 4860..18539")
    add("S6-H1", "HRANGE1-EVAL-FULL-3POW21", "full_landscape_exact_run", "ALL", "optimized exact H1 evaluator full run", H1_EXPECTED_RANGE["checked_points"],
        "range=[0,3^21); chunks=2093; rawH=[-378,1217]; H_tot=[-2268,7302]; upper rawH>=1218 violations=0; lower rawH<=-379 violations=0; audit=PASS; rerun=sample",
        "streaming_cpp_exact_evaluator", "ready_v0_27_hrange1",
        "run_h1_evaluator.py streamed the full unrestricted normal-form landscape and audit_h1_evaluator.py verified coverage/endpoints/sample rerun")
    add("S6-H1", "S6-H1", "global_theorem", "ALL", "global_H_range", H1_EXPECTED_RANGE["checked_points"],
        "min_{Omega'}H_tot=-2268; max_{Omega'}H_tot=7302; endpoint_counts=min:8,max:12; min_word=012120201012120201012; max_word=000000000111111111220",
        "global_H_range_theorem", "proved_v0_27_h1",
        "unrestricted H1 is now closed by the audited exact evaluator; the max endpoint is impure with N_-=3, while H2 separately controls the pure frontier")
    add("S6-H2", "S6-H2", "global_theorem", "ALL", "global_pure_frontier", CERTPACK_FINAL_EXPECTED["frontier_total"],
        "max_{Omega'}{H_tot:N_-=0}=7020; proof=interval-pruned nodes plus depth-9 SMT UNSAT coverage for rawH>=1171",
        "global_pure_frontier_theorem", "proved_v0_25_h2",
        "PAB and row-complement give the lower bound H_tot=7020,N_-=0; the final certificate pack excludes every pure H_tot>7020 completion")
    add("S6-H3", "S6-H3", "global_theorem", "ALL", "PAB_row_complement_guardrail", len(H3_GUARDRAIL_WITNESSES),
        f"PAB={H3_PAB_WORD}; row_complement={H3_ROW_COMPLEMENT_WORD}; both have H_tot=7020,N_-=0; by S6-H2 both lie on PureFrontier_H(Omega'); H is not a unique PAB selector",
        "pure_frontier_guardrail_theorem", "proved_v0_26_h3",
        "H3 is a guardrail/bridge theorem, not a final PAB selector; row-complement has the same pure H-profile")
    add("S6-H4", "H4-SIGNED-CLASSIFIER", "runner_interface", "ALL", "signed-cancellation classifier runner", OMEGA_PRIME_POINTS,
        "default full scan over [0,3^21); pair_min_rawH=1171; witness_min_rawH=1217; outputs chunks/chunk_pairs/pair_counts/rawH_summary/witnesses/checkpoint",
        "streaming_cpp_signed_classifier", "ready_v0_28_h4_runner",
        "run_h4_classifier.py and audit_h4_classifier.py provide the signed-cancellation classification artifact interface used by the full H4 theorem run")
    add("S6-H4", "H4-SIGNED-FULL-3POW21", "full_landscape_exact_run", "ALL", "signed-cancellation classifier full run", H4_EXPECTED_RANGE["checked_points"],
        "range=[0,3^21); chunks=2093; pair_min_rawH=1171; high_points=12; high_pure_points=0; pair_counts=(rawH=1217,N_-=3,count=12); witnesses=12; audit=PASS; rerun=sample",
        "streaming_cpp_signed_classifier", "ready_v0_29_h4_signed_full",
        "run_h4_classifier.py streamed the full unrestricted landscape and audit_h4_classifier.py verified coverage/pair counts/witnesses/sample rerun")
    add("S6-H4", "S6-H4", "global_theorem", "ALL", "signed_cancellation_frontier", H4_EXPECTED_RANGE["high_points"],
        "{x in Omega': H_tot>7020} has 12 points; all have H_tot=7302, rawH=1217, N_-=3, H_pos=7308, H_neg_abs=6; no pure high-H points",
        "signed_cancellation_frontier_theorem", "proved_v0_29_h4",
        "H4 classifies the entire region above the pure frontier; the only signed-cancellation excess is the 12-point unrestricted maximum orbit")

    return rows


# ---------------------------------------------------------------------------
# Table IO and reference loading
# ---------------------------------------------------------------------------


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str] = RESULT_FIELDS) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def assert_csv_equal(path: Path, expected: list[dict[str, str]]) -> None:
    if not path.is_file():
        fail(f"missing table {path}")
    got = read_csv(path)
    norm_expected = [{k: str(r.get(k, "")) for k in RESULT_FIELDS} for r in expected]
    norm_got = [{k: str(r.get(k, "")) for k in RESULT_FIELDS} for r in got]
    if norm_got != norm_expected:
        fail(f"table mismatch: {path}")


def reference_dir_has_l1(reference_dir: Path) -> bool:
    return (
        (reference_dir / "L1.zip").is_file()
        or (reference_dir / "L1" / "layer1H" / "scripts" / "h_core.py").is_file()
        or (reference_dir / "layer1H" / "scripts" / "h_core.py").is_file()
    )


def default_reference_dir() -> Path:
    candidates = (
        WORKSPACE_DIR / "cycle1_layers123",
        SCRIPT_DIR / "cycle1_layers123",
        SCRIPT_DIR,
        Path("/mnt/data"),
    )
    for candidate in candidates:
        if reference_dir_has_l1(candidate):
            return candidate
    return WORKSPACE_DIR / "cycle1_layers123"


def resolve_l1_reference(reference_dir: Path) -> tuple[str, Path]:
    reference_dir = reference_dir.resolve()
    zip_path = reference_dir / "L1.zip"
    if zip_path.is_file():
        return "zip", zip_path

    unpacked_path = reference_dir / "L1"
    if (unpacked_path / "layer1H" / "scripts" / "h_core.py").is_file():
        return "dir", unpacked_path

    if (reference_dir / "layer1H" / "scripts" / "h_core.py").is_file():
        return "dir", reference_dir

    fail(
        "missing L1 reference at "
        f"{reference_dir}; expected L1.zip, unpacked L1/, or direct L1 root"
    )


def read_text_from_l1_reference(l1_ref: tuple[str, Path], member: str) -> str:
    kind, path = l1_ref
    if kind == "zip":
        with zipfile.ZipFile(path) as zf:
            return zf.read(member).decode("utf-8")

    rel = member[3:] if member.startswith("L1/") else member
    file_path = path / rel
    if not file_path.is_file():
        fail(f"missing L1 reference file {file_path}")
    return file_path.read_text(encoding="utf-8")


def read_csv_from_l1_reference(l1_ref: tuple[str, Path], member: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(read_text_from_l1_reference(l1_ref, member))))


def load_h_core(reference_dir: Path) -> types.ModuleType:
    l1_ref = resolve_l1_reference(reference_dir)
    source = read_text_from_l1_reference(l1_ref, "L1/layer1H/scripts/h_core.py")
    mod = types.ModuleType("h_core_from_L1_reference")
    source_label = f"{l1_ref[1]}:L1/layer1H/scripts/h_core.py"
    exec(compile(source, source_label, "exec"), mod.__dict__)
    return mod


def column_blind_x21(a: int, b: int, d: tuple[int, int, int]) -> str:
    return x21_from_parts([a] * 9, [b] * 9, list(d))


def deterministic_samples(n: int) -> list[str]:
    rng = random.Random(6003)
    return ["".join(str(rng.randrange(3)) for _ in range(21)) for _ in range(n)]


# ---------------------------------------------------------------------------
# Verification routines
# ---------------------------------------------------------------------------


def compare_point_list(xs: list[str], label: str, h_core: types.ModuleType | None = None, check_certificate: bool = True) -> None:
    triples = list(product(S, S, S))
    for i, x in enumerate(xs):
        M = mtab(x)
        DL, DC = distance_banks(M)
        direct_rows = [local_direct_record(M, b, t, a, e, f) for b, t, a, e, f in product(S, S, S, S, S)]
        red_rows = [local_reduced_record_with_banks(M, DL, DC, b, t, a, e, f) for b, t, a, e, f in product(S, S, S, S, S)]
        cert_rows = local_certificate_interface_records(x) if check_certificate else None
        if check_certificate:
            iterable = zip(direct_rows, red_rows, cert_rows or [])
            for q_index, (direct, red, cert) in enumerate(iterable):
                for key in ("xy", "yz", "zR", "epL", "epR", "dI", "dB", "h"):
                    if int(red[key]) != int(direct[key]):
                        fail(f"{label}[{i}] q#{q_index} reduction mismatch {key}: got {red[key]}, expected {direct[key]}, x21={x}")
                    if int(cert[key]) != int(red[key]):
                        fail(f"{label}[{i}] q#{q_index} certificate-interface mismatch {key}: got {cert[key]}, expected {red[key]}, x21={x}")
        else:
            for q_index, (direct, red) in enumerate(zip(direct_rows, red_rows)):
                for key in ("xy", "yz", "zR", "epL", "epR", "dI", "dB", "h"):
                    if int(red[key]) != int(direct[key]):
                        fail(f"{label}[{i}] q#{q_index} reduction mismatch {key}: got {red[key]}, expected {direct[key]}, x21={x}")
        L, C = signature_banks(M)
        for c, u, ell in product(S, S, S):
            pidx = 3 * u + ell
            if L[c][pidx] != mv(M, u, c, ell):
                fail(f"{label}[{i}] L alias mismatch c={c},u={u},ell={ell}")
        for s, alpha, z, u, ell in product(S, S, S, S, S):
            pidx = 3 * u + ell
            expected = mv(M, s, alpha, (s + mv(M, u - s, z - s, ell - s)) % 3)
            if C[(s, alpha, z)][pidx] != expected:
                fail(f"{label}[{i}] C alias mismatch g={(s, alpha, z)},u={u},ell={ell}")
        for c, cp in product(S, S):
            if DL[(c, cp)] != DL[(cp, c)] or not (0 <= DL[(c, cp)] <= 9):
                fail(f"{label}[{i}] D_L axiom mismatch {(c, cp)}")
            if c == cp and DL[(c, cp)] != 0:
                fail(f"{label}[{i}] D_L diagonal nonzero {c}")
        for g, gp in product(triples, triples):
            if DC[(g, gp)] != DC[(gp, g)] or not (0 <= DC[(g, gp)] <= 9):
                fail(f"{label}[{i}] D_C axiom mismatch {g},{gp}")
            if g == gp and DC[(g, gp)] != 0:
                fail(f"{label}[{i}] D_C diagonal nonzero {g}")
        red_metrics = h_metrics_from_rows(red_rows)
        if check_certificate:
            cert_metrics = h_metrics_from_rows(cert_rows or [])
            for field in METRIC_FIELDS:
                if int(red_metrics[field]) != int(cert_metrics[field]):
                    fail(f"{label}[{i}] cert metric mismatch {field}: got {cert_metrics[field]}, expected {red_metrics[field]}, x21={x}")
        if h_core is not None:
            ref = h_core.h_metrics(x)
            for field in METRIC_FIELDS:
                if int(red_metrics[field]) != int(ref[field]):
                    fail(f"{label}[{i}] h_core metric mismatch {field}: got {red_metrics[field]}, expected {ref[field]}, x21={x}")
    cert_label = ", S6-CERT-IF" if check_certificate else ""
    print(f"PASS {label}: direct local formula, S6-RED{cert_label}, and metrics for {len(xs)} points")


def verify_reference_witnesses(reference_dir: Path, h_core: types.ModuleType) -> list[str]:
    xs = list(h_core.standard_six().values())
    key_rows = read_csv_from_l1_reference(
        resolve_l1_reference(reference_dir),
        "L1/layer1H/tables/H_key_witnesses.csv",
    )
    xs += [r["x21"] for r in key_rows]
    compare_point_list(xs, "standard+key witnesses", h_core)
    return xs


def verify_column_blind(h_core: types.ModuleType) -> None:
    xs = [column_blind_x21(a, b, d) for a, b in product(S, S) for d in product(S, S, S)]
    compare_point_list(xs, "column_blind_x_Delta exhaustive", h_core, check_certificate=False)


def verify_samples(h_core: types.ModuleType, n: int) -> None:
    xs = deterministic_samples(n)
    compare_point_list(xs, f"deterministic generic sample n={n}", h_core, check_certificate=False)


def sanity_check_result_rows(rows: list[dict[str, str]]) -> None:
    by_id = {r["result_id"]: r for r in rows}
    required = [
        "BD-PURE", "RED-L", "RED-C", "RED-DL", "RED-DC", "RED-HLOCAL", "RED-CONSTRAINT-MIXED",
        "CERT-X", "CERT-MU", "CERT-L", "CERT-C-AUX", "CERT-C", "CERT-DL", "CERT-DC", "CERT-LOCAL",
        "CERT-SELECT-DC", "CERT-SELECT-DL", "CERT-PURE", "CERT-OBJ", "CERT-CENSUS-TERNARY", "CERT-CENSUS-DIST",
        "ENGINE0-KERNEL", "ENGINE0-column_blind_x_Delta-RANGE", "ENGINE0-column_blind_x_Delta-PURE",
        "ENGINE0-affine_x_Delta-RANGE", "ENGINE0-affine_x_Delta-PURE", "ENGINE0-PURE-WITNESSES",
        "ENGINE1-INTERVAL-KERNEL", "ENGINE1-ROOT-BOUND", "ENGINE1-PAB-LEAF", "ENGINE1-ROWCOMP-LEAF",
        "ENGINE1-RADIUS1-PAB", "ENGINE1-RADIUS1-ROWCOMP", "ENGINE1-SOUNDED-SUBCUBES",
        "BRANCH0-SCOUT-D0", "BRANCH0-SCOUT-D4", "BRANCH0-SCOUT-BARRIER", "BRANCH0-FRONTIER-R2",
        "SMT0-CB-ENCODING", "SMT0-CB-PURE-GT7020", "SMT0-CB-FRONTIER7020",
        "SMT1-GLOBAL-ONEHOT-PB", "SMT1-GLOBAL-PURE-GT7020",
        "BRANCH1-DIAG-FIRST-D8", "BRANCH1-INTERLEAVE-D8", "BRANCH1-ORDER-COMPARISON",
        "BRANCH2-GREEDY-PREFIX-D6", "BRANCH2-GREEDY-TAIL-B-D8", "BRANCH2-GREEDY-TAIL-A-D8",
        "BRANCH3-RUNNER", "BRANCH3-GREEDY-B-D9",
        "BOUND1-SMT-NODE-EVAL", "BOUND1-D9-FIRST20-UNSAT",
        "BOUND2-BATCH-D9-FIRST81", "CERTPACK0-UNSAT-NODE-SCHEMA",
        "BOUND3-CHUNK-D9-O0-L162", "CERTPACK1-RESUMABLE-CHUNK-SCHEMA",
        "BOUND4-CHUNK-D9-O162-L162", "CERTPACK2-SECOND-CHUNK",
        "BOUND5-MULTICHUNK-D9-O0-L162-C2", "CERTPACK3-MULTICHUNK-SCHEMA",
        "BOUND6-MULTICHUNK-D9-O324-L162-C4", "CERTPACK4-MIXED-MULTICHUNK",
        "UNKNOWN1-D9-O324-REPLAY12", "BOUND7-D9-O324-UNKNOWN12-T60S", "CERTPACK5-CLOSED-D9-O324-O972",
        "BOUND8-WIDE-D9-O972-L162-C8-T300S", "CERTPACK6-WIDE-D9-O972-O2268",
        "BOUND9-WIDE-D9-O2268-L162-C8-T300S", "CERTPACK7-WIDE-D9-O2268-O3564",
        "BOUND10-WIDE-D9-O3564-L162-C8-T300S", "CERTPACK8-WIDE-D9-O3564-O4860",
        "BOUND11-OVERNIGHT-D9-O4860-O18540", "CERTPACK9-OVERNIGHT-D9-O4860-O18540",
        "CERTPACK-FINAL-D9-H2-COVERAGE",
        "HRANGE1-EVAL-FULL-3POW21", "S6-H1", "S6-H2", "S6-H3",
        "H4-SIGNED-CLASSIFIER", "H4-SIGNED-FULL-3POW21", "S6-H4",
    ]
    for rid in required:
        if rid not in by_id:
            fail(f"result table missing {rid}")
    c = cert_if_census()
    expected_counts = {
        "BD-PURE": "243", "RED-L": "3", "RED-C": "27", "RED-DL": "9", "RED-DC": "729", "RED-HLOCAL": "243",
        "CERT-X": str(c["normal_coordinate_blocks"]),
        "CERT-MU": str(c["mu_table_read_blocks"]),
        "CERT-L": str(c["left_signature_blocks"]),
        "CERT-C-AUX": str(c["continuation_aux_blocks"]),
        "CERT-C": str(c["continuation_blocks"]),
        "CERT-DL": str(c["DL_entries"]),
        "CERT-DC": str(c["DC_entries"]),
        "CERT-LOCAL": str(c["local_scalar_blocks"]),
        "CERT-SELECT-DC": str(c["DC_selector_cases"]),
        "CERT-SELECT-DL": str(c["DL_selector_cases"]),
        "CERT-PURE": str(c["pure_inequalities"]),
        "CERT-OBJ": str(c["block_sum_vars"] + c["global_objective_vars"]),
        "CERT-CENSUS-TERNARY": str(c["ternary_onehot_blocks_total"]),
        "CERT-CENSUS-DIST": str(c["distance_position_comparisons_total"]),
        "ENGINE0-KERNEL": "243",
        "ENGINE0-column_blind_x_Delta-RANGE": str(ENGINE0_EXPECTED["column_blind_x_Delta"]["points"]),
        "ENGINE0-column_blind_x_Delta-PURE": str(ENGINE0_EXPECTED["column_blind_x_Delta"]["pure_count"]),
        "ENGINE0-affine_x_Delta-RANGE": str(ENGINE0_EXPECTED["affine_x_Delta"]["points"]),
        "ENGINE0-affine_x_Delta-PURE": str(ENGINE0_EXPECTED["affine_x_Delta"]["pure_count"]),
        "ENGINE0-PURE-WITNESSES": str(len(ENGINE0_PURE_FRONTIER_WITNESSES)),
        "ENGINE1-INTERVAL-KERNEL": "243",
        "ENGINE1-ROOT-BOUND": "243",
        "ENGINE1-PAB-LEAF": "243",
        "ENGINE1-ROWCOMP-LEAF": "243",
        "ENGINE1-RADIUS1-PAB": "43",
        "ENGINE1-RADIUS1-ROWCOMP": "43",
        "ENGINE1-SOUNDED-SUBCUBES": str(len(deterministic_partial_domains())),
        "BRANCH0-SCOUT-D0": "1",
        "BRANCH0-SCOUT-D1": "3",
        "BRANCH0-SCOUT-D2": "9",
        "BRANCH0-SCOUT-D3": "27",
        "BRANCH0-SCOUT-D4": "81",
        "BRANCH0-SCOUT-BARRIER": str(sum(r["nodes"] for r in branch0_expected_interval_scout())),
        "BRANCH0-FRONTIER-R2": str(BRANCH0_SHELL_TOTAL_POINTS),
        "SMT0-CB-ENCODING": "5",
        "SMT0-CB-PURE-GT7020": "243",
        "SMT0-CB-FRONTIER7020": "1",
        "SMT1-GLOBAL-ONEHOT-PB": "21",
        "SMT1-GLOBAL-PURE-GT7020": "243",
        "BRANCH1-DIAG-FIRST-D8": "6561",
        "BRANCH1-INTERLEAVE-D8": "6561",
        "BRANCH1-ORDER-COMPARISON": str(len(BRANCH1_ORDER_NAMES)),
        "BRANCH2-GREEDY-PREFIX-D6": str(len(BRANCH2_GREEDY_EXPECTED_PREFIX)),
        "BRANCH2-GREEDY-TAIL-B-D8": "6561",
        "BRANCH2-GREEDY-TAIL-A-D8": "6561",
        "BRANCH3-RUNNER": str(len(BRANCH3_GREEDY_B_FIRST_ORDER)),
        "BRANCH3-GREEDY-B-D9": str(BRANCH3_EXPECTED_D9["live_nodes"]),
        "BOUND1-SMT-NODE-EVAL": str(BOUND1_EXPECTED_SAMPLE["fixed_coordinates_per_node"]),
        "BOUND1-D9-FIRST20-UNSAT": str(BOUND1_EXPECTED_SAMPLE["sampled_nodes"]),
        "BOUND2-BATCH-D9-FIRST81": str(BOUND2_EXPECTED_BATCH["batch_nodes"]),
        "CERTPACK0-UNSAT-NODE-SCHEMA": str(BOUND2_EXPECTED_BATCH["certified_unsat_entries"]),
        "BOUND3-CHUNK-D9-O0-L162": str(BOUND3_EXPECTED_CHUNK["batch_nodes"]),
        "CERTPACK1-RESUMABLE-CHUNK-SCHEMA": str(BOUND3_EXPECTED_CHUNK["certified_unsat_entries"]),
        "BOUND4-CHUNK-D9-O162-L162": str(BOUND4_EXPECTED_CHUNK["batch_nodes"]),
        "CERTPACK2-SECOND-CHUNK": str(BOUND4_EXPECTED_CHUNK["certified_unsat_entries"]),
        "BOUND5-MULTICHUNK-D9-O0-L162-C2": str(BOUND5_EXPECTED_RUN["total_nodes"]),
        "CERTPACK3-MULTICHUNK-SCHEMA": str(BOUND5_EXPECTED_RUN["certified_unsat_entries"]),
        "BOUND6-MULTICHUNK-D9-O324-L162-C4": str(BOUND6_EXPECTED_RUN["total_nodes"]),
        "CERTPACK4-MIXED-MULTICHUNK": str(BOUND6_EXPECTED_RUN["certified_unsat_entries"]),
        "UNKNOWN1-D9-O324-REPLAY12": str(BOUND7_EXPECTED_TARGETED["source_replay_unknown_nodes"]),
        "BOUND7-D9-O324-UNKNOWN12-T60S": str(BOUND7_EXPECTED_TARGETED["targeted_nodes"]),
        "CERTPACK5-CLOSED-D9-O324-O972": str(BOUND7_EXPECTED_TARGETED["closed_segment_certified_unsat_entries"]),
        "BOUND8-WIDE-D9-O972-L162-C8-T300S": str(BOUND8_EXPECTED_RUN["total_nodes"]),
        "CERTPACK6-WIDE-D9-O972-O2268": str(BOUND8_EXPECTED_RUN["certified_unsat_entries"]),
        "BOUND9-WIDE-D9-O2268-L162-C8-T300S": str(BOUND9_EXPECTED_RUN["total_nodes"]),
        "CERTPACK7-WIDE-D9-O2268-O3564": str(BOUND9_EXPECTED_RUN["certified_unsat_entries"]),
        "BOUND10-WIDE-D9-O3564-L162-C8-T300S": str(BOUND10_EXPECTED_RUN["total_nodes"]),
        "CERTPACK8-WIDE-D9-O3564-O4860": str(BOUND10_EXPECTED_RUN["certified_unsat_entries"]),
        "BOUND11-OVERNIGHT-D9-O4860-O18540": str(BOUND11_EXPECTED_RUN["total_nodes"]),
        "CERTPACK9-OVERNIGHT-D9-O4860-O18540": str(BOUND11_EXPECTED_RUN["certified_unsat_entries"]),
        "CERTPACK-FINAL-D9-H2-COVERAGE": str(CERTPACK_FINAL_EXPECTED["certified_unsat_entries"]),
        "HRANGE1-EVAL-FULL-3POW21": str(H1_EXPECTED_RANGE["checked_points"]),
        "S6-H1": str(H1_EXPECTED_RANGE["checked_points"]),
        "S6-H2": str(CERTPACK_FINAL_EXPECTED["frontier_total"]),
        "S6-H3": str(len(H3_GUARDRAIL_WITNESSES)),
        "H4-SIGNED-CLASSIFIER": str(OMEGA_PRIME_POINTS),
        "H4-SIGNED-FULL-3POW21": str(H4_EXPECTED_RANGE["checked_points"]),
        "S6-H4": str(H4_EXPECTED_RANGE["high_points"]),
    }
    for rid, expected in expected_counts.items():
        if by_id[rid]["count"] != expected:
            fail(f"{rid} count must be {expected}, got {by_id[rid]['count']}")
    support_rows = [r for r in rows if r["kind"] == "support_profile" and r["object"] == "C_{s,alpha,z}"]
    got_classes = {r["classification"]: int(r["count"]) for r in support_rows}
    expected_classes = {"offdiag=AB;diag=yes;cells=7": 9, "offdiag=AB;diag=yes;cells=8": 6, "offdiag=AB;diag=yes;cells=10": 12}
    if got_classes != expected_classes:
        fail(f"unexpected continuation support classes: {got_classes}")
    front_total = sum(int(r["count"]) for r in rows if r["kind"] == "front_read_pattern")
    if front_total != 243:
        fail(f"front_read_pattern rows must sum to 243, got {front_total}")
    witness_formula = by_id["ENGINE0-PURE-WITNESSES"]["formula"]
    if tuple(witness_formula.split(";")) != ENGINE0_PURE_FRONTIER_WITNESSES:
        fail("ENGINE0-PURE-WITNESSES formula does not match the expected witness set")
    if "[-13050,13086]" not in by_id["ENGINE1-ROOT-BOUND"]["formula"]:
        fail("ENGINE1-ROOT-BOUND formula must expose the current root interval [-13050,13086]")
    if "pure_max=7020" not in by_id["ENGINE1-RADIUS1-PAB"]["formula"]:
        fail("ENGINE1-RADIUS1-PAB must record pure_max=7020")
    if "pure_max=7020" not in by_id["ENGINE1-RADIUS1-ROWCOMP"]["formula"]:
        fail("ENGINE1-RADIUS1-ROWCOMP must record pure_max=7020")
    if "pure_gt_7020=0" not in by_id["BRANCH0-FRONTIER-R2"]["formula"]:
        fail("BRANCH0-FRONTIER-R2 must record pure_gt_7020=0")
    if "UNSAT" not in by_id["SMT0-CB-PURE-GT7020"]["formula"]:
        fail("SMT0-CB-PURE-GT7020 must record the UNSAT controlled boundary")
    if "prunable=81" not in by_id["BRANCH1-DIAG-FIRST-D8"]["formula"]:
        fail("BRANCH1-DIAG-FIRST-D8 must record prunable=81")
    if "chosen_order=20,19,18,17,16,15" not in by_id["BRANCH2-GREEDY-PREFIX-D6"]["formula"]:
        fail("BRANCH2-GREEDY-PREFIX-D6 must record the greedy prefix")
    if "live=18540" not in by_id["BRANCH3-GREEDY-B-D9"]["formula"]:
        fail("BRANCH3-GREEDY-B-D9 must record the depth-9 live frontier")
    if "UNSAT=20" not in by_id["BOUND1-D9-FIRST20-UNSAT"]["formula"]:
        fail("BOUND1-D9-FIRST20-UNSAT must record the sampled SMT node pruning result")
    if "UNSAT=81" not in by_id["BOUND2-BATCH-D9-FIRST81"]["formula"]:
        fail("BOUND2-BATCH-D9-FIRST81 must record the batched SMT node pruning result")
    if "certified=81" not in by_id["CERTPACK0-UNSAT-NODE-SCHEMA"]["formula"]:
        fail("CERTPACK0-UNSAT-NODE-SCHEMA must record the pack entry count")
    if "next_offset=162" not in by_id["BOUND3-CHUNK-D9-O0-L162"]["formula"]:
        fail("BOUND3-CHUNK-D9-O0-L162 must record the resumable next offset")
    if "certified=162" not in by_id["CERTPACK1-RESUMABLE-CHUNK-SCHEMA"]["formula"]:
        fail("CERTPACK1-RESUMABLE-CHUNK-SCHEMA must record the chunk pack count")
    if "next_offset=324" not in by_id["BOUND4-CHUNK-D9-O162-L162"]["formula"]:
        fail("BOUND4-CHUNK-D9-O162-L162 must record the second chunk next offset")
    if "cumulative_certified=324" not in by_id["CERTPACK2-SECOND-CHUNK"]["formula"]:
        fail("CERTPACK2-SECOND-CHUNK must record the cumulative certified count")
    if "context_builds=1" not in by_id["BOUND5-MULTICHUNK-D9-O0-L162-C2"]["formula"]:
        fail("BOUND5-MULTICHUNK-D9-O0-L162-C2 must record one-context execution")
    if "certified=324" not in by_id["CERTPACK3-MULTICHUNK-SCHEMA"]["formula"]:
        fail("CERTPACK3-MULTICHUNK-SCHEMA must record the multi-chunk certified count")
    if "UNKNOWN=13" not in by_id["BOUND6-MULTICHUNK-D9-O324-L162-C4"]["formula"]:
        fail("BOUND6-MULTICHUNK-D9-O324-L162-C4 must record the UNKNOWN tail")
    if "cumulative_certified=959" not in by_id["CERTPACK4-MIXED-MULTICHUNK"]["formula"]:
        fail("CERTPACK4-MIXED-MULTICHUNK must record the cumulative certified count")
    if "replay_UNKNOWN=12" not in by_id["UNKNOWN1-D9-O324-REPLAY12"]["formula"]:
        fail("UNKNOWN1-D9-O324-REPLAY12 must record the replay UNKNOWN tail")
    if "UNSAT=12" not in by_id["BOUND7-D9-O324-UNKNOWN12-T60S"]["formula"]:
        fail("BOUND7-D9-O324-UNKNOWN12-T60S must record the targeted UNSAT closure")
    if "cumulative_certified=972" not in by_id["CERTPACK5-CLOSED-D9-O324-O972"]["formula"]:
        fail("CERTPACK5-CLOSED-D9-O324-O972 must record the closed cumulative certified count")
    if "timeout_ms=300000" not in by_id["BOUND8-WIDE-D9-O972-L162-C8-T300S"]["formula"]:
        fail("BOUND8-WIDE-D9-O972-L162-C8-T300S must record the wide timeout")
    if "cumulative_certified=2268" not in by_id["CERTPACK6-WIDE-D9-O972-O2268"]["formula"]:
        fail("CERTPACK6-WIDE-D9-O972-O2268 must record the wide cumulative certified count")
    if "timeout_ms=300000" not in by_id["BOUND9-WIDE-D9-O2268-L162-C8-T300S"]["formula"]:
        fail("BOUND9-WIDE-D9-O2268-L162-C8-T300S must record the wide timeout")
    if "cumulative_certified=3564" not in by_id["CERTPACK7-WIDE-D9-O2268-O3564"]["formula"]:
        fail("CERTPACK7-WIDE-D9-O2268-O3564 must record the second wide cumulative certified count")
    if "timeout_ms=300000" not in by_id["BOUND10-WIDE-D9-O3564-L162-C8-T300S"]["formula"]:
        fail("BOUND10-WIDE-D9-O3564-L162-C8-T300S must record the wide timeout")
    if "cumulative_certified=4860" not in by_id["CERTPACK8-WIDE-D9-O3564-O4860"]["formula"]:
        fail("CERTPACK8-WIDE-D9-O3564-O4860 must record the third wide cumulative certified count")
    if "rerun=all" not in by_id["CERTPACK9-OVERNIGHT-D9-O4860-O18540"]["formula"]:
        fail("CERTPACK9-OVERNIGHT-D9-O4860-O18540 must record the full audit rerun")
    if "coverage=[0,18540)" not in by_id["CERTPACK-FINAL-D9-H2-COVERAGE"]["formula"]:
        fail("CERTPACK-FINAL-D9-H2-COVERAGE must record full depth-9 coverage")
    if "rawH=[-378,1217]" not in by_id["HRANGE1-EVAL-FULL-3POW21"]["formula"]:
        fail("HRANGE1-EVAL-FULL-3POW21 must record the exact rawH range")
    if by_id["S6-H1"]["status"] != "proved_v0_27_h1":
        fail("S6-H1 must be marked as proved after the exact evaluator audit")
    if "min_{Omega'}H_tot=-2268" not in by_id["S6-H1"]["formula"] or "max_{Omega'}H_tot=7302" not in by_id["S6-H1"]["formula"]:
        fail("S6-H1 must record the global H range theorem statement")
    if by_id["S6-H2"]["status"] != "proved_v0_25_h2":
        fail("S6-H2 must be marked as proved after the final certificate pack")
    if "max_{Omega'}{H_tot:N_-=0}=7020" not in by_id["S6-H2"]["formula"]:
        fail("S6-H2 must record the global pure-frontier theorem statement")
    if by_id["S6-H3"]["status"] != "proved_v0_26_h3":
        fail("S6-H3 must be marked as proved after S6-H2")
    if "H is not a unique PAB selector" not in by_id["S6-H3"]["formula"]:
        fail("S6-H3 must record the non-unique PAB-selector guardrail")
    if by_id["H4-SIGNED-CLASSIFIER"]["status"] != "ready_v0_28_h4_runner":
        fail("H4-SIGNED-CLASSIFIER must be marked ready after the runner smoke audit")
    if "pair_min_rawH=1171" not in by_id["H4-SIGNED-CLASSIFIER"]["formula"]:
        fail("H4-SIGNED-CLASSIFIER must record the default high-H threshold")
    if by_id["H4-SIGNED-FULL-3POW21"]["status"] != "ready_v0_29_h4_signed_full":
        fail("H4-SIGNED-FULL-3POW21 must record the audited full H4 artifact")
    if "high_points=12" not in by_id["H4-SIGNED-FULL-3POW21"]["formula"] or "high_pure_points=0" not in by_id["H4-SIGNED-FULL-3POW21"]["formula"]:
        fail("H4-SIGNED-FULL-3POW21 must record high-H signed counts")
    if by_id["S6-H4"]["status"] != "proved_v0_29_h4":
        fail("S6-H4 must be marked proved after the audited classifier run")
    if "H_tot>7020" not in by_id["S6-H4"]["formula"] or "N_-=3" not in by_id["S6-H4"]["formula"]:
        fail("S6-H4 must record the signed-cancellation frontier theorem statement")
    print("PASS S6-BD/S6-RED/S6-CERT-IF/S6-CERT-ENGINE-0/S6-CERT-ENGINE-1/S6-BRANCH-0/S6-SMT-0/S6-SMT-1/S6-BRANCH-1/S6-BRANCH-2/S6-BRANCH-3/S6-BOUND-1/S6-BOUND-2/S6-CERT-PACK-0/S6-BOUND-3/S6-CERT-PACK-1/S6-BOUND-4/S6-CERT-PACK-2/S6-BOUND-5/S6-CERT-PACK-3/S6-BOUND-6/S6-CERT-PACK-4/S6-UNKNOWN-1/S6-BOUND-7/S6-CERT-PACK-5/S6-BOUND-8/S6-CERT-PACK-6/S6-BOUND-9/S6-CERT-PACK-7/S6-BOUND-10/S6-CERT-PACK-8/S6-BOUND-11/S6-CERT-PACK-9/S6-CERT-PACK-FINAL/S6-H1/S6-H2/S6-H3/S6-H4 result rows and counts")



def verify_engine1_interval_layer() -> None:
    summaries = engine1_reference_summaries()
    root = summaries["root"]
    if root["H_lower"] != -13050 or root["H_upper"] != 13086:
        fail(f"S6-CERT-ENGINE-1 root interval mismatch: {root}")
    if root["local_impossible"] != 0 or root["local_forced"] != 0 or root["local_unresolved"] != 243:
        fail(f"S6-CERT-ENGINE-1 root local-status mismatch: {root}")

    for label, x in [
        ("PAB_leaf", "111111111222222222000"),
        ("row_complement_leaf", "222222222111111111000"),
    ]:
        leaf = summaries[label]
        exact = h_metrics_reduced(x)
        if leaf["H_lower"] != exact["H_tot"] or leaf["H_upper"] != exact["H_tot"]:
            fail(f"S6-CERT-ENGINE-1 {label} is not exact: interval={leaf}, exact={exact}")
        if leaf["local_impossible"] != 0 or leaf["local_forced"] != 243:
            fail(f"S6-CERT-ENGINE-1 {label} pure-status mismatch: {leaf}")

    for label in ["radius1_PAB", "radius1_row_complement"]:
        shell = summaries[label]
        expected = {
            "points": 43,
            "H_max": 7302,
            "pure_count": 11,
            "pure_max": 7020,
            "pure_frontier_count": 1,
            "all_max_N_neg_values": "3",
        }
        for key, value in expected.items():
            if shell[key] != value:
                fail(f"S6-CERT-ENGINE-1 {label} expected {key}={value}, got {shell[key]}")

    total_completions = 0
    for label, dom in deterministic_partial_domains():
        ctx = DomainIntervalContext(dom)
        local_intervals = [local_domain_interval(ctx, *q) for q in Q_LIST]
        node = partial_node_bounds(dom)
        actual_H_values: list[int] = []
        actual_local_values = [[] for _ in Q_LIST]
        pure_completions = 0
        for x in iter_domain_completions(dom):
            rows = local_reduced_records(x)
            metrics = h_metrics_from_rows(rows)
            actual_H_values.append(int(metrics["H_tot"]))
            pure_completions += 1 if int(metrics["N_neg"]) == 0 else 0
            for i, r in enumerate(rows):
                actual_local_values[i].append(int(r["h"]))
        total_completions += len(actual_H_values)
        if not actual_H_values:
            fail(f"S6-CERT-ENGINE-1 {label} has no completions")
        if min(actual_H_values) < node["H_lower"] or max(actual_H_values) > node["H_upper"]:
            fail(f"S6-CERT-ENGINE-1 {label} global interval not sound: node={node}, actual=[{min(actual_H_values)},{max(actual_H_values)}]")
        if node["local_impossible"] > 0 and pure_completions != 0:
            fail(f"S6-CERT-ENGINE-1 {label} claims a locally impossible pure constraint but pure completions exist")
        for i, (interval, vals) in enumerate(zip(local_intervals, actual_local_values)):
            lo = int(interval["h_min"])
            hi = int(interval["h_max"])
            amin = min(vals)
            amax = max(vals)
            if amin < lo or amax > hi:
                fail(f"S6-CERT-ENGINE-1 {label} q#{i} local interval not sound: interval=[{lo},{hi}], actual=[{amin},{amax}]")
            if bool(interval["pure_impossible"]) and amax >= 0:
                fail(f"S6-CERT-ENGINE-1 {label} q#{i} pure_impossible flag is unsound")
            if bool(interval["pure_forced"]) and amin < 0:
                fail(f"S6-CERT-ENGINE-1 {label} q#{i} pure_forced flag is unsound")

    print(
        "PASS S6-CERT-ENGINE-1 partial-domain interval layer: "
        f"root=[{root['H_lower']},{root['H_upper']}], "
        f"subcubes={len(deterministic_partial_domains())}, completions={total_completions}"
    )


def verify_branch0() -> None:
    scout = branch0_interval_depth_scout(BRANCH0_MAX_DEPTH)
    expected = branch0_expected_interval_scout()
    if scout != expected:
        fail(f"S6-BRANCH-0 interval depth scout mismatch: got {scout}, expected {expected}")
    shell = branch0_frontier_shell_summary(BRANCH0_SHELL_RADIUS)
    expected_shell = {
        "radius": BRANCH0_SHELL_RADIUS,
        "centers": 6,
        "points_per_center": 883,
        "points": 5298,
        "distinct_points": 5298,
        "H_min": 4524,
        "H_max": 7302,
        "pure_count": 444,
        "pure_max": 7020,
        "pure_frontier_count": 6,
        "pure_gt_7020_count": 0,
        "H_eq_7302_N_neg_values": "3",
        "per_center_points": "883/883/883/883/883/883",
        "per_center_pure_count": "74/74/74/74/74/74",
        "per_center_pure_frontier_count": "1/1/1/1/1/1",
    }
    for key, value in expected_shell.items():
        if shell[key] != value:
            fail(f"S6-BRANCH-0 frontier shell expected {key}={value}, got {shell[key]}")
    print(
        "PASS S6-BRANCH-0 branch/frontier scout: "
        f"depth<= {BRANCH0_MAX_DEPTH} nodes={sum(r['nodes'] for r in scout)}, "
        f"radius<={BRANCH0_SHELL_RADIUS} shell points={shell['points']}, "
        f"pure_max={shell['pure_max']}, pure_gt_7020={shell['pure_gt_7020_count']}"
    )


def verify_smt0() -> None:
    summary = smt0_column_blind_summary()
    gt = summary["gt"]
    frontier = summary["frontier"]
    if gt["answer"] != "unsat":
        fail(f"S6-SMT-0 expected column-blind pure H_tot>7020 UNSAT, got {gt}")
    if frontier["answer"] != "sat":
        fail(f"S6-SMT-0 expected column-blind pure H_tot>=7020 SAT, got {frontier}")
    metrics = frontier.get("metrics")
    if not isinstance(metrics, dict):
        fail(f"S6-SMT-0 frontier query returned no metrics: {frontier}")
    if int(metrics["H_tot"]) != 7020 or int(metrics["N_neg"]) != 0:
        fail(f"S6-SMT-0 frontier witness has wrong metrics: {frontier}")
    witness = str(frontier.get("witness", ""))
    if witness not in ENGINE0_PURE_FRONTIER_WITNESSES:
        fail(f"S6-SMT-0 frontier witness is not in the controlled frontier set: {frontier}")
    print(
        "PASS S6-SMT-0 column-blind SMT interface: "
        "pure H_tot>7020 UNSAT, frontier H_tot=7020 SAT"
    )


def run_smt_global(args: argparse.Namespace) -> None:
    result = smt1_global_onehot_pb_query(
        target_rawH=args.smt_target_rawH,
        timeout_ms=args.smt_timeout_ms,
    )
    msg = (
        "S6-SMT-1 global onehot-pb query: "
        f"target_rawH>={result['target_rawH']} answer={result['answer']} "
        f"elapsed={result['elapsed_seconds']}s build={result['build_seconds']}s "
        f"timeout_ms={result['timeout_ms']}"
    )
    if result["answer"] == "unknown":
        msg += f" reason={result.get('reason')}"
    print(msg)
    if result["answer"] == "sat":
        metrics = result.get("metrics")
        if not isinstance(metrics, dict):
            fail(f"S6-SMT-1 SAT result returned no exact metrics: {result}")
        if int(metrics["N_neg"]) != 0 or int(metrics["rawH"]) < int(result["target_rawH"]):
            fail(f"S6-SMT-1 SAT witness failed exact metric check: {result}")
        print(f"S6-SMT-1 witness: {result['witness']}")
        print(f"S6-SMT-1 witness metrics: H_tot={metrics['H_tot']} N_neg={metrics['N_neg']} rawH={metrics['rawH']}")


def verify_branch1() -> None:
    for order_name in BRANCH1_ORDER_NAMES:
        got = branch1_interval_depth_scout(order_name, BRANCH1_MAX_DEPTH)
        expected = branch1_expected_interval_scout(order_name)
        if got != expected:
            fail(f"S6-BRANCH-1 {order_name} mismatch: got {got}, expected {expected}")
    diag = branch1_expected_interval_scout("diag_first")[-1]
    inter = branch1_expected_interval_scout("interleave_AB_diag_last")[-1]
    print(
        "PASS S6-BRANCH-1 deep interval scout: "
        f"depth={BRANCH1_MAX_DEPTH}, diag_first prunable={diag['prunable_nodes']}, "
        f"interleave_AB_diag_last prunable={inter['prunable_nodes']}"
    )


def verify_branch2() -> None:
    prefix, rows = branch2_greedy_prefix(BRANCH2_GREEDY_DEPTH)
    if prefix != BRANCH2_GREEDY_EXPECTED_PREFIX:
        fail(f"S6-BRANCH-2 greedy prefix mismatch: got {prefix}, expected {BRANCH2_GREEDY_EXPECTED_PREFIX}")
    last = rows[-1]
    if last["nodes"] != 729 or last["prunable_nodes"] != 0 or last["H_upper_min"] != 11808 or last["H_upper_max"] != 12762 or last["forced_sum"] != 2702:
        fail(f"S6-BRANCH-2 greedy prefix final stats mismatch: {last}")

    tail_b = branch2_expected_tail_scout(BRANCH2_GREEDY_TAIL_B_ORDER)
    expected_b = {"prunable_nodes": 81, "pure_impossible_nodes": 81, "upper_pruned_nodes": 0, "H_upper_min": 11460, "H_upper_max": 12666}
    for key, value in expected_b.items():
        if tail_b[key] != value:
            fail(f"S6-BRANCH-2 B-tail expected {key}={value}, got {tail_b[key]}")

    tail_a = branch2_expected_tail_scout(BRANCH2_GREEDY_TAIL_A_ORDER)
    expected_a = {"prunable_nodes": 81, "pure_impossible_nodes": 81, "upper_pruned_nodes": 0, "H_upper_min": 11520, "H_upper_max": 12660}
    for key, value in expected_a.items():
        if tail_a[key] != value:
            fail(f"S6-BRANCH-2 A-tail expected {key}={value}, got {tail_a[key]}")

    print(
        "PASS S6-BRANCH-2 greedy adaptive scout: "
        f"prefix={','.join(str(i) for i in prefix)}, "
        f"B-tail prunable={tail_b['prunable_nodes']}, A-tail prunable={tail_a['prunable_nodes']}"
    )


def print_branch3_summary(summary: dict[str, object]) -> None:
    print(
        "S6-BRANCH-3 bounded frontier runner: "
        f"order={summary['order_name']} depth={summary['reached_depth']}/{summary['requested_depth']} "
        f"status={summary['status']} target_H={summary['target_H']} "
        f"generated={summary['total_generated']} pruned={summary['total_pruned_nodes']} "
        f"pure_impossible={summary['total_pure_impossible_pruned']} upper_le_target={summary['total_upper_pruned']} "
        f"live={summary['live_nodes']} H_upper_live=[{summary['live_H_upper_min']},{summary['live_H_upper_max']}] "
        f"elapsed={summary['elapsed_seconds']}s"
    )
    rows = summary.get("rows", [])
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            print(
                "S6-BRANCH-3 "
                f"D{row['depth']} idx={row['branch_index']} parents={row['parents']} "
                f"generated={row['generated']} pruned={row['pruned_nodes']} "
                f"pure_impossible={row['pure_impossible_nodes']} upper_le_target={row['upper_pruned_nodes']} "
                f"live={row['live_nodes']} H_upper_live=[{row['live_H_upper_min']},{row['live_H_upper_max']}]"
            )


def verify_branch3(args: argparse.Namespace) -> None:
    summary = branch3_frontier_runner(
        max_depth=args.branch3_depth,
        order_name=args.branch3_order,
        target_H=args.branch3_target_H,
        max_generated_nodes=args.branch3_max_generated,
        time_limit_seconds=args.branch3_time_limit,
    )
    print_branch3_summary(summary)
    is_reference = (
        args.branch3_depth == BRANCH3_REFERENCE_DEPTH
        and args.branch3_order == "greedy_B_first"
        and args.branch3_target_H == BRANCH3_TARGET_H
        and args.branch3_max_generated == 0
        and args.branch3_time_limit == 0.0
    )
    if is_reference:
        if summary["status"] != "complete":
            fail(f"S6-BRANCH-3 reference run did not complete: {summary}")
        for key, value in BRANCH3_EXPECTED_D9.items():
            if summary[key] != value:
                fail(f"S6-BRANCH-3 reference expected {key}={value}, got {summary[key]}")
        rows = summary.get("rows", [])
        if not isinstance(rows, list) or not rows:
            fail(f"S6-BRANCH-3 reference returned no rows: {summary}")
        last = rows[-1]
        if not isinstance(last, dict) or last["branch_index"] != 12 or last["generated"] != 19440 or last["pruned_nodes"] != 900:
            fail(f"S6-BRANCH-3 depth-9 split row mismatch: {last}")
    print(
        "PASS S6-BRANCH-3 bounded frontier runner: "
        f"depth={summary['reached_depth']}, live={summary['live_nodes']}, "
        f"pruned={summary['total_pruned_nodes']}, upper_le_target={summary['total_upper_pruned']}"
    )


def verify_bound1(args: argparse.Namespace) -> None:
    summary = bound1_smt_node_probe(
        depth=args.bound1_depth,
        sample_limit=args.bound1_sample_limit,
        target_rawH=args.bound1_target_rawH,
        timeout_ms=args.bound1_timeout_ms,
    )
    print(
        "S6-BOUND-1 SMT node probe: "
        f"depth={summary['depth']} sampled={summary['sampled_nodes']} "
        f"target_rawH>={summary['target_rawH']} "
        f"UNSAT={summary['unsat_nodes']} SAT={summary['sat_nodes']} UNKNOWN={summary['unknown_nodes']} "
        f"fixed=[{summary['fixed_count_min']},{summary['fixed_count_max']}] "
        f"build={summary['build_seconds']}s checks={summary['check_seconds']}s elapsed={summary['elapsed_seconds']}s"
    )
    results = summary.get("results", [])
    if isinstance(results, list):
        for i, rec in enumerate(results[:5]):
            if isinstance(rec, dict):
                print(
                    "S6-BOUND-1 sample "
                    f"#{i} answer={rec['answer']} fixed_count={rec['fixed_count']} fixed={rec['fixed_signature']}"
                )

    is_reference = (
        args.bound1_depth == BOUND1_REFERENCE_DEPTH
        and args.bound1_sample_limit == BOUND1_REFERENCE_SAMPLE_LIMIT
        and args.bound1_target_rawH == SMT1_GLOBAL_GT_RAW_H
    )
    if is_reference:
        for key, value in BOUND1_EXPECTED_SAMPLE.items():
            got_key = "fixed_count_min" if key == "fixed_coordinates_per_node" else key
            got = summary[got_key]
            if got != value:
                fail(f"S6-BOUND-1 reference expected {key}={value}, got {got}")
        if summary["fixed_count_max"] != BOUND1_EXPECTED_SAMPLE["fixed_coordinates_per_node"]:
            fail(f"S6-BOUND-1 reference fixed_count_max mismatch: {summary}")
    if int(summary["sat_nodes"]) > 0:
        for rec in results if isinstance(results, list) else []:
            if isinstance(rec, dict) and rec.get("answer") == "sat":
                metrics = rec.get("metrics")
                if not isinstance(metrics, dict) or int(metrics["N_neg"]) != 0 or int(metrics["rawH"]) < int(summary["target_rawH"]):
                    fail(f"S6-BOUND-1 SAT witness failed exact metric check: {rec}")
    print(
        "PASS S6-BOUND-1 pure-aware SMT node evaluator: "
        f"sampled={summary['sampled_nodes']}, UNSAT={summary['unsat_nodes']}, "
        f"SAT={summary['sat_nodes']}, UNKNOWN={summary['unknown_nodes']}"
    )


def verify_bound2(args: argparse.Namespace) -> None:
    summary = bound2_smt_batch_pack(
        depth=args.bound2_depth,
        batch_limit=args.bound2_batch_limit,
        target_rawH=args.bound2_target_rawH,
        timeout_ms=args.bound2_timeout_ms,
    )
    print(
        "S6-BOUND-2 SMT batch pack: "
        f"depth={summary['depth']} batch={summary['batch_nodes']} "
        f"target_rawH>={summary['target_rawH']} "
        f"UNSAT={summary['unsat_nodes']} SAT={summary['sat_nodes']} UNKNOWN={summary['unknown_nodes']} "
        f"unique={summary['unique_signatures']} cache_hits={summary['cache_hits']} "
        f"certified={summary['certified_unsat_entries']} noncertified={summary['noncertified_nodes']} "
        f"build={summary['build_seconds']}s checks={summary['check_seconds']}s elapsed={summary['elapsed_seconds']}s"
    )
    entries = summary.get("pack_entries", [])
    if isinstance(entries, list):
        for entry in entries[:5]:
            if isinstance(entry, dict):
                print(
                    "S6-CERT-PACK-0 entry "
                    f"#{entry['node_index']} answer={entry['answer']} fixed={entry['fixed_signature']}"
                )

    is_reference = (
        args.bound2_depth == BOUND2_REFERENCE_DEPTH
        and args.bound2_batch_limit == BOUND2_REFERENCE_BATCH_LIMIT
        and args.bound2_target_rawH == BOUND1_TARGET_RAW_H
    )
    if is_reference:
        for key, value in BOUND2_EXPECTED_BATCH.items():
            if summary[key] != value:
                fail(f"S6-BOUND-2 reference expected {key}={value}, got {summary[key]}")
        if summary["fixed_count_min"] != 9 or summary["fixed_count_max"] != 9:
            fail(f"S6-BOUND-2 reference fixed-count mismatch: {summary}")
    if int(summary["sat_nodes"]) > 0:
        results = summary.get("results", [])
        for rec in results if isinstance(results, list) else []:
            if isinstance(rec, dict) and rec.get("answer") == "sat":
                metrics = rec.get("metrics")
                if not isinstance(metrics, dict) or int(metrics["N_neg"]) != 0 or int(metrics["rawH"]) < int(summary["target_rawH"]):
                    fail(f"S6-BOUND-2 SAT witness failed exact metric check: {rec}")
    print(
        "PASS S6-BOUND-2/S6-CERT-PACK-0 batched SMT pack: "
        f"batch={summary['batch_nodes']}, certified={summary['certified_unsat_entries']}, "
        f"SAT={summary['sat_nodes']}, UNKNOWN={summary['unknown_nodes']}"
    )


def verify_bound3(args: argparse.Namespace) -> None:
    summary = bound3_smt_chunk_pack(
        depth=args.bound3_depth,
        chunk_offset=args.bound3_offset,
        chunk_limit=args.bound3_limit,
        target_rawH=args.bound3_target_rawH,
        timeout_ms=args.bound3_timeout_ms,
    )
    print(
        "S6-BOUND-3 resumable SMT chunk pack: "
        f"depth={summary['depth']} offset={summary['batch_offset']} limit={summary['batch_limit']} "
        f"next={summary['next_offset']} total={summary['frontier_total']} chunks={summary['chunk_count']} "
        f"UNSAT={summary['unsat_nodes']} SAT={summary['sat_nodes']} UNKNOWN={summary['unknown_nodes']} "
        f"certified={summary['certified_unsat_entries']} noncertified={summary['noncertified_nodes']} "
        f"build={summary['build_seconds']}s checks={summary['check_seconds']}s elapsed={summary['elapsed_seconds']}s"
    )
    entries = summary.get("pack_entries", [])
    if isinstance(entries, list):
        for entry in entries[:5]:
            if isinstance(entry, dict):
                print(
                    "S6-CERT-PACK-1 entry "
                    f"global#{entry['node_index']} answer={entry['answer']} fixed={entry['fixed_signature']}"
                )

    is_reference = (
        args.bound3_depth == BOUND3_REFERENCE_DEPTH
        and args.bound3_offset == BOUND3_REFERENCE_CHUNK_OFFSET
        and args.bound3_limit == BOUND3_REFERENCE_CHUNK_LIMIT
        and args.bound3_target_rawH == BOUND1_TARGET_RAW_H
    )
    if is_reference:
        for key, value in BOUND3_EXPECTED_CHUNK.items():
            if summary[key] != value:
                fail(f"S6-BOUND-3 reference expected {key}={value}, got {summary[key]}")
        if summary["fixed_count_min"] != 9 or summary["fixed_count_max"] != 9:
            fail(f"S6-BOUND-3 reference fixed-count mismatch: {summary}")
    if int(summary["sat_nodes"]) > 0:
        results = summary.get("results", [])
        for rec in results if isinstance(results, list) else []:
            if isinstance(rec, dict) and rec.get("answer") == "sat":
                metrics = rec.get("metrics")
                if not isinstance(metrics, dict) or int(metrics["N_neg"]) != 0 or int(metrics["rawH"]) < int(summary["target_rawH"]):
                    fail(f"S6-BOUND-3 SAT witness failed exact metric check: {rec}")
    print(
        "PASS S6-BOUND-3/S6-CERT-PACK-1 resumable SMT chunk pack: "
        f"offset={summary['batch_offset']}, next={summary['next_offset']}, "
        f"certified={summary['certified_unsat_entries']}, SAT={summary['sat_nodes']}, UNKNOWN={summary['unknown_nodes']}"
    )


def verify_bound5(args: argparse.Namespace) -> None:
    summary = bound5_smt_multi_chunk_pack(
        depth=args.bound5_depth,
        start_offset=args.bound5_offset,
        chunk_limit=args.bound5_limit,
        chunks=args.bound5_chunks,
        target_rawH=args.bound5_target_rawH,
        timeout_ms=args.bound5_timeout_ms,
    )
    print(
        "S6-BOUND-5 one-context SMT multi-chunk pack: "
        f"depth={summary['depth']} start={summary['start_offset']} limit={summary['chunk_limit']} "
        f"chunks={summary['chunks_completed']}/{summary['chunks_requested']} next={summary['next_offset']} "
        f"total_nodes={summary['total_nodes']} frontier_total={summary['frontier_total']} "
        f"UNSAT={summary['unsat_nodes']} SAT={summary['sat_nodes']} UNKNOWN={summary['unknown_nodes']} "
        f"certified={summary['certified_unsat_entries']} noncertified={summary['noncertified_nodes']} "
        f"build={summary['build_seconds']}s checks={summary['check_seconds']}s elapsed={summary['elapsed_seconds']}s"
    )
    chunks = summary.get("chunk_summaries", [])
    if isinstance(chunks, list):
        for chunk in chunks[:5]:
            if isinstance(chunk, dict):
                print(
                    "S6-CERT-PACK-3 chunk "
                    f"#{chunk['chunk_index']} offset={chunk['offset']} nodes={chunk['nodes']} "
                    f"UNSAT={chunk['unsat_nodes']} SAT={chunk['sat_nodes']} UNKNOWN={chunk['unknown_nodes']} "
                    f"next={chunk['next_offset']}"
                )

    is_reference = (
        args.bound5_depth == BOUND5_REFERENCE_DEPTH
        and args.bound5_offset == BOUND5_REFERENCE_START_OFFSET
        and args.bound5_limit == BOUND5_REFERENCE_CHUNK_LIMIT
        and args.bound5_chunks == BOUND5_REFERENCE_CHUNKS
        and args.bound5_target_rawH == BOUND1_TARGET_RAW_H
    )
    if is_reference:
        for key, value in BOUND5_EXPECTED_RUN.items():
            if summary[key] != value:
                fail(f"S6-BOUND-5 reference expected {key}={value}, got {summary[key]}")
        if summary["fixed_count_min"] != 9 or summary["fixed_count_max"] != 9:
            fail(f"S6-BOUND-5 reference fixed-count mismatch: {summary}")
    if int(summary["sat_nodes"]) > 0:
        results = summary.get("results", [])
        for rec in results if isinstance(results, list) else []:
            if isinstance(rec, dict) and rec.get("answer") == "sat":
                metrics = rec.get("metrics")
                if not isinstance(metrics, dict) or int(metrics["N_neg"]) != 0 or int(metrics["rawH"]) < int(summary["target_rawH"]):
                    fail(f"S6-BOUND-5 SAT witness failed exact metric check: {rec}")
    print(
        "PASS S6-BOUND-5/S6-CERT-PACK-3 one-context multi-chunk pack: "
        f"nodes={summary['total_nodes']}, next={summary['next_offset']}, "
        f"certified={summary['certified_unsat_entries']}, SAT={summary['sat_nodes']}, UNKNOWN={summary['unknown_nodes']}"
    )


def verify_bound7(args: argparse.Namespace) -> None:
    summary = bound7_smt_unknown_tail_closure(
        target_rawH=args.bound7_target_rawH,
        timeout_ms=args.bound7_timeout_ms,
    )
    print(
        "S6-BOUND-7 targeted UNKNOWN tail closure: "
        f"nodes={summary['targeted_nodes']} target_rawH>={summary['target_rawH']} "
        f"timeout_ms={summary['timeout_ms']} UNSAT={summary['unsat_nodes']} "
        f"SAT={summary['sat_nodes']} UNKNOWN={summary['unknown_nodes']} "
        f"closed_segment={summary['closed_segment_certified_unsat_entries']} "
        f"cumulative_certified={summary['cumulative_certified_unsat_entries']} "
        f"build={summary['build_seconds']}s checks={summary['check_seconds']}s elapsed={summary['elapsed_seconds']}s"
    )
    results = summary.get("results", [])
    if isinstance(results, list):
        for rec in results:
            if isinstance(rec, dict):
                print(
                    "S6-UNKNOWN-1 targeted entry "
                    f"global#{rec['node_index']} answer={rec['answer']} seconds={rec['seconds']} fixed={rec['fixed_signature']}"
                )

    is_reference = (
        args.bound7_target_rawH == BOUND1_TARGET_RAW_H
        and args.bound7_timeout_ms == BOUND7_NODE_TIMEOUT_MS
    )
    if is_reference:
        checks = {
            "depth": BOUND7_EXPECTED_TARGETED["depth"],
            "source_start_offset": BOUND7_EXPECTED_TARGETED["source_start_offset"],
            "source_chunk_limit": BOUND7_EXPECTED_TARGETED["source_chunk_limit"],
            "source_chunks": BOUND7_EXPECTED_TARGETED["source_chunks"],
            "source_next_offset": BOUND7_EXPECTED_TARGETED["source_next_offset"],
            "source_total_nodes": BOUND7_EXPECTED_TARGETED["source_total_nodes"],
            "source_replay_unsat_nodes": BOUND7_EXPECTED_TARGETED["source_replay_unsat_nodes"],
            "source_replay_unknown_nodes": BOUND7_EXPECTED_TARGETED["source_replay_unknown_nodes"],
            "targeted_nodes": BOUND7_EXPECTED_TARGETED["targeted_nodes"],
            "timeout_ms": BOUND7_EXPECTED_TARGETED["targeted_timeout_ms"],
            "unsat_nodes": BOUND7_EXPECTED_TARGETED["unsat_nodes"],
            "sat_nodes": BOUND7_EXPECTED_TARGETED["sat_nodes"],
            "unknown_nodes": BOUND7_EXPECTED_TARGETED["unknown_nodes"],
            "targeted_certified_unsat_entries": BOUND7_EXPECTED_TARGETED["targeted_certified_unsat_entries"],
            "closed_segment_certified_unsat_entries": BOUND7_EXPECTED_TARGETED["closed_segment_certified_unsat_entries"],
            "cumulative_checked_nodes": BOUND7_EXPECTED_TARGETED["cumulative_checked_nodes"],
            "cumulative_certified_unsat_entries": BOUND7_EXPECTED_TARGETED["cumulative_certified_unsat_entries"],
        }
        for key, value in checks.items():
            if summary[key] != value:
                fail(f"S6-BOUND-7 reference expected {key}={value}, got {summary[key]}")
        if summary["fixed_count_min"] != 9 or summary["fixed_count_max"] != 9:
            fail(f"S6-BOUND-7 reference fixed-count mismatch: {summary}")
    if int(summary["sat_nodes"]) > 0:
        for rec in results if isinstance(results, list) else []:
            if isinstance(rec, dict) and rec.get("answer") == "sat":
                metrics = rec.get("metrics")
                if not isinstance(metrics, dict) or int(metrics["N_neg"]) != 0 or int(metrics["rawH"]) < int(summary["target_rawH"]):
                    fail(f"S6-BOUND-7 SAT witness failed exact metric check: {rec}")
    print(
        "PASS S6-UNKNOWN-1/S6-BOUND-7 targeted UNKNOWN closure: "
        f"targeted={summary['targeted_nodes']}, certified={summary['targeted_certified_unsat_entries']}, "
        f"SAT={summary['sat_nodes']}, UNKNOWN={summary['unknown_nodes']}"
    )


def verify_bound8(args: argparse.Namespace) -> None:
    summary = bound5_smt_multi_chunk_pack(
        depth=BOUND8_EXPECTED_RUN["depth"],
        start_offset=BOUND8_EXPECTED_RUN["start_offset"],
        chunk_limit=BOUND8_EXPECTED_RUN["chunk_limit"],
        chunks=BOUND8_EXPECTED_RUN["chunks_requested"],
        target_rawH=args.bound8_target_rawH,
        timeout_ms=args.bound8_timeout_ms,
    )
    print(
        "S6-BOUND-8 wide SMT multi-chunk pack: "
        f"depth={summary['depth']} start={summary['start_offset']} limit={summary['chunk_limit']} "
        f"chunks={summary['chunks_completed']}/{summary['chunks_requested']} next={summary['next_offset']} "
        f"total_nodes={summary['total_nodes']} timeout_ms={summary['timeout_ms']} "
        f"UNSAT={summary['unsat_nodes']} SAT={summary['sat_nodes']} UNKNOWN={summary['unknown_nodes']} "
        f"certified={summary['certified_unsat_entries']} noncertified={summary['noncertified_nodes']} "
        f"build={summary['build_seconds']}s checks={summary['check_seconds']}s elapsed={summary['elapsed_seconds']}s"
    )
    chunks = summary.get("chunk_summaries", [])
    if isinstance(chunks, list):
        for chunk in chunks:
            if isinstance(chunk, dict):
                print(
                    "S6-CERT-PACK-6 chunk "
                    f"#{chunk['chunk_index']} offset={chunk['offset']} nodes={chunk['nodes']} "
                    f"UNSAT={chunk['unsat_nodes']} SAT={chunk['sat_nodes']} UNKNOWN={chunk['unknown_nodes']} "
                    f"next={chunk['next_offset']}"
                )

    is_reference = (
        args.bound8_target_rawH == BOUND1_TARGET_RAW_H
        and args.bound8_timeout_ms == BOUND8_EXPECTED_RUN["timeout_ms"]
    )
    if is_reference:
        for key, value in BOUND8_EXPECTED_RUN.items():
            if key in ("cumulative_checked_nodes", "cumulative_certified_unsat_entries", "timeout_ms", "chunk_unsat_profile", "chunk_unknown_profile"):
                continue
            if summary[key] != value:
                fail(f"S6-BOUND-8 reference expected {key}={value}, got {summary[key]}")
        if summary["timeout_ms"] != BOUND8_EXPECTED_RUN["timeout_ms"]:
            fail(f"S6-BOUND-8 reference timeout mismatch: {summary}")
        if summary["fixed_count_min"] != 9 or summary["fixed_count_max"] != 9:
            fail(f"S6-BOUND-8 reference fixed-count mismatch: {summary}")
    if int(summary["sat_nodes"]) > 0:
        results = summary.get("results", [])
        for rec in results if isinstance(results, list) else []:
            if isinstance(rec, dict) and rec.get("answer") == "sat":
                metrics = rec.get("metrics")
                if not isinstance(metrics, dict) or int(metrics["N_neg"]) != 0 or int(metrics["rawH"]) < int(summary["target_rawH"]):
                    fail(f"S6-BOUND-8 SAT witness failed exact metric check: {rec}")
    print(
        "PASS S6-BOUND-8/S6-CERT-PACK-6 wide SMT multi-chunk pack: "
        f"nodes={summary['total_nodes']}, next={summary['next_offset']}, "
        f"certified={summary['certified_unsat_entries']}, SAT={summary['sat_nodes']}, UNKNOWN={summary['unknown_nodes']}"
    )


def verify_bound9(args: argparse.Namespace) -> None:
    summary = bound5_smt_multi_chunk_pack(
        depth=BOUND9_EXPECTED_RUN["depth"],
        start_offset=BOUND9_EXPECTED_RUN["start_offset"],
        chunk_limit=BOUND9_EXPECTED_RUN["chunk_limit"],
        chunks=BOUND9_EXPECTED_RUN["chunks_requested"],
        target_rawH=args.bound9_target_rawH,
        timeout_ms=args.bound9_timeout_ms,
    )
    print(
        "S6-BOUND-9 wide SMT multi-chunk pack: "
        f"depth={summary['depth']} start={summary['start_offset']} limit={summary['chunk_limit']} "
        f"chunks={summary['chunks_completed']}/{summary['chunks_requested']} next={summary['next_offset']} "
        f"total_nodes={summary['total_nodes']} timeout_ms={summary['timeout_ms']} "
        f"UNSAT={summary['unsat_nodes']} SAT={summary['sat_nodes']} UNKNOWN={summary['unknown_nodes']} "
        f"certified={summary['certified_unsat_entries']} noncertified={summary['noncertified_nodes']} "
        f"build={summary['build_seconds']}s checks={summary['check_seconds']}s elapsed={summary['elapsed_seconds']}s"
    )
    chunks = summary.get("chunk_summaries", [])
    if isinstance(chunks, list):
        for chunk in chunks:
            if isinstance(chunk, dict):
                print(
                    "S6-CERT-PACK-7 chunk "
                    f"#{chunk['chunk_index']} offset={chunk['offset']} nodes={chunk['nodes']} "
                    f"UNSAT={chunk['unsat_nodes']} SAT={chunk['sat_nodes']} UNKNOWN={chunk['unknown_nodes']} "
                    f"next={chunk['next_offset']}"
                )

    is_reference = (
        args.bound9_target_rawH == BOUND1_TARGET_RAW_H
        and args.bound9_timeout_ms == BOUND9_EXPECTED_RUN["timeout_ms"]
    )
    if is_reference:
        for key, value in BOUND9_EXPECTED_RUN.items():
            if key in ("cumulative_checked_nodes", "cumulative_certified_unsat_entries", "timeout_ms", "chunk_unsat_profile", "chunk_unknown_profile"):
                continue
            if summary[key] != value:
                fail(f"S6-BOUND-9 reference expected {key}={value}, got {summary[key]}")
        if summary["timeout_ms"] != BOUND9_EXPECTED_RUN["timeout_ms"]:
            fail(f"S6-BOUND-9 reference timeout mismatch: {summary}")
        if summary["fixed_count_min"] != 9 or summary["fixed_count_max"] != 9:
            fail(f"S6-BOUND-9 reference fixed-count mismatch: {summary}")
    if int(summary["sat_nodes"]) > 0:
        results = summary.get("results", [])
        for rec in results if isinstance(results, list) else []:
            if isinstance(rec, dict) and rec.get("answer") == "sat":
                metrics = rec.get("metrics")
                if not isinstance(metrics, dict) or int(metrics["N_neg"]) != 0 or int(metrics["rawH"]) < int(summary["target_rawH"]):
                    fail(f"S6-BOUND-9 SAT witness failed exact metric check: {rec}")
    print(
        "PASS S6-BOUND-9/S6-CERT-PACK-7 wide SMT multi-chunk pack: "
        f"nodes={summary['total_nodes']}, next={summary['next_offset']}, "
        f"certified={summary['certified_unsat_entries']}, SAT={summary['sat_nodes']}, UNKNOWN={summary['unknown_nodes']}"
    )


def verify_bound10(args: argparse.Namespace) -> None:
    summary = bound5_smt_multi_chunk_pack(
        depth=BOUND10_EXPECTED_RUN["depth"],
        start_offset=BOUND10_EXPECTED_RUN["start_offset"],
        chunk_limit=BOUND10_EXPECTED_RUN["chunk_limit"],
        chunks=BOUND10_EXPECTED_RUN["chunks_requested"],
        target_rawH=args.bound10_target_rawH,
        timeout_ms=args.bound10_timeout_ms,
    )
    print(
        "S6-BOUND-10 wide SMT multi-chunk pack: "
        f"depth={summary['depth']} start={summary['start_offset']} limit={summary['chunk_limit']} "
        f"chunks={summary['chunks_completed']}/{summary['chunks_requested']} next={summary['next_offset']} "
        f"total_nodes={summary['total_nodes']} timeout_ms={summary['timeout_ms']} "
        f"UNSAT={summary['unsat_nodes']} SAT={summary['sat_nodes']} UNKNOWN={summary['unknown_nodes']} "
        f"certified={summary['certified_unsat_entries']} noncertified={summary['noncertified_nodes']} "
        f"build={summary['build_seconds']}s checks={summary['check_seconds']}s elapsed={summary['elapsed_seconds']}s"
    )
    chunks = summary.get("chunk_summaries", [])
    if isinstance(chunks, list):
        for chunk in chunks:
            if isinstance(chunk, dict):
                print(
                    "S6-CERT-PACK-8 chunk "
                    f"#{chunk['chunk_index']} offset={chunk['offset']} nodes={chunk['nodes']} "
                    f"UNSAT={chunk['unsat_nodes']} SAT={chunk['sat_nodes']} UNKNOWN={chunk['unknown_nodes']} "
                    f"next={chunk['next_offset']}"
                )

    is_reference = (
        args.bound10_target_rawH == BOUND1_TARGET_RAW_H
        and args.bound10_timeout_ms == BOUND10_EXPECTED_RUN["timeout_ms"]
    )
    if is_reference:
        for key, value in BOUND10_EXPECTED_RUN.items():
            if key in ("cumulative_checked_nodes", "cumulative_certified_unsat_entries", "timeout_ms", "chunk_unsat_profile", "chunk_unknown_profile"):
                continue
            if summary[key] != value:
                fail(f"S6-BOUND-10 reference expected {key}={value}, got {summary[key]}")
        if summary["timeout_ms"] != BOUND10_EXPECTED_RUN["timeout_ms"]:
            fail(f"S6-BOUND-10 reference timeout mismatch: {summary}")
        if summary["fixed_count_min"] != 9 or summary["fixed_count_max"] != 9:
            fail(f"S6-BOUND-10 reference fixed-count mismatch: {summary}")
    if int(summary["sat_nodes"]) > 0:
        results = summary.get("results", [])
        for rec in results if isinstance(results, list) else []:
            if isinstance(rec, dict) and rec.get("answer") == "sat":
                metrics = rec.get("metrics")
                if not isinstance(metrics, dict) or int(metrics["N_neg"]) != 0 or int(metrics["rawH"]) < int(summary["target_rawH"]):
                    fail(f"S6-BOUND-10 SAT witness failed exact metric check: {rec}")
    print(
        "PASS S6-BOUND-10/S6-CERT-PACK-8 wide SMT multi-chunk pack: "
        f"nodes={summary['total_nodes']}, next={summary['next_offset']}, "
        f"certified={summary['certified_unsat_entries']}, SAT={summary['sat_nodes']}, UNKNOWN={summary['unknown_nodes']}"
    )


def verify_certpack_final(args: argparse.Namespace) -> None:
    coverage = certpack_final_static_coverage()
    segments_path = args.final_pack_run_dir / "segments.csv"
    if not segments_path.is_file():
        fail(f"S6-CERT-PACK-FINAL bundle segment table missing: {segments_path}")
    segment_rows = certpack_read_csv(segments_path)
    if len(segment_rows) != len(CERTPACK_FINAL_SEGMENTS):
        fail(f"S6-CERT-PACK-FINAL expected {len(CERTPACK_FINAL_SEGMENTS)} segment rows, got {len(segment_rows)}")
    for row, expected in zip(segment_rows, CERTPACK_FINAL_SEGMENTS):
        name, start, end, certified = expected
        label = f"segments.csv:{name}"
        if row.get("segment") != name:
            fail(f"{label}: segment name mismatch, got {row.get('segment')!r}")
        if certpack_int(row, "start_offset", label) != start:
            fail(f"{label}: start_offset mismatch")
        if certpack_int(row, "end_offset", label) != end:
            fail(f"{label}: end_offset mismatch")
        if certpack_int(row, "nodes", label) != end - start:
            fail(f"{label}: nodes mismatch")
        if certpack_int(row, "certified_unsat", label) != certified:
            fail(f"{label}: certified_unsat mismatch")
        for field in ("sat", "unknown", "unresolved"):
            if certpack_int(row, field, label) != 0:
                fail(f"{label}: expected {field}=0")
    summary = certpack_final_audit(args.final_pack_run_dir)
    if coverage["end_offset"] != summary["frontier_total"]:
        fail(f"S6-CERT-PACK-FINAL static coverage/frontier mismatch: coverage={coverage}, summary={summary}")
    if summary["checked_nodes"] != BOUND11_EXPECTED_RUN["total_nodes"]:
        fail(f"S6-BOUND-11 expected checked_nodes={BOUND11_EXPECTED_RUN['total_nodes']}, got {summary['checked_nodes']}")
    if summary["unsat_nodes"] != BOUND11_EXPECTED_RUN["unsat_nodes"]:
        fail(f"S6-BOUND-11 expected unsat_nodes={BOUND11_EXPECTED_RUN['unsat_nodes']}, got {summary['unsat_nodes']}")
    if coverage["certified_unsat_entries"] != CERTPACK_FINAL_EXPECTED["certified_unsat_entries"]:
        fail(f"S6-CERT-PACK-FINAL expected certified={CERTPACK_FINAL_EXPECTED['certified_unsat_entries']}, got {coverage['certified_unsat_entries']}")
    print(
        "PASS S6-BOUND-11/S6-CERT-PACK-9 audited overnight tail: "
        f"range=[{summary['start_offset']},{summary['end_offset']}), "
        f"UNSAT={summary['unsat_nodes']}, SAT={summary['sat_nodes']}, UNKNOWN={summary['unknown_nodes']}, "
        f"chunks={summary['chunks']}, windows={summary['windows']}, rerun_rows={summary['rerun_rows']}"
    )
    print(
        "PASS S6-CERT-PACK-FINAL/S6-H2 coverage: "
        f"segments={coverage['segments']}, certified={coverage['certified_unsat_entries']}/"
        f"{CERTPACK_FINAL_EXPECTED['frontier_total']}, SAT=0, unresolved=0, pure_max=7020"
    )


def verify_h1_range(args: argparse.Namespace) -> None:
    summary = h1_eval_audit(args.h1_run_dir)
    if int(summary["checked_points"]) != OMEGA_PRIME_POINTS:
        fail(f"S6-H1 expected checked_points={OMEGA_PRIME_POINTS}, got {summary['checked_points']}")
    if int(summary["upper_violations"]) != 0 or int(summary["lower_violations"]) != 0:
        fail(f"S6-H1 expected zero default-threshold violations, got {summary}")
    if int(summary["min_H_tot"]) != H1_EXPECTED_RANGE["min_H_tot"] or int(summary["max_H_tot"]) != H1_EXPECTED_RANGE["max_H_tot"]:
        fail(f"S6-H1 range mismatch: {summary}")
    print(
        "PASS S6-H1 global H range: "
        f"points={summary['checked_points']}, H_tot=[{summary['min_H_tot']},{summary['max_H_tot']}], "
        f"rawH=[{summary['min_rawH']},{summary['max_rawH']}], "
        f"endpoint_counts=min:{summary['min_count']} max:{summary['max_count']}, rerun={summary['rerun']}:{summary['rerun_rows']}"
    )


def verify_h4_signed_frontier(args: argparse.Namespace) -> None:
    summary = h4_classifier_audit(args.h4_run_dir)
    if int(summary["checked_points"]) != OMEGA_PRIME_POINTS:
        fail(f"S6-H4 expected checked_points={OMEGA_PRIME_POINTS}, got {summary['checked_points']}")
    if int(summary["high_points"]) != H4_EXPECTED_RANGE["high_points"]:
        fail(f"S6-H4 high point count mismatch: {summary}")
    if int(summary["high_pure_points"]) != 0 or int(summary["high_impure_points"]) != H4_EXPECTED_RANGE["high_impure_points"]:
        fail(f"S6-H4 signed high-region counts mismatch: {summary}")
    if summary["max_N_neg_values"] != H4_EXPECTED_RANGE["max_N_neg_values"]:
        fail(f"S6-H4 max N_neg values mismatch: {summary}")
    print(
        "PASS S6-H4 signed-cancellation frontier: "
        f"points={summary['checked_points']}, high_rawH>={H4_EXPECTED_RANGE['pair_min_rawH']} count={summary['high_points']}, "
        f"pure_high={summary['high_pure_points']}, pair=(rawH=1217,N_-=3,count={summary['max_count']}), "
        f"witnesses={summary['witness_rows']}, rerun={summary['rerun']}:{summary['rerun_rows']}"
    )


def verify_h3_guardrail() -> None:
    if H3_PAB_WORD == H3_ROW_COMPLEMENT_WORD:
        fail("S6-H3 guardrail witnesses must be distinct")
    witness_words = {word for _label, word in H3_GUARDRAIL_WITNESSES}
    frontier_words = set(ENGINE0_PURE_FRONTIER_WITNESSES)
    if not witness_words <= frontier_words:
        fail(f"S6-H3 witnesses must be retained in ENGINE0 pure frontier list: {witness_words - frontier_words}")

    summaries = []
    for label, word in H3_GUARDRAIL_WITNESSES:
        metrics = h_metrics_reduced(word)
        for key, expected in H3_EXPECTED_WITNESS_METRICS.items():
            if int(metrics[key]) != expected:
                fail(f"S6-H3 {label} metric {key}={metrics[key]}, expected {expected}")
        dom = domain_from_x21(word)
        leaf = partial_node_bounds(dom)
        if int(leaf["H_lower"]) != H3_EXPECTED_WITNESS_METRICS["H_tot"] or int(leaf["H_upper"]) != H3_EXPECTED_WITNESS_METRICS["H_tot"]:
            fail(f"S6-H3 {label} interval leaf is not exact at H=7020: {leaf}")
        if int(leaf["local_impossible"]) != 0 or int(leaf["local_forced"]) != 243:
            fail(f"S6-H3 {label} is not a pure forced leaf: {leaf}")
        summaries.append(f"{label}:{word}")

    print(
        "PASS S6-H3 PAB/row-complement guardrail: "
        f"witnesses={';'.join(summaries)}, H_tot=7020, N_neg=0, nonunique_H_selector=1"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Unified Stage-6 verifier: S6-BD, S6-RED, S6-CERT-IF, S6-CERT-ENGINE-0, S6-CERT-ENGINE-1, S6-BRANCH-0, S6-SMT-0, and optional branch/SMT runners.")
    ap.add_argument("--reference-dir", type=Path, default=default_reference_dir(), help="Directory containing L1.zip, unpacked L1/, or the cycle1_layers123 reference")
    ap.add_argument("--table", type=Path, default=DEFAULT_TABLE, help="Unified Stage-6 mathematical results CSV")
    ap.add_argument("--write-table", action="store_true", help="Regenerate the unified results table")
    ap.add_argument("--sample-count", type=int, default=32, help="Number of deterministic generic samples")
    ap.add_argument("--skip-column-blind", action="store_true", help="Skip exhaustive column-blind x Delta local-formula check")
    ap.add_argument("--skip-engine0", action="store_true", help="Skip S6-CERT-ENGINE-0 vectorized kernel and column-blind certificate checks")
    ap.add_argument("--run-engine0-affine", action="store_true", help="Run the exact affine x Delta S6-CERT-ENGINE-0 certificate check")
    ap.add_argument("--skip-engine1", action="store_true", help="Skip S6-CERT-ENGINE-1 partial-domain interval checks")
    ap.add_argument("--skip-branch0", action="store_true", help="Skip S6-BRANCH-0 branch/frontier scout checks")
    ap.add_argument("--skip-smt0", action="store_true", help="Skip S6-SMT-0 Z3 column-blind solver-interface smoke check")
    ap.add_argument("--skip-certpack-final", action="store_true", help="Skip S6-CERT-PACK-FINAL artifact audit")
    ap.add_argument("--skip-h1", action="store_true", help="Skip S6-H1 exact range artifact audit")
    ap.add_argument("--skip-h3", action="store_true", help="Skip S6-H3 PAB/row-complement guardrail check")
    ap.add_argument("--skip-h4", action="store_true", help="Skip S6-H4 signed-cancellation classifier artifact audit")
    ap.add_argument("--only-certpack-final", action="store_true", help="Run only the S6-CERT-PACK-FINAL artifact audit")
    ap.add_argument("--only-h1", action="store_true", help="Run only the S6-H1 exact range artifact audit")
    ap.add_argument("--only-h3", action="store_true", help="Run only the S6-H3 PAB/row-complement guardrail check")
    ap.add_argument("--only-h4", action="store_true", help="Run only the S6-H4 signed-cancellation classifier artifact audit")
    ap.add_argument("--final-pack-run-dir", type=Path, default=BOUND11_FINAL_RUN_DIR, help="Directory containing the audited overnight H2 run artifacts")
    ap.add_argument("--h1-run-dir", type=Path, default=H1_FINAL_RUN_DIR, help="Directory containing the audited H1 exact evaluator artifacts")
    ap.add_argument("--h4-run-dir", type=Path, default=H4_FINAL_RUN_DIR, help="Directory containing the audited H4 classifier artifacts")
    ap.add_argument("--run-smt-global", action="store_true", help="Run optional S6-SMT-1 global pure high-H SMT query")
    ap.add_argument("--only-smt-global", action="store_true", help="Run only the optional S6-SMT-1 global query, without the standard verifier checks")
    ap.add_argument("--smt-timeout-ms", type=int, default=600000, help="Z3 timeout for --run-smt-global in milliseconds")
    ap.add_argument("--smt-target-rawH", type=int, default=SMT1_GLOBAL_GT_RAW_H, help="RawH lower bound for --run-smt-global")
    ap.add_argument("--run-branch1", action="store_true", help="Run optional S6-BRANCH-1 depth-8 interval scout")
    ap.add_argument("--run-branch2", action="store_true", help="Run optional S6-BRANCH-2 greedy adaptive interval scout")
    ap.add_argument("--run-branch3", action="store_true", help="Run optional S6-BRANCH-3 bounded frontier branch-and-prune runner")
    ap.add_argument("--only-branch3", action="store_true", help="Run only the optional S6-BRANCH-3 frontier runner, without standard verifier checks")
    ap.add_argument("--branch3-depth", type=int, default=BRANCH3_REFERENCE_DEPTH, help="Depth for --run-branch3")
    ap.add_argument("--branch3-order", choices=BRANCH3_ORDER_NAMES, default="greedy_B_first", help="Coordinate order for --run-branch3")
    ap.add_argument("--branch3-target-H", type=int, default=BRANCH3_TARGET_H, help="Pure-frontier H upper-pruning target for --run-branch3")
    ap.add_argument("--branch3-max-generated", type=int, default=0, help="Optional cap on generated child nodes for --run-branch3; 0 means no cap")
    ap.add_argument("--branch3-time-limit", type=float, default=0.0, help="Optional wall-clock cap in seconds for --run-branch3; 0 means no cap")
    ap.add_argument("--run-bound1", action="store_true", help="Run optional S6-BOUND-1 SMT node evaluator probe")
    ap.add_argument("--only-bound1", action="store_true", help="Run only the optional S6-BOUND-1 SMT node evaluator probe")
    ap.add_argument("--bound1-depth", type=int, default=BOUND1_REFERENCE_DEPTH, help="Branch depth for --run-bound1")
    ap.add_argument("--bound1-sample-limit", type=int, default=BOUND1_REFERENCE_SAMPLE_LIMIT, help="Number of live branch nodes to probe for --run-bound1")
    ap.add_argument("--bound1-timeout-ms", type=int, default=BOUND1_NODE_TIMEOUT_MS, help="Z3 timeout per node check for --run-bound1")
    ap.add_argument("--bound1-target-rawH", type=int, default=SMT1_GLOBAL_GT_RAW_H, help="RawH lower bound for --run-bound1")
    ap.add_argument("--run-bound2", action="store_true", help="Run optional S6-BOUND-2 batched SMT node pack")
    ap.add_argument("--only-bound2", action="store_true", help="Run only the optional S6-BOUND-2 batched SMT node pack")
    ap.add_argument("--bound2-depth", type=int, default=BOUND2_REFERENCE_DEPTH, help="Branch depth for --run-bound2")
    ap.add_argument("--bound2-batch-limit", type=int, default=BOUND2_REFERENCE_BATCH_LIMIT, help="Number of live branch nodes to include in --run-bound2")
    ap.add_argument("--bound2-timeout-ms", type=int, default=BOUND2_NODE_TIMEOUT_MS, help="Z3 timeout per node check for --run-bound2")
    ap.add_argument("--bound2-target-rawH", type=int, default=BOUND1_TARGET_RAW_H, help="RawH lower bound for --run-bound2")
    ap.add_argument("--run-bound3", action="store_true", help="Run optional S6-BOUND-3 resumable SMT chunk pack")
    ap.add_argument("--only-bound3", action="store_true", help="Run only the optional S6-BOUND-3 resumable SMT chunk pack")
    ap.add_argument("--bound3-depth", type=int, default=BOUND3_REFERENCE_DEPTH, help="Branch depth for --run-bound3")
    ap.add_argument("--bound3-offset", type=int, default=BOUND3_REFERENCE_CHUNK_OFFSET, help="Live-frontier node offset for --run-bound3")
    ap.add_argument("--bound3-limit", type=int, default=BOUND3_REFERENCE_CHUNK_LIMIT, help="Live-frontier node limit for --run-bound3")
    ap.add_argument("--bound3-timeout-ms", type=int, default=BOUND2_NODE_TIMEOUT_MS, help="Z3 timeout per node check for --run-bound3")
    ap.add_argument("--bound3-target-rawH", type=int, default=BOUND1_TARGET_RAW_H, help="RawH lower bound for --run-bound3")
    ap.add_argument("--run-bound5", action="store_true", help="Run optional S6-BOUND-5 one-context SMT multi-chunk pack")
    ap.add_argument("--only-bound5", action="store_true", help="Run only the optional S6-BOUND-5 one-context SMT multi-chunk pack")
    ap.add_argument("--bound5-depth", type=int, default=BOUND5_REFERENCE_DEPTH, help="Branch depth for --run-bound5")
    ap.add_argument("--bound5-offset", type=int, default=BOUND5_REFERENCE_START_OFFSET, help="Live-frontier start offset for --run-bound5")
    ap.add_argument("--bound5-limit", type=int, default=BOUND5_REFERENCE_CHUNK_LIMIT, help="Nodes per chunk for --run-bound5")
    ap.add_argument("--bound5-chunks", type=int, default=BOUND5_REFERENCE_CHUNKS, help="Number of chunks to run with one SMT context for --run-bound5")
    ap.add_argument("--bound5-timeout-ms", type=int, default=BOUND2_NODE_TIMEOUT_MS, help="Z3 timeout per node check for --run-bound5")
    ap.add_argument("--bound5-target-rawH", type=int, default=BOUND1_TARGET_RAW_H, help="RawH lower bound for --run-bound5")
    ap.add_argument("--run-bound7", action="store_true", help="Run optional S6-BOUND-7 targeted UNKNOWN-tail closure")
    ap.add_argument("--only-bound7", action="store_true", help="Run only the optional S6-BOUND-7 targeted UNKNOWN-tail closure")
    ap.add_argument("--bound7-timeout-ms", type=int, default=BOUND7_NODE_TIMEOUT_MS, help="Z3 timeout per targeted node check for --run-bound7")
    ap.add_argument("--bound7-target-rawH", type=int, default=BOUND1_TARGET_RAW_H, help="RawH lower bound for --run-bound7")
    ap.add_argument("--run-bound8", action="store_true", help="Run optional S6-BOUND-8 wide high-timeout multi-chunk pack")
    ap.add_argument("--only-bound8", action="store_true", help="Run only the optional S6-BOUND-8 wide high-timeout multi-chunk pack")
    ap.add_argument("--bound8-timeout-ms", type=int, default=BOUND8_EXPECTED_RUN["timeout_ms"], help="Z3 timeout per node check for --run-bound8")
    ap.add_argument("--bound8-target-rawH", type=int, default=BOUND1_TARGET_RAW_H, help="RawH lower bound for --run-bound8")
    ap.add_argument("--run-bound9", action="store_true", help="Run optional S6-BOUND-9 wide high-timeout multi-chunk pack")
    ap.add_argument("--only-bound9", action="store_true", help="Run only the optional S6-BOUND-9 wide high-timeout multi-chunk pack")
    ap.add_argument("--bound9-timeout-ms", type=int, default=BOUND9_EXPECTED_RUN["timeout_ms"], help="Z3 timeout per node check for --run-bound9")
    ap.add_argument("--bound9-target-rawH", type=int, default=BOUND1_TARGET_RAW_H, help="RawH lower bound for --run-bound9")
    ap.add_argument("--run-bound10", action="store_true", help="Run optional S6-BOUND-10 wide high-timeout multi-chunk pack")
    ap.add_argument("--only-bound10", action="store_true", help="Run only the optional S6-BOUND-10 wide high-timeout multi-chunk pack")
    ap.add_argument("--bound10-timeout-ms", type=int, default=BOUND10_EXPECTED_RUN["timeout_ms"], help="Z3 timeout per node check for --run-bound10")
    ap.add_argument("--bound10-target-rawH", type=int, default=BOUND1_TARGET_RAW_H, help="RawH lower bound for --run-bound10")
    args = ap.parse_args()

    if args.only_smt_global:
        run_smt_global(args)
        return 0
    if args.only_certpack_final:
        verify_certpack_final(args)
        return 0
    if args.only_h1:
        verify_h1_range(args)
        return 0
    if args.only_h3:
        verify_h3_guardrail()
        return 0
    if args.only_h4:
        verify_h4_signed_frontier(args)
        return 0
    if args.only_branch3:
        verify_branch3(args)
        return 0
    if args.only_bound1:
        verify_bound1(args)
        return 0
    if args.only_bound2:
        verify_bound2(args)
        return 0
    if args.only_bound3:
        verify_bound3(args)
        return 0
    if args.only_bound5:
        verify_bound5(args)
        return 0
    if args.only_bound7:
        verify_bound7(args)
        return 0
    if args.only_bound8:
        verify_bound8(args)
        return 0
    if args.only_bound9:
        verify_bound9(args)
        return 0
    if args.only_bound10:
        verify_bound10(args)
        return 0

    ensure_numpy_or_reexec(needs_numpy=(not args.skip_engine0 or not args.skip_branch0))

    rows = result_rows()
    sanity_check_result_rows(rows)
    if args.write_table:
        write_csv(args.table, rows)
        print(f"PASS wrote unified Stage-6 mathematical results table: {args.table}")
    else:
        assert_csv_equal(args.table, rows)
        print(f"PASS unified Stage-6 mathematical results table: {args.table}")

    reference_dir = args.reference_dir.resolve()
    h_core = load_h_core(reference_dir)
    verify_reference_witnesses(reference_dir, h_core)
    if not args.skip_column_blind:
        verify_column_blind(h_core)
    verify_samples(h_core, args.sample_count)
    if not args.skip_engine0:
        verify_engine0_kernel_against_reduced()
        verify_engine0_column_blind()
        if args.run_engine0_affine:
            verify_engine0_affine()
    if not args.skip_engine1:
        verify_engine1_interval_layer()
    if not args.skip_branch0:
        verify_branch0()
    if not args.skip_smt0:
        verify_smt0()
    if not args.skip_certpack_final:
        verify_certpack_final(args)
    if not args.skip_h1:
        verify_h1_range(args)
    if not args.skip_h3:
        verify_h3_guardrail()
    if not args.skip_h4:
        verify_h4_signed_frontier(args)
    if args.run_smt_global:
        run_smt_global(args)
    if args.run_branch1:
        verify_branch1()
    if args.run_branch2:
        verify_branch2()
    if args.run_branch3:
        verify_branch3(args)
    if args.run_bound1:
        verify_bound1(args)
    if args.run_bound2:
        verify_bound2(args)
    if args.run_bound3:
        verify_bound3(args)
    if args.run_bound5:
        verify_bound5(args)
    if args.run_bound7:
        verify_bound7(args)
    if args.run_bound8:
        verify_bound8(args)
    if args.run_bound9:
        verify_bound9(args)
    if args.run_bound10:
        verify_bound10(args)
    print("PASS S6-RED signature-distance reduction")
    print("PASS S6-CERT-IF finite certificate interface")
    if not args.skip_engine0:
        print("PASS S6-CERT-ENGINE-0 controlled-domain certificate engine")
    if not args.skip_engine1:
        print("PASS S6-CERT-ENGINE-1 partial-domain interval engine")
    if not args.skip_branch0:
        print("PASS S6-BRANCH-0 branch/frontier scout")
    if not args.skip_smt0:
        print("PASS S6-SMT-0 finite-domain SMT interface smoke")
    if not args.skip_certpack_final:
        print("PASS S6-CERT-PACK-FINAL audited H2 certificate package")
    if not args.skip_h1:
        print("PASS S6-H1 global H range theorem")
    if not args.skip_h3:
        print("PASS S6-H3 PAB/row-complement guardrail theorem")
    if not args.skip_h4:
        print("PASS S6-H4 signed-cancellation frontier theorem")
    if args.run_branch1:
        print("PASS S6-BRANCH-1 optional deep interval scout")
    if args.run_branch2:
        print("PASS S6-BRANCH-2 optional greedy adaptive interval scout")
    if args.run_branch3:
        print("PASS S6-BRANCH-3 optional bounded frontier runner")
    if args.run_bound1:
        print("PASS S6-BOUND-1 optional pure-aware SMT node evaluator")
    if args.run_bound2:
        print("PASS S6-BOUND-2 optional batched SMT node pack")
    if args.run_bound3:
        print("PASS S6-BOUND-3 optional resumable SMT chunk pack")
    if args.run_bound5:
        print("PASS S6-BOUND-5 optional one-context SMT multi-chunk pack")
    if args.run_bound7:
        print("PASS S6-BOUND-7 optional targeted UNKNOWN-tail closure")
    if args.run_bound8:
        print("PASS S6-BOUND-8 optional wide high-timeout multi-chunk pack")
    if args.run_bound9:
        print("PASS S6-BOUND-9 optional wide high-timeout multi-chunk pack")
    if args.run_bound10:
        print("PASS S6-BOUND-10 optional wide high-timeout multi-chunk pack")
    print("PASS Stage-6 unified verifier complete")
    return 0


def verify_bundle_markdown(path: Path) -> None:
    if not path.is_file():
        fail(f"bundle markdown is missing: {path}")
    text = path.read_text(encoding="utf-8")
    required = (
        "Theorem 6.1",
        "Global hidden-continuation frontier",
        "min_{x\\in\\Omega'}H_{tot}(x)=-2268",
        "max_{x\\in\\Omega'}H_{tot}(x)=7302",
        "max_{x\\in\\Omega'}\\{H_{tot}(x):N_-(x)=0\\}=7020",
        "twelve-point impure signed-cancellation spike",
    )
    missing = [needle for needle in required if needle not in text]
    if missing:
        fail(f"bundle markdown is missing required theorem text: {missing}")
    print(f"PASS bundle markdown theorem text: {path}")


def bundle_main() -> int:
    ap = argparse.ArgumentParser(description="Verify the compact Stage-6 theorem bundle.")
    ap.add_argument("--stage6-md", type=Path, default=SCRIPT_DIR / "stage6.md", help="Bundle theorem markdown")
    ap.add_argument("--h1-run-dir", type=Path, default=H1_FINAL_RUN_DIR, help="H1 raw artifact directory")
    ap.add_argument("--h2-run-dir", "--final-pack-run-dir", dest="final_pack_run_dir", type=Path, default=BOUND11_FINAL_RUN_DIR, help="H2 raw artifact directory")
    ap.add_argument("--h4-run-dir", type=Path, default=H4_FINAL_RUN_DIR, help="H4 raw artifact directory")
    ap.add_argument("--only-h1", action="store_true", help="Run only the H1 artifact audit")
    ap.add_argument("--only-h2", "--only-certpack-final", dest="only_h2", action="store_true", help="Run only the H2 pure-frontier artifact audit")
    ap.add_argument("--only-h3", action="store_true", help="Run only the PAB/row-complement witness sanity check")
    ap.add_argument("--only-h4", action="store_true", help="Run only the H4 signed-cancellation artifact audit")
    ap.add_argument("--skip-md", action="store_true", help="Skip stage6.md theorem-text sanity check")
    ap.add_argument("--skip-h1", action="store_true", help="Skip H1 artifact audit")
    ap.add_argument("--skip-h2", action="store_true", help="Skip H2 pure-frontier artifact audit")
    ap.add_argument("--skip-h3", action="store_true", help="Skip PAB/row-complement witness sanity check")
    ap.add_argument("--skip-h4", action="store_true", help="Skip H4 signed-cancellation artifact audit")
    args = ap.parse_args()

    if args.only_h1:
        verify_h1_range(args)
        return 0
    if args.only_h2:
        verify_certpack_final(args)
        return 0
    if args.only_h3:
        verify_h3_guardrail()
        return 0
    if args.only_h4:
        verify_h4_signed_frontier(args)
        return 0

    if not args.skip_md:
        verify_bundle_markdown(args.stage6_md)
    if not args.skip_h2:
        verify_certpack_final(args)
    if not args.skip_h1:
        verify_h1_range(args)
    if not args.skip_h3:
        verify_h3_guardrail()
    if not args.skip_h4:
        verify_h4_signed_frontier(args)
    print("PASS Stage-6 theorem bundle complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(bundle_main())
