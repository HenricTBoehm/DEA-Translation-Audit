#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
sha256sum -c SHA256SUMS
for name in adr001 v035; do
  PYTHONPATH=../ADR-001 python3 "poblete_${name}_check.py" --out "$scratch/poblete-${name}-results.json"
  cmp "$scratch/poblete-${name}-results.json" "poblete-${name}-results.json"
done
PYTHONPATH=.:../ADR-001 python3 typed-v1.0.1/check.py --out "$scratch/typed.json"
cmp "$scratch/typed.json" typed-v1.0.1/results.json
printf '%s\n' 'PASS: Poblete archives and typed regression'
