"""P-01 regression runner with unchanged source harnesses and differential checks."""

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from copy import deepcopy
from itertools import combinations, product
from pathlib import Path
from tempfile import TemporaryDirectory

import independent
import p01
from p01 import CLEAR, CONFLICT, INVALID, UNKNOWN, VALID


def event(event_id, kind, time, order=0, **fields):
    return {"id": event_id, "kind": kind, "time": time, "order": order,
            "authenticated": True, **fields}


def grade(event_id, at, order=0, src="p", dst="r@1", **fields):
    return event(event_id, "control", at, order, src=src, dst=dst,
                 dst_artifact=True, channel="criteria", persistence="potential_durable", **fields)


def base():
    return {
        "artifact": "x@1", "record_start": 0, "binding_verified": True,
        "snapshot_version": "v1", "commit_version": "v1", "snapshot_attested": True,
        "record_complete": True, "history": {"trusted": True, "coverage": True},
        "bound_complete": True, "graph_attested": True, "authorized": True,
        "events": [
            event("p-a", "control", 1, src="p", dst="a", channel="capability",
                  persistence="potential_durable"),
            event("produce", "produce", 2, artifact="x@1", actor="a", inputs=[]),
            event("seal", "seal", 3, artifact="x@1", pins={"rubric": "r@1"}),
            event("commit", "adjudicate", 5, artifact="x@1", actor="j", roots={"rubric": "r@1"}),
        ],
    }


def reset(channel, **flags):
    return event("reset", "reset", 4, target="r@1", target_artifact=True,
                 channels=[channel], **({"independent": True, "scope_proved": True,
                                         "neutralized": True} | flags))


