# Layer 1 v3+H documentation pack

This folder contains the integrated Layer 1 v3+H package. It keeps the original Layer 1 v3 Assoc / `Z(q)` theorem package and adds the Layer 1H (mathcal_H) hidden continuation contrast module as a controlled theorem package.

Core deliverable:
- `layer1_landscape_v3.md` — self-contained integrated Layer 1 text with §11 “Hidden continuation contrast \(\mathcal H\)”.

## Integrated theorem content

### Assoc / Z(q)

- Normal form: `Omega' ~= S^18 x S^3`.
- Global Assoc theorem: `63 <= Assoc <= 597`, equivalently `21 <= rawAssoc <= 199`.
- Full exact distribution `Z(q)` is included in `tables/layer1_v3_Zq_full_assoc_distribution.csv`.
- Compact finite proof-obligation layer is checked by `scripts/global_assoc_tail_reduction_verify.py`.

### Layer 1H: hidden continuation contrast

- Operator-lifted four-point observable `H = I - B`.
- Normalized master formula: `H_tot(A,B,d) = 6 rawH(A,B,d)` with `3^7 = 2187` normalized terms.
- Controlled exact atlases are bundled for `column-blind x Delta`, `affine x Delta`, and `degree <= 2 x Delta`.
- Controlled pure frontier: `max{H_tot : N_- = 0} = 7020` on the three controlled strata.
- The raw controlled maximum is `H_tot = 7302`, with a small signed-cancellation tail `H_- = 6`, `N_- = 3`.

## Core tables

Assoc / Z(q):
- `tables/layer1_v3_Zq_full_assoc_distribution.csv`
- `tables/layer1_v3_Zq_full_assoc_distribution_with_probability.csv`
- `tables/layer1_v3_fixed_diagonal_summary.csv`
- `tables/layer1_v3_extremal_loci_solutions.csv`
- `tables/layer1_v3_extremal_loci_orbits.csv`
- `tables/layer1_v3_column_blind_d000_table.csv`
- `tables/layer1_v3_extremal_hacc_feature_summary.csv`
- `tables/layer1_v3_selection_bridge_claims.csv`
- `tables/layer1_v3_structure_bridge_summary.csv`
- `tables/layer1_v3_term_signature_summary.csv`
- `tables/layer1_v3_proof_targets.csv`
- `tables/layer1_v3_radius_shell_summary.csv`
- `tables/layer1_v3_status_registry_zq.csv`

Layer 1H (mathcal_H):
- `layer1H/tables/H_controlled_summary.csv`
- `layer1H/tables/H_degree2_exact_summary.csv`
- `layer1H/tables/H_frontier_locus_class_summary.csv`
- `layer1H/tables/H_frontier_term_signature_summary.csv`
- `layer1H/tables/H_local_shell_summary.csv`
- `layer1H/tables/H_status_registry.csv`

## Core scripts

Assoc / Z(q):
- `scripts/verify_layer1_v3_final.py`
- `scripts/full_zq_verify.py`
- `scripts/extremal_loci_verify.py`
- `scripts/extremal_diagonal_probe_verify.py`
- `scripts/proof_skeleton_check.py`
- `scripts/global_assoc_tail_reduction_verify.py`
- `scripts/selection_bridge_verify.py`
- `scripts/independent_witness_check.py`
- `scripts/f3_witness_verifier.py`

Layer 1H (mathcal_H):
- `layer1H/scripts/h_degree2_aggregate_chunks.py`
- `layer1H/scripts/h_master_formula_verify.py`
- `layer1H/scripts/h_frontier_signatures.py`
- `layer1H/scripts/h_local_shells.py`
- `layer1H/scripts/verify_layer1H_final.py`

Integrated smoke verifier:
- `scripts/verify_layer1_v3H_final.py`

## Recommended smoke-test commands

From this directory:

```bash
python3 scripts/verify_layer1_v3H_final.py
```

Optional full Assoc tail-reduction check:

```bash
python3 scripts/verify_layer1_v3H_final.py --with-tail
```

For separate checks:

```bash
python3 scripts/verify_layer1_v3_final.py
python3 scripts/full_zq_verify.py
python3 scripts/extremal_loci_verify.py
python3 scripts/extremal_diagonal_probe_verify.py
python3 scripts/proof_skeleton_check.py
python3 scripts/selection_bridge_verify.py
python3 scripts/independent_witness_check.py
python3 scripts/f3_witness_verifier.py
python3 scripts/global_assoc_tail_reduction_verify.py --root .

python3 scripts/verify_layer1_v3H_final.py --regenerate-h

# or direct H final check only:
(cd layer1H && python3 scripts/verify_layer1H_final.py)
```

## Inclusion policy

The package keeps the compact Layer 1 v3 files plus the certified Layer 1H module. Exploratory reports and obsolete intermediate stage files are intentionally excluded from the core artifact map.
