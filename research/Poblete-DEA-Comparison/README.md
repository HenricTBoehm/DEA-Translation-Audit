# Poblete et al. (2026) × DEA — comparison candidate

**Status:** research comparison / audit intake; **not normative**, **not a validated DEA deployment**, and **not a result of the DEA pilot**.

Reference: Poblete, Cravero and Diaz, *A Governed Human–AI–Agent Workflow for Specialized Data and Data Engineering Agents: Authorization, Verification, and Provenance*, *Electronics* 15(21), 5135 (2026), DOI https://doi.org/10.3390/electronics15215135.

## Contents and provenance

The seven text/source files in this directory are byte-for-byte copies of the submitted `dea-poblete-comparison.zip`:

- `poblete-vs-dea-comparison.md`: crosswalk narrative for DEA v0.3.4.3 and ADR-001.
- `poblete-vs-dea-v035-delta.md`: comparison to **non-adopted** DEA v0.3.5 working draft.
- `crosswalk-poblete-dea.csv`: 21 source-to-construct comparison rows (X1–X21).
- `poblete_adr001_check.py` and `poblete-adr001-results.json`: five **assumption-based** control-model readings of the paper.
- `poblete_v035_check.py` and `poblete-v035-results.json`: those same hypothetical readings passed through an approximation of the draft v0.3.5 conflict/record-completeness gate.

The original source ZIP is stored unchanged at `source-archive/dea-poblete-comparison.zip` (SHA-256 `dafa9893120cb303a5a0307828be8d6a5884fe46455f255c19a932610d7c1bd1`). It includes a compiled `__pycache__` artifact, which is **not** extracted into the versioned source tree.

`SHA256SUMS` contains SHA-256 hashes of the seven original extracted source files and the original ZIP. This README and `REVIEW_NOTES.md` are additional intake documentation, not part of the supplied research package.

The article PDF referenced by the comparison is **not** redistributed. Its reported source PDF hash was **not independently verified here**; the publisher's HTML page was used for contextual checking. The companion preprint and the referenced LATTICE literature were not reviewed in this intake.

## Reproduce

The original scripts assume an adjacent directory named `../dea-adr-001`, whereas the repository contains the dependency at `research/ADR-001/adr001_ctrl.py`. The scripts are preserved unchanged; supply that directory on `PYTHONPATH` instead.

From the **repository root**, with Python 3 and the standard library:

```sh
cd research/Poblete-DEA-Comparison
sha256sum -c SHA256SUMS
PYTHONPATH=../ADR-001 python3 poblete_adr001_check.py --out /tmp/poblete-adr001-results.json
PYTHONPATH=../ADR-001 python3 poblete_v035_check.py --out /tmp/poblete-v035-results.json
python3 - <<'PY'
import json
for generated, archived in (
    ('/tmp/poblete-adr001-results.json', 'poblete-adr001-results.json'),
    ('/tmp/poblete-v035-results.json', 'poblete-v035-results.json'),
):
    with open(generated) as f: g = json.load(f)
    with open(archived) as f: a = json.load(f)
    assert g == a, (generated, archived)
    print('MATCH', archived)
PY
```

This validates reproducibility **of the given computations**, not their truth for the actual Poblete deployment. The comparator's construction is conditional on the chosen edge assumptions and on the ADR-001 model.

## Important review restrictions

- The paper does **not** establish who could technically control the executor or modify the orchestrator's acceptance criteria. PB-1…PB-4 are hypothetical topologies, not observations.
- **PB-3v is not a well-typed ADR-001 model as currently encoded:** it sets `t_exec=2`, although the imported ADR-001 harness stipulates `theta_E={0,1}`. Rebind the verification report to a separately defined production/adjudication transition and rerun before relying on that result as a DEA test.
- The model represents the orchestrator's alias/identity as mutually controlling nodes (`p↔j`). ADR-001 already identifies identity-vs-control typing as open. The coding choice must not be mistaken for a validated identity semantics.
- The v0.3.5 script sets `RecordComplete=False` for the *published description* (missing proof of completeness), not because it inspected the underlying system. Therefore `UNDETERMINED` means **not established from the available publication**, not proof of actual missing enforcement.
- `NO_CONFLICT_ESTABLISHED` is not authorization, evidential sufficiency, or scientific validity. Its meaning is conditioned on complete trusted records.
- The scripts emit results but contain no standalone automatic proof/test assertions beyond producing JSON. Regression assertions comparing with archived JSON are shown above.

See `REVIEW_NOTES.md` for the detailed acceptance criteria. No normative change to DEA v0.3.4.3, ADR-001, or v0.3.5 results from this archive.

## Versioned verification report fixture

`bash research/Poblete-DEA-Comparison/check_regressions.sh` verifies the eight original hashes, reruns both source scripts, compares both JSON files byte-for-byte and checks the separately versioned [typed replacement](typed-v1.0.1/results.json). The original PB-3v verdict remains archived and inadmissible under the original stage typing. The typed replacement records a separate report production event and seal at 2, a Stage-8 decision about the report at 3, and a distinct input artifact already sealed at 1. It keeps lookback start 0 as an explicit fixture assumption.

| Evidence | Execution output | Verification report |
|---|---|---|
| Publication alone | UNDETERMINED | UNDETERMINED |
| Complete hypothetical record with effective report-production edge at 2 | NO_CONFLICT_ESTABLISHED | CONFLICT |
| Incomplete hypothetical record with that authenticated edge | UNDETERMINED | CONFLICT |
| Complete hypothetical record without that edge | NO_CONFLICT_ESTABLISHED | NO_CONFLICT_ESTABLISHED |

These are isolated control-gate results. They establish neither overall authorization nor an empirical conflict in the published experiment.
