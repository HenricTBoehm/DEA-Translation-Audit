# Source manifest / provenance boundaries

**Not copied into GitHub by this protocol PR** (provide to GPT Work as attachments):

- Uploaded `dea-hr1-history-remainder.zip` SHA-256: `69475ff7729c60bb70d4eac8e6c5de03206ae26abd2200fc37a499e0d72c8859`. Contains `DEA-HR-1_controlled-history-truncation.md`, `hr1_remainder.py`, `hr1-regression-cases.json`, `results/hr1-results.json`. The historic results are source claims pending exact reproduction.
- Existing local `DEA_DRHC_P02_Forschungsskizze_2026-11-16.md` SHA-256: `281164128d9c120a0689abc64dd326db4e9e8def8c2b6de7ab16ff1db6eff7fe`. Contextual candidate, not normative.

**Repository inputs** (re-check heads at time of testing):
- P-01: draft PR #7, head `91e842fdae94356ff323f3afb2e99245369108da`.
- Temporal Control Evidence: draft PR #6, head `4c4265b5230bf6010a75c95e17de62c066990bf2`.
- Reproduction audit: draft PR #5, head `eb45248ede423efca4c7ca8ba0afd70d1ef61bde`.
- Poblete comparison: draft PR #4, head `d5a73f9f654b380731d63b961cf8cacb09ecc0bf`. Its real operational control edges are not evidenced.

**Known source caveat:** HR-1's randomized results are sensitive to iteration over Python sets in the original implementation; fixed RNG seed alone is insufficient to guarantee byte-identical figures across hash seeds. Preserve the original code/results, rerun with environment captured, then create a *separately versioned* deterministic correction. HR-1's actual control-history completeness is assumed by fixture attestations rather than generated and independently verified.

No manuscript source was updated. Scientific adoption remains NO-GO.
