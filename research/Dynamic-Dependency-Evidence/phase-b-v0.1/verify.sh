#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
sha256sum -c SHA256SUMS
(cd ../../Minimal-Differential-Harness/phase-a-v0.1 && sha256sum -c SHA256SUMS)
temp=$(mktemp -d)
trap 'rm -rf "$temp"' EXIT
flags=()
if [[ $# -eq 1 ]]; then
    flags=(--opa "$(realpath "$1")")
fi
for seed in 0 42; do
    PYTHONHASHSEED="$seed" python3 -B run.py "${flags[@]}" --out "$temp/$seed"
    python3 -B verify.py "$temp/$seed/RESULTS.json"
done
cmp "$temp/0/RESULTS.json" "$temp/42/RESULTS.json"
if [[ $# -eq 1 ]]; then
    cmp "$temp/0/RESULTS.json" RESULTS.json
fi
