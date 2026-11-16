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
