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
    cj = rows("l3_CJ_finite_relations.csv")
    rel = {r["claim"]: r["result"] for r in cj}
    require(rel.get("C^3=1 on M^x") == "True", "C^3 relation missing")
    require(rel.get("J^2=1 on M^x") == "True", "J^2 relation missing")
    require(rel.get("J C J = C^{-1}") == "True", "dihedral relation missing")
    require(rel.get("PAB AbsTrans={C,J}") == "True", "PAB pure C/J relation missing")
    require(rel.get("row-complement AbsTrans={C^{-1},C^{-1}J}") == "True", "row-complement drift relation missing")

    h = rows("l3_H_bridge_pab_comp.csv")
    require(len(h) == 2, "H bridge comparison should have two rows")
    by_point = {r["point"]: r for r in h}
    require(set(by_point) == {"PAB", "row_complement"}, "H bridge points mismatch")
    require(by_point["PAB"]["H_tot"] == "7020", "PAB H_tot mismatch")
    require(by_point["row_complement"]["H_tot"] == "7020", "row-complement H_tot mismatch")
    require(by_point["PAB"]["H_minus"] == "0" and by_point["row_complement"]["H_minus"] == "0", "pure H_minus mismatch")

    mat = {r["claim"]: r["value"] for r in rows("l3_mat3_bridge_table.csv")}
    require(mat.get("cross-row AJB^T formula on basis") == "True", "matrix bridge formula check missing")
    require(mat.get("PAB/matrix-product basis coincidences") == "9", "matrix bridge coincidence count mismatch")

    br = rows("l3_companion_symplectic_summary.csv")
    comp = [r for r in br if r["block"] == "companion_lie"]
    symp = [r for r in br if r["block"] == "signed_symplectic"]
    require(any(r["result"] == "SU(3) x SU(2) x U(1)" for r in comp), "compact Lie package type missing")
    result = {(r["item"], r["claim"]): r["result"] for r in symp}
    require(result.get(("C_hat", "A^T Omega A")) == "symplectic", "C_hat symplectic check missing")
    require(result.get(("J_unsigned", "A^T Omega A")) == "anti-symplectic", "J_unsigned anti-symplectic check missing")
    require(result.get(("J_signed", "A^T Omega A")) == "symplectic", "J_signed symplectic check missing")
    require(result.get(("C_hat^3", "equals I")) == "True", "C_hat^3 relation missing")
    require(result.get(("J_signed^2", "equals -I")) == "True", "J_signed^2 projective relation missing")

    lift = rows("l3_signed_lift_matrices.csv")
    names = {r["matrix"] for r in lift}
    require(names == {"Omega", "C_hat", "J_unsigned", "J_signed"}, "signed lift matrix set mismatch")
    require(all(len([r for r in lift if r["matrix"] == name]) == 6 for name in names), "signed lift matrix sparsity mismatch")

    tick = rows("l3_tick_map_audit.csv")
    require(len(tick) == 3, "tick map audit should have three rows")
    require(all(r["sequence"] == "C,J,C,C,J" for r in tick), "tick map sequence mismatch")
    require(any(r["check"] == "finite path visits all six directed edges" and r["result"] == "True" for r in tick), "tick path coverage missing")

    os.write(1, b"PASS verify_l3_bridges\n")


if __name__ == "__main__":
    main()
    os._exit(0)
