#!/usr/bin/env bash
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
(cd "$here" && sha256sum -c SHA256SUMS && cd original && sha256sum -c ORIGINAL_SHA256SUMS)
ref="$here/../../Gap-Register-Protocol/v0.1.2-candidate"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
setup() {
    local target=$1 source=$2
    mkdir -p "$target/source" "$target/vendor/pr13"
    cp "$source/"{build.py,score.py,selftest.py} "$target/"
    cp "$source/source/spec.py" "$target/source/"
    cp "$ref/"{oracle.py,cases.py,PUBLIC_CASES.json} "$target/vendor/pr13/"
}
setup "$tmp/original" "$here/original"
(cd "$tmp/original" && python3 build.py && python3 selftest.py)
for seed in 0 42; do
    setup "$tmp/$seed" "$here"
    cp "$here/prepare_pilot.py" "$tmp/$seed/"
    (
        cd "$tmp/$seed"
        export PYTHONHASHSEED="$seed"
        python3 build.py
        python3 selftest.py
        python3 prepare_pilot.py --model UNPINNED-DRY-RUN --out pilot
    )
done
diff -r "$tmp/0/build" "$tmp/42/build"
diff -r "$tmp/0/pilot" "$tmp/42/pilot"
printf '%s\n' 'PASS: original and revised public suites; revised build and pilot byte-identical under two hash seeds'
