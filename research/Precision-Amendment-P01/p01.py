"""P-01 candidate over synthetic, externally authenticated assertions."""

from fractions import Fraction
from itertools import combinations

INVALID = "MODEL_INVALID"
UNKNOWN = "UNDETERMINED"
CLEAR = "NO_CONFLICT_ESTABLISHED"
VALID = "VALID"
CONFLICT = "CONFLICT"
CHANNELS = ("artifact", "capability", "credential", "criteria")
LIFECYCLE = ("produce", "seal", "adjudicate")
REQUIRED = {
    "produce": ("artifact", "actor", "inputs"),
    "seal": ("artifact", "pins"),
    "adjudicate": ("artifact", "actor", "roots"),
    "control": ("src", "dst", "channel", "persistence"),
    "reset": ("target", "channels"),
    "read": ("actor", "artifact"),
}


def art(ref):
    return "artifact", ref


def target(case, event, key):
    ref = event[key]
    return art(ref) if event.get(key + "_artifact", False) else ("principal", canonical(case, ref))


def canonical(case, identity):
    return case.get("binding", {}).get(identity, identity)


def order_fraction(value):
    if type(value) not in (int, str):
        raise ValueError("expected an exact rational")
    return Fraction(value)


def coordinate(event):
    return event["time"], order_fraction(event["order"])


def is_id(value):
    return type(value) is str and bool(value)


def string_list(value):
    return type(value) is list and all(is_id(item) for item in value)


def ref_map(value):
    return type(value) is dict and all(is_id(k) and is_id(v) for k, v in value.items())


def normalize(case):
    """Join authenticated partial assertions by ID, then check immutable constraints."""
    contradicted, missing = [], []
    events, unverified = {}, []
    artifact, start = case.get("artifact"), case.get("record_start")
    if not is_id(artifact) or type(start) is not int or start < 0:
        contradicted.append("invalid governed object or record start")
    for row in case["events"]:
        if row.get("authenticated") is not True:
            unverified.append(row)
            continue
        event_id, kind = row.get("id"), row.get("kind")
        if not is_id(event_id) or not is_id(kind) or kind not in REQUIRED:
            contradicted.append("ill-typed authenticated envelope:" + str(event_id))
            continue
        if row.get("order") is not None and row.get("time") is None:
            contradicted.append("authenticated rank assertion without timestamp:" + event_id)
        fields = {key: value for key, value in row.items() if value is not None}
        if fields.get("order") is not None:
            try:
                fields["order"] = str(order_fraction(fields["order"]))
            except (ValueError, ZeroDivisionError):
                contradicted.append("invalid logical position:" + event_id)
        previous = events.setdefault(event_id, {})
        for key, value in fields.items():
            if key in previous and (type(previous[key]) is not type(value) or previous[key] != value):
                contradicted.append(f"incompatible assertions:{event_id}:{key}")
            else:
                previous[key] = value
    for row in unverified:
        submitted_id = row.get("id")
        proven = events.get(submitted_id) if is_id(submitted_id) else None
        claim = {key: value for key, value in row.items() if key != "authenticated" and value is not None}
        if "order" in claim:
            try:
                claim["order"] = str(order_fraction(claim["order"]))
            except (ValueError, ZeroDivisionError):
                proven = None
        if proven is None or any(type(proven.get(k)) is not type(v) or proven.get(k) != v
                                 for k, v in claim.items()):
            missing.append("event authentication:" + str(submitted_id))
    for link in case.get("dependencies", ()):
        if link.get("authenticated") is True and not all(is_id(link.get(k)) for k in ("from", "to", "role")):
            contradicted.append("ill-typed authenticated dependency link")
    positions, lifecycle = {}, {}
    for event in events.values():
        event_id, kind = event["id"], event["kind"]
        for key in ("time", "order", *REQUIRED[kind]):
            if key not in event:
                missing.append(f"event field:{event_id}:{key}")
                continue
            value = event[key]
            if key == "time":
                ok = type(value) is int and value >= 0
            elif key in ("roots", "pins"):
                ok = ref_map(value)
            elif key in ("channels", "inputs"):
                ok = string_list(value) and (key != "channels" or bool(value) and set(value) <= set(CHANNELS))
            else:
                ok = is_id(value)
            if not ok:
                contradicted.append(f"ill-typed event field:{event_id}:{key}")
        for key in ("src_artifact", "dst_artifact", "target_artifact"):
            if key in event and type(event[key]) is not bool:
                contradicted.append(f"ill-typed endpoint tag:{event_id}:{key}")
        if kind in LIFECYCLE:
            if kind in lifecycle:
                contradicted.append("multiple authenticated " + kind + " events")
            lifecycle[kind] = event
            if "artifact" in event and event["artifact"] != artifact:
                contradicted.append("incompatible object binding:" + event_id)
        if not contradicted and "order" in event and "time" in event:
            pos = coordinate(event)
            if pos in positions:
                contradicted.append("different authenticated event IDs at " + str(pos))
            positions[pos] = event_id
    for kind in LIFECYCLE:
        if kind not in lifecycle:
            missing.append("required event:" + kind)
    if case.get("binding_verified") is not True:
        missing.append("verified principal mapping")
    elif not ref_map(case.get("binding", {})):
        contradicted.append("malformed attested principal mapping")
    seal, decision = lifecycle.get("seal", {}), lifecycle.get("adjudicate", {})
    if "roots" in decision and not contradicted:
        # A required pin is part of the committed decision closure, possibly as an indirect input.
        _, versions, _ = bound_artifacts(case, decision["roots"])
        for name, ref in seal.get("pins", {}).items():
            if name in versions and versions[name] != {ref}:
                contradicted.append("sealed dependency version mismatch:" + name)
            elif name not in versions:
                if case.get("bound_complete") is True and case.get("graph_attested") is True and all(
                    link.get("authenticated") is True for link in case.get("dependencies", ())
                ):
                    contradicted.append("sealed dependency absent from certified closure:" + name)
                else:
                    missing.append("sealed dependency binding:" + name)
        for name, choices in versions.items():
            if len(choices) > 1:
                contradicted.append("mutually exclusive dependency versions:" + name)
    return events, lifecycle, sorted(set(contradicted)), sorted(set(missing))


