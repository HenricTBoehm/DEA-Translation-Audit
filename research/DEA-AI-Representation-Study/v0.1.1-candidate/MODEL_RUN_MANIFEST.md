# Model run manifest · interface v1 draft

Use immutable run config and append-only per-attempt JSONL plus independently signed release map. The stored manifest may be private. Field contract:

| Record | Required fields |
|---|---|
| Run config | schema_version, run_id, provider, request_model_id, pinned_snapshot_or_unavailable, planned_arm_set, task_id, tokenizer_version_or_unavailable, supported_decoding_keys, requested_decoding, effective_decoding_or_explicit_unknown, max_input_tokens, max_output_tokens, tools=false, retrieval=false, fresh_context=true, prompt_template_digests_by_arm, randomization_method, schedule_digest, seed_private_locator, frozen_at, cohort_designation, prior_DEA_development_exposure (yes/no/unknown and source), transport/runtime versions |
| Scheduled request | opaque_run_token, arm, study_stratum (assessor-only if revealing), evidence_digest, sent_prompt_digest, sampling_index, randomized_order_index, request settings reference, stable schedule status |
| Returned attempt | opaque_run_token, attempt_index, actual provider/model/snapshot if returned and status if unknown, actual settings as returned, UTC started_at, duration_ms, input_tokens and output_tokens or explicit unavailable, raw_output or null, completion_status, failure_type, request ID if allowed, retry_reason and predecessor, provider stop reason |
| Assessment | opaque_run_token, evidence_digest, oracle_version, certificate ledger reference, score version, parse status and aggregate inclusion, adjudication log; this record remains outside the runner and participant |

Lock raw prompt/system bytes and evidence bytes independently. Retain raw replies even when parse fails, subject to private storage rules. Audit exact transport equality for A/B/C/C′ except rule body; no conversation memory or tools. Fail closed on duplicate/unplanned tokens, unapproved drift, holdout hint fields or missing required metadata without explicit status. Document unsupported properties such as seeds or snapshots as unknown. Retry transport failures only using the same request under a preset ceiling of one retry, before visibility of any answer. Never retry a bad verdict. Log all terminal failures and schedule slots. Preselect a fixed primary model and one sample index; development-used models belong in a separate sensitivity stratum. No manifest from a model run was produced during revision.
