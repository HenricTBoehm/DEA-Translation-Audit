# Phase B v0.1 · Evidence comparison and decision

**EXPLORATORY – NOT SCORED – NOT FREEZE VALIDATION.** Ten real threshold evaluations completed. The independent child-FD assay identified the registered threshold inode and full-length offset advance **10/10**. Every result matched an independent finite arithmetic check. Two executions under different Python hash seeds reproduced the exact observation/result artifact. All three unchanged Phase A consumers executed through each of three evidence profiles, 90 invocations overall. No private holdouts or production access.

## Evidence results

| Quantity / denominator | E1 | E2 | Combined |
|---|---:|---:|---:|
| Correct threshold identity / 10 independently FD-confirmed evaluations | 8 | 10 | 9 |
| Wrong reported identity / 10 | 1 | 0 | 0 |
| Omitted or withheld identity / 10 | 1 | 0 | 1 |
| All five dependencies reported (score, policy, checked resolver, used resolver, read) / 10 | 9 | 10 | 9 |
| Complete candidate observation claims / 10 | 9 | 10 | 9 |
| Closed candidate observation with wrong reference version / complete candidate claims | 1/9 | 0/10 | 0/9 |
| Unresolved due to missing observation / 10 | 1 | 0 | 0 |
| Correct SR-1 abstention / missing-observation attempts | 1/1 | 0/0 | 0/0 |
| Detected input/projection contradictions / 10 | 1 | 1 | 2 |
| Surviving effects positively reconstructed / 5 reference-positive attempts | 2 | 4 | 3 |
| Surviving effects false negatives / 5 positives | 1 | 0 | 0 |
| Surviving effects withheld / 5 positives | 2 | 1 | 2 |
| Incorrectly asserted surviving effects / 5 negatives | 0 | 0 | 0 |

Candidate coverage means generated scoped closure before admission and includes B10, whose mutually inconsistent bind/read is still rejected. Claims in the row above remain conditional on collection and issuer assumptions. The five-dependency count measures the number of expected roles reported, without pretending independent per-field control ground truth. Of five positive successor rights and five positive selector permissions, each relation yielded E1 3 true positives and 2 unknown, E2 4 true positives and 1 unknown, combined 3 true positives and 2 unknown. All five negatives of each relation were recovered correctly in this deliberately bounded ledger. History absence after rejecting B10 is an unknown diagnostic, not an incorrect no-effect claim. The independent lineage/policy-shape assumptions are explicit in the experiment design.

Release comparison keeps actual and accepted evidence apart. There are four coherent attempts with material SR-1 conflict in the controlled reference; B10 is excluded as an invalid binding. The actual-conflict release counts for D0/D1/OPA were respectively E1 **3/1/1**, E2 **4/0/0**, combined **3/0/0**, each of four actual conflicts. Releases against *accepted-evidence* SR-1 conflict were E1 **2/0/0**, E2 **4/0/0**, combined **3/0/0**, with denominators two, four and three accepted conflict attempts. D0's releases partly reflect its narrower target. D1 and OPA's E1 release in B08 is instead caused by a plausible false read claim. SR-1 is the reference hazard rule for this table, and B04's separate selector hypothesis is outside it. Full denominators/contingencies and source-level evidence are in [RESULTS.json](RESULTS.json).

## F1–F9

| Question | Result |
|---|---|
| F1 · Observed dependencies | E1 reported process-side score, policy, resolver and exact threshold digests. It matched 8 of 10 independent threshold IDs. E2 recovered 10 of 10 from kernel open/access and immutable snapshots within the fenced interval. |
| F2 · Claims and reconstruction | E1 asserts what it read and computed. Registry match verifies the named object and digest. E2 observes names and access and reconstructs version/bytes through the manifest. Independent FD evidence supports exact threshold identity and full offset movement. Neither observer independently establishes every semantic operation or external permission. |
| F3 · Missed effects | E1 omits the B07 read, attributes B08 to a wrong but real version, and misses B08's surviving effect. E2 misses no threshold identity in this scope. Reconstructed role paths are withheld on invalid B10. General dependencies and historical completeness beyond the provided ledger remain untested. |
| F4 · Rights and binding | B03 can publish an unused alternative. B04 can select an existing material alternative without authoring it. B02 has both capabilities and a bound surviving effect. Binding and policy authority remain distinct. |
| F5 · Semantic vs evidence | D0 excludes rubric-side lineage, visible in B02/B05 with equally complete evidence. D1 and SR-1 agree on these concrete runs despite their Phase A distinction. B04 changes materially under the separate selector hypothesis. The B07/B08 E1-versus-E2 differences are evidence gaps or contradictions. |
| F6 · Available mechanisms | Kernel observation, content addressing, explicit controlled role/provenance records, custom replay and configurable policy provide the measured function. No DEA-specific sensor is needed. Establishing operational history truth and capture completeness remains open. |
| F7 · Costs and trust | E1 needs application instrumentation and trust in the emitting process. E2 needs a bounded watched scope, capture integrity and a known version registry. Independent FD ground truth needs an additional parent inspection. Shared history control is L3. Timing and accounting are in the cost report. |
| F8 · Smallest distinguishing case | B07 supplies one omitted application read, one selected threshold and a surviving producer effect. E2 recovers the read while E1 cannot, changing D1/SR-1 from UNDETERMINED to CONFLICT. B08 also detects a same-output false binding. Both gaps were deliberately introduced under the same observed executions, so neither is an incidence estimate. E1 can directly report its own digest, whereas E2 reconstructs it conditional on the registry. |
| F9 · Remaining research | No distinct DEA-specific acquisition or decision advantage was shown. A limited open question is which independent, affordable evidence can support selection authority and historical completeness in an operational deployment. |

## Disposition

| Dimension | Assessment |
|---|---|
| Technical execution | **GO**, 10/10 isolated evaluations and actual unchanged OPA, D0 and D1 executions |
| Reproducibility | **GO** on recorded Linux scope, exact output across the two seeds |
| Reliability | **Conditional**, external FD/registry corroboration in a controlled evaluator |
| Dependency completeness | **Scoped only**, no general completeness attestation |
| Historical reconstruction | **Conditional**, verified effects from a controlled ledger; no independent operational rights/history oracle |
| Trust | Explicit separate trust in process, kernel, controller, collection scope, immutable artifact assumptions and assessor; contradicting inputs detected without a general X-TRUST solution |
| Practical cost | Bounded machine costs measured; human and production burden open |
| Evidence of scientific advantage | Exploratory evidence of recoverability and semantics, no independent DEA advantage |

**NO-GO for another DEA-versus-policy benchmark on this fixture.** Consider a narrowly scoped operational study only if a real resolver has independently auditable version selection, rights and effect history, and the incremental cost of obtaining those facts can be measured. The tested acquisition function is achievable using established observation and policy facilities plus explicit generic L3 joining and replay. This says nothing about full-stack equivalence or production-grade completeness. The Phase A X-TRUST boundary remains: indistinguishable accepted evidence cannot expose every false attestation.
