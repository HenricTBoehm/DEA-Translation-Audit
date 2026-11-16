# Public reference cases

The [machine-readable cases](PUBLIC_CASES.json) include exact events, admissible projected evidence, assessor truth and nominated expectations. [RESULTS.json](RESULTS.json) records observed oracle output, proof reason, witness and exact wire digest for each execution.

| Group | Public checks |
|---|---|
| K1 | Present/absent actual standard read; when the dependency view is open, opposite-truth twins have identical evidence. |
| K2 | Nominally different operator; p vs q controls the current criterion; the twins withhold the decisive right. |
| K3 | p vs q writes with valid rights before revoke; the change survives in the version actually bound; the twins withhold the write. |
| X-ORDER | Authenticated seal before production, impossible under the grammar. |
| X-TRUST | Separate false dependency-coverage claim with identical bytes to K1-C. |
| M1–M5 | Material threshold, cosmetic layout, hidden or indirect dynamic use, identity-only signer, retract without undo. |
| Temporal and scope extensions | Revoked write, missing or contradictory rank, out-of-range and unverified ranks, missing history, contradiction even with history open, same-time order, new version after binding, original binding, partial and verified reset, neutralized but unbound successor, positive under global incompleteness, absent positive, no rank to add required root, multiple witnesses, duplicate IDs. |

The preserved smoke suite is 13 executions over 10 ordinary views (3 CLEAR, 3 CONFLICT, 6 UNDETERMINED, 1 INVALID). Add X-TRUST separately and 24 public adversarial cases, for 38 executions. This restates the original groups in the corrected grammar with distinct issuer/keys, bounded immutable versions and explicit observed reads. It does not replace the v0.1.1 data. Supplementary model checks derive 144 combinations of actor, channel, revoke, reset, version and ordering. Some have intentionally invalid histories. These are public finite checks, not held-out data or evidence of any contender's capabilities.
