"""Finite comparison against examiner-owned references and scoped documentation review."""

import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
from statistics import median
from time import perf_counter_ns
from timeit import repeat

import benchmarks
import cases
import governance
import pilot
import sensitivity
import stability


def serialize(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def scope_review(observed, independent):
    """Requirements comparison. An external, version-matched source is a precondition."""
    spec, model = observed["scientific"], observed["model"]
    if independent is None or independent["scope"] != spec["scope"]:
        return ["SOURCE_SCOPE_UNVERIFIED"]
    findings = []
    missing_vars = set(independent["variable_requirements"]) - spec["domains"].keys()
    findings.extend("MISSING_VARIABLE:" + k for k in missing_vars)
    findings.extend("MISSING_EFFECT:" + k for k in independent["effect_requirements"]
                    if k not in missing_vars and spec["weights"].get(k, 0) == 0)
    roots = next(e["roots"] for e in model["events"] if e["kind"] == "adjudicate")
    findings.extend("MISSING_BINDING:" + k for k, value in independent["binding_requirements"].items()
                    if roots.get(k) != value)
    outside = independent["missing_world"]
    if outside is not None and set(outside) == set(spec["domains"]):
        values = [outside[k] for k in sorted(spec["domains"])]
        if spec.get("allowed") is not None and values not in spec["allowed"]:
            findings.append("OMITTED_ADMISSIBLE_WORLD")
    return sorted(findings)


def control_only(o):
    return governance.hr1(o["model"], o["remainder"])


def sensitivity_arm(o):
    return control_only(o), sensitivity.joint_exhaustive(pilot.diagnostic_input(o))


def dea_arm(o):
    response = pilot.arm_d(o)
    diag = response["diagnostic"]
    return response["governance"], (diag["status"], diag.get("outcomes", []),
                                     diag.get("minimal_substantive_query"))


def relevant(worlds):
    """From examiner truth, report direct ceteris-paribus switches with example pairs."""
    witnesses = {}
    for left, right in combinations(worlds, 2):
        if left["decision"] == right["decision"]:
            continue
        diff = [k for k, v in left["values"].items() if right["values"][k] != v]
        if len(diff) == 1:
            witnesses.setdefault(diff[0], [left, right])
    return witnesses


def projected_truth_deficits(observed, truth):
    """Compare a declared model to independently constructed truth rows."""
    spec = observed["scientific"]
    names = sorted(spec["domains"])
    required = set(truth["needed_governance_bindings"])
    seen = next(e["roots"] for e in observed["model"]["events"] if e["kind"] == "adjudicate")
    deficits = []
    if required - seen.keys():
        deficits.append("governance dependency missing")
    for evidence in truth["worlds"]:
        values = evidence["values"]
        if values.keys() != spec["domains"].keys():
            deficits.append("variable inventory differs")
            continue
        definition = [values[k] for k in names]
        if any(value not in spec["domains"][name] for value, name in zip(definition, names)) or (
            spec.get("allowed") is not None and definition not in spec["allowed"]
        ):
            deficits.append("world omitted")
            continue
        score = spec["offset"] + sum(values[k] * weight for k, weight in spec["weights"].items())
        if ("ACCEPT" if score >= spec["threshold"] else "REJECT") != evidence["decision"]:
            deficits.append("decision effect differs")
    return sorted(set(deficits))


def trial(name, case):
    observed, true = case["observed"], case["truth"]
    output_c = control_only(observed)
    output_s, s = sensitivity_arm(observed)
    output_d, d = dea_arm(observed)
    if serialize(output_c) != serialize(output_s) or serialize(output_c) != serialize(output_d):
        raise AssertionError((name, "governance changed"))
    if s != d:
        raise AssertionError((name, s, d))
    if (output_c["status"], d[0], d[2]) != (case["expected"]["C"], case["expected"]["science"], case["expected"]["query"]):
        raise AssertionError((name, output_c, d, case["expected"]))
    findings = scope_review(observed, case["source"])
    if findings != case["expected"]["audit_findings"]:
        raise AssertionError((name, findings))
    return case | {
        "observed_sha256": sha256(serialize(observed)).hexdigest(),
        "C": {"governance": output_c, "diagnostic": "NOT_APPLICABLE"},
        "C_plus_S": {"governance": output_s, "diagnostic": s},
        "D": {"governance": output_d, "diagnostic": d},
        "audited_questions": findings,
        "substantive_value_if_certified": d[1][0] if d[0] == "CERTIFIED_STABLE" else "UNDETERMINED",
        "reference_switch_witnesses": relevant(true["worlds"]),
        "reference_outcomes": sorted({w["decision"] for w in true["worlds"]}),
        "reference_deficits": projected_truth_deficits(observed, true),
    }


def summary(rows):
    measures = {arm: Counter() for arm in ("C", "C_plus_S", "D")}
    audit = Counter()
    for row in rows.values():
        truth, observed = row["truth"], row["observed"]
        necessary = set(row["reference_switch_witnesses"])
        observable_necessary = necessary & observed["scientific"]["domains"].keys()
        true_instability = len(row["reference_outcomes"]) > 1
        for arm, metrics in measures.items():
            output = row[arm]
            status, _, request = output["diagnostic"] if arm != "C" else ("NOT_APPLICABLE", [], None)
            asks = set(request or [])
            claimed_complete = (arm != "C" and observed["scientific"]["covered"]
                                and status in ("CERTIFIED_STABLE", "UNSTABLE"))
            metrics["cases"] += 1
            metrics["reference_relevant_variables"] += len(necessary)
            metrics["relevant_explicitly_modeled"] += len(observable_necessary)
            metrics["relevant_absent_from_model"] += len(necessary - observable_necessary)
            metrics["relevant_targeted"] += len(asks & necessary)
            metrics["relevant_not_targeted"] += len(necessary - asks)
            metrics["unnecessary_targeted_facts"] += len(asks - necessary)
            metrics["all_targeted_facts"] += len(asks)
            metrics["targeted_cases"] += bool(asks & necessary)
            metrics["underlying_unstable_cases"] += true_instability
            metrics["certified_stable_claims"] += status == "CERTIFIED_STABLE"
            metrics["false_certified_stable_claims"] += status == "CERTIFIED_STABLE" and true_instability
            metrics["modeled_certified_complete_cases"] += claimed_complete
            metrics["false_complete_scope_claims"] += claimed_complete and bool(row["reference_deficits"])
            metrics["known_control_conflict_cases"] += truth["control_conflict"] is True
            metrics["known_conflict_cleared"] += truth["control_conflict"] is True and output["governance"]["passes_gate_with_authority"]
            metrics["governance_unchanged_from_C"] += output["governance"] == row["C"]["governance"]
        audit["scopes_with_reference_deficit"] += bool(row["reference_deficits"])
        audit["defective_scopes_flagged_with_matched_evidence"] += bool(row["reference_deficits"]) and any(
            f != "SOURCE_SCOPE_UNVERIFIED" for f in row["audited_questions"])
        audit["nondefective_scopes_falsely_flagged"] += not row["reference_deficits"] and any(
            f != "SOURCE_SCOPE_UNVERIFIED" for f in row["audited_questions"])
        audit["absent_relevant_variables_identified_by_external_source"] += len({
            f.split(":", 1)[1] for f in row["audited_questions"] if f.startswith("MISSING_VARIABLE:")
        } & (necessary - observable_necessary))
        audit["stale_scope_evidence_rejected"] += row["audited_questions"] == ["SOURCE_SCOPE_UNVERIFIED"]
    return {"methods": {arm: dict(metrics) for arm, metrics in measures.items()}, "external_review": dict(audit)}


def correction_rechecks(synthetic, public):
    corrections = {}
    for name in benchmarks.CASES:
        incomplete = public[name + "-omitted-option"]
        reviewed = public[name + "-known-option"]
        assert incomplete["audited_questions"] and incomplete["D"]["diagnostic"][0] == "CERTIFIED_STABLE"
        assert reviewed["D"]["diagnostic"][0] == "UNSTABLE" and reviewed["C"] == incomplete["C"]
        assert reviewed["observed"]["scientific"]["scope"] == incomplete["observed"]["scientific"]["scope"]
        corrections[name] = {"before": incomplete["D"], "reviewed": reviewed["D"],
                             "evidence": incomplete["audited_questions"]}
    before = synthetic["Q-C"]
    replacement = deepcopy(before["observed"])
    reviewed_bindings = before["source"]["binding_requirements"]
    decision = next(e for e in replacement["model"]["events"] if e["kind"] == "adjudicate")
    decision["roots"].update(reviewed_bindings)
    # A hypothetical fresh adjudication with new versioned bindings and modeled evidence.
    replacement["model"].update(attempt="Q-C-reviewed@2", snapshot_version="reviewed@2",
                                commit_version="reviewed@2")
    corrected = control_only(replacement)
    assert corrected["status"] == "CONFLICT" and before["C"]["governance"]["passes_gate_with_authority"]
    corrections["Q-C"] = {"before": before["C"]["governance"], "hypothetical_new_attempt": corrected,
                          "reviewed_roots": decision["roots"]}
    return corrections


def bounded_compare():
    common = cases.model({"u": [0, 1], "v": [0, 1]})["scientific"]
    by_status = Counter()
    policies = product((-1, 0, 1), (-1, 0, 1), (-1, 0, 1), (0, 1),
                       (None, [], [[0, 0], [1, 1]]), (False, True))
    for a, b, offset, limit, allowed, covered in policies:
        spec = common | {"weights": {"u": a, "v": b}, "offset": offset, "threshold": limit,
                         "allowed": allowed, "covered": covered, "samples": [[0, 0]]}
        base = sensitivity.joint_exhaustive(spec)
        other = stability.evaluate(spec)
        if base != (other["status"], other.get("outcomes", []), other.get("minimal_substantive_query")):
            raise AssertionError(spec)
        by_status[base[0]] += 1
    return dict(sorted(by_status.items()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--timing", type=Path)
    args = parser.parse_args()
    data, times = benchmarks.evaluate()
    synthetic = {key: trial(key, row) for key, row in cases.suites().items()}
    start = perf_counter_ns()
    public = {key: trial(key, row) for key, row in cases.public_cases(data)}
    compared = perf_counter_ns()
    twin_l, twin_r = (synthetic[k] for k in ("Q-B", "Q-B0"))
    assert twin_l["observed_sha256"] == twin_r["observed_sha256"]
    assert twin_l["D"] == twin_r["D"] and twin_l["reference_outcomes"] != twin_r["reference_outcomes"]
    rechecks = correction_rechecks(synthetic, public)
    by_status = bounded_compare()
    result = {
        "format": "decision-question-audit-v0.1", "synthetic": synthetic, "public_benchmark_fits": data,
        "public_benchmark_variants": public, "synthetic_metrics": summary(synthetic),
        "public_benchmark_metrics": summary(public), "combined_metrics": summary(synthetic | public),
        "bounded_joint_equivalence": {"cases": sum(by_status.values()), "status_counts": by_status},
        "nonidentifiability": {"same_observed_sha256": twin_l["observed_sha256"], "pair": ["Q-B", "Q-B0"]},
        "independent_review_rechecks": rechecks,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.timing:
        written = perf_counter_ns()
        workload = [c["observed"] for c in (synthetic | public).values()]
        measurements = {}
        for name, arm in (("C", control_only), ("C_plus_S", sensitivity_arm), ("D", dea_arm)):
            elapsed = repeat(lambda: [arm(o) for o in workload], repeat=5, number=80)
            measurements[name] = round(median(elapsed) * 1e6 / (80 * len(workload)), 3)
        report = {"case_checks_ms": times, "four_public_comparisons_and_review_ms": (compared - start) / 1e6,
                  "snapshot_aggregation_and_full_report_write_ms": (written - compared) / 1e6,
                  "machine_median_us_per_case": measurements, "repeats": 5, "calls_per_repeat": 80 * len(workload)}
        args.timing.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"PASS: {len(synthetic)} synthetic, {len(public)} benchmark variants, {sum(by_status.values())} finite comparisons")


if __name__ == "__main__":
    main()
