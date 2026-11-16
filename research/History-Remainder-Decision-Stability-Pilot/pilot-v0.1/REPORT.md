# Independent pilot v0.1, execution and decision report

Executed 2026-11-16 on Linux x86-64 with CPython 3.12.14. The PR #8 plan is the base of this stacked draft. [Evaluation criteria](EVALUATION_CRITERIA.md) were committed locally before any A–D comparative run.

| Input | Exact Git SHA | Use |
|---|---|---|
| main | 2fc5e7f353f1984e663110e3eb0a0d9e38ba7fa4 | Verified repository state |
| PR #8 | edebea66d8295e323f8aa013c507307b3c5066f8 | Frozen plan, S01–S12 and source checksums |
| PR #7 | 91e842fdae94356ff323f3afb2e99245369108da | P-01 event admission, bindings and effect replay, called directly |
| PR #6 | 4c4265b5230bf6010a75c95e17de62c066990bf2 | Historical-closure and ordered-journey prototype as prior context |
| PR #5 | eb45248ede423efca4c7ca8ba0afd70d1ef61bde | Prior reproduction evidence |
| PR #4 | d5a73f9f654b380731d63b961cf8cacb09ecc0bf | Comparative motivation under its stated evidence limits |

All five PRs were open and Draft on intake. HR-1 ZIP SHA-256 is 69475ff7729c60bb70d4eac8e6c5de03206ae26abd2200fc37a499e0d72c8859. The supplied DRHC note is 281164128d9c120a0689abc64dd326db4e9e8def8c2b6de7ab16ff1db6eff7fe. Both match PR #8. ZIP CRC passes. Exact member hashes are in [SOURCE-MEMBERS.sha256](SOURCE-MEMBERS.sha256). The original sources and archival results are external inputs. Per-run outputs and post-correction results are in [evidence](evidence/).

## HR-1 reproduction and adversarial validity

Unchanged harness, RNG seed 20261116, three PYTHONHASHSEED values (0, 1, 42), 20,000 draws per regime in each run. All named outcomes match the archive. Each generated random report differs in bytes from the others and from the archival report. Sorting the true token set before assigning RNG draws is the sole [deterministic correction](HR-1-deterministic-v1.patch). The corrected runs yield one identical JSON across all three seeds. Exact hashes, runtimes and parameters are in [HR1-RUNS.json](evidence/HR1-RUNS.json).

| HR-1 regime | Corrected false clearance / draws | Corrected false CONFLICT / draws |
|---|---:|---:|
| A, tight attested bound | 0 / 20,000 | 0 / 20,000 |
| B, drop backward-cone coverage | 1,948 / 20,000 | 0 / 20,000 |
| C, state-dependent reset | 75 / 20,000 | 148 / 20,000 |
| D, loose bound label 0.10 | 0 / 20,000 | 0 / 20,000 |
| E, loose bound label 0.30 | 0 / 20,000 | 0 / 20,000 |
| F, bound restricted to cone | 0 / 20,000 | 0 / 20,000 |

Among no-conflict draws, the tight bound blocked 0/9,938. The loose bounds blocked 1,816/9,852 and 4,684/9,931. In the original generator the named 0.10 and 0.30 parameters are multiplied by 0.2 per candidate token. The precision rates are observations of this generator. The qualitative distinction survives all seeds: uncovered history and nonmonotone updates can produce false clearance, and more permissive upper bounds can increase conservative holds without asserting a positive conflict. The draws in different regimes are distinct. These rates do not quantify deployment risk or the causal effect of increasing bound size on an identical population.

CM-R1–R8 reproduced, including the intentional P2 counterexample CM-R6. A backward evaluator independently agreed on 21 controller-set comparisons (concrete, witnessed, bounded on each of the seven admissible cases). P1 is a real gate: removing a seal from the archived positive fixture makes the original transformer return CLEAR outside its preconditions. P3 needs a channel-complete backward cone, including aliases and entering relays. A complete upper certificate is consumed as an assumption. A deliberately false P3 assertion reproduced false clearance in the executable pilot. P4's issuer test is against the upper controller sets. P5 requires separate authentication for actual pre-state witnesses. Merely asserting a possible token as actual can manufacture a conflict. These tests are in [COUNTEREXAMPLES.md](COUNTEREXAMPLES.md).

The pilot uses Z for an attested empty remainder across the relevant cone, B for a scoped upper bound, and U for unproved coverage. U can hold despite a known constant scientific result. A proved actual witness can block in any mode if the event admission and witness evidence are established. The C gate wraps P-01 twice where necessary, once with the witnessed actual seeds and once with the upper seeds plus those witnesses. An intersection only in the latter is a BOUND hold. Missing coverage, invalid reset evidence or lack of issuer independence is a REMAINDER hold. The pilot treats uncovered channels in the conservative reverse cone as blockers until coverage is attested. Relative to the original toy engine, P-01 supplies versioned dependencies, typed signatures and event admission. The temporal cone overincludes safe possible ancestors, including producer influences considered after seal for the purpose of coverage. That may hold cases an exact cone could clear.

## Paired governance experiment

All arms receive the same case data. A and B perform the checks defined for their scope. B checks provenance, mandatory dependency binding, canonical identity and seal/commit agreement before ruling on the roles. C adds effective control and HR-1; D calls precisely the same C implementation and attaches a substantive diagnostic. Model truth comes from a separate backward token query over the concrete synthetic pre-state and the true dependencies, with admissibility and authority as explicit fixture facts. Those concrete historical tokens are unavailable to the arms unless furnished as authenticated evidence.

