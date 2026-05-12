# mathcal_H hidden-continuation theorem bundle

Compact theorem/certificate bundle for the global hidden-continuation theorem,
prepared on 2026-05-03 and integrated into the PAB support repository on
2026-05-04. The implementation verifier keeps the historical filename
`verify_stage6_bundle.py`; the public wrapper is `verify_mathcal_H_bundle.py`.

The bundle supports the global hidden-continuation theorem in
`paper/main.tex` and `paper/main.pdf`.  It is intentionally kept separate from
the `L1/`, `L2/`, and `L3/` layer corpus.

When unpacked in the active project root, the layout is:

```text
mathcal_H/
  README.md
  stage6.md
  verify_mathcal_H_bundle.py
  verify_stage6_bundle.py      # implementation file
  h1/
    run_h1_evaluator.py
    h1_eval_core.cpp
    raw/
  h2/
    run_h2_frontier.py
    verify_h2_coverage_light.py
    raw/
  h4/
    run_h4_classifier.py
    h4_signed_core.cpp
    raw/
```

The `h1/raw`, `h2/raw`, and `h4/raw` directories contain accepted run logs and
audit artifacts.  Treat them as read-only certificate material.  New manual runs
should use a separate `--run-dir`.

## Quick bundle verification

Run from the bundle directory:

```bash
cd mathcal_H
PYTHONDONTWRITEBYTECODE=1 python3 verify_mathcal_H_bundle.py
```

Focused checks:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 verify_mathcal_H_bundle.py --only-h1
PYTHONDONTWRITEBYTECODE=1 python3 verify_mathcal_H_bundle.py --only-certpack-final
PYTHONDONTWRITEBYTECODE=1 python3 verify_mathcal_H_bundle.py --only-h3
PYTHONDONTWRITEBYTECODE=1 python3 verify_mathcal_H_bundle.py --only-h4
```

The `--only-certpack-final` command is the focused H2 / pure-frontier
certificate-pack audit.  For a fast static artifact-coverage check, run:

```bash
cd mathcal_H/h2
PYTHONDONTWRITEBYTECODE=1 python3 verify_h2_coverage_light.py
```

Runtime note: the full verifier performs the bundle-level mathematical checks
and can be substantially heavier than the root manuscript verifier.  For a
focused audit of accepted artifacts, use the four focused commands above.  The
H2 command `--only-certpack-final` is the heaviest focused check because it
audits the pure-frontier certificate pack.

There is no separate `h3/raw` directory.  The PAB/row-complement witness check is a
short witness sanity check embedded in `verify_mathcal_H_bundle.py` and documented
in `stage6.md`.

## H1: unrestricted range

Accepted result:

```text
points      = 3^21 = 10460353203
rawH range  = [-378, 1217]
H_tot range = [-2268, 7302]
min count   = 8
max count   = 12
```

Scripts and artifacts:

```text
h1/run_h1_evaluator.py
h1/h1_eval_core.cpp
h1/raw/checkpoint.json
h1/raw/chunks.csv
h1/raw/violations.csv
h1/raw/audit_report.json
h1/raw/audit_rerun.csv
h1/raw/events.log
```

## H2: pure frontier

Accepted result:

```text
depth-9 live frontier = 18540 nodes
certified UNSAT       = 18540
SAT                   = 0
UNKNOWN               = 0
pure maximum H_tot    = 7020
```

Scripts and artifacts:

```text
h2/run_h2_frontier.py
h2/verify_h2_coverage_light.py
h2/raw/checkpoint.json
h2/raw/segments.csv
h2/raw/nodes.csv
h2/raw/chunks.csv
h2/raw/windows.csv
h2/raw/unknown.csv
h2/raw/sat.csv
h2/raw/audit_report.json
h2/raw/audit_rerun.csv
h2/raw/events.log
```

## H3: PAB/row-complement witness check

Accepted result:

```text
PAB            rawH = 1170, H_tot = 7020, N_- = 0
row-complement rawH = 1170, H_tot = 7020, N_- = 0
```

This check is embedded in `verify_mathcal_H_bundle.py` and has no separate raw
artifact directory.

## H4: signed-cancellation classification

Accepted result:

```text
points above pure frontier = 12
all have rawH              = 1217
all have H_tot             = 7302
all have N_-               = 3
pure high points           = 0
```

Scripts and artifacts:

```text
h4/run_h4_classifier.py
h4/h4_signed_core.cpp
h4/raw/checkpoint.json
h4/raw/chunks.csv
h4/raw/chunk_pairs.csv
h4/raw/pair_counts.csv
h4/raw/rawH_summary.csv
h4/raw/witnesses.csv
h4/raw/summary.json
h4/raw/audit_report.json
h4/raw/audit_rerun.csv
h4/raw/events.log
```

## Integration note

The mathcal_H bundle is not a replacement for the `L1/`, `L2/`, and `L3/`
layer corpus.  The layer verifiers check the finite landscape, selection, and
selected-magma structural layers; this bundle audits the external global
hidden-continuation theorem package.
