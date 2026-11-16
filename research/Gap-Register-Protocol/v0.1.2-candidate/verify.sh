#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
sha256sum -c SHA256SUMS
PYTHONHASHSEED=0 python3 -B verify.py
PYTHONHASHSEED=42 python3 -B verify.py
