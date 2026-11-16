# Phase C v0.1 · Operational Evidence Pilot

**NO-GO – EXISTING MECHANISMS SUFFICIENT**, within the controlled single-database scope. **EXPLORATORY – NOT SCORED – NOT FREEZE VALIDATION.**

PostgreSQL 17.11 completed C00–C04 using SCRAM identities, native ACLs and real committed state. There are five durable decisions, one for each control. Two clean clusters with different Python hash seeds produced identical evidence artifacts. No comparison of DEA versus Rego performance or expression was run.

| Question | Observed finding |
|---|---|
| F1 · Separate authority | Yes. The writer created a version and failed to select it in C01. The selector in C02 selected both versions and failed to create or alter a criterion. The catalog and real SQLSTATE 42501 controls agreed. |
| F2 · Actual version | Yes in the tested mechanism. The evaluation SQL selected and used the version in a single native statement. The receipt, digest, arithmetic and durable decision independently agree in the controlled run. |
| F3 · Historical provenance | Yes for tested events. Retained author/version and publication→selection transaction ordering distinguish criterion authorship from selection. The C03 log corroborates the event window. External identity and log completeness remain unproven. |
| F4 · Surviving effect | Yes. C03 revoked the writer's insertion grant and a subsequent insertion returned 42501. The previously written threshold 1 was still selected, consumed, and changed the score-0 result from accept to reject relative to the base. |
| F5 · Binding changes | C04 rejected the check/use disagreement (23514), stale binding (40001) and missing check (23514), with zero durable rows for these failures. In the valid transaction, a concurrent selection timed out on the locked row (55P03). The fresh decision later became visible, and subsequent selection changed the current version without altering that recorded binding. This verifies enforcement through the tested commit path. |
| F6 · Assertions | Complete historical coverage, organizational identity and off-system rights are unverified. An independently authenticated human preliminary review is asserted only, even when the submitted pair matches. The server and administrative integrity assumptions remain explicit. |
| F7 · L3 work | Schema-specific selection receipts, the small commit guard, lineage joins and test instrumentation are custom. Native authentication, ACLs, FK, snapshots, row locks, transaction atomicity and SQL errors supply the enforcing primitives. |
| F8 · Gain over Phase B | Yes for a bounded question. Phase B stipulated authorities and detected a mismatch. Phase C exercised effective permissions by separate authenticated logins and verified prevention at commit. C02 causally demonstrates operative selection control independent of writing. The setup is still a pilot. |
| F9 · Remaining DEA question | No DEA-specific operational gap was isolated here. External evidence completeness and accountability across trust boundaries remain engineering/research questions. Demonstrating their DEA-specific relevance would require a concrete decentralized mechanism, observable unmet duty and evidence of improvement over an existing method. |

**Recommendation:** close this research branch at Phase C as a bounded null result for distinct DEA advantage. Reopen only if a real deployment supplies a concrete missing obligation that native mechanisms plus ordinary explicit evidence joins cannot fulfill, or a testable hypothesis that DEA materially improves its fulfillment. The findings support the exact operational profile investigated. They do not establish complete cross-system control provenance or a new general DEA result.
