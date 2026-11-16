#!/usr/bin/env bash
set -euo pipefail
distribution=$(realpath "${1:?usage: bash verify.sh /absolute/distribution-root}")
cd "$(dirname "$0")"
sha256sum -c SHA256SUMS
(cd ../../Dynamic-Dependency-Evidence/phase-b-v0.1 && sha256sum -c SHA256SUMS)
temp=$(mktemp -d)
trap 'rm -rf "$temp"' EXIT
for seed in 0 42; do
    PYTHONHASHSEED="$seed" python3 -B run.py --distribution "$distribution" --out "$temp/$seed"
    cmp "$temp/$seed/RESULTS.json" RESULTS.json
done
