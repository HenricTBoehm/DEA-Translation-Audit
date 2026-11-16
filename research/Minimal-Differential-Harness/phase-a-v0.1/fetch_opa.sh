#!/usr/bin/env bash
set -euo pipefail
dir=${1:?usage: bash fetch_opa.sh /absolute/download-directory}
mkdir -p "$dir"
cd "$dir"
asset=opa_linux_amd64_static
remote=https://github.com/open-policy-agent/opa/releases/download/v1.22.4
curl -fLSs --max-time 180 "$remote/$asset" -o "$asset"
curl -fLSs --max-time 60 "$remote/$asset.sha256" -o "$asset.sha256"
printf '%s  %s\n' 35e3b352e715e80624ead6c89930d8585f6f7d94cdc409eb2a9fe36620dcccba "$asset" |
    sha256sum -c -
printf '%s  %s\n' a09d17f9a8f2ac02d85b91f11c719b905e47eadaf8da33a829c1e46fc173989a "$asset.sha256" |
    sha256sum -c -
sha256sum -c "$asset.sha256"
chmod +x "$asset"
"./$asset" version
