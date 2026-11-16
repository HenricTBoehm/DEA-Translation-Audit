# DEA-ADR-001: Temporal Effective Control and Attribution

| | |
|---|---|
| **Status** | Proposed. Not normative and not applied to any DEA text. |
| **Reference baseline** | DEA v0.3.4.3, frozen (PDF SHA-256 `51a2553e…7c33`) |
| **Decides** | (1) when a principal controls an identity, for Ctrl_θ (DEA p.8); and (2) which acts are attributed to which principals, for T3, H_EJ and H_DE^ext |
| **Does not decide** | Case(x) and the blocker ledger (ADR-002); MayAdjudicate ≠ AdjAssignment ≠ EvidenceSufficiency (ADR-003); the pilot protocol |
| **Executable evidence** | `adr001_ctrl.py` (standard library only), which writes `results/adr001-results.json`; regression cases are in `adr001-regression-cases.json` |

## 1 Context

DEA v0.3.4.3 p.8 currently reads:
- p controls a at θ when p "can exercise a's relevant credentials, write or replace its governed decision artifact or decision criteria, or alter its effective capabilities **during the stage**".
- "The relation is the reflexive, transitive closure of these declared direct-control edges; the controlling graph and its historical versions must be bound to the execution/adjudication record."
- p.10, Eq.16: ExecConflict(j,x,θ_J) := ∃p,a,θ_E : Ctrl_θJ(p,j) ∧ Ctrl_θE(p,a) ∧ OwnOutput(a,x,θ_E).

The text leaves five things open:

1. **Closure timing.** The text does not say whether the closure is taken per instant or over the whole stage. The two readings give different adjudication decisions (CTRL-6b; 72 of 16,807 models in the RP-1.0 class).
2. **Paths that never existed.** Closing the union of a stage's edges creates control paths that never existed in causal order. This is your concern, and CM2 below shows it.
3. **Act timing.** Control that begins *after* an act, and control over a producer *after* its act but *before* its output is fixed, are not addressed.
4. **Cycles.** Cyclic control graphs are admitted implicitly, but how acts are attributed among mutually controlling principals is not stated.
5. **Cross-stage relays.** "During the stage" excludes control that a principal exercised in θ_E and that carries forward into θ_J.

**Kept separate.** The RP-1.0 verification found that RBAC role-hierarchy *encodings* fail on cyclic graphs (C4). That is a property of those target formalisms, not a defect of DEA, and it is **not** a driver here. Only items 1–5 are.

## 2 Decision drivers (testable properties)

| ID | Property | Rationale |
|---|---|---|
| P1 Relay robustness | If p controls o at t₁ and o controls x at t₂ ≥ t₁ within the relevant window, then p controls x | Otherwise rotating control edges in time evades the guard (CM1) |
| P2 Phantom-freeness | A path whose edges occur only against time order does not establish control | p cannot act through o after o's control over x has ended (CM2) |
| P3 No anachronism | Control that begins after the attributed act is irrelevant to that act | j's disposition at t cannot be influenced by control acquired after t (CM3) |
| P4 Tamper window | Control over the producer counts until the output is sealed | A principal that controls a after a's act but before x is fixed can alter x (CM4) |
| P5 Cross-stage carry-over | Control exercised in θ_E that persists into θ_J counts | Planted criteria survive stage boundaries (CM5) |
| P6 Well-definedness | Defined on arbitrary graphs, including cycles, with explicit attribution | DEA's text permits cycles (CM6, CM7) |
| P7 Monotone, fail-closed | Adding edge activity never removes a conflict; uncertain timing can be widened safely | Needed for conservative handling of imperfect records (CM9) |
| P8 Static conservativity | On time-invariant graphs the result equals the v0.3.4.3 closure | Existing static regression cases (G2 S1–S13) keep their outcome |
| P9 Auditability | Every blocking decision has a checkable witness; every permitting decision is recomputable from the bound graph versions | The record binding is already required (p.8) |

