# Remediation protocol RP-1.0: DEA v0.3.4.3 translation audit

**Status.** RP-1.0 was written on 2026-11-16 before the remediation harness was first executed. The harness checks this file's SHA-256 and stops if it differs.

**Not prospectively registered.** RP-1.0 was not timestamped or registered with any external party. Its "pre-execution" status rests only on the session record and on the hash check. The original protocol `00-translation-protocol.md` had the same property, which does **not** make it "frozen" in any externally verifiable sense (see §8).

**Scope.** This is a verification and prior-art assessment. The DEA v0.3.4.3 manuscript is not modified, renamed, re-versioned or republished.

## 1 Inputs and integrity

| Input | Requirement |
|---|---|
| Baseline PDF | `DEA_v0.3.4.3_architecture_closure_candidate_2026-11-15.pdf`, SHA-256 `51a2553e8bb13fe80bc3f0e6245ba0c4dcbe0a31db03ad577a3f3f26f8c97c33`. The path is configurable (`--baseline` or `DEA_BASELINE`). |
| Baseline `.tex` | Not available for v0.3.4.3. Only v0.3.4.1, v0.3.4 and v0.3.3 `.tex` exist, and they are **not** used as semantics. |
| This protocol | Hash embedded in `harness/run_audit.py`. |
| Original package | `original-package/`, copied unchanged, with `ORIGINAL_SHA256SUMS` and an archival zip. It is treated as immutable evidence. |

If the baseline or protocol is missing or altered, the harness exits non-zero (exit 2) and writes **no** results file.

## 2 Primary sources

