# DEA v0.3.4.3: adversarial translation audit against workflow-authorization prior art

**Baseline:** DEA v0.3.4.3 Architecture Closure Candidate, 15 Nov 2026. The file was read-only throughout (SHA-256 `51a2553e…8c97c33`, checked on every run).
**Protocol:** `00-translation-protocol.md`, frozen before any test was written (SHA `c8d7beb0…6752006`). The test script refuses to run if the protocol has changed.
**Tests:** `dea-v0343-translation-tests.py`, standard library only, about 1.3 s. Results are in `dea-v0343-translation-results.json`.
**Page citations:** DEA pages are printed pages. For Bertino, printed page = PDF page + 64. For Li et al., printed page = PDF page. W&L-07 pages are preprint pages.

## 1 Verdict in brief

- **Formal novelty:** none demonstrated. Every priority construct has a Regime B translation that preserves outcomes in both directions on every model class tested. The targets are Bertino et al.'s logic program extended with declared auxiliary predicates and positive recursion, Wang & Li's model with user-defined relations, and Basin's CSP. That result is finite evidence, not a general equivalence proof. The machinery DEA needs (stratified Datalog, user-defined binary relations, trace reachability) all exists in the prior art.
- **Regime A (native vocabulary) fails** for:
  - disposition-specific authorization;
  - per-object binding of H_EJ in Bertino;
  - time-indexed control;
  - the cross-instance ledger;
  - goal-relative NAP.

  Three of these failures are backed by invariance arguments (EJ-7, NAP-3, LED-4). They are **not-expressible results for native vocabulary only**. They show that the prior authors did not *state* these semantics. They do not show that the semantics need new logic.
- **Already native:**
  - T3 in W&L (form-2 constraint);
  - transition binding (instance-local predicates);
  - the single-output, all-disposition ExecConflict guard in Bertino;
  - MayCompute ⇏ MayAccept (in every target).
- **What survives** is domain-specific semantics plus governance methodology (§7). Empirical effectiveness is untested.

## 2 Source status

| Source | Status | Effect |
|---|---|---|
| Bertino, Ferrari & Atluri 1999 | original PDF, read | full use |
| Li, Tripunitara & Bizri 2007 | author PDF, read | full use |
| **Wang & Li 2010 (TISSEC)** | **not in workspace** | all cells UNDETERMINED-SOURCE; ESORICS'07 preliminary version (W&L-07) used as a *labelled proxy* |
| **Ahn & Sandhu 1999 (RSL99)** | **not in workspace** | all cells UNDETERMINED-SOURCE; no tests |
| Basin, Burri & Karjoth (obstruction-free, extended version) | PDF in `uploads/`, read | additional comparator |
| Jonscher 1994; Nash & Poland 1990; Warner & Atluri 2006; Clark & Wilson 1987 | secondary only | never used to classify |

Detail, hashes and page maps are in `dea-v0343-sources.md`.

The v0.3.4.3 reference list cites Clark–Wilson. It cites **none** of Bertino, Li et al., Wang & Li, Basin or Crampton. That gap is a citation obligation whatever the verdict.

## 3 Translation definitions (abridged; exact code in the test script)

### 3.1 H_EJ, AuthorizedForDisposition, ExecConflict (DEA Eq. 12, 16, 32; p.9–10, 14)

| Target | Regime | Translation |
|---|---|---|
| Bertino | A | Tasks T_exec and T_adj; one activation per output. `user(u,T_adj)` holds iff u holds any grant (Table I, p.73). Rule: `cannot_dou(U,T_adj) ← executeu(U,T_exec,K)` (Table III, p.75; Def 4.3). |
| Bertino | B | Adds aux `obj(K,X)`, `granted(U,X,S)` and `assigned(U,X,S)`. `panic ← assigned(U,X,S), not granted(U,X,S)`. `panic ← assigned(U,X,_), obj(K,X), executeu(U,T_exec,K)`. Read as **detection**, by R4. |
| W&L-07 | A | Steps s_exec_k and s_adj_k per output. SA is derived from the grants on k. C = {≠(s_adj_k, s_exec_k)} (Def 2, p.6). |
| Li 2007 | A | SSoD ⟨{p_exec, p_adj}, 2⟩ evaluated on the current UA/PA (Notation 1, p.9; Def 3, p.10). |

