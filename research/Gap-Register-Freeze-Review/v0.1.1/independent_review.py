"""Independent synthetic scope/oracle review. This is not a comparator implementation."""

import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

CONFLICT = "CONFLICT"
CLEAR = "CLEAR"
NO_CONFLICT = "NO_CONFLICT"
UNKNOWN = "UNDETERMINED"
INVALID = "INVALID"
MATERIAL = ("threshold", "criterion", "output")


def event(rank, op, **attrs):
    return {"rank": rank, "op": op, **attrs}


def independent_trace(family, value, ranks):
    """Hydrate a stipulated template into an explicit reference history.

    Extra semantic facts are written here, rather than inferred from the reported
    labels. kq makes the independent writer's key explicit in the reference.
    """
    rubric = "r@2" if family == "K3" else "r@1"
    dependencies = [(rubric, "threshold")]
    if family == "K1" and value:
        dependencies.append(("standard@1", "criterion"))
    initial = [("ka", "x@1", "output")]
    initial.append(("ka" if family == "K1" else "kq", "standard@1", "criterion"))
    operations = [
        event(ranks["produce"], "produce", key="ka", obj="x@1"),
        event(ranks["seal"], "seal", obj="x@1"),
        event(ranks["adjudicate"], "read_and_adjudicate", dependencies=dependencies),
    ]
    if family == "K2":
        initial.append(("ka" if value == "p" else "kq", rubric, "threshold"))
    if family == "K3":
        writer = "ka" if value == "p" else "kq"
        initial.append((writer, rubric, "threshold"))
        operations.extend([
            event(ranks["historical_modify"], "write", key=writer, obj=rubric, field="threshold", effect="included-modification"),
            event(ranks["revoke"], "revoke", key="ka"),
        ])
        # r@2 is a committed snapshot in this history; validity of a prior write
        # is distinct from the ability to change what the adjudicator reads now.
        seal = next(event for event in operations if event["op"] == "seal")
        seal["also_freeze"] = [rubric]
    return {"keys": {"ka": "p", "kq": "q", "kj": "j"}, "initial_rights": initial, "events": operations}


def history_result(trace):
    """Replay role rights and contents; query only fields that can affect the fixed evaluation."""
    keys = trace["keys"]
    rights = {tuple(r) for r in trace["initial_rights"]}
    live = set(keys)
    frozen, written = set(), {}
    produced, sealed = None, False
    witness = {}
    ranks = [e["rank"] for e in trace["events"]]
    if any(type(rank) is not int or not 0 <= rank <= 5 for rank in ranks) or len(set(ranks)) != len(ranks):
        return INVALID, {}
    for row in sorted(trace["events"], key=lambda e: e["rank"]):
        op = row["op"]
        if op == "produce":
            slot = row["key"], row["obj"], "output"
            if produced is not None or row["key"] not in live or slot not in rights:
                return INVALID, {}
            produced = keys[row["key"]]
        elif op == "write":
            slot = row["key"], row["obj"], row["field"]
            if row["key"] not in live or slot not in rights or row["obj"] in frozen:
                return INVALID, {}
            written[row["obj"], row["field"]] = keys[row["key"]], row["effect"]
        elif op == "seal":
            if produced is None or sealed:
                return INVALID, {}
            sealed = True
            frozen.add(row["obj"])
            frozen.update(row.get("also_freeze", ()))
        elif op == "revoke":
            live.discard(row["key"])
        elif op == "reset":
            addr = row["obj"], row["field"]
            successor = row.get("successor")
            if row["proved"] and addr in written and written[addr][1] == row["effect"]:
                if row["obj"] in frozen and (not successor or successor == row["obj"]):
                    return INVALID, {}
                if successor:
                    for (target, field), effect in list(written.items()):
                        if target == row["obj"] and field != row["field"]:
                            written[successor, field] = effect
                    frozen.add(successor)
                else:
                    del written[addr]
        elif op == "read_and_adjudicate":
            if not sealed:
                return INVALID, {}
            for obj, field in row["dependencies"]:
                if field not in MATERIAL:
                    continue
                if (obj, field) in written and written[obj, field][0] == produced:
                    witness[f"{obj}:{field}"] = written[obj, field][1]
                if obj not in frozen and any(
                    key in live and keys[key] == produced and (key, obj, field) in rights for key in keys
                ):
                    witness[f"{obj}:{field}"] = "live effective write"
            return (CONFLICT if witness else NO_CONFLICT), witness
        else:
            raise ValueError(op)
    return INVALID, {}


