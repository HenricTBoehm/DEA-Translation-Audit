# DEA audit execution report

Run date 2026-11-16, Linux x86-64, CPython 3.12.14, standard library only. Wall times reflect concurrent jobs on this host. `bash`, `patch`, `sha256sum` and `cmp` are the other verification dependencies. The baseline PDF digest was verified before either harness was run. No private PDF was copied into either PR.

## Repository inventory at start

| Ref or package | Commit | Observed state |
|---|---|---|
| `main` / remote HEAD | `2fc5e7f353f1984e663110e3eb0a0d9e38ba7fa4` | 56 tracked files, no workflow |
| `import/rp-1.0-baseline` | `0e905d1fc26f7272a19814a1fb1876815ca24d77` | PR #1 merged as `56f55c4a924b4dd4e168fa0f9f20aa76d468df13` |
| `audit/vp-1.0-verification-review` | `1557b84e58a57b1a44122007735620ccc1322457` | PR #2 merged as `de53392dd4875932776fdad2686a2e8bb91a6a8a` |
| `research/adr-001-causal-control-proposal` | `b483fde801cedfaf04de652abc7c50a03808de7d` | PR #3 merged into the starting `main`; ADR still non-normative |
| `research/poblete-dea-comparison-2026` | `fb542df11e513faa6a4cc72fd37088f06c1c114f` | PR #4 was the sole open PR, Draft; 67 tracked files, no workflow |

RP includes a protocol, report, mapping, original source subpackage, independent target engines, harness, and two result JSONs. VP includes a verifier, check results, crosswalk corrections, five unapplied patch groups, notes, and source ZIP. ADR includes the proposal, standalone harness, separate named fixtures, result JSON and source ZIP. Poblete adds the two scripts, two result JSONs, crosswalk, comparison/delta, docs and source ZIP. [Original manifests](ORIGINAL_MANIFESTS.txt) record 29 RP, 7 nested RP, 14 VP, 5 ADR and 8 Poblete expected checksums. All passed. ZIP CRCs and member bytes matched the tracked copies of 30 RP, 15 VP, 4 ADR and 7 Poblete substantive files. ADR and Poblete each retain one bytecode member only in the original ZIP.

## Commands and results

| Area | Command or check | Observed |
|---|---|---|
| ADR-001 | In `research/ADR-001`, `sha256sum -c SHA256SUMS`, then `python3 adr001_ctrl.py --out /tmp/adr001-results.json` | PASS, exit 0 in 10m38.559s. 11 named, 470,596 exhaustive and 20,000 seeded random models. All archived checks reproduced with zero invariant violations. JSON matched byte-for-byte. |
| Independent ADR | `python3 research/verification-runs/2026-11/check_adr001.py` | PASS, 11 fixtures / 100 decisions with witness sets. 2,932 random cases have invalid event order. |
| Poblete | In the comparison folder, `sha256sum -c SHA256SUMS` and `PYTHONPATH=../ADR-001 python3 poblete_adr001_check.py --out /tmp/poblete-adr001-results.json`, likewise `poblete_v035_check.py --out /tmp/poblete-v035-results.json` | PASS, 0.298 s and 0.074 s, both JSON comparisons byte-identical. PB-3v remained inadmissible. |
| Typed Poblete | `bash research/Poblete-DEA-Comparison/check_regressions.sh` | PASS, rejects three malformed transitions, tests eight evidence decisions. |
| RP-1.0 | `python3 RP-1.0/harness/run_audit.py --baseline "$pdf" --out "$scratch/rp/remediation-results.json"` with verified absolute PDF path | PASS in 4m38.339s, all 44 expected regressions and six machine checks match; 54 comparisons include four oracle embeddings excluded from native expressiveness claims. 25 of the 50 non-oracle translation rows contain expected failures in one or both directions. Countermodels byte-identical. RP results differ only at `meta.python` (3.14.4 vs 3.12.14). |
| VP-1.0 original | `python3 VP-1.0/verify.py --baseline "$pdf" --package-zip "$zip" --out "$scratch/vp-original.json"` | FAIL, exit 1 in 0.800s. Flat archive triggers missing prefixed manifest. No result JSON. All five standalone patch groups passed dry-run against RP. |
| VP v1.0.1 | `bash VP-1.0/verification-v1.0.1/run.sh --baseline "$pdf" --package-zip "$zip" --out "$scratch/vp-v1.0.1.json"` | PASS, exit 0 in 6m41.359s. R6 reproduces RP semantics. 40 of 41 original check records are identical and only R6 differs. The archive digest differs from historical VP provenance. |
| CI | `bash research/verification-runs/2026-11/check_repository.sh quick` | PASS locally both on the technical tree and the synthetic combined PR tree. GitHub PR workflow [run 43869640730](https://github.com/HenricTBoehm/DEA-Translation-Audit/actions/runs/43869640730) succeeded at the first technical commit. Manual GitHub dispatch depends on workflow presence on default branch. |

`pdf` and `zip` are described in [REPRODUCIBILITY.md](REPRODUCIBILITY.md). Check-level statuses, SHA-256 and byte-vs-semantic comparisons are in [RESULTS_COMPARISON.json](RESULTS_COMPARISON.json).

## VP result interpretation

The standalone verifier emitted 25 PASS, 9 FAIL, 6 UNDETERMINED and 1 NOT EXECUTED records, matching the original status counts. The nine failed claim checks are reproduced audit findings. The separately reviewed Wang & Li 2010 source is documented in [WANG_LI_2010.md](WANG_LI_2010.md); W1 remains unexecuted in the inherited verifier procedure. The first corrected attempt produced the same JSON but returned exit 2 during wrapper cleanup after the wrapper was edited mid-run. The final separate invocation used the finished wrapper and exited 0, with identical result JSON. The runner confines the verifier's temporary files to its own cleanup directory.

## Supplemental ADR chronology check

The standalone chronology-filtered rerun retained 17,068 random models and found zero violations across the five implemented invariant counters (18.158 s). The finite enumerator produces valid chronology by construction. The byte-identical historical random result includes all 20,000 draws. This filtered run provides evidence for the admissible subset and preserves the original test domain as an archival fact.

## Source-bound scope of the draft gate

Two independently located copies of the non-adopted DEA v0.3.5 working draft (2026-11-16) matched SHA-256 `636c3c2b9e702e06a600d07462b0f90436451e55a9f1374e1f99ff5f313ae566`. The targeted read covered pp. 10–14 and Appendix D. Equation (16) binds a positive witness to an object's own production event and seal. Equation (17) also requires disposition authority and a complete record. This supports the typed split between execution output and verification report, and the control-gate label in the fixture. The draft already identifies invalid chronology (CM11), incomplete records (CM12), separate identity evidence (CM13) and partial resets (CM14). The new ADR finding concerns executable coverage and the 2,932 invalid samples in the archived harness. It does not establish a specification defect in the draft's express requirement. In the draft's Appendix D, CM8 remains unresolved pending reset order and scope.

The [publisher HTML](https://www.mdpi.com/2079-9292/15/21/5135) sections 6 and 10 describe the report-stage checkpoint and the study's authority/provenance limits. The evidence available from the paper leaves actual conflicts and overall disposition authority undetermined.

## Scientific scope

See [counterexamples and proof scope](COUNTEREXAMPLES.md), [open obligations](OPEN_OBLIGATIONS.md), and the direct [Wang & Li 2010 source review](WANG_LI_2010.md). The frozen RP/VP/ADR evidence remains intact. The technical correction changes VP extraction and what R6 tests. The separate typed Poblete fixture changes the model of the report, under explicitly hypothetical control evidence.
