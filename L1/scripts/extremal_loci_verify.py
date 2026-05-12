#!/usr/bin/env python3
"""Layer 1 v3: independent verifier for enumerated extremal loci.

Reads tables/layer1_v3_extremal_loci_solutions.csv and checks every enumerated
extremal solution by two independent finite evaluations:
  * direct 9^3 associativity count;
  * normalized 3^5 master-term count with block decomposition.

The enumeration/no-more-solutions claim is certified by the C++ branch-and-bound
counter, not by this verifier. This script verifies the listed solutions and
the S3/C2 orbit accounting using only the compact final-pack tables.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
from typing import Dict, Tuple

S = (0, 1, 2)
M = tuple(product(S, S))
LABELS = ("RRR", "RRS", "RSR", "RSS", "RST")
ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"


def comp(a: int, b: int) -> int:
    return (-a - b) % 3


def idx(a: int, b: int, e: int) -> int:
    a %= 3
    b %= 3
    e %= 3
    if b == 1:
        return 3 * a + e
    if b == 2:
        return 9 + 3 * a + e
    raise ValueError("cross coordinate requires b=1 or b=2")


def tau_x21(x: str) -> str:
    vals = [int(ch) for ch in x]
    y = [0] * 21
    for a, e in product(S, S):
        i = idx(a, 1, e)
        j = idx(-a, 2, -e)
        y[j] = (-vals[i]) % 3
        i2 = idx(a, 2, e)
        j2 = idx(-a, 1, -e)
        y[j2] = (-vals[i2]) % 3
    y[18] = (-vals[18]) % 3
    y[19] = (-vals[20]) % 3
    y[20] = (-vals[19]) % 3
    return "".join(map(str, y))


def canonical(x: str) -> str:
    return min(x, tau_x21(x))


def make_mult(x: str):
    vals = [int(ch) for ch in x]
    d = vals[18:21]

    def g(r1: int, c1: int, r2: int, c2: int) -> int:
        a = (c1 - r1) % 3
        b = (r2 - r1) % 3
        e = (c2 - r1) % 3
        if b == 1:
            return (r1 + vals[3 * a + e]) % 3
        if b == 2:
            return (r1 + vals[9 + 3 * a + e]) % 3
        raise ValueError("not a cross-row input")

    def mult(p: Tuple[int, int], q: Tuple[int, int]) -> Tuple[int, int]:
        r1, c1 = p
        r2, c2 = q
        if r1 != r2:
            return (r1, g(r1, c1, r2, c2))
        if c1 != c2:
            return (r1, comp(c1, c2))
        return (r1, (r1 + d[(c1 - r1) % 3]) % 3)

    return mult


def assoc_direct(x: str) -> int:
    mult = make_mult(x)
    return sum(
        1
        for a, b, c in product(M, repeat=3)
        if mult(mult(a, b), c) == mult(a, mult(b, c))
    )


def mval(vals: list[int], b: int, a: int, e: int) -> int:
    b %= 3
    a %= 3
    e %= 3
    if b == 0:
        return vals[18 + a] if a == e else comp(a, e)
    if b == 1:
        return vals[3 * a + e]
    return vals[9 + 3 * a + e]


def term_label(b: int, t: int) -> int:
    if b == 0 and t == 0:
        return 0
    if b == 0 and t != 0:
        return 1
    if b != 0 and t == 0:
        return 2
    if b != 0 and t == b:
        return 3
    return 4


def assoc_master_blocks(x: str) -> tuple[int, Dict[str, int]]:
    vals = [int(ch) for ch in x]
    raw = 0
    blocks = [0] * 5
    for b, t, a, e, f in product(S, S, S, S, S):
        xy = mval(vals, b, a, e)
        lhs = mval(vals, t, xy, f)
        yz = mval(vals, (t - b) % 3, (e - b) % 3, (f - b) % 3)
        rhs = mval(vals, b, a, (b + yz) % 3)
        if lhs == rhs:
            raw += 1
            blocks[term_label(b, t)] += 1
    return raw, dict(zip(LABELS, blocks))


def read_csv(name: str) -> list[dict[str, str]]:
    with (TABLES / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    rows = read_csv("layer1_v3_extremal_loci_solutions.csv")
    assert rows, "no extremal solutions loaded"

    seen = set()
    by_mode = defaultdict(list)
    for row in rows:
        x = row["x21"]
        assert len(x) == 21 and set(x) <= {"0", "1", "2"}
        assert x not in seen, f"duplicate solution: {x}"
        seen.add(x)

        mode = row["mode"]
        expected_raw = 21 if mode == "min" else 199
        raw, blocks = assoc_master_blocks(x)
        direct = assoc_direct(x)

        assert raw == expected_raw, (mode, x, raw)
        assert direct == 3 * raw, (mode, x, direct, raw)
        assert row["canonical_x21"] == canonical(x)
        assert row["tau_x21"] == tau_x21(x)
        assert row["tau_fixed"] == str(x == tau_x21(x))

        block_str = ";".join(f"{k}:{v}" for k, v in blocks.items())
        assert row["raw_blocks"] == block_str

        by_mode[mode].append(x)

    for mode, xs in sorted(by_mode.items()):
        fixed = sum(1 for x in xs if x == tau_x21(x))
        can_count = len({canonical(x) for x in xs})
        assert can_count == (len(xs) + fixed) // 2
        print(
            f"{mode}: solutions={len(xs)}, tau_fixed={fixed}, "
            f"S3_orbits={can_count}, block_patterns={dict(Counter(row['raw_blocks'] for row in rows if row['mode'] == mode))}"
        )

    print("All listed extremal solutions passed direct 9^3 and master 3^5 checks.")


if __name__ == "__main__":
    main()
