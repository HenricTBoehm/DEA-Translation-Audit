# Public case studies

## Selection and frozen procedure

The two cases were selected and their acceptance rule committed in RESEARCH_QUESTION.md before downloading and fitting. NIST StRD supplies observed inputs, the formula and certified numbers for both. The exercise tests reproducibility of a candidate coefficient vector. It uses the published target fit and adds an audit-specific rule: accept only if the maximum relative error against all certified coefficients is at most 1e-8. NIST's documented model is observed evidence. The missing execution flag, deliberately incorrect implementation and falsely complete analyst model are synthetic interventions. There was no observed archival omission, field experiment or adjudication by NIST. The governance fixture reports missing real institutional evidence; it holds in all four variants. [Norris](https://itl.nist.gov/div898/strd/lls/data/Norris.shtml) · [Pontius](https://www.itl.nist.gov/div898/strd/lls/data/Pontius.shtml)

| Benchmark | Required published fit | Synthetic omission | Full / omitted max relative error, exact solve | Full / omitted decision |
|---|---|---|---:|---|
| Norris, ozone calibration (36 observations) | intercept + linear term | remove intercept | 4.38965228e-15 / 1 | ACCEPT / REJECT |
| Pontius, load cell calibration (40 observations) | intercept + linear + quadratic terms | remove quadratic term | 7.58556892e-16 / 8.13004239 | ACCEPT / REJECT |

The rational normal-equation solver and independent scaled QR solver agree on all four acceptance decisions. QR maximum errors for the prescribed fits were 4.71898508e-14 and 2.48883394e-12. Accepted values, rounded for inspection, and original certified coefficients are recorded in the result JSON. The two execution choices are alternative claims about how a candidate was produced, evaluated against the original fixed reference and tolerance. They are not competing authorized NIST models. [Norris raw data](https://itl.nist.gov/div898/strd/lls/data/LINKS/DATA/Norris.dat) · [Pontius raw data](https://www.itl.nist.gov/div898/strd/lls/data/LINKS/DATA/Pontius.dat)

## Results under identical evidence

For each dataset, when the execution option is listed and its value is withheld, C+S and D report UNSTABLE and ask one question (whether the required term was enabled). When the field itself is omitted and coverage asserted, each returns CERTIFIED_STABLE and an empty query (incorrect relative to the two reference executions). C supplies only the shared governance hold. Comparing the declared execution inventory with the original formula identifies the absent setting in both benchmarks. Restoring the documented dimension to the scientific query changes the result from CERTIFIED_STABLE to UNSTABLE in both methods; governance stays held. This evaluation of injected omissions is counted separately from actual recorded NIST facts.

## Measured effort and unresolved costs

| Measured action | Norris | Pontius |
|---|---:|---:|
| Original ASCII fetch, HTTP 200, elapsed seconds | 4.621747 | 5.063965 |
| Read, parse and validate receipt of original formula/columns, ms | 0.511416 | 0.607392 |
| Two fits by two solvers, tolerance checks and witness formatting, ms | 0.908903 | 1.940658 |

The web query opening the two ASCII sources and searching comparison literature took 1.69 s wall time. Four comparator and scope-review invocations took a combined 4.262481 ms. Aggregation and writing the complete audit JSON took 40.695084 ms, including other synthetic checks in that phase. Machine times are observed quantities from this execution. Human review time, independent adjudicator effort, cryptographic attestation issuance and production certificate costs were NOT EXECUTED. Timing is intentionally excluded from exact replay. [Machine timing](TIMING.json)
