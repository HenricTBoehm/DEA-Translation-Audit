# Counterexamples and premise checks

Exact synthetic inputs and outputs are in [PILOT.json](evidence/PILOT.json) and [ADVERSARIAL.json](evidence/ADVERSARIAL.json). The scored pilot assumes the attested premises hold. Attacks on those premises are separate from the confusion matrices.

| Premise / case | Minimal distinguishing input and witness | Result |
|---|---|---|
| P1, malformed original trace | Remove seal from CM-R8. The legacy engine has a witnessed controller on both sides, but its frozen production set is empty. | Legacy returns CLEAR outside its preconditions. P-01/pilot distinguishes missing seal (UNDETERMINED) from authenticated reversed order (MODEL_INVALID). |
| P2, CM-R6 | A reset fires only if the extra trigger exists in the upper state. The true state has (p→j) and lacks the trigger. | Upper CLEAR with true conflict. A state-dependent reset may destroy inclusion. |
| P3, CM-R3/S09 | Before the window (p→q); inside it (p→a) and (q→j). Bootstrap names only the endpoints. | Backward cone includes (q). The unknown channel yields a hold. This also holds when the trace uses a verified alias for (q). A deliberately false complete attestation still yields false CLEAR. |
| P3, CM-R4 | Leave the criteria channel of (j) out of an otherwise complete bound. | Missing channel becomes unknown. A missing channel cannot be assumed empty. |
| P3, CM-R5/S08 | A sound coarse bound allows possible (p→rubric); the concrete trace has no such token. | BOUND hold and no positive conflict claim. |
| P4, CM-R7 | Use (p), already a possible producer controller, as the issuer of the bound. | Held because the certificate is self-issued in the tested model. |
| P5, CM-R8 | (p→j) is certified in the actual pre-state, versus listed only in an upper bound. | CONFLICT versus UNDETERMINED. Falsely certifying a merely possible token as actual can manufacture a false conflict in the legacy model. |
| G-A, S02/S06 | (p) controls (a) and the mandatory rubric, including acquisition after seal and before adjudication. | C/D report CONFLICT; both may simultaneously have a certified constant substantive outcome. |
| Reset, S10/S11 | Credential-only reset versus independently proved criteria reset on the exact rubric. | The first retains the witness. The second clears the relevant effect in this fixture. |
| Fixed scope, S05 | Seal pins rubric@1, commit uses rubric@2. Rename both scientific scope labels to rubric@2. | Still MODEL_INVALID for governance and STABILITY_UNDETERMINED. A separate counterfactual attempt can be analyzed, outside the scored attempt. |
| Divergent axes | S01 has independent roles and complete evidence; make the fixed policy depend on an unobserved calibration fact. | Governance passes while substantive value is UNSTABLE. |
| Dynamic dependency, S12 | Rubric has a mandatory resolver missing from the verified dependency closure. | Governance and scientific diagnostics withhold certification. Marking a partial scientific description as exhaustive cannot repair the missing procedure dependency. |

The backward oracle agrees on the concrete, witnessed and upper sets for the seven admissible archived traces (21 comparisons). CM-R6 violates P2 and is checked separately by its explicit reset witness. The numeric reproduction patch changes only the order in which random draws are assigned to pre-state tokens.
