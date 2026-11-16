#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.."
case "${1:-quick}" in quick|full) ;; *) printf '%s\n' 'Usage: check_repository.sh [quick|full]' >&2; exit 2 ;; esac
for directory in RP-1.0 RP-1.0/original-package VP-1.0 research/ADR-001; do
    manifest=SHA256SUMS
    if [[ $directory == */original-package ]]; then manifest=ORIGINAL_SHA256SUMS; fi
    (cd "$directory" && sha256sum -c "$manifest")
done
python3 research/verification-runs/2026-11/check_adr001.py
python3 research/verification-runs/2026-11/check_vp.py
if [[ -d research/Poblete-DEA-Comparison ]]; then
    bash research/Poblete-DEA-Comparison/check_regressions.sh
fi
if [[ ${1:-quick} == full ]]; then
    scratch=$(mktemp -d)
    trap 'rm -rf -- "$scratch"' EXIT
    python3 research/ADR-001/adr001_ctrl.py --out "$scratch/adr001-results.json"
    cmp "$scratch/adr001-results.json" research/ADR-001/results/adr001-results.json
fi
printf 'PASS: repository checks (%s)\n' "${1:-quick}"
