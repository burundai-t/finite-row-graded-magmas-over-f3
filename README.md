# Finite Row-Graded Magmas over F3: Intrinsic Selection and Linearization

This repository contains the current manuscript and the finite support package
for the preprint.

The repository separates three roles:

1. `paper/` contains the canonical manuscript source and compiled PDF.
2. `L1/`, `L2/`, and `L3/` are frozen reference layers for finite landscape,
   selection, and selected-PAB structural checks.
3. `mathcal_H/` is the separate global hidden-continuation bundle.

The current theorem statement is in `paper/main.tex`. The layer directories are
frozen provenance/reference packages. If wording in a layer note differs from
the current manuscript, use `paper/main.tex` and `SUPPORT_INDEX.txt` as
authoritative.

## Repository layout

```text
pab_preprint_support/
  README.md
  SUPPORT_INDEX.txt
  PACKAGE_NOTE.md
  LICENSE
  .gitignore

  paper/
    main.tex
    main.pdf
    LICENSE.md

  L1/
    scripts/
    tables/
    ...

  L2/
    scripts/
    tables/
    ...

  L3/
    scripts/
    tables/
    linearization_steps/
    ...

  mathcal_H/
    README.md
    verify_mathcal_H_bundle.py
    h1/
    h2/
    h4/

```

## Canonical manuscript

The canonical source is:

```text
paper/main.tex
```

The compiled manuscript is:

```text
paper/main.pdf
```

To rebuild the PDF from the repository root:

```bash
cd paper
lualatex -interaction=nonstopmode -halt-on-error main.tex
lualatex -interaction=nonstopmode -halt-on-error main.tex
lualatex -interaction=nonstopmode -halt-on-error main.tex
cd ..
```

If `latexmk` is available, this is also acceptable:

```bash
cd paper
latexmk -lualatex -interaction=nonstopmode -halt-on-error main.tex
cd ..
```

## Quick finite-layer verification

Equivalent component commands:

```bash
python3 -S L1/scripts/verify_layer1_v3_final.py
python3 -S L2/scripts/verify_layer2_selection_final.py

python3 L3/scripts/verify_layer3_frontA.py
python3 -S L3/scripts/verify_layer3_frontB.py
python3 -S L3/scripts/verify_layer3_frontC.py
python3 -S L3/scripts/verify_layer3_frontD.py
python3 -S L3/scripts/verify_layer3_frontE.py
python3 -S L3/scripts/verify_layer3_frontF.py
python3 -S L3/scripts/verify_layer3_frontG.py
python3 -S L3/scripts/verify_layer3_frontH.py
python3 -S L3/scripts/verify_l3_fiber_algebra_5dim.py
```

These commands audit the frozen `L1/L2/L3` reference layers. They are not a
full recomputation of the global hidden-continuation theorem. Use plain `python3` for L3 Front A.  The remaining L3 checks are dependency-free and are run with `python3 -S`.

The L3 fiber-algebra verifier checks the five-dimensional row-fiber algebra used in Proposition 15.3.

The L3 Front C verifier checks the closed intertwiner formula for constant
endomorphisms:

```text
Hom_{e_r} = { u eps^T : u in span(e_(r,r), sum_{c != r} e_(r,c)) }.
```

## `mathcal_H` hidden-continuation bundle

The global hidden-continuation theorem is supported by `mathcal_H/`.

Focused `mathcal_H` audits can also be run from inside `mathcal_H/`:

```bash
cd mathcal_H
PYTHONDONTWRITEBYTECODE=1 python3 verify_mathcal_H_bundle.py --only-h1
PYTHONDONTWRITEBYTECODE=1 python3 verify_mathcal_H_bundle.py --only-h2
PYTHONDONTWRITEBYTECODE=1 python3 verify_mathcal_H_bundle.py --only-h3
PYTHONDONTWRITEBYTECODE=1 python3 verify_mathcal_H_bundle.py --only-h4
cd ..
```

Accepted `mathcal_H` results:

