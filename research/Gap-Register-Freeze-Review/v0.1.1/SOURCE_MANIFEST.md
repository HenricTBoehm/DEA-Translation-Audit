# Source manifest and evidentiary status

Verified 16 November 2026. Primary review package: DEA_Gap_Register_Differential_Audit_v0.1.1_Review_Package.zip, SHA-256 `754268ed45cd18321657dc7e7b26ec31e6bddb14f397af01fc86691763cbe166`. Exact version supplied in the task. This manifest is the versioned reference to the original package. The original bytes are an external input to the replay. ZIP CRC passes for all 11 members, ten manifest entries pass, and the bundled protocol texts match separately supplied v0.1 and v0.1.1 files. Original v0.1 Markdown matches its declared hash, whereas the historical v0.1 ZIP is NOT EXECUTED/unavailable as an exact verified artifact here. The latter historical hash is a claim of v0.1.1 and was not used as an input.

| GitHub ref inspected | Exact commit | Evidence used |
|---|---|---|
| main | 2fc5e7f353f1984e663110e3eb0a0d9e38ba7fa4 | Repository base |
| PR #7 | 91e842fdae94356ff323f3afb2e99245369108da | Source-level D1/P-01 specification and implementation |
| PR #10 | 96731f6ac458dd7b0d9ec855eec0036d91f47467 | Prior HR-1 and Decision Stability report, scope and evidence limits |
| PR #11 | 7fee1797e31963fe60720476d8f34305148e2415 | Prior Q-C and C+S/D comparative result; full-equivalence question remains open |

The three PR heads matched their specified SHAs and were open drafts. Q-C is the earlier omitted-standard example, HC-1 is the original D0 pre-window surviving criterion example (TeX lines 924 ff.), and S04/S12 are past pilot findings. None becomes a new benchmark outcome here. The full D0 original, rather than a summary, is the archived manuscript in its v0.3.5.1 draft review package. Its whole package manifest verified. This review used the exact TeX; the PDF fingerprint is also recorded. Historical executions were not counted as part of this run.

## Exact input bytes

```text
754268ed45cd18321657dc7e7b26ec31e6bddb14f397af01fc86691763cbe166  DEA_Gap_Register_Differential_Audit_v0.1.1_Review_Package.zip
636a27cfeec63a5859fe54462457421e84a8712c8196aa5bb4a528615271cc9b  DEA_Gap_Register_Differential_Audit_Protocol_v0.1.1.md
72e7dcc945e9b93c4a872e0b0415eb089073927e182486a24a385c33d4832f62  DEA_Gap_Register_Differential_Audit_Protocol_v0.1.md
2500b01f3a4c806a0d4fcdafadf4c42457d312f1bf23e374ce3963fee4958486  CHANGELOG_v0.1_to_v0.1.1.md
39252b24d6218baf4d7a8b8d8c7c98ae19ec17841ca8da071b33a0deeaccfff3  COMPARATOR_MATRIX_v0.1.1.md
636a27cfeec63a5859fe54462457421e84a8712c8196aa5bb4a528615271cc9b  DEA_Gap_Register_Differential_Audit_Protocol_v0.1.1.md
72e7dcc945e9b93c4a872e0b0415eb089073927e182486a24a385c33d4832f62  DEA_Gap_Register_Differential_Audit_Protocol_v0.1.md
9ea33d0432bedfd759ae24f10aaaf6e97fbc4b57234d154c5bb02624199162ca  FREEZE_CHECKLIST_v0.1.1.md
c42ec67395f76508fe56220a8d2389480757eba45fcfc4edd9b95e828a59d88b  README.md
40a7a28ce61a48acbb9eaaba9bf9f4e48028eb0acc5c4df523cbc90b79100a2c  cases-v0.1.1.json
72f5eb98c36548f21884ea7a1db8b6f16faa70382abc54c5b09b7f4ddd6e1ffe  oracle-results-v0.1.1.json
6e38ea88967abe4f476fe66cff51369210cd2a9ea2caff319afc69134c828ec5  oracle.py
ad4a3c700edf6c047651a2b78f242e440e45371432290e7472494027d97ce876  test_oracle.py
51a1f79fb4188d5fe81fda6c65f1a5dfd05f940d65b75f215b10adbcb525f23b  SHA256SUMS
d655d4585970cb8cf2d605467b827c4b061daaab6041e554e402e944116630e9  DEA_v0.3.5.1_draft_review_package.zip
b36a06a8cdf3edcb0789e2c6980f65ae9d2ce7dcac62d8f00abd7cf9c70b8617  manuscript/DEA_v0.3.5.1_working_draft_2026-11-16.tex
192ae941fe96f4712f6130236b1c5df7cbfe07fecc14559bec17390ca461b76b  manuscript/DEA_v0.3.5.1_working_draft_2026-11-16.pdf
dfcf307af88a8ec076f282f35df67cc120874931707cc428b5d4311884e4d2d4  harness/dea_v0351_reference.py
0eeb9a16999366ce781533aae742d168e5e234c967e700ff65eaf073a019f94a  SHA256SUMS
f2a3ea1ffa02937c23d60a80945742d5fd75f5ed2a02fcc69a3b124b338bcd26  91e842fdae94356ff323f3afb2e99245369108da:research/Precision-Amendment-P01/DEA-v0.3.5.1-Precision-Amendment-P01.md
b10f02eff92f5ca06b03f63e1b991ce079fe6445327157dc9fd04acf882beb44  91e842fdae94356ff323f3afb2e99245369108da:research/Precision-Amendment-P01/p01.py
f534449e2f01bcf7af8fce059f58d17009586e2cd52322af718449258d520e48  96731f6ac458dd7b0d9ec855eec0036d91f47467:research/History-Remainder-Decision-Stability-Pilot/pilot-v0.1/REPORT.md
6bbd72da924047936d752b5cc01881c15107fbccbd0bd95ec7706f994039b0dd  7fee1797e31963fe60720476d8f34305148e2415:research/Decision-Question-Completeness-Audit/v0.1/BASELINE_COMPARISON.md
a4fc4a1d41e4a535f3ae52365f3186cc2ab33a580f30cbdc4e7a795987d21770  7fee1797e31963fe60720476d8f34305148e2415:research/Decision-Question-Completeness-Audit/v0.1/COUNTEREXAMPLES.md
```