### 3.2 NAP (Eq. 46–47, p.17–18)

| Target | Translation |
|---|---|
| WSP-A1 | S = all carrier actions; NAP_T := unsatisfiable (Defs 3–4, p.7) |
| WSP-A2 | S = authorized actions; NAP_T := S = ∅ |
| Bertino B | `reach(Y) ← reach(X), edge(X,A,Y), allowed(A)`; `nap ← not goal_reached` |
| Basin A | NAP_T := an obstructed reachable trace exists (Def 7, p.14) |
| Basin B | Goal states terminate (✓); NAP_T := no authorized ✓-trace |
| WSP reduction | users := edges, slots := 1..\|S\|, ρ_chain. **Violates R3**; reported, not counted. |

### 3.3 Ctrl_θ (p.8–9)

DEA (reading A-T): Ctrl_θ(p,a) holds iff a direct-control path p→*a exists at some instant inside θ. ExecConflict holds iff some p has Ctrl_θJ(p,j) ∧ Ctrl_θE(p,a).

| Target | Translation |
|---|---|
| W&L A snapshot | ρ_co is taken from the configuration at check time (W&L p.7 runtime re-check) |
| W&L A compiled | B := the DEA co-control relation. Allowed by R2's exception, because W&L Def 1 takes B as given. |
| Bertino A | Pseudo-role Ctrl_p, with `belong/2` fixed at instance start |
| Bertino B | Aux `ctrl_edge(P,A,T)` with positive recursive `ctrl*` per instant |
| Li A | Users are atomic |

### 3.4 Ledger (p.12–13)

| Target | Translation |
|---|---|
| Bertino A | `panic ← count(success(T_cont,K),n), n>B` per instance (pattern of C6/R6,1, p.72, p.78) |
| W&L A | No counting form exists |
| Bertino B | Persistent aux `ledger_count(C,β,N)`, `case_of`, `closed`, with independent reopen via `ctrl*` |

### 3.5 T3 and H_DE^ext (Eq. 11, 13, 31, 33)

| Construct | Target / regime | Translation |
|---|---|---|
| T3 | W&L A | ⟨≠(∃{s_scope, s_exec_k}, s_acc_k)⟩, form 2 of Def 2 |
| T3 | Bertino A | `cannot_dou(U,T_acc) ← executeu(U,T_scope,_), executeu(U,T_exec,K)` |
| H_DE^ext | W&L B | Pseudo-user ν authorized for the gate; native constraint ⟨ρ*(∃{s_gate, s_scope}, s_ext)⟩ with ρ*(u,v) ≡ u≠v ∧ u≠ν |

## 4 Results

Columns: n = models; Fwd = DEA-permitted ⇒ target-permitted; Bwd = target-permitted ⇒ DEA-permitted.