def ordered_completion(lifecycle, start):
    """Fixed lifecycle timestamps must be nondecreasing; fixed pairs strictly increase."""
    ticks = [start, *(lifecycle[k]["time"] for k in LIFECYCLE if "time" in lifecycle.get(k, {}))]
    if ticks != sorted(ticks):
        return False
    observed = [lifecycle[k] for k in LIFECYCLE if "time" in lifecycle.get(k, {})
                and "order" in lifecycle[k]]
    return all(coordinate(left) < coordinate(right) for left, right in combinations(observed, 2))


def bound_artifacts(case, roots):
    """Follow authenticated dependency links out of authenticated decision roots."""
    versions = {name: {ref} for name, ref in roots.items()}
    paths = {ref: ("decision-root:" + name,) for name, ref in sorted(roots.items())}
    links = [link for link in case.get("dependencies", ()) if link.get("authenticated") is True]
    pending = list(paths)
    while pending:
        parent = pending.pop()
        for index, link in enumerate(links):
            if link["from"] != parent:
                continue
            name, ref = link["role"], link["to"]
            versions.setdefault(name, set()).add(ref)
            if ref not in paths:
                paths[ref] = (*paths[parent], "dependency:" + str(index) + ":" + ref)
                pending.append(ref)
    return set(paths), versions, paths


def verified_reset(event):
    return all(event.get(k) is True for k in ("independent", "scope_proved", "neutralized"))


def record_gaps(case, trace):
    missing = []
    history = case.get("history", {})
    if not (history.get("trusted") is True and history.get("coverage") is True):
        missing.append("historical closure")
    if any(not verified_seed(seed)
           for seed in history.get("seeds", ())):
        missing.append("verified history seeds")
    if case.get("record_complete") is not True:
        missing.append("control record coverage")
    if (case.get("bound_complete") is not True or case.get("graph_attested") is not True
            or any(link.get("authenticated") is not True for link in case.get("dependencies", ()))):
        missing.append("certified complete decision dependencies")
    if (case.get("snapshot_attested") is not True or not is_id(case.get("snapshot_version"))
            or case.get("snapshot_version") != case.get("commit_version")):
        missing.append("matching attested evaluation/commit snapshots")
    for event in trace:
        if event["kind"] == "reset" and not verified_reset(event):
            missing.append("verified reset:" + event["id"])
        if event["kind"] == "control" and (
            event["persistence"] != "potential_durable" or event["channel"] not in CHANNELS
        ):
            missing.append("supported causal control effect:" + event["id"])
    return missing


