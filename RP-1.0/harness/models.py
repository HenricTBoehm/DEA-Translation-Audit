"""Neutral model generators and regression scenarios (no verdict logic)."""
import itertools

USERS = ("a", "b", "c")


def mc_ej():
    """MC-EJ: 1-2 outputs; exec/adj users; disposition in {Accept, Hold, Reject, Supplement} (1 output)
    or {Accept, Hold} (2 outputs); grants = exactly-assigned or other-disposition-only; optional revocation
    of one user's execution permission (relevant only to snapshot formalisms)."""
    other = {"Accept": "Hold", "Hold": "Accept", "Reject": "Supplement", "Supplement": "Reject"}
    for n in (1, 2):
        dset = ("Accept", "Reject", "Hold", "Supplement") if n == 1 else ("Accept", "Hold")
        for ex in itertools.product(USERS[:2] if n == 2 else USERS, repeat=n):
            for ad in itertools.product(USERS, repeat=n):
                for ds in itertools.product(dset, repeat=n):
                    for gv in ("assigned", "other"):
                        g = sorted((ad[k], k, ds[k] if gv == "assigned" else other[ds[k]]) for k in range(n))
                        for rv in [()] + [(u,) for u in USERS]:
                            yield {"n": n, "exec": list(ex), "adj": list(ad), "disp": list(ds),
                                   "grants": g, "exec_perm_revoked": list(rv)}


def mc_t3():
    for d in USERS:
        for ex in itertools.product(USERS, repeat=2):
            for ac in itertools.product(USERS, repeat=2):
                yield {"scope": d, "exec": list(ex), "acc": list(ac)}


def mc_de():
    for d in ("a", "b"):
        for x in ("a", "b"):
            for g in ("a", "b", "nu"):
                yield {"scope": d, "ext": x, "gate": g}


# Ctrl: windows theta_E = [0,1], theta_J = [2,3]; 7 interval options (RP-1.0 D6)
IV = {"none": (), "E": (0, 1), "J": (2, 3), "EJ": (0, 1, 2, 3), "J_early": (2,), "J_late": (3,), "E_early": (0,)}
EDGE_SLOTS = [("p", "o"), ("p", "a"), ("p", "j"), ("o", "a"), ("o", "j")]


def mc_ctrl():
    for combo in itertools.product(IV, repeat=len(EDGE_SLOTS)):
        yield {"edges": {f"{s}->{t}": iv for (s, t), iv in zip(EDGE_SLOTS, combo) if iv != "none"}}


EV = ([("cont", w, c, b) for w in ("W1", "W2") for c in ("X", "Y") for b in ("beta", "gamma")] +
      [("term", w, "X", "beta") for w in ("W1", "W2")] +
      [("reopen", w, "X", "beta", ind) for w in ("W1", "W2") for ind in (True, False)])


def mc_led():
    for n in (1, 2, 3):
        for seq in itertools.product(EV, repeat=n):
            yield {"B": 1, "events": [list(e) for e in seq]}


FLAGS = list(itertools.product((False, True), repeat=3))


def mc_nap():
    """Exhaustive family of dea-nap-finite-model.py: 26,262 models."""
    for n in (1, 2):
        states = [str(i) for i in range(n)]
        pairs = list(itertools.product(states, repeat=2))
        for assign in itertools.product([None] + FLAGS, repeat=len(pairs)):
            edges = [(f"e{i}", s, t, all(fl)) for i, ((s, t), fl) in enumerate(zip(pairs, assign)) if fl is not None]
            for gm in range(1 << n):
                yield {"states": states, "start": "0", "goals": [states[i] for i in range(n) if gm >> i & 1],
                       "edges": edges}


