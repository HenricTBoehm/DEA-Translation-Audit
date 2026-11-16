"""Single source for all four representations of the DEA representation study v0.1.1.

Every representation renders the SAME rule set (SR-1 + finite event grammar of
Gap-Register PR #13, commit b1631406) rule by rule. Each rule carries a visible
tag [R1]..[R12] that is identical in all conditions, so coverage can be checked
mechanically. Condition C' is NOT hand-written: it is C with every DEA term
replaced through TERMS_CPRIME (see build.py).

Semantics are fixed by vendor/pr13/oracle.py; the texts below are renderings of
that semantics, not alternatives to it. Where a text and oracle.py disagree,
oracle.py is authoritative and the text is a defect (see PROTOCOL §4.3).
"""

RULE_IDS = [f"R{i}" for i in range(1, 13)]

# --------------------------------------------------------------------------
# Terminology for C and C'. C' is produced by substituting these values.
# --------------------------------------------------------------------------
TERMS_C = {
    "FW": "DEA",
    "RoleE": "Execution",
    "RoleA": "Adjudication",
    "MayExecute": "MayEditScoreAtProduction",
    "MayAdjudicate": "MayAdjudicate",
    "Ctrl": "Ctrl",
    "Lin": "Lin",
    "Eff": "EffectiveControllers",
    "Bound": "Bound*",
    "J": "J*",
    "Exec": "Exec",
    "HC": "HistoryClosed",
    "RC": "RecordComplete",
    "WF": "WellFormedEvents",
    "CLEAR": "CLEAR",
    "CONFLICT": "CONFLICT",
    "UNDET": "UNDETERMINED",
    "INVALID": "INVALID",
    "OpGrant": "Grant",
    "OpRetract": "Retract",
    "OpRevoke": "Revoke",
    "OpModify": "Modify",
    "OpReset": "Reset",
    "OpProduce": "Execute",
    "OpSeal": "Seal",
    "OpBind": "Bind",
    "OpRead": "Consume",
    "OpAdj": "Adjudicate",
}

TERMS_CPRIME = {
    "FW": "typed influence model",
    "RoleE": "Producer",
    "RoleA": "Reviewer",
    "MayExecute": "HasScoreEditRightAtProduction",
    "MayAdjudicate": "MayFinalizeEvaluation",
    "Ctrl": "ActiveRight",
    "Lin": "FieldOrigin",
    "Eff": "CriterionInfluencers",
    "Bound": "ReadVersionSet",
    "J": "ReviewInfluenceSet",
    "Exec": "ScoreChoiceSet",
    "HC": "HistoryCoverage",
    "RC": "ReadCoverage",
    "WF": "ValidRecordShape",
    "CLEAR": "MayRelease",
    "CONFLICT": "CommonInfluence",
    "UNDET": "InsufficientEvidence",
    "INVALID": "InvalidRecord",
    "OpGrant": "ActivateRight",
    "OpRetract": "WithdrawRight",
    "OpRevoke": "DisableKey",
    "OpModify": "WriteSuccessor",
    "OpReset": "ResetChannel",
    "OpProduce": "ProduceOutput",
    "OpSeal": "SealOutput",
    "OpBind": "FixVersionView",
    "OpRead": "ReadVersion",
    "OpAdj": "Finalize",
}

# Vocabulary that must not occur in A, B or C' rule texts or evidence renderings.
DEA_LEXICON = [
    "DEA", "MayExecute", "MayAdjudicate", "Ctrl", "EffectiveControllers", "Bound*",
    "J*", "HistoryClosed", "RecordComplete", "WellFormedEvents", "Adjudicat",
    "Execution", "Distinction", "Consume", "CLEAR",
]

# --------------------------------------------------------------------------
# Rule texts. Keys: condition -> rule id -> text.
# --------------------------------------------------------------------------
RULES = {"A": {}, "B": {}, "C": {}}