**Behavioural assumption A-PLANT.** Control over an identity includes the ability to plant persistent behaviour in it: its criteria, artifacts or capabilities. The planted behaviour persists until a recorded, independently authorised reset. P1 and P5 rest on this assumption. It follows from the p.8 edge kinds "write or replace its governed decision artifact or decision criteria" and "alter its effective capabilities".

## 3 Formal model and the three path semantics

**Model.**
- **Time.** A totally ordered time domain 𝕋. The executable model uses 𝕋 = {0,1,2,3}, θ_E = {0,1}, θ_J = {2,3}.
- **Control graph.** For each declared direct-control edge u→v, an activity set act(u,v) ⊆ 𝕋, a finite union of intervals. E(t) = {u→v : t ∈ act(u,v)}.
- **Acts.**
  - Executor a acts at t_E ∈ θ_E.
  - The output x is sealed at σ(x) ≥ t_E. Sealing means a content-addressed commitment bound to the record.
  - Adjudicator j assigns at t_J ∈ θ_J.

**Path semantics.** For a window W ⊆ 𝕋, a principal p and an identity x:

| Variant | Definition of Ctrl_W(p, x) |
|---|---|
| **A: simultaneous (pointwise)** | ∃t ∈ W : p →* x in E(t) |
| **B: stage union** | p →* x in ⋃_{t∈W} E(t) |
| **C: time-respecting (journey)** | p = x, or there are v₀=p, …, v_k=x and t₁ ≤ … ≤ t_k in W with v_{i−1}→v_i ∈ E(t_i) |

Variant C is evaluated by a single forward sweep over W: R := {p}, and for each t ∈ W in order, R := closure of R under E(t). The cost is O(|W|·(|V|+|E|)).

**Lemma 1 (inclusion).** A ⊆ C ⊆ B, for every W.
- *Proof.* A simultaneous path at t is a journey with t₁ = … = t_k = t. Every edge of a journey lies in the union.
- *Strictness.* CM1 is in C but not A. CM2 is in B but not C.
- *Check.* Zero violations in 490,596 models.

**Lemma 2 (static coincidence).** If E(t) is constant on W, then A = B = C = the reflexive-transitive closure of E. This gives P8.
- *Check.* Zero violations on all time-invariant models.

**Lemma 3 (monotonicity).** All three variants are monotone in every activity set and in W. This gives P7.
- *Check.* Zero violations under random single-instant additions.

**Lemma 4 (non-transitivity of C).** Ctrl^C over a fixed window is in general **not** transitively closed.
- *Witness.* o→j at 2 and p→o at 3. Then Ctrl^C(p,o) and Ctrl^C(o,j) hold, but Ctrl^C(p,j) does not.
- *Consequence.* The p.8 wording "reflexive, transitive closure" must become "reflexive, time-respecting reachability" if C is adopted.

## 4 Windows: when an act's attribution is evaluated

| Window | W_E (producer side) | W_J (adjudicator side) |
|---|---|---|
| stage (the v0.3.4.3 reading) | θ_E | θ_J |
| act-anchored | θ_E ∩ (−∞, t_E] | θ_J ∩ (−∞, t_J] |
| **causal (proposed)** | [θ_E⁻, σ(x)] | [θ_E⁻, t_J] |

The causal window has three features:
- **Upper bound.** It cuts off each side at the moment the act's result becomes immutable: the seal of x on the producer side, and the assignment on the adjudicator side. This gives P3 and P4.
- **Lower bound.** Both sides start at the beginning of the governed transition's record, θ_E⁻. This gives P5.
- **Upper bound is safe.** Activity after the cut-off provably cannot change the decision. Randomising all post-cut-off activity changed no decision (I4, 0 violations).

**ExecConflict** holds iff ∃p : Ctrl_{W_E}(p,a) ∧ Ctrl_{W_J}(p,j).

## 5 Countermodels and admissible adjudication decisions

Notation:
- ✗ means ExecConflict, so j may not assign any s ∈ Σ_adj (Accept, Reject, Hold or Supplement) to x.
- ✓ means j is not excluded on control grounds. Disposition authorisation and evidence remain separate questions (ADR-003).