| Corpus and arm | Control conflicts falsely passed | False CONFLICT reports | Holds among eligible | UNDETERMINED of all | Structurally invalid passed |
|---|---:|---:|---:|---:|---:|
| S01–S12 A | 4/4 | 0/8 | 0/7 | 0/12 | 1/1 |
| S01–S12 B | 4/4 | 0/8 | 1/7 | 1/12 | 0/1 |
| S01–S12 C and D, each | 0/4 | 0/8 | 4/7 | 5/12 | 0/1 |
| Finite A and B, each | 32/32 | 0/64 | 0/64 | 0/96 | 0/0 |
| Finite C and D, each | 0/32 | 0/64 | 42/64 | 58/96 | 0/0 |
| Random A and B, each | 349/349 | 0/651 | 0/651 | 0/1,000 | 0/0 |
| Random C and D, each | 0/349 | 0/651 | 403/651 | 577/1,000 | 0/0 |

Eligible means structurally valid, authorized in the fixture, and free of a concrete modeled control conflict. The one invalid S05 is included in the no-conflict denominator and excluded from eligibility. A/B deliberately lack extended effective-control attribution per the preregistered comparison. Four-eyes compliance and provenance assurance are observed evidence in their own right. Their modeled decisions are not claims that a real team applies no other safeguards.

The bounded enumeration covers the full Cartesian product of six declared factors (96 combinations). The seed-20261116 random arm draws 1,000 times with replacement from these same combinations, 96 distinct tuples. It checks reproducible execution under resampling. It supplies no independent external statistical sample. There was no C/D governance change on 1,108 paired cases, including reasons, witnesses and authority flags serialized as identical bytes. There were also five scientific probes and thirteen adversarial pilot probes, including S01 with independent control and different substantive outcomes and S05 with a counterfactual rubric. Separately, changing the scientific rule in all twelve named cases left the C bytes invariant.

## Substantive information and cost

The world fixture fixes attempt, sealed output, rubric, policy and commit versions. A known finite closed domain permits exhaustive comparison of admissible historic fact assignments. Two valid different-outcome assignments suffice for UNSTABLE. Agreement from samples yields only SAMPLED_STABLE. Empty, misbound or dynamically incomplete worlds yield STABILITY_UNDETERMINED. For this pilot the completeness assertion is a synthetic fixture premise.

| Corpus | Science diagnostic among governance holds | Total modeled scientific facts, ask all versus exact minimal query |
|---|---|---:|
| 12 named, 5 holds | 2 certified insensitive (S03/S08), 2 targeted (S04/S09), 1 unresolved (S12) | 8 → 2 over 4 covered cases |
| 96 finite, 58 holds | 29 insensitive, 29 targeted | 116 → 29 over 58 covered cases |
| 1,000 random, 577 holds | 274 insensitive, 303 targeted | 1,154 → 303 over 577 covered draws |

In S04 the fixed threshold policy changes outcome if the missing calibration fact changes; archive context can vary without altering that outcome. In S09 the separate scientific query is archive context, while the relay-control history still requires governance evidence. S03/S08 need no further modeled scientific fact to establish the candidate outcome's insensitivity. S12 has no justified census. S02/S06/S10 all demonstrate simultaneous stable scientific output and CONFLICT. No governance evidence request was removed. The ask-all column is a transparent substantive reference workload, not a measured retrieval strategy used by HR-1 or comparable to production evidence costs.

| Arm | Declared logical attestation categories | Median isolated time per named case |
|---|---:|---:|
| A | 2 | 1.748 μs |
| B | 7 | 73.801 μs |
| C | 11 | 393.761 μs |
| D | 11 governance + 2 substantive | 521.944 μs |

Five repeats, 1,200 calls per arm per repeat, CPython 3.12.14. D added 128.183 μs per case in this run, about 33%. Counts are logical categories (see the enumerated lists in [PILOT.json](evidence/PILOT.json)). No measured issuer, implementation or human process costs are available. Governance implementation is 97 Python lines including A/B/C wrappers and reuses the pinned P-01 code. The diagnostic kernel adds 55 lines plus scope binding and the adapter in pilot.py. The independent oracle is 111 lines. World enumeration scales with the product of domain sizes; exact smallest nonadaptive queries can require checking subsets of all unresolved variables. Costs can exceed any benefit with expensive or unverifiable coverage.

## Decision

- **Technical reproducibility — GO** for the pinned fixtures and interpreter, with separate deterministic HR-1 replay.
- **Formal viability — CONDITIONAL GO** within the explicit finite scope and subject to authenticated P1–P5, exact protected versions and independently justified world coverage. Fixed resets are monotone under inclusion, so inclusion of witnessed, true and upper states is preserved by fact-scoped propagation; projection at seal and commit preserves inclusion. This explains the conditional gate and is independent of the observed frequencies. Exact finite stability follows from evaluating each admissible world. A sound overapproximation could certify a singleton if nonempty actual worlds are established; this implementation only certifies the exact finite fixture census.
- **Practical incremental value — CONDITIONAL GO for a targeted follow-up trial.** The smallest supported use is an audited version-pinned threshold decision with one unresolved outcome-changing historical fact and at least one alternative missing fact, under certified finite domain coverage. S04 separates the relevant calibration request from the irrelevant archive-context request while HR-1 still holds. This information is absent from the HR-1 control verdict. Net economic or scientific benefit remains undetermined: no real cases, costs, world attestations or comparison to a human sensitivity check were measured. Treat normative integration as **NO-GO** on this evidence. The null hypothesis of no practical net value remains viable.
