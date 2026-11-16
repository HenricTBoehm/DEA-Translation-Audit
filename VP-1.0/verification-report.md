# Independent verification of remediation audit RP-1.0 (DEA v0.3.4.3)

**Object of verification:** `dea-v0343-remediation.zip` (SHA-256 `18667ba7…56fa`), including `02-remediation-report.md`.
**Baseline:** DEA v0.3.4.3 PDF (`51a2553e…7c33`). It was not modified.
**Harness:** `verify.py` (standard library only). It produced 41 checks, recorded in `results/verification-results.json`.
**Reviewer independence:** limited. This review was carried out in the same environment, and by the same assistant, that produced RP-1.0. The checks therefore rely on executable re-implementations (`ind_closure`, `ind_conflict`, `ind_nap`, `ind_ledger`, a separate Hanf canonical form, and newly constructed boundary models), not on reviewer separation.

## 1 Result by status

### PASS (25)

| ID | Verified |
|---|---|
| R1–R4 | Checksums verify (29 files), as do the baseline and protocol SHA-256. Seven failure modes give exit 2 or 3 and write no results. |
| R6 | A clean-room run from the zip, with the baseline supplied via `DEA_BASELINE`, reproduces both result files byte-identically. |
| N1 | 54 comparisons. The 4 oracle embeddings are CTRL-ORACLE-WL [A]/A, [B]/A, [A]/B and [B]/B. |
| N2, N3 | 6 proof records; 44 regression cases (G2 13, G3 9, G4 14, NAP 8). |
| A2 | ⟨≠(∃{s_D,s_E}, s_J)⟩ is implemented as a disjunction. The conjunctive misreading differs on d = j ≠ e. |
| A3 | Li principal-as-role encodings of T3 and H_EJ are correct on all four controller-intersection models. |
| B1 | An R1–R3-respecting element-local image separates the NAP-3 pair. |
| B3 | The Hanf pair has equal r-type multisets and opposite NAP for r = 1…4, with L = M = 2r+2. |
| B6, B7 | The diagnostic states are sound with respect to semantic NAP (depths 0–3), and the NAP reference agrees with an independent BFS on 26,262/26,262 models. |
| C1, C2 | CTRL-6b is reproduced: pointwise closure gives no conflict, union closure gives conflict. The independent recount gives 72/16,807. |
| C4b | Bertino Regime B (recursive Datalog) preserves Ctrl on 6,598 general and cyclic samples. |
| C6 | The fresh-user monotonicity lemma holds in a bounded check. |
| D1–D4, D6 | The ledger reference agrees with an independent re-implementation (2,954/2,954). The PRF-LED4 witness and N1 are reproduced. All 386 LED-A-BER-INST failures are cross-instance. The five ledger concerns are kept separate. |
| E1, E6 | The W&L-07 engine conforms to Defs 1–5 (one specification erratum). No DEA decision logic is copied into the engines. |

### FAIL (9)

| ID | Report claim | Finding |
|---|---|---|
| A1 | T3 and H_EJ are "native (A-IDX)" in Bertino and W&L-07 (§8) | Holds for **nominal identity and task indexing only**. When one principal controls three distinct identities (BM2), DEA forbids and the Bertino and W&L A-IDX images permit. H_EJ also fails on the pairwise model BM1. |
| B4 | PRF-NAP-HANF covers WSP translations with single-user steps (§4) | The theorem holds for T_loc(r), and only by the definition of that class. Inclusion of WSP translations is argued informally, not proved. It is not a result for arbitrary admissible translations. |
| B8 | "Every independent Regime-B translation is preserved" (§1) | NAP-B-LI-RH and NAP-B-RSL-RH produce role hierarchies whose closure RH* is not a partial order on 324 cyclic MC-NAP models. These images are not RBAC states. |
| C3 | Implicit: MC-CTRL is representative | Every edge slot is p→o→{a, j}. The class contains no cycles and no a↔j edges. |
| C4 | "Transitive control and reachability come for free in RBAC role hierarchies" (§1); Li-RH and RSL-RH encode either reading "exactly" (§7) | Valid only for acyclic per-instant or per-window edge sets. 3,053 of 3,299 sampled general graphs give a cyclic RH. Repairing this needs SCC condensation, which is a global pre-computation and not RH*. |
| C5 | PRF-CTRL-WL-MONO is proven under A-STEP + LOCAL-REL (§4) | The proof as written is invalid. A "some-controller" translation is exact on the proof's pair m0/m1 but wrong on m2. The proof is repaired with the pair m1/m2 plus an added GENERICITY assumption; the conclusion survives. |
| E2 | Engines implement Li 2007 | `rbac_li.py` does not enforce the condition that RH* be a partial order (p.10). |
| N4 | All 44 regression cases match the expectation (§5) | 6 expectations were authored in the same session (S8, S13, N1, N2, M8, depth-2 diagnostic). S8 and M8 were re-derived from the text and agree. |
| R5 | Static independence check (§3) | Plain imports are detected, but dynamic and obfuscated references are not. Semantic independence was established by inspection (E6), not by the check. |