| ID | Construct | Target | Reg. | n | Fwd | Bwd |
|---|---|---|---|---|---|---|
| EJ-1 | H_EJ, uniform grants | Bertino | A | 162 | **FAIL 40** | ok |
| EJ-2 | + disposition-specific grants | Bertino | A | 324 | **FAIL 40** | **FAIL 116** |
| EJ-3 | Eq.16 complete | Bertino | B | 324 | ok | ok |
| EJ-4 | H_EJ, uniform grants | W&L-07 | A | 162 | ok | ok |
| EJ-5 | disposition-specific grants | W&L-07 | A | 324 | ok | **FAIL 140** |
| EJ-6 | ExecConflict vs SSoD | Li | A | 648 | **FAIL 128** | **FAIL 94** |
| EJ-8 | single output, all dispositions | Bertino | A | 36 | ok | ok |
| NAP-1 | NAP | WSP (W&L-07) | A1 | 26,262 | **FAIL 26** | **FAIL 13,818** |
| NAP-2 | NAP | WSP | A2 | 26,262 | **FAIL 4,202** | **FAIL 8,200** |
| NAP-4 | NAP | WSP reduction | R3-viol. | 26,262 | ok | ok |
| NAP-5 | NAP | Bertino | B | 26,262 | ok | ok |
| NAP-6 | NAP | Basin obstruction | A | 26,262 | **FAIL 334** | **FAIL 13,510** |
| NAP-7 | NAP | Basin CSP | B | 26,262 | ok | ok |
| CTRL-1 | Ctrl_θ | W&L-07 snapshot | A | 7,776 | **FAIL 592** | **FAIL 2,592** |
| CTRL-2 | Ctrl_θ | W&L-07, B compiled | A* | 7,776 | ok | ok |
| CTRL-3 | Ctrl_θ | Bertino pseudo-roles | A | 7,776 | **FAIL 1,530** | **FAIL 1,530** |
| CTRL-4 | Ctrl_θ | Bertino | B | 7,776 | ok | ok |
| CTRL-5 | Ctrl_θ | Li | A | 7,776 | ok | **FAIL 3,888** |
| LED-1 | ledger | Bertino | A | 2,954 | **FAIL 976** | **FAIL 312** |
| LED-2 | ledger | W&L-07 | A | 2,954 | ok | **FAIL 756** |
| LED-3 | ledger | Bertino | B | 2,954 | ok | ok |
| T3-1 | T3 | Bertino | A | 243 | **FAIL 36** | ok |
| T3-2 | T3 | W&L-07 | A | 243 | ok | ok |
| T3-3 | T3 | Bertino | B | 243 | ok | ok |
| DE-1 | H_DE^ext, mandatory gate | Bertino / W&L-07 | A | 12 | **FAIL 6** | ok |
| DE-2 | H_DE^ext, no gate | Bertino / W&L-07 | A | 12 | ok | **FAIL 4** |
| DE-3 | H_DE^ext | W&L-07 | B | 12 | ok | ok |

\*A with B compiled outside the formalism; see §5.3.

## 5 Minimal countermodels (verbatim from the JSON)

### 5.1 H_EJ and validity/permission

