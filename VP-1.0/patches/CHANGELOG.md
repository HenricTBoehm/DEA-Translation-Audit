# Verification patches VP-1 … VP-5 (against RP-1.0)

The patches apply to a **copy** of the extracted RP-1.0 package. The originals are left untouched: `dea-v0343-remediation/`, its zip and `original-package/`. No patch touches the DEA v0.3.4.3 baseline or the protocol `01-remediation-protocol-v1.md`, whose SHA is unchanged.

Apply and run:
```
unzip -q dea-v0343-remediation.zip -d /tmp/vp
for p in dea-v0343-verification/patches/*.patch; do patch -d /tmp/vp/dea-v0343-remediation -p1 < "$p"; done
python3 /tmp/vp/dea-v0343-remediation/harness/run_audit.py --baseline <DEA_v0.3.4.3 PDF> --out /tmp/vp/out/remediation-results.json
```
Expected output: `patched-remediation-results.json`, SHA-256 `44be72b5…6963`.

| ID | File | Defect (verification check) | Change |
|---|---|---|---|
| VP-1a | `engines/rbac_li.py` | E2, C4, B8: cyclic RH accepted although Li p.10 requires RH* to be a partial order | `check_partial_order(RH)` added; `auth_perms` raises `ValueError` on a non-trivial RH* cycle |
| VP-1b | `engines/rsl99.py` | E3, C4, B8: same for RSL99 (p.47) | `Snapshot` raises on a non-trivial RH* cycle |
| VP-1c | `translations.py` | consequence of VP-1a/b | `_rbac_state_guard` on `tr_ctrl_li_rh`, `tr_ctrl_rsl_rh`, `tr_nap_li_rh`, `tr_nap_rsl_rh`: an invalid image returns the observable `INVALID_TARGET_STATE`, so the comparison fails visibly instead of crashing |
| VP-2 | `run_audit.py` | C5: the PRF-CTRL-WL-MONO pair m0/m1 does not exclude a translation that writes (y, z) for every z on an edge x→y | pair replaced by m1 = {p→a, p→j} vs m2 = {p→a, o→j}; GENERICITY assumption added to the status, assumptions and argument |
| VP-3 | `run_audit.py` | B1: the PRF-NAP3 check only executed the R3-violating LABEL reduction | `r3_image` (an R3-respecting, element-local image) is now executed and must separate m1/m2 |
| VP-4 | `03-translation-specification.md` | E1: §0 described W&L runtime as "extends to a valid plan" | text corrected to Def 5 as implemented |
| VP-5 | `run_audit.py` (`g2_li`, static check) | R5: the regex missed non-`import` references; `g2_li` crashed under VP-1 | the static check flags any occurrence of `dea_ref` outside the module docstring; `g2_li` returns `INVALID_TARGET_STATE` on cyclic RH |

## Effect on results (original vs patched)

| Item | Original RP-1.0 | Patched |
|---|---|---|
| NAP-B-LI-RH | preserved (26,262) | **not preserved**: 81 forward and 324 backward failures, all on the 324 MC-NAP models with a cycle among allowed edges (minimal: 0⇄1, no goals) |
| NAP-B-RSL-RH | preserved | **not preserved**: same 324 models |
| CTRL-B-LI-RH[A/B], CTRL-B-RSL-RH[A/B] | preserved | unchanged; MC-CTRL is acyclic (C3) |
| PRF-CTRL-WL-MONO | A-STEP + LOCAL-REL; pair m0/m1 | A-STEP + LOCAL-REL + GENERICITY; pair m1/m2; check still true |
| PRF-NAP3 | check true | check true, now including the R3-respecting separation |
| Regression G2 S2 (shared credential, cyclic control) | target Li-RH H_EJ = true | `INVALID_TARGET_STATE`; DEA output and expectation unchanged |
| All other translations, proofs and regression rows | — | identical |
| `meta.harness_sha256` | — | changes, as expected |

## Residual limits

VP-5 still does not detect obfuscated imports such as `importlib.import_module("dea_" + "ref")`; this was tested and the obfuscated import was not flagged. A static check cannot establish semantic independence. That was established by inspection (E6) and by the independent re-implementations in `verify.py`.
