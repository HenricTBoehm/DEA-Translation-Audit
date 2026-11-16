#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if (( $# < 1 || $# > 2 )); then
    printf '%s\n' 'Usage: bash verify.sh /path/review.zip [/path/D0.zip]' >&2
    exit 2
fi
bundle=$(realpath -- "$1")
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
printf '%s  %s\n' '754268ed45cd18321657dc7e7b26ec31e6bddb14f397af01fc86691763cbe166' "$bundle" | sha256sum -c
sha256sum -c SHA256SUMS
unzip -t "$bundle"
unzip -q "$bundle" -d "$scratch"
pkg="$scratch/dea-gap-register-v0.1.1"
(cd "$pkg" && sha256sum -c SHA256SUMS)
if (( $# == 2 )); then
    d0=$(realpath -- "$2")
    printf '%s  %s\n' 'd655d4585970cb8cf2d605467b827c4b061daaab6041e554e402e944116630e9' "$d0" | sha256sum -c
    unzip -q "$d0" -d "$scratch/d0"
    (cd "$scratch/d0" && sha256sum -c SHA256SUMS)
    printf '%s  %s\n' 'b36a06a8cdf3edcb0789e2c6980f65ae9d2ce7dcac62d8f00abd7cf9c70b8617' \
        "$scratch/d0/manuscript/DEA_v0.3.5.1_working_draft_2026-11-16.tex" | sha256sum -c
fi
export PYTHONDONTWRITEBYTECODE=1
python3 "$pkg/test_oracle.py"
python3 "$pkg/oracle.py" > "$scratch/original.json"
cmp "$scratch/original.json" "$pkg/oracle-results-v0.1.1.json"
for seed in 0 42; do
    PYTHONHASHSEED=$seed python3 independent_review.py --package "$pkg" --out "$scratch/student-$seed.json"
    cmp "$scratch/student-$seed.json" RESULTS.json
done
printf '%s\n' 'PASS: exact archived fixture replay and independent adversarial review'
