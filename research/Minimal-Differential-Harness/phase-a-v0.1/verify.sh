#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
sha256sum -c SHA256SUMS
(cd ../../Gap-Register-Protocol/v0.1.2-candidate && bash verify.sh)
python3 -B checks.py
phase_output=$(mktemp -d)
trap 'rm -rf "$phase_output"' EXIT
if [[ $# == 1 ]]; then
    PYTHONHASHSEED=42 python3 -B run.py --opa "$1" --output "$phase_output"
    cmp "$phase_output/RESULTS.json" RESULTS.json
    cmp "$phase_output/SUMMARY.json" SUMMARY.json
    python3 -B reconfigure.py "$1"
else
    PYTHONHASHSEED=42 python3 -B run.py --output "$phase_output"
fi
