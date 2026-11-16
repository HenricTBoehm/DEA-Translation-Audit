#!/usr/bin/env python3
"""Encode the Poblete et al. (2026) workflow topology as DEA-ADR-001 control models (stdlib only).
Mapping: p = Human Orchestrator, j = the Human Orchestrator's acceptance identity (Stage 8; bound to p by
mutual identity edges over all T, ADR-001 s7), a = Data Engineering Agent (Stage 5 executor; also Stage 7
read-only verifier), o = Data Expert Agent (Stages 2-3). theta_E = {0,1} ~ Stages 5-6, t=2 ~ Stage 7, t=3 ~ Stage 8.
Which edges exist is NOT reported in the paper; each model is one reading. Usage:
  python3 poblete_adr001_check.py --out results.json
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dea-adr-001"))
import adr001_ctrl as A

ALL = {0, 1, 2, 3}
ID = {"p->j": ALL, "j->p": ALL}
READINGS = {
    "PB-1_human_can_alter_executor_during_execution": (
        A.M({**ID, "p->a": {0, 1}}, tE=1, tJ=3, sigma=1),
        "Human holds the executor's workspace credentials or can revise its contract/context while Stages 5-6 run "
        "(not reported; p.9 manual context transfer, p.30 no explicit identity/authorization mechanism)"),
    "PB-2_only_independent_pre_stage_manifest": (
        A.M({**ID}, tE=1, tJ=3, sigma=1),
        "Human's only influence is the Stage-4 authorization, treated as an independently issued pre-stage manifest "
        "(DEA p.8: does not establish control)"),
    "PB-3_post_seal_context_injection_before_verification_x": (
        A.M({**ID, "p->a": {2}}, tE=1, tJ=3, sigma=1),
        "Human relays context to the agent only after the execution evidence is persisted (Stage 6), before Stage 7; "
        "object = execution output x"),
    "PB-3v_same_reading_object_is_verification_report": (
        A.M({**ID, "p->a": {2}}, tE=2, tJ=3, sigma=2),
        "As PB-3, but the object judged is the Stage-7 verification report produced by the same agent"),
    "PB-4_planner_relay_via_human_during_execution": (
        A.M({**ID, "o->a": {1}}, tE=1, tJ=3, sigma=1),
        "Planner output copied unchecked into the executor's instructions during execution (Fig. 8, p.29), modelled "
        "as an unmediated planner->executor criteria edge; the planner has no control edge to the acceptor"),
}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="results.json"); a = ap.parse_args()
    out = {}
    for k, (m, d) in READINGS.items():
        c, w = A.conflict(m, "C", "causal")
        WE, WJ = A.windows(m, "causal")
        cE = A.ctrl_all(m, "C", WE)
        out[k] = {"reading": d, "edges": {e: sorted(s) for e, s in m["edges"].items()},
                  "t_exec": m["tE"], "seal": m["sigma"], "t_adj": m["tJ"],
                  "ExecConflict_C_causal": c, "common_controllers": w,
                  "human_may_assign_any_Sigma_adj": not c,
                  "Ctrl_E_controllers_of_executor": sorted(x for x in cE if "a" in cE[x]),
                  "audit_readings": {f"{s}/{an}": A.conflict(m, s, an)[0] for s in A.SEMS for an in A.ANCHORS}}
    json.dump(out, open(a.out, "w"), indent=1)
    for k, v in out.items():
        print(k, "ExecConflict=", v["ExecConflict_C_causal"], v["common_controllers"])


if __name__ == "__main__":
    main()
