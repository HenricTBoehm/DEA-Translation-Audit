# P-01 counterexamples

Start with authenticated (p→a), producer (a) sealing (x) and nominally independent adjudicator (j). Exact inputs, judgments, witnesses and missing evidence are in [RESULTS.json](RESULTS.json).

| Case | Minimal change | Outcome |
|---|---|---|
| RA1 / A01 | (p→r@1) where (r@1) is the mandatory rubric | Identity-only clear. P-01 gives CONFLICT with (p) and rubric evidence. |
| RA4 / A04 | (p→q→r@1), with (r@1) an indirect mandatory input | P-01 gives CONFLICT with a dependency chain. |
| RA2 / A02 | Effective control of the still-bound (r@1) is acquired between seal and commit | P-01 gives CONFLICT. |
| A13 | Seal pins (r@1), evaluation and commit both use (r@2) | Legacy clear with stable snapshots. P-01 gives MODEL_INVALID. |
| A20 | Seal pins the rubric role to (r@1), closure binds (r@1) only as commentary | MODEL_INVALID. Checking version membership alone misses the substitution. |
| RA5 / RA6 / A11 / A14 | Exact criteria reset, credential-only reset, unproven result of reset, or upstream reset after propagation | Only the exact proved target/channel neutralization clears the covered effect. |
| A08 / A16 | Withhold authentication for the edge or required dependency link | UNDETERMINED, with no positive witness. |
| A07 / A15 | Leave the dependency certificate open, without or with a supported witness | UNDETERMINED or CONFLICT respectively. |
| A12 / A21 | Change the protected snapshot or control graph between evaluation and commit | UNDETERMINED. A fresh evaluation is required. |
| B01 / B11 | Omit the seal, then consider production already known to follow commit | The old harness gives UNDETERMINED twice. P-01 separates missing from impossible. |
| B03–06 / W1–2 | Duplicate production, exact retransmission, ID equivocation or confirmed coordinate collision | Exact retransmission is idempotent. Immutable conflicts yield MODEL_INVALID. |
| C11 / B08–09 | Same tick with unknown rank, versus signed reverse order | UNDETERMINED versus MODEL_INVALID. |
| B10 | A commit ID attests distinct root maps | MODEL_INVALID independently of control effects. |
| W3 / B15 | Submit an unverified late-seal claim, or an exact unverified copy of an authenticated seal | The unmatched claim yields UNDETERMINED. The matched copy is resolved. |

A stored event ordered after commit (A03/A22) has no effect on the bounded replay. The archived draft evaluator rejects an event beyond its declared interval. This domain distinction explains its A03 result. A09 explicitly admits a typed read with no control effect. The Poblete work supplies motivation for RA1, while its actual control edges remain undetermined.
