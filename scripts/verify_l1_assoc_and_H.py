#!/usr/bin/env python3
from pathlib import Path
import csv
import os

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"


def rows(name):
    with open(TABLES / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    zq = rows("l1_assoc_distribution.csv")
    raw = [int(r["raw"]) for r in zq]
    assoc = [int(r["assoc"]) for r in zq]
    count = [int(r["count"]) for r in zq]
    require(sum(count) == 3**21, "Z(q) counts do not sum to 3^21")
    require(len([c for c in count if c != 0]) == 167, "nonzero coefficient count mismatch")
    require(min(raw) == 21 and max(raw) == 199, "rawAssoc range mismatch")
    require(min(assoc) == 63 and max(assoc) == 597, "Assoc range mismatch")
    require(all(a == 3 * r for a, r in zip(assoc, raw)), "Assoc != 3*rawAssoc in Z(q) table")
    mode_i = max(range(len(count)), key=lambda i: count[i])
    require(assoc[mode_i] == 237 and count[mode_i] == 426_317_976, "mode mismatch")

    total = sum(count)
    mean_num = sum(a * c for a, c in zip(assoc, count))
    require(mean_num == 245 * total, "Assoc mean mismatch")
    # Var = E[X^2] - 245^2 = 27820/27.
    second_num = sum(a * a * c for a, c in zip(assoc, count))
    require(27 * (second_num - 245 * 245 * total) == 27820 * total, "Assoc variance mismatch")

    counts = rows("l1_extremal_loci_counts.csv")
    min_rows = [r for r in counts if r["mode"] == "min"]
    max_rows = [r for r in counts if r["mode"] == "max"]
    require(len(min_rows) == 8 and len(max_rows) == 3, "endpoint locus row counts mismatch")
    require(sum(int(r["solutions"]) for r in min_rows) == 24, "min endpoint count mismatch")
    require(sum(int(r["solutions"]) for r in max_rows) == 6, "max endpoint count mismatch")
    require(all(int(r["target_assoc"]) == 63 for r in min_rows), "min endpoint target mismatch")
    require(all(int(r["target_assoc"]) == 597 for r in max_rows), "max endpoint target mismatch")
    require(all(r["stopped_by_limit"] == "False" for r in counts), "endpoint certificate stopped by limit")

    orbits = rows("l1_extremal_loci_orbits.csv")
    require(len([r for r in orbits if r["mode"] == "min"]) == 12, "min endpoint orbit count mismatch")
    require(len([r for r in orbits if r["mode"] == "max"]) == 3, "max endpoint orbit count mismatch")
    require(all(int(r["assoc"]) in {63, 597} for r in orbits), "endpoint orbit assoc mismatch")

    solutions = rows("l1_extremal_loci_solutions.csv")
    require(len([r for r in solutions if r["mode"] == "min"]) == 24, "min endpoint witness count mismatch")
    require(len([r for r in solutions if r["mode"] == "max"]) == 6, "max endpoint witness count mismatch")
    require(all(int(r["assoc"]) == 63 for r in solutions if r["mode"] == "min"), "min witness assoc mismatch")
    require(all(int(r["assoc"]) == 597 for r in solutions if r["mode"] == "max"), "max witness assoc mismatch")

    proof_targets = rows("l1_assoc_proof_targets.csv")
    require(len(proof_targets) == 6, "assoc proof target row count mismatch")
    require({r["side"] for r in proof_targets} == {"minimum", "maximum"}, "assoc proof target sides mismatch")

    hsum = rows("l1H_controlled_summary.csv")
    require(len(hsum) == 3, "controlled H summary should have three strata")
    require(all(int(r["H_max"]) == 7302 for r in hsum), "controlled H_max mismatch")
    require(all(int(r["pure_H_max"]) == 7020 for r in hsum), "controlled pure_H_max mismatch")
    require(any(int(r["H_min"]) == -2268 for r in hsum), "controlled H_min -2268 missing")

    std = rows("l1H_standard_six.csv")
    pab = [r for r in std if "PAB" in r["label"]]
    require(len(pab) == 1, "PAB row missing in H_standard_six")
    require(int(pab[0]["Assoc"]) == 219, "PAB Assoc mismatch")
    require(int(pab[0]["H_tot"]) == 7020 and int(pab[0]["N_neg"]) == 0, "PAB H profile mismatch")

    os.write(1, b"PASS verify_l1_assoc_and_H\n")


if __name__ == "__main__":
    main()
    os._exit(0)