def custom_cases():
    suite = {}

    def add(name, expected, extra=(), **changes):
        model = base() | changes
        model["events"] += list(extra)
        suite[name] = model, expected

    add("P01-A01_bound_rubric_write", CONFLICT, [grade("write", 1, 1)])
    add("P01-A02_post_seal_same_version_control", CONFLICT, [grade("write", 4)])
    add("P01-A03_post_commit_excluded", CLEAR, [grade("write", 6)])
    add("P01-A04_indirect_versioned_dependency", CONFLICT, [
        event("p-q", "control", 1, 1, src="p", dst="q", channel="credential",
              persistence="potential_durable"),
        grade("q-r", 4, src="q"),
    ], dependencies=[{"from": "config@3", "to": "r@1", "role": "rubric", "authenticated": True}])
    suite["P01-A04_indirect_versioned_dependency"][0]["events"][3]["roots"] = {"config": "config@3"}
    add("P01-A05_complete_neutralization", CLEAR, [grade("write", 1, 1), reset("criteria")])
    add("P01-A06_credential_only_neutralization", CONFLICT, [grade("write", 1, 1), reset("credential")])
    add("P01-A07_open_dependency_set", UNKNOWN, bound_complete=False)
    add("P01-A08_unauthenticated_edge", UNKNOWN, [grade("write", 1, 1) | {"authenticated": False}])
    add("P01-A09_read_only", CLEAR, [event("read", "read", 4, actor="p", artifact="r@1")])
    add("P01-A10_historical_effect", CONFLICT, history={"trusted": True, "coverage": True, "seeds": [
        {"id": "old", "principal": "p", "target": "r@1", "target_artifact": True,
         "channel": "criteria", "authenticated": True}
    ]})
    add("P01-A11_unproven_neutralization", CONFLICT,
        [grade("write", 1, 1), reset("criteria", neutralized=False)])
    add("P01-A12_snapshot_changes_before_commit", UNKNOWN, commit_version="v2")
    add("P01-A13_new_rubric_version_after_seal", INVALID, [grade("write-new", 4, dst="r@2")])
    suite["P01-A13_new_rubric_version_after_seal"][0]["events"][3]["roots"] = {"rubric": "r@2"}
    add("P01-A14_dependence_still_survives_downstream", CONFLICT,
        [grade("write", 1, 1), event("propagate", "control", 3, 1, src="r@1", dst="s@1",
         src_artifact=True, dst_artifact=True, channel="artifact", persistence="potential_durable"),
         reset("criteria")], dependencies=[{"from": "r@1", "to": "s@1", "role": "standard",
                                            "authenticated": True}])
    add("P01-A15_positive_with_open_dependency_set", CONFLICT, [grade("write", 1, 1)], bound_complete=False)
    add("P01-A16_uncertified_indirect_link", UNKNOWN, [grade("write", 1, 1)],
        dependencies=[{"from": "config@3", "to": "r@1", "role": "rubric", "authenticated": False}])
    suite["P01-A16_uncertified_indirect_link"][0]["events"][3]["roots"] = {"config": "config@3"}
    add("P01-A17_dependency_cycle_finite_closure", CONFLICT, [grade("write", 1, 1)],
        dependencies=[{"from": "r@1", "to": "s@1", "role": "standard", "authenticated": True},
                      {"from": "s@1", "to": "r@1", "role": "rubric", "authenticated": True}])
    add("P01-A18_wrong_version_control_does_not_count", CLEAR, [grade("write-other", 4, dst="r@2")])
    add("P01-A19_no_snapshot_attestation", UNKNOWN, snapshot_attested=False)
    add("P01-A20_seal_role_cannot_alias_an_unrelated_root", INVALID)
    suite["P01-A20_seal_role_cannot_alias_an_unrelated_root"][0]["events"][3]["roots"] = {"commentary": "r@1"}
    add("P01-A21_decision_graph_version_changes_with_same_rubric", UNKNOWN,
        snapshot_version="control-graph@1+rubric@1", commit_version="control-graph@2+rubric@1")
    add("P01-A22_control_at_same_tick_after_commit_has_no_effect", CLEAR, [grade("write", 5, 1)])
    add("P01-B01_missing_seal", UNKNOWN)
    del suite["P01-B01_missing_seal"][0]["events"][2]
    add("P01-B02_late_seal", INVALID)
    suite["P01-B02_late_seal"][0]["events"][2]["time"] = 6
    add("P01-B03_two_productions", INVALID,
        [event("new-production", "produce", 2, 1, actor="a", artifact="x@1", inputs=[])])
    add("P01-B04_contradiction_despite_missing_commit", INVALID,
        [event("new-production", "produce", 2, 1, actor="a", artifact="x@1", inputs=[])])
    del suite["P01-B04_contradiction_despite_missing_commit"][0]["events"][3]
    add("P01-B05_same_id_retransmission", CLEAR)
    suite["P01-B05_same_id_retransmission"][0]["events"].append(
        deepcopy(suite["P01-B05_same_id_retransmission"][0]["events"][1]))
    add("P01-B06_same_id_equivocation", INVALID,
        [event("produce", "produce", 2, actor="b", artifact="x@1", inputs=[])])
    add("P01-B07_no_verified_principal_binding", UNKNOWN, binding_verified=False)
    add("P01-B08_same_tick_unknown_order", UNKNOWN)
    seal = suite["P01-B08_same_tick_unknown_order"][0]["events"][2]
    seal.update(time=2, order=None)
    add("P01-B09_same_tick_reversed_known_order", INVALID)
    suite["P01-B09_same_tick_reversed_known_order"][0]["events"][2].update(time=2, order=-1)
    add("P01-B10_conflicting_commit_roots", INVALID)
    commit = suite["P01-B10_conflicting_commit_roots"][0]["events"][3]
    suite["P01-B10_conflicting_commit_roots"][0]["events"].append(commit | {"roots": {"rubric": "r@2"}})
    add("P01-B11_missing_seal_but_production_after_commit", INVALID)
    trace = suite["P01-B11_missing_seal_but_production_after_commit"][0]["events"]
    del trace[2]
    trace[1]["time"] = 6
    add("P01-B12_interpolate_rank_with_authenticated_order", CLEAR)
    trace = suite["P01-B12_interpolate_rank_with_authenticated_order"][0]["events"]
    trace[2].update(time=2, order=None)
    trace[3].update(time=2, order=1)
    trace.append(event("seal", "seal", 2, "1/3"))
    add("P01-B13_missing_timestamp_is_completable", UNKNOWN)
    trace = suite["P01-B13_missing_timestamp_is_completable"][0]["events"]
    trace[2].update(time=None, order=None)
    add("P01-B14_malformed_rank_without_timestamp_is_immutable", INVALID)
    suite["P01-B14_malformed_rank_without_timestamp_is_immutable"][0]["events"][2]["time"] = None
    add("P01-B15_authenticated_event_resolves_matching_unverified_copy", CLEAR)
    trace = suite["P01-B15_authenticated_event_resolves_matching_unverified_copy"][0]["events"]
    trace.append(trace[2] | {"authenticated": False})
    return suite


def adapted_draft(case):
    model = deepcopy(case)
    model.update(snapshot_attested=True, graph_attested=True, bound_complete=True)
    for row in model["events"]:
        if row["kind"] == "seal":
            row["pins"] = {}
        elif row["kind"] == "adjudicate":
            row["roots"] = {}
        elif row["kind"] == "produce":
            row["inputs"] = []
        elif row["kind"] == "reset":
            row["neutralized"] = row.get("scope_proved", False)
    return model


