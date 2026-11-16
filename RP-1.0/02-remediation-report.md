# DEA v0.3.4.3 translation audit — remediation report

**Protocol:** RP-1.0 (`01-remediation-protocol-v1.md`, SHA-256 `107a9793…3dac`)
**Baseline:** DEA v0.3.4.3 PDF, SHA-256 `51a2553e…7c33`. The baseline was not modified.
**Original audit package:** preserved unchanged in `original-package/`, together with `ORIGINAL_SHA256SUMS`.

## 1 Summary

- **Withdrawn.** Three original claims of non-expressibility do not hold as stated.
  - **EJ-7** is refuted. Uniform task indexing makes disposition-specific authorization native in Bertino 1999 and W&L-07.
  - **NAP-3** is refuted. The invariance pair can be separated by a local translation, and exact WSP reductions exist.
  - **LED-4** survives only within the stated translation class A-INST-LOCAL.
- **Oracles removed.** The six Regime-B tests that reused the DEA evaluator now run on independent engines. EJ-3 had also relied on `panic`, which only detects violations.
  - Every independent Regime-B translation is preserved. Most are restatements of the DEA definitions.
  - Two of them are genuine reductions to native machinery: role-hierarchy closure in Li 2007 and in RSL99.
- **Transitive control and reachability come for free in RBAC role hierarchies.** RH* (Li p.10) and `roles*` (RSL99 Fig. 1) compute DEA's control closure and NAP reachability once principals or states are encoded as roles. Any claim that these constructs lie beyond the expressive power of the RBAC literature is therefore not supported.
- **CTRL-6b is an architectural ambiguity.** Per-instant closure and window-union closure disagree on 72 of 16,807 models, and DEA v0.3.4.3 p.8 does not select either reading.
- **Wang & Li 2010 could not be obtained.** Every cell for that paper is SOURCE-UNVERIFIED.

## 2 Integrity and reproducibility (brief §3.1)

| Requirement | Original package | Remediation |
|---|---|---|
| Baseline path | hard-coded workspace path | `--baseline` or `DEA_BASELINE` |
| Missing or altered baseline | `baseline_intact=false`, run continues | exit 2, **no results written**. Tested: no path, nonexistent path, PDF with one appended byte |
| Missing or altered protocol | checked | exit 2, no results |
| Order of checks | — | integrity and static independence run before any test is computed |
| Clean-room run | not documented | `README.md`; verified from an extracted archive (§9) |
| "Frozen" protocol | claimed | withdrawn. The original protocol mtime (08:46:03) precedes the first script save (08:49:31). This is self-attested and has no external timestamp. RP-1.0 has the same limitation, and says so. |

**Reproduction and independent verification are different things.**
- Re-running the original script reproduces its numbers, but only with the original's own semantics.
- This package verifies those numbers independently: it re-implements the targets as separate engines, so original results are confirmed or corrected rather than re-executed (change log §2).
- The verification is independent at the code level only. It was carried out by the same auditor, with no second reviewer.

## 3 Oracle removal (brief §3.2)

| Original | Defect | Replacement (independent engine) | Result |
|---|---|---|---|
| EJ-3 | reused DEA logic; `panic` read as detection | EJ-B-BER (`bertino.py` + `datalog.py`, `cannot_dou` prevention) | preserved, 1,440 models; RESTATEMENT |
| T3-3 | aux `obj/2` with a DEA-shaped rule | T3-A-BER-2 (native, A-IDX); T3-B-LI/RSL-HIST | preserved |
| NAP-5 | DEA reachability reused | NAP-B-BER (recursive Datalog) | preserved, 26,262; RESTATEMENT |
| NAP-7 | DEA NAP reused for the TICK process | NAP-B-BAS-TICK (`lts.py` word enumeration) | preserved; REDUCTION |
| CTRL-4 | DEA closure reused | CTRL-B-BER[A], CTRL-B-BER[B] | each matches **only its own reading** |
| LED-3 | DEA ledger reused | LED-B-BER (persistent store, count/max aggregates) | preserved, 2,954; RESTATEMENT |
| CTRL-2 | precomputed co-control relation reported as "A (compiled B)" | kept as CTRL-ORACLE-WL, **excluded as evidence** | — |

**Static check.** No file in `engines/` or `translations.py` imports `dea_ref`. The harness exits 3 if one does.

## 4 Non-expressibility claims (brief §4)