# ---------------------------------- A -------------------------------------
RULES["A"]["R1"] = """Setting. There are four signing keys. Key ka belongs to person p, key kq to person q, key kj to the evaluator j, and key ki to the administrator. There is one output, x@1, whose score is an integer from 0 to 3. There are three criterion documents r, s and t, each in versions @0, @1 and @2 (for example r@0, r@1, r@2). Every version has two fields, threshold and layout, each 0 or 1. All @0 versions start with threshold 0 and layout 0, and nobody is recorded as author of these starting values. The evaluation rule is called sum-thresholds@1: the output is accepted if its score is at least the sum of the thresholds of the criterion versions that the evaluator actually read."""

RULES["A"]["R2"] = """Format of records. Every record has an id, a time and a rank, plus the fields of its type. Ids, times and ranks are whole numbers from 0 to 15; a rank may be marked unverified. Ids must be unique. Only the administrator's key ki may grant, retract, revoke or reset. Only the evaluator's key kj may seal, bind, read and finalize. The output may be produced with ka, kq or kj; its score is 0 to 3. Rights are given only to ka or kq, and only on the score of x or on the threshold or layout field of r, s or t. Only ka or kq can be revoked. A written or reset version must be the next number of the same document as its base (r@0 to r@1, r@1 to r@2); written values are 0 or 1. Produce, seal, bind and finalize all name x@1; seal, bind and finalize name the rule sum-thresholds@1; bind names a syntactically allowed version as root; a read names a version and either no parent or a version name as parent. If any record breaks these format rules, the case is invalid."""

RULES["A"]["R3"] = """Order. Records take effect in order of rank. Ranks must all differ, and along the rank order the times may never decrease (equal times are allowed; then rank decides). If some ranks are unverified, every way of giving them unused ranks from 0 to 15 that keeps the times non-decreasing is a possible order."""

RULES["A"]["R4"] = """Rights and revocation. A grant gives one key one right (on the score of x, or on one field of one document). Granting a right the key already holds, or granting anything to a revoked key, is impossible. A retract removes a right the key currently holds; retracting a right that is not held is impossible. A revoke permanently disables a key: any later record signed with that key is impossible, and revoking the same key twice is impossible. Retracting and revoking do not change any existing version."""

RULES["A"]["R5"] = """New versions. A write by key k creates a new version from a base version. The base must be the newest existing version of that document, the new version must not exist yet, and k must at that moment hold the right on the written field of that document. The new version copies both fields and their author records from the base, except the written field. If the written value differs from the base value, k (through the grant that gave it the right, and this write) becomes the only recorded author of that field in the new version. If the value is unchanged, the earlier author record of that field is kept. A reset by the administrator also creates the next version of the document from its newest version; the named field is set to 0 and has no recorded author there; the other field and its author record are copied. Each version can be created only once."""

RULES["A"]["R6"] = """Main sequence. Produce, seal, bind and finalize each happen exactly once and in this order, and nothing may happen after finalize. If the producing key holds the right on the score of x at the moment of producing, the person behind that key could choose the score. Otherwise the produced score must be 0. Bind names the root, which must already exist. At bind, the following are frozen: all versions existing at that moment, which version is the newest of each document, and the rights then held by keys that are not revoked."""

RULES["A"]["R7"] = """Reads. Reads happen after bind and before finalize. The first read must be the root and has no parent. Every further read names, as its parent, a version that was already read, and may not be the root. Each document can be read in at most one version, and only versions that existed at bind can be read."""

RULES["A"]["R8"] = """Influence on a criterion. A person has influence on a version that was read if (a) that person's key is a recorded author of the threshold field of exactly that version, or (b) at bind that version was the newest version of its document, it is not an @2 version (so a next version could still be made), and that person's key held, at bind and without being revoked, the right on the threshold of that document."""

RULES["A"]["R9"] = """Conflict. There is a conflict if the person who could choose the score (see Main sequence) also has influence on at least one version that was read. Signing the production without the score right gives no such ability. Changes to the layout field, and rights on documents that were never read, do not create influence."""

RULES["A"]["R10"] = """Completeness statements. Each case states two yes/no facts. "History complete" means every record other than reads is present. "Reads complete" means every read that took place is listed. If reads are stated complete, at least the root read must be present. If reads are not stated complete and no read is listed, there must be a free rank strictly between bind and the last listed record, where the missing root read could fit; otherwise the case is impossible."""

