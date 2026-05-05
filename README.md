# σ-Equivariant Magmas on AG(2,3)

This repository accompanies the preprint
**"σ-Equivariant Magmas on AG(2,3): finite landscape, intrinsic selection,
and linearization."**

The paper studies a finite family of sigma-equivariant magmas on
`S x S`, where `S = F_3`.  The main thread is:

```text
finite landscape -> intrinsic finite selection -> linearization of PAB
```

The repository contains the manuscript, the finite certificate tables used by
the manuscript-facing checks, and the separate `mathcal_H` bundle for the
global hidden-continuation theorem.

## Contents

```text
paper/
  main.pdf        preprint PDF
  main.tex        LaTeX source for the preprint

scripts/
  verify_preprint_support.py
  verify_l1_assoc_and_H.py
  verify_l2_selection.py
  verify_l3_operator_and_T2.py
  verify_l3_bridges.py
  verify_l3_fiber_algebra_5dim.py

tables/
  CSV certificate tables for the L1/L2/L3 manuscript checks

mathcal_H/
  certificate bundle for the global hidden-continuation theorem
```

## Quick Verification

The compact manuscript-facing verifier checks the repository inventory and then
runs the L1/L2/L3 table audits:

```bash
python3 -S scripts/verify_preprint_support.py
```

The global hidden-continuation certificate bundle is verified separately:

```bash
cd mathcal_H
PYTHONDONTWRITEBYTECODE=1 python3 verify_stage6_bundle.py
```

Focused bundle checks are also available:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 verify_stage6_bundle.py --only-h1
PYTHONDONTWRITEBYTECODE=1 python3 verify_stage6_bundle.py --only-certpack-final
PYTHONDONTWRITEBYTECODE=1 python3 verify_stage6_bundle.py --only-h3
PYTHONDONTWRITEBYTECODE=1 python3 verify_stage6_bundle.py --only-h4
```

For a fast static H2 coverage audit:

```bash
cd mathcal_H/h2
PYTHONDONTWRITEBYTECODE=1 python3 verify_h2_coverage_light.py
```

The full `mathcal_H` verifier can be noticeably heavier than the root verifier;
the focused commands above are useful when checking one certificate component at
a time.

## Expected Checkpoints

A successful root check ends with:

```text
PASS verify_preprint_support
```

The focused `mathcal_H` checks certify the following headline facts:

```text
H1 unrestricted range:
  points      = 3^21 = 10460353203
  H_tot range = [-2268, 7302]
  rawH range  = [-378, 1217]
  endpoint counts = min:8, max:12

H2 pure frontier:
  depth-9 live frontier = 18540 nodes
  certified UNSAT       = 18540
  SAT                   = 0
  UNKNOWN/unresolved    = 0
  pure maximum H_tot    = 7020

H3 PAB/row-complement witness check:
  PAB            H_tot = 7020, N_- = 0
  row-complement H_tot = 7020, N_- = 0

H4 signed-cancellation classification:
  points above pure frontier = 12
  all have H_tot             = 7302
  all have N_-               = 3
  pure high points           = 0
```

There is no separate `mathcal_H/h3/raw` directory.  H3 is a short witness check
embedded in `mathcal_H/verify_stage6_bundle.py`.

## Notes On Reproducibility

The root `tables/` directory contains the compact CSV tables cited by the
manuscript-facing verifier.  The raw H1/H2/H4 certificate artifacts remain
inside `mathcal_H/h1/raw`, `mathcal_H/h2/raw`, and `mathcal_H/h4/raw`; they are
part of the certificate bundle and should not be flattened into `tables/`.

The removed `VERIFY_LOGS` directory contained transcripts from previous local
verification runs.  It is not needed to reproduce the checks, because the
commands above regenerate their own terminal output from the committed scripts,
tables, and certificate artifacts.

## License

See `LICENSE`.
