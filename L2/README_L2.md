# README_L2 — Layer 2 selection package, v0.7 Front H

This folder contains the stabilized working package for **Layer 2: selection of PAB from the Layer 1 v3+H landscape**.

Layer 1 supplies the finite landscape theorem package:

\[
\Omega'\cong \mathcal G\times\Delta\cong S^{18}\times S^3,
\qquad |\Omega'|=3^{21}.
\]

Layer 2 proves a finite selection theorem: PAB is the unique survivor after applying information compression, nondegenerate anchoring, local path-dependence, and finite directed-edge dynamics. Hidden continuation contrast \(\mathcal H\) is included as an auxiliary bridge, not as a required selector.

## Current status

Version `v0.7` closes all planned fronts A--H:

- **Front A:** package skeleton, tables, verifier pipeline;
- **Front B:** information criteria \(\mathcal H_{acc}=0\) and \(H_{diag}=0\);
- **Front C:** nondegenerate anchors;
- **Front D:** local path-dependence theorem via `Assoc_000`;
- **Front E:** finite pure `C/J` directed-edge selector;
- **Front F:** independence/minimality registry and deletion audit;
- **Front G:** hidden continuation contrast \(\mathcal H\) as an auxiliary bridge;
- **Front H:** artifact manifest, table integrity audit, and consistency audit.

The finite selection chain is:

\[
\Omega'
\xrightarrow{\mathcal H_{acc}=0,\ H_{diag}=0}
9\times3
\xrightarrow{\mathrm{nontrivial},\ \mathrm{diag\ idempotence}}
6\times1
\xrightarrow{\min\operatorname{Assoc}_{000}}
2\times1
\xrightarrow{\mathrm{pure}\ C/J\ \mathrm{drift/kick}}
1.
\]

Final survivor:

\[
(g_1,000)=\mathrm{PAB}.
\]

## Main guardrails

1. `Assoc` is not a global PAB selector. It is used only locally, inside the information-compressed and nondegenerate column-blind domain.
2. Weak `q/p` splitting is rejected: both PAB and row-complement pass weak sector tests.
3. The finite dynamic selector is the stronger pure `C/J` criterion: PAB has `{C,J}`, while row-complement has `{C^{-1},C^{-1}J}`.
4. The old continuous `C^2` symplectic realization is retained as an open geometric bridge, not as a dependency of the finite selection theorem.
5. Hidden continuation contrast \(\mathcal H\) is auxiliary only: PAB and row-complement both have the same pure profile \(H_{tot}=7020, H_-=0, N_-=0\) at `d=000`, and the global \(\Omega'\) H-certificate remains open.

## Verifier

Run from the package root:

```bash
/usr/bin/python3 scripts/verify_layer2_selection_final.py
```

Expected output includes:

```text
Layer 2 selection verifier v0.7: PASS
  Front B closed: information criteria formalized and finite cores checked
  Front C closed: nondegenerate anchors formalized and checked
  Front D closed: local path-dependence theorem checked on six nontrivial column-blind rules
  Front E finite core closed: pure C/J directed-edge selector separates PAB from row-complement
  Front F closed: independence/minimality registry and deletion audit generated
  Front G closed: hidden continuation contrast H integrated as auxiliary bridge
  Front H closed: artifact manifest, table integrity audit, and consistency audit generated
```

## Core artifacts

- `layer2_selection_v1.md` — main theorem text;
- `README_L2.md` — this artifact map;
- `scripts/verify_layer2_selection_final.py` — single smoke verifier;
- `verify_v0_7_final.log` — latest verifier log;
- `tables/` — generated tables for Fronts B--H.

## Front H hardening tables

- `tables/layer2_frontH_artifact_manifest.csv`
- `tables/layer2_frontH_table_integrity_audit.csv`
- `tables/layer2_frontH_consistency_audit.csv`
- `tables/layer2_frontH_final_package_registry.csv`
- `tables/layer2_frontH_open_bridge_registry.csv`

## Core table groups

Information and anchors:

- `tables/layer2_information_criteria.csv`
- `tables/layer2_hacc_column_blind_rules.csv`
- `tables/layer2_hacc_representative_audit.csv`
- `tables/layer2_diag_entropy_table.csv`
- `tables/layer2_diag_entropy_distribution.csv`
- `tables/layer2_nondegenerate_anchor_audit.csv`

Path-dependence:

- `tables/layer2_path_dependence_table.csv`
- `tables/layer2_assoc_block_decomposition_cb.csv`
- `tables/layer2_path_dependence_theorem.csv`
- `tables/layer2_assoc_guardrail.csv`

Finite directed-edge dynamics:

- `tables/layer2_frontE_canonical_maps.csv`
- `tables/layer2_frontE_nontrivial_cb_absorption_audit.csv`
- `tables/layer2_absorption_degree_all_cb.csv`
- `tables/layer2_absorption_transitions_pab_comp.csv`
- `tables/layer2_frontE_survivor_transition_factorization.csv`
- `tables/layer2_frontE_pure_drift_kick_theorem.csv`
- `tables/layer2_qp_splitting_audit.csv`
- `tables/layer2_weak_qp_splitting_details.csv`

Independence/minimality:

- `tables/layer2_frontF_criterion_role_registry.csv`
- `tables/layer2_frontF_deletion_audit.csv`
- `tables/layer2_frontF_criterion_removal_audit.csv`
- `tables/layer2_frontF_minimal_selector_sets.csv`
- `tables/layer2_frontF_minimal_core_registry.csv`
- `tables/layer2_frontF_dependency_matrix.csv`
- `tables/layer2_frontF_no_Hdiag_idempotent_assoc_audit.csv`
- `tables/layer2_criterion_independence.csv`
- `tables/layer2_minimality_deletion_audit.csv`

Hidden continuation contrast bridge:

- `tables/layer2_frontG_H_column_blind_audit.csv`
- `tables/layer2_frontG_H_controlled_summary.csv`
- `tables/layer2_frontG_H_controlled_summary_imported.csv`
- `tables/layer2_frontG_H_key_witnesses.csv`
- `tables/layer2_frontG_H_pure_frontier_locus_cb.csv`
- `tables/layer2_frontG_H_selector_guardrails.csv`
- `tables/layer2_frontG_H_bridge_policy.csv`
- `tables/layer2_frontG_H_local_shell_summary.csv`
- `tables/layer2_frontG_H_auxiliary_bridge.csv`
- `tables/layer2_frontG_H_status_registry.csv`

Global selection/status:

- `tables/layer2_selection_chain.csv`
- `tables/layer2_status_registry.csv`

## Remaining open bridges

The finite Layer 2 selector is closed. Remaining items are bridges or exposition upgrades:

- continuous `C^2` symplectic realization theorem from the finite pure `C/J` criterion;
- global \(\Omega'\) certification of hidden continuation contrast \(\mathcal H\);
- optional hand-compression of finite verifier checks for a publication-style proof.