### UNDETERMINED (6)

| ID | Item |
|---|---|
| B2 | Whether an R3-respecting translation of NAP into WSP that preserves NAP exists. |
| B5 | Hella, Libkin, Nurmonen & Wong (J.ACM 2001): the paper and its Hanf/Gaifman analogues were verified at abstract level only. The embedding of Bertino Regime A into that logic is not shown, so the conditional Bertino-A cells stay conditional. |
| D5 | Case(x) transitivity and precedence. DEA p.12 does not fix them, and SameBlocker is a supplied label. |
| E3 | RSL99: OE/AO and the Reduction algorithm are not implemented; formulas were reduced by hand. |
| E4 | Bertino: only the reactive fragment is implemented; the planning component is not. |
| E5 | Basin Def 7 is implemented only as an analogue. |

### NOT EXECUTED (1)

| ID | Item |
|---|---|
| W1 | Wang & Li 2010 against W&L 2007. `1880022.1880034.pdf` is not in the workspace; I searched the whole filesystem, and ACM DL returns 403. No definition was compared and no result was transferred. Every 2010 cell stays SOURCE-UNVERIFIED. |

## 2 Answers to the brief's formal questions

- **A — T3 and H_EJ.** The A-IDX results establish preservation for nominal identity and task indexing only. They do **not** establish equivalence under effective multi-principal control (DEA p.8):
  - BM1 breaks the H_EJ images.
  - BM2 breaks the T3 and H_EJ images.
  - BM3 is correct.
  - The W&L constraint is existential, and its disjunctive reading is confirmed (BM4).
  - Ctrl-aware T3 in W&L-07 reduces to the Ctrl problem, so it inherits PRF-CTRL-WL-MONO.
- **B — NAP.**
  - *NAP-3.* The refutation stands as a refutation of invariance only.
  - *PRF-NAP-HANF, statement.* No translation whose verdict depends only on the multiset of radius-r neighbourhood types preserves NAP. Model class: finite labelled graphs with distinguished start and goal states. Observable: the NAP verdict. Each r needs one pair, and the uniform family with L = M = 2r+2 works (checked here for r ≤ 4).
  - *PRF-NAP-HANF, scope.* The radius-1 and radius-2 witnesses suffice for the theorem *within T_loc(r)*. They say nothing about translations outside that class, including WSP translations with search or several candidate users.
  - *Diagnostics.* VERIFIED_NAP, WITNESS and UNDETERMINED are diagnostic states and remain distinct from semantic NAP (B6).
- **C — Ctrl.**
  - *CTRL-6b.* Reproduced (C1, C2).
  - *RBAC role hierarchies.* Mapping principals or states to roles reproduces Ctrl for DAG control graphs, but not for arbitrary graphs. Cycles make RH* a preorder, which is not an RBAC state.
  - *Identity changes.* Not modelled (C3).
  - *Temporal changes.* Need time- or window-indexed role copies, which is a syntactic encoding chosen per reading.
  - *Bertino Regime B.* Handles cycles, but by restating the closure.
