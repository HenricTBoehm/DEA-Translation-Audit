# DEA Translation Audit

Reproducibility materials for the adversarial translation and prior-art audit of **DEA v0.3.4.3** (15 November 2026). The authoritative DEA manuscript is **not** modified or republished here.

## Status — research audit candidate, not a formal verification certificate

**RP-1.0 / M0** is an archived, integrity-checked baseline. Its remediation report rates the audit **CONDITIONAL GO**. Reproducing the reference output is not equivalent to proving the translations semantically correct or establishing formal novelty.

The complete, unmodified remediation package is preserved under [`RP-1.0/`](RP-1.0/), including the prior audit in `RP-1.0/original-package/`. File-level checksums remain those distributed with RP-1.0. Future changes should be proposed on branches and reviewed in pull requests; do not rewrite this baseline.

## Reproduce

Requirements: Python 3.8+, `sha256sum`, and the separately supplied DEA v0.3.4.3 baseline PDF. **The baseline PDF is intentionally not redistributed.** Its required SHA-256 is:

`51a2553e8bb13fe80bc3f0e6245ba0c4dcbe0a31db03ad577a3f3f26f8c97c33`

```bash
cd RP-1.0
sha256sum -c SHA256SUMS
python3 harness/run_audit.py \
  --baseline /absolute/path/to/DEA_v0.3.4.3_architecture_closure_candidate_2026-11-15.pdf \
  --out /tmp/dea-rp10/remediation-results.json
cmp /tmp/dea-rp10/remediation-results.json results/remediation-results.json
cmp /tmp/dea-rp10/countermodels.json results/countermodels.json
```

The checked-in reference results are not a substitute for rerunning the harness. The original RP-1.0 `README.md` documents the archived ZIP's standalone extraction workflow; its commands assume a separately created directory named `dea-v0343-remediation`.

## Open verification obligations

1. **Wang & Li (2010):** journal article not inspected in RP-1.0; related 2007 ESORICS work is not a drop-in substitute. The 2010 source is available to the researcher for future review, but the RP-1.0 report remains unchanged.
2. **RBAC hierarchy domain:** an independent audit found that 324 of 26,262 models used in a Li-role-hierarchy NAP reduction produce non-antisymmetric role relations; equivalence on those structures is not yet an admissible reduction into a partial-order RBAC hierarchy. Recheck with a valid encoding or explicitly narrow the model class.
3. **CTRL-6b:** the DEA baseline does not select per-instant versus stage-union control closure. The original boundary model distinguishes them.
4. **Proof scope:** in particular, inspect `PRF-NAP-HANF`, `PRF-LED4`, and `PRF-CTRL-WL-MONO` against their precise translation classes and the cited primary definitions. Finite regression agreement is not a universal proof.
5. **Independent review:** RP-1.0 engines were created and evaluated by the same auditor; independent source-semantic review is outstanding.

These are **known limitations**, not modifications to RP-1.0 results. See [`RP-1.0/02-remediation-report.md`](RP-1.0/02-remediation-report.md) and [`RP-1.0/07-contribution-assessment.md`](RP-1.0/07-contribution-assessment.md).

## Scope and rights

This repository is a research artifact and does not establish a new formal authorization logic or experimentally validated enforcement effectiveness. Third-party primary-literature PDFs are not redistributed. **No open-source license has yet been selected; public visibility alone does not grant reuse rights.** The archived RP-1.0 contents are preserved for provenance and reproducibility, not silently re-licensed.