def serialized_view(ranks, family, observation, coverage):
    # For this audit the template names stand for public structure; a scored
    # runner needs an explicit wire schema without benchmark labels.
    value = {"structure": family, "ranks": ranks, "observation": observation, "coverage": coverage}
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def status(epistemic, allowed):
    if not allowed:
        return INVALID
    if all(verdict == CONFLICT for verdict in allowed):
        return CONFLICT
    return CLEAR if epistemic and all(v == NO_CONFLICT for v in allowed) else UNKNOWN


def independent_profiles(pack):
    families = {}
    for name, row in pack["families"].items():
        entries = []
        for value in row["values"]:
            trace = independent_trace(name, value, pack["timelines"][name])
            verdict, witness = history_result(trace)
            entries.append({"value": value, "trace": trace, "truth": verdict, "witness": witness})
        families[name] = entries
    assert sum(map(len, families.values())) == 6
    output, attacks = [], []
    for profile in (*pack["profiles"], *pack["premise_attacks"]):
        family = profile["family"]
        ranks = dict(pack["timelines"][family], **profile.get("order_override", {}))
        observation = profile["authenticated_observation"]
        def accepts(value):
            return observation is None or (type(value) is type(observation) and value == observation)
        candidates = [history_result(independent_trace(family, w["value"], ranks))[0]
                      for w in families[family] if accepts(w["value"])]
        possible = [item for item in candidates if item != INVALID]
        result = status(profile["coverage_attested"], possible)
        expected = profile.get("expected_justified", profile.get("expected_conditional"))
        assert result == expected, (profile["id"], result)
        tests = {w["value"]: w for w in families[family]}
        actuals = profile["actual_values"] or [None]
        for actual in actuals:
            view = serialized_view(ranks, family, observation, profile["coverage_attested"])
            outcome = {"profile": profile["id"], "view_sha256": sha256(view).hexdigest(),
                       "sanitized_view": json.loads(view), "justified": result,
                       "actual": tests[actual]["truth"] if actual is not None else INVALID,
                       "actual_value_private": actual, "compatible_worlds": len(possible)}
            if profile in pack["premise_attacks"]:
                attacks.append(outcome)
            else:
                output.append(outcome)
    by_id = {label: [row for row in output if row["profile"] == label] for label in ("K1-I", "K2-I", "K3-I")}
    for label, twins in by_id.items():
        assert len(twins) == 2 and twins[0]["view_sha256"] == twins[1]["view_sha256"], label
        assert twins[0]["actual"] != twins[1]["actual"], label
    honest = next(row for row in output if row["profile"] == "K1-C")
    assert len(attacks) == 1 and attacks[0]["view_sha256"] == honest["view_sha256"]
    assert attacks[0]["actual"] == CONFLICT and attacks[0]["justified"] == CLEAR
    return families, output, attacks


def scoring_checks(rows):
    expected = {CLEAR: "RELEASE", CONFLICT: "BLOCK_CONFLICT",
                UNKNOWN: "BLOCK_UNDETERMINED", INVALID: INVALID}
    constants = {"always_deny": "BLOCK_UNDETERMINED", "always_permit": "RELEASE",
                 "always_invalid": INVALID, "always_conflict_without_proof": "BLOCK_CONFLICT"}

    def score(returned):
        counts = Counter()
        for row in rows:
            verdict = row["justified"]
            release = returned == "RELEASE"
            counts["S1_mismatches"] += release != (verdict == CLEAR)
            counts["S2_mismatches"] += returned != expected[verdict] or returned == "BLOCK_CONFLICT"
            counts["false_holds_on_CLEAR"] += verdict == CLEAR and not release
            counts["unjustified_releases"] += verdict != CLEAR and release
            counts["actual_false_releases"] += row["actual"] == CONFLICT and release
            counts["unjustified_positive_claims"] += returned == "BLOCK_CONFLICT"
            counts["false_invalid"] += verdict != INVALID and returned == INVALID
            counts["missed_invalid"] += verdict == INVALID and returned != INVALID
            counts["correct_abstentions"] += verdict == UNKNOWN and returned == "BLOCK_UNDETERMINED"
        return dict(counts)
    result = {name: score(v) for name, v in constants.items()}
    assert [(result[k]["S1_mismatches"], result[k]["S2_mismatches"]) for k in constants] == [
        (3, 7), (10, 10), (3, 12), (3, 13)]
    return result


