"""Independent finite oracle, using historical path replay per origin and direct world truth tables."""

from itertools import combinations, product
from fractions import Fraction
from functools import lru_cache

LIFE = ("produce", "seal", "adjudicate")
CHANNELS = ("artifact", "capability", "credential", "criteria")


def closure(roots, links):
    graph = {(e["from"], e["to"]) for e in links if e["authenticated"]}
    while True:
        before = graph
        graph |= {(u, z) for u, v in graph for w, z in graph if v == w}
        if graph == before:
            return roots | {v for u, v in graph if u in roots}


def concrete(model, initial, hidden=()):
    """Derive potential control backwards for the exact scoped fixture trace."""
    events = sorted(model["events"], key=lambda e: (e["time"], Fraction(e["order"])))
    production, seal, decision = (next(i for i, e in enumerate(events) if e["kind"] == k) for k in LIFE)
    alias = model.get("binding", {})

    def node(key, artifact=False):
        return ("artifact", key) if artifact else ("identity", alias.get(key, key))

    a = node(events[production]["actor"])
    j = node(events[decision]["actor"])
    refs = closure(set(events[decision]["roots"].values()), [*model.get("dependencies", []), *hidden])
    seeded = {(alias.get(t["principal"], t["principal"]), node(t["target"], t.get("target_artifact")),
               t["channel"]) for t in initial}
    origins = {a[1], j[1]} | {t[0] for t in seeded}
    origins |= {node(e["src"])[1] for e in events[:decision]
                if e["kind"] == "control" and not e.get("src_artifact")}

    @lru_cache(None)
    def reaches(p, target, channel, stop):
        if stop == 0:
            return (p, target, channel) in seeded
        e = events[stop - 1]
        if (e["kind"] == "reset" and node(e["target"], e.get("target_artifact")) == target
                and channel in e["channels"] and all(e.get(k) is True for k in ("independent", "scope_proved", "neutralized"))):
            return False
        if (e["kind"] == "control" and node(e["dst"], e.get("dst_artifact")) == target and e["channel"] == channel
                and controls(p, node(e["src"], e.get("src_artifact")), stop - 1)):
            return True
        return reaches(p, target, channel, stop - 1)

    def controls(p, target, stop):
        return target == ("identity", p) or any(reaches(p, target, c, stop) for c in CHANNELS)

    produced = {p for p in origins if any(controls(p, endpoint, i)
                for endpoint, i in [(target, stop) for target in (a, node(model["artifact"], True))
                                    for stop in range(production + 1, seal + 1)] +
                [(node(ref, True), production) for ref in events[production]["inputs"]])}
    judged = {p for p in origins if any(controls(p, z, decision) for z in (j, *(node(r, True) for r in refs)))}
    return produced, judged


def expected_arms(evidence, truth):
    """Decision table for the fixture domain, independent of the pilot's gate code."""
    m, r = evidence["model"], evidence["remainder"]
    clear, unsure, conflict = "NO_CONFLICT_ESTABLISHED", "UNDETERMINED", "CONFLICT"
    if not truth["valid"]:
        return clear, "MODEL_INVALID", "MODEL_INVALID"
    if not m["bound_complete"]:
        return clear, unsure, unsure
    pw, jw = concrete(m, r["witnesses"] if r["actual_attested"] else [])
    if pw & jw:
        return clear, clear, conflict
    if not r["attested"] or not r["actual_attested"]:
        return clear, clear, unsure
    pb, jb = concrete(m, r["witnesses"] + r["upper"])
    if r["issuer"] in pb | jb or pb & jb:
        return clear, clear, unsure
    return clear, clear, clear


def scientific(spec):
    if (spec["scope"] != spec["world_scope"] or not spec["policy_defined"]
            or any(name not in spec["domains"] for name in (*spec["weights"], *spec["observed"]))):
        return "STABILITY_UNDETERMINED", set(), None
    names = sorted(spec["domains"])
    worlds = product(*(spec["domains"][n] for n in names))
    admissible = {}
    for row in worlds:
        data = dict(zip(names, row))
        if any(data[k] != v for k, v in spec["observed"].items()):
            continue
        if "allowed" in spec and list(row) not in spec["allowed"]:
            continue
        if not spec["covered"] and list(row) not in spec["samples"]:
            continue
        # Construct integer margin from the declared coefficient map.
        margin = spec["offset"] - spec["threshold"] + sum(data[k] * c for k, c in spec["weights"].items())
        admissible[row] = "REJECT" if margin < 0 else "ACCEPT"
    labels = set(admissible.values())
    if not labels:
        return "STABILITY_UNDETERMINED", labels, None
    status = "UNSTABLE" if len(labels) > 1 else "CERTIFIED_STABLE" if spec["covered"] else "SAMPLED_STABLE"
    if not spec["covered"]:
        return status, labels, None
    separating_sets = [{i for i, (a, b) in enumerate(zip(left, right)) if a != b}
                       for left, right in combinations(admissible, 2) if admissible[left] != admissible[right]]
    for n in range(len(names) + 1):
        for group in combinations(range(len(names)), n):
            if all(changes.intersection(group) for changes in separating_sets):
                return status, labels, [names[i] for i in group]
    raise AssertionError("different outputs for identical worlds")