RULES["A"]["R11"] = """Decision. Work through these steps in order. 1. If any record breaks the format rules, answer INVALID. 2. If history is not complete, answer BLOCK_UNDETERMINED with reason history_not_closed; but if no possible order satisfies the restricted order check, answer INVALID. 3. If history is complete and no possible order satisfies all rules on rights, versions, main sequence, reads and completeness, answer INVALID. 4. If any rank is unverified, answer BLOCK_UNDETERMINED with reason rank_unverified. 5. If there is a conflict, answer BLOCK_CONFLICT and give the evidence for it. 6. Otherwise, if reads are complete, answer RELEASE. 7. Otherwise answer BLOCK_UNDETERMINED with reason dependencies_not_closed.
With open history, the listed lifecycle stages must be a subsequence of produce, seal, bind, finalize, without repeats. No event may follow a listed finalize. If a bind appears, no read may precede it. Disallow revoked signer use, repeated revocation and duplicate version creation. Do not apply closed-history replay to an open history."""

RULES["A"]["R12"] = """Do not conclude more than the rules allow. Revoking a key or retracting a right does not remove an author already recorded in an existing version. A reset neutralizes only the field it names, and only in the new version it creates; it does nothing for a different version that was bound or read. A completeness statement is taken as given; you are not asked to judge whether it is true."""

# ---------------------------------- B -------------------------------------
RULES["B"]["R1"] = """STATE MODEL
- Principals and keys: p:ka, q:kq, j:kj (evaluator), admin:ki.
- Output: x@1 with score in {0,1,2,3}.
- Documents: {r, s, t}; versions d@0, d@1, d@2.
- Version state: threshold in {0,1}, layout in {0,1}; each field carries an author set.
- Initial state: every d@0 has threshold=0, layout=0, author sets empty.
- Acceptance rule sum-thresholds@1: accept iff score >= sum of threshold over all read versions."""

RULES["B"]["R2"] = """RECORD SCHEMA (any violation => INVALID)
- Common fields: id, time, rank. id, time in 0..15; rank in 0..15 or unverified. ids unique.
- GRANT/RETRACT: signer ki; subject in {ka,kq}; (target,channel) = (x,score) or (d,threshold|layout) with d in {r,s,t}.
- REVOKE: signer ki; subject in {ka,kq}.
- WRITE: any key from the table; base, new in versions of the same document; number(new) = number(base)+1; channel in {threshold,layout}; value in {0,1}.
- RESET: signer ki; base/new as for WRITE; channel in {threshold,layout}.
- PRODUCE: signer in {ka,kq,kj}; version x@1; value in 0..3.
- SEAL / FINALIZE: signer kj; version x@1; rule sum-thresholds@1.
- BIND: signer kj; version x@1; rule sum-thresholds@1; root is a version name.
- READ: signer kj; version is a version name; parent = none or a version name."""

RULES["B"]["R3"] = """ORDERING
- Apply records in ascending rank. Ranks are pairwise distinct.
- time must be non-decreasing along rank order (ties allowed; rank breaks ties).
- Unverified ranks: every assignment of unused ranks 0..15 that keeps time non-decreasing is a candidate order."""

RULES["B"]["R4"] = """TRANSITIONS: RIGHTS
| Record  | Precondition (else contradiction)            | Effect |
| GRANT   | right not active; subject not revoked        | right(subject,target,channel) active |
| RETRACT | right active                                 | right inactive |
| REVOKE  | subject not already revoked                  | subject revoked; any later record signed by subject = contradiction |
- RETRACT and REVOKE do not modify any version."""

RULES["B"]["R5"] = """TRANSITIONS: VERSIONS
| Record | Precondition (else contradiction) | Effect on new version |
| WRITE  | base = current head of document; new not yet created; signer holds active right(signer,document,channel) | copy base; set channel:=value; if value != base value: authors(channel) := {(signer, granting record, this record)}; else keep authors(channel) |
| RESET  | base = current head; new not yet created | copy base; channel := 0; authors(channel) := empty |
- new becomes the head of its document. Each version is created at most once."""

RULES["B"]["R6"] = """TRANSITIONS: MAIN SEQUENCE
- PRODUCE < SEAL < BIND < FINALIZE, each exactly once; no record after FINALIZE.
- PRODUCE: if signer holds active right(signer,x,score) => ScoreChooser := owner(signer); else ScoreChooser is undefined and value must be 0 (else contradiction).
- BIND: root must exist. Snapshot: existing versions, head of each document, active rights of non-revoked keys."""