def mutations(package, pack):
    """Expected design counterexamples. Keep package input and oracle byte-identical."""
    spec = importlib.util.spec_from_file_location("archived_oracle", package / "oracle.py")
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    known = next(row for row in pack["profiles"] if row["id"] == "K3-F")
    variants = {
        "revoke_before_historical_write": known | {"order_override": {"historical_modify": 3, "seal": 4, "adjudicate": 5}},
        "out_of_alphabet_adjudication": known | {"order_override": {"adjudicate": 6}},
        "missing_order_coordinate": known | {"order_override": {"seal": None}},
        "positive_with_open_coverage": known | {"coverage_attested": False},
    }
    actual = {k: old.evaluate_profile(pack, v)["justified_conditional"] for k, v in variants.items()}
    assert list(actual.values()) == [CONFLICT, CONFLICT, INVALID, CONFLICT]
    altered = independent_trace("K3", "p", {**pack["timelines"]["K3"], "historical_modify": 3, "seal": 4, "adjudicate": 5})
    assert history_result(altered)[0] == INVALID

    p = independent_trace("K1", True, pack["timelines"]["K1"])
    final = next(row for row in p["events"] if row["op"] == "read_and_adjudicate")
    p["initial_rights"].remove(("ka", "standard@1", "criterion"))
    p["initial_rights"].append(("ka", "standard@1", "layout"))
    final["dependencies"].append(("standard@1", "layout"))
    assert history_result(p) == (NO_CONFLICT, {})  # Coarse artifact-level matching would accuse p.

    via_resolver = deepcopy(p)
    c = next(row for row in via_resolver["events"] if row["op"] == "read_and_adjudicate")
    c["dependencies"].append(("selected_threshold@1", "threshold"))
    via_resolver["initial_rights"].append(("ka", "selected_threshold@1", "threshold"))
    assert history_result(via_resolver)[0] == CONFLICT  # Projecting away the actual resolver target loses p.

    residue = independent_trace("K3", "p", pack["timelines"]["K3"])
    end_later = [{**e, "rank": 5} if e["op"] == "read_and_adjudicate" else e for e in residue["events"]]
    credential = end_later + [event(4, "reset", obj="r@2", field="credential",
                                     effect="included-modification", proved=True)]
    exact = [dict(e, dependencies=[("r@3", "threshold")]) if e["op"] == "read_and_adjudicate" else e
             for e in end_later]
    exact.append(event(4, "reset", obj="r@2", field="threshold", successor="r@3",
                       effect="included-modification", proved=True))
    assert history_result(residue | {"events": credential})[0] == CONFLICT
    assert history_result(residue | {"events": exact})[0] == NO_CONFLICT
    assert history_result(residue | {"events": end_later + [{**exact[-1], "successor": "r@2"}]})[0] == INVALID

    return {"archived_probes": {key: {"input": variants[key], "result": val} for key, val in actual.items()},
            "reference_revoke_first": {"trace": altered, "result": INVALID},
            "cosmetic_write_to_consumed_artifact": {"trace": p, "result": NO_CONFLICT},
            "resolved_dynamic_threshold": {"trace": via_resolver, "result": CONFLICT},
            "credential_reset": {"trace": residue | {"events": credential}, "result": CONFLICT},
            "exact_neutralization": {"trace": residue | {"events": exact}, "result": NO_CONFLICT}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    pack = json.loads((args.package / "cases-v0.1.1.json").read_bytes())
    truth, rows, attacks = independent_profiles(pack)
    fixed = Counter(row["justified"] for row in rows)
    assert fixed == {CLEAR: 3, CONFLICT: 3, UNKNOWN: 6, INVALID: 1}
    digest_lookup = {row["view_sha256"]: row["justified"] for row in rows}
    assert len(digest_lookup) == 10 and all(digest_lookup[row["view_sha256"]] == row["justified"] for row in rows)
    report = {"scope": "review only; transparent finite reference reconstruction",
              "reference_worlds": truth, "ordinary_executions": rows, "premise_attack": attacks,
              "ordinary_counts": dict(fixed), "unmodified_corpus_lookup_matches": len(rows),
              "negative_scoring_controls": scoring_checks(rows), "adversarial": mutations(args.package, pack)}
    args.out.write_text(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("PASS: six explicit reference worlds, 13 ordinary executions, X-TRUST, scoring controls and counterexamples")


if __name__ == "__main__":
    main()