- **D — Ledger.**
  - *PRF-LED4.* Valid under A-INST-LOCAL.
  - *Cross-instance histories or merged workflows.* With either one admitted, the obstruction disappears (D2), and LED-B-BER is preserved.
  - *N1.* Reproduced. It is a FAILED-ENCODING, not non-expressibility.
  - *Case(x) and SameBlocker.* Their identity semantics are inputs, not targets of translation (D5).

## 3 Patches

`patches/` contains VP-1 to VP-5 and `CHANGELOG.md`. The originals are untouched. After patching:
- NAP-B-LI-RH and NAP-B-RSL-RH become *not preserved*, failing on 324 models.
- PRF-CTRL-WL-MONO carries GENERICITY.
- PRF-NAP3 executes the R3-respecting separation.
- All other results are unchanged.

## 4 Unresolved obligations

**Mathematical**
1. Wang & Li 2010: compare its definitions with W&L-07, then re-run C1a–C6 against 2010 (W1).
2. Prove or refute that the admissible WSP translations, under R1–R3, lie in T_loc(r) (B4). Alternatively, settle B2 directly.
3. Bertino Regime A: prove locality for the non-recursive fragment, or verify Hella et al. against the full text (B5).
4. Ctrl in Li and RSL99 on cyclic graphs: either show that no uniform translation without global pre-computation exists, or give one (C4).
5. T3, H_EJ and H_DE^ext under Ctrl in Bertino Regime A: undetermined (A1). The A-IDX images are refuted; other translations are not excluded.
6. PRF-CTRL-WL-MONO: justify GENERICITY as an admissibility condition in the protocol (C5).
7. Every "preserved" result remains finite-class agreement, not an equivalence theorem.

**Architectural (DEA side — for a later version, not v0.3.4.3)**
1. CTRL-6b: choose pointwise or window-union closure (C1).
2. Cyclic control and attribution: DEA p.8 permits cycles, and attribution of mutually controlling principals should be stated explicitly (C4).
3. Case(x): fix transitivity, precedence of content, locator and provenance, and the SameBlocker review procedure (D5).
4. Ledger enforcement obligations (unique continuation IDs, atomic decrement, protected updates) are untested (D6).

## 5 Decision on the audit

**CONDITIONAL GO.**

**Verified (executed and reproduced):**
- Integrity and reproducibility.
- The counts.
- The refutations of EJ-7 and NAP-3, scoped as above.
- CTRL-6b.
- PRF-LED4 under A-INST-LOCAL.
- N1.
- The diagnostic separation.

**Conditions:**
1. Scope T3, H_EJ and H_DE^ext "native" to nominal identity.
2. Restrict the Li and RSL99 Ctrl/NAP reductions to acyclic graphs, and withdraw "come for free in RBAC role hierarchies" as a general claim.
3. Restate PRF-CTRL-WL-MONO with GENERICITY and the pair m1/m2.
4. State PRF-NAP-HANF as a result about T_loc(r) only.
5. Disclose the self-authored regression expectations.
6. Keep W&L 2010 SOURCE-UNVERIFIED until the PDF is supplied.

**NO-GO** for describing the audit as "independently verified" without these qualifications, and for the two §1 headline claims marked FAIL (B8, C4).

## 6 Scientific contribution of DEA (separate from the audit)

The verification does not change the substantive picture:
- **Formal expressive power:** none demonstrated. Every DEA construction tested is expressible by uniform extension in at least one prior formalism. Bertino Regime B (recursive Datalog with aggregates) covers Ctrl on general graphs, NAP and the ledger. The non-expressibility results that survive are relative to explicitly restricted translation classes, so they do not establish novelty.
- **Domain semantics and governance methodology** (typed permission vs validity, Ctrl attribution, the case/blocker ledger as an accounting discipline, NAP diagnostics): **CONDITIONAL GO**, conditional on resolving the architectural obligations above.
- **Formal novelty:** **NO-GO**.
- **Empirical effectiveness:** **NO-GO** — the pilot is "forthcoming" (DEA p.22).