## Public specification snapshots, candidate pins

Hashes below fingerprint retrieved payloads, including HTML presentation where applicable. Future HTML delivery can differ. Pin the normative text revision and the exact execution artifacts separately. No public spec payload has been redistributed with this PR.

| Snapshot | URL | SHA-256 |
|---|---|---|
| xacml-3.0.html | [xacml-3.0.html](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html) | `164d5e89893530f5a45b6183bcd4256fa39c44487495fc41fe27ae0110d1c7d7` |
| opa-1.0.0.html | [opa-1.0.0.html](https://github.com/open-policy-agent/opa/releases/tag/v1.0.0) | `babd06ab9a8b62be11dd7b1d4b251cc561bd53e40a3045e7ad147e0726e62953` |
| slsa-1.0.html | [slsa-1.0.html](https://slsa.dev/spec/v1.0/provenance) | `29c34f964bef9f26b53033160186def184a9b41498be9cc67ed5bfd9ab1a56b7` |
| slsa-0.1.html | [slsa-0.1.html](https://slsa.dev/provenance/v0.1) | `867fcdb5359a7336b42ed647d26ade81991eb1ed4aa6399b3835fec05985bf5b` |
| prov-dm.html | [prov-dm.html](https://www.w3.org/TR/2013/REC-prov-dm-20130430/) | `5c925c21bc96c285b25017c3b90d82cf74251d07713b71fcb81ca60f873c9e88` |
| rfc5280.txt | [rfc5280.txt](https://www.rfc-editor.org/rfc/rfc5280.txt) | `a2f2628c0a83b873fc4786abd921f9b2c02395954b655d190bf16b831633345d` |
| tuf-1.0.31.html | [tuf-1.0.31.html](https://theupdateframework.github.io/specification/v1.0.31/) | `6263ec6966ee36fa562bfde4b1bc4937822af3d95bf73b020973c5eef109d7c1` |
| nasa-7009b.pdf | [nasa-7009b.pdf](https://standards.nasa.gov/sites/default/files/standards/NASA/B/1/NASA-STD-7009B-Final-3-5-2024.pdf) | `7b95a2065325dc3035c35ce110557d817555d3f22210ce5f6ce0bb2fb4ccd8b4` |
| in-toto-1.0.md | [in-toto-1.0.md](https://raw.githubusercontent.com/in-toto/specification/926031f40be8db78f992f02f3e50e97a09db5320/in-toto-spec.md) | `17d3326e4cf58234619dbfe821cdc5187e55e2c89f7b63f03699c46588322097` |