```text
H1 unrestricted range:
  rawH in [-378, 1217]
  H_tot in [-2268, 7302]
  endpoint counts min=8, max=12

H2 pure-frontier exclusion:
  depth-9 live frontier = 18540 nodes
  certified UNSAT = 18540
  SAT = 0, UNKNOWN = 0
  pure maximum H_tot = 7020

H3 PAB/row-complement witness check:
  rawH = 1170, H_tot = 7020, N_- = 0

H4 signed-cancellation classification:
  exactly 12 points above the pure frontier
  all have rawH = 1217, H_tot = 7302, N_- = 3
```

## Full recomputation and spot recomputation

The `mathcal_H/h1`, `mathcal_H/h2`, and `mathcal_H/h4` directories contain
accepted raw artifact directories. Treat these as read-only certificate
material. New runs should write to a separate `--run-dir`, typically under
`mathcal_H/runs/`.

Full recomputation commands may be hours long. Spot recomputation commands are
reviewer-facing sanity checks over an arbitrary segment; they are not a
replacement for the accepted full artifacts.

### H1 full recomputation

```bash
cd mathcal_H
PYTHONDONTWRITEBYTECODE=1 python3 h1/run_h1_evaluator.py \
  --start-index 0 \
  --end-index 0 \
  --run-dir runs/h1_full \
  --force \
  --self-test
cd ..
```

### H1 spot recomputation

```bash
cd mathcal_H
PYTHONDONTWRITEBYTECODE=1 python3 h1/run_h1_evaluator.py \
  --start-index 123456 \
  --end-index 124456 \
  --run-dir runs/h1_segment_123456_124456 \
  --force \
  --self-test
cd ..
```

### H2 full pure-frontier recomputation

```bash
cd mathcal_H
PYTHONDONTWRITEBYTECODE=1 python3 h2/run_h2_frontier.py \
  --depth 9 \
  --start-offset 0 \
  --end-offset 0 \
  --run-dir runs/h2_full \
  --force
cd ..
```

### H2 spot recomputation

```bash
cd mathcal_H
PYTHONDONTWRITEBYTECODE=1 python3 h2/run_h2_frontier.py \
  --depth 9 \
  --start-offset 1000 \
  --end-offset 1100 \
  --run-dir runs/h2_segment_1000_1100 \
  --force
cd ..
```

### H4 full recomputation

```bash
cd mathcal_H
PYTHONDONTWRITEBYTECODE=1 python3 h4/run_h4_classifier.py \
  --start-index 0 \
  --end-index 0 \
  --run-dir runs/h4_full \
  --force \
  --self-test
cd ..
```

### H4 spot recomputation

```bash
cd mathcal_H
PYTHONDONTWRITEBYTECODE=1 python3 h4/run_h4_classifier.py \
  --start-index 123456 \
  --end-index 124456 \
  --run-dir runs/h4_segment_123456_124456 \
  --force \
  --self-test
cd ..
```

For shorter smoke runs, the H1/H2/H4 runner scripts also expose
`--max-points`, `--max-nodes`, and `--time-limit-hours` options. Inspect each
runner with `--help` before changing production parameters.

## License

This repository uses a split license.

```text
paper/                     CC BY 4.0
all other repository files  MIT
```

The manuscript files in `paper/`, including `paper/main.tex` and
`paper/main.pdf`, are licensed under CC BY 4.0; see `paper/LICENSE.md`.

All other repository files, including verifier scripts, repository tools,
finite tables, certificate artifacts, support documentation, and verification
logs, are licensed under the MIT License; see `LICENSE`.

## Reproducibility notes

Recommended environment:

```text
Python 3.10+
A C++ compiler for the H1/H4 recomputation cores, such as clang++ or g++
Z3 Python bindings for H2 recomputation
LuaLaTeX or latexmk for rebuilding the manuscript PDF
```

## Logs

`VERIFY_LOGS/` stores package-build and audit logs. The logs are optional
support evidence; the executable commands above are the primary reproducibility
interface.
