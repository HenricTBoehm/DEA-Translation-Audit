# Evidence levels and edge-status ledger

**E1** is the authenticated client-side observation. Responses to binding check/evaluation and commit calls record the result the client says it received, exact version, epoch, digest and predicate result. A matching displayed result alone is insufficient.

**E2** is native server evidence through a separate read-only observer login plus a local server-log read by the harness. It checks effective grants, retained versions, binding state, authenticated selection actor, evaluation rows, and durable decision rows. SQL statement logs identify the login with the operation and capture the C03 sequence. Client-supplied application tags correlate statements with probes. Authorization is carried by SCRAM sessions and table/function permissions, not these labels. Selection receipts and final rows come from the same PostgreSQL trusted base as the executed SQL.

**E3** uses independently controlled input versions, expected action schedule, real positive/negative calls with separate role credentials, independent SHA-256 and arithmetic, and visibility/lock contention probes. The author/revocation case checks transaction ID order and independent server journal ordering. Commit integrity includes an adversarial same-row update from an independently authenticated live connection, beyond rereading stored claims. The assessor still trusts PostgreSQL, the host, and the cluster administrator. This is not independent recovery from hostile or secretly rewritten server state.

`RESULTS.json` records a per-case edge ledger. VERIFIED is scoped to this trusted-base experiment, while a negative probe can establish CONTRADICTED for the claimed unauthorized or stale transition.

| Edge | Verification used |
|---|---|
| Principal → effective permission | Authenticated test logins, native role catalog, allowed/denied calls for inspected roles |
| Permission → actual selection | Actual expected role's SQL operation, retained row/log actor cross-check, or trusted genesis in C01. C01 writer's assertion of selection is contradicted by actual denial. |
| Selection → resolver state | Epoch and version in transactional receipt and observed active row, including pre/post snapshots in C04 |
| Resolver state → consumed version | Evaluation row from the snapshot join, verified equality to epoch receipt, threshold digest and independent arithmetic. Stale checked pair in C04 is contradicted by actual consumption. |
| Consumed version → historical material effect | Original author and content verified for C02–C04. Writer's old material effect in C03 survives authenticated grant removal; there is no exercised earlier writer effect on selected v0 in C00/C01. |
| Consumed version → committed decision | Persisted decision joins recorded evaluation and receipt. Native guard plus competing lock timeout establish the within-transaction binding. Stale, missing and mismatched checks leave no row. |

A narrative that a human independently inspected a value before calling commit is **ASSERTED_ONLY** by the client. C04 establishes matching submitted and used bindings, not a signed human review receipt. External non-recorded rights, absence of prior unlogged control and complete out-of-scope event capture are **UNKNOWN**. Organizational identity of a real operator, actions outside this host, and operating-system administrator changes are **NOT OBSERVABLE** here. An authenticated journal line does not guarantee a complete journal. The X-TRUST indistinguishability boundary stays intact. Neither contradictory evidence nor missing activity should be replaced by a presumed clean history.
