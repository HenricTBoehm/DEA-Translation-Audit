# DEA Operational Evidence Pilot · Phase C v0.1

**EXPLORATORY – NOT SCORED – NOT FREEZE VALIDATION**

Read the [result and F1–F9](REPORT.md), [feasibility and source pins](FEASIBILITY.md), [experiment design](EXPERIMENT_DESIGN.md), [authority matrix](AUTHORITY_AND_SELECTION.md), [evidence chain](EVIDENCE_CHAIN.md), [costs](COSTS.md) and [limitations](LIMITATIONS.md). The only persisted data in the PR are synthetic observations and timing.

Reproduce on Debian 13 amd64 or an ABI-compatible Linux with CPython 3.12, curl, dpkg-deb, permitted temporary PostgreSQL storage and loopback TCP. Run as a non-root user:

```sh
bash fetch.sh /tmp/dea-phase-c-pg-dist
bash verify.sh /tmp/dea-phase-c-pg-dist
```

The pinned packages are validated before extraction. No system package installation, OS-user creation, service setup or external network listener is required. Each run creates a separate short-lived cluster with restricted random test credentials and SCRAM. If a pinned package disappears from the stable pool, use the identical package from a Debian archive or snapshot and check the hashes in fetch.sh before extraction. Different binaries or OS boundaries require recording a separate reproduction.

For a new timing snapshot, run python3 -B run.py with the same --distribution and a fresh --out directory. The verifier compares RESULTS.json byte-for-byte; timings are intentionally independent of that comparison.
