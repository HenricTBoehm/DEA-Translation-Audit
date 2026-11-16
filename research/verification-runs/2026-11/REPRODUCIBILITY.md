# Independent reproduction

Use Bash, Python 3 and its standard library, `sha256sum`, `cmp` and `patch`. The verification run used CPython 3.12.14 on Linux x86-64. The frozen RP results record Python 3.14.4. No Python packages are needed for the runs. Changing interpreters can change the runtime metadata and potentially seeded reproducibility, so always compare the outputs against the references.

## Public checks

```sh
bash research/verification-runs/2026-11/check_repository.sh quick
bash research/verification-runs/2026-11/check_repository.sh full
```

The quick run validates the archived manifests and independently enumerates simple routes with timestamp assignments for the ADR-001 cases. A time-expanded graph checks the reset convention. It tests archive layouts and comparison failures for the VP correction. If the Poblete comparison is present, it reruns both archived scripts and the typed fixture. The full run adds the untouched ADR harness and a byte comparison. Causal windows and case expectations come from the independent fixture JSON in the quick run. The full harness uses hard-coded fixtures, 64 static combinations × 4 actor-time pairs in its enumerated subset, and seed 20261116 for random models. Its 2,932 inadmissible chronologies are part of the archived sample denominator.

For PR #4 by itself, run `bash research/Poblete-DEA-Comparison/check_regressions.sh`. The workflow is proposed in PR #5. Its PR trigger runs the quick checks on the checked-out PR tree. Manual dispatch becomes available after the workflow exists on the default branch, per the [event documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch). The workflow grants read-only content access and checks out with credentials persistence disabled.

## Full private inputs

Get the frozen PDF and the flat RP ZIP from the original distribution. Match these exact digests before executing:

| Input | SHA-256 |
|---|---|
| DEA v0.3.4.3 architecture closure candidate PDF | `51a2553e8bb13fe80bc3f0e6245ba0c4dcbe0a31db03ad577a3f3f26f8c97c33` |
| RP ZIP used here (30 flat members) | `18b39eaf7535f55f42a775846c1b2a9e45d73dd6e33c6f31a40093d5f263aaa7` |
| Historical RP ZIP identified by the original VP results | `18667ba7c76fd71f193e6061de221ca0120b51892d7d9aac1a011577ab5156fa` |

See [ORIGINAL_MANIFESTS.txt](ORIGINAL_MANIFESTS.txt) for the five original checksum lists. Compare individual archive member bytes to the tracked files, allowing the recorded archival-only bytecode in ADR/Poblete. The verified RP flat ZIP matched all 30 tracked members. The historical RP ZIP remains a distinct provenance reference.

```sh
pdf=/absolute/path/to/DEA_v0.3.4.3_architecture_closure_candidate_2026-11-15.pdf
zip=/absolute/path/to/dea-v0343-remediation.zip
scratch=$(mktemp -d)
mkdir "$scratch/rp"
sha256sum "$pdf" "$zip"
python3 RP-1.0/harness/run_audit.py --baseline "$pdf" --out "$scratch/rp/remediation-results.json"
bash VP-1.0/verification-v1.0.1/run.sh \
  --baseline "$pdf" --package-zip "$zip" --out "$scratch/vp-v1.0.1.json"
```

Compare the RP result JSON structurally after normalizing exactly `meta.python`. Compare the countermodel JSON without normalization. Retain raw hashes and byte equality for both files. VP v1.0.1 performs these checks in a temporary extraction and serializes all three dimensions of the comparison. Baseline and journal PDFs belong outside version control.

To repeat the additional chronology-filtered sample, use the original generator and run the same invariant analysis over its valid subsequence. The single-edge perturbation stream advances only for retained models, so these statistics constitute a separate run.

```sh
PYTHONPATH=research/ADR-001 python3 - <<'PY'
from adr001_ctrl import analyse, mc_random
valid = (m for m in mc_random(20000, seed=20261116) if m["tE"] <= m["sigma"] <= m["tJ"])
stats, violations, disagreements, witnesses = analyse(valid)
print(stats, violations, disagreements, witnesses)
assert stats["models"] == 17068 and not any(violations.values())
PY
```
