# Candidate research design: stability is not authority

## Scope and relation to DEA

This proposal is **not** a replacement for HistoryClosed or P-01. HR-1 bounds the residual effective-control state before the audit window. A separate robustness probe considers how uncertain historical facts affect the *substantive* outcome of the approved decision procedure. P-01 remains responsible for versioned mandatory rubric closure, authenticated event admission and the governance gate.

## Formal candidates (subject to adversarial review)

Fix an exact sealed output x, a governed attempt, the authorized evaluation procedure d, policy version, dependency-role pins and evaluation/commit scope s. Let E be verified evidence; let W_s(E) be a **nonempty** set of concrete histories/environments compatible with E, the fixed procedure, all protected versions and permitted transitions. A world violating a sealed mandatory dependency is not an admissible world for this attempt: that contradiction is handled by the control/input gate. Alternative rubric versions can be studied **only** in an explicitly labeled counterfactual sensitivity analysis, not passed off as compliant histories.

For w in W_s(E), d_s(w) is the substantive decision outcome; define PossibleOutcomes_s(E) = {d_s(w) : w in W_s(E)}.

DecisionStable_s(E) iff W_s(E) != empty AND cardinality(PossibleOutcomes_s(E)) = 1.

The statement above is **relative to W_s(E)**. A universal real-world claim requires a justified coverage certificate showing all relevant admissible worlds are represented or safely overapproximated. If world coverage is not justified, classify the result as SAMPLED_STABLE or STABILITY_UNDETERMINED; NEVER CERTIFIED_STABLE. An empty set or inconsistent scope is not vacuous stability.

If a sound abstract interpretation returns an overapproximation O_plus(E) of PossibleOutcomes, then cardinality(O_plus(E)) = 1 implies a stable outcome **conditional on soundness**, while a larger set may be conservative/inconclusive.

## Non-override law

Let G(E) be the separate P-01/HR-1 governance result and T(E) a stability result. An operational admission decision MUST NOT be obtained by replacing G with T.

- G = CONFLICT: block irrespective of T.
- G = MODEL_INVALID: reject input irrespective of T.
- G = UNDETERMINED: no governance clearance irrespective of T, even if T = CERTIFIED_STABLE.
- G = NO_CONFLICT_ESTABLISHED: merely passes the control gate; actual disposition still needs independent authority, evidence sufficiency and substantive checks.

Stability can help prioritize evidence gathering. It never reclassifies an authenticated conflict as non-conflict.

## Distinctions to preserve

- Past causal influence is broader than operational effective control. Reading a rubric is not by itself control.
- Historical **possible** control is not proof of actual manipulation.
- A control certificate is about provenance/authority, not scientific truth.
- A finite Monte Carlo sample does not prove universal stability or certificate soundness.
- Probabilistic risk tolerance, if studied, is a separate non-formal policy and cannot justify formal CLEAR.
- Missing history/certificate is an epistemic gap, not a positive conflict witness.

## Hypotheses, not results

H1: For at least some governance-UNDETERMINED cases, stability analysis distinguishes outcome-sensitive from outcome-insensitive missing history.
H2: This classification reduces unnecessary historical evidence requests without generating additional false governance clearance.
H3: The extra cost of analysis is measurable and may outweigh its diagnostic benefit.

All three require tests; none is adopted.