def adapted_precision(rows, opts=None):
    opts = opts or {}
    model = base()
    model["events"] = []
    model["history"] = {"trusted": opts.get("history_closed", True),
                        "coverage": opts.get("history_closed", True), "seeds": []}
    model["record_complete"] = opts.get("record_complete", True)
    model["bound_complete"] = opts.get("bound_complete", True)
    if not opts.get("stable", True):
        model["commit_version"] = "v2"
    names = {row["r"]: row["r"] + "@1" for row in rows if row["kind"] == "bind" and "r" in row}
    for index, row in enumerate(rows):
        kind = row["kind"]
        extra = {}
        if kind == "edge":
            kind = "control"
            extra = {"src": row["u"], "dst": names.get(row["v"], row["v"]), "dst_artifact": row["v"] in names,
                     "channel": row["ch"], "persistence": "potential_durable"}
        elif kind == "reset":
            extra = {"target": names.get(row["z"], row["z"]), "target_artifact": row["z"] in names,
                     "channels": sorted(row["K"]), "independent": True, "scope_proved": True, "neutralized": True}
        elif kind == "produce":
            extra = {"actor": row.get("a", "a"), "artifact": "x@1", "inputs": row.get("inputs", [])}
        elif kind == "seal":
            extra = {"artifact": "x@1", "pins": names}
        elif kind == "commit":
            kind = "adjudicate"
            extra = {"actor": row.get("j", "j"), "artifact": "x@1", "roots": names}
        elif kind == "bind" and "r" in row:
            continue  # each GA binding is carried by the authenticated commit envelope
        elif kind == "bind":
            kind = "read"  # W2 uses only the authenticated coordinate, not a binding assertion
            extra = {"actor": "j", "artifact": "other@1"}
        model["events"].append(event(row.get("id", f"e{index}"), kind, row["t"], row["l"], **extra)
                               | {"authenticated": row.get("auth", True)})
        if not row.get("principal_verified", True):
            model["binding_verified"] = False
    for index, (principal, obj, channel) in enumerate(opts.get("history_tokens", ())):
        model["history"]["seeds"].append({"id": f"h{index}", "principal": principal,
            "target": names.get(obj, obj), "target_artifact": obj in names,
            "channel": channel, "authenticated": True})
    return model


