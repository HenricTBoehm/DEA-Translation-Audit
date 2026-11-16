# Experiment design, runtime procedure and cases

Phase A found 38 cases, 31 views, 114/114 identical raw/derived outcomes within a consumer, D0/D1/SR-1 agreement of 26/32/38 out of 38 against SR-1, plus 38/38 D1 matches in alternative Rego. Phase B studies acquisition. It does not repeat that decision experiment or infer comparative superiority from synthetic public cases.

## Procedure and independent reference

A parent creates one isolated temporary directory per evaluation. It publishes the score, policy, resolver versions and thresholds under filenames containing SHA-256, using exclusive create and read-only file mode. A logical threshold artifact changes only by publishing a fresh version. The parent rechecks digests, metadata and inode/size before and after observation. The mutable file binding.json points to an immutable resolver, which names an immutable threshold. The isolated child checks content addresses as it reads the score, policy and resolver, opens the selected threshold and actually reads its bytes. It executes the versioned predicate score >= threshold for score in {0,1,2,3}, threshold in {0,1}. It emits the numeric decision as stdout. The E1 assertions use a separate stderr record.

Three ordered checkpoints fence the checked binding, threshold-open and threshold-read steps. E2 watches the directory across the same real execution. A separate assessor reads the child's descriptor link, device/inode and offset before and after the threshold read, matches it to the pre/post manifest and checks arithmetic with an independent finite truth expression. Neither E1 nor E2 receives those descriptor results. The controller action schedule and expected path stay assessor-only. The kernel and controller are trusted. Process checkpoints synchronize observation, while observed descriptor identity and offset come from the kernel. The reference confirms the exact file and full-length offset advance in this controlled evaluator, independently of its trace and E2. Actual semantic use is further supported by the reviewed procedure and stdout consistency. It is not a proof against an arbitrary program seeking and fabricating output, nor an independent verifier of all computation.

The controller records synthetic writer, selector and authority roles, and realizes their concrete artifact publication and binding intervention as filesystem operations. All run under one test OS user. The role history is a controlled model input, not a signature audit or identification of independent OS users. Controller permissions and the actual FD are separate evidence. Stable file names and read-only permissions are fixture and capture assumptions, not privileged immutable OS enforcement. Each child exchanges data only through the local root and pipes in this experiment. No network calls exist in the evaluator.

| Case | Controlled intervention | Assessor-confirmed threshold and scientific output |
|---|---|---|
| B01 | No producer write or selection authority | r@0 (0), accept |
| B02 | Producer writes and can select r@1 | r@1 (1), reject |
| B03 | Producer creates r@1, independent resolver fixes r@0 | r@0 (0), accept |
| B04 | Producer can select; q created r@1 | r@1 (1), reject |
| B05 | Producer writes r@1 and loses key before read | r@1 (1), reject; surviving provenance |
| B06 | Independent threshold reset to r@2 plus authorized rebind | r@2 (0), accept; old r@1 unmodified |
| B07 | Actual r@1 read omitted from E1 | r@1 (1), reject |
| B08 | E1 coherently claims the real alternate r@0; score 1 preserves outcome under either | r@1 (1), accept |
| B09 | Producer changes layout alone, new version | r@1 (0), accept |
| B10 | Checked r@0; replace pointer by atomic rename; child intentionally resolves again | r@1 (1), reject; exact bind/read mismatch |

B10 tests a bounded within-run change. Atomic rename gives one pointer snapshot to each individual read, not atomicity across the whole decision. At commit the policy sees an invalid version relation. Only a proposed adjudication is evaluated. No effective commit, transaction-time access enforcement or production TOCTOU exploit is exercised. B07/B08 are deliberately induced application evidence defects, not incidence estimates.
