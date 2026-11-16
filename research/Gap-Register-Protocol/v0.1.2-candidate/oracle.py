"""Bounded synthetic reference. No DEA, policy engine or real authentication."""
from itertools import permutations

KEYS = {"ka": "p", "kq": "q", "kj": "j", "ki": "issuer"}
CHANNELS = {"threshold", "layout"}
ARTIFACTS = {"r", "s", "t"}
RANKS = range(16)
VERSIONS = {f"{artifact}@{n}" for artifact in ARTIFACTS for n in range(3)}
FIELDS = {
    "grant": {"subject", "target", "channel"},
    "retract": {"subject", "target", "channel"},
    "revoke": {"subject"},
    "modify": {"base", "version", "channel", "value"},
    "reset": {"base", "version", "channel"},
    "produce": {"version", "value"},
    "seal": {"version", "policy"},
    "bind": {"version", "root", "policy"},
    "read": {"version", "parent"},
    "adjudicate": {"version", "policy"},
}
SINGLETONS = ("produce", "seal", "bind", "adjudicate")
POLICY = "sum-thresholds@1"


def grammar(event):
    common = {"id", "kind", "key", "time", "rank"}
    kind = event.get("kind")
    if not isinstance(kind, str) or kind not in FIELDS or set(event) != common | FIELDS[kind]:
        return False
    if any(not isinstance(event[field], str) for field in FIELDS[kind] - {"value", "parent"}):
        return False
    key = event["key"]
    if not isinstance(key, str) or key not in KEYS or type(event["time"]) is not int or event["time"] not in RANKS:
        return False
    rank = event["rank"]
    if rank is not None and (type(rank) is not int or rank not in RANKS):
        return False
    if kind in {"grant", "retract", "revoke", "reset"} and key != "ki":
        return False
    if kind in {"seal", "bind", "read", "adjudicate"} and key != "kj":
        return False
    if kind in {"grant", "retract"}:
        target, channel = event["target"], event["channel"]
        return event["subject"] in {"ka", "kq"} and (
            (target == "x" and channel == "score") or
            (target in ARTIFACTS and channel in CHANNELS))
    if kind == "revoke":
        return event["subject"] in {"ka", "kq"}
    if kind in {"modify", "reset"}:
        base, version = event["base"], event["version"]
        if base not in VERSIONS or version not in VERSIONS:
            return False
        if base[0] != version[0] or int(base[-1]) + 1 != int(version[-1]):
            return False
        return event["channel"] in CHANNELS and (
            kind == "reset" or (type(event["value"]) is int and event["value"] in (0, 1)))
    if kind == "read":
        return event["version"] in VERSIONS and (
            event["parent"] is None or isinstance(event["parent"], str) and event["parent"] in VERSIONS)
    if event["version"] != "x@1":
        return False
    if kind == "produce":
        return key in {"ka", "kq", "kj"} and type(event["value"]) is int and event["value"] in range(4)
    if kind == "bind" and event["root"] not in VERSIONS:
        return False
    return event["policy"] == POLICY


def ordered_completions(events):
    """Enumerate rank embeddings for supplied records, without inventing records."""
    if len(events) > len(RANKS):
        return
    known = {event["rank"]: event for event in events if event["rank"] is not None}
    missing = [event for event in events if event["rank"] is None]
    if len(known) + len(missing) != len(events):
        return
    available = [rank for rank in RANKS if rank not in known]
    for slots in permutations(available, len(missing)):
        chosen = {**known, **{rank: {**event, "rank": rank} for event, rank in zip(missing, slots)}}
        order = [chosen[rank] for rank in sorted(chosen)]
        if all(a["time"] <= b["time"] for a, b in zip(order, order[1:])):
            yield order


def statically_possible(events):
    stages = [event["kind"] for event in events if event["kind"] in SINGLETONS]
    if stages != [kind for kind in SINGLETONS if kind in stages]:
        return False
    revoked = set()
    versions = set()
    seen = set()
    binding_listed = "bind" in stages
    for event in events:
        kind, key = event["kind"], event["key"]
        if key in revoked:
            return False
        if kind == "revoke":
            if event["subject"] in revoked:
                return False
            revoked.add(event["subject"])
        if kind in {"modify", "reset"}:
            if event["version"] in versions:
                return False
            versions.add(event["version"])
        if "adjudicate" in seen or kind == "read" and binding_listed and "bind" not in seen:
            return False
        seen.add(kind)
    return True


