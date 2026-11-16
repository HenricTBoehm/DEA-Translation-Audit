# Review and execution notes

Reviewed on 2026-11-16 using Python 3.12.14 (Linux x86-64, standard library). CPython 3.13.5 also reproduced the machine report byte-for-byte. This is an executable candidate for two amendments, with mathematical assumptions stated in the [specification](DEA-v0.3.5.1-Precision-Amendment-P01.md).

| Source | Exact Git commit | Observed status |
|---|---|---|
| main including ADR-001 | 2fc5e7f353f1984e663110e3eb0a0d9e38ba7fa4 | Base for P-01 |
| PR [#4](https://github.com/HenricTBoehm/DEA-Translation-Audit/pull/4) | d5a73f9f654b380731d63b961cf8cacb09ecc0bf | Open Draft, comparison quick regressions PASS |
| PR [#5](https://github.com/HenricTBoehm/DEA-Translation-Audit/pull/5) | eb45248ede423efca4c7ca8ba0afd70d1ef61bde | Open Draft, quick checks PASS, earlier full reproduction reviewed |
| PR [#6](https://github.com/HenricTBoehm/DEA-Translation-Audit/pull/6) | 4c4265b5230bf6010a75c95e17de62c066990bf2 | Open Draft, seven unchanged tests PASS |

Both ZIP CRC checks passed, all 11 supplied draft manifest entries matched, and the standalone precision note matched its ZIP member byte-for-byte. [SOURCES.sha256](SOURCES.sha256) contains archives, the optional note, every member, and the Git source fingerprints. The exact executable SHA and regenerated result of each source run can be traced to that manifest.

| Test area | PASS | FAIL | UNDETERMINED or NOT EXECUTED |
|---|---:|---:|---|
| Original precision-check executable | 21 | 0 | Defined unknown verdicts reproduced as expected. JSON byte-identical. |
| Original draft executable | 32 | 0 | Defined unknown verdicts reproduced as expected. JSON byte-identical. |
| Original PR #6 | 7 | 0 | Includes its 343 ordered traces. |
| Draft compatibility under explicit adapter | 32 | 0 | Same expected statuses. |
| RA1–RA10 | 10 | 0 | RA7 unresolved as expected. |
| C11, C12, C19, C29–C32 and W1–W4 | 11 | 0 | G-B statuses compare with the precision proposal. |
| New targeted cases | 37 | 0 | Explicit model verdicts are in RESULTS.json. Legacy comparison omitted for three P-01-only input encodings. |
| Independent finite checks | 591 | 0 | 343 coordinate variants, 216 influence traces and 32 authenticated subsets. 211 inclusion pairs separately checked. |
| Prior full ADR/RP/VP reproduction | — | — | NOT EXECUTED in this run. Read the pinned prior report in PR #5. |
| Draft case generator, TeX/PDF rebuild, production attestation and isolation | — | — | NOT EXECUTED. The case generator is a build utility; tests consumed the original frozen case JSON. |

The precision audit's original **literal Boolean** comparison fails six of the seven C cases and W3. This is a failure of that literal reading, while the original executable's **proposed** interpretation passed all its own assertions. The delivered draft reference executable already returns the intended unknown statuses for its 32 fixtures. New cases expose limitations that it does not cover, including B11 where it returns unknown before checking the known contradictory production and commit.

The draft adapter preserves IDs, original case expectations and clocks. It supplies empty explicit roots and pins for the identity-only fixtures, authoritative snapshot binding for the supplied fixture versions, and mirrors the existing reset scope assertion as a synthetic neutralization assertion where the original evaluator grants that semantics. These additions are assumptions of the adapter. The RA adapter maps each selected rubric to a fixed synthetic version and uses that version in both seal and commit. The separately named A13 tests deliberate version replacement. In W2 the synthetic non-lifecycle claim is represented by a read marker at the same authenticated coordinate. W4's WELL_FORMED label becomes VALID. A and B narrow the declared candidate and leave the archived originals intact.

The forward evaluator and backward comparison share typed inputs, normalization, attestation interpretation and immutable field checks. The comparison searches concrete representative rank placements independently, computes dependency closure by fixed point, and derives influence through recursive queries on event prefixes, without running the forward reducer. Agreement includes the producer set, decision set and principal/target witnesses. Both share the abstract effect policy and its assumptions. The bounded checks do not establish runtime security or scientific adoption.

PR #6 models temporal journeys and historical closure at a boundary. P-01 consumes versioned residual effects and channel-specific resets, plus versioned mandatory decision dependencies, and separates a missing input from an immutable contradiction. P-01 keeps the research streams separate.