RULES["B"]["R7"] = """TRANSITIONS: READS
- READ only after BIND and before FINALIZE.
- First READ: version = root, parent = none.
- Later READ: parent already read; version != root.
- At most one read version per document; version must exist in the BIND snapshot."""

RULES["B"]["R8"] = """DERIVED RELATION Influence(P, v) for a read version v
- (a) P owns a key in authors(threshold) of v; or
- (b) in the BIND snapshot: v = head of its document, number(v) < 2, and P's key holds an active, non-revoked right(key, document(v), threshold)."""

RULES["B"]["R9"] = """CONFLICT RULE
- Conflict iff ScoreChooser is defined and Influence(ScoreChooser, v) holds for some read version v.
- Not sufficient: producing without score right; layout writes; rights on unread documents."""

RULES["B"]["R10"] = """COMPLETENESS FLAGS
- history_closed=true: all non-READ records are present.
- dependencies_closed=true: all performed READs are present; then at least the root READ must be present.
- dependencies_closed=false and no READ present: a free rank strictly between BIND and the last record must exist (slot for the root READ); else contradiction."""

RULES["B"]["R11"] = """DECISION CHECKLIST (first matching line wins)
1. Schema violation => INVALID.
2. history_closed=false => BLOCK_UNDETERMINED [history_not_closed]; except: no candidate order satisfies the restricted order check => INVALID.
3. history_closed=true and no candidate order is contradiction-free under R4-R7 and R10 => INVALID.
4. any rank unverified => BLOCK_UNDETERMINED [rank_unverified].
5. Conflict => BLOCK_CONFLICT with witness.
6. dependencies_closed=true => RELEASE.
7. else => BLOCK_UNDETERMINED [dependencies_not_closed].
Restricted order predicate with open history: recorded lifecycle stages form a subsequence of PRODUCE, SEAL, BIND, FINALIZE, without repeats. Reject records after FINALIZE, READ before observed BIND, use of revoked signer, repeated revocation or duplicate version creation. Closed-history replay guards do not apply here."""

RULES["B"]["R12"] = """NON-INFERENCES
- REVOKE/RETRACT do not remove authors already recorded in existing versions.
- RESET neutralizes only its channel and only in the version it creates; other bound/read versions are unaffected.
- Completeness flags are taken as given; their truth is not assessed."""

# ---------------------------------- C -------------------------------------
# {T:Name} tokens are substituted from TERMS_C (C) or TERMS_CPRIME (C').
RULES["C"]["R1"] = """Signature. Principals {p, q, j, admin}; key ownership pi(ka)=p, pi(kq)=q, pi(kj)=j, pi(ki)=admin. The {T:RoleE} role is held by the principal executing x@1; the {T:RoleA} role is held by j via kj ({T:MayAdjudicate}(kj)); ki is the administrative authority. Output x@1 with score sigma in {0,1,2,3}. Criterion versions V = { d@n : d in {r,s,t}, n in {0,1,2} }, each with channels ch in {threshold, layout}, value val(v,ch) in {0,1} and controller lineage {T:Lin}(v,ch). Initially val(d@0,ch)=0 and {T:Lin}(d@0,ch) = empty. Policy sum-thresholds@1: Accept iff sigma >= sum over v in {T:Bound}(x) of val(v,threshold)."""

RULES["C"]["R2"] = """{T:WF} (structural part). An event is e = (id, op, key, time, rank, args) with id, time in 0..15, rank in 0..15 or unverified; ids unique. {T:OpGrant}, {T:OpRetract}, {T:OpRevoke}, {T:OpReset} require key ki; {T:OpSeal}, {T:OpBind}, {T:OpRead}, {T:OpAdj} require key kj; {T:OpProduce} requires key in {ka,kq,kj} and score 0..3. {T:Ctrl} grants and retracts concern subject in {ka,kq} and (x, score) or (d, threshold|layout); {T:OpRevoke} concerns ka or kq. {T:OpModify}/{T:OpReset}: base and new version of the same d with n(new) = n(base)+1, channel threshold|layout, modified value 0|1. {T:OpProduce}, {T:OpSeal}, {T:OpBind}, {T:OpAdj} name x@1; {T:OpSeal}, {T:OpBind}, {T:OpAdj} name sum-thresholds@1; {T:OpBind} names a version as root; {T:OpRead} names a version and parent none or a version. Any violation: {T:WF} = false, decision {T:INVALID}."""

