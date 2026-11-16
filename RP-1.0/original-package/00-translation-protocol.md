# Frozen translation protocol — DEA v0.3.4.3 prior-art audit

Frozen 2026-11-16 08:46 UTC, **before** any test in `dea-v0343-translation-tests.py` was written or run. The test script checks this file's SHA-256 at start-up and records it in the results. If the protocol changes, the earlier results are void.

## P0 Baseline (read-only)

- `uploads/DEA_v0.3.4.3_architecture_closure_candidate_2026-11-15.pdf`, 35 pp., SHA-256 `51a2553e…8c97c33`. Cited as **[DEA p.N, Eq. k]** with printed page numbers.
- The Paper-Karte (`DEA_Capability_Separated_Governance_Map_v0_3_4_3.pdf`, `caa006c5…a8baa`) is a summary only. It is not normative (its own p.4 says so) and is not used as a semantic source.
- Not used as semantics: the v0.3.4.1 `.tex` file, the unapplied v0.3.4.2 patch file, and the earlier countermodel scripts. Their *scenarios* are reused as regression inputs, **re-evaluated under v0.3.4.3 rules**. Any outcome that changes is reported as a baseline divergence, never silently reconciled.

### DEA semantics used (v0.3.4.3)

- **D1** H_EJ, T3 and H_DE^ext as in Eqs. (11)–(13), with the bans in Eqs. (31)–(33) [p.9, p.14]. The independent gate must take effect before e and must not be self-conferred [p.14].
- **D2** Ctrl_θ(p,a) is defined by direct-control edges: credential use, writing or replacing decision artifacts or criteria, or changing capabilities *during the stage*.
  - The relation is the **reflexive–transitive closure** of these edges, and edge history is recorded.
  - Shared weights, read-only access and an independently issued pre-stage manifest are not edges.
  - A TCB principal that in fact controls both sides of a boundary is **not exempt** [p.8–9].
  - Temporal reading **A-T**: Ctrl_θ(p,a) holds iff a direct-control path from p to a exists at some instant inside θ's window. This is a declared interpretation of "during the stage". Its alternatives are tested in §5 of the report.
- **D3** ExecConflict and MayAdjudicate_M as in Eq. (16) [p.10]. The guard applies to **every** s ∈ Σ_adj (Accept, Reject, Hold, Supplement). Assignments that conflict are not effective, whatever the grant. An Execution-local stop is in Σ_op and is not an assignment.
- **D4** Ledger κ = (Case(x), [β]_SameBlocker), with budget B_κ per opening, a grant only if b > 0, and atomic decrement.
  - A terminal disposition closes κ.
  - Reopening requires an independent authority sharing no controlling principal with the requester or D.
  - The per-ledger bound is B_κ(1+r_κ) [p.12–13].
- **D5** NAP(M,s0) ⇔ Π_auth,goal = ∅, as in Eqs. (46)–(47) [p.17–18]. The diagnostic classes are witness / verified NAP / undetermined [p.19].

## P1 Primary sources and their status

| Source | Status | Use |
|---|---|---|
| Bertino, Ferrari & Atluri 1999, TISSEC 2(1):65–104 | PDF in `uploads/`, read | full |
| Li, Tripunitara & Bizri 2007, TISSEC 10(2) Art. 5 | author PDF, read | full |
| Wang & Li **2010** (TISSEC, R2BAC journal version) | **not available in the workspace** | every cell is UNDETERMINED-SOURCE until it is supplied |
| Wang & Li 2007, ESORICS (preliminary version of the same model) | author PDF, read | **proxy**; cited as "W&L-07", never as the 2010 paper |
| Ahn & Sandhu 1999 (RSL99), RBAC'99 pp. 43–54 | **not available** | every cell is UNDETERMINED-SOURCE |
| Basin, Burri & Karjoth (obstruction-free enforcement, extended version) | PDF in `uploads/`, read | additional prior work |
| Jonscher et al. 1994; Nash & Poland 1990; Warner & Atluri 2006; Clark & Wilson 1987 | **secondary only** | labelled SECONDARY, never used to classify |

## P2 Translation regimes

**Regime A (strict native).** A translation may use only the source formalism's own predicate, relation and constraint symbols with their published meaning:

- **Bertino:** Tables I–IV and rule classes Defs 4.1–4.6.
- **W&L-07:** ⟨U,UR,B⟩, constraint forms 1–5 (Def 2), and valid plans (Defs 3–4). Any user-defined relation ρ ⊆ U×U is native, by Def 1.
- **Li 2007:** RBAC state ⟨UA,PA,RH⟩, SSoD policies, and SMER constraints.
- **Basin:** the CSP processes of Defs 1–8.