def replay(events, require_root):
    """Return (production route, evaluation routes), or None on contradiction."""
    if not statically_possible(events):
        return None
    stages = []
    active, revoked = {}, set()
    snapshots = {f"{a}@0": {c: (0, ()) for c in CHANNELS} for a in ARTIFACTS}
    latest = {a: f"{a}@0" for a in ARTIFACTS}
    used, routes = {}, []
    production = None
    binding = None
    for event in events:
        kind, key, eid = event["kind"], event["key"], event["id"]
        if kind == "revoke":
            revoked.add(event["subject"])
        elif kind in {"grant", "retract"}:
            entry = (event["subject"], event["target"], event["channel"])
            if kind == "grant":
                if entry in active or entry[0] in revoked:
                    return None
                active[entry] = eid
            elif entry not in active:
                return None
            else:
                del active[entry]
        elif kind in {"modify", "reset"}:
            base, version, channel = event["base"], event["version"], event["channel"]
            if latest[base[0]] != base or version in snapshots:
                return None
            current = snapshots[base]
            if kind == "modify":
                grant = active.get((key, base[0], channel))
                if grant is None:
                    return None
                value = event["value"]
                effects = current[channel][1] if value == current[channel][0] else ((key, grant, eid),)
            else:
                value, effects = 0, ()
            snapshots[version] = {**current, channel: (value, effects)}
            latest[base[0]] = version
        elif kind in SINGLETONS:
            if kind != SINGLETONS[len(stages)]:
                return None
            stages.append(kind)
            if kind == "produce":
                grant = active.get((key, "x", "score"))
                if grant is not None:
                    production = (KEYS[key], grant, eid)
                elif event["value"] != 0:
                    return None
            elif kind == "bind":
                if event["root"] not in snapshots:
                    return None
                binding = (eid, event["root"], dict(snapshots), dict(latest),
                           {entry: grant for entry, grant in active.items() if entry[0] not in revoked})
        elif kind == "read":
            if stages != list(SINGLETONS[:3]):
                return None
            bind_id, root, frozen, heads, rights = binding
            version, parent = event["version"], event["parent"]
            if version not in frozen or version[0] in used:
                return None
            if parent is None:
                if version != root or used:
                    return None
            elif parent not in used.values() or version == root:
                return None
            used[version[0]] = version
            for writer, grant, write in frozen[version]["threshold"][1]:
                routes.append((KEYS[writer], version, "surviving", grant, write, bind_id, eid))
            if heads[version[0]] == version and not version.endswith("@2"):
                for (author, target, channel), grant in sorted(rights.items()):
                    if (target, channel) == (version[0], "threshold"):
                        routes.append((KEYS[author], version, "potential", grant, bind_id, eid))
    if stages != list(SINGLETONS):
        return None
    if not used:
        bind_rank = next(event["rank"] for event in events if event["kind"] == "bind")
        filled = {event["rank"] for event in events}
        can_add_root = any(rank not in filled for rank in range(bind_rank + 1, events[-1]["rank"]))
        if require_root or not can_add_root:
            return None
    return production, routes


def input_valid(events):
    if not all(isinstance(event, dict) for event in events):
        return False
    ids = [event.get("id") for event in events]
    return (all(type(eid) is int and eid in RANKS for eid in ids)
            and len(ids) == len(set(ids)) and all(grammar(event) for event in events))


def witnesses(state):
    production, routes = state
    if production is None:
        return []
    return sorted([list(production) + list(route[1:]) for route in routes if route[0] == production[0]])


def truth(world):
    events = world["events"]
    if not input_valid(events) or any(event["rank"] is None for event in events):
        return "MODEL_INVALID"
    for order in ordered_completions(events):
        state = replay(order, require_root=True)
        if state is not None:
            return "CONFLICT" if witnesses(state) else "NO_CONFLICT"
    return "MODEL_INVALID"


def justified(evidence):
    events = evidence["events"]
    closed = evidence["history_closed"]
    dependencies = evidence["dependencies_closed"]
    if not input_valid(events):
        return {"verdict": "INVALID", "proof": "authenticated_grammar"}
    viable = (order for order in ordered_completions(events) if statically_possible(order))
    if not closed:
        reason = "history_open" if next(viable, None) is not None else "no_structural_completion"
        return {"verdict": "UNDETERMINED" if reason == "history_open" else "INVALID", "proof": reason}
    for order in viable:
        state = replay(order, require_root=dependencies)
        if state is None:
            continue
        if any(event["rank"] is None for event in events):
            return {"verdict": "UNDETERMINED", "proof": "rank_unverified"}
        positive = witnesses(state)
        if positive:
            return {"verdict": "CONFLICT", "proof": "scoped_replay", "witness": positive[0]}
        if dependencies:
            return {"verdict": "CLEAR", "proof": "scoped_replay_and_dependency_coverage"}
        return {"verdict": "UNDETERMINED", "proof": "dependency_coverage_open"}
    return {"verdict": "INVALID", "proof": "no_closed_completion"}