RULES["C"]["R3"] = """Order. Events apply in rank order; ranks pairwise distinct; time non-decreasing along rank (ties resolved by rank). Unverified ranks: the admissible orders are all assignments of unused ranks 0..15 that keep time non-decreasing."""

RULES["C"]["R4"] = """{T:Ctrl} dynamics. {T:OpGrant}(ki: {T:Ctrl}+(k, target.ch)) requires {T:Ctrl}(k,target,ch) inactive and k not revoked; it activates it. {T:OpRetract} requires {T:Ctrl}(k,target,ch) active; it deactivates it. {T:OpRevoke}(ki: k) requires k not revoked; afterwards every event signed by k is a contradiction. {T:OpRetract} and {T:OpRevoke} leave every existing version and its {T:Lin} unchanged."""

RULES["C"]["R5"] = """Version transitions. {T:OpModify}(k: base -> new, ch := val) requires base = head(d), new not yet created, and {T:Ctrl}(k,d,ch) active via grant g. new copies base; val(new,ch) := val; if val differs from val(base,ch) then {T:Lin}(new,ch) := {(k, g, e)} else {T:Lin}(new,ch) := {T:Lin}(base,ch). {T:OpReset}(ki: base -> new, ch := 0) requires base = head(d), new not yet created; new copies base with val(new,ch) := 0 and {T:Lin}(new,ch) := empty. new becomes head(d); each version is created at most once."""

RULES["C"]["R6"] = """Lifecycle. {T:OpProduce} < {T:OpSeal} < {T:OpBind} < {T:OpAdj}, each exactly once; no event after {T:OpAdj}. {T:MayExecute}(k, x) holds iff {T:Ctrl}(k, x, score) is active at {T:OpProduce}; then {T:Exec}(x) := {pi(k)}, otherwise {T:Exec}(x) := empty and the produced score must be 0. {T:OpBind} requires an existing root and freezes: the set of existing versions, head_bind(d) for each d, and the active {T:Ctrl} of non-revoked keys ({T:Ctrl}_bind)."""

RULES["C"]["R7"] = """{T:Bound}(x). {T:OpRead} events occur after {T:OpBind} and before {T:OpAdj}. The first {T:OpRead} is the root with parent none; each further {T:OpRead} has a parent already in {T:Bound}(x) and is not the root. At most one version per d; only versions frozen at {T:OpBind}. {T:Bound}(x) is the set of versions so read."""

RULES["C"]["R8"] = """{T:Eff}(v) for v in {T:Bound}(x) = { pi(k) : (k,g,e) in {T:Lin}(v, threshold) } united with { pi(k) : v = head_bind(d(v)), n(v) < 2, {T:Ctrl}_bind(k, d(v), threshold) }. {T:J}(x) = union of {T:Eff}(v) over v in {T:Bound}(x)."""

RULES["C"]["R9"] = """Conflict(x) iff {T:Exec}(x) intersected with {T:J}(x) is non-empty. Identity of the signer of {T:OpProduce} without {T:MayExecute} gives no element of {T:Exec}(x); layout lineage and {T:Ctrl} on unread documents give no element of {T:J}(x)."""

RULES["C"]["R10"] = """Closure premises. {T:HC} = true: every non-{T:OpRead} event is in the record. {T:RC} = true: every performed {T:OpRead} is in the record; then the root {T:OpRead} must be present. If {T:RC} = false and no {T:OpRead} is recorded, a free rank strictly between {T:OpBind} and the last event must exist for the root {T:OpRead}; otherwise contradiction."""

