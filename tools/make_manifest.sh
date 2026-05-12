#!/usr/bin/env bash
set -euo pipefail

# Generate a deterministic SHA-256 manifest for the release repository.
# Excluded: .git/, MANIFEST.sha256 itself, Python caches, .DS_Store, and
# local recomputation outputs under runs/ or mathcal_H/runs/.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

rm -f MANIFEST.sha256

find . \
  -type f \
  ! -path './.git/*' \
  ! -path './MANIFEST.sha256' \
  ! -path './runs/*' \
  ! -path './mathcal_H/runs/*' \
  ! -path '*/__pycache__/*' \
  ! -name '*.pyc' \
  ! -name '.DS_Store' \
  -print0 \
  | sort -z \
  | xargs -0 sha256sum > MANIFEST.sha256
