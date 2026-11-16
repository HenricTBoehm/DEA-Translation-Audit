# Rights, operations and post-hoc control interpretation

The tested role/authentication matrix distinguishes effective column or function privileges verified in the PostgreSQL catalogs, actual SQL success/SQLSTATE through separate logins, and native persisted state. See RESULTS.json for full per-case snapshots, actors and operations.

| Relation | Writer | Selector | Adjudicator | Committer | Enforcement and evidence |
|---|---|---|---|---|---|
| MayCreateVersion | Yes until C03 revoke | No | No | No | INSERT(version,threshold); positive creation and negative probes |
| MayModifyCriterion in place | No | No | No | No | No UPDATE grant on criterion; negative probes for writer/selector |
| MaySelectVersion | No | Yes | No | No | UPDATE(version) on the binding row; version FK; actual denied writer selection |
| DidSelectVersion | None | Succeeded in four scenarios | None | None | Selection trigger records actual changing or reaffirming operation; C01 uses provisioned v0 |
| DidConsumeVersion | None | None | Yes when function succeeds | No | Database evaluation row binds the criterion read to arithmetic and exact digest |
| MayAdjudicate | No | No | Yes | No | EXECUTE on the evaluation function |
| MayCommit | No | No | No | Yes, guarded | EXECUTE only on the commit guard; direct commit-row INSERT denied |

The observer has read-only scope. The test administrator/owner is outside that matrix and is part of the trusted base. Authority to author a different threshold in a fresh version is a material capability; it does not imply direct alteration of already published bytes. Selection changes activation, not author. C02 separately verifies existing versions and measures a material selection effect at the same score. C03 proves a concrete surviving effect on the selected snapshot after removing the author's publication capability. Revocation acts on future writes and does not change the stored version.

The PR #14/#15 consumers were reviewed as control standards without rerunning a D0/D1/OPA tournament. D0's scoped identity comparison needs verified production/adjudicator identity and completeness. D1 adds surviving material influence on exact read versions and requires source evidence for the overlap. C03 shows the historical criterion-side input; this experiment makes no shared-production conflict claim. The existing SR-1 Rego is configured over such provenance and has no independent resolver-authority fact in its frozen projection. C02's selector can materially control the outcome without a criterion write. A separate unvalidated hypothesis would treat the resolver decision as its own bound dependency and use a witnessed actor, enforceable alternative set and material counterfactual, in addition to production/control facts. A configured policy could consume those facts, while the executed native guard already enforces the narrow same-binding commit requirement. No new DEA predicate or revised P-01 implementation is included or claimed as validated.