RULES["C"]["R11"] = """Decision function (first applicable clause). 1. {T:WF} = false: {T:INVALID}. 2. {T:HC} = false: {T:UNDET} (history_not_closed), unless no admissible order satisfies the restricted order check: {T:INVALID}. 3. {T:HC} = true and no admissible order is contradiction-free under R4-R7 and R10: {T:INVALID}. 4. Some rank unverified: {T:UNDET} (rank_unverified). 5. Conflict(x): {T:CONFLICT} with witness. 6. {T:RC} = true: {T:CLEAR}. 7. Otherwise: {T:UNDET} (dependencies_not_closed). Output mapping: {T:CLEAR} = RELEASE, {T:CONFLICT} = BLOCK_CONFLICT, {T:UNDET} = BLOCK_UNDETERMINED, {T:INVALID} = INVALID.
Restricted order predicate if {T:HC} is false: recorded stages form a subsequence of {T:OpProduce}, {T:OpSeal}, {T:OpBind}, {T:OpAdj}, without repeats. Reject events after {T:OpAdj}, {T:OpRead} before observed {T:OpBind}, use of revoked signer, repeated revocation or duplicate version creation. Do not apply closed-history replay."""

RULES["C"]["R12"] = """Non-inferences. {T:OpRevoke} and {T:OpRetract} do not remove {T:Lin} entries of existing versions. {T:OpReset} clears {T:Lin} only for its channel and only in the version it creates; versions in {T:Bound}(x) other than that one are unaffected. {T:HC} and {T:RC} are premises supplied with the record; their truth is not assessed."""

PREAMBLE = {
    "A": "You are checking whether an evaluation result may be released. The rules below define the situation and the decision.",
    "B": "You are checking whether an evaluation result may be released. The specification below defines the state model, transitions and decision checklist.",
    "C": "You are checking whether an evaluation result may be released. The {T:FW} formalization below defines the decision. {T:MayExecute} is only the study's score-edit right at production.",
}

# --------------------------------------------------------------------------
# Shared answer instructions: byte-identical in every condition.
# --------------------------------------------------------------------------
COMMON_WIRE = """EVIDENCE FORMAT
The evidence JSON contains events, history_closed and dependencies_closed.
Each event has exactly id, kind, key, time, rank and these additional fields:
grant/retract: subject, target, channel; revoke: subject;
modify: base, version, channel, value; reset: base, version, channel;
produce: version, value; seal/adjudicate: version, policy;
bind: version, root, policy; read: version, parent.
Numeric ids, times, ranks and values are JSON integers, not booleans.
rank null means unverified; parent null means no parent. Unrecognized kinds
and missing or extra fields are invalid. Numeric array position is a zero-based
row locator, distinct from event id and temporal rank. Do not invent missing events."""

ANSWER_INSTRUCTIONS = """ANSWER FORMAT
Return one JSON object with verdict, witness, missing, certificate and
justification (at most 80 words). Verdict: RELEASE, BLOCK_CONFLICT,
BLOCK_UNDETERMINED or INVALID. Unused witness and certificate are null;
unused missing is [].
BLOCK_CONFLICT witness: principal (p/q), criterion_version, route
(recorded_author/bind_time_right), event_ids and optional extra_event_ids.
Required IDs: production, score grant, criterion grant, bind, read, and
write for recorded_author. Only ancestor reads on that read path may be extras.
BLOCK_UNDETERMINED: list applicable reasons (history_not_closed,
rank_unverified, dependencies_not_closed), including the one used by the rule.
RELEASE: certificate {"code":"coverage_replay","rows":[bind and adjudicate
row locators]}. The decision is conditional on both supplied closure flags
and checked replay with no supported conflict.
INVALID: certificate has code and rows. authenticated_grammar cites one bad
row or both rows with duplicate ids. no_structural_completion and
no_closed_completion cite all row locators for the bounded impossibility
check; an empty record uses []. Cite these indices even if event ids are invalid."""

USER_FOOTER = "Apply the rules to this case and answer in the required JSON format."

