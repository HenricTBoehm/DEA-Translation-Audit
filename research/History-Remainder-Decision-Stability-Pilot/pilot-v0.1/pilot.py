"""Run the predeclared synthetic comparison and produce deterministic evidence."""

import argparse
import hashlib
import json
import random
import statistics
import timeit
from collections import Counter
from copy import deepcopy
from pathlib import Path

import fixtures
import governance
import oracle
import p01
import stability

SEED = 20261116
GOVERNANCE_CLAIMS = {
    "A": ["role declaration", "disposition authority"],
    "B": ["role declaration", "disposition authority", "canonical identities", "event coverage/order",
          "mandatory roots/links", "seal bindings", "eval/commit snapshot binding"],
    "C": ["role declaration", "disposition authority", "canonical identities", "event coverage/order",
          "mandatory roots/links", "seal bindings", "eval/commit snapshot binding", "historical bound scope",
          "certified actual effects", "independent issuer", "transformer and reset evidence"],
}
GOVERNANCE_CLAIMS["D"] = GOVERNANCE_CLAIMS["C"]


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def diagnostic_input(evidence):
    """Bind the scientific domain to the concrete protected procedure, independently of G."""
    spec = deepcopy(evidence["scientific"])
    m = evidence["model"]
    phase = {}
    for event in m["events"]:
        kind = event["kind"]
        if kind in ("seal", "adjudicate") and event["authenticated"] is True:
            if kind in phase and phase[kind] != event:
                spec["policy_defined"] = False
            phase[kind] = event
    seal, commit = phase.get("seal", {}), phase.get("adjudicate", {})
    rubric = seal.get("pins", {}).get("rubric")
    protected = {"attempt": m.get("attempt"), "seal": seal.get("artifact"), "rubric": rubric,
                 "policy": m.get("policy"), "commit": m.get("commit_version")}
    if (rubric != commit.get("roots", {}).get("rubric")
            or protected != spec["scope"] or any(m.get(k) is not True
                                                  for k in ("snapshot_attested", "bound_complete", "graph_attested"))
            or protected["commit"] != m["snapshot_version"]
            or any(link.get("authenticated") is not True for link in m.get("dependencies", ()))):
        spec["policy_defined"] = False
    return spec


def arm_d(evidence):
    return {"governance": governance.hr1(evidence["model"], evidence["remainder"]),
            "diagnostic": stability.evaluate(diagnostic_input(evidence))}


def trial(case):
    evidence = {k: v for k, v in case.items() if k != "oracle"}
    truth = case["oracle"]
    arms = governance.evaluate(evidence)
    d = arm_d(evidence)
    if encoded(arms["C"]) != encoded(d["governance"]):
        raise AssertionError("governance changed by attaching diagnostic")
    expected = oracle.expected_arms(evidence, truth)
    if tuple(arms[k]["status"] for k in "ABC") != expected:
        raise AssertionError((expected, arms, evidence))
    diag = d["diagnostic"]
    spec = diagnostic_input(evidence)
    ref = oracle.scientific(spec)
    if (diag["status"], set(diag.get("outcomes", ())), diag.get("minimal_substantive_query")) != ref:
        raise AssertionError((diag, ref))
    px, js = oracle.concrete(evidence["model"], truth["prestate"], truth.get("hidden_dependencies", ()))
    return {"truth": {"conflict": bool(px & js), "principals": sorted(px & js),
                      "valid": truth["valid"], "authorized": truth["authorized"]},
            "A": arms["A"], "B": arms["B"], "C": arms["C"], "D": d}


def summarize(rows):
    report = {}
    for arm in "ABCD":
        outcomes = Counter()
        confusion = Counter()
        for row in rows:
            record = row[arm] if arm != "D" else row["D"]["governance"]
            truth, verdict = row["truth"], record["status"]
            eligible = truth["valid"] and truth["authorized"] and not truth["conflict"]
            passed = record["passes_gate_with_authority"]
            outcomes[verdict] += 1
            confusion["conflict_truth"] += truth["conflict"]
            confusion["nonconflict_truth"] += not truth["conflict"]
            confusion["true_eligible"] += eligible
            confusion["invalid_truth"] += not truth["valid"]
            confusion["false_clear_control"] += truth["conflict"] and passed
            confusion["false_positive_conflict"] += not truth["conflict"] and verdict == p01.CONFLICT
            confusion["conservative_holds_among_eligible"] += eligible and verdict == p01.UNKNOWN
            confusion["clear_invalid"] += not truth["valid"] and passed
            confusion["gate_passes"] += passed
            if record["reason"].startswith(("BOUND:", "REMAINDER:")):
                confusion[record["reason"].split(":")[0]] += 1
        report[arm] = {"n": len(rows), "outcomes": dict(outcomes), "counts": dict(confusion)}

    diagnostic = Counter()
    requests = Counter()
    for row in rows:
        d, g = row["D"]["diagnostic"], row["C"]["status"]
        diagnostic[d["status"]] += 1
        query = d.get("minimal_substantive_query")
        if g == p01.UNKNOWN:
            requests["governance_unknown"] += 1
            requests["outcome_insensitive"] += d["status"] == "CERTIFIED_STABLE"
            requests["targeted_query"] += d["status"] == "UNSTABLE" and query is not None
            if query is not None:
                requests["covered_query_comparisons"] += 1
                requests["all_substantive_facts"] += len(fixtures.fixture()["scientific"]["domains"])
                requests["minimal_substantive_facts"] += len(query)
        requests["stable_and_conFLICT"] += g == p01.CONFLICT and d["status"] == "CERTIFIED_STABLE"
    return report | {"stability": dict(diagnostic), "incremental": dict(requests)}


