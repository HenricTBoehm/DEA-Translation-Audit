#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ $# != 1 ]]; then
    printf '%s\n' 'Usage: bash verify.sh /absolute/path/to/dea-hr1-history-remainder.zip' >&2
    exit 2
fi
bundle=$(realpath -- "$1")
work=$(mktemp -d)
trap 'rm -rf -- "$work"' EXIT
printf '%s  %s\n' '69475ff7729c60bb70d4eac8e6c5de03206ae26abd2200fc37a499e0d72c8859' "$bundle" | sha256sum -c
sha256sum -c SHA256SUMS
mkdir "$work/source" "$work/p01"
unzip -q "$bundle" -d "$work/source"
(cd "$work/source" && sha256sum -c "$OLDPWD/SOURCE-MEMBERS.sha256")
git -C "$(git rev-parse --show-toplevel)" archive 91e842fdae94356ff323f3afb2e99245369108da research/Precision-Amendment-P01 | tar -x -C "$work/p01"
export PYTHONPATH="$work/p01/research/Precision-Amendment-P01"

# Leave the source code and archived results untouched.
patch --silent --output "$work/hr1_deterministic.py" "$work/source/hr1_remainder.py" HR-1-deterministic-v1.patch
for seed in 0 1 42; do
    PYTHONHASHSEED=$seed python3 "$work/source/hr1_remainder.py" --n 20000 --out "$work/original-$seed.json"
    cmp "$work/original-$seed.json" "evidence/original-$seed.json"
    PYTHONHASHSEED=$seed python3 "$work/hr1_deterministic.py" --n 20000 --out "$work/deterministic-$seed.json"
    cmp "$work/deterministic-$seed.json" evidence/deterministic.json
done
PYTHONHASHSEED=0 python3 adversarial.py --source "$work/source" --out "$work/adversarial.json"
cmp "$work/adversarial.json" evidence/ADVERSARIAL.json
for seed in 0 42; do
    PYTHONHASHSEED=$seed python3 pilot.py --n 1000 --out "$work/pilot-$seed.json"
    cmp "$work/pilot-$seed.json" evidence/PILOT.json
done
printf '%s\n' 'PASS: original and corrected HR-1, countermodels, independent pilot and checksums'