| Test | Direction | Model | Outcome |
|---|---|---|---|
| EJ-1/2 | fwd | exec = (a,b); adj = (a,a); both Accept; a granted on both outputs | DEA: a may adjudicate x₁ (b's output). Bertino: `cannot_dou(a,T_adj)` blocks every adjudication by a. `cannot_dou/2` has no activation argument (p.75), so per-object SoD inside one instance needs `obj/2`. |
| EJ-2/5 | bwd | exec = a; adj = b; grant (b, x₀, **Hold**); assignment **Accept** | DEA: not effective. Target: effective. Neither Bertino roles nor W&L SA take a disposition argument. |
| EJ-6 | bwd | a executed x₀; a's p_exec is then revoked; a adjudicates | Li's SSoD is satisfied, because the state is safe. DEA blocks, because ExecConflict is historical. This is Li's own revoke/reassign example (p.3), which Li assigns to *dynamic/object* SoD and leaves out of scope. |

**Invariance (EJ-7).** Two models differ only in grant(Hold) versus grant(Accept). Every Regime A image of them is identical, but the DEA outcomes differ. So AuthorizedForDisposition is **NOT-EXPRESSIBLE in Regime A** for Bertino and W&L-07. Reading `success`/`abort` as Accept/Reject is barred, because Bertino fn. 4 on p.72 defines abort as an error.

**EJ-8.** For one output, the v0.3.4.3 all-disposition guard *is* natively expressible in Bertino. This is a consequence of the v0.3.4.3 strengthening (p.10): under v0.3.4.2's Accept-only guard, self-Hold separated the two.

### 5.2 NAP

| Test | Direction | Model | Outcome |
|---|---|---|---|
| NAP-1 | bwd | one state, which is the goal; an unauthorized self-loop | DEA: not NAP (the empty path reaches the goal). WSP: unsatisfiable. |
| NAP-1 | fwd | one state, no edges, no goal | DEA: NAP. WSP with S = ∅: vacuously satisfiable. |

**Invariance (NAP-3).** Take the diagnosis-only countermodel of DEA p.19 (`diag`: 0→0, goal {1}) and its twin (`diag`: 0→1). Their step set, authorization and constraint set are equal, so their WSP images are identical, but the NAP verdicts differ. NAP is therefore **NOT-EXPRESSIBLE in WSP/R2BAC under R3**: WSP has no state, effect or goal symbol.

NAP-4 shows the mismatch is one of *sorts*, not of power. Once users are repurposed as transitions, NAP reduces exactly to WSP-style planning on all 26,262 models.

**NAP-6.** Basin's obstruction is a different property. It is universal over control-flow options, whereas NAP is existential over goal paths.

**NAP-8.** No compared formalism has a three-valued verdict (witness / verified NAP / undetermined). All of them decide finite instances. "Undetermined" matters only for DEA's open or hybrid carriers.

### 5.3 Ctrl_θ (windows θE = [0,1], θJ = [2,3], check at t = 3)

| Test | Direction | Model | Outcome |
|---|---|---|---|
| CTRL-1 | bwd | o→a only in θE; o→j in θJ | DEA: conflict. The snapshot at t=3 misses it, because o no longer controls a. Control relinquished after execution. |
| CTRL-1 | fwd | o→a and o→j both only in θJ | DEA: no conflict, because o acquired control of a after a executed. The snapshot blocks. |
| CTRL-3 | — | — | Bertino's `belong/2` is specification-time, so it fails both ways. |
| CTRL-5 | — | — | Li has no relation between users, so it misses every collapse caused by a common controller. |

**CTRL-2.** Supplying W&L's user-defined relation B as the DEA co-control relation preserves outcomes. This is the decisive point for novelty: W&L Def 1 *expects* such relations to be supplied from outside the model. DEA's contribution is *which* relation to compile (credential use, artifact or criterion writes, capability changes, transitive closure, TCB not exempt). That is a domain specification, not a new constraint form.

**DEA-internal ambiguity (CTRL-6b, hand-built boundary case).** Take p→o only at t=2, o→j only at t=3, and p→a in θE:
- with per-instant closure, there is **no conflict**;
- with closure over the union of the window, there **is a conflict**.

v0.3.4.3 p.8 does not say when the closure is taken. Inside MC-CTRL no such case arose (CTRL-6 is negative), because MC-CTRL had no "θJ-late only" interval.

**Regression G2 S1–S13.** Every scenario matches its v0.3.4.3 expectation. The only divergence from v0.3.4.2 intent is **S8 (TCB admin without a role)**, which is now an H_EJ conflict because TCB principals are not exempt (p.9). It is reported, not reconciled. All G2 scenarios are time-invariant, so they cannot tell snapshot translations from history translations.

### 5.4 Ledger (B = 1)

| Test | Direction | Model | Outcome |
|---|---|---|---|
| LED-1 | fwd | two continuations in W1 on (X,β) and (X,γ) | DEA grants both, because they are separate ledgers. The per-instance counter refuses the second. |
| LED-1 | bwd | continuations on (X,β) in W1, then in W2 | DEA refuses the second. Bertino's per-instance count grants it. |

**Invariance (LED-4).** Bertino's execution predicates are instance-local (C6 "within the same workflow", p.72). So the ledger is **NOT-EXPRESSIBLE in Bertino Regime A**.

The closest prior formalism, Warner & Atluri 2006 (inter-instance constraints), is known only second-hand via W&L-07 p.15. Against that work the result is **UNDETERMINED**.

Regression G4, grants under DEA vs Bertino A:

| Scenario | DEA | Bertino A |
|---|---|---|
| A1 | 1 | 5 |
| A3 | 1 | 1 |
| A4 | 1 | 4 |
| A6 | 1 | 4 |
| A8 | 1 | 2 |
| L1–L3 | 2 | 2 |
| **A7** | **4** | **4** |

A7 is a DEA residual, not a translation issue: Case(x) itself misses near-duplicates.

### 5.5 T3 and H_DE^ext

- **T3-1 fwd:** scope a; exec (a,b); acc (a,a). DEA permits a to accept x₁. Bertino's instance-level rule blocks it.
- **T3-2:** W&L form 2, ⟨≠(∃{scope, exec_k}, acc_k)⟩, is exactly ¬T3_k. T3 is **native** in W&L.
- **T3-4:** T3 = DefineScope ∧ H_EJ. Eq. (31) is entailed by Eq. (32), so T3 adds no constraint content beyond H_EJ. The paper itself says Eq. (16) is stronger (p.14).
- **T3-5:** binding to a single transition (DEA's θ₁/θ₂/θ₃ example, p.9) is native through instance-local semantics.
- **DE-1/2:** a fixed gate step over-restricts; omitting the gate under-restricts. **DE-3:** one pseudo-user ν plus a native ∃-form constraint preserves the outcome.

## 6 Classification

| DEA construct | Bertino 1999 | W&L (07 proxy; 2010 undetermined) | Li 2007 | RSL99 | Basin |
|---|---|---|---|---|---|
| H_EJ, per object, uniform grants | EXT (EJ-1/3) | NATIVE (EJ-4) | NOT-EXPR-A: static SSoD is a different objective (EJ-6; Li p.3, p.6); EXT untested | UNDET-SRC | n/t |
| AuthorizedForDisposition | NOT-EXPR-A (EJ-7) → EXT (EJ-3) | NOT-EXPR-A (EJ-7); EXT expected, not run | UNDET | UNDET-SRC | n/t |
| ExecConflict, single output, all Σ_adj | NATIVE (EJ-8) | NATIVE | NOT-EXPR-A | UNDET-SRC | n/t |
| MayCompute ⇏ MayAccept | NATIVE (EJ-9) | NATIVE | NATIVE; RH caveat | UNDET-SRC | — |
| Goal-relative NAP | NOT-EXPR-A → EXT (NAP-5) | NOT-EXPR under R3 (NAP-3) | n/a | UNDET-SRC | NOT-EXPR-A (NAP-6) → EXT (NAP-7) |
| Three-valued NAP diagnosis | not present | not present | not present | UNDET-SRC | not present |
| Ctrl_θ, time-indexed, transitive | NOT-EXPR-A (CTRL-3) → EXT (CTRL-4) | snapshot fails (CTRL-1); NATIVE with compiled B (CTRL-2) | NOT-EXPR-A (CTRL-5) | UNDET-SRC | n/t |
| Case/blocker ledger | NOT-EXPR-A (LED-4) → EXT (LED-3) | NOT-EXPR-A (no counting form) | n/a | UNDET-SRC | n/t |
| T3, transition-bound | EXT (T3-1/3); binding NATIVE | NATIVE (T3-2) | n/a | UNDET-SRC | n/t |
| H_DE^ext | EXT | EXT (DE-3) | n/a | UNDET-SRC | n/t |
| Σ_op / Σ_adj typing, P(x) ∉ Σ_adj | EXT, trivially (two task sorts) | EXT | n/a | UNDET-SRC | — |

Abbreviations:
- **NATIVE:** EXPRESSIBLE-NATIVE.
- **EXT:** EXPRESSIBLE-EXTENSION.
- **NOT-EXPR-A:** not expressible in Regime A, by invariance or semantic argument. Never a claim about Regime B.
- **UNDET:** UNDETERMINED. **UNDET-SRC:** undetermined because the source is not available.
- **n/t:** not tested.

**Reverse direction (REV-1).** Several prior constructs have no DEA counterpart:
- BoD ⟨=(s1,s2)⟩ (W&L-07);
- cardinality C1 and per-activation SoD C5 (Bertino p.72);
- k-n SSoD (Li Notation 1).

DEA is a fixed set of invariants. With respect to these targets it is a fragment, not a constraint language.

## 7 Novelty, split four ways

| Dimension | Finding |
|---|---|
| **Formal novelty** | **Not demonstrated.** Everything is Regime B expressible with stratified Datalog, user-defined relations or CSP trace properties. The NOT-EXPR-A results are vocabulary gaps, not new logic. |
| **Domain-specific semantics** | Candidates: (i) an epistemic typing of outcomes (Σ_adj vs Σ_op) with an all-disposition adjudicative guard and P(x) ∉ Σ_adj; (ii) a concrete operational Ctrl criterion for AI-assisted pipelines (credentials, artifact or criterion writes, capability changes, transitivity, TCB not exempt), which is the content of the relation W&L leave external; (iii) ledger identity keyed on content and provenance, not on workflow instance (pending Warner & Atluri 2006 and RSL99); (iv) goal-relative NAP relative to a current manifest, with NAP ⇏ Reject. |
| **Governance methodology** | NAP is diagnostic, not adjudicative. The executor reports and does not adjudicate. Reopening needs independent authority. Diagnosis is three-valued. The audit discipline is falsification-first, with residuals declared (App. C). None of these is a formal result. |
| **Empirical effectiveness** | **Untested.** Only the prospective M/R/C design exists. No evidence that DEA reduces failures in practice. |

## 8 Limitations

1. **Missing sources.** Wang & Li 2010 and RSL99 are absent. RSL99 is the most likely source of prior art for conflicting users, roles and permissions and for prerequisite constraints. Every RSL99 cell is open.
2. **Proxy.** W&L-07 is not W&L 2010. The journal version may add features (e.g. resiliency, extended constraint forms) that change some classifications.
3. **Finite classes.** All "preserved" results hold on enumerated classes only, with at most 3 users, 2 outputs, 2 states and 3 events. None is a general equivalence proof.
4. **Regime B is cheap.** In EJ-3, NAP-5, CTRL-4, LED-3 and T3-3 the auxiliary vocabulary nearly mirrors the DEA definitions. These show that the *machinery* suffices. They do not show that prior authors *anticipated* the semantics.
5. **Prevention vs detection.** Bertino Regime B uses `panic`, which is detection (R4). Prevention would need planning-time `cannot_dou` with `obj/2`, which was not separately tested.
6. **DEA ambiguities found.**
   - CTRL-6b: the timing of the closure is unstated.
   - "During the stage" is read as A-T; that reading is declared, not taken from the text.
   - A7: Case(x) misses near-duplicates (a known residual).
7. **Baseline divergence.** S8 changed from compliant (v0.3.4.2 intent) to conflict (v0.3.4.3).
8. **Secondary-only items.** Jonscher 1994 (author/referee activation conflict, cited by Bertino p.68), Nash & Poland, Warner & Atluri and Clark–Wilson E4 have not been inspected.
9. **Translation design.** All translations were designed by a single auditor. Another translator might find Regime A encodings that these invariance arguments do not cover. The arguments cover all translations satisfying R1–R3, but R3 itself is a modelling choice.

## 9 Narrowest defensible contribution claim

> DEA v0.3.4.3 does not introduce new formal machinery. Each of its priority invariants is expressible, on the finite classes tested, as a conservative extension of established workflow-authorization formalisms: Bertino et al. 1999 with auxiliary predicates, Wang & Li's user-defined relations, and Basin et al.'s CSP processes. T3 and transition binding are native. Its contribution is a *domain instantiation and governance discipline* for AI-assisted execution and adjudication:
>
> - a specified operational effective-control relation whose co-control closure supplies the conflict relation that prior models take as given;
> - an epistemic/operational outcome typing with an all-disposition adjudicative separation guard;
> - a case- and blocker-keyed supplementation budget that persists across workflow instances;
> - a goal-relative non-admissibility diagnosis that is explicitly non-adjudicative and three-valued.
>
> Its practical effectiveness is untested.

The two cross-instance points (ledger, independent reopening) stay provisional until RSL99, Wang & Li 2010 and Warner & Atluri 2006 have been inspected.

## 10 Open questions

1. Please upload RSL99 and Wang & Li 2010 so the UNDET-SRC cells can be closed.
2. DEA must state the closure timing for Ctrl_θ: per instant, or over the window union (CTRL-6b).
3. Is the TCB non-exemption (the S8 change) intended for administrators who hold no workflow role?
4. Should DEA claim T3 at all, given T3-4? It is a label for a subset of H_EJ.
