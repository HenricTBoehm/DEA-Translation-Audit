# Revised contribution assessment: DEA v0.3.4.3 against the inspected prior art

The four dimensions are assessed independently. A positive finding in one does not transfer to another.

## 1 Formal expressiveness: **no demonstrated novelty**

Every tested DEA construct is expressible in at least one inspected formalism, natively or with a declared extension. Most of these encodings are restatements; the role-hierarchy ones are genuine reductions.

| DEA construct | Closest directly supported prior formalism (primary) | Status |
|---|---|---|
| T3 | Bertino `cannot_dou` with two execution atoms; W&L-07 ∃-entailment (Def 2 form 2) | native (A-IDX) |
| H_EJ + AuthorizedForDisposition | Bertino role/task + `cannot_dou`; W&L-07 ≠-entailment | native (A-IDX) |
| H_DE^ext | Bertino `cannot_dou` with `count` (Tab. IV) | native |
| ExecConflict with transitive Ctrl | RBAC role-hierarchy inheritance: Li RH* (p.10), RSL99 `roles*` (Fig. 1) | reduction (principal-as-role) |
| Temporally changing Ctrl_θ | time-indexed copies of the above; either reading | reduction. The DEA reading is itself unresolved |
| Goal-relative NAP | reachability: Li RH* / RSL99 `roles*` (roles-as-states); WSP label reduction; Basin + goal termination | reduction |
| Case/blocker ledger | Bertino C6-style count constraints (within an instance) + persistent store | restatement (B) |

**What remains formally DEA-specific.** The definitions do not appear verbatim in the sources:
- a disposition-indexed adjudication guard;
- a goal-relative non-admissibility predicate with a three-valued diagnostic discipline;
- a per-ledger bound B(1 + r) across workflow instances.

Under RP-1.0, "not verbatim in the sources" is not expressive novelty.

**Bounded negative results:**
- Ctrl is not expressible in W&L-07 under A-STEP + LOCAL-REL.
- The ledger is not expressible in Bertino under per-instance locality.
- NAP is not expressible by r-local translations.

These show that the specific *combination* of transitive, historical control with cross-instance persistence exceeds each prior formalism's **native** fragment. The combination is not beyond established machinery: stratified Datalog with recursion, or RBAC with hierarchies, covers it.

**Wang & Li 2010 is unverified.** Its resiliency and satisfiability results may cover further ground. No claim against it can be made in either direction.

## 2 Domain-specific epistemic semantics: **defensible as a modelling contribution**

The following are domain semantics, not formal expressiveness. None of the inspected sources addresses scientific adjudication.
- Typed separation of operational permission from adjudicative validity (Eqs. 14–15).
- Placement vs disposition.
- Hold and Supplement as adjudicative dispositions governed by H_EJ.
- Case identity from content, locator and provenance.
- NAP distinguished from budget exhaustion.
- "Verified NAP" kept separate from inconclusive search.

The contribution is a vocabulary and typing discipline for research governance. It must not be presented as a new authorization logic.

## 3 Governance and enforcement methodology: **defensible with qualifications**

These are design commitments consistent with established practice: separation of control-graph attribution from nominal role names, non-exemption of the TCB, independent reopening, and binding historical control versions to records.

Qualifications:
- The CTRL-6b ambiguity must be resolved in a future version before the control rule can be implemented unambiguously.
- `Case(x)` equivalence relies on a reviewed equivalence (residual A7).

## 4 Empirical effectiveness: **no evidence**

v0.3.4.3 announces a forthcoming pilot (p.22). No deployment data, user study or incident comparison exists. No effectiveness claim is defensible.

## 5 Narrowest defensible claim

> DEA is a domain-specific governance architecture for scientific adjudication. It composes established authorization machinery — entailment and SoD constraints, role-hierarchy closure, stratified rule bases with aggregates, reachability — into a typed separation of operational permission from adjudicative validity, with explicit control-graph attribution and a cross-workflow continuation ledger. Its formal constructs are expressible in, or reducible to, prior formalisms; its contribution is the domain semantics and governance design, not new formal expressive power.

## 6 Verdicts

### A. Audit quality: **CONDITIONAL GO**

The package is reproducible (clean-room verified, integrity hard-fail) and source-grounded for 3 of 4 primary papers. The target engines are independent of the DEA evaluator. Every non-expressibility claim states its translation class.

Blockers:
1. Wang & Li 2010 is not inspected. *Minimum action:* obtain the article and re-run the W&L cells.
2. There is one auditor; the engines have not been reviewed by a second person. *Minimum action:* a second reviewer checks `engines/r2bac.py` and `engines/bertino.py` against the cited definitions, or writes an alternative implementation.
3. The Bertino Regime A locality argument is conditional on Hella et al. 2001. *Minimum action:* verify the theorem's scope, or keep the cell labelled conditional.

### B. DEA contribution: **CONDITIONAL GO** for dimensions 2–3; **NO-GO** for any claim of formal novelty or empirical effectiveness

Conditions:
1. State the contribution as in §5.
2. Resolve the CTRL-6b reading in a future version; v0.3.4.3 itself is not edited.
3. Withhold comparative claims against Wang & Li 2010 until the source is inspected.
4. Make no effectiveness claim before the pilot reports.
