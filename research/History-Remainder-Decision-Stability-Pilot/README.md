# DEA HR-1 × Decision Stability — bounded comparative pilot

**Status:** non-normative, pre-registered research design; **not** a validated implementation or scientific adoption.
**Repository baseline:** main@2fc5e7f353f1984e663110e3eb0a0d9e38ba7fa4.
**Related:** Draft PR #7 (P-01), #6 (temporal evidence), #5 (reproducibility), #4 (hypothetical Poblete comparison). No merges required.

## Research question

Can decision-output stability under explicitly modeled historical uncertainty give **additional diagnostic information** beyond HR-1's conservative history-remainder/control gate, without converting an unresolved or proven governance conflict into a clearance?

Compare two independent properties:

1. **Governance:** authenticated effective control, historical completeness, mandatory rubric dependencies and seal/commit evidence. Verdicts remain MODEL_INVALID / CONFLICT / NO_CONFLICT_ESTABLISHED / UNDETERMINED.
2. **Substantive stability:** does the same **fixed, authorized evaluation procedure** reach the same domain judgment over every admissible, evidence-compatible historical world? Stability is a diagnostic only, NEVER permission to adjudicate.

If the set of worlds is not certified as covering the relevant alternatives, stability may be called **observed in sampled worlds**, never universally proved.

## Materials

The uploaded HR-1 bundle and the earlier DRHC P-02 note are **not embedded in this PR**. Their exact SHA-256 identifiers and limitations are in SOURCE_MANIFEST.md. GPT Work must obtain these files as task attachments; absence is NOT_EXECUTED, not an invitation to reconstruct and claim source reproduction.

## Work packages

- Freeze a 12-scenario casepack and baseline A/B/C/D before running comparative tests.
- Reproduce HR-1 unchanged, report exact/qualitative differences and Python hash-order sensitivity.
- Independently implement the decision-stability check and its countermodel oracle, keeping the control verdict as an independent output.
- Measure extra diagnostic yield, false-negative control clearance, blocking/undetermined rate, witness traceability and evidence/certificate effort.
- Publish a separate Draft PR for executable artifacts; preserve this protocol, previous manuscripts and archived outputs. No automatic merges.

See DESIGN.md, PILOT_PROTOCOL.md, SOURCE_MANIFEST.md and OPEN_OBLIGATIONS.md.
