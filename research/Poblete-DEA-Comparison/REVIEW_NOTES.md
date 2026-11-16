# Integration and adversarial review notes — 2026-11-16

## Intake checks

- Original input: `dea-poblete-comparison.zip`, SHA-256 `dafa9893120cb303a5a0307828be8d6a5884fe46455f255c19a932610d7c1bd1`.
- ZIP CRC: PASS, eight members: seven text/source files and one Python 3.14 bytecode cache entry.
- The source scripts reproduced both archived result JSON files exactly after arranging the ADR-001 dependency in the original expected sibling directory. Five hypothetical PB readings were executed; no external system state or actual Poblete authorization record was evaluated.
- Compatibility for the GitHub directory layout is documented using `PYTHONPATH=../ADR-001`. Original scripts and result JSON are unchanged.
- The source `.pyc` remains in the original archival ZIP only.

## Findings and constraints

1. **PB-3v stage typing — must repair.** The v0.3.5 and ADR-001 models define execution time within theta_E={0,1}; PB-3v sets t_exec=2 to model the Stage-7 verification report, without retyping the production stage. Its reported `CONFLICT` is a computation, not yet a formally admitted regression witness. Future correction: create a new transition with its own stages or generalize the harness while preserving the original source as a snapshot.
2. **No observed control graph.** None of the PB edge assumptions was established from the reported workflow. A `CONFLICT` in PB-1 is an *if-then* result only.
3. **Insufficient evidence != defective implementation.** The v0.3.5 `RECORD['as_reported']=False` reflects missing publication evidence for all the required certified records. That does not establish their actual absence and does not imply a demonstrated violation by the publication's authors.
4. **Principal identity vs control edge.** `p↔j` models the Human Orchestrator and acceptance identity through mutual control. A separate `SamePrincipal` relation may be required to avoid conflation. ADR-001 is not normatively adopted.
5. **Scientific acceptance and metrics.** The paper's technical evaluation and pilot metrics are not evidence for UTR/UAR, independent verification of DEA's T3 or CTRL-6b, or improvements in false-block rates.
6. **Source and claim audit.** Publisher HTML was accessible and confirms the paper's workflow and stated limits; the exact referenced PDF hash, preprint, detailed figures, LATTICE [10], and page-by-page equality were not checked during this intake. All claims of absence of DEA controls remain *scoped observations* of the compared draft, not global nonexistence proofs.
7. **Data leakage research lead.** Reference read-access and held-out-ground-truth separation (G-P1) is a plausible ADR-003/pilot hypothesis, not an established missing DEA feature without a comprehensive source review.

## Correct future work

- Repair PB-3v's stage constraints and add a structural validation guard to the test harness.
- Add an independently justified counterfactual with and without a real effective-control path; clearly separate verified edge evidence from assumed topology.
- Audit v0.3.5 for evidence completeness, missing-seal treatment, and whether an `UNDETERMINED` case should pause, route for independent adjudication, or return for additional evidence; measure false blocks in the pilot.
- Review preprint and governance-first capability-control literature (especially LATTICE) before any novelty claim.
- The 21-row crosswalk, two reports and computation results remain a *research package for review*, not a normative specification or empirical DEA validation.

## Adversarial reproduction and PB-3v correction

- **CONFIRMED** — On PR #4's original head `fb542df11e513faa6a4cc72fd37088f06c1c114f` using CPython 3.12.14, both original checks finished successfully (0.298 s and 0.074 s wall time) and generated identical bytes. SHA-256 for ADR-001 comparison `771001987bd36eb79ead90a6bb1c87987cfdc8ba8b8e16ffa2bfb4e52a17fb79`, for draft comparison `5571734c1e9efdf365bf7d333903501ec6cf17f81bd41f090ab5d23648736c2b`.
- **MODEL_INVALID** — PB-3v sets production at 2 outside the original {0,1}. The archival evaluator computes a conflict because its causal windows use the seal, yet the input fails stage membership. Treat the archived decision as invalid evidence. The original PB-1, PB-2, PB-3 and PB-4 times satisfy stage and seal constraints. Their edge choice, artifact scope and identity assumptions remain conditional.
- **CONFIRMED** — In [typed-v1.0.1](typed-v1.0.1/check.py), stage 7 produces a distinct report about the already sealed execution output. Stage 8 adjudicates the report. The same-person mapping is a fixture-level canonical identity, so the adjudicator is reflexively reachable from the human principal without invented bidirectional edges. With authenticated hypothetical human control of report production at 2, C still computes `CONFLICT`, now on a well-formed transition. For the execution output the same edge falls after the seal. The paired no-edge control and incomplete-record variants are executable.
- **UNDETERMINED** — An actual human-to-agent edge, certified events, scope, authorized resets, and proof of record completeness are unavailable from the paper. The manuscript describes separate read-only verification and subsequent human decision, and acknowledges limitations in historical records and explicit identity/authorization mechanisms (publisher HTML §§6 and 10, https://www.mdpi.com/2079-9292/15/21/5135). Read-only with respect to the evaluated state leaves report production as a separate question. Sealing at 2 and the order of edge activity before the report seal are scenario assumptions.
- **FAILED_ENCODING** — The archived `as_reported` label still evaluates hypothetical edges and reports positive conflicts for PB-1/PB-3v. A positive outcome on incomplete evidence requires a verified witness. The typed variant uses an empty positively authenticated graph for publication-only evidence and yields `UNDETERMINED`. Verify the broader evidence and identity semantics before a scientific claim. Keep this PR Draft.