| Countermodel | A/stage (audit reading A) | B/stage (audit reading B) | C/stage | A/act | C/act | **C/causal (proposed)** |
|---|---|---|---|---|---|---|
| CM1 forward relay (CTRL-6b): p→a{0,1}, p→o{2}, o→j{3} | ✓ | ✗ | ✗ | ✓ | ✗ | **✗** |
| CM2 reverse relay (phantom): o→j{2}, p→o{3} | ✓ | ✗ | ✓ | ✓ | ✓ | **✓** |
| CM3 anachronism: p→j{3}, t_J = 2 | ✗ | ✗ | ✗ | ✓ | ✓ | **✓** |
| CM4 producer controlled after act, before seal: p→a{1}, t_E = 0, σ = 1 | ✗ | ✗ | ✗ | ✓ | ✓ | **✗** |
| CM4b as CM4, but sealed at 0 | ✗ | ✗ | ✗ | ✓ | ✓ | **✓** |
| CM5 cross-stage relay: p→o{1}, o→j{2,3} | ✓ | ✓ | ✓ | ✓ | ✓ | **✗** |
| CM6 static cycle p⇄o, o→j, p→a | ✗ | ✗ | ✗ | ✗ | ✗ | **✗** |
| CM7 alternating mutual control: o→a, o→p{2}, p→o{3}, p→j | ✗ | ✗ | ✗ | ✗ | ✗ | **✗** |
| CM8 = CM1 plus a recorded independent reset of o at 3 (variant C-R) | ✓ | ✗ | ✗ | ✓ | ✗ | **✓** (C-R) |
| CM9 p→o timing uncertain in [2,3], widened | ✗ | ✗ | ✗ | ✗ | ✗ | **✗** |
| CM10 no common controller | ✓ | ✓ | ✓ | ✓ | ✓ | **✓** |

**Property satisfaction:**

| Configuration | P1 relay (CM1) | P2 no phantom (CM2) | P3 no anachronism (CM3) | P4 tamper window (CM4) | P5 cross-stage (CM5) |
|---|---|---|---|---|---|
| A/stage | no | yes | no | yes | no |
| B/stage | yes | no | no | yes | no |
| C/stage | yes | yes | no | yes | no |
| A/act | no | yes | yes | no | no |
| C/act | yes | yes | yes | no | no |
| B/causal | yes | no | yes | yes | yes |
| **C/causal** | **yes** | **yes** | **yes** | **yes** | **yes** |

Only C/causal satisfies all five properties.

## 6 Bounded evidence (finite, not a proof)

**Model classes:**
- *MC-T (exhaustive):* 470,596 models. Six edge slots (p→a, p→o, o→p, o→j, o→a, p→j), seven activity options each, and all four (t_E, t_J) combinations. The class includes the cycle p⇄o.
- *Random sample:* 20,000 models over all 12 edge slots, with arbitrary activity subsets and seal times (seed 20261116).

**Invariants.** I1 (inclusion), I2 (monotonicity), I3 (static coincidence), I4 (no anachronism under C/causal) and I6 (equal control rows inside a static SCC) all had **0 violations**.

**Disagreement counts in MC-T** (models where two configurations reach different conflict decisions). They are class-dependent and are not frequency estimates:
- A vs C (causal): 3,640.
- C vs B (causal): 3,256.
- Act-anchored vs causal (C): 71,552. All of these are added blocks and none are removals. This is the cost of P5, the record horizon.
- Stage vs causal (C): +56,472 blocks and −72,040 blocks.

## 7 Cycles and attribution (P6)

- **Cycles are admitted.** Every definition is reachability, so no acyclicity assumption is needed on the DEA side, and SCC condensation is unnecessary.
- **Static SCCs.** All members of a static strongly connected component have identical control rows (I6). An act of any member is attributed to every member and to every principal that controls any member.
- **Temporal cycles.** These are resolved by journey order and are not collapsed (CM7).
- **Identity bindings.** Aliases, key rotation and operator-of relations are declared as mutual edges for their validity interval. Identity change therefore becomes a temporal cycle and needs no extra mechanism. This handling is proposed only; I have not tested it beyond CM6 and CM7.

