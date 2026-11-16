# Comparator roles, matched profiles and budgets

Stratum A minimal comparison is D0, D1 and OPA/Rego (v1 syntax; source version v1.0.0 reviewed in PR #12). The OPA nomination is prospective and awaits acceptance and an executable artifact fingerprint. XACML 3.0 Core can enter only with a pinned PDP and prospective profile freeze. Detailed document pins and prior-art roles are inherited at the pinned [PR #12 source manifest](../../Gap-Register-Freeze-Review/v0.1.1/SOURCE_MANIFEST.md). in-toto, SLSA, PROV-DM, X.509/CRL and TUF can supply particular evidence functions when paired with an explicit downstream gate. NASA-STD-7009B anchors acceptance requirements, outside runtime scoring. A provenance representation or validator alone is not a contestant for final verdicts.

D0 source semantics stay fixed. Do not synthesize a rubric-to-adjudicator identity edge for D0 to match D1. D1 includes only the documented P-01 change. Faithful implementation limits can be tested, recorded and independently reviewed later. Permit every contender exactly the same raw fields and approved common payload; do not provide principal control sets, residuals or other decision-ready truth to only one contender. In A the common producer supplies neutral authenticated event facts and same scoped attestations. Native outputs and generic errors must be mapped using a declared, independently checked table. A bare deny gives a hold with unavailable reason, never an inferred conflict. Undocumented external calls are disallowed. In B each arm gets equal raw visibility and may choose a compatible scoped producer; measure its costs and assumptions.

| Level | Gate, producer or adapter classification rule |
|---|---|
| L0 | Released native behavior using default or standard attachment. |
| L1 | Documented configuration or use of released predicates on the common primitives. |
| L2 | Composition of unchanged released components through documented schema-preserving adapters. |
| L3 | New inference, replay, tracing, control-attribution, history closure or evidence production, independent of language or component branding. |

Label gate and producer separately by highest level used; disclose every adapter classification and component contribution. A serializer cannot hide semantic preprocessing. Pre-register a profile-limited documented configuration/composition arm and a separate matched custom engineering arm if useful. A specialized rule confers neither native coverage nor an expression-limit proof.

## Proposed binding caps once independently adopted

A profiles (D0, D1, established composition) allow per arm up to **16 person-hours** to produce mapping, policy and implementation materials within the selected level, and **4 person-hours** of review; symmetrically limit any L3 parity arm to the same cap. B allows up to **24 person-hours** of acquisition configuration/implementation and **4 person-hours** of review per arm. Count custodian and common harness work separately; debit arm-specific assistance against that arm. Preserve time logs and disabled functionality rather than granting one arm a private extension. These caps are feasibility bounds chosen for a narrow pilot, subject to independent prospective acceptance.

On one pinned Linux x86-64 image, limit execution per request to one CPU core, 512 MiB resident memory, 5 s wall time, 64 KiB request and 64 KiB output. For B allow up to 30 s per attempt for bounded raw acquisition on the same resources, with separately logged issuer/monitor work. No network except a controlled identical declared fixture service in B; no external data files in A beyond participant-config artifact and request. Use fixed measurement scope and runner provenance. These caps need preflight viability checks with neutral fixtures before freeze, no contestant results used for tuning. A capped arm that stops records execution status, never mathematical nonexpressibility.

Open profile obligations include exact build/container digests, source-interpretation signoff for D0/D1, policy features or PIP/replacement allowances, trust roots, issuer freshness and raw source simulation, start/stop accounting, allowed adapters, absence/fallback reasons and final caps. See [OPEN_OBLIGATIONS.md](OPEN_OBLIGATIONS.md).
