# Countermodel catalogue

The machine-readable form, with all 38 entries, is `results/countermodels.json`, which `run_audit.py` regenerates. Each countermodel below is the smallest failing model by JSON size within its class.

**Columns:**
- **Direction:** *fwd* means DEA permits and the target refuses; *bwd* means the target permits and DEA refuses.
- **DEA / Target:** the events each side permits.

## Regime A encodings

| Test | Dir | Fails / class | Minimal countermodel | DEA | Target | Diagnosis |
|---|---|---|---|---|---|---|
| EJ-A-BER-1 | fwd | 160/1,440 | exec = [a, b]; a adjudicates both outputs (Hold), grants (a,0,Hold), (a,1,Hold) | {1} | {} | a coarse T_exec blocks output 1 after a executed output 0 |
| EJ-A-BER-1 | bwd | 512/1,440 | exec a; adj b requests Accept; grant (b,0,Hold) only | {} | {0} | coarse T_adj ignores the disposition |
| EJ-A-WL-1 | bwd | 608/1,440 | same as above | {} | {0} | same |
| EJ-A-LI / EJ-A-RSL | bwd | 100/1,440 | a executes 0; a's exec permission revoked; a adjudicates Hold with grant | {} | {0} | current-state safety forgets history; fixed by A-HIST |
| T3-A-BER-1 | fwd | 36/243 | scope a; exec [a, b]; acc [a, a] | {1} | {} | coarse T_exec merges outputs |
| DE-A-WL-1 | fwd | 6/12 | scope a, ext b, gate a | {ext} | {} | mandatory != gate ignores DEA's disjunction |
| DE-A-WL-2 | bwd | 4/12 | scope = ext = gate = a | {} | {ext} | no gate |
| CTRL-A-WL-snap / A-LI / A-RSL-CU | bwd | 8,160 (A) or 8,232 (B) /16,807 | o→a in θ_E, o→j in θ_J | {} | {eff.} | direct-edge snapshot at t = 3 misses indirect and historical control |
| LED-A-BER-INST | fwd | 2/2,954 | term W1 Xβ; reopen W2 Xβ (independent); cont W1 Xβ | {2} | {} | reopening in W2 is invisible to W1 |
| LED-A-BER-INST | bwd | 384/2,954 | cont W1 Xβ; cont W2 Xβ | {0} | {0,1} | budget not shared across instances (cf. PRF-LED4) |
| LED-A-BER-DETECT | fwd | 792/2,954 | cont W1 Xβ; cont W1 Yβ | {0,1} | {0} | `panic` counts across ledger keys; detection only |
| LED-A-WL | bwd | 756/2,954 | cont W1 Xβ twice | {0} | {0,1} | no counting form |
| NAP-A-WSP-1 | fwd / bwd | 26 / 13,818 | fwd: single state, no edges, no goal. bwd: goal = start, blocked self-loop | — | — | satisfiability ≠ goal reachability |
| NAP-A-WSP-2 | fwd / bwd | 4,202 / 8,200 | fwd: allowed self-loop, no goal. bwd: goal = start, no edges | — | — | non-empty ≠ goal-reaching |
| NAP-A-BAS-OBS | fwd / bwd | 334 / 13,510 | as NAP-A-WSP-1 | — | — | obstruction ≠ NAP |

## Readings of Ctrl_θ (DEA-internal)

| Test | Dir | Fails | Countermodel | Note |
|---|---|---|---|---|
| CTRL-*[B] vs DEA-A | fwd | 72/16,807 | p→o only at t = 2 (J_early), o→j only at t = 3 (J_late), p→a in θ_E | union closure blocks; per-instant closure does not |
| CTRL-*[A] vs DEA-B | bwd | 72/16,807 | same | mirror image |

The same 72 models separate the oracle, Bertino-B, Li-RH and RSL-RH encodings. The disagreement is in DEA, not in the targets (PRF-CTRL6B).

## Proof witnesses

| Proof | Witness |
|---|---|
| PRF-LED4 | model 1: [cont W2 Xβ] → granted. Model 2: [cont W1 Xβ, cont W2 Xβ] → W2 refused. W2's own projection is identical in both. |
| PRF-CTRL-WL-MONO | m0 = no edges (effective); m1 = p→a in θ_E, p→j in θ_J (conflict under A and B) |
| PRF-NAP-HANF | A: s→x1…x6→g plus y0→…→y6→z1…z6 cycle. B: endpoints swapped (s-chain into the cycle, y-chain to g). Same radius-1 and radius-2 type multisets; NAP(A) = false, NAP(B) = true. |
| PRF-NAP3 (refutation) | m1: diagnosis-only self-loop, goal unreachable. m2: the same action reaches the goal. Separated by NAP-R-WSP-LABEL. |
| PRF-CTRL6B | see the table above |

## Regression boundary cases (expected outputs under v0.3.4.3)

| Case | DEA output | Note |
|---|---|---|
| G2 S8 TCB admin | (T3, H_EJ, D~E) = (T, T, T) | v0.3.4.2 intent was (F, F, F) |
| G2 S13 (new) P→orc→e, P→j | (F, T, F) | transitive control |
| G3 M8 self-hold | 0 effective | v0.3.4.2 intent was 1 |
| G4 A7 shifted locator | 4 grants | documented residual: superficial similarity is not equivalence (p.12) |
| G4 N1 term, reopen, cont, cont (new) | 1 | A-MERGE target grants 2. The B = 1 count encoding over-grants after reopening; only length-4 cases show it. |
| NAP depth-bounded chain (new) | "undetermined" at depth 2 | no target has a three-valued verdict |