# ------------------------------------------------------------------ regression scenarios
# G2 (v0.3.4.2 closure script, dea-v0342-countermodels.py l.174-200), re-encoded as direct-control edges
# under v0.3.4.3 p.8-9 (shared credential = mutual edges; excluded clauses produce no edge; TCB not exempt).
G2 = {
    "S1_compliant": [],
    "S2_one_operator_shared_credential": [(x, y) for x in "dej" for y in "dej" if x != y],
    "S3_same_model_separate_control": [],
    "S4_shared_readable_state": [],
    "S5_controller_behind_E_and_J": [("P", "e"), ("P", "j")],
    "S6_E_writes_J_decision_record": [("e", "j")],
    "S7_D_alters_E_caps_mid_stage": [("d", "e")],
    "S8_TCB_admin_not_role_holder": [("adm", "d"), ("adm", "e"), ("adm", "j")],
    "S9_TCB_admin_also_acts_as_D": [("adm", "d"), ("adm", "e"), ("adm", "j")],
    "S10_orchestrator_spawns_subagents_with_own_token": [("orc", "e"), ("orc", "j")],
    "S11_E_supplies_verifier_run_by_J0": [("e", "j")],
    "S12_D_rubric_fixed_in_prestage_manifest": [],
}
G2_V0342_INTENT = {  # (T3, H_EJ, D~E) as recorded in the v0.3.4.2 script
    "S1_compliant": (False, False, False), "S2_one_operator_shared_credential": (True, True, True),
    "S3_same_model_separate_control": (False, False, False), "S4_shared_readable_state": (False, False, False),
    "S5_controller_behind_E_and_J": (False, True, False), "S6_E_writes_J_decision_record": (False, True, False),
    "S7_D_alters_E_caps_mid_stage": (False, False, True), "S8_TCB_admin_not_role_holder": (False, False, False),
    "S9_TCB_admin_also_acts_as_D": (True, True, True),
    "S10_orchestrator_spawns_subagents_with_own_token": (False, True, False),
    "S11_E_supplies_verifier_run_by_J0": (False, True, False),
    "S12_D_rubric_fixed_in_prestage_manifest": (False, False, False)}
G2_NEW = {"S13_transitive_P_orc_e (new)": [("P", "orc"), ("orc", "e"), ("P", "j")]}

# G3: M1, M3, M5-M9 from dea-v0342-countermodels.py l.288-316; M2, M4 from dea-v0341-countermodels.py l.232-234.
# Encoded as a single output x produced by 'E'; ctrl maps identities to controlling principals.
G3 = {
    "M1_independent": dict(prod="E", ctrl={}, grants=[("J", "Accept")], assign=("J", "Accept")),
    "M2_self_unauthorized (v0.3.4.1)": dict(prod="E", ctrl={}, grants=[("J", "Accept")], assign=("E", "Accept")),
    "M3_self_granted": dict(prod="E", ctrl={}, grants=[("E", "Accept")], assign=("E", "Accept")),
    "M4_self_granted_unused (v0.3.4.1)": dict(prod="E", ctrl={}, grants=[("E", "Accept")], assign=None),
    "M5_proxy_judge_same_controller": dict(prod="E", ctrl={"E": {"E", "P"}, "J2": {"J2", "P"}},
                                           grants=[("J2", "Accept")], assign=("J2", "Accept")),
    "M6_J_verifies_then_accepts_E_output": dict(prod="E", ctrl={}, grants=[("J", "Accept")], assign=("J", "Accept")),
    "M7_J_accepts_own_repair": dict(prod="J", ctrl={}, grants=[("J", "Accept")], assign=("J", "Accept")),
    "M8_self_hold": dict(prod="E", ctrl={}, grants=[("E", "Hold")], assign=("E", "Hold")),
    "M9_timing_grant_before_output": dict(prod="E", ctrl={}, grants=[("E", "Accept")], assign=("E", "Accept")),
}
G3_V0342_INTENT = {"M1_independent": 1, "M2_self_unauthorized (v0.3.4.1)": 0, "M3_self_granted": 0,
                   "M4_self_granted_unused (v0.3.4.1)": 0, "M5_proxy_judge_same_controller": 0,
                   "M6_J_verifies_then_accepts_E_output": 1, "M7_J_accepts_own_repair": 0, "M8_self_hold": 1,
                   "M9_timing_grant_before_output": 0}


