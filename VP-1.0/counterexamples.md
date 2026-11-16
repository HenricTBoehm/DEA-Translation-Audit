# Minimal counterexamples (independent verification of RP-1.0)

All of these are recomputed by `verify.py`. The check IDs refer to `results/verification-results.json`.

## CX-1 T3 / H_EJ "native (A-IDX)" does not survive effective control (A1)

Actors: d = scope, e = execution, j = acceptance. ctl(P) is the set of identities that P controls, reflexively (DEA p.8).

| Model | Control | DEA T3 | DEA H_EJ | Bertino A-IDX T3 | W&L-07 ∃ T3 | Bertino A-IDX H_EJ | Li principal-as-role |
|---|---|---|---|---|---|---|---|
| BM1 pairwise, no triple | P1{d,e}, P2{e,j}, P3{d,j} | permit | **forbid** | permit ✓ | permit ✓ | **permit ✗** | correct |
| BM2 triple, distinct nominal | P{d,e,j} | **forbid** | **forbid** | **permit ✗** | **permit ✗** | **permit ✗** | correct |
| BM3 triple, identical nominal | d = e = j | forbid | forbid | forbid ✓ | forbid ✓ | forbid ✓ | correct |
| BM4 d = j ≠ e | none | permit | permit | permit ✓ | permit ✓ | permit ✓ | correct |

- **Minimal witness: BM2.** It has one principal controlling three distinct identities.
- **Conclusion.** The A-IDX results establish preservation for nominal identity and task indexing only. They do not establish it under multi-principal control.
- **Existential form (A2).** BM4 also separates the correct existential reading of ⟨≠(∃{s_D,s_E}, s_J)⟩, which permits (d = j suffices to satisfy the disjunction), from the conjunctive misreading ⟨≠(s_D,s_J)⟩ ∧ ⟨≠(s_E,s_J)⟩, which forbids.

## CX-2 Role-hierarchy reductions on cyclic graphs (C4, B8)

- **Ctrl.** Edges o→p and p→o, active throughout, reading A.
  - `_rh_encoding` yields RH ∋ (r_p_t, r_o_t) and (r_o_t, r_p_t), so RH* is not antisymmetric.
  - Under Li p.10 ("RH* is a partial order") and RSL99 p.47 this is not an RBAC state.
  - The engines accept it silently.
  - Prevalence: 3,053 of 3,299 sampled general graphs.
- **NAP.** States {0, 1}, allowed edges 0→1 and 1→0, no goals, so DEA NAP holds.
  - The roles-as-states image has RH = {(r_0, r_1), (r_1, r_0)}.
  - Prevalence: 324 of the 26,262 MC-NAP models.
  - Under patch VP-1, NAP-B-LI-RH and NAP-B-RSL-RH fail on exactly these models.
- **Not affected.** Bertino Regime B, which uses recursive Datalog, agrees on all 6,598 cyclic and general samples (C4b).

## CX-3 Gap in the PRF-CTRL-WL-MONO proof as written (C5)

**The translation.** It respects A-STEP and LOCAL-REL as worded ("each control edge contributes only pairs containing its endpoints"):

- Edge x→y adds (y, z) to K, for every user z.
- Steps: s_E (role RE, held by a) ≺ s_J (role RJ, held by j).
- Constraint: ⟨¬K(∃{s_E, s_J}, s_E)⟩.

This constraint is violated exactly when both a and j have some controller.

| Model | DEA (A and B) | Translation | |
|---|---|---|---|
| m0: no edges | effective | permit | ✓ |
| m1: p→a in θ_E, p→j in θ_J | conflict | block | ✓ |
| m2: p→a in θ_E, o→j in θ_J | effective | block | ✗ |

**Effect on the proof.** The pair m0/m1 used in the proof does not refute this translation. The lemma needs every added pair to contain a fresh user, but LOCAL-REL does not imply that.

**Repair (VP-2).** Use the pair m1/m2 and add GENERICITY: an edge's contribution is invariant under renaming non-acting principals.
- The images then agree on {a, j}.
- By the lemma (C6), pairs on non-acting users cannot change the run.

The non-expressibility conclusion therefore holds under A-STEP + LOCAL-REL + GENERICITY.

## CX-4 CTRL-6b (C1; DEA-internal ambiguity, reproduced)

θ_E = {0, 1}, θ_J = {2, 3}. Edges: p→a at t ∈ {0, 1}, p→o only at t = 2, o→j only at t = 3.

| Reading | p ∈ Ctrl_θJ(j)? | ExecConflict |
|---|---|---|
| Pointwise closure | no | false |
| Closure of window union | yes | true |

The two readings disagree on 72 of the 16,807 MC-CTRL models (independent recount, C2). Every MC-CTRL graph is a DAG of depth ≤ 2 (C3).

## CX-5 N1: the A-MERGE count encoding over-grants (D3)

Events: `term W1 x β` · `reopen W2 x β (independent)` · `cont W2 x β` · `cont W2 x β`, with B = 1.

| Evaluator | Granted continuations |
|---|---|
| DEA (independent ledger) | event 2 |
| LED-A-BER-MERGE | events 2 and 3 ✗ |
| LED-B-BER | event 2 |

This refutes one encoding (FAILED-ENCODING). It does not establish non-expressibility.

## CX-6 PRF-LED4 witness is scoped to A-INST-LOCAL (D2)

| Model | Events | DEA verdict on W2's continuation |
|---|---|---|
| model 1 | `[cont W2 X β]` | grant |
| model 2 | `[cont W1 X β, cont W2 X β]` | deny |

The W2 projections are identical. Once cross-instance facts or merged instances are admitted, the projections differ and the obstruction disappears. All 386 LED-A-BER-INST failures involve at least two workflows (D4).

## CX-7 Case(x) identity is not fixed by DEA (D5)

Objects:

| Object | Content | Locator |
|---|---|---|
| x | c1 | L1 |
| y | c1 | L2 |
| z | c2 | L2 |

The harness merges x, y and z transitively, although x and z share neither content nor locator. DEA p.12 fixes neither transitivity nor precedence among content identity, locator and provenance. SameBlocker is supplied as a reviewed label.

## CX-8 NAP-3 invariance (B1)

An R1–R3-respecting element-local image separates m1 = `diag_only_p19` from m2 = `diag_goal_twin`. In it, steps are actions and the step-assignment role is fixed by whether the action's target is a goal. This refutes the invariance premise. It does **not** supply an R3-respecting translation that preserves NAP; that question is UNDETERMINED (B2).
