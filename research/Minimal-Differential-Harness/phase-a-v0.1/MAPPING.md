# Exact sources and two evidence layers

| Source | Verified identifier |
|---|---|
| Public cases and wire, PR #13 | `b1631406c9434a214da98b2a49115be26a40c7db`; candidate manifest and both hash-seed runs verified |
| D0 v0.3.5.1 draft ZIP | SHA-256 `d655d4585970cb8cf2d605467b827c4b061daaab6041e554e402e944116630e9` |
| D0 full TeX | SHA-256 `b36a06a8cdf3edcb0789e2c6980f65ae9d2ce7dcac62d8f00abd7cf9c70b8617` |
| P-01, PR #7 | `91e842fdae94356ff323f3afb2e99245369108da`; specification SHA-256 `f2a3ea1ffa02937c23d60a80945742d5fd75f5ed2a02fcc69a3b124b338bcd26` |
| PR #6 dependency of P-01 tests | `4c4265b5230bf6010a75c95e17de62c066990bf2` |
| Official OPA binary | [v1.22.4](https://github.com/open-policy-agent/opa/releases/tag/v1.22.4), asset 739019430, linux/amd64 static, Go 1.27.4, Rego v1, build `ba39415db4b3c90cd68942a74b3cc2223ec2b23c-dirty` |
| Executable SHA-256 | `35e3b352e715e80624ead6c89930d8585f6f7d94cdc409eb2a9fe36620dcccba` |
| Official checksum asset 739019504 SHA-256 | `a09d17f9a8f2ac02d85b91f11c719b905e47eadaf8da33a829c1e46fc173989a` |

OPA v1.22.4 is this exploratory run's choice. It replaces the prospective v1.0.0 example for this run alone. The publisher checksum and GitHub Release API asset digest agreed with the executable before execution. Independent build and release-attestation verification were not performed.

The pinned P-01 command ran the unmodified 32-model D0 and 21-model precision programs, seven PR #6 tests, 32 compatibility cases, 10 RA, 11 C/W, 37 targeted cases and bounded independent checks. Its entire JSON result matched the archive. Verify the D0 and precision ZIPs and their extracted members using PR #7 SOURCES.sha256 and the D0 manifest. Extract both into directories named after the basenames under one source directory. From the repo root with pinned objects available:

```sh
sources=$(mktemp -d)
git archive 91e842fdae94356ff323f3afb2e99245369108da research/Precision-Amendment-P01 | tar -xf - -C "$sources"
git archive 4c4265b5230bf6010a75c95e17de62c066990bf2 research/Temporal-Control-Evidence/v0.1 | tar -xf - -C "$sources"
cd "$sources/research/Precision-Amendment-P01"
sha256sum -c SHA256SUMS
PYTHONHASHSEED=0 python3 -B regressions.py \
  --source-dir /absolute/path/to/extracted-source-directory \
  --pr6-dir "$sources/research/Temporal-Control-Evidence/v0.1" \
  --out "$sources/p01.json"
cmp "$sources/p01.json" RESULTS.json
```

## D0 and D1 projection

D0 applies the verdict order of TeX equations v0351-conflict, v0351-decision and v0351-atomic with reflexive producer and reviewer identity. The wire has no identity-control edges, principal reassignments, alternate output writers or mutable-output effects after production. The sets reduce to the authenticated producer and reviewer. Rubric controllers do not enter D0's reviewer set. D0's reflexivity still applies to a fixed-score signer, independently of SR-1's production-right test.

D1 adds controllers via surviving effects on the actually read exact versions (P-01 G-A), with the reviewer identity path and conservative admission (G-B). The ordered read tree supplies mandatory paths. A right to create a different immutable successor does not alter a fixed version. SR-1 separately recognizes an eligible successor immediately before bind, when the consumed version is a writable head and a successor slot exists. The chosen P-01 mapping requires explicit evidence of control of a mutable resolver or policy to add that dependency. This wire carries no such control capability. A broader reading of pre-bind selection needs a separate preregistered mapping and scope review. The additional Rego probe configures the chosen D1 rule.

Common wire admission checks grammar constraints before applying any source predicate. The profile is more specialized than the literal D0 and P-01 grammars and supplies a synthetic attested clean start, immutable versions and a single stable attempt. Hence the invalidity comparisons are wire-profile comparisons. General D0/P-01 semantics, real atomic commit and authorization are outside these translations. Both DEA arms require wire history and dependency closure for negative clearance.

## Provenance fields

| Field | Origin and premise |
|---|---|
| wire_sha256 | SHA-256 of exact neutral canonical bytes. A-derived verifies the binding. The digest does not authenticate the producer. |
| event_check, event_reason | Finite typed grammar, ID uniqueness, admissible rank order, scoped validity for rights and versions. Open history only checks necessary conditions and otherwise stays incomplete. |
| scope.history, scope.reads | Wire claims; their meaning depends on original assumed issuer and collection completeness. |
| producer, reviewer | Produce/adjudicate event ID, key and fixed canonical bootstrap owner. |
| score_right | Matching live score grant at production or null. Revocation and retract determine validity. |
| seal, binding, commit | Exact output, policy and event IDs, plus root at bind. |
| versions, heads | Genesis values and current descendant catalog at bind with immutable base and creation event. |
| versions.*.fields | Binary field values and surviving principal/key/write/grant from the last effective write. A no-op inherits the prior source. A certified reset clears only its channel on the new version. Right/key loss leaves prior version lineage. |
| rights | Live grant tuples at bind, with target, field, grant event, owner and key. |
| reads | Exact observed read IDs, version and parent links in rank order. |

The shared producer consumes only the wire. Expected verdicts, case IDs, true worlds, overlaps and conflict witnesses are never exported. A-raw shares the finite wire validator and small schema constructors but uses predecessor queries and backward lineage instead of the forward export. Each A-raw pipeline executes that L3 work afresh. For OPA it is a custom host adapter that passes its intermediate neutral facts to an actual Rego process. The A-derived gate receives the same normalized facts as the other reusers.

Verified 38 canonical wire digests against the archived assessor and compared forward/backward exports on all 38 wires and 144 generated histories. The archived independent checker checked invalid histories and the archived oracle supplied 12 witness paths whose IDs, version, active rights and fields we cross-checked. Reflexive identity and rejection of provenance for another wire were also exercised. Operational attestation validity, runtime capture, atomicity and hidden data remain untested.
