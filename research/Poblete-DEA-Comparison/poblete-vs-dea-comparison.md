# Poblete, Cravero & Diaz (2026) against DEA v0.3.4.3, ADR-001–003 and the pilot

| | |
|---|---|
| **Source** | `uploads/electronics-15-05135.pdf`, Electronics 15, 5135, CC-BY, published 5 Nov 2026 (SHA-256 `2b5cd104…4bcc`) |
| **Reference** | DEA v0.3.4.3 (frozen), DEA-ADR-001 (proposed) |
| **Classes** | CORRESPONDENCE: same distinction with comparable semantics. ANALOGY: similar function, but a different mechanism or strength. ABSENT. CONDITIONAL CONFLICT. UNDETERMINED. NOT EVIDENCE. |
| **Row-level crosswalk** | `crosswalk-poblete-dea.csv` (X1–X21, with pages on both sides) |
| **Executable check** | `poblete_adr001_check.py`, which writes `poblete-adr001-results.json` and reuses `../dea-adr-001/adr001_ctrl.py` |

## 1 Verdict

1. **Closest known instance of DEA arm R, not arm C.** The paper is an instance of the role-separated arm (DEA p.23) with human gates. The authors themselves describe the contracts as "not formally verified contracts or independently enforced access-control policies" (p.19, p.21). They also state that verification independence is only "procedural" (p.9, p.18). The executor's capability is "broader than its authorized scope" (p.10). It is not prior art for capability-enforced separation.
2. **The concepts overlap DEA.**
   - Capability ≠ Authority and Execution Success ≠ Verified State (p.2) correspond to DEA Eq. 35, Eq. 14/15 and Eq. 17 (pp.9–14).
   - The paper and its preprint predate v0.3.4.3: the preprint appeared on 29 Sep 2026 (p.32). It must therefore be cited.
   - DEA's contribution cannot rest on these distinctions. This is consistent with the RP-1.0 verification verdict (formal novelty NO-GO).
3. **Human acceptance is a conditional ExecConflict.** Under DEA Eq. 16, the Human Orchestrator's acceptance (Stage 8) is excluded if the human controlled the executor during execution. The paper does not report whether that was the case (p.9, p.30). See §3.
4. **No empirical evidence for or against DEA RQ1/RQ2.** There is no comparison arm, there is one synthetic case, and the same ground truth was used during refinement and for reporting (p.3, pp.30–31).

## 2 Main correspondences and differences

The full list is in the CSV. Selected rows:

| ID | Poblete (p.) | DEA (p.) | Class |
|---|---|---|---|
| X1 | Capability ≠ Authority (2) | Eq. 35; prompts descriptive (4, 14) | Concept CORRESPONDENCE, mechanism ANALOGY |
| X2 | Execution Success ≠ Verified State (2) | MayCompute ⇏ MayAccept, Eq. 17 (10) | CORRESPONDENCE |
| X4 | Authorize operation ≠ accept state (27) | Eq. 14 vs Eq. 15 (9) | CORRESPONDENCE |
| X5 | Execution contract (17, 20, 33) | A = (S,I,O,R,F), Eq. 19 (11) | Field CORRESPONDENCE, status ANALOGY |
| X7 | Read-only verification by the executor itself (17–18, 21) | IRR "without trusting the executor's narrative" (24) | ANALOGY |
| X9 | Human acceptance (18) | Eq. 16 + Ctrl (8, 10) | CONDITIONAL CONFLICT |
| X10 | Human scopes and accepts (17–18) | T3, Eq. 11 (9) | UNDETERMINED |
| X12 | Refinement after PARTIALLY_EFFECTIVE_FROZEN (21, 23) | Supplement / Progress, Eqs. 22–26 (11–12) | ANALOGY; ledger ABSENT |
| X15 | Same ground truth during refinement and reporting (3, 30, 36) | No read-access rule for the reference (9, 11, 16) | ABSENT, candidate G-P1 |
| X17 | Executor capability exceeds scope (10) | Arm R definition (23) | CORRESPONDENCE |

## 3 ADR-001 test: the Poblete topology as control models

**Mapping:**
- p = Human Orchestrator.
- j = the human's acceptance identity, bound to p by mutual identity edges.
- a = Data Engineering Agent, which executes in Stage 5 and verifies in Stage 7.
- o = Data Expert Agent.
- θ_E corresponds to Stages 5–6.

Which edges exist is **not reported**, so each reading below is an assumption.