| Source | Status | Rule |
|---|---|---|
| Bertino, Ferrari & Atluri 1999 | original PDF | usable |
| Ahn & Sandhu 1999 (RSL99) | original PDF (Academia, 12 pp., pp. 43–54) | usable |
| Li, Tripunitara & Bizri 2007 | author PDF | usable |
| Wang & Li 2010 (TISSEC 13(4):40) | **not obtainable** (no OA copy; ACM paywall) | every comparison is **SOURCE-UNVERIFIED**. W&L ESORICS'07 results are reported **only under their own name** and never as 2010 results. |
| Basin, Burri & Karjoth (extended CSF'11) | PDF | additional comparator, provenance stated |
| Jonscher 1994, Nash & Poland 1990, Warner & Atluri 2006, Clark–Wilson 1987 | secondary citations | never used to classify |

## 3 Regimes

### Regime A (strict native)

Only published primitives with their published semantics are allowed.

- **Bertino:** facts over Tables I–II predicates (`role`, `belong`, `executeu`, `executer`, `success`, `abort`). Rules may have only native heads (`cannot_dou`, `cannot_dor`, `must_executeu`, `must_executer`, `panic`; Defs 4.2, 4.4). Bodies may contain specification, execution, comparison and aggregate literals. This class is non-recursive. The harness checks it mechanically.
- **W&L-07:** Defs 1–5.
- **Li 2007:** Notation 1–2, Def 3.
- **RSL99:** §3–4 functions and sets. The semantics are RFOPL over a single snapshot (p.47).

**Allowed modelling choice (A-IDX).** Tasks and steps may be uniformly indexed by DEA output and disposition. Tasks and steps are uninterpreted labels in Bertino Def 2.1 and W&L Def 2. Any result that depends on A-IDX is flagged. Without A-IDX it reverts to FAILED-ENCODING, not to "proven".

**Forbidden in Regime A:**
- reinterpreting `success`/`abort` as dispositions;
- reinterpreting users or roles as states, edges, labels or controllers;
- using `panic` as enforcement.

### Regime B (uniform conservative extension)

Regime B allows declared auxiliary predicates, relations or structures, listed per test, together with their stated semantics.

- Translations must be uniform and element-local.
- Translations must not import the DEA reference evaluator or any shared decision function.
- On DEA-free inputs, all native verdicts must be unchanged.
- **Recursion, persistent state, history or time indexing count as added expressive structure** and must be stated as such.

### Oracle embedding (excluded as evidence)

A translation is an oracle embedding if it emits a precomputed DEA verdict or DEA-derived relation, such as a co-control closure or a reachability set. Such a test is run for transparency and labelled **ORACLE-EMBEDDING**. It is never counted as expressibility evidence.

**Informativeness.** Each Regime B success is rated:
- **RESTATEMENT:** the auxiliary rules transcribe the DEA definition clause by clause.
- **REDUCTION:** a non-trivial encoding into native machinery.

## 4 Independence of execution

Target semantics are executed by engines in `harness/engines/` that do not import `dea_ref.py`:

| Engine | Target semantics |
|---|---|
| `datalog.py` | generic stratified Datalog with negation and count/max aggregates (Bertino Prop. 4.1: a CB is a stratified normal program) |
| `bertino.py` | Bertino CB validation and runtime |
| `r2bac.py` | W&L-07 Defs 1–5 |
| `rbac_li.py` | Li Def 3 |
| `rsl99.py` | RFOPL evaluator |
| `lts.py` | Basin-style trace semantics by word enumeration |

Translators in `harness/translations.py` emit target structures only. A static check fails the run if any engine or translator imports `dea_ref`.

## 5 Model classes and regression

- **Enumerated classes:** as in the original package, with corrections.
  - MC-EJ adds revocation.
  - MC-CTRL adds a θJ-late-only interval, making 7^5 = 16,807 models, so that the CTRL-6b pattern lies inside the class.
- **Both readings of Ctrl_θ:** every Ctrl test is evaluated against
  - **DEA-A:** per-instant closure;
  - **DEA-B:** closure of the window union.
- **Regression scenarios** are re-encoded from the historical scripts and evaluated under v0.3.4.3. Each is reported as included, excluded, unavailable or newly constructed:

| Suite | Cases |
|---|---|
| G2 | S1–S12 |
| G3 | M1–M9; M2 and M4 come from the v0.3.4.1 script |
| G4 | A1–A8, L1–L4 |
| NAP | named cases A–D, minimal self-loop, diagnosis-only pair |

## 6 Classification vocabulary

Each cell receives exactly one of:

- **NATIVE-EXPRESSIBLE:** a Regime A translation, executed independently, is preserved in both directions on all tested classes. This is bounded evidence, and cells resting on it carry the label "bounded".
- **EXTENSION-EXPRESSIBLE:** Regime A was not achieved, and a non-oracle Regime B translation is preserved. The cell carries an informativeness rating.
- **FAILED-ENCODING:** the encodings tried were not preserved, and no impossibility proof exists.
- **PROVEN-NON-EXPRESSIBLE (under stated assumptions):** this requires
  1. the target language and semantics,
  2. the translation class,
  3. the model class,
  4. the observables and preservation relation, and
  5. an argument covering **every** member of the translation class.

  Arguments that rely on an external theorem name it and are marked conditional.
- **UNDETERMINED.**
- **SOURCE-UNVERIFIED.**

FAILED-ENCODING is never promoted to PROVEN.

## 7 Preservation

For each model:
- **Forward:** every event DEA permits or makes effective is permitted by the target.
- **Backward:** the converse.

Observables are event-level, never just aggregate counts. Detection (`panic`) and prevention (`cannot_do*`) are reported as separate observables.

## 8 Deviations from the original protocol (00-translation-protocol.md)

| # | Original | RP-1.0 | Reason |
|---|---|---|---|
| D1 | Baseline missing gives `baseline_intact=false` but the run continues | hard fail, exit 2, no results | integrity |
| D2 | "Frozen before any test" | wording withdrawn; pre-execution and self-attested only | no external timestamp |
| D3 | Regime B target functions reuse the DEA evaluator (EJ-3, NAP-5/7, CTRL-4, LED-3, T3-3) | independent engines; reuse is banned and statically checked | oracle |
| D4 | CTRL-2 "compiled B" treated as native | labelled ORACLE-EMBEDDING | precomputes the verdict |
| D5 | DEA Ctrl reference uses per-instant closure only | DEA-A and DEA-B both evaluated | DEA p.8 does not decide |
| D6 | MC-CTRL "gap" option: protocol says 5 options, implementation has 6 | 7 options declared explicitly (adds J_late) | spec/implementation mismatch |
| D7 | LED-1 Regime A described as `panic` | prevention via `cannot_dou`; detection reported separately | R4 violation |
| D8 | Regression declared as G2/G3/G4/NAP; implemented G2 S1–S13 and 9 of 12 G4 cases only | full reconciliation table | coverage |
| D9 | Invariance claims EJ-7, NAP-3, LED-4 stated for "every translation" | re-proved for explicit translation classes or downgraded | proof scope |
| D10 | Wang & Li 2010 replaced by W&L-07 "proxy" in classification cells | 2010 cells SOURCE-UNVERIFIED; W&L-07 reported separately | source fidelity |
| D11 | RSL99 unavailable | RSL99 original inspected and tested | source now available |
