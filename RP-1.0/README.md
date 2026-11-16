# DEA v0.3.4.3 translation-audit remediation package (RP-1.0)

This package independently verifies the original translation audit in `original-package/`, which is preserved unchanged. It does not modify DEA v0.3.4.3.

## Contents

| File | Purpose |
|---|---|
| `02-remediation-report.md` | findings, corrections, unresolved issues |
| `07-contribution-assessment.md` | the four contribution dimensions and verdicts A and B |
| `04-crosswalk.csv` | construct × source grid with pages, classification and tests |
| `03-translation-specification.md` | Regime A and Regime B mappings, as implemented |
| `05-countermodel-catalogue.md` | minimal countermodels and proof witnesses |
| `06-change-log.md` | differences from the original package |
| `01-remediation-protocol-v1.md` | protocol RP-1.0 (hash-checked by the harness) |
| `harness/` | standard-library Python 3 harness (`run_audit.py`, `engines/`, `translations.py`, `dea_ref.py`, `models.py`) |
| `results/remediation-results.json`, `results/countermodels.json` | machine-readable results |
| `original-package/` | the original audit files, their checksums and the archival zip |
| `SHA256SUMS` | checksums of every file in this package |

## Clean-room reproduction

The only requirements are Python ≥ 3.8 and the baseline PDF (SHA-256 `51a2553e8bb13fe80bc3f0e6245ba0c4dcbe0a31db03ad577a3f3f26f8c97c33`). The run takes about 2–3 minutes.

```bash
mkdir /tmp/cleanroom && cd /tmp/cleanroom
unzip /path/to/dea-v0343-remediation.zip
cd dea-v0343-remediation
sha256sum -c SHA256SUMS
python3 harness/run_audit.py --baseline /path/to/DEA_v0.3.4.3_architecture_closure_candidate_2026-11-15.pdf \
        --out /tmp/cleanroom/out/remediation-results.json
cmp /tmp/cleanroom/out/remediation-results.json results/remediation-results.json && echo REPRODUCED
cmp /tmp/cleanroom/out/countermodels.json results/countermodels.json && echo REPRODUCED
```

## Exit codes

| Code | Meaning | Results file written? |
|---|---|---|
| 0 | success | yes |
| 1 | uncaught exception during tests | no |
| 2 | baseline or protocol missing or altered, or harness incomplete | no |
| 3 | static independence check failed (an engine or translator imports `dea_ref`) | no |
| 4 | internal error while writing output | no (or incomplete) |
