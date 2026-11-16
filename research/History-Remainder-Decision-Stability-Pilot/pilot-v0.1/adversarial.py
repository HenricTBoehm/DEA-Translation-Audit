"""Targeted attacks on admitted premises, separate from the scored sample."""

import argparse
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import fixtures
import governance
import oracle
from pilot import arm_d, encoded, trial


def old_module(file):
    spec = importlib.util.spec_from_file_location("archived_hr1", file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def independent_legacy_snapshots(module):
    """Map the seven admissible traces to a backward query model."""
    agreement = {}
    for name, scenario in module.CASES.items():
        if name.startswith("CM-R6"):
            continue  # State-dependent deletion belongs to the failed P2 domain.
        trace = scenario["ev"]
        artifacts = {"x", *(e["r"] for e in trace if e["k"] == "bind")}
        channels = {"art": "artifact", "cap": "capability", "cred": "credential", "crit": "criteria"}
        events = []
        for i, e in enumerate(trace):
            fields = {}
            kind = e["k"]
            if kind == "bind":
                continue
            if kind == "edge":
                kind = "control"
                fields = dict(src=e["u"], dst=e["v"], dst_artifact=e["v"] in artifacts,
                              channel=channels[e["ch"]])
            elif kind == "produce":
                fields = dict(actor=e["a"], artifact=e["x"], inputs=[])
            elif kind == "seal":
                fields = dict(artifact=e["x"])
            elif kind == "reset":
                fields = dict(target=e["z"], target_artifact=e["z"] in artifacts,
                              channels=sorted(channels[k] for k in e["K"]), independent=True,
                              scope_proved=True, neutralized=True)
            elif kind == "commit":
                kind = "adjudicate"
                fields = dict(actor=e["j"], roots={ref: ref for ref in sorted(artifacts - {"x"})})
            events.append(fixtures.row(f"e{i}", kind, e["t"], e["l"], **fields))
        states = {"concrete": scenario["true"], "witnessed": scenario["w"],
                  "bound": scenario.get("b_hr1", scenario["b"])}
        result = {}
        for label, state in states.items():
            seeds = [fixtures.token(target, artifact=target in artifacts, source=origin, channel=channels[ch])
                     for origin, target, ch in sorted(state)]
            px, js = oracle.concrete({"artifact": "x", "events": events}, seeds)
            if (px, js) != module.sets(state, trace):
                raise AssertionError((name, label, px, js, module.sets(state, trace)))
            result[label] = {"P_x": sorted(px), "J_star": sorted(js)}
        agreement[name] = result
    return agreement


def original(mod, expected):
    archived = mod.run_cases()
    assert archived == expected["cases"]
    cases = {name.split("_")[0]: result for name, result in archived.items()}
    assert [cases[f"CM-R{i}"]["HR1_verdict"] for i in range(1, 9)] == [
        "UNDETERMINED", "CLEAR", "UNDETERMINED", "UNDETERMINED", "UNDETERMINED", "CLEAR",
        "UNDETERMINED", "CONFLICT"]
    assert cases["CM-R6"]["unsound"] and [case for case in cases if cases[case]["unsound"]] == ["CM-R6"]
    relay = mod.CASES["CM-R3_bootstrap_leak_via_uncovered_relay"]
    assert "q" in mod.cone(relay["ev"], {"a2", "x", "j2", "r"})
    assert "q" not in mod.cone([e for e in relay["ev"] if e.get("u") != "q"], {"a2", "x", "j2", "r"})
    r8 = mod.CASES["CM-R8_certified_actual_pre_state_witness"]
    assert mod.verdict(set(), r8["b"], r8["ev"])[0] == "UNDETERMINED"
    assert mod.verdict(r8["w"], r8["b"], r8["ev"])[0] == "CONFLICT"
    no_seal = [e for e in r8["ev"] if e["k"] != "seal"]
    assert mod.verdict(r8["w"], r8["b"], no_seal)[0] == "CLEAR"  # P1 deliberately violated.
    r5 = mod.CASES["CM-R5_loose_bound_blocks_without_conflict_claim"]
    assert mod.verdict({("p", "r", "crit")}, r5["b"], r5["ev"])[0] == "CONFLICT"
    assert not mod.truth(r5["true"], r5["ev"])  # P5 deliberately violated.
    return {"CM_R1_R8": archived, "independent_snapshots": independent_legacy_snapshots(mod), "legacy_missing_seal_P1": {"events": no_seal, "actual": "CLEAR"},
            "forged_actual_P5": {"token": ["p", "r", "crit"], "actual": "CONFLICT", "true_conflict": False}}


def pilot_cases():
    names = fixtures.named()
    probes = []

    def check(name, case, expected_g, expected_t, truth_only_false_clear=False):
        arms = governance.evaluate(case)
        result = arm_d(case)
        assert encoded(arms["C"]) == encoded(result["governance"])
        actual = (arms["C"]["status"], result["diagnostic"]["status"])
        assert actual == (expected_g, expected_t), (name, actual)
        if truth_only_false_clear:
            p, j = oracle.concrete(case["model"], case["oracle"]["prestate"])
            assert p & j and result["governance"]["passes_gate_with_authority"]
        probes.append({"id": name, "input": case, "expected": [expected_g, expected_t], "actual": result})

    stable, unstable, unknown = "CERTIFIED_STABLE", "UNSTABLE", "STABILITY_UNDETERMINED"
    clear, hold, invalid, conflict = "NO_CONFLICT_ESTABLISHED", "UNDETERMINED", "MODEL_INVALID", "CONFLICT"
    case = deepcopy(names["S01"])
    case["scientific"].update(offset=0, weights={"calibration": 1})
    assert not trial(case)["truth"]["conflict"]
    check("formally_independent_but_substantively_sensitive", case, clear, unstable)

    case = deepcopy(names["S05"])
    case["scientific"]["scope"]["rubric"] = "rubric@2"
    check("both_substantive_scopes_relabelled_but_seal_pins_original", case, invalid, unknown)
    counterfactual = deepcopy(case)
    counterfactual["model"]["events"][1]["pins"]["rubric"] = "rubric@2"
    counterfactual["model"]["attempt"] = "alternate-attempt@2"
    for key in ("scope", "world_scope"):
        counterfactual["scientific"][key]["attempt"] = "alternate-attempt@2"
    check("separate_counterfactual_scope_not_scored", counterfactual, clear, stable)

    case = deepcopy(names["S01"])
    del case["model"]["events"][1]
    check("missing_seal", case, hold, unknown)
    case = deepcopy(names["S01"])
    case["model"]["events"][1]["time"] = 6
    # Contradictory order prevents governance. Its independently fixed score remains constant.
    check("contradictory_seal_order", case, invalid, stable)

    case = deepcopy(names["S02"])
    case["remainder"].update(kind="U", attested=False)
    check("supported_positive_despite_missing_history", case, conflict, stable)

    case = deepcopy(names["S08"])
    case["remainder"].update(issuer="p", upper=[])
    check("self_issued_bound_P4", case, hold, stable)

    case = deepcopy(names["S09"])
    case["remainder"].update(kind="B", attested=True)
    case["model"]["binding"] = {"relay": "q"}
    case["oracle"]["prestate"][0]["target"] = "q"
    case["remainder"]["uncovered"] = [["q", "credential"]]
    check("alias_on_bootstrap_relay", case, hold, unstable)
    case["remainder"]["uncovered"] = []
    # A false coverage claim is outside the certified domain. No oracle truth is fed to C.
    check("false_complete_bound_P3", case, clear, unstable, truth_only_false_clear=True)

    case = deepcopy(names["S12"])
    case["scientific"]["policy_defined"] = True
    check("uncertified_dynamic_dependency_blocks_census", case, hold, unknown)
    case = deepcopy(names["S01"])
    case["scientific"]["weights"] = {"omitted_dynamic_variable": 1}
    check("unspecified_scientific_input_blocks_census", case, clear, unknown)
    case = deepcopy(names["S01"])
    case["model"]["dependencies"] = [{"from": "rubric@1", "to": "resolver@1",
                                     "role": "resolver", "authenticated": False}]
    assert governance.evaluate(case)["B"]["status"] == hold
    check("unverified_dependency_blocks_B_and_D_despite_outer_flags", case, hold, unknown)

    case = deepcopy(names["S08"])
    control = next(e for e in case["model"]["events"] if e["kind"] == "control")
    rank = control.pop("order")
    case["model"]["events"].append(fixtures.row(control["id"], "control", control["time"], rank))
    case["remainder"]["uncovered"] = [["essentials_outside_cone", "criteria"]]
    check("compatible_partial_assertions_are_joined_before_cone", case, hold, stable)
    return probes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    legacy = original(old_module(args.source / "hr1_remainder.py"),
                      json.loads((args.source / "results/hr1-results.json").read_bytes()))
    result = {"original_adversarial": legacy, "pilot_probes": pilot_cases()}
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("PASS: 8 archived countermodels, P1/P5 attacks and", len(result["pilot_probes"]), "pilot probes")


if __name__ == "__main__":
    main()
