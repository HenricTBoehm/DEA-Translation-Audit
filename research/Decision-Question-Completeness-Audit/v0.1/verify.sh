#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if (( $# > 1 )); then
    printf '%s\n' 'Usage: bash verify.sh [absolute path to original HR-1 ZIP]' >&2
    exit 2
fi
repo=$(git rev-parse --show-toplevel)
pilot=96731f6ac458dd7b0d9ec855eec0036d91f47467
p01=91e842fdae94356ff323f3afb2e99245369108da
pilot_path=research/History-Remainder-Decision-Stability-Pilot/pilot-v0.1
p01_path=research/Precision-Amendment-P01
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
sha256sum -c SHA256SUMS
git -C "$repo" archive "$pilot" "$pilot_path" | tar -x -C "$scratch"
git -C "$repo" archive "$p01" "$p01_path" | tar -x -C "$scratch"
printf '%s  %s\n' 'ec4686bafa7277633f257f6ada543ffef25a5ad9e1d841063e549dff87391acf' \
    "$scratch/$pilot_path/evidence/PILOT.json" | sha256sum -c
(cd "$scratch/$pilot_path" && sha256sum -c SHA256SUMS)
(cd "$scratch/$p01_path" && sha256sum -c SHA256SUMS)
export PYTHONPATH="$scratch/$pilot_path:$scratch/$p01_path"
for seed in 0 42; do
    PYTHONHASHSEED=$seed python3 audit.py --out "$scratch/results-$seed.json"
    cmp "$scratch/results-$seed.json" RESULTS.json
done
if (( $# == 1 )); then
    git -C "$repo" diff --exit-code "$pilot" -- "$pilot_path"
    bash "$repo/$pilot_path/verify.sh" "$1"
fi
printf '%s\n' 'PASS: published sources and independently replayed question-completeness audit'
