#!/usr/bin/env python3
from pathlib import Path
import csv, os, sys

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"

def rows(name):
    with open(TABLES / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def main():
    chain = rows("l2_selection_chain.csv")
    totals = {r["stage"]: r["total"] for r in chain}
    require(totals.get("0") == "3^21", "Omega' total mismatch")
    require(totals.get("1") == "27", "information-compression total mismatch")
    require(totals.get("2") == "6", "anchor total mismatch")
    require(totals.get("3") == "2", "local Assoc_000 survivor total mismatch")
    require(totals.get("4") == "1", "pure C/J final survivor total mismatch")

    path = rows("l2_path_dependence_table.csv")
    selected = [r for r in path if r["selected_by_local_path_dependence"] == "True"]
    require(len(path) == 6, "expected six nontrivial column-blind rules")
    require(len(selected) == 2, "expected two local Assoc_000 survivors")
    require({r["label"] for r in selected} == {"g1=r2 / PAB", "row-complement"}, "local survivors mismatch")
    require(all(int(r["Assoc_000"]) == 219 for r in selected), "selected Assoc_000 mismatch")

    minimal = rows("l2_minimal_selector_sets.csv")
    full = [r for r in minimal if r["set_name"] == "full narrative v0.7"][0]
    core = [r for r in minimal if r["set_name"] == "core finite uniqueness"][0]
    require(full["total_survivors"] == "1", "full narrative should select one survivor")
    require(core["total_survivors"] == "1", "core finite uniqueness should select one survivor")

    cj = rows("l2_pure_CJ_survivors.csv")
    require(len(cj) == 2, "expected PAB and row-complement rows")
    verdict = {r["rule"]: r["selected_by_pure_CJ"] for r in cj}
    require(verdict.get("PAB") == "True", "PAB should be selected by pure C/J")
    require(verdict.get("row-complement") == "False", "row-complement should fail pure C/J")
    os.write(1, b"PASS verify_l2_selection\n")

if __name__ == "__main__":
    main()
    os._exit(0)
