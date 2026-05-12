#!/usr/bin/env bash
# Quick finite-layer verification for the frozen L1/L2/L3 reference package.
# This audits finite layer tables and structural checks. It does not run mathcal_H.
set -euo pipefail

if [[ -n "${PAB_REPO_ROOT:-}" ]]; then
  REPO_ROOT="${PAB_REPO_ROOT}"
else
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi
cd "${REPO_ROOT}"

export PYTHONDONTWRITEBYTECODE=1

run_check() {
  local label="$1"
  shift
  printf '== %s ==\n' "$label"
  "$@"
  printf '\n'
}

run_check "L1 finite landscape / associativity reference" python3 -S L1/scripts/verify_layer1_v3_final.py
run_check "L2 finite selection reference" python3 -S L2/scripts/verify_layer2_selection_final.py

# Use ordinary python3 for L3 Front A, which may use installed site packages.
# The remaining L3 checks are dependency-free and run with -S.
run_check "L3 Front A" python3 L3/scripts/verify_layer3_frontA.py
run_check "L3 Front B" python3 -S L3/scripts/verify_layer3_frontB.py
run_check "L3 Front C" python3 -S L3/scripts/verify_layer3_frontC.py
run_check "L3 Front D" python3 -S L3/scripts/verify_layer3_frontD.py
run_check "L3 Front E" python3 -S L3/scripts/verify_layer3_frontE.py
run_check "L3 Front F" python3 -S L3/scripts/verify_layer3_frontF.py
run_check "L3 Front G" python3 -S L3/scripts/verify_layer3_frontG.py
run_check "L3 Front H" python3 -S L3/scripts/verify_layer3_frontH.py
run_check "L3 Fiber algebra 5D" python3 -S L3/scripts/verify_l3_fiber_algebra_5dim.py

printf '== quick finite-layer checks passed ==\n'
