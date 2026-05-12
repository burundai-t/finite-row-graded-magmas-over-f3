#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], cwd: Path | None = None) -> None:
    where = cwd if cwd is not None else ROOT
    print(f"$ {' '.join(cmd)}  (cwd={where})")
    subprocess.run(cmd, cwd=where, check=True)


def require(path: str) -> None:
    p = ROOT / path
    if not p.exists():
        raise FileNotFoundError(f"missing required artifact: {path}")


def check_integrated_text() -> None:
    text = (ROOT / "layer1_landscape_v3.md").read_text(encoding="utf-8")
    markers = [
        "## 10. Full distribution $Z(q)$",
        "## 11. Hidden continuation contrast \\(\\mathcal H\\)",
        "## 12. Selection bridge",
        "## 16. Minimal artifact map",
        "H_{tot}(A,B,d)=6\\,rawH(A,B,d)",
        "\\max\\{H_{tot}:N_-=0\\}=7020",
    ]
    for marker in markers:
        if marker not in text:
            raise AssertionError(f"missing marker in integrated text: {marker}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Layer 1 v3+H integrated smoke verifier")
    parser.add_argument("--with-tail", action="store_true", help="also run the optional Global Assoc tail-reduction verifier")
    parser.add_argument("--regenerate-h", action="store_true", help="rerun H table-regeneration helpers before the H verifier")
    args = parser.parse_args()

    required = [
        "layer1_landscape_v3.md",
        "README_L1.md",
        "tables/layer1_v3_Zq_full_assoc_distribution.csv",
        "tables/layer1_v3_fixed_diagonal_summary.csv",
        "scripts/verify_layer1_v3_final.py",
        "scripts/global_assoc_tail_reduction_verify.py",
        "layer1H/Layer1H.md",
        "layer1H/Layer1H_controlled_frontier_theorem.md",
        "layer1H/tables/H_controlled_summary.csv",
        "layer1H/tables/H_degree2_exact_summary.csv",
        "layer1H/scripts/verify_layer1H_final.py",
    ]
    for path in required:
        require(path)
    check_integrated_text()

    # Core Layer 1 smoke checks.
    run([sys.executable, "scripts/verify_layer1_v3_final.py"])
    run([sys.executable, "scripts/full_zq_verify.py"])
    run([sys.executable, "scripts/extremal_loci_verify.py"])
    run([sys.executable, "scripts/extremal_diagonal_probe_verify.py"])
    run([sys.executable, "scripts/proof_skeleton_check.py"])
    run([sys.executable, "scripts/selection_bridge_verify.py"])
    run([sys.executable, "scripts/independent_witness_check.py"])
    run([sys.executable, "scripts/f3_witness_verifier.py"])

    if args.with_tail:
        run([sys.executable, "scripts/global_assoc_tail_reduction_verify.py", "--root", "."])

    # Layer 1H checks. Regenerators are optional; the final verifier checks stored tables.
    hroot = ROOT / "layer1H"
    if args.regenerate_h:
        run([sys.executable, "scripts/h_degree2_aggregate_chunks.py"], cwd=hroot)
        run([sys.executable, "scripts/h_master_formula_verify.py"], cwd=hroot)
        run([sys.executable, "scripts/h_frontier_signatures.py"], cwd=hroot)
        run([sys.executable, "scripts/h_local_shells.py"], cwd=hroot)
    else:
        run([sys.executable, "scripts/h_master_formula_verify.py"], cwd=hroot)
    run([sys.executable, "scripts/verify_layer1H_final.py"], cwd=hroot)

    print("Layer 1 v3+H integrated verifier: PASS")


if __name__ == "__main__":
    main()
