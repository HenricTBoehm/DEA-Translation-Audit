"""Run public reference, independent checks, and assessor negative controls."""
import hashlib
import json
import sys
from collections import Counter
from itertools import product
from pathlib import Path

from cases import altered, cases, grant, reset, revoke, trace, wire, write
from crosscheck import evaluate, rank_realizations
from oracle import justified, truth
from scoring import ACTIONS, metrics

HERE = Path(__file__).resolve().parent


def review():
    results = []
    for case in cases():
        evidence = case["evidence"]
        public_bytes = wire(evidence)
        projection = json.loads(public_bytes)
        actual = truth(case["world"])
        decision = justified(projection)
        truth_independent, _ = evaluate(case["world"]["events"])
        assert actual == truth_independent == case["expected_truth"], case["label"]
        assert decision["verdict"] == case["expected"], case["label"]

        if decision["verdict"] in ("CLEAR", "CONFLICT"):
            checked, causal_versions = evaluate(projection["events"],
                                                root_required=projection["dependencies_closed"])
            assert checked == ("NO_CONFLICT" if decision["verdict"] == "CLEAR" else "CONFLICT")
            if causal_versions is not None:
                assert decision["witness"][3] in causal_versions
        results.append({
            "label": case["label"], "truth": actual, "justified": decision["verdict"],
            "proof_reason": decision["proof"], "witness": decision.get("witness"),
            "wire_sha256": hashlib.sha256(public_bytes).hexdigest(), "premise": case["premise"],
        })

    indexed = {case["label"]: case for case in cases()}
    views = {row["label"]: row["wire_sha256"] for row in results}
    for family in range(1, 4):
        first, second = (indexed[f"K{family}-I-{suffix}"] for suffix in ("a", "b"))
        assert wire(first["evidence"]) == wire(second["evidence"])
        assert first["expected_truth"] != second["expected_truth"]
    assert wire(indexed["X-TRUST"]["evidence"]) == wire(indexed["K1-C"]["evidence"])

    for row in (indexed["missing-rank"], indexed["contradictory-rank"]):
        possible = any(evaluate(order)[0] != "MODEL_INVALID"
                       for order in rank_realizations(row["evidence"]["events"]))
        assert possible == (row["expected"] == "UNDETERMINED")
    both_missing = altered(indexed["K3-F"]["world"]["events"], 4, rank=None)
    both_missing = altered(both_missing, 5, rank=None, time=4)
    assert any(evaluate(order)[0] == "CONFLICT" for order in rank_realizations(both_missing))
    assert justified({**indexed["K3-F"]["evidence"], "events": both_missing})["verdict"] == "UNDETERMINED"

    # Equal authenticated timestamps with unique ranks are admissible; reversing
    # same-time ranks across revoke/write is independently checked below.
    checked = Counter()
    for (writer, channel, withdrawal, successor, selection, timing) in product(
        ("ka", "kq"), ("threshold", "layout"), ("none", "revoke"),
        ("none", "layout", "threshold"), ("r@0", "r@1", "r@2"), ("before", "after")
    ):
        first, second = (3, 5) if timing == "before" else (5, 3)
        changes = [grant(1, writer, "r", channel), write(first, writer, "r@0", "r@1", channel)]
        if withdrawal == "revoke":
            changes.append(revoke(second, writer))
        if successor != "none":
            changes.append(reset(6, "r@1", "r@2", successor))
        rows = trace(*changes, root=selection)
        model = truth({"events": rows})
        assert model == evaluate(rows)[0], (writer, channel, withdrawal, successor, selection, timing)
        checked[model] += 1

    clean = indexed["K1-C"]["evidence"]
    assert wire(clean) == wire({**clean, "events": list(reversed(clean["events"]))})
    for contaminated in ({**clean, "expected": "CLEAR"},
                         {**clean, "events": [{**clean["events"][0], "case_id": "K1-C"}]}):
        try:
            wire(contaminated)
        except ValueError:
            pass
        else:
            raise AssertionError("assessor data escaped the wire schema")

    regular = [row for row in results[:14] if row["label"] != "X-TRUST"]
    lookup = {row["wire_sha256"]: ACTIONS[row["justified"]] for row in regular}
    assert len(lookup) == 10
    public_fit = sum(lookup[row["wire_sha256"]] == ACTIONS[row["justified"]] for row in regular)
    unseen = [row for row in results[14:] if row["wire_sha256"] not in lookup]
    assert public_fit == 13 and unseen
    attacks = {}
    controls = {
        "ideal": None, "always_deny": "BLOCK_UNDETERMINED", "always_permit": "RELEASE",
        "always_invalid": "INVALID", "proofless_conflict": "BLOCK_CONFLICT",
        "always_no_decision": "NO_DECISION", "public_lookup": "PUBLIC_LOOKUP",
    }
    for name, action in controls.items():
        rows = []
        for row in results:
            response = lookup.get(row["wire_sha256"], "NO_DECISION") if action == "PUBLIC_LOOKUP" else action
            rows.append({**row, "action": response or ACTIONS[row["justified"]],
                         "proof": "NONE" if response else "VERIFIED", "fidelity": "NOT EXECUTED"})
        ordinary = rows[:13]
        distinct = list({row["wire_sha256"]: row for row in ordinary}.values())
        # Actual-truth counts stay execution-based when two worlds share a view.
        distinct_only = {k: v for k, v in metrics(distinct).items()
                         if k not in {"false_release_truth", "holds_on_actual_no_conflict",
                                      "release_invalid_truth", "miss_actual_invalid"}}
        attacks[name] = {"regular": metrics(ordinary), "distinct_views": distinct_only,
                         "premise_attack": metrics(rows[13:14]), "supplement": metrics(rows[14:])}
    assert attacks["ideal"]["regular"]["verdict_verified"] == [13, 13]
    assert attacks["always_deny"]["regular"]["false_hold_justified"] == [3, 3]
    assert attacks["always_permit"]["regular"]["false_release_justified"] == [10, 10]
    assert attacks["always_invalid"]["regular"]["false_invalid"] == [12, 12]
    assert attacks["proofless_conflict"]["regular"]["unverified_conflict"] == [13, 13]
    assert attacks["ideal"]["premise_attack"]["false_release_truth"] == [1, 1]
    assert views["X-TRUST"] == views["K1-C"]
    return {
        "status": "public synthetic checks; no comparators, custody or authentication run",
        "public_results": results,
        "regular_justified_counts": dict(Counter(row["justified"] for row in regular)),
        "regular_truth_counts": dict(Counter(row["truth"] for row in regular)),
        "generated_complete_histories": dict(checked),
        "lookup_regular_exact": [public_fit, len(regular)],
        "supplement_not_in_regular_lookup": len(unseen),
        "scoring_controls": attacks,
    }


def check_or_save(filename, obj):
    payload = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    path = HERE / filename
    if sys.argv[1:] == ["--write-public"]:
        path.write_text(payload, encoding="utf-8")
    else:
        assert path.read_text(encoding="utf-8") == payload, filename


if __name__ == "__main__":
    if sys.flags.optimize:
        raise SystemExit("assertions must be enabled")
    if sys.argv[1:] not in ([], ["--write-public"]):
        raise SystemExit("usage: python3 verify.py [--write-public]")
    check_or_save("PUBLIC_CASES.json", cases())
    report = review()
    check_or_save("RESULTS.json", report)
    print(f"PASS: {len(report['public_results'])} public cases; "
          f"{sum(report['generated_complete_histories'].values())} generated histories; "
          "rank, premise, projection and scoring controls")
