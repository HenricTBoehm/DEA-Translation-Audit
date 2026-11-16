# Sources: access status, hashes and page maps

## Baseline (read-only)

| File | SHA-256 | Role |
|---|---|---|
| `uploads/DEA_v0.3.4.3_architecture_closure_candidate_2026-11-15.pdf` (35 pp.) | `51a2553e8bb13fe80bc3f0e6245ba0c4dcbe0a31db03ad577a3f3f26f8c97c33` | normative semantics |
| `uploads/DEA_Capability_Separated_Governance_Map_v0_3_4_3.pdf` (4 pp.) | `caa006c5115fe49dc1f6998f75223eae9341066769da966c9038dfba7c3a8baa` | summary only, non-normative (its own p.4) |

### DEA pages used

| Page | Content |
|---|---|
| p.8–9 | Ctrl_θ: direct-control edges and reflexive–transitive closure. History is bound to the record. Shared weights, read access and the pre-stage manifest are not edges. The TCB is not exempt. |
| p.9 | Eqs. (11)–(15); permission vs validity |
| p.9–10 | Σ_op / Σ_adj; Eq. (16): ExecConflict guard over **all** of Σ_adj |
| p.10–11 | Eq. (17) MayCompute ⇏ MayAccept; Eq. (18) |
| p.12–13 | ledger κ, B_κ, closure, independent reopening, bound B_κ(1+r_κ) and N_C, distinct-blocker countermodel |
| p.14 | Eqs. (31)–(33); "Eq. (16) intentionally stronger" |
| p.17–21 | NAP Eqs. (41)–(48); diagnostic classes and diagnosis-only countermodel (p.19); NAP ⇏ Reject Eqs. (51)–(54); Jpre/Jpost Eq. (56); P(x) ∉ Σ_adj Eq. (61) |
| p.32–34 | App. C: residuals and what is not established |
| refs | Clark–Wilson is cited. Bertino, Li, Wang & Li, Basin and Crampton are **not** cited. |

## Primary sources

| Source | Access | SHA-256 | Page convention |
|---|---|---|---|
| Bertino, Ferrari & Atluri, *The specification and enforcement of authorization constraints in workflow management systems*, ACM TISSEC 2(1):65–104, 1999, doi:10.1145/300830.300837 | PDF in `uploads/` | `3a9003ef…586b47` | printed = PDF + 64 |
| Li, Tripunitara & Bizri, *On mutually exclusive roles and separation-of-duty*, ACM TISSEC 10(2) Art. 5, 2007, doi:10.1145/1237500.1237501 | author PDF (scratch copy) | `7ed961f6…f15aa6` | printed = PDF |
| Wang & Li, *Satisfiability and resiliency in workflow systems*, ESORICS 2007 (preliminary version) | author preprint (scratch copy) | `b8bf42d4…98af` | preprint pages; **proxy for 2010** |
| **Wang & Li 2010**, ACM TISSEC (journal version) | **NOT AVAILABLE** | — | all cells UNDETERMINED-SOURCE |
| **Ahn & Sandhu 1999**, RSL99, Proc. RBAC'99, pp. 43–54 | **NOT AVAILABLE** | — | all cells UNDETERMINED-SOURCE |
| Basin, Burri & Karjoth, *Obstruction-free authorization enforcement* (extended version of CSF'11) | PDF in `uploads/` | `df96ce00…944c1` | manuscript pages |

### Page map: Bertino 1999

| Page | Content |
|---|---|
| p.66 | three impartial referees |
| p.67 | Ex. 1.1 (tax refund) |
| p.68 | "same check" dynamic SoD; Jonscher's activation conflict (secondary) |
| p.69 | sequential tasks |
| p.70 | role-dominance fallback |
| p.71 | Def 2.1: instances, one user per activation |
| p.72 | C1–C7. C6 counts per-user aborts "within the same workflow"; fn. 4: abort = error. |
| p.73 | Table I |
| p.74 | Table II |
| p.75 | Table III (`cannot_dou/2`), Defs 4.1–4.3 |
| p.76 | Table IV, Def 4.4 |
| p.77 | Table V, Defs 4.5–4.6 |
| p.78 | Ex. 4.1 (R6,1) |
| p.94 | planner assumes success |

### Page map: Li et al. 2007

| Page | Content |
|---|---|
| p.2 | dynamic/object SoD (Nash & Poland, Sandhu, Foley) |
| p.3 | Bob revoke/reassign |
| p.5 | Clark–Wilson quote |
| p.5–6 | Nash & Poland, cited |
| p.6 | policy vs mechanism |
| p.7 | related work, including Bertino |
| p.8 | DMER fails across sessions |
| p.9 | Notation 1 (k-n SSoD) |
| p.10 | Defs 3–4, role hierarchy |
| p.12 | Def 6 SMER |
| p.13 | Defs 7, 9 |
| p.14 | Def 10 |

### Page map: Wang & Li 2007

| Page | Content |
|---|---|
| p.1–2 | conflict of interest (COI), peer-review COI |
| p.5 | grant-proposal example |
| p.6 | Def 1 ⟨U,UR,B⟩ with user-defined relations, complements, =/≠; Def 2, constraint forms 1–5 (incl. ∃-forms, ρ_conflict_interest, BoD) |
| p.7 | Defs 3–5: plan, valid plan, runtime re-check |
| p.13–14 | resiliency |
| p.15 | related work: Bertino has no user-defined relations; Warner & Atluri inter-instance constraints; Crampton 2005; WSP NP-complete |

### Page map: Basin et al.

| Page | Content |
|---|---|
| p.2 | history-dependent vs history-independent |
| p.10 | Def 4: SoD with release points |
| p.12 | Defs 5–6: BoD |
| p.14 | Def 7: obstruction |
| p.15 | Def 8 |
| p.16 | Def 9: EPE, NP-hard |
| p.22 | release point is novel |

## Secondary only (not used to classify)

| Item | Seen via |
|---|---|
| Jonscher 1994 (author/referee activation conflict) | Bertino p.68 |
| Nash & Poland 1990 (object-based SoD) | Li p.5–6 |
| Warner & Atluri 2006 (inter-instance constraints) | W&L-07 p.15 |
| Clark & Wilson 1987, rule E4 | course notes only; DEA cites C–W directly |
| Crampton 2005 | W&L-07 p.15 |
