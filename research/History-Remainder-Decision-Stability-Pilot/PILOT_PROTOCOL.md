# Pilot protocol (proposal; no test results)

## Compared methods

A. Nominal four-eyes separation.
B. A plus event provenance, exact seal/criteria version and authenticated binding checks.
C. B plus P-01 effective-control gate and HR-1 remainder (Z/B/U), preserving governance verdicts.
D. C plus independent Decision Stability **diagnostic**, with governance verdicts bit-identical to C.

Use paired cases with identical available evidence and clearly stated extra prerequisites. Baselines must be implementable comparators, not deliberately weak caricatures.

## Predeclared synthetic scenarios (expected properties; NOT executed)

| ID | Situation | Check |
|---|---|---|
| S01 | Independent actor and adjudicator, full certificates | No artificial blocker |
| S02 | Common principal controls producer and mandatory rubric | C must expose CONFLICT; stability must not override |
| S03 | Missing prehistory, all certified allowable worlds share scientific outcome | G stays UNDETERMINED; T may be stable if coverage certified |
| S04 | Missing prehistory, admissible worlds yield different outcomes | G stays UNDETERMINED; T unstable |
| S05 | Seal pins rubric@1, eval/commit both use rubric@2 | MODEL_INVALID regardless of stability |
| S06 | Bound same rubric version controlled post-seal before commit | Compare effective-control witness |
| S07 | Read-only rubric knowledge without effective control | No control witness solely from reading |
| S08 | Coarse but sound historical upper bound with spurious blockers | Overblocking and refinement cost |
| S09 | Pre-window principal controls in-window relay (bootstrap leak) | No false CLEAR from a partial bootstrap |
| S10 | Credential reset while planted criteria effect survives | Channel-specific remainder must persist |
| S11 | Independently proved exact neutralization | Negative result may be possible, subject to other gates |
| S12 | Dynamic evaluator dependency or alias is unresolved | No assumed complete closure |

For S03/S04, use a **fixed sealed policy**; vary only admissible unobserved history/environment facts. Separately tag hypothetical changes of the policy/rubric as counterfactual studies (not valid attempts).

## Measurements and rules

Record confusion matrices against independently constructed synthetic ground truth; distinguish FALSE_CLEAR from false CONFLICT and conservative holds. Report Remainder Block Rate, BOUND/REMAINDER split, fraction of governance-UNDETERMINED cases where T adds useful discrimination, calls for additional attestations, time/CPU, certificate production effort, scenario coverage and any unsoundness. Include baseline arms A/B and an ablation C vs D. Every figure needs denominator, seed, Python version, PYTHONHASHSEED and exact source/hash.

Start with named countermodels; then exhaustively enumerate a small finite domain; only then run randomized tests. Randomized generation MUST be deterministic across hash seeds (stable iteration order before RNG), or report non-reproducibility. Record difference between a negative witness proof and a merely sampled absence of a witness.

Pre-register success/failure criteria **before** viewing comparison results: D should preserve every C governance verdict while classifying some unresolved cases by verified substantive sensitivity with tolerable cost. If D adds no reliable actionable information, recommend no integration. Formal guarantees require a separate proof; empirical counts are not proofs.

## Deliverables for GPT Work

Versioned code, oracle, cases, exact command line, output JSON, SHA256SUMS, counterexamples, assumptions, comparison report, decision table and open obligations. Publish via a NEW Draft PR; never edit HR-1 originals or silently incorporate this proposal into the main DEA manuscript.
