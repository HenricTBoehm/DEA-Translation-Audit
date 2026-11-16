# Observed cost and responsibility

One measured run on the recorded local Linux environment, wall time per named client call. Separate fresh psql invocations include startup, SCRAM and round-trip cost. This is not steady-state throughput. E2 reconstruction is a client SELECT plus local ledger checking. The SELECT cost is measured and local checking/serialization is not separately timed.

| Operation | N | Median | Min–max |
|---|---:|---:|---:|
| Authorized selection calls (selected normal control stages) | 5 | 21.408 ms | 20.048–76.783 ms |
| Evaluation calls | 8 | 30.193 ms | 23.606–58.559 ms |
| Guarded commit call to returned row (C04 return still uncommitted) | 5 | 43.052 ms | 26.606–70.728 ms |
| Observer tables read | 5 | 24.317 ms | 21.898–51.021 ms |
| Effective ACL snapshot | 6 | 42.600 ms | 20.706–72.423 ms |

The C04 competing select elapsed 184.51 ms with a native lock timeout configured at 150 ms, inclusive of process and connection time. Releasing the held valid commit took a further 1.54 ms measured after the deliberate contention. See MEASUREMENTS.json for per-call times. Human authoring/validation, operational integration, continuous observer costs, standalone digest/reconstruction cost, memory and CPU profiles are **NOT EXECUTED**. Nothing is extrapolated to production operating cost.

| Level | Scope |
|---|---|
| L0 | Existing SQL storage, constraints, native statement snapshots, row locks, transaction atomicity and error signaling |
| L1 | Role/column/function GRANT configuration, SCRAM, log configuration and input queries |
| L2 | Using ordinary psql with PostgreSQL and independent hash verification as composed existing components |
| L3 | Application-specific epoch receipt and commit guard, provenance stitching, local reference assertions and test harness; SQL language does not turn these into built-in policy features |

Added 94 nonblank noncomment SQL lines, 67 cluster-runner lines and 231 Python experiment/reference lines. There is no new general resolver or stand-alone permissions ledger. The schema-specific guard is ordinary SQL plus native locks, with all durable writes occurring inside PostgreSQL.
