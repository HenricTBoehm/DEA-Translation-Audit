# DEA as an AI Working Formalism · Representation Study v0.1.1

**DRAFT REVISION — NOT FROZEN — NO CONFIRMATORY MODEL RUN. Partial candidate pending verified v0.1 intake.** This protocol component can be reviewed independently. The original ZIP and its Python modules were unavailable as bytes in this run. The treatment source, builder, and Python scoring suite have not been revised or verified.

## Question and conditions

Does a DEA-style description of the same bounded SR-1 rules improve correctness, verified justification or efficiency? Results can favor either representation, support equivalence, or remain inconclusive. The prior decision/provenance/operational pilots found no independent DEA advantage in their bounded profiles. C describes SR-1 with DEA-style notation; D0 and D1 do not supply treatment answers.

| Arm | Intended treatment |
|---|---|
| A | Precise natural language, identical assumptions and proof requirements |
| B | Strong declarative state/transition specification with explicit guards and ordered decisions |
| C | DEA-style terminology and structure, audited as study notation |
| C′ | Exact C structure with intelligible, DEA-neutral identifiers |

Primary C–B compares useful structured representations as packages. B–A assesses this state/transition representation against precise prose; wording and organization also differ. C–C′ tests the effect of this terminology substitution conditional on C's structure. It cannot separate branding from differences in lexical associations and tokenization. A cryptic original control may be used only in a separately declared public pilot; C′–cryptic is an exploratory contrast of informative versus opaque names with structure fixed. No additional main-study arm.

## Constant input and stopping boundary

Across arms only the rule section varies. Serialize evidence once using a frozen UTF-8 neutral canonical schema with stable row locators, and inject the same bytes in each prompt. Common legend explains all keys, numeric or null ranks, both closure flags, unauthenticated information semantics and row locators. Common response syntax, system message, delimiters, examples (prefer none), tools/retrieval policy, budget, language and sampling parameters. Hash actual sent bytes per arm/item and verify evidence segment equality before submission. No decoder mode privilege unique to an arm. Condition-specific evidence renderings may be tested later, under a separate package-effect question. Measure actual per-model tokenizer lengths and report remaining input-length imbalance. Do not pad with irrelevant text to hit length parity.

The original R1–R12 are frozen pending intake. Preserve every rule by an explicit old-to-new semantic map, not by copying headings alone. No change to the frozen oracle, event grammar, model semantics or historical packages. The public B outline in EQUIVALENCE_REPORT.md is a specification aid pending the R1–R12 crosswalk, not a released prompt. Use the checked PR #13 SR-1 policy and exact version bounds as the reference. See the equivalence report, scoring contract and statistical plan before selecting models or cases.

The public calibration pool and synthetic checker fixtures may diagnose implementation defects only. E4, independent B review, Henric's C review, O1/O2 and authorized assessor custody are gates. No private holdouts were made, and no model run was performed for this revision. After these gates, a bounded pilot can test logistics and measurement on public material. It cannot support a confirmatory representation claim.
