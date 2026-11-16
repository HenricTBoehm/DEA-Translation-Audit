# Exact sources and scope of verification

Checked 16 November 2026. GitHub reported all four pull requests open drafts with the following heads. Exact hashes were verified against Git refs and source records. These are provenance pins, independent of future branch movements.

| Ref | Inspected SHA | Use |
|---|---|---|
| main | `2fc5e7f353f1984e663110e3eb0a0d9e38ba7fa4` | Repository root reviewed; branch publication uses the review head |
| [PR #12](https://github.com/HenricTBoehm/DEA-Translation-Audit/pull/12) | `80d0e5a77937df62521f3a4f47a9437097ad5eb7` | Primary v0.1.2 delta, review, freeze decision, oracle and threat reports, comparator fairness, obligations, source manifest and results |
| [PR #7](https://github.com/HenricTBoehm/DEA-Translation-Audit/pull/7) | `91e842fdae94356ff323f3afb2e99245369108da` | D1 P-01 specification, exact role/dependency amendment on top of D0 |
| [PR #10](https://github.com/HenricTBoehm/DEA-Translation-Audit/pull/10) | `96731f6ac458dd7b0d9ec855eec0036d91f47467` | Historical bounded pilot, conditional HR-1 and stability context |
| [PR #11](https://github.com/HenricTBoehm/DEA-Translation-Audit/pull/11) | `7fee1797e31963fe60720476d8f34305148e2415` | Historical no independent Decision Stability advantage over ordinary joint sensitivity at matched evidence |

The original archived package bytes were available. Verified the review archive SHA, CRC, ten member digests, and ran the historical verification script from the pinned review. It checks the archive and D0 source records and reproduced the original result JSON bytewise, alongside the ten original self-tests. Verified the full D0 TeX and PDF under the D0 manifest. The historical v0.1 ZIP and actual old pilot/PR #11 experiments were not rerun. Original sources are referenced by exact IDs/digests instead of repackaged.

```text
754268ed45cd18321657dc7e7b26ec31e6bddb14f397af01fc86691763cbe166  DEA_Gap_Register_Differential_Audit_v0.1.1_Review_Package.zip
636a27cfeec63a5859fe54462457421e84a8712c8196aa5bb4a528615271cc9b  DEA_Gap_Register_Differential_Audit_Protocol_v0.1.1.md
72f5eb98c36548f21884ea7a1db8b6f16faa70382abc54c5b09b7f4ddd6e1ffe  oracle-results-v0.1.1.json
d655d4585970cb8cf2d605467b827c4b061daaab6041e554e402e944116630e9  DEA_v0.3.5.1_draft_review_package.zip
b36a06a8cdf3edcb0789e2c6980f65ae9d2ce7dcac62d8f00abd7cf9c70b8617  manuscript/DEA_v0.3.5.1_working_draft_2026-11-16.tex
192ae941fe96f4712f6130236b1c5df7cbfe07fecc14559bec17390ca461b76b  manuscript/DEA_v0.3.5.1_working_draft_2026-11-16.pdf
f2a3ea1ffa02937c23d60a80945742d5fd75f5ed2a02fcc69a3b124b338bcd26  PR7:DEA-v0.3.5.1-Precision-Amendment-P01.md
f534449e2f01bcf7af8fce059f58d17009586e2cd52322af718449258d520e48  PR10:pilot-v0.1/REPORT.md
6bbd72da924047936d752b5cc01881c15107fbccbd0bd95ec7706f994039b0dd  PR11:v0.1/BASELINE_COMPARISON.md
```

The exact PR #12 input file digests and public prior-art snapshot digests are in its [SHA256SUMS](../../Gap-Register-Freeze-Review/v0.1.1/SHA256SUMS) and [SOURCE_MANIFEST.md](../../Gap-Register-Freeze-Review/v0.1.1/SOURCE_MANIFEST.md). Reverify the original input from the repo root:

```sh
review=research/Gap-Register-Freeze-Review/v0.1.1
(cd "$review" && bash verify.sh /absolute/path/to/v0.1.1.zip /absolute/path/to/D0.zip)
```

D0 TeX section “Typed surviving influence and the history boundary” begins at line 884. Equations v0351-conflict, v0351-decision and v0351-atomic start at 982, 1005 and 1029. D0 attributes adjudication to reviewer identity; artifact-targeted tokens alone do not add mandatory rubric controllers to the reviewer set. D1's P-01 explicitly expands it via the bound artifact set. This source-level finding is not an executed D0 or D1 result. Exact source separation and verified diff are prerequisites for the eventual participant mappings.
