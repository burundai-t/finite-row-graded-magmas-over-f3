#!/usr/bin/env bash
set -euo pipefail

# Reviewer-facing mathcal_H audit wrapper.
#
# Default mode is intentionally fast: it runs the H1, H3, and H4 artifact
# audits, plus the static H2 coverage/consistency audit.  It does not run the
# heavier H2 full artifact audit unless explicitly requested.
#
# Usage:
#   tools/run_mathcal_H_audit.sh
#   tools/run_mathcal_H_audit.sh --include-h2-full
#
# The shorter alias --full-h2 is also accepted.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
MATHCAL_H_DIR="${ROOT_DIR}/mathcal_H"

INCLUDE_H2_FULL=0
for arg in "$@"; do
  case "$arg" in
    --full-h2|--include-h2-full)
      INCLUDE_H2_FULL=1
      ;;
    -h|--help)
      cat <<'HELP'
Usage:
  tools/run_mathcal_H_audit.sh
  tools/run_mathcal_H_audit.sh --include-h2-full

Default mode:
  - H1 artifact audit
  - H3 PAB/row-complement witness audit
  - H4 signed-cancellation artifact audit
  - H2 light coverage/consistency audit

The default mode does not run the heavier H2 full artifact audit.
Use --include-h2-full to add that focused H2 audit. The alias --full-h2 is also accepted.
HELP
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 2
      ;;
  esac
done

cd "$MATHCAL_H_DIR"

echo "== mathcal_H: H1 artifact audit =="
PYTHONDONTWRITEBYTECODE=1 python3 verify_mathcal_H_bundle.py --only-h1

if [[ "$INCLUDE_H2_FULL" -eq 1 ]]; then
  echo "== mathcal_H: H2 full artifact audit =="
  PYTHONDONTWRITEBYTECODE=1 python3 verify_mathcal_H_bundle.py --only-certpack-final
else
  echo "== mathcal_H: H2 full artifact audit skipped by default =="
  echo "   To include it, run: tools/run_mathcal_H_audit.sh --include-h2-full"
fi

echo "== mathcal_H: H3 PAB/row-complement witness audit =="
PYTHONDONTWRITEBYTECODE=1 python3 verify_mathcal_H_bundle.py --only-h3

echo "== mathcal_H: H4 signed-cancellation artifact audit =="
PYTHONDONTWRITEBYTECODE=1 python3 verify_mathcal_H_bundle.py --only-h4

echo "== mathcal_H: H2 light coverage/consistency audit =="
cd "$MATHCAL_H_DIR/h2"
PYTHONDONTWRITEBYTECODE=1 python3 verify_h2_coverage_light.py

echo "== mathcal_H audit: PASS =="