def g4_scenarios():
    """G4 (dea-v0342-countermodels.py l.426-532). Objects carry content/locator/lineage so that
    Case(x) is computed by the DEA reference evaluator, not given."""
    x = {"oid": "x", "content": "h(x)", "locator": "src#L10-20"}
    sc = {}
    sc["A1_renamed_workflows_x5"] = [("cont", f"W{i}", x, "beta") for i in range(5)]
    sc["A2_renamed_manifest_same_workflow"] = [("cont", "W1", x, "beta"), ("cont", "W1", x, "beta")]
    sc["A3_restaging_same_workflow"] = [("cont", "W1", x, "beta")] * 6
    sc["A4_relabelled_object_same_content"] = [("cont", f"W{i}", {"oid": f"x_v{i}", "content": "h(x)",
                                                                  "locator": f"other#{i}"}, "beta") for i in range(4)]
    prev, a5 = "x", [("cont", "W0", x, "beta")]
    for i in range(1, 4):
        o = {"oid": f"x_e{i}", "content": f"h(x+{i})", "locator": f"edit#{i}", "derived_from": prev}
        prev = o["oid"]
        a5.append(("cont", f"W{i}", o, "beta"))
    sc["A5_edited_object_with_lineage"] = a5
    sc["A6_reextraction_same_locator"] = [("cont", "W0", x, "beta")] + [
        ("cont", f"W{i}", {"oid": f"x_r{i}", "content": f"h(reextract{i})", "locator": "src#L10-20"}, "beta")
        for i in range(1, 4)]
    sc["A7_near_duplicate_shifted_locator"] = [("cont", "W0", x, "beta")] + [
        ("cont", f"W{i}", {"oid": f"x_s{i}", "content": f"h(shift{i})", "locator": f"src#L{10+i}-{20+i}"}, "beta")
        for i in range(1, 4)]
    sc["A8_self_reopen_after_terminal"] = [("cont", "W1", x, "beta"), ("term", "W1", x, "beta"),
                                           ("reopen", "W2", x, "beta", False), ("cont", "W2", x, "beta")]
    y = {"oid": "y", "content": "h(y)", "locator": "src#L40-50"}
    sc["L1_new_object_same_blocker_type"] = [("cont", "W1", x, "beta"), ("cont", "W2", y, "beta")]
    sc["L2_same_object_new_blocker"] = [("cont", "W1", x, "beta"), ("cont", "W2", x, "gamma")]
    sc["L3_independent_logged_reopen"] = [("cont", "W1", x, "beta"), ("term", "W1", x, "beta"),
                                          ("reopen", "W2", x, "beta", True), ("cont", "W2", x, "beta")]
    sc["L4_multistage_after_accept_no_blocker"] = [("cont", "W1", x, "beta")] + [("cont", "W1", x, None)] * 3
    # newly constructed boundary cases (length 4, outside MC-LED)
    sc["N1_term_reopen_cont_cont (new)"] = [("term", "W1", x, "beta"), ("reopen", "W2", x, "beta", True),
                                            ("cont", "W2", x, "beta"), ("cont", "W2", x, "beta")]
    sc["N2_double_term_single_reopen (new)"] = [("term", "W1", x, "beta"), ("term", "W1", x, "beta"),
                                                ("reopen", "W2", x, "beta", True), ("cont", "W2", x, "beta")]
    return sc


G4_V0342_INTENT = {"A1_renamed_workflows_x5": 1, "A2_renamed_manifest_same_workflow": 1,
                   "A3_restaging_same_workflow": 1, "A4_relabelled_object_same_content": 1,
                   "A5_edited_object_with_lineage": 1, "A6_reextraction_same_locator": 1,
                   "A7_near_duplicate_shifted_locator": 4, "A8_self_reopen_after_terminal": 1,
                   "L1_new_object_same_blocker_type": 2, "L2_same_object_new_blocker": 2,
                   "L3_independent_logged_reopen": 2, "L4_multistage_after_accept_no_blocker": 4}

# NAP named cases (dea-nap-finite-model.py l.203-240) and the DEA p.19 diagnosis-only pair
NAP_NAMED = {
    "A_no_actions_goal_unsatisfied": {"states": ["0"], "start": "0", "goals": [], "edges": []},
    "B_authorized_irrelevant_action": {"states": ["0", "1"], "start": "0", "goals": [],
                                       "edges": [("irrelevant", "0", "1", True)]},
    "C_blocked_direct_authorized_alternative": {"states": ["0", "1"], "start": "0", "goals": ["1"],
                                                "edges": [("blocked", "0", "1", False), ("alternative", "0", "1", True)]},
    "D_goal_already_satisfied": {"states": ["0"], "start": "0", "goals": ["0"], "edges": []},
    "minimal_self_loop_no_goal": {"states": ["0"], "start": "0", "goals": [], "edges": [("a", "0", "0", True)]},
    "diag_only_p19": {"states": ["0", "1"], "start": "0", "goals": ["1"], "edges": [("diag", "0", "0", True)]},
    "diag_goal_twin": {"states": ["0", "1"], "start": "0", "goals": ["1"], "edges": [("diag", "0", "1", True)]},
}
NAP_NAMED_EXPECTED = {"A_no_actions_goal_unsatisfied": True, "B_authorized_irrelevant_action": True,
                      "C_blocked_direct_authorized_alternative": False, "D_goal_already_satisfied": False,
                      "minimal_self_loop_no_goal": True, "diag_only_p19": True, "diag_goal_twin": False}
