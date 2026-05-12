#!/usr/bin/env python3
"""Layer 1 v3 independent witness verifier.

Purpose: verify the certified-extrema witnesses by a compact Python implementation
independent of the C++ branch-and-bound solver.

It checks both:
  * direct 9^3 associativity count on M = F3 x F3;
  * normalized 3^5 master formula with block decomposition.
"""

from itertools import product
from typing import Dict, Tuple

S = (0, 1, 2)
M = tuple(product(S, S))

BLOCKS = {
    0: "RRR",  # b=0, t=0
    1: "RRS",  # b=0, t!=0
    2: "RSR",  # b!=0, t=0
    3: "RSS",  # b!=0, t=b
    4: "RST",  # b!=0, t!=0, t!=b
}

def mod3(x: int) -> int:
    return x % 3

def comp(a: int, b: int) -> int:
    return (-a - b) % 3

def parse_table(s: str) -> Tuple[int, ...]:
    assert len(s) == 9 and set(s) <= set("012"), s
    return tuple(int(ch) for ch in s)

def tab_get(T: Tuple[int, ...], a: int, e: int) -> int:
    return T[3 * (a % 3) + (e % 3)]

def mval(A: Tuple[int, ...], B: Tuple[int, ...], d: Tuple[int, ...], b: int, a: int, e: int) -> int:
    b, a, e = b % 3, a % 3, e % 3
    if b == 0:
        return d[a] if a == e else comp(a, e)
    if b == 1:
        return tab_get(A, a, e)
    return tab_get(B, a, e)

def mult(A: Tuple[int, ...], B: Tuple[int, ...], d: Tuple[int, ...], x: Tuple[int, int], y: Tuple[int, int]) -> Tuple[int, int]:
    r1, c1 = x
    r2, c2 = y
    if r1 == r2:
        if c1 == c2:
            return (r1, (r1 + d[(c1 - r1) % 3]) % 3)
        return (r1, comp(c1, c2))
    b = (r2 - r1) % 3
    a = (c1 - r1) % 3
    e = (c2 - r1) % 3
    return (r1, (r1 + mval(A, B, d, b, a, e)) % 3)

def assoc_direct(A: Tuple[int, ...], B: Tuple[int, ...], d: Tuple[int, ...]) -> int:
    count = 0
    for x, y, z in product(M, repeat=3):
        if mult(A, B, d, mult(A, B, d, x, y), z) == mult(A, B, d, x, mult(A, B, d, y, z)):
            count += 1
    return count

def block_label(b: int, t: int) -> str:
    if b == 0 and t == 0:
        return "RRR"
    if b == 0 and t != 0:
        return "RRS"
    if b != 0 and t == 0:
        return "RSR"
    if b != 0 and t == b:
        return "RSS"
    return "RST"

def assoc_master_blocks(A: Tuple[int, ...], B: Tuple[int, ...], d: Tuple[int, ...]) -> Tuple[int, Dict[str, int], int]:
    raw = 0
    raw_blocks = {name: 0 for name in BLOCKS.values()}
    for b, t, a, e, f in product(S, repeat=5):
        xy = mval(A, B, d, b, a, e)
        lhs = mval(A, B, d, t, xy, f)
        yz = mval(A, B, d, (t - b) % 3, (e - b) % 3, (f - b) % 3)
        rhs = mval(A, B, d, b, a, (b + yz) % 3)
        if lhs == rhs:
            raw += 1
            raw_blocks[block_label(b, t)] += 1
    return 3 * raw, {k: 3 * v for k, v in raw_blocks.items()}, raw

def verify(name: str, A_s: str, B_s: str, d_s: str, expected_assoc: int, expected_blocks: Dict[str, int]) -> Dict[str, object]:
    A, B, d = parse_table(A_s), parse_table(B_s), tuple(int(ch) for ch in d_s)
    direct = assoc_direct(A, B, d)
    master, blocks, raw = assoc_master_blocks(A, B, d)
    ok = direct == master == expected_assoc and blocks == expected_blocks
    return {
        "name": name,
        "A": A_s,
        "B": B_s,
        "d": d_s,
        "assoc_direct": direct,
        "assoc_master": master,
        "raw_master_terms": raw,
        "blocks": blocks,
        "expected_assoc": expected_assoc,
        "expected_blocks": expected_blocks,
        "ok": ok,
    }

def main() -> None:
    witnesses = [
        (
            "min63_previous_search",
            "210210210",
            "001021001",
            "100",
            63,
            {"RRR": 33, "RRS": 6, "RSR": 6, "RSS": 6, "RST": 12},
        ),
        (
            "min63_solver_alternate",
            "010210010",
            "021021021",
            "100",
            63,
            {"RRR": 33, "RRS": 6, "RSR": 6, "RSS": 6, "RST": 12},
        ),
        (
            "max597_previous_search",
            "110001110",
            "011100011",
            "111",
            597,
            {"RRR": 57, "RRS": 108, "RSR": 108, "RSS": 162, "RST": 162},
        ),
        (
            "max597_solver_alternate",
            "202020020",
            "220002002",
            "000",
            597,
            {"RRR": 57, "RRS": 108, "RSR": 108, "RSS": 162, "RST": 162},
        ),
    ]
    results = [verify(*w) for w in witnesses]
    for r in results:
        print(f"{r['name']}: direct={r['assoc_direct']} master={r['assoc_master']} raw={r['raw_master_terms']} ok={r['ok']}")
        print(f"  blocks={r['blocks']}")
    if not all(r["ok"] for r in results):
        raise SystemExit("verification failed")
    print("All v3 independent witness checks passed.")

if __name__ == "__main__":
    main()
