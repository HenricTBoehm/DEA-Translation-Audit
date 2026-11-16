"""Ordinary joint sensitivity on an explicitly declared finite input space."""

from itertools import combinations, product

UNKNOWN = "STABILITY_UNDETERMINED"


def joint_exhaustive(spec):
    keys = sorted(spec["domains"])
    if (spec["scope"] != spec["world_scope"] or not spec["policy_defined"]
            or set(spec["weights"]) - set(keys) or set(spec["observed"]) - set(keys)
            or any(not spec["scope"].get(k) for k in ("attempt", "seal", "rubric", "policy", "commit"))):
        return UNKNOWN, [], None
    observed, restricted = spec["observed"], spec.get("allowed")
    candidates = product(*(spec["domains"][k] for k in keys))
    study = {}
    for values in candidates:
        assignments = dict(zip(keys, values))
        if any(assignments[k] != value for k, value in observed.items()):
            continue
        if restricted is not None and list(values) not in restricted:
            continue
        if not spec["covered"] and list(values) not in spec["samples"]:
            continue
        total = spec["offset"] + sum(weight * assignments[k] for k, weight in spec["weights"].items())
        study[values] = "ACCEPT" if total >= spec["threshold"] else "REJECT"
    outcomes = sorted(set(study.values()))
    if not outcomes:
        return UNKNOWN, [], None
    if not spec["covered"]:
        return ("UNSTABLE" if len(outcomes) > 1 else "SAMPLED_STABLE"), outcomes, None

    # A query separates outcomes iff it hits the difference set of every opposing pair.
    differences = [{k for k, x, y in zip(keys, left, right) if x != y}
                   for left, right in combinations(study, 2) if study[left] != study[right]]
    unresolved = [k for k in keys if k not in observed]
    for count in range(len(unresolved) + 1):
        query = next((list(q) for q in combinations(unresolved, count)
                      if all(pair.intersection(q) for pair in differences)), None)
        if query is not None:
            return ("UNSTABLE" if differences else "CERTIFIED_STABLE"), outcomes, query
    raise AssertionError("distinct assignments cannot remain indistinguishable on every unknown")
