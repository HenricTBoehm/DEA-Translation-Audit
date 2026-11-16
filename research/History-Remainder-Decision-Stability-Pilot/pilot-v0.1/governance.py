"""A/B/C control gates. D imports C as an unchanged component."""

from copy import deepcopy

import p01


def response(status, reason, authorized, witnesses=()):
    return {"status": status, "reason": reason, "witnesses": list(witnesses),
            "passes_gate_with_authority": status == p01.CLEAR and authorized}


def nominal(model):
    roles = {e["kind"]: e["actor"] for e in model["events"]
             if e["kind"] in ("produce", "adjudicate") and e.get("actor")}
    if not all(k in roles for k in ("produce", "adjudicate")) or roles["produce"] == roles["adjudicate"]:
        return response(p01.UNKNOWN, "nominal four-eyes admission not satisfied", False)
    return response(p01.CLEAR, "declared roles distinct", model["authorized"])


def provenance(model):
    rows, life, problems, missing = p01.normalize(model)
    if problems or not p01.ordered_completion(life, model["record_start"]):
        return response(p01.INVALID, "event admission", False)
    if missing:
        return response(p01.UNKNOWN, "event admission", False)
    if any(model.get(k) is not True for k in ("snapshot_attested", "graph_attested", "bound_complete", "record_complete")
           ) or not model.get("snapshot_version") or model["snapshot_version"] != model.get("commit_version") or any(
               link.get("authenticated") is not True for link in model.get("dependencies", ())):
        return response(p01.UNKNOWN, "missing version-bound procedural provenance", False)
    actors = {e["kind"]: p01.canonical(model, e["actor"]) for e in rows.values()
              if e["kind"] in ("produce", "adjudicate")}
    if actors["produce"] == actors["adjudicate"]:
        return response(p01.CONFLICT, "same authenticated principal", False, [actors["produce"]])
    return response(p01.CLEAR, "authenticated roles and version-bound procedural provenance", model["authorized"])


def cone(model, trace, producer, end):
    """Conservative reverse closure with seal/commit targets and fixed-scope inputs."""
    refs, _, _ = p01.bound_artifacts(model, end["roots"])
    nodes = {p01.canonical(model, end["actor"]), p01.canonical(model, producer["actor"]),
             model["artifact"], *producer["inputs"], *refs}
    for e in sorted(trace, key=p01.coordinate, reverse=True):
        if e["kind"] == "control":
            src = p01.target(model, e, "src")[1]
            dst = p01.target(model, e, "dst")[1]
            if dst in nodes:
                nodes.add(src)
    return sorted(nodes)

def hr1(model, remainder):
    actual = p01.evaluate(with_history(model, remainder))
    if actual["input"] != p01.VALID:
        return response(actual["input"], "event admission", False)
    if actual["outcome"] == p01.CONFLICT:
        return response(p01.CONFLICT, "witnessed effective control", False, actual["witnesses"])
    rows, lifecycle, _, _ = p01.normalize(model)
    end = lifecycle["adjudicate"]
    trace = [e for e in rows.values()
             if model["record_start"] <= e["time"] and p01.coordinate(e) < p01.coordinate(end)]
    if any(e["kind"] == "reset" and not p01.verified_reset(e) for e in trace):
        return response(p01.UNKNOWN, "REMAINDER: reset proof missing", False)
    if any(e["kind"] == "control" and (e["persistence"] != "potential_durable" or e["channel"] not in p01.CHANNELS)
           for e in trace):
        return response(p01.UNKNOWN, "REMAINDER: unsupported transformer", False)
    influenced_targets = set(cone(model, trace, lifecycle["produce"], end)) if remainder["uncovered"] else set()
    if (remainder["kind"] not in ("Z", "B") or remainder["attested"] is not True
            or remainder["actual_attested"] is not True
            or not remainder.get("issuer")
            or (remainder["kind"] == "Z" and (remainder["witnesses"] or remainder["upper"]))
            or any(not p01.verified_seed(s) for s in (*remainder["witnesses"], *remainder["upper"]))
            or any(target in influenced_targets or p01.canonical(model, target) in influenced_targets
                   for target, _ in remainder["uncovered"])):
        return response(p01.UNKNOWN, "REMAINDER: unproved historical bound", False)
    upper = p01.evaluate(with_history(model, remainder, upper=True))
    issuer = p01.canonical(model, remainder["issuer"])
    if issuer in upper["P_x"] or issuer in upper["J_star"]:
        return response(p01.UNKNOWN, "REMAINDER: non-independent issuer", False)
    if upper["outcome"] == p01.CONFLICT:
        return response(p01.UNKNOWN, "BOUND: possible intersection only", False)
    if actual["outcome"] != p01.CLEAR or upper["outcome"] != p01.CLEAR:
        return response(p01.UNKNOWN, "REMAINDER: " + "; ".join(actual["missing"]), False)
    return response(p01.CLEAR, "certified empty upper intersection", model["authorized"])


def with_history(model, remainder, *, upper=False):
    enriched = deepcopy(model)
    seeds = list(remainder["witnesses"]) if remainder["actual_attested"] is True else []
    if upper:
        seeds.extend(remainder["upper"])
    enriched["history"] = {"trusted": True, "coverage": True, "seeds": seeds}
    return enriched


def evaluate(evidence):
    model, remainder = evidence["model"], evidence["remainder"]
    return {"A": nominal(model), "B": provenance(model), "C": hr1(model, remainder)}