| Reading | Edge assumption | ExecConflict (C/causal) | Same result under all 9 variant/window combinations? |
|---|---|---|---|
| PB-1 | Human can alter the executor's credentials, contract or context during execution | **yes**: human acceptance excluded | yes |
| PB-2 | Only the Stage-4 authorization, as an independently issued pre-stage manifest (DEA p.8) | no | yes |
| PB-3 | Human injects context after the seal (Stage 6), before verification; object x | no | yes |
| PB-3v | As PB-3; the object is the Stage-7 verification report | **yes** | no: only the causal windows block |
| PB-4 | Planner output copied unchecked into the executor (Fig. 8) | no | yes |

**Findings:**
- **The paper does not discriminate between the ADR-001 semantics.** The outcome depends on whether a control edge *exists*, not on its timing. As a test case it confirms neither A, B nor C.
- **New open point for ADR-001 (proposed O8): uncertainty about whether an edge exists.** D-5 covers only uncertain *timing*. DEA says control "must be established from credentials, ACLs, … records" and that trusting the TCB "is an explicit assumption, not evidence of an absent control edge" (p.8–9). This points toward fail-closed treatment of unknown edges, but it is not decided. Poblete's sixth limitation, that "explicit identity and authorization mechanisms" are missing (p.30), is exactly that situation.
- **Verification artifacts need their own seal (PB-3v).** If the executor also produces the verification evidence, the conflict guard has to be applied per object, including the verification report. This feeds ADR-003.
- **Unchecked context relay is not a control problem (PB-4).** Ctrl does not catch it. It is an evidence-status problem and belongs in ADR-003.

## 4 Inputs for ADR-002 and ADR-003 (analogies only, no DEA change)

- **ADR-002.** The repeated-execution failure (pp.11–12, p.34) and the frozen-baseline / checkpoint-identity remedy motivate idempotent, uniquely identified continuations. They work at a different level (data step vs ledger). The Refinement cycle has no budget, no Case(x) and no SameBlocker (X12).
- **ADR-003: acceptance criteria vs operational completion.** Poblete places acceptance thresholds (F1 ≥ 0.95, Precision ≥ 0.90, Recall > 0.8784; p.24) inside the *execution* contract. DEA keeps G_M as an operational completion predicate, "not a judgment of scientific sufficiency" (p.11). The paper is a concrete case of the mixture that ADR-003 must keep apart.
- **ADR-003: authorized ≠ sufficient.** The aggregate thresholds were met, but "these aggregate metrics alone do not independently establish compliance with every issue-specific non-regression condition" (p.24). The paper does not say whether Refinement 2 was formally accepted (UNDETERMINED). If it was, it would fall in the numerator of DEA's UAR (Eq. 70, p.24): an authorized acceptance without sufficient evidence.
- **ADR-003: evidence status of inputs.** REPORTED / VERIFIED / FROZEN (p.29) has no DEA predicate for the epistemic status of transferred claims (X11, X16).
- **Candidate gap G-P1: read access to the adjudication reference.** DEA protects the reference against mutation but, as far as I found, does not regulate D/E read access to it across supplementation cycles. Poblete shows the effect: the result is "not a held-out estimate" (p.36). This is not established: the search was keyword-based plus a reading of pp.9–16 and 25–26.

## 5 Use in the pilot

- **Use the paper as a strong arm-R baseline.** The contract templates in App. A (pp.33–34) can serve as the arm-R prompts, so that R is not a straw man (DEA p.23, H2).
- **Preregister the failure families in App. B (pp.34–35) as task or perturbation families:**
  - repeated execution;
  - grain mismatch;
  - rule-mapping drift;
  - premature remediation;
  - cross-rule regression;
  - unverified context relay;
  - state-authority ambiguity.
- **Hold the human's role constant across M/R/C** (DEA p.23 "hold constant"). In Poblete the human both gates and accepts, which would otherwise confound the arms.
- **What the paper does not supply.** Its metrics do not give UTR, UAR, wrongly blocked decisions or IRR. F1 corresponds at most to Scientific Utility. The pilot also needs:
  - a held-out reference standard that D/E cannot access;
  - frozen model versions. Poblete could not report them (p.32).

## 6 Limitations

- I did not read the accompanying experience report (preprints.org 202609.2499), which contains CP13/CP7 and the provenance records (p.32).
- I did not read the closer prior art the paper cites: [7] Wang et al. (runtime policy enforcement for MCP), [8] Jorgensen & Ma (bounded autonomy) and [10] LATTICE (a "governance-first architecture … policy-based authorization controls", p.5). **LATTICE in particular should go into the prior-art audit as a potential arm-C precedent.**
- The UML figures were read from the text layer only.
- PB-1 to PB-4 are assumption-based readings, not reconstructions of the experiment.
