# DEA Minimal Differential Implementation Harness · Exploratory Phase A v0.1

**EXPLORATORY – NOT SCORED – NOT FREEZE VALIDATION**

A-raw executes an L3 event/lineage adapter inside each arm. A-derived reuses one independent forward provenance export per input across the three arms. The truth and expected verdicts stay in the assessor. The scope is one bounded versioned decision and its governance gate.

- [Results and interpretation](REPORT.md) · [observations](RESULTS.json) · [counts](SUMMARY.json)
- [Source projection and provenance contract](MAPPING.md) · [prospective expectations](hypotheses.md)
- [Runtime observations](MEASUREMENTS.json) · [configuration preflight](CONFIG_CAPTURE.json)

Requires CPython 3.12 and Linux amd64. Python paths use the standard library. Fetch the official OPA release and verify the asset and upstream checksum before execution.

```sh
bash fetch_opa.sh /tmp/phase-a-official-opa
bash verify.sh /tmp/phase-a-official-opa/opa_linux_amd64_static
```

Without an executable argument, verification runs the Python arms and records OPA as NOT EXECUTED. A mismatched digest aborts. Recompute timing separately:

```sh
audit_cpu=$(python3 -c 'import os; print(min(os.sched_getaffinity(0)))')
PYTHONHASHSEED=0 taskset -c "$audit_cpu" python3 -B run.py \
  --opa /tmp/phase-a-official-opa/opa_linux_amd64_static \
  --output /tmp/phase-a-reproduction --benchmark
```

Verification compares deterministic observations and summary byte-for-byte when OPA is supplied. Timing reruns are expected to vary. The script also runs the pinned PR #13 oracle consistency suite. Reproduce older D0, precision and P-01 suites with [the source commands](MAPPING.md).