No new primitive is allowed. Reinterpreting a native symbol is also not allowed; for example, reading Bertino's `success/abort` as Accept/Reject is forbidden (Bertino p.72, fn. 4).

**Regime B (uniform conservative extension).** Regime A plus a single, globally declared list of auxiliary symbols:

| Symbol | Purpose |
|---|---|
| `obj(K,X)` | activation K yields object X |
| `assigned(U,X,S)` | adjudicative assignment event |
| `granted(U,X,S)` | AuthorizedForDisposition |
| `ctrl_edge(P,A,θ)` + positive recursive closure `ctrl*` | control |
| `case_of(Inst,C)`, `blocker(Inst,β)`, `ledger_count(C,β,N)` | persistent state across instances |
| `budget(B)` | budget |
| pseudo-user `ν` ("no-one") | optional steps |
| `state/edge/goal` facts with positive recursion `reach` | for logic-program targets |

Every auxiliary symbol is defined once, identically for all models. Native symbols keep their meaning. "Conservative" means that on DEA-free inputs every native verdict is unchanged.

## P3 Translation rules (both regimes)

- **R1 Uniformity.** tr is one function of the DEA model. It is written before testing and is not tuned per model.
- **R2 No oracle.** tr must not compute the target outcome. For example, it must not decide reachability, conflicts or budget exhaustion and then emit a flag. Only local, per-element mapping is allowed. The one exception is the closure of declared relations, and only where the target formalism itself supplies or presupposes relations computed outside it (W&L-07 Def 1).
- **R3 Sort preservation.** DEA identities and principals map to users, transitions to workflow instances or steps, and objects to activations or aux objects. A translation that repurposes users as states or edges is a *reduction*, not a translation. It is reported but cannot establish expressibility.
- **R4 Effectiveness.** In Bertino, a DEA "non-effective" assignment corresponds to an assignment that is prevented (cannot_dou) or that raises `panic`. The `panic` reading is allowed only in Regime B, and is marked as detection rather than prevention.

## P4 Model classes (finite, enumerated)

| Class | Contents |
|---|---|
| MC-EJ | identities {a,b,c}; 1–2 critical outputs; sequential or interleaved order; executor and adjudicator per output; disposition ∈ {Accept, Reject, Hold, Supplement}; grant sets |
| MC-DE | users {a,b}; scope user, external-effect user, and gate ∈ users ∪ {none} |
| MC-CTRL | principals {p,q}, intermediate identity o, executor a, adjudicator j; direct edges from {p,q,o} to {o,a,j}, each with an interval ∈ {none, θE only, θJ only, both, gap}; windows θE=[0,1], θJ=[2,3]; check time t_J=3 |
| MC-LED | 1–3 continuation events over workflows {W1,W2} × cases {X,Y} × blockers {β,γ}; B=1; terminal and reopen events with independent or co-controlled reopener |
| MC-NAP | the exhaustive family from `dea-nap-finite-model.py`: 1–2 states, at most one edge per ordered pair, 8 flag tuples, every goal subset (26,262 models); plus the DEA p.19 diagnosis-only countermodel |
| REG | regression scenarios G2 S1–S12, G3 M1–M9, G4 A1–A8 and L1–L4 (v0.3.4.2 closure), re-evaluated under P0 |

## P5 Preservation criteria

For each model m: Out_DEA(m) is the set of effective events (authorizations and effective adjudicative assignments), or the NAP verdict. Out_T(tr(m)) is the target's set of permitted events, or its verdict, mapped back.

- **Forward (soundness):** DEA-permitted ⇒ target-permitted. A failure means the target is *over-restrictive*.
- **Backward (completeness):** target-permitted ⇒ DEA-permitted. A failure means the target is *under-restrictive*.
- **Preserved on MC** means both hold for every m in the class. This is **never** read as a general equivalence proof.

## P6 Classification rules

- **EXPRESSIBLE-NATIVE:** a Regime A translation is preserved on all classes tested.
- **EXPRESSIBLE-EXTENSION:** Regime A fails, and a Regime B translation is preserved.
- **NOT-EXPRESSIBLE (under stated assumptions):** this requires either
  - (i) an invariance proof: two DEA models with different outcomes whose images are identical under *every* Regime A/B translation satisfying R1–R3, or
  - (ii) an explicit semantic argument from the formalism's definitions.

  A failed encoding attempt alone gives at most UNDETERMINED.
- **UNDETERMINED:** the source is unavailable, or neither a preserved translation nor a proof was obtained.
- Novelty claims are classified separately as *formal novelty*, *domain-specific semantics*, *governance methodology*, or *empirical effectiveness*. Expressibility results bear only on the first.