def verified_seed(seed):
    return (seed.get("authenticated") is True and seed.get("channel") in CHANNELS
            and all(is_id(seed.get(k)) for k in ("id", "principal", "target"))
            and type(seed.get("target_artifact", False)) is bool)


def initial_tokens(case):
    history = case.get("history", {})
    if history.get("trusted") is not True:
        return
    for seed in history.get("seeds", ()):
        if verified_seed(seed):
            yield (canonical(case, seed["principal"]), target(case, seed, "target"), seed["channel"],
                   (seed["id"],))


def influence(case, trace, lifecycle, refs):
    """Forward replay over versioned targets and independently neutralized channels."""
    state = {}
    produced = {}
    producer = ("principal", canonical(case, lifecycle["produce"]["actor"]))
    adjudicator = ("principal", canonical(case, lifecycle["adjudicate"]["actor"]))
    output = art(case["artifact"])
    for principal, obj, channel, proof in initial_tokens(case):
        state.setdefault(obj, {})[(principal, channel)] = proof

    def controllers(obj):
        origins = {p: proof for (p, _), proof in state.get(obj, {}).items()}
        if obj[0] == "principal":
            origins[obj[1]] = ("self:" + obj[1],)
        return origins

    def collect(obj, reason):
        for p, proof in controllers(obj).items():
            produced.setdefault(p, (*proof, reason))

    mutable = False
    for event in trace:
        kind, event_id = event["kind"], event["id"]
        if kind == "control" and event["persistence"] == "potential_durable" and event["channel"] in CHANNELS:
            src, dst = target(case, event, "src"), target(case, event, "dst")
            for p, proof in controllers(src).items():
                state.setdefault(dst, {}).setdefault((p, event["channel"]), (*proof, event_id))
        elif kind == "reset" and verified_reset(event):
            obj = target(case, event, "target")
            state[obj] = {key: proof for key, proof in state.get(obj, {}).items() if key[1] not in event["channels"]}
        elif kind == "produce":
            mutable = True
            for ref in event["inputs"]:
                collect(art(ref), "production-input:" + event_id)
        elif kind == "seal":
            mutable = False
        if mutable:
            collect(producer, "mutable-production:" + event_id)
            collect(output, "mutable-object:" + event_id)
    return produced, {obj: controllers(obj) for obj in (adjudicator, *(art(ref) for ref in refs))}


def evaluate(case):
    events, lifecycle, problems, missing = normalize(case)
    if not problems and not ordered_completion(lifecycle, case["record_start"]):
        problems.append("no ordered completion of the authenticated lifecycle")
    report = {"input": INVALID if problems else UNKNOWN if missing else VALID,
              "contradictions": sorted(set(problems)), "missing": missing, "witnesses": [],
              "P_x": [], "J_star": [], "bound": [], "authorized_by_fixture": False}
    if report["input"] != VALID:
        return report | {"outcome": report["input"]}
    decision = lifecycle["adjudicate"]
    trace = sorted((event for event in events.values()
                    if case["record_start"] <= event["time"] and coordinate(event) < coordinate(decision)),
                   key=coordinate)
    gaps = record_gaps(case, trace)
    refs, _, bindings = bound_artifacts(case, decision["roots"])
    produced, influenced = influence(case, trace, lifecycle, refs)
    witnesses = []
    for obj, controllers in sorted(influenced.items()):
        for p in sorted(produced.keys() & controllers.keys()):
            witnesses.append({"principal": p, "production": produced[p], "decision_target": obj,
                              "decision": controllers[p], "binding": bindings.get(obj[1], ()) if obj[0] == "artifact" else ()})
    outcome = CONFLICT if witnesses else UNKNOWN if gaps else CLEAR
    return report | {"outcome": outcome, "witnesses": witnesses, "bound": sorted(refs), "missing": gaps,
                     "P_x": sorted(produced), "J_star": sorted(set().union(*influenced.values())),
                     "authorized_by_fixture": outcome == CLEAR and case.get("authorized") is True}
