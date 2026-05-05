#!/usr/bin/env python3
from pathlib import Path
import csv
import os

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "tables"


def rows(name):
    with open(TABLES / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fieldnames(name):
    with open(TABLES / name, newline="", encoding="utf-8") as f:
        return csv.DictReader(f).fieldnames


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    ops = rows("l3_operator_spectrum_rank.csv")
    require(len(ops) == 9, "operator table should have nine carrier rows")
    require(all(int(r["rank"]) == 3 for r in ops), "every left translation should have rank 3")
    diag = [r for r in ops if r["type"] == "diagonal"]
    off = [r for r in ops if r["type"] == "off_diagonal"]
    require(len(diag) == 3 and len(off) == 6, "diagonal/off-diagonal counts mismatch")
    require(all(r["minimal_polynomial"] == "t(t-1)(t+1)" for r in diag), "diagonal minimal polynomial mismatch")
    require(all(r["minimal_polynomial"] == "t^2(t-1)(t+1)" for r in off), "off-diagonal minimal polynomial mismatch")
    require(all(int(r["J2_blocks_at_zero"]) == 0 for r in diag), "diagonal should have no zero Jordan block")
    require(all(int(r["J2_blocks_at_zero"]) == 1 for r in off), "off-diagonal should have one zero Jordan block")

    env = rows("l3_composition_envelope.csv")
    require(len(env) == 3, "composition envelope should have three target rows")
    require(all(int(r["monoid_elements_in_Wr"]) == 17 for r in env), "Wr monoid count mismatch")
    require(all(int(r["dim_Wr"]) == 9 for r in env), "Wr dimension mismatch")
    product_law = rows("l3_composition_product_law.csv")
    require(len(product_law) == 9, "composition product law should have nine row-pair checks")
    require(all(r["product_subset_left_W"] == "True" for r in product_law), "W_r W_s subset W_r check failed")
    require(all(int(r["products_checked"]) == 289 for r in product_law), "composition product check count mismatch")

    absorption = rows("l3_absorption_spectrum.csv")
    spectrum = {int(r["eigenvalue"]): int(r["multiplicity"]) for r in absorption}
    require(spectrum == {-1: 2, 0: 3, 2: 1}, "absorption spectrum mismatch")
    transitions = rows("l3_absorption_transitions.csv")
    require(len(transitions) == 6, "absorption transition table should have six directed edges")

    inter = rows("l3_intertwiner_audit.csv")
    require(len(inter) == 9, "intertwiner audit should have nine endomorphism rows")
    const_dims = [int(r["dimension"]) for r in inter if r["type"] == "constant"]
    auto_dims = [int(r["dimension"]) for r in inter if r["type"] == "automorphism"]
    require(const_dims == [2, 2, 2], "constant intertwiner dimensions mismatch")
    require(len(auto_dims) == 6 and all(d == 1 for d in auto_dims), "automorphism intertwiner dimensions mismatch")

    summary = {r["quantity"]: r for r in rows("l3_T2_factorization_summary.csv")}
    require(summary["binary_term_functions"]["value"] == "630", "T2 size mismatch")
    require(summary["binary_term_functions"]["formula"] == "2*21*15", "T2 formula mismatch")

    idx = rows("l3_T2_factorization_index.csv")
    require(len(idx) == 630, "T2 factorization index should have 630 rows")
    require(len({r["id"] for r in idx}) == 630, "T2 ids should be unique")
    require({r["owner"] for r in idx} == {"x", "y"}, "T2 owner set mismatch")
    require(len({r["S_id"] for r in idx}) == 21, "T2 S factor size mismatch")
    require(len({r["U_id"] for r in idx}) == 15, "T2 U factor size mismatch")

    s21 = rows("l3_T2_S21_operation_table.csv")
    u15 = rows("l3_T2_U15_operation_table.csv")
    require(len(s21) == 21 and len(fieldnames("l3_T2_S21_operation_table.csv")) == 22, "S21 operation table dimensions mismatch")
    require(len(u15) == 15 and len(fieldnames("l3_T2_U15_operation_table.csv")) == 16, "U15 operation table dimensions mismatch")
    require({int(r["lhs_S_id"]) for r in s21} == set(range(21)), "S21 lhs id set mismatch")
    require({int(r["lhs_U_id"]) for r in u15} == set(range(15)), "U15 lhs id set mismatch")

    mult = rows("l3_T2_binary_multiplication_table.csv")
    mult_fields = fieldnames("l3_T2_binary_multiplication_table.csv")
    require(len(mult) == 630 and len(mult_fields) == 631, "full T2 multiplication table dimensions mismatch")
    require(mult_fields[0] == "lhs_id" and mult_fields[-1] == "rhs_629", "full T2 multiplication header mismatch")
    require({int(r["lhs_id"]) for r in mult} == set(range(630)), "full T2 lhs id set mismatch")

    os.write(1, b"PASS verify_l3_operator_and_T2\n")


if __name__ == "__main__":
    main()
    os._exit(0)
