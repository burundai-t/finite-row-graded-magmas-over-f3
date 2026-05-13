# Package note

This repository is a self-contained support package for the current PAB
preprint. It is organized to keep the mathematical manuscript, finite reference
layers, hidden-continuation support, verification logs, and integrity manifest
separate.

## Canonical source

The canonical mathematical source is:

```text
paper/main.tex
```

The compiled PDF is:

```text
paper/main.pdf
```

For theorem wording, definitions, and proof statements, use `paper/main.tex`.
The file `SUPPORT_INDEX.txt` is the navigation map from manuscript claims to
support layers and verifier commands.

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

## Repository roles

The repository separates three roles.

1. `paper/` contains the current manuscript source and compiled PDF.
2. `L1/`, `L2/`, and `L3/` are frozen reference layers for finite checks.
3. `mathcal_H/` is the global hidden-continuation bundle.

The layer notes inside `L1/`, `L2/`, and `L3/` are provenance/reference notes.
If wording in a layer note differs from the current manuscript, use
`paper/main.tex`, `SUPPORT_INDEX.txt`, and `README.md` as authoritative for the
current repository.

### Full recomputation

Full recomputation commands are listed in `README.md` and `SUPPORT_INDEX.txt`.
They recompute complete H1/H2/H4 production targets and may take substantially
longer than the default audit scripts. They write outputs under `runs/`.

### Spot recomputation

Spot recomputation commands are also listed in `README.md` and
`SUPPORT_INDEX.txt`. They recompute bounded arbitrary segments and are intended
as reviewer-facing smoke checks. They are not replacements for the accepted full
artifacts.

## Artifact policy

Accepted finite support artifacts remain inside their layer directories:

```text
L1/
L2/
L3/
mathcal_H/
```

Within `L3/`, the five-dimensional row-fiber algebra support consists of `L3/scripts/verify_l3_fiber_algebra_5dim.py` and the two `L3/tables/l3_fiber_algebra_5dim_*` tables.

New recomputation outputs should be written under `runs/` and are not included
in the release by default unless intentionally promoted.

## Reviewer entry points

For claim-by-claim navigation, open:

```text
SUPPORT_INDEX.txt
```
