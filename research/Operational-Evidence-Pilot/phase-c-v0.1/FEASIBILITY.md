# Feasibility and provenance

**FEASIBILITY GO.** PostgreSQL provides native runtime SELECT against a current persisted binding, version rows, authenticated logins, column ACLs and locks. No selection algorithm or substitute authorization registry is implemented in Python. The authorized update succeeds through the normal SQL entry point. Schema, database audit and a narrowly scoped commit guard configure the mechanism.

| Alternative | Observed or reviewed constraint |
|---|---|
| Git 2.52.0 | Content-addressed object versions and conditional ref transactions are available. Local shared-repository plumbing does not expose the independent writer/selector database-style authorization needed here without an additional authority service or policies. Not executed as a resolver. |
| SQLite 3.53.1 | Embedded SQL and transactions are available. An actual in-memory GRANT probe returned a syntax error. Native independent writer and selector logins are absent. |
| PostgreSQL 17.11 | Not preinstalled. Extracted three pinned Debian packages in temporary storage. Unix socket probe was denied by this execution sandbox. Loopback-only SCRAM cluster successfully started. Before implementing C00–C04, a temporary SQL probe showed an allowed version insertion and selection update with the opposite grants absent in the PostgreSQL catalog. |

The downloaded package bytes match SHA-256 values from Debian's signed trixie InRelease and associated package index. See fetch.sh. The used server version was 17.11 (Debian 17.11-0+deb13u1) on Debian 13.6 amd64, Linux 6.18.57, CPython 3.12.14. System package state was uninvolved. PostgreSQL documentation references [GRANT](https://www.postgresql.org/docs/17/sql-grant.html), [transaction isolation](https://www.postgresql.org/docs/17/transaction-iso.html), [UPDATE](https://www.postgresql.org/docs/17/sql-update.html). Alternatives [Git ref transactions](https://git-scm.com/docs/git-update-ref.html) and [SQLite omitted SQL features](https://sqlite.org/omitted.html).

| Reference | Verified commit | Relevance |
|---|---|---|
| PR #15 | `ed22942b350ac54f9dd32b07e8ef8a3860c3428f` | Verified parent and Phase B read/binding observation limits |
| PR #14 | `228d793b1a1c2edcd7e0b1c0cc914482b76359e6` | Frozen source-scoped D0, P-01/D1 and SR-1/Rego consumers |
| PR #13 | `b1631406c9434a214da98b2a49115be26a40c7db` | Existing finite wire and exploratory boundaries |
| PR #12 | `80d0e5a77937df62521f3a4f47a9437097ad5eb7` | Conditional premises, X-TRUST and independent review |
| PR #7 | `91e842fdae94356ff323f3afb2e99245369108da` | Exact version/mandatory dependency control semantics |

All pins were checked against the remote PR heads. Phase B's committed digest manifest was also checked. No historic files or PRs were edited.
