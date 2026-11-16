# DEA v0.3.4.3: independent verification of RP-1.0

## Reproduce

Requires `python3` (standard library only), the remediation zip and the DEA v0.3.4.3 baseline PDF. Run from the workspace root:

```
python3 co-scientist-outputs/dea-v0343-verification/verify.py \
  --package-zip co-scientist-outputs/dea-v0343-remediation.zip \
  --baseline uploads/DEA_v0.3.4.3_architecture_closure_candidate_2026-11-15.pdf \
  --out co-scientist-outputs/dea-v0343-verification/results/verification-results.json
```

- **Run time.** About 2.5 minutes. Most of this is the clean-room re-run of `run_audit.py` (check R6).
- **Faster run.** `--skip-repro` skips R6 and finishes in about 3 seconds.
- **Exit codes.** The script exits 2, writing nothing, if the baseline is missing or its SHA-256 differs.
- **Isolation.** Each failure-mode test runs in a fresh extraction under the system temp directory. The package and the baseline are never modified.
- **Determinism.** Sampling is seeded (20261116).

## Patches

To apply the patches and re-run, see `patches/CHANGELOG.md`.

## Contents

| File | Content |
|---|---|
| `verification-report.md` | PASS / FAIL / UNDETERMINED / NOT EXECUTED; obligations; audit decision; DEA contribution assessment |
| `claim-evidence-table.csv` | 22 report claims, each with its source definition, implementation, proof, countermodel, checks and status |
| `counterexamples.md` | CX-1 … CX-8 |
| `crosswalk-corrections.csv` | 19 corrections to RP-1.0 `04-crosswalk.csv`, including the Wang & Li 2010 rows |
| `results/verification-results.json` | 41 machine-readable checks |
| `patches/` | VP-1 … VP-5, `CHANGELOG.md` and `patched-remediation-results.json` |
| `verify.py` | the verification harness |
| `SHA256SUMS` | checksums |
