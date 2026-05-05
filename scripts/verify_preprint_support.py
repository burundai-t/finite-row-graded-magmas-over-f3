#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import os
import sys

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
TABLES = ROOT / "tables"
PAPER = ROOT / "paper"
MATHCAL_H = ROOT / "mathcal_H"

# Compact manuscript-facing verifier set.
CHECKS = [
    "verify_l1_assoc_and_H.py",
    "verify_l2_selection.py",
    "verify_l3_operator_and_T2.py",
    "verify_l3_fiber_algebra_5dim.py",
    "verify_l3_bridges.py",
]

REQUIRED_ROOT_FILES = {
    ".gitignore",
    "LICENSE",
    "README.md",
}
REQUIRED_ROOT_DIRS = {
    "mathcal_H",
    "paper",
    "scripts",
    "tables",
}
REQUIRED_PAPER_FILES = {
    "main.pdf",
    "main.tex",
}

REQUIRED_TABLES = {
    "l1_assoc_distribution.csv",
    "l1_extremal_loci_counts.csv",
    "l1_extremal_loci_orbits.csv",
    "l1_extremal_loci_solutions.csv",
    "l1_assoc_proof_targets.csv",
    "l1H_controlled_summary.csv",
    "l1H_standard_six.csv",
    "l2_selection_chain.csv",
    "l2_path_dependence_table.csv",
    "l2_minimal_selector_sets.csv",
    "l2_pure_CJ_survivors.csv",
    "l3_CJ_finite_relations.csv",
    "l3_operator_spectrum_rank.csv",
    "l3_composition_envelope.csv",
    "l3_composition_product_law.csv",
    "l3_absorption_transitions.csv",
    "l3_absorption_spectrum.csv",
    "l3_intertwiner_audit.csv",
    "l3_mat3_bridge_table.csv",
    "l3_H_bridge_pab_comp.csv",
    "l3_T2_factorization_summary.csv",
    "l3_T2_factorization_index.csv",
    "l3_T2_S21_operation_table.csv",
    "l3_T2_U15_operation_table.csv",
    "l3_T2_binary_multiplication_table.csv",
    "l3_companion_symplectic_summary.csv",
    "l3_signed_lift_matrices.csv",
    "l3_tick_map_audit.csv",
    "l3_fiber_algebra_5dim_multiplication.csv",
    "l3_fiber_algebra_5dim_structure.csv",
}

REQUIRED_SCRIPTS = set(CHECKS) | {"verify_preprint_support.py"}

FORBIDDEN_DIRS = {
    "L1", "L2", "L3", "logs", "reports", "__pycache__", "__MACOSX",
    "VERIFY_LOGS",
}
FORBIDDEN_FILES = {
    "L1.zip", "L2.zip", "L3.zip",
    "HASH_MANIFEST.csv", "FILE_MANIFEST.csv", "TABLE_PROVENANCE.csv",
    "REPRODUCIBILITY_SUMMARY.json",
    "PAB_preprint_layered_v14_final.md", "PAB_preprint_updated.md",
    "README.txt", "gitignore.txt",
}
FORBIDDEN_MANUSCRIPT_TOKENS = ["[S:", "src:L", "guardrail"]
REQUIRED_MANUSCRIPT_TOKENS = [
    "finite landscape",
    "intrinsic finite selection",
    "linearization",
    "global hidden-continuation theorem",
    "Theorem 7.2",
    "Global hidden-continuation certificate handles",
    "closed by Theorem 7.2 and the",
    r"\texttt{mathcal\_H/} certificate bundle",
    "All-arity term algebra",
]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def check_inventory():
    root_files = {p.name for p in ROOT.iterdir() if p.is_file()}
    root_dirs = {p.name for p in ROOT.iterdir() if p.is_dir()}
    paper_files = {p.name for p in PAPER.iterdir() if p.is_file()}
    table_files = {p.name for p in TABLES.glob("*.csv")}
    script_files = {p.name for p in SCRIPTS.glob("*.py")}

    require(REQUIRED_ROOT_FILES <= root_files,
            f"missing root files: {sorted(REQUIRED_ROOT_FILES - root_files)}")
    require(REQUIRED_ROOT_DIRS <= root_dirs,
            f"missing root dirs: {sorted(REQUIRED_ROOT_DIRS - root_dirs)}")
    require(REQUIRED_PAPER_FILES <= paper_files,
            f"missing paper files: {sorted(REQUIRED_PAPER_FILES - paper_files)}")
    require(table_files == REQUIRED_TABLES,
            f"unexpected table inventory: missing={sorted(REQUIRED_TABLES - table_files)} extra={sorted(table_files - REQUIRED_TABLES)}")
    require(script_files == REQUIRED_SCRIPTS,
            f"unexpected script inventory: missing={sorted(REQUIRED_SCRIPTS - script_files)} extra={sorted(script_files - REQUIRED_SCRIPTS)}")
    require((MATHCAL_H / "verify_stage6_bundle.py").is_file(),
            "missing mathcal_H/verify_stage6_bundle.py")
    require((MATHCAL_H / "README.md").is_file(),
            "missing mathcal_H/README.md")
    require(not (root_dirs & FORBIDDEN_DIRS),
            f"forbidden dirs present: {sorted(root_dirs & FORBIDDEN_DIRS)}")
    require(not (root_files & FORBIDDEN_FILES),
            f"forbidden files present: {sorted(root_files & FORBIDDEN_FILES)}")

    manuscript = (PAPER / "main.tex").read_text(encoding="utf-8")
    require((PAPER / "main.pdf").stat().st_size > 0, "paper/main.pdf is empty")
    for token in FORBIDDEN_MANUSCRIPT_TOKENS:
        require(token not in manuscript, f"forbidden manuscript token present: {token}")
    for token in REQUIRED_MANUSCRIPT_TOKENS:
        require(token in manuscript, f"required manuscript token missing: {token}")


def load_and_run(script):
    path = SCRIPTS / script
    name = script[:-3]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    mod.main()


def main():
    check_inventory()
    for script in CHECKS:
        load_and_run(script)
    os.write(1, b"PASS verify_preprint_support\n")


if __name__ == "__main__":
    main()
    os._exit(0)
