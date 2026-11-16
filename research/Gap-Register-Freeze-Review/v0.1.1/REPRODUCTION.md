# Reproducibility

CPython 3.12.14 (Clang 22.1.3), Linux x86-64, Python standard library, Bash, unzip, GNU sha256sum and cmp. Original archived self-tests reported 0.001 s for ten tests. Checks are deterministic; elapsed time is a host-specific observation. No benchmark timing or runtime configuration from a comparator was measured.

The review replay needs the original v0.1.1 ZIP identified by SOURCE_MANIFEST.md. Optional second argument verifies the exact D0 draft package and its TeX hash. Both remain external inputs. The source verifier checks hashes before scripts run.

```sh
cd research/Gap-Register-Freeze-Review/v0.1.1
bash verify.sh /absolute/path/to/DEA_Gap_Register_Differential_Audit_v0.1.1_Review_Package.zip
bash verify.sh /absolute/path/to/review.zip /absolute/path/to/DEA_v0.3.5.1_draft_review_package.zip
```

The script runs the archived consistency checks unchanged in a temporary extraction, compares its original oracle report byte-for-byte, then executes the independent finite review under hash seeds 0 and 42. Both outputs must match RESULTS.json. This includes original-oracle mutations in memory and the independent safety and scoring counterexamples. Freeze claims and comparator code are not part of the executable checks.