def timing(cases):
    m = [({k: v for k, v in c.items() if k != "oracle"}) for c in cases.values()]
    functions = {
        "A": lambda c: governance.nominal(c["model"]),
        "B": lambda c: governance.provenance(c["model"]),
        "C": lambda c: governance.hr1(c["model"], c["remainder"]),
        "D": arm_d,
    }
    return {name: {"calls_per_repeat": 1200, "repeats": 5,
                   "median_us_per_case": round(1e6 * statistics.median(timeit.repeat(
                       lambda: [function(c) for c in m], repeat=5, number=100)) / 1200, 3)}
            for name, function in functions.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timing", type=Path)
    parser.add_argument("--n", type=int, default=1000)
    args = parser.parse_args()
    named = fixtures.named()
    cases = {key: trial(row) for key, row in named.items()}
    expected_named = {
        "S01": (p01.CLEAR, "CERTIFIED_STABLE"), "S02": (p01.CONFLICT, "CERTIFIED_STABLE"),
        "S03": (p01.UNKNOWN, "CERTIFIED_STABLE"), "S04": (p01.UNKNOWN, "UNSTABLE"),
        "S05": (p01.INVALID, "STABILITY_UNDETERMINED"), "S06": (p01.CONFLICT, "CERTIFIED_STABLE"),
        "S07": (p01.CLEAR, "CERTIFIED_STABLE"), "S08": (p01.UNKNOWN, "CERTIFIED_STABLE"),
        "S09": (p01.UNKNOWN, "UNSTABLE"), "S10": (p01.CONFLICT, "CERTIFIED_STABLE"),
        "S11": (p01.CLEAR, "CERTIFIED_STABLE"), "S12": (p01.UNKNOWN, "STABILITY_UNDETERMINED"),
    }
    for key, result in cases.items():
        if (result["C"]["status"], result["D"]["diagnostic"]["status"]) != expected_named[key]:
            raise AssertionError(key)
    probes = {}
    for key, (spec, expected) in fixtures.stability_probes().items():
        actual = stability.evaluate(spec)
        reference = oracle.scientific(spec)
        if (expected != actual["status"] or
                (actual["status"], set(actual.get("outcomes", ())), actual.get("minimal_substantive_query")) != reference):
            raise AssertionError(key)
        probes[key] = {"input": spec, "expected": expected, "actual": actual}
    # Replacing diagnostics with a constant-score policy must leave the governing bytes unchanged.
    for case in named.values():
        changed = deepcopy(case)
        changed["scientific"].update(weights={}, offset=1)
        evidence = {k: v for k, v in case.items() if k != "oracle"}
        if encoded(arm_d(changed)["governance"]) != encoded(governance.evaluate(evidence)["C"]):
            raise AssertionError("intervention on diagnostic changed control decision")

    finite = [trial(fixtures.generated(bits)) for bits in fixtures.parameters()]
    generator = random.Random(SEED)
    draws = [tuple(generator.randrange(n) for n in (2, 2, 2, 2, 3, 2)) for _ in range(args.n)]
    randomized = [trial(fixtures.generated(bits)) for bits in draws]
    outcomes = {"seed": SEED, "named": {key: {"input": named[key], "evaluation": row} for key, row in cases.items()},
                "stability_probes": probes, "governance_claims_by_arm": GOVERNANCE_CLAIMS,
                "diagnostic_claims": ["fixed substantive procedure and effect interpretation", "world-domain coverage"],
                "case_order": ["named", "finite", "random"], "finite_specs": "fixtures.parameters()",
                "random_draw_digest": hashlib.sha256(encoded(draws).encode()).hexdigest(),
                "random_unique": len(set(draws)), "named_metrics": summarize(list(cases.values())),
                "finite_metrics": summarize(finite), "random_metrics": summarize(randomized)}
    args.out.write_text(json.dumps(outcomes, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    if args.timing:
        args.timing.write_text(json.dumps(timing(named), sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("PASS:", len(named), "named,", len(probes), "diagnostic probes,", len(finite),
          "enumerated,", len(randomized), "deterministically drawn; no C/D governance changes")


if __name__ == "__main__":
    main()