# --------------------------------------------------------------------------
# Evidence rendering templates. {field} = wire field; {T:Name} = term (C only).
# Templates must be injective; build.py verifies by parsing every rendering back.
# --------------------------------------------------------------------------
EVENT_TEMPLATES = {
    "A": {
        "grant": "Record {id} (time {time}, rank {rank}): key {key} grants key {subject} the right on the {channel} of {target}.",
        "retract": "Record {id} (time {time}, rank {rank}): key {key} retracts from key {subject} the right on the {channel} of {target}.",
        "revoke": "Record {id} (time {time}, rank {rank}): key {key} revokes key {subject}.",
        "modify": "Record {id} (time {time}, rank {rank}): key {key} writes {channel} = {value} into new version {version}, based on {base}.",
        "reset": "Record {id} (time {time}, rank {rank}): key {key} resets {channel} to 0 in new version {version}, based on {base}.",
        "produce": "Record {id} (time {time}, rank {rank}): key {key} produces {version} with score {value}.",
        "seal": "Record {id} (time {time}, rank {rank}): key {key} seals {version} under rule {policy}.",
        "bind": "Record {id} (time {time}, rank {rank}): key {key} binds {version} under rule {policy} with root {root}.",
        "read": "Record {id} (time {time}, rank {rank}): key {key} reads {version} (parent: {parent}).",
        "adjudicate": "Record {id} (time {time}, rank {rank}): key {key} finalizes the evaluation of {version} under rule {policy}.",
    },
    "B": {
        "grant": "#{id} t={time} rank={rank} GRANT by={key} subject={subject} target={target} channel={channel}",
        "retract": "#{id} t={time} rank={rank} RETRACT by={key} subject={subject} target={target} channel={channel}",
        "revoke": "#{id} t={time} rank={rank} REVOKE by={key} subject={subject}",
        "modify": "#{id} t={time} rank={rank} WRITE by={key} base={base} new={version} channel={channel} value={value}",
        "reset": "#{id} t={time} rank={rank} RESET by={key} base={base} new={version} channel={channel}",
        "produce": "#{id} t={time} rank={rank} PRODUCE by={key} version={version} value={value}",
        "seal": "#{id} t={time} rank={rank} SEAL by={key} version={version} rule={policy}",
        "bind": "#{id} t={time} rank={rank} BIND by={key} version={version} rule={policy} root={root}",
        "read": "#{id} t={time} rank={rank} READ by={key} version={version} parent={parent}",
        "adjudicate": "#{id} t={time} rank={rank} FINALIZE by={key} version={version} rule={policy}",
    },
    "C": {
        "grant": "e{id} [t={time}; rank={rank}] {T:OpGrant}({key}: {T:Ctrl}+({subject}, {target}.{channel}))",
        "retract": "e{id} [t={time}; rank={rank}] {T:OpRetract}({key}: {T:Ctrl}-({subject}, {target}.{channel}))",
        "revoke": "e{id} [t={time}; rank={rank}] {T:OpRevoke}({key}: {subject})",
        "modify": "e{id} [t={time}; rank={rank}] {T:OpModify}({key}: {base} -> {version}, {channel} := {value})",
        "reset": "e{id} [t={time}; rank={rank}] {T:OpReset}({key}: {base} -> {version}, {channel} := 0)",
        "produce": "e{id} [t={time}; rank={rank}] {T:OpProduce}({key}: {version}, score := {value})",
        "seal": "e{id} [t={time}; rank={rank}] {T:OpSeal}({key}: {version}, {policy})",
        "bind": "e{id} [t={time}; rank={rank}] {T:OpBind}({key}: {version}, {policy}, root = {root})",
        "read": "e{id} [t={time}; rank={rank}] {T:OpRead}({key}: {version} <- {parent})",
        "adjudicate": "e{id} [t={time}; rank={rank}] {T:OpAdj}({key}: {version}, {policy})",
    },
}

FLAG_TEMPLATES = {
    "A": ("History complete (all records other than reads are present): {history_closed}.",
          "Reads complete (every read that took place is listed): {dependencies_closed}."),
    "B": ("history_closed={history_closed}", "dependencies_closed={dependencies_closed}"),
    "C": ("{T:HC} = {history_closed}", "{T:RC} = {dependencies_closed}"),
}
BOOL_WORDS = {"A": ("yes", "no"), "B": ("true", "false"), "C": ("true", "false")}
EVIDENCE_HEADER = {"A": "CASE RECORDS", "B": "CASE LOG", "C": "EVENT RECORD"}
NULL_RANK = "unverified"
NULL_PARENT = "none"
