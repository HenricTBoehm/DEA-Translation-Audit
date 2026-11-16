# Implementation, costs and open obligations

The kernel inotify notification and proc descriptors are established **L0** primitives. Selecting a watch mask and scope is **L1** configuration. The bounded watcher/decoder, joining filenames to manifests, checking collection, resolver/path recognition, and the historical/control producer are custom. Classify the assembled acquisition pipeline as **L3**, even though it composes established facilities. E1's instrumented runtime and record verification are custom L3. The unchanged Rego decision consumer retains its Phase A L1 classification over declared facts. Its input mapping and history export are L3 and charged independently.

Nonblank and noncomment source lines are evaluator plus embedded E1 53, independent observation and reference descriptor inspection 49, E1/E2 acceptance and projection 59, scenario controller 73, runner/assessment/adapter 250 and regression checks 45. These overlapping shared modules are counted once and cannot give an E1-only versus E2-only authoring estimate. No previous release code is charged as new code. Per run, independent reference uses two FD inspections, two full-file manifest scans, a truth-table check and three synchronization handshakes. E2 uses one per-run directory watch and four drains. E1 emits one report. The three producer combinations each invoke the same three consumer paths.

| Measurement | Median across ten scenarios | Range |
|---|---:|---:|
| Joint evaluator and observation wall time | 70.67 ms | 55.17–85.25 ms |
| E1 normalization | 0.0067 ms | 0.0060–0.0088 ms |
| E2 normalization | 0.0237 ms | 0.0206–0.0343 ms |
| E1 projection plus three consumers | 34.47 ms | 31.34–62.62 ms |
| E2 projection plus three consumers | 36.41 ms | 26.61–76.25 ms |
| Combined projection plus three consumers | 41.00 ms | 24.87–66.78 ms |
| Historical cumulative child peak sampled by runner | 32,116 KiB | 30,196–32,944 KiB |

Values describe one bounded run and are recorded in [MEASUREMENTS.json](MEASUREMENTS.json). The memory figure is Linux RUSAGE_CHILDREN high-water across completed children so far and may include an earlier OPA process. It is not isolated per-path memory or simultaneous RSS. The joint wall time includes startup and coordination; isolated instrumentation overhead, per-method CPU/peak memory and stable latency benchmarking are **NOT EXECUTED**. Human time and real issuer/monitor/security-integration burden are **NOT EXECUTED**. No comparative engineering cost claim follows.

## Open obligations

- Source trust. E1 trusts process claims; E2 additionally trusts kernel, quiet scoped capture and registry, and lacks syscall byte/pid attribution. Assessor FD checks add direct per-PID evidence with trusted synchronization and controlled no-seek evaluator. General hostile or cooperating processes, memory-based inputs and coverage beyond the controlled scope remain unverified.
- Controlled test identities have no independent operational identity provider, signed rights ledger or production revocation. Replay confirms consequences of that ledger and registered version history. Real evidence acquisition for history, permissions and neutralization is open.
- B10 detects a bind/read mismatch after the fact. A general protected commit needs validated same-version atomicity and a trusted ability to enforce it. This study carries out no real commit.
- Wider dependency capture should include resolver choice and configuration authority as first-class dependencies if required by the target rule. That policy change requires prospective approval and a bounded domain, rather than retrospective credit for D1 or SR-1.
