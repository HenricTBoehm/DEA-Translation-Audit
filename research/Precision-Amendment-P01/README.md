# Reproduce P-01

- [Formal specification](DEA-v0.3.5.1-Precision-Amendment-P01.md)
- [Review and execution notes](REVIEW_NOTES.md)
- [Counterexamples](COUNTEREXAMPLES.md)
- [Open obligations](OPEN_OBLIGATIONS.md)
- [Machine-readable results](RESULTS.json)

Run with Python 3.10 or newer and the standard library. Obtain the two original packages from the intended distribution whose hashes appear in SOURCES.sha256. They contain the original reports, case definitions and golden results. The standalone report is optional for execution.


Extract the packages into separate directories named after the ZIP basenames under one source directory. From that source directory verify the package and member fingerprints against the matching paths in SOURCES.sha256. Verify the draft's own SHA256SUMS from its extracted package root. Git source fingerprints are listed under their repository-relative paths. Obtain PR #6 at commit 4c4265b5230bf6010a75c95e17de62c066990bf2 in a separate checkout.

```sh
cd research/Precision-Amendment-P01
sha256sum -c SHA256SUMS
python3 regressions.py \
  --source-dir /absolute/path/to/extracted-source-directory \
  --pr6-dir /absolute/path/to/pr6/research/Temporal-Control-Evidence/v0.1 \
  --out /tmp/p01-results.json
cmp /tmp/p01-results.json RESULTS.json
```

The runner first executes both originals unmodified and compares their entire generated JSON files to the archived bytes. It executes all seven PR #6 tests and then the compatibility cases, targeted fixtures and bounded differential checks. Identity and precision adapters are deterministic and reviewed in REVIEW_NOTES.md. Each old input is located by its original case ID and checked against the corresponding source fingerprints. The machine report records the exact normalized input hash, expected verdict, actual outcome, witness evidence and missing requirements. New inputs are included verbatim in the report.

For the new package only, the reference callable is p01.evaluate and the independent comparison is independent.evaluate. The synthetic new fixtures live in regressions.custom_cases. Example of running only those fixtures:

```sh
python3 - <<'PY'
from regressions import check, custom_cases
results = {name: check(model, expected) for name, (model, expected) in custom_cases().items()}
assert all(row["matches"] for row in results.values())
print(f'{len(results)} targeted cases pass')
PY
```
