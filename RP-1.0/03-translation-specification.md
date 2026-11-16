# Translation specification (RP-1.0)

Every translation is implemented in `harness/translations.py` and executed by an engine in `harness/engines/`. Neither directory imports the DEA reference evaluator `harness/dea_ref.py`; `run_audit.py` checks this statically and exits 3 if it is violated.

Notation: `k` is a DEA output index, `s` a disposition in {Accept, Reject, Hold, Supplement}, θ_E = {0,1} the execution window and θ_J = {2,3} the adjudication window.

## 0 Target semantics as implemented

| Engine | Source | Semantics executed |
|---|---|---|
| `datalog.py` | Bertino Prop. 4.1, p.78 | bottom-up stratified Datalog with negation, comparisons, `count`/`max` |
| `bertino.py` | Bertino Def 2.1 p.71; Tab. I–IV pp.73–76; Defs 4.2, 4.4, 4.7 | u is authorised for T iff ∃R: role(R,T) ∧ belong(u,R). A request is **prevented** iff `cannot_dou(u,T)` (or `cannot_dor` for a role of u) is derivable. If not prevented, `executeu(u,T,k)` and `success(T,k)` are added. `panic` is evaluated afterwards and reported as **detection only**. Regime A checks: native heads only, no native head in a body (non-recursive), native fact predicates only. |
| `r2bac.py` | W&L-07 Defs 1–5, pp.6–7 | constraint forms ρ(s1,s2), ρ(∃S,s), ρ(s,∃S). Plans are total; satisfiability is exhaustive. Runtime (Def 5): a step is permitted iff the user is authorised and the partial plan extends to a valid plan. Def 3 predecessor condition is enforced in `_wl_runtime_ordered`. |
| `rbac_li.py` | Li Notation 1–2 p.9–10, Def 3 | auth_perms via UA ∘ RH* ∘ PA; ssod⟨P,k⟩ safe iff no k−1 users together hold all of P |
| `rsl99.py` | RSL99 §3–4, Fig. 1–3, Table 1 | RFOPL over a single snapshot (p.47). Functions `user`, `roles`, `roles*` (with RH closure, Fig. 1), `permissions`; `OE`/`AO` are expanded by universal quantification after Reduction (Theorems 1–2). |
| `lts.py` | Basin Defs 1–8; Def 7 p.14 | word enumeration up to \|S\| steps; `obstructed`, `tick_reachable` |

## 1 Regime A (native vocabulary)

