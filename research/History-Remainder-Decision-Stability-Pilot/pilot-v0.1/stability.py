"""Substantive diagnostic. Inputs contain no governance verdict."""

from itertools import combinations, product

SCOPE = ("attempt", "seal", "rubric", "policy", "commit")


def evaluate(spec):
    scope = spec["scope"]
    if (not all(scope.get(key) for key in SCOPE) or scope != spec["world_scope"]
            or not spec["policy_defined"]
            or (spec["observed"].keys() | spec["weights"].keys()) - spec["domains"].keys()):
        return {"status": "STABILITY_UNDETERMINED", "reason": "unresolved or incompatible fixed scope"}
    keys = tuple(sorted(spec["domains"]))
    sampled = spec["samples"]
    allowed = spec.get("allowed")

    def admissible(values):
        return (all(value in spec["domains"][key] for key, value in zip(keys, values))
                and all(values[keys.index(key)] == val for key, val in spec["observed"].items())
                and (allowed is None or list(values) in allowed))

    if spec["covered"]:
        worlds = [row for row in product(*(spec["domains"][key] for key in keys)) if admissible(row)]
    else:
        worlds = sorted({tuple(row) for row in sampled if len(row) == len(keys) and admissible(row)})
    if not worlds:
        return {"status": "STABILITY_UNDETERMINED", "reason": "no established admissible world"}
    outcomes, by_world = {}, {}
    for row in worlds:
        value = spec["offset"] + sum(spec["weights"].get(key, 0) * val for key, val in zip(keys, row))
        outcome = "ACCEPT" if value >= spec["threshold"] else "REJECT"
        by_world[row] = outcome
        outcomes.setdefault(outcome, dict(zip(keys, row)))
    if len(outcomes) > 1:
        status = "UNSTABLE"
    else:
        status = "CERTIFIED_STABLE" if spec["covered"] else "SAMPLED_STABLE"
    query = None
    if spec["covered"]:
        unresolved = tuple(i for i, key in enumerate(keys) if key not in spec["observed"])
        for size in range(len(unresolved) + 1):
            for group in combinations(unresolved, size):
                partitions = {}
                for row, label in by_world.items():
                    signature = tuple(row[i] for i in group)
                    partitions.setdefault(signature, set()).add(label)
                if all(len(labels) == 1 for labels in partitions.values()):
                    query = [keys[i] for i in group]
                    break
            if query is not None:
                break
    return {"status": status, "outcomes": sorted(outcomes), "witness_worlds": outcomes,
            "world_count": len(worlds), "coverage": "finite fixture exhaustive" if spec["covered"] else "samples",
            "scope": scope, "minimal_substantive_query": query}
