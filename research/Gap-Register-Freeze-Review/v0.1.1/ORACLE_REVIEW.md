# Fallorakel, independence and scoring

## What was actually executed

The original ten consistency tests passed. The original oracle JSON was byte-identical to the package result. The independent script expands the family values into six neutral histories with explicit rights, reads, credential changes and recorded effect lineage, then evaluates those histories. It does not call DEA or use expected family verdicts to derive results. It does reuse the stipulated family descriptions, finite worlds and additional key/field conventions declared in the script. Code independence is verified relative to this finite exercise. Independence of the original factual labels and evidence issuers is unverified. Running the archived oracle on probes is a separate operation.

| Check | Result |
|---|---|
| Counts with separate truth and justification | 6 canonical worlds. 13 regular executions, 10 observable profiles. 3 CLEAR, 3 CONFLICT, 6 UNDETERMINED, 1 INVALID. Truth on the 12 valid executions is 6 CONFLICT and 6 NO_CONFLICT. |
| I twins | Three byte-identical pairs in the audit's sanitized serialization, with different truth and identical justified verdict. Only structurally visible information and observations enter that serialization. This does not attest a future wire adapter. |
| X-TRUST | Same sanitized request as K1-C, conditional CLEAR, actual CONFLICT. A false purported completeness attestation is not discoverable from those bytes. |
| Negative controls | Always-deny, always-permit, always-invalid and proofless always-conflict all fail both S1 and S2. See exact counters below. |
| Generalization | Mapping 10 public request hashes to expected labels passes all 13 runs, and also obeys all I-twin equalities. Stable role renaming alone cannot disqualify canonicalized lookup. |

The JSON input currently contains `actual_values`, expectations, instructions and family designators in the same package. Those fields belong to the evaluator. In the audit, a defined projection generates distinct requests for the consumer proof. This is a constructive illustration and not proof that a future comparator will read only those fields. Credible architecture requires an isolated scorer with private oracle metadata, replayable per-case wire evidence hashes and no case oracle accessible from a policy/query.

## Remaining correctness issues

1. **§2.3, §3 and oracle.py.** The archive checks three integer lifecycle ranks. It does not validate the whole alphabet or enforce key validity at modify. A witnessed post-revocation write and a rank outside 0–5 still produce CONFLICT. A missing seal rank produces INVALID although the prose allows completion. This matters for separating unsupported facts from actual contradiction. Add canonical event IDs, uniqueness and typed timed transitions. Test an unknown rank, contradictory rank, duplicate IDs and a missing authenticated material fact. Rerun external review.
2. **§2.2–2.3 and K3.** It is possible to agree with the expected K3-C q label while making incompatible assumptions about q's key: the alphabet supplies ka and kj but no independently bound q key or signed write provenance. Define the neutral key-owner mapping, active field capabilities, exact artifact versions and history. Reset is discussed but absent from the alphabet. Explicitly separate successor neutralization and an immutable version. Rerun independent oracle review.
3. **§3 positive witness.** The finite universal formula can label CONFLICT from a degenerate template and without verifying the asserted decisive observation. With coverage false, K3-F still returns CONFLICT under the supplied positive field. That is permitted *if* this field represents a supported witness; neither proof existence nor authenticity is verified by the code. Require a replayable exact positive path (or a separately justified scope-bound exhaustive implication under equally verified premises). A merely possible influence earns UNDETERMINED. Apply INVALID only to an authenticated contradiction relative to the authorized grammar and scope, not out-of-support observation alone. Unknown/unsupported cases require a separate reason.

## Proposed total scoring rule

Each response contains one action in {RELEASE, BLOCK_CONFLICT, BLOCK_UNDETERMINED, INVALID, NO_DECISION}, a native status and an independently checked proof tag in {VERIFIED, REJECTED, UNVERIFIED, NONE}. Unknown/error and a bare deny are not positive conflict witnesses. NO_DECISION is kept distinct from correct evidence-based abstention. A comparator with no natural gate has a component capability record only.

| Axis | Counters and explicit denominators |
|---|---|
| S1 | Correct releases and false holds on 3 CLEAR; unjustified releases on the other 10, including INVALID or open evidence; overall release mismatch on 13. Count every nonrelease on eligible CLEAR as false hold (including INVALID/error). |
| Truth-relative | Actual false releases among 6 concrete CONFLICT ordinary executions; false holds among actual 6 conflict-free recorded separately from the 3 release-eligible ones. X-ORDER excluded from truth-conflict denominator. X-TRUST reported separately as its own conditional vs actual pair. |
| S2 | Exact justified verdict and correct reason/proof out of 13; witnessed diagnosis among 3 CONFLICT; correct evidence abstention among 6 UNDETERMINED, and separately among 3 unique views; missed INVALID among 1; falsely asserted INVALID among 12. Premise-caused, underdiagnosed and execution-error reasons remain separate. A proofless positive accusation is counted regardless of lucky truth. |
| S3 | Mapping violations over the 10 unique observable views and per augmentation/evidence access. Unverifiable mapping yields UNDETERMINED, and a failed fidelity row cannot support a superiority/limitation claim. |
| S4 | For each claim about scope, mediation, identity and neutralization, track assertion authentication and ascertainment of content independently. Distinguish supported, asserted only, contradicted and unknown. For X-TRUST report the model-conditional output and actual semantics separately. Never score detection from identical bytes as universally required. |
| Cost | Separate configured policy, custom code, issuer/monitor burden, trust assumptions, external facts and computation. Preregister the primary cost unit and comparable budgets, and measure it or use NOT EXECUTED. S1–S4 do not encode cost. |

Count per case and per distinct view alongside denominators, with no inferential statistics on repeated twins. Define a predeclared dominance rule: no worse on fixed release, diagnostic, evidence and premise obligations and at least one practically meaningful difference with credible matched cost. Keep cost vectors separate from security failures. An abstaining gate may be safe on witnessed positives yet fails diagnosis there and fails availability on CLEAR. Do not pool underdiagnosed negatives into successes.

| Simulated response pattern (no comparator code) | S1 mismatches / 13 | S2 mismatches / 13 |
|---|---:|---:|
| Always-deny represented as unclassified hold | 3 | 7 |
| Always-permit | 10 | 10 |
| Always-invalid | 3 | 12 |
| Always-CONFLICT with no proof | 3 | 13 |

The current S1/S2 text gives the right high-level direction but omits several cross-cells and rates. The proposed map needs prospective independent approval. The exact inputs, typed traces, leaks, mutants and adjudication counts are in [RESULTS.json](RESULTS.json).
