# VP verification runner v1.0.1

Use the original flat RP-1.0 ZIP, the frozen baseline PDF and a scratch output path.

```sh
bash VP-1.0/verification-v1.0.1/run.sh \
  --package-zip /absolute/path/dea-v0343-remediation.zip \
  --baseline /absolute/path/DEA_v0.3.4.3_architecture_closure_candidate_2026-11-15.pdf \
  --out /tmp/vp-v1.0.1.json
```

Requires Python 3, Bash and `patch`. The runner applies the checked-in patch to a temporary copy of the original verifier. It supports the published flat ZIP and the original single-root wrapper. Verify the input ZIP's origin before execution because the verifier executes its archived harness. The runner preserves the byte comparisons and both RP archive hashes in the report. R6 compares all JSON values after normalizing only `meta.python`; a semantic R6 failure and failures of the mechanical R1–R4 checks produce a failing exit status. The verifier aborts before executing the harness when the RP manifest has mismatched hashes. The inherited negative findings are reported as check records. `--skip-repro` explicitly skips R6.

The [audit run](../../research/verification-runs/2026-11/) records the executed comparison, the journal source review and outstanding obligations. VP's inherited W1 record is a reference to the unperformed automated check in that verifier.