## 8 Decision (proposed)

| ID | Decision |
|---|---|
| D-1 | Ctrl uses **time-respecting reachability (C)** over declared direct-control edges, each with an activity set. |
| D-2 | Attribution windows are **causal**: producer side [θ_E⁻, σ(x)], adjudicator side [θ_E⁻, t_J]. If σ(x) is not recorded, then σ(x) := t_J (fail-closed). |
| D-3 | Cycles are admitted. Attribution is to every principal with time-respecting reachability to the actor, which includes every member of a mutual-control component. |
| D-4 | A journey is cut only by a **recorded, independently authorised reset** of an intermediate identity (C-R). An unrecorded reset has no effect. |
| D-5 | Uncertain activity timing is widened to its uncertainty interval (fail-closed). This is sound by Lemma 3. |
| D-6 | A blocking decision records a witness journey (edges, instants, versions). A permitting decision records the reachable sets computed from the bound graph versions. |

**Proposed replacement wording for p.8.** This is not applied; it is for a later candidate.
> The relation is the reflexive, time-respecting reachability over declared direct-control edges: p controls a for an act if a chain of edges p→…→a was active at non-decreasing instants within the act's attribution window. The window opens at the start of the governed transition's execution stage and closes when the act's result becomes immutable (seal of the output for the producer; recording of the assignment for the adjudicator). A chain is interrupted only by a recorded, independently authorised reset of an intermediate identity.

## 9 Consequences

- **More blocking than audit reading A.** CM1, CM4 and CM5 become blocking. In deployments with frequent re-delegation, more objects will need routing to an independent adjudicator.
- **Less blocking than union semantics.** C/causal blocks less than B in the phantom case (CM2) and the anachronism case (CM3), and when the output was sealed before the late control began (CM4b).
- **New record obligations:**
  - activity intervals for every control edge;
  - seal events for outputs;
  - assignment timestamps;
  - reset records.
- **The guard is about control only.** A ✓ in §5 does not imply the disposition is authorised or evidentially sufficient (ADR-003).

## 10 Rejected alternatives

- **A (simultaneous).** Evadable by timed rotation of control (CM1) and misses cross-stage carry-over (CM5). It would be acceptable only if A-PLANT were false, that is, if identities were provably stateless between instants.
- **B (union).** Produces phantom paths (CM2). Its stage form also attributes anachronistically (CM3), and its stage form still misses CM5.
- **Stage windows, whatever the path semantics.** These violate P3 and P5.

## 11 Open obligations

1. **Lookback before θ_E⁻.** Planting before the execution stage (pre-stage control) is outside the window. Choose between θ_E⁻ and the earliest bound graph version. The existing p.8 exclusion of independently issued pre-stage manifests stays.
2. **Distributed time.** If events are only partially ordered, replace ≤ by happened-before and specify how concurrent edges are treated. Fail-closed would treat them as ordered both ways.
3. **T3 and H_DE^ext.** The windows for the scope act (Distinction) and for external effects need the same anchoring. Not tested.
4. **Dense time and half-open intervals.** Only discrete instants were executed.
5. **Resets.** Only node-level resets were modelled. Partial resets (criteria only, or credentials only) are open.
6. **Proof status.** Lemmas 1–4 have short proofs here. Every other statement is finite-class evidence from `adr001_ctrl.py`.
7. **Prevalence.** The prevalence of the decision differences in real deployments is unknown. This belongs in the pilot, after the semantics are frozen.

## Reproduce

```
python3 co-scientist-outputs/dea-adr-001/adr001_ctrl.py --out co-scientist-outputs/dea-adr-001/results/adr001-results.json
```

The run takes about 3.5 minutes. It exits 0 only if all 11 regression cases match and no invariant is violated.
