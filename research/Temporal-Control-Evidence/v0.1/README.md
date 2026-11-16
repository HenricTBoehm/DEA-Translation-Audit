# Temporal control evidence v0.1

Experimental fixture for DEA v0.3.5 obligations O1–O3. Run the self-contained test harness with Python 3.10+ and its standard library.

```sh
cd research/Temporal-Control-Evidence/v0.1
python3 -m unittest -v
```

| Check | Required evidence | Result |
|---|---|---|
| 1. Input validity | Scope binding, nonnegative resolved event ranks, record start ≤ execution ≤ seal ≤ adjudication | `VALID`, `MODEL_INVALID`, or `UNDETERMINED` for a missing event |
| 2. Historical coverage | Attested relevant record from the declared start through adjudication and separately attested closure at that start | Reports in-window coverage and historical closure individually |
| 3. Control witness | Two time-respecting journeys from a common canonical principal to producer and adjudicator, respectively cut off at seal and decision | Reports concrete ordered witness paths, including the empty self-attribution path |

A valid input and a verified witness yield `CONFLICT`, including under incomplete history. A valid input with both coverage checks and no witness yields `NO_CONFLICT_ESTABLISHED` within the reported scope. Missing evidence yields `UNDETERMINED`. The outcome concerns the control gate. Authorization to assign a disposition is a separate predicate.

## Boundary assumptions

- A scope binds the identities, artifact version and control-record version. Fixture attestations stand for external authenticated attestations. A trusted initial state attests that no relevant earlier influence survives into the scope. Verified neutralization attests that all relevant surviving effects, including propagated effects, were removed before the record starts. An authenticated earlier edge contradicts the fixture's initial-state declaration. Neutralizing a credential alone gives no such attestation for criteria or derived artifacts.
- Integer ranks represent an already resolved event order. Separate edge events at the same rank are rejected. An edge recorded at a boundary rank belongs to the inclusive boundary snapshot. Event-order provenance and genuinely simultaneous propagation remain research obligations. The graph models persistent control conservatively within its declared scope and contains no additional in-window resets.
- Certificate issuance, residual-effect enumeration, time-varying alias validation and binding the result atomically to adjudication remain outside this bounded fixture. `NO_CONFLICT_ESTABLISHED` is a result under the supplied, scope-bound attestations.

## Counterexample and checks

If `p→j` at 0 plants a surviving criterion and `p→a` at 1 can affect execution, a record starting at 1 can be complete through the decision and still omit the adjudication-side influence. The fixture returns `UNDETERMINED` for that record. Starting at 0 exposes the positive witness. With independently attested full neutralization by 1, the same downstream window supports a bounded negative result.

The seven test methods cover this counterexample, malformed and incomplete chronology, scope and coverage mismatches, reverse relays, boundary cutoffs, self-attribution and unauthenticated edges. The journey scan is checked against independent forward replay across all 343 ordered traces with three ranks and three principals, with at most one directed edge per rank.