| Test | DEA input → target structure | Observable |
|---|---|---|
| EJ-A-BER-1 (original) | one T_exec, one T_adj; belong(u,R_adj) for every grant holder; `cannot_dou(U,T_adj) ← executeu(U,T_exec,K)` | adjudication k permitted |
| **EJ-A-BER-2** | tasks T_exec_k, T_adj_k_s; role(R_adj_k_s,T_adj_k_s); belong(u,R_adj_k_s) iff (u,k,s) granted; `cannot_dou(U,T_adj_k_s) ← executeu(U,T_exec_k,K)` | request T_adj_k_disp(k) permitted |
| EJ-A-WL-1 / **EJ-A-WL-2** | steps s_exec_k, s_adj_k(_s); UR from executors/grants; ⟨≠(s_adj, s_exec_k)⟩; order exec ≺ adj | runtime permission |
| EJ-A-LI | UA = executors (revoked removed) + grant holders; ssod⟨{p_exec_k, p_adj_k_s},2⟩ on current state | holds p_adj ∧ safe |
| EJ-A-RSL | snapshot UA as above; CR = {{Rex_k, Radj_k_s}}; Table 1 #1 | assigned ∧ sat |
| T3-A-BER-1/2 | `cannot_dou(U,T_acc(_k)) ← executeu(U,T_scope,_), executeu(U,T_exec(_k),_)` | acceptance k permitted |
| T3-A-WL | ⟨≠(∃{s_scope, s_exec_k}, s_acc_k)⟩ | runtime |
| DE-A-BER | `cannot_dou(U,T_ext) ← executeu(U,T_scope,K), count([executeu(V,T_gate,K2), V≠U], N), N = 0` | ext permitted |
| DE-A-WL-1/2 | mandatory gate step with ≠ constraints / no gate step | ext permitted |
| CTRL-A-WL-snap | relation ctl = direct edges active at t = 3; ⟨¬ctl(s_J,s_E)⟩, ⟨¬ctl(s_E,s_J)⟩, ⟨≠⟩ | adjudication effective |
| CTRL-A-LI / CTRL-A-RSL-CU | atomic users / CU = direct edges at t = 3, SSOD-CU (Table 1 #5) | effective |
| LED-A-BER-INST | one Bertino instance per (DEA workflow, case, blocker); `cannot_dou(U,T_cont) ← count(success(T_cont)) > count(success(T_reopen))`; `cannot_dou(U,T_cont)` while terminated; reopening only by role R_ind (independent requester); B = 1 form | continuation permitted (**prevention**) |
| LED-A-BER-DETECT | original LED-1: `panic ← count(success(T_cont,K),N), N > B` per workflow | **detection** only; never counted as enforcement |
| LED-A-WL | each continuation an authorised step | permitted |
| NAP-A-WSP-1/2 | S = all / authorised carrier actions | NAP := unsat / S = ∅ |
| NAP-A-BAS-OBS | carrier as LTS | NAP := obstructed (Def 7) |

**A-IDX.** Indexing tasks and steps by output and disposition is a declared modelling choice: tasks and steps are uninterpreted labels in Bertino Def 2.1 and W&L Def 2. The number of task activations must be known in advance (Bertino p.71).

**A\* (LED-A-BER-MERGE).** This maps one DEA ledger key to one Bertino instance across DEA workflows. It reinterprets the instance boundary, so it is reported separately from both A and B.

## 2 Regime B (declared conservative extensions)

| Test | Declared auxiliary structure | Informativeness |
|---|---|---|
| EJ-B-BER | `produced/2` (post-fact of an exec activation), `granted/3`, `req/2`, `cand/1`; native heads only | RESTATEMENT |
| EJ-B-LI-HIST, EJ-B-RSL-HIST, T3-B-LI-HIST, T3-B-RSL-HIST | **A-HIST**: UA records "has performed the function", irrespective of later revocation | RESTATEMENT |
| DE-B-WL | pseudo-user ν; ρ\* = {(u,v): u ≠ v, u ≠ ν}; ⟨ρ\*(∃{s_gate,s_scope}, s_ext)⟩ | REDUCTION |
| CTRL-B-BER[A\|B] | `edge/3`, `node/1`, `time/1`, `inE/1`, `inJ/1`; positive recursion `rp/3` (per instant) or `rE/2`, `rJ/2` (window union); `cannot_dou(J,T_adj) ← ctrlJ(P,J), ctrlE(P,A), executeu(A,T_exec,K)` | RESTATEMENT |
| CTRL-B-LI-RH[A\|B] | **principal-as-role**: role r_x_t per node and instant (A) or per node and window (B); edge x→y active at t gives RH(r_x_t, r_y_t); node x ∈ UA(r_x_*); p_exec on a's roles in θ_E, p_adj on j's roles in θ_J; ssod⟨{p_exec,p_adj},2⟩. RH* (Li p.10) computes the closure. | REDUCTION |
| CTRL-B-RSL-RH[A\|B] | same structure; Table 1 #2 (MOD-CP) with `roles*` (Fig. 1) | REDUCTION |
| LED-B-BER | persistent cross-instance store: `led/3`, `term/3`, `opn/3`, `key/2`, `budget/1`; IDB `closed/2`, `lastopen/3` (max), `used/3` (count); prevention via `cannot_dou` | RESTATEMENT |
| NAP-B-BER | `edge/3`, `ok/1`, `start/1`, `goal/1`; recursive `reach/1`; `nap ← ¬reached` | RESTATEMENT |
| NAP-B-LI-RH, NAP-B-RSL-RH | **roles-as-states**: allowed edge x→y gives RH(r_x, r_y); probe ∈ UA(r_start); PA(p_goal) on goal roles; NAP iff the probe lacks p_goal | REDUCTION |
| NAP-B-BAS-TICK | TICK enabled exactly in goal states | REDUCTION |
| NAP-R-WSP-LABEL | users {R, N} as reachability labels; ⟨imp(s_x,s_y)⟩ per allowed edge with imp = ¬(R,N); start ↦ R only, goals ↦ N only; NAP := satisfiable. **Violates R3.** | REDUCTION |
| NAP-R-WSP-PATH | users = allowed edges + idle loops; \|S\| slots chained by ρ_chain. **Violates R3.** | REDUCTION |

**Oracle embedding (excluded as evidence).** In CTRL-ORACLE-WL[A|B], R2BAC's relation is the co-control relation precomputed outside the target. It is executed for transparency only.

## 3 Inputs supplied to targets, not computed by them

- **Ledger:** `Case(x)` is computed by the DEA reference from content, locator and lineage, then supplied to the ledger targets as an attribute. None of the targets has content or provenance identity. Ledger results therefore say nothing about expressing `Case(x)` itself.
- **Reopening:** the independence of a reopening is supplied as a boolean.
- **G3 regression:** targets see identities only, so proxy control (M5) is not represented in Regime A.

## 4 Preservation relation

For each model m and each event e:
- **forward:** e ∈ DEA(m) ⇒ e ∈ Target(tr(m));
- **backward:** e ∈ Target(tr(m)) ⇒ e ∈ DEA(m).

Every failure is recorded with a minimal countermodel, chosen as the smallest JSON encoding among the failures. Agreement over a finite class is bounded regression evidence and does not establish a general equivalence.