| Claim | Status | Reason |
|---|---|---|
| EJ-7 (Bertino, W&L) | **REFUTED** | The original argument quantified only over translations with one adjudication task per output. Under A-IDX, EJ-A-BER-2 and EJ-A-WL-2 are preserved in both directions on MC-EJ. The pair is separated. |
| NAP-3 (WSP under R3) | **REFUTED as stated**; reported as FAILED-ENCODING / NON-EXPRESSIBILITY NOT ESTABLISHED | The pair m1/m2 differs in a 1-local feature. NAP-R-WSP-LABEL and NAP-R-WSP-PATH are exact, but they repurpose users. |
| NAP, translation class T_loc(r) | **PROVEN under stated assumptions** (PRF-NAP-HANF) | Graphs A and B (L = M = 6) have identical multisets of radius-1 and radius-2 neighbourhood types (machine-checked) but opposite NAP. The class covers WSP translations with single-user steps and locally generated constraints. It does **not** cover translations with search over several candidate users. Extending it to Bertino Regime A depends on Hanf-locality of FO with aggregates (Hella, Libkin, Nurmonen & Wong, J. ACM 2001), an external result not re-verified here, so that extension is **conditional**. |
| LED-4 (Bertino) | **PROVEN under A-INST-LOCAL** (PRF-LED4) | A permit/deny verdict in instance W depends only on CB(W), the spec and W's history (Def 4.7). The machine-found witness has the same W2 projection `[cont W2 X β]` in two models with different DEA verdicts. Dropping A-INST-LOCAL (A-MERGE, B) removes the obstruction. |
| Ctrl in W&L-07 | **PROVEN under A-STEP + LOCAL-REL** (PRF-CTRL-WL-MONO) | Monotonicity lemma: adding fresh users and pairs that contain them preserves every valid plan on old users. The DEA pair m0/m1 is checked for both readings. Ctrl is expressible only by ORACLE-EMBEDDING. |
| Ctrl in Li / RSL99 | **not non-expressible** | Principal-as-role reductions (Regime B) are exact for each reading. |

## 5 Protocol deviations corrected (brief §6)

- **LED-1.** Detection and prevention are now separate observables.
  - LED-A-BER-DETECT (`panic`) fails in both directions: forward 792, backward 384.
  - LED-A-BER-INST (`cannot_dou` prevention, per instance) fails forward 2 and backward 384. All failures are cross-instance effects.
  - Persistence across instances is handled only in LED-A-BER-MERGE (A\*) and LED-B-BER (B).
  - LED-B-BER is preserved on MC-LED and on all G4 cases.
  - LED-A-BER-MERGE is preserved on MC-LED but over-grants on the new length-4 case N1: its B = 1 count rule cannot reset per opening without a cross-task order.
- **Regression coverage:**

| Suite | Included | Newly constructed | Excluded / unavailable | Divergence from v0.3.4.2 intent |
|---|---|---|---|---|
| G2 S1–S12 | 12 | S13 (transitive control) | — | S8: TCB admin now gives (T3, H_EJ, D~E) = (T, T, T). v0.3.4.3 p.8–9: "TCB principal is not exempt"; acts are attributed to each controlling principal for T3 |
| G3 M1–M9 | 9 (M2 and M4 from the v0.3.4.1 script) | — | — | M8 self-hold: 1 → 0 (guard covers every s ∈ Σ_adj, p.10) |
| G4 A1–A8, L1–L4 | 12 (A2, A5 and L4 were missing in the original) | N1, N2 (length 4) | — | none (A-MERGE target over-grants on N1) |
| NAP | 7 named | depth-bound diagnostic | hybrid cases (continuous flows); G1 placement typing | — |

All 44 regression cases match the v0.3.4.3 expectation. The original's "53/53, 32/32" were v0.3.4.2 and v0.3.4.1 counts and are **not** re-claimed. The original's "39 results" were 27 translation comparisons and 12 claim checks. The present package has 54 comparisons (4 of them oracle embeddings, excluded) and 6 proof or refutation records.

## 6 Primary sources (brief §7)

