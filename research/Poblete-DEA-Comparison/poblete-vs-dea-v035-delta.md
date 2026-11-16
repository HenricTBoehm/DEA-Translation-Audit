# Poblete et al. (2026) against DEA v0.3.5 working draft: what changed relative to v0.3.4.3

| | |
|---|---|
| **New reference** | `uploads/DEA_v0.3.5_working_draft_2026-11-16.pdf` / `.tex`, 39 pp. The draft is non-adopted. Page numbers refer to the PDF. |
| **Previous comparison** | `poblete-vs-dea-comparison.md` and `crosswalk-poblete-dea.csv` (against v0.3.4.3) |
| **Executable check** | `poblete_v035_check.py`, which writes `poblete-v035-results.json` |
| **Assumption** | "v0.5" in the request is read as this v0.3.5 working draft. |

## 1 Status of each earlier finding under v0.3.5

| # | Finding against v0.3.4.3 | v0.3.5 (page) | Status |
|---|---|---|---|
| F1 | Poblete must be cited; its distinctions (Eq. 1–3) overlap DEA Eq. 14/15/17/35 | Cited and positioned as "a contextual and prospective comparator, not evidence that DEA's own formal rules are correct or novel" (p.8). Listed as material prior art (p.30). | **Addressed** |
| F2 | Poblete is an arm-R instance (prompt contracts, procedural verification) | Arm R definition unchanged (p.25). Poblete is not named as an R instantiation. | Open, minor: could be stated at p.25 |
| F3 | Human acceptance is a conditional ExecConflict, dependent on an unreported control edge | New three-way outcome CONFLICT / NO_CONFLICT_ESTABLISHED / UNDETERMINED. MayAdjudicate requires RecordComplete (pp.10–11). | **Changed**: see §2 |
| F4 | Proposed ADR-001 O8: uncertainty about whether an edge exists, not only when it is active | "An unrecorded seal, contradictory timestamps, incomplete control graph or unverifiable identity mapping makes RecordComplete false … It does not by itself establish … ExecConflict" (p.13) | **Addressed**: fail-closed on permission, not on the conflict itself |
| F5 | Verification report produced by the executor needs its own seal (PB-3v) | A seal binds one object version, including "evidence/criteria references" (p.12). Executor-produced verification artifacts are not named as objects under the guard. | Open → ADR-003 |
| F6 | Acceptance thresholds sit inside the execution contract, but G_M ≠ sufficiency | G_M is still "not a judgment of scientific sufficiency" (p.14). E may report at most RESULT_READY_FOR_ADJUDICATION (p.14). There is no rule that acceptance criteria be kept separate from, or hidden from, E. | Partly addressed |
| F7 | Authorized ≠ evidentially sufficient (Poblete p.24) | "Permission does not imply … that its scientific content is correct" (p.11). There is no EvidenceSufficiency predicate. RecordComplete covers provenance completeness, not evidential sufficiency. | Open → ADR-003 |
| F8 | No predicate for the evidence status of transferred claims (REPORTED/VERIFIED) | Unchanged. "Narrative similarity is not identity" (p.18). | Open → ADR-003 |
| F9 | G-P1: no rule on D/E read access to the adjudication reference across supplementation cycles | State separation still forbids only silent *rewriting* (p.17). J still "receives … the relevant reference rubric" (p.14). Blinding applies only to pilot reviewers (p.29). | **Open** |
| F10 | Ledger analogies (repeated execution, Refinement without budget) | The ledger is explicitly unchanged (pp.14–15, p.37). | Open → ADR-002, as planned |
| F11 | Pilot: hold the human's role constant; held-out reference; freeze model versions | M/R/C unchanged (p.25). New RQ3 on the temporal conflict guard "relative to a justified comparator with the same evidence inputs" (p.5). | Partly addressed |

## 2 Poblete readings under the v0.3.5 gate

The readings are the same as before: p = Human Orchestrator, a = Data Engineering Agent, j = the human's acceptance identity.

| Reading | As reported (RecordComplete = false) | With an assumed complete record |
|---|---|---|
| PB-1 Human can alter the executor during execution | CONFLICT | CONFLICT |
| PB-2 Only Stage-4 authorization as pre-stage manifest | **UNDETERMINED** | NO_CONFLICT_ESTABLISHED* |
| PB-3 Context injection after the seal; object x | **UNDETERMINED** | NO_CONFLICT_ESTABLISHED |
| PB-3v As PB-3; object = verification report | CONFLICT | CONFLICT |
| PB-4 Planner output relayed to the executor | **UNDETERMINED** | NO_CONFLICT_ESTABLISHED |

\*Only if the record start t₀ covers the Stage-4 authorization. That lookback question is open (v0.3.5 O2, p.38).

**Consequences:**

1. **As documented, Poblete's Stage-8 acceptance would not be permissible under v0.3.5 in any reading.** It is either CONFLICT or UNDETERMINED. The reasons are the paper's own: traceability "partially supported" (p.26), no "explicit identity and authorization mechanisms" (p.30), and incomplete historical records (pp.31–32).
2. **Under v0.3.4.3 the same case was only *conditionally* conflicting.** v0.3.5 is therefore strictly more restrictive here. The extra blocks come from **record incompleteness, not from a proven conflict**.
3. **This is a blocking risk the pilot does not yet measure.** Realistic human-in-the-loop deployments are likely to end in UNDETERMINED. Table 5 (p.26) has no metric for adjudications blocked because RecordComplete is false. Without one, the "wrongly blocked decisions" from your priority 4 are not measured for this mechanism.

## 3 Divergences between v0.3.5 and ADR-001 (to record explicitly)

| Point | ADR-001 | v0.3.5 | Assessment |
|---|---|---|---|
| Missing seal | D-5: σ(x) := t_J (fail-closed conflict test) | Blocks the disposition until provenance is completed; no substitution (p.11) | More conservative. The ADR regression set is unaffected because no CM lacks a seal. |
| CM8 reset | Permitted under C-R | UNDETERMINED until reset scope and tie-ordering are formalized (pp.12, 38) | Withdrawn deliberately and documented |
| CM9 uncertain timing | ExecConflict = true | "Conservative conflict candidate; preserve uncertainty evidence" (p.38) | **Ambiguous**: CONFLICT or UNDETERMINED? Must be fixed in the regression table. |
| Test engine | `co-scientist-outputs/dea-adr-001/adr001_ctrl.py` exists | "The referenced generating Python program was not delivered … not independently rerun" (p.38, O8) | The program is in the workspace and can be supplied for O8 |

## 4 Limitations

- I read v0.3.5 selectively, not as a full diff against v0.3.4.3. I covered the status block and abstract, §1 RQs, related work (§2.7–2.8), the threat model, §3 temporal control, §4 D/E/J and ledger, §6 state separation, §11–13, the prior-art discussion, and Appendices C–D.
- Statements that something is "unchanged" rely on keyword search plus reading of those sections.
- Poblete's experience report and LATTICE [10] are still unread.
