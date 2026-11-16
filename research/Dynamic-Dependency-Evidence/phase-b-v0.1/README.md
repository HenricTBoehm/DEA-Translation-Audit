# DEA Dynamic Dependency Evidence Acquisition · Phase B v0.1

**EXPLORATORY – NOT SCORED – NOT FREEZE VALIDATION**

This public local test compares application assertions with external Linux filesystem observations for a real versioned threshold evaluation. Phase A's policies are reused as diagnostic consumers. Start with the [results and conclusions](REPORT.md), [experiment and scenario design](EXPERIMENT_DESIGN.md), [observation and mapping contract](EVIDENCE_MAPPING.md), and [costs and open obligations](COST_REPORT.md).

## Reproduce

Use Linux x86-64, CPython 3.12, inotify and readable child /proc descriptors. From this directory:

```sh
bash ../../Minimal-Differential-Harness/phase-a-v0.1/fetch_opa.sh /tmp/dea-phase-b-opa
bash verify.sh /tmp/dea-phase-b-opa/opa_linux_amd64_static
```

Verification uses the pinned OPA release, two hash seeds and fresh isolated temporary roots. On the recorded environment it compares the exact results and runs reference/regression checks. Rerun timing separately:

```sh
python3 -B run.py --opa /tmp/dea-phase-b-opa/opa_linux_amd64_static --out /tmp/dea-phase-b-run
```

Omit the OPA argument to record its consumer as NOT EXECUTED. If the runtime denies child-descriptor verification or inotify, the independent evidence is incomplete or unavailable on that host. Keep those results separate from the archived 10 confirmations. Do not treat the application log as a replacement external witness. All files are synthetic, with no private cases.