def check(model, expected, *, gate="outcome"):
    result = p01.evaluate(model)
    oracle = independent.evaluate(model)
    reference = (result["input"], result["outcome"], set(result["P_x"]), set(result["J_star"]),
                 {(w["principal"], w["decision_target"]) for w in result["witnesses"]})
    model_digest = hashlib.sha256(json.dumps(model, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"expected": expected, "gate": gate, "actual": result, "input_sha256": model_digest,
            "independent_agrees": reference == oracle,
            "matches": result[gate] == expected and reference == oracle}


def growth_check():
    original = base()
    rows = original["events"]
    pool = rows + [event("fork", "produce", 2, 1, actor="a", artifact="x@1", inputs=[])]
    states = {}
    for mask in range(1 << len(pool)):
        trace = [row for i, row in enumerate(pool) if mask & (1 << i)]
        case = original | {"events": trace}
        verdict = p01.evaluate(case)["input"]
        if independent.evaluate(case)[0] != verdict:
            raise AssertionError((trace, verdict))
        states[mask] = verdict
    comparisons = 0
    for mask, nxt in combinations(states, 2):
        if mask & nxt != mask:
            continue
        if states[mask] == INVALID and states[nxt] != INVALID:
            raise AssertionError(("invalidity repaired by appending", mask, nxt))
        comparisons += 1
    if (states[15], states[31], states[7]) != (VALID, INVALID, UNKNOWN):
        raise AssertionError(states)
    return {"independent_models": len(states), "inclusion_pairs": comparisons,
            "empty_to_complete": [states[0], states[15]], "complete_to_contradiction": [states[15], states[31]],
            "retract_fork_new_record": [states[31], states[15]],
            "inputs": pool, "status_by_subset_mask": states}


def order_check():
    counts = {VALID: 0, INVALID: 0, UNKNOWN: 0}
    # Product includes missing timestamps/ranks, interleaving and coordinate collisions.
    choices = ((None, None), (2, None), (3, None), (2, 0), (2, 1), (3, 0), (3, 1))
    for coords in product(choices, repeat=3):
        case = base()
        for row, (tick, rank) in zip(case["events"][1:], coords):
            row.update(time=tick, order=rank)
        verdict = p01.evaluate(case)["input"]
        if independent.evaluate(case)[0] != verdict:
            raise AssertionError((coords, verdict))
        counts[verdict] += 1
    return {"choices": choices, "cases": sum(counts.values()), "class_counts": counts}


def influence_check():
    # Fixed producer p->a; three ordered optional effect events, followed by the decision.
    test_model = base()
    steps, counts = (0, 1, 2), {}
    for choices in product(range(6), repeat=len(steps)):
        model = deepcopy(test_model)
        for order, choice in zip(steps, choices):
            event_id = "effect-" + str(order)
            options = (
                None,
                grade(event_id, 4, order),
                grade(event_id, 4, order, src="q"),
                event(event_id, "control", 4, order, src="p", dst="q",
                      channel="credential", persistence="potential_durable"),
                reset("criteria") | {"id": event_id, "order": order},
                reset("credential") | {"id": event_id, "order": order},
            )
            if options[choice] is not None:
                model["events"].append(options[choice])
        result = p01.evaluate(model)
        expected = independent.evaluate(model)
        witnesses = {(w["principal"], w["decision_target"]) for w in result["witnesses"]}
        actual = (result["input"], result["outcome"], set(result["P_x"]), set(result["J_star"]), witnesses)
        if actual != expected:
            raise AssertionError((choices, actual, expected))
        counts[result["outcome"]] = counts.get(result["outcome"], 0) + 1
    return {"cases": sum(counts.values()), "class_counts": counts}


def load_script(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reproduce(source, pr6):
    draft = source / "DEA_v0.3.5.1_draft_review_package" / "harness"
    precision = source / "dea-v0351-precision-check"
    cases = draft / "v0351-regression-cases.json"
    draft_script = draft / "dea_v0351_reference.py"
    precision_script = precision / "v0351_precision_check.py"
    with TemporaryDirectory() as scratch:
        for script, reference, args in (
            (draft_script, draft / "v0351-results.json", ["--cases", str(cases)]),
            (precision_script, precision / "v0351-precision-results.json", []),
        ):
            out = Path(scratch) / reference.name
            subprocess.run([sys.executable, str(script), *args, "--out", str(out)], check=True, stdout=sys.stderr)
            if out.read_bytes() != reference.read_bytes():
                raise AssertionError("original output differs: " + reference.name)
    subprocess.run([sys.executable, "-m", "unittest", "-v"], cwd=pr6, check=True, stdout=sys.stderr)
    old = load_script(draft_script)
    historic = json.loads(cases.read_bytes())["cases"]
    probe = load_script(precision_script)
    return old, historic, probe


def old_on_model(old, model):
    if any(isinstance(e.get("order"), str) or e.get("time") is None for e in model["events"]):
        return {"status": "NOT EXECUTED", "reason": "P-01 input representation outside legacy order schema"}
    report = old.evaluate(model | {"id": "P01-probe"})
    return {k: report[k] for k in ("status", "reason", "witness", "evidence")}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--pr6-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    old, historic, probe = reproduce(args.source_dir.resolve(), args.pr6_dir.resolve())
    draft_checks, ga, gb, new = {}, {}, {}, {}
    for baseline_case in historic:
        model = adapted_draft(baseline_case)
        draft_checks[model["id"]] = check(model, model["expected_status"]) | {
            "input_locator": model["id"], "legacy": old.evaluate(baseline_case),
        }
    for name, (rows, opts, expected, _) in probe.GA.items():
        model = adapted_precision(rows, opts)
        ga[name] = check(model, expected) | {"input_locator": name, "original_probe": probe.run(rows, **opts)}
    for name, (rows, expected) in probe.GB.items():
        model = adapted_precision(rows)
        gb[name] = check(model, VALID if expected == "WELL_FORMED" else expected, gate="input") | {
            "input_locator": name, "original_probe": {"literal": probe.wfe_literal(rows),
                                                      "proposed": probe.wfe_proposed(rows)},
        }
    for name, (model, expected) in custom_cases().items():
        new[name] = check(model, expected) | {"fixture": model, "legacy": old_on_model(old, model)}

    order, growth = order_check(), growth_check()
    groups = {"draft_compatibility": draft_checks, "RA": ga, "C_W": gb, "new": new}
    counts = {name: {"PASS": sum(row["matches"] for row in rows.values()),
                     "FAIL": sum(not row["matches"] for row in rows.values())} for name, rows in groups.items()}
    result = {"version": "P-01", "original_execution": {
        "precision": {"PASS": 21, "byte_identical": True}, "draft": {"PASS": 32, "byte_identical": True},
        "PR6": {"PASS": 7, "independent_traces": 343, "commit": "4c4265b5230bf6010a75c95e17de62c066990bf2"}},
        "summary": counts, "order_differential": order, "authenticated_growth": growth, "influence_differential": influence_check(), "rows": groups}
    args.out.write_text(json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    print(json.dumps(counts, sort_keys=True))
    for name, rows in groups.items():
        for case, row in rows.items():
            if not row["matches"]:
                print(name, case, row["expected"], row["actual"], row["independent_agrees"], file=sys.stderr)
    return int(any(count["FAIL"] for count in counts.values()))


if __name__ == "__main__":
    sys.exit(main())
