# Exploratory Phase A v0.1 · Results

**EXPLORATORY – NOT SCORED – NOT FREEZE VALIDATION**

## Decision results

Each of the six routes saw the same 38 public executions (31 distinct wire views). The SR-1 column is a descriptive comparison against the study rule.

| Decider | Layer | Clear | Conflict | Undetermined | Invalid | SR-1 conditional agreement |
|---|---|---:|---:|---:|---:|---:|
| D0 | A-raw / A-derived, each | 18 | 0 | 12 | 8 | 26/38 |
| D1 | A-raw / A-derived, each | 12 | 6 | 12 | 8 | 32/38 |
| OPA SR-1 | A-raw / A-derived, each | 7 | 12 | 11 | 8 | 38/38 |

1. **A-raw.** D0 clears K2-F, K3-F and M1. D1 adds six diagnoses via surviving threshold effects on actually used immutable versions, including K3-F and M1. D1 still clears K2-F, where the witness is prospective control over an eligible successor. OPA's SR-1 policy treats it as a conflict. D0 and D1 abstain on the open-global positive case for which SR-1 finds a verified local prospective path.
2. **A-derived.** All **114/114** pairs of raw/derived responses match within their decider, including reasons and witnesses. Divergences across deciders persist. Byte-identical views return identical responses in each route. All agree on the eight wire-invalid evidence views by their shared profile admission.
3. **Reconstruction.** The common forward producer took a median 3.88 ms per corpus of 38 inputs, with validation and export serialization. A-raw recomputes per arm. A-derived exports once per execution and shares the result, including repeated executions of the same view.
4. **Native L1.** Official Rego v1 returned all 38 SR-1 conditional verdicts and the same 12 witness paths as the reference. The policy uses native filtering, comparison, sorting and Boolean rules over already reconstructed facts. That demonstrates a configured L1 gate. The end-to-end derived pipeline includes the L3 producer and assumes trustworthy collection.
5. **L3.** The finite event validator, rights as of bind, version provenance and historical effect persistence are custom. A-raw runs with this L3 work for all three arms. The common A-derived producer is likewise L3. D0 and D1 are custom Python source projections. The common replay effort does not count as a feature of any native gate.
6. **Cause.** D0 versus D1 reflects reviewer-side attribution scope. D1 versus SR-1 reflects exact-version control versus a prospective bind-time alternative under the chosen source mapping. A richer resolver with exposed selection controls is unresolved. All arms conditionally clear X-TRUST despite an actual conflict, with the same bytes as K1-C. D0 clears **11/12**, D1 **5/12**, and OPA **0/12** rows with a justified SR-1 conflict. On the separate truth axis, the respective counts are **12/23**, **6/23** and **1/23**. Those axes also include bounded invalid evidence that differs from actual-world invalidity; see the per-row assessor record.
7. **Reconfiguration.** A separate native Rego diagnostic matched the D1 verdict on **38/38** rows using the very same derived facts. Switching from SR-1 to that rule removes the difference from D1 and changes the decision target. Matching both on their six differing cases with unchanged bindings is impossible for one response. The result supports configurability, without proving whole-architecture equivalence or a general expression boundary.

## Implementation and cost

Counts are nonblank, noncomment source lines. Shared validation 138 (wire.py, L3), per-arm backward reconstruction 50 (raw.py, L3), forward producer and shared schema constructors 69 (provenance.py, L3), adapters 49, primary harness and instrumentation 154, independent checks 73. D0 and D1 decision modules 23 and 16 respectively. SR-1 Rego gate 38 (L1 over declared facts); the separate diagnostic probe takes 20 lines and is excluded from primary metrics. Costs for validation and schema helpers are declared once as shared source work. Their execution is included in each raw arm and in the common forward producer run. These counts exclude the established runtime, archived test suites and result data.

Recorded on Linux x86-64, CPython 3.12.14, one CPU affinity, one warm-up and ten timed fresh-worker corpus runs per route. Each trial makes 38 calls. Python decisions are in-process; OPA starts and compiles the CLI for each case. CPU includes child processes during the timed loop. Peak RSS is lifetime for the worker or the largest individual child process, separately. It includes the input harness and cannot be added as simultaneous resident memory. Throughput against alternative runtime lifecycles is unmeasured.

| Route | Median ms / 38 cases | Worker peak KiB, median | Largest child peak KiB, median |
|---|---:|---:|---:|
| D0 raw | 3.82 | 14,596 | — |
| D0 derived | 0.47 | 14,596 | — |
| D1 raw | 3.40 | 14,596 | — |
| D1 derived | 0.50 | 14,596 | — |
| OPA raw | 643.90 | 14,596 | 32,308 |
| OPA derived | 632.79 | 14,596 | 32,180 |
| Common forward producer only | 3.88 | 14,596 | — |

The [measurement snapshot](MEASUREMENTS.json) retains ranges and CPU. The local timed configuration replay from an already downloaded asset took **0.329 s** to install and check, **0.049 s** to compile/check Rego, and **0.302 s** for Python/evidence preflight. Human authoring time, download time, actual evidence acquisition, issuer and monitor work, and matched deployment cost were **NOT EXECUTED / not measured**. No relative integration-cost advantage is established.

## Scientific disposition

**Technical feasibility demonstrated** for the scoped mappings and official OPA executable. **Scientific value remains exploratory.** The decision rules are expressible in configured Rego once the shared data exist. Substantive differences remain because the exact-version and prospective control definitions answer different questions. This run gives insufficient reason for a confirmatory decision-only competition using the same rules and evidence.

A later preregistered comparison is worthwhile if it tests **how independent procedures obtain and verify actual dependency, selection and effect-history evidence under matched access and budget**. The minimal useful follow-up compares evidence producers for one versioned threshold decision with actual dynamic reads and uncertain history. First settle exact-version and precursor-selection semantics, then use prospectively isolated cases. Practical burden, evidence reliability and atomicity need operational measurements. Neither general DEA superiority nor full equivalence follows here.
