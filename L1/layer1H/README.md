# Layer 1H certified atlas — v0.5 / level 2.5 final

This package implements the hidden continuation contrast \(\mathcal H\) as a certified Layer 1H controlled theorem module.

Core verified content:

- normalized master formula \(H_{tot}=6rawH\) with \(3^7=2187\) terms;
- PAB \(H_{tot}=7020\);
- exact `column-blind × Δ` range `[1836,7302]`;
- exact `affine × Δ` range `[-2268,7302]`;
- exact total-degree `≤2` polynomial `× Δ` range `[-2268,7302]` over `14,348,907` points;
- controlled purity frontier `max{H_tot:N_-=0}=7020` on all three exact strata;
- frontier signed-class atlas;
- frontier term signatures;
- radius-1 and radius-2 local Hamming shells around seven centers;
- signed-spectrum consistency `H_tot=H_+-H_-`;
- theorem-style compression in `Layer1H_controlled_frontier_theorem.md`;
- compact appendix patch for the main Layer 1 text in `Layer1H_appendix_for_layer1_v3.md`.

Run the verification stack:

```bash
python3 -S scripts/h_master_formula_verify.py
python3 -S scripts/h_frontier_signatures.py
python3 -S scripts/h_local_shells.py
python3 -S scripts/verify_layer1H_final.py
```

Optional rebuild of the degree `≤2` exact pass from stored chunks:

```bash
python3 -S scripts/h_degree2_aggregate_chunks.py
python3 -S scripts/verify_layer1H_final.py
```

To regenerate degree `≤2` chunks from scratch:

```bash
g++ -std=c++17 -O3 -march=native -fopenmp scripts/h_degree2_targeted.cpp -o scripts/h_degree2_targeted_chunked
./scripts/h_degree2_targeted_chunked . OFFSET LIMIT
python3 -S scripts/h_degree2_aggregate_chunks.py
```

Important tables:

```text
tables/H_degree2_exact_summary.csv
tables/H_degree2_frontier_loci.csv
tables/H_degree2_frontier_orbits.csv
tables/H_frontier_locus_class_summary.csv
tables/H_frontier_term_signature_summary.csv
tables/H_frontier_local_value_histogram.csv
tables/H_center_profiles.csv
tables/H_local_shell_summary.csv
tables/H_status_registry.csv
```

Current status: level 2.5 is complete as a controlled Layer 1H atlas. Remaining work is global \(\Omega'\)-certification: global H-range, global pure frontier, and full \(Z_H\)/joint distribution.