| Source | Status | Key definitions used |
|---|---|---|
| Bertino, Ferrari & Atluri 1999 | inspected (printed page = PDF page + 64) | Def 2.1 p.71; C6 p.72; Tab. I–IV pp.73–76; Defs 4.2, 4.4, 4.7 pp.75–77; Prop. 4.1 p.78 |
| Ahn & Sandhu 1999 (RSL99) | **now inspected** (printed page = PDF page + 42) | Fig. 1 p.46 (roles*, RH); CU p.45/47; snapshot assumption p.47; RFOPL and Theorems 1–2 pp.48–51; Table 1 #1, #2, #5 p.53; §5.3 p.53: history-based SoD needs "suitable extensions" that are not given |
| Li, Tripunitara & Bizri 2007 | inspected | Notation 1 p.9; Notation 2 (RH*) and Def 3 p.10 |
| Wang & Li 2010 | **unavailable** (no OA copy; OpenAlex `best_oa_location` null; not on the authors' page) | none; SOURCE-UNVERIFIED |
| Wang & Li 2007 (ESORICS) | inspected; reported only under its own name | Defs 1–5 pp.6–7 |
| Basin, Burri & Karjoth | inspected (extended version) | Defs 1–8; Def 7 p.14 |

Secondary citations (Sandhu TCE and Nash & Poland, via RSL99 p.44; Clark–Wilson; Jonscher) are never used to classify a cell. The full grid is in `04-crosswalk.csv`.

## 7 CTRL-6b (brief §8)

**Boundary model:** p→o only at t = 2, o→j only at t = 3, p→a in θ_E.

| Semantics | p controls j in θ_J? | ExecConflict | Adjudication |
|---|---|---|---|
| A: per-instant closure | no (no single instant has both edges) | false | effective |
| B: closure of window union | yes | true | blocked |

- **Prevalence.** Over MC-CTRL the readings disagree on 72 of 16,807 models. The original class did not contain the distinguishing pattern, which is why the original CTRL-6 reported `holds: false`.
- **What DEA says.** v0.3.4.3 p.8 says Ctrl_θ holds "at transition θ … during the stage", is "the reflexive, transitive closure of these declared direct-control edges", and requires "historical versions" to be bound. It does not fix whether closure is taken per instant or over the stage.
- **Classification:** architectural ambiguity. The original audit silently used reading A.
- **Proposed clarification for a later version, not applied to v0.3.4.3:** state one sentence, either "Ctrl_θ is the reflexive–transitive closure of the union of direct-control edges active at any time in the stage" (B, conservative: it blocks more) or the per-instant reading (A). Then add the CTRL-6b model as a normative regression case.
- **Targets.** Bertino-B, Li-RH and RSL-RH each encode either reading exactly. The ambiguity is in DEA, not in the targets.

## 8 Results overview (brief §9–10)

- **Native in Regime A** (bounded, finite classes): T3 in Bertino (A-IDX) and W&L-07; H_EJ with disposition-specific grants in Bertino and W&L-07 (A-IDX); H_DE^ext in Bertino through a `count` aggregate.
- **Expressible by extension:**
  - H_EJ and T3 in Li and RSL99 (A-HIST, restatement);
  - H_DE^ext in W&L-07 (pseudo-user);
  - static Ctrl in Bertino-B (restatement) and in Li and RSL99 (reduction);
  - NAP in all compared formalisms (Bertino-B, Li/RSL roles-as-states, Basin TICK, WSP label/path);
  - the ledger in Bertino (B only; A-MERGE fails on N1).
- **Proven non-expressible under stated assumptions:**
  - Ctrl in W&L-07 (A-STEP + LOCAL-REL);
  - the ledger in Bertino (A-INST-LOCAL);
  - NAP in T_loc(r).
- **Undetermined:** permission vs epistemic validity, and NAP diagnostic uncertainty. These are typing and reporting distinctions with no observable in any authorization semantics. Absent terminology is not treated as evidence.
- **Preserved distinctions:**
  - Hold/Supplement are adjudicative dispositions under H_EJ (M8; EJ tests include Hold and Supplement).
  - NAP ≠ budget exhaustion (DEA p.12).
  - Verified NAP ≠ inconclusive search (diagnostic regression).
  - Placement vs disposition is excluded: there is no target counterpart.

## 9 Clean-room reproduction

The package was zipped, extracted into a fresh directory, and run with only `python3` and the baseline PDF. `sha256sum -c SHA256SUMS` passed, and both `results/remediation-results.json` and `results/countermodels.json` were reproduced **byte-identically** (`cmp`). Procedure: `README.md`.

## 10 Unresolved issues

1. **Wang & Li 2010** is unavailable. To resolve: upload the article, add its definitions to the crosswalk, and re-run the W&L comparisons against the 2010 definitions (satisfiability and resiliency).
2. **Single auditor.** To resolve: an independent second implementation of at least one engine (R2BAC or Bertino), or a review of `engines/` against the cited definitions.
3. **Bertino Regime A for NAP and Ctrl** depends on an external locality theorem. To resolve: verify it against Hella et al. 2001, or prove locality for the non-recursive Bertino fragment directly.
4. **Bounded evidence.** Every "preserved" result is finite-class agreement, not an equivalence theorem.
5. **Case(x)** is supplied to the ledger targets rather than expressed in them. Content and provenance identity were not compared.
