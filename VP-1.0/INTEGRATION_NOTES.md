# VP-1.0 intake notes — 2026-11-16

**Status:** archival Draft PR only. This is not an endorsement of the mathematical proofs or a completed independent verification.

## Original source

- `dea-v0343-verification.zip` SHA-256: `e0adca3e074dd799e69677fd83f119c459e7af57da4e3542dc83bfc3bdb06421`.
- The extracted package has 15 files, and its own `SHA256SUMS` validates the 14 listed members.
- The RP-1.0 remediation ZIP supplied in this conversation has SHA-256 `18b39eaf7535f55f42a775846c1b2a9e45d73dd6e33c6f31a40093d5f263aaa7`, different from the `18667ba7...56fa` ZIP recorded in this verification package.
- RP-1.0's 30 member files have been verified on import, but an identical byte-level ZIP provenance cannot be inferred from member-level equality.

## Reproducibility blocker (newly observed)

`verify.py`'s `extract()` returns `<temp>/dea-v0343-remediation` unconditionally. The actual `dea-v0343-remediation.zip` used for RP-1.0 stores the files at the ZIP root. Direct execution fails immediately with `FileNotFoundError` for `SHA256SUMS` before any checks are recorded.

A *local-only* rewrap of the RP-1.0 archive into a top-level directory allowed the source `verify.py --skip-repro` to finish. It matched the 40 non-R6 reported check records; R6 was `NOT_EXECUTED` rather than the submitted `PASS`, as expected. This rewrap changes the ZIP SHA-256 and is not an acceptable permanent provenance workaround.

A portable extraction fix should be implemented in a separate PR or clearly patched here, followed by a new verification run against the published RP-1.0 ZIP with its original SHA-256. The package's README paths also reference a different workspace layout.

## Known substantive findings (reported, not individually proved by this PR)

- `B8` and `C4`: reductions via RBAC role hierarchies accept non-partial-orders for cyclic control/transition graphs (324/26,262 NAP models; 3,053/3,299 sampled general Ctrl graphs).
- `A1`: task-indexed native T3/H_EJ encoding only preserves nominal identity; multi-principal control countermodels fail.
- `B4`, `C5`: proposed nonexpressibility theorem classes and one proof hypothesis require narrowing/correction.
- `C1`/`C2`: pointwise vs stage-union Ctrl closure diverges on 72/16,807 sampled models.
- `W1`: Wang & Li (2010) not checked by the verification package. Its original PDF was subsequently supplied to this conversation; the missing comparison is a follow-up, not automatically closed.

## Publication scope

The unchanged `VP-1.0` original files and original ZIP are archived on a **draft branch** to permit review. No verification patches are applied to RP-1.0 here, the DEA v0.3.4.3 baseline is unchanged, and no external copyrighted paper PDFs are included. Do not merge before resolving the extraction prerequisite, validating the claim/evidence matrix against original sources, and separating mathematical proofs from finite tests.
