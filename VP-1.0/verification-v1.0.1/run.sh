#!/usr/bin/env bash
set -euo pipefail
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
patch --silent --output "$scratch/verify.py" "$here/../verify.py" "$here/verify.patch"
export DEA_VP_ARCHIVED_RESULTS="$here/../results/verification-results.json"
mkdir "$scratch/work"
TMPDIR="$scratch/work" python3 "$scratch/verify.py" "$@"
