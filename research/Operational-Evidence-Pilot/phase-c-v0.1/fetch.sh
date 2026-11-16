#!/usr/bin/env bash
set -euo pipefail
destination=${1:?usage: bash fetch.sh /absolute/distribution-root}
mkdir -p "$destination"
destination=$(realpath "$destination")
cache=$(mktemp -d)
trap 'rm -rf "$cache"' EXIT
cd "$cache"
origin=https://deb.debian.org/debian/pool/main/p/postgresql-17
for package in postgresql-17 postgresql-client-17 libpq5; do
    filename="${package}_17.11-0+deb13u1_amd64.deb"
    curl -fLsS --max-time 120 "$origin/$filename" -o "$filename"
done
sha256sum -c <<'EOF'
d2ce1ddffafa783f9acda4c92c86fc21e8288bff3782d739294f14fa797d7886  postgresql-17_17.11-0+deb13u1_amd64.deb
9d8558f8dd57c8e92e218a20698383575d53742ca3f9e7c2b7fe5f246d5216ae  postgresql-client-17_17.11-0+deb13u1_amd64.deb
20a4c9ef58b4baf90deda67cfb2cc062871c062830dddc234d28f5ac7931b86b  libpq5_17.11-0+deb13u1_amd64.deb
EOF
for filename in *.deb; do
    dpkg-deb -x "$filename" "$destination"
done
