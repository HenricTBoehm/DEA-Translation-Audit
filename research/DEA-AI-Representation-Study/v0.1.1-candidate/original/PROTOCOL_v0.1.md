# DEA as an AI Working Formalism — Representation Study Protocol v0.1

| | |
|---|---|
| **Status** | DRAFT for review. **Not frozen. No language model has been run.** Build and scoring pipeline are executable and self-tested (synthetic responders only). |
| **Date** | 2026-11-16 |
| **Ground truth** | Conditional oracle `justified()` of Gap-Register v0.1.2 candidate, Draft PR #13, commit `b1631406c9434a214da98b2a49115be26a40c7db`; vendored byte-identically (`oracle.py` `df0a4230…ce18`, `cases.py` `5a65c4d5…6858`, `PUBLIC_CASES.json` `3f07e797…ca55`; full hashes asserted in `build.py`). |
| **Relation to earlier work** | Follows the bounded null result of Phases A–C (PR #14–16): no semantic or technical DEA advantage was shown. This study asks a different question and makes no claim about DEA semantics. |
| **Normative DEA adoption** | NO-GO (unchanged). |

---

## 1. Question and hypotheses

**Research question.** Given the same information, does stating the decision rules in DEA form make AI systems decide more reliably, more checkably or more cheaply than an equally precise established representation?

The rule set is fixed: SR-1 plus the finite event grammar of PR #13. Only the **representation** varies. The study therefore tests a representational advantage, not semantic novelty (which Phases A–C did not find).

| ID | Hypothesis | Contrast |
|---|---|---|
| **H1 (primary)** | DEA form lowers the rate of unjustified releases compared with an established structured form | C vs B |
| H2 | Any C advantage comes from DEA terminology rather than from the structure of the rules | C vs C′ |
| H3 | Structured forms beat precise natural language | B vs A, C vs A |
| **H0 (strong null)** | C is no better than B on any loss component | — |

The study must be able to support H0, and H0 is reported with the same weight as H1. A C advantage over A alone is **not** evidence for DEA. It only shows that structure helps.

## 2. Conditions

| Condition | Content | Author |
|---|---|---|
| **A** | Precise natural-language rules. No DEA vocabulary. | Draft: Co-scientist. Revise before freeze. |
| **B** | Established structured form: state model, transition tables, ordered decision checklist. No DEA vocabulary. | Draft: Co-scientist. **Should be revised by someone not involved in DEA** (O2). |
| **C** | DEA formalization: roles, `Ctrl`, `Lin`, `EffectiveControllers`, `Bound*`, `J*`, `Exec`, `HistoryClosed`, `RecordComplete`, `WellFormedEvents`, verdicts CLEAR/CONFLICT/UNDETERMINED/INVALID. | Draft: Co-scientist. **DEA fidelity must be reviewed by Henric** (O1). |
| **C′** | C with every DEA term replaced by a neutral symbol (`Q1…Q11`, `Op1…Op10`, `V1…V4`, `Role-1/2`). **Generated mechanically from C**, never edited by hand. | — |

**Held constant across all four conditions:**

1. **One source.** All texts come from `source/spec.py`. Each rule R1–R12 is written once per condition, side by side, with the same visible tag `[Rk]`.
2. **Same answer schema.** The answer instructions are byte-identical in every system prompt: verdict ∈ {RELEASE, BLOCK_CONFLICT, BLOCK_UNDETERMINED, INVALID}, a witness object, missing reasons, and a justification. No condition gets a richer output vocabulary.
3. **Same information.** Evidence is rendered per condition from the canonical PR #13 wire. Every rendering must parse back to the identical wire bytes (E2).
4. **Same footer and record order** (by id).

**Important limitation of C.** C states SR-1 in DEA vocabulary, including SR-1's bind-time route, which P-01/D1 does not contain. C is therefore **not** D0 or D1. The study tests whether the DEA way of *writing* rules helps, not whether DEA's own decision semantics are right.

## 3. Items

| Pool | Source | Size | Use |
|---|---|---|---|
| P | PR #13 public cases | 31 distinct views (38 executions): 6 CLEAR, 12 CONFLICT, 5 UNDETERMINED, 8 INVALID | Calibration and pipeline only |
| G | PR #13 generated histories (`verify.py`, 144) | 141 distinct views: 83 CLEAR, 10 CONFLICT, 48 INVALID | Calibration only |
| **H** | **Private holdout**, built by an independent custodian under PR #13 `HOLDOUT_PROTOCOL.md` | ≥ 48 views per difficulty level, stratified **12 CLEAR / 12 CONFLICT / 12 UNDETERMINED / 12 INVALID**. UNDETERMINED covers all three reasons. CONFLICT covers both witness routes. | **Only confirmatory pool** |

All of P and G are public on GitHub and possibly in training data. **They carry no confirmatory weight.** The public pools are also unbalanced (only 5 UNDETERMINED), so they cannot test the abstention hypotheses.

**Difficulty.** The PR #13 histories are short. If current models solve them in every condition, nothing can be measured. The custodian therefore builds H at two lengths:
- **H-base:** histories as in PR #13.
- **H-long:** 2–3× more events, with distractors that do not change the verdict (layout writes, rights on unread documents, rights for q, retracted rights). The oracle verifies each one.

Both lengths are scored. The difficulty parameters are fixed in the pilot (§5.2).

## 4. Equivalence checks (before freeze)

| Check | Method | Status |
|---|---|---|
| E1 Rule coverage | Each tag R1–R12 occurs exactly once per condition | **PASS** (`build/EQUIVALENCE_REPORT.md`) |
| E2 Information equivalence of evidence | Render → parse → canonical wire, compared byte for byte, for all items × conditions | **PASS**, 0/688 failures |
| E3 Vocabulary separation | No DEA lexicon in A, B or C′ (rules and evidence) | **PASS** |
| E4 Rule equivalence (human derivation check) | Two people, independent of each other, each get one representation per item and nothing else. Each derives the verdict for 20 stratified items. Required: ≥ 95 % agreement with the oracle in **every** condition. A miss is traced to its rule and fixed in that condition. | **NOT EXECUTED** |
| E5 Length | Rule text max/min ≈ tokens ≤ 1.5. Total prompt length is also logged as a covariate. | 1.466 (A longest). Revisit after O1/O2. |
| E6 Defect rule | If a rendering contradicts `oracle.py`, the rendering is the defect. It is fixed before freeze, in that condition only. The oracle is not changed to fit a text. | Applies |

E4 is the real guarantee of "equally precise". E1–E3 are necessary but not sufficient: a rule can be present and still be stated more clearly in one condition.

## 5. Execution

### 5.1 Model runs

- **Models.** At least 3 models from at least 2 vendors, with version IDs pinned. Record whether a model was used during DEA development. Such models are reported separately and also excluded in a sensitivity analysis.
- **Calls.** One call per (model, condition, item, sample). System prompt = representation, user message = evidence. Fresh context, no tools, no retrieval. Output capped at 1,024 tokens.
- **Samples.** k = 5 per cell at the vendor's default temperature. The decoding settings are logged.
- **Order.** Call order is randomized. Conditions are interleaved, not run as blocks.
- **Logging.** Raw text, tokens in/out, latency, and model/version for every call. Format as in `score.py`.

### 5.2 Pilot (calibration, before freeze)

1. **Smoke test.** At most 5 public items per condition. Only schema validity is checked. Verdicts are not looked at.
2. **Difficulty calibration.** Condition **A only**, on P, G and a public H-like sample built with the holdout generator. Target: A's accuracy between 50 % and 85 %. Above 90 %, the H-long parameters are raised. B, C and C′ are **not** run in calibration, so no condition can be tuned toward a result.
3. **Endpoint check.** If A's pooled unjustified-release rate in calibration is below 5 %, the primary endpoint switches to `wrong_verdict` before freeze. Unjustified release then becomes the first secondary endpoint. This switch is the only one allowed.

### 5.3 Confirmatory run

Only on H, after freeze. Contestant prompts are frozen before H is revealed to the runner. The custodian scores. Results are reported in full, including any null or adverse result.

## 6. Outcomes

Each response yields binary loss components. All are computed automatically against Ω_just by `score.py`.

| Henric's criterion | Operationalization | Denominator |
|---|---|---|
| Fewer unjustified releases | **`unjustified_release`** (primary) | justified non-CLEAR |
| Missing premises recognized | `abstention_reason_wrong`: BLOCK_UNDETERMINED without the correct reason, or with a false reason | justified UNDETERMINED |
| Fewer inadmissible inferences | `unsupported_conflict`, `false_invalid` | justified non-CONFLICT, non-INVALID |
| More checkable justifications | `conflict_witness_not_verified`: the cited witness (principal, version, route, required record ids) must match an oracle witness in replay | reported BLOCK_CONFLICT |
| Effort | Output tokens and latency to a correct result (descriptive) | correct responses |
| Availability | `false_hold` | justified CLEAR |
| Robustness | `schema_failure` (scored as NO_DECISION), `missed_invalid`, `wrong_verdict` | all / justified INVALID / all |

A truth-relative count (`actual_conflict_released`) is reported separately. X-TRUST stays isolated, because no condition can pass it from the given evidence.

**Not verified in v0.1:** the proof behind RELEASE and INVALID. Only the verdict is checked there. This is recorded as `UNVERIFIED`.

## 7. Analysis and decision rule

- **Primary model.** Mixed logistic regression on justified non-CLEAR items in H: `unjustified_release ~ condition + length + (1|item) + (1|model) + (1|model:item)`. Twin views count once.
- **Contrasts.** C−B (primary, two-sided α = 0.05). C−C′, B−A and C−A are secondary, with Holm correction.
- **Componentwise rule** (consistent with `DIFFERENTIAL_HYPOTHESES.md`). A **representation advantage of C over B** is claimed only if all of the following hold:
  - the primary contrast favors C significantly,
  - no other loss component is significantly worse for C,
  - `false_hold` is non-inferior with a margin of 5 percentage points,
  - the advantage replicates in both H-base and H-long.
- **Other outcomes.** They are reported as one of: *parity*, *DEA deficit* (B better), *crossed* (trade-off, with the affected components named), or *inconclusive*. A terminology effect (C better than C′) is reported separately from a structure effect (C′ ≈ C better than B).
- **Power.** Before freeze, a simulation from the pilot rates sets H's size and k. If the required size is not feasible, the study is labeled exploratory before any confirmatory run. This is obligation O5.

## 8. What this study cannot show

- **Semantic advantage.** All conditions encode the same rule.
- **Correctness of DEA's own semantics.** C ≠ D0/D1.
- **Other users.** It says nothing about human users, and nothing about rules other than SR-1 in this finite domain.
- **Translation and integration.** Natural language → executable policy is not tested. That is the separate integration hypothesis, worth testing only if H1 holds.
- **Contamination.** Private items limit it but cannot rule it out for vocabulary and style. C′ controls for recognition of the terms.

## 9. Open obligations before freeze

| # | Obligation |
|---|---|
| O1 | Henric reviews C for DEA fidelity. In particular: `MayExecute` used for "may choose the score", `Lin`/`EffectiveControllers` used for authorship lineage, and the role names. Changes go into `spec.py`; C′ is regenerated. |
| O2 | An author not involved in DEA revises B and may restructure it, provided E1–E5 still pass. |
| O3 | Run the E4 human derivation check and fix any defects (E6). |
| O4 | Appoint a custodian, then build and seal H-base and H-long under `HOLDOUT_PROTOCOL.md` with the quotas in §3. |
| O5 | Run the pilot (§5.2), the power simulation and the endpoint check. Pin models and decoding. |
| O6 | Write a freeze record: hashes of `source/spec.py`, `build/representations/*`, `score.py` and the vendored oracle, plus the approver and date. |

**Stop rules.** Stop, and report the reason, if any of the following happens:
- E4 does not reach 95 % in every condition after two revision rounds,
- H cannot be built with the required strata,
- a representation is changed after confirmatory outputs have been seen,
- the custodian cannot be kept separate from the people who write the representations.

## 10. Files and reproduction

```
python3 build.py      # representations, items, prompts, equivalence report  → build/
python3 selftest.py   # scoring pipeline vs. synthetic responders           → build/selftest/
python3 score.py RESPONSES.jsonl OUTDIR
```

Python 3.10+, standard library only. `build/prompts/{A,B,C,Cprime}.jsonl` hold 172 public calibration prompts per condition, ready for the pilot smoke test.
