# Change log: original package → remediation package

The original package is preserved unchanged in `original-package/`; hashes are in `ORIGINAL_SHA256SUMS`. All changes below are made in new files. The numbered deviations D1–D11 are defined in `01-remediation-protocol-v1.md` §8.

## 1 Process and infrastructure

| # | Original | Remediation |
|---|---|---|
| 1 | Protocol described as "frozen" | Wording withdrawn; the protocol is self-attested pre-execution only (D2) |
| 2 | Baseline missing: run continues | Exit 2, no output (D1); tested three failure modes |
| 3 | Hard-coded workspace paths | `--baseline` / `DEA_BASELINE`; harness-relative paths |
| 4 | One script that mixes DEA and target logic | `engines/` (5 target engines + Datalog), `translations.py`, `dea_ref.py`; static import check (exit 3) |
| 5 | Regime-B targets reuse the DEA evaluator | Independent engines (D3) |
| 6 | CTRL-2 counted as native | ORACLE-EMBEDDING, excluded (D4) |
| 7 | Single Ctrl reading | DEA-A and DEA-B evaluated (D5) |
| 8 | MC-CTRL: 6 interval options, inconsistent with the protocol's 5 | 7 options, 16,807 models (D6) |
| 9 | Counts reported as "39 results" | 54 comparisons (4 oracle), 6 proof records, 44 regression cases, reported separately |

## 2 Result-level changes

| Original | Original result | Remediated result |
|---|---|---|
| EJ-1/2 (Bertino, coarse) | fwd 40 / bwd 116 fail | Reproduced qualitatively as EJ-A-BER-1 (enlarged class) |
| EJ-3 (Bertino B, `panic`) | preserved | Detection is not enforcement. Replaced by EJ-B-BER (prevention): preserved |
| EJ-5 (W&L coarse) | bwd 140 | EJ-A-WL-1 bwd 608 (enlarged class); **EJ-A-WL-2 (A-IDX) preserved** |
| EJ-6 (Li, revocation) | 128/94 | EJ-A-LI bwd 100 (current state); EJ-B-LI-HIST preserved |
| EJ-7 claim | NOT-EXPRESSIBLE | **Refuted** (PRF-EJ7) |
| T3-1 / T3-2 / T3-3 | fwd 36 / ok / ok (oracle) | Same / same / replaced by T3-A-BER-2 (native) and T3-B-*-HIST |
| DE-1/2 "Bertino / W&L-07" | both fail | W&L-07 failures confirmed. **Bertino is native through `count` (DE-A-BER)**; the original had conflated the two targets |
| DE-3 | preserved | DE-B-WL preserved (independent R2BAC engine with Def 3 ordering) |
| NAP-1/2/6 | fail | Reproduced exactly (26/13,818; 4,202/8,200; 334/13,510) |
| NAP-3 claim | NOT-EXPRESSIBLE | **Refuted as stated**; replaced by PRF-NAP-HANF (class T_loc(r)) |
| NAP-4 | preserved | NAP-R-WSP-PATH preserved; NAP-R-WSP-LABEL added |
| NAP-5 / NAP-7 | preserved (oracle) | NAP-B-BER / NAP-B-BAS-TICK preserved (independent) |
| — | — | New: NAP-B-LI-RH, NAP-B-RSL-RH (role-hierarchy reductions) |
| CTRL-1 / CTRL-5 | fail | Confirmed (CTRL-A-WL-snap, CTRL-A-LI, CTRL-A-RSL-CU) |
| CTRL-3 (Bertino pseudo-roles, "A") | fail | Dropped: reinterpreting roles as controllers is not admissible in Regime A |
| CTRL-4 | preserved (oracle, reading A) | CTRL-B-BER[A] and [B]: each preserved for its own reading only |
| — | — | New: PRF-CTRL-WL-MONO; CTRL-B-LI-RH and CTRL-B-RSL-RH reductions |
| CTRL-6 | "holds: false" | **72/16,807 disagreements** after D6; PRF-CTRL6B classifies this as an architectural ambiguity |
| LED-1 (`panic`) | fail; described as Regime A enforcement | Split into LED-A-BER-DETECT (detection) and LED-A-BER-INST (prevention) (D7) |
| LED-3 | preserved (oracle) | LED-B-BER preserved (independent) |
| LED-4 claim | NOT-EXPRESSIBLE | PROVEN only under A-INST-LOCAL (PRF-LED4, machine-found witness) |
| CTRL-REG / LED-REG | G2 S1–S13; 9 of 12 G4 cases | G2 12+1, G3 9, G4 12+2, NAP 7+1, all matching v0.3.4.3 (D8) |
| Wang & Li 2010 "proxy" cells | W&L-07 used as a proxy | SOURCE-UNVERIFIED (D10) |
| RSL99 | unavailable | Inspected; 6 RSL99 test families, 10 comparisons (D11) |

## 3 Post-protocol additions and fixes made during execution (transparency)

These were made after the first run of the RP-1.0 harness. None changes the protocol file.

1. **Datalog variable convention.** Constants such as `T_adj` were parsed as variables. Variables are now uppercase identifiers without `_`. Unsafe-literal checks now test bindings instead of values.
2. **NAP-R-WSP-LABEL.** When the start state is a goal, the start step must have no admissible user. The first run allowed one (13,131 backward failures). This was an implementation bug.
3. **G4 Case(x) labelling.** Case(x) is now computed once over the complete object record. Incremental union-find had relabelled earlier events, which made A4 and A6 deviate.
4. **G2 expectations.** S8 was corrected to (T, T, T) and S13 to (F, T, F), from the v0.3.4.3 text (p.8–9); the earlier values had been assumed.
5. **Added tests:**
   - EJ-B-LI-HIST and EJ-B-RSL-HIST (after the revocation failure);
   - T3-B-LI-HIST and NAP-B-RSL-RH (to fill crosswalk cells);
   - T3-A-RSL relabelled T3-B-RSL-HIST, because mapping acts to UA is A-HIST.
