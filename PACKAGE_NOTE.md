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

The repository separates five roles.

1. `paper/` contains the current manuscript source and compiled PDF.
2. `L1/`, `L2/`, and `L3/` are frozen reference layers for finite checks.
3. `mathcal_H/` is the global hidden-continuation bundle.
4. `VERIFY_LOGS/` contains optional logs from verification runs.
5. `MANIFEST.sha256` records release-file integrity hashes.

The layer notes inside `L1/`, `L2/`, and `L3/` are provenance/reference notes.
If wording in a layer note differs from the current manuscript, use
`paper/main.tex`, `SUPPORT_INDEX.txt`, and `README.md` as authoritative for the
current repository.

## Verification modes

The package deliberately separates four verification modes.

### Quick finite-layer checks

```bash
tools/run_quick_checks.sh
```

This audits the frozen `L1/L2/L3` reference layers, including the L3 five-dimensional row-fiber algebra check. It does not run the global hidden-continuation bundle.

### mathcal_H artifact audit

```bash
tools/run_mathcal_H_audit.sh
```

This runs the default reviewer-facing `mathcal_H` audit route. It checks H1,
H3, H4, and the light H2 coverage/consistency audit.

The default light H2 check audits accepted artifact coverage and consistency. It
is not an SMT rerun.

For the heavier focused H2 artifact audit, use:

```bash
tools/run_mathcal_H_audit.sh --include-h2-full
```

### Full recomputation

Full recomputation commands are listed in `README.md` and `SUPPORT_INDEX.txt`.
They recompute complete H1/H2/H4 production targets and may take substantially
longer than the default audit scripts. They write outputs under `runs/`.

### Spot recomputation

Spot recomputation commands are also listed in `README.md` and
`SUPPORT_INDEX.txt`. They recompute bounded arbitrary segments and are intended
as reviewer-facing smoke checks. They are not replacements for the accepted full
artifacts.

## Integrity manifest

The repository manifest is:

```text
MANIFEST.sha256
```

Regenerate and check it with:

```bash
tools/make_manifest.sh
sha256sum -c MANIFEST.sha256
```

The manifest excludes `.git/`, `MANIFEST.sha256` itself, Python cache files,
`.DS_Store`, and local recomputation outputs under `runs/` or
`mathcal_H/runs/`.

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

`VERIFY_LOGS/` may contain logs from the commands used to prepare or audit this
repository. These logs are useful for traceability, but the primary entry points
remain the commands in `README.md` and `SUPPORT_INDEX.txt`.

## Reviewer entry points

Recommended order for a first audit:

```bash
# 1. finite layer audit
tools/run_quick_checks.sh | tee VERIFY_LOGS/quick_checks.log

# 2. hidden-continuation artifact audit
tools/run_mathcal_H_audit.sh | tee VERIFY_LOGS/mathcal_H_audit.log

# 3. optional heavier H2 artifact audit
tools/run_mathcal_H_audit.sh --include-h2-full | tee VERIFY_LOGS/mathcal_H_audit_with_h2_full.log

# 4. manifest check
tools/make_manifest.sh
sha256sum -c MANIFEST.sha256
```

For claim-by-claim navigation, open:

```text
SUPPORT_INDEX.txt
```
